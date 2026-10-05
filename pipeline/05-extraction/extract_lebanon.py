#!/usr/bin/env python3
"""Step 5 (phase 1): fetch + triage + extract all event-candidate URLs.

Routes per the access register: live direct for LBCI/Al Jadeed/MTV,
archive.almanar.com.lb for Al-Manar, Wayback nearest-2024 capture for NNA
(and as fallback for the others). Raw HTML saved under data/lebanon/raw/.

Extraction is deliberately light (title, published_at, body text via
largest-<p>-cluster heuristic) — records flow into the corpus schema
properly at the normalization stage; this produces triage-verified
candidate records with real dates.
"""
import csv, hashlib, html as htmllib, json, re, sys, time, urllib.parse, urllib.request
from pathlib import Path

DATA = Path(__file__).resolve().parents[2] / "data"
RAW = DATA / "lebanon" / "raw"
UA = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) research-collection"}

STRONG = ["pager", "beeper", "بيجر", "البيجر", "بيجرات", "أجهزة النداء", "اجهزة النداء",
          "gold apollo", "غولد أبولو", "غولد ابولو"]
RELATED = ["walkie", "ووكي", "توكي", "لاسلكي", "اللاسلكي", "icom", "أيكوم", "ايكوم",
           "أجهزة الاتصال", "اجهزة الاتصال", "exploding devices", "تفجير الأجهزة", "تفجير أجهزة"]


def fetch(url, timeout=45):
    req = urllib.request.Request(url, headers=UA)
    return urllib.request.urlopen(req, timeout=timeout).read().decode("utf-8", "replace")


def get_with_route(outlet, url):
    """Return (html, route) trying the register's route order."""
    tries = []
    if outlet == "almanar":
        tries = [(url.replace("www.almanar.com.lb", "archive.almanar.com.lb")
                     .replace("://almanar.com.lb", "://archive.almanar.com.lb"), "archive-subdomain"),
                 ("https://web.archive.org/web/20240918/" + url, "wayback")]
    elif outlet == "nna":
        tries = [("https://web.archive.org/web/20240918/" + url, "wayback"),
                 (url, "direct")]
    else:
        tries = [(url, "direct"),
                 ("https://web.archive.org/web/20240918/" + url, "wayback")]
    for u, route in tries:
        try:
            h = fetch(u)
            if len(h) > 4000:
                return h, route
        except Exception:
            time.sleep(1)
    return None, "fail"


def extract(html):
    title = None
    m = re.search(r'property="og:title" content="([^"]+)"', html) or re.search(r"<title>([^<]+)</title>", html)
    if m:
        title = htmllib.unescape(m.group(1)).strip()
    pub = None
    for pat in (r'property="article:published_time" content="([0-9T:\-+.]+)"',
                r'"datePublished"\s*:\s*"([0-9T:\-+.]+)"',
                r'name="publishdate" content="([^"]+)"'):
        m = re.search(pat, html)
        if m:
            pub = m.group(1)[:10]
            break
    body = re.sub(r"<script.*?</script>|<style.*?</style>|<header.*?</header>|<footer.*?</footer>|<nav.*?</nav>", " ", html, flags=re.S | re.I)
    paras = [htmllib.unescape(re.sub(r"<[^>]+>", " ", p)) for p in re.findall(r"<p[^>]*>(.*?)</p>", body, re.S)]
    paras = [" ".join(p.split()) for p in paras if len(p.split()) > 4]
    text = "\n".join(paras)
    return title, pub, text


def relevance(*texts):
    blob = " ".join(t.lower() for t in texts if t)
    if any(k in blob for k in STRONG):
        return "strong"
    if any(k in blob for k in RELATED):
        return "related"
    return "none"


def main():
    RAW.mkdir(parents=True, exist_ok=True)
    out = []
    for outlet in ["lbci", "aljadeed", "mtv", "almanar", "nna"]:
        rows = list(csv.DictReader(open(DATA / "lebanon" / "04-enumeration" / f"{outlet}-urls.csv", encoding="utf-8")))
        cands = [r for r in rows if r["event_candidate"] == "1"]
        print(f"== {outlet}: {len(cands)} candidates", flush=True)
        (RAW / outlet).mkdir(exist_ok=True)
        for i, r in enumerate(cands):
            url = r["url"]
            h, route = get_with_route(outlet, url)
            rec = {"outlet": outlet, "url": url, "fetch_route": route,
                   "manifest_date": r.get("publication_date", "")}
            if h:
                digest = hashlib.sha256(url.encode()).hexdigest()[:16]
                (RAW / outlet / f"{digest}.html").write_text(h, encoding="utf-8")
                title, pub, text = extract(h)
                rec.update({"raw_path": f"raw/{outlet}/{digest}.html", "title": title,
                            "published_at": pub or r.get("publication_date", ""),
                            "body_words": len(text.split()), "body_text": text[:20000],
                            "relevance": relevance(title, text[:6000], urllib.parse.unquote(url))})
            else:
                rec.update({"raw_path": "", "title": None, "published_at": "",
                            "body_words": 0, "body_text": "", "relevance": "fetch-failed"})
            out.append(rec)
            if (i + 1) % 25 == 0:
                print(f"   {i+1}/{len(cands)}", flush=True)
            time.sleep(0.7)
    with open(DATA / "lebanon" / "05-extraction/candidates.jsonl", "w", encoding="utf-8") as f:
        for rec in out:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")
    from collections import Counter
    print("relevance:", Counter(r["relevance"] for r in out))
    print("routes:", Counter(r["fetch_route"] for r in out))
    print("DONE", len(out))


if __name__ == "__main__":
    main()
