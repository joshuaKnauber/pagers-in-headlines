#!/usr/bin/env python3
"""Build fetch/check task lists for the Israel/Lebanon recall audit.

Strata (one task per item key; discovery routes merged):
  gdelt        every GDELT GKG URL of a gate outlet (independent discovery)
  manifest-kw  enumerated in-window items NOT tagged by the original sweep whose
               title/slug carries a Hezbollah/Lebanon/escalation keyword
  manifest-untitled  enumerated in-window items whose sweep title was empty or
               a block page (N12 Radware, Makan empty) -> never triaged
  mtv-slugless MTV sitemap items in window (no slug -> never triaged)
  control      random sample of in-window, untagged, non-keyword items
               (leakage estimate)
Writes data/<country>/08-recall-audit/raw/tasks-<stratum>.csv
"""
import csv, glob, random, re, sys, urllib.parse
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import recall_audit_il_lb_common as C

random.seed(20240917)
KW_HE = ["חיזבאללה", "נסראללה", "לבנון", "לבנונ", "ביירות", "דאחי", "הסלמה", "מוסד", "איראן", "סייבר",
         "מבצע", "צפון", "חסן", "פיצוץ", "התפוצצ", "פצועים", "נפגעים", "גלנט", "הלבנונית", "מכשיר"]
KW_AR = ["حزب الله", "حزب-الله", "نصرالله", "نصر الله", "نصر-الله", "اسرائيل", "إسرائيل", "الإسرائيلي",
         "الاسرائيلي", "العدو", "الموساد", "الضاحية", "جرحى", "الجرحى", "شهداء", "الشهداء", "شهيد", "مستشفى",
         "المستشفيات", "انفجار", "تفجير", "انفجارات", "تفجيرات", "خرق", "السيبراني", "الأبيض", "الابيض",
         "وزير الصحة", "التصعيد", "تصعيد", "الحرب", "عدوان", "العدوان", "الدم", "مجزرة", "المقاومة", "إيران",
         "ايران", "أماني", "اماني", "لبنان", "hezbollah", "israel", "nasrallah", "explosion", "blast", "mossad",
         "wounded", "hospital", "blood", "attack", "cyber", "escalat", "war", "strike", "lebanon"]
KW = KW_HE + KW_AR
SIZES = {}
BANDS = {"lbci": (796200, 798550), "aljadeed": (502450, 504350), "almanar": (12479500, 12520500)}
CONTROL_N = {"ynet": 200, "n12": 100, "kikar": 150, "makan": 60,
             "lbci": 150, "aljadeed": 150, "mtv": 150, "almanar": 120, "nna": 0}
ROUTE = {"ynet": "live", "kikar": "live", "n12": "wayback", "makan": "wayback",
         "lbci": "live", "aljadeed": "live", "mtv": "live", "almanar": "almanar-archive", "nna": "wayback",
         "akhbar": "live", "annahar": "live", "olj": "live", "nidaa": "live"}


def add(tasks, outlet, url, route, disc, extra=""):
    k = C.url_key(url)
    if k in tasks:
        if disc not in tasks[k]["discovery"].split(";"):
            tasks[k]["discovery"] += ";" + disc
        return
    tasks[k] = {"outlet": outlet, "url": url, "route": route, "discovery": disc, "extra": extra}


def israel(tasks_by):
    ours = C.load_ours("israel")
    # gdelt
    t = tasks_by["gdelt"]
    for r in csv.DictReader(open(C.DATA / "israel/08-recall-audit/raw/gdelt-gkg-hits.csv", encoding="utf-8")):
        u = r["url"]
        o = C.outlet_of(u)
        host = urllib.parse.urlsplit(u).netloc
        if o is None or any(x in host for x in ("livegame.", "specials.", "fashionforward.")):
            continue
        if o == "n12" and ("Article-" not in u or not re.search(r"mako\.co\.il/(news-|pzm-soldiers)", u)):
            continue
        if o == "ynet" and "/article/" not in u:
            continue
        route = ROUTE[o]
        if o == "n12":
            d = ours.get(C.url_key(u))
            mu = d.get("manifest_url") if d else None
            ts = d.get("first_capture") if d else r["gkg_date"]
            u2 = mu or u
            add(t, o, u2, f"wayback:{ts or r['gkg_date']}", "gdelt", r["title"])
        else:
            add(t, o, u.replace("http://", "https://"), route, "gdelt", r["title"])
    # manifest strata
    for o in ["ynet", "n12", "kikar", "makan"]:
        rows = {}
        for f in glob.glob(str(C.DATA / f"israel/04-enumeration/{o}-titles-*.csv")):
            for r in csv.DictReader(open(f, encoding="utf-8")):
                rows[r["url"]] = r
        caps = {r["url"]: r["first_capture"] for r in csv.DictReader(open(C.DATA / f"israel/04-enumeration/{o}-urls.csv", encoding="utf-8"))}
        nokw = []
        for u, r in rows.items():
            fc = caps.get(u, "")
            if not ("20240917" <= fc[:8] <= "20241001") or r["relevance"]:
                continue
            title = r["title"]
            route = ROUTE[o] if ROUTE[o] == "live" else f"wayback:{fc}"
            if not title or "Radware" in title or len(title) < 8:
                add(tasks_by["manifest-untitled"], o, u, route, "manifest-untitled", title)
            elif any(k in title for k in KW):
                add(tasks_by["manifest-kw"], o, u, route, "manifest-kw", title)
            else:
                nokw.append((u, route, title))
        for u, route, title in random.sample(nokw, min(CONTROL_N[o], len(nokw))):
            add(tasks_by["control"], o, u, route, "control", title)
        SIZES[o] = {"nokw_population": len(nokw)}


def lebanon(tasks_by):
    t = tasks_by["gdelt"]
    for r in csv.DictReader(open(C.DATA / "lebanon/08-recall-audit/raw/gdelt-gkg-hits.csv", encoding="utf-8")):
        u = r["url"]
        o = C.outlet_of(u)
        if o is None or "program.almanar" in u or "/watch/" in u:
            continue
        k = C.url_key(u)
        if not re.search(r":(?:[a-z]+/)?\d", k):
            continue
        add(t, o, u, ROUTE[o], "gdelt", r["title"])
    alm_titles = {C.url_key(r["url"]): r for r in csv.DictReader(open(C.DATA / "lebanon/04-enumeration/almanar-titles.csv", encoding="utf-8"))}
    for o in ["lbci", "aljadeed", "mtv", "almanar", "nna"]:
        rows = list(csv.DictReader(open(C.DATA / f"lebanon/04-enumeration/{o}-urls.csv", encoding="utf-8")))
        bykey = defaultdict(list)
        for r in rows:
            bykey[C.url_key(r["url"])].append(r)
        nokw = []
        for k, rs in bykey.items():
            idp = k.split(":", 1)[1].split("/")[0]
            if not idp.isdigit():
                continue
            n = int(idp)
            if o in BANDS:
                inwin = BANDS[o][0] <= n <= BANDS[o][1]
            elif o == "mtv":
                inwin = any("2024-09-17" <= (r.get("publication_date") or "")[:10] <= "2024-09-24" for r in rs)
            else:
                inwin = any("20240917" <= r["first_capture"][:8] <= "20240926" for r in rs)
            if not inwin:
                continue
            cand = any(r["event_candidate"] == "1" for r in rs) or (o == "almanar" and alm_titles.get(k, {}).get("relevance"))
            if cand:
                continue
            # prefer a slugged URL
            rs.sort(key=lambda r: r["url"].rstrip("/").split("/")[-1].isdigit())
            u = rs[0]["url"]
            text = " ".join(urllib.parse.unquote(r["url"]).lower() for r in rs)
            if o == "almanar":
                text = alm_titles.get(k, {}).get("title", "")
            route = ROUTE[o] if ROUTE[o] != "wayback" else f"wayback:{rs[0]['first_capture']}"
            slugless = all(r["url"].rstrip("/").split("/")[-1].isdigit() for r in rs)
            if o == "mtv" and slugless:
                add(tasks_by["mtv-slugless"], o, u, route, "mtv-slugless", "")
            elif any(w in text for w in KW_AR):
                add(tasks_by["manifest-kw"], o, u, route, "manifest-kw", text[:200] if o == "almanar" else "")
            else:
                nokw.append((u, route, text[:200] if o == "almanar" else ""))
        for u, route, title in random.sample(nokw, min(CONTROL_N[o], len(nokw))):
            add(tasks_by["control"], o, u, route, "control", title)
        SIZES[o] = {"nokw_population": len(nokw)}


def main():
    country = sys.argv[1]
    tasks_by = defaultdict(dict)
    (israel if country == "israel" else lebanon)(tasks_by)
    import json
    (C.DATA / country / "08-recall-audit" / "raw" / "strata-sizes.json").write_text(json.dumps(SIZES, indent=1))
    if len(sys.argv) > 2 and sys.argv[2] == "sizes-only":
        print(SIZES)
        return
    seen = set()
    for stratum, tasks in tasks_by.items():
        p = C.DATA / country / "08-recall-audit" / "raw" / f"tasks-{stratum}.csv"
        w = csv.DictWriter(open(p, "w", newline="", encoding="utf-8"), fieldnames=["outlet", "url", "route", "discovery", "extra"])
        w.writeheader()
        n = 0
        for k, t in tasks.items():
            w.writerow(t)
            n += 1
        from collections import Counter
        print(stratum, n, Counter(t["outlet"] for t in tasks.values()))


if __name__ == "__main__":
    main()
