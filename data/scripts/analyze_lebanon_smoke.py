#!/usr/bin/env python3
"""Lebanon smoke-test analysis over corpus-v1.jsonl.

Measures (spec):
 A. Two-wave timeline: relevant records per outlet per day (event window).
 B. Displacement: pager-story share of MTV's TOTAL dated output per day
    (MTV has a complete sitemap publication denominator).
 C. Framing vocabulary per outlet (headline+body presence shares):
    - actor naming: plain "Israel" vs enemy/Zionist register
    - event naming: intransitive explosion vs transitive detonation
      (Arabic morphology encodes agency), aggression, attack, massacre,
      crime/terror
    - casualty register: martyr vs neutral killed/victim
 D. Outlet-equal vs reach-weighted vocabulary shares (census tiers).
 E. Wire vs local: vocabulary differences for Reuters/AFP-credited records.
 F. Day-0/1 caution: attribution (any Israel/enemy mention) by day.
Units: record-level presence; tickers/briefs analyzed on their full stored
text (which is headline-dominated) - genre noted, not mixed silently.
"""
import json, re
from collections import Counter, defaultdict
from pathlib import Path
import csv

DATA = Path(__file__).resolve().parent.parent / "lebanon"

FAM = {
 "israel_plain": ["إسرائيل","اسرائيل","الإسرائيلي","الاسرائيلي","الإسرائيلية","الاسرائيلية","israel"],
 "enemy_register": ["العدو","للعدو","الصهيوني","الصهيونية","صهيوني","zionist","enemy"],
 "explosion_intrans": ["انفجار","انفجارات","انفجرت","انفجر","explosion","blast","exploded"],
 "detonation_trans": ["تفجير","تفجيرات","detonat","bombing of"],
 "aggression": ["عدوان","العدوان","اعتداء","الاعتداء","aggression"],
 "attack": ["هجوم","الهجوم","هجمات","attack"],
 "massacre": ["مجزرة","مجازر","massacre"],
 "crime_terror": ["جريمة","إجرام","اجرام","إرهاب","ارهاب","إرهابية","ارهابية","terror","crime"],
 "operation": ["عملية أمنية","العملية الإسرائيلية","العملية الاسرائيلية","operation"],
 "martyr": ["شهيد","شهداء","استشهاد","استشهد","martyr"],
 "casualty_neutral": ["قتيل","قتلى","ضحية","ضحايا","وفيات","killed","victim","dead","casualt"],
}
TIERS = {"lbci": 4, "mtv": 4, "aljadeed": 4, "almanar": 4, "nna": 1}  # census: 4 mass + context


def text_of(r):
    return ((r["content"]["headline"] or "") + " \n " + (r["content"]["body"] or "")).lower()


def hits(t, fam):
    return any(k.lower() in t for k in FAM[fam])


def main():
    recs = [json.loads(l) for l in open(DATA / "corpus-v1.jsonl", encoding="utf-8")]
    recs = [r for r in recs if r["deduplication"]["is_primary_record"]]
    outdir = DATA / "analysis"
    outdir.mkdir(exist_ok=True)

    # A. timeline per outlet/day
    tl = defaultdict(Counter)
    for r in recs:
        d = r["publication"]["published_at"][:10]
        if d:
            tl[r["source"]["page_publisher"]][d] += 1
    with open(outdir / "timeline-outlet-day.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f); w.writerow(["outlet", "date", "records"])
        for o, days in tl.items():
            for d, n in sorted(days.items()):
                w.writerow([o, d, n])

    # B. displacement vs MTV total output
    mtv_total = Counter()
    for r in csv.DictReader(open(DATA / "enumeration" / "mtv-urls.csv", encoding="utf-8")):
        if r.get("publication_date"):
            mtv_total[r["publication_date"][:10]] += 1
    with open(outdir / "displacement-mtv.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f); w.writerow(["date", "mtv_total_output", "mtv_pager_records", "pager_share_pct"])
        for d in sorted(mtv_total):
            if "2024-09-14" <= d <= "2024-10-17":
                p = tl["mtv"].get(d, 0)
                w.writerow([d, mtv_total[d], p, round(100 * p / mtv_total[d], 2)])

    # C. vocabulary per outlet (+ genre split)
    vocab = defaultdict(lambda: defaultdict(int))
    denom = Counter()
    for r in recs:
        o = r["source"]["page_publisher"]
        t = text_of(r)
        denom[o] += 1
        for fam in FAM:
            if hits(t, fam):
                vocab[o][fam] += 1
    with open(outdir / "vocabulary-outlet.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f); w.writerow(["outlet", "n"] + list(FAM))
        for o in denom:
            w.writerow([o, denom[o]] + [round(100 * vocab[o][fam] / denom[o], 1) for fam in FAM])

    # D. outlet-equal vs reach-weighted shares
    def agg(weighted):
        num, den = Counter(), 0.0
        for o in denom:
            wgt = TIERS.get(o, 1) if weighted else 1
            den += wgt
            for fam in FAM:
                num[fam] += wgt * vocab[o][fam] / denom[o]
        return {fam: round(100 * num[fam] / den, 1) for fam in FAM}
    eq, rw = agg(False), agg(True)

    # E. wire vs local
    wire_v, wire_n = defaultdict(int), Counter()
    for r in recs:
        grp = "wire" if r["provenance"]["credit"] in ("Reuters", "AFP", "AP") else "local"
        wire_n[grp] += 1
        t = text_of(r)
        for fam in FAM:
            if hits(t, fam):
                wire_v[(grp, fam)] += 1

    # F. attribution by day
    att = defaultdict(lambda: [0, 0])
    for r in recs:
        slot = r["publication"]["time_slot"]
        if slot.startswith("day_") and int(slot[4:]) <= 4:
            t = text_of(r)
            att[slot][1] += 1
            if hits(t, "israel_plain") or hits(t, "enemy_register"):
                att[slot][0] += 1

    # ---- report ----
    rep = ["# Lebanon smoke-test analysis (raw outputs)\n"]
    rep.append("## A. Records per outlet per day (top days)\n")
    for o, days in tl.items():
        top = sorted(days.items())[:12]
        rep.append(f"- **{o}**: " + ", ".join(f"{d[5:]}:{n}" for d, n in top))
    rep.append("\n## C. Vocabulary shares per outlet (% of records containing family)\n")
    hdr = "| outlet | n | " + " | ".join(FAM) + " |"
    rep.append(hdr); rep.append("|" + "---|" * (len(FAM) + 2))
    for o in ["lbci", "mtv", "aljadeed", "almanar", "nna"]:
        if o in denom:
            rep.append(f"| {o} | {denom[o]} | " + " | ".join(str(round(100 * vocab[o][f] / denom[o], 1)) for f in FAM) + " |")
    rep.append("\n## D. Outlet-equal vs reach-weighted (Lebanon overall, %)\n")
    rep.append("| family | outlet-equal | reach-weighted |"); rep.append("|---|---|---|")
    for fam in FAM:
        rep.append(f"| {fam} | {eq[fam]} | {rw[fam]} |")
    rep.append("\n## E. Wire vs local (%)\n")
    rep.append("| family | wire (n=%d) | local (n=%d) |" % (wire_n["wire"], wire_n["local"]))
    rep.append("|---|---|---|")
    for fam in FAM:
        a = 100 * wire_v[("wire", fam)] / max(wire_n["wire"], 1)
        b = 100 * wire_v[("local", fam)] / max(wire_n["local"], 1)
        rep.append(f"| {fam} | {a:.1f} | {b:.1f} |")
    rep.append("\n## F. Any Israel/enemy attribution by day\n")
    for slot in sorted(att):
        h, n = att[slot]
        rep.append(f"- {slot}: {h}/{n} = {100*h/n:.0f}%")
    (outdir / "smoke-raw.md").write_text("\n".join(rep), encoding="utf-8")
    print("\n".join(rep))


if __name__ == "__main__":
    main()
