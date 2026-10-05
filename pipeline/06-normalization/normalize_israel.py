#!/usr/bin/env python3
"""Normalize Israel candidates + Abu Ali messages into 06-corpus/corpus.jsonl."""
import csv, hashlib, json, re
from collections import Counter, defaultdict
from datetime import date
from pathlib import Path

DATA = Path(__file__).resolve().parents[2] / "data" / "israel"
EVENT_DAY = date(2024, 9, 17)

# v1.1 review overrides: event-prompted but not event coverage (anecdote,
# Raisi speculation, cartoon-reaction story) — downgrade strong→related
RELEVANCE_OVERRIDES = {
    "il_kikar_361888163b": "related",
    "il_kikar_4e84dd272c": "related",
    "il_makan_c9d393a825": "related",
}
AR = re.compile(r"[؀-ۿ]"); HE = re.compile(r"[א-ת]")


def lang(text):
    t = (text or "")[:2000]
    if not t.strip(): return "und"
    a, h = len(AR.findall(t)), len(HE.findall(t))
    if h > a and h > 5: return "he"
    if a > 5: return "ar"
    return "en"


def slot(pub):
    try:
        d = (date.fromisoformat(pub[:10]) - EVENT_DAY).days
    except Exception:
        return ""
    if d < 0: return "pre_event"
    if d <= 7: return f"day_{d}"
    if d <= 14: return "week_2"
    if d <= 30: return "first_month"
    return "tail"


def wire(t):
    lead = (t or "")[:500]
    for name, keys in [("Reuters", ["רויטרס", "reuters", "رويترز"]), ("AFP", ["אי.אף.פי", "afp"]),
                       ("AP", ["איי.פי", "associated press"])]:
        if any(k in lead.lower() for k in keys): return name
    return ""


def strip_boiler(recs):
    byo = defaultdict(list)
    for r in recs:
        if r.get("body_text"): byo[r["outlet"]].append(r)
    for o, rs in byo.items():
        if len(rs) < 5: continue
        freq = Counter()
        for r in rs:
            for l in set(filter(None, (x.strip() for x in r["body_text"].split("\n")))):
                freq[l] += 1
        boiler = {l for l, c in freq.items() if c >= max(3, 0.3 * len(rs)) and len(l) > 15}
        for r in rs:
            nb = "\n".join(l for l in r["body_text"].split("\n") if l.strip() not in boiler)
            if len(nb) < len(r["body_text"]):
                r["body_text"], r["body_words"] = nb, len(nb.split())
    return recs


def main():
    recs = [json.loads(l) for l in open(DATA / "05-extraction/candidates.jsonl", encoding="utf-8")]
    recs = strip_boiler(recs)
    out, seen = [], {}
    dropped = Counter()
    for r in recs:
        if r["relevance"] not in ("strong", "related"):
            dropped[r["relevance"]] += 1; continue
        pub = r.get("published_at", "")
        if pub and not ("2024-09-01" <= pub[:10] <= "2024-10-31"):
            dropped["out-of-window"] += 1; continue
        body = r.get("body_text") or ""
        bh = hashlib.sha256(body.encode()).hexdigest() if body else ""
        primary, grp = True, ""
        if bh and r["body_words"] > 20:
            if bh in seen: primary, grp = False, seen[bh]
            else: grp = seen.setdefault(bh, f"x{bh[:10]}")
        title = r.get("title") or ""
        dt = ("flash_or_lead" if r["outlet"] == "ynet" and r["body_words"] < 90
              else "article")
        out.append({"schema_version": "1.1.0-phase1",
            "document_id": f"il_{r['outlet']}_{hashlib.sha256(r['url'].encode()).hexdigest()[:10]}",
            "event_id": "lebanon_pager_attacks_2024",
            "source": {"page_publisher": r["outlet"], "country_or_media_system": "Israel",
                       "language": lang(title + " " + body)},
            "publication": {"published_at": pub, "date_source": r.get("date_source", ""),
                            "time_slot": slot(pub), "document_type": dt, "canonical_url": r["url"]},
            "content": {"headline": title, "body": body, "word_count": r["body_words"], "body_sha256": bh},
            "provenance": {"credit": wire(title + " " + body),
                           "content_origin": "syndicated_or_adapted" if wire(title + " " + body) else "local_or_unspecified"},
            "capture": {"collection_route": r["fetch_route"], "raw_path": r.get("raw_path", "")},
            "extraction": {"method": r.get("extract_method", ""), "relevance": r["relevance"], "warnings": [] if pub else ["date_missing"]},
            "deduplication": {"exact_duplicate_cluster_id": grp, "is_primary_record": primary}})
    # Abu Ali tagged messages as telegram_post records (body-hash dedup:
    # overlapping rolling-page captures can repeat a message)
    ab_seen = {}
    for m in csv.DictReader(open(DATA / "04-enumeration" / "abuali-messages.csv", encoding="utf-8")):
        if not m["relevance"]: continue
        abh = hashlib.sha256(m["text"].encode()).hexdigest()
        ab_primary, ab_grp = True, ""
        if abh in ab_seen: ab_primary, ab_grp = False, ab_seen[abh]
        else: ab_grp = ab_seen.setdefault(abh, f"x{abh[:10]}")
        out.append({"schema_version": "1.1.0-phase1",
            "document_id": f"il_abuali_{m['post_id']}", "event_id": "lebanon_pager_attacks_2024",
            "source": {"page_publisher": "abuali", "country_or_media_system": "Israel", "language": lang(m["text"])},
            "publication": {"published_at": m["datetime"][:10], "date_source": "telegram-ts",
                            "time_slot": slot(m["datetime"]), "document_type": "telegram_post",
                            "canonical_url": f"https://t.me/abualiexpress/{m['post_id']}"},
            "content": {"headline": m["text"][:120], "body": m["text"], "word_count": len(m["text"].split()),
                        "body_sha256": hashlib.sha256(m["text"].encode()).hexdigest()},
            "provenance": {"credit": "", "content_origin": "local_or_unspecified"},
            "capture": {"collection_route": "wayback-capture-stream", "raw_path": ""},
            "extraction": {"method": "telegram-capture", "relevance": m["relevance"], "warnings": []},
            "deduplication": {"exact_duplicate_cluster_id": ab_grp, "is_primary_record": ab_primary}})
    # apply review relevance overrides
    for r in out:
        if r["document_id"] in RELEVANCE_OVERRIDES:
            r["extraction"]["relevance"] = RELEVANCE_OVERRIDES[r["document_id"]]
    with open(DATA / "06-corpus/corpus.jsonl", "w", encoding="utf-8") as f:
        for r in out: f.write(json.dumps(r, ensure_ascii=False) + "\n")
    prim = [r for r in out if r["deduplication"]["is_primary_record"]]
    print("normalized:", len(out), "| primary:", len(prim), "| dropped:", dict(dropped))
    print("outlets:", Counter(r["source"]["page_publisher"] for r in prim))
    print("doc types:", Counter(r["publication"]["document_type"] for r in prim))
    print("languages:", Counter(r["source"]["language"] for r in prim))
    print("slots:", dict(sorted(Counter(r["publication"]["time_slot"] for r in prim if r["publication"]["time_slot"]).items())))


if __name__ == "__main__":
    main()
