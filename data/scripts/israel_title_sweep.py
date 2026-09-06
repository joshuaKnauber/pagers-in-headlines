#!/usr/bin/env python3
"""Title sweep worker for Israel step 5.

Usage: israel_title_sweep.py <outlet> <mode:live|wayback> <shard> <nshards> [delay]
Reads data/israel/enumeration/<outlet>-urls.csv, fetches each URL's title
(live page or its first_capture Wayback snapshot), tags event candidates
by Hebrew/Arabic title terms, writes
data/israel/enumeration/<outlet>-titles-<shard>.csv.
"""
import csv, html as H, re, sys, time, urllib.request
from pathlib import Path

DATA = Path(__file__).resolve().parent.parent / "israel" / "enumeration"
UA = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) research-collection"}

STRONG = ["ביפר", "הביפר", "ביפרים", "איתורית", "איתוריות", "זימונית", "זימוניות",
          "גולד אפולו", "بيجر", "البيجر", "بيجرات", "أجهزة النداء", "اجهزة النداء", "pager", "beeper"]
RELATED = ["מכשירי קשר", "מכשירי הקשר", "ווקי טוקי", "ווקי-טוקי", "לאסלקי",
           "لاسلكي", "اللاسلكي", "ووكي", "أجهزة الاتصال", "اجهزة الاتصال", "walkie", "icom", "איקום"]


def tag(title):
    t = title.lower()
    if any(k in t for k in (s.lower() for s in STRONG)):
        return "strong"
    if any(k in t for k in (s.lower() for s in RELATED)):
        return "related"
    return ""


def get_title(url, timeout=25):
    raw = urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=timeout).read(90000)
    t = raw.decode("utf-8", "replace")
    m = re.search(r"<title>([^<]{3,300})</title>", t)
    if not m:
        m = re.search(r'property="og:title" content="([^"]{3,300})"', t)
    return H.unescape(m.group(1)).strip() if m else ""


def main():
    outlet, mode, shard, nshards = sys.argv[1], sys.argv[2], int(sys.argv[3]), int(sys.argv[4])
    delay = float(sys.argv[5]) if len(sys.argv) > 5 else 1.0
    rows = list(csv.DictReader(open(DATA / f"{outlet}-urls.csv", encoding="utf-8")))
    mine = [r for i, r in enumerate(rows) if i % nshards == shard]
    out_path = DATA / f"{outlet}-titles-{shard}.csv"
    done = set()
    if out_path.exists():
        done = {r["url"] for r in csv.DictReader(open(out_path, encoding="utf-8"))}
    f = open(out_path, "a", newline="", encoding="utf-8")
    w = csv.writer(f)
    if not done:
        w.writerow(["url", "title", "relevance", "fetch_route"])
    fails = 0
    for i, r in enumerate(mine):
        if r["url"] in done:
            continue
        target = r["url"] if mode == "live" else f"https://web.archive.org/web/{r['first_capture']}/{r['url']}"
        title, route = "", mode
        for attempt in range(2):
            try:
                title = get_title(target)
                break
            except Exception:
                time.sleep(5 if mode == "live" else 15)
        if not title:
            fails += 1
        w.writerow([r["url"], title[:250], tag(title), route])
        if (i + 1) % 100 == 0:
            f.flush()
            print(f"{outlet}#{shard}: {i+1}/{len(mine)} fails={fails}", flush=True)
        time.sleep(delay)
    f.close()
    print(f"{outlet}#{shard} DONE {len(mine)} fails={fails}", flush=True)


if __name__ == "__main__":
    main()
