"""Shared helpers for the recall audit (URL keys, our-data index, term detection, body extraction)."""
import csv, glob, html as H, json, re, urllib.parse
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2] / "data"
WINDOW = ("2024-09-17", "2024-09-24")

OUTLET_HOSTS = {
 "germany": {"tagesschau": ["tagesschau.de"], "zdfheute": ["zdf.de", "zdfheute.de"], "rtl": ["rtl.de"],
             "ntv": ["n-tv.de"], "bild": ["bild.de"], "spiegel": ["spiegel.de"], "welt": ["welt.de"],
             "tonline": ["t-online.de"], "rnd": ["rnd.de"]},
 "us": {"fox": ["foxnews.com"], "cnn": ["cnn.com"], "abc": ["abcnews.go.com", "abcnews.com"],
        "cbs": ["cbsnews.com"], "nbc": ["nbcnews.com"], "nyt": ["nytimes.com"],
        "wapo": ["washingtonpost.com"], "yahoo": ["yahoo.com"], "usatoday": ["usatoday.com"],
        "ap": ["apnews.com"], "reuters": ["reuters.com"]},
}
ORIGINAL_ROUTE = {
 "tagesschau": "wayback-cdx", "zdfheute": "wayback-cdx", "rtl": "wayback-cdx", "ntv": "wayback-cdx",
 "bild": "bild-dated-archive", "spiegel": "wayback-cdx", "welt": "wayback-cdx+copilot-curated",
 "tonline": "wayback-cdx", "rnd": "wayback-cdx",
 "fox": "gdelt-doc-api+codex-curated", "cnn": "wayback-cdx", "abc": "wayback-cdx", "cbs": "sitemap",
 "nbc": "sitemap", "nyt": "gdelt-doc-api+codex-curated", "wapo": "wayback-cdx-prefix+codex-curated",
 "yahoo": "gdelt-doc-api+codex-curated", "usatoday": "gdelt-doc-api+codex-curated", "ap": "sitemap",
 "reuters": "wayback-cdx-prefix+codex-curated",
}


# subdomains / sections that are NOT the audited (German-language / US English-language) outlet are rejected
CBS_LOCAL = re.compile(r"^/(newyork|chicago|losangeles|sanfrancisco|boston|philadelphia|pittsburgh|minnesota|miami|"
                       r"colorado|baltimore|detroit|texas|sacramento|atlanta|bayarea|dfw|mass)/", re.I)
ALLOWED_SUB = {"www", "edition", "us", "news", "m", "amp", "radio", "mobile", ""}


def outlet_of(country, url):
    sp = urllib.parse.urlsplit(url)
    host = sp.netloc.lower().split(":")[0]
    for o, hs in OUTLET_HOSTS[country].items():
        for h in hs:
            if host == h or host.endswith("." + h):
                sub = host[: -len(h)].rstrip(".")
                if sub not in ALLOWED_SUB:
                    return None  # e.g. arabic.cnn.com, jp.reuters.com, tw.news.yahoo.com, finance.yahoo.com
                if o == "nyt" and re.match(r"/es/", sp.path):
                    return None
                if o == "cbs" and CBS_LOCAL.match(sp.path):
                    return None  # CBS-owned local stations = "local TV" census category, not CBS News
                if o == "yahoo" and host == "www.yahoo.com" and not sp.path.startswith("/news"):
                    return None
                return o
    return None


def norm_url(url):
    u = urllib.parse.unquote((url or "").strip())
    u = re.sub(r"^https?://web\.archive\.org/web/\d+(id_)?/", "", u)
    u = re.sub(r"^https?://", "", u, flags=re.I)
    u = u.split("#")[0].split("?")[0]
    host, _, path = u.partition("/")
    host = host.lower()
    host = re.sub(r"^(www\d?|m|amp|mobile|edition|news|us)\.", "", host)
    path = re.sub(r"(/amp)?/?$", "", path)
    path = re.sub(r"\.amp(\.html)?$", r"\1", path)
    path = re.sub(r"^amp/", "", path)
    path = re.sub(r"/index\.html$", "", path)
    if host == "zdfheute.de":
        host, path = "zdf.de", "nachrichten/" + path
    if host == "yahoo.com" and not path.startswith("news/"):
        path = "news/" + path
    if host == "abcnews.com":
        host = "abcnews.go.com"
    return f"{host}/{path}".lower()


KEYS = [
 ("rtl.de", r"-id(\d{6,})"), ("n-tv.de", r"article(\d{6,})"), ("bild.de", r"-([0-9a-f]{24})(?:$|\.)"),
 ("bild.de", r"-(\d{6,9})\.bild"), ("spiegel.de", r"-a-([0-9a-f-]{20,})"),
 ("welt.de", r"/(?:article|plus|video|liveticker)(\d{6,})"), ("t-online.de", r"id_(\d{6,})"),
 ("rnd.de", r"-([a-z0-9]{26})\.html"), ("abcnews.go.com", r"-(\d{6,10})$"),
 ("nbcnews.com", r"(rcna\d+|ncna\d+)"), ("yahoo.com", r"-(\d{9})\.html"),
 ("usatoday.com", r"/(\d{10,12})$"), ("apnews.com", r"([0-9a-f]{32})"),
 ("zdf.de", r"/([a-z0-9-]+-1\d\d\.html)$"),
]


def key(url):
    n = norm_url(url)
    if LIVE_RE.search(url or "") and not WIRE_FEED_RE.search(url or "") and "t-online.de" not in n:
        # RND reuses one ID across per-day ticker pages (date in slug): key on full URL.
        # t-online's newsblog is ONE rolling page whose slug follows the latest headline: keep the ID key.
        return n
    host = n.split("/", 1)[0]
    for h, pat in KEYS:
        if host == h:
            m = re.search(pat, n)
            if m:
                return f"{h}#{m.group(1)}"
    return n


def norm_title(t):
    t = H.unescape(t or "").lower()
    t = re.sub(r"\s*[|–-]\s*(tagesschau\.de|zdfheute|der spiegel|welt|bild|n-tv\.de|t-online|rnd\.de|cnn|fox news|"
               r"abc news|cbs news|nbc news|the new york times|the washington post|ap news|reuters|usa today|yahoo news).*$", "", t)
    t = re.sub(r"[^a-z0-9äöüß ]+", " ", t)
    return " ".join(t.split())


def load_ours(country):
    D = ROOT / country
    corpus, cands, manifest = {}, {}, {}
    for l in open(D / "06-corpus/corpus.jsonl", encoding="utf-8"):
        r = json.loads(l)
        k = key(r["publication"]["canonical_url"])
        prev = corpus.get(k)
        if prev is None or (r["deduplication"]["is_primary_record"] and not prev["deduplication"]["is_primary_record"]):
            corpus[k] = r
    for l in open(D / "05-extraction/candidates.jsonl", encoding="utf-8"):
        r = json.loads(l)
        cands.setdefault(key(r["url"]), r)
    for f in glob.glob(str(D / "04-enumeration" / "*-urls.csv")):
        o = Path(f).name.replace("-urls.csv", "")
        for r in csv.DictReader(open(f, encoding="utf-8")):
            manifest.setdefault(key(r["url"]), (o, r["url"], r.get("event_candidate", ""), r.get("source", "")))
    return corpus, cands, manifest


# ---------------- term detection ----------------
STRONG = {
 "germany": re.compile(r"pager|piepser|funkger(?:ä|ae)t|walkie|gold[\s-]apollo", re.I),
 "us": re.compile(r"\bpagers?\b|\bbeepers?\b|walkie|gold[\s-]apollo|\bicom\b", re.I),
}
WEAK = {
 "germany": re.compile(r"(kommunikationsger(?:ä|ae)t|explodierende[nrm]?\s+(?:\w+\s+)?ger(?:ä|ae)t|"
                       r"elektronische[nrm]?\s+ger(?:ä|ae)te|ger(?:ä|ae)te-?(?:explosion|angriff|attack)|"
                       r"(?:explosion|detonation)\w*\W+(?:\w+\W+){0,5}?ger(?:ä|ae)t|"
                       r"(?:angriff|attacke|anschl(?:ä|ae)g)\w*\s+auf\s+(?:\w+\s+){0,2}?(?:technische|elektronische|tragbare|kommunikations)\w*\s*ger(?:ä|ae)te|"
                       r"ger(?:ä|ae)te?n?\W+(?:\w+\W+){0,5}?(?:explodier|detonier|in die luft))", re.I),
 "us": re.compile(r"((?:exploding|booby[- ]trapped|rigged|explosive[- ]laden)\s+(?:\w+\s+)?(?:devices|radios|gadgets)|"
                  r"device (?:explosions|attacks|blasts|detonations)|handheld radios|communications? devices?|"
                  r"(?:explosions?|blasts?|detonations?|attacks?)\s+(?:\w+\s+){0,5}?(?:devices|radios|gadgets)|"
                  r"(?:devices|radios|gadgets)\s+(?:\w+\s+){0,5}?(?:explod|detonat|blew up))", re.I),
}
CTX = re.compile(r"libanon|hisbollah|hezbollah|lebanon|beirut|lebanese|libanesisch", re.I)


def has_mention(text, country):
    if not text:
        return None
    m = STRONG[country].search(text)
    if m:
        return m
    for w in WEAK[country].finditer(text):
        ctx = text[max(0, w.start() - 400): w.end() + 400]
        if CTX.search(ctx):
            return w
    return None


# ---------------- body extraction ----------------
def ldjson_items(t):
    out = []
    for m in re.finditer(r'<script[^>]*type="application/ld\+json"[^>]*>(.*?)</script>', t, re.S | re.I):
        try:
            d = json.loads(m.group(1).strip())
        except Exception:
            continue
        stack = d if isinstance(d, list) else [d]
        while stack:
            it = stack.pop()
            if isinstance(it, list):
                stack.extend(it); continue
            if not isinstance(it, dict):
                continue
            if "@graph" in it:
                stack.extend(it["@graph"] if isinstance(it["@graph"], list) else [it["@graph"]])
            out.append(it)
    return out


def meta(t, name):
    m = (re.search(r'<meta[^>]+(?:property|name)="%s"[^>]+content="([^"]*)"' % re.escape(name), t, re.I) or
         re.search(r'<meta[^>]+content="([^"]*)"[^>]+(?:property|name)="%s"' % re.escape(name), t, re.I))
    return H.unescape(m.group(1)).strip() if m else ""


def strip_tags(s):
    return " ".join(H.unescape(re.sub(r"<[^>]+>", " ", s)).split())


def extract(t):
    """Return dict(title, desc, date, body, body_src, paras[(text, nonlink_text)], is_liveblog_ld)."""
    items = ldjson_items(t)
    title = desc = date = ""
    body = ""
    live = False
    for it in items:
        typ = it.get("@type")
        typ = typ if isinstance(typ, list) else [typ]
        if any(x in ("NewsArticle", "Article", "ReportageNewsArticle", "LiveBlogPosting", "VideoObject",
                     "AnalysisNewsArticle", "OpinionNewsArticle", "WebPage", "BlogPosting") for x in typ):
            if "LiveBlogPosting" in typ:
                live = True
            title = title or H.unescape(str(it.get("headline") or it.get("name") or ""))
            desc = desc or H.unescape(str(it.get("description") or ""))
            date = date or str(it.get("datePublished") or it.get("uploadDate") or "")[:19]
            ab = it.get("articleBody")
            if isinstance(ab, str) and len(ab.split()) > len(body.split()):
                body = ab
            for up in it.get("liveBlogUpdate") or []:
                if isinstance(up, dict):
                    body += " " + str(up.get("headline") or "") + " " + str(up.get("articleBody") or "")
    title = title or meta(t, "og:title") or (strip_tags(re.search(r"<title>(.*?)</title>", t, re.S).group(1))
                                            if re.search(r"<title>(.*?)</title>", t, re.S) else "")
    desc = desc or meta(t, "og:description") or meta(t, "description")
    date = date or meta(t, "article:published_time") or meta(t, "datePublished") or meta(t, "date")
    scope = t
    am = re.search(r"<article\b.*</article>", t, re.S | re.I)
    if am and len(am.group(0)) > 3000:
        scope = am.group(0)
    scope = re.sub(r"<script.*?</script>|<style.*?</style>|<nav.*?</nav>|<footer.*?</footer>|<aside.*?</aside>",
                   " ", scope, flags=re.S | re.I)
    paras = []
    for p in re.findall(r"<(?:p|li|h2|h3)\b[^>]*>(.*?)</(?:p|li|h2|h3)>", scope, re.S | re.I):
        full = strip_tags(p)
        nonlink = strip_tags(re.sub(r"<a\b.*?</a>", " ", p, flags=re.S | re.I))
        if len(full.split()) >= 4:
            paras.append((full, nonlink))
    body_src = "ld-json" if len(body.split()) >= 60 else "p"
    if body_src == "p":
        body = " ".join(p for p, _ in paras)
    can = (re.search(r'<link[^>]+rel="canonical"[^>]+href="([^"]+)"', t) or re.search(r'<link[^>]+href="([^"]+)"[^>]+rel="canonical"', t))
    canonical = H.unescape(can.group(1)) if can else meta(t, "og:url")
    canonical = re.sub(r"^https?://web\.archive\.org/web/\d+(id_)?/", "", canonical or "")
    paywall = bool(re.search(r'"isAccessibleForFree"\s*:\s*"?(false|False)', t)) or \
        bool(re.search(r"\(S\+\)|SPIEGEL\+|WELTplus|BILDplus|BILD\+", title + " " + t[:3000]))
    return dict(title=strip_tags(title), desc=strip_tags(desc), date=date, body=" ".join(H.unescape(body).split()),
                body_src=body_src, paras=paras, live_ld=live, paywall=paywall, canonical=canonical)


def para_sig(nonlink):
    """Signature of a paragraph for boilerplate detection (see recall_audit_build.boilerplate)."""
    return " ".join(nonlink.split())[:160]


def assess(ex, country, skip=None):
    """Substantive-mention check. Returns (mention: bool|None, central: bool, evidence str, note).
    skip: optional set of paragraph signatures (para_sig) that are site chrome for this outlet."""
    head = f"{ex['title']} {ex['desc']}"
    if skip and ex["body_src"] != "ld-json":
        kept = [(f, n) for f, n in ex["paras"] if para_sig(n) not in skip]
        if len(kept) < len(ex["paras"]):
            ex = dict(ex, paras=kept)
    if ex["body_src"] == "ld-json":
        m = has_mention(ex["body"], country)
        lead = ex["body"][:700]
        ev = ex["body"][max(0, m.start() - 120): m.end() + 120] if m else ""
        mention = bool(m) or bool(has_mention(head, country))
    else:
        mention, ev, link_only = False, "", False
        for full, nonlink in ex["paras"]:
            if has_mention(full, country):
                mm = has_mention(nonlink, country)
                if mm and len(nonlink.split()) >= 8:
                    mention, ev = True, nonlink[max(0, mm.start() - 150): mm.end() + 150]
                    break
                link_only = True
        if not mention and has_mention(head, country):
            mention, ev = True, "[headline/description] " + head[:250]
        lead = " ".join(p for p, _ in ex["paras"][:3])[:700]
        if not mention and link_only:
            return False, False, "", "term only inside link text (teaser/related link)"
    central = bool(has_mention(head, country)) or bool(has_mention(lead, country))
    return mention, central, " ".join(ev.split())[:300], ""


LIVE_RE = re.compile(r"liveblog|live-blog|newsticker|liveticker|live-ticker|/live/|/live-news/|live-updates|"
                     r"/live-story|newsblog|nahost-news|-news-ticker", re.I)
LIVE_TITLE_RE = re.compile(r"liveblog|live-?ticker|newsblog|news-?ticker|live updates|\blive:|im liveblog|\+\+", re.I)


WIRE_FEED_RE = re.compile(r"welt\.de/newsticker/dpa_nt/|/HBBTV/Teletext/|n-tv\.de/ticker/", re.I)


def is_wire_feed(url):
    """Automated single-item feeds (WELT dpa newsticker pages, RTL teletext pages): articles, not live blogs."""
    return bool(WIRE_FEED_RE.search(url or ""))


def is_liveblog(url, title=""):
    if is_wire_feed(url):
        return False
    return bool(LIVE_RE.search(url or "")) or bool(LIVE_TITLE_RE.search(title or ""))
