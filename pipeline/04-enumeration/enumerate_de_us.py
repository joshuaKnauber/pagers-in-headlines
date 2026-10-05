#!/usr/bin/env python3
"""Step-4 enumeration for Germany + US (usage: enumerate_de_us.py [germany|us|all]).

Sources per the access registers:
- cdx: time-sliced (2-day) Wayback CDX queries per outlet, restricted
  client-side to the event-era article pattern; slices retried and
  resumable (per-outlet done-file records completed slices).
- sitemap: outlet-native dated sitemaps (complete manifests + lastmod).
- bild-archive: live dated archive pages (complete daily lists).
- gdelt: keyword×domain layer for CDX-dead outlets (NYT/Yahoo/USAToday),
  6s throttle, weekly slices.

Output: data/<country>/enumeration/<outlet>-urls.csv
(url, first_capture, source, event_candidate) + summary.csv.
"""
import csv, gzip, html as H, io, json, re, sys, time, urllib.parse, urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2] / "data"
UA = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36"}
W_FROM, W_TO = "20240915", "20241017"

DE_STRONG = ["pager", "piepser", "funkger", "walkie", "gold-apollo"]
DE_CTX = ["libanon", "hisbollah", "hezbollah", "beirut"]
DE_EVT = ["explos", "detonat", "angriff", "attacke", "geraet"]
US_STRONG = ["pager", "beeper", "walkie", "gold-apollo", "icom"]
US_CTX = ["lebanon", "hezbollah", "beirut"]
US_EVT = ["explos", "blast", "detonat", "device", "attack"]


def tag(url, strong, ctx, evt):
    u = urllib.parse.unquote(url).lower()
    if any(t in u for t in strong):
        return "strong"
    if any(t in u for t in ctx) and any(t in u for t in evt):
        return "related"
    return ""


DE = {
 "tagesschau": dict(kind="cdx", target="tagesschau.de", mt="domain",
    art=r"tagesschau\.de/(inland|ausland|wirtschaft|investigativ|wissen|faktenfinder)/.*\.html$"),
 "zdfheute": dict(kind="cdx", target="zdf.de/nachrichten", mt="prefix",
    art=r"zdf\.de/nachrichten/[a-z]+/.*-1\d\d\.html$"),
 "rtl": dict(kind="cdx", target="rtl.de/news", mt="prefix",
    art=r"rtl\.de/news/.*id\d+\.html$"),
 "ntv": dict(kind="cdx", target="n-tv.de", mt="domain",
    art=r"n-tv\.de/(politik|panorama|wirtschaft|der_tag|mediathek/videos)/.*article\d+\.html$"),
 "spiegel": dict(kind="cdx", target="spiegel.de", mt="domain",
    art=r"spiegel\.de/[a-z]+/.*-a-[0-9a-f][0-9a-f-]{20,}$"),
 "welt": dict(kind="cdx", target="welt.de", mt="domain",
    art=r"welt\.de/[a-z]+.*/(article|video|liveticker)\d{6,}/"),
 "tonline": dict(kind="cdx", target="t-online.de", mt="domain",
    art=r"t-online\.de/.*/id_\d{6,}/"),
 "rnd": dict(kind="cdx", target="rnd.de", mt="domain",
    art=r"rnd\.de/[a-z]+/.*-[A-Z0-9]{26}\.html$"),
 "bild": dict(kind="bild-archive"),
 # WELT's ia_archiver block starves CDX (33 URLs) — GDELT candidate
 # supplement appended onto the same manifest
 "welt-supp": dict(kind="gdelt", domain="welt.de", append=True, file="welt-urls.csv",
    terms=['pager', 'piepser', '"walkie talkie"', 'hisbollah explosion', 'libanon pager']),
}
US = {
 "fox": dict(kind="gdelt", domain="foxnews.com"),  # IA captures Fox too sparsely for a CDX denominator; GDELT candidate layer
 "abc": dict(kind="cdx", target="abcnews.go.com", mt="domain",
    art=r"abcnews\.go\.com/[A-Za-z]+/(wireStory|story|video)?/?.*-?\d{6,10}$"),
 "cnn": dict(kind="cdx", target="cnn.com/2024", mt="prefix",
    art=r"cnn\.com/2024/(09|10)/\d\d/[a-z-]+/.*"),
 # domain-wide CDX queries on these two 504 wholesale; section prefixes are cheap
 "wapo": dict(kind="cdx", mt="prefix", targets=[
    "washingtonpost.com/world", "washingtonpost.com/national-security",
    "washingtonpost.com/politics", "washingtonpost.com/business",
    "washingtonpost.com/technology", "washingtonpost.com/investigations"],
    art=r"washingtonpost\.com/[a-z-]+/2024/(09|10)/\d\d/[a-z0-9-]+/?$"),
 "reuters": dict(kind="cdx", mt="prefix", targets=[
    "reuters.com/world", "reuters.com/business", "reuters.com/technology"],
    art=r"reuters\.com/[a-z-]+(/[a-z-]+)?/.*-2024-(09|10)-\d\d/?$"),
 "cbs": dict(kind="sitemap", urls=[
    "https://www.cbsnews.com/xml-sitemap/article-2024-09.xml",
    "https://www.cbsnews.com/xml-sitemap/article-2024-09-2.xml",
    "https://www.cbsnews.com/xml-sitemap/article-2024-10.xml",
    "https://www.cbsnews.com/xml-sitemap/article-2024-10-2.xml"]),
 "nbc": dict(kind="sitemap", urls=[
    "https://www.nbcnews.com/sitemap/nbcnews/sitemap-2024-09-article.xml",
    "https://www.nbcnews.com/sitemap/nbcnews/sitemap-2024-10-article.xml"]),
 "ap": dict(kind="sitemap", urls=[
    "https://apnews.com/ap-sitemap-202409.xml",
    "https://apnews.com/ap-sitemap-202410.xml"]),
 "nyt": dict(kind="gdelt", domain="nytimes.com"),
 "yahoo": dict(kind="gdelt", domain="news.yahoo.com"),
 "usatoday": dict(kind="gdelt", domain="usatoday.com"),
}


def fetch(url, timeout=120, binary=False):
    try:
        r = urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=timeout)
        data = r.read()
    except urllib.error.HTTPError as e:
        if e.code in (403, 429):  # CDN/TLS-fingerprint block → curl fallback
            data = _curl(url, timeout)
        else:
            raise
    if binary:
        return data
    return data.decode("utf-8", "replace")


def _curl(url, timeout):
    import subprocess
    p = subprocess.run(["curl", "-s", "-m", str(timeout), "-A", UA["User-Agent"], url],
                       capture_output=True)
    if p.returncode != 0 or not p.stdout:
        raise RuntimeError(f"curl failed rc={p.returncode}")
    return p.stdout


def slices():
    import datetime as dt
    d = dt.date(2024, 9, 15)
    end = dt.date(2024, 10, 17)
    while d <= end:
        d2 = min(d + dt.timedelta(days=1), end)
        yield d.strftime("%Y%m%d"), d2.strftime("%Y%m%d")
        d = d2 + dt.timedelta(days=1)


def cdx_outlet(name, cfg, outdir, strong, ctx, evt):
    done_f = outdir / f".{name}-slices.done"
    done = set(done_f.read_text().split()) if done_f.exists() else set()
    path = outdir / f"{name}-urls.csv"
    seen = set()
    if path.exists():
        seen = {r["url"] for r in csv.DictReader(open(path, encoding="utf-8"))}
    f = open(path, "a", newline="", encoding="utf-8")
    w = csv.writer(f)
    if not seen:
        w.writerow(["url", "first_capture", "source", "event_candidate"])
    art = re.compile(cfg["art"])
    incomplete = 0
    targets = cfg.get("targets") or [cfg["target"]]
    for a, b in slices():
        key = f"{a}-{b}"
        if key in done:
            continue
        rows, failed = [], False
        for target in targets:
            url = (f"https://web.archive.org/cdx/search/cdx?url={target}"
                   f"&matchType={cfg['mt']}&from={a}&to={b}&output=text"
                   f"&collapse=urlkey&filter=statuscode:200&fl=timestamp,original&limit=60000")
            got = None
            for attempt in range(5):
                try:
                    body = fetch(url)
                    if body.lstrip().startswith("<"):  # nginx 504 page served as HTTP 200
                        time.sleep(25)
                        continue
                    got = body.splitlines()
                    break
                except Exception as e:
                    # salvage partial body if any (IncompleteRead carries .partial)
                    part = getattr(e, "partial", None)
                    if part:
                        got = part.decode("utf-8", "replace").splitlines()[:-1]
                        incomplete += 1
                        break
                    time.sleep(25)
            if got is None:
                failed = True
                break
            rows.extend(got)
            if len(targets) > 1:
                time.sleep(2)
        if failed:
            print(f"  !! {name} slice {key} FAILED", flush=True)
            incomplete += 1
            continue
        n = 0
        for line in rows:
            p = line.split(" ", 1)
            if len(p) != 2:
                continue
            ts, orig = p
            if not art.search(orig) or orig in seen:
                continue
            seen.add(orig)
            w.writerow([orig, ts, "cdx", tag(orig, strong, ctx, evt)])
            n += 1
        done.add(key)
        done_f.write_text(" ".join(sorted(done)))
        f.flush()
        print(f"  {name} {key}: +{n} (total {len(seen)})", flush=True)
        time.sleep(3)
    f.close()
    return len(seen), incomplete == 0


def sitemap_outlet(name, cfg, outdir, strong, ctx, evt):
    path = outdir / f"{name}-urls.csv"
    rows_out, seen = [], set()
    ok = True
    for sm in cfg["urls"]:
        try:
            data = fetch(sm, binary=True)
            if sm.endswith(".gz") or data[:2] == b"\x1f\x8b":
                data = gzip.decompress(data)
            t = data.decode("utf-8", "replace")
        except Exception as e:
            print(f"  !! {name} sitemap {sm}: {e}", flush=True)
            ok = False
            continue
        locs = re.findall(r"<loc>(.*?)</loc>", t)
        mods = re.findall(r"<lastmod>(.*?)</lastmod>", t)
        mod_by_i = mods if len(mods) == len(locs) else [""] * len(locs)
        n = 0
        for u, m in zip(locs, mod_by_i):
            u = H.unescape(u.strip())
            if u in seen:
                continue
            seen.add(u)
            rows_out.append([u, m[:10].replace("-", ""), "sitemap", tag(u, strong, ctx, evt)])
            n += 1
        print(f"  {name} {sm.rsplit('/',1)[-1]}: +{n}", flush=True)
        time.sleep(2)
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["url", "first_capture", "source", "event_candidate"])
        w.writerows(rows_out)
    return len(rows_out), ok


def bild_archive(name, cfg, outdir, strong, ctx, evt):
    import datetime as dt
    path = outdir / f"{name}-urls.csv"
    rows_out, seen = [], set()
    ok = True
    d = dt.date(2024, 9, 15)
    while d <= dt.date(2024, 10, 17):
        u = f"https://www.bild.de/themen/uebersicht/archiv/archiv-82532020.bild.html?archiveDate={d.isoformat()}"
        try:
            t = fetch(u, timeout=60)
            hrefs = set(re.findall(r'href="(/[a-z0-9-]+/[^"]*?-[0-9a-f]{24}(?:\.bild\.html)?)"', t))
            hrefs |= set(re.findall(r'href="(/[a-z0-9-]+/[^"]*?-\d{6,9}\.bild\.html)"', t))
            n = 0
            for h in hrefs:
                full = "https://www.bild.de" + h.split("?")[0]
                if full in seen:
                    continue
                seen.add(full)
                rows_out.append([full, d.strftime("%Y%m%d"), "bild-archive", tag(full, strong, ctx, evt)])
                n += 1
            print(f"  bild {d}: +{n}", flush=True)
        except Exception as e:
            print(f"  !! bild {d}: {e}", flush=True)
            ok = False
        time.sleep(2)
        d += dt.timedelta(days=1)
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["url", "first_capture", "source", "event_candidate"])
        w.writerows(rows_out)
    return len(rows_out), ok


def gdelt_outlet(name, cfg, outdir, strong, ctx, evt):
    path = outdir / cfg.get("file", f"{name}-urls.csv")
    rows_out, seen = [], set()
    ok = True
    keep = []  # supplement mode: preserve existing rows (e.g. WELT's CDX URLs)
    if cfg.get("append") and path.exists():
        for r in csv.DictReader(open(path, encoding="utf-8")):
            keep.append([r["url"], r["first_capture"], r["source"], r["event_candidate"]])
            seen.add(r["url"])
    terms = cfg.get("terms", ['pager', 'beeper', '"walkie talkie"', 'hezbollah exploding', 'lebanon pagers'])
    weeks = [("20240915000000", "20240921235959"), ("20240922000000", "20240928235959"),
             ("20240929000000", "20241005235959"), ("20241006000000", "20241017235959")]
    for term in terms:
        for a, b in weeks:
            q = urllib.parse.quote(f'{term} domain:{cfg["domain"]}')
            u = (f"https://api.gdeltproject.org/api/v2/doc/doc?query={q}"
                 f"&mode=artlist&format=json&maxrecords=250&startdatetime={a}&enddatetime={b}&sort=datedesc")
            d = None
            for attempt in range(3):
                try:
                    raw = fetch(u, timeout=60).strip()
                    if not raw.startswith("{"):  # rate-limit / html notice
                        time.sleep(10); continue
                    d = json.loads(raw); break
                except Exception:
                    time.sleep(10)
            if d is None:
                print(f"  !! {name} gdelt {term} {a[:8]}: no json", flush=True)
                ok = False
                time.sleep(6); continue
            for art in d.get("articles", []):
                url = art.get("url", "")
                if not url or url in seen:
                    continue
                seen.add(url)
                ts = (art.get("seendate", "") or "")[:8]
                rows_out.append([url, ts, "gdelt", tag(url, strong, ctx, evt) or "gdelt-hit"])
            time.sleep(6)
    print(f"  {name} gdelt: +{len(rows_out)} urls (kept {len(keep)})", flush=True)
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["url", "first_capture", "source", "event_candidate"])
        w.writerows(keep + rows_out)
    return len(keep) + len(rows_out), ok


def run(country, cfgs, strong, ctx, evt, cdx_only=False):
    outdir = ROOT / country / "04-enumeration"
    outdir.mkdir(exist_ok=True)
    summary = []
    if cdx_only:
        cfgs = {k: v for k, v in cfgs.items() if v["kind"] == "cdx"}
    order = sorted(cfgs.items(), key=lambda kv: kv[1]["kind"] == "cdx")  # non-CDX first
    for name, cfg in order:
        print(f"== {country}/{name} ({cfg['kind']})", flush=True)
        fn = {"cdx": cdx_outlet, "sitemap": sitemap_outlet,
              "bild-archive": bild_archive, "gdelt": gdelt_outlet}[cfg["kind"]]
        n, complete = fn(name, cfg, outdir, strong, ctx, evt)
        summary.append([name, cfg["kind"], n, "yes" if complete else "NO"])
    with open(outdir / "summary.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["outlet", "source_kind", "urls", "complete"])
        w.writerows(summary)
    print(f"== {country} SUMMARY:", summary, flush=True)


if __name__ == "__main__":
    which = sys.argv[1] if len(sys.argv) > 1 else "all"
    cdx_only = len(sys.argv) > 2 and sys.argv[2] == "cdxonly"
    if which in ("germany", "all"):
        run("germany", DE, DE_STRONG, DE_CTX, DE_EVT, cdx_only)
    if which in ("us", "all"):
        run("us", US, US_STRONG, US_CTX, US_EVT, cdx_only)
    print("ENUM DONE", flush=True)
