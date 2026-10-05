#!/usr/bin/env python3
"""Prune suspicious done-slices so the resume pass re-verifies them.

Wayback served nginx-504 HTML as HTTP 200 during enumeration; those
slices completed "+0" and were wrongly marked done. Rule: a done-slice
whose 2-day window contains zero first_capture rows in the outlet CSV is
either genuinely empty or a silent 504 — remove it from .done and let
the (now HTML-aware) resume pass decide.
"""
import csv, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2] / "data"

for country in ("germany", "us"):
    d = ROOT / country / "04-enumeration"
    for done_f in sorted(d.glob(".*-slices.done")):
        outlet = done_f.name[1:].replace("-slices.done", "")
        csv_f = d / f"{outlet}-urls.csv"
        caps = set()
        if csv_f.exists():
            for r in csv.DictReader(open(csv_f, encoding="utf-8")):
                if r["source"] == "cdx" and r["first_capture"]:
                    caps.add(r["first_capture"][:8])
        keys = done_f.read_text().split()
        keep, pruned = [], []
        for k in keys:
            a, b = k.split("-")
            if any(a <= c <= b for c in caps):
                keep.append(k)
            else:
                pruned.append(k)
        if pruned:
            done_f.write_text(" ".join(sorted(keep)))
        print(f"{country}/{outlet}: kept {len(keep)}, re-verify {len(pruned)}")
