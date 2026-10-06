#!/usr/bin/env python3
"""Corpus v2: merge collection round 2 into the corpus. Usage: build_corpus_v2.py <country> [--dry]

Inputs (data/<country>/):
  06-corpus/corpus.jsonl, excluded.jsonl     corpus v1.3.1 (and this script's own earlier output)
  05-extraction/round2/reextract-v1.jsonl    existing records re-extracted with the validated round-2 extractor
  05-extraction/round2/candidates.jsonl      gap-manifest items extracted from saved pages (stage 1)
  05-extraction/round2/liveblog-entries.jsonl  live-blog entries (stage 2, Germany and US)
  05-extraction/round2/gap-manifest-input.csv  the recall audit's gap manifest as it was before round 2

Steps:
  1. Existing records: body replaced by the re-extraction when it passed its checks (warning
     body_reextracted_v2). Headlines are kept. Records without a raw file keep their stored body.
  2. Gap items and live-blog entries are added as new records (extraction.round = 2).
  3. Derived fields are recomputed on every run, for old and new records alike:
     - salience: central (attack named in the headline or the first 400 characters of the body),
       mention (named further down), allusive (read by hand or audit evidence: refers to the attack
       without naming it), none. One rule for all countries, with the recall audit's term lists.
     - relevance follows salience: central -> strong, mention/allusive -> related, none -> context.
     - duplicates: identical bodies (> 20 words) within one outlet form a cluster with one primary
       record; a copy in another outlet stays primary and gets deduplication.same_text_as. Relations
       set by earlier passes (earlier_version, near_duplicate, repost, URL-variant clusters) are kept.
       Live-blog entries of one outlet with >= 80% word overlap (daily blogs repost entries): the later
       one is a liveblog_near_duplicate.
     - published_at is the date in the outlet's home time zone when an exact time is known.
     - document-type fixes, Abu Ali comment-link footer removed, missing languages detected.
  4. schema_version 1.2.0.
Idempotent: re-running changes nothing.
"""
import csv, hashlib, json, re, sys
from collections import Counter
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2] / "data"
PIPE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PIPE / "08-recall-audit"))
DRY = "--dry" in sys.argv
EVENT_DAY = date(2024, 9, 17)
SCHEMA = "1.2.0"
LABEL = {"lebanon": "Lebanon", "israel": "Israel", "germany": "Germany", "us": "United States"}
HOME_UTC_OFFSET = {"lebanon": 3, "israel": 3, "germany": 2, "us": -4}  # Sep-Oct 2024 (summer time everywhere)
TYPE_MAP = {"liveblog": "live_blog"}
RELEVANCE = {"central": "strong", "mention": "related", "allusive": "related", "none": "context"}
KEEP_RELATIONS = {"earlier_version", "near_duplicate", "repost"}
ABUALI_FOOTER = "כדי להגיב לכתבה לחצו כאן"

# Read by hand. Salience overrides with the reason.
MANUAL = {
    "lb_almanar_12486432": ("allusive", "health minister on the toll 'relative to the size of the aggression'"),
    "lb_almanar_12487444": ("allusive", "medical aid for 'the wounded of the Zionist aggression'"),
    "lb_almanar_12487763": ("allusive", "Safieddine: 'the Zionist aggression will be punished'"),
    "lb_almanar_12488269": ("allusive", "condition of the Iranian ambassador, who was injured by a pager"),
    "lb_almanar_12495859": ("allusive", "bulletin intro: 'the aggression of Tuesday and Wednesday, heavy and unprecedented'"),
    "lb_almanar_12497828": ("allusive", "'the Israeli electronic aggression on Lebanon'"),
    "lb_almanar_12498895": ("none", "Sep 20 strike on the southern suburb (Aqil), a different event"),
    "lb_almanar_12504384": ("none", "airstrike toll and rubble removal, a different event"),
    "lb_almanar_12506265": ("none", "rocket fire on Ramat David, a different event"),
    "lb_almanar_12512293": ("none", "rocket fire on Haifa and Safed, a different event"),
    "lb_lbci_796719": ("central", "flash: 'explosion of a number of devices in the Dahiyeh, the South and the Bekaa'"),
    "lb_lbci_797515": ("allusive", "bulletin intro: 77 dead and thousands wounded 'in three massacres'"),
    "us_fox_722f8f8697": ("mention", "attack named only in an in-article related-story headline (all caps)"),
    "us_fox_4bb048af54": ("mention", "attack named only in an in-article related-story headline (all caps)"),
    "il_kikar_d7845b3b06": ("none", "Rafah fighting; only generic 'מכשירי קשר' among seized weapons"),
    "us_nyt_01e7967f66": ("allusive", "deck: 'The explosion of wireless devices across Lebanon casts in sharp relief…'"),
}

# Audit false positives: a device word in an unrelated story. Not added to the corpus at all.
AUDIT_FALSE_POSITIVES = {
    "ge_rnd_e930e8efa8": "ice hockey: DEL referees get a Funkgerät",
    "ge_welt_8b9ff2d9d5": "ice hockey: DEL season preview",
    "ge_spiegel_81b2cbf352": "youth fire brigade: 'piept das Funkgerät von meinem Papa'",
    "us_cnn_fba13e8a24": "architecture: London's 'Walkie Talkie' building",
    "us_yahoo_2169913fc0": "St. Louis: firefighter used an officer's walkie-talkie",
    "us_yahoo_d7d93f8010": "school phone bans: teachers use walkie-talkies",
}

# Document types found wrong by the v2.0 review.
TYPE_FIXES = {
    **{d: "live_blog" for d in ("us_yahoo_e21870ad61", "us_yahoo_3c662b7688", "us_yahoo_6170ab94e6",
                                "us_yahoo_79562cddf8", "us_yahoo_9d70057879", "us_yahoo_4d87ecdf5f")},
    "lb_nna_722149": "press_review",
    "ge_bild_ac3c4b356a": "video_page",
}
NEWSLETTER_RE = re.compile(r"Morning Rundown|^Die Lage am|^Die Lage:", re.I)


def slot(pub):
    try:
        d = (date.fromisoformat(pub[:10]) - EVENT_DAY).days
    except ValueError:
        return ""
    if d < 0: return "pre_event"
    if d <= 7: return f"day_{d}"
    if d <= 14: return "week_2"
    if d <= 30: return "first_month"
    return "tail"


def local_date(ts, country):
    """Date in the outlet's home time zone, if ts carries an explicit offset or Z."""
    if not ts or not re.search(r"(Z|[+-]\d\d:?\d\d)$", ts.strip()):
        return ""
    t = ts.strip().replace("Z", "+00:00")
    t = re.sub(r"([+-]\d\d)(\d\d)$", r"\1:\2", t)
    t = re.sub(r"\.\d+(?=[+-])", "", t)
    try:
        dt = datetime.fromisoformat(t)
    except ValueError:
        return ""
    return dt.astimezone(timezone(timedelta(hours=HOME_UTC_OFFSET[country]))).date().isoformat()


def hit_fn(country):
    """text, doc -> attack named in text? (doc = the whole item, for context rules)"""
    if country in ("germany", "us"):
        from recall_audit_common import has_mention
        region = re.compile(r"liban|leban|hisbollah|hezbollah|beirut|israel", re.I)
        generic = re.compile(r"funk|walkie|radio", re.I)
        # devices / Geräte next to a blast word; the audit's term lists miss these phrasings
        blast = r"(?:explo|detonat|blast|sprengst|planted|angriff|anschlag|attack)"
        thing = r"(?:devices?|ger[äa]te[n]?|kommunikations\w+|communications? equipment)"
        extra = re.compile(thing + r"[^.]{0,120}?" + blast + "|" + blast + r"\w*[^.]{0,120}?" + thing, re.I)

        def f(t, doc):
            m = has_mention(t, country)
            if m and (not generic.search(m.group(0)) or region.search(doc)):
                return True
            return bool(extra.search(t)) and bool(region.search(doc))
        return f
    import recall_audit_il_lb_common as C
    return lambda t, doc: C.device_hits(t, doc)[0] > 0


def salience_of(hit, headline, body):
    doc = headline + " " + body
    if hit(headline + " " + body[:400], doc):
        return "central"
    return "mention" if hit(body, doc) else "none"


def audit_evidence(country):
    D = ROOT / country / "08-recall-audit"
    if country in ("germany", "us"):
        return {r["url"]: [r.get("evidence", "")] for r in csv.DictReader(open(D / "reference-set.csv", encoding="utf-8"))}
    import recall_audit_il_lb_common as C
    items = json.load(open(D / "raw" / "items.json", encoding="utf-8"))
    out = {"key:" + k: [s if isinstance(s, str) else json.dumps(s, ensure_ascii=False) for s in (v.get("snips") or [])]
           for k, v in items.items()}
    out["_key"] = C.url_key
    return out


def evidence_in_body(ev, url, body):
    snips = ev.get("key:" + ev["_key"](url), []) if "_key" in ev else ev.get(url, [])
    for s in snips:
        s = " ".join(re.sub(r"^\[headline/description\]\s*", "", s).split())
        if any(s[i:i + 30] in body for i in range(0, max(len(s) - 30, 1), 15) if s[i:i + 30]):
            return True
    return False


def new_id(country, c):
    if country == "lebanon":
        m = re.search(r"/(\d{5,})(?:[/?]|$)", c["url"])
        return f"lb_{c['outlet']}_{m.group(1) if m else hashlib.sha256(c['url'].encode()).hexdigest()[:10]}"
    if c["outlet"] == "abuali":
        return f"il_abuali_{c['url'].rstrip('/').rsplit('/', 1)[1]}"
    cc = {"israel": "il", "germany": "ge", "us": "us"}[country]
    return f"{cc}_{c['outlet']}_{hashlib.sha256(c['url'].encode()).hexdigest()[:10]}"


def body_fields(body):
    return {"body": body, "word_count": len(body.split()), "body_sha256": hashlib.sha256(body.encode()).hexdigest()}


def checks_pass(rx):
    ch = rx.get("checks") or {}
    return bool(rx.get("ok")) and all((v.get("ok") if isinstance(v, dict) else v is True) for v in ch.values())


def detect_language(text):
    if re.search(r"[֐-׿]", text): return "he"
    if re.search(r"[؀-ۿ]", text): return "ar"
    if re.search(r"\b(der|die|und|nicht|ist|mit)\b", text): return "de"
    return "en" if text.strip() else ""


def warn(r, w):
    if w not in r["extraction"]["warnings"]:
        r["extraction"]["warnings"].append(w)


def main(country):
    D = ROOT / country
    R2 = D / "05-extraction/round2"
    cpath, xpath = D / "06-corpus/corpus.jsonl", D / "06-corpus/excluded.jsonl"
    recs = [json.loads(l) for l in open(cpath, encoding="utf-8")]
    excluded = [json.loads(l) for l in open(xpath, encoding="utf-8")] if xpath.exists() else []
    rx = {r["document_id"]: r for r in map(json.loads, open(R2 / "reextract-v1.jsonl", encoding="utf-8"))}
    cands = [json.loads(l) for l in open(R2 / "candidates.jsonl", encoding="utf-8")]
    manifest_dates = {r["url"]: r.get("published_date", "")[:10]
                      for r in csv.DictReader(open(R2 / "gap-manifest-input.csv", encoding="utf-8"))}
    hit = hit_fn(country)
    ev = audit_evidence(country)
    log = Counter()

    # 1. existing records: re-extracted bodies
    for r in recs:
        r["extraction"].setdefault("round", 1)
        if r["extraction"]["round"] != 1:
            continue
        x = rx.get(r["document_id"])
        if x is None or "no_raw" in x.get("warnings", []):
            log["no_raw_kept"] += 1
        elif not checks_pass(x):
            log["reextract_failed_kept"] += 1
        elif x["body_text"] != r["content"]["body"]:
            r["content"].update(body_fields(x["body_text"]))
            r["extraction"]["method"] = x.get("extract_method", r["extraction"]["method"])
            warn(r, "body_reextracted_v2")
            log["reextracted"] += 1
    # 2. gap items
    if country in ("germany", "us"):
        from recall_audit_common import key as url_key
    else:
        from recall_audit_il_lb_common import url_key
    ukey = lambda u: url_key(u) if u else ""
    have = {r["document_id"]: r for r in recs + excluded}
    urls = {ukey(r["publication"]["canonical_url"]) for r in recs + excluded
            if r["publication"]["document_type"] != "live_blog_entry"}
    for c in cands:
        if not c["ok"]:
            log["skip:" + (c["failure"] or "not_ok")] += 1; continue
        if c["document_type_hint"] == "liveblog":
            log["skip:deferred_liveblog"] += 1; continue
        did = new_id(country, c)
        if did in have and have[did]["extraction"].get("round") == 2:
            r = have[did]  # added on an earlier run: refresh the text from the (possibly re-extracted) candidate
            body = c["body_text"]
            if r["content"]["body"] != body or r["content"]["headline"] != c["title"]:
                r["content"].update(headline=c["title"], **body_fields(body))
                r["extraction"]["method"] = c.get("extract_method", r["extraction"]["method"])
                log["gap_refreshed"] += 1
            continue
        if did in AUDIT_FALSE_POSITIVES:
            log["skip:audit_false_positive"] += 1; continue
        if ukey(c["url"]) in urls or ukey(c["canonical_url"]) in urls:
            log["skip:url_already_in_corpus"] += 1; continue
        if did in have:
            did = f"{did}_{hashlib.sha256(c['url'].encode()).hexdigest()[:6]}"  # e.g. a second language edition
            log["id_suffixed"] += 1
        pub, warnings = c["published_at"], ["added_v2_gapfill"] + list(c.get("warnings", []))
        published_time = c.get("published_time", "")
        md = manifest_dates.get(c["url"], "")
        if not (pub and "2024-09-17" <= pub <= "2024-10-17") and "2024-09-17" <= md <= "2024-10-17":
            pub, published_time = md, ""  # the page shows a later modification date; the audit verified publication
            c = dict(c, date_source="audit-manifest")
            warnings.append("page_date_not_publication_v2")
        if not (pub and "2024-09-17" <= pub <= "2024-10-17"):
            log["skip:no_date_or_out_of_window"] += 1; continue
        body = c["body_text"]
        if salience_of(hit, c["title"], body) == "none":
            if evidence_in_body(ev, c["url"], " ".join(body.split()) + " " + c["title"]):
                warnings.append("allusive_or_detector_gap")
            elif c.get("paywall") or len(body.split()) < 90:
                warnings.append("evidence_beyond_captured_text")
        if c.get("paywall"):
            warnings.append("paywall")
        prov = c.get("provider", "")
        rec = {"schema_version": SCHEMA, "document_id": did, "event_id": "lebanon_pager_attacks_2024",
               "source": {"page_publisher": c["outlet"], "country_or_media_system": LABEL[country],
                          "language": c.get("language", "")},
               "publication": {"published_at": pub, "date_source": c.get("date_source", ""), "time_slot": "",
                               "document_type": TYPE_MAP.get(c["document_type_hint"], c["document_type_hint"]),
                               "canonical_url": c["canonical_url"] or c["url"]},
               "content": {"headline": c["title"], **body_fields(body)},
               "provenance": {"credit": prov, "content_origin": "syndicated_or_adapted" if prov else "local_or_unspecified"},
               "capture": {"collection_route": c["fetch_route"], "raw_path": c["raw_path"]},
               "extraction": {"method": c.get("extract_method", ""), "relevance": "", "warnings": warnings,
                              "round": 2, "gap_status": c.get("gap_status", "")},
               "deduplication": {"exact_duplicate_cluster_id": "", "is_primary_record": True}}
        if published_time:
            rec["publication"]["published_time"] = published_time
        if "footer_comment_link" in c:
            rec["content"]["footer_comment_link"] = c["footer_comment_link"]
        recs.append(rec)
        have[did] = rec
        urls.add(ukey(rec["publication"]["canonical_url"]))
        log["added"] += 1
    # 2b. live-blog entries (stage 2)
    lbp = R2 / "liveblog-entries.jsonl"
    for e in (map(json.loads, open(lbp, encoding="utf-8")) if lbp.exists() else []):
        did = f"{country[:2]}_{e['outlet']}_lb_{hashlib.sha256((e['blog_url'] + '#' + e['entry_id']).encode()).hexdigest()[:10]}"
        if did in have:
            continue
        rec = {"schema_version": SCHEMA, "document_id": did, "event_id": "lebanon_pager_attacks_2024",
               "source": {"page_publisher": e["outlet"], "country_or_media_system": LABEL[country],
                          "language": e.get("language", "")},
               "publication": {"published_at": e["published_at"], "published_time": e.get("published_time", ""),
                               "date_source": "liveblog-entry", "time_slot": "", "document_type": "live_blog_entry",
                               "canonical_url": e.get("entry_url") or e["blog_url"], "liveblog_url": e["blog_url"],
                               "liveblog_entry_id": e["entry_id"]},
               "content": {"headline": e.get("title", ""), **body_fields(e["body_text"])},
               "provenance": {"credit": "", "content_origin": "local_or_unspecified"},
               "capture": {"collection_route": f"wayback:{e['first_seen_capture']}", "raw_path": e["raw_path"],
                           "last_seen_capture": e.get("last_seen_capture", "")},
               "extraction": {"method": e.get("extract_method", ""), "relevance": "",
                              "warnings": ["added_v2_liveblog"] + list(e.get("warnings", [])), "round": 2},
               "deduplication": {"exact_duplicate_cluster_id": "", "is_primary_record": True}}
        recs.append(rec)
        have[did] = rec
        log["liveblog_entries_added"] += 1

    # 3. derived fields, recomputed from content on every run
    for r in recs:
        r["schema_version"] = SCHEMA
        p, ct, x = r["publication"], r["content"], r["extraction"]
        if r["source"]["page_publisher"] == "abuali":
            for f in ("headline", "body"):
                s = ct[f].rstrip()
                if s.endswith(ABUALI_FOOTER):
                    ct[f] = s[: -len(ABUALI_FOOTER)].rstrip()
                    ct["footer_comment_link"] = True
            ct.update(body_fields(ct["body"]))
        if not r["source"].get("language"):
            r["source"]["language"] = detect_language(ct["headline"] + " " + ct["body"])
            warn(r, "language_detected_v2")
        ld = local_date(p.get("published_time", ""), country)
        if ld and ld != p["published_at"] and "2024-09-17" <= ld <= "2024-10-17":
            p["published_at"] = ld
            warn(r, "date_local_time_zone_v2")
        p["time_slot"] = slot(p["published_at"])
        # document type
        dt = TYPE_FIXES.get(r["document_id"], p["document_type"])
        if dt == "article" and NEWSLETTER_RE.search(ct["headline"]):
            dt = "newsletter"
        if dt == "article" and ("paywall" in x["warnings"] or "page_truncated_by_access_wall" in x["warnings"]):
            dt = "flash_or_lead"
        if dt == "article" and ct["word_count"] == 0:
            dt = "brief"
        if dt == "article" and 0 < ct["word_count"] < 90 and x.get("round") == 2:
            dt = "flash_or_lead"
        if dt != p["document_type"]:
            p["document_type"] = dt
            warn(r, "type_fixed_v2")
        # salience and relevance
        s = salience_of(hit, ct["headline"], ct["body"])
        if s == "none" and "allusive_or_detector_gap" in x["warnings"]:
            s = "allusive"
        elif s == "none" and "evidence_beyond_captured_text" in x["warnings"]:
            s = "mention"
        x.pop("manual_note", None)
        if r["document_id"] in MANUAL:
            s, note = MANUAL[r["document_id"]]
            x["manual_note"] = note
            warn(r, "manual_salience_v2")
        x["salience"] = s
        x["relevance"] = RELEVANCE[s]
        order = ["method", "relevance", "salience", "round", "gap_status", "manual_note", "warnings"]
        r["extraction"] = {k: x[k] for k in order if k in x} | {k: v for k, v in x.items() if k not in order}
    # 4. duplicates: reset what this script computes, keep relations from earlier passes
    for r in recs:
        d = r["deduplication"]
        d.pop("same_text_as", None)
        if d.get("relation") in KEEP_RELATIONS or (d.get("exact_duplicate_cluster_id") or "x")[:1] != "x":
            continue  # earlier_version / near_duplicate / repost / URL-variant clusters (ampdup_, pathdup_)
        d.pop("relation", None); d.pop("version_of", None)
        d["is_primary_record"] = True
        d["exact_duplicate_cluster_id"] = ""
    order = sorted(recs, key=lambda r: (r["extraction"]["round"], r["publication"].get("published_time") or "",
                                        r["document_id"]))
    first_in_outlet, first_any = {}, {}
    for r in order:
        d, ct = r["deduplication"], r["content"]
        if ct["word_count"] <= 20 or not d["is_primary_record"]:
            continue
        k = (r["source"]["page_publisher"], ct["body_sha256"])
        d["exact_duplicate_cluster_id"] = f"x{ct['body_sha256'][:10]}"
        if k in first_in_outlet:
            d.update(is_primary_record=False, version_of=first_in_outlet[k], relation="exact_duplicate")
            continue
        first_in_outlet[k] = r["document_id"]
        other = first_any.get(ct["body_sha256"])
        if other and other[0] != r["source"]["page_publisher"]:
            d["same_text_as"] = other[1]  # cross-outlet copy: both readerships saw it, both stay primary
        first_any.setdefault(ct["body_sha256"], (r["source"]["page_publisher"], r["document_id"]))
    # live-blog near-duplicates within one blog
    by_blog = {}
    for r in order:
        if r["publication"]["document_type"] == "live_blog_entry" and r["deduplication"]["is_primary_record"]:
            by_blog.setdefault(r["source"]["page_publisher"], []).append(r)  # outlets repost entries across daily blogs
    for entries in by_blog.values():
        kept = []
        for r in entries:
            ws = set(r["content"]["body"].lower().split())
            twin = next((k for k, kw in kept if ws and len(ws & kw) / len(ws | kw) >= 0.8), None)
            if twin:
                r["deduplication"].update(is_primary_record=False, version_of=twin, relation="liveblog_near_duplicate")
            else:
                kept.append((r["document_id"], ws))

    prim = [r for r in recs if r["deduplication"]["is_primary_record"]]
    print(f"--- {country}: {len(recs)} records, {len(prim)} primary | {json.dumps(dict(sorted(log.items())))}")
    print("    salience (primary):", dict(Counter(r["extraction"]["salience"] for r in prim)))
    print("    by round (primary):", dict(Counter(r["extraction"]["round"] for r in prim)))
    if DRY:
        print("    [dry] not writing")
        return
    with open(cpath, "w", encoding="utf-8") as f:
        for r in recs:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")


if __name__ == "__main__":
    main(sys.argv[1])
