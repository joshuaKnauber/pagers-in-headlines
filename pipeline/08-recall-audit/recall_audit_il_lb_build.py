#!/usr/bin/env python3
"""Assemble the Israel / Lebanon recall-audit reference sets.

Usage: recall_audit_il_lb_build.py <country> [review]
  review -> also writes raw/review-queue.csv (items needing a human read)

Inputs (data/<country>/08-recall-audit/raw/):
  check-results*.jsonl   fetched + extracted items (re-extracted here from raw HTML
                         with the current matcher, so worker-version drift is moot)
  abuali-live-messages.csv (israel)   live Telegram route
  mediacloud-stories.csv (lebanon)    Media Cloud full-text route
  manual-review.csv      human verdicts: key,verdict(central|mention|none|offwindow),note
Outputs (data/<country>/08-recall-audit/):
  reference-set.csv, gap-manifest.csv, raw/recall-tables.json
"""
import csv, glob, json, re, sys, urllib.parse
from collections import Counter, defaultdict
from datetime import datetime, timedelta, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import recall_audit_il_lb_common as C

WIN = ("2024-09-17", "2024-09-24")
TZ = timezone(timedelta(hours=3))   # IDT and EEST are both UTC+3 in Sep 2024
MONTHS_AR = {"يناير": 1, "كانون الثاني": 1, "فبراير": 2, "مارس": 3, "أبريل": 4, "ابريل": 4, "مايو": 5, "يونيو": 6,
             "يوليو": 7, "أغسطس": 8, "اغسطس": 8, "سبتمبر": 9, "أيلول": 9, "ايلول": 9, "أكتوبر": 10, "اكتوبر": 10,
             "تشرين الأول": 10, "نوفمبر": 11, "ديسمبر": 12,
             "January": 1, "February": 2, "March": 3, "April": 4, "May": 5, "June": 6, "July": 7, "August": 8,
             "September": 9, "October": 10, "November": 11, "December": 12}
# Sequential-ID anchors (first ID seen on a Beirut date) from corpus dates; used only when a page has no date.
ID_ANCHORS = {
    "lbci": [(796250, "2024-09-17"), (796570, "2024-09-18"), (796840, "2024-09-19"), (797080, "2024-09-20"),
             (797350, "2024-09-21"), (797560, "2024-09-22"), (797800, "2024-09-23"), (798100, "2024-09-24"),
             (798500, "2024-09-25")],
    "aljadeed": [(502470, "2024-09-17"), (502640, "2024-09-18"), (502840, "2024-09-19"), (503000, "2024-09-20"),
                 (503300, "2024-09-21"), (503420, "2024-09-22"), (503600, "2024-09-23"), (503900, "2024-09-24"),
                 (504300, "2024-09-25")],
}
INDEPENDENT = {"gdelt", "mediacloud", "abuali-live", "id-census", "id-sample", "websearch", "cdx-section",
               "mtv-sitemap", "bulletin-intro"}


def local_date(s):
    s = (s or "").strip()
    if not s:
        return ""
    s2 = s.replace("Z", "+00:00")
    s2 = re.sub(r"([+-]\d{2})(\d{2})$", r"\1:\2", s2)
    try:
        d = datetime.fromisoformat(s2)
        if d.tzinfo is None:
            return d.date().isoformat()
        return d.astimezone(TZ).date().isoformat()
    except Exception:
        m = re.match(r"(\d{4}-\d{2}-\d{2})", s)
        return m.group(1) if m else ""


def almanar_page_date(t):
    m = re.search(r"icon-calendar[^<]*</i>\s*(\d{1,2})\s+([^\s،,]+(?:\s[^\s،,]+)?)،?\s*(\d{4})", t)
    if m:
        mon = MONTHS_AR.get(m.group(2).strip())
        if mon:
            return f"{int(m.group(3)):04d}-{mon:02d}-{int(m.group(1)):02d}"
    return ""


def id_date(outlet, key):
    try:
        n = int(key.split(":", 1)[1].split("/")[0])
    except Exception:
        return ""
    anchors = ID_ANCHORS.get(outlet)
    if not anchors or n < anchors[0][0] or n >= anchors[-1][0]:
        return ""
    d = ""
    for a, day in anchors:
        if n >= a:
            d = day
    return d + "~id"


def discovery_routes(disc):
    out = []
    for d in disc.split(";"):
        base = d.split(":")[0]
        out.append(base)
    return out


def load_checks(country):
    recs = {}
    for f in sorted(glob.glob(str(C.DATA / country / "08-recall-audit" / "raw" / "check-results*.jsonl"))):
        for line in open(f, encoding="utf-8"):
            try:
                r = json.loads(line)
            except Exception:
                continue
            k = C.url_key(r["url"])
            prev = recs.get(k)
            if prev is None:
                recs[k] = r
            else:
                ds = set(prev["discovery"].split(";")) | set(r["discovery"].split(";"))
                if r.get("ok") and not prev.get("ok"):
                    recs[k] = r
                recs[k]["discovery"] = ";".join(sorted(ds))
    return recs


def mtv_dates():
    d = {}
    for r in csv.DictReader(open(C.DATA / "lebanon" / "04-enumeration" / "mtv-urls.csv", encoding="utf-8")):
        if r.get("publication_date"):
            d[C.url_key(r["url"])] = r["publication_date"][:10]
    return d


def reextract(country, r):
    p = C.DATA / country / r["raw"]
    t = p.read_text(encoding="utf-8", errors="replace")
    ex = C.extract(r["outlet"], t)
    # strip Wayback toolbar residue from titles
    title = re.sub(r"\s*[|\-–]\s*(Lebanon News|MTV Lebanon|N12|ynet|כיכר השבת)\s*$", "", ex["title"]).strip()
    title = re.sub(r"\s+–\s+موقع قناة المنار.*$", "", title)
    title = re.sub(r"^N12\s*-\s*", "", title)
    date = local_date(ex["date"])
    if r["outlet"] == "almanar" and not date:
        date = almanar_page_date(t)
    if r["outlet"] == "nna" and not date:
        m = re.search(r"(\d{1,2})\s+(أيلول|ايلول|تشرين الأول|تشرين الاول)\s+(2024)", ex["body"][:400])
        if m:
            date = f"2024-{9 if 'يلول' in m.group(2) else 10:02d}-{int(m.group(1)):02d}"
    final = r.get("fetch_info", "")
    soft404 = bool(re.search(r"404|لم يتم العثور|الصفحة غير موجودة|העמוד לא נמצא|Page not found", title[:80]))
    return ex, title, date, soft404, t


def classify(title, body, desc):
    nt, _ = C.device_hits(title, body)
    nb, snips = C.device_hits(body, title)
    nd, _ = C.device_hits(desc, title)
    lead = " ".join(body.split()[:60])
    nl, _ = C.device_hits(lead, title + " " + body)
    words = len(body.split())
    if nt or nb >= 3 or (nl and words < 120):
        cls = "central"
    elif nb or nd:
        cls = "mention"
    else:
        cls = "none"
    return cls, nt, nb, nd, snips


def manual(country):
    p = C.DATA / country / "08-recall-audit" / "raw" / "manual-review.csv"
    out = {}
    if p.exists():
        for r in csv.DictReader(open(p, encoding="utf-8")):
            out[r["key"]] = (r["verdict"], r.get("note", ""))
    return out


def build(country, want_review=False):
    ours = C.load_ours(country)
    checks = load_checks(country)
    man = manual(country)
    mtvd = mtv_dates() if country == "lebanon" else {}
    items = {}
    stats = Counter()
    for k, r in checks.items():
        if not r.get("ok"):
            if "HTTP 404" in r.get("fetch_info", "") and ("id-census" in r["discovery"] or "id-sample" in r["discovery"]):
                stats["id_nonexistent"] += 1
                continue
            stats["fetch_fail"] += 1
            items[k] = {"key": k, "outlet": r["outlet"], "url": r["url"], "title": r.get("extra", ""),
                        "date": "", "routes": discovery_routes(r["discovery"]), "class": "unknown",
                        "fetch": "fail: " + r.get("fetch_info", "")[:80], "snips": [], "nt": 0, "nb": 0}
            continue
        ex, title, date, soft404, t = reextract(country, r)
        if soft404 or (len(ex["body"].split()) < 3 and not title):
            stats["soft404"] += 1
            continue
        if r["outlet"] == "mtv" and k in mtvd:
            date = mtvd[k]
        if not date and r["outlet"] in ID_ANCHORS:
            date = id_date(r["outlet"], k)
        cls, nt, nb, nd, snips = classify(title, ex["body"], ex["desc"])
        cap = ""
        m = re.search(r"web\.archive\.org/web/(\d{14})", r.get("fetched", "") + " " + r.get("fetch_info", ""))
        if m:
            cap = m.group(1)
        items[k] = {"key": k, "outlet": r["outlet"], "url": r["url"], "title": title, "date": date,
                    "routes": discovery_routes(r["discovery"]), "class": cls, "nt": nt, "nb": nb, "nd": nd,
                    "snips": snips, "words": len(ex["body"].split()), "method": ex["method"],
                    "fetch": "wayback" if "web.archive.org" in r.get("fetched", "") else "live", "capture": cap,
                    "lead": " ".join(ex["body"].split()[:40])}
    # --- extra routes
    if country == "israel":
        archived = {}
        for r in csv.DictReader(open(C.DATA / "israel/04-enumeration/abuali-messages.csv", encoding="utf-8")):
            archived[int(r["post_id"])] = r
        for r in csv.DictReader(open(C.DATA / "israel/08-recall-audit/raw/abuali-live-messages.csv", encoding="utf-8")):
            pid = int(r["post_id"])
            k = f"abuali:t.me/abualiexpress/{pid}"
            n, sn = C.device_hits(r["text"])
            items[k] = {"key": k, "outlet": "abuali", "url": f"https://t.me/abualiexpress/{pid}",
                        "title": r["text"][:140], "date": local_date(r["datetime"]), "routes": ["abuali-live"],
                        "class": ("central" if C.device_hits(r["text"][:160])[0] else "mention") if n else "none",
                        "nt": n, "nb": n, "nd": 0, "snips": sn,
                        "words": len(r["text"].split()), "fetch": "live", "capture": "",
                        "lead": r["text"][:200], "in_archived_stream": pid in archived,
                        "archived_tag": (archived.get(pid) or {}).get("relevance", "")}
    if country == "lebanon":
        p = C.DATA / "lebanon/08-recall-audit/raw/mediacloud-stories.csv"
        if p.exists():
            for r in csv.DictReader(open(p, encoding="utf-8")):
                k = C.url_key(r["url"])
                if k in items:
                    if "mediacloud" not in items[k]["routes"]:
                        items[k]["routes"].append("mediacloud")
                    continue
                # foreign-language editions not body-checked: MC full-text hit is the evidence
                items[k] = {"key": k, "outlet": "almanar", "url": r["url"], "title": r["title"],
                            "date": r["publish_date"][:10], "routes": ["mediacloud"], "class": "mention-mc",
                            "nt": len(C.device_hits(r["title"])[1]), "nb": 0, "nd": 0, "snips": [],
                            "words": 0, "fetch": "not-fetched", "capture": "", "lead": ""}
    for it in items.values():
        if it["outlet"] == "almanar" and re.search(r"//(english|french|spanish|en-archive|fr-archive)\.", it["url"]):
            it["outlet"] = "almanar_foreign"
    # --- manual overrides
    for k, (v, note) in man.items():
        if k in items:
            items[k]["manual"] = v
            items[k]["manual_note"] = note
    # --- window + status
    rows = []
    for k, it in items.items():
        cls = it.get("manual") or it["class"]
        d = it["date"].replace("~id", "")
        inwin = bool(d) and WIN[0] <= d <= WIN[1]
        it["inwin"] = inwin if d else None
        if cls == "offwindow":
            it["inwin"] = False
        it["final_class"] = cls
        d_o = ours.get(k)
        st, doc = C.pipeline_status(d_o)
        note = []
        if it["outlet"] == "abuali":
            if k in ours and ours[k].get("corpus"):
                st, doc = C.pipeline_status(ours[k])
            elif it.get("in_archived_stream"):
                st = "in_manifest_not_candidate"
                note.append(f"in archived capture stream (tag={it.get('archived_tag') or 'none'})")
            else:
                st = "not_in_manifest"
                note.append("message absent from all 65 Wayback captures of t.me/s (capture gap)")
        if st == "not_in_manifest" and it["title"]:
            fk, sc = C.fuzzy_title_match(it["title"], ours, it["outlet"])
            if fk:
                st2, doc2 = C.pipeline_status(ours[fk])
                if st2 != "not_in_manifest":
                    note.append(f"fuzzy-title match {fk} ({sc:.2f})")
                    st, doc = st2, doc2
        it["status"], it["doc"] = st, doc
        it["note"] = note
    return items, stats


def recall_tables(items, outlets):
    tab = {}
    for o in outlets:
        for scope in ("all", "independent"):
            for cls in ("central", "mention"):
                sel = [it for it in items.values() if it["outlet"] == o and it.get("inwin") and it["final_class"] == cls
                       and (scope == "all" or any(r in INDEPENDENT for r in it["routes"]))]
                n = len(sel)
                hit = sum(1 for it in sel if it["status"] == "in_corpus")
                tab[f"{o}|{scope}|{cls}"] = {"n": n, "in_corpus": hit,
                                             "status": dict(Counter(it["status"] for it in sel))}
    return tab


FORMAT_HINTS = [
    (r"lebanon-news-intro|مقدمة (?:ال)?نشرة|مقدمات نشرات", "bulletin_intro"),
    (r"أسرار الصحف|الصحافة اليوم|عناوين الصحف|newspaper-secrets", "press_review"),
    (r"/yokra", "yedioth_print"),
    (r"ynet\.co\.il/(?!news/)", "ynet_non_news_section"),
    (r"pzm-soldiers|finances-news|nexter-news|men-men_news", "mako_non_n12_path"),
]


def fmt_hint(it):
    blob = it["url"] + " " + urllib.parse.unquote(it["url"]) + " " + it["title"]
    out = [name for rx, name in FORMAT_HINTS if re.search(rx, blob)]
    if it["outlet"] == "abuali":
        out.append("telegram_post")
    if it.get("words", 99) < 40 and it["outlet"] in ("lbci", "mtv", "aljadeed", "almanar", "ynet"):
        out.append("short_flash_or_ticker")
    return out


def corpus_window(country):
    """Primary corpus records in window, classified with the same matcher."""
    out = defaultdict(Counter)
    for line in open(C.DATA / country / "06-corpus/corpus.jsonl", encoding="utf-8"):
        r = json.loads(line)
        if not r["deduplication"]["is_primary_record"]:
            continue
        d = r["publication"].get("published_at") or ""
        if not (WIN[0] <= d[:10] <= WIN[1]):
            continue
        o = r["source"]["page_publisher"]
        if o == "almanar" and re.search(r"//(english|french)\.", r["publication"]["canonical_url"]):
            o = "almanar_foreign"
        cls, *_ = classify(r["content"]["headline"], r["content"]["body"], "")
        out[o][cls] += 1
    return out


N12_RECENT = re.compile(r"[12]9102[67]\.htm")


def control_extrapolation(country, items):
    """Per outlet and sampled stratum: unchecked units x relevant rate among checked random units.
    Units also hit by an independent route (gdelt, websearch) are excluded from the rate (biased)."""
    sizes = json.loads((C.DATA / country / "08-recall-audit" / "raw" / "strata-sizes.json").read_text())
    pops = defaultdict(dict)
    for stratum in ("manifest-kw", "manifest-untitled"):
        p = C.DATA / country / "08-recall-audit" / "raw" / f"tasks-{stratum}.csv"
        if p.exists():
            for r in csv.DictReader(open(p, encoding="utf-8")):
                if r["outlet"] == "n12" and not N12_RECENT.search(r["url"]):
                    continue   # N12 strata were sampled only among 2024-era mako IDs
                pops[r["outlet"]][stratum] = pops[r["outlet"]].get(stratum, 0) + 1
    for o, sz in sizes.items():
        pops[o]["control"] = sz["nokw_population"]
    res = {}
    for o, strata in pops.items():
        tot = 0.0
        det = {}
        for stratum, pop in strata.items():
            members = [it for it in items.values() if it["outlet"] == o and stratum in it["routes"]
                       and (o != "n12" or N12_RECENT.search(it["url"]))]
            checked = [it for it in members if it["class"] != "unknown"]
            pure = [it for it in checked if not ({"gdelt", "websearch", "mediacloud"} & set(it["routes"]))]
            rel = [it for it in pure if it.get("inwin") and it["final_class"] in ("central", "mention")]
            unchecked = max(0, pop - len(checked))
            rate = len(rel) / len(pure) if pure else None
            ext = round(rate * unchecked, 1) if rate is not None else None
            det[stratum] = {"population": pop, "checked": len(checked), "pure_checked": len(pure),
                            "pure_relevant": len(rel), "unchecked": unchecked, "extrapolated": ext}
            tot += ext or 0
        res[o] = {"strata": det, "extrapolated_missing": round(tot, 1)}
    return res


def write_outputs(country, items):
    base = C.DATA / country / "08-recall-audit"
    ref = [it for it in items.values() if it.get("inwin") and it["final_class"] in ("central", "mention", "mention-mc")]
    ref.sort(key=lambda it: (it["outlet"], it["date"], it["url"]))
    with open(base / "reference-set.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["outlet", "url", "title", "published_date", "discovery_route", "central_or_mention", "status",
                    "matched_document_id", "notes"])
        for it in ref:
            cls = "mention" if it["final_class"] == "mention-mc" else it["final_class"]
            notes = list(it["note"])
            notes.append(f"device hits title/body={it['nt']}/{it['nb']}")
            if it["final_class"] == "mention-mc":
                notes.append("not body-checked: Media Cloud full-text match only (foreign-language edition)")
            if it.get("manual_note"):
                notes.append("review: " + it["manual_note"])
            fh = fmt_hint(it)
            if fh:
                notes.append("format=" + ",".join(fh))
            if it.get("date", "").endswith("~id"):
                notes.append("date inferred from sequential ID")
            notes.append(f"fetched via {it['fetch']}" + (f" {it['capture']}" if it.get("capture") else ""))
            w.writerow([it["outlet"], it["url"], it["title"][:200], it["date"].replace("~id", ""),
                        ";".join(sorted(set(it["routes"]))), cls, it["status"], it["doc"], "; ".join(notes)])
    gap = [it for it in ref if it["status"] != "in_corpus" and it["fetch"] != "not-fetched"]
    with open(base / "gap-manifest.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["outlet", "url", "title", "published_date", "central_or_mention", "status", "collection_route",
                    "capture_timestamp", "format", "discovery_route"])
        for it in gap:
            route = "wayback" if it["fetch"] == "wayback" else ("live" if it["outlet"] != "almanar" else "archive.almanar.com.lb (live)")
            if it["outlet"] == "abuali":
                route = "live t.me/s/abualiexpress?before=<id> (no Wayback capture)"
            w.writerow([it["outlet"], it["url"], it["title"][:200], it["date"].replace("~id", ""), it["final_class"],
                        it["status"], route, it.get("capture", ""), ",".join(fmt_hint(it)), ";".join(sorted(set(it["routes"])))])
    return ref, gap


def main():
    country = sys.argv[1]
    items, stats = build(country)
    outlets = C.COUNTRY[country] + (["almanar_foreign"] if country == "lebanon" else [])
    print(stats)
    if len(sys.argv) > 2 and sys.argv[2] == "review":
        p = C.DATA / country / "08-recall-audit" / "raw" / "review-queue.csv"
        w = csv.writer(open(p, "w", newline="", encoding="utf-8"))
        w.writerow(["key", "outlet", "date", "class", "nt", "nb", "status", "routes", "title", "snippets", "url"])
        for k, it in sorted(items.items(), key=lambda x: (x[1]["outlet"], x[1]["date"])):
            if it.get("manual") or it["inwin"] is False:
                continue
            if it["final_class"] in ("mention",) or (it["final_class"] == "central" and it["nt"] == 0) \
                    or (it["final_class"] == "central" and it["status"] != "in_corpus"):
                w.writerow([k, it["outlet"], it["date"], it["final_class"], it["nt"], it["nb"], it["status"],
                            ";".join(it["routes"]), it["title"][:150], " || ".join(it["snips"][:3])[:600], it["url"]])
        print("review queue written")
    ref, gap = write_outputs(country, items)
    print("reference items", len(ref), "gap", len(gap), Counter(it["outlet"] for it in gap))
    cw = corpus_window(country)
    ext = control_extrapolation(country, items)
    summary = {}
    for o in outlets:
        miss = Counter((it["final_class"], it["status"]) for it in ref if it["outlet"] == o and it["status"] != "in_corpus")
        summary[o] = {"corpus_window": dict(cw.get(o, {})), "missing_found": {f"{a}|{b}": v for (a, b), v in miss.items()},
                      "extrapolation": ext.get(o)}
    (C.DATA / country / "08-recall-audit" / "raw" / "census-summary.json").write_text(json.dumps({"summary": summary, "ext": ext}, ensure_ascii=False, indent=1))
    tab = recall_tables(items, outlets)
    (C.DATA / country / "08-recall-audit" / "raw" / "recall-tables.json").write_text(json.dumps(tab, ensure_ascii=False, indent=1))
    for k, v in tab.items():
        if v["n"]:
            print(k, v)
    json.dump({k: {kk: vv for kk, vv in it.items() if kk != "lead"} for k, it in items.items()},
              open(C.DATA / country / "08-recall-audit" / "raw" / "items.json", "w"), ensure_ascii=False)


if __name__ == "__main__":
    main()
