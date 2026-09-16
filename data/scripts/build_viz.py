#!/usr/bin/env python3
"""Build the cross-country comparison viz doc (N countries).

Computes the payload from every existing data/<country>/corpus-v1.jsonl
(matched per-language term families) plus the MTV displacement CSV,
injects into viz-template.html → data/analysis/pager-coverage-viz.html.
Countries whose corpus file is missing are skipped automatically.
"""
import csv, json
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

COUNTRIES = [
    ("lebanon", "Lebanon", "🇱🇧", "#d0212a"),
    ("israel", "Israel", "🇮🇱", "#0038b8"),
    ("germany", "Germany", "🇩🇪", "#1a1a1a"),
    ("us", "United States", "🇺🇸", "#3c3b6e"),
]

# Matched per-language families. ar/he as frozen in the LB↔IL comparison;
# de/en added for Germany/US (en list applies to any non-native-language
# records too). Caveat: English "detonat" counts as agentive — English
# does not morphologically split agency the way Arabic/Hebrew/German do.
M = {
 "“the pagers exploded” — as if on their own": dict(
    ar=["انفجار", "انفجارات", "انفجرت"], he=["פיצוץ", "פיצוצים", "התפוצצ"],
    de=["explosion", "explodiert", "detonier"], en=["explosion", "blast", "exploded"]),
 "“somebody detonated the pagers”": dict(
    ar=["تفجير", "تفجيرات"], he=["פוצצו", "פיצצה", "פיצץ", "פוצץ"],
    de=["gezündet", "zur explosion gebracht", "sprengte", "gesprengt"], en=["detonat"]),
 "an “operation”": dict(
    ar=["عملية أمنية", "العملية الإسرائيلية"], he=["מבצע"],
    de=["operation"], en=["operation"]),
 "an “attack”": dict(
    ar=["هجوم", "الهجوم"], he=["מתקפה", "מתקפת"],
    de=["angriff", "attacke", "anschlag"], en=["attack"]),
 # de "verbrechen" alone and en bare "terror" dropped 2026-09-14: they
 # match routine Hezbollah descriptors, not condemnation framing
 "a “massacre” or “crime”": dict(
    ar=["عدوان", "العدوان", "مجزرة", "جريمة", "إرهاب", "ارهاب"], he=["טבח", "פשע מלחמה"],
    de=["massaker", "kriegsverbrechen"], en=["massacre", "aggression", "war crime", "terror attack on"]),
 "the dead are “terrorists”": dict(
    ar=[], he=["מחבל"], de=["terroristen"], en=["terrorist"]),
 "the dead are “martyrs”": dict(
    ar=["شهيد", "شهداء", "استشهاد"], he=[], de=["märtyrer"], en=["martyr"]),
 "“according to foreign reports”": dict(
    ar=[], he=["דיווחים זרים", "פרסומים זרים", "גורמים זרים"], de=[], en=[]),
}
SPECTRUM_MEASURES = ["“somebody detonated the pagers”", "an “operation”",
                     "the dead are “terrorists”", "the dead are “martyrs”"]
OUTLET_LABEL = {"lbci": "LBCI", "mtv": "MTV", "aljadeed": "Al Jadeed", "almanar": "Al-Manar",
                "nna": "NNA", "ynet": "Ynet", "n12": "N12", "kikar": "Kikar HaShabbat",
                "makan": "Makan 33", "abuali": "Abu Ali Express",
                "tagesschau": "Tagesschau", "zdfheute": "ZDFheute", "rtl": "RTL", "ntv": "ntv",
                "bild": "Bild", "spiegel": "Spiegel", "welt": "WELT", "tonline": "t-online",
                "rnd": "RND", "fox": "Fox News", "cnn": "CNN", "abc": "ABC", "cbs": "CBS",
                "nbc": "NBC", "nyt": "NYT", "wapo": "WaPo", "yahoo": "Yahoo", "usatoday": "USA Today",
                "ap": "AP", "reuters": "Reuters"}
MASS = {"lbci", "mtv", "aljadeed", "almanar", "ynet", "n12", "tagesschau", "zdfheute", "rtl",
        "ntv", "bild", "spiegel", "welt", "tonline", "fox", "cnn", "abc", "cbs", "nbc",
        "nyt", "wapo", "yahoo", "usatoday"}


def load(p):
    rs = [json.loads(l) for l in open(p, encoding="utf-8")]
    return [r for r in rs if r["deduplication"]["is_primary_record"]
            and r["extraction"]["relevance"] in ("strong", "related")]


def text(r):
    # press reviews are pasted newspaper digests — their bodies are other
    # outlets' voices, so only the headline counts toward shares
    if r["publication"]["document_type"] == "press_review":
        return (r["content"]["headline"] or "").lower()
    return ((r["content"]["headline"] or "") + " " + (r["content"]["body"] or "")[:6000]).lower()


def hit(r, fam):
    t, l = text(r), r["source"]["language"]
    keys = fam.get(l, []) + fam.get("en", []) if l != "en" else fam.get("en", [])
    return any(k in t for k in keys)


def share(recs, fam):
    return round(100 * sum(hit(r, fam) for r in recs) / len(recs), 1) if recs else 0.0


def main():
    countries = []
    for key, label, flag, color in COUNTRIES:
        p = ROOT / key / "corpus-v1.jsonl"
        if not p.exists():
            print("skip (no corpus):", key)
            continue
        recs = load(p)
        d = Counter(r["publication"]["time_slot"] for r in recs
                    if r["publication"]["time_slot"].startswith("day_"))
        tot = sum(d.values()) or 1
        outlets = []
        byo = defaultdict(list)
        for r in recs:
            byo[r["source"]["page_publisher"]].append(r)
        for o, rs in byo.items():
            if len(rs) < 5:
                continue
            outlets.append({"outlet": OUTLET_LABEL.get(o, o), "n": len(rs), "mass": o in MASS,
                            "values": {m: share(rs, M[m]) for m in SPECTRUM_MEASURES}})
        countries.append({
            "key": key, "label": label, "flag": flag, "color": color, "n": len(recs),
            "measures": {name: share(recs, fam) for name, fam in M.items()},
            "days": [{"day": i, "pct": round(100 * d.get(f"day_{i}", 0) / tot, 1)} for i in range(8)],
            "outlets": outlets})
        print(f"{label}: {len(recs)} records, {len(outlets)} outlets")

    disp = [{"date": r["date"], "share": float(r["pager_share_pct"]), "total": int(r["mtv_total_output"])}
            for r in csv.DictReader(open(ROOT / "lebanon" / "analysis" / "displacement-mtv.csv", encoding="utf-8"))
            if r["date"] <= "2024-10-10"]

    viz = {"generated": "2026-09-14", "countries": countries,
           "measure_names": list(M.keys()), "spectrum_measures": SPECTRUM_MEASURES,
           "displacement": disp}
    tpl = (ROOT / "analysis" / "viz-template.html").read_text(encoding="utf-8")
    out = (tpl.replace("__DATA__", json.dumps(viz, ensure_ascii=False))
              .replace("__GENERATED__", viz["generated"]))
    (ROOT / "analysis" / "pager-coverage-viz.html").write_text(out, encoding="utf-8")
    print("wrote pager-coverage-viz.html |", ", ".join(f"{c['label']} {c['n']}" for c in countries))


if __name__ == "__main__":
    main()
