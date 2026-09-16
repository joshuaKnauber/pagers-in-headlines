#!/usr/bin/env python3
"""Step-5 extraction for Germany/US. Usage: extract_de_us.py <germany|us>

Fetches every tagged candidate (strong/related/gdelt-hit + curated) via
the outlet's register route (curl, browser UA — several CDNs block
python TLS), extracts JSON-LD body/date first, p-cluster fallback,
retags relevance on title+body, appends to corpus-candidates-v1.jsonl.
Resumable (skips URLs already in the output).
Routes: live | wayback (first_capture ts) | avail (availability API per
URL, NYT — captures exist but CDX/enumeration is blocked).
"""
import csv, glob, hashlib, html as H, json, re, subprocess, sys, time, urllib.parse
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36"

ROUTES = {
 "germany": dict(live=["tagesschau", "zdfheute", "rtl", "ntv", "bild", "spiegel", "welt", "tonline"],
                 wayback=["rnd"], avail=[]),
 "us": dict(live=["fox", "cnn", "cbs", "nbc", "usatoday", "yahoo", "ap"],
            wayback=["abc", "wapo", "reuters"], avail=["nyt"]),
}
STRONG = {
 "germany": ["pager", "piepser", "funkger", "walkie", "gold apollo", "gold-apollo"],
 "us": ["pager", "beeper", "walkie", "gold apollo", "gold-apollo", "icom"],
}
CTX = ["hisbollah", "hezbollah", "libanon", "lebanon", "beirut"]
EVT = ["explod", "explos", "detonat", "blast", "sprengst", "gerät"]


def curl(url, timeout=90):
    p = subprocess.run(["curl", "-sL", "-m", str(timeout), "-A", UA,
                        "-H", "Accept: text/html,application/xhtml+xml",
                        "-H", "Accept-Language: en-US,en;q=0.9,de;q=0.8", url],
                       capture_output=True)
    if p.returncode != 0 or len(p.stdout) < 500:
        raise RuntimeError(f"curl rc={p.returncode} len={len(p.stdout)}")
    return p.stdout.decode("utf-8", "replace")


def ldjson(t):
    out = {}
    for m in re.finditer(r'<script[^>]*type="application/ld\+json"[^>]*>(.*?)</script>', t, re.S):
        try:
            d = json.loads(m.group(1).strip())
        except Exception:
            continue
        for it in (d if isinstance(d, list) else [d]):
            if isinstance(it, dict) and "@graph" in it:
                pass
            if isinstance(it, dict) and it.get("@type") in ("NewsArticle", "Article", "ReportageNewsArticle", "VideoObject", "LiveBlogPosting"):
                out.setdefault("date", (it.get("datePublished") or it.get("uploadDate") or "")[:10])
                if it.get("articleBody"):
                    out.setdefault("body", it["articleBody"])
                if it.get("headline"):
                    out.setdefault("headline", H.unescape(it["headline"]))
    return out


def pcluster(t):
    body = re.sub(r"<script.*?</script>|<style.*?</style>|<header.*?</header>|<footer.*?</footer>|<nav.*?</nav>|<aside.*?</aside>", " ", t, flags=re.S | re.I)
    paras = [H.unescape(re.sub(r"<[^>]+>", " ", p)) for p in re.findall(r"<p[^>]*>(.*?)</p>", body, re.S)]
    return "\n".join(" ".join(p.split()) for p in paras if len(p.split()) > 4)


def title_of(t):
    m = re.search(r"<title>([^<]{3,300})</title>", t)
    return H.unescape(m.group(1)).strip() if m else ""


def avail_capture(url):
    q = f"http://archive.org/wayback/available?url={urllib.parse.quote(url, safe='')}&timestamp=20240918"
    d = json.loads(curl(q, 40))
    c = d.get("archived_snapshots", {}).get("closest")
    if c and c.get("timestamp", "9") <= "20241231":
        return c["timestamp"]
    return None


def relevance(text, country):
    tl = text.lower()
    if any(k in tl for k in STRONG[country]):
        return "strong"
    if any(k in tl for k in CTX) and any(k in tl for k in EVT):
        return "related"
    return "none"


def main():
    country = sys.argv[1]
    routes = ROUTES[country]
    D = ROOT / country
    (D / "raw").mkdir(exist_ok=True)
    out_path = D / "corpus-candidates-v1.jsonl"
    done = set()
    if out_path.exists():
        done = {json.loads(l)["url"] for l in open(out_path, encoding="utf-8")}
    outf = open(out_path, "a", encoding="utf-8")
    order = routes["live"] + routes["wayback"] + routes["avail"]
    for outlet in order:
        f = D / "enumeration" / f"{outlet}-urls.csv"
        if not f.exists():
            print(f"!! no manifest {outlet}", flush=True)
            continue
        cands = [r for r in csv.DictReader(open(f, encoding="utf-8")) if r["event_candidate"]]
        (D / "raw" / outlet).mkdir(parents=True, exist_ok=True)
        route = ("live" if outlet in routes["live"] else
                 "wayback" if outlet in routes["wayback"] else "avail")
        print(f"== {country}/{outlet}: {len(cands)} candidates via {route}", flush=True)
        for i, r in enumerate(cands):
            url = r["url"]
            if url in done:
                continue
            if route == "live":
                target = url
            elif route == "wayback":
                ts = (r["first_capture"] or "20240918")[:14]
                target = f"https://web.archive.org/web/{ts}/{url}"
            else:
                ts = None
                try:
                    ts = avail_capture(url)
                except Exception:
                    pass
                if not ts:
                    outf.write(json.dumps({"outlet": outlet, "url": url, "fetch_route": "avail",
                                           "title": "", "published_at": r["first_capture"][:8] if r["first_capture"] else "",
                                           "body_words": 0, "body_text": "", "relevance": "no-capture"},
                                          ensure_ascii=False) + "\n")
                    continue
                target = f"https://web.archive.org/web/{ts}/{url}"
            rec = {"outlet": outlet, "url": url, "fetch_route": route, "manifest_tag": r["event_candidate"]}
            h = None
            for attempt in range(3):
                try:
                    h = curl(target)
                    break
                except Exception:
                    time.sleep(6 if route == "live" else 20)
            if h:
                dig = hashlib.sha256(url.encode()).hexdigest()[:16]
                (D / "raw" / outlet / f"{dig}.html").write_text(h, encoding="utf-8")
                ld = ldjson(h)
                body = " ".join((ld.get("body") or pcluster(h)).split())
                title = ld.get("headline") or title_of(h)
                rec.update({"raw_path": f"raw/{outlet}/{dig}.html", "title": title,
                            "published_at": ld.get("date", ""),
                            "date_source": "ld-json" if ld.get("date") else "",
                            "body_words": len(body.split()), "body_text": body[:20000],
                            "extract_method": "ld-json" if ld.get("body") else "p-cluster",
                            "relevance": relevance(title + " " + body[:6000], country)})
            else:
                rec.update({"raw_path": "", "title": "", "published_at": "",
                            "body_words": 0, "body_text": "", "relevance": "fetch-failed"})
            outf.write(json.dumps(rec, ensure_ascii=False) + "\n")
            outf.flush()
            done.add(url)
            if (i + 1) % 25 == 0:
                print(f"   {outlet} {i+1}/{len(cands)}", flush=True)
            time.sleep(1.2 if route == "live" else 3.0)
    outf.close()
    print(f"EXTRACT {country} DONE", flush=True)


if __name__ == "__main__":
    main()
