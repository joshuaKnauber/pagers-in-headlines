#!/usr/bin/env python3
"""Normalize the Lebanon phase-1 candidate corpus into corpus-schema-v1-
aligned records.

In:  data/lebanon/05-extraction/candidates.jsonl (+ enumeration manifests, raw/)
Out: data/lebanon/06-corpus/corpus.jsonl        (normalized, primary+relevant only)
     data/lebanon/06-corpus/normalization-quality.csv (every input record's disposition)
"""
import csv, hashlib, json, re
from collections import Counter, defaultdict
from datetime import date, timedelta
from pathlib import Path

DATA = Path(__file__).resolve().parents[2] / "data" / "lebanon"
EVENT_DAY = date(2024, 9, 17)

WIRES = [
    ("Reuters", ["رويترز", "reuters"]),
    ("AFP", ["فرانس برس", "أ ف ب", "ا ف ب", "afp", "وكالة الصحافة الفرنسية"]),
    ("AP", ["أسوشيتد برس", "اسوشيتد برس", "associated press"]),
    ("NNA", ["الوكالة الوطنية للإعلام", "الوكالة الوطنية للاعلام", "national news agency"]),
]

LANG_AR = re.compile(r"[؀-ۿ]")


def detect_lang(title, body):
    text = ((title or "") + " " + (body or ""))[:2000]
    if not text.strip():
        return "und"
    ar = len(LANG_AR.findall(text)) / max(len(text), 1)
    return "ar" if ar > 0.15 else "en"


def almanar_date_fn():
    """Piecewise-linear ID->date from fresh-crawl day medians."""
    anchors = []
    rows = list(csv.DictReader(open(DATA / "04-enumeration" / "almanar-urls.csv", encoding="utf-8")))
    byday = defaultdict(list)
    for r in rows:
        m = re.search(r"/(\d{6,})/?$", r["url"])
        if m and r["first_capture"][:8].isdigit():
            byday[r["first_capture"][:8]].append(int(m.group(1)))
    for d, ids in sorted(byday.items()):
        ids = sorted(i for i in ids if i > 12_400_000)
        if len(ids) >= 15:  # fresh-crawl day
            anchors.append((ids[len(ids) // 2], date(int(d[:4]), int(d[4:6]), int(d[6:8]))))
    anchors.sort()

    def fn(aid):
        if not anchors or aid < 12_400_000:   # outside the Arabic-site modern band (e.g. english.almanar IDs)
            return None
        if aid <= anchors[0][0]:
            return anchors[0][1]
        for (i1, d1), (i2, d2) in zip(anchors, anchors[1:]):
            if i1 <= aid <= i2:
                frac = (aid - i1) / max(i2 - i1, 1)
                return d1 + timedelta(days=round(frac * (d2 - d1).days))
        return anchors[-1][1]
    return fn


def doc_type(rec, url_dec):
    if rec.get("doc_type_hint") == "live_ticker" or "مباشر" in url_dec or "/breaking-news/" in url_dec:
        return "live_ticker"
    w = rec["body_words"]
    if w < 40:
        return "brief"
    t = (rec.get("title") or "")
    if any(k in t for k in ("السيد نصرالله", "بيان", "كلمة")):
        return "statement"
    return "article"


def wire_credit(title, body):
    lead = ((title or "") + " " + (body or "")[:400]).lower()
    for name, keys in WIRES:
        for k in keys:
            if k in lead:
                return name
    return ""


def strip_boilerplate(recs):
    """Remove lines that recur across >=30% of an outlet's bodies (page
    furniture like live-ticker strips captured from the fetch-day page)."""
    byo = defaultdict(list)
    for r in recs:
        if r.get("body_text"):
            byo[r["outlet"]].append(r)
    for o, rs in byo.items():
        if len(rs) < 5:
            continue
        freq = Counter()
        for r in rs:
            for line in set(filter(None, (l.strip() for l in r["body_text"].split("\n")))):
                freq[line] += 1
        boiler = {l for l, c in freq.items() if c >= max(3, 0.3 * len(rs)) and len(l) > 15}
        for r in rs:
            kept = [l for l in r["body_text"].split("\n") if l.strip() not in boiler]
            nb = "\n".join(kept)
            if len(nb) < len(r["body_text"]):
                r["body_text"] = nb
                r["body_words"] = len(nb.split())
                r["boilerplate_stripped"] = True
    return recs


def main():
    manifest_dates = {}
    for outlet in ("mtv", "lbci"):
        for r in csv.DictReader(open(DATA / "04-enumeration" / f"{outlet}-urls.csv", encoding="utf-8")):
            if r.get("publication_date"):
                mm = re.search(r"/(\d{5,})(?:[/?]|$)", r["url"])
                if mm:
                    manifest_dates[(outlet, mm.group(1))] = (r["publication_date"], "sitemap-lastmod")
    manar_date = almanar_date_fn()

    recs = [json.loads(l) for l in open(DATA / "05-extraction/candidates.jsonl", encoding="utf-8")]
    recs = strip_boilerplate(recs)
    out, quality = [], []
    seen_hash = {}
    for rec in recs:
        disp = "included"
        if "duplicate_of" in rec:
            disp = "excluded:url-duplicate"
        elif rec["relevance"] not in ("strong", "related"):
            disp = f"excluded:{rec['relevance']}"
        if disp != "included":
            quality.append((rec["url"], disp, ""))
            continue

        url_dec = __import__("urllib.parse", fromlist=["unquote"]).unquote(rec["url"])
        m = re.search(r"/(\d{5,})(?:[/?]|$)", rec["url"])
        aid = m.group(1) if m else hashlib.sha256(rec["url"].encode()).hexdigest()[:10]
        pub, pub_src = rec.get("published_at") or "", "page-meta" if rec.get("published_at") else ""
        if not pub and (rec["outlet"], aid) in manifest_dates:
            pub, pub_src = manifest_dates[(rec["outlet"], aid)]
        if not pub and rec["outlet"] == "almanar" and m:
            d = manar_date(int(aid))
            if d:
                pub, pub_src = d.isoformat(), "id-interpolated"
        if not pub and rec.get("manifest_date"):
            pub, pub_src = rec["manifest_date"], "manifest"
        warn = [] if pub else ["date_missing"]

        body = rec.get("body_text") or ""
        bh = hashlib.sha256(body.encode()).hexdigest() if body else ""
        dup_primary = True
        exact_group = ""
        if bh and rec["body_words"] > 20:
            if bh in seen_hash:
                dup_primary = False
                exact_group = seen_hash[bh]
                warn.append("exact_body_duplicate")
            else:
                seen_hash[bh] = f"x{bh[:10]}"
                exact_group = seen_hash[bh]

        slot = ""
        if pub:
            try:
                dd = (date.fromisoformat(pub[:10]) - EVENT_DAY).days
                slot = ("pre_event" if dd < 0 else f"day_{dd}" if dd <= 7 else
                        "week_2" if dd <= 14 else "first_month" if dd <= 30 else "tail")
            except ValueError:
                warn.append("date_unparsed")

        out.append({
            "schema_version": "1.1.0-phase1",
            "document_id": f"lb_{rec['outlet']}_{aid}",
            "event_id": "lebanon_pager_attacks_2024",
            "source": {"page_publisher": rec["outlet"], "country_or_media_system": "Lebanon",
                       "language": detect_lang(rec.get("title"), body)},
            "publication": {"published_at": pub, "date_source": pub_src, "time_slot": slot,
                            "document_type": doc_type(rec, url_dec), "canonical_url": rec["url"]},
            "content": {"headline": rec.get("title"), "body": body,
                        "word_count": rec["body_words"], "body_sha256": bh},
            "provenance": {"credit": wire_credit(rec.get("title"), body),
                           "content_origin": "syndicated_or_adapted" if wire_credit(rec.get("title"), body) else "local_or_unspecified"},
            "capture": {"collection_route": rec["fetch_route"], "raw_path": rec.get("raw_path", "")},
            "extraction": {"method": rec.get("extract_method", "p-cluster"),
                           "relevance": rec["relevance"], "warnings": warn},
            "deduplication": {"exact_duplicate_cluster_id": exact_group, "is_primary_record": dup_primary},
        })
        quality.append((rec["url"], "included", ";".join(warn)))

    with open(DATA / "06-corpus/corpus.jsonl", "w", encoding="utf-8") as f:
        for r in out:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    with open(DATA / "06-corpus/normalization-quality.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["url", "disposition", "warnings"])
        w.writerows(quality)

    prim = [r for r in out if r["deduplication"]["is_primary_record"]]
    print("normalized:", len(out), "| primary:", len(prim))
    print("doc types:", Counter(r["publication"]["document_type"] for r in prim))
    print("languages:", Counter(r["source"]["language"] for r in prim))
    print("dated:", sum(1 for r in prim if r["publication"]["published_at"]), "| date sources:",
          Counter(r["publication"]["date_source"] for r in prim if r["publication"]["published_at"]))
    print("wire credits:", Counter(r["provenance"]["credit"] for r in prim if r["provenance"]["credit"]))
    print("time slots:", dict(sorted(Counter(r["publication"]["time_slot"] for r in prim if r["publication"]["time_slot"]).items())))


if __name__ == "__main__":
    main()
