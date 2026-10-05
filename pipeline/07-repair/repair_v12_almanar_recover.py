#!/usr/bin/env python3
"""Al-Manar v1.2 recovery (deep-dive review fix).

1. Re-date all existing Al-Manar corpus records from the article-meta
   date block in their raw captures (real page dates; replaces
   id-interpolated ±1-day dates).
2. Fetch the 21 untagged day-0/1 items the title sweep missed
   (Hezbollah statement series, health-minister toll, martyr notices)
   from archive.almanar.com.lb, extract, and append as new records.
3. Tag those rows in enumeration/almanar-titles.csv.
"""
import csv, hashlib, html as htmllib, json, re, subprocess, sys, time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2] / "data"
LB = ROOT / "lebanon"
DRY = "--dry" in sys.argv

MONTHS = {m: i + 1 for i, m in enumerate(
    ["January", "February", "March", "April", "May", "June", "July",
     "August", "September", "October", "November", "December"])}

NEW = {  # id -> relevance
    "12481735": "strong", "12481977": "strong", "12482076": "strong",
    "12482087": "strong", "12482153": "strong", "12482318": "strong",
    "12482351": "strong", "12482450": "strong", "12482857": "strong",
    "12482461": "related", "12482703": "related",
    "12483066": "related", "12483088": "related", "12483704": "related",
    "12483737": "related", "12483770": "related", "12483792": "related",
    "12483869": "related", "12483880": "related",
    "12484188": "related", "12484254": "related",
}
MARTYR_IDS = {i for i in NEW if i >= "12483066"} | {"12484188", "12484254"}


def page_date(t):
    m = re.search(r"icon-calendar[^<]*</i>\s*(\d{1,2})\s+(\w+)،\s*(\d{4})", t)
    if not m:
        return None
    d, mon, y = int(m.group(1)), MONTHS.get(m.group(2)), int(m.group(3))
    return f"{y:04d}-{mon:02d}-{d:02d}" if mon else None


def slot(d):
    days = {f"2024-09-{17+i:02d}": i for i in range(8)}
    if d in days:
        return f"day_{days[d]}"
    if "2024-09-24" < d <= "2024-10-01":
        return "week_2"
    return "first_month" if d > "2024-10-01" else "pre_window"


def strip_tags(seg):
    seg = re.sub(r"<script[^>]*>.*?</script>", " ", seg, flags=re.S | re.I)
    seg = re.sub(r"<[^>]+>", " ", seg)
    return htmllib.unescape(re.sub(r"\s+", " ", seg)).strip()


def extract(t):
    m = re.search(r'property="og:title" content="([^"]*)"', t)
    head = htmllib.unescape(m.group(1)) if m else ""
    body = ""
    m = re.search(r'<div class="article-content">(.*?)</div>', t, re.S)
    if m:
        body = strip_tags(m.group(1))
    return head, body


def main():
    recs = [json.loads(l) for l in open(LB / "06-corpus/corpus.jsonl", encoding="utf-8")]
    have = {r["document_id"].split("_")[-1] for r in recs
            if r["source"]["page_publisher"] == "almanar"}

    # 1. re-date existing records from raw
    n_redate = 0
    for r in recs:
        if r["source"]["page_publisher"] != "almanar":
            continue
        p = LB / r["capture"]["raw_path"]
        if not p.exists():
            continue
        d = page_date(open(p, encoding="utf-8", errors="ignore").read())
        if d and d != r["publication"].get("published_at"):
            r["publication"]["published_at"] = d
            r["publication"]["time_slot"] = slot(d)
            n_redate += 1
        if d:
            r["publication"]["date_source"] = "page-meta-v12"
    print("re-dated existing almanar records:", n_redate)

    # 2. fetch + append the missed items
    rawdir = LB / "raw" / "almanar"
    added = []
    for pid, rel in sorted(NEW.items()):
        if pid in have:
            continue
        fp = rawdir / f"recov_{pid}.html"
        if not fp.exists():
            if DRY:
                print("[dry] would fetch", pid)
                continue
            out = subprocess.run(
                ["curl", "-s", "-m", "40", "-A", "Mozilla/5.0",
                 f"https://archive.almanar.com.lb/{pid}"],
                capture_output=True).stdout
            if not out or len(out) < 5000:
                print("FETCH FAIL", pid, len(out or b""))
                continue
            fp.write_bytes(out)
            time.sleep(3)
        t = open(fp, encoding="utf-8", errors="ignore").read()
        head, body = extract(t)
        d = page_date(t)
        if not head:
            print("EXTRACT FAIL", pid)
            continue
        head = re.sub(r"\s*[–-]\s*موقع قناة المنار.*$", "", head).strip()
        warns = ["recovered_v12_titlesweep_miss"]
        if pid in MARTYR_IDS:
            warns.append("martyr_notice_death_cause_unverified")
        rec = {
            "schema_version": "1.1.0-phase1",
            "document_id": f"lb_almanar_{pid}",
            "event_id": "lebanon_pager_attacks_2024",
            "source": {"page_publisher": "almanar",
                       "country_or_media_system": "Lebanon", "language": "ar"},
            "publication": {"published_at": d or "",
                            "date_source": "page-meta-v12" if d else "unknown",
                            "time_slot": slot(d) if d else "",
                            "document_type": "brief" if len(body.split()) < 90 else "article",
                            "canonical_url": f"https://www.almanar.com.lb/{pid}"},
            "content": {"headline": head, "body": body,
                        "word_count": len(body.split()),
                        "body_sha256": hashlib.sha256(body.encode()).hexdigest() if body else ""},
            "provenance": {"credit": "", "content_origin": "local_or_unspecified"},
            "capture": {"collection_route": "archive-host-live",
                        "raw_path": f"raw/almanar/recov_{pid}.html"},
            "extraction": {"method": "container-v12", "relevance": rel,
                           "warnings": warns},
            "deduplication": {"exact_duplicate_cluster_id": "",
                              "is_primary_record": True},
        }
        recs.append(rec)
        added.append((pid, d, rel, head[:50]))
    for a in added:
        print("added", *a)

    if not DRY:
        with open(LB / "06-corpus/corpus.jsonl", "w", encoding="utf-8") as f:
            for r in recs:
                f.write(json.dumps(r, ensure_ascii=False) + "\n")
        # 3. tag titles.csv
        tp = LB / "04-enumeration" / "almanar-titles.csv"
        rows = list(csv.DictReader(open(tp, encoding="utf-8")))
        for row in rows:
            if row["id"] in NEW and not (row.get("relevance") or "").strip():
                row["relevance"] = NEW[row["id"]]
        with open(tp, "w", encoding="utf-8", newline="") as f:
            w = csv.DictWriter(f, fieldnames=rows[0].keys())
            w.writeheader()
            w.writerows(rows)
        print("corpus + titles.csv written")


if __name__ == "__main__":
    main()
