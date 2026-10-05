#!/usr/bin/env python3
"""Recall audit route A: GDELT 2.0 raw GKG files (English + translingual).

Streams every 15-minute GKG file for 2024-09-17 00:00 UTC .. 2024-09-25 06:00 UTC,
keeps only rows whose SourceCommonName is one of the audited outlets' domains,
and writes them (slim columns) to data/<country>/08-recall-audit/raw/gdelt/gkg-rows.tsv.
GKG themes/locations/organisations are derived from the full article text, so
this route is independent of URL slugs and of the original enumeration routes.
Resumable (done-file). No API key; public bucket.
"""
import csv, datetime as dt, io, subprocess, sys, zipfile
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2] / "data"
DE = {"tagesschau.de", "zdf.de", "zdfheute.de", "rtl.de", "n-tv.de", "bild.de", "spiegel.de",
      "welt.de", "t-online.de", "rnd.de"}
US = {"foxnews.com", "cnn.com", "abcnews.go.com", "abcnews.com", "cbsnews.com", "nbcnews.com",
      "nytimes.com", "washingtonpost.com", "yahoo.com", "news.yahoo.com", "usatoday.com",
      "apnews.com", "reuters.com"}
OUT = {c: ROOT / c / "08-recall-audit" / "raw" / "gdelt" for c in ("germany", "us")}


def stamps():
    t = dt.datetime(2024, 9, 17, 0, 0)
    end = dt.datetime(2024, 9, 25, 6, 0)
    while t < end:
        yield t.strftime("%Y%m%d%H%M%S")
        t += dt.timedelta(minutes=15)


def one(job):
    ts, kind = job
    url = f"https://data.gdeltproject.org/gdeltv2/{ts}.{kind}.csv.zip"
    for attempt in range(3):
        p = subprocess.run(["curl", "-s", "-f", "-m", "180", url], capture_output=True)
        if p.returncode == 0 and p.stdout[:2] == b"PK":
            break
    else:
        return ts, kind, None
    z = zipfile.ZipFile(io.BytesIO(p.stdout))
    rows = []
    for line in z.read(z.namelist()[0]).decode("utf-8", "replace").split("\n"):
        c = line.split("\t")
        if len(c) < 27:
            continue
        dom = c[3].lower()
        if dom in DE or dom in US:
            # date, domain, url, V2Themes, V2Locations, V2Persons, V2Orgs, extras(title)
            rows.append(("germany" if dom in DE else "us",
                         [ts, kind, c[1], dom, c[4], c[8][:3000], c[10][:2000], c[12][:1500],
                          c[14][:1500], c[26][:600]]))
    return ts, kind, rows


def main():
    for d in OUT.values():
        d.mkdir(parents=True, exist_ok=True)
    done_f = OUT["us"] / ".done"
    done = set(done_f.read_text().split()) if done_f.exists() else set()
    jobs = [(ts, k) for ts in stamps() for k in ("gkg", "translation.gkg") if f"{ts}.{k}" not in done]
    outs = {c: open(OUT[c] / "gkg-rows.tsv", "a", encoding="utf-8", newline="") for c in OUT}
    ws = {c: csv.writer(f, delimiter="\t") for c, f in outs.items()}
    failed = []
    with ThreadPoolExecutor(4) as ex:
        for i, (ts, kind, rows) in enumerate(ex.map(one, jobs)):
            if rows is None:
                failed.append(f"{ts}.{kind}")
                continue
            for c, r in rows:
                ws[c].writerow(r)
            done.add(f"{ts}.{kind}")
            if i % 40 == 0:
                for f in outs.values():
                    f.flush()
                done_f.write_text(" ".join(sorted(done)))
                print(f"{i}/{len(jobs)} {ts} {kind}", flush=True)
    done_f.write_text(" ".join(sorted(done)))
    print("FAILED (missing in GDELT bucket or fetch error):", failed, flush=True)
    print("GDELT DONE", flush=True)


if __name__ == "__main__":
    main()
