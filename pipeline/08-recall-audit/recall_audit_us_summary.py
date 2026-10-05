#!/usr/bin/env python3
"""Recall audit (US): numbers for recall-audit-notes.md that recall-table.csv does not show directly.

- overall recall with and without Yahoo (and with Yahoo restricted to Yahoo-original items)
- path/format classes of the missing items per outlet (video, wire copy, live blog, newsletter, ...)
- ABC wireStory pairs (/US/ and /International/ copies of the same AP story)
- slug-tagger outcome on not_in_manifest items per outlet
- drop reasons of in_candidates_dropped rows, paywall counts
Reads reference-set.csv, gap-manifest.csv, raw/yahoo-providers.csv (run recall_audit_us_yahoo.py first).
Usage: recall_audit_us_summary.py
"""
import csv, json, re, sys
from collections import Counter, defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "04-enumeration"))  # enumerate_de_us
from recall_audit_common import ROOT
from enumerate_de_us import tag, US_STRONG, US_CTX, US_EVT

RAD = ROOT / "us" / "08-recall-audit"
ref = list(csv.DictReader(open(RAD / "reference-set.csv", encoding="utf-8")))
gap = list(csv.DictReader(open(RAD / "gap-manifest.csv", encoding="utf-8")))
yp = {r["url"]: r for r in csv.DictReader(open(RAD / "raw" / "yahoo-providers.csv", encoding="utf-8"))
      if r["source"] == "reference"}


def fmt(a, b):
    return f"{a}/{b} = {a / b:.2f}" if b else f"{a}/{b}"


def recall(rows, label):
    n, i = len(rows), sum(r["status"] == "in_corpus" for r in rows)
    c = [r for r in rows if r["central_or_mention"] == "central"]
    m = [r for r in rows if r["central_or_mention"] == "mention"]
    print(f"{label:55s} all {fmt(i, n):16s} central {fmt(sum(r['status'] == 'in_corpus' for r in c), len(c)):16s} "
          f"mention {fmt(sum(r['status'] == 'in_corpus' for r in m), len(m))}")


print("== overall recall")
recall(ref, "all outlets")
recall([r for r in ref if r["outlet"] != "yahoo"], "without Yahoo")
recall([r for r in ref if r["outlet"] not in ("yahoo", "reuters")], "without Yahoo and Reuters")
recall([r for r in ref if r["outlet"] != "yahoo" or yp.get(r["url"], {}).get("provider_class") == "yahoo-original"],
       "with Yahoo restricted to Yahoo-original items")
ind = [r for r in ref if r["outlet"] != "yahoo" and r["independent_routes"]]
recall(ind, "without Yahoo, independently found items only")


def fclass(r):
    u, o = r["url"], r["outlet"]
    if r["is_liveblog"]:
        return "live blog"
    if re.search(r"/video/|/videos/|/video\d", u):
        return "video page"
    if o == "abc" and "/wireStory/" in u:
        return "AP wire copy (ABC wireStory)"
    if o == "wapo" and re.search(r"_story\.html|/[0-9a-f]{8}-[0-9a-f]{4}-", u):
        return "AP wire copy (WaPo _story)"
    if re.search(r"/briefing/|/newsletters?/|daily-briefing|5-things|morning-rundown|the-excerpt", u):
        return "newsletter/briefing"
    if re.search(r"/podcasts?/", u):
        return "podcast page"
    if re.search(r"/opinions?/", u):
        return "opinion"
    if re.search(r"/interactive/|/graphics/|/card/", u):
        return "interactive/graphic/card"
    if "radio.foxnews.com" in u:
        return "Fox News Radio"
    return "article"


print("\n== missing items (not in corpus) by format, per outlet (status not_in_manifest / other)")
for o in sorted({r["outlet"] for r in ref}):
    rows = [r for r in ref if r["outlet"] == o and r["status"] != "in_corpus"]
    c = Counter((fclass(r), r["status"] == "not_in_manifest") for r in rows)
    print(f"  {o}: " + "; ".join(f"{k[0]}{'' if k[1] else ' (other status)'} {v}" for k, v in sorted(c.items(), key=lambda x: -x[1])))

print("\n== ABC wireStory duplicate pairs (same slug under /US/ and /International/ etc.)")
slug = defaultdict(list)
for r in ref:
    if r["outlet"] == "abc" and "/wireStory/" in r["url"]:
        slug[re.sub(r"-\d+$", "", r["url"].rstrip("/").split("/")[-1])].append(r)
pairs = {k: v for k, v in slug.items() if len(v) > 1}
print(f"  wireStory rows {sum(len(v) for v in slug.values())}, distinct stories {len(slug)}, slugs with >1 copy {len(pairs)}")
abc = [r for r in ref if r["outlet"] == "abc"]
seen, dedup = set(), []
for r in abc:
    k = re.sub(r"-\d+$", "", r["url"].rstrip("/").split("/")[-1]) if "/wireStory/" in r["url"] else r["url"]
    if k not in seen:
        seen.add(k); dedup.append(r)
recall(dedup, "ABC after collapsing wireStory copies")
recall([r for r in abc if "/wireStory/" not in r["url"]], "ABC own-byline items only (no wireStory)")
wp = [r for r in ref if r["outlet"] == "wapo"]
recall([r for r in wp if fclass(r) != "AP wire copy (WaPo _story)"], "WaPo without AP wire copies")

print("\n== slug-tagger outcome for not_in_manifest items (would the original tagger have caught them?)")
for o in sorted({r["outlet"] for r in ref}):
    c = Counter((r["central_or_mention"], tag(r["url"], US_STRONG, US_CTX, US_EVT) or "untagged")
                for r in ref if r["outlet"] == o and r["status"] == "not_in_manifest")
    if c:
        print(f"  {o}: " + ", ".join(f"{k[0]}/{k[1]} {v}" for k, v in sorted(c.items())))

print("\n== in_candidates_dropped notes")
for r in ref:
    if r["status"] == "in_candidates_dropped":
        print(f"  {r['outlet']:8s} {r['central_or_mention']:8s} {r['url'][:90]} | {r['notes'][:110]}")

print("\n== paywall flags among missing items")
print(" ", Counter(r["outlet"] for r in gap if r["paywall"] == "yes"))
print("\n== gap manifest size (central) per outlet")
g = Counter(r["outlet"] for r in gap)
gc = Counter(r["outlet"] for r in gap if r["central_or_mention"] == "central")
gl = Counter(r["outlet"] for r in gap if r["status"] == "live_blog_unverified")
print("  " + ", ".join(f"{o} {g[o]} ({gc[o]}; unverified live blogs {gl[o]})" for o in sorted(g)), "| total", sum(g.values()))

print("\n== reference routes per outlet (items found by each route)")
for o in sorted({r["outlet"] for r in ref}):
    c = Counter()
    for r in ref:
        if r["outlet"] == o:
            for x in r["discovery_route"].split(";"):
                c[x.split(":")[0]] += 1
    print(f"  {o}: {dict(c)}; with an independent route: {sum(1 for r in ref if r['outlet'] == o and r['independent_routes'])}")
