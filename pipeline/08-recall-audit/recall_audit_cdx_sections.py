#!/usr/bin/env python3
"""Recall audit route E (NOT independent for WaPo/Reuters: same CDX-prefix mechanism as the
original enumeration, re-run with narrow per-day prefixes to test whether the original
/world failure hid content). Output: data/us/08-recall-audit/raw/listings/cdx-sections-rerun.csv
"""
import csv, re, subprocess, time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2] / "data"
PREFIXES = [f"washingtonpost.com/world/2024/09/{d}/" for d in range(17, 25)] + \
           [f"washingtonpost.com/national-security/2024/09/{d}/" for d in range(17, 25)] + \
           [f"washingtonpost.com/politics/2024/09/{d}/" for d in range(17, 25)] + \
           [f"washingtonpost.com/opinions/2024/09/{d}/" for d in range(17, 25)] + \
           [f"washingtonpost.com/technology/2024/09/{d}/" for d in range(17, 25)]
REUTERS = ["reuters.com/world/middle-east/", "reuters.com/world/", "reuters.com/technology/", "reuters.com/business/"]


def cdx(prefix, frm="20240917", to="20240925"):
    u = (f"https://web.archive.org/cdx/search/cdx?url={prefix}&matchType=prefix&from={frm}&to={to}"
         f"&filter=statuscode:200&collapse=urlkey&fl=timestamp,original&limit=50000")
    for a in range(4):
        p = subprocess.run(["curl", "-s", "-m", "300", u], capture_output=True)
        t = p.stdout.decode("utf-8", "replace")
        if p.returncode == 0 and not t.lstrip().startswith("<"):
            return t.splitlines()
        time.sleep(45)
    return None


rows, failed = [], []
for pre in PREFIXES + REUTERS:
    lines = cdx(pre)
    time.sleep(3)
    if lines is None:
        failed.append(pre); print("!! failed", pre, flush=True); continue
    n = 0
    for l in lines:
        ts, _, orig = l.partition(" ")
        o = orig.split("?")[0]
        if "reuters.com" in o and not re.search(r"-2024-09-(1[6-9]|2[0-5])/?$", o):
            continue
        outlet = "wapo" if "washingtonpost" in o else "reuters"
        rows.append([outlet, re.sub(r"^http://", "https://", o.replace(":80/", "/")), "", ts[:4] + "-" + ts[4:6] + "-" + ts[6:8],
                     "cdx-section-rerun"])
        n += 1
    print(pre, len(lines), n, flush=True)
seen, out = set(), []
for r in rows:
    if r[1] not in seen:
        seen.add(r[1]); out.append(r)
with open(ROOT / "us" / "08-recall-audit" / "raw" / "listings" / "cdx-sections-rerun.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f); w.writerow(["outlet", "url", "title", "date", "route"]); w.writerows(out)
print("DONE", len(out), "failed", failed, flush=True)
