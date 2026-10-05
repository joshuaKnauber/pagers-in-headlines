#!/usr/bin/env python3
"""Recall audit route D: live-blog discovery via Wayback CDX prefix queries on live-blog paths
(Sep 17-25 2024), keeping every capture timestamp (needed for timestamped re-collection).
Also scans the original manifests for live-blog-shaped URLs (not independent; flagged).
Output: data/<country>/08-recall-audit/raw/liveblogs-cdx.csv (outlet,url,captures,first,last)
        data/<country>/08-recall-audit/raw/liveblogs-discovered.csv (pool input)
"""
import csv, re, subprocess, sys, time
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from recall_audit_common import ROOT, is_liveblog, outlet_of, LIVE_RE

PREFIXES = {
 "germany": ["tagesschau.de/newsticker/", "zdf.de/nachrichten/politik/ausland/", "rtl.de/cms/stories/",
             "n-tv.de/politik/", "bild.de/news/ausland/", "bild.de/politik/ausland/",
             "spiegel.de/ausland/", "welt.de/politik/ausland/liveticker", "t-online.de/nachrichten/ausland/",
             "rnd.de/politik/"],
 "us": ["cnn.com/world/live-news/", "cnn.com/politics/live-news/", "foxnews.com/live-news/",
        "abcnews.go.com/International/live-updates/", "abcnews.go.com/live-updates/",
        "cbsnews.com/live-updates/", "nbcnews.com/news/world/live-blog/", "apnews.com/live/",
        "washingtonpost.com/world/2024/09/", "usatoday.com/story/news/world/2024/09/",
        "reuters.com/world/middle-east/", "reuters.com/world/live"],
}
TOPIC = re.compile(r"libanon|lebanon|hisbollah|hezbollah|nahost|israel|pager|beirut|mideast|middle-east|gaza|iran", re.I)


def cdx(prefix):
    u = (f"https://web.archive.org/cdx/search/cdx?url={prefix}&matchType=prefix&from=20240917&to=20240925"
         f"&filter=statuscode:200&fl=timestamp,original&limit=200000")
    for a in range(5):
        p = subprocess.run(["curl", "-s", "-m", "300", u], capture_output=True)
        t = p.stdout.decode("utf-8", "replace")
        if p.returncode == 0 and not t.lstrip().startswith("<"):
            return t.splitlines()
        time.sleep(20)
    return None


def main():
    for country, prefs in PREFIXES.items():
        caps = defaultdict(list)
        failed = []
        for pre in prefs:
            lines = cdx(pre)
            time.sleep(2)
            if lines is None:
                failed.append(pre); print("!! failed", pre, flush=True); continue
            n = 0
            for l in lines:
                ts, _, orig = l.partition(" ")
                o = orig.split("?")[0].split("#")[0].replace(":80/", "/")
                if is_liveblog(o) and TOPIC.search(o):
                    caps[re.sub(r"^http://", "https://", o)].append(ts)
                    n += 1
            print(country, pre, len(lines), "live-captures", n, flush=True)
        d = ROOT / country / "08-recall-audit" / "raw"
        with open(d / "liveblogs-cdx.csv", "w", newline="", encoding="utf-8") as f:
            w = csv.writer(f); w.writerow(["outlet", "url", "n_captures", "first", "last", "captures"])
            for u, ts in sorted(caps.items()):
                ts = sorted(set(ts))
                w.writerow([outlet_of(country, u), u, len(ts), ts[0], ts[-1], " ".join(ts)])
        # manifest scan (non-independent)
        rows = []
        for f in (ROOT / country / "04-enumeration").glob("*-urls.csv"):
            for r in csv.DictReader(open(f, encoding="utf-8")):
                fc = (r.get("first_capture") or "")[:8]
                if is_liveblog(r["url"]) and TOPIC.search(r["url"]) and (not fc or "20240916" <= fc <= "20240925"):
                    rows.append([outlet_of(country, r["url"]), r["url"], "", "", "manifest-liveblog-scan"])
        for u, ts in caps.items():
            rows.append([outlet_of(country, u), u, "", "", "wayback-cdx-liveblog-path"])
        with open(d / "liveblogs-discovered.csv", "w", newline="", encoding="utf-8") as f:
            w = csv.writer(f); w.writerow(["outlet", "url", "title", "date", "route"]); w.writerows(rows)
        print(country, "liveblog urls", len(caps), "manifest-scan", len(rows) - len(caps), "failed", failed, flush=True)


if __name__ == "__main__":
    main()
