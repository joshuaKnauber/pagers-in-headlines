#!/usr/bin/env python3
"""Retry of the CNN live-news CDX prefix (failed during IA throttling); appends to liveblogs-cdx.csv
and liveblogs-discovered.csv for the US."""
import csv, subprocess, sys, time
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from recall_audit_common import ROOT, is_liveblog
import re
TOPIC = re.compile(r"libanon|lebanon|hisbollah|hezbollah|nahost|israel|pager|beirut|mideast|middle-east|gaza|iran", re.I)
caps = {}
for pre in ["cnn.com/world/live-news/", "cnn.com/politics/live-news/"]:
    u = (f"https://web.archive.org/cdx/search/cdx?url={pre}&matchType=prefix&from=20240917&to=20240925"
         f"&filter=statuscode:200&fl=timestamp,original&limit=100000")
    lines = None
    for a in range(6):
        p = subprocess.run(["curl", "-s", "-m", "300", u], capture_output=True)
        t = p.stdout.decode("utf-8", "replace")
        if p.returncode == 0 and not t.lstrip().startswith("<"):
            lines = t.splitlines(); break
        time.sleep(60)
    print(pre, None if lines is None else len(lines), flush=True)
    for l in lines or []:
        ts, _, o = l.partition(" ")
        o = re.sub(r"^http://", "https://", o.split("?")[0].replace(":80/", "/"))
        if TOPIC.search(o):
            caps.setdefault(o, []).append(ts)
d = ROOT / "us" / "08-recall-audit" / "raw"
with open(d / "liveblogs-cdx.csv", "a", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    for u, ts in sorted(caps.items()):
        ts = sorted(set(ts)); w.writerow(["cnn", u, len(ts), ts[0], ts[-1], " ".join(ts)])
with open(d / "liveblogs-discovered.csv", "a", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    for u in caps:
        w.writerow(["cnn", u, "", "", "wayback-cdx-liveblog-path"])
print("cnn live urls", len(caps))
