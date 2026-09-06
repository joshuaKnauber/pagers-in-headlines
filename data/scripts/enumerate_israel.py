#!/usr/bin/env python3
"""Step 4 enumeration - Israel gate rows.

Same CDX approach as Lebanon (see enumerate_outlets.py) with Israel's
event-era patterns from the access register. Israeli article URLs are
opaque (no keyword slugs), so event_candidate tagging is deferred to the
step-5 title sweep; this run delivers manifests + capture denominators.

Abu Ali Express is capture-stream enumeration: every archived snapshot of
t.me/s/abualiexpress in the window (messages extracted from captures in
step 5 with cross-capture dedup).
"""
import csv, json, re, sys, time, urllib.parse, urllib.request
from collections import Counter
from pathlib import Path

DATA = Path(__file__).resolve().parent.parent
WINDOW = ("20240915", "20241017")
UA = {"User-Agent": "Mozilla/5.0 (research collection; pager-news project)"}

OUTLETS = {
    "ynet": {"cdx_url": "ynet.co.il/news/article", "match": "prefix",
             "article_re": r"ynet\.co\.il/news/article/[a-z0-9]{5,12}/?$"},
    "n12": {"cdx_url": "mako.co.il/news", "match": "prefix",
            "article_re": r"mako\.co\.il/news-[^?]*/Article-[0-9a-f]+\.htm",
            "strip_query": True},
    "kikar": {"cdx_url": "kikar.co.il", "match": "domain",
              "article_re": r"kikar\.co\.il/[a-z-]{3,30}/[a-z0-9]{4,10}/?$"},
    "makan": {"cdx_url": "makan.org.il", "match": "domain",
              "article_re": r"makan\.org\.il/content/news/[^?\"]+/\d{4,}/?"},
}


def fetch(url, timeout=90):
    req = urllib.request.Request(url, headers=UA)
    return urllib.request.urlopen(req, timeout=timeout).read().decode("utf-8", "replace")


def cdx_enumerate(cfg):
    rows, resume = {}, None
    base = ("https://web.archive.org/cdx/search/cdx?url={u}&matchType={m}"
            "&from={f}&to={t}&output=json&collapse=urlkey&filter=statuscode:200"
            "&limit=15000&showResumeKey=true").format(
        u=urllib.parse.quote(cfg["cdx_url"]), m=cfg["match"], f=WINDOW[0], t=WINDOW[1])
    art = re.compile(cfg["article_re"], re.I)
    for _ in range(25):
        url = base + (f"&resumeKey={urllib.parse.quote(resume)}" if resume else "")
        for attempt in range(3):
            try:
                raw = fetch(url); break
            except Exception as e:
                print(f"    retry: {e}", file=sys.stderr); time.sleep(12)
        else:
            return rows, False
        try:
            data = json.loads(raw)
        except json.JSONDecodeError:
            data = []
            for line in raw.splitlines():
                line = line.strip().rstrip(",").lstrip("[")
                try:
                    r = json.loads("[" + line.strip("[]") + "]")
                    if len(r) >= 3: data.append(r)
                except Exception: pass
        resume = None
        body = data[1:] if data and data[0] and data[0][0] == "urlkey" else data
        if body and body[-1] and len(body[-1]) == 1:
            resume = body[-1][0]
            body = body[:-2] if len(body) >= 2 and body[-2] == [] else body[:-1]
        for r in body:
            if len(r) >= 3:
                u = r[2].split("?")[0] if cfg.get("strip_query") else r[2]
                if art.search(u) and (u not in rows or r[1] < rows[u]):
                    rows[u] = r[1]
        if not resume:
            return rows, True
        time.sleep(2)
    return rows, False


def abuali_captures():
    """All snapshot timestamps of the rolling channel page in the window."""
    raw = fetch("https://web.archive.org/cdx/search/cdx?url=t.me/s/abualiexpress"
                f"&from={WINDOW[0]}&to={WINDOW[1]}&output=text&filter=statuscode:200&limit=20000")
    ts = [l.split()[1] for l in raw.splitlines() if len(l.split()) > 2]
    return sorted(set(ts))


def main():
    outdir = DATA / "israel" / "enumeration"
    outdir.mkdir(parents=True, exist_ok=True)
    summary = []
    for name, cfg in OUTLETS.items():
        print(f"== {name}", flush=True)
        rows, complete = cdx_enumerate(cfg)
        days = Counter(v[:8] for v in rows.values())
        with (outdir / f"{name}-urls.csv").open("w", newline="", encoding="utf-8") as f:
            w = csv.writer(f); w.writerow(["url", "first_capture", "source", "event_candidate"])
            for u in sorted(rows):
                w.writerow([u, rows[u], "cdx", 0])
        peak = days.most_common(1)[0] if days else ("", 0)
        summary.append([name, len(rows), complete, peak[0], peak[1]])
        print(f"   urls={len(rows)} complete={complete} peak={peak}", flush=True)
    ts = abuali_captures()
    with (outdir / "abuali-captures.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f); w.writerow(["capture_ts", "capture_url"])
        for t in ts:
            w.writerow([t, f"https://web.archive.org/web/{t}/https://t.me/s/abualiexpress"])
    days = Counter(t[:8] for t in ts)
    summary.append(["abuali", len(ts), True, *(days.most_common(1)[0] if days else ("", 0))])
    print(f"== abuali capture-stream: {len(ts)} snapshots; days covered: {len(days)}", flush=True)
    with (outdir / "summary.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f); w.writerow(["outlet", "urls_or_captures", "cdx_complete", "peak_day", "peak_count"])
        w.writerows(summary)
    print("DONE")


if __name__ == "__main__":
    main()
