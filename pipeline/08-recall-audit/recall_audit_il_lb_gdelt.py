#!/usr/bin/env python3
"""Recall audit (Israel + Lebanon): GDELT 2.0 GKG domain filter.

Independent discovery route: GDELT's own crawler (not Wayback). Streams every
15-minute GKG file (English + translingual) from the window, keeps rows whose
SourceCommonName / DocumentIdentifier belong to an audited domain, and writes
url, crawl timestamp, page title (from the Extras <PAGE_TITLE> field).

Raw GKG zips are streamed in memory and discarded (12 GB total); only the
filtered rows are kept:
  data/{israel,lebanon}/08-recall-audit/raw/gdelt-gkg-hits.csv

Usage: recall_audit_il_lb_gdelt.py [nworkers]
"""
import csv, html, io, re, sys, time, urllib.request, zipfile
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

DATA = Path(__file__).resolve().parents[2] / "data"
FROM, TO = "20240917000000", "20240926000000"   # crawl-time UTC; publication window Sep 17-24
MASTERS = ["https://data.gdeltproject.org/gdeltv2/masterfilelist-translation.txt",
           "https://data.gdeltproject.org/gdeltv2/masterfilelist.txt"]
DOMAINS = {
    "israel": ["ynet.co.il", "mako.co.il", "n12.co.il", "kikar.co.il", "makan.org.il", "kan.org.il"],
    "lebanon": ["lbcgroup.tv", "mtv.com.lb", "aljadeed.tv", "almanar.com.lb", "nna-leb.gov.lb",
                "al-akhbar.com", "nidaalwatan.com", "annahar.com", "lorientlejour.com", "lorientoday.com"],
}
csv.field_size_limit(10**9)


def get(url, tries=4):
    for i in range(tries):
        try:
            return urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": "research"}), timeout=120).read()
        except Exception as e:
            err = e
            time.sleep(5 * (i + 1))
    raise err


def files():
    out = []
    for m in MASTERS:
        cache = Path("/tmp/gd") / m.rsplit("/", 1)[1]
        txt = cache.read_text() if cache.exists() else get(m).decode()
        for line in txt.splitlines():
            p = line.split()
            if len(p) == 3 and p[2].endswith("gkg.csv.zip"):
                ts = p[2].rsplit("/", 1)[1][:14]
                if FROM <= ts < TO:
                    out.append(p[2].replace("http://", "https://"))
    return out


def scan(url):
    hits = []
    try:
        z = zipfile.ZipFile(io.BytesIO(get(url)))
    except Exception as e:
        return url, None, str(e)
    with z.open(z.namelist()[0]) as f:
        for line in io.TextIOWrapper(f, encoding="utf-8", errors="replace"):
            p = line.rstrip("\n").split("\t")
            if len(p) < 27:
                continue
            src, doc = p[3].lower(), p[4]
            for country, doms in DOMAINS.items():
                if any(d in src or d in doc.lower()[:60] for d in doms):
                    m = re.search(r"<PAGE_TITLE>(.*?)</PAGE_TITLE>", p[26], re.S)
                    title = html.unescape(m.group(1)).strip() if m else ""
                    hits.append([country, p[1], src, doc, title[:300],
                                 "translation" if ".translation." in url else "english"])
                    break
    return url, hits, ""


def main():
    nw = int(sys.argv[1]) if len(sys.argv) > 1 else 6
    fl = files()
    print(f"{len(fl)} gkg files", flush=True)
    outs = {}
    for c in DOMAINS:
        p = DATA / c / "08-recall-audit" / "raw" / "gdelt-gkg-hits.csv"
        p.parent.mkdir(parents=True, exist_ok=True)
        f = p.open("w", newline="", encoding="utf-8")
        w = csv.writer(f)
        w.writerow(["country", "gkg_date", "source", "url", "title", "stream"])
        outs[c] = (f, w)
    errs = []
    done = 0
    with ThreadPoolExecutor(nw) as ex:
        futs = [ex.submit(scan, u) for u in fl]
        for fu in as_completed(futs):
            url, hits, err = fu.result()
            done += 1
            if hits is None:
                errs.append((url, err))
            else:
                for h in hits:
                    outs[h[0]][1].writerow(h)
            if done % 100 == 0:
                for f, _ in outs.values():
                    f.flush()
                print(f"{done}/{len(fl)} errs={len(errs)}", flush=True)
    for f, _ in outs.values():
        f.close()
    with (DATA / "israel" / "08-recall-audit" / "raw" / "gdelt-errors.txt").open("w") as f:
        for u, e in errs:
            f.write(f"{u}\t{e}\n")
    print("DONE errs", len(errs))


if __name__ == "__main__":
    main()
