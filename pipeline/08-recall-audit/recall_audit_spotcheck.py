#!/usr/bin/env python3
"""Recall audit spot-check: draw a seeded sample of reference rows (2 per outlet, one central and one
mention where possible) and print, for each, the title, the date evidence and a wider window of
body text around the matched attack term, so a human can judge whether the row really concerns the
Sep 17/18 2024 pager/walkie-talkie attacks and falls in the Sep 17-24 window.

Usage: recall_audit_spotcheck.py <country> [seed]          -> prints sample, writes raw/spot-check-sample.csv
       recall_audit_spotcheck.py <country> --verdicts FILE -> merges a url,verdict,comment CSV into raw/spot-check.csv
"""
import csv, json, random, sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from recall_audit_common import *  # noqa


def html_for(country, k, cache, corpus_by_id, did):
    v = cache.get(k, {})
    f = v["fetch"].split(":", 1)[1] if v.get("fetch", "").startswith("our-raw:") else v.get("raw_file", "")
    if not f and did and did in corpus_by_id:
        f = corpus_by_id[did]["capture"].get("raw_path") or ""
    p = ROOT / country / f if f else None
    return (p.read_text(encoding="utf-8", errors="replace") if p and p.exists() else ""), f


def sample(country, seed):
    ra = ROOT / country / "08-recall-audit"
    ref = list(csv.DictReader(open(ra / "reference-set.csv", encoding="utf-8")))
    cache = {}
    for l in open(ra / "raw" / "verify-cache.jsonl", encoding="utf-8"):
        r = json.loads(l); cache[r["key"]] = r
    corpus = {}
    for l in open(ROOT / country / "06-corpus/corpus.jsonl", encoding="utf-8"):
        r = json.loads(l); corpus[r["document_id"]] = r
    rnd = random.Random(seed)
    picks = []
    for o in sorted({r["outlet"] for r in ref}):
        for cm in ("central", "mention"):
            pool = [r for r in ref if r["outlet"] == o and r["central_or_mention"] == cm]
            if not pool:
                pool = [r for r in ref if r["outlet"] == o and r not in picks]
            if pool:
                picks.append(rnd.choice(pool))
    out = []
    for r in picks:
        k = key(r["url"])
        html, f = html_for(country, k, cache, corpus, r["matched_document_id"])
        ctx, pdate = "", ""
        if html:
            ex = extract(html)
            pdate = ex["date"][:10]
            m = has_mention(ex["body"], country)
            if m:
                ctx = ex["body"][max(0, m.start() - 450): m.end() + 450]
        elif r["matched_document_id"] in corpus:
            b = corpus[r["matched_document_id"]]["content"]["body"]
            m = has_mention(b, country)
            ctx = b[max(0, m.start() - 450): m.end() + 450] if m else ""
        out.append(dict(outlet=r["outlet"], url=r["url"], title=r["title"], published_date=r["published_date"],
                        page_date=pdate, central_or_mention=r["central_or_mention"], status=r["status"],
                        evidence=r["evidence"], context=" ".join(ctx.split()), page_file=f))
        print(f"\n### {r['outlet']} | {r['central_or_mention']} | {r['status']} | ref date {r['published_date']} | page date {pdate}")
        print(r["url"]); print("TITLE:", r["title"][:200]); print("CTX:", " ".join(ctx.split())[:1000] or r["evidence"])
    with open(ra / "raw" / "spot-check-sample.csv", "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(out[0])); w.writeheader(); w.writerows(out)


def merge(country, vf):
    ra = ROOT / country / "08-recall-audit"
    s = list(csv.DictReader(open(ra / "raw" / "spot-check-sample.csv", encoding="utf-8")))
    v = {r["url"]: r for r in csv.DictReader(open(vf, encoding="utf-8"))}
    for r in s:
        r["verdict"] = v.get(r["url"], {}).get("verdict", "")
        r["comment"] = v.get(r["url"], {}).get("comment", "")
    with open(ra / "raw" / "spot-check.csv", "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(s[0])); w.writeheader(); w.writerows(s)
    from collections import Counter
    print(Counter(r["verdict"] for r in s))


if __name__ == "__main__":
    if "--verdicts" in sys.argv:
        merge(sys.argv[1], sys.argv[sys.argv.index("--verdicts") + 1])
    else:
        sample(sys.argv[1], int(sys.argv[2]) if len(sys.argv) > 2 else 20241004)
