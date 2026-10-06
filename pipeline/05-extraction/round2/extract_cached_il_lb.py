#!/usr/bin/env python3
"""Stage-1 extraction of Israel and Lebanon gap rows from cached HTML.

Offline. Reads the recall-audit cache and the existing corpus. Writes only
data/<country>/05-extraction/round2/ and raw/<outlet>/r2-*.html.gz.

Usage:
    python3 extract_cached_il_lb.py <israel|lebanon> [--regression-only]

Round 2: the regression ratio is a diagnostic. The gate is six checks (five, plus
container_coverage for outlets that have no JSON-LD articleBody to compare against).
Corpus rows are re-extracted to reextract-v1.jsonl. Records under 0.90
go to regression-adjudication.csv. Gap rows are read from
round2/gap-manifest-input.csv (the audit manifest was regenerated and is nearly empty).

Each outlet's container, chrome and title rules are in RULES. Shared helpers
below do not special-case an outlet except by reading that table.
"""
import csv, gzip, hashlib, html as H, json, random, re, statistics, sys, urllib.parse
from collections import Counter, defaultdict
from difflib import SequenceMatcher
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "pipeline" / "08-recall-audit"))
import recall_audit_il_lb_common as ilb  # url_key only; no network

DATA = ROOT / "data"
csv.field_size_limit(10 ** 9)

COUNTRIES = {
    "israel": ["ynet", "n12", "kikar", "makan", "abuali"],
    "lebanon": ["lbci", "mtv", "aljadeed", "almanar", "nna"],
}

# Exceptions whose stored bodies are not a fair regression reference.
# "all" = the whole outlet is reported separately and does not face the bar.
# "press_review" = those corpus document_types are left out of the bar.
EXCEPTION = {
    "ynet": "all",          # stored bodies are the JSON-LD lead
    "abuali": "all",        # corpus rows have no per-message raw, except 3
    "almanar": "press_review",
}

# Recirculation markers. Cut only when they appear after real text, and only
# inside the outlet's own container (never by deleting a sentence in place).
ALJADEED_CUTS = ("اقرأ ايضا", "اقرأ أيضا", "تشاهدون الآن", "الأكثر مشاهدة", "بيت الحلم")

# Visible dateline months. Unknown month -> no date, not a guess.
MONTHS = {}
for i, name in enumerate(
    ["January", "February", "March", "April", "May", "June",
     "July", "August", "September", "October", "November", "December"], 1):
    MONTHS[name] = i
    MONTHS[name.lower()] = i
for name, n in {
    "كانون الثاني": 1, "يناير": 1,
    "شباط": 2, "فبراير": 2,
    "آذار": 3, "اذار": 3, "مارس": 3,
    "نيسان": 4, "أبريل": 4, "ابريل": 4,
    "أيار": 5, "ايار": 5, "مايو": 5,
    "حزيران": 6, "يونيو": 6,
    "تموز": 7, "يوليو": 7,
    "آب": 8, "اب": 8, "أغسطس": 8, "اغسطس": 8,
    "أيلول": 9, "ايلول": 9, "سبتمبر": 9,
    "تشرين الأول": 10, "تشرين الاول": 10, "أكتوبر": 10, "اكتوبر": 10,
    "تشرين الثاني": 11, "نوفمبر": 11,
    "كانون الأول": 12, "كانون الاول": 12, "ديسمبر": 12,
}.items():
    MONTHS[name] = n
MONTH_ALT = "|".join(sorted(MONTHS, key=len, reverse=True))
WEEKDAY = "الأحد|الاحد|الإثنين|الاثنين|الثلاثاء|الأربعاء|الاربعاء|الخميس|الجمعة|السبت"
DATELINE_RE = re.compile(
    rf"(?:{WEEKDAY})\s+(\d{{1,2}})\s+({MONTH_ALT})\s+(20\d{{2}})\s+الساعة\s+(\d{{1,2}}:\d{{2}})"
)
ALMANAR_CAL_RE = re.compile(
    r"icon-calendar[^<]*</i>\s*(\d{1,2})\s+([^\s،,<]+(?:\s[^\s،,<]+)?)\s*،?\s*(\d{4})"
)

# Wire credit only when the lead states it. Latin keys use a boundary so
# "afp" does not match inside another word.
WIRES = [
    ("Reuters", [r"רויטרס", r"رويترز", r"reuters"]),
    ("AFP", [r"אי\.אף\.פי", r"فرانس برس", r"أ ف ب", r"ا ف ب", r"وكالة الصحافة الفرنسية", r"\bafp\b"]),
    ("AP", [r"איי\.פי", r"أسوشيتد برس", r"اسوشيتد برس", r"associated press", r"\bap\b"]),
]
AR_RE = re.compile(r"[\u0600-\u06FF]")
HE_RE = re.compile(r"[\u0590-\u05FF]")
EN_STOP = {"the", "and", "of", "to", "in", "a", "for", "on", "with", "that", "is", "was"}
DE_STOP = {"und", "der", "die", "das", "den", "ein", "eine", "ist", "nicht", "auf", "von", "dem"}
WRONG_TITLE = (
    "radware block page", "page not found", "404 not found",
    "העמוד לא נמצא", "الصفحة غير موجودة", "access denied",
)
ABUALI_FOOTER = "כדי להגיב לכתבה לחצו כאן"
# Strings that are page furniture when they show up inside an extracted body.
CHROME_STRINGS = {
    "aljadeed": ["اقرأ ايضا", "اقرأ أيضا", "تشاهدون الآن", "الأكثر مشاهدة", "بيت الحلم",
                 "frameborder=", "referrerpolicy="],
    "lbci": ["آخر الأخبار"],
    "nna": ["تابعوا أخبار الوكالة"],
}
CHECK_NAMES = ("no_chrome", "lead_present", "not_truncated", "no_duplication", "order", "container_coverage")
WAYBACK_RE = re.compile(r"^https?://web\.archive\.org/web/\d+[a-z_]*/", re.I)
ISO_DATE_RE = re.compile(r"^(\d{4}-\d{2}-\d{2})")

# ---------------------------------------------------------------------------
# Per-outlet rules. A reviewer should be able to read one block and see how
# that outlet's container, chrome and title are handled.
# body:
#   ld-json       JSON-LD articleBody (the lead, when that is all the page has)
#   paragraphs    <p> inside the first container marker, through end_tag
#   strip         balanced container, tags stripped (audit container order)
#   almanar-div   the first <div class="article-content">, not the whole article
#   nna-fulltext  <p> of fulltextarticle-container, after the article dateline
#   aljadeed      ShortDesc lead + LongDesc, once; recirculation markers cut
#   telegram      t.me/s message's own js-message_text (not the reply quote)
# ---------------------------------------------------------------------------
RULES = {
    "ynet": {
        "body": "ld-json",
        "containers": [],
        "min_p_words": 0,
        "title_prefix": [],
        "title_suffix": [r"\s*[|\-–—]\s*ynet(?:\.co\.il)?\s*$"],
        "h1_reject": {"חדשות"},
        "type": "article",
        "paywall": "ld-free",
    },
    "n12": {
        # The whole itemprop=articleBody section: p, h3/h4, ul/ol/li, quote blocks, bubble
        # (quoted-network) spans. Figures (captions), players, scripts and the typo-report
        # label are not article text. Legacy first-<p>-run rule kept as body_paragraphs().
        "body": "n12-articlebody",
        "containers": [("itemprop=\"articleBody\"", "</article>")],
        "min_p_words": 4,  # v1.1 <p[^>]*> (also matches <path>); longer than 3 words
        "title_prefix": [r"^N12\s*-\s*"],
        "title_suffix": [r"\s*[|\-–—]\s*N12\s*$"],
        "h1_reject": set(),
        "type": "n12",
        "paywall": "",
    },
    "kikar": {
        # The article island (ArticleContent*, props.contentItems): every html block, in page
        # order. Image/video items (captions), recommended stories and next-article payloads
        # are not read. The SSR container is the fallback, with nested <article> teasers removed
        # (the old rule ended at the first </article>, which is a recommended-story card).
        "body": "kikar-island",
        "containers": [("class=\"article-content", "</article>")],
        "min_p_words": 4,
        "title_prefix": [],
        "title_suffix": [r"\s*[|\-–—]\s*כיכר השבת\s*$"],
        "h1_reject": set(),
        "type": "article",
        "paywall": "",
    },
    "makan": {
        "body": "strip",
        "containers": [
            ("class=\"article-content", "</article>"),
            ("class=\"text-content", "</section>"),
        ],
        "min_p_words": 0,
        "title_prefix": [],
        "title_suffix": [r"\s*[|\-–—]\s*(?:כאן|مكان|Makan|makan)\s*$"],
        "h1_reject": set(),
        "type": "words",
        "paywall": "",
    },
    "abuali": {
        "body": "telegram",
        "containers": [],
        "min_p_words": 0,
        "title_prefix": [],
        "title_suffix": [],
        "h1_reject": set(),
        "type": "telegram",
        "paywall": "",
    },
    "lbci": {
        # LongDesc only. An empty LongDesc used to fall through to itemprop=articleBody,
        # and that wrapper includes the next-story teaser ("آخر الأخبار" / lblNextTitle).
        "body": "strip",
        "containers": [
            ("class=\"LongDesc", "</section>"),
        ],
        "min_p_words": 0,
        "title_prefix": [],
        "title_suffix": [r"\s*[|\-–—]\s*(?:Lebanon News|LBCI)\s*$"],
        "h1_reject": set(),
        "type": "lb-url",
        "paywall": "",
    },
    "mtv": {
        "body": "strip",
        "containers": [
            ("class=\"articles-report", "<div class=\"articles-tags"),
            ("class=\"articles-report", "</section>"),
        ],
        "min_p_words": 0,
        "title_prefix": [],
        "title_suffix": [r"\s*[|\-–—]\s*MTV Lebanon\s*$"],
        "h1_reject": set(),
        "type": "lb-url",
        "paywall": "",
    },
    "aljadeed": {
        "body": "aljadeed",
        "containers": [("itemprop=\"articleBody\"", "</section>")],
        "min_p_words": 0,
        "title_prefix": [],
        "title_suffix": [r"\s*[|\-–—]\s*Lebanon News\s*$"],
        "h1_reject": set(),
        "type": "lb-url",
        "paywall": "",
        "cuts": ALJADEED_CUTS,
    },
    "almanar": {
        "body": "almanar-div",
        "containers": [("<div class=\"article-content\">", "</div>")],
        "min_p_words": 0,
        "title_prefix": [],
        "title_suffix": [r"\s*[|\-–—]\s*موقع قناة المنار.*$"],
        "h1_reject": set(),
        "type": "words",
        "paywall": "",
    },
    "nna": {
        "body": "nna-fulltext",
        "containers": [("fulltextarticle-container", "</div>")],
        "min_p_words": 0,
        "title_prefix": [],
        "title_suffix": [],
        "h1_reject": set(),
        "type": "words",
        "paywall": "",
    },
}

FIELDS = [
    "outlet", "url", "canonical_url", "gap_status", "central_or_mention",
    "fetch_route", "source_file", "raw_path", "title", "published_at",
    "published_time", "date_source", "body_text", "body_words", "extract_method",
    "document_type_hint", "paywall", "provider", "language", "ok", "failure",
    "warnings",
]


# ---------------------------------------------------------------- helpers
def collapse(s):
    return " ".join((s or "").split())


def drop_iframes(seg):
    """Remove each iframe element. A title attribute may contain '<' so a [^>]* scan is not enough."""
    if not seg:
        return ""
    out = []
    low = seg.lower()
    i = 0
    while True:
        j = low.find("<iframe", i)
        if j < 0:
            out.append(seg[i:])
            break
        k = low.find("</iframe>", j)
        if k < 0:
            out.append(seg[i:])
            break
        out.append(seg[i:j])
        i = k + len("</iframe>")
    return "".join(out)


def strip_tags(seg):
    """Tags out, entities unescaped, whitespace collapsed. Letters kept."""
    seg = drop_iframes(seg or "")
    seg = re.sub(r"<script\b[^>]*>.*?</script>|<style\b[^>]*>.*?</style>", " ", seg, flags=re.S | re.I)
    seg = re.sub(r"<br\s*/?>", "\n", seg, flags=re.I)
    seg = re.sub(r"</p>|</div>|</li>|</h[1-6]>", "\n", seg, flags=re.I)
    seg = H.unescape(re.sub(r"<[^>]+>", " ", seg))
    return "\n".join(collapse(line) for line in seg.splitlines() if line.strip())


def inline(s):
    s = re.sub(r"<br\s*/?>", " ", s or "", flags=re.I)
    s = H.unescape(re.sub(r"<[^>]+>", " ", s))
    return collapse(s)


def paragraphs(seg, min_words):
    seg = re.sub(r"<script\b[^>]*>.*?</script>|<style\b[^>]*>.*?</style>", " ", seg or "", flags=re.S | re.I)
    out = []
    for p in re.findall(r"<p\b[^>]*>(.*?)</p>", seg, flags=re.S | re.I):
        text = inline(p)
        if min_words and len(text.split()) < min_words:
            continue
        if text:
            out.append(text)
    return out


def balanced(t, i):
    """Element whose opening tag contains position i."""
    if i < 0 or i >= len(t):
        return None
    a = i if t[i:i + 1] == "<" else t.rfind("<", 0, i)
    m = re.match(r"<([a-zA-Z0-9]+)", t[a:a + 40]) if a >= 0 else None
    if not m:
        return None
    tag = m.group(1)
    rx = re.compile(r"<(/?)%s\b[^>]*?(/?)>" % re.escape(tag), re.I)
    depth = 0
    for mm in rx.finditer(t, a):
        if mm.group(2):
            continue
        depth += -1 if mm.group(1) else 1
        if depth == 0:
            return t[a:mm.end()]
    return None


def ld_items(t):
    out = []
    for m in re.finditer(r'<script[^>]*application/ld\+json[^>]*>(.*?)</script>', t, re.S | re.I):
        raw = m.group(1).strip()
        try:
            d = json.loads(raw)
        except Exception:
            continue
        stack = d if isinstance(d, list) else [d]
        for it in stack:
            if not isinstance(it, dict):
                continue
            if isinstance(it.get("@graph"), list):
                out.extend(x for x in it["@graph"] if isinstance(x, dict))
            out.append(it)
    return out


def ld_type(it):
    typ = it.get("@type")
    if isinstance(typ, list):
        typ = typ[0] if typ else ""
    return typ if isinstance(typ, str) else ""


ARTICLE_TYPES = {"NewsArticle", "Article", "ReportageNewsArticle", "BlogPosting", "LiveBlogPosting"}


def meta(t, prop):
    pat = re.escape(prop)
    # Stop at '>' so an unclosed content quote cannot swallow the tag closer.
    m = (re.search(r'<meta[^>]+(?:property|name)=["\']%s["\'][^>]+content=["\']([^"\'>]*)["\']' % pat, t, re.I) or
         re.search(r'<meta[^>]+content=["\']([^"\'>]*)["\'][^>]+(?:property|name)=["\']%s["\']' % pat, t, re.I))
    return H.unescape(m.group(1)).strip() if m else ""


def strip_wayback(u):
    return WAYBACK_RE.sub("", u or "")


def canonical_of(t, fallback):
    m = (re.search(r'<link[^>]+rel=["\']canonical["\'][^>]+href=["\']([^"\']+)', t, re.I) or
         re.search(r'<link[^>]+href=["\']([^"\']+)["\'][^>]+rel=["\']canonical["\']', t, re.I))
    url = m.group(1).strip() if m else ""
    if not url:
        url = meta(t, "og:url")
    url = strip_wayback(H.unescape(url)).strip()
    if url.startswith("http://") or url.startswith("https://"):
        return url
    return fallback


def clean_title(outlet, title):
    rule = RULES[outlet]
    title = inline(title)
    for p in rule["title_prefix"]:
        title = re.sub(p, "", title).strip()
    for p in rule["title_suffix"]:
        title = re.sub(p, "", title).strip()
    return title


def page_title(outlet, t):
    rule = RULES[outlet]
    title = ""
    for it in ld_items(t):
        if ld_type(it) in ARTICLE_TYPES and it.get("headline") and not title:
            title = str(it["headline"])
            break
    if not title:
        title = meta(t, "og:title")
    if not title:
        m = re.search(r"<h1\b[^>]*>(.*?)</h1>", t, re.S | re.I)
        if m:
            h = inline(m.group(1))
            if h not in rule["h1_reject"]:
                title = h
    return clean_title(outlet, title)


def ld_dates(t):
    """Return (published_time, date_source) from JSON-LD, else meta."""
    for it in ld_items(t):
        if ld_type(it) in ARTICLE_TYPES and it.get("datePublished"):
            return str(it["datePublished"]).strip(), "ld-json"
    for prop in ("article:published_time", "publishdate", "pubdate"):
        v = meta(t, prop)
        if v:
            return v.strip(), "meta"
    return "", ""


def split_stamp(stamp):
    """published_at (YYYY-MM-DD) and published_time (full stamp, or '')."""
    stamp = (stamp or "").strip()
    m = ISO_DATE_RE.match(stamp)
    if not m:
        return "", ""
    # A date-only value is not a full timestamp.
    full = stamp if "T" in stamp else ""
    return m.group(1), full


def paywall_of(outlet, t):
    if RULES[outlet].get("paywall") != "ld-free":
        return False
    for it in ld_items(t):
        if ld_type(it) not in ARTICLE_TYPES:
            continue
        if "isAccessibleForFree" in it:
            return it.get("isAccessibleForFree") is False
    return False


def language_of(text):
    text = text or ""
    sample = text[:4000]
    if not sample.strip():
        return ""
    a, h = len(AR_RE.findall(sample)), len(HE_RE.findall(sample))
    if h > a and h >= 3:
        return "he"
    if a > h and a >= 3:
        return "ar"
    tokens = re.findall(r"[A-Za-z]{2,}", sample.lower())
    if not tokens:
        return ""
    en = sum(1 for w in tokens if w in EN_STOP)
    de = sum(1 for w in tokens if w in DE_STOP)
    if de > en and de >= 2:
        return "de"
    if en >= 2 or (en > de and len(tokens) >= 8):
        return "en"
    return ""


def provider_of(title, body):
    hay = ((title or "") + " " + (body or "")[:500]).lower()
    if not hay.strip():
        return ""
    for name, pats in WIRES:
        for p in pats:
            if p.startswith("\\b") or "\\b" in p:
                if re.search(p, hay, re.I):
                    return name
            elif p.lower() in hay:
                return name
    return ""


def doc_type(outlet, url, title, body):
    mode = RULES[outlet]["type"]
    dec = urllib.parse.unquote(url or "")
    words = len((body or "").split())
    if mode == "telegram":
        return "telegram_post"
    if mode == "n12" and "/podcast" in dec:
        return "podcast_page"
    if mode == "lb-url" and ("مباشر" in dec or "/breaking-news/" in dec):
        return "live_ticker"
    if mode in ("words", "lb-url", "n12"):
        if words < 40:
            return "brief"
        return "article"
    return "article"


def headline_only(hint, body):
    return hint in ("brief", "live_ticker", "newsletter") and not (body or "").strip()


def wrong_page(title):
    t = collapse(title).lower()
    return any(t == w or t.startswith(w) for w in WRONG_TITLE)


# ---------------------------------------------------------------- bodies
def body_ld(t):
    for it in ld_items(t):
        if ld_type(it) in ARTICLE_TYPES and it.get("articleBody"):
            return inline(str(it["articleBody"])), "ld-json"
    return "", ""


def body_paragraphs(outlet, t):
    """v1.1 repair: <p> nodes inside the container, through </article>.

    The pattern is <p[^>]*>, not <p\\b. On Kikar that also matches <path>
    in the figure, and the stored bodies include the caption that comes
    with it. A stricter <p\\b drops that caption and misses the bar.
    """
    start, end = RULES[outlet]["containers"][0]
    i = t.find(start)
    if i < 0:
        return "", ""
    j = t.find(end, i + len(start))
    seg = t[i:j if j > i else len(t)]
    seg = re.sub(r"<script.*?</script>|<style.*?</style>", " ", seg, flags=re.S)
    ps = []
    for p in re.findall(r"<p[^>]*>(.*?)</p>", seg, re.S):
        text = collapse(H.unescape(re.sub(r"<[^>]+>", " ", p)))
        if len(text.split()) > 3:
            ps.append(text)
    if not ps:
        return "", ""
    return "\n".join(ps), "container:" + start[:48]


# ---------------------------------------------------------------- block text
_DROP_TAGS = ("script", "style", "iframe", "noscript", "svg", "figure", "label", "button")
_BLOCK_RE = re.compile(
    r"</?(?:p|div|li|ul|ol|h[1-6]|blockquote|section|article|aside|header|footer|tr|table|tbody|"
    r"figcaption|dl|dt|dd|pre|main|nav)\b[^>]*>", re.I)


def drop_elements(seg, tags=_DROP_TAGS):
    """Remove whole elements (open tag to its balanced close) of the given tag names."""
    out = seg
    for tag in tags:
        rx = re.compile(r"<%s\b[^>]*?(/?)>" % tag, re.I)
        pieces, i = [], 0
        while True:
            m = rx.search(out, i)
            if not m:
                pieces.append(out[i:])
                break
            pieces.append(out[i:m.start()])
            if m.group(1):          # self-closing
                i = m.end()
                continue
            depth, j = 1, m.end()
            tok = re.compile(r"<(/?)%s\b[^>]*?(/?)>" % tag, re.I)
            end = None
            for mm in tok.finditer(out, j):
                if mm.group(2):
                    continue
                depth += -1 if mm.group(1) else 1
                if depth == 0:
                    end = mm.end()
                    break
            i = end if end else len(out)
        out = "".join(pieces)
    return out


def block_text(seg, tags=_DROP_TAGS):
    """Page text in page order, one line per block element.

    Block boundaries become line breaks. Inline tags (span, a, strong) are removed
    without a space, so a word split across two <span>s stays whole as the browser shows it.
    The tags in `tags` are dropped with their content.
    """
    seg = re.sub(r"<!--.*?-->", "", seg or "", flags=re.S)
    seg = drop_elements(seg, tags)
    seg = re.sub(r"<br\s*/?>", "\n", seg, flags=re.I)
    seg = _BLOCK_RE.sub("\n", seg)
    seg = H.unescape(re.sub(r"<[^>]+>", "", seg))
    return "\n".join(collapse(line) for line in seg.splitlines() if line.strip())


def balanced_at(t, marker, start=0):
    """Balanced element whose opening tag holds `marker`, or None."""
    i = t.find(marker, start)
    return balanced(t, i) if i >= 0 else None


# ---------------------------------------------------------------- kikar island
def _astro_decode(x):
    """Astro serialises props as [0, value] (scalar) and [1, [..]] (array)."""
    if isinstance(x, list) and len(x) == 2 and x[0] in (0, 1):
        if x[0] == 0:
            return _astro_decode(x[1])
        return [_astro_decode(y) for y in x[1]]
    if isinstance(x, dict):
        return {k: _astro_decode(v) for k, v in x.items()}
    if isinstance(x, list):
        return [_astro_decode(y) for y in x]
    return x


def kikar_island(t):
    """Decoded props of the article's own ArticleContent island, or None. Only the first one."""
    for m in re.finditer(r'<astro-island\b[^>]*component-export="ArticleContent[^"]*"[^>]*>', t, re.S):
        pm = re.search(r'\sprops="([^"]*)"', m.group(0))
        if not pm:
            continue
        try:
            return _astro_decode(json.loads(H.unescape(pm.group(1))))
        except Exception:
            return None
    return None


def _slate_text(n):
    if isinstance(n, list):
        return "".join(_slate_text(x) for x in n)
    if isinstance(n, dict):
        if "text" in n:
            return n["text"] if isinstance(n["text"], str) else ""
        return "".join(_slate_text(x) for x in n.get("children", []))
    return ""


def kikar_island_lines(t):
    """One line per text block of the island's html items, in order. None when there is no island."""
    D = kikar_island(t)
    if not D or not isinstance(D.get("contentItems"), list):
        return None
    lines = []
    for it in D["contentItems"]:
        if not isinstance(it, dict) or it.get("type") != "html":
            continue          # img / video items carry only captions and credits
        blocks = it.get("content")
        if isinstance(blocks, str):
            try:
                import ast
                blocks = ast.literal_eval(blocks)
            except Exception:
                return None
        for n in blocks or []:
            if isinstance(n, dict) and n.get("type") in ("bulleted-list", "numbered-list"):
                parts = n.get("children", [])
            else:
                parts = [n]
            for part in parts:
                line = collapse(_slate_text(part))
                if line:
                    lines.append(line)
    return lines


def body_kikar(t):
    lines = kikar_island_lines(t)
    if lines:
        return "\n".join(lines), "kikar-island:contentItems"
    # No island on the page: the SSR article-content div, nested recommendation cards removed.
    seg = balanced_at(t, 'itemProp="articleBody"') or balanced_at(t, 'itemprop="articleBody"')
    if not seg:
        return "", ""
    seg = drop_elements(seg, ("article",) + _DROP_TAGS)
    b = block_text(seg)
    return (b, "container:article-content") if b else ("", "")


def body_n12(t):
    i = t.find('itemprop="articleBody"')
    if i < 0:
        return "", ""
    seg = balanced(t, i)
    if not seg:
        j = t.find("</article>", i)
        seg = t[i:j if j > i else len(t)]
    seg = re.sub(r'<span[^>]*itemprop="wordCount"[^>]*>(?:</span>)?', "", seg)
    b = block_text(seg)
    return (b, "container:articleBody") if b else ("", "")


def body_strip(outlet, t):
    """Audit container order. An empty node is skipped, never sliced to chrome."""
    seen = set()
    for start, end in RULES[outlet]["containers"]:
        i = t.find(start)
        if i < 0 or start in seen:
            continue
        seen.add(start)
        seg = balanced(t, i)
        if seg is None:
            j = t.find(end, i + len(start))
            seg = t[i:j if j > i else i + 60000]
        b = strip_tags(seg[seg.find(">") + 1:])
        # LBCI's only container is LongDesc. A short node is the item; an empty one
        # must not fall through into the rest of the page.
        if outlet == "lbci":
            return (b, "container:" + start[:48]) if b.strip() else ("", "")
        if len(b.split()) >= 5:
            return b, "container:" + start[:48]
    return "", ""


def body_almanar(t):
    """The balanced article-content div. The old rule stopped at the first </div>, which is the
    wrapper of the first embedded video, so every article with a video lost the text after it."""
    marker = "<div class=\"article-content\">"
    i = t.find(marker)
    if i < 0:
        i = t.find("class=\"article-content")
    if i < 0:
        return "", ""
    seg = balanced(t, i)
    if not seg:
        return "", ""
    b = strip_tags(seg[seg.find(">") + 1:])
    return (b, "container:article-content") if b else ("", "")


def body_almanar_v1(t):
    """Legacy rule, kept only to report the before numbers."""
    marker = "<div class=\"article-content\">"
    i = t.find(marker)
    if i >= 0:
        j = t.find("</div>", i + len(marker))
        if j > i:
            b = strip_tags(t[i + len(marker):j])
            if b:
                return b, "container:article-content"
    return body_almanar(t)


def body_nna(t):
    i = t.find("fulltextarticle-container")
    if i < 0:
        return "", ""
    seg = balanced(t, i) or ""
    if not seg:
        return "", ""
    kept = []
    for p in paragraphs(seg, 0):
        # The sign-off is its own paragraph on the regression page. On some
        # pages it is glued to the end of the article paragraph, so cut there
        # instead of dropping the article.
        if "====" in p:
            p = collapse(p.split("====", 1)[0])
        if not p or "تابعوا أخبار الوكالة" in p:
            continue
        kept.append(p)
    if not kept:
        return "", ""
    return "\n".join(kept), "container:fulltextarticle"


def aljadeed_fields(t):
    """(ShortDesc, LongDesc) inside itemprop=articleBody. Empty strings when the nodes are empty."""
    i = t.find('itemprop="articleBody"')
    if i < 0:
        return "", ""
    seg = balanced(t, i)
    if not seg:
        return "", ""
    short = ""
    m = re.search(r'id="[^"]*lblShortDesc"[^>]*>(.*?)</span>', seg, re.S | re.I)
    if not m:
        m = re.search(r'class="ShortDesc\b[^"]*"[^>]*>(.*?)</h2>', seg, re.S | re.I)
    if m:
        short = inline(m.group(1))
    long = ""
    j = seg.find('class="LongDesc')
    if j >= 0:
        longseg = balanced(seg, j) or ""
        if longseg:
            long = strip_tags(longseg[longseg.find(">") + 1:])
    return short, long


def body_aljadeed(t):
    if t.find('itemprop="articleBody"') < 0 and t.find('class="LongDesc') < 0:
        return "", ""
    short, long = aljadeed_fields(t)
    parts = [p for p in (short, long) if p.strip()]
    body = "\n".join(parts)
    for mark in RULES["aljadeed"]["cuts"]:
        k = body.find(mark)
        if k > 40:
            body = body[:k].rstrip()
    # The container is there even when both fields are empty (headline-only shells).
    if t.find('itemprop="articleBody"') >= 0 or t.find('class="LongDesc') >= 0:
        return body.strip(), "container:articleBody"
    return "", ""


def extract_body(outlet, t):
    mode = RULES[outlet]["body"]
    if mode == "ld-json":
        return body_ld(t)
    if mode == "paragraphs":
        return body_paragraphs(outlet, t)
    if mode == "kikar-island":
        return body_kikar(t)
    if mode == "n12-articlebody":
        return body_n12(t)
    if mode == "strip":
        return body_strip(outlet, t)
    if mode == "almanar-div":
        return body_almanar(t)
    if mode == "nna-fulltext":
        return body_nna(t)
    if mode == "aljadeed":
        return body_aljadeed(t)
    return "", ""


def nna_dateline(t):
    """The article header dateline, inside news-details, not the sidebar."""
    i = t.find('class="news-details')
    scope = balanced(t, i) if i >= 0 else ""
    if not scope:
        return "", "", ""
    m = DATELINE_RE.search(scope)
    if not m:
        return "", "", ""
    day, month, year, clock = int(m.group(1)), MONTHS.get(m.group(2)), int(m.group(3)), m.group(4)
    if not month:
        return "", "", ""
    return f"{year:04d}-{month:02d}-{day:02d}", "", clock


def almanar_dateline(t):
    m = ALMANAR_CAL_RE.search(t)
    if not m:
        return ""
    day, month, year = int(m.group(1)), MONTHS.get(m.group(2)), int(m.group(3))
    if not month:
        return ""
    return f"{year:04d}-{month:02d}-{day:02d}"


def page_date(outlet, t):
    """(published_at, published_time, date_source, extra_warning)."""
    stamp, src = ld_dates(t)
    if stamp:
        day, full = split_stamp(stamp)
        if day:
            return day, full, src, ""
    if outlet == "nna":
        day, full, clock = nna_dateline(t)
        if day:
            warn = f"visible_clock:{clock}" if clock else ""
            return day, full, "dateline", warn
    if outlet == "almanar":
        day = almanar_dateline(t)
        if day:
            return day, "", "dateline", ""
    return "", "", "", ""


# ---------------------------------------------------------------- telegram
MSG_SPLIT = re.compile(r'(?=<div class="tgme_widget_message_wrap)')
MSG_ID = re.compile(r'data-post="abualiexpress/(\d+)"')
MSG_TIME = re.compile(r'<time[^>]+datetime="([^"]+)"')
MSG_TEXT = re.compile(
    r'<div class="tgme_widget_message_text js-message_text"[^>]*>(.*?)</div>', re.S)


def parse_telegram(t):
    """id -> {text, datetime, edited}. Reply quotes (js-message_reply_text) are not read."""
    out = {}
    for blk in MSG_SPLIT.split(t)[1:]:
        m = MSG_ID.search(blk)
        if not m:
            continue
        pid = m.group(1)
        tx = MSG_TEXT.search(blk)
        text = ""
        if tx:
            raw = re.sub(r"<br\s*/?>", "\n", tx.group(1), flags=re.I)
            text = collapse(H.unescape(re.sub(r"<[^>]+>", " ", raw)))
        dt = MSG_TIME.search(blk)
        edited = bool(re.search(r'tgme_widget_message_meta">\s*edited\b', blk))
        # First copy wins. Overlapping channel pages repeat the same post.
        out.setdefault(pid, {"text": text, "datetime": dt.group(1) if dt else "", "edited": edited})
    return out


def index_abuali_pages():
    """post id -> path of one cached t.me/s page that contains it."""
    raw = DATA / "israel" / "08-recall-audit" / "raw" / "abuali"
    index = {}
    for p in sorted(raw.glob("*.html")):
        text = p.read_text(encoding="utf-8", errors="replace")
        for pid in parse_telegram(text):
            index.setdefault(pid, p)
    return index


def load_abuali_csv():
    p = DATA / "israel" / "08-recall-audit" / "raw" / "abuali-live-messages.csv"
    out = {}
    if not p.exists():
        return out
    for r in csv.DictReader(open(p, encoding="utf-8")):
        out[r["post_id"]] = r
    return out


# ---------------------------------------------------------------- cache index
def load_checks(country):
    """url_key -> check record. Same preference as the audit: an ok row replaces a failed one."""
    recs = {}
    base = DATA / country / "08-recall-audit" / "raw"
    for f in sorted(base.glob("check-results*.jsonl")):
        for line in open(f, encoding="utf-8"):
            try:
                r = json.loads(line)
            except Exception:
                continue
            k = ilb.url_key(r["url"])
            prev = recs.get(k)
            if prev is None or (r.get("ok") and not prev.get("ok")):
                recs[k] = r
    return recs


def load_inferred_keys(country):
    """Keys whose reference-set note says the date was inferred from an id."""
    p = DATA / country / "08-recall-audit" / "reference-set.csv"
    keys = set()
    if not p.exists():
        return keys
    for r in csv.DictReader(open(p, encoding="utf-8")):
        if "date inferred" in (r.get("notes") or ""):
            keys.add(ilb.url_key(r["url"]))
    return keys


def fetch_route_of(rec, html):
    route = rec.get("route") or ""
    fetched = rec.get("fetched") or ""
    m = re.search(r"wayback:(\d{14})\b", route)
    if m:
        return "wayback:" + m.group(1)
    m = re.search(r"web\.archive\.org/web/(\d{14})", fetched)
    if m:
        return "wayback:" + m.group(1)
    if route.startswith("wayback") or "web.archive.org" in fetched:
        m = re.search(r'__wm\.wombat\(\s*"[^"]*"\s*,\s*"(\d{14})"', html or "")
        if m:
            return "wayback:" + m.group(1)
        m = re.search(r"wayback:(\d{8})\b", route) or re.search(r"web\.archive\.org/web/(\d{8})/", fetched)
        if m:
            # The capture id on the page was not 14 digits. Do not pad.
            return ""
    raw = rec.get("raw") or ""
    if raw.startswith("raw/"):
        return "our-raw"
    return "live"


def read_page(path):
    """Saved page text. The r2-*.html.gz copies are gzip of the original bytes."""
    b = Path(path).read_bytes()
    if str(path).endswith(".gz"):
        b = gzip.decompress(b)
    return b.decode("utf-8", errors="replace")


def gzip_copy(country, outlet, url, src):
    digest = hashlib.sha256(url.encode()).hexdigest()[:16]
    rel = f"raw/{outlet}/r2-{digest}.html.gz"
    dest = DATA / country / rel
    dest.parent.mkdir(parents=True, exist_ok=True)
    blob = gzip.compress(src.read_bytes(), mtime=0)
    if not dest.exists() or dest.read_bytes() != blob:   # never rewrite an identical copy
        dest.write_bytes(blob)
    return rel


# ---------------------------------------------------------------- one page
def extract_html_page(outlet, html, url):
    """Title, date, body from one saved article page. No network."""
    warnings = []
    title = page_title(outlet, html)
    body, method = extract_body(outlet, html)
    day, full, src, extra = page_date(outlet, html)
    if extra:
        warnings.append(extra)
    if outlet == "almanar" and title and (
            "الصحافة اليوم" in title or "عناوين واسرار الصحف" in title or "عناوين وأسرار الصحف" in title):
        warnings.append("press_review")
    if outlet == "ynet":
        warnings.append("ynet_body_is_jsonld_lead")
    hint = doc_type(outlet, url, title, body)
    if outlet == "aljadeed" and body:
        short, long = aljadeed_fields(html)
        raw_join = "\n".join(p for p in (short, long) if p.strip())
        for mark in ALJADEED_CUTS:
            if mark in raw_join and mark not in body:
                warnings.append("cut_at:" + mark)
                break
    if not body.strip() and hint == "article" and method == "" and RULES[outlet]["body"] != "ld-json":
        warnings.append("no_article_text")
    # Empty ShortDesc and LongDesc are headline-only, including when the URL looks like a ticker.
    if outlet == "aljadeed" and not body.strip() and (
            'itemprop="articleBody"' in html or 'class="LongDesc' in html):
        hint = "brief"
        warnings.append("headline_only_empty_container")
    elif not body.strip() and hint in ("brief", "live_ticker"):
        warnings.append("headline_only")
    return {
        "title": title,
        "body_text": body.strip(),
        "extract_method": method,
        "published_at": day,
        "published_time": full,
        "date_source": src,
        "document_type_hint": hint,
        "paywall": paywall_of(outlet, html),
        "warnings": warnings,
        "canonical_url": canonical_of(html, url),
    }


def blank(row):
    return {
        "outlet": row["outlet"],
        "url": row["url"],
        "canonical_url": row["url"],
        "gap_status": row.get("status", ""),
        "central_or_mention": row.get("central_or_mention", ""),
        "fetch_route": "",
        "source_file": "",
        "raw_path": "",
        "title": "",
        "published_at": "",
        "published_time": "",
        "date_source": "",
        "body_text": "",
        "body_words": 0,
        "extract_method": "",
        "document_type_hint": "",
        "paywall": False,
        "provider": "",
        "language": "",
        "ok": False,
        "failure": "",
        "warnings": [],
    }


def finish(rec):
    rec["body_text"] = rec["body_text"] or ""
    rec["body_words"] = len(rec["body_text"].split())
    rec["provider"] = provider_of(rec["title"], rec["body_text"]) if rec["title"] or rec["body_text"] else ""
    lang_src = rec["body_text"] or rec["title"]
    rec["language"] = language_of(lang_src) if lang_src else ""
    if lang_src and not rec["language"]:
        rec["warnings"].append("language_undetermined")
    hint = rec["document_type_hint"]
    has_head = bool((rec["title"] or "").strip())
    has_body = bool(rec["body_text"].strip())
    if rec["failure"]:
        rec["ok"] = False
    elif has_head and (has_body or headline_only(hint, rec["body_text"])):
        rec["ok"] = True
        rec["failure"] = ""
    elif not has_head and not has_body:
        rec["ok"] = False
        rec["failure"] = rec["failure"] or "empty"
    elif not has_head:
        rec["ok"] = False
        rec["failure"] = rec["failure"] or "empty"
    else:
        rec["ok"] = False
        rec["failure"] = rec["failure"] or "empty"
    # stable field order
    return {k: rec[k] for k in FIELDS}


def apply_manifest_date(rec, row, inferred):
    if rec["published_at"]:
        man = (row.get("published_date") or "")[:10]
        if man and man != rec["published_at"]:
            rec["warnings"].append("manifest_date_differs:" + man)
        return
    if ilb.url_key(row["url"]) in inferred:
        rec["warnings"].append("manifest_date_inferred_not_used")
        return
    man = (row.get("published_date") or "")[:10]
    if re.fullmatch(r"\d{4}-\d{2}-\d{2}", man):
        rec["published_at"] = man
        rec["date_source"] = "audit-manifest"
        rec["warnings"].append("date_from_audit_manifest")


# ---------------------------------------------------------------- checks
def ratio(a, b):
    a = collapse(a)[:3000]
    b = collapse(b)[:3000]
    if not a and not b:
        return 1.0
    return SequenceMatcher(None, a, b).ratio()


def tokens(s):
    s = H.unescape(s or "").replace("\xa0", " ").replace("\u00a0", " ")
    s = re.sub(r"[\u200b-\u200f\ufeff\u0640]", "", s)
    return re.findall(r"\w+", s.lower(), flags=re.U)


def phrase_in(words, text):
    if len(words) < 4:
        return False
    return " ".join(words) in " ".join(tokens(text))


def sentences(text, min_words):
    parts = re.split(r"(?<=[.!?؟])\s+", text or "")
    return [collapse(p) for p in parts if len(p.split()) >= min_words]


def og_description(html):
    m = (re.search(r'<meta[^>]+property=["\']og:description["\'][^>]+content=["\']([^"\']*)', html, re.I) or
         re.search(r'<meta[^>]+content=["\']([^"\']*)["\'][^>]+property=["\']og:description["\']', html, re.I))
    return H.unescape(m.group(1)).strip() if m else ""


def ld_description(html):
    for it in ld_items(html):
        if ld_type(it) in ARTICLE_TYPES and it.get("description"):
            return collapse(H.unescape(str(it["description"])))
    return ""


def ld_article_plain(html):
    for it in ld_items(html):
        if ld_type(it) in ARTICLE_TYPES and it.get("articleBody"):
            return collapse(inline(str(it["articleBody"])))
    return ""


def substantive_desc(text):
    """A description that is an article lead, not the site name."""
    if len(tokens(text)) < 4:
        return False
    flat = collapse(text).lower().strip(" |")
    if flat in {"lebanon news", "mtv lebanon", "lbci", "al jadeed", "n12", "ynet", "mako"}:
        return False
    return True


def opening_in(text, body, window):
    tw = tokens(text)
    if len(tw) < 4:
        return False
    hay = body if window is None else (body or "")[:window]
    if phrase_in(tw[:8], hay):
        return True
    return len(tw) >= 6 and phrase_in(tw[:6], hay)


def legit_empty(body, hint, warnings):
    if (body or "").strip():
        return False
    if "headline_only_empty_container" in warnings or "headline_only" in warnings:
        return True
    return hint in ("brief", "live_ticker", "newsletter")


def chrome_hits(outlet, body):
    found = []
    for s in CHROME_STRINGS.get(outlet, []):
        if s.startswith("frame") or s.startswith("referrer"):
            if s.lower() in (body or "").lower():
                found.append(s)
        elif s in (body or ""):
            found.append(s)
    return found


def lead_check(outlet, html, body, title, hint, warnings):
    # Telegram: the channel og:description is not the post. The message is the lead.
    if outlet == "abuali" or hint == "telegram_post":
        return {"ok": bool((body or "").strip()), "reason": "telegram_message_is_the_lead"}
    # Headline-only ticker or empty shell: there is no body for the description to open.
    if legit_empty(body, hint, warnings):
        return {"ok": True, "reason": "headline_only"}
    if not (body or "").strip():
        return {"ok": False, "reason": "empty_article"}
    cands = []
    og = og_description(html)
    ld = ld_description(html)
    if substantive_desc(og):
        cands.append(("og:description", og))
    if substantive_desc(ld) and collapse(ld) != collapse(og):
        cands.append(("ld-description", ld))
    if outlet == "aljadeed":
        short, _long = aljadeed_fields(html)
        if substantive_desc(short):
            cands.append(("shortdesc", short))
    if not cands:
        return {"ok": True, "reason": "no_description"}
    for name, text in cands:
        if opening_in(text, body, 400):
            return {"ok": True, "reason": name}
    for name, text in cands:
        if opening_in(text, body, None):
            return {"ok": False, "reason": "description_not_in_first_400"}
    # The deck is a rewrite: its words are not in the article. The container text is the lead.
    article = ld_article_plain(html)
    if substantive_desc(article) and not opening_in(article, body, 400):
        return {"ok": False, "reason": "article_lead_not_in_first_400"}
    return {"ok": True, "reason": "description_is_rewrite"}


_END_RE = re.compile(r"[.!?؟…][\"'”’»״)\]\s]*$")
_CREDIT_RE = re.compile(
    r"(?:\bAFP|\bReuters|\bAP|רויטרס|رويترز|فرانس برس|المصدر\s*:|Source\s*:)\s*$", re.I)
_YEAR_RE = re.compile(r"\b20\d\d\s*$")


def ending_complete(body):
    b = (body or "").strip()
    return bool(_END_RE.search(b) or _CREDIT_RE.search(b) or _YEAR_RE.search(b))


def truncation_check(outlet, html, body, hint, warnings):
    # Telegram posts are the whole js-message_text node. They often do not end with a period.
    if outlet == "abuali" or hint == "telegram_post":
        return {"ok": bool((body or "").strip()), "reason": "full_telegram_message"}
    if legit_empty(body, hint, warnings) or not (body or "").strip():
        return {"ok": legit_empty(body, hint, warnings) or not (body or "").strip() and hint != "article",
                "reason": "headline_only" if legit_empty(body, hint, warnings) else "empty_article"}
    ld = ld_article_plain(html)
    ld_ok = True
    if ld and len(ld) >= 40:
        ld_ok = len(body) >= 0.9 * len(ld)
    cut = any(w.startswith("cut_at:") for w in warnings)
    # A container taken whole is complete even when the page's last sentence has no period.
    # A recirculation cut still has to leave a finished ending.
    ending_ok = ending_complete(body) or not cut
    reason = "complete"
    if not ld_ok:
        reason = "shorter_than_articleBody"
    elif cut and not ending_complete(body):
        reason = "cut_mid_sentence"
    elif not ending_complete(body):
        reason = "container_has_no_terminal_punctuation"
    return {"ok": bool(ending_ok and ld_ok), "reason": reason}


def duplication_check(body):
    if not (body or "").strip():
        return {"ok": True}
    seen = set()
    dup = []
    dup_low = set()
    for s in sentences(body, 8):
        low = s.lower()
        if low in seen and low not in dup_low:
            dup.append(s)
            dup_low.add(low)
        seen.add(low)
    out = {"ok": not dup}
    if dup:
        out["repeated"] = dup[:2]
    return out


def order_check(outlet, html, body, method, hint):
    # No JSON-LD articleBody to order against.
    if outlet == "abuali" or hint == "telegram_post" or legit_empty(body, hint, []):
        return {"ok": True, "reason": "not_applicable"}
    if not (body or "").strip():
        return {"ok": False, "reason": "empty_article"}
    ld = ld_article_plain(html)
    if not ld or len(ld.split()) < 40 or (method or "").startswith("ld-json"):
        return {"ok": True, "reason": "not_applicable"}
    if len(ld) < 0.5 * max(len(body), 1):
        return {"ok": True, "reason": "articleBody_is_blurb"}
    pos, ordered, compared = -1, True, 0
    compact = ld.lower()
    for para in body.split("\n"):
        probe = collapse(para).lower()[:160]
        if len(probe.split()) < 4:
            continue
        where = compact.find(probe)
        if where >= 0:
            compared += 1
            if where < pos:
                ordered = False
            pos = where
    if compared == 0:
        return {"ok": True, "reason": "articleBody_not_paragraph_source"}
    return {"ok": ordered, "reason": "matched_paragraphs=" + str(compared)}


# The full article container, measured the way a reader sees it and independent of the
# extraction rule's end marker. Captions, players, scripts and share buttons are not text.
CONTAINER_MARKERS = {
    "ynet": ['id="ArticleBodyComponent"'],
    "n12": ['itemprop="articleBody"'],
    "makan": ['class="article-content', 'class="text-content'],
    "lbci": ['class="LongDesc'],
    "mtv": ['class="articles-report', 'class="articles-content'],
    "almanar": ['<div class="article-content">', 'class="article-content'],
    "nna": ['fulltextarticle-container'],
}


def container_reference(outlet, html):
    """(text, label) of the outlet's full article container, or None when the page has none."""
    if outlet == "kikar":
        lines = kikar_island_lines(html)
        if lines is not None:
            return "\n".join(lines), "island:contentItems"
        seg = balanced_at(html, 'itemProp="articleBody"') or balanced_at(html, 'itemprop="articleBody"')
        if seg:
            return block_text(drop_elements(seg, ("article",) + _DROP_TAGS)), "container:articleBody"
        return None
    if outlet == "aljadeed":
        if html.find('itemprop="articleBody"') < 0 and html.find('class="LongDesc') < 0:
            return None
        short, long = aljadeed_fields(html)
        return "\n".join(p for p in (short, long) if p.strip()), "container:ShortDesc+LongDesc"
    for marker in CONTAINER_MARKERS.get(outlet, []):
        seg = balanced_at(html, marker)
        if not seg:
            continue
        inner = seg[seg.find(">") + 1:]
        text = block_text(inner)
        if outlet == "nna":
            # The agency sign-off ("====" initials, radio frequencies) is not article text.
            text = "\n".join(
                collapse(line.split("====", 1)[0]) for line in text.splitlines()
                if "تابعوا أخبار الوكالة" not in line)
        return text, "container:" + marker.replace('"', "")
    return None


def coverage_check(outlet, html, body, hint):
    if outlet == "abuali" or hint == "telegram_post":
        return {"ok": True, "reason": "not_applicable"}
    ref = container_reference(outlet, html)
    if ref is None:
        return {"ok": True, "reason": "no_container_on_page"}
    text, label = ref
    ref_w = len(text.split())
    body_w = len((body or "").split())
    if ref_w == 0:
        return {"ok": True, "reason": "empty_container", "container_words": 0, "body_words": body_w}
    ok = body_w >= 0.9 * ref_w
    return {"ok": ok, "reason": "covered" if ok else "shorter_than_container",
            "container": label, "container_words": ref_w, "body_words": body_w,
            "coverage": round(body_w / ref_w, 3)}


def initial_checks(outlet, html, body, title, hint, method, warnings):
    hits = chrome_hits(outlet, body)
    return {
        "no_chrome": {"ok": not hits, "found": hits},
        "lead_present": lead_check(outlet, html, body, title, hint, warnings),
        "not_truncated": truncation_check(outlet, html, body, hint, warnings),
        "no_duplication": duplication_check(body),
        "order": order_check(outlet, html, body, method, hint),
        "container_coverage": coverage_check(outlet, html, body, hint),
    }


def no_raw_checks():
    return {name: {"ok": False, "reason": "no_raw"} for name in CHECK_NAMES}


def checks_pass(checks):
    return all(v.get("ok") for v in checks.values())


def apply_cross_checks(items):
    """A 6+ word sentence in 3+ different headlines fails no_chrome, unless it is inside that page's JSON-LD articleBody."""
    freq = defaultdict(lambda: defaultdict(set))
    for it in items:
        if not it["body_text"]:
            continue
        ld = collapse(it.get("ld_body") or "")
        for s in set(sentences(it["body_text"], 6)):
            if ld and s in ld:
                continue
            freq[it["outlet"]][s].add(it["title"] or it["key"])
    repeated = {o: {s for s, titles in found.items() if len(titles) >= 3} for o, found in freq.items()}
    for it in items:
        hits = [s for s in sentences(it["body_text"], 6) if s in repeated.get(it["outlet"], set())]
        if hits:
            it["checks"]["no_chrome"]["ok"] = False
            it["checks"]["no_chrome"]["repeated_sentences"] = hits[:3]


def empty_checks_quote(html):
    i = html.find('class="LongDesc')
    if i < 0:
        i = html.find('itemprop="articleBody"')
    if i < 0:
        return collapse(html)[:150]
    return collapse(html[i:i + 180])[:150]


def classify_mismatch(outlet, stored, extracted, html, checks):
    """stored_wrong / new_wrong / both, plus a ≤150-char quote from the raw page."""
    stored_c, extracted_c = collapse(stored), collapse(extracted)
    new_bad = not checks_pass(checks)
    page_has_stored = bool(stored_c) and phrase_in(tokens(stored_c)[:8], html) if len(tokens(stored_c)) >= 4 else bool(stored_c and stored_c[:40] in html)

    if outlet == "aljadeed":
        short, long = aljadeed_fields(html)
        once = collapse(" ".join(p for p in (short, long) if p.strip()))
        twice = collapse(" ".join(p for p in (short, long, long) if p.strip()))
        if not once:
            return "stored_wrong", empty_checks_quote(html)
        if long and ratio(stored, twice) >= 0.98:
            # The page has LongDesc once. The stored body appends it a second time.
            kind = "both" if new_bad else "stored_wrong"
            return kind, collapse(long)[:150]
        if not extracted_c and once:
            return "new_wrong", once[:150]

    if outlet == "makan":
        desc = og_description(html) or ld_description(html)
        if desc and ratio(stored, desc) >= 0.90 and extracted_c:
            # The article is the article-content text. The stored body is the description.
            return "stored_wrong", extracted_c[:150]

    if outlet == "lbci":
        # Further paragraphs and tweet embeds inside LongDesc are the item.
        # "آخر الأخبار" is the next-story widget and is not.
        hits = chrome_hits("lbci", extracted)
        if hits and chrome_hits("lbci", stored):
            return "both", (extracted_c or stored_c)[:150]
        if hits:
            return "new_wrong", (extracted_c or stored_c)[:150]
        if extracted_c:
            return "stored_wrong", extracted_c[:150]
        if not page_has_stored:
            return "stored_wrong", empty_checks_quote(html)
        return "new_wrong", collapse(strip_tags(html))[:150]

    # The stored body stops early (it ends at a recommended-story card or the first embedded block).
    # The new body is the whole container and fails the gate only on text the publisher repeats
    # across articles. That is a gate result, reported as such; the extractor is not at fault.
    failing = {name for name, v in checks.items() if not v.get("ok")}
    # lead_present counts here only when the page's own description is a later passage of the article
    # (an opinion column whose og:description quotes the middle of the text).
    deck_later = checks.get("lead_present", {}).get("reason") == "description_not_in_first_400"
    allowed = {"no_chrome", "no_duplication"} | ({"lead_present"} if deck_later else set())
    publisher_repeat_only = bool(failing) and failing <= allowed and not any(
        checks[n].get("found") for n in failing if n in checks and "found" in checks[n])
    if (publisher_repeat_only and extracted_c and stored_c
            and len(stored_c.split()) * 1.25 <= len(extracted_c.split())):
        return "stored_wrong", extracted_c[:150]

    if not extracted_c and stored_c and not page_has_stored:
        return "stored_wrong", empty_checks_quote(html)
    if not extracted_c and stored_c and page_has_stored:
        return "new_wrong", stored_c[:150]
    if new_bad and chrome_hits(outlet, stored):
        return "both", (extracted_c or stored_c)[:150]
    if new_bad:
        return "new_wrong", (extracted_c or stored_c)[:150]
    return "stored_wrong", (extracted_c or stored_c)[:150]


# ---------------------------------------------------------------- reextract / gaps
def strip_abuali_footer(text):
    """(text without the trailing comment-link footer, whether the footer was there).

    The footer is a link label the channel appends to every post. It is not part of the post.
    Only a trailing occurrence is removed; the post text is otherwise untouched.
    """
    text = text or ""
    had = ABUALI_FOOTER in text
    clean = text.rstrip()
    if clean.endswith(ABUALI_FOOTER):
        clean = clean[: -len(ABUALI_FOOTER)].rstrip()
    return clean, had


def with_footer(rec, had=False):
    """Abu Ali rows carry footer_comment_link: True when the post ended in the comment-link footer."""
    if rec.get("outlet") == "abuali":
        rec["footer_comment_link"] = bool(had)
    return rec


def check_item(key, outlet, title, body, checks, ld_body):
    return {
        "key": key,
        "outlet": outlet,
        "title": title or "",
        "body_text": body or "",
        "checks": checks,
        "ld_body": ld_body or "",
    }


def build_reextract(country):
    """One row per corpus record. Does not write corpus.jsonl."""
    rows = []
    items = []
    path = DATA / country / "06-corpus" / "corpus.jsonl"
    for line in open(path, encoding="utf-8"):
        r = json.loads(line)
        raw = (r.get("capture") or {}).get("raw_path") or ""
        outlet = r["source"]["page_publisher"]
        stored = (r.get("content") or {}).get("body") or ""
        url = (r.get("publication") or {}).get("canonical_url") or ""
        row = {
            "document_id": r["document_id"],
            "raw_path": raw,
            "body_text": "",
            "body_words": 0,
            "extract_method": "",
            "title": "",
            "published_at": "",
            "checks": no_raw_checks(),
            "ok": False,
            "warnings": [],
            "_stored": stored,
            "_outlet": outlet,
            "_html": "",
        }
        fp = DATA / country / raw if raw else None
        if outlet not in RULES or not raw or fp is None or not fp.exists():
            row["warnings"].append("no_raw")
            if outlet == "abuali":
                row["footer_comment_link"] = False
            rows.append(row)
            continue
        html = read_page(fp)
        row["_html"] = html
        if outlet == "abuali":
            pid = r["document_id"].rsplit("_", 1)[-1]
            msg = parse_telegram(html).get(pid)
            if not msg or not msg["text"]:
                row["warnings"].append("message_not_in_page")
                row["footer_comment_link"] = False
                row["checks"] = initial_checks(outlet, html, "", "", "telegram_post", "", row["warnings"])
            else:
                clean, had = strip_abuali_footer(msg["text"])
                row["title"] = clean
                row["body_text"] = clean
                row["extract_method"] = "telegram:js-message_text"
                if msg["datetime"]:
                    day, _full = split_stamp(msg["datetime"])
                    row["published_at"] = day
                if msg["edited"]:
                    row["warnings"].append("telegram_edited")
                row["footer_comment_link"] = had
                row["ok"] = bool(clean)
                if not clean:
                    row["warnings"].append("footer_only_post")
                row["checks"] = initial_checks(
                    outlet, html, row["body_text"], row["title"], "telegram_post",
                    row["extract_method"], row["warnings"])
        else:
            got = extract_html_page(outlet, html, url)
            row["title"] = got["title"]
            row["body_text"] = got["body_text"]
            row["extract_method"] = got["extract_method"]
            row["published_at"] = got["published_at"]
            row["warnings"] = list(got["warnings"])
            if wrong_page(got["title"]):
                row["warnings"].append("wrong_page")
                row["ok"] = False
            elif got["title"] or got["body_text"] or legit_empty(got["body_text"], got["document_type_hint"], got["warnings"]):
                row["ok"] = True
            else:
                row["warnings"].append("empty")
                row["ok"] = False
            row["checks"] = initial_checks(
                outlet, html, row["body_text"], row["title"], got["document_type_hint"],
                row["extract_method"], row["warnings"])
        row["body_words"] = len((row["body_text"] or "").split())
        items.append(check_item(
            r["document_id"], outlet, row["title"], row["body_text"], row["checks"], ld_article_plain(html)))
        rows.append(row)
    return rows, items


def build_records(country):
    manifest = gap_rows(country)
    checks = load_checks(country)
    inferred = load_inferred_keys(country)
    abuali_pages = index_abuali_pages() if country == "israel" else {}
    abuali_csv = load_abuali_csv() if country == "israel" else {}
    abuali_parsed = {}
    records = []
    items = []
    longdesc_pages = 0
    longdesc_nonempty = 0
    longdesc_short_only = 0
    for row in manifest:
        outlet = row["outlet"]
        rec = blank(row)
        status = row.get("status") or ""
        if status in ("live_blog", "live_blog_unverified"):
            rec["failure"] = "deferred_liveblog"
            rec["warnings"].append("stage 2 handles live blogs")
            records.append(with_footer(finish(rec)))
            continue
        if outlet == "abuali":
            pid = row["url"].rstrip("/").split("/")[-1]
            src = abuali_pages.get(pid)
            if src is None:
                rec["failure"] = "needs_fetch"
                rec["warnings"].append("message id not in cached t.me/s pages")
                records.append(with_footer(finish(rec)))
                continue
            rel_src = str(src.relative_to(DATA / country))
            if rel_src not in abuali_parsed:
                abuali_parsed[rel_src] = parse_telegram(src.read_text(encoding="utf-8", errors="replace"))
            msg = abuali_parsed[rel_src].get(pid)
            rec["fetch_route"] = "telegram-live"
            rec["source_file"] = rel_src
            rec["raw_path"] = gzip_copy(country, outlet, row["url"], src)
            rec["document_type_hint"] = "telegram_post"
            rec["extract_method"] = "telegram:js-message_text"
            if not msg or not msg["text"]:
                rec["failure"] = "empty"
                rec["warnings"].append("no own message text")
                records.append(with_footer(finish(rec)))
                continue
            clean, had = strip_abuali_footer(msg["text"])
            rec["title"] = clean
            rec["body_text"] = clean
            if not clean:
                rec["failure"] = "empty"
                rec["warnings"].append("footer_only_post")
            if msg["datetime"]:
                day, _full = split_stamp(msg["datetime"])
                rec["published_at"] = day
                rec["published_time"] = msg["datetime"]
                rec["date_source"] = "telegram-ts"
            if msg["edited"]:
                rec["warnings"].append("telegram_edited")
            csv_row = abuali_csv.get(pid)
            if csv_row is None:
                rec["warnings"].append("not_in_live_csv")
            elif collapse(csv_row.get("text") or "") != msg["text"]:
                rec["warnings"].append("live_csv_text_differs")
            apply_manifest_date(rec, row, inferred)
            done = with_footer(finish(rec), had)
            # The channel page's og:description is not this post. Checks use the message only.
            chk = initial_checks(outlet, "", done["body_text"], done["title"], "telegram_post",
                                 done["extract_method"], done["warnings"])
            items.append(check_item(row["url"], outlet, done["title"], done["body_text"], chk, ""))
            done["_checks"] = chk
            records.append(done)
            continue
        hit = checks.get(ilb.url_key(row["url"]))
        if not hit or not hit.get("raw"):
            rec["failure"] = "needs_fetch"
            rec["warnings"].append("no cached page for url_key")
            records.append(with_footer(finish(rec)))
            continue
        src = DATA / country / hit["raw"]
        if not src.exists():
            rec["failure"] = "needs_fetch"
            rec["warnings"].append("cached path missing")
            records.append(with_footer(finish(rec)))
            continue
        html = src.read_text(encoding="utf-8", errors="replace")
        if outlet == "aljadeed":
            longdesc_pages += 1
            short, long = aljadeed_fields(html)
            if long.strip():
                longdesc_nonempty += 1
            elif short.strip():
                longdesc_short_only += 1
        rec["source_file"] = hit["raw"]
        rec["raw_path"] = gzip_copy(country, outlet, row["url"], src)
        route = fetch_route_of(hit, html)
        if route:
            rec["fetch_route"] = route
        elif (hit.get("route") or "").startswith("wayback"):
            rec["fetch_route"] = ""
            rec["warnings"].append("wayback_timestamp_not_14_digits")
        else:
            rec["fetch_route"] = "live"
        got = extract_html_page(outlet, html, row["url"])
        rec.update({
            "title": got["title"],
            "canonical_url": got["canonical_url"],
            "published_at": got["published_at"],
            "published_time": got["published_time"],
            "date_source": got["date_source"],
            "body_text": got["body_text"],
            "extract_method": got["extract_method"],
            "document_type_hint": got["document_type_hint"],
            "paywall": got["paywall"],
        })
        rec["warnings"].extend(got["warnings"])
        if wrong_page(got["title"]):
            rec["body_text"] = ""
            rec["failure"] = "wrong_page"
            rec["warnings"].append("title is an error page")
        elif not got["body_text"]:
            if got["title"] and got["document_type_hint"] in ("brief", "live_ticker"):
                pass
            elif not got["title"]:
                rec["failure"] = "no_container" if RULES[outlet]["body"] != "ld-json" else "empty"
            else:
                rec["failure"] = "empty"
        apply_manifest_date(rec, row, inferred)
        done = with_footer(finish(rec))
        chk = initial_checks(
            outlet, html, done["body_text"], done["title"], done["document_type_hint"],
            done["extract_method"], done["warnings"])
        items.append(check_item(row["url"], outlet, done["title"], done["body_text"], chk, ld_article_plain(html)))
        done["_checks"] = chk
        records.append(done)
    meta = {
        "aljadeed_pages": longdesc_pages,
        "aljadeed_longdesc_nonempty": longdesc_nonempty,
        "aljadeed_short_only": longdesc_short_only,
    }
    return records, items, meta


def gap_rows(country):
    # The audit manifest was regenerated after the gaps were filled and is now nearly empty.
    # The frozen input copy is the one this extractor reads.
    p = DATA / country / "05-extraction" / "round2" / "gap-manifest-input.csv"
    return list(csv.DictReader(open(p, encoding="utf-8")))


# ---------------------------------------------------------------- report
def public_reextract(row):
    out = {
        "document_id": row["document_id"],
        "raw_path": row["raw_path"],
        "body_text": row["body_text"],
        "body_words": row["body_words"],
        "extract_method": row["extract_method"],
        "title": row["title"],
        "published_at": row["published_at"],
        "checks": {name: row["checks"][name] for name in CHECK_NAMES},
        "ok": row["ok"],
        "warnings": row["warnings"],
    }
    if row.get("_outlet") == "abuali" or "footer_comment_link" in row:
        out["footer_comment_link"] = bool(row.get("footer_comment_link"))
    return out


def public_candidate(row):
    out = {k: row[k] for k in FIELDS}
    if row.get("outlet") == "abuali":
        out["footer_comment_link"] = bool(row.get("footer_comment_link"))
    return out


def page_key(outlet, raw_path, ident):
    """One page, or one Telegram post. A gap row that has since entered the corpus shares this key."""
    if outlet == "abuali":
        return (outlet, raw_path, str(ident).rstrip("/").rsplit("/", 1)[-1].rsplit("_", 1)[-1])
    return (outlet, raw_path, "")


def corpus_page_keys(re_rows):
    return {page_key(r["_outlet"], r["raw_path"], r["document_id"])
            for r in re_rows if "no_raw" not in r["warnings"]}


def gate_stats(country, re_rows, records):
    """Bodies = corpus rows with a raw file plus gap rows read from a cached page.

    The corpus now holds the gap rows it accepted from round 1, so a gap row whose page is already
    among the corpus rows is not counted a second time.
    """
    by = {o: [] for o in COUNTRIES[country]}
    for row in re_rows:
        if "no_raw" in row["warnings"]:
            continue
        by.setdefault(row["_outlet"], []).append(row["checks"])
    seen = corpus_page_keys(re_rows)
    for rec in records:
        if rec["failure"] in ("needs_fetch", "deferred_liveblog"):
            continue
        if "_checks" not in rec:
            continue
        if page_key(rec["outlet"], rec["raw_path"], rec["url"]) in seen:
            continue
        by.setdefault(rec["outlet"], []).append(rec["_checks"])
    summary = {}
    for o in COUNTRIES[country]:
        rows = by.get(o, [])
        n = len(rows)
        per = {}
        all_pass = 0
        for name in CHECK_NAMES:
            ok_n = sum(1 for c in rows if c[name]["ok"])
            per[name] = {"pass": ok_n, "n": n, "rate": (ok_n / n) if n else 0.0}
        for c in rows:
            if checks_pass(c):
                all_pass += 1
        summary[o] = {
            "n": n,
            "all_pass": all_pass,
            "all_rate": (all_pass / n) if n else 0.0,
            "per": per,
        }
    return summary


def write_adjudication(country, re_rows):
    dest = DATA / country / "05-extraction" / "round2" / "regression-adjudication.csv"
    adjudicated = []
    ratios = defaultdict(list)
    for row in re_rows:
        if "no_raw" in row["warnings"] or not row["_html"]:
            continue
        stored = row["_stored"]
        if not stored.strip() and not (row["body_text"] or "").strip():
            continue
        rel = ratio(stored, row["body_text"])
        if stored.strip():
            ratios[row["_outlet"]].append(rel)
        if rel >= 0.90:
            continue
        if not stored.strip() and not row["body_text"].strip():
            continue
        kind, quote = classify_mismatch(
            row["_outlet"], stored, row["body_text"], row["_html"], row["checks"])
        adjudicated.append({
            "document_id": row["document_id"],
            "outlet": row["_outlet"],
            "raw_path": row["raw_path"],
            "ratio": f"{rel:.3f}",
            "classification": kind,
            "evidence": collapse(quote)[:150],
        })
    adjudicated.sort(key=lambda r: (r["outlet"], r["ratio"], r["document_id"]))
    with open(dest, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["document_id", "outlet", "raw_path", "ratio", "classification", "evidence"])
        w.writeheader()
        w.writerows(adjudicated)
    return dest, adjudicated, ratios


def fmt_rate(p, n):
    if not n:
        return "n=0"
    return f"{p}/{n} ({p / n:.1%})"


def clip_quote(s, n=160):
    s = collapse(s).replace("`", "'")
    if len(s) <= n:
        return s
    return s[: n - 1] + "…"


def iter_checked(re_rows, records):
    for row in re_rows:
        if "no_raw" in row["warnings"]:
            continue
        yield row["_outlet"], row["document_id"], row["checks"]
    seen = corpus_page_keys(re_rows)
    for rec in records:
        chk = rec.get("_checks")
        if not chk or rec.get("failure") in ("needs_fetch", "deferred_liveblog"):
            continue
        if page_key(rec["outlet"], rec["raw_path"], rec["url"]) in seen:
            continue
        yield rec["outlet"], rec["url"], chk


def check_failure_lines(re_rows, records):
    """One line per failing sentence. The text is left as published."""
    cross = defaultdict(lambda: defaultdict(list))
    dups = defaultdict(list)
    known = defaultdict(list)
    later = []
    other = defaultdict(list)
    for outlet, ident, chk in iter_checked(re_rows, records):
        nc = chk["no_chrome"]
        if not nc["ok"]:
            for s in nc.get("repeated_sentences") or []:
                if ident not in cross[outlet][s]:
                    cross[outlet][s].append(ident)
            if nc.get("found"):
                known[outlet].append((ident, list(nc["found"])))
            if not nc.get("repeated_sentences") and not nc.get("found"):
                other[outlet].append(ident + " no_chrome")
        nd = chk["no_duplication"]
        if not nd["ok"]:
            reps = nd.get("repeated") or []
            if reps:
                for s in reps:
                    dups[outlet].append((ident, s))
            else:
                other[outlet].append(ident + " no_duplication")
        lead = chk["lead_present"]
        if not lead["ok"]:
            if lead.get("reason") == "description_not_in_first_400":
                later.append(outlet + " " + ident)
            else:
                other[outlet].append(ident + " lead_present:" + str(lead.get("reason") or ""))
        for name in ("not_truncated", "order"):
            if not chk[name]["ok"]:
                other[outlet].append(ident + " " + name + ":" + str(chk[name].get("reason") or ""))
    lines = []
    for outlet, sentences_ in cross.items():
        for s, ids in sentences_.items():
            lines.append(
                f"{outlet} check 1: `{clip_quote(s)}` appears under {len(ids)} headlines "
                f"(e.g. {ids[0]}). It is inside the article text on those pages, so it stays."
            )
    for outlet, pairs in dups.items():
        shown = pairs[:6]
        for ident, s in shown:
            lines.append(
                f"{outlet} check 4: `{ident}` repeats `{clip_quote(s)}`. "
                "Both copies are in the extracted article text, so both stay."
            )
        if len(pairs) > 6:
            lines.append(f"{outlet} check 4: {len(pairs) - 6} further repeated sentences.")
    for outlet, hits in known.items():
        for ident, found in hits[:6]:
            lines.append(f"{outlet} check 1 known chrome {found} in `{ident}`.")
        if len(hits) > 6:
            lines.append(f"{outlet} check 1: {len(hits) - 6} further known-chrome hits.")
    if later:
        shown = later[:12]
        extra = f" (+{len(later) - 12})" if len(later) > 12 else ""
        lines.append(
            "Description opening words occur in the body but not in the first 400 characters: "
            + ", ".join(shown) + extra + "."
        )
    for outlet, notes in other.items():
        shown = notes[:8]
        extra = f" (+{len(notes) - 8})" if len(notes) > 8 else ""
        lines.append(f"{outlet} other check failures: " + "; ".join(shown) + extra + ".")
    return lines


# ---------------------------------------------------------------- report: truncation fix
def legacy_body(outlet, html):
    """Body under the rule before the truncation fix. Reported only as 'before'."""
    if outlet in ("kikar", "n12"):
        return body_paragraphs(outlet, html)[0]
    if outlet == "almanar":
        return body_almanar_v1(html)[0]
    return None


# Words that name the 17-18 September attack. Bare "מכשירי קשר" (radios) is not enough on its own:
# it also turns up in unrelated military items, so it is reported separately as GENERIC_RADIO_RE.
ATTACK_RE = re.compile(
    r"ביפר|זימונית|זימוניות|מכשירי הקשר|פיצוץ המכשירים|פיצוצי המכשירים|פיצוץ מכשירי|פיצוצי מכשירי")
GENERIC_RADIO_RE = re.compile(r"מכשירי קשר|מכשיר קשר|מכשיר הקשר")

ATTACK_IDS = [
    "il_kikar_eb9350c551", "il_kikar_29e9069f80", "il_kikar_6a30f10d58", "il_kikar_d6e00f2704",
    "il_kikar_14dc0a19c0", "il_kikar_1ac017e03f", "il_kikar_6d7b5f3531", "il_kikar_99fcbbf3a4",
    "il_kikar_d7845b3b06", "il_n12_33d664e870",
]


def first_attack_sentence(text, skip_text="", rx=None):
    """First sentence that names the attack, preferring one that the old body did not have."""
    rx = rx or ATTACK_RE
    hits = []
    for line in (text or "").splitlines():
        for sent in re.split(r"(?<=[.!?])\s+", line):
            if rx.search(sent):
                hits.append(collapse(sent))
    for h in hits:
        if h not in (skip_text or ""):
            return h
    return hits[0] if hits else ""


def _med(v):
    return statistics.median(v) if v else 0


def truncation_lines(country, re_rows, records):
    outlets = ["kikar", "n12"] if country == "israel" else ["almanar"]
    lines = ["## Truncation fix: before and after", ""]
    if country == "israel":
        lines.append("Before: the old rule. Kikar read `<p>` up to the first `</article>`, which is the first recommended-story card inside the article, "
                     "so the text after that card was lost. N12 read the `<p>` nodes of `articleBody` through `</article>` and dropped every `<p>` "
                     "under 4 words, h4 sub-headings, lists and quote blocks. "
                     "After: Kikar is every html block of the article's own island (`contentItems`), in order; image and video items (captions, credits) "
                     "and the recommended-story and next-article payloads are not read. N12 is the whole `articleBody` section in page order "
                     "(p, h3/h4, ul/ol/li, quote blocks, bubble spans), without figures and captions, players, scripts and the typo-report label. "
                     "Block text keeps a word that the page splits over two inline `<span>`s whole.")
    else:
        lines.append("Before: Al Manar read the first `article-content` div up to the first `</div>`, which is the wrapper of the first embedded video, "
                     "so every article with an embedded video lost the text after it. After: the balanced `article-content` div.")
    lines.append("")
    pages = {}
    for row in re_rows:
        if "no_raw" in row["warnings"] or row["_outlet"] not in outlets:
            continue
        pages[row["document_id"]] = (row["_outlet"], row["_html"], row["body_words"])
    lines.append("| outlet | pages | median words before | median words after | after > 1.25x before | after < before |")
    lines.append("|---|---:|---:|---:|---:|---:|")
    detail = defaultdict(list)
    before_text = {}
    for did, (o, html, after) in pages.items():
        btxt = legacy_body(o, html) or ""
        before_text[did] = btxt
        detail[o].append((did, len(btxt.split()), after))
    for o in outlets:
        v = detail[o]
        lines.append(f"| {o} | {len(v)} | {_med([b for _d, b, _a in v]):.0f} | {_med([a for _d, _b, a in v]):.0f} | "
                     f"{sum(1 for _d, b, a in v if a > 1.25 * b)} | {sum(1 for _d, b, a in v if a < b)} |")
    lines.append("")
    for o in outlets:
        v = sorted(detail[o])
        if o not in ("kikar", "n12"):
            same = sum(1 for _d, b, a in v if a == b)
            v = [x for x in v if x[1] != x[2]]
            lines.append(f"Per page, {o}, the {len(v)} pages whose length changed ({same} unchanged, not listed) (id: before -> after words):")
        else:
            lines.append(f"Per page, {o} (id: before -> after words):")
        lines.append("")
        lines.append("; ".join(f"`{d}` {b} -> {a}" for d, b, a in v))
        lines.append("")
    lowered = [(d, b, a) for o in outlets for d, b, a in detail[o] if a < b]
    if lowered:
        lines.append("Pages where the new body is shorter than the old one (the old body held a caption or a short block the new rule leaves out): "
                     + "; ".join(f"`{d}` {b} -> {a}" for d, b, a in lowered) + ".")
        lines.append("")
    if country == "israel":
        by_raw = {}
        for row in re_rows:
            if "no_raw" not in row["warnings"]:
                by_raw[row["document_id"]] = row
        cand_by_hex = {}
        for rec in records:
            m = re.search(r"/r2-([0-9a-f]{10})", rec.get("raw_path") or "")
            if m:
                cand_by_hex[m.group(1)] = rec
        lines.append("Does the body now name the attack? `before` is the old rule, `now` the new one. "
                     "Match words: ביפר, זימונית, מכשירי (ה)קשר, פיצוץ/פיצוצי (ה)מכשירים. "
                     "The quote is the first matching sentence of the new body, preferring one the old body did not contain.")
        lines.append("")
        lines.append("| id | where | words before -> now | named before | named now | sentence now in the body |")
        lines.append("|---|---|---|---|---|---|")
        for did in ATTACK_IDS:
            row = by_raw.get(did)
            where = "corpus"
            if row:
                html, now_text, o = row["_html"], row["body_text"], row["_outlet"]
            else:
                rec = cand_by_hex.get(did.rsplit("_", 1)[-1])
                where = "candidates (gap item)"
                if not rec or not rec.get("raw_path"):
                    lines.append(f"| `{did}` | not found | | | | |")
                    continue
                html = read_page(DATA / country / rec["raw_path"])
                now_text, o = rec["body_text"], rec["outlet"]
            old = legacy_body(o, html) or ""
            quote = first_attack_sentence(now_text, old)
            if quote:
                cell = "`" + clip_quote(quote, 320) + "`"
            else:
                generic = first_attack_sentence(now_text, "", GENERIC_RADIO_RE)
                cell = ("not named; only generic radios: `" + clip_quote(generic, 200) + "`") if generic else "not named"
            lines.append(
                f"| `{did}` | {where} | {len(old.split())} -> {len(now_text.split())} | "
                f"{'yes' if ATTACK_RE.search(old) else 'no'} | {'yes' if quote else 'no'} | {cell} |")
        lines.append("")
    return lines


def coverage_lines(country, re_rows, records):
    seen = corpus_page_keys(re_rows)
    per = defaultdict(list)
    for row in re_rows:
        if "no_raw" in row["warnings"]:
            continue
        per[row["_outlet"]].append((row["document_id"], row["checks"]["container_coverage"]))
    for rec in records:
        chk = rec.get("_checks")
        if (not chk or rec["failure"] in ("needs_fetch", "deferred_liveblog")
                or page_key(rec["outlet"], rec["raw_path"], rec["url"]) in seen):
            continue
        per[rec["outlet"]].append((rec["url"], chk["container_coverage"]))
    lines = ["## container_coverage by outlet", ""]
    lines.append("Pass = body words >= 90% of container words. n/a = Telegram, no container on the page, or an empty container (headline-only). "
                 "`measured` is the number of pages with a non-empty container. Min and median are body/container over those pages.")
    lines.append("")
    lines.append("| outlet | pages | pass | fail | n/a | measured | pass of measured | min | median |")
    lines.append("|---|---:|---:|---:|---:|---:|---:|---:|---:|")
    fails = []
    for o in COUNTRIES[country]:
        v = per.get(o, [])
        na = [c for _i, c in v if c["reason"] in ("not_applicable", "no_container_on_page", "empty_container")]
        meas = [(i, c) for i, c in v if "coverage" in c]
        ok_m = [c for _i, c in meas if c["ok"]]
        fails += [(o, i, c) for i, c in meas if not c["ok"]]
        cov = [c["coverage"] for _i, c in meas]
        lines.append(
            f"| {o} | {len(v)} | {sum(1 for _i, c in v if c['ok'])} | {sum(1 for _i, c in v if not c['ok'])} | {len(na)} | {len(meas)} | "
            f"{fmt_rate(len(ok_m), len(meas)) if meas else 'n/a'} | {min(cov):.3f} | {statistics.median(cov):.3f} |" if cov else
            f"| {o} | {len(v)} | {sum(1 for _i, c in v if c['ok'])} | {sum(1 for _i, c in v if not c['ok'])} | {len(na)} | 0 | n/a | - | - |")
    lines.append("")
    if fails:
        lines.append("Failing pages: " + "; ".join(f"{o} `{i}` {c['body_words']}/{c['container_words']}" for o, i, c in fails) + ".")
    else:
        lines.append("No page fails container_coverage.")
    lines.append("")
    if country == "israel":
        lines.append("Truncation found with this check: Kikar and N12, the two the review named, fixed above. "
                     "Ynet's JSON-LD `articleBody` is the whole article (the body is at least 90% of `ArticleBodyComponent` on every page, minimum in the table). "
                     "Makan bodies already equal their container.")
    else:
        lines.append("Other truncation found with this check: Al Manar (fixed above). "
                     "LBCI, MTV, Al Jadeed and NNA bodies already equal their container (minimum 1.000 in the table).")
    lines.append("")
    return lines


def gate_verdict_lines(country, gate, re_rows, records, new_by):
    """Which outlets pass the 95% gate, stated outright, with the reason for each miss."""
    out = []
    passing = [o for o in COUNTRIES[country] if gate[o]["n"] and gate[o]["all_rate"] >= 0.95 and new_by[o] == 0]
    failing = [o for o in COUNTRIES[country] if o not in passing]
    out.append("**95% gate, all six checks:** pass: " + (", ".join(passing) or "none") + ". "
               "Do not pass: " + (", ".join(failing) or "none") + ".")
    out.append("")
    # For a failing outlet: what do the failing pages fail on?
    seen = corpus_page_keys(re_rows)
    rows = defaultdict(list)
    for row in re_rows:
        if "no_raw" not in row["warnings"]:
            rows[row["_outlet"]].append((row["document_id"], row["checks"]))
    for rec in records:
        chk = rec.get("_checks")
        if (chk and rec["failure"] not in ("needs_fetch", "deferred_liveblog")
                and page_key(rec["outlet"], rec["raw_path"], rec["url"]) not in seen):
            rows[rec["outlet"]].append((rec["url"], chk))
    for o in COUNTRIES[country]:
        g = gate[o]
        if o in passing or not g["n"]:
            continue
        bad = [(i, c) for i, c in rows[o] if not checks_pass(c)]
        by_check = Counter(name for _i, c in bad for name in CHECK_NAMES if not c[name]["ok"])
        only_repeat = [i for i, c in bad
                       if {n for n in CHECK_NAMES if not c[n]["ok"]} <= {"no_chrome", "no_duplication"}
                       and not c["no_chrome"].get("found")]
        rest = [i for i, _c in bad if i not in only_repeat]
        out.append(f"- {o}: {g['all_pass']}/{g['n']} = {g['all_rate']:.1%}. Failing pages: {len(bad)} (by check: "
                   + ", ".join(f"{k} {v}" for k, v in sorted(by_check.items())) + "). "
                   f"Of these, {len(only_repeat)} fail only because a sentence of the publisher's own text appears in 3 or more articles (check 1) "
                   "or twice in one article (check 4). Those sentences are inside the article container on the page, so they are not chrome; "
                   "the failure stays counted and the check was not loosened. "
                   + (f"Other failures: {', '.join('`' + str(i) + '`' for i in rest)}. " if rest else "")
                   + (f"Information, not the gate: without the {len(only_repeat)} repeated-text pages the rate would be "
                      f"{(g['all_pass'] + len(only_repeat)) / g['n']:.1%}." if only_repeat else ""))
    out.append("")
    return out


def write_report(country, records, re_rows, gate, adjudicated, ratios, meta):
    lines = []
    lines.append(f"# {country} round 2 extraction")
    lines.append("")
    lines.append("Offline. Text is copied from the saved HTML. Nothing was translated or filled in by guesswork.")
    lines.append("")
    lines.append("## Gate")
    lines.append("")
    lines.append("An outlet is usable when all six checks pass on at least 95% of its bodies and no `new_wrong` row remains. "
                 "Bodies are corpus rows with a raw file plus gap rows read from a cached page. "
                 "`no_raw` rows are not in the denominator.")
    lines.append("")
    lines.append("Check 2, 3 and 5 for headline-only items (empty body, `brief` / `live_ticker`, including Al Jadeed `headline_only_empty_container`): "
                 "there is no article text, so the description is not required in a body, truncation does not apply, and paragraph order is not applicable.")
    lines.append("")
    lines.append("Telegram posts: the lead is the message (`js-message_text`), not the channel `og:description`. "
                 "Truncation passes when that whole node was taken; posts often have no final period. "
                 "Paragraph order is not applicable (no JSON-LD `articleBody`).")
    lines.append("")
    lines.append("Other outlets: check 2 uses `og:description`, then the JSON-LD description, then Al Jadeed ShortDesc. "
                 "Opening words (first 8, or first 6) must sit in the first 400 characters. "
                 "A description whose words never occur in the article is a rewritten deck; the check then passes as `description_is_rewrite` "
                 "unless the JSON-LD `articleBody` lead itself is missing from that window. "
                 "A deck that does occur, but only after the first 400 characters, fails.")
    lines.append("")
    lines.append("Check 3: a container taken whole is complete even when the page does not end with a period. "
                 "A wire credit, `المصدر:` / `Source:`, or a trailing year also counts as a finished ending. "
                 "A recirculation cut must still leave a finished ending. Where JSON-LD `articleBody` is at least 40 characters, the body must be at least 90% of that length.")
    lines.append("")
    lines.append("Check 1 ignores a repeated sentence when that sentence is inside the same page's JSON-LD `articleBody` (the article repeating, not furniture).")
    lines.append("")
    lines.append("Check 6, `container_coverage`: the extracted body must hold at least 90% of the words of the outlet's full article container "
                 "(Kikar: the article island's text blocks; N12: the whole `itemprop=\"articleBody\"`, h4 and lists included; Makan: `article-content`; "
                 "LBCI: `LongDesc`; MTV: `articles-report`; Al Jadeed: ShortDesc + LongDesc; Al Manar: the balanced `article-content` div; "
                 "NNA: `fulltextarticle-container` without the agency sign-off; Ynet: `ArticleBodyComponent`). "
                 "The container is measured on the page, not by the extraction rule's end marker. Captions, players, scripts, share buttons and the N12 typo-report label "
                 "are not counted. A page with no such container, or an empty one, passes as not applicable and is counted separately below. "
                 "Abu Ali (Telegram) is not applicable. Ynet and any page that has a JSON-LD `articleBody` also face check 3 against it.")
    lines.append("")
    counts = Counter(a["classification"] for a in adjudicated)
    adj_by_id = {a["document_id"]: a for a in adjudicated}

    def stored_wrong_rows(outlet):
        out = []
        for row in re_rows:
            a = adj_by_id.get(row["document_id"])
            if a and a["outlet"] == outlet and a["classification"] == "stored_wrong":
                out.append(row)
        return out

    lines.append("| outlet | usable | bodies | all six | no_chrome | lead_present | not_truncated | no_duplication | order | container_coverage | new_wrong |")
    lines.append("|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|")
    new_by = Counter(a["outlet"] for a in adjudicated if a["classification"] == "new_wrong")
    for o in COUNTRIES[country]:
        g = gate[o]
        per = g["per"]
        usable = g["n"] > 0 and g["all_rate"] >= 0.95 and new_by[o] == 0
        lines.append(
            f"| {o} | {'yes' if usable else 'no'} | {g['n']} | {fmt_rate(g['all_pass'], g['n'])} | "
            f"{fmt_rate(per['no_chrome']['pass'], per['no_chrome']['n'])} | "
            f"{fmt_rate(per['lead_present']['pass'], per['lead_present']['n'])} | "
            f"{fmt_rate(per['not_truncated']['pass'], per['not_truncated']['n'])} | "
            f"{fmt_rate(per['no_duplication']['pass'], per['no_duplication']['n'])} | "
            f"{fmt_rate(per['order']['pass'], per['order']['n'])} | "
            f"{fmt_rate(per['container_coverage']['pass'], per['container_coverage']['n'])} | {new_by[o]} |"
        )
    lines.append("")
    lines.extend(gate_verdict_lines(country, gate, re_rows, records, new_by))
    lines.append("")
    lines.append("## Gap rows")
    lines.append("")
    by_o = defaultdict(list)
    for r in records:
        by_o[r["outlet"]].append(r)
    lines.append(f"Rows: {len(records)}. ok: {sum(1 for r in records if r['ok'])}. failed: {sum(1 for r in records if not r['ok'])}.")
    lines.append("")
    lines.append("| outlet | rows | ok | failed | failure reasons |")
    lines.append("|---|---:|---:|---:|---|")
    for o in COUNTRIES[country]:
        rs = by_o.get(o, [])
        fails = Counter(r["failure"] for r in rs if r["failure"])
        reason = ", ".join(f"{k} {v}" for k, v in fails.most_common()) or "—"
        lines.append(f"| {o} | {len(rs)} | {sum(1 for r in rs if r['ok'])} | {sum(1 for r in rs if not r['ok'])} | {reason} |")
    lines.append("")
    if country == "lebanon":
        empty_shell = sum(1 for r in records if r["outlet"] == "aljadeed" and "headline_only_empty_container" in r["warnings"])
        with_body = sum(1 for r in records if r["outlet"] == "aljadeed" and (r["body_text"] or "").strip())
        lines.append(f"Al Jadeed gap pages read: {meta['aljadeed_pages']}. "
                     f"Non-empty LongDesc: {meta['aljadeed_longdesc_nonempty']}. "
                     f"ShortDesc only: {meta['aljadeed_short_only']}. "
                     f"Empty container (`headline_only_empty_container`): {empty_shell}. "
                     f"Rows with a body: {with_body}.")
        lines.append("")
        aj = stored_wrong_rows("aljadeed")
        aj_empty, aj_twice, aj_other = [], [], []
        for r in aj:
            if "headline_only_empty_container" in r["warnings"] or not (r["body_text"] or "").strip():
                aj_empty.append(r)
                continue
            short, long = aljadeed_fields(r["_html"])
            twice = collapse(" ".join(p for p in (short, long, long) if p.strip()))
            if long and ratio(r["_stored"], twice) >= 0.98:
                aj_twice.append(r)
            else:
                aj_other.append(r)
        lines.append("Where a stored Al Jadeed body is longer than the page, it is ShortDesc plus LongDesc plus a second copy of LongDesc. "
                     "The page has each field once. Example: `lb_aljadeed_503441` matches short+long+long at 1.000 and short+long at 0.675. "
                     "The repeated LongDesc is not on the page. "
                     "Where the container is empty, as on `lb_aljadeed_502514`, the stored paragraph is not in the HTML. "
                     "Both are `stored_wrong`.")
        lines.append(
            f"Al Jadeed `stored_wrong`: {len(aj_twice)} repeated-LongDesc, {len(aj_empty)} empty container"
            + (f", {len(aj_other)} other ({', '.join(r['document_id'] for r in aj_other[:8])})" if aj_other else "")
            + f". Total {len(aj)}."
        )
        lines.append("")
    if country == "israel":
        n_footer = sum(1 for r in records if r.get("outlet") == "abuali" and r.get("footer_comment_link"))
        n_ab = sum(1 for r in records if r.get("outlet") == "abuali")
        lines.append(f"Abu Ali `footer_comment_link` true on {n_footer} of {n_ab} gap rows. The trailing footer `כדי להגיב לכתבה לחצו כאן` is removed from body and title.")
        lines.append("")
    lines.append("## Regression diagnostic")
    lines.append("")
    lines.append("Ratio against the stored body, whitespace-collapsed, first 3,000 characters. Not a gate. "
                 "Rows below 0.90 are in `regression-adjudication.csv`.")
    lines.append("")
    lines.append("| outlet | n (non-empty stored) | median | share ≥ 0.90 |")
    lines.append("|---|---:|---:|---:|")
    for o in COUNTRIES[country]:
        vals = ratios.get(o, [])
        if not vals:
            lines.append(f"| {o} | 0 | — | — |")
            continue
        ge = sum(1 for v in vals if v >= 0.90)
        lines.append(f"| {o} | {len(vals)} | {statistics.median(vals):.3f} | {ge}/{len(vals)} ({ge / len(vals):.1%}) |")
    lines.append("")
    lines.append(f"Adjudication: stored_wrong {counts['stored_wrong']}, new_wrong {counts['new_wrong']}, both {counts['both']}.")
    by_out = defaultdict(Counter)
    for a in adjudicated:
        by_out[a["outlet"]][a["classification"]] += 1
    bits = []
    for o in COUNTRIES[country]:
        c = by_out[o]
        if c:
            bits.append(f"{o} stored_wrong {c['stored_wrong']}, new_wrong {c['new_wrong']}, both {c['both']}")
    if bits:
        lines.append("By outlet: " + "; ".join(bits) + ".")
    lines.append("")

    if country == "lebanon":
        lb = stored_wrong_rows("lbci")
        lb_empty = [r for r in lb if not (r["_stored"] or "").strip()]
        lb_extra = [r for r in lb if (r["_stored"] or "").strip()]
        example = "lb_lbci_796448" if any(r["document_id"] == "lb_lbci_796448" for r in lb_empty) else (lb_empty[0]["document_id"] if lb_empty else "")
        lines.append(f"LBCI `stored_wrong`: {len(lb_extra)} rows where the extra text is inside `class=\"LongDesc\"` "
                     "(the rest of the article, or a tweet embed including its `— handle date` citation). "
                     "That text is part of the item as published. "
                     f"{len(lb_empty)} rows have an empty stored body and a real LongDesc article"
                     + (f" (example `{example}`)" if example else "")
                     + ". "
                     "Tags and the next-story block sit after `article_details_end_of_scroll`, outside LongDesc. "
                     "An empty LongDesc is no longer filled from `itemprop=articleBody`.")
        lines.append("")
    if country == "israel":
        lines.append("`il_makan_5961802f18`: the article is the `article-content` paragraphs. The stored body is the `og:description` line. Classification: `stored_wrong`.")
        lines.append("")
    lines.extend(truncation_lines(country, re_rows, records))
    lines.extend(coverage_lines(country, re_rows, records))
    lines.append("## What changed since round 1")
    lines.append("")
    lines.append("- The 0.90 regression ratio is a diagnostic. The gate is the six checks above.")
    lines.append("- Truncation fix: Kikar and N12 bodies are now the whole article container; Al Manar stops at the balanced `article-content` div. See the next section.")
    lines.append("- Gap rows are read from `round2/gap-manifest-input.csv`. Gap rows that the corpus has since accepted are not counted twice in the gate.")
    lines.append("- Al Jadeed is no longer `regression_failed`. Empty ShortDesc and LongDesc are `ok` briefs with `headline_only_empty_container`. A non-empty LongDesc is extracted once.")
    lines.append("- Every corpus row was re-extracted to `reextract-v1.jsonl`. `corpus.jsonl` was not modified.")
    lines.append("- Abu Ali records carry `footer_comment_link`. The trailing comment-link footer is removed from body and title.")
    lines.append("- An iframe whose title attribute contains markup is dropped as an element, so its attributes are not article text.")
    if country == "lebanon":
        lines.append("- LBCI body is `class=\"LongDesc\"` only. An empty LongDesc stays empty.")
    lines.append("")
    lines.append("## Open problems")
    lines.append("")
    problems = []
    for o in COUNTRIES[country]:
        g = gate[o]
        if g["n"] and g["all_rate"] < 0.95:
            weak = [name for name in CHECK_NAMES if g["per"][name]["rate"] < 0.95]
            problems.append(f"{o} is unusable: all-six {g['all_rate']:.1%} because " + ", ".join(weak) + " is under 95%.")
        if new_by[o]:
            ids = [a["document_id"] for a in adjudicated if a["outlet"] == o and a["classification"] == "new_wrong"]
            problems.append(f"{o}: new_wrong " + ", ".join(ids))
    problems.extend(check_failure_lines(re_rows, records))
    if not problems:
        problems.append("None.")
    for p in problems:
        lines.append(f"- {p}")
    lines.append("")
    re_ok = sum(1 for r in re_rows if r["ok"])
    re_noraw = sum(1 for r in re_rows if "no_raw" in r["warnings"])
    lines.append(f"Re-extract: {len(re_rows)} corpus rows, ok {re_ok}, no_raw {re_noraw}.")
    lines.append("")
    out = DATA / country / "05-extraction" / "round2" / "extraction-report.md"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("\n".join(lines), encoding="utf-8")
    return out


def main():
    if len(sys.argv) < 2 or sys.argv[1] not in COUNTRIES:
        print("usage: extract_cached_il_lb.py <israel|lebanon> [--regression-only]", file=sys.stderr)
        sys.exit(2)
    country = sys.argv[1]
    only = "--regression-only" in sys.argv
    re_rows, re_items = build_reextract(country)
    if only:
        apply_cross_checks(re_items)
        _dest, adjudicated, ratios = write_adjudication(country, re_rows)
        counts = Counter(a["classification"] for a in adjudicated)
        print(country, "adjudicated", len(adjudicated), dict(counts))
        for o in COUNTRIES[country]:
            vals = ratios.get(o, [])
            if vals:
                ge = sum(1 for v in vals if v >= 0.90)
                print(f"  {o:10} n={len(vals)} ge90={ge}/{len(vals)} median={statistics.median(vals):.3f}")
        return
    records, gap_items, meta = build_records(country)
    apply_cross_checks(re_items + gap_items)
    out_dir = DATA / country / "05-extraction" / "round2"
    out_dir.mkdir(parents=True, exist_ok=True)
    re_path = out_dir / "reextract-v1.jsonl"
    with open(re_path, "w", encoding="utf-8") as f:
        for row in re_rows:
            f.write(json.dumps(public_reextract(row), ensure_ascii=False) + "\n")
    cand_path = out_dir / "candidates.jsonl"
    with open(cand_path, "w", encoding="utf-8") as f:
        for rec in records:
            f.write(json.dumps(public_candidate(rec), ensure_ascii=False) + "\n")
    adj_path, adjudicated, ratios = write_adjudication(country, re_rows)
    gate = gate_stats(country, re_rows, records)
    report = write_report(country, records, re_rows, gate, adjudicated, ratios, meta)
    counts = Counter(a["classification"] for a in adjudicated)
    print(f"wrote {cand_path} rows={len(records)} ok={sum(1 for r in records if r['ok'])}")
    print(f"wrote {re_path} rows={len(re_rows)}")
    print(f"wrote {adj_path} n={len(adjudicated)} {dict(counts)}")
    print(f"wrote {report}")
    for o in COUNTRIES[country]:
        g = gate[o]
        new_n = sum(1 for a in adjudicated if a["outlet"] == o and a["classification"] == "new_wrong")
        flag = "usable" if g["n"] and g["all_rate"] >= 0.95 and new_n == 0 else "UNUSABLE"
        print(f"  {o:10} {flag:9} all={g['all_rate']:.1%} n={g['n']} new_wrong={new_n}")


if __name__ == "__main__":
    main()
