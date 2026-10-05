#!/usr/bin/env python3
"""Recall audit route C: archived homepages + section/topic pages (Wayback), Sep 17-23 2024.

For each outlet page x target timestamp, fetch the nearest capture in raw (id_) mode,
keep it under raw/wayback-pages/, and extract same-site article links with anchor text.
Captures more than 36h from the target are discarded. <=1 request/s to archive.org.
Output: data/<country>/08-recall-audit/raw/listings/wayback-pages.csv (outlet,url,title,date,route)
"""
import csv, html as H, re, subprocess, time, datetime as dt
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2] / "data"
UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36"
TS = ["20240917170000", "20240918080000", "20240918190000", "20240919120000", "20240920120000",
      "20240921150000", "20240923120000"]
PAGES = {
 "germany": {
  "tagesschau": ["https://www.tagesschau.de/", "https://www.tagesschau.de/thema/libanon"],
  "zdfheute": ["https://www.zdf.de/nachrichten", "https://www.zdf.de/nachrichten/politik/ausland"],
  "rtl": ["https://www.rtl.de/news/"],
  "ntv": ["https://www.n-tv.de/", "https://www.n-tv.de/thema/hisbollah"],
  "bild": ["https://www.bild.de/", "https://www.bild.de/politik/ausland-und-internationales/"],
  "spiegel": ["https://www.spiegel.de/", "https://www.spiegel.de/thema/hisbollah/"],
  "welt": ["https://www.welt.de/", "https://www.welt.de/politik/ausland/"],
  "tonline": ["https://www.t-online.de/", "https://www.t-online.de/nachrichten/ausland/"],
  "rnd": ["https://www.rnd.de/", "https://www.rnd.de/politik/"],
 },
 "us": {
  "cnn": ["https://www.cnn.com/", "https://www.cnn.com/world/middleeast"],
  "fox": ["https://www.foxnews.com/", "https://www.foxnews.com/world"],
  "abc": ["https://abcnews.go.com/", "https://abcnews.go.com/International"],
  "cbs": ["https://www.cbsnews.com/", "https://www.cbsnews.com/world/"],
  "nbc": ["https://www.nbcnews.com/", "https://www.nbcnews.com/world"],
  "nyt": ["https://www.nytimes.com/", "https://www.nytimes.com/section/world/middleeast"],
  "wapo": ["https://www.washingtonpost.com/", "https://www.washingtonpost.com/world/middle-east/"],
  "yahoo": ["https://news.yahoo.com/", "https://www.yahoo.com/news/world/"],
  "usatoday": ["https://www.usatoday.com/", "https://www.usatoday.com/news/world/"],
  "ap": ["https://apnews.com/", "https://apnews.com/hub/israel-hamas-war"],
  "reuters": ["https://www.reuters.com/", "https://www.reuters.com/world/middle-east/"],
 }}
HOST = {"tagesschau": "tagesschau.de", "zdfheute": "zdf.de", "rtl": "rtl.de", "ntv": "n-tv.de",
        "bild": "bild.de", "spiegel": "spiegel.de", "welt": "welt.de", "tonline": "t-online.de",
        "rnd": "rnd.de", "cnn": "cnn.com", "fox": "foxnews.com", "abc": "abcnews.go.com",
        "cbs": "cbsnews.com", "nbc": "nbcnews.com", "nyt": "nytimes.com", "wapo": "washingtonpost.com",
        "yahoo": "yahoo.com", "usatoday": "usatoday.com", "ap": "apnews.com", "reuters": "reuters.com"}


def fetch(url):
    for a in range(3):
        p = subprocess.run(["curl", "-sL", "-m", "90", "-A", UA, "-w", "\n__EFF__%{url_effective}", url],
                           capture_output=True)
        out = p.stdout.decode("utf-8", "replace")
        body, _, eff = out.rpartition("\n__EFF__")
        if p.returncode == 0 and len(body) > 2000 and "504 Gateway" not in body[:500]:
            return body, eff
        time.sleep(60)
    return None, None


def main():
    import sys
    global TS
    only = [a for a in sys.argv[1:] if not a.startswith("--")] or list(PAGES)
    if "us" in only and len(only) == 1 and "--offline" not in sys.argv:
        TS = ["20240917200000", "20240918200000", "20240920120000"]  # reduced (IA throttling)
    for country, outlets in PAGES.items():
        if country not in only:
            continue
        d = ROOT / country / "08-recall-audit" / "raw" / "wayback-pages"
        d.mkdir(parents=True, exist_ok=True)
        rows = []
        for outlet, pages in outlets.items():
            host = HOST[outlet]
            for page in pages:
                got = set()
                prefix = re.sub(r"[^a-z0-9]+", "_", page.split("//")[1].lower())[:60] + "-"
                existing = {f.name[len(prefix):len(prefix) + 14]: f for f in d.glob(prefix + "*.html")}
                for ts in TS:
                    t0 = dt.datetime.strptime(ts, "%Y%m%d%H%M%S")
                    reuse = [c for c in existing if c.isdigit() and
                             abs((dt.datetime.strptime(c, "%Y%m%d%H%M%S") - t0).total_seconds()) < 12 * 3600]
                    if reuse:
                        body = existing[reuse[0]].read_text(encoding="utf-8")
                        eff = f"https://web.archive.org/web/{reuse[0]}id_/{page}"
                    elif "--offline" in sys.argv:  # re-extract links from cached captures only
                        body, eff = None, None
                    else:
                        body, eff = fetch(f"https://web.archive.org/web/{ts}id_/{page}")
                        time.sleep(2.0)
                    if not body:
                        print("!! nofetch", outlet, page, ts, flush=True); continue
                    m = re.search(r"/web/(\d{14})", eff or "")
                    cap = m.group(1) if m else ""
                    if not cap or cap in got:
                        continue
                    t0, t1 = dt.datetime.strptime(ts, "%Y%m%d%H%M%S"), dt.datetime.strptime(cap, "%Y%m%d%H%M%S")
                    if abs((t1 - t0).total_seconds()) > 36 * 3600:
                        print("  far capture", outlet, page, ts, cap, flush=True); continue
                    got.add(cap)
                    fn = re.sub(r"[^a-z0-9]+", "_", page.split("//")[1].lower())[:60] + f"-{cap}.html"
                    (d / fn).write_text(body, encoding="utf-8")
                    n = 0
                    for a in re.finditer(r'<a\b[^>]*?href="([^"#]+)"[^>]*>(.*?)</a>', body, re.S):
                        href = H.unescape(a.group(1))
                        href = re.sub(r"^https?://web\.archive\.org/web/\d+(id_)?/", "", href)
                        if href.startswith("//"):  # protocol-relative link (Fox): was mangled to host//host/
                            href = "https:" + href
                        elif href.startswith("/"):
                            href = page.split("/", 3)[0] + "//" + page.split("/")[2] + href
                        if host not in href.split("/")[2] if href.startswith("http") else True:
                            continue
                        text = " ".join(H.unescape(re.sub(r"<[^>]+>", " ", a.group(2))).split())
                        if len(text) < 15 and len(href) < 60:
                            continue
                        # ABC story URLs carry their only stable ID in ?id=NNN: keep it
                        mid = re.search(r"[?&]id=(\d+)", href) if "abcnews" in href else None
                        clean_href = href.split("?")[0].split("#")[0] + (f"?id={mid.group(1)}" if mid else "")
                        rows.append([outlet, clean_href, text[:300], cap[:8],
                                     f"wayback-page:{page.split('//')[1]}@{cap}"])
                        n += 1
                    print(outlet, page, cap, n, flush=True)
        with open(ROOT / country / "08-recall-audit" / "raw" / "listings" / "wayback-pages.csv", "w",
                  newline="", encoding="utf-8") as f:
            w = csv.writer(f); w.writerow(["outlet", "url", "title", "date", "route"]); w.writerows(rows)
        print("DONE", country, len(rows), flush=True)


if __name__ == "__main__":
    main()
