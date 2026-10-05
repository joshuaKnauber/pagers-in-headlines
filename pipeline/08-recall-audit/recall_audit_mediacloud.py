#!/usr/bin/env python3
"""Recall audit route: Media Cloud full-text search (onlinenews-mediacloud).

Usage: recall_audit_mediacloud.py sources            -> resolve source ids
       recall_audit_mediacloud.py stories            -> pager-term story lists per outlet
       recall_audit_mediacloud.py topic              -> Hezbollah/Lebanon topic story counts+lists
Key read from repo-root .env (MEDIACLOUD_API_KEY); never printed.
Throttle: ~7s between requests, exponential backoff on 429.
Outputs (raw JSON per query) under data/<country>/08-recall-audit/raw/mediacloud/.
"""
import json, sys, time, urllib.parse, urllib.request, urllib.error
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2] / "data"
REPO = ROOT.parent
KEY = next(l.split("=", 1)[1].strip().strip('"').strip("'") for l in open(REPO / ".env")
           if l.startswith("MEDIACLOUD_API_KEY="))
HDR = {"Authorization": f"Token {KEY}", "Accept": "application/json",
       "User-Agent": "mediacloud-python/4 pager-news-research"}
API = "https://search.mediacloud.org/api"
OUTLETS = {
 "germany": {"tagesschau": "tagesschau.de", "zdfheute": "zdf.de", "zdfheute2": "zdfheute.de",
             "rtl": "rtl.de", "ntv": "n-tv.de", "bild": "bild.de", "spiegel": "spiegel.de",
             "welt": "welt.de", "tonline": "t-online.de", "rnd": "rnd.de"},
 "us": {"fox": "foxnews.com", "cnn": "cnn.com", "abc": "abcnews.go.com", "cbs": "cbsnews.com",
        "nbc": "nbcnews.com", "nyt": "nytimes.com", "wapo": "washingtonpost.com",
        "yahoo": "yahoo.com", "yahoo2": "news.yahoo.com", "usatoday": "usatoday.com",
        "ap": "apnews.com", "reuters": "reuters.com"},
}
Q = {
 "germany": 'Pager OR Pagern OR Pagers OR Piepser OR Piepsern OR Funkgeräte OR Funkgeräten OR Funkgerät '
            'OR Walkie OR Walkie-Talkies OR "Gold Apollo" OR Pager-Explosionen OR Pager-Angriff OR Pager-Angriffe',
 "us": 'pager OR pagers OR beeper OR beepers OR walkie-talkie OR walkie-talkies OR "walkie talkies" '
       'OR "walkie talkie" OR "Gold Apollo"',
}
TOPIC = {"germany": "Hisbollah OR Libanon OR Hezbollah", "us": "Hezbollah OR Lebanon"}
_last = [0.0]


def get(path, params):
    url = f"{API}{path}?{urllib.parse.urlencode(params)}"
    delay = 7
    for attempt in range(8):
        wait = _last[0] + 7 - time.time()
        if wait > 0:
            time.sleep(wait)
        _last[0] = time.time()
        try:
            r = urllib.request.urlopen(urllib.request.Request(url, headers=HDR), timeout=90)
            return json.loads(r.read().decode())
        except urllib.error.HTTPError as e:
            if e.code == 429 or e.code >= 500:
                time.sleep(delay); delay *= 2; continue
            raise RuntimeError(f"HTTP {e.code} {e.read()[:300]!r}")
        except Exception:
            time.sleep(delay); delay *= 2
    raise RuntimeError("gave up")


def out(country):
    d = ROOT / country / "08-recall-audit" / "raw" / "mediacloud"
    d.mkdir(parents=True, exist_ok=True)
    return d


def sources():
    for c, m in OUTLETS.items():
        res = {}
        for k, dom in m.items():
            d = get("/sources/sources/", {"name": dom, "limit": 10})
            res[k] = [{kk: s.get(kk) for kk in ("id", "name", "label", "homepage", "platform",
                                                  "stories_per_week", "first_story")}
                      for s in d.get("results", [])]
            print(c, k, [(s["id"], s["name"], s["stories_per_week"]) for s in res[k]], flush=True)
        json.dump(res, open(out(c) / "sources.json", "w"), indent=1)


def pick(c):
    src = json.load(open(out(c) / "sources.json"))
    ids = {}
    for k, lst in src.items():
        dom = OUTLETS[c][k]
        good = [s for s in lst if (s["name"] or "").lower() in (dom, "www." + dom, "m." + dom)]
        key = k.rstrip("2")
        for s in good:
            if str(s["id"]) not in ids.get(key, []):
                ids[key] = ids.get(key, []) + [str(s["id"])]
    return ids


def story_list(c, name, ids, q, tag, start="2024-09-17", end="2024-09-25"):
    params = {"q": q, "start": start, "end": end, "platform": "onlinenews-mediacloud",
              "ss": ",".join(ids)}
    tot = get("/search/total-count", params)
    stories, tok = [], None
    while True:
        p = dict(params)
        if tok:
            p["pagination_token"] = tok
        d = get("/search/story-list", p)
        stories += d.get("stories", [])
        tok = d.get("pagination_token")
        if not tok or not d.get("stories"):
            break
    json.dump({"query": q, "sources": ids, "total": tot, "stories": stories},
              open(out(c) / f"{tag}-{name}.json", "w"), indent=1, ensure_ascii=False, default=str)
    print(c, name, tag, "total", tot, "got", len(stories), flush=True)


if __name__ == "__main__":
    mode = sys.argv[1]
    if mode == "sources":
        sources()
    else:
        for c in OUTLETS:
            for name, ids in pick(c).items():
                if mode == "stories":
                    story_list(c, name, ids, Q[c], "pager")
                elif mode == "topic":
                    story_list(c, name, ids, TOPIC[c], "topic")
