#!/usr/bin/env python3
"""Israel step-5 extraction: fetch tagged candidates, extract fields.

Usage: israel_extract.py <outlet> [<outlet> ...]
Reads <outlet>-titles-*.csv (tagged rows), fetches via the outlet's
register route, extracts via JSON-LD first (Ynet/mako serve
datePublished/articleBody), falls back to <p>-cluster. Appends to
data/israel/corpus-candidates-v1.jsonl; raw under data/israel/raw/.
"""
import csv, glob, hashlib, html as H, json, re, sys, time, urllib.request
from pathlib import Path

DATA = Path(__file__).resolve().parent.parent / "israel"
RAW = DATA / "raw"
UA = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) research-collection"}
ROUTES = {"ynet": "live", "kikar": "live", "n12": "wayback", "makan": "wayback"}

STRONG = ["ביפר", "ביפרים", "איתורית", "זימונית", "גולד אפולו", "بيجر", "البيجر", "pager", "beeper"]
RELATED = ["מכשירי קשר", "מכשירי הקשר", "ווקי טוקי", "ווקי-טוקי", "لاسلكي", "اللاسلكي",
           "أجهزة الاتصال", "walkie", "icom", "איקום"]


def fetch(url, timeout=45):
    return urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=timeout).read().decode("utf-8", "replace")


def ldjson(t):
    out = {}
    for m in re.finditer(r'<script type="application/ld\+json"[^>]*>(.*?)</script>', t, re.S):
        try:
            d = json.loads(m.group(1))
        except Exception:
            continue
        items = d if isinstance(d, list) else [d]
        for it in items:
            if isinstance(it, dict) and it.get("@type") in ("NewsArticle", "Article", "ReportageNewsArticle"):
                out.setdefault("date", (it.get("datePublished") or "")[:10])
                if it.get("articleBody"):
                    out.setdefault("body", it["articleBody"])
                out.setdefault("headline", it.get("headline"))
    return out


def pcluster(t):
    body = re.sub(r"<script.*?</script>|<style.*?</style>|<header.*?</header>|<footer.*?</footer>|<nav.*?</nav>", " ", t, flags=re.S | re.I)
    paras = [H.unescape(re.sub(r"<[^>]+>", " ", p)) for p in re.findall(r"<p[^>]*>(.*?)</p>", body, re.S)]
    paras = [" ".join(p.split()) for p in paras if len(p.split()) > 4]
    return "\n".join(paras)


def main():
    outlets = sys.argv[1:]
    out_path = DATA / "corpus-candidates-v1.jsonl"
    done = set()
    if out_path.exists():
        done = {json.loads(l)["url"] for l in open(out_path, encoding="utf-8")}
    outf = open(out_path, "a", encoding="utf-8")
    for outlet in outlets:
        cands = []
        for f in glob.glob(str(DATA / "enumeration" / f"{outlet}-titles-*.csv")):
            for r in csv.DictReader(open(f, encoding="utf-8")):
                if r["relevance"]:
                    cands.append(r)
        # need first_capture for wayback route
        caps = {}
        if ROUTES[outlet] == "wayback":
            for r in csv.DictReader(open(DATA / "enumeration" / f"{outlet}-urls.csv", encoding="utf-8")):
                caps[r["url"]] = r["first_capture"]
        (RAW / outlet).mkdir(parents=True, exist_ok=True)
        print(f"== {outlet}: {len(cands)} tagged", flush=True)
        for i, r in enumerate(cands):
            if r["url"] in done:
                continue
            target = r["url"] if ROUTES[outlet] == "live" else f"https://web.archive.org/web/{caps.get(r['url'],'20240918')}/{r['url']}"
            rec = {"outlet": outlet, "url": r["url"], "fetch_route": ROUTES[outlet], "sweep_title": r["title"]}
            h = None
            for attempt in range(2):
                try:
                    h = fetch(target); break
                except Exception:
                    time.sleep(8)
            if h:
                dig = hashlib.sha256(r["url"].encode()).hexdigest()[:16]
                (RAW / outlet / f"{dig}.html").write_text(h, encoding="utf-8")
                ld = ldjson(h)
                body = ld.get("body") or pcluster(h)
                body = " ".join(body.split()) if body else ""
                title = ld.get("headline") or r["title"]
                blob = (title + " " + body[:6000]).lower()
                rel = ("strong" if any(k.lower() in blob for k in STRONG)
                       else "related" if any(k.lower() in blob for k in RELATED) else "none")
                rec.update({"raw_path": f"raw/{outlet}/{dig}.html", "title": title,
                            "published_at": ld.get("date", ""), "date_source": "ld-json" if ld.get("date") else "",
                            "body_words": len(body.split()), "body_text": body[:20000],
                            "extract_method": "ld-json" if ld.get("body") else "p-cluster",
                            "relevance": rel})
            else:
                rec.update({"raw_path": "", "title": r["title"], "published_at": "", "body_words": 0,
                            "body_text": "", "relevance": "fetch-failed"})
            outf.write(json.dumps(rec, ensure_ascii=False) + "\n")
            outf.flush()
            if (i + 1) % 20 == 0:
                print(f"   {i+1}/{len(cands)}", flush=True)
            time.sleep(1.0)
    outf.close()
    print("EXTRACT DONE", flush=True)


if __name__ == "__main__":
    main()
