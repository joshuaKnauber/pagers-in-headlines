#!/usr/bin/env python3
"""Recall audit worker: fetch + extract + device-term check for a task list.

Usage: recall_audit_il_lb_check.py <country> <tasks.csv> <out.jsonl> [threads]
tasks.csv columns: outlet,url,route,discovery,extra
  route: live | wayback[:<ts>] | almanar-archive
Resumable (skips urls already in out.jsonl). Raw HTML cached under
data/<country>/08-recall-audit/raw/<outlet>/ (sha16 of fetched URL).
Hosts are throttled per host (archive.org 1 req/s globally in-process).
"""
import csv, json, sys, threading, urllib.parse
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import recall_audit_il_lb_common as C


def target(outlet, url, route):
    if route.startswith("wayback"):
        ts = route.split(":", 1)[1] if ":" in route else "20240918"
        return C.wayback_url(url, ts)
    if route == "almanar-archive":
        return (url.replace("://www.almanar.com.lb", "://archive.almanar.com.lb")
                   .replace("://almanar.com.lb", "://archive.almanar.com.lb"))
    return url


def run_one(country, t):
    outlet, url, route = t["outlet"], t["url"], t["route"]
    rawdir = C.DATA / country / "08-recall-audit" / "raw" / outlet
    tu = target(outlet, url, route)
    html, info = C.fetch(tu, rawdir)
    if html is None and route == "live":
        tu2 = C.wayback_url(url, "20240918")
        html, info2 = C.fetch(tu2, rawdir)
        info = f"{info}; wayback-fallback {info2}"
        if html is not None:
            tu = tu2
    rec = dict(t)
    rec.update({"key": C.url_key(url), "fetched": tu, "fetch_info": info})
    if html is None:
        rec.update({"ok": False})
        return rec
    ex = C.extract(outlet, html)
    nb, snips = C.device_hits(ex["body"])
    nt, _ = C.device_hits(ex["title"])
    nd, _ = C.device_hits(ex["desc"])
    rec.update({"ok": True, "title": ex["title"][:300], "date": ex["date"], "method": ex["method"],
                "body_words": len(ex["body"].split()), "hits_title": nt, "hits_body": nb, "hits_desc": nd,
                "snippets": snips, "class": C.classify(ex["title"], ex["body"]),
                "lead": " ".join(ex["body"].split()[:45]),
                "raw": str((rawdir / (C.hashlib.sha256(tu.encode()).hexdigest()[:16] + ".html")).relative_to(C.DATA / country))})
    return rec


def main():
    country, tasks_p, out_p = sys.argv[1], Path(sys.argv[2]), Path(sys.argv[3])
    nthreads = int(sys.argv[4]) if len(sys.argv) > 4 else 3
    tasks = list(csv.DictReader(open(tasks_p, encoding="utf-8")))
    done = set()
    if out_p.exists():
        for line in open(out_p, encoding="utf-8"):
            try:
                done.add(json.loads(line)["url"])
            except Exception:
                pass
    todo = [t for t in tasks if t["url"] not in done]
    print(f"{len(tasks)} tasks, {len(todo)} to do", flush=True)
    lock = threading.Lock()
    f = open(out_p, "a", encoding="utf-8")
    n = [0]

    def work(t):
        try:
            rec = run_one(country, t)
        except Exception as e:
            rec = dict(t, ok=False, fetch_info=f"exception {e}")
        with lock:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")
            f.flush()
            n[0] += 1
            if n[0] % 50 == 0:
                print(f"{n[0]}/{len(todo)}", flush=True)

    with ThreadPoolExecutor(nthreads) as ex:
        list(ex.map(work, todo))
    f.close()
    print("DONE", flush=True)


if __name__ == "__main__":
    main()
