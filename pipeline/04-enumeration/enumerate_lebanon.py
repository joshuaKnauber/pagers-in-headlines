#!/usr/bin/env python3
"""Step 4: enumerate candidate event-window URLs per required outlet.

Sources:
  - Wayback CDX (primary): all captured URLs matching the outlet's
    *event-era* article pattern (identity findings from step 3), with
    resumeKey pagination. First-capture timestamp is kept as a rough
    publication-date proxy (day-of crawling was dense for these domains).
  - GDELT DOC API (keyword layer): event-phrase queries per domain,
    throttled to 1 request / 6 s.

Outputs (data/<country>/enumeration/):
  - <outlet>-urls.csv     url, first_capture, source, event_candidate
  - summary.csv           outlet, total_urls, event_candidates, per-day counts
Event-candidate tagging is slug-keyword based (URL-decoded) and is a
*recall aid for triage*, not a relevance verdict: numeric-URL outlets
(Al-Manar) can't be tagged from slugs and need title-level triage later.
"""
import csv
import json
import re
import sys
import time
import urllib.parse
import urllib.request
from collections import Counter, defaultdict
from pathlib import Path

DATA = Path(__file__).resolve().parents[2] / "data"
WINDOW = ("20240915", "20241017")
UA = {"User-Agent": "Mozilla/5.0 (research collection; pager-news project)"}

# Event-era article patterns per step-3 identity findings.
OUTLETS = {
    "lbci": {
        "cdx_url": "lbcgroup.tv/news", "match": "prefix",
        "article_re": r"lbcgroup\.tv/news/[^/]+/\d+/",
        "gdelt_domain": "lbcgroup.tv",
    },
    "aljadeed": {
        "cdx_url": "aljadeed.tv/news", "match": "prefix",
        "article_re": r"aljadeed\.tv/news/[^/]+/\d+/",
        "gdelt_domain": "aljadeed.tv",
    },
    "mtv": {
        "cdx_url": "mtv.com.lb", "match": "domain",
        "article_re": r"mtv\.com\.lb/(?:en/|ar/)?news/",
        "gdelt_domain": "mtv.com.lb",
    },
    "almanar": {
        "cdx_url": "almanar.com.lb", "match": "domain",
        "article_re": r"almanar\.com\.lb/\d{6,}$",
        "gdelt_domain": "almanar.com.lb",
    },
    "nna": {
        "cdx_url": "nna-leb.gov.lb", "match": "domain",
        "article_re": r"nna-leb\.gov\.lb/(?:ar|en)/[^/]+/\d{5,}/",
        "gdelt_domain": "nna-leb.gov.lb",
    },
}

# Slug keywords (lowercased, URL-decoded match). Recall aid only.
EVENT_TERMS = [
    "pager", "beeper", "بيجر", "البيجر", "بيجرز", "لاسلكي", "اللاسلكي",
    "ووكي", "توكي", "gold-apollo", "gold_apollo", "icom", "أجهزة-الاتصال",
    "اجهزة-الاتصال", "أجهزة-النداء", "اجهزة-النداء", "exploding-devices",
    "device-blasts", "hezbollah-devices",
]
GDELT_QUERIES = ['"pager"', '"%D8%AA%D9%81%D8%AC%D9%8A%D8%B1%D8%A7%D8%AA%20%D8%A7%D9%84%D8%A8%D9%8A%D8%AC%D8%B1"']


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
    for page in range(20):  # hard cap
        url = base + (f"&resumeKey={urllib.parse.quote(resume)}" if resume else "")
        for attempt in range(3):
            try:
                raw = fetch(url)
                break
            except Exception as e:
                print(f"    cdx retry {attempt+1}: {e}", file=sys.stderr)
                time.sleep(10)
        else:
            print("    cdx page failed, keeping partial", file=sys.stderr)
            return rows, False
        try:
            data = json.loads(raw)
        except json.JSONDecodeError:
            # truncated page: salvage complete lines
            data = []
            for line in raw.splitlines():
                line = line.strip().rstrip(",").lstrip("[")
                try:
                    r = json.loads("[" + line.strip("[]") + "]")
                    if len(r) >= 3:
                        data.append(r)
                except Exception:
                    pass
            print(f"    salvaged {len(data)} rows from truncated page", file=sys.stderr)
        resume = None
        body = data[1:] if data and data[0] and data[0][0] == "urlkey" else data
        if body and body[-1] and len(body[-1]) == 1:      # resumeKey trailer
            resume = body[-1][0]
            body = body[:-2] if len(body) >= 2 and body[-2] == [] else body[:-1]
        for r in body:
            if len(r) >= 3 and art.search(r[2]):
                u = r[2]
                if u not in rows or r[1] < rows[u]:
                    rows[u] = r[1]
        if not resume:
            return rows, True
        time.sleep(2)
    return rows, False


def gdelt_enumerate(domain):
    out = {}
    for q in GDELT_QUERIES:
        url = ("https://api.gdeltproject.org/api/v2/doc/doc?query={q}%20domain:{d}"
               "&mode=artlist&maxrecords=250&startdatetime={f}000000&enddatetime={t}235959"
               "&format=json").format(q=q, d=domain, f=WINDOW[0], t=WINDOW[1])
        try:
            data = json.loads(fetch(url, timeout=45))
            for a in data.get("articles", []):
                out.setdefault(a["url"], a.get("seendate", "")[:8])
        except Exception as e:
            print(f"    gdelt {domain} query failed: {e}", file=sys.stderr)
        time.sleep(6)
    return out


def main():
    outdir = DATA / "lebanon" / "04-enumeration"
    outdir.mkdir(parents=True, exist_ok=True)
    summary = []
    for name, cfg in OUTLETS.items():
        print(f"== {name}", flush=True)
        cdx, complete = cdx_enumerate(cfg)
        print(f"   cdx article urls: {len(cdx)} (complete={complete})", flush=True)
        gd = gdelt_enumerate(cfg["gdelt_domain"])
        print(f"   gdelt urls: {len(gd)}", flush=True)
        merged = {}
        for u, ts in cdx.items():
            merged[u] = {"first_capture": ts, "source": "cdx"}
        for u, d in gd.items():
            if u in merged:
                merged[u]["source"] = "cdx+gdelt"
            else:
                merged[u] = {"first_capture": d, "source": "gdelt"}
        days, cand = Counter(), 0
        with (outdir / f"{name}-urls.csv").open("w", encoding="utf-8", newline="") as f:
            w = csv.writer(f)
            w.writerow(["url", "first_capture", "source", "event_candidate"])
            for u in sorted(merged):
                info = merged[u]
                slug = urllib.parse.unquote(u).lower()
                is_cand = any(t in slug for t in EVENT_TERMS) or info["source"] != "cdx"
                cand += is_cand
                days[info["first_capture"][:8]] += 1
                w.writerow([u, info["first_capture"], info["source"], int(is_cand)])
        summary.append({
            "outlet": name, "total_urls": len(merged), "event_candidates": cand,
            "cdx_complete": complete, "gdelt_urls": len(gd),
            "peak_day": (days.most_common(1)[0] if days else ("", 0)),
        })
        print(f"   candidates: {cand}", flush=True)
    with (outdir / "summary.csv").open("w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["outlet", "total_article_urls", "event_candidates", "cdx_complete", "gdelt_urls", "peak_capture_day", "peak_count"])
        for s in summary:
            w.writerow([s["outlet"], s["total_urls"], s["event_candidates"], s["cdx_complete"], s["gdelt_urls"], s["peak_day"][0], s["peak_day"][1]])
    print("DONE")


if __name__ == "__main__":
    main()
