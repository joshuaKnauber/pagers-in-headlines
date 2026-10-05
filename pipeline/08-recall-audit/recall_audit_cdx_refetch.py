#!/usr/bin/env python3
"""Recall audit: second fetch attempt for pool items whose verification failed because the
Wayback capture nearest to 2024-09-20 was an archived error (Reuters 401, WaPo 403, 404s).

The plain `web/<ts>id_/<url>` lookup replays the nearest capture whatever its status. Reuters and
WaPo blocked the archive crawler for much of Sep 2024, so the nearest capture is often a 401/403
page even when a 200 capture exists. This script asks CDX for 200-status captures between
Sep 17 and Oct 1 2024, fetches the one closest to Sep 20, and appends a normal verify-cache entry
(same fields as recall_audit_build.verify_one). Live blogs are skipped (handled by build --liveblogs).

Usage: recall_audit_cdx_refetch.py us [outlet ...]
Polite: one request to archive.org at a time, >=2.5 s apart, backoff on refusals.
"""
import csv, hashlib, json, subprocess, sys, time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from recall_audit_common import *  # noqa
from recall_audit_build import curl, page_ok, RA

_last = [0.0]


def ia(url, timeout=90):
    for attempt in range(4):
        wait = _last[0] + 2.5 - time.time()
        if wait > 0:
            time.sleep(wait)
        _last[0] = time.time()
        body, code, eff = curl(url, timeout=timeout)
        if code == "000" or code.startswith("5") or code == "429":
            time.sleep(30 * (attempt + 1))
            continue
        return body, code, eff
    return "", "000", ""


def cdx_200(u):
    bare = re.sub(r"^https?://", "", u).split("?")[0]
    # timemap/json is CDX-backed but answers in ~1 s; /cdx/search/cdx took ~60 s per URL in Oct 2026
    q = (f"https://web.archive.org/web/timemap/json?url={urllib.parse.quote(bare, safe='/:')}"
         f"&from=20240917&to=20241001&filter=statuscode:200")
    body, code, _ = ia(q)
    if code != "200":
        return None, f"cdx:{code}"
    try:
        rows = json.loads(body or "[]")
    except Exception:
        return None, "cdx:bad-json"
    ts = [r[1] for r in rows[1:] if len(r) > 1 and r[1][:1].isdigit()]
    if not ts:
        return None, "cdx:no-200-capture"
    return min(ts, key=lambda t: abs(int(t[:12]) - 202409201200)), f"cdx:{len(ts)}x200"


def main(country, outlets):
    ra = RA(country)
    cache_f = ra / "raw" / "verify-cache.jsonl"
    done = {}
    for l in open(cache_f, encoding="utf-8"):
        r = json.loads(l)
        done[r["key"]] = r
    pool = list(csv.DictReader(open(ra / "raw" / "pool.csv", encoding="utf-8")))
    todo = [p for p in pool if done.get(p["key"], {}).get("fetch") == "FAILED"
            and (not outlets or p["outlet"] in outlets)
            and not (is_liveblog(p["url"], p["title"]) and not is_wire_feed(p["url"]))
            and ("cdx-refetch" not in done[p["key"]].get("tried", "") or done[p["key"]].get("url") != p["url"])]
    print(country, "refetch todo", len(todo), flush=True)
    out = open(cache_f, "a", encoding="utf-8")
    for i, p in enumerate(todo):
        url = p["url"].replace("washingtonpost.com//", "washingtonpost.com/").replace("foxnews.com//", "")
        prev = done[p["key"]].get("tried", "")
        res = dict(key=p["key"], outlet=p["outlet"], url=p["url"], fetch="FAILED", capture_ts="")
        ts, note = cdx_200(url)
        tried = f"{prev} cdx-refetch {note}"
        if ts:
            body, code, eff = ia(f"https://web.archive.org/web/{ts}id_/{url}")
            tried += f" wayback:{ts}:{code}"
            if page_ok(body, code, url, url):
                d = ra / "raw" / "pages" / p["outlet"]
                d.mkdir(parents=True, exist_ok=True)
                fn = d / (hashlib.sha256(p["url"].encode()).hexdigest()[:16] + f"-{ts}.html")
                fn.write_text(body, encoding="utf-8")
                ex = extract(body)
                mention, central, ev, an = assess(ex, country)
                res.update(fetch="wayback", capture_ts=ts, raw_file=str(fn.relative_to(ROOT / country)),
                           page_title=ex["title"][:300], page_date=ex["date"][:10], body_words=len(ex["body"].split()),
                           body_src=ex["body_src"], mention=mention, central=central, evidence=ev,
                           assess_note=an, live_ld=ex["live_ld"])
        res["tried"] = tried.strip()
        out.write(json.dumps(res, ensure_ascii=False) + "\n"); out.flush()
        print(i, p["outlet"], res["fetch"], res.get("mention"), note, p["url"][:100], flush=True)
    out.close()


if __name__ == "__main__":
    main(sys.argv[1], set(sys.argv[2:]))
