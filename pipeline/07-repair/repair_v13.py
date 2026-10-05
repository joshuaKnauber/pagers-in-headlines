#!/usr/bin/env python3
"""Corpus v1.3 repair pass (2026-10-05, recall-audit fixes).

Edits data/<country>/06-corpus/corpus.jsonl in place. Records that do not belong
in the corpus move to 06-corpus/excluded.jsonl with an `exclusion` reason.
Every touched record gets a `*_v13` warning. Stages:

lebanon: drop off-topic LBCI earbuds item and the Oct 6 Al Jadeed radio-interception
         item; Al Jadeed Clemenceau near-duplicate pair; MTV dates bounded by
         neighbouring IDs' first captures; NNA dates and body from the page;
         Al-Manar martyr notices -> relevance `context`.
israel:  drop the Sep 23 evacuation-calls item and the Damascus car-bomb post;
         N12 podcast page retyped; N12 date from article:published_time;
         Abu Ali 75653 (12:57 UTC, first pager post) + two reposts added from the
         live Telegram preview fetched by the recall audit.
germany: RND article versions (same article ID, slug changed) linked, later
         version primary; related records without device wording -> `context`;
         t-online newsblog and ntv der_tag entries retyped.
us:      CNN/CBS records without device wording -> `context`; out-of-window and
         out-of-scope records dropped; 36-word Yahoo item retyped `brief`.
ap:      (network) re-collect the 23 AP candidates from Wayback (every live fetch
         had returned a Cloudflare challenge page) and add the relevant ones.
claims:  drop catalogue seeds that point at excluded records.
fixups:  v1.3.1, after the adversarial review of v1.3 (2026-10-05): two exclusions and
         three `context` downgrades reversed, Abu Ali reply posts given their own text,
         Spiegel paywall leads from the page description, AP syndication credits on ABC
         and Yahoo copies, AP editor's notes cut, timestamp and hash conventions.

Run: python3 pipeline/07-repair/repair_v13.py <stage|all> [--dry]
     ('all' runs every stage except ap, then fixups; ap needs the network)
"""
import csv, hashlib, html as H, json, re, shutil, subprocess, sys, time
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2] / "data"
PIPE = Path(__file__).resolve().parents[1]
DRY = "--dry" in sys.argv
EVENT_DAY = date(2024, 9, 17)
V = "1.3"
DEVICE_RE = re.compile(r"pager|piepser|funkger|walkie|beeper|gold apollo|kommunikations(?:technik|ausr[üu]stung|ger[äa]t)"
                       r"|elektronische(?:n)? ger[äa]t|exploding device|communication device"
                       r"|بيجر|بايجر|أجهزة (?:ال)?اتصال|اللاسلكي|ביפר|זימונית|מכשירי קשר", re.I)


def slot(pub):
    d = (date.fromisoformat(pub[:10]) - EVENT_DAY).days
    if d < 0: return "pre_event"
    if d <= 7: return f"day_{d}"
    if d <= 14: return "week_2"
    if d <= 30: return "first_month"
    return "tail"


class Corpus:
    def __init__(self, country):
        self.country = country
        self.path = ROOT / country / "06-corpus" / "corpus.jsonl"
        self.xpath = ROOT / country / "06-corpus" / "excluded.jsonl"
        self.recs = [json.loads(l) for l in open(self.path, encoding="utf-8")]
        self.excluded = [json.loads(l) for l in open(self.xpath, encoding="utf-8")] if self.xpath.exists() else []
        self.log = []

    def get(self, did):
        for r in self.recs:
            if r["document_id"] == did:
                return r
        if any(r["document_id"] == did for r in self.excluded):
            return None  # already excluded on an earlier run
        raise KeyError(did)

    def warn(self, r, w):
        if w not in r["extraction"]["warnings"]:
            r["extraction"]["warnings"].append(w)

    def exclude(self, did, reason):
        r = self.get(did)
        if r is None or "restored_v131" in r["extraction"]["warnings"]:  # reversed by the v1.3.1 fixups
            return
        self.recs.remove(r)
        r["exclusion"] = {"version": V, "reason": reason}
        self.excluded.append(r)
        self.log.append(f"exclude  {did}: {reason}")

    def context(self, did, why):
        try:
            r = self.get(did)
        except KeyError:  # listed by a later audit run (e.g. an AP record) but not in this corpus state
            self.log.append(f"skip     {did}: not in corpus")
            return
        if r is None or r["extraction"]["relevance"] == "context" or \
                "relevance_restored_v131" in r["extraction"]["warnings"]:
            return
        text = r["content"]["headline"] + " " + r["content"]["body"]
        if DEVICE_RE.search(text):  # the audit's term list is narrower; never downgrade a record that names the devices
            self.log.append(f"keep     {did}: device wording found ({DEVICE_RE.search(text).group(0)})")
            return
        self.log.append(f"context  {did} (was {r['extraction']['relevance']}): {why}")
        r["extraction"]["relevance"] = "context"
        self.warn(r, "relevance_context_v13")

    def retype(self, did, t):
        r = self.get(did)
        if r is None or r["publication"]["document_type"] == t:
            return
        self.log.append(f"retype   {did}: {r['publication']['document_type']} -> {t}")
        r["publication"]["document_type"] = t
        self.warn(r, "retyped_v13")

    def date(self, did, d, source, published_time=None):
        r = self.get(did)
        if r is None:
            return
        p = r["publication"]
        if p["published_at"] == d and p["date_source"] == source:
            return
        self.log.append(f"date     {did}: '{p['published_at']}' -> {d} ({source})")
        p.update(published_at=d, date_source=source, time_slot=slot(d))
        if published_time:
            p["published_time"] = published_time
        w = r["extraction"]["warnings"]
        if "date_missing" in w:
            w.remove("date_missing")
        self.warn(r, "dated_v13")

    def set_body(self, did, body, why, language=None):
        r = self.get(did)
        if r is None or r["content"]["body"] == body:
            return
        c = r["content"]
        self.log.append(f"body     {did}: {c['word_count']} -> {len(body.split())} words ({why})")
        c.update(body=body, word_count=len(body.split()),
                 body_sha256=hashlib.sha256(body.encode()).hexdigest())
        if language:
            r["source"]["language"] = language
        self.warn(r, f"body_{why}_v13")

    def secondary(self, did, primary_id, kind):
        """kind: 'near_duplicate' (same item, posted twice) or 'earlier_version' (same article, updated)."""
        r = self.get(did)
        if r is None:
            return
        d = r["deduplication"]
        if not d["is_primary_record"] and d.get("version_of") == primary_id:
            return
        d.update(is_primary_record=False, version_of=primary_id, relation=kind)
        self.warn(r, f"{kind}_v13")
        self.log.append(f"{kind:9.9s} {did} -> primary {primary_id}")

    def restore(self, did, why):
        for r in list(self.excluded):
            if r["document_id"] == did:
                self.excluded.remove(r)
                r.pop("exclusion", None)
                self.warn(r, "restored_v131")
                self.recs.append(r)
                self.log.append(f"restore  {did}: {why}")

    def relevance(self, did, rel, why):
        r = self.get(did)
        if r is None or r["extraction"]["relevance"] == rel:
            return
        self.log.append(f"relevance {did}: {r['extraction']['relevance']} -> {rel} ({why})")
        r["extraction"]["relevance"] = rel
        w = r["extraction"]["warnings"]
        if "relevance_context_v13" in w:
            w.remove("relevance_context_v13")
        self.warn(r, "relevance_restored_v131")

    def save(self):
        n_prim = sum(r["deduplication"]["is_primary_record"] for r in self.recs)
        print(f"--- {self.country}: {len(self.log)} changes | {len(self.recs)} records, {n_prim} primary, "
              f"{len(self.excluded)} excluded")
        for l in self.log:
            print("  ", l)
        if DRY:
            print("   [dry] not writing")
            return
        with open(self.path, "w", encoding="utf-8") as f:
            for r in self.recs:
                f.write(json.dumps(r, ensure_ascii=False) + "\n")
        if self.excluded:
            with open(self.xpath, "w", encoding="utf-8") as f:
                for r in self.excluded:
                    f.write(json.dumps(r, ensure_ascii=False) + "\n")


def audit_issues(country, issue_prefix):
    p = ROOT / country / "08-recall-audit" / "raw" / "corpus-issues.csv"
    return [r for r in csv.DictReader(open(p, encoding="utf-8")) if r["issue"].startswith(issue_prefix)]


def lebanon():
    C = Corpus("lebanon")
    C.exclude("lb_lbci_797960", "off-topic: wireless earbuds and hearing loss; matched on لاسلكية (wireless)")
    C.exclude("lb_aljadeed_507118", "different event: Oct 6 Washington Post report that Israel intercepted "
              "Hezbollah radio traffic for nine years, not the device attack")
    # Clemenceau walkie-talkie brief posted twice; 502819 is the misspelt repost ("تفـ جير").
    # 502553 / 502564 (listed by the audit) stay apart: different items 17 minutes apart
    # (open-coverage programme notice vs. news brief).
    C.secondary("lb_aljadeed_502819", "lb_aljadeed_502815", "near_duplicate")
    C.set_body("lb_aljadeed_502815", "", "emptied_iframe_chrome")
    # MTV: own first capture and neighbouring IDs' first captures bound the date
    C.date("lb_mtv_1490054", "2024-09-26", "id-capture-bounded-v13")
    C.date("lb_mtv_1490462", "2024-09-27", "id-capture-bounded-v13")
    # NNA: date line on the page; 722276's stored body was unrelated English text
    C.date("lb_nna_722276", "2024-09-18", "page-dateline-v13")
    t = open(ROOT / "lebanon" / C.get("lb_nna_722276")["capture"]["raw_path"], encoding="utf-8", errors="ignore").read() \
        if C.get("lb_nna_722276") else ""
    if t:
        i = t.find("وطنية - حذر الكرملين", t.find("الأربعاء 18 أيلول 2024   الساعة 12:57"))  # article body after its dateline
        seg = re.sub(r"<[^>]+>", " ", t[i:i + 3000])
        body = " ".join(H.unescape(seg).replace("\xa0", " ").split())
        body = body[:body.find("====")].strip() if "====" in body else body
        assert body.startswith("وطنية - حذر الكرملين") and "بيسكوف" in body, body[:200]
        C.set_body("lb_nna_722276", body, "from_page", language="ar")
    C.date("lb_nna_722542", "2024-09-19", "page-timestamp-v13", published_time="2024-09-19T08:21:22")
    for r in list(C.recs):
        if any("martyr_notice" in w for w in r["extraction"]["warnings"]):
            C.context(r["document_id"], "martyr notice; names no device on the page")
    C.save()


def israel():
    C = Corpus("israel")
    C.exclude("il_ynet_35be01752a", "different event: Sep 23 reports that Israel hacked radio stations and phoned "
              "residents of south Lebanon to evacuate")
    C.exclude("il_abuali_75669", "separate incident: Saberin report of an explosive charge in a car in Damascus; "
              "no device named")
    C.retype("il_n12_ae690238dc", "podcast_page")
    C.date("il_n12_42fc90d847", "2024-09-17", "meta-repair-v13", published_time="2024-09-17T19:00:00Z")
    # Abu Ali first pager post and the two replies to it, from the live t.me/s preview
    live = {r["post_id"]: r for r in csv.DictReader(open(ROOT / "israel/08-recall-audit/raw/abuali-live-messages.csv",
                                                          encoding="utf-8"))}
    page = ROOT / "israel/08-recall-audit/raw/abuali/a0bedcf293cca3cc.html"
    raw_rel = "raw/abuali/live-a0bedcf293cca3cc.html"
    have = {r["document_id"] for r in C.recs}
    for pid, primary in (("75653", True), ("75655", True), ("75656", True)):
        did = f"il_abuali_{pid}"
        if did in have:
            continue
        m = live[pid]
        assert f"abualiexpress/{pid}" in page.read_text(encoding="utf-8", errors="ignore")
        body = m["text"]
        bh = hashlib.sha256(body.encode()).hexdigest()
        rec = {"schema_version": "1.1.0-phase1", "document_id": did, "event_id": "lebanon_pager_attacks_2024",
               "source": {"page_publisher": "abuali", "country_or_media_system": "Israel", "language": "he"},
               "publication": {"published_at": m["datetime"][:10], "date_source": "telegram-ts",
                               "time_slot": slot(m["datetime"]), "document_type": "telegram_post",
                               "canonical_url": f"https://t.me/abualiexpress/{pid}", "published_time": m["datetime"]},
               "content": {"headline": body, "body": body, "word_count": len(body.split()), "body_sha256": bh},
               "provenance": {"credit": "", "content_origin": "local_or_unspecified"},
               "capture": {"collection_route": "live-telegram-preview", "raw_path": raw_rel},
               "extraction": {"method": "telegram-live-preview", "relevance": "strong", "warnings": ["added_v13"]},
               "deduplication": {"exact_duplicate_cluster_id": f"x{bh[:10]}", "is_primary_record": primary}}
        if not primary:
            rec["deduplication"].update(version_of="il_abuali_75653", relation="repost")
        C.recs.append(rec)
        C.log.append(f"add      {did} ({m['datetime']})")
    if not DRY and not (ROOT / "israel" / raw_rel).exists():
        (ROOT / "israel/raw/abuali").mkdir(parents=True, exist_ok=True)
        shutil.copyfile(page, ROOT / "israel" / raw_rel)
    C.save()


def germany():
    C = Corpus("germany")
    # same RND article ID under two slugs: the article was updated and renamed. Later dateModified is primary.
    for older, newer in (("8077ee3c89", "2976713b85"), ("9bfa7a57f3", "9839d97395"),
                         ("a34b40e8b3", "01d7465f51"), ("e494be678a", "8a981c41ba")):
        C.secondary(f"ge_rnd_{older}", f"ge_rnd_{newer}", "earlier_version")
    for r in audit_issues("germany", "off-topic"):
        C.context(r["document_id"], "no pager/walkie-talkie/device wording in headline or body")
    C.retype("ge_tonline_1e9c010a33", "live_blog")
    for r in C.recs:
        if "/der_tag/" in r["publication"]["canonical_url"] and r["publication"]["document_type"] in ("article", "flash_or_lead"):
            C.retype(r["document_id"], "live_ticker")
    C.save()


def us():
    C = Corpus("us")
    for r in audit_issues("us", "off-topic"):
        C.context(r["document_id"], "no pager/walkie-talkie/device wording in headline or body")
    C.exclude("us_cbs_deca8d7e0f", "out of window: published 2024-10-31 (window ends Oct 17)")
    C.exclude("us_nbc_d7d1591943", "out of window: published 2024-10-29 (window ends Oct 17)")
    C.exclude("us_cbs_b6fde07557", "out of scope: CBS Chicago local station page, not CBS News")
    for did, ed in (("us_yahoo_6b6ad5ce8c", "Yahoo Canada"), ("us_yahoo_ae4f6eb3f5", "Yahoo Finance"),
                    ("us_yahoo_e4c4db9ea5", "Yahoo Singapore")):
        C.exclude(did, f"out of scope: {ed} edition, not Yahoo News US")
    C.retype("us_yahoo_5f33d95679", "brief")
    C.save()


def curl(url, timeout=60):
    p = subprocess.run(["curl", "-sL", "--compressed", "-m", str(timeout), "-A",
                        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) "
                        "Chrome/126.0 Safari/537.36", url], capture_output=True)
    return p.stdout.decode("utf-8", "replace") if p.returncode == 0 else ""


def ap_body(h):
    """AP story container: <div class="RichTextStoryBody"> up to the author box / Page-below.
    The generic p-cluster also catches the menu and embedded related-story promos."""
    i = h.find('class="RichTextStoryBody')
    if i < 0:
        return ""
    ends = [j for j in (h.find("Page-authorInfo", i), h.find('class="Page-below"', i)) if j > 0]
    seg = h[i:min(ends)] if ends else h[i:]
    seg = re.sub(r"<script.*?</script>|<style.*?</style>|<bsp-list-loadmore.*?</bsp-list-loadmore>|<figure.*?</figure>",
                 " ", seg, flags=re.S | re.I)
    ps = (" ".join(H.unescape(re.sub(r"<[^>]+>", " ", p)).split()) for p in re.findall(r"<p[^>]*>(.*?)</p>", seg, re.S))
    return "\n".join(p for p in ps if p)


def ap():
    """Re-collect AP candidates from Wayback, update candidates.jsonl, add relevant ones to the corpus."""
    sys.path.insert(0, str(PIPE / "05-extraction"))
    sys.path.insert(0, str(PIPE / "06-normalization"))
    sys.path.insert(0, str(PIPE / "08-recall-audit"))
    sys.argv = sys.argv[:1]
    import extract_de_us as X
    import normalize_de_us as N
    from recall_audit_common import key, has_mention
    D = ROOT / "us"
    cpath = D / "05-extraction" / "candidates.jsonl"
    cands = [json.loads(l) for l in open(cpath, encoding="utf-8")]
    cache = {}
    for l in open(D / "08-recall-audit/raw/verify-cache.jsonl", encoding="utf-8"):
        v = json.loads(l)
        cache[v["key"]] = v
    C = Corpus("us")
    have = {r["publication"]["canonical_url"] for r in C.recs} | {r["publication"]["canonical_url"] for r in C.excluded}
    STRONG_TERMS = ["pager", "beeper", "walkie", "gold apollo", "gold-apollo", "icom"]
    for r in cands:
        if r["outlet"] != "ap" or r.get("fetch_route") == "wayback-v13":
            continue
        dig = hashlib.sha256(r["url"].encode()).hexdigest()[:16]
        h, ts = "", ""
        v = cache.get(key(r["url"]))
        if v and v.get("fetch", "").startswith("wayback") and v.get("raw_file"):
            h, ts = (D / v["raw_file"]).read_text(encoding="utf-8", errors="ignore"), v.get("capture_ts", "")
        else:
            q = ("https://web.archive.org/cdx/search/cdx?url=" + r["url"] + "&from=20240917&to=20241031"
                 "&filter=statuscode:200&fl=timestamp&limit=5&output=json")
            try:
                rows = json.loads(curl(q, 60) or "[]")[1:]
            except Exception:
                rows = []
            if rows:
                ts = rows[0][0]
                time.sleep(3)
                h = curl(f"https://web.archive.org/web/{ts}id_/{r['url']}", 90)
        if not h or "Just a moment" in X.title_of(h):
            print(f"   no usable capture: {r['url']}")
            continue
        ld = X.ldjson(h)
        cont = ap_body(h)
        body = " ".join((ld.get("body") or cont or X.pcluster(h)).split())
        method = "ld-json" if ld.get("body") else "ap-container" if cont else "p-cluster"
        title = ld.get("headline") or X.title_of(h)
        rel = X.relevance(title + " " + body[:6000], "us")
        r.update(fetch_route="wayback-v13", capture_ts=ts, raw_path=f"raw/ap/{dig}.html", title=title,
                 published_at=ld.get("date", ""), date_source="ld-json" if ld.get("date") else "",
                 body_words=len(body.split()), body_text=body[:20000], extract_method=method, relevance=rel)
        if not DRY:
            (D / "raw/ap" / f"{dig}.html").write_text(h, encoding="utf-8")
        C.log.append(f"refetch  ap {ts} {rel:8} {r['published_at']} {title[:70]}")
        # same rules as normalize_de_us.main
        if rel == "strong" and not any(k in (title + " " + body[:1500]).lower() for k in STRONG_TERMS):
            rel = r["relevance"] = "related"
        pub = r["published_at"]
        if rel not in ("strong", "related") or r["url"] in have:
            continue
        if "/live/" in r["url"]:
            C.log.append("   deferred to the gap fill: live blog (to be split into timestamped entries)")
            continue
        if not has_mention(title + " " + body, "us"):
            rel = "context"
        if pub and not ("2024-09-17" <= pub[:10] <= "2024-10-17"):
            C.log.append(f"   skip out of window {pub}")
            continue
        bh = hashlib.sha256(body.encode()).hexdigest() if body else ""
        dt = "video_page" if "/video/" in r["url"] else (
            "flash_or_lead" if len(body.split()) < 90 else "article")
        C.recs.append({"schema_version": "1.1.0-phase1",
            "document_id": f"us_ap_{hashlib.sha256(r['url'].encode()).hexdigest()[:10]}",
            "event_id": "lebanon_pager_attacks_2024",
            "source": {"page_publisher": "ap", "country_or_media_system": "United States",
                       "language": N.lang(title + " " + body, "us")},
            "publication": {"published_at": pub, "date_source": r["date_source"], "time_slot": slot(pub) if pub else "",
                            "document_type": dt, "canonical_url": r["url"]},
            "content": {"headline": title, "body": body, "word_count": len(body.split()), "body_sha256": bh},
            "provenance": {"credit": "AP", "content_origin": "wire_original"},
            "capture": {"collection_route": f"wayback:{ts}", "raw_path": f"raw/ap/{dig}.html"},
            "extraction": {"method": r["extract_method"], "relevance": rel,
                           "warnings": ["added_v13_ap_wayback"] + ([] if pub else ["date_missing"])},
            "deduplication": {"exact_duplicate_cluster_id": f"x{bh[:10]}" if bh else "", "is_primary_record": True}})
        C.log.append(f"add      us_ap ({dt}, {len(body.split())} words)")
    # AP video pages have no story container: the p-cluster fallback is site menu only -> headline-only record
    for r in C.recs:
        if r["source"]["page_publisher"] == "ap" and r["publication"]["document_type"] == "video_page" \
                and r["extraction"]["method"] == "p-cluster":
            C.set_body(r["document_id"], "", "emptied_page_chrome")
    if not DRY:
        with open(cpath, "w", encoding="utf-8") as f:
            for r in cands:
                f.write(json.dumps(r, ensure_ascii=False) + "\n")
    C.save()


def claims():
    excluded = set()
    for c in ("lebanon", "israel", "germany", "us"):
        p = ROOT / c / "06-corpus" / "excluded.jsonl"
        if p.exists():
            excluded |= {json.loads(l)["document_id"] for l in open(p, encoding="utf-8")}
    p = ROOT / "cross-country/09-claims/claim-catalogue.jsonl"
    cl = [json.loads(l) for l in open(p, encoding="utf-8")]
    n = 0
    for c in cl:
        keep = [s for s in c["corpus_seed_examples"] if s not in excluded]
        if keep != c["corpus_seed_examples"]:
            print(f"   claims: {c['claim_id']} drops {set(c['corpus_seed_examples']) - set(keep)}")
            c["corpus_seed_examples"] = keep
            n += 1
    print(f"--- claims: {n} claims changed")
    if not DRY and n:
        with open(p, "w", encoding="utf-8") as f:
            for c in cl:
                f.write(json.dumps(c, ensure_ascii=False) + "\n")


def fixups():
    """v1.3.1: findings of the adversarial review of v1.3."""
    C = Corpus("lebanon")
    C.restore("lb_aljadeed_507118", "about the attack: Al Jadeed relays the Washington Post's Oct 5-6 investigation "
              "(Israel listened in on Hezbollah walkie-talkies for 9 years and kept the option to turn them into bombs)")
    for r in C.recs:
        if r["content"]["body"] == "" and r["content"]["body_sha256"] == "":
            r["content"]["body_sha256"] = hashlib.sha256(b"").hexdigest()
    r = C.get("lb_nna_722542")
    if r["publication"].get("published_time") == "2024-09-19T08:21:22":
        r["publication"]["published_time"] = "2024-09-19T08:21:22Z"
        C.log.append("time     lb_nna_722542: published_time in UTC with Z, as on the page")
    C.save()

    C = Corpus("israel")
    C.restore("il_abuali_75669", "probably the Syrian part of the attack (13:35 UTC, amid the pager posts; the channel's "
              "75676 at 14:03 links explosions in Syria to Hezbollah pagers)")
    C.relevance("il_abuali_75669", "related", "possible Syrian wave of the device attack")
    C.warn(C.get("il_abuali_75669"), "possible_syrian_wave_v131")
    live = {r["post_id"]: r for r in csv.DictReader(open(ROOT / "israel/08-recall-audit/raw/abuali-live-messages.csv",
                                                          encoding="utf-8"))}
    for pid in ("75655", "75656"):  # replies to 75653, not reposts; v1.3 took the quoted text
        r = C.get(f"il_abuali_{pid}")
        own = live[pid]["text"]
        assert "הזימונית" in own and own != live["75653"]["text"]
        if r["content"]["body"] != own or not r["deduplication"]["is_primary_record"]:
            bh = hashlib.sha256(own.encode()).hexdigest()
            r["content"].update(headline=own, body=own, word_count=len(own.split()), body_sha256=bh)
            r["deduplication"] = {"exact_duplicate_cluster_id": f"x{bh[:10]}", "is_primary_record": True}
            C.warn(r, "text_fixed_reply_post_v131")
            C.log.append(f"text     il_abuali_{pid}: own text of a reply to 75653, now primary")
    C.warn(C.get("il_abuali_75653"), "live_text_post_edit_v131")  # live page marks the post as edited
    r = C.get("il_n12_42fc90d847")
    if r["publication"].get("published_time") == "2024-09-17T19:00:00Z":
        r["publication"]["published_time"] = "2024-09-17T22:00+0300"
        C.log.append("time     il_n12_42fc90d847: published_time in N12's +0300 format")
    C.save()

    C = Corpus("germany")
    C.relevance("ge_spiegel_0c74f9ad5e", "strong", "page lead: 'Im Libanon sind zahlreiche Walkie-Talkies explodiert'")
    C.relevance("ge_tagesschau_5d524e455b", "related", "body: 'Nach den tödlichen Angriffen auf Kommunikationstechnik'")
    C.relevance("ge_zdfheute_ad2e30a014", "related", "body: 'Explosion von Kommunikationsausrüstung im Libanon'")
    for did in ("ge_spiegel_0c74f9ad5e", "ge_spiegel_8be8faca25", "ge_spiegel_56bd1c4430", "ge_spiegel_eb13e72e65",
                "ge_spiegel_176d1e0d56"):  # SPIEGEL+ shells: the free page shows the lead, kept in meta description
        r = C.get(did)
        if r["content"]["body"]:
            continue
        t = open(ROOT / "germany" / r["capture"]["raw_path"], encoding="utf-8", errors="ignore").read()
        m = re.search(r'<meta[^>]+name="description"[^>]+content="([^"]*)"', t)
        C.set_body(did, " ".join(H.unescape(m.group(1)).split()), "lead_from_meta")
    C.save()

    C = Corpus("us")
    for r in C.recs:
        if r["content"]["body"] == "" and r["content"]["body_sha256"] == "":
            r["content"]["body_sha256"] = hashlib.sha256(b"").hexdigest()
    for did in ("us_abc_fd43fc1794", "us_yahoo_3820a5161a"):  # ~99% identical to us_ap_00afe7047e
        r = C.get(did)
        if r["provenance"]["credit"] != "AP":
            r["provenance"] = {"credit": "AP", "content_origin": "syndicated_or_adapted"}
            C.warn(r, "credit_v131")
            C.log.append(f"credit   {did}: AP, syndicated")
    note = "More explosions have been reported in Lebanon following the pager attack Tuesday. Follow AP’s live updates. "
    for r in C.recs:
        if r["source"]["page_publisher"] == "ap" and r["content"]["body"].startswith(note):
            C.set_body(r["document_id"], r["content"]["body"][len(note):], "editor_note_cut")
    C.save()


STAGES = {"lebanon": lebanon, "israel": israel, "germany": germany, "us": us, "ap": ap, "claims": claims,
          "fixups": fixups}

if __name__ == "__main__":
    arg = sys.argv[1]
    for s in (["lebanon", "israel", "germany", "us", "claims", "fixups"] if arg == "all" else [arg]):
        STAGES[s]()
