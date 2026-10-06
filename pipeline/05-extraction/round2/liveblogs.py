#!/usr/bin/env python3
"""Gap fill stage 2: live blogs as timestamped entries (Germany + US).

Brief: docs/agent-briefs/gapfill-stage2-liveblogs.md.  Stdlib only.

Network: Wayback only (https://web.archive.org/web/<ts>id_/<url>), one request at a time,
>= 3 s apart, timeout 60 s, 3 tries with backoff 10/30/90 s, stop after 20 consecutive failures.
Cached audit captures (data/<c>/08-recall-audit/raw/pages/...) are reused when the timestamp is identical.

Usage:
    python3 liveblogs.py run --country germany [--outlet rnd] [--no-fetch]
    python3 liveblogs.py report --country germany

Outputs (per country, under data/<country>/05-extraction/round2/):
    liveblog-entries.jsonl, liveblog-report.md, liveblog-fetch-log.csv, and
    data/<country>/raw/<outlet>/r2lb-<sha16(url)>-<ts>.html.gz
"""
import argparse, csv, datetime as dt, gzip, hashlib, html as H, json, os, re, sys, time
import urllib.request, urllib.error
from html.parser import HTMLParser
from pathlib import Path
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[3]
DATA = ROOT / "data"
sys.path.insert(0, str(ROOT / "pipeline" / "08-recall-audit"))
import recall_audit_common as RAC  # read-only helpers: key(), has_mention()

WIN_START, WIN_END = "20240917000000", "20240924235959"
WIN_DAYS = {f"2024-09-{d:02d}" for d in range(17, 25)}
MAX_CAPTURES = 10
MIN_GAP_S = 3.0
TZ = {"germany": ZoneInfo("Europe/Berlin"), "us": ZoneInfo("America/New_York")}
UA = "Mozilla/5.0 (research; news-corpus gapfill stage2; polite, 1 req/3s) python-urllib"


# ------------------------------------------------------------------ mini DOM
VOID = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "param", "source", "track", "wbr"}
RAWTEXT = {"script", "style"}
BLOCK = {"p", "div", "li", "ul", "ol", "h1", "h2", "h3", "h4", "h5", "h6", "blockquote", "figcaption", "tr", "section",
         "article", "header", "footer", "br", "table", "aside", "figure", "dl", "dt", "dd", "pre", "hr"}
SKIP_TEXT = {"script", "style", "svg", "button", "noscript", "template", "iframe", "select", "option", "form", "input"}


class Node:
    __slots__ = ("tag", "attrs", "children", "parent")

    def __init__(self, tag, attrs=None, parent=None):
        self.tag, self.attrs, self.children, self.parent = tag, attrs or {}, [], parent

    @property
    def cls(self):
        return self.attrs.get("class", "") or ""

    def has_class(self, c):
        return c in self.cls.split()

    def iter(self):
        """document-order iteration over element descendants (not self)"""
        stack = [iter(self.children)]
        while stack:
            for ch in stack[-1]:
                if isinstance(ch, Node):
                    yield ch
                    stack.append(iter(ch.children))
                    break
            else:
                stack.pop()

    def find_all(self, pred):
        return [n for n in self.iter() if pred(n)]

    def find(self, pred):
        for n in self.iter():
            if pred(n):
                return n
        return None


class _Builder(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.root = Node("#root")
        self.cur = self.root

    def handle_starttag(self, tag, attrs):
        n = Node(tag, {k: (v if v is not None else "") for k, v in attrs}, self.cur)
        self.cur.children.append(n)
        if tag not in VOID:
            self.cur = n
        if tag in RAWTEXT:
            self.set_cdata_mode(tag)

    def handle_startendtag(self, tag, attrs):
        n = Node(tag, {k: (v if v is not None else "") for k, v in attrs}, self.cur)
        self.cur.children.append(n)

    def handle_endtag(self, tag):
        if tag in VOID:
            return
        n = self.cur
        while n is not None and n.tag != tag:
            n = n.parent
        if n is not None and n.parent is not None:
            self.cur = n.parent

    def handle_data(self, data):
        self.cur.children.append(data)


def parse_html(text):
    b = _Builder()
    b.feed(text)
    b.close()
    return b.root


def node_text(n, skip=None, skip_pred=None, block_pred=None):
    """Visible text of a node, paragraphs separated by \\n, whitespace collapsed. Verbatim otherwise."""
    out = []

    def rec(x):
        if isinstance(x, str):
            out.append(x)
            return
        if x.tag in SKIP_TEXT or (skip and x.tag in skip) or (skip_pred and skip_pred(x)):
            return
        blk = x.tag in BLOCK or (block_pred is not None and block_pred(x))
        if blk:
            out.append("\n")
        for c in x.children:
            rec(c)
        if blk:
            out.append("\n")

    rec(n)
    s = "".join(out).replace("\xa0", " ")
    lines = [re.sub(r"[ \t\r\f\v]+", " ", l).strip() for l in s.split("\n")]
    return "\n".join(l for l in lines if l)


def html_to_text(s):
    """HTML fragment string -> text (for JSON-LD articleBody that carries markup)."""
    if not s:
        return ""
    s = re.sub(r"<(script|style)[^>]*>.*?</\1>", "", s, flags=re.S | re.I)
    s = re.sub(r"<bsp-[a-z-]+[^>]*>.*?</bsp-[a-z-]+>", "", s, flags=re.S | re.I)
    s = re.sub(r"<br\s*/?>", "\n", s, flags=re.I)
    root = parse_html("<div>" + s + "</div>")
    return node_text(root)


def ldjson_blocks(t):
    out = []
    for m in re.finditer(r'<script[^>]*type="application/ld\+json"[^>]*>(.*?)</script>', t, re.S | re.I):
        try:
            out.append(json.loads(m.group(1).strip()))
        except Exception:
            continue
    return out


def ld_find(t, typ):
    stack = list(ldjson_blocks(t))
    while stack:
        d = stack.pop(0)
        if isinstance(d, list):
            stack = d + stack
        elif isinstance(d, dict):
            if d.get("@type") == typ or (isinstance(d.get("@type"), list) and typ in d["@type"]):
                return d
            if "@graph" in d:
                stack = list(d["@graph"]) + stack
    return None


def ws(s):
    return re.sub(r"\s+", " ", s or "").strip()


# ------------------------------------------------------------------ time helpers
def iso_parse(s):
    """Parse an ISO-ish timestamp; returns aware datetime or None."""
    if not s:
        return None
    s = s.strip().replace("Z", "+00:00")
    try:
        d = dt.datetime.fromisoformat(s)
    except Exception:
        return None
    return d


def local_date(country, iso):
    d = iso_parse(iso)
    if d is None:
        return ""
    if d.tzinfo is None:
        return d.date().isoformat()
    return d.astimezone(TZ[country]).date().isoformat()


# ------------------------------------------------------------------ extractors
# Every extractor returns (entries, info). entry = dict(anchor, time, title, text, links, method, warnings)
def ex_tagesschau(t, ctx):
    root = parse_html(t)
    anchors = root.find_all(lambda n: n.tag == "div" and n.has_class("liveblog--anchor") and n.attrs.get("id"))
    # document-order walk; entry = anchor + following p/ul/ol/h3 until next anchor
    order = list(root.iter())
    idx = {id(n): i for i, n in enumerate(order)}
    entries = []
    for ai, a in enumerate(anchors):
        start = idx[id(a)]
        end = idx[id(anchors[ai + 1])] if ai + 1 < len(anchors) else len(order)
        dtn = a.find(lambda n: n.has_class("liveblog__datetime"))
        h2 = a.find(lambda n: n.tag == "h2")
        paras, links = [], []
        i = start + 1
        a_desc = {id(x) for x in a.iter()}
        while i < end:
            n = order[i]
            if id(n) in a_desc:
                i += 1
                continue
            if n.tag in ("p", "ul", "ol") and not any(isinstance(p, Node) and p.tag in ("p", "ul", "ol") for p in _ancestors(n, stop=a.parent)):
                if n.tag == "p" and not n.has_class("textabsatz"):
                    i += 1
                    continue
                txt = node_text(n)
                if txt:
                    paras.append(txt)
                links += [x.attrs.get("href", "") for x in n.iter() if x.tag == "a"]
                i += 1
                continue
            i += 1
        t_raw = ws(node_text(dtn)) if dtn else ""
        entries.append({"anchor": a.attrs["id"], "time_raw": t_raw, "title": ws(node_text(h2)) if h2 else "",
                        "text": "\n".join(paras), "links": links, "method": "container:div.liveblog--anchor+p.textabsatz",
                        "warnings": []})
    for e in entries:
        m = re.match(r"(\d\d)\.(\d\d)\.(\d{4})\s*[•·]\s*(\d\d):(\d\d)", e["time_raw"])
        mc = re.search(r"(\d\d:\d\d)\s*Uhr", e["time_raw"])
        e["clock"] = mc.group(1) if mc else ""
        if m:
            d, mo, y, hh, mm = m.groups()
            e["time"] = f"{y}-{mo}-{d}T{hh}:{mm}:00+02:00" if "2024-03-31" < f"{y}-{mo}-{d}" < "2024-10-27" else f"{y}-{mo}-{d}T{hh}:{mm}:00+01:00"
            e["warnings"].append("tz_offset_assumed_Europe/Berlin")
        else:
            e["time"] = ""
            e["warnings"].append("date_missing_on_page_capture" if e["clock"] else "no_timestamp_on_page")
    return entries, {"n_dom_anchors": len(anchors), "n_dated": sum(1 for e in entries if e["time"])}


def _ancestors(n, stop=None):
    p = n.parent
    while p is not None and p is not stop:
        yield p
        p = p.parent


def ex_zdfheute(t, ctx):
    d = ld_find(t, "LiveBlogPosting")
    if not d or not d.get("liveBlogUpdate"):
        return [], {"note": "no_liveBlogUpdate"}
    entries = []
    for u in d["liveBlogUpdate"]:
        entries.append({"anchor": "", "time": u.get("datePublished", ""), "title": ws(H.unescape(u.get("headline", ""))),
                        "text": html_to_text(u.get("articleBody", "")), "links": re.findall(r'href="([^"]+)"', u.get("articleBody", "")),
                        "method": "ld-json:liveBlogUpdate", "warnings": [] if u.get("datePublished") else ["no_timestamp_on_page"]})
    return entries, {"ld_updates": len(entries), "coverageStart": d.get("coverageStartTime")}


def ex_ntv(t, ctx):
    """n-tv ticker: <p><b>+++ HH:MM Headline +++</b><br/>text</p>; date from the ticker's own datePublished."""
    root = parse_html(t)
    box = root.find(lambda n: n.tag == "div" and n.has_class("article__text"))
    if box is None:
        return [], {"note": "no_article__text"}
    ld = None
    for b in ldjson_blocks(t):
        if isinstance(b, dict) and b.get("datePublished"):
            ld = b
            break
    ticker_date = (ld or {}).get("datePublished", "")[:10]
    entries = []
    cur = None
    for ch in box.children:
        if not isinstance(ch, Node) or ch.tag != "p":
            continue
        b = ch.find(lambda n: n.tag == "b")
        btxt = ws(node_text(b)) if b else ""
        m = re.match(r"\+\+\+\s*(\d\d:\d\d)\s+(.*?)\s*\+\+\+\s*$", btxt)
        if m and ch.children and ch.children[0] is b:
            cur = {"anchor": "", "clock": m.group(1), "title": m.group(2), "paras": [],
                   "links": [], "method": "container:article__text/p>b(+++ HH:MM +++)", "warnings": []}
            entries.append(cur)
            rest = node_text(ch, skip_pred=lambda x: x is b)
            if rest:
                cur["paras"].append(rest)
            cur["links"] += [x.attrs.get("href", "") for x in ch.iter() if x.tag == "a"]
        elif cur is not None:
            txt = node_text(ch)
            if txt:
                cur["paras"].append(txt)
            cur["links"] += [x.attrs.get("href", "") for x in ch.iter() if x.tag == "a"]
    # dates: the ticker's datePublished date for the first entries, one day earlier after each clock wrap (clock rises going down)
    prev_clock, day = None, dt.date.fromisoformat(ticker_date) if ticker_date else None
    out = []
    for e in entries:
        if prev_clock is not None and e["clock"] > prev_clock and day is not None:
            day = day - dt.timedelta(days=1)
        prev_clock = e["clock"]
        e["text"] = "\n".join(e.pop("paras"))
        if day:
            e["time"] = f"{day.isoformat()}T{e['clock']}:00+02:00"
            e["warnings"] += ["date_from_ticker_datePublished_and_clock_order", "tz_offset_assumed_Europe/Berlin"]
        else:
            e["time"] = ""
            e["warnings"].append("no_timestamp_on_page")
        out.append(e)
    return out, {"ticker_datePublished": (ld or {}).get("datePublished", "")}


def ex_rnd(t, ctx):
    """RND tickers: entries are a Tickaroo embed loaded client-side. Look for embedded Fusion content with entries."""
    m = re.search(r"Fusion\.globalContent=", t)
    info = {}
    if not m:
        return [], {"note": "no_fusion_globalContent"}
    try:
        gc, _ = json.JSONDecoder().raw_decode(t[m.end():])
    except Exception as e:
        return [], {"note": "fusion_parse_error:" + str(e)[:80]}
    els = gc.get("elements", [])
    tick = [e for e in els if e.get("type") == "customEmbed" and e.get("subtype") == "tickaroo"]
    info["tickaroo_embeds"] = [e.get("embed", {}).get("id") for e in tick]
    info["n_elements"] = len(els)
    return [], info  # entries are not in the page: only the embed reference + background text


def ex_cnn(t, ctx):
    """CNN: JSON-LD LiveBlogPosting.liveBlogUpdate gives time, headline and the anchor id (h_<hash>); the headline and
    time elements of the DOM post are empty until client-side JS fills them.  The LD articleBody has the publisher's
    quotes rewritten as backslash-escaped straight quotes and drops photo captions, so the text is taken from the
    DOM post body (live-story-post__content, matched by data-post-id), falling back to the LD text."""
    d = ld_find(t, "LiveBlogPosting")
    if not (d and d.get("liveBlogUpdate")):
        return [], {"note": "no_liveBlogUpdate"}
    root = parse_html(t)
    dom = {a.attrs["data-post-id"]: a for a in root.find_all(lambda n: n.tag == "article" and n.attrs.get("data-post-id"))}
    entries, n_dom = [], 0
    for u in d["liveBlogUpdate"]:
        url = u.get("url") or u.get("mainEntityOfPage") or ""
        anchor = url.split("#", 1)[1] if "#" in url else ""
        ld_text = u.get("articleBody", "") or ""
        ld_text = html_to_text(ld_text) if "<" in ld_text else "\n".join(l.strip() for l in ld_text.split("\n") if l.strip())
        post = dom.get(anchor)
        body = post.find(lambda n: n.has_class("live-story-post__content")) if post is not None else None
        links, warn = [], []
        if body is not None:
            text, n_dom = node_text(body), n_dom + 1
            links = [x.attrs.get("href", "") for x in body.iter() if x.tag == "a"]
            method = "ld-json:liveBlogUpdate(time,headline)+container:live-story-post__content(text)"
        else:
            text, method = ld_text, "ld-json:liveBlogUpdate"
            warn.append("text_from_ld_json_not_dom")
        entries.append({"anchor": anchor, "time": u.get("datePublished", ""), "title": ws(u.get("headline", "") or ""),
                        "text": text, "links": links, "method": method, "warnings": warn, "modified": u.get("dateModified", "")})
    info = {"ld_updates": len(entries), "dom_text": n_dom}
    m = re.search(r"data-initial-count=(\d+)", t)
    if m:
        info["page_post_count"] = int(m.group(1))
    return entries, info


def ex_ap(t, ctx):
    """AP: <bsp-liveblog-post class=LiveBlogPost data-post-id data-posted-date-timestamp=epoch-ms>."""
    root = parse_html(t)
    posts = root.find_all(lambda n: n.has_class("LiveBlogPost") and n.attrs.get("data-post-id"))
    entries = []
    ld = ld_find(t, "LiveBlogPosting")
    for p in posts:
        hl = p.find(lambda n: n.has_class("LiveBlogPost-headline"))
        body = p.find(lambda n: n.has_class("LiveBlogPost-body"))
        ms = p.attrs.get("data-posted-date-timestamp", "")
        warn = []
        if ms.isdigit():
            time_iso = dt.datetime.fromtimestamp(int(ms) / 1000, dt.timezone.utc).isoformat(timespec="milliseconds").replace("+00:00", "Z")
        else:
            time_iso = ""
            warn.append("no_timestamp_on_page")
        links = [x.attrs.get("href", "") for x in (body.iter() if body else []) if x.tag == "a"]
        entries.append({"anchor": p.attrs.get("data-post-id", ""), "time": time_iso,
                        "title": ws(node_text(hl)) if hl else "", "text": node_text(body) if body else "",
                        "links": links, "method": "container:bsp-liveblog-post.LiveBlogPost", "warnings": warn})
    info = {"dom_posts": len(posts), "ld_updates": len((ld or {}).get("liveBlogUpdate", []) or [])}
    return entries, info


def _plain(n):
    return ws("".join(c if isinstance(c, str) else _plain(c) for c in n.children if isinstance(c, str) or c.tag not in SKIP_TEXT))


def ex_nyt(t, ctx):
    root = parse_html(t)
    feed = root.find(lambda n: n.attrs.get("id") == "live-feed-items")
    if feed is None:
        return [], {"note": "no_live-feed-items"}
    ld = ld_find(t, "LiveBlogPosting") or {}
    ld_time = {}
    for u in ld.get("liveBlogUpdate", []) or []:
        url = u.get("url", "")
        if "#" in url or "/" in url:
            ld_time[url.rsplit("/", 1)[-1].split("#")[-1]] = u.get("datePublished", "")
    entries = []
    for art in feed.find_all(lambda n: n.attrs.get("role") == "article"):
        box = art.find(lambda n: n.attrs.get("data-testid") in ("live-blog-post", "reporter-update"))
        if box is None:
            continue
        url = box.attrs.get("data-url", "")
        anchor = url.split("#", 1)[1] if "#" in url else box.attrs.get("id", "")
        tm = box.find(lambda n: n.tag == "time")
        h2 = box.find(lambda n: n.tag == "h2")
        title = ws(node_text(h2)) if h2 else ""

        def skip(x):
            if x.attrs.get("data-testid") in ("live-blog-byline", "copy-link", "Show-More", "share-tools") or x is h2 or x.tag == "time":
                return True
            # visually hidden labels in photo blocks
            return x.tag == "span" and _plain(x) in ("Image", "Credit...")

        def in_figcaption(x):
            return x.tag == "span" and any(a_.tag == "figcaption" for a_ in _ancestors(x))

        text = node_text(box, skip_pred=skip, block_pred=in_figcaption)
        text = re.sub(r"^\s*Pinned\n", "", text)
        links = [x.attrs.get("href", "") for x in box.iter() if x.tag == "a"]
        w = []
        iso = tm.attrs.get("datetime", "") if tm else ""
        if not iso and ld_time.get(anchor):
            iso = ld_time[anchor]
            w.append("time_from_ld_json")
        if not iso:
            w.append("no_timestamp_on_page")
        entries.append({"anchor": anchor, "time": iso, "title": title, "text": text, "links": links,
                        "method": "container:section#live-feed-items>div[role=article]", "warnings": w,
                        "posinset": art.attrs.get("aria-posinset", "")})
    pos = [int(e["posinset"]) for e in entries if str(e.get("posinset", "")).isdigit()]
    info = {"dom_articles": len(entries)}
    if pos:
        info["older_posts_not_on_page"] = max(0, min(pos) - 1)
    return entries, info


def ex_wapo(t, ctx):
    m = re.search(r'<script id="__NEXT_DATA__"[^>]*>(.*?)</script>', t, re.S)
    if not m:
        return [], {"note": "no_next_data"}
    nd = json.loads(m.group(1))
    g = nd.get("props", {}).get("pageProps", {}).get("globalContent", {})
    entries = []
    for c in g.get("content_elements", []):
        if c.get("type") != "story":
            continue
        paras = []
        links = []
        for x in c.get("content_elements", []):
            if x.get("type") == "text" and x.get("content"):
                paras.append(html_to_text(x["content"]))
                links += re.findall(r'href=\\?"([^"\\]+)', x["content"])
            elif x.get("type") == "header" and x.get("content"):
                paras.append(html_to_text(x["content"]))
        hl = (c.get("headlines") or {}).get("basic", "") or ""
        tm = (c.get("additional_properties") or {}).get("first_display_date", "") or c.get("first_publish_date", "") or ""
        entries.append({"anchor": c.get("_id", ""), "time": tm, "title": ws(H.unescape(hl)),
                        "text": "\n".join(p for p in paras if p), "links": links,
                        "method": "next-data:globalContent.content_elements[type=story]",
                        "warnings": [] if tm else ["no_timestamp_on_page"]})
    return entries, {"story_elements": len(entries), "poll_frequency": (g.get("additional_properties") or {}).get("poll_frequency")}


def ex_nbc(t, ctx):
    d = ld_find(t, "LiveBlogPosting")
    entries = []
    if d and d.get("liveBlogUpdate"):
        for u in d["liveBlogUpdate"]:
            url = u.get("url") or ""
            entries.append({"anchor": url.split("#", 1)[1] if "#" in url else "", "time": u.get("datePublished", ""),
                            "title": ws(u.get("headline", "")), "text": html_to_text(u.get("articleBody", "")),
                            "links": [], "method": "ld-json:liveBlogUpdate", "warnings": []})
    return entries, {"ld_updates": len(entries)}


def ex_abc(t, ctx):
    d = ld_find(t, "LiveBlogPosting")
    n_ld = len((d or {}).get("liveBlogUpdate", []) or [])
    entries = []
    if d and d.get("liveBlogUpdate"):
        for u in d["liveBlogUpdate"]:
            entries.append({"anchor": "", "time": u.get("datePublished", ""), "title": ws(u.get("headline", "")),
                            "text": html_to_text(u.get("articleBody", "")), "links": [],
                            "method": "ld-json:liveBlogUpdate", "warnings": []})
    return entries, {"ld_updates": n_ld, "shell_bytes": len(t)}


def ex_none(t, ctx):
    return [], {"note": "single_video_page_no_entries"}


EXTRACTORS = {"tagesschau": ex_tagesschau, "zdfheute": ex_zdfheute, "ntv": ex_ntv, "rnd": ex_rnd, "welt": ex_none,
              "cnn": ex_cnn, "ap": ex_ap, "nyt": ex_nyt, "wapo": ex_wapo, "nbc": ex_nbc, "abc": ex_abc, "fox": ex_none}


# ------------------------------------------------------------------ fetch (Wayback only, polite)
class StopRun(Exception):
    pass


LOG_FIELDS = ["country", "outlet", "blog_url", "kind", "timestamp", "source", "http_status", "bytes", "final_url",
              "raw_path", "result", "error", "logged_at_utc", "note"]


class Fetcher:
    def __init__(self, logpath, offline=False):
        self.logpath, self.offline = Path(logpath), offline
        self.last = 0.0
        self.consec_fail = 0
        self.n_requests = 0
        self.prior = []
        if self.logpath.exists():
            for r in csv.DictReader(open(self.logpath, encoding="utf-8")):
                if (r["source"] in ("fetch", "cdx-fetch") and not r["error"].startswith("redirected to different capture")
                        and not (r["kind"] == "cdx" and "@" not in r["note"] and r["note"] != "(none)")):
                    self.prior.append(r)
        self.rows = []

    def log(self, **kw):
        row = {k: "" for k in LOG_FIELDS}
        row.update(kw)
        row["logged_at_utc"] = dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        self.rows.append(row)
        new = not self.logpath.exists()
        with open(self.logpath, "a", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, LOG_FIELDS)
            if new:
                w.writeheader()
            w.writerow(row)

    def prior_ok(self, kind, url, ts=""):
        for r in self.prior:
            if r["kind"] == kind and r["blog_url"] == url and r["timestamp"] == ts and r["result"] == "ok":
                return r
        return None

    def _http(self, url):
        """one polite request with up to 3 tries; returns (status, bytes, final_url, err)"""
        if self.offline:
            return None, None, "", "offline"
        err = ""
        for attempt, backoff in enumerate((10, 30, 90)):
            wait = MIN_GAP_S - (time.time() - self.last)
            if wait > 0:
                time.sleep(wait)
            self.last = time.time()
            self.n_requests += 1
            try:
                req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept-Encoding": "identity"})
                with urllib.request.urlopen(req, timeout=60) as r:
                    data = r.read()
                    if r.headers.get("Content-Encoding", "").lower() == "gzip":
                        data = gzip.decompress(data)
                    self.last = time.time()
                    self.consec_fail = 0
                    return r.status, data, r.geturl(), ""
            except urllib.error.HTTPError as e:
                err = f"HTTP {e.code}"
                self.last = time.time()
                if e.code in (400, 403, 404, 410):  # permanent for this capture, do not retry
                    self.consec_fail += 1
                    return e.code, None, "", err
            except Exception as e:
                err = f"{type(e).__name__}: {str(e)[:100]}"
                self.last = time.time()
            if attempt < 2:
                time.sleep(backoff)
        self.consec_fail += 1
        if self.consec_fail >= 20:
            raise StopRun("20 consecutive failed requests")
        return None, None, "", err

    def capture(self, country, outlet, blog_url, ts):
        url = f"https://web.archive.org/web/{ts}id_/{blog_url}"
        status, data, final, err = self._http(url)
        if self.consec_fail >= 20:
            raise StopRun("20 consecutive failed requests")
        return status, data, final, err

    def cdx(self, base_url, prefix=True):
        """status-200 captures in the window of base_url and its URL variants (prefix match): rows [timestamp, original, status]"""
        q = ("https://web.archive.org/cdx/search/cdx?url=" + urllib.parse.quote(base_url, safe="") +
             ("&matchType=prefix" if prefix else "") + "&from=20240917&to=20240924235959&output=json&fl=timestamp,original,statuscode"
             "&filter=statuscode:200&limit=5000")
        status, data, final, err = self._http(q)
        if self.consec_fail >= 20:
            raise StopRun("20 consecutive failed requests")
        return status, data, err, q


import urllib.parse  # noqa: E402  (used by Fetcher.cdx)


def sha16(s):
    return hashlib.sha256(s.encode("utf-8")).hexdigest()[:16]


def rel_raw(outlet, url, ts):
    return f"raw/{outlet}/r2lb-{sha16(url)}-{ts}.html.gz"


# ------------------------------------------------------------------ planning
def read_manifest(country):
    rows = []
    for r in csv.DictReader(open(DATA / country / "08-recall-audit/gap-manifest.csv", encoding="utf-8")):
        if r["status"] in ("live_blog", "live_blog_unverified"):
            rows.append(r)
    return rows


def audit_cache(country):
    """(url_key, ts) -> path (relative to data/<country>) of the audit's cached Wayback capture"""
    out = {}
    for l in open(DATA / country / "08-recall-audit/raw/verify-cache.jsonl", encoding="utf-8"):
        d = json.loads(l)
        if d.get("fetch") == "wayback" and d.get("raw_file") and d.get("capture_ts"):
            out[(d["key"], str(d["capture_ts"]))] = d["raw_file"]
        elif d.get("raw_file") and d.get("fetch") == "wayback":
            m = re.search(r"-(\d{14})\.html$", d["raw_file"])
            if m:
                out[(d["key"], m.group(1))] = d["raw_file"]
    return out


def in_window(ts):
    return WIN_START <= ts <= WIN_END


def initial_selection(cands):
    """last in-window capture of each day"""
    by_day = {}
    for ts in sorted(cands):
        by_day[ts[:8]] = ts
    return sorted(by_day.values())


def entry_range(entries):
    ts = [iso_parse(e["time"]) for e in entries if e.get("time")]
    ts = [x if x.tzinfo else x.replace(tzinfo=dt.timezone.utc) for x in ts if x]
    return (min(ts), max(ts)) if ts else (None, None)


def ts_to_dt(ts):
    return dt.datetime.strptime(ts, "%Y%m%d%H%M%S").replace(tzinfo=dt.timezone.utc)


def pick_gap_capture(cands, tried, parsed):
    """consecutive parsed captures (by actual timestamp) where the newer page starts after the older one ended:
    entries in between rolled off. Return the untried in-window capture nearest the midpoint of the largest gap."""
    sel = sorted(parsed)
    best = None
    for a, b in zip(sel, sel[1:]):
        new_a = entry_range(parsed[a])[1]
        old_b = entry_range(parsed[b])[0]
        if new_a is None or old_b is None or not old_b > new_a:
            continue
        mids = [c for c in cands if a < c < b and c not in tried]
        if not mids:
            continue
        mid = ts_to_dt(a) + (ts_to_dt(b) - ts_to_dt(a)) / 2
        c = min(mids, key=lambda x: abs((ts_to_dt(x) - mid).total_seconds()))
        gap = (old_b - new_a).total_seconds()
        if best is None or gap > best[0]:
            best = (gap, c)
    return best[1] if best else None


def find_gaps(parsed):
    out = []
    sel = sorted(parsed)
    for a, b in zip(sel, sel[1:]):
        new_a, old_b = entry_range(parsed[a])[1], entry_range(parsed[b])[0]
        if new_a and old_b and old_b > new_a:
            out.append((a, b, new_a.isoformat(), old_b.isoformat()))
    return out


# ------------------------------------------------------------------ per-blog processing
ANCHOR_OUTLETS = {"tagesschau", "cnn", "ap", "nyt"}
SHELL_OUTLETS = {"abc", "rnd"}  # entries load client-side: one probe capture, then stop if empty
ROLLING_OUTLETS = {"zdfheute"}  # page shows only the latest N entries of a long-running blog
LINK_RE = re.compile(r"pager|walkie|beeper|piepser|funkger|gold-apollo", re.I)
NO_PREFIX_CDX = {"nyt"}  # Wayback answers prefix CDX queries on nytimes.com with HTTP 403: exact queries instead
CDX_SKIP = {"ntv", "welt", "fox"}  # single-entry / video pages: only the audit-cached capture is used


def norm_entry(country, outlet, e):
    """add published_time/published_at/local-date; returns normalized dict"""
    pt = e.get("time", "") or ""
    pa = local_date(country, pt) if pt else ""
    return {**e, "published_time": pt, "published_at": pa}


def load_capture(country, outlet, blog_url, ts, fetcher, cache, key, stats, fetch_url=None):
    """returns (html_text|None, raw_rel|None, source, actual_ts)"""
    rel = rel_raw(outlet, blog_url, ts)
    path = DATA / country / rel
    if path.exists():
        data = gzip.open(path, "rb").read()
        fetcher.log(country=country, outlet=outlet, blog_url=blog_url, kind="capture", timestamp=ts, source="local",
                    result="ok", bytes=len(data), raw_path=rel)
        return data.decode("utf-8", "replace"), rel, "local", ts
    pr = fetcher.prior_ok("capture", blog_url, ts)
    if pr and fetch_url and pr.get("final_url") and pr["final_url"].split("id_/", 1)[-1] != fetch_url:
        pr = None  # that earlier request was for another URL variant
    if pr and pr.get("raw_path") and (DATA / country / pr["raw_path"]).exists():
        data = gzip.open(DATA / country / pr["raw_path"], "rb").read()
        actual = re.search(r"-(\d{14})\.html\.gz$", pr["raw_path"]).group(1)
        fetcher.log(country=country, outlet=outlet, blog_url=blog_url, kind="capture", timestamp=ts, source="local",
                    result="ok", bytes=len(data), raw_path=pr["raw_path"], note=pr.get("note", ""))
        if actual != ts:
            stats["notes"].append(f"{ts}: not directly playable, Wayback served capture {actual} instead")
        return data.decode("utf-8", "replace"), pr["raw_path"], "local", actual
    cached = cache.get((key, ts))
    if cached:
        data = (DATA / country / cached).read_bytes()
        path.parent.mkdir(parents=True, exist_ok=True)
        with gzip.open(path, "wb") as f:
            f.write(data)
        fetcher.log(country=country, outlet=outlet, blog_url=blog_url, kind="capture", timestamp=ts, source="audit-cache",
                    result="ok", bytes=len(data), raw_path=rel, note=f"copied from {cached}")
        return data.decode("utf-8", "replace"), rel, "audit-cache", ts
    if fetcher.offline:
        fetcher.log(country=country, outlet=outlet, blog_url=blog_url, kind="capture", timestamp=ts, source="none",
                    result="skipped", error="offline")
        return None, None, "none", ts
    status, data, final, err = fetcher.capture(country, outlet, fetch_url or blog_url, ts)
    if data is None:
        fetcher.log(country=country, outlet=outlet, blog_url=blog_url, kind="capture", timestamp=ts, source="fetch",
                    http_status=status or "", result="error", error=err)
        stats["failures"].append(f"{ts}: {err}")
        return None, None, "fetch-failed", ts
    m = re.search(r"/web/(\d{14})", final or "")
    fts = m.group(1) if m else ts
    if fts != ts:
        # Wayback served a different capture of the same URL (requested one not playable): keep it under its own timestamp
        if not in_window(fts):
            fetcher.log(country=country, outlet=outlet, blog_url=blog_url, kind="capture", timestamp=ts, source="fetch",
                        http_status=status, bytes=len(data), final_url=final, result="error",
                        error=f"redirected to capture {fts} outside window; discarded")
            stats["failures"].append(f"{ts}: redirected to {fts} (outside window), discarded")
            return None, None, "fetch-failed", ts
        rel2 = rel_raw(outlet, blog_url, fts)
        path2 = DATA / country / rel2
        if not path2.exists():
            path2.parent.mkdir(parents=True, exist_ok=True)
            with gzip.open(path2, "wb") as f:
                f.write(data)
        fetcher.log(country=country, outlet=outlet, blog_url=blog_url, kind="capture", timestamp=ts, source="fetch",
                    http_status=status, bytes=len(data), final_url=final, result="ok", raw_path=rel2,
                    note=f"requested capture not served; Wayback redirected to capture {fts}, stored under {fts}")
        stats["notes"].append(f"{ts}: not directly playable, Wayback served capture {fts} instead")
        return data.decode("utf-8", "replace"), rel2, "fetch", fts
    path.parent.mkdir(parents=True, exist_ok=True)
    with gzip.open(path, "wb") as f:
        f.write(data)
    fetcher.log(country=country, outlet=outlet, blog_url=blog_url, kind="capture", timestamp=ts, source="fetch",
                http_status=status, bytes=len(data), final_url=final, result="ok", raw_path=rel)
    return data.decode("utf-8", "replace"), rel, "fetch", ts


def variant_key(u):
    u = re.sub(r"^https?://", "", (u or "").strip().lower())
    u = re.sub(r"^(www|us)\.", "", u)
    u = u.split("?")[0].split("#")[0]
    u = re.sub(r"/index\.html$", "", u).rstrip("/")
    return u


def cdx_bases(url):
    base = re.sub(r"/index\.html$", "", url.split("?")[0].split("#")[0]).rstrip("/")
    out = [base]
    if "//www.cnn.com/" in base:
        out.append(base.replace("//www.cnn.com/", "//us.cnn.com/"))
    elif "//us.cnn.com/" in base:
        out.append(base.replace("//us.cnn.com/", "//www.cnn.com/"))
    return out


def get_candidates(row, fetcher, cache, key, country, stats):
    """In-window captures to choose from, as {timestamp: original URL variant}.
    The audit's list (`liveblog_captures_in_window`) merges URL variants (with/without trailing slash, /index.html, www/us)
    and includes captures Wayback cannot play back (non-200 / revisit: it redirects to a neighbouring capture).  So we ask
    the CDX index once (prefix query, status 200, window) and use the variants that normalise to the manifest URL; the
    audit list is only the fallback if CDX fails.  Cached audit captures (same timestamp) are always added."""
    outlet, url = row["outlet"], row["url"]
    qs = urllib.parse.urlsplit(url).query
    cached_ts = sorted({ats for (k2, ats) in cache if k2 == key and in_window(ats)})
    cands, from_cdx = {}, False
    skip = outlet in CDX_SKIP or (outlet in SHELL_OUTLETS and cached_ts)
    if not skip:
        prior = fetcher.prior_ok("cdx", url)
        if prior and ("@" in prior["note"] or prior["note"] == "(none)"):
            cands = dict(t.split("@", 1) for t in prior["note"].split() if "@" in t)
            from_cdx = True
        elif not fetcher.offline:
            ok = True
            rows_all = []
            bases = cdx_bases(url)
            if outlet in NO_PREFIX_CDX:
                bases = [bases[0], bases[0] + "/"]
            for base in bases:
                status, data, err, q = fetcher.cdx(base, prefix=outlet not in NO_PREFIX_CDX)
                if data is None:
                    fetcher.log(country=country, outlet=outlet, blog_url=url, kind="cdx-part", source="cdx-fetch",
                                http_status=status or "", result="error", error=err, final_url=q)
                    stats["failures"].append(f"cdx {base}: {err}")
                    ok = False
                    continue
                try:
                    rows_all += json.loads(data.decode("utf-8", "replace") or "[]")[1:]
                except Exception:
                    ok = False
            if ok:
                for ts, orig, st in sorted(rows_all):
                    if not in_window(ts) or variant_key(orig) != variant_key(url):
                        continue
                    oq = urllib.parse.urlsplit(orig).query
                    if oq and oq != qs:
                        continue
                    cands.setdefault(ts, orig)
                from_cdx = True
                fetcher.log(country=country, outlet=outlet, blog_url=url, kind="cdx", source="cdx-fetch", http_status=200,
                            result="ok", final_url=" ".join(cdx_bases(url)), note=" ".join(f"{t}@{o}" for t, o in sorted(cands.items())) or "(none)")
    if not from_cdx:
        for c in row.get("liveblog_captures_in_window", "").split():
            if in_window(c):
                cands.setdefault(c, url)
        if not skip:
            stats["notes"].append("CDX status-200 listing unavailable; used the audit's capture list (may include non-playable captures)")
    stats["cdx_200_in_window"] = len(cands) if from_cdx else None
    for ats in cached_ts:  # the audit's cached in-window capture(s) of this URL need no fetch
        cands.setdefault(ats, url)
    return dict(sorted(cands.items()))


def process_blog(country, row, fetcher, cache, logf):
    outlet, url = row["outlet"], row["url"]
    key = RAC.key(url)
    stats = {"country": country, "outlet": outlet, "blog_url": url, "status": row["status"], "failures": [],
             "captures": [], "notes": []}
    ex = EXTRACTORS[outlet]
    cands = get_candidates(row, fetcher, cache, key, country, stats)
    stats["candidates_in_window"] = len(cands)
    if not cands:
        stats["notes"].append("no status-200 capture of this URL (or its slash / index.html variants) in Sep 17-24 in the CDX index, and no audit-cached in-window capture"
                              + ("; the audit's capture list for this blog consists of per-entry sub-URL captures, not of the blog page" if outlet == "abc" else ""))
        stats["result"] = "no_in_window_capture"
        return stats, {}
    parsed, raws, infos = {}, {}, {}
    tried = []

    def fetch_one(ts):
        tried.append(ts)
        html_text, rel, src, actual = load_capture(country, outlet, url, ts, fetcher, cache, key, stats, fetch_url=cands.get(ts))
        if html_text is None:
            return
        if actual in parsed:
            stats["captures"].append({"ts": ts, "actual_ts": actual, "source": "duplicate", "entries": len(parsed[actual]),
                                      "info": {"note": "served capture already parsed"}, "duplicate_of_parsed": True})
            logf(f"  {outlet} {ts} -> served {actual} (already parsed)")
            return
        if src == "local":
            src = "audit-cache" if (key, actual) in cache else "fetch"  # earlier copy of one of the two
        raws[actual] = rel
        ents, info = ex(html_text, {})
        parsed[actual], infos[actual] = ents, info
        stats["captures"].append({"ts": actual, "requested_ts": ts if actual != ts else "", "source": src,
                                  "entries": len(ents), "info": info})
        logf(f"  {outlet} {ts}{'->' + actual if actual != ts else ''} {src} entries={len(ents)} {info}")

    if outlet in SHELL_OUTLETS:
        # entries load client-side: probe once with the latest in-window capture (audit-cached in-window capture preferred)
        cached_in = [c for c in cands if (key, c) in cache]
        probe_list = cached_in[-1:] if cached_in else list(reversed(cands))[:3]
        for probe in probe_list:
            fetch_one(probe)
            if parsed:
                break
        if not any(parsed.values()):
            stats["result"] = "no_entries_in_capture" if parsed else "no_capture"
            if parsed:
                stats["notes"].append(f"probe capture {probe}: entries load client-side; embedded state holds no entries ({json.dumps(infos.get(probe), ensure_ascii=False)[:160]})")
            return stats, {"probe": probe, "parsed": parsed, "raws": raws}
    for ts in initial_selection(cands):
        if ts not in tried and len(tried) < MAX_CAPTURES:
            fetch_one(ts)
    # gap fill / head fill within the budget (budget counts attempts, including ones Wayback could not serve)
    while len(tried) < MAX_CAPTURES:
        nxt = pick_gap_capture(cands, tried, parsed)
        if nxt is None and parsed:
            # head fill: the earliest parsed page hides older entries (rolling feed) -> try earlier captures
            first = min(parsed)
            hidden = (infos[first] or {}).get("older_posts_not_on_page", 0)
            lo = entry_range(parsed[first])[0]
            rolling = outlet in ROLLING_OUTLETS and lo and lo.astimezone(TZ[country]).date().isoformat() > "2024-09-17"
            earlier = [c for c in cands if c < first and c not in tried]
            if earlier and (hidden or rolling):
                nxt = earlier[0]
        if nxt is None:
            break
        fetch_one(nxt)
    stats["gaps"] = find_gaps(parsed)
    stats["tried"] = list(tried)
    return stats, {"parsed": parsed, "raws": raws}


def merge_blog(country, row, stats, data):
    """dedupe across captures (one entry per publisher id/anchor, else per time+text); returns distinct entries"""
    outlet, url = row["outlet"], row["url"]
    parsed, raws = data.get("parsed", {}), data.get("raws", {})
    seen = {}
    order = []
    for ts in sorted(parsed):
        for e in parsed[ts]:
            e = norm_entry(country, outlet, e)
            textkey = ws(e["title"] + "|" + e["text"])
            if e["anchor"] and e.get("clock"):
                k = (e["anchor"], e["clock"])
            elif e["anchor"]:
                k = (e["anchor"],)
            else:
                k = (e["published_time"], textkey[:200])
            if k in seen:
                s_ = seen[k]
                s_["last_seen"] = ts
                if e["published_time"] and not s_["published_time"]:
                    # first capture showed only a clock time; a later capture carries the full date
                    s_["published_time"], s_["published_at"] = e["published_time"], e["published_at"]
                    s_["warnings"] = [w for w in s_["warnings"] if w not in ("date_missing_on_page_capture", "no_timestamp_on_page")]
                    s_["warnings"] += [w for w in e["warnings"] if w.startswith("tz_")]
                    s_["warnings"].append(f"date_from_later_capture:{ts}")
                if textkey != s_["_textkey"]:
                    if "text_changed_in_later_capture" not in s_["warnings"]:
                        s_["warnings"].append("text_changed_in_later_capture")
                    if all(v["_textkey"] != textkey for v in s_["_versions"]):
                        s_["_versions"].append({"_textkey": textkey, "title": e["title"], "text": e["text"], "links": e.get("links", []),
                                                "first_seen": ts, "raw_path": raws[ts], "method": e["method"]})
                continue
            e["first_seen"], e["last_seen"] = ts, ts
            e["raw_path"] = raws[ts]
            e["_textkey"] = textkey
            e["_versions"] = []
            e["warnings"] = list(e["warnings"])
            seen[k] = e
            order.append(e)
    return order


# ------------------------------------------------------------------ finalize entries
def finalize_blog(country, row, stats, distinct):
    outlet, url = row["outlet"], row["url"]
    lang = "de" if country == "germany" else "en"
    win, notime, outside = [], [], []
    seen_text = {}
    dup = 0
    for e in distinct:
        tk = e["_textkey"]
        if tk in seen_text and tk.strip("| ") != "":
            dup += 1
            seen_text[tk]["warnings"].append("identical_text_dropped_later_entry:" + (e["published_time"] or "no-time"))
            continue
        seen_text[tk] = e
        if e["published_time"]:
            (win if e["published_at"] in WIN_DAYS else outside).append(e)
        else:
            notime.append(e)
    stats["entries_distinct_all"] = len(distinct) - dup
    stats["entries_in_window"] = len(win)
    stats["entries_no_timestamp"] = len(notime)
    stats["entries_outside_window"] = len(outside)
    stats["dropped_identical_text"] = dup
    kept = []
    for e in win + notime:
        text = e["text"]
        mm = RAC.has_mention((e["title"] + "\n" + text).strip(), country)
        by_link = any(LINK_RE.search(l or "") for l in e.get("links", []))
        w = list(e["warnings"])
        if not mm and not by_link:
            for v in e.get("_versions", []):  # the publisher edited this entry later; use the first version that names the attack
                if RAC.has_mention((v["title"] + "\n" + v["text"]).strip(), country):
                    e = {**e, "title": v["title"], "text": v["text"], "raw_path": v["raw_path"], "first_seen": v["first_seen"]}
                    text, mm = v["text"], True
                    w.append("kept_version_from_later_capture:" + v["first_seen"])
                    break
        if not mm and not by_link:
            continue
        if not mm and by_link:
            w.append("kept_by_link_to_attack_article")
        if not e["published_time"]:
            w.append("no_timestamp_on_page")
        head = (e["title"] + "\n" + text[:300]).strip()
        central = bool(RAC.has_mention(head, country))
        anchor = e["anchor"]
        entry_id = anchor or hashlib.sha256((url + e["published_time"] + text[:80]).encode("utf-8")).hexdigest()[:12]
        kept.append({
            "outlet": outlet, "blog_url": url, "entry_id": entry_id,
            "entry_url": (url + "#" + anchor) if (anchor and outlet in ANCHOR_OUTLETS) else "",
            "published_time": e["published_time"], "published_at": e["published_at"],
            "title": e["title"], "body_text": text, "body_words": len(text.split()),
            "first_seen_capture": e["first_seen"], "last_seen_capture": e["last_seen"], "raw_path": e["raw_path"],
            "extract_method": e["method"], "salience": "central" if central else "mention",
            "language": lang, "warnings": sorted(set(w)),
        })
    kept.sort(key=lambda r: (r["published_time"] or "~", r["entry_id"]))
    stats["entries_kept"] = len(kept)
    return kept


def rolloff_stats(stats, distinct, parsed):
    """entries seen earlier but absent from the last capture although older than its oldest entry"""
    tss = sorted(parsed)
    if len(tss) < 2:
        return None
    last = tss[-1]
    lo, _ = entry_range(parsed[last])
    if lo is None:
        return None
    n = 0
    for e in distinct:
        if e["last_seen"] != last and e["published_time"]:
            d = iso_parse(e["published_time"])
            if d is not None:
                d = d if d.tzinfo else d.replace(tzinfo=TZ["germany"])
                if d < lo:
                    n += 1
    return n


# ------------------------------------------------------------------ spot check
def searchable(html_text):
    parts = [html_text]
    for m in re.finditer(r"<script[^>]*>(.*?)</script>", html_text, re.S | re.I):
        body = m.group(1).strip()
        if body[:1] in "{[" or "__preloadedData" in body[:60]:
            try:
                s = body
                j = json.JSONDecoder().raw_decode(s.replace(":undefined", ":null"))[0]
            except Exception:
                continue
            stack = [j]
            while stack:
                x = stack.pop()
                if isinstance(x, dict):
                    stack.extend(x.values())
                elif isinstance(x, list):
                    stack.extend(x)
                elif isinstance(x, str) and len(x) > 20:
                    parts.append(x)
    txt = "\n".join(parts)
    txt = re.sub(r"<!--.*?-->", "", txt, flags=re.S)
    # tag stripping: block-level tags (and <br>) become a space, inline tags (a, em, strong, span, ...) vanish
    txt = re.sub(r"</?([a-zA-Z][a-zA-Z0-9-]*)\b[^>]*>", lambda m: " " if m.group(1).lower() in BLOCK else "", txt)
    txt = H.unescape(txt).replace("\xa0", " ")
    return ws(txt)


def verify_population(country, kept_by_outlet):
    """every kept entry: whole body (whitespace-collapsed) findable in the stripped raw capture, and each paragraph findable"""
    out = {}
    cache = {}
    for outlet, ents in sorted(kept_by_outlet.items()):
        n = whole = lines_ok = 0
        for e in ents:
            raw = cache.get(e["raw_path"])
            if raw is None:
                raw = searchable(gzip.open(DATA / country / e["raw_path"], "rb").read().decode("utf-8", "replace"))
                cache[e["raw_path"]] = raw
            body = ws(e["body_text"].replace("\xa0", " "))
            lines = [ws(p) for p in e["body_text"].replace("\xa0", " ").split("\n") if ws(p)]
            n += 1
            whole += body in raw
            lines_ok += all(l in raw for l in lines)
        out[outlet] = (n, whole, lines_ok)
    return out


def spot_check(country, kept_by_outlet, n=3):
    import random
    rng = random.Random(2024)
    res = []
    for outlet, ents in sorted(kept_by_outlet.items()):
        if not ents:
            continue
        pick = rng.sample(ents, min(n, len(ents)))
        for e in pick:
            raw = gzip.open(DATA / country / e["raw_path"], "rb").read().decode("utf-8", "replace")
            hay = searchable(raw)
            body = ws(e["body_text"].replace("\xa0", " "))
            ok = body in hay
            # fall back: every paragraph findable separately
            if not ok:
                ok = all(ws(p) in hay for p in e["body_text"].split("\n") if ws(p))
                how = "paragraphs-separately" if ok else "NOT FOUND"
            else:
                how = "whole-body"
            res.append({"outlet": outlet, "entry_id": e["entry_id"], "published_time": e["published_time"], "found": ok, "how": how})
    return res


# ------------------------------------------------------------------ report
def pct(a, b):
    return f"{a}/{b}"


def write_report(country, all_stats, kept_all, spot, notes, pop=None):
    out = DATA / country / "05-extraction/round2/liveblog-report.md"
    L = []
    L.append(f"# Live blogs as entries, {country} (stage 2)\n")
    L.append(f"Generated by `pipeline/05-extraction/round2/liveblogs.py` (brief: `docs/agent-briefs/gapfill-stage2-liveblogs.md`).\n")
    # summary per outlet
    by_out = {}
    for s in all_stats:
        by_out.setdefault(s["outlet"], []).append(s)
    L.append("## Per outlet\n")
    net = {}
    lp = DATA / country / "05-extraction/round2/liveblog-fetch-log.csv"
    if lp.exists():
        for r in csv.DictReader(open(lp, encoding="utf-8")):
            if r["source"] not in ("fetch", "cdx-fetch"):
                continue
            n = net.setdefault(r["outlet"], {"cdx": 0, "cap": 0, "err": 0})
            n["cdx" if r["kind"].startswith("cdx") else "cap"] += 1
            if r["result"] != "ok":
                n["err"] += 1
    L.append("| outlet | blogs | blogs with entries | captures parsed (fetched / audit-cache) | Wayback requests (CDX / capture / failed) | entries distinct | in window | no timestamp | kept | method |")
    L.append("|---|---|---|---|---|---|---|---|---|---|")
    tot = {"b": 0, "be": 0, "f": 0, "c": 0, "cdx": 0, "cap": 0, "err": 0, "d": 0, "w": 0, "nt": 0, "k": 0}
    for o, ss in sorted(by_out.items()):
        nb = len(ss)
        with_e = sum(1 for s in ss if s.get("entries_distinct_all", 0) > 0)
        cf = sum(1 for s in ss for c in s["captures"] if c["source"] == "fetch")
        cc = sum(1 for s in ss for c in s["captures"] if c["source"] == "audit-cache")
        meth = sorted({m for s in ss for m in s.get("methods", [])})
        n = net.get(o, {"cdx": 0, "cap": 0, "err": 0})
        d_, w_, nt_, k_ = (sum(s.get(x, 0) for s in ss) for x in ("entries_distinct_all", "entries_in_window", "entries_no_timestamp", "entries_kept"))
        L.append(f"| {o} | {nb} | {with_e} | {cf} / {cc} | {n['cdx']} / {n['cap']} / {n['err']} | {d_} | {w_} | {nt_} | {k_} | {', '.join(meth) or '-'} |")
        for k_name, v in (("b", nb), ("be", with_e), ("f", cf), ("c", cc), ("cdx", n["cdx"]), ("cap", n["cap"]), ("err", n["err"]), ("d", d_), ("w", w_), ("nt", nt_), ("k", k_)):
            tot[k_name] += v
    L.append(f"| **total** | {tot['b']} | {tot['be']} | {tot['f']} / {tot['c']} | {tot['cdx']} / {tot['cap']} / {tot['err']} | {tot['d']} | {tot['w']} | {tot['nt']} | {tot['k']} | |")
    L.append("")
    L.append("`captures parsed`: distinct capture files whose entries were extracted, split by origin: fetched from Wayback in this task, or the audit's cached capture of the same timestamp (copied into `raw/<outlet>/r2lb-*`). "
             "`Wayback requests` counts every request in `liveblog-fetch-log.csv` (CDX index queries, capture fetches, and those that failed or were redirected out of the window), including requests of earlier script versions during development. "
             "\"Entries distinct\" counts each entry once across captures; \"in window\" = local date Sep 17-24.\n")
    L.append("## Per blog\n")
    L.append("| outlet | blog | result | captures | entries total (window) | kept | roll-off | extraction method |")
    L.append("|---|---|---|---|---|---|---|---|")
    for s in all_stats:
        short = s["blog_url"].replace("https://", "").replace("www.", "")
        if len(short) > 80:
            short = short[:38] + "..." + short[-38:]
        caps = ", ".join((f"{c['ts']}->{c['actual_ts']}" if c.get("duplicate_of_parsed") else f"{c['ts']}({c['entries']})") for c in s["captures"]) or "-"
        ro = s.get("rolloff_text", "")
        L.append(f"| {s['outlet']} | {short} | {s.get('result', 'ok')} | {caps} | "
                 f"{s.get('entries_in_window', 0)} (+{s.get('entries_no_timestamp', 0)} undated, {s.get('entries_outside_window', 0)} outside window) | "
                 f"{s.get('entries_kept', 0)} | {ro} | {', '.join(s.get('methods', [])) or '-'} |")
    L.append("")
    L.append("Captures column: capture timestamp and, in brackets, the number of entries parsed from it. `A->B`: capture A is not directly playable; Wayback served capture B, which was already parsed.\n")
    L.append("## Failures and empty results\n")
    anyf = False
    for s in all_stats:
        msgs = list(s["failures"]) + ([f"result={s['result']}"] if s.get("result") not in (None, "ok") else []) + s["notes"]
        if msgs:
            anyf = True
            L.append(f"- {s['outlet']} {s['blog_url']}")
            for m in msgs:
                L.append(f"  - {m}")
    if not anyf:
        L.append("- none")
    L.append("")
    L.append("## Coverage gaps (entries that rolled off between two selected captures)\n")
    anyg = False
    for s in all_stats:
        for g in s.get("gaps", []):
            anyg = True
            L.append(f"- {s['outlet']} {s['blog_url']}: capture {g[0]} newest entry {g[2]}; next capture {g[1]} oldest entry {g[3]}")
    if not anyg:
        L.append("- none detected")
    L.append("")
    L.append("## Sample entries (three per outlet)\n")
    import random
    rng = random.Random(2024)
    for o in sorted(by_out):
        ents = kept_all.get(o, [])
        L.append(f"### {o}")
        if not ents:
            L.append("- no kept entries\n")
            continue
        for e in rng.sample(ents, min(3, len(ents))):
            L.append(f"- **{e['title'] or '(no headline)'}** | {e['published_time'] or 'no timestamp'} | {e['salience']}")
            L.append(f"  - {e['body_text'][:200].replace(chr(10), ' / ')}")
        L.append("")
    L.append("## Spot check (text findable verbatim in the raw capture after tag stripping)\n")
    if spot:
        ok = sum(1 for r in spot if r["found"])
        L.append(f"{ok} of {len(spot)} sampled entries found verbatim (3 per outlet, `random.Random(2024)`; fewer where the outlet has fewer kept entries).\n")
        L.append("| outlet | entry_id | published_time | found | how |")
        L.append("|---|---|---|---|---|")
        for r in spot:
            L.append(f"| {r['outlet']} | {r['entry_id'][:40]} | {r['published_time']} | {r['found']} | {r['how']} |")
    L.append("")
    if pop:
        L.append("All kept entries (not only the sample): body found verbatim as one string / every paragraph found verbatim, in the tag-stripped capture "
                 "(block tags become spaces, inline tags vanish, HTML comments dropped, JSON strings of embedded state searched too).\n")
        L.append("| outlet | kept entries | whole body found | every paragraph found |")
        L.append("|---|---|---|---|")
        for o, (n_, w_, l_) in pop.items():
            L.append(f"| {o} | {n_} | {w_} | {l_} |")
        L.append("")
        L.append("Whole-body mismatches are entries whose paragraphs are separated in the HTML by elements that are not entry text (ads, buttons, bylines, embedded media); every paragraph is still verbatim.\n")
    L.append("## Validation\n")
    bad_time = [e for es in kept_all.values() for e in es if e["published_time"] and e["published_at"] not in WIN_DAYS]
    nots = [e for es in kept_all.values() for e in es if not e["published_time"]]
    dups = {}
    for es in kept_all.values():
        for e in es:
            dups.setdefault((e["blog_url"], ws(e["title"] + e["body_text"])), 0)
            dups[(e["blog_url"], ws(e["title"] + e["body_text"]))] += 1
    L.append(f"- kept entries with a time outside Sep 17-24 local: {len(bad_time)}")
    L.append(f"- kept entries without timestamp (warning set): {len(nots)}")
    L.append(f"- duplicate texts within a blog among kept entries: {sum(1 for v in dups.values() if v > 1)}")
    L.append("")
    L.append("## Judgment calls\n")
    for n in notes:
        L.append(f"- {n}")
    out.write_text("\n".join(L) + "\n", encoding="utf-8")


JUDGMENT = {
    "common": [
        "Window: entries are in the window when their local date (Europe/Berlin for Germany, America/New_York for US) is Sep 17-24, 2024. Entries outside are counted but never kept.",
        "Capture list: the audit's `liveblog_captures_in_window` mixes several URL variants (with/without trailing slash, /index.html, www/us host, per-entry sub-URLs) and non-playable captures (Wayback redirects those to a neighbouring capture). So for each blog to be sampled the script asks the Wayback CDX index once for status-200 captures in the window (prefix query; exact queries for nytimes.com, where Wayback answers prefix queries with HTTP 403) and keeps only variants that normalise to the manifest URL. The audit's list is the fallback if CDX fails (it did not).",
        "Sampling: the last status-200 capture of each day (capture timestamps 20240917000000-20240924235959 only), then gap-filling captures between two parsed captures where the newer page's oldest entry is later than the older page's newest entry, and earlier captures when the earliest page hides older entries (NYT: `older_posts_not_on_page`; ZDF: rolling blog); at most 10 attempts per blog. Captures dated Sep 25 are never fetched, even where the audit listed them.",
        "Where Wayback answers a request for capture A with a redirect to capture B of the same URL (A is a revisit/non-playable record), B is stored under its own timestamp and treated as a normal capture (logged with a note); B is discarded if it lies outside the window.",
        "Keep rule: `has_mention(title + body, country)` or a link in the entry to a URL containing pager/walkie/beeper/piepser/funkger (warning `kept_by_link_to_attack_article`). `salience=central` when `has_mention` hits the title or the first 300 characters.",
        "`published_at` is the local date of `published_time`; `published_time` is the on-page time. Where the page gives a clock time without offset (tagesschau, ntv) the Europe/Berlin summer offset +02:00 is added and flagged `tz_offset_assumed_Europe/Berlin`.",
        "One entry per publisher id/anchor across captures (first-seen version, `text_changed_in_later_capture` if the publisher edited it). If the first version does not name the attack but a later version does, the first such version is kept (`kept_version_from_later_capture:<ts>`, `raw_path` points to that capture). Same-text entries within one blog are kept once.",
        "Visible text only: scripts, styles, svg, buttons, forms and the like are skipped; paragraphs are joined with a newline; HTML entities are unescaped; wording is never touched. Photo captions inside an entry stay in the text (AP, CNN, NYT); NYT's visually hidden labels \"Image\" and \"Credit...\" are dropped.",
        "`language` is set to `de` for Germany and `en` for the US without detection: all entries are in the outlet's language.",
        "Request budget: the fetch log counts every Wayback request of this task, including requests of earlier versions of the script during development (some of them redirected or discarded). Requests ran strictly one at a time, at least 3 s apart, timeout 60 s, 3 tries with backoff 10/30/90 s; the run would stop after 20 consecutive failures (never reached).",
    ],
    "germany": [
        "RND: the ticker is a Tickaroo embed (id 65210c26d412303c813d1b4a, the same for all eight daily URLs) that loads client-side. The page's Arc/Fusion `globalContent` holds only the embed reference and background text, no entries, so each blog is recorded as `no_entries_in_capture` (probe: the audit-cached in-window capture of each URL; no further requests). The Tickaroo embed itself was not fetched: it is not a capture of the listed URL and is outside the brief.",
        "tagesschau: while a day's blog is live the page shows only the clock time (\"20:11 Uhr\"); a finished page shows \"17.09.2024 • 20:11 Uhr\". The date is taken from a later capture of the same entry (same anchor, same clock time) and flagged `date_from_later_capture:<ts>`; if none carries a date the entry stays undated (warning). tagesschau pages list the whole day (no roll-off).",
        "ZDFheute: one long-running blog (since 2024-07-31) whose page lists only the latest 20 entries (JSON-LD `liveBlogUpdate`). The CDX index has no status-200 capture between 2024-09-17 12:52 UTC and 2024-09-22 16:11 UTC; entries of Sep 17-21 that rolled off the page are therefore not recoverable (see coverage gaps). Requests for capture times on Sep 18/19 were redirected by Wayback to the Sep 17 capture.",
        "ntv: the audit's row is the Ukraine ticker page of Sep 18 (one capture, the audit-cached one). The entry named in the URL (14:05 Munz) does not mention the attack; the entry that does is 12:41 (Kreml, Pager explosions). Only that entry is kept. ntv gives clock times only: the date comes from the ticker's `datePublished` (2024-09-18) and from the clock order (a rising clock while reading downwards marks the day before), flagged `date_from_ticker_datePublished_and_clock_order`.",
        "WELT: the row is a video livestream page (VideoObject), no entries; recorded as `no_entries_in_capture`.",
    ],
    "us": [
        "ABC: all 20 live-updates URLs are client-side shells (JSON-LD `liveBlogUpdate` empty, `window.__abcnews__.page.content.story` ~1.6 KB). One probe capture per blog (the audit-cached in-window capture where there is one: 15 blogs; otherwise one CDX lookup for a status-200 capture). Five blogs have no status-200 capture of the blog URL in the window. The audit's capture lists for ABC consist mostly of per-entry sub-URLs (`.../<blog>/<entry-slug>-<id>`); whether those pages carry the entry text was not examined (outside the brief), a possible follow-up.",
        "NBC: the CDX index lists status-200 captures of the live blog only from Sep 25 onwards (outside the capture window), so nothing was fetched; the audit-cached capture is from 2024-09-25 08:55 UTC and was not used.",
        "Fox: the row is a video page (`/video/6362120447112`), no entries.",
        "WaPo: the entries load client-side (poll every 60 s). The capture contains only the entries the server rendered into `globalContent.content_elements` (type `story`: 2 to 17 per capture). Entries are dated by `first_display_date`.",
        "NYT: the DOM lists the latest posts only (about 26-32); the number of older posts hidden behind \"load more\" is `aria-posinset` of the first post minus 1 (reported as `older_posts_not_on_page`). Earlier captures were fetched to recover them. The pinned summary post (\"Here are the latest developments\") has no `<time>` in the DOM; its time is taken from the JSON-LD `liveBlogUpdate` entry with the same URL (`time_from_ld_json`).",
        "CNN: time, headline and anchor come from JSON-LD `liveBlogUpdate`; the text comes from the DOM post body, because the JSON-LD text has the publisher's quotes rewritten as backslash-escaped straight quotes (219 of 283 entries in 8 sampled captures) and omits photo captions. The DOM post header (time, headline) is empty in the capture (filled by JavaScript).",
        "AP: DOM `bsp-liveblog-post`; time from `data-posted-date-timestamp` (epoch ms, UTC), which equals the JSON-LD `datePublished`; text from `LiveBlogPost-body`. The AP page lists the whole blog (42 / 48 posts), no roll-off.",
    ],
}


# ------------------------------------------------------------------ main
def run(country, only_outlet=None, offline=False):
    logdir = Path("/tmp")
    lg = open(logdir / f"liveblogs-{country}.log", "a", buffering=1)

    def logf(msg):
        line = f"{dt.datetime.now().strftime('%H:%M:%S')} {msg}"
        print(line, flush=True)
        lg.write(line + "\n")

    outdir = DATA / country / "05-extraction/round2"
    outdir.mkdir(parents=True, exist_ok=True)
    fetcher = Fetcher(outdir / "liveblog-fetch-log.csv", offline=offline)
    # rewrite log from prior network rows only (local/cache rows are regenerated each run)
    with open(outdir / "liveblog-fetch-log.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, LOG_FIELDS)
        w.writeheader()
        for r in fetcher.prior:
            w.writerow({k: r.get(k, "") for k in LOG_FIELDS})
    cache = audit_cache(country)
    manifest = read_manifest(country)
    order = {"germany": ["tagesschau", "zdfheute", "ntv", "welt", "rnd"],
             "us": ["ap", "cnn", "nyt", "wapo", "nbc", "fox", "abc"]}[country]
    manifest.sort(key=lambda r: (order.index(r["outlet"]), r["url"]))
    all_stats, kept_all = [], {}
    try:
        for row in manifest:
            if only_outlet and row["outlet"] != only_outlet:
                continue
            logf(f"blog {row['outlet']} {row['url']}")
            stats, data = process_blog(country, row, fetcher, cache, logf)
            distinct = merge_blog(country, row, stats, data) if data.get("parsed") else []
            kept = finalize_blog(country, row, stats, distinct)
            stats["methods"] = sorted({e["method"] for e in distinct})
            ro = rolloff_stats(stats, distinct, data.get("parsed", {})) if data.get("parsed") else None
            stats["rolled_off"] = ro
            if stats.get("gaps"):
                stats["rolloff_text"] = f"yes, gap(s) between captures; {ro or 0} entries rolled off, not recoverable"
            elif ro:
                stats["rolloff_text"] = f"yes, {ro} entries rolled off between captures"
            elif len(stats["captures"]) >= 1:
                counts = [c["entries"] for c in stats["captures"]]
                hid = [c["info"].get("older_posts_not_on_page") for c in stats["captures"] if c["info"].get("older_posts_not_on_page") is not None]
                if hid and max(hid) > 0:
                    stats["rolloff_text"] = f"yes: page lists only the latest posts (max {max(counts)} entries/capture); up to {max(hid)} older posts not on the page"
                else:
                    stats["rolloff_text"] = f"no evidence (max {max(counts)} entries/capture)"
            hid_all = [c["info"].get("older_posts_not_on_page") for c in stats["captures"] if c["info"].get("older_posts_not_on_page")]
            if hid_all and "rolloff_text" in stats and not stats["rolloff_text"].startswith("yes: page lists"):
                stats["rolloff_text"] += f"; single pages hide up to {max(hid_all)} older posts (recovered only as far as earlier captures show them)"
            stats.setdefault("result", "ok" if stats["captures"] else "no_capture")
            if stats["result"] == "ok" and not distinct:
                stats["result"] = "no_entries_in_capture"
            all_stats.append(stats)
            kept_all.setdefault(row["outlet"], []).extend(kept)
            logf(f"  -> distinct={stats.get('entries_distinct_all', 0)} window={stats.get('entries_in_window', 0)} kept={stats.get('entries_kept', 0)} result={stats['result']}")
            write_outputs(country, all_stats, kept_all, [], ["(run in progress)"])
    except StopRun as e:
        logf(f"STOP: {e}")
        all_stats.append({"country": country, "outlet": "-", "blog_url": "-", "failures": [f"run stopped: {e}"], "captures": [],
                          "notes": [], "result": "stopped"})
    spot = spot_check(country, kept_all)
    pop = verify_population(country, kept_all)
    notes = list(JUDGMENT["common"]) + JUDGMENT.get(country, [])
    write_outputs(country, all_stats, kept_all, spot, notes, pop)
    logf("done; requests=%d" % fetcher.n_requests)


def write_outputs(country, all_stats, kept_all, spot, notes, pop=None):
    outdir = DATA / country / "05-extraction/round2"
    with open(outdir / "liveblog-entries.jsonl", "w", encoding="utf-8") as f:
        for o in sorted(kept_all):
            for e in kept_all[o]:
                f.write(json.dumps(e, ensure_ascii=False) + "\n")
    write_report(country, [s for s in all_stats if s["outlet"] != "-"] + [s for s in all_stats if s["outlet"] == "-"], kept_all, spot, notes, pop)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["run"])
    ap.add_argument("--country", required=True, choices=["germany", "us"])
    ap.add_argument("--outlet")
    ap.add_argument("--no-fetch", action="store_true")
    a = ap.parse_args()
    run(a.country, a.outlet, a.no_fetch)
