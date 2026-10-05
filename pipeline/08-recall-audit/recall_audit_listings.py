#!/usr/bin/env python3
"""Recall audit route B: outlet-native dated listings NOT used by the original enumeration.

Usage: recall_audit_listings.py [route ...]
Each route writes data/<country>/08-recall-audit/raw/listings/<route>.csv
(outlet,url,title,date,route) and keeps fetched listing HTML/XML under raw/listings/html/.
Window: 2024-09-17 .. 2024-09-24 (dates outside are kept only if the listing is dated
inside the window; filtering happens in the build step).
"""
import csv, gzip, html as H, json, re, subprocess, sys, time, datetime as dt
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2] / "data"
UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36"
DAYS = [dt.date(2024, 9, 17) + dt.timedelta(days=i) for i in range(8)]


def curl(url, ua=UA, timeout=90, minlen=300):
    for a in range(3):
        p = subprocess.run(["curl", "-sL", "--compressed", "-m", str(timeout), "-A", ua, url], capture_output=True)
        if p.returncode == 0 and len(p.stdout) > minlen and not p.stdout.lstrip().startswith(b"<html><head><title>504"):
            data = p.stdout
            if data[:2] == b"\x1f\x8b":
                data = gzip.decompress(data)
            return data.decode("utf-8", "replace")
        time.sleep(8)
    raise RuntimeError(f"fetch failed {url}")


def save(country, name, text):
    d = ROOT / country / "08-recall-audit" / "raw" / "listings" / "html"
    d.mkdir(parents=True, exist_ok=True)
    (d / name).write_text(text, encoding="utf-8")


def write(country, route, rows):
    d = ROOT / country / "08-recall-audit" / "raw" / "listings"
    d.mkdir(parents=True, exist_ok=True)
    seen, out = set(), []
    for r in rows:
        if r[1] in seen:
            continue
        seen.add(r[1]); out.append(r)
    with open(d / f"{route}.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f); w.writerow(["outlet", "url", "title", "date", "route"]); w.writerows(out)
    print(route, len(out), flush=True)


def clean(s):
    return " ".join(H.unescape(re.sub(r"<[^>]+>", " ", s or "")).split())


def tagesschau():
    rows = []
    for page in range(1, 7):
        t = curl(f"https://www.tagesschau.de/archiv?datum=2024-09-01&pageIndex={page}")
        save("germany", f"tagesschau-archiv-p{page}.html", t)
        for blk in t.split('data-teaserdate="')[1:]:
            ts = int(re.match(r"\d+", blk).group())
            m = re.search(r'href="(/[^"]+\.html)"', blk)
            h = re.search(r'teaserheadline">(.*?)</(?:p|span|h\d)>', blk, re.S) or re.search(r'headline[^>]*>(.*?)</', blk, re.S)
            tl = re.search(r'topline[^>]*>(.*?)</', blk, re.S)
            if m:
                title = clean(h.group(1)) if h else ""
                if tl and clean(tl.group(1)):
                    title = clean(tl.group(1)) + ": " + title
                rows.append(["tagesschau", "https://www.tagesschau.de" + m.group(1), title,
                             dt.datetime.fromtimestamp(ts).date().isoformat(), "tagesschau-archive"])
        time.sleep(1.5)
    write("germany", "tagesschau-archive", rows)


def spiegel():
    rows = []
    for d in DAYS:
        t = curl(f"https://www.spiegel.de/nachrichtenarchiv/artikel-{d:%d.%m.%Y}.html")
        save("germany", f"spiegel-archiv-{d}.html", t)
        for m in re.finditer(r'<article aria-label="([^"]*)"[^>]*>.*?<a href="(https://www\.spiegel\.de/[^"]+)"', t, re.S):
            rows.append(["spiegel", m.group(2), clean(m.group(1)), d.isoformat(), "spiegel-nachrichtenarchiv"])
        time.sleep(1.5)
    write("germany", "spiegel-nachrichtenarchiv", rows)


def welt():
    rows = []
    for d in DAYS:
        t = curl(f"https://www.welt.de/schlagzeilen/nachrichten-vom-{d.day}-{d.month}-{d.year}.html")
        save("germany", f"welt-schlagzeilen-{d}.html", t)
        t2 = t.replace('\\"', '"')
        for m in re.finditer(r'href="(/[a-z][^"]*/(?:article|plus|video|liveticker)\d{6,}/[^"]*\.html)"[^>]*title="([^"]*)"', t2):
            rows.append(["welt", "https://www.welt.de" + m.group(1), clean(m.group(2)), d.isoformat(), "welt-schlagzeilen"])
        for m in re.finditer(r'href="(/[a-z][^"]*/(?:article|plus|video|liveticker)\d{6,}/[^"]*\.html)"', t2):
            rows.append(["welt", "https://www.welt.de" + m.group(1), "", d.isoformat(), "welt-schlagzeilen"])
        time.sleep(1.5)
    # prefer titled rows (first occurrence kept)
    write("germany", "welt-schlagzeilen", rows)


def nyt():
    rows = []
    for d in DAYS:
        t = curl(f"https://www.nytimes.com/sitemap/{d:%Y/%m/%d}/")
        save("us", f"nyt-sitemap-{d}.html", t)
        for m in re.finditer(r'<li><a href="(https://www\.nytimes\.com/[^"]+)">(.*?)</a></li>', t):
            rows.append(["nyt", m.group(1), clean(m.group(2)), d.isoformat(), "nyt-daily-sitemap"])
        time.sleep(2)
    write("us", "nyt-daily-sitemap", rows)


def xml_sitemap(country, outlet, route, urls, datefn):
    rows = []
    for i, u in enumerate(urls):
        try:
            t = curl(u)
        except Exception as e:
            print("!!", u, e); continue
        save(country, f"{route}-{i}.xml", t)
        for m in re.finditer(r"<url>(.*?)</url>", t, re.S):
            loc = re.search(r"<loc>\s*(.*?)\s*</loc>", m.group(1))
            lm = re.search(r"<lastmod>\s*(.*?)\s*</lastmod>", m.group(1))
            if not loc:
                continue
            loc = H.unescape(loc.group(1))
            d = datefn(loc, lm.group(1) if lm else "")
            if d and "2024-09-16" <= d <= "2024-09-25":
                rows.append([outlet, loc, "", d, route])
        time.sleep(2)
    write(country, route, rows)


def ntv():
    xml_sitemap("germany", "ntv", "ntv-sitemap", ["https://www.n-tv.de/sitemap/sitemap-2024-09.xml.gz"],
                lambda u, lm: lm[:10])


def bild():
    xml_sitemap("germany", "bild", "bild-sitemap", ["https://www.bild.de/sitemap-index-202409.xml"],
                lambda u, lm: lm[:10])


def rtl():
    xml_sitemap("germany", "rtl", "rtl-sitemap", ["https://www.rtl.de/sitemap-index-2024-09.xml"],
                lambda u, lm: lm[:10])


def cnn():
    secs = ["world", "politics", "us", "business", "health", "science", "tech", "opinions", "middleeast"]
    urls = [f"https://www.cnn.com/sitemap/article/{s}/2024/09.xml" for s in secs]
    urls += [f"https://www.cnn.com/sitemap/live-story/{s}/2024/09.xml" for s in ("world", "politics", "us")]
    urls += [f"https://www.cnn.com/sitemap/video/{s}/2024/09.xml" for s in ("world", "politics")]

    def dfn(u, lm):
        m = re.search(r"/2024/(\d\d)/(\d\d)/", u)
        return f"2024-{m.group(1)}-{m.group(2)}" if m else lm[:10]
    xml_sitemap("us", "cnn", "cnn-sitemap", urls, dfn)


def rnd():
    rows = []
    for d in DAYS:
        url = f"https://web.archive.org/web/20241001000000id_/https://www.rnd.de/archiv/artikel-{d:%d-%m-%Y}/"
        p = subprocess.run(["curl", "-sL", "-m", "120", "-A", UA, "-w", "\n__EFF__%{url_effective}", url], capture_output=True)
        t, _, eff = p.stdout.decode("utf-8", "replace").rpartition("\n__EFF__")
        time.sleep(2)
        m = re.search(r"/web/(\d{14})", eff)
        if len(t) < 5000 or not m:
            print("!! rnd archive no capture", d, eff, flush=True); continue
        save("germany", f"rnd-archiv-{d}-{m.group(1)}.html", t)
        for m2 in re.finditer(r'href="((?:https://www\.rnd\.de)?/[a-z][^"]*-[A-Z0-9]{26}\.html)"[^>]*>(.*?)</a>', t, re.S):
            u = m2.group(1)
            u = u if u.startswith("http") else "https://www.rnd.de" + u
            rows.append(["rnd", u, clean(m2.group(2))[:300], d.isoformat(), "rnd-dated-archive(wayback)"])
    write("germany", "rnd-dated-archive", rows)


def fox():
    rows = []
    for pg in range(6, 45):
        try:
            t = curl(f"https://www.foxnews.com/sitemap.xml?type=articles&page={pg}")
        except Exception as e:
            print("!! fox page", pg, e); continue
        mods = re.findall(r"<lastmod>([^<]{10})", t)
        print("fox page", pg, mods[:1], mods[-1:], len(mods), flush=True)
        hit = False
        for m in re.finditer(r"<url>(.*?)</url>", t, re.S):
            loc = re.search(r"<loc>\s*(.*?)\s*</loc>", m.group(1)); lm = re.search(r"<lastmod>([^<]{10})", m.group(1))
            if loc and lm and "2024-09-16" <= lm.group(1) <= "2024-09-25":
                rows.append(["fox", H.unescape(loc.group(1)), "", lm.group(1), "fox-sitemap"]); hit = True
        if hit:
            save("us", f"fox-sitemap-p{pg}.xml", t)
        if mods and max(mods) < "2024-09-16":
            break
        time.sleep(2)
    write("us", "fox-sitemap", rows)
    rows = []
    for pg in range(1, 12):
        try:
            t = curl(f"https://www.foxnews.com/sitemap.xml?type=liveblogs" + (f"&page={pg}" if pg > 1 else ""))
        except Exception:
            break
        save("us", f"fox-liveblogs-sitemap-{pg}.xml", t)
        locs = re.findall(r"<loc>\s*(.*?)\s*</loc>", t)
        if not locs:
            break
        for u in locs:
            if re.search(r"(sept?(ember)?-(1[7-9]|2[0-4])(-2024)?$|09-(1[7-9]|2[0-4])(-24)?$)", u) and not re.search(r"-2[56]$|-(19|20)-26$", u):
                rows.append(["fox", u, "", "", "fox-liveblogs-sitemap"])
        time.sleep(2)
    write("us", "fox-liveblogs-sitemap", rows)


if __name__ == "__main__":
    for r in sys.argv[1:] or ["tagesschau", "spiegel", "welt", "nyt", "ntv", "bild", "rtl", "cnn", "rnd"]:
        try:
            globals()[r]()
        except Exception as e:
            print("!! route", r, e, flush=True)
