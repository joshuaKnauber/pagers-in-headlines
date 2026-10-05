#!/usr/bin/env python3
"""Print the recall tables used in recall-audit-notes.md (markdown).

Usage: recall_audit_il_lb_report.py <country>
Reads raw/items.json, raw/census-summary.json written by recall_audit_il_lb_build.py.
"""
import json, re, sys, urllib.parse
from collections import Counter, defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import recall_audit_il_lb_common as C

INDEP = ["gdelt", "mediacloud", "abuali-live", "websearch", "id-census", "cdx-section", "id-sample"]


def miss_reason(it):
    r = it["routes"]
    st = it["status"]
    u = urllib.parse.unquote(it["url"])
    if st == "in_corpus":
        return None
    if it["outlet"] == "abuali":
        return "telegram capture gap (no Wayback capture of the message)" if st == "not_in_manifest" else "in captured stream, dropped by device-word rule"
    if st == "not_in_manifest":
        if "/yokra" in u:
            return "enumeration: Yedioth print (yokra) IDs excluded by URL regex"
        if it["outlet"] == "ynet" and not re.search(r"ynet\.co\.il/news/article/", u):
            return "enumeration: outside /news/article/ prefix (section)"
        if it["outlet"] == "n12" and not re.search(r"mako\.co\.il/news-", u):
            return "enumeration: mako path outside news-* prefix"
        if "id-census" in r:
            return "enumeration: never captured by Wayback (found by outlet ID census)"
        return "enumeration: not captured by Wayback / not in manifest"
    if st == "in_candidates_dropped":
        return "triage: tagged/extracted but dropped"
    # in manifest, not tagged
    if "mtv-slugless" in r:
        return "triage: sitemap URL without slug, never title-checked"
    if "manifest-untitled" in r:
        return "triage: sweep title empty/blocked (Radware) - never checked"
    if it.get("nt", 0) > 0:
        return "triage: device word in headline, but sweep title/slug differed or term list missed it"
    return "triage: headline/slug has no device word (body-only mention)"


def main():
    country = sys.argv[1]
    base = C.DATA / country / "08-recall-audit" / "raw"
    items = json.loads((base / "items.json").read_text())
    summ = json.loads((base / "census-summary.json").read_text())
    outlets = list(summ["summary"].keys())
    ref = [it for it in items.values() if it.get("inwin") and it["final_class"] in ("central", "mention", "mention-mc")]
    print("## census recall")
    print("| outlet | corpus central | corpus mention | missing central | missing mention | extrapolated (control) | recall central | recall mention | recall all |")
    print("|---|---|---|---|---|---|---|---|---|")
    for o in outlets:
        s = summ["summary"][o]
        cc = s["corpus_window"].get("central", 0)
        cm = s["corpus_window"].get("mention", 0)
        mc = sum(v for k, v in s["missing_found"].items() if k.startswith("central"))
        mm = sum(v for k, v in s["missing_found"].items() if k.startswith("mention"))
        ex = (s.get("extrapolation") or {}).get("extrapolated_missing") or 0
        rc = cc / (cc + mc) if cc + mc else float("nan")
        rm = cm / (cm + mm) if cm + mm else float("nan")
        ra = (cc + cm) / (cc + cm + mc + mm + ex) if cc + cm + mc + mm + ex else float("nan")
        print(f"| {o} | {cc} | {cm} | {mc} | {mm} | {ex} | {rc:.0%} | {rm:.0%} | {ra:.0%} |")
    print("\n## route-specific recall (independent discovery routes; in-window, relevant)")
    print("| outlet | route | central n | central in corpus | mention n | mention in corpus |")
    print("|---|---|---|---|---|---|")
    for o in outlets:
        for rt in INDEP:
            sel = [it for it in ref if it["outlet"] == o and rt in it["routes"]]
            if not sel:
                continue
            c = [it for it in sel if it["final_class"] == "central"]
            m = [it for it in sel if it["final_class"] != "central"]
            print(f"| {o} | {rt} | {len(c)} | {sum(it['status']=='in_corpus' for it in c)} | {len(m)} | {sum(it['status']=='in_corpus' for it in m)} |")
    print("\n## miss reasons (reference items not in corpus)")
    mr = defaultdict(Counter)
    for it in ref:
        x = miss_reason(it)
        if x:
            mr[it["outlet"]][(x, "central" if it["final_class"] == "central" else "mention")] += 1
    for o in outlets:
        for (x, cl), v in sorted(mr[o].items(), key=lambda kv: -kv[1]):
            print(f"| {o} | {x} | {cl} | {v} |")
    print("\n## language split of missing (lbci/mtv)")
    for o in ("lbci", "mtv"):
        c = Counter()
        for it in ref:
            if it["outlet"] == o and it["status"] != "in_corpus":
                lang = "en" if re.search(r"[A-Za-z]{4,}", it["title"][:30]) and not re.search(r"[؀-ۿ]", it["title"][:30]) else "ar"
                c[lang] += 1
        print(o, dict(c))
    print("\n## extrapolation detail")
    print(json.dumps(summ["ext"], ensure_ascii=False, indent=0)[:3000])


if __name__ == "__main__":
    main()
