#!/usr/bin/env python3
"""Normalize Germany/US candidates into 06-corpus/corpus.jsonl. Usage: normalize_de_us.py <germany|us>

Same schema/rules as Lebanon/Israel plus the accumulated QC safeguards:
- per-outlet boilerplate line strip (line frequency >= 30%)
- per-outlet auto-LCP strip (Al Jadeed lesson: if >=60% of an outlet's
  bodies share a long common prefix, it is chrome — cut it)
- exact-body dedup, window filter, flash_or_lead typing, wire credit.
"""
import hashlib, json, re, sys
from collections import Counter, defaultdict
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2] / "data"
EVENT_DAY = date(2024, 9, 17)
COUNTRY_LABEL = {"germany": "Germany", "us": "United States"}

WIRES = [("dpa", ["(dpa)", "von dpa", "dpa/", "/dpa", "quelle: dpa"]),
         ("Reuters", ["reuters"]),
         ("AP", ["(ap)", "associated press", "ap news"]),
         ("AFP", ["(afp)", "afp/"])]


def lang(text, country):
    t = (text or "")[:2000].lower()
    if country == "us":
        return "en"
    de_hits = sum(t.count(w) for w in [" der ", " und ", " nicht ", " eine ", " mit "])
    en_hits = sum(t.count(w) for w in [" the ", " and ", " with ", " that "])
    return "de" if de_hits >= en_hits else "en"


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


def wire(text):
    lead = (text or "")[:500].lower()
    for name, keys in WIRES:
        if any(k in lead for k in keys):
            return name
    return ""


def strip_boiler(recs):
    byo = defaultdict(list)
    for r in recs:
        if r.get("body_text"):
            byo[r["outlet"]].append(r)
    for o, rs in byo.items():
        if len(rs) < 5:
            continue
        # (a) frequent-line strip
        freq = Counter()
        for r in rs:
            for l in set(filter(None, (x.strip() for x in r["body_text"].split("\n")))):
                freq[l] += 1
        boiler = {l for l, c in freq.items() if c >= max(3, 0.3 * len(rs)) and len(l) > 15}
        for r in rs:
            nb = "\n".join(l for l in r["body_text"].split("\n") if l.strip() not in boiler)
            r["body_text"] = nb
        # (b) auto-LCP strip: long shared prefix across most bodies = chrome
        bodies = [r["body_text"] for r in rs if len(r["body_text"]) > 200]
        if len(bodies) >= 5:
            import os
            sample = sorted(bodies)[:max(5, int(0.6 * len(bodies)))]
            lcp = os.path.commonprefix(sample)
            if len(lcp) > 50:
                cut = len(lcp)
                n = 0
                for r in rs:
                    if r["body_text"].startswith(lcp):
                        r["body_text"] = r["body_text"][cut:].lstrip()
                        n += 1
                print(f"  LCP-strip {o}: {cut} chars from {n} bodies")
        # (c) known share-bar/template prefixes (bodies are single-line —
        # line-frequency can't see them)
        SCRUB = ["facebook x whatsapp e-mail link kopieren artikel drucken teilen folgen",
                 "artikel teilen", "eilmeldung — __proto_headline__ eilmeldung — __proto_headline__",
                 "merkliste hinzufügen", "democracy dies in darkness"]
        for r in rs:
            low = r["body_text"].lower()
            for s in SCRUB:
                if low.startswith(s):
                    r["body_text"] = r["body_text"][len(s):].lstrip()
                    low = r["body_text"].lower()
        # (d) v1.1 review round: outlet-specific chrome surgery
        for r in rs:
            b = r["body_text"]
            if o == "yahoo" and b.lower().startswith("return to homepage"):
                # fetch-day nav ticker prefix (Al Jadeed trap): article
                # restarts at the record's own headline if present
                t = (r.get("title") or "")[:60]
                i = b.find(t[:40]) if len(t) > 20 else -1
                b = b[i:] if i > 200 else b[b.lower().find("min read") + 8:] if "min read" in b[:1500].lower() else b
            if o == "reuters":
                low = b.lower()
                i = low.rfind("purchase licensing rights", 0, 900)
                if i >= 0:
                    b = b[i + len("purchase licensing rights"):].lstrip(" ,.")
                for marker in ("Read Next", "Suggested Topics", "More from Reuters"):
                    j = b.find(marker)
                    if j > len(b) * 0.4:
                        b = b[:j]
            if o == "wapo":
                j = b.rfind("Read more")
                if j > len(b) * 0.7:
                    b = b[:j]
            if o == "spiegel":
                for marker in ("Dialog schließen", "Mehr zum Thema"):
                    j = b.find(marker)
                    if j > len(b) * 0.5:
                        b = b[:j]
            r["body_text"] = b
        for r in rs:
            r["body_words"] = len(r["body_text"].split())
    return recs


def main():
    country = sys.argv[1]
    D = ROOT / country
    recs = [json.loads(l) for l in open(D / "05-extraction/candidates.jsonl", encoding="utf-8")]
    recs = strip_boiler(recs)
    out, seen = [], {}
    dropped = Counter()
    STRONG_TERMS = ["pager", "piepser", "funkger", "walkie", "gold apollo", "gold-apollo", "beeper", "icom"]
    for r in recs:
        # v1.1 review round: reject archived Wayback landing pages
        if (r.get("title") in ("Wayback Machine", "") and
                r.get("body_text", "").lower().startswith("keep the news in the wayback")):
            dropped["archive-landing-page"] += 1
            continue
        # centrality rule: 'strong' requires an event term in title or
        # the first 1500 chars — incidental late mentions demote to related
        if r["relevance"] == "strong":
            head = ((r.get("title") or "") + " " + (r.get("body_text") or "")[:1500]).lower()
            if not any(k in head for k in STRONG_TERMS):
                r["relevance"] = "related"
        if r["relevance"] not in ("strong", "related"):
            dropped[r["relevance"]] += 1
            continue
        pub = r.get("published_at", "")
        if pub and not ("2024-09-01" <= pub[:10] <= "2024-10-31"):
            dropped["out-of-window"] += 1
            continue
        body = r.get("body_text") or ""
        bh = hashlib.sha256(body.encode()).hexdigest() if body else ""
        primary, grp = True, ""
        if bh and r["body_words"] > 20:
            if bh in seen:
                primary, grp = False, seen[bh]
            else:
                grp = seen.setdefault(bh, f"x{bh[:10]}")
        title = r.get("title") or ""
        dt = "flash_or_lead" if r["body_words"] < 90 else "article"
        wc = wire(title + " " + body)
        out.append({"schema_version": "1.1.0-phase1",
            "document_id": f"{country[:2]}_{r['outlet']}_{hashlib.sha256(r['url'].encode()).hexdigest()[:10]}",
            "event_id": "lebanon_pager_attacks_2024",
            "source": {"page_publisher": r["outlet"], "country_or_media_system": COUNTRY_LABEL[country],
                       "language": lang(title + " " + body, country)},
            "publication": {"published_at": pub, "date_source": r.get("date_source", ""),
                            "time_slot": slot(pub), "document_type": dt, "canonical_url": r["url"]},
            "content": {"headline": title, "body": body, "word_count": r["body_words"], "body_sha256": bh},
            "provenance": {"credit": wc,
                           "content_origin": "syndicated_or_adapted" if wc else "local_or_unspecified"},
            "capture": {"collection_route": r["fetch_route"], "raw_path": r.get("raw_path", "")},
            "extraction": {"method": r.get("extract_method", ""), "relevance": r["relevance"],
                           "warnings": [] if pub else ["date_missing"]},
            "deduplication": {"exact_duplicate_cluster_id": grp, "is_primary_record": primary}})
    with open(D / "06-corpus/corpus.jsonl", "w", encoding="utf-8") as f:
        for r in out:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    prim = [r for r in out if r["deduplication"]["is_primary_record"]]
    print("normalized:", len(out), "| primary:", len(prim), "| dropped:", dict(dropped))
    print("outlets:", Counter(r["source"]["page_publisher"] for r in prim))
    print("doc types:", Counter(r["publication"]["document_type"] for r in prim))
    print("slots:", dict(sorted(Counter(r["publication"]["time_slot"] for r in prim if r["publication"]["time_slot"]).items())))


if __name__ == "__main__":
    main()
