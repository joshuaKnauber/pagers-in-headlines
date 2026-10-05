#!/usr/bin/env python3
"""Recall audit diagnostics. Usage: recall_audit_analyze.py <germany|us>

1. Reverse check of the reference routes: of our own primary corpus records dated Sep 17-24 that
   mention the attacks, how many did each independent route find? (estimates reference-route coverage)
2. Slug test for gap items: would the original slug keyword tagger have caught them if enumerated?
3. Corpus issues: duplicates by stable URL id, no attack term, out-of-window dates, date vs URL-date
   conflicts, live-blog-shaped records typed as article, video/short records typed article.
Writes raw/route-coverage.csv, raw/corpus-issues.csv; prints summaries.
"""
import csv, json, re, sys
from collections import Counter, defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "04-enumeration"))  # enumerate_de_us
from recall_audit_common import *  # noqa
from enumerate_de_us import tag, DE_STRONG, DE_CTX, DE_EVT, US_STRONG, US_CTX, US_EVT
from recall_audit_build import route_independent


def main(country):
    ra = ROOT / country / "08-recall-audit"
    pool = {r["key"]: r for r in csv.DictReader(open(ra / "raw" / "pool.csv", encoding="utf-8"))}
    corpus = [json.loads(l) for l in open(ROOT / country / "06-corpus/corpus.jsonl", encoding="utf-8")]
    prim = [r for r in corpus if r["deduplication"]["is_primary_record"]]
    # 1. route coverage of our own in-window, on-topic corpus records
    cov = defaultdict(Counter)
    for r in prim:
        pub = r["publication"]["published_at"][:10]
        if not ("2024-09-17" <= pub <= "2024-09-24"):
            continue
        if not has_mention(r["content"]["headline"] + " " + r["content"]["body"], country):
            continue
        o = r["source"]["page_publisher"]
        k = key(r["publication"]["canonical_url"])
        routes = pool[k]["routes"].split(";") if k in pool else []
        if k not in pool:  # fuzzy: pool row matched to this doc by title
            for p in pool.values():
                if p["our_corpus_key"] == k:
                    routes = p["routes"].split(";"); break
        cov[o]["n"] += 1
        cov[o]["any_route"] += bool(routes)
        cov[o]["mediacloud"] += "mediacloud" in routes
        cov[o]["gdelt-gkg"] += "gdelt-gkg" in routes
        cov[o]["listing"] += any(x not in ("mediacloud", "gdelt-gkg") for x in routes)
        cov[o]["indep"] += any(route_independent(x, o) for x in routes)
    with open(ra / "raw" / "route-coverage.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["outlet", "corpus_inwindow_ontopic", "found_by_any_reference_route", "found_by_independent_route",
                    "mediacloud", "gdelt_gkg", "listings_or_pages"])
        for o in sorted(cov):
            c = cov[o]
            w.writerow([o, c["n"], c["any_route"], c["indep"], c["mediacloud"], c["gdelt-gkg"], c["listing"]])
    print(open(ra / "raw" / "route-coverage.csv").read())
    # 2. slug test for gap items
    S, C, E = (DE_STRONG, DE_CTX, DE_EVT) if country == "germany" else (US_STRONG, US_CTX, US_EVT)
    ref = list(csv.DictReader(open(ra / "reference-set.csv", encoding="utf-8")))
    st = Counter()
    for r in ref:
        if r["status"] in ("in_manifest_not_candidate", "not_in_manifest", "live_blog"):
            st[(r["status"], r["central_or_mention"], tag(r["url"], S, C, E) or "untagged")] += 1
    print("slug-tagger outcome on gap items:")
    for k, v in sorted(st.items()):
        print("  ", k, v)
    # 3. corpus issues
    issues = []
    byid = defaultdict(list)
    for r in prim:
        byid[key(r["publication"]["canonical_url"])].append(r)
    for k, v in byid.items():
        if len(v) > 1:
            for r in v:
                issues.append([r["document_id"], r["source"]["page_publisher"], "duplicate",
                               f"same stable URL id as {', '.join(x['document_id'] for x in v if x is not r)} (slug changed; both primary)",
                               r["publication"]["canonical_url"]])
    byh = defaultdict(list)
    for r in prim:
        h = r["content"]["headline"].strip().lower()
        if h:
            byh[(r["source"]["page_publisher"], h)].append(r)
    for (o, h), v in byh.items():
        if len(v) > 1 and len({key(x["publication"]["canonical_url"]) for x in v}) > 1:
            for r in v:
                issues.append([r["document_id"], o, "possible duplicate", f"identical headline to {', '.join(x['document_id'] for x in v if x is not r)}",
                               r["publication"]["canonical_url"]])
    for r in prim:
        u = r["publication"]["canonical_url"]
        pub = r["publication"]["published_at"][:10]
        body = r["content"]["headline"] + " " + r["content"]["body"]
        did, o = r["document_id"], r["source"]["page_publisher"]
        if outlet_of(country, u) is None:
            issues.append([did, o, "scope", "URL outside the audited outlet's scope (e.g. CBS-owned local station page)", u])
        if not has_mention(body, country):
            issues.append([did, o, "off-topic?", f"no pager/walkie/device-explosion term in headline or body (relevance={r['extraction']['relevance']}, {r['content']['word_count']} words)", u])
        if pub and not ("2024-09-17" <= pub <= "2024-10-17"):
            issues.append([did, o, "date", f"published_at {pub} outside the Sep 17-Oct 17 collection window", u])
        m = re.search(r"/(20\d\d)/(\d\d)/(\d\d)/", u)
        if m and pub and pub != f"{m.group(1)}-{m.group(2)}-{m.group(3)}":
            from datetime import date
            d1 = date.fromisoformat(pub); d2 = date(int(m.group(1)), int(m.group(2)), int(m.group(3)))
            if abs((d1 - d2).days) > 1:
                issues.append([did, o, "date", f"published_at {pub} vs URL date {d2}", u])
        if not pub:
            issues.append([did, o, "date", "no published_at", u])
        if is_liveblog(u, r["content"]["headline"]):
            issues.append([did, o, "type", f"live-blog/newsblog page typed {r['publication']['document_type']}; one record stands for many timestamped entries", u])
        if re.search(r"/videos?/|mediathek", u) and r["publication"]["document_type"] == "article":
            issues.append([did, o, "type", "video URL typed article", u])
        if r["publication"]["document_type"] == "article" and r["content"]["word_count"] < 90:
            issues.append([did, o, "type", f"article with {r['content']['word_count']} words", u])
        if r["content"]["word_count"] == 0:
            issues.append([did, o, "empty", "empty body", u])
    with open(ra / "raw" / "corpus-issues.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f); w.writerow(["document_id", "outlet", "issue", "detail", "url"]); w.writerows(issues)
    print("corpus issues:", Counter(i[2] for i in issues))


def md(country):
    ra = ROOT / country / "08-recall-audit"
    T = list(csv.DictReader(open(ra / "raw" / "recall-table.csv", encoding="utf-8")))
    gm = Counter(r["outlet"] for r in csv.DictReader(open(ra / "gap-manifest.csv", encoding="utf-8")))
    gmc = Counter(r["outlet"] for r in csv.DictReader(open(ra / "gap-manifest.csv", encoding="utf-8")) if r["central_or_mention"] == "central")
    corpus = Counter(json.loads(l)["source"]["page_publisher"] for l in open(ROOT / country / "06-corpus/corpus.jsonl")
                     if json.loads(l)["deduplication"]["is_primary_record"])
    print("| outlet | corpus (all dates) | ref items | in corpus | recall | central: in/ref | recall | mention: in/ref | recall | MC hits in ref | gap manifest (central) |")
    print("|---|---|---|---|---|---|---|---|---|---|---|")
    for t in T:
        o = t["outlet"]
        print(f"| {o} | {corpus[o]} | {t['ref_n']} | {t['in_corpus']} | {t['recall']} | {t['central_in']}/{t['central_n']} | {t['central_recall']} | "
              f"{t['mention_in']}/{t['mention_n']} | {t['mention_recall']} | {t['mc_n']} | {gm[o]} ({gmc[o]}) |")
    print()
    print("| outlet | in_corpus | live_blog | in_candidates_dropped | in_manifest_not_candidate | not_in_manifest | inaccessible |")
    print("|---|---|---|---|---|---|---|")
    tot = Counter()
    for t in T:
        vals = [int(t[h]) for h in ("st_in_corpus", "st_live_blog", "st_in_candidates_dropped", "st_in_manifest_not_candidate", "st_not_in_manifest", "st_inaccessible")]
        for i, v in enumerate(vals):
            tot[i] += v
        print(f"| {t['outlet']} | " + " | ".join(map(str, vals)) + " |")
    print("| **total** | " + " | ".join(str(tot[i]) for i in range(6)) + " |")


if __name__ == "__main__":
    (md if "--md" in sys.argv else main)(sys.argv[1])
