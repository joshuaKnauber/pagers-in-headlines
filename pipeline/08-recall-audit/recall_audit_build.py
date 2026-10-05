#!/usr/bin/env python3
"""Recall audit build. Usage: recall_audit_build.py <germany|us> <pool|verify|report>

pool   : merge all independent discovery routes into raw/pool.csv (topic-filtered, window-ish),
         attach our-data status (corpus / candidates / manifest) by URL key + fuzzy title.
verify : fetch bodies for pool items (our raw HTML first; else live / Wayback), decide
         substantive mention + central, best publication date. Cache: raw/verify-cache.jsonl,
         fetched HTML under raw/pages/.
report : reference-set.csv, gap-manifest.csv, raw/recall-table.csv.
"""
import csv, difflib, html as H, hashlib, json, re, subprocess, sys, time, threading, urllib.parse
from collections import Counter, defaultdict
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from recall_audit_common import *  # noqa

UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36"
GOOGLEBOT = "Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)"
TOPIC = re.compile(r"libanon|hisbollah|hezbollah|lebanon|lebanese|beirut|nasrallah|pager|piepser|funkger|walkie|"
                   r"beeper|nahost|israel|mossad|mideast|middle.east|netanjahu|netanyahu|gallant|galant|"
                   r"gold.apollo|explosion|exploding|explodier", re.I)
WAYBACK_PRIMARY = {"rnd", "abc", "wapo", "reuters", "nyt", "ap"}


def RA(country):
    return ROOT / country / "08-recall-audit"


def url_date(u):
    m = re.search(r"/(20\d\d)/(\d\d)/(\d\d)/", u) or re.search(r"-(20\d\d)-(\d\d)-(\d\d)/?$", u)
    return f"{m.group(1)}-{m.group(2)}-{m.group(3)}" if m else ""


# ---------------------------------------------------------------- pool
def lb_parent(u):
    """Collapse live-blog entry permalinks / API fragments to the parent blog URL."""
    u = u.split("?")[0].split("#")[0]
    u = re.sub(r"/(API|v1\.\d+|--grid-columns|[a-zA-Z]+\.(link|image|url))/?$", "/", u)
    m = re.match(r"(https?://[^/]+/(?:International/)?live-updates/[^/]+)/", u)
    if m:
        return m.group(1) + "/"
    return u


def pool(country):
    ra = RA(country)
    rows = []  # outlet,url,title,date,route
    # A. Media Cloud full-text (pager terms) -> mention candidates
    for f in (ra / "raw" / "mediacloud").glob("pager-*.json"):
        d = json.load(open(f))
        for s in d["stories"]:
            o = outlet_of(country, s["url"])
            rows.append([o, s["url"], s.get("title") or "", (s.get("publish_date") or "")[:10], "mediacloud"])
    # B. GDELT GKG (body-derived locations/orgs + title)
    g = ra / "raw" / "gdelt" / "gkg-rows.tsv"
    if g.exists():
        csv.field_size_limit(10 ** 9)
        for c in csv.reader(open(g, encoding="utf-8"), delimiter="\t"):
            if len(c) < 10:
                continue
            ts, kind, date, dom, url, themes, locs, pers, orgs, extras = c[:10]
            o = outlet_of(country, url)
            if not o:
                continue
            tm = re.search(r"<PAGE_TITLE>(.*?)</PAGE_TITLE>", extras)
            title = tm.group(1) if tm else ""
            lebanon = "#Lebanon#" in locs or "#LE#" in locs
            hez = re.search(r"hezbollah|hisbollah", orgs, re.I)
            if lebanon or hez or TOPIC.search(title + " " + url):
                rows.append([o, url, title, f"{date[:4]}-{date[4:6]}-{date[6:8]}", "gdelt-gkg"])
    # C. dated listings / sitemaps / archived pages
    for f in (ra / "raw" / "listings").glob("*.csv"):
        for r in csv.DictReader(open(f, encoding="utf-8")):
            if TOPIC.search((r["title"] or "") + " " + urllib.parse.unquote(r["url"])):
                o = outlet_of(country, r["url"])
                rows.append([o, r["url"], r["title"], r["date"], r["route"]])
    # D. live-blog discovery (codex web search + manual), file raw/liveblogs-discovered.csv
    lb = ra / "raw" / "liveblogs-discovered.csv"
    if lb.exists():
        for r in csv.DictReader(open(lb, encoding="utf-8")):
            rows.append([r["outlet"], lb_parent(r["url"]), r["title"], r["date"], r["route"]])
    # merge by key
    merged = {}
    for o, u, t, d, route in rows:
        if re.match(r"^\d{8}", d or ""):
            d = f"{d[:4]}-{d[4:6]}-{d[6:8]}"
        if not u.startswith("http") or not o:
            continue
        k = key(u)
        m = merged.setdefault(k, dict(outlet=o, url=u, title="", date="", routes=set(), key=k))
        m["routes"].add(route.split("@")[0] if route.startswith("wayback-page") else route)
        t = H.unescape(H.unescape(t or "")).strip()
        if t and (not m["title"] or route == "mediacloud"):
            m["title"] = t
        if d and (not m["date"] or route == "mediacloud"):
            m["date"] = d
        if "mediacloud" == route:
            m["url"] = u
    # window-ish prefilter (exact window decided after verification)
    out = []
    for m in merged.values():
        d = m["date"] or url_date(m["url"])
        if d and not ("2024-09-16" <= d[:10] <= "2024-09-25"):
            continue
        if re.search(r"\.(jpg|png|pdf|mp4)$|/(tag|tags|topic|topics|thema|themen|category|section|hub|author|autor|news-event)/",
                     m["url"], re.I) and not is_liveblog(m["url"], m["title"]):
            continue
        if re.match(r"^https?://[^/]+/[A-Za-z-]+/?$", m["url"]) and not is_liveblog(m["url"], m["title"]):
            continue  # one-segment section/landing page (e.g. washingtonpost.com/israel-hamas-war/)
        out.append(m)
    corpus, cands, manifest = load_ours(country)
    ctitles = defaultdict(list)
    for k, r in corpus.items():
        ctitles[r["source"]["page_publisher"]].append((norm_title(r["content"]["headline"]), "corpus", k))
    for k, r in cands.items():
        ctitles[r["outlet"]].append((norm_title(r.get("title")), "cand", k))
    with open(ra / "raw" / "pool.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["outlet", "url", "key", "title", "date", "routes", "our_corpus_key", "our_cand_key",
                    "manifest_hit", "match_method"])
        for m in sorted(out, key=lambda x: (x["outlet"], x["date"], x["url"])):
            k = m["key"]
            ck = k if k in corpus else ""
            dk = k if k in cands else ""
            mm = "url-key" if (ck or dk) else ""
            if not (ck or dk) and m["title"]:
                nt = norm_title(m["title"])
                best = (0, None, None)
                for t, kind, kk in ctitles[m["outlet"]]:
                    if t:
                        r_ = difflib.SequenceMatcher(None, nt, t).ratio()
                        if r_ > best[0]:
                            best = (r_, kind, kk)
                if best[0] >= 0.9:
                    mm = f"fuzzy-title:{best[0]:.2f}"
                    if best[1] == "corpus":
                        ck = best[2]
                    if best[2] in cands:
                        dk = best[2]
            mh = manifest.get(k)
            w.writerow([m["outlet"], m["url"], k, m["title"], m["date"], ";".join(sorted(m["routes"])),
                        ck, dk, f"{mh[0]}|{mh[2] or 'untagged'}|{mh[3]}" if mh else "", mm])
    print(country, "pool", len(out), Counter(m["outlet"] for m in out))


# ---------------------------------------------------------------- verify
_wb_lock = threading.Lock()
_wb_last = [0.0]
_host_last = defaultdict(float)
_host_lock = defaultdict(threading.Lock)


def curl(url, ua=UA, timeout=60):
    p = subprocess.run(["curl", "-sL", "--compressed", "-m", str(timeout), "-A", ua,
                        "-H", "Accept-Language: de-DE,de;q=0.9,en;q=0.8",
                        "-w", "\n__META__%{http_code} %{url_effective}", url], capture_output=True)
    out = p.stdout.decode("utf-8", "replace")
    body, _, metaline = out.rpartition("\n__META__")
    code, _, eff = metaline.partition(" ")
    return body, code, eff


_ia_down_until = [0.0]


def wayback(url, ts="20240920000000"):
    if time.time() < _ia_down_until[0]:
        return None, "", "ia-refusing"
    with _wb_lock:
        wait = _wb_last[0] + 2.0 - time.time()
        if wait > 0:
            time.sleep(wait)
        _wb_last[0] = time.time()
    for attempt in range(3):
        body, code, eff = curl(f"https://web.archive.org/web/{ts}id_/{url}", timeout=90)
        if code == "200" and "<title>504" not in body[:300] and len(body) > 1500:
            m = re.search(r"/web/(\d{14})", eff)
            return body, (m.group(1) if m else ""), eff
        if code in ("404", "403"):
            return None, "", code
        if code == "000":  # connection refused = IA rate-limit penalty
            if "--patient" in sys.argv and attempt < 2:
                time.sleep(120)
                with _wb_lock:
                    _wb_last[0] = time.time()
                continue
            _ia_down_until[0] = time.time() + (0 if "--patient" in sys.argv else 600)
            return None, "", "ia-refusing"
        time.sleep(6)
        with _wb_lock:
            _wb_last[0] = time.time()
    return None, "", code


def live(url, outlet):
    host = urllib.parse.urlsplit(url).netloc
    with _host_lock[host]:
        wait = _host_last[host] + 1.0 - time.time()
        if wait > 0:
            time.sleep(wait)
        _host_last[host] = time.time()
        ua = GOOGLEBOT if outlet == "yahoo" else UA
        if outlet == "zdfheute":
            url = url.replace("://www.zdf.de/nachrichten/", "://www.zdfheute.de/")
        return curl(url, ua=ua)


BAD = re.compile(r"<title>\s*(Just a moment|Access Denied|Seite nicht gefunden|Diese Seite wurde leider nicht gefunden|"
                 r"Page not found|404|Error|Attention Required|Ihre Datenschutzeinstellungen|Yahoo News\s*</title>|"
                 r"Latest World & National News)", re.I)


def page_ok(body, code, eff, url):
    if not body or code not in ("200",) or len(body) < 3000 or BAD.search(body[:6000]):
        return False
    pu, pe = urllib.parse.urlsplit(url), urllib.parse.urlsplit(eff or url)
    if len(pe.path.strip("/")) < 3 and len(pu.path.strip("/")) > 3:  # redirected to homepage
        return False
    return True


def verify_one(country, row, ours):
    corpus, cands = ours
    outlet, url = row["outlet"], row["url"]
    res = dict(key=row["key"], outlet=outlet, url=url)
    html, src, cap = None, "", ""
    # 1. our own raw HTML
    for k in (row["our_corpus_key"], row["our_cand_key"]):
        r = corpus.get(k) if k in corpus else None
        rp = (r["capture"]["raw_path"] if r else "") or (cands.get(k, {}).get("raw_path") if k in cands else "")
        if rp and (ROOT / country / rp).exists():
            t = (ROOT / country / rp).read_text(encoding="utf-8", errors="replace")
            if not BAD.search(t[:6000]) and len(t) > 3000:
                html, src = t, f"our-raw:{rp}"
                break
    # 2. live then wayback (or wayback first for wayback-primary outlets)
    tried = []
    lbrow = is_liveblog(url, row.get("title", "")) and not is_wire_feed(url)
    if html is None:
        order = ["wayback", "live"] if outlet in WAYBACK_PRIMARY else ["live", "wayback"]
        if lbrow:
            order = ["wayback"]  # rolling live blogs: today's live page shows other content
        for how in order:
            if how == "live":
                b, code, eff = live(url, outlet)
                tried.append(f"live:{code}")
                if page_ok(b, code, eff, url):
                    html, src = b, "live"
                    break
            else:
                if outlet == "yahoo" and "mediacloud" not in row["routes"]:
                    tried.append("wayback:skipped(yahoo non-MC item)")
                    continue
                tgts = ["20240920000000"]
                if lbrow:
                    caps = sorted(ts_ for ts_ in LBCAPS.get(country, {}).get(row["key"], []) if "20240917180000" <= ts_ <= "20240925000000")
                    tgts = []
                    for goal in (202409191200, 202409211200, 202409241200):
                        if caps:
                            c_ = min(caps, key=lambda x: abs(int(x[:12]) - goal))
                            if c_ not in tgts:
                                tgts.append(c_)
                    tgts = tgts or ["20240919120000"]
                b = None
                for tgt in tgts:
                    b_, ts_, eff_ = wayback(url, tgt)
                    tried.append(f"wayback:{ts_ or eff_}")
                    if lbrow and ts_ and ts_[:8] > "20240926":
                        tried.append("capture-outside-window")
                        continue
                    if b_:
                        b, ts, eff = b_, ts_, eff_
                        if not lbrow or assess(extract(b_), country)[0]:
                            break
                if b is None:
                    continue
                if b and page_ok(b, "200", eff.split("/", 5)[-1] if eff else url, url):
                    html, src, cap = b, "wayback", ts
                    break
        if html is not None and src in ("live", "wayback"):
            d = RA(country) / "raw" / "pages" / outlet
            d.mkdir(parents=True, exist_ok=True)
            fn = d / (hashlib.sha256(url.encode()).hexdigest()[:16] + (f"-{cap}" if cap else "-live") + ".html")
            fn.write_text(html, encoding="utf-8")
            res["raw_file"] = str(fn.relative_to(ROOT / country))
    res["fetch"] = src or "FAILED"
    res["tried"] = " ".join(tried)
    res["capture_ts"] = cap
    if html is None:
        return res
    ex = extract(html)
    mention, central, ev, note = assess(ex, country)
    res.update(page_title=ex["title"][:300], page_date=ex["date"][:10], body_words=len(ex["body"].split()),
               body_src=ex["body_src"], mention=mention, central=central, evidence=ev, assess_note=note,
               live_ld=ex["live_ld"])
    return res


LBCAPS = {}


def load_lbcaps(country):
    f = RA(country) / "raw" / "liveblogs-cdx.csv"
    d = {}
    if f.exists():
        for r in csv.DictReader(open(f, encoding="utf-8")):
            d.setdefault(key(lb_parent(r["url"])), []).extend(r["captures"].split())
    LBCAPS[country] = d
    return d


def verify(country):
    load_lbcaps(country)
    ra = RA(country)
    cache_f = ra / "raw" / "verify-cache.jsonl"
    done = {}
    if cache_f.exists():
        for l in open(cache_f, encoding="utf-8"):
            r = json.loads(l)
            done[r["key"]] = r
    rows = [r for r in csv.DictReader(open(ra / "raw" / "pool.csv", encoding="utf-8"))]
    todo = [r for r in rows if r["key"] not in done or
            ("--liveblogs" in sys.argv and is_liveblog(r["url"], r["title"]) and not is_wire_feed(r["url"])
             and (done[r["key"]].get("fetch") == "live" or (done[r["key"]].get("capture_ts") or "9") < "20240917180000"
                  or (done[r["key"]].get("fetch") == "wayback" and not done[r["key"]].get("mention")
                      and not (r["outlet"] == "tagesschau" and (done[r["key"]].get("page_date") or "9") < "2024-09-16")
                      and (done[r["key"]].get("page_date") or "9") >= "2024-06-01"))) or done[r["key"]].get("fetch") == "FAILED" and ("--retry" in sys.argv or "ia-refusing" in done[r["key"]].get("tried", "") or "wayback:000" in done[r["key"]].get("tried", ""))]
    corpus, cands, _ = load_ours(country)
    print(country, "verify todo", len(todo), "of", len(rows), flush=True)
    out = open(cache_f, "a", encoding="utf-8")
    lock = threading.Lock()
    n = [0]

    def job(r):
        try:
            res = verify_one(country, r, (corpus, cands))
        except Exception as e:
            res = dict(key=r["key"], outlet=r["outlet"], url=r["url"], fetch="FAILED", tried=f"exc:{e}")
        with lock:
            out.write(json.dumps(res, ensure_ascii=False) + "\n"); out.flush()
            n[0] += 1
            if n[0] % 25 == 0:
                print(" verified", n[0], flush=True)
    # live-first outlets in a parallel pool (per-host 1 req/s); Wayback-primary outlets in a
    # single-thread pool so IA backoffs never starve the live work
    byo = defaultdict(list)
    for r in todo:
        byo[r["outlet"]].append(r)
    rr = []
    live_o = [o for o in byo if o not in WAYBACK_PRIMARY]
    while any(byo[o] for o in live_o):
        for o in live_o:
            if byo[o]:
                rr.append(byo[o].pop(0))
    wbo = [o for o in byo if o in WAYBACK_PRIMARY]
    # priority inside each outlet: Media Cloud hits and attack-term titles first
    for o in wbo:
        byo[o].sort(key=lambda r: (0 if "mediacloud" in r["routes"] else 1 if has_mention(r["title"], country) else 2))
    wb = []
    while any(byo[o] for o in wbo):
        for o in wbo:
            if byo[o]:
                wb.append(byo[o].pop(0))
    with ThreadPoolExecutor(6) as ex1, ThreadPoolExecutor(1) as ex2:
        f1 = ex1.map(job, rr)
        f2 = ex2.map(job, wb)
        list(f1); list(f2)
    out.close()


# ---------------------------------------------------------------- report
INDEPENDENT = {  # routes that share no discovery mechanism with the outlet's original route
 "mediacloud": lambda o: True,
 "gdelt-gkg": lambda o: not ORIGINAL_ROUTE[o].startswith("gdelt"),
}


def route_independent(route, outlet):
    if route in INDEPENDENT:
        return INDEPENDENT[route](outlet)
    if route in ("manifest-liveblog-scan", "cdx-section-rerun"):
        return False
    if route.startswith("wayback-page") or route == "wayback-cdx-liveblog-path":
        return True  # link/topic-based, not slug-keyword based (still Wayback-dependent)
    return True  # outlet-native listings not used originally


def drop_reason(c):
    t = (c.get("title") or "")
    rel = c.get("relevance")
    if rel == "no-capture":
        return "no Wayback capture found via availability API at extraction"
    if "Just a moment" in t:
        return "fetch returned Cloudflare challenge page (body empty) -> relevance none"
    if "Access Denied" in t:
        return "Wayback capture used was an Akamai 'Access Denied' page -> relevance none"
    if "nicht gefunden" in t or "Latest World & National News" in t or t.strip() in ("Yahoo News",):
        return "live URL 404/redirected to section page at extraction -> relevance none"
    if rel == "none":
        if (c.get("body_words") or 0) < 400 and c.get("outlet") in ("spiegel", "welt", "bild", "wapo", "nyt"):
            return f"no event term in extracted body ({c.get('body_words')} words; likely paywall teaser) -> relevance none"
        return f"no event term in extracted body ({c.get('body_words')} words) -> relevance none"
    if rel in ("strong", "related"):
        pub = c.get("published_at", "")
        if pub and not ("2024-09-01" <= pub[:10] <= "2024-10-31"):
            return f"dropped as out-of-window (extracted date {pub[:10]})"
        return "relevant candidate but absent from corpus (normalize filter: landing page / dedup)"
    return f"relevance={rel}"


def page_path(country, v):
    hp = v["fetch"].split(":", 1)[1] if v.get("fetch", "").startswith("our-raw:") else v.get("raw_file", "")
    return (ROOT / country / hp) if hp and (ROOT / country / hp).exists() else None


def boilerplate(country, pool_rows, ver):
    """Paragraphs that recur on >=3 fetched pages of one outlet with different titles are site chrome
    (teaser cards, video playlists, 'latest' boxes). Seen in the US audit: ABC live-updates shells all
    carry the teaser 'Israel had hand in manufacturing pagers...', NYT video pages carry a playlist
    item 'Heightened Anxiety in Lebanon After Wireless Device Explosions'. Returns ({outlet: set(sig)}, extracted)."""
    exs, pages, titles, words = {}, defaultdict(set), defaultdict(set), {}
    for k, p in pool_rows.items():
        v = ver.get(k, {})
        if v.get("fetch") in (None, "FAILED"):
            continue
        fp = page_path(country, v)
        if not fp:
            continue
        ex = extract(fp.read_text(encoding="utf-8", errors="replace"))
        exs[k] = ex
        if ex["body_src"] == "ld-json":
            continue
        tid = norm_title(ex["title"])[:30] or k
        for _, nonlink in ex["paras"]:
            sig = para_sig(nonlink)
            if len(sig.split()) >= 4:
                pages[(p["outlet"], sig)].add(k)
                titles[(p["outlet"], sig)].add(tid)
                words[(p["outlet"], sig)] = max(words.get((p["outlet"], sig), 0), len(nonlink.split()))
    bp = defaultdict(set)
    for (o, sig), ts in titles.items():
        # >=3 differently titled pages, or >=2 for short headline-like lines (teaser cards).
        # Long prose paragraphs are never chrome: ntv "Der Tag" entries reuse the same dpa paragraph
        # (e.g. Nasrallah's "alle roten Linien" quote, ~55 words) across several pages as real body text.
        nw = words[(o, sig)]  # full paragraph length; sig itself is cut at 160 characters
        if (len(ts) >= 3 and nw <= 35) or (len(ts) >= 2 and nw <= 20 and not sig.rstrip().endswith(".")):
            bp[o].add(sig)
    return bp, exs


def report(country):
    ra = RA(country)
    pool_rows = {r["key"]: r for r in csv.DictReader(open(ra / "raw" / "pool.csv", encoding="utf-8"))}
    ver = {}
    for l in open(ra / "raw" / "verify-cache.jsonl", encoding="utf-8"):
        r = json.loads(l)
        ver[r["key"]] = r
    corpus, cands, manifest = load_ours(country)
    lbcaps = {}
    f = ra / "raw" / "liveblogs-cdx.csv"
    if f.exists():
        for r in csv.DictReader(open(f, encoding="utf-8")):
            lbcaps.setdefault(key(lb_parent(r["url"])), []).extend(r["captures"].split())
    ref, excluded = [], []
    bp, exs = boilerplate(country, pool_rows, ver)
    chrome_hits = []
    for k, p in pool_rows.items():
        v = ver.get(k, {})
        routes = p["routes"].split(";")
        title = p["title"] or v.get("page_title", "")
        lb = (is_liveblog(p["url"], title) or bool(v.get("live_ld"))) and not is_wire_feed(p["url"])
        # date
        cand_dates = [v.get("page_date", ""), p["date"], url_date(p["url"])]
        if p["our_corpus_key"]:
            cand_dates.insert(0, corpus[p["our_corpus_key"]]["publication"]["published_at"])
        date = next((d[:10] for d in cand_dates if d and d[:4] == "2024"), "")
        if lb and k in lbcaps:
            pdate = (v.get("page_date") or "")[:10]
            in_win = ("2024-09-17" <= date <= "2024-09-24") or (
                any("20240917" <= ts[:8] <= "20240924" for ts in lbcaps[k]) and (not pdate or pdate >= "2024-06-01"))
        else:
            in_win = "2024-09-17" <= date <= "2024-09-24"
        if not in_win:
            excluded.append([p["outlet"], p["url"], title, date, p["routes"], "outside window (or undated)"]); continue
        fetched = v.get("fetch") not in (None, "FAILED")
        if fetched:
            if k in exs:  # re-assess with current detector, ignoring site-chrome paragraphs
                ex_ = exs[k]
                m_, c_, ev_, note_ = assess(ex_, country, skip=bp.get(p["outlet"]))
                if assess(ex_, country)[0] and not m_:
                    chrome_hits.append([p["outlet"], p["url"], assess(ex_, country)[2][:120]])
                    note_ = "attack term only in site-chrome paragraph (recurs on several differently titled pages)"
                v.update(mention=m_, central=c_, evidence=ev_, assess_note=note_, live_ld=ex_["live_ld"],
                         paywall=ex_["paywall"] or "/plus" in p["url"], canonical=ex_["canonical"])
                ck_ = key(ex_["canonical"]) if ex_["canonical"].startswith("http") else ""
                if ck_ and ck_ != k and outlet_of(country, ex_["canonical"]) == p["outlet"] and ck_ in pool_rows:
                    excluded.append([p["outlet"], p["url"], title, date, p["routes"],
                                     f"fetched copy resolves to another pool item ({ex_['canonical']}); counted there"])
                    continue
            mention, central = v.get("mention"), v.get("central")
            if not mention:
                if p["our_corpus_key"]:
                    body = corpus[p["our_corpus_key"]]["content"]
                    if has_mention(body["headline"] + " " + body["body"], country):
                        mention, central = True, bool(has_mention(body["headline"] + " " + body["body"][:700], country))
            if not mention and lb and (v.get("body_words") or 0) < 600:
                excluded.append([p["outlet"], p["url"], title, date, p["routes"],
                                 f"unverifiable live blog: captured HTML holds only {v.get('body_words')} words (entries load client-side)"])
                continue
            if not mention:
                excluded.append([p["outlet"], p["url"], title, date, p["routes"],
                                 "no substantive mention in body" + (f" ({v.get('assess_note')})" if v.get("assess_note") else "")])
                continue
            evidence = v.get("evidence", "")
        else:
            title_hit = bool(has_mention(title, country))
            if "mediacloud" not in routes and not p["our_corpus_key"] and not title_hit:
                excluded.append([p["outlet"], p["url"], title, date, p["routes"], f"unverifiable (fetch failed: {v.get('tried','') or 'not attempted'})"]); continue
            if p["our_corpus_key"]:
                body = corpus[p["our_corpus_key"]]["content"]
                mention = has_mention(body["headline"] + " " + body["body"], country)
                if not mention:
                    excluded.append([p["outlet"], p["url"], title, date, p["routes"], "corpus body has no attack term"]); continue
                central = bool(has_mention(body["headline"] + " " + body["body"][:700], country))
            else:
                central = bool(has_mention(title, country))
            evidence = ("corpus body" if p["our_corpus_key"] else
                        "Media Cloud full-text hit (body not re-fetched)" if "mediacloud" in routes else
                        "attack term in headline (body not re-fetched)")
        notes = []
        if re.search(r"/videos?/|/video\d|/clip/", p["url"]):
            notes.append("video page")
        if is_wire_feed(p["url"]):
            notes.append("automated wire-feed page (WELT dpa newsticker / RTL teletext), not an editorial article")
        doc_id = ""
        if p["our_corpus_key"]:
            cr = corpus[p["our_corpus_key"]]
            doc_id = cr["document_id"]
            status = "in_corpus"
            if not cr["deduplication"]["is_primary_record"]:
                notes.append("matched record is a non-primary duplicate")
            if lb:
                nc = len({ts for ts in lbcaps.get(k, []) if "20240917" <= ts[:8] <= "20240924"})
                notes.append(f"live blog: corpus holds one snapshot; {nc} Wayback captures in window" if nc else
                             "live blog: corpus holds one snapshot")
            if p["match_method"].startswith("fuzzy"):
                notes.append(f"matched by {p['match_method']}")
        elif lb:
            status = "live_blog"
            if p["our_cand_key"]:
                notes.append("was a candidate, dropped: " + drop_reason(cands[p["our_cand_key"]]))
            elif p["manifest_hit"]:
                notes.append("in manifest (" + p["manifest_hit"] + ") but not a candidate")
            else:
                notes.append("not in manifest")
        elif p["our_cand_key"]:
            status = "in_candidates_dropped"
            notes.append(drop_reason(cands[p["our_cand_key"]]))
        elif p["manifest_hit"]:
            status = "in_manifest_not_candidate"
            notes.append("manifest tag: " + p["manifest_hit"])
        else:
            status = "not_in_manifest"
        throttled = "ia-refusing" in v.get("tried", "") or not v
        if status != "in_corpus" and not fetched and not throttled:
            notes.append(f"pipeline stage: {status}")
            status = "inaccessible"
            notes.append("fetch failed now: " + v.get("tried", ""))
        elif status != "in_corpus" and not fetched:
            notes.append("not re-fetched during audit (Internet Archive refused connections); access unconfirmed")
        if v.get("paywall"):
            notes.append("paywalled (teaser/lead only on the fetched copy)")
        if fetched and status != "in_corpus":
            notes.append(f"accessible via {v.get('fetch')}" + (f" capture {v.get('capture_ts')}" if v.get("capture_ts") else ""))
        indep = [r for r in routes if route_independent(r, p["outlet"])]
        ref.append(dict(outlet=p["outlet"], url=p["url"], title=title, published_date=date,
                        discovery_route=";".join(routes), independent_routes=";".join(indep),
                        central_or_mention="central" if central else "mention", status=status,
                        matched_document_id=doc_id, is_liveblog="yes" if lb else "",
                        evidence=evidence, notes="; ".join(notes),
                        fetch=v.get("fetch", ""), capture_ts=v.get("capture_ts", ""), key=k,
                        paywall="yes" if v.get("paywall") else ""))
    ref.sort(key=lambda r: (r["outlet"], r["published_date"], r["url"]))
    cols = ["outlet", "url", "title", "published_date", "discovery_route", "independent_routes", "central_or_mention",
            "status", "matched_document_id", "is_liveblog", "evidence", "notes"]
    with open(ra / "reference-set.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=cols, extrasaction="ignore"); w.writeheader(); w.writerows(ref)
    with open(ra / "raw" / "excluded-pool-items.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f); w.writerow(["outlet", "url", "title", "date", "routes", "reason"]); w.writerows(excluded)
    # gap manifest
    with open(ra / "gap-manifest.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["outlet", "url", "title", "published_date", "status", "central_or_mention", "access_route",
                    "capture_ts", "fetch_url", "paywall", "liveblog_captures_in_window", "notes"])
        for r in ref:
            if r["status"] in ("in_corpus", "inaccessible"):
                continue
            fe = r["fetch"]
            route = ("wayback" if fe == "wayback" else "live" if fe == "live" else
                     "our-raw (re-extract)" if fe.startswith("our-raw") else "unconfirmed (try wayback)")
            fu = (f"https://web.archive.org/web/{r['capture_ts']}id_/{r['url']}" if fe == "wayback" else r["url"])
            caps = [ts for ts in lbcaps.get(r["key"], []) if "20240917" <= ts[:8] <= "20240925"]
            w.writerow([r["outlet"], r["url"], r["title"], r["published_date"], r["status"], r["central_or_mention"],
                        route, r["capture_ts"], fu, r["paywall"], " ".join(sorted(set(caps))) if r["is_liveblog"] else "", r["notes"]])
        # live blogs that exist in the window but whose captured HTML cannot show the entries
        for e in excluded:
            if e[5].startswith("unverifiable live blog"):
                kk = key(e[1])
                caps = [ts for ts in lbcaps.get(kk, []) if "20240917" <= ts[:8] <= "20240925"]
                w.writerow([e[0], e[1], e[2], e[3], "live_blog_unverified", "", "wayback", "", "", "",
                            " ".join(sorted(set(caps))), e[5] + "; not in reference set (mention unverifiable)"])
    # recall table
    T = defaultdict(Counter)
    for r in ref:
        o = r["outlet"]
        for scope in ("all", r["central_or_mention"]):
            T[o][f"{scope}_n"] += 1
            T[o][f"{scope}_in"] += r["status"] == "in_corpus"
        if r["independent_routes"]:
            T[o]["indep_n"] += 1
            T[o]["indep_in"] += r["status"] == "in_corpus"
        if "mediacloud" in r["discovery_route"]:
            T[o]["mc_n"] += 1
            T[o]["mc_in"] += r["status"] == "in_corpus"
        T[o]["st_" + r["status"]] += 1
    with open(ra / "raw" / "recall-table.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        hdr = ["outlet", "ref_n", "in_corpus", "recall", "central_n", "central_in", "central_recall", "mention_n",
               "mention_in", "mention_recall", "indep_n", "indep_in", "indep_recall", "mc_n", "mc_in",
               "st_in_corpus", "st_live_blog", "st_in_candidates_dropped", "st_in_manifest_not_candidate",
               "st_not_in_manifest", "st_inaccessible"]
        w.writerow(hdr)
        rate = lambda a, b: f"{a / b:.2f}" if b else ""
        for o in sorted(T):
            t = T[o]
            w.writerow([o, t["all_n"], t["all_in"], rate(t["all_in"], t["all_n"]), t["central_n"], t["central_in"],
                        rate(t["central_in"], t["central_n"]), t["mention_n"], t["mention_in"],
                        rate(t["mention_in"], t["mention_n"]), t["indep_n"], t["indep_in"],
                        rate(t["indep_in"], t["indep_n"]), t["mc_n"], t["mc_in"]] +
                       [t[h] for h in hdr[15:]])
    print(open(ra / "raw" / "recall-table.csv").read())
    print("excluded", Counter(e[5].split(" (")[0] for e in excluded))
    print("rows whose only mention was site chrome:", len(chrome_hits), Counter(c[0] for c in chrome_hits))
    for c in chrome_hits:
        print("   ", c)


if __name__ == "__main__":
    c, stage = sys.argv[1], sys.argv[2]
    {"pool": pool, "verify": verify, "report": report}[stage](c)
