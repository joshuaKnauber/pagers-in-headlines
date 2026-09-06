#!/usr/bin/env python3
"""Build the Lebanon↔Israel comparison viz doc.

Computes the comparison payload from both corpus-v1.jsonl files (same
matched term families as the v1 comparison table) plus the MTV
displacement CSV, injects it into viz-template.html, writes
data/analysis/lebanon-israel-viz-v1.html (self-contained, file:// ready;
d3 from CDN).
"""
import csv, json
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# Matched per-language families — identical to lebanon-israel-comparison-v1.md
M = {
 "“the pagers exploded” — no actor": dict(ar=["انفجار", "انفجارات", "انفجرت"], he=["פיצוץ", "פיצוצים", "התפוצצ"], en=["explosion", "blast", "exploded"]),
 "“detonated” — actor named": dict(ar=["تفجير", "تفجيرات"], he=["פוצצו", "פיצצה", "פיצץ", "פוצץ"], en=["detonat"]),
 "an “operation”": dict(ar=["عملية أمنية", "العملية الإسرائيلية"], he=["מבצע"], en=["operation"]),
 "an “attack”": dict(ar=["هجوم", "الهجوم"], he=["מתקפה", "מתקפת"], en=["attack"]),
 "a “massacre” or “crime”": dict(ar=["عدوان", "العدوان", "مجزرة", "جريمة", "إرهاب", "ارهاب"], he=["טבח", "פשע מלחמה"], en=["massacre", "aggression", "war crime", "terror"]),
 "the dead are “terrorists”": dict(ar=[], he=["מחבל"], en=["terrorist"]),
 "the dead are “martyrs”": dict(ar=["شهيد", "شهداء", "استشهاد"], he=[], en=["martyr"]),
 "“according to foreign reports”": dict(ar=[], he=["דיווחים זרים", "פרסומים זרים", "גורמים זרים"], en=[]),
}
SPECTRUM_MEASURES = ["“detonated” — actor named", "an “operation”",
                     "the dead are “terrorists”", "the dead are “martyrs”"]
OUTLET_LABEL = {"lbci": "LBCI", "mtv": "MTV", "aljadeed": "Al Jadeed",
                "almanar": "Al-Manar", "nna": "NNA", "ynet": "Ynet",
                "n12": "N12", "kikar": "Kikar HaShabbat", "makan": "Makan 33",
                "abuali": "Abu Ali Express"}
MASS = {"lbci", "mtv", "aljadeed", "almanar", "ynet", "n12"}


def load(p):
    rs = [json.loads(l) for l in open(p, encoding="utf-8")]
    return [r for r in rs if r["deduplication"]["is_primary_record"]
            and r["extraction"]["relevance"] in ("strong", "related")]


def text(r):
    return ((r["content"]["headline"] or "") + " " + (r["content"]["body"] or "")[:6000]).lower()


def hit(r, fam):
    t, l = text(r), r["source"]["language"]
    keys = fam.get(l, []) + fam.get("en", []) if l in ("ar", "he") else fam.get("en", [])
    return any(k in t for k in keys)


def share(recs, fam):
    return round(100 * sum(hit(r, fam) for r in recs) / len(recs), 1) if recs else 0.0


def main():
    LB = load(ROOT / "lebanon" / "corpus-v1.jsonl")
    IL = load(ROOT / "israel" / "corpus-v1.jsonl")

    measures = [{"name": n, "lb": share(LB, f), "il": share(IL, f)} for n, f in M.items()]

    outlets = []
    for country, recs in [("Lebanon", LB), ("Israel", IL)]:
        byo = defaultdict(list)
        for r in recs:
            byo[r["source"]["page_publisher"]].append(r)
        for o, rs in byo.items():
            if len(rs) < 5:  # NNA n=2 — unusable for shares (smoke finding)
                continue
            outlets.append({"outlet": OUTLET_LABEL.get(o, o), "country": country,
                            "n": len(rs), "mass": o in MASS,
                            "values": {m: share(rs, M[m]) for m in SPECTRUM_MEASURES}})

    daycurve = []
    for country, recs in [("Lebanon", LB), ("Israel", IL)]:
        d = Counter(r["publication"]["time_slot"] for r in recs
                    if r["publication"]["time_slot"].startswith("day_"))
        tot = sum(d.values())
        daycurve.append({"country": country,
                         "days": [{"day": i, "pct": round(100 * d.get(f"day_{i}", 0) / tot, 1)}
                                  for i in range(8)]})

    disp = [{"date": r["date"], "share": float(r["pager_share_pct"]), "total": int(r["mtv_total_output"])}
            for r in csv.DictReader(open(ROOT / "lebanon" / "analysis" / "displacement-mtv.csv", encoding="utf-8"))
            if r["date"] <= "2024-10-10"]

    viz = {"generated": "2026-09-06", "n_lb": len(LB), "n_il": len(IL),
           "measures": measures, "outlets": outlets, "daycurve": daycurve,
           "displacement": disp, "spectrum_measures": SPECTRUM_MEASURES}

    tpl = (ROOT / "analysis" / "viz-template.html").read_text(encoding="utf-8")
    out = (tpl.replace("__DATA__", json.dumps(viz, ensure_ascii=False))
              .replace("__GENERATED__", viz["generated"]))
    (ROOT / "analysis" / "lebanon-israel-viz-v1.html").write_text(out, encoding="utf-8")
    print("wrote lebanon-israel-viz-v1.html |", len(LB), "LB /", len(IL), "IL records |",
          len(outlets), "outlets")


if __name__ == "__main__":
    main()
