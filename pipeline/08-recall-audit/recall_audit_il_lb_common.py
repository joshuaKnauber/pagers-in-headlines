#!/usr/bin/env python3
"""Shared helpers for the Israel/Lebanon recall audit (recall_audit_il_lb_*.py).

- url_key(): outlet-aware canonical keys (article IDs), so that aliases,
  section mirrors (mako pzm-soldiers vs news-military), mobile/AMP variants,
  query strings and slug/encoding differences collapse onto one item.
- load_ours(): our pipeline's knowledge of every key: corpus (primary or
  not), candidates (and why dropped), manifest (tagged or not), titles.
- fetch(): cached polite fetcher; Wayback 504/offline pages detected by body.
- body(): container-first body extraction (JSON-LD articleBody > outlet
  container > p-cluster), so related-link chrome does not count as mention.
- device_hits(): device-term matcher (he/ar/en/fr) with snippets.
"""
import csv, glob, hashlib, html as H, json, re, threading, time, urllib.parse, urllib.request
from pathlib import Path

DATA = Path(__file__).resolve().parents[2] / "data"
UA = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124 Safari/537.36 research-collection"}
csv.field_size_limit(10**9)

HOSTS = {
    "ynet": ["ynet.co.il"], "n12": ["mako.co.il", "n12.co.il"], "kikar": ["kikar.co.il"],
    "makan": ["makan.org.il", "kan.org.il"], "abuali": ["t.me"],
    "lbci": ["lbcgroup.tv"], "mtv": ["mtv.com.lb"], "aljadeed": ["aljadeed.tv"],
    "almanar": ["almanar.com.lb"], "nna": ["nna-leb.gov.lb"],
    "akhbar": ["al-akhbar.com"], "nidaa": ["nidaalwatan.com"], "annahar": ["annahar.com"],
    "olj": ["lorientlejour.com", "lorientoday.com"],
}
COUNTRY = {"israel": ["ynet", "n12", "kikar", "makan", "abuali"],
           "lebanon": ["lbci", "mtv", "aljadeed", "almanar", "nna"]}
LONGFORM = ["akhbar", "nidaa", "annahar", "olj"]


def outlet_of(url):
    host = urllib.parse.urlsplit(url).netloc.lower().split(":")[0]
    for o, hs in HOSTS.items():
        if any(host == h or host.endswith("." + h) for h in hs):
            return o
    return None


def url_key(url):
    """Canonical item key. Returns e.g. 'ynet:sjhba8dta', 'n12:20a0da95f750291026'."""
    u = urllib.parse.unquote(url.strip())
    u = re.sub(r"^https?://web\.archive\.org/web/\d+[a-z_]*/", "", u)
    sp = urllib.parse.urlsplit(u if "://" in u else "https://" + u)
    host = sp.netloc.lower().split(":")[0]
    path = sp.path
    o = outlet_of("https://" + host)
    if o == "ynet":
        m = re.search(r"/article/([A-Za-z0-9]+)", path)
        if m:
            return "ynet:" + m.group(1).lower()
    if o == "n12":
        m = re.search(r"Article-([0-9a-f]+)\.htm", path, re.I)
        if m:
            return "n12:" + m.group(1).lower()
    if o == "kikar":
        m = re.search(r"/([a-z0-9]{4,10})/?$", path)
        if m:
            return "kikar:" + m.group(1).lower()
    if o == "makan":
        m = re.search(r"/(\d{4,})/?$", path)
        if m:
            return "makan:" + m.group(1)
    if o in ("lbci", "aljadeed"):
        m = re.search(r"/news/[^/]+/(\d+)", path) or re.search(r"/(\d{5,})(?:/|$)", path)
        if m:
            lang = "en" if path.rstrip("/").endswith("/en") else ""
            return f"{o}:{m.group(1)}{'/en' if lang else ''}"
    if o == "mtv":
        m = re.search(r"/news/(?:[^/]+/)?(\d{5,})", path, re.I)
        if m:
            return "mtv:" + m.group(1)
    if o == "almanar":
        m = re.search(r"/(\d{6,})/?$", path)
        if m:
            sub = host.replace("www.", "").replace("archive.", "")
            ed = "" if sub == "almanar.com.lb" else sub.split(".")[0] + "/"
            return f"almanar:{ed}{m.group(1)}"
    if o == "nna":
        m = re.search(r"/(\d{5,})(?:/|$)", path)
        if m:
            return "nna:" + m.group(1)
    if o == "akhbar":
        m = re.search(r"/(\d{5,})(?:/|$)", path)
        if m:
            return "akhbar:" + m.group(1)
    if o == "annahar":
        m = re.search(r"/(\d{6,})(?:/|$)", path)
        if m:
            return "annahar:" + m.group(1)
    if o == "olj":
        m = re.search(r"/article/(\d+)", path)
        if m:
            return "olj:" + m.group(1)
    if o == "nidaa":
        m = re.search(r"/(?:node|article)/(\d+)", path) or re.search(r"/(\d{4,})(?:/|-|$)", path)
        if m:
            return "nidaa:" + m.group(1)
    return f"{o or host}:" + host.replace("www.", "").replace("m.", "", 1 if host.startswith("m.") else 0) + path.rstrip("/").lower()


# ---------------------------------------------------------------- our data
def _norm_title(t):
    t = H.unescape(t or "")
    t = re.sub(r"\s*[|\-–—]\s*(N12|ynet|כיכר השבת|Lebanon News|MTV Lebanon|موقع قناة المنار.*|Fashion Forward).*$", "", t)
    t = re.sub(r"^N12\s*-\s*", "", t)
    t = re.sub(r"[֑-ׇً-ْـ]", "", t)  # niqqud, harakat, tatweel
    t = re.sub(r"[^\w\s]", " ", t)
    return " ".join(t.lower().split())


def load_ours(country):
    """key -> dict(status_pipeline, document_id, title, is_primary, relevance, tagged, manifest_title)."""
    base = DATA / country
    ours = {}

    def get(k):
        return ours.setdefault(k, {"in_manifest": False, "tagged": False, "candidate": None,
                                   "corpus": None, "titles": set()})
    # manifests
    for f in glob.glob(str(base / "04-enumeration" / "*-urls.csv")):
        outlet = Path(f).name.split("-")[0]
        if outlet == "almanar" and f.endswith("raw.csv"):
            continue
        for r in csv.DictReader(open(f, encoding="utf-8")):
            k = url_key(r["url"])
            d = get(k)
            d["in_manifest"] = True
            d["manifest_url"] = r["url"]
            d["first_capture"] = r.get("first_capture", "")
            if r.get("event_candidate") == "1":
                d["tagged"] = True
            if country == "lebanon":
                slug = urllib.parse.unquote(r["url"]).rstrip("/").split("/")[-1]
                if slug in ("ar", "en"):
                    slug = urllib.parse.unquote(r["url"]).rstrip("/").split("/")[-2]
                d["titles"].add(slug.replace("-", " ").replace("_", " "))
    for f in glob.glob(str(base / "04-enumeration" / "*-titles*.csv")):
        for r in csv.DictReader(open(f, encoding="utf-8")):
            k = url_key(r["url"])
            d = get(k)
            if r.get("title"):
                d["titles"].add(r["title"])
                d.setdefault("sweep_title", r["title"])
            if r.get("relevance"):
                d["tagged"] = True
    # candidates
    p = base / "05-extraction/candidates.jsonl"
    for line in open(p, encoding="utf-8"):
        r = json.loads(line)
        k = url_key(r["url"])
        d = get(k)
        d["candidate"] = r
        if r.get("title"):
            d["titles"].add(r["title"])
    # corpus
    for line in open(base / "06-corpus/corpus.jsonl", encoding="utf-8"):
        r = json.loads(line)
        k = url_key(r["publication"]["canonical_url"])
        d = get(k)
        prev = d["corpus"]
        if prev is None or (r["deduplication"]["is_primary_record"] and not prev["deduplication"]["is_primary_record"]):
            d["corpus"] = r
        d["titles"].add(r["content"]["headline"])
    for d in ours.values():
        d["ntitles"] = {_norm_title(t) for t in d["titles"] if t}
    return ours


def corpus_title_index(country):
    """normalised headline -> key, for fuzzy fallback."""
    idx = {}
    for line in open(DATA / country / "06-corpus/corpus.jsonl", encoding="utf-8"):
        r = json.loads(line)
        idx[_norm_title(r["content"]["headline"])] = url_key(r["publication"]["canonical_url"])
    return idx


def fuzzy_title_match(title, ours, outlet, thresh=0.82):
    """Token-set similarity over titles of items of the same outlet."""
    nt = _norm_title(title)
    if len(nt) < 12:
        return None, 0.0
    a = set(nt.split())
    best, bk = 0.0, None
    for k, d in ours.items():
        if not k.startswith(outlet + ":"):
            continue
        for t in d["ntitles"]:
            b = set(t.split())
            if not b:
                continue
            s = len(a & b) / max(1, min(len(a), len(b)))
            j = len(a & b) / max(1, len(a | b))
            sc = 0.5 * s + 0.5 * j
            if sc > best:
                best, bk = sc, k
    return (bk, best) if best >= thresh else (None, best)


def pipeline_status(d):
    """Map our pipeline's knowledge of a key onto the audit status vocabulary."""
    if d is None:
        return "not_in_manifest", ""
    c = d.get("corpus")
    if c is not None:
        if c["deduplication"]["is_primary_record"]:
            return "in_corpus", c["document_id"]
        return "in_corpus", c["document_id"] + " (non-primary duplicate)"
    cand = d.get("candidate")
    if cand is not None:
        return "in_candidates_dropped", f"candidate relevance={cand.get('relevance')}"
    if d.get("in_manifest"):
        if d.get("tagged"):
            return "in_candidates_dropped", "tagged in manifest/title sweep but never extracted"
        return "in_manifest_not_candidate", ""
    return "not_in_manifest", ""


# ---------------------------------------------------------------- fetching
_locks = {}
_last = {}
import os
GAPS = {"web.archive.org": float(os.environ.get("WB_GAP", "1.05"))}


def _throttle(host):
    lk = _locks.setdefault(host, threading.Lock())
    with lk:
        gap = GAPS.get(host, 0.6)
        w = gap - (time.time() - _last.get(host, 0))
        if w > 0:
            time.sleep(w)
        _last[host] = time.time()


def bad_wayback(t):
    head = t[:4000]
    return ("Temporarily Offline" in head or "504 Gateway Time-out" in head or
            ("<center>nginx</center>" in t[:3000] and len(t) < 5000) or
            "Wayback Machine has not archived that URL" in t or "Hrm." in head and "Wayback Machine" in head)


def fetch(url, cache_dir, timeout=45, tries=3, headers=None):
    """Return (html or None, info). Cache keyed by url sha."""
    cache_dir = Path(cache_dir)
    cache_dir.mkdir(parents=True, exist_ok=True)
    fn = cache_dir / (hashlib.sha256(url.encode()).hexdigest()[:16] + ".html")
    if fn.exists() and fn.stat().st_size > 500:
        return fn.read_text(encoding="utf-8", errors="replace"), "cache"
    host = urllib.parse.urlsplit(url).netloc
    info = ""
    for i in range(tries):
        _throttle(host)
        try:
            req = urllib.request.Request(url, headers=headers or UA)
            with urllib.request.urlopen(req, timeout=timeout) as r:
                raw = r.read()
                final = r.geturl()
            if raw[:2] == b"\x1f\x8b":
                import gzip
                raw = gzip.decompress(raw)
            t = raw.decode("utf-8", "replace")
            if "web.archive.org" in host and bad_wayback(t):
                info = "wayback-error-page"
                time.sleep(8 * (i + 1))
                continue
            fn.write_text(t, encoding="utf-8")
            return t, "ok" + ("" if final == url else f" -> {final}")
        except urllib.error.HTTPError as e:
            info = f"HTTP {e.code}"
            if e.code in (404, 410, 403):
                break
            time.sleep(6 * (i + 1))
        except Exception as e:
            info = type(e).__name__ + ":" + str(e)[:80]
            if "archive.org" in host and ("refused" in str(e) or "timed out" in str(e)):
                time.sleep(25 * (i + 1))   # IA connection refusal = rate limiting; back off hard
            else:
                time.sleep(6 * (i + 1))
    return None, info


def wayback_url(url, ts="20240918"):
    return f"https://web.archive.org/web/{ts}/{url}"


def wayback_avail(url, ts="20240918"):
    """Nearest capture via CDX (status 200)."""
    q = ("https://web.archive.org/cdx/search/cdx?url=" + urllib.parse.quote(url, safe="") +
         "&filter=statuscode:200&fl=timestamp,original&limit=5&from=2024&to=2025")
    _throttle("web.archive.org")
    try:
        t = urllib.request.urlopen(urllib.request.Request(q, headers=UA), timeout=60).read().decode()
    except Exception as e:
        return None
    rows = [l.split() for l in t.splitlines() if l.strip() and not l.startswith("<")]
    if not rows:
        return None
    rows.sort(key=lambda r: abs(int(r[0][:8]) - int(ts)))
    return rows[0][0]


# ---------------------------------------------------------------- extraction
def _strip(seg):
    seg = re.sub(r"<script.*?</script>|<style.*?</style>|<figure.*?</figure>|<aside.*?</aside>", " ", seg, flags=re.S | re.I)
    seg = re.sub(r"<br\s*/?>|</p>|</div>|</li>", "\n", seg, flags=re.I)
    seg = H.unescape(re.sub(r"<[^>]+>", " ", seg))
    return "\n".join(" ".join(l.split()) for l in seg.splitlines() if l.strip())


def ld_items(t):
    out = []
    for m in re.finditer(r'<script[^>]*application/ld\+json[^>]*>(.*?)</script>', t, re.S):
        try:
            d = json.loads(m.group(1).strip())
        except Exception:
            continue
        stack = d if isinstance(d, list) else [d]
        for it in stack:
            if isinstance(it, dict):
                if "@graph" in it and isinstance(it["@graph"], list):
                    out.extend(x for x in it["@graph"] if isinstance(x, dict))
                out.append(it)
    return out


CONTAINERS = {
    "kikar": [('class="article-content', "</article>")],
    "n12": [('itemprop="articleBody"', "</article>")],
    "makan": [('class="article-content', "</article>"), ('class="text-content', "</section>")],
    "lbci": [('class="LongDesc', "</section>"), ('itemprop="articleBody"', "</section>")],
    "aljadeed": [('class="LongDesc', "</section>"), ('itemprop="articleBody"', "</section>")],
    "mtv": [('class="articles-report', '<div class="articles-tags'), ('class="articles-report', "</section>")],
    "almanar": [('<div class="article-content">', '<div class="article-tags'), ('<div class="article-content">', "</article>")],
    "nna": [('class="news-details', '<div class="share'), ('class="article-content', "</article>")],
    "akhbar": [('class="article-body', "</article>"), ('class="field-name-body', "</section>")],
    "annahar": [('class="articleMainText', "</div>\n</div>"), ('itemprop="articleBody"', "</article>")],
    "olj": [('class="article_body', "</article>"), ('class="article-body', "</article>")],
}


def balanced(t, i):
    """Slice of the element whose opening tag contains position i (nesting-aware)."""
    a = i if t[i:i + 1] == "<" else t.rfind("<", 0, i)
    m = re.match(r"<([a-zA-Z0-9]+)", t[a:a + 20]) if a >= 0 else None
    if not m:
        return None
    tag = m.group(1).lower()
    rx = re.compile(r"<(/?)%s\b[^>]*?(/?)>" % tag, re.I)
    depth = 0
    for mm in rx.finditer(t, a):
        if mm.group(2):
            continue
        depth += -1 if mm.group(1) else 1
        if depth == 0:
            return t[a:mm.end()]
    return None


def meta(t, prop):
    m = (re.search(r'<meta[^>]+(?:property|name)="%s"[^>]+content="([^"]*)"' % re.escape(prop), t) or
         re.search(r'<meta[^>]+content="([^"]*)"[^>]+(?:property|name)="%s"' % re.escape(prop), t))
    return H.unescape(m.group(1)).strip() if m else ""


def extract(outlet, t):
    """Return dict(title, date, body, method)."""
    title, date, body, method = "", "", "", ""
    for it in ld_items(t):
        typ = it.get("@type")
        typ = typ if isinstance(typ, str) else (typ[0] if isinstance(typ, list) and typ else "")
        if typ in ("NewsArticle", "Article", "ReportageNewsArticle", "BlogPosting", "LiveBlogPosting", "WebPage"):
            if it.get("datePublished") and not date:
                date = str(it["datePublished"])
            if it.get("headline") and not title and typ != "WebPage":
                title = H.unescape(str(it["headline"]))
            if it.get("articleBody") and not body:
                body = H.unescape(re.sub(r"<[^>]+>", " ", str(it["articleBody"])))
                method = "ld-json"
    if not title:
        title = meta(t, "og:title")
        if not title:
            m = re.search(r"<title>([^<]{3,400})</title>", t)
            title = H.unescape(m.group(1)).strip() if m else ""
    if not date:
        date = meta(t, "article:published_time") or meta(t, "publishdate") or meta(t, "pubdate")
    if not body or len(body.split()) < 8:
        seen_start = set()
        for start, end in CONTAINERS.get(outlet, []):
            i = t.find(start)
            if i < 0 or start in seen_start:
                continue
            seen_start.add(start)
            seg = balanced(t, i)
            if seg is None:
                j = t.find(end, i + len(start))
                seg = t[i:j if j > i else i + 60000]
            b = _strip(seg[seg.find(">") + 1:])
            if len(b.split()) >= 5:
                body, method = b, "container"
                break
            if seg is not None and len(b.split()) < 5:
                method = "container-empty"   # empty node: try other markers, never the chrome slice
    if not body and method != "container-empty":
        bb = re.sub(r"<script.*?</script>|<style.*?</style>|<header.*?</header>|<footer.*?</footer>|<nav.*?</nav>|<aside.*?</aside>", " ", t, flags=re.S | re.I)
        ps = [_strip(p) for p in re.findall(r"<p[^>]*>(.*?)</p>", bb, re.S)]
        body = "\n".join(p for p in ps if len(p.split()) > 4)
        method = "p-cluster"
    desc = meta(t, "og:description") or meta(t, "description")
    return {"title": title.strip(), "date": date, "body": body.strip(), "method": method, "desc": desc}


# ---------------------------------------------------------------- relevance
# Device / event-name terms. STRONG count anywhere; WEAK (generic "radio /
# communication devices") count only when the same text carries a blast co-term.
STRONG = [
    r"ביפר", r"איתורי(?:ת|ות)", r"זימוני(?:ת|ות)", r"ווקי[ -]?טוקי", r"גולד אפולו", r"איקום",
    r"بيجر", r"بايجر", r"بيجرز", r"(?:أ|ا)جهزة (?:ال)?نداء", r"ووكي ?توكي", r"الووكي", r"(?:غ|ج)ولد (?:أ|ا)بولو",
    r"آيكوم|ايكوم|أيكوم", r"مجزر\w* (?:يوم )?(?:ال)?ثلاثاء", r"مجزر\w* (?:يوم )?(?:ال)?(?:أ|ا)ربعاء", r"مجزرت(?:ي|ين) (?:ال)?ثلاثاء", r"(?:العدوان|الاعتداء|الهجوم) السيبراني",
    r"(?<![a-z])pagers?(?![a-z])", r"(?<![a-z])beepers?(?![a-z])", r"walkie[- ]?talkies?", r"talkies?[- ]walkies?",
    r"gold apollo", r"(?<![a-z])icom(?![a-z])", r"(?<![a-z])bipeurs?(?![a-z])", r"exploding devices",
]
WEAK = [
    r"מכשיר(?:י)? (?:ה)?קשר", r"מכשיר(?:י)? (?:ה)?רדיו", r"(?:ה)?מכשירים (?:ש)?(?:התפוצצו|פוצצו)", r"מתקפת (?:ה)?מכשירים",
    r"פיצוצי (?:ה)?מכשירים",
    r"لاسلكي", r"اللاسلكي", r"لاسلكية", r"(?:أ|ا)جهز(?:ة|ه) (?:ال)?اتصال(?:ات)?", r"وسائل (?:ال)?اتصال(?:ات)?",
    r"الخرق (?:ال)?(?:أ|ا)مني", r"(?:أ|ا)جهزة (?:ال)?(?:ب|پ)يجر", r"تفجير(?:ات)? (?:ال)?(?:أ|ا)جهزة",
    r"انفجار(?:ات)? (?:ال)?(?:أ|ا)جهزة",
    r"device (?:explosions|blasts|attacks)", r"wireless devices", r"communication devices",
]
COTERM = re.compile(r"פיצו|התפוצצ|התפוצץ|פוצץ|נפץ|מלכוד|ממולכ|פוצצ|تفجير|انفجار|انفجرت|تفجيرات|انفجارات|مفخخ|فجّر|فجر|هجمات|هجوم|اعتداء|العدوان|explo|blast|detonat|attack", re.I)
STRONG_RE = re.compile("|".join(STRONG), re.I)
WEAK_RE = re.compile("|".join(WEAK), re.I)
CORE_RE = re.compile("|".join(STRONG + WEAK), re.I)
ARNORM = re.compile(r"[\u064B-\u0652\u0670\u0640\u0591-\u05C7\u200f\u200e]")


def device_hits(text, context=None):
    """Return (n_hits, snippets). WEAK terms count only if text (or context) has a blast co-term."""
    text = ARNORM.sub("", text or "")
    hits = list(STRONG_RE.finditer(text))
    if COTERM.search(text) or (context and COTERM.search(ARNORM.sub("", context))):
        hits += list(WEAK_RE.finditer(text))
    hits.sort(key=lambda m: m.start())
    # collapse hits within 80 chars of each other into one mention cluster
    clusters, last = [], -10**9
    for m in hits:
        if m.start() - last > 80:
            clusters.append(m)
        last = m.end()
    hits = clusters
    snips = []
    for m in hits[:6]:
        a, b = max(0, m.start() - 70), min(len(text), m.end() + 70)
        snips.append(text[a:b].replace("\n", " "))
    return len(hits), snips


def classify(title, body):
    """central / mention / none from title+body device hits (pre-review)."""
    nt, _ = device_hits(title, body)
    nb, _ = device_hits(body, title)
    lead = " ".join(body.split()[:60])
    nl, _ = device_hits(lead, title + " " + body)
    if nt or nl or nb >= 3:
        return "central"
    if nb:
        return "mention"
    return "none"
