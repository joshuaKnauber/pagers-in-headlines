#!/usr/bin/env python3
"""Recall audit (US): who wrote the Yahoo News items? Splits Yahoo reference items and Yahoo corpus
records by content provider, read from the fetched page (Yahoo's `providerId` field and the provider
logo/byline), and recomputes Yahoo recall per provider class.

Provider classes
  yahoo-original    : providerId 'Yahoo! News' / yahoo_* ids, or provider name "Yahoo News"
  wire              : ap.org, ap_*, reuters.com, reuters-*, afp, dpa_international, upi, bloomberg
  audited-us-outlet : syndicated copy of another audited US outlet (CNN, NBC, CBS, ABC, USA Today, Fox)
  other-partner     : any other partner (The Hill, Telegraph, local TV, Semafor, ...)
  unknown           : page not fetched or no provider field

Also writes, for AP and Reuters, the Yahoo-hosted copies that mention the attacks: these are an
independent sign of what the wire itself published (used in the notes for Reuters, which has no
other independent route).

Usage: recall_audit_us_yahoo.py
Output: data/us/08-recall-audit/raw/yahoo-providers.csv, prints tables.
"""
import csv, json, sys
from collections import Counter, defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from recall_audit_common import *  # noqa

C = "us"
RAD = ROOT / C / "08-recall-audit"


def provider(html):
    pid = re.search(r'"providerId":"([^"]*)"', html)
    pid = pid.group(1) if pid else ""
    name = ""
    m = re.search(r'"provider":\{"@type":"Organization","name":"([^"]*)"', html)
    if m:
        name = m.group(1)
    if not name:
        m = re.search(r'sec:logo-provider[^>]*>.{0,600}?(?:alt|aria-label)="([^"]*)"', html, re.S)
        if m:
            name = H.unescape(m.group(1))
    if not name:
        m = re.search(r'caas-attr-provider[^>]*>.{0,300}?(?:alt|aria-label)="([^"]*)"', html, re.S)
        if m:
            name = H.unescape(m.group(1))
    au = re.search(r'"author":\{"@type":"(?:Person|Organization)"[^}]*?"name":"([^"]*)"', html)
    return pid, name, (au.group(1) if au else "")


def klass(pid, name, author):
    p, n, a = pid.lower(), name.lower(), author.lower()
    if not (p or n):
        return "unknown", ""
    if p in ("yahoo! news",) or p.startswith("yahoo") or n in ("yahoo news", "yahoo! news") or "yahoo news" in a:
        return "yahoo-original", "Yahoo News"
    for pat, lab in ((r"^ap\.org$|^ap_|associated press", "AP"), (r"reuters", "Reuters"), (r"\bafp\b|^afp", "AFP"),
                     (r"dpa_international|\bdpa\b", "dpa"), (r"united_press_international|\bupi\b", "UPI"),
                     (r"bloomberg", "Bloomberg")):
        if re.search(pat, p) or re.search(pat, n):
            return "wire", lab
    for pat, lab in ((r"^cnn_|^cnn$|\bcnn\b", "CNN"), (r"^nbc_news|nbc news", "NBC"), (r"^cbs_news|cbs news", "CBS"),
                     (r"abcnews|abc news", "ABC"), (r"^usa_today|usa today", "USA Today"), (r"fox_news|fox news", "Fox")):
        if re.search(pat, p) or re.search(pat, n):
            return "audited-us-outlet", lab
    return "other-partner", name or pid


def page_for(row, cache, corpus):
    v = cache.get(row["key"]) or {}
    f = ""
    if v.get("fetch", "").startswith("our-raw:"):
        f = v["fetch"].split(":", 1)[1]
    elif v.get("raw_file"):
        f = v["raw_file"]
    if not f and row.get("matched_document_id"):
        r = corpus.get(row["matched_document_id"])
        f = r["capture"]["raw_path"] if r else ""
    p = ROOT / C / f if f else None
    return p.read_text(encoding="utf-8", errors="replace") if p and p.exists() else ""


def main():
    cache = {}
    for l in open(RAD / "raw" / "verify-cache.jsonl", encoding="utf-8"):
        r = json.loads(l)
        cache[r["key"]] = r
    corpus = {}
    for l in open(ROOT / C / "06-corpus/corpus.jsonl", encoding="utf-8"):
        r = json.loads(l)
        corpus[r["document_id"]] = r
    ref = list(csv.DictReader(open(RAD / "reference-set.csv", encoding="utf-8")))
    for r in ref:
        r["key"] = key(r["url"])
    rows = []
    for r in ref:
        if r["outlet"] != "yahoo":
            continue
        html = page_for(r, cache, corpus)
        pid, name, au = provider(html) if html else ("", "", "")
        k, lab = klass(pid, name, au)
        rows.append(dict(source="reference", url=r["url"], title=r["title"], date=r["published_date"],
                         central_or_mention=r["central_or_mention"], status=r["status"],
                         document_id=r["matched_document_id"], provider_id=pid, provider_name=name,
                         author=au, provider_class=k, provider_label=lab))
    seen = {x["document_id"] for x in rows if x["document_id"]}
    for did, r in corpus.items():
        if r["source"]["page_publisher"] != "yahoo" or not r["deduplication"]["is_primary_record"] or did in seen:
            continue
        p = ROOT / C / (r["capture"].get("raw_path") or "")
        html = p.read_text(encoding="utf-8", errors="replace") if r["capture"].get("raw_path") and p.exists() else ""
        pid, name, au = provider(html) if html else ("", "", "")
        k, lab = klass(pid, name, au)
        rows.append(dict(source="corpus-only", url=r["publication"]["canonical_url"], title=r["content"]["headline"],
                         date=r["publication"]["published_at"][:10], central_or_mention="", status="in_corpus",
                         document_id=did, provider_id=pid, provider_name=name, author=au,
                         provider_class=k, provider_label=lab))
    cols = ["source", "url", "title", "date", "central_or_mention", "status", "document_id", "provider_id",
            "provider_name", "author", "provider_class", "provider_label"]
    with open(RAD / "raw" / "yahoo-providers.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=cols); w.writeheader(); w.writerows(rows)
    R = [x for x in rows if x["source"] == "reference"]
    print("Yahoo reference items by provider class (in corpus / ref; central in/ref):")
    T = defaultdict(Counter)
    for x in R:
        t = T[x["provider_class"]]
        t["n"] += 1; t["in"] += x["status"] == "in_corpus"
        t["c"] += x["central_or_mention"] == "central"
        t["cin"] += x["central_or_mention"] == "central" and x["status"] == "in_corpus"
        t[x["status"]] += 1
    for k_ in ("yahoo-original", "wire", "audited-us-outlet", "other-partner", "unknown"):
        t = T[k_]
        print(f"  {k_:18s} {t['in']:3d}/{t['n']:3d}  central {t['cin']}/{t['c']}  "
              f"not_in_manifest={t['not_in_manifest']} inaccessible={t['inaccessible']} dropped={t['in_candidates_dropped']}")
    print("labels:", Counter((x["provider_class"], x["provider_label"]) for x in R
                              if x["provider_class"] in ("wire", "audited-us-outlet", "yahoo-original")).most_common())
    print("other-partner top:", Counter(x["provider_label"] for x in R if x["provider_class"] == "other-partner").most_common(15))
    print("corpus-only Yahoo records:", Counter(x["provider_class"] + ":" + x["provider_label"] for x in rows if x["source"] == "corpus-only"))
    print("all corpus Yahoo (ref matched + corpus-only):",
          Counter(x["provider_class"] + ":" + x["provider_label"] for x in rows if x["status"] == "in_corpus"))

    # Yahoo-hosted wire copies as a proxy reference for AP and Reuters themselves
    import difflib
    ctitles = defaultdict(list)
    for did, r in corpus.items():
        if r["deduplication"]["is_primary_record"]:
            ctitles[r["source"]["page_publisher"]].append(norm_title(r["content"]["headline"]))
    for lab, own in (("Reuters", "reuters"), ("AP", "ap")):
        items = [x for x in R if x["provider_label"] == lab]
        distinct = {}
        for x in items:
            distinct.setdefault(norm_title(x["title"]), x)
        hit_own = sum(1 for t in distinct if t and any(difflib.SequenceMatcher(None, t, c).ratio() >= 0.85 for c in ctitles[own]))
        hit_any = sum(1 for t, x in distinct.items() if t and (x["status"] == "in_corpus" or any(
            difflib.SequenceMatcher(None, t, c).ratio() >= 0.85 for c in ctitles[own])))
        cen = sum(1 for x in distinct.values() if x["central_or_mention"] == "central")
        print(f"Yahoo-hosted {lab} items in reference: {len(items)} rows, {len(distinct)} distinct headlines "
              f"({cen} central); headline found among {own} corpus records: {hit_own}; "
              f"found in corpus as {own} record or Yahoo copy: {hit_any}")


if __name__ == "__main__":
    main()
