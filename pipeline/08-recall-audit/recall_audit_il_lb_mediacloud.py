#!/usr/bin/env python3
"""Recall audit (Israel + Lebanon): Media Cloud full-text discovery route.

Media Cloud's online-news collector is an independent discovery route (RSS /
sitemap ingestion, not Wayback CDX, not GDELT). Full-text search over the
stories it holds, per source id, for Sep 17-24 2024.

Usage:
  recall_audit_il_lb_mediacloud.py sources            -> resolve source ids
  recall_audit_il_lb_mediacloud.py probe <sid> <q>    -> total-count for one query
  recall_audit_il_lb_mediacloud.py stories <country>  -> story lists for all queries
Key is read from the repo-root .env (MEDIACLOUD_API_KEY) and never printed.
Throttle: >= 7 s between requests, exponential backoff on 429 (key is shared).
"""
import csv, json, sys, time, urllib.parse, urllib.request, urllib.error
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "data"
API = "https://search.mediacloud.org/api"
START, END = "2024-09-17", "2024-09-24"
GAP = 7.5
_last = [0.0]


def key():
    for line in (ROOT / ".env").read_text().splitlines():
        if line.strip().startswith("MEDIACLOUD_API_KEY"):
            return line.split("=", 1)[1].strip().strip('"').strip("'")
    raise SystemExit("no key")


HDR = {"Authorization": f"Token {key()}", "Accept": "application/json",
       "User-Agent": "mediacloud-python/4 pager-news-research"}


def call(path, params):
    url = f"{API}/{path}?" + urllib.parse.urlencode(params)
    for attempt in range(8):
        wait = GAP - (time.time() - _last[0])
        if wait > 0:
            time.sleep(wait)
        _last[0] = time.time()
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=HDR), timeout=120) as r:
                return json.loads(r.read())
        except urllib.error.HTTPError as e:
            if e.code == 429 or e.code >= 500:
                time.sleep(20 * (attempt + 1))
                continue
            raise RuntimeError(f"HTTP {e.code}: {e.read()[:300]!r}")
        except Exception:
            time.sleep(15 * (attempt + 1))
    raise RuntimeError("gave up")


DOMAINS = {
    "israel": ["ynet.co.il", "mako.co.il", "n12.co.il", "kikar.co.il", "kan.org.il", "makan.org.il"],
    "lebanon": ["mtv.com.lb", "lbcgroup.tv", "aljadeed.tv", "almanar.com.lb", "nna-leb.gov.lb",
                "al-akhbar.com", "nidaalwatan.com", "annahar.com", "lorientlejour.com", "lorientoday.com"],
}
QUERIES = {
    "israel": {
        "he_devices": 'ביפר OR ביפרים OR הביפרים OR "מכשירי קשר" OR "מכשירי הקשר" OR זימונית OR זימוניות OR איתורית OR איתוריות OR "ווקי טוקי"',
        "ar_devices": 'بيجر OR البيجر OR البايجر OR بايجر OR اللاسلكي OR "أجهزة الاتصال" OR "اجهزة الاتصال" OR pager OR pagers',
    },
    "lebanon": {
        "ar_devices": 'بيجر OR البيجر OR البايجر OR بايجر OR البيجرز OR اللاسلكي OR "أجهزة الاتصال" OR "اجهزة الاتصال" OR "أجهزة النداء" OR "اجهزة النداء" OR pager OR pagers OR "walkie-talkie" OR "walkie-talkies" OR bipeurs OR bipeur OR talkies-walkies',
        "ar_massacre": '"مجزرة الثلاثاء" OR "مجزرة الأربعاء" OR "العدوان السيبراني" OR "الاعتداء السيبراني" OR "الخرق الأمني" OR "التفجيرات"',
    },
}


def sources():
    out = {}
    for c, doms in DOMAINS.items():
        for d in doms:
            res = call("sources/sources/", {"name": d, "limit": 5})
            cands = [(r.get("id"), r.get("name"), r.get("stories_per_week"), r.get("platform")) for r in res.get("results", [])]
            print(c, d, cands, flush=True)
            out[d] = cands
    p = DATA / "israel" / "08-recall-audit" / "raw" / "mediacloud-sources.json"
    p.write_text(json.dumps(out, ensure_ascii=False, indent=1))


def count(sid, q, start=START, end=END):
    return call("search/total-count", {"q": q, "start": start, "end": end,
                                       "platform": "onlinenews-mediacloud", "ss": sid})


def stories(country, sids):
    outp = DATA / country / "08-recall-audit" / "raw" / "mediacloud-stories.csv"
    w = csv.writer(outp.open("w", newline="", encoding="utf-8"))
    w.writerow(["domain", "source_id", "query", "publish_date", "title", "url", "indexed_date", "language"])
    for dom, sid in sids.items():
        for qn, q in QUERIES[country].items():
            tok, n = None, 0
            while True:
                params = {"q": q, "start": START, "end": END, "platform": "onlinenews-mediacloud", "ss": sid}
                if tok:
                    params["pagination_token"] = tok
                res = call("search/story-list", params)
                for s in res.get("stories", []):
                    w.writerow([dom, sid, qn, s.get("publish_date"), s.get("title"), s.get("url"),
                                s.get("indexed_date"), s.get("language")])
                    n += 1
                tok = res.get("pagination_token")
                if not tok:
                    break
            print(country, dom, qn, n, flush=True)


if __name__ == "__main__":
    cmd = sys.argv[1]
    if cmd == "sources":
        sources()
    elif cmd == "probe":
        print(json.dumps(count(sys.argv[2], sys.argv[3])))
    elif cmd == "stories":
        sids = json.loads(sys.argv[3])
        stories(sys.argv[2], sids)
