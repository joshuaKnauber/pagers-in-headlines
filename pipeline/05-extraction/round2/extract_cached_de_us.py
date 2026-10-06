#!/usr/bin/env python3
"""Offline round-2 extraction from the recall audit's saved Germany/US pages.

Usage: python3 extract_cached_de_us.py <germany|us> [--regression-only]

This deliberately has no HTTP client.  Every candidate is traceable to the
audit cache and its raw copy is made byte-for-byte before extraction.
"""
import csv
import difflib
import gzip
import hashlib
import html
import json
import os
import random
import re
import statistics
import sys
from collections import Counter, defaultdict
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
DATA = ROOT / "data"


# Each outlet's extraction choices are together here.  Class matches are
# substrings because publishers deploy hashed CSS class names.  A container is
# never selected from the whole page by a generic paragraph sweep.
RULES = {
    "germany": {
        "bild": {"containers": [("class", "article-body")],
                 "cut": ["Haben Sie eine Meinung zu diesem Artikel?"], "suffix": ["BILD"]},
        "ntv": {"containers": [("class", "article-detail"), ("class", "article-body"),
                                ("class", "article__text")],
                "cut": ["ntv bei Google bevorzugen", "Weitere Artikel"], "suffix": ["ntv.de", "n-tv.de"]},
        "rnd": {"containers": [("class", "Articlestyled__ArticleBodyWrapper"), ("id", "contentMain"), ("class", "contentMain"),
                                ("class", "ArticleBody")],
                "cut": ["Das tägliche Kreuzworträtsel", "Kreuzworträtsel"], "suffix": ["RND"]},
        "rtl": {"containers": [("class", "article-body"), ("class", "article-content")],
                "cut": ["Mehr zum Thema", "Auch interessant"], "suffix": ["RTL.de", "RTL"]},
        "spiegel": {"containers": [("class", "RichText--sans"), ("class", "RichText")],
                   "cut": ["Dialog schließen", "Mehr zum Thema", "Merkliste hinzufügen",
                           "Mehr zur Lage im Nahostkonflikt lesen Sie", "lesen Sie in der SPIEGEL-Titelstory"],
                   "suffix": ["DER SPIEGEL", "SPIEGEL"]},
        "tagesschau": {"containers": [("class", "article__content"), ("class", "meldung__text"),
                                         ("class", "content")],
                       "cut": ["Mehr zum Thema"], "suffix": ["tagesschau.de"]},
        "tonline": {"containers": [("class", "ArticleBody"), ("class", "article-body-stage"),
                                      ("class", "article-body")],
                    "cut": ["Mehr zum Thema", "Auch interessant", "Den täglichen Tagesanbruch-Newsletter",
                           "Tagesanbruch-Newsletter können Sie", "Alle Tagesanbruch-Ausgaben",
                           "Alle Nachrichten lesen Sie hier"], "suffix": ["t-online"]},
        "welt": {"containers": [("class", "c-article-page__text"), ("class", "c-rich-text-renderer--article"),
                                   ("class", "article-content")],
                 "cut": ["Mehr zum Thema", "Auch interessant", "Alle Inhalte"], "suffix": ["WELT", "DIE WELT"]},
        "zdfheute": {"containers": [("class", "article__content"), ("class", "article-text"),
                                       ("class", "article-content")],
                     "cut": ["Mehr zum Thema", "Weitere Nachrichten"], "suffix": ["ZDFheute"]},
    },
    "us": {
        "abc": {"containers": [("class", "Article__Content"), ("class", "article-body"),
                                  ("class", "Article__Body")],
                "cut": ["Trending Reader Picks", "Read More"], "suffix": ["ABC News"]},
        "ap": {"containers": [("class", "RichTextStoryBody")],
               "cut": ["More explosions have been reported in Lebanon following the pager attack Tuesday. Follow AP’s live updates.",
                       "More explosions have been reported in Lebanon following the pager attack Tuesday. Follow AP's live updates."],
               "suffix": ["AP News", "AP"]},
        "cbs": {"containers": [("class", "content__body"), ("class", "article-content"),
                                  ("class", "ArticleBody")],
                "cut": ["More from CBS News", "Read more"], "suffix": ["CBS News"]},
        "cnn": {"containers": [("class", "article__content"), ("class", "body tabcontent"),
                                  ("class", "article__body")],
                "cut": ["CNN Newsource", "Related video", "\U0001f4e7 Check out all of CNN"], "suffix": ["CNN"]},
        "fox": {"containers": [("class", "article-body"), ("class", "td-post-content")],
                "cut": ["Get all the stories you need-to-know", "Click here to get the Fox News app", "Read more"],
                "suffix": ["Fox News"]},
        "nbc": {"containers": [("class", "article-body"), ("class", "article-body__content"),
                                  ("class", "article-content")],
                "cut": ["More from NBC News", "Sign up for"], "suffix": ["NBC News"]},
        "nyt": {"containers": [("class", "StoryBodyCompanionColumn"), ("class", "meteredContent"),
                                  ("name", "article")],
                "cut": ["Advertisement", "Continue reading the main story"], "suffix": ["The New York Times", "NYTimes.com"]},
        "reuters": {"containers": [("class", "article-body__paragraph"), ("class", "article-body__content"), ("class", "article-body__container"),
                                      ("class", "article__content")],
                    "cut": ["Read Next", "Suggested Topics", "More from Reuters"], "suffix": ["Reuters"]},
        "usatoday": {"containers": [("class", "gnt_ar_b"), ("class", "article-body"),
                                       ("class", "articleBody")],
                     "cut": ["Read more", "Our team of experts"], "suffix": ["USA TODAY"]},
        "wapo": {"containers": [("class", "article-body"), ("class", "article-content")],
                 "cut": ["History: The roots of the Israeli-Palestinian conflict"], "suffix": ["The Washington Post"]},
        "yahoo": {"containers": [("name", "article"), ("class", "col-body")],
                  "cut": ["Return to Homepage", "Recommended Stories", "Why you can trust us"],
                  "suffix": ["Yahoo News", "Yahoo"]},
    },
}

REGRESSION_JUDGMENTS = {
    "germany": {
        "bild": "Stored bodies in the lowest comparisons contain ticker or video-overlay text before the article. The stored body is not a fair article-body reference, but the outlet still fails the stated bar.",
        "rnd": "The low comparisons include stored crossword or related-story tails, and one two-word stored body. The stored body is wrong in those cases; the outlet nevertheless misses the stated share threshold.",
        "spiegel": "Many stored bodies begin with share controls or print-page text. The stored body is wrong for those pages, but the remaining comparison set still fails the bar.",
        "zdfheute": "The saved pages carry prose in the React page state while the historic bodies are much longer generic-page collections. The extractor cannot reproduce the stored bodies without taking page chrome, so this outlet is skipped.",
    },
    "us": {
        "fox": "Several stored bodies start with video-overlay text. The stored body is not a fair clean-body reference, but the outlet still fails the stated bar.",
        "reuters": "The stored records retain Reuters summary/header material that the article-paragraph rule excludes. The extractor is cleaner but does not pass the required comparison bar.",
        "usatoday": "The saved page has metadata but no recoverable article container. This is an extractor/source limitation, so the outlet is skipped.",
        "wapo": "The article-body rule does not reproduce the stored lead, caption and byline sequence. Treat the extractor as failing this outlet rather than accepting a low-ratio substitute.",
        "yahoo": "The lowest comparisons include a different page-state body or Yahoo key-takeaway material. The stored body is not consistently a fair clean-body reference, but the outlet still misses the stated threshold.",
    },
}


class Node:
    def __init__(self, tag, attrs, parent=None):
        self.tag, self.attrs, self.parent, self.children = tag, dict(attrs), parent, []


class Tree(HTMLParser):
    VOID = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "param", "source", "track", "wbr"}
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.root = Node("root", [])
        self.stack = [self.root]
    def handle_starttag(self, tag, attrs):
        n = Node(tag.lower(), attrs, self.stack[-1]); self.stack[-1].children.append(n)
        if tag.lower() not in self.VOID: self.stack.append(n)
    def handle_startendtag(self, tag, attrs): self.handle_starttag(tag, attrs)
    def handle_endtag(self, tag):
        tag = tag.lower()
        for i in range(len(self.stack) - 1, 0, -1):
            if self.stack[i].tag == tag:
                self.stack = self.stack[:i]
                return
    def handle_data(self, data): self.stack[-1].children.append(data)


def clean(s):
    return " ".join(html.unescape(s or "").split())


def descendants(node):
    for x in node.children:
        if isinstance(x, Node):
            yield x
            yield from descendants(x)


SKIP_TAGS = {"script", "style", "noscript", "svg", "button", "nav", "footer", "aside", "form"}
# Space at block boundaries only. Joining every text node with a space turns "fighters," into "fighters ,".
BLOCK_TAGS = {"p", "div", "h1", "h2", "h3", "h4", "h5", "h6", "li", "tr", "blockquote",
              "section", "article", "figcaption", "ul", "ol", "figure", "br", "header"}


def node_text(node):
    bits = []
    def walk(x):
        if isinstance(x, str):
            bits.append(x)
        elif x.tag in SKIP_TAGS:
            return
        else:
            if x.tag in BLOCK_TAGS:
                bits.append(" ")
            for c in x.children:
                walk(c)
            if x.tag in BLOCK_TAGS:
                bits.append(" ")
    walk(node)
    return clean("".join(bits))


def match_node(node, kind, value):
    if kind == "name": return node.tag == value
    return value.lower() in node.attrs.get(kind, "").lower()


def choose_node(tree, rules):
    all_nodes = [tree.root] + list(descendants(tree.root))
    for kind, value in rules["containers"]:
        candidates = [n for n in all_nodes if match_node(n, kind, value)]
        if candidates:
            # The largest matching article region is more likely to contain the prose.
            return max(candidates, key=lambda n: len(node_text(n)))
    return None


def is_caption(node):
    def bad(p):
        if p.tag in {"figcaption", "figure"}:
            return True
        cl = p.attrs.get("class", "").lower()
        return "caption" in cl or "fig__caption" in cl
    return bad(node) or has_ancestor(node, bad)


def is_link_only(node):
    anchors = [c for c in descendants(node) if isinstance(c, Node) and c.tag == "a"]
    if len(anchors) != 1:
        return False
    return node_text(node) == node_text(anchors[0])


def sentence_ended(text):
    # German closing quotes are “ (U+201C) and «, after the period.
    return bool(re.search(r"(?:[.!?…]|\.\.\.)[\"'“”„«»’)\]]*$", text.strip()))


def paragraphs(node, skip=(), stop=()):
    """Paragraphs and prose list items inside one article container.

    skip: class substrings of promo wrappers to leave out. stop: heading texts that end the article."""
    if node is None:
        return []
    if node.tag == "div" and "article-body__paragraph" in node.attrs.get("class", ""):
        return [node_text(node)]
    ps = []
    for n in descendants(node):
        if stop and n.tag in {"h2", "h3"} and node_text(n).lower() in stop:
            break
        if n.tag not in {"p", "li"} or is_caption(n):
            continue
        if skip and has_ancestor(n, lambda p: any(k in p.attrs.get("class", "") or k in p.attrs.get("data-testid", "")
                                                  for k in skip)):
            continue
        if n.tag == "li" and any(c.tag == "p" for c in descendants(n)):
            continue
        if has_ancestor(n, lambda p: p.tag in {"nav", "footer", "aside"} or p.attrs.get("role") == "complementary" or
                        any(k in p.attrs.get("class", "").lower() for k in ("related", "recommend", "recirc", "newsletter"))):
            continue
        text = node_text(n)
        words = text.split()
        if len(words) < 3 or text in ps:
            continue
        if is_link_only(n) and not sentence_ended(text):
            continue
        # A related-link list is short and untitled. Prose items in the article are full sentences.
        if n.tag == "li" and (len(words) < 15 or not sentence_ended(text)):
            continue
        ps.append(text)
    return ps


def ancestors(node):
    while node.parent:
        node = node.parent
        yield node


def has_ancestor(node, predicate):
    return any(predicate(parent) for parent in ancestors(node))


def article_paragraphs(tree, outlet, url="", fields=None):
    """Return the publisher's rendered article paragraphs in document order.

    Selectors name publisher structure. They do not sweep the page for paragraphs.
    """
    fields = fields or {}
    nodes = list(descendants(tree.root))
    out = []
    def add(text):
        text = clean(text)
        if len(text.split()) >= 3 and text not in out:
            out.append(text)

    if outlet == "ntv":
        # The rendered storyline: bold lead text, paragraphs and subheads, in document order.
        # Teaser cards, share bar and related-video widgets use other classes.
        for n in nodes:
            cl = n.attrs.get("class", "")
            if n.tag in {"p", "h2", "h3"} and ("storyline_lead_text_leadtext" in cl or "storyline_paragraph_p" in cl
                                                or "storyline_subheadline" in cl) and not is_caption(n):
                add(node_text(n))
        return out
    if outlet == "spiegel":
        # Lead is loose text in the first RichText--sans block. The article is the
        # data-area=text blocks on a normal story and data-area=multibox on a video story.
        # Captions, the paywall box, podcast promo and share bar live in other data-areas.
        for n in nodes:
            cl = n.attrs.get("class", "")
            if n.tag != "div" or "RichText--sans" not in cl:
                continue
            if any(c.tag == "p" for c in descendants(n)):
                continue
            if is_caption(n) or has_ancestor(n, lambda p: p.attrs.get("data-area") in
                                              {"nav-bar", "footer", "header-bar", "audio-player", "paywall", "contentbox"}):
                continue
            text = node_text(n)
            if len(text.split()) >= 8:
                add(text)
                break
        for n in nodes:
            if n.tag != "p" or is_caption(n):
                continue
            area = ""
            for p in ancestors(n):
                if p.attrs.get("data-area"):
                    area = p.attrs["data-area"]
                    break
            if area in {"text", "multibox"}:
                add(node_text(n))
        if len(out) > 1 and out[0] in "\n".join(out[1:]):
            out = out[1:]
        return out
    if outlet == "wapo":
        # The deck is the subheadline in the header. font-copy is the article.
        for n in nodes:
            if n.tag == "p" and n.attrs.get("data-testid") == "subheadline":
                add(node_text(n))
                break
        for n in nodes:
            if n.tag == "p" and "font-copy" in n.attrs.get("class", "") and not is_caption(n):
                add(node_text(n))
        return out
    if outlet == "zdfheute":
        # Paragraph classes are hashed per build. The article paragraphs are the <p>
        # elements in <main> that are not inside a teaser <article>, a caption or a byline.
        mains = [n for n in nodes if n.tag == "main"]
        if not mains:
            return []
        for n in descendants(mains[0]):
            if n.tag != "p":
                continue
            # A quote card is a <blockquote> inside a <figure>; the speaker sits in the <figcaption>, which is skipped.
            quote_card = (has_ancestor(n, lambda p: p.tag == "blockquote")
                          and not has_ancestor(n, lambda p: p.tag == "figcaption"))
            if is_caption(n) and not quote_card:
                continue
            if has_ancestor(n, lambda p: p.tag in {"article", "aside", "footer"}):
                continue
            text = node_text(n)
            if len(text.split()) < 3:
                continue
            if re.match(r"von\s+\S", text, re.I) and len(text.split()) < 16:
                continue
            if "ZDF-Studio" in text and len(text.split()) < 16:
                continue
            if "WhatsApp" in text or "Zur Anmeldung" in text:
                continue
            # Consent copy for an embedded graphic, repeated once per embed.
            if "speichern wir Ihre Zustimmung" in text or "Ein Klick für den Datenschutz" in text:
                continue
            add(text)
        return out
    if outlet == "fox":
        for n in nodes:
            if n.tag not in {"p", "h2", "h3"}:
                continue
            # "article-content-wrap" is the page column and includes the sidebar. The article is the
            # element whose class token is article-content.
            if not has_ancestor(n, lambda p: "article-content" in p.attrs.get("class", "").split()):
                continue
            if is_caption(n) or is_link_only(n):
                continue
            if has_ancestor(n, lambda p: p.tag == "aside" or "sidebar" in p.attrs.get("class", "") or "newsletter" in p.attrs.get("class", "")
                            or p.attrs.get("class", "") in {"author-bio", "article-meta"}):
                continue
            text = node_text(n)
            if "CLICK HERE TO GET" in text.upper() or "successfully subscribed" in text.lower():
                continue
            add(text)
        return out
    if outlet == "yahoo":
        arts = [n for n in nodes if n.tag == "article"]
        phrase = " ".join(lead_words(fields.get("title", ""))[:6])
        matched = [n for n in arts if phrase and phrase in " ".join(lead_words(node_text(n)[:500]))]
        chosen = max(matched, key=lambda n: len(node_text(n))) if matched else (arts[0] if arts else None)
        if not chosen:
            return []
        for n in descendants(chosen):
            if n.tag != "p" or is_caption(n):
                continue
            if has_ancestor(n, lambda p: "takeaway" in p.attrs.get("class", "").lower()):
                continue
            text = node_text(n)
            if "key takeaways" in text.lower() and len(text.split()) < 50:
                continue
            if is_link_only(n) and not sentence_ended(text):
                continue
            add(text)
        return out
    if outlet == "usatoday":
        for n in nodes:
            if n.tag != "p" or is_caption(n) or not has_ancestor(n, lambda p: p.tag == "article"):
                continue
            text = node_text(n)
            # A section-link card is rendered as a paragraph, but is not prose.
            if sentence_ended(text):
                add(text)
        return out
    if outlet == "reuters":
        for n in nodes:
            if "article-body__paragraph" in n.attrs.get("class", "") and not is_caption(n):
                add(node_text(n))
        return out
    if outlet == "tonline":
        stages = [n for n in nodes if "article-body-stage" in n.attrs.get("class", "") and not
                  has_ancestor(n, lambda p: "article-body-stage" in p.attrs.get("class", ""))]
        if not stages:
            return []
        def stamped(n):
            return bool(re.search(r"\b\d{1,2}[.:]\d{2}\s*Uhr", node_text(n)[:140]))
        if any(stamped(n) for n in stages) or "newsblog" in (url or "").lower():
            use = [n for n in stages if len(node_text(n).split()) > 30]
        else:
            # Top-level stages of one article are sometimes a duplicate copy of the same
            # text and sometimes the next section (a newsletter continues in a second stage).
            # Keep a later stage only when its sentences are not already in an earlier one.
            use, seen = [], ""
            ranked = sorted(stages, key=lambda n: len(node_text(n)), reverse=True)
            for n in ranked:
                text = node_text(n)
                if len(text.split()) <= 30:
                    continue
                found = sentences(text, 8)
                if found and sum(s.lower() in seen for s in found) / len(found) >= 0.5:
                    continue
                use.append(n)
                seen += "\n" + text.lower()
            use = [n for n in stages if n in use]
        for stage in use:
            for para in paragraphs(stage, skip=("ConsentLayer",)):
                add(para)
        return out
    if outlet == "rnd":
        # The deck is the article subhead. The body wrapper is the prose.
        for n in nodes:
            if n.tag == "p" and "ArticleSubHead" in n.attrs.get("class", ""):
                add(node_text(n))
                break
        bodies = [n for n in nodes if "ArticleBody" in n.attrs.get("class", "") or
                  "Articlestyled__ArticleBodyWrapper" in n.attrs.get("class", "")]
        chosen = next((n for n in bodies if "ArticleBodyWrapper" in n.attrs.get("class", "")), None)
        if chosen is None and bodies:
            chosen = max(bodies, key=lambda n: len(node_text(n)))
        # Newsletter call-to-action widgets, "Mehr zum Thema" teaser blocks, and the "Abonnieren Sie auch" footer.
        for para in paragraphs(chosen, skip=("CallToAction", "NewsletterWidget", "MoreItems", "ContentTeaser"),
                               stop=("abonnieren sie auch",)):
            add(para)
        return out
    if outlet == "welt":
        for n in nodes:
            if n.tag != "p" or is_caption(n):
                continue
            if has_ancestor(n, lambda p: "c-inline-alert" in p.attrs.get("class", "")
                            or "preferred-sources" in p.attrs.get("class", "")):
                continue
            intro = has_ancestor(n, lambda p: "c-article-page__intro" in p.attrs.get("class", ""))
            body = has_ancestor(n, lambda p: "c-article-page__text" in p.attrs.get("class", "")
                                or "c-rich-text-renderer--article" in p.attrs.get("class", ""))
            if not intro and not body:
                continue
            text = node_text(n)
            if text.startswith("Klicken Sie hier, um sich Artikel von WELT"):
                continue
            add(text)
        return out
    if outlet == "nyt":
        for n in nodes:
            if n.tag == "p" and n.attrs.get("id") == "article-summary":
                add(node_text(n))
        for n in nodes:
            if n.tag != "p" or is_caption(n):
                continue
            if not has_ancestor(n, lambda p: p.attrs.get("id") == "story"
                                or "StoryBodyCompanionColumn" in p.attrs.get("class", "")):
                continue
            # The truncator wrapper holds the article. Only the message nodes are the access wall.
            if has_ancestor(n, lambda p: p.attrs.get("data-testid") == "optimistic-truncator-message"
                            or p.attrs.get("id") == "optimistic-truncator-a11y"):
                continue
            # <noscript> fallback text, the "Our coverage" link guide, and the author-bio block at the foot.
            if has_ancestor(n, lambda p: p.tag == "noscript" or p.attrs.get("id") == "styln-guide"
                            or "bottom-of-article" in p.attrs.get("class", "")):
                continue
            text = node_text(n)
            if "verify access" in text.lower() or text.startswith("Want all of The Times"):
                continue
            if sentence_ended(text) or len(text.split()) >= 15:
                add(text)
        return out
    if outlet == "abc":
        for n in nodes:
            if n.tag == "p" and "Article__Headline__Desc" in n.attrs.get("class", ""):
                add(node_text(n))
                break
        for n in nodes:
            if n.tag != "p" or is_caption(n):
                continue
            if not has_ancestor(n, lambda p: "Article__Content" in p.attrs.get("class", "")):
                continue
            add(node_text(n))
        return out
    if outlet == "cnn":
        # Video pages put a one-line slate ("X joins The Lead") in the player, not an article.
        for n in nodes:
            if n.tag != "p" or is_caption(n):
                continue
            if has_ancestor(n, lambda p: "video-resource" in p.attrs.get("class", "")
                            or "video-inline" in p.attrs.get("class", "")):
                continue
            if not has_ancestor(n, lambda p: "article__content" in p.attrs.get("class", "")
                                or "article__body" in p.attrs.get("class", "")):
                continue
            text = node_text(n)
            if sentence_ended(text) or len(text.split()) >= 15:
                add(text)
        return out
    return None


# Wrapper classes that hold promo or programme-info paragraphs inside an article container.
PARA_SKIP = {"nbc": ("byline", "expanded-byline"), "tagesschau": ("sendungsbezug", "meldungsfooter", "teaser-absatz", "teaser", "absatzbild")}


def ld_items(source):
    out = []
    ld_re = re.compile(
        r'<script\b[^>]*type\s*=\s*(?:"application/ld\+json"|\'application/ld\+json\'|application/ld\+json)[^>]*>(.*?)</script\s*>',
        re.I | re.S)
    for m in ld_re.finditer(source):
        try: value = json.loads(html.unescape(m.group(1).strip()))
        except (ValueError, TypeError): continue
        stack = value if isinstance(value, list) else [value]
        while stack:
            item = stack.pop()
            if isinstance(item, list): stack.extend(item); continue
            if not isinstance(item, dict): continue
            graph = item.get("@graph")
            if isinstance(graph, list): stack.extend(graph)
            out.append(item)
    return out


def _attr(tag, name):
    m = re.search(r'(?:^|\s)' + name + r'\s*=\s*(?:"([^"]*)"|\'([^\']*)\'|([^\s"\'=<>`]+))', tag, re.I)
    if not m:
        return ""
    return html.unescape(next(g for g in m.groups() if g is not None))


def meta(source, name):
    want = name.lower()
    for m in re.finditer(r"<meta\b[^>]*>", source, re.I):
        tag = m.group(0)
        key = (_attr(tag, "property") or _attr(tag, "name") or _attr(tag, "itemprop")).lower()
        if key == want:
            return clean(_attr(tag, "content"))
    return ""


def page_fields(source):
    items = ld_items(source)
    accepted = {"newsarticle", "article", "reportagenewsarticle", "analysisnewsarticle", "opinionnewsarticle", "videobject", "liveblogposting", "blogposting"}
    choice = None
    for item in items:
        ty = item.get("@type", [])
        ty = ty if isinstance(ty, list) else [ty]
        if any(str(x).lower() in accepted for x in ty):
            choice = item
            if item.get("articleBody") or item.get("headline"): break
    title = clean((choice or {}).get("headline") or (choice or {}).get("name") or meta(source, "og:title"))
    desc = clean((choice or {}).get("description") or meta(source, "og:description") or meta(source, "description"))
    when = str((choice or {}).get("datePublished") or (choice or {}).get("uploadDate") or "")
    date_source = "ld-json" if when else ""
    if not when:
        when = meta(source, "article:published_time") or meta(source, "datePublished") or meta(source, "date")
        date_source = "meta" if when else ""
    body = clean((choice or {}).get("articleBody") if choice else "")
    canonical = ""
    m = re.search(r'<link\b[^>]*rel=["\']canonical["\'][^>]*href=["\']([^"\']+)', source, re.I)
    if not m: m = re.search(r'<link\b[^>]*href=["\']([^"\']+)["\'][^>]*rel=["\']canonical["\']', source, re.I)
    if m: canonical = clean(m.group(1))
    canonical = re.sub(r'^https?://web\.archive\.org/web/\d+(?:id_)?/', '', canonical or meta(source, "og:url"))
    return {"title": title, "description": desc, "when": when, "date_source": date_source,
            "ld_body": body, "canonical": canonical, "items": items}


def title_clean(title, suffixes):
    title = clean(title)
    for suffix in suffixes:
        title = re.sub(r"\s*[|\-–—]\s*" + re.escape(suffix) + r"(?:\.de)?\s*$", "", title, flags=re.I)
    # Section or type labels the page appends to the headline (Bild "| Politik", Welt "- Video").
    title = re.sub(r"\s*\|\s*(?:Politik|News|Unterhaltung|Sport|Geld|Ratgeber|Regional|Video)\s*$", "", title)
    title = re.sub(r"\s+[-\u2013]\s+(?:Video|Podcast)\s*$", "", title)
    return title.strip()


def trim_chrome(texts, cut_markers):
    out = []
    for text in texts:
        if not text: continue
        for marker in cut_markers:
            pos = text.lower().replace("\u2019", "'").find(marker.lower().replace("\u2019", "'"))
            if pos >= 0:
                text = text[:pos].strip()
        if text: out.append(text)
    return out


def structured_body(source, outlet):
    """Read publisher page-state fields when the rendered article is absent.

    These are exact text fields in the saved page, not an inferred substitute for
    article prose.  They are listed here rather than used as a generic script
    scrape because their schemas are outlet-specific.
    """
    if outlet == "ntv":
        # n-tv's rolling "Der Tag" stores each prose unit in this widget field.
        found = re.findall(r'"paragraph"\s*:\s*\{\s*"value"\s*:\s*"((?:\\.|[^"\\])*)"', source)
        out = []
        for value in found:
            try: text = clean(json.loads('"' + value + '"'))
            except ValueError: continue
            if len(text.split()) >= 3 and text not in out: out.append(text)
        return out
    if outlet == "zdfheute":
        # ZDF's React flight payload encodes paragraph children as JSON strings.
        out = []
        for value in re.findall(r'\\"p\\"[^\n]{0,900}?\\"children\\":\\"((?:\\\\.|[^"\\])*)\\"', source):
            try: text = clean(json.loads('"' + value.replace('\\\\"', '\\\"') + '"'))
            except ValueError: continue
            if len(text.split()) >= 3 and text not in out: out.append(text)
        return out
    if outlet == "abc":
        # ABC embeds the AP/ABC body in a JSON page-state object.
        anchor = '"Body","props":{"body":'
        start = source.find(anchor)
        if start >= 0:
            start = source.find("[", start + len(anchor))
            try: body, _ = json.JSONDecoder().raw_decode(source[start:])
            except (ValueError, TypeError): body = []
            out = []
            def walk(value):
                if isinstance(value, dict):
                    if value.get("type") == "p":
                        text = []
                        def content(v):
                            if isinstance(v, str): text.append(v)
                            elif isinstance(v, list):
                                for x in v: content(x)
                            elif isinstance(v, dict): content(v.get("content", []))
                        content(value.get("content", []))
                        value_text = clean(" ".join(text))
                        if len(value_text.split()) >= 3: out.append(value_text)
                    for child in value.values(): walk(child)
                elif isinstance(value, list):
                    for child in value: walk(child)
            walk(body)
            return out
    return []


def provider_for(outlet, url, source, body, yahoo_providers):
    """Wire or content provider, only where the page or the audit's page-derived table states it."""
    if outlet == "yahoo":
        # The audit's providers table was built from each Yahoo page; there is no guessing from the text.
        return yahoo_providers.get(url, "")
    ends = body[:800] + " " + body[-600:]
    if outlet == "abc":
        if "/wireStory/" in url or re.search(r"\(AP\)|Associated Press|\bAP\b", ends):
            return "AP"
        return ""
    if outlet == "welt" and "newsticker/dpa_nt/" in url: return "dpa"
    for p in ("dpa", "Reuters", "Associated Press", "AFP"):
        if re.search(r"(?:\(|von|by|copyright)\s*" + re.escape(p) + r"\b", body[:800], re.I):
            return {"Associated Press": "AP"}.get(p, p)
    return ""


def language(body, country):
    # Assigned from the dominant script, then from ordinary function words (no model).
    text = body.lower()
    arabic = len(re.findall(r"[\u0600-\u06ff]", text)); hebrew = len(re.findall(r"[\u0590-\u05ff]", text))
    latin = len(re.findall(r"[a-zäöüß]", text))
    if arabic > latin and arabic >= hebrew: return "ar"
    if hebrew > latin: return "he"
    if country == "germany": return "de" if any(w in f" {text} " for w in (" der ", " die ", " und ", " ist ")) else ""
    return "en" if any(w in f" {text} " for w in (" the ", " and ", " with ", " that ")) else ""


def doc_type(outlet, url, fields, source=""):
    if outlet == "welt" and "newsticker/dpa_nt/" in url: return "wire_feed"
    if outlet == "rtl" and "/HBBTV/Teletext/" in url: return "teletext"
    if "radio.foxnews.com" in (url or "") or re.search(r"/podcasts?/", url or "", re.I):
        return "podcast_page"
    if re.search(r"/videos?/|/mediathek/|/watch/", url or "", re.I) or (outlet == "cnn" and "/videos" in (url or "")):
        return "video_page"
    if outlet == "cnn" and "5 things" in fields["title"].lower(): return "newsletter"
    ty = " ".join(str(i.get("@type", "")) for i in fields["items"]).lower()
    if "videoobject" in ty or (outlet == "fox" and 'og:type" content="video"' in source[:8000]):
        return "video_page"
    if "liveblogposting" in ty: return "liveblog"
    return "article"


def access_closed(source, title):
    if re.search(r'"isAccessibleForFree"\s*:\s*"?false', source[:200000], re.I):
        return True
    if re.search(r"\(S\+\)|WELTplus|BILDplus", title or ""):
        return True
    if "Sie können den Artikel leider nicht mehr aufrufen" in source:
        return True
    return False


# Whole paragraphs that are a newsletter, app or podcast promo. Dropped as a block, not edited mid-sentence.
BOILER_SUBSTR = {
    "cnn": ["5 things pm is produced", "welcome to 5 things", "one-stop shop for the latest headlines",
            "to get up to speed and on with your day", "sign up for cnn", "if your day doesn't start until",
            "sign up here for the", "a version of this story appears in cnn's"],
    "cbs": ["click here to browse full transcripts"],
    "nyt": ["sign up here to get this newsletter", "sign up for the on politics newsletter", "play: today's spelling bee",
            "play the spelling bee", "for more audio journalism and storytelling, download", "and follow the new york times on instagram",
            "reach whet and the team at briefing@nytimes.com", "tune in, and tell us what you think at",
            "do you have questions about the election", "send them to us, and we'll find the answers"],
    "usatoday": ["hit play on the player below", "this transcript was automatically generated",
                 "there may be some differences between the audio and the text", "sign up for the email here",
                 "sign up for the daily briefing email", "thank you for supporting our journalism",
                 "unable to view our graphics"],
    "fox": ["click here to get the fox news app", "fox news antisemitism exposed", "fox news' antisemitism exposed"],
    "zdfheute": ["zdfheute-whatsapp-channel", "zur anmeldung"],
    "spiegel": ["in der aktuellen podcastfolge", "diesen podcast können sie"],
    "tonline": ["lesen sie auch:", "tagesanbruch – der newsletter", "kostenlos abonnieren"],
    "welt": ["hier können sie die aktuelle folge", "abonnieren sie den podcast", "mehr podcasts von welt",
             "folgen sie glasauge", "\u201edas bringt der tag\u201c – jeden morgen", "jeden samstag blickt welt-chefkorrespondent"],
    "tagesschau": ["whatsapp-channel"],
    "yahoo": ["key takeaways", "powered by yahoo scout", "try the telegraph free", "broaden your horizons with award-winning",
              "all rights reserved. this material may not be published", "for the latest news, weather, sports, and streaming video, head to",
              "for the latest news, follow us on facebook", "create an account at cnn.com",
              "this story originally appeared in los angeles times", "sign up for essential california",
              "this article was originally published on nbcnews.com", "this article was originally published on msnbc.com",
              "read the original article", "read more at the daily beast", "stay informed and gain unlimited access to the daily beast",
              "get the daily beast's biggest scoops", "sign up for from the politics desk", "sign up to the selection newsletter",
              "this article is republished from the conversation", "the dispatch is a new digital media company",
              "download the free boston 25", "follow boston 25 news on facebook", "watch boston 25 news now",
              "more top stories from around the world", "more on israel:", "original article source:",
              "originally appeared on abcnews.go.com", "this article originally appeared on usa today",
              "this article originally appeared on detroit free press", "©2024 bloomberg"],
}


# Paragraphs that are only a label for a link box that follows (the box itself is not prose).
BOILER_EXACT = {"welt": {"lesen sie auch"},
                "yahoo": {"best of rolling stone", "best of deadline", "most read from bloomberg businessweek"}}


# Section labels and photo credits that sit as paragraphs among the prose.
BOILER_RE = {"yahoo": re.compile(
    r"^(?:more from|best of|most read from)\b.{0,40}$|\bcredit\s*[-\u2013]\s*\S.{0,80}$|"
    r"^read more\b[:\s]|^related:|^go deeper:|^more from the fact-check team|"
    r"\bsign up (?:now|here|for|to)\b.{0,80}\b(?:newsletter|inbox|alerts)\b|\bsubscribe to (?:our|more|the)\b.{0,60}\bnewsletter|"
    r"\bdownload (?:the|our)\b.{0,40}\bapps?\b|\bclick here to (?:download|sponsor)\b|\bin your inbox\b|^sign up now\.?$|"
    r"^(?:about the yodel|if you start your day with the yodel|editor's note: cnn's 5 things)|"
    r"^listen to the bloomberg daybreak|^watch episodes of the daily t|^never miss a story|^for more people news|"
    r"^opinion alerts:|^you can read diverse opinions|^want a daily wrap-up|^looking for more on michigan's elections|"
    r"^contact clara hendrickson|^if it's in the news right now, the l\.a\. times' opinion|"
    r"^north america correspondent anthony zurcher|^here's what else is happening today\. and remember", re.I)}


def drop_boiler(texts, outlet):
    kept = []
    for text in texts:
        low = text.lower().replace("\u2019", "'")
        if outlet in BOILER_RE and len(text.split()) <= 70 and BOILER_RE[outlet].search(text.strip()):
            continue
        if low.strip(" :") in BOILER_EXACT.get(outlet, ()):
            continue
        if any(s in low and (len(text.split()) <= 45 or low.find(s) < 40) for s in BOILER_SUBSTR.get(outlet, [])):
            continue
        kept.append(text)
    return kept


def ld_is_dirty(ld, outlet):
    """JSON-LD articleBody is not the article when it is a lead or it inlines page chrome."""
    if len((ld or "").split()) < 35:
        return True
    low = ld.lower()
    if "verlinkt auf http" in low:
        return True
    return any(s.lower() in low for s in CHROME.get(outlet, []))


def extract(source, country, outlet, url, yahoo_providers):
    rule = RULES[country][outlet]
    fields = page_fields(source)
    tree = Tree(); tree.feed(source)
    node = choose_node(tree, rule)
    structured = drop_boiler(trim_chrome(structured_body(source, outlet), rule["cut"]), outlet)
    raw_specific = article_paragraphs(tree, outlet, url, fields)
    if raw_specific is None:
        raw_specific = paragraphs(node, skip=PARA_SKIP.get(outlet, ())) if node else []
    specific = drop_boiler(trim_chrome(raw_specific, rule["cut"]), outlet)
    cont = specific
    if outlet == "tagesschau":
        # "Stand:" is the updated-at line. A trailing "mehr" is the expander control.
        cont = [re.sub(r"(?<=[.!?]) mehr$", "", t) for t in cont]
        cont = [t for t in cont if t and not re.match(r"Stand:\s+\d{2}\.\d{2}\.\d{4}", t)]
    ld_body = fields["ld_body"]
    cont_body = "\n".join(cont)
    dirty = ld_is_dirty(ld_body, outlet)
    # Prefer the rendered article. JSON-LD wins only when it is clean and the container missed most of it.
    if cont_body and (dirty or len(cont_body) >= 0.9 * max(len(ld_body), 1)):
        body, method = cont_body, "container:" + outlet
    elif not dirty:
        body, method = ld_body, "ld-json"
    elif structured:
        body, method = "\n".join(structured), "page-state:" + outlet
    else:
        body, method = "", ""
    closed = access_closed(source, fields["title"])
    paywall = False
    if body and "Sie können den Artikel leider nicht mehr aufrufen" in body:
        body, method, paywall = "", "", True
    if not body and fields["description"] and (closed or re.search(r"WELTplus|BILDplus|SPIEGEL\+", (fields["title"] or "") + source[:8000])):
        body, method, paywall = fields["description"], "meta-description-paywall", True
    dtype = doc_type(outlet, url, fields, source)
    # An article that embeds a video also carries a VideoObject. With a full article body it is an article.
    if dtype == "video_page" and not re.search(r"/videos?/|/mediathek/|/watch", url or "", re.I) and len(body.split()) >= 150:
        dtype = "article"
    desc = fields["description"]
    if (dtype in ("video_page", "podcast_page") and not body and len(desc.split()) >= 4
            and desc.lower().strip() not in {"fox news", "cnn", "reuters"}):
        body, method = desc, "meta-description-" + dtype.split("_")[0]
    if method == "meta-description-paywall" or (closed and 0 < len(body.split()) < 80):
        paywall = True
    warnings = []
    if outlet == "nyt" and body and "optimistic-truncator-message" in source and "Want all of The Times" in source:
        # The capture shows the access wall: what follows the visible paragraphs is not on the page.
        paywall = True
        warnings.append("page_truncated_by_access_wall")
    if method == "meta-description-paywall":
        warnings.append("paywalled_lead_only")
    title = title_clean(fields["title"], rule["suffix"])
    provider = provider_for(outlet, url, source, body, yahoo_providers)
    when = fields["when"]
    date = re.search(r"\d{4}-\d{2}-\d{2}", when)
    return {"title": title, "canonical_url": fields["canonical"], "published_at": date.group(0) if date else "",
            "published_time": when, "date_source": fields["date_source"], "body_text": body,
            "extract_method": method, "document_type_hint": dtype, "paywall": paywall,
            "provider": provider, "language": language(body, country), "warnings": warnings}


def key_func(url):
    # Keep cache matching identical to recall_audit_common.key without importing a mutable pipeline module.
    u = html.unescape(url or "").strip().replace("%23", "#")
    u = re.sub(r"^https?://web\.archive\.org/web/\d+(?:id_)?/", "", u)
    u = re.sub(r"^https?://", "", u, flags=re.I).split("#")[0].split("?")[0].lower()
    host, _, path = u.partition("/")
    host = re.sub(r"^(www\d?|m|amp|mobile|edition|news|us)\.", "", host)
    path = re.sub(r"(/amp)?/?$", "", path); path = re.sub(r"\.amp(\.html)?$", r"\1", path); path = re.sub(r"/index\.html$", "", path)
    if host == "zdfheute.de": host, path = "zdf.de", "nachrichten/" + path
    if host == "abcnews.com": host = "abcnews.go.com"
    n = host + "/" + path
    tests = [("rtl.de", r"-id(\d{6,})"), ("n-tv.de", r"article(\d{6,})"), ("bild.de", r"-([0-9a-f]{24})(?:$|\.)"),
             ("bild.de", r"-(\d{6,9})\.bild"), ("spiegel.de", r"-a-([0-9a-f-]{20,})"),
             ("welt.de", r"/(?:article|plus|video|liveticker)(\d{6,})"), ("t-online.de", r"id_(\d{6,})"),
             ("rnd.de", r"-([a-z0-9]{26})\.html"), ("abcnews.go.com", r"-(\d{6,10})$"),
             ("nbcnews.com", r"(rcna\d+|ncna\d+)"), ("yahoo.com", r"-(\d{9})\.html"),
             ("usatoday.com", r"/(\d{10,12})$"), ("apnews.com", r"([0-9a-f]{32})")]
    if (not re.search(r"liveblog|live-blog|newsticker|liveticker|live-ticker|/live/|/live-news/|live-updates|/live-story|newsblog|nahost-news|-news-ticker", url, re.I)
            or "t-online.de" in n or (host == "welt.de" and "/newsticker/dpa_nt/" in n)):
        for h, pat in tests:
            if host == h:
                m = re.search(pat, n)
                if m: return h + "#" + m.group(1)
    return n


def cache_source(cache_row):
    fetch = cache_row.get("fetch", "")
    if fetch.startswith("our-raw:"): return fetch.split(":", 1)[1], "our-raw"
    raw = cache_row.get("raw_file", "")
    if raw: return raw, ("wayback:" + cache_row["capture_ts"] if fetch == "wayback" and cache_row.get("capture_ts") else fetch)
    return "", fetch


CHROME = {
    "spiegel": ["Artikel anhören", "Link kopieren", "X.com Facebook E-Mail", "Bild vergrößern", "Dieser Ausdruck wurde"],
    "bild": ["BILD LIVE", "Mehr aus BILD", "Mehr zum Video anzeigen"],
    "ntv": ["ntv bei Google bevorzugen"],
    "rnd": ["Das tägliche Kreuzworträtsel", "Mit meiner Anmeldung zum Newsletter", "Abonnieren Sie auch"],
    "rtl": ["Mehr zum Thema"],
    "tagesschau": ["Mehr zum Thema", "WhatsApp-Channel", "Dieses Thema im Programm"],
    "tonline": ["Auch interessant", "Lesen Sie auch:", "Tagesanbruch – Der Newsletter", "Einwilligung, um den von unserer Redaktion"],
    "welt": ["Alle Inhalte", "Mehr Podcasts von WELT", "Abonnieren Sie den Podcast"],
    "zdfheute": ["Weitere Nachrichten", "ZDFheute-WhatsApp-Channel", "speichern wir Ihre Zustimmung", "Erst wenn Sie hier klicken"],
    "fox": ["CLICK HERE TO GET", "Click here to get the Fox News app", "Fox News Antisemitism Exposed", "Warning, graphic video"],
    "yahoo": ["Return to Homepage", "Recommended Stories", "Why you can trust us", "Key takeaways", "Powered by Yahoo Scout"],
    "wapo": ["History: The roots of the Israeli-Palestinian conflict"],
    "usatoday": ["Facebook Twitter Email", "Hit play on the player below", "Thank you for supporting our journalism"],
    "cbs": ["More from CBS News", "Click here to browse full transcripts"],
    "cnn": ["one-stop shop for the latest headlines", "Welcome to 5 Things"],
    "nbc": ["More from NBC News"],
    "reuters": ["Read Next", "Suggested Topics", "Our Standards: The Thomson Reuters Trust Principles"],
    "abc": ["Trending Reader Picks"],
    "ap": ["Follow AP's live updates", "Follow AP’s live updates"],
    "nyt": ["Continue reading the main story", "Share full article", "Thank you for your patience while we verify access", "Want all of The Times"],
}
# Phrases that mark a stored corpus body as chrome even when the new body is clean.
STORED_MARKERS = [
    "artikel anhören", "link kopieren", "x.com facebook", "key takeaways", "powered by yahoo",
    "click here to get", "antisemitism exposed", "warning, graphic video", "kreuzworträtsel",
    "our standards:", "dieser ausdruck wurde", "share full article", "history: the roots",
    "mehr zum video anzeigen", "bild live", "opens new tab", "follow ap's live updates",
    "follow ap’s live updates", "trending reader picks",
    "weiterlesen nach der anzeige", "anzeige spiele", "speichern wir ihre zustimmung",
    "erst wenn sie hier klicken", "artikel teilen",
]
CHECK_NAMES = ("no_chrome", "lead_present", "not_truncated", "no_duplication", "order")
PROMO_SENTENCE = re.compile(
    r"artikel anhören|link kopieren|click here to get|return to homepage|recommended stories|"
    r"key takeaways|powered by yahoo|whatsapp-channel|antisemitism exposed|kreuzworträtsel|"
    r"one-stop shop for the latest|welcome to 5 things|5 things pm is produced|"
    r"our standards: the thomson|bild vergrößern|follow ap.s live updates",
    re.I)


def raw_text(path):
    if path.suffix == ".gz":
        with gzip.open(path, "rt", encoding="utf-8", errors="replace") as f: return f.read()
    return path.read_text(encoding="utf-8", errors="replace")


def sentences(body, n=8):
    return [clean(s) for s in re.split(r"(?<=[.!?])\s+", clean(body)) if len(clean(s).split()) >= n]


def lead_words(text):
    return re.findall(r"[\wÀ-ÖØ-öø-ÿ]+", (text or "").lower())


def word_at(needle, hay, max_gap):
    """Return the hay index where needle begins, allowing up to max_gap extra words between items."""
    if not needle:
        return None
    for start, word in enumerate(hay):
        if word != needle[0]:
            continue
        pos, ok = start + 1, True
        for item in needle[1:]:
            found = None
            for j in range(pos, min(len(hay), pos + max_gap + 1)):
                if hay[j] == item:
                    found = j
                    break
            if found is None:
                ok = False
                break
            pos = found + 1
        if ok:
            return start
    return None


def loose_find(needle, hay, max_gap=4):
    if word_at(needle, hay, max_gap) is not None:
        return "exact"
    if len(needle) >= 6:
        for i in range(len(needle)):
            trial = needle[:i] + needle[i + 1:]
            if word_at(trial, hay, max_gap) is not None:
                return "near"
    return None


def visible_words(source):
    plain = re.sub(r"<script\b[^>]*>.*?</script\s*>|<style\b[^>]*>.*?</style\s*>", " ", source, flags=re.I | re.S)
    plain = re.sub(r"<[^>]+>", " ", plain)
    return lead_words(html.unescape(plain))


def lead_spans(text):
    return [(m.group(0).lower(), m.start()) for m in re.finditer(r"[\wÀ-ÖØ-öø-ÿ]+", text or "")]


def find_lead(needle, spans):
    """Character offset in the body where the needle words begin (exact, or with one word dropped), else None."""
    hay = [w for w, _ in spans]
    at = word_at(needle, hay, 4)
    if at is not None:
        return spans[at][1], "exact"
    if len(needle) >= 6:
        for i in range(len(needle)):
            at = word_at(needle[:i] + needle[i + 1:], hay, 4)
            if at is not None:
                return spans[at][1], "near"
    return None, None


def lead_status(desc, body, source):
    """Calibrated lead check (same as Israel/Lebanon).

    Opening words of the description in the first 400 characters: pass. Not in the body at all: the
    description is a rewritten teaser, pass (description_is_rewrite). In the body but after the first
    400 characters: fail, for the caller to look at what precedes it.
    """
    words = lead_words(desc)
    if len(words) < 4:
        return True, "no_description" if not words else "description_under_4_words", None
    first = lead_words(re.split(r"[.!?]", desc, maxsplit=1)[0])
    target = first[:8] if len(first) >= 8 else (first if len(first) >= 4 else words[:8])
    where, kind = find_lead(target, lead_spans(body))
    if where is not None and where < 400:
        return True, "" if kind == "exact" else "description_paraphrase_in_lead", where
    if where is not None:
        return False, "description_after_400_chars", where
    # A rewrite. Note when the page shows the exact words in a prose paragraph the body lacks (reviewed by hand).
    if prose_has_exact_lead(source, target):
        return True, "description_is_rewrite:on_page_not_in_body", None
    return True, "description_is_rewrite", None


def prose_has_exact_lead(source, target):
    tree = Tree()
    tree.feed(source)
    for n in descendants(tree.root):
        if n.tag not in {"p", "h2", "li"} or is_caption(n):
            continue
        if has_ancestor(n, lambda p: p.tag in {"nav", "footer", "aside"}):
            continue
        if loose_find(target, lead_words(node_text(n))) == "exact":
            return True
    return False


# Closing lines a publisher puts after the last sentence: credits, bios, sign-offs, source lines.
TRAILER = re.compile(
    r"\[[A-Z][^\]]{1,40}\]$|"
    r"^(?:Updated|Last updated|Published)\b.{0,40}\b(?:EDT|EST|PDT|PST|ET|GMT|UTC)\b|"
    r"^(?:By|Von)\s+\S|^Ihr(?:e)?\s+\S|^Mit .{3,80} sprach .{3,60}$|"
    r"https?://\S+$|\bMore about [A-Z]|"
    r"this article (?:was originally published|originally appeared) on\b|\boriginally appeared on\b|"
    r"\badditional reporting by\b|^Original article source:|^Read the original article on\b|"
    r"create an account at CNN\.com|"
    r"(?:mit informationen von|mit material von|das gespräch führte|contributed to this report|"
    r"contributed reporting|reported from|contributed)\b", re.I)


def ends_ok(body):
    last = body.strip().split("\n")[-1].strip()
    if sentence_ended(last):
        return True
    if re.fullmatch(r"\([^)]{2,500}\)", last) or re.search(r"\([^)]{2,80}\)$", last):
        return True
    if re.search(r"\b[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}\b", last):
        return True
    return bool(TRAILER.search(last))


def last_para_in_list(source, last):
    """True when `last` is the text of a paragraph or item that sits inside a <li> on the page."""
    tree = Tree()
    tree.feed(source)
    for n in descendants(tree.root):
        if n.tag in {"p", "li"} and node_text(n) == last and (n.tag == "li" or has_ancestor(n, lambda p: p.tag == "li")):
            return True
    return False


def page_quote_exact(source, text):
    """A <=150-character quote of `text` that really is in the page (visible text, or the page's own JSON), else ''."""
    q = clean(text)[:150].rstrip()
    if not q:
        return ""
    squeeze = lambda t: re.sub(r"\s+", "", t)
    key = squeeze(q.lower())
    if key in squeeze(plain_page(source).lower()):
        return q
    # Some outlets ship the article only as JSON page state; compare with the JSON-escaped form of the quote.
    raw = squeeze(source.lower())
    for escaped in (json.dumps(q, ensure_ascii=False)[1:-1], json.dumps(q, ensure_ascii=True)[1:-1]):
        if squeeze(escaped.lower()) in raw:
            return q
    return ""


CAPTIONISH = re.compile(r"\bcredit\b\s*[-–:]|\bgetty\b|\bphoto\b|\bimage\b|\bpictured\b|listen to this|"
                        r"\bshare\b|\bsubscribe\b|\badvertisement\b|\bread more\b|\bfollow\b|\bsign up\b", re.I)


def initial_checks(source, extraction, outlet):
    body = extraction["body_text"]
    fields = page_fields(source)
    # A body that is the page's own description is the publisher's metadata text, not a scraped region.
    hits = [] if extraction.get("extract_method", "").startswith("meta-description") else [
        s for s in CHROME.get(outlet, []) if s.lower() in body.lower()]
    checks = {"no_chrome": {"ok": bool(body) and not hits, "found": hits}}
    lead_ok, lead_reason, where = lead_status(fields["description"], body, source)
    checks["lead_present"] = {"ok": bool(body) and lead_ok, "reason": lead_reason}
    if body and not lead_ok and where is not None:
        before = body[:where].strip()
        # Everything up to the paragraph that holds the description's words.
        upto = body.find("\n", where)
        head = (body[:upto] if upto >= 0 else body).strip()
        paras = [x for x in head.split("\n") if x.strip()]
        quote = page_quote_exact(source, paras[0]) if paras else ""
        # What precedes the description is a genuine opening when it carries no caption, credit or share
        # text. Reviewed by hand in the report; chrome would be fixed in the extractor.
        if quote and paras and not CAPTIONISH.search(head):
            checks["lead_present"] = {"ok": True, "reason": lead_reason,
                                      "exception": {"type": "description_is_a_later_sentence", "quote": quote}}
    ending = ends_ok(body)
    method = extraction.get("extract_method", "")
    truncated_note = None
    end_exception = None
    if body and not ending and not method.startswith("meta-description"):
        last = body.strip().split("\n")[-1].strip()
        # A bullet the publisher wrote without a full stop, or a dash-led sign-off line, is the page's own ending.
        if re.match(r"^[\u2014\u2013-]\s*\S", last) or last_para_in_list(source, last):
            quote = page_quote_exact(source, last)
            if quote:
                ending = True
                end_exception = {"type": "ends_without_full_stop", "quote": quote[-150:] if len(quote) > 150 else quote}
    if method.startswith("meta-description") and body:
        # The body is the page's description. A caption or teaser needs no full stop; one the publisher
        # cut with an ellipsis is a truncated page text, noted rather than failed.
        if re.search(r"(?:\.\.\.|…)$", body.strip()):
            ending = True
            truncated_note = {"type": "page_truncated", "quote": body.strip()[-150:]}
        else:
            ending = True
    ld = fields["ld_body"]
    dirty = ld_is_dirty(ld, outlet)
    long_enough = dirty or len(body) >= 0.9 * len(ld)
    checks["not_truncated"] = {"ok": bool(body) and ending and long_enough, "ending": ending, "ld_length": long_enough,
                               "reason": "" if long_enough else "shorter_than_json_ld"}
    if end_exception and "exception" not in checks["not_truncated"]:
        checks["not_truncated"]["exception"] = end_exception
    if truncated_note and page_quote_exact(source, truncated_note["quote"]):
        checks["not_truncated"]["exception"] = {"type": truncated_note["type"], "quote": page_quote_exact(source, truncated_note["quote"])}
    orig = {}
    for sent in sentences(body):
        orig.setdefault(sent.lower(), sent)
    ss = [s.lower() for s in sentences(body)]
    repeated = [s for s, c in Counter(ss).items() if c > 1]
    dup = {"ok": bool(body) and not repeated}
    if body and repeated:
        quote = page_quote_exact(source, orig[repeated[0]])
        # The same sentence really sits twice in the page's article text. A body that is mostly copies fails.
        if quote and len(repeated) <= max(3, len(ss) // 10) and len(repeated) * 4 < len(ss):
            dup = {"ok": True, "repeated": repeated[:6], "exception": {"type": "sentence_twice_in_article", "quote": quote}}
        else:
            dup["repeated"] = repeated[:6]
    checks["no_duplication"] = dup
    checks["order"] = {"ok": bool(body), "reason": "pending"}
    return checks


# Hand-reviewed single cases: a page whose last paragraph is a guest list the publisher wrote without a full stop.
MANUAL_EXCEPTIONS = {"r2-4ba1838be9e4053f.html.gz": {"not_truncated": "ends_without_full_stop"}}


def apply_cross_checks(items):
    """Repeated sentences across headlines, and JSON-LD paragraph order."""
    by_outlet = defaultdict(lambda: defaultdict(set))
    for item in items:
        if not item.get("body_text"):
            continue
        for sentence in sentences(item["body_text"], 6):
            by_outlet[item["outlet"]][sentence.lower()].add(item.get("headline") or item["id"])
    repeated = {o: {s for s, heads in found.items() if len(heads) >= 3} for o, found in by_outlet.items()}
    prose = defaultdict(list)
    for item in items:
        checks = item["checks"]
        body = item.get("body_text") or ""
        promo, ordinary = [], []
        for sentence in sentences(body, 6):
            if sentence.lower() in repeated.get(item["outlet"], set()):
                (promo if PROMO_SENTENCE.search(sentence) else ordinary).append(sentence)
        if promo:
            checks["no_chrome"]["ok"] = False
            checks["no_chrome"]["repeated_sentences"] = promo[:3]
        source = item.get("source") or ""
        if ordinary:
            prose[item["outlet"]].extend(ordinary[:2])
            quote = page_quote_exact(source, ordinary[0]) if source else ""
            # A sentence several articles share is the publisher's own text (wire copy, a standing paragraph),
            # not chrome, when it sits in the extracted article text on the page.
            if quote and not checks["no_chrome"].get("exception"):
                checks["no_chrome"]["exception"] = {"type": "sentence_recurs_across_articles", "quote": quote}
                checks["no_chrome"]["recurring"] = ordinary[:3]
            elif not quote:
                checks["no_chrome"]["ok"] = False
                checks["no_chrome"]["repeated_sentences"] = ordinary[:3]
        ld = page_fields(source)["ld_body"] if source else ""
        if not body:
            checks["order"] = {"ok": False, "reason": "empty"}
        elif not ld or len(ld.split()) < 35 or item.get("extract_method") == "ld-json":
            checks["order"] = {"ok": True, "reason": "not_applicable" if not ld or len(ld.split()) < 35 else "ld_json_source"}
        elif ld_is_dirty(ld, item["outlet"]):
            checks["order"] = {"ok": True, "reason": "json_ld_contains_chrome"}
        else:
            pos, ordered, compared = -1, True, 0
            compact_ld = clean(ld).lower()
            paras = [p for p in body.split("\n") if p.strip()]
            for paragraph in paras:
                probe = clean(paragraph).lower()[:160]
                # A paragraph that occurs several times in the JSON-LD (a repeated line in a transcript) is
                # matched at its first occurrence after the previous match. Only a paragraph that occurs
                # solely before the previous match is out of order.
                where = compact_ld.find(probe, max(pos, 0))
                if where < 0:
                    where = compact_ld.find(probe)
                    if where >= 0:
                        compared += 1
                        ordered = False
                    continue
                compared += 1
                pos = where
            if compared == 0:
                checks["order"] = {"ok": True, "reason": "json_ld_differs"}
            elif compared < len(paras) and not ordered:
                checks["order"] = {"ok": False, "reason": "matched_paragraphs=" + str(compared)}
            else:
                checks["order"] = {"ok": ordered, "reason": "matched_paragraphs=" + str(compared)}
        # Cases reviewed by hand where the page's own text trips a check no rule describes (documented in the report).
        for name, kind in MANUAL_EXCEPTIONS.get(os.path.basename(item.get("raw_path", "")), {}).items():
            if not checks[name]["ok"] and body and source:
                last = body.strip().split("\n")[-1].strip()
                quote = page_quote_exact(source, last[-150:])
                if quote:
                    checks[name] = {**checks[name], "ok": True, "exception": {"type": kind, "quote": quote}}
        item["ok_checks"] = all(v.get("ok", False) for v in checks.values())
    return {o: list(dict.fromkeys(v))[:8] for o, v in prose.items()}


def validation_summary(items, country):
    out = {}
    for outlet in RULES[country]:
        rows = [i for i in items if i["outlet"] == outlet and i.get("body_text") and i.get("checks")]
        checks = {}
        for name in CHECK_NAMES:
            failed = [i["raw_path"] for i in rows if not i["checks"][name]["ok"]]
            checks[name] = {"n": len(rows), "pass": len(rows) - len(failed),
                            "rate": (len(rows) - len(failed)) / len(rows) if rows else 0.0,
                            "failed": failed}
        failed_any = [i["raw_path"] for i in rows if not all(i["checks"][n]["ok"] for n in CHECK_NAMES)]
        all_pass = {"n": len(rows), "pass": len(rows) - len(failed_any),
                    "rate": (len(rows) - len(failed_any)) / len(rows) if rows else 0.0, "failed": failed_any}
        exceptions = Counter(i["checks"][n]["exception"]["type"] for i in rows for n in CHECK_NAMES
                             if i["checks"][n].get("exception"))
        usable = bool(rows) and all_pass["rate"] >= .95
        out[outlet] = {"checks": checks, "usable": usable, "all_pass": all_pass, "exceptions": exceptions}
    return out


INLINE = r"a|b|i|u|em|strong|span|small|sup|sub|mark|abbr|cite|time|font|bdi"


def plain_page(source):
    """Visible text of the page. Inline tags join text, other tags separate it."""
    plain = re.sub(r"<script\b[^>]*>.*?</script\s*>|<style\b[^>]*>.*?</style\s*>", " ", source, flags=re.I | re.S)
    plain = re.sub(r"</?(?:" + INLINE + r")\b[^>]*>", "", plain, flags=re.I)
    return clean(re.sub(r"<[^>]+>", " ", html.unescape(plain)))


def page_quote(plain, needle):
    probe = clean(needle)[:60]
    at = plain.lower().find(probe.lower()[:40]) if probe else -1
    if at < 0:
        return plain[:150]
    return plain[max(0, at - 20):at + 130][:150]


def sentence_fraction(part, whole):
    found = sentences(part)
    if not found:
        return 0.0
    blob = clean(whole).lower()
    return sum(s.lower() in blob for s in found) / len(found)


def opening_in_caption(source, stored):
    """True when the stored body's opening is a caption or credit on the page."""
    probe = clean(stored)[:70].lower()
    if len(probe) < 25 or not source:
        return False
    tree = Tree()
    tree.feed(source)
    for n in descendants(tree.root):
        if not is_caption(n):
            continue
        if probe[:40] in node_text(n).lower():
            return True
    return False


def classify_gap(stored, new, plain, ok_checks, outlet, source=""):
    stored_l = clean(stored).lower()
    stored_chrome = any(m in stored_l for m in STORED_MARKERS) or any(
        s.lower() in stored_l for s in CHROME.get(outlet, []))
    if "+++" in stored:
        stored_chrome = True
    if source and opening_in_caption(source, stored):
        stored_chrome = True
    if not new:
        on_page = bool(stored) and clean(stored)[:80].lower() in plain.lower()
        return "new_wrong" if on_page else "stored_wrong"
    if len(stored.split()) < 15 and len(new.split()) > len(stored.split()):
        return "stored_wrong"
    new_open, stored_open = clean(new)[:50].lower(), clean(stored)[:50].lower()
    if stored_open and stored_open not in plain.lower() and new_open and new_open in plain.lower():
        return "stored_wrong"
    new_in_stored = sentence_fraction(new, stored)
    stored_in_new = sentence_fraction(stored, new)
    if stored_chrome and new_in_stored >= 0.5:
        return "stored_wrong"
    if stored_in_new >= 0.85:
        return "stored_wrong"
    if new_in_stored >= 0.85 and len(new) >= 0.85 * max(len(stored), 1):
        return "stored_wrong"
    if new_in_stored >= 0.85:
        # The extracted sentences are in the stored body. A shorter extract that still
        # passes the truncation checks has dropped stored chrome, not the article.
        return "stored_wrong" if ok_checks else "new_wrong"
    if stored_chrome and not ok_checks:
        return "both"
    if not ok_checks:
        return "new_wrong"
    if stored_chrome or (ok_checks and max(new_in_stored, stored_in_new) >= 0.6):
        return "stored_wrong"
    return "both"


def regression(country, reextract):
    by_outlet = defaultdict(list)
    adjudications = []
    for row in reextract:
        if not row["stored_body"] or not row["source"] or row["outlet"] not in RULES[country]:
            continue
        ratio = difflib.SequenceMatcher(None, clean(row["stored_body"])[:3000], clean(row["body_text"])[:3000]).ratio()
        by_outlet[row["outlet"]].append(ratio)
        if ratio < .90:
            plain = plain_page(row["source"])
            kind = classify_gap(row["stored_body"], row["body_text"], plain, row["ok_checks"], row["outlet"], row["source"])
            if kind == "new_wrong":
                needle = row["stored_body"]
            elif kind == "stored_wrong":
                needle = next((m for m in STORED_MARKERS if m in clean(row["stored_body"]).lower()), row["body_text"] or row["stored_body"])
            else:
                needle = row["body_text"] or row["stored_body"]
            adjudications.append({"document_id": row["document_id"], "outlet": row["outlet"], "raw_path": row["raw_path"],
                                  "ratio": f"{ratio:.3f}", "classification": kind, "evidence": page_quote(plain, needle)})
    summary = {}
    for outlet in RULES[country]:
        vals = by_outlet[outlet]
        summary[outlet] = {"n": len(vals), "median": statistics.median(vals) if vals else 0.0,
                           "share": sum(v >= .90 for v in vals) / len(vals) if vals else 0.0}
    return summary, adjudications


def check_warnings(checks):
    """Warning strings for a record: every publisher exception with its quote, and a rewritten-teaser lead."""
    out = []
    for name in CHECK_NAMES:
        c = checks.get(name, {})
        if c.get("exception"):
            out.append(f"publisher_exception:{name}:{c['exception']['type']}:{c['exception']['quote']}")
        if name == "lead_present" and str(c.get("reason", "")).startswith("description_is_rewrite"):
            out.append(c["reason"].replace(":", ":"))
    return out


COMMON_CHANGES = [
    "The gate is the five body checks, pass rate counted over all five together (exceptions count as passes). A low ratio against a stored v1 body is a diagnostic and is classified in `regression-adjudication.csv`.",
    "Lead check recalibrated as for Israel/Lebanon: a description whose opening words occur nowhere in the body is a rewritten teaser (pass, `description_is_rewrite`). It fails only when the words occur after the first 400 characters, and then a `publisher_exception` is recorded only if the text before them is genuine article text.",
    "Truncation check: closing lines a publisher puts after the last sentence (contributor credits, wire source lines, URL lines, bylines, interview credits, `[Source]` tags, update stamps) are accepted; a bulleted last item without full stop is an exception with a quote; a body that is the page description is accepted unless the publisher cut it with an ellipsis (`page_truncated`).",
    "Order check: a paragraph that occurs several times in the JSON-LD `articleBody` is matched at its first occurrence after the previous match.",
    "Exceptions are verified in code: the quote must occur in the page's visible text or its JSON page state. Cross-page repeated sentences (6+ words, 3+ bodies, different headlines) are chrome when they match a promo pattern, otherwise `sentence_recurs_across_articles`.",
    "Video pages are recognised by URL (`/video/`, `/videos/`, `/mediathek/`) or by a VideoObject without a full article body; their body is the page description. Podcast pages (`radio.foxnews.com`, `/podcast`) likewise.",
    "Titles lose section or type labels the page appends (Bild `| Politik`, Welt `- Video`).",
]
CHANGES = {
    "germany": COMMON_CHANGES + [
        "ntv (was unusable, lead_present 28/59): the page-state paragraph widget omits the bold lead text (`storyline_lead_text_leadtext`), which is the page description. The extractor now reads the rendered storyline (lead text, paragraphs, subheads) in document order; the page-state reader stays as fallback.",
        "Spiegel (was unusable, not_truncated 59/66): the seven failures were newsletter sign-offs (\"Ich wünsche Ihnen ...\", \"Ihr Martin Knobbe, Leiter ...\") without a full stop. The extractor was right; the check now accepts sign-offs. Spiegel reads `data-area=text`/`multibox` paragraphs plus the RichText lead; paywalled SPIEGEL+ pages give the lead with `paywall: true`.",
        "RND: newsletter call-to-action widgets (`CallToAction`, `NewsletterWidget`), \"Mehr zum Thema\" teaser blocks and the \"Abonnieren Sie auch\" footer are left out.",
        "tagesschau: embedded teaser boxes (`teaser-absatz`, role complementary), programme info (`sendungsbezug`), image info (`absatzbild`) and the WhatsApp-channel line are left out. The teaser boxes had been the recurring sentences.",
        "t-online: the X-embed consent layer, \"Lesen Sie auch:\" link lines and Tagesanbruch newsletter blurbs are left out.",
        "WELT: \"Lesen Sie auch\" link labels, podcast show boilerplate and a satire footer are left out.",
        "ZDFheute: quote cards (a `<blockquote>` inside a `<figure>`) are kept, the speaker `<figcaption>` is not.",
    ],
    "us": COMMON_CHANGES + [
        "ABC (was unusable, lead_present 37/52, no_duplication 46/52): the old lead rule was stricter than the calibration and the duplicated sentences are real repeats between datelines of AP rolling stories. `provider: AP` only when the URL is `/wireStory/` or the page credits AP.",
        "AP (was unusable, not_truncated 31/34): the failures ended on \"Follow AP's war coverage at <URL>\" or a contributor credit. The two AP video pages are now video pages with the description as body.",
        "CNN: the 3 `new_wrong` and the blocked status came from video pages whose only text is a one-line slate (\"X joins The Lead\"). The description is now the body of video pages. The 5 Things promo lines and the newsletter editor's note are cut.",
        "NYT: the access-wall `<noscript>` text, the \"Our coverage\" link guide (`#styln-guide`), the author-bio block (`bottom-of-article`) and newsletter call-to-action lines are left out. Captures that show the access wall get `paywall: true` and the warning `page_truncated_by_access_wall`.",
        "WaPo: every `font-copy` paragraph plus the deck; the photo caption, byline block and the \"History\" promo are not taken. Paywalled captures give the description with `paywall: true`.",
        "Yahoo: the provider comes from `data/us/08-recall-audit/raw/yahoo-providers.csv` (column `provider_name`; round 1 read a column that does not exist, so no provider was ever set). Syndication footers (Telegraph offers, \"Read the original article ...\", newsletter and app prompts, Nexstar copyright line), section labels (\"Best of Rolling Stone\") and photo credits are dropped as whole paragraphs. Key-takeaway boxes and the \"Return to Homepage\" ticker stay out.",
        "Fox: author-bio blocks are left out; `radio.foxnews.com` podcast pages give the description. NBC: the byline bio block is left out. USA Today: podcast-player boilerplate, newsletter and subscription prompts are left out. CBS: the transcript promo line is left out.",
        "Language is assigned from the dominant script (Hebrew or Arabic tweet text inside an English body no longer makes it `he`/`ar`).",
    ],
}
JUDGMENTS = {
    "germany": [
        "Sub-headings are not part of the body, except for ntv (and Fox in the US). Image captions, bylines and teasers are not body.",
        "Spiegel newsletter pages keep their sign-off (\"Ihr Martin Knobbe, ...\"); the line recurs across newsletter issues and is listed as `sentence_recurs_across_articles`.",
        "t-online keeps its closing note on machine-assisted text (single occurrences).",
        "Stored v1 bodies of bild, spiegel, rnd, tonline and zdfheute contain share bars, player code, caption blocks, +++ tickers and consent text. Every record below 0.90 was checked for stored-only sentences; the stored-only text was chrome, captions, sub-headings or spacing artefacts in all 79 cases.",
    ],
    "us": [
        "Author bios and byline blocks (Fox `author-bio`, NBC `byline`, NYT `bottom-of-article`) are not body. Contributor credits that are paragraphs of the story are kept.",
        "NBC Morning Rundown pages keep their own newsletter text, including the sign-up line for The Selection (4 bodies, listed as recurring); Yahoo copies of them have the prompts cut.",
        "CNN video pages with a one-line slate keep that slate as body (stored v1 does the same).",
        "One hand-registered exception: the Yahoo \"Sunday shows preview\" page ends on a guest list without a full stop (`ends_without_full_stop`, quote in the exception list).",
        "Of 48 records below 0.90 against v1, all are `stored_wrong`: stored bodies carry captions, \"Share full article\" blocks, \"Our Coverage\" guides, Yahoo key-point boxes, Fox video overlays and promo text; the new body had no article text that the stored body lacks except leads and decks.",
    ],
}
OPEN_PROBLEMS = {
    "germany": [
        "Live blogs are deferred (17 rows). Paywalled pages give only the lead (`paywall: true`): Spiegel 7, Bild 1, WELT 1.",
        "A one-off promo or footer that occurs in fewer than 3 bodies cannot be found automatically; the automatic chrome check only sees recurring text.",
    ],
    "us": [
        "Live blogs are deferred (43 rows). Paywalled or lead-only captures: NYT 19, WaPo 5 (see `paywall`).",
        "Yahoo syndicates dozens of outlets; footers and promos that occur in fewer than 3 bodies are only caught by the generic patterns in `BOILER_RE`. Expect a few left over.",
        "CBS `Face the Nation` transcript: the guest list (short list items) is not in the body.",
        "ABC page-state bodies and AP rolling stories contain repeated background paragraphs that are in the publisher's text.",
    ],
}


def exception_lines(check_items, outlet):
    """Distinct publisher exceptions of one outlet: (type, quote) with the number of bodies and the check."""
    seen = {}
    for it in check_items:
        if it["outlet"] != outlet:
            continue
        for name in CHECK_NAMES:
            e = it["checks"][name].get("exception")
            if e:
                key = (e["type"], name, e["quote"])
                seen.setdefault(key, []).append(it["raw_path"])
    return sorted(seen.items(), key=lambda kv: (kv[0][0], -len(kv[1]), kv[0][2]))


def report(country, records, validation, reg, adjudications, prose, check_items=(), reextract=()):
    out = DATA / country / "05-extraction/round2/extraction-report.md"
    by_outlet = defaultdict(list)
    for r in records:
        by_outlet[r["outlet"]].append(r)
    adj_counts = Counter(row["classification"] for row in adjudications)
    lines = ["# Round 2 extraction report (" + country + ")", "",
             "Extractor: `pipeline/05-extraction/round2/extract_cached_de_us.py`. Offline; every candidate's raw copy is a byte-exact gzip of its cached source page.",
             "", "## Counts", "",
             f"- Gap rows: {len(records)}", f"- ok: {sum(r['ok'] for r in records)}",
             f"- Failures by reason: {dict(sorted(Counter(r['failure'] for r in records if r['failure']).items()))}",
             "", "| outlet | usable | rows | ok | live blogs deferred | other failures |", "| --- | --- | ---: | ---: | ---: | ---: |"]
    for outlet in RULES[country]:
        rows = by_outlet[outlet]
        live = sum(r["failure"] == "deferred_liveblog" for r in rows)
        lines.append(f"| {outlet} | {'yes' if validation[outlet]['usable'] else 'no'} | {len(rows)} | {sum(r['ok'] for r in rows)} | {live} | {sum(not r['ok'] for r in rows) - live} |")
    lines += ["", "## Gate: five checks per body", "",
              "A body passes when all five checks pass; a check that fails on the publisher's own text carries a `publisher_exception` with a page quote and counts as a pass. "
              "Bodies counted: the re-extracted corpus pages with a raw file plus the gap pages that produced a body. Gate: at least 95% pass all five, and no fixable `new_wrong`.", "",
              "| outlet | bodies | all five | rate | no_chrome | lead_present | not_truncated | no_duplication | order | exceptions |",
              "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |"]
    for outlet in RULES[country]:
        v = validation[outlet]
        c = v["checks"]
        ex = ", ".join(f"{k}={n}" for k, n in sorted(v["exceptions"].items())) or "none"
        lines.append(f"| {outlet} | {v['all_pass']['n']} | {v['all_pass']['pass']} | {v['all_pass']['rate']:.1%} | "
                     + " | ".join(f"{c[n]['pass']}/{c[n]['n']}" for n in CHECK_NAMES) + f" | {ex} |")
    lines += ["", "Lead check as calibrated for Israel/Lebanon: the description's opening words in the first 400 characters pass; "
              "a description whose opening words occur nowhere in the body is a rewritten teaser and passes, labelled `description_is_rewrite`; "
              "words found only after the first 400 characters fail unless what precedes them is genuine article text (`description_is_a_later_sentence`, with a quote).", ""]
    rewrites = Counter()
    for it in check_items:
        reason = it["checks"]["lead_present"].get("reason", "")
        if reason.startswith("description_is_rewrite"):
            rewrites[(it["outlet"], reason)] += 1
    if rewrites:
        lines.append("`description_is_rewrite` counts: " + ", ".join(f"{o} {r.split(':')[-1] if ':' in r else 'rewrite'}={n}" for (o, r), n in sorted(rewrites.items())) + ".")
        lines.append("(`on_page_not_in_body` means the page shows the description's opening words in a prose element that the extractor did not take; these were reviewed by hand.)")
        lines.append("")
    lines += ["## Publisher exceptions used", ""]
    totals = Counter()
    for outlet in RULES[country]:
        items = exception_lines(check_items, outlet)
        if not items:
            continue
        lines += [f"### {outlet}", ""]
        for (typ, name, quote), who in items:
            totals[typ] += len(who)
            lines.append(f"- `{typ}` ({name}), {len(who)} bod{'y' if len(who) == 1 else 'ies'}: \"{quote}\"")
        lines.append("")
    lines += ["Totals by type: " + (", ".join(f"{k}={v}" for k, v in sorted(totals.items())) or "none") + ".", ""]
    lines += ["## Chrome check", "",
              "Sentences of 6+ words found in 3 or more bodies of one outlet with different headlines were reviewed one by one. Page chrome that turned up was removed by container or paragraph rules, not sentence by sentence; what remains is wire or standing publisher text, listed above as `sentence_recurs_across_articles`.", ""]
    lines += ["## Regression diagnostic against stored v1 bodies", "",
              "Diagnostic only: stored v1 bodies often hold page chrome (share bars, caption blocks, newsletter boxes, player code).", "",
              "| outlet | n | median ratio | share >= 0.90 |", "| --- | ---: | ---: | ---: |"]
    for outlet, val in reg.items():
        lines.append(f"| {outlet} | {val['n']} | {val['median']:.3f} | {val['share']:.1%} |")
    lines += ["", f"Adjudication of every record below 0.90 (`regression-adjudication.csv`): stored_wrong={adj_counts['stored_wrong']}, new_wrong={adj_counts['new_wrong']}, both={adj_counts['both']}.", ""]
    # Spot samples.
    lines += ["## Spot samples", "", "Chosen with `random.Random(2024)` from the gap candidates that have a body.", ""]
    rng = random.Random(2024)
    for outlet in RULES[country]:
        pool = [r for r in by_outlet[outlet] if r["body_text"]]
        if not pool:
            continue
        lines.append(f"### {outlet}")
        for r in rng.sample(pool, min(3, len(pool))):
            body = r["body_text"].replace("\n", " / ")
            lines += ["", f"- {r['title']} | {r['published_at'] or 'no date'} | {r['document_type_hint']} | {r['extract_method']}",
                      f"  - first 200: {body[:200]}", f"  - last 150: {body[-150:]}"]
        lines.append("")
    lines += ["## What changed since round 1", ""] + CHANGES.get(country, []) + ["", "## Judgment calls", ""] + JUDGMENTS.get(country, []) + ["", "## Open problems", ""]
    opened = False
    for outlet in RULES[country]:
        if not validation[outlet]["usable"]:
            failed = [n for n, value in validation[outlet]["checks"].items() if value["rate"] < .95]
            lines.append(f"- {outlet}: unusable ({', '.join(failed) if failed else 'a fixable new_wrong or both adjudication'}). Gap rows are kept with `validation_failed`.")
            opened = True
    for line in OPEN_PROBLEMS.get(country, []):
        lines.append("- " + line)
        opened = True
    if not opened:
        lines.append("- None.")
    out.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main():
    if len(sys.argv) < 2 or sys.argv[1] not in RULES:
        raise SystemExit("usage: extract_cached_de_us.py <germany|us>")
    run(sys.argv[1], write=True)


def run(country, write=True, only=None):
    D = DATA / country
    outdir = D / "05-extraction/round2"
    if write: outdir.mkdir(parents=True, exist_ok=True)
    yahoo_providers = {}
    yp = D / "08-recall-audit/raw/yahoo-providers.csv"
    if yp.exists():
        for r in csv.DictReader(open(yp, encoding="utf-8")):
            name = (r.get("provider_name") or "").strip()
            if name: yahoo_providers[r.get("url", "")] = {"Associated Press": "AP"}.get(name, name)

    reextract, check_items = [], []
    for line in open(D / "06-corpus/corpus.jsonl", encoding="utf-8"):
        old = json.loads(line); raw = old.get("capture", {}).get("raw_path", "")
        outlet = old.get("source", {}).get("page_publisher", "")
        if only and outlet != only: continue
        item = {"document_id": old.get("document_id", ""), "raw_path": raw, "body_text": "", "body_words": 0,
                "extract_method": "", "title": "", "published_at": "", "checks": {}, "ok": False, "warnings": [],
                "outlet": outlet, "stored_body": old.get("content", {}).get("body", ""), "source": "", "id": old.get("document_id", "")}
        path = D / raw if raw else None
        if outlet not in RULES[country] or not path or not path.exists():
            item["warnings"].append("missing_raw_or_unknown_outlet")
            item["checks"] = {name: {"ok": False, "reason": "missing_raw"} for name in CHECK_NAMES}
        else:
            source = raw_text(path); ex = extract(source, country, outlet, old.get("publication", {}).get("canonical_url", ""), yahoo_providers)
            item.update({k: ex[k] for k in ("body_text", "extract_method", "title", "published_at")}); item["body_words"] = len(item["body_text"].split()); item["source"] = source
            item["headline"] = ex["title"]; item["checks"] = initial_checks(source, ex, outlet); check_items.append(item)
        reextract.append(item)

    manifests = list(csv.DictReader(open(D / "08-recall-audit/gap-manifest.csv", encoding="utf-8")))
    cache = {r["key"]: r for r in (json.loads(x) for x in open(D / "08-recall-audit/raw/verify-cache.jsonl", encoding="utf-8"))}
    records, candidate_items = [], []
    for row in manifests:
        outlet, url = row["outlet"], row["url"]
        if only and outlet != only: continue
        rec = {"outlet": outlet, "url": url, "canonical_url": url, "gap_status": row["status"], "central_or_mention": row["central_or_mention"], "fetch_route": "", "source_file": "", "raw_path": "", "title": "", "published_at": "", "published_time": "", "date_source": "", "body_text": "", "body_words": 0, "extract_method": "", "document_type_hint": "article", "paywall": False, "provider": "", "language": "", "ok": False, "failure": "", "warnings": []}
        if row["status"] in {"live_blog", "live_blog_unverified"}: rec["failure"] = "deferred_liveblog"; records.append(rec); continue
        cached = cache.get(key_func(url))
        if not cached: rec["failure"] = "needs_fetch"; records.append(rec); continue
        source_rel, route = cache_source(cached); rec["fetch_route"], rec["source_file"] = route, source_rel
        source_path = D / source_rel
        if not source_rel or not source_path.exists(): rec["failure"] = "needs_fetch"; records.append(rec); continue
        raw_rel = f"raw/{outlet}/r2-{hashlib.sha256(url.encode()).hexdigest()[:16]}.html.gz"; raw_file = D / raw_rel
        if write:
            raw_file.parent.mkdir(parents=True, exist_ok=True)
            # Keep an existing copy when it already decompresses to the exact source bytes.
            same = False
            if raw_file.exists():
                with gzip.open(raw_file, "rb") as z: same = z.read() == source_path.read_bytes()
            if not same:
                with gzip.open(raw_file, "wb") as z: z.write(source_path.read_bytes())
        source = raw_text(source_path); ex = extract(source, country, outlet, url, yahoo_providers)
        rec.update(ex); rec["raw_path"] = raw_rel; rec["canonical_url"] = ex["canonical_url"] or url; rec["body_words"] = len(rec["body_text"].split())
        if not rec["published_at"] and re.fullmatch(r"\d{4}-\d{2}-\d{2}", row.get("published_date", "")): rec["published_at"], rec["date_source"] = row["published_date"], "audit-manifest"
        item = {"id": raw_rel, "raw_path": raw_rel, "outlet": outlet, "headline": rec["title"], "body_text": rec["body_text"], "extract_method": rec["extract_method"], "source": source, "checks": initial_checks(source, ex, outlet), "ok_checks": False}
        candidate_items.append(item); check_items.append(item); records.append(rec)

    prose = apply_cross_checks(check_items)
    reg, adjudications = regression(country, reextract)
    blocked = {row["outlet"] for row in adjudications if row["classification"] in {"new_wrong", "both"}}
    validation = validation_summary(check_items, country)
    for outlet in validation:
        if outlet in blocked:
            validation[outlet]["usable"] = False
    for item in reextract:
        item["ok"] = bool(item.get("body_text") and item.get("ok_checks"))
    fetched = [r for r in records if r["gap_status"] not in {"live_blog", "live_blog_unverified"} and r["failure"] != "needs_fetch"]
    for rec, item in zip(fetched, candidate_items):
        usable = validation[rec["outlet"]]["usable"]
        rec["ok"] = bool(rec["title"] and (rec["body_text"] or rec["document_type_hint"] in ("video_page", "podcast_page")) and usable)
        if rec["ok"]:
            rec["failure"] = ""
        elif not rec["title"]:
            rec["failure"] = "wrong_page"
        elif not usable:
            rec["failure"] = "validation_failed"
        elif not rec["body_text"]:
            rec["failure"] = "no_container"
        else:
            rec["failure"] = "empty"
        rec["warnings"] = list(rec.get("warnings", [])) + check_warnings(item["checks"])
        if rec["body_text"] and not item["ok_checks"]:
            rec["warnings"].append("automatic_checks_failed")
    if not write:
        return {"records": records, "reextract": reextract, "check_items": check_items, "validation": validation,
                "adjudications": adjudications, "reg": reg, "prose": prose, "blocked": blocked}
    kept_rows = []
    for item in reextract:
        item["warnings"] = check_warnings(item.get("checks", {}))
        kept_rows.append({k: item[k] for k in ("document_id", "raw_path", "body_text", "body_words", "extract_method", "title", "published_at", "checks", "ok", "warnings")})
    with open(outdir / "reextract-v1.jsonl", "w", encoding="utf-8") as f:
        for r in kept_rows: f.write(json.dumps(r, ensure_ascii=False) + "\n")
    with open(outdir / "candidates.jsonl", "w", encoding="utf-8") as f:
        for r in records: f.write(json.dumps(r, ensure_ascii=False) + "\n")
    with open(outdir / "regression-adjudication.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["document_id", "outlet", "raw_path", "ratio", "classification", "evidence"]); writer.writeheader(); writer.writerows(adjudications)
    report(country, records, validation, reg, adjudications, prose, check_items, reextract)
    print(country, "rows", len(records), "ok", sum(r["ok"] for r in records),
          "usable", [o for o, v in validation.items() if v["usable"]],
          "blocked", sorted(blocked))


def survey(country, only=None, show=("lead_present", "not_truncated", "no_duplication", "no_chrome", "order"), width=200):
    """Debug listing of failing checks and of every exception used (no files written)."""
    r = run(country, False, only)
    for o, v in r["validation"].items():
        if v["checks"]["order"]["n"]:
            print(o, "usable" if v["usable"] else "UNUSABLE", f"all5 {v['all_pass']['pass']}/{v['all_pass']['n']}", dict(v["exceptions"]))
    for it in r["check_items"]:
        for n in show:
            c = it["checks"][n]
            if not c["ok"] and it["body_text"]:
                print("FAIL", n, it["outlet"], it["raw_path"], {k: v for k, v in c.items() if k != "ok"})
    return r


def recurring(r, only, width=170):
    """All sentences (6+ words) that sit in 3+ bodies with different headlines, with the paragraph they close."""
    items = [i for i in r["check_items"] if i["outlet"] == only and i["body_text"]]
    heads = defaultdict(set)
    for i in items:
        for sent in sentences(i["body_text"], 6): heads[sent.lower()].add(i.get("headline") or i["raw_path"])
    for sent, hs in sorted(heads.items(), key=lambda kv: -len(kv[1])):
        if len(hs) >= 3: print("REC", len(hs), sent[:width])


PROMOISH = re.compile(r"whatsapp|newsletter|abonnier|subscribe|sign up|download|\bapp\b|instagram|facebook|twitter|\bx\.com|"
                      r"youtube|telegram|follow (?:us|@)|folgen sie|lesen sie (?:auch|mehr)|hier (?:klicken|lesen|anmelden)|"
                      r"click here|read more|read the original|originally appeared|©|copyright|advertis|anzeige|cookie|"
                      r"push-?nachricht|eilmeldung|mehr zum thema|mehr dazu|verwandte|related|recommended|trending|"
                      r"for more |watch |listen |podcast|photo:|foto:|bild:|credit|getty|\bap photo|image:|bildquelle|"
                      r"all rights|alle rechte|weiterlesen|continue reading|story continues|click to|tap to|"
                      r"here\'s how|share this|teilen|kommentar", re.I)


def promoish(r, only, width=170):
    """Distinct paragraphs of an outlet's bodies that look like promo or page furniture (for hand review)."""
    seen = {}
    for i in r["check_items"]:
        if i["outlet"] != only: continue
        for para in i["body_text"].split("\n"):
            if PROMOISH.search(para) and len(para.split()) <= 40:
                seen.setdefault(para[:width], []).append(i["raw_path"].split("/")[-1][:12])
    for para, who in sorted(seen.items(), key=lambda kv: -len(kv[1])):
        print("PROMO?", len(who), who[0], "|", para)


def newonly(country, r, only, width=190):
    """Sentences the new body has that the stored v1 body lacks (stored text is not a clean reference; for hand review)."""
    stored = {}
    for line in open(DATA / country / "06-corpus/corpus.jsonl", encoding="utf-8"):
        d = json.loads(line); stored[d.get("document_id", "")] = d.get("content", {}).get("body", "")
    norm = lambda t: re.sub(r"\W+", " ", clean(t).lower()).strip()
    for it in r["reextract"]:
        if it.get("outlet", "") and it["outlet"] != only: continue
        sb = stored.get(it.get("document_id", ""))
        if not sb or not it.get("body_text"): continue
        blob = norm(sb)
        for para in it["body_text"].split("\n"):
            if norm(para) and norm(para) not in blob:
                print("NEW-ONLY", it["document_id"][:22], "|", para[:width])


def storedonly(country, r, only, limit=70, width=200):
    """Stored v1 sentences (8+ words) missing from the new body, most frequent first (for hand review of stored_wrong)."""
    stored = {}
    for line in open(DATA / country / "06-corpus/corpus.jsonl", encoding="utf-8"):
        d = json.loads(line); stored[d.get("document_id", "")] = d.get("content", {}).get("body", "")
    norm = lambda t: re.sub(r"\W+", " ", clean(t).lower()).strip()
    seen = defaultdict(list)
    for it in r["reextract"]:
        if it.get("outlet") != only: continue
        sb = stored.get(it.get("document_id", ""))
        if not sb: continue
        blob = norm(it.get("body_text", ""))
        for sent in sentences(sb, 8):
            if norm(sent) not in blob:
                seen[sent[:width]].append(it["document_id"][:20])
    for sent, who in sorted(seen.items(), key=lambda kv: -len(kv[1]))[:limit]:
        print("STORED-ONLY", len(who), who[0], "|", sent)


def review(country, only, nsample=4):
    """Debug listing for hand review of one outlet (no files written)."""
    r = survey(country, only)
    items = [i for i in r["check_items"] if i["outlet"] == only]
    print("methods", Counter(i["extract_method"] for i in items))
    print("empty", sum(1 for i in items if not i["body_text"]), "of", len(items))
    words = sorted(len(i["body_text"].split()) for i in items)
    print("words min/med/max", words[0], words[len(words) // 2], words[-1])
    first, last = Counter(), Counter()
    for i in items:
        paras = [p for p in i["body_text"].split("\n") if p.strip()]
        if paras: first[paras[0][:90]] += 1; last[paras[-1][:90]] += 1
    print("FIRST-PARAGRAPH repeats", [(k, v) for k, v in first.most_common(6) if v > 1])
    print("LAST-PARAGRAPH repeats", [(k, v) for k, v in last.most_common(8) if v > 1])
    rec = Counter()
    for i in items:
        for n in CHECK_NAMES:
            e = i["checks"][n].get("exception")
            if e: rec[(n, e["type"], e["quote"][:110])] += 1
    for k, v in rec.most_common(40): print("EXC", v, k)
    rnd = random.Random(7)
    pool = [i for i in items if i["body_text"]]
    for i in rnd.sample(pool, min(nsample, len(pool))):
        paras = i["body_text"].split("\n")
        print("--", i["raw_path"], "|", i.get("headline", "")[:80], "|", i["extract_method"], len(i["body_text"].split()))
        print("   FIRST:", paras[0][:220]); print("   LAST:", paras[-1][:220])
    return r


if __name__ == "__main__": main()
