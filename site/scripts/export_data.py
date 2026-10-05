#!/usr/bin/env python3
"""Export site data: data/ -> site/src/data/reader.json.

Prototype for the reader view. Claim matches are PROVISIONAL until claims are coded
per article (step 9): a match is either a catalogue seed example (`seed`, read by hand)
or a literal hit of one of the claim's detection hints (`hint`, unreviewed and noisy:
hints are cue phrases, not claim detectors).

Run: python3 site/scripts/export_data.py
"""
import csv, json, re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "data"
OUT = ROOT / "site" / "src" / "data" / "reader.json"
WINDOW = ("2024-09-17", "2024-10-17")

COUNTRIES = [("lebanon", "Lebanon"), ("israel", "Israel"), ("germany", "Germany"), ("us", "United States")]
OUTLETS = {  # id: display name, in display order per country
    "lebanon": {"lbci": "LBCI", "mtv": "MTV", "aljadeed": "Al Jadeed", "almanar": "Al-Manar", "nna": "NNA"},
    "israel": {"ynet": "Ynet", "n12": "N12", "kikar": "Kikar HaShabbat", "makan": "Makan", "abuali": "Abu Ali Express"},
    "germany": {"tagesschau": "Tagesschau", "zdfheute": "ZDFheute", "rtl": "RTL", "ntv": "ntv", "bild": "Bild",
                "spiegel": "Der Spiegel", "welt": "WELT", "tonline": "t-online", "rnd": "RND"},
    "us": {"fox": "Fox News", "cnn": "CNN", "abc": "ABC News", "cbs": "CBS News", "nbc": "NBC News",
           "nyt": "New York Times", "wapo": "Washington Post", "yahoo": "Yahoo News", "usatoday": "USA Today",
           "ap": "AP", "reuters": "Reuters"},
}
# Recall Sep 17-24 from the recall audits (census recall for LB/IL, reference-set recall for DE/US).
# None = not measurable. See data/cross-country/08-recall-audit-summary.md.
RECALL_LB_IL = {"lbci": 0.45, "mtv": 0.33, "aljadeed": 0.43, "almanar": 0.43, "nna": None,
                "ynet": 0.40, "n12": 0.05, "kikar": 0.38, "makan": None, "abuali": 0.15}
RECALL_NOTE = {"makan": "no independent check", "nna": "no reference", "reuters": "not auditable",
               "wapo": "too few independent items", "yahoo": "mostly syndicated copy", "n12": "extrapolated",
               "zdfheute": "small reference (11)", "rtl": "small reference (8)"}

AR_DIG = str.maketrans("٠١٢٣٤٥٦٧٨٩", "0123456789")


def norm(s):
    s = (s or "").translate(AR_DIG).lower()
    s = re.sub(r"(?<=\d)[,.](?=\d{3})", "", s)
    s = re.sub("[ً-ْـ]", "", s)
    for a, b in (("أ", "ا"), ("إ", "ا"), ("آ", "ا"), ("ة", "ه"), ("ى", "ي")):
        s = s.replace(a, b)
    s = re.sub(r"[\"“”„«»״׳']", "", s)
    return " ".join(s.split())


def hints_of(claim):
    out = []
    for hs in claim["detection_hints"].values():
        for h in hs:
            alts = [h] if "/" not in h else [re.sub(r"(\S+)/(\S+)", r"\1", h), re.sub(r"(\S+)/(\S+)", r"\2", h)]
            out += [n for n in map(norm, alts) if len(n) >= 8]
    return out


def salience(hints, headline, lead, body):
    for zone, text in (("headline", headline), ("lead", lead), ("body", body)):
        if any(h in text for h in hints):
            return zone
    return None


def recall_for(country, outlet):
    if country in ("lebanon", "israel"):
        return RECALL_LB_IL.get(outlet)
    p = DATA / country / "08-recall-audit" / "raw" / "recall-table.csv"
    for r in csv.DictReader(open(p, encoding="utf-8")):
        if r["outlet"] == outlet:
            if outlet in ("wapo", "reuters"):
                return None
            return float(r["recall"]) if r["recall"] else None
    return None


def archive_url(rec):
    route = rec["capture"]["collection_route"] or ""
    url = rec["publication"]["canonical_url"]
    if url.startswith("https://t.me/"):
        return ""
    m = re.search(r"(\d{14})", route)
    return f"https://web.archive.org/web/{m.group(1) if m else '2024'}/{url}"


def main():
    claims = [json.loads(l) for l in open(DATA / "cross-country/09-claims/claim-catalogue.jsonl", encoding="utf-8")]
    hints = {c["claim_id"]: hints_of(c) for c in claims}
    seeds = {}
    for c in claims:
        for s in c["corpus_seed_examples"]:
            seeds.setdefault(s, []).append(c["claim_id"])

    outlets, articles = [], []
    for country, _ in COUNTRIES:
        for oid, name in OUTLETS[country].items():
            outlets.append({"id": oid, "name": name, "country": country, "recall": recall_for(country, oid),
                            "recall_note": RECALL_NOTE.get(oid, "")})
        for line in open(DATA / country / "06-corpus" / "corpus.jsonl", encoding="utf-8"):
            r = json.loads(line)
            p = r["publication"]
            if not r["deduplication"]["is_primary_record"] or r["extraction"]["relevance"] == "context":
                continue
            if not p["published_at"] or not (WINDOW[0] <= p["published_at"][:10] <= WINDOW[1]):
                continue
            h, b = norm(r["content"]["headline"]), norm(r["content"]["body"])
            matched = []
            for c in claims:
                cid = c["claim_id"]
                sal = salience(hints[cid], h, b[:400], b)
                is_seed = r["document_id"] in seeds and cid in seeds[r["document_id"]]
                if sal or is_seed:
                    matched.append([cid, sal or "body", "seed" if is_seed else "hint"])
            articles.append({"id": r["document_id"], "outlet": r["source"]["page_publisher"], "country": country,
                             "date": p["published_at"][:10], "time": (p.get("published_time") or "")[11:16],
                             "type": p["document_type"], "lang": r["source"]["language"],
                             "headline": " ".join(r["content"]["headline"].split())[:300],
                             "words": r["content"]["word_count"], "url": p["canonical_url"],
                             "archive": archive_url(r), "claims": matched})
    articles.sort(key=lambda a: (a["date"], a["time"]))
    out = {"window": WINDOW, "countries": [{"id": c, "name": n} for c, n in COUNTRIES], "outlets": outlets,
           "claims": [{k: c[k] for k in ("claim_id", "statement_en", "category", "status", "pilot", "first_public")}
                      for c in claims],
           "articles": articles}
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(out, ensure_ascii=False), encoding="utf-8")
    n_seed = sum(1 for a in articles for m in a["claims"] if m[2] == "seed")
    n_hint = sum(1 for a in articles for m in a["claims"] if m[2] == "hint")
    print(f"wrote {OUT.relative_to(ROOT)}: {len(articles)} articles, {len(outlets)} outlets, "
          f"{len(claims)} claims, {n_seed} seed + {n_hint} hint matches")


if __name__ == "__main__":
    main()
