#!/usr/bin/env python3
"""Corpus v1.2 repair pass (2026-09-16 deep-dive review fixes).

Edits data/<country>/06-corpus/corpus.jsonl in place (same convention as
repair_v11_israel.py). Stages per country:

us:      re-extract fox/cnn/yahoo bodies from raw HTML containers
         (kills 2026 fetch-day chrome), AMP/desktop dedup,
         Yahoo provenance.credit rebuild from body/raw markers.
germany: t-online headlines from og:title, RND crossword-tail scrub,
         Bild opinion-CTA scrub, WELT nav-prefix scrub, Spiegel
         Merkliste/meinung residue scrub, Spiegel paywall shells
         retyped flash_or_lead w/ empty body.
lebanon: Al Jadeed chrome re-extraction from raw, Al-Manar headline
         chrome strip + press-review doc-typing, MTV date repair
         from raw meta.
israel:  N12 mako path-twin dedup, Makan Archive-Team body
         re-extraction, published_time recovery from raw (all
         records where JSON-LD/meta carries a clock).

Run: python3 pipeline/07-repair/repair_v12.py <country> [--dry]
"""
import hashlib, html as htmllib, json, re, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2] / "data"
DRY = "--dry" in sys.argv


def load(country):
    p = ROOT / country / "06-corpus/corpus.jsonl"
    return p, [json.loads(l) for l in open(p, encoding="utf-8")]


def save(p, recs):
    if DRY:
        print("[dry] not writing", p)
        return
    with open(p, "w", encoding="utf-8") as f:
        for r in recs:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    print("wrote", p)


def raw_text(country, r):
    rp = r["capture"]["raw_path"]
    if not rp:
        return ""
    fp = ROOT / country / rp
    if not fp.exists():
        return ""
    return open(fp, encoding="utf-8", errors="ignore").read()


def strip_tags(seg):
    seg = re.sub(r"<script[^>]*>.*?</script>", " ", seg, flags=re.S | re.I)
    seg = re.sub(r"<style[^>]*>.*?</style>", " ", seg, flags=re.S | re.I)
    seg = re.sub(r"<[^>]+>", " ", seg)
    return htmllib.unescape(re.sub(r"\s+", " ", seg)).strip()


def paragraphs(seg):
    ps = re.findall(r"<p[^>]*>(.*?)</p>", seg, flags=re.S)
    out = [strip_tags(p) for p in ps]
    return " ".join(t for t in out if t)


def set_body(r, body, note):
    body = body.strip()
    r["content"]["body"] = body
    r["content"]["word_count"] = len(body.split())
    if r["content"].get("body_sha256"):
        r["content"]["body_sha256"] = hashlib.sha256(body.encode()).hexdigest()
    w = r["extraction"].setdefault("warnings", [])
    if note not in w:
        w.append(note)


def canon_url(u):
    u = re.sub(r"\.amp$", "", u)
    u = u.replace("/amp/", "/")
    return u.rstrip("/")


# ---------------------------------------------------------------- us
YAHOO_CREDIT = [
    ("Reuters", [r"\(Reuters\)", r"Thomson Reuters"]),
    ("AP", [r"\(AP\)", r"Associated Press"]),
    ("AFP", [r"AFP/Getty", r"\(AFP\)", r"Agence France"]),
    ("Telegraph", [r"The Telegraph"]),
    ("NBC News", [r"NBC News"]),
    ("USA Today", [r"USA TODAY"]),
    ("Fortune", [r"featured on Fortune\.com"]),
    ("The Independent", [r"The Independent"]),
    ("HuffPost", [r"HuffPost"]),
    ("The New Republic", [r"New Republic"]),
]


def repair_us(recs):
    n_re = n_dedup = n_credit = 0
    for r in recs:
        o = r["source"]["page_publisher"]
        if o not in ("fox", "cnn", "yahoo"):
            continue
        t = raw_text("us", r)
        if not t:
            continue
        new = ""
        if o == "fox":
            m = re.search(r'<div class="article-body"', t)
            if m:
                seg = t[m.start():]
                end = seg.find("</article>")
                new = paragraphs(seg[: end if end > 0 else len(seg)])
        elif o == "cnn":
            if "/video/" in r["publication"]["canonical_url"]:
                m = re.search(
                    r'<meta\s+(?:property|name)="og:description"\s+content="([^"]*)"', t
                ) or re.search(
                    r'<meta\s+content="([^"]*)"\s+(?:property|name)="og:description"', t
                )
                new = htmllib.unescape(m.group(1)) if m else ""
                r["publication"]["document_type"] = "video_page"
            else:
                ps = re.findall(
                    r'<p[^>]*class="[^"]*paragraph[^"]*"[^>]*>(.*?)</p>', t, flags=re.S
                )
                new = " ".join(x for x in (strip_tags(p) for p in ps) if x)
        elif o == "yahoo":
            i = t.find("<article")
            if i >= 0:
                j = t.find("</article>", i)
                new = paragraphs(t[i: j if j > 0 else len(t)])
            # trailing fetch-day recirculation sometimes inside article
            new = re.sub(r"This story was originally featured on Fortune\.com.*$",
                         "This story was originally featured on Fortune.com", new)
        if new and (new != r["content"]["body"]):
            set_body(r, new, "body_reextracted_v12_container")
            n_re += 1
        elif not new and o == "cnn" and "/video/" in r["publication"]["canonical_url"]:
            set_body(r, "", "body_cleared_v12_video_no_description")
            n_re += 1

    # Yahoo credit rebuild
    for r in recs:
        if r["source"]["page_publisher"] != "yahoo" or r["provenance"]["credit"]:
            continue
        hay = (r["content"]["body"] or "")[:4000] + " " + (r["content"]["body"] or "")[-1500:]
        for credit, pats in YAHOO_CREDIT:
            if any(re.search(p, hay) for p in pats):
                r["provenance"]["credit"] = credit
                r["provenance"]["content_origin"] = "syndicated_or_adapted"
                n_credit += 1
                break

    # AMP/desktop dedup: same canonical URL within one outlet
    seen = {}
    for r in recs:
        if not r["deduplication"]["is_primary_record"]:
            continue
        key = (r["source"]["page_publisher"],
               canon_url(r["publication"]["canonical_url"]))
        if key in seen:
            keep = seen[key]
            # keep the non-AMP (canonical) capture; if tie, higher word count
            a_amp = "/amp/" in r["publication"]["canonical_url"] or r["publication"]["canonical_url"].endswith(".amp")
            k_amp = "/amp/" in keep["publication"]["canonical_url"] or keep["publication"]["canonical_url"].endswith(".amp")
            drop = r if (a_amp and not k_amp) else keep if (k_amp and not a_amp) else \
                   (r if r["content"]["word_count"] <= keep["content"]["word_count"] else keep)
            survivor = keep if drop is r else r
            drop["deduplication"]["is_primary_record"] = False
            drop["deduplication"]["exact_duplicate_cluster_id"] = "ampdup_" + survivor["document_id"]
            survivor["deduplication"]["exact_duplicate_cluster_id"] = "ampdup_" + survivor["document_id"]
            seen[key] = survivor
            n_dedup += 1
        else:
            seen[key] = r
    print(f"us: re-extracted {n_re}, amp-dedup {n_dedup}, yahoo credits {n_credit}")


# ----------------------------------------------------------- germany
def repair_germany(recs):
    n_head = n_scrub = n_pw = 0
    for r in recs:
        o = r["source"]["page_publisher"]
        b = r["content"]["body"] or ""
        if o == "tonline" and not (r["content"]["headline"] or "").strip():
            t = raw_text("germany", r)
            m = re.search(r'<meta\s+(?:property|name)="og:title"\s+content="([^"]*)"', t) or \
                re.search(r'<meta\s+content="([^"]*)"\s+(?:property|name)="og:title"', t) or \
                re.search(r"<title>([^<]*)</title>", t)
            if m:
                h = htmllib.unescape(m.group(1))
                h = re.sub(r"\s*[|–-]\s*(t-online|Nachrichten).*$", "", h).strip()
                if h:
                    r["content"]["headline"] = h
                    r["extraction"]["warnings"].append("headline_from_ogtitle_v12")
                    n_head += 1
        nb = b
        if o == "rnd":
            nb = re.sub(r"\s*(Das tägliche Kreuzworträtsel|Kreuzworträtsel).*$", "", nb)
        if o == "bild":
            nb = re.sub(r"\s*Haben Sie eine Meinung zu diesem Artikel\?.*$", "", nb)
        if o == "welt":
            nb = re.sub(r"^\s*Inhaltsbereich Hauptnavigation Suche Login Fußbereich \d*\s*", "", nb)
        if o == "spiegel":
            nb = re.sub(r"\s*Merkliste[^.]{0,80}hinzufügen\s*", " ", nb)
            nb = re.sub(r"(meinung\s+){2,}", "", nb, flags=re.I)
            if "nicht mehr aufrufen" in nb:
                nb = ""
                r["publication"]["document_type"] = "flash_or_lead"
                r["extraction"]["warnings"].append("paywall_shell_v12_body_cleared")
                n_pw += 1
        nb = re.sub(r"\s+", " ", nb).strip()
        if nb != b:
            set_body(r, nb, "body_scrubbed_v12")
            n_scrub += 1
        if o == "rnd" and r["content"]["word_count"] < 20 and \
                r["publication"]["document_type"] == "article":
            r["publication"]["document_type"] = "flash_or_lead"
    print(f"germany: tonline headlines {n_head}, scrubbed {n_scrub}, spiegel paywall shells {n_pw}")


# ----------------------------------------------------------- lebanon
def repair_lebanon(recs):
    n_re = n_head = n_type = n_date = 0
    for r in recs:
        o = r["source"]["page_publisher"]
        if o == "aljadeed":
            b = r["content"]["body"] or ""
            if "2026" in b or "بيت الحلم" in b:
                t = raw_text("lebanon", r)
                new = ""
                if t:
                    m = re.search(r'class="[^"]*(article-content|LongDesc|news-details|articleBody)[^"]*"', t)
                    if m:
                        seg = t[m.start():]
                        end = min(x for x in (seg.find("</article>"), seg.find("</section>"), len(seg)) if x > 0)
                        new = paragraphs(seg[:end]) or strip_tags(seg[:min(end, 20000)])
                    else:
                        m2 = re.search(r'<meta\s+(?:property|name)="og:description"\s+content="([^"]*)"', t)
                        new = htmllib.unescape(m2.group(1)) if m2 else ""
                # last resort: keep old body
                if not new:
                    new = b
                # tail-cut recirculation chrome ("read also / now watching")
                cut = len(new)
                for mark in ("اقرأ ايضا", "تشاهدون الآن", "الأكثر مشاهدة", "بيت الحلم"):
                    k = new.find(mark)
                    if k > 0:
                        cut = min(cut, k)
                new = new[:cut]
                set_body(r, new, "body_dechromed_v12")
                n_re += 1
        if o == "almanar":
            h = r["content"]["headline"] or ""
            nh = re.sub(r"\s*[–-]\s*موقع قناة المنار.*$", "", h).strip()
            if nh != h:
                r["content"]["headline"] = nh
                n_head += 1
            h = r["content"]["headline"] or ""
            if ("الصحافة اليوم" in h or "عناوين واسرار الصحف" in h) and \
                    r["publication"]["document_type"] != "press_review":
                r["publication"]["document_type"] = "press_review"
                n_type += 1

    # MTV undated: interpolate from sequential ids (Al-Manar precedent);
    # assign only when both bracketing dated ids agree on the date.
    import bisect
    mtv = [r for r in recs if r["source"]["page_publisher"] == "mtv"]
    dated = sorted((int(r["document_id"].split("_")[-1]), r["publication"]["published_at"])
                   for r in mtv if r["publication"].get("published_at"))
    days = {f"2024-09-{17+i:02d}": i for i in range(8)}
    for r in mtv:
        if r["publication"].get("published_at"):
            continue
        u = int(r["document_id"].split("_")[-1])
        i = bisect.bisect_left(dated, (u, ""))
        lo = dated[i - 1] if i > 0 else None
        hi = dated[i] if i < len(dated) else None
        d = None
        if lo and hi and lo[1] == hi[1]:
            d = lo[1]
        elif lo is None and hi and hi[0] - u <= 10:
            d = hi[1]
        elif hi is None and lo and u - lo[0] <= 10:
            d = lo[1]
        if d:
            r["publication"]["published_at"] = d
            r["publication"]["date_source"] = "id-interpolated-v12"
            if d in days:
                r["publication"]["time_slot"] = f"day_{days[d]}"
            elif d > "2024-09-24":
                r["publication"]["time_slot"] = "week_2" if d <= "2024-10-01" else "first_month"
            n_date += 1
    print(f"lebanon: aljadeed re-extracted {n_re}, almanar heads {n_head}, press_review {n_type}, mtv dates {n_date}")


# ------------------------------------------------------------ israel
def repair_israel(recs):
    n_dedup = n_body = n_time = 0
    # N12 mako path twins: same Article-<hash> id
    seen = {}
    for r in recs:
        if r["source"]["page_publisher"] != "n12" or not r["deduplication"]["is_primary_record"]:
            continue
        m = re.search(r"(Article-[0-9a-f]+)", r["publication"]["canonical_url"])
        if not m:
            continue
        key = m.group(1)
        if key in seen:
            keep = seen[key]
            drop = r if r["content"]["word_count"] <= keep["content"]["word_count"] else keep
            survivor = keep if drop is r else r
            drop["deduplication"]["is_primary_record"] = False
            drop["deduplication"]["exact_duplicate_cluster_id"] = "pathdup_" + survivor["document_id"]
            survivor["deduplication"]["exact_duplicate_cluster_id"] = "pathdup_" + survivor["document_id"]
            seen[key] = survivor
            n_dedup += 1
        else:
            seen[key] = r
    for r in recs:
        b = r["content"]["body"] or ""
        if r["document_id"] == "il_makan_5961802f18" or "History is littered with hundreds of conflicts" in b:
            t = raw_text("israel", r)
            new = ""
            if t:
                m = re.search(r'<meta\s+(?:property|name)="og:description"\s+content="([^"]*)"', t)
                new = htmllib.unescape(m.group(1)) if m else ""
            set_body(r, new, "archive_team_body_replaced_v12")
            if len(new.split()) < 90:
                r["publication"]["document_type"] = "flash_or_lead"
            n_body += 1
        # published_time recovery
        if not r["publication"].get("published_time"):
            t = raw_text("israel", r)
            m = re.search(r'"datePublished"\s*:\s*"(2024-\d\d-\d\dT\d\d:\d\d[^"]*)"', t)
            if m:
                r["publication"]["published_time"] = m.group(1)
                n_time += 1
    # Abu Ali: timestamps from the telegram message stream
    import csv
    msgs = {row["post_id"]: row["datetime"] for row in
            csv.DictReader(open(ROOT / "israel" / "04-enumeration" / "abuali-messages.csv", encoding="utf-8"))}
    for r in recs:
        if r["source"]["page_publisher"] == "abuali" and not r["publication"].get("published_time"):
            pid = r["document_id"].split("_")[-1]
            if pid in msgs:
                r["publication"]["published_time"] = msgs[pid]
                n_time += 1
    print(f"israel: n12 path-dedup {n_dedup}, bodies fixed {n_body}, timestamps {n_time}")


# ------------------------------------------------- v1.2.1 fixups
# post-review corrections (codex adversarial review, 2026-09-16)
FOX_TAIL = [" newsletter brings you", "By entering your email and clicking the Subscribe",
            "Subscribed You've successfully subscribed"]


def fixups_us(recs):
    n = 0
    for r in recs:
        if r["source"]["page_publisher"] != "fox":
            continue
        b = r["content"]["body"] or ""
        cut = len(b)
        for mk in FOX_TAIL:
            k = b.find(mk)
            if k > 0:
                cut = min(cut, k)
        if cut < len(b):
            set_body(r, b[:cut].rstrip(), "fox_newsletter_tail_cut_v121")
            n += 1
    print(f"us fixups: fox tails cut {n}")


def fixups_lebanon(recs):
    n = 0
    for r in recs:
        if r["source"]["page_publisher"] == "aljadeed" and \
                "body_dechromed_v12" in r["extraction"]["warnings"]:
            # review finding: all 27 raws have empty LongDesc nodes —
            # these are headline-only ticker shells; any body text was chrome
            set_body(r, "", "body_emptied_v121_shell_page")
            if r["publication"]["document_type"] == "article":
                r["publication"]["document_type"] = "brief"
            n += 1
    print(f"lebanon fixups: aljadeed shells emptied {n}")


def fixups_counts(country, recs):
    n = 0
    for r in recs:
        b = r["content"]["body"] or ""
        wc = len(b.split())
        if r["content"]["word_count"] != wc:
            r["content"]["word_count"] = wc
            n += 1
        if r["content"].get("body_sha256"):
            h = hashlib.sha256(b.encode()).hexdigest()
            if r["content"]["body_sha256"] != h:
                r["content"]["body_sha256"] = h
    print(f"{country} fixups: word_counts recomputed {n}")


def fixups(country, recs):
    if country == "us":
        fixups_us(recs)
    if country == "lebanon":
        fixups_lebanon(recs)
    fixups_counts(country, recs)


STAGES = {"us": repair_us, "germany": repair_germany,
          "lebanon": repair_lebanon, "israel": repair_israel}

if __name__ == "__main__":
    if sys.argv[1] == "fixups":
        for country in ("us", "germany", "lebanon", "israel"):
            p, recs = load(country)
            fixups(country, recs)
            save(p, recs)
    else:
        country = sys.argv[1]
        p, recs = load(country)
        STAGES[country](recs)
        save(p, recs)
