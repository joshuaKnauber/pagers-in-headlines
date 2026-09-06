#!/usr/bin/env python3
"""Derive the collection gate for every census row, mechanically.

The gate answers "is this outlet load-bearing for collection?" from fields
already in the frozen census - no per-outlet judgment enters here. Rules:

  required            tier == mass                  (reach gate)
  required-baseline   'wire' in medium              (corpus design: the
                                                     editorial-vs-distribution
                                                     split needs wire baselines)
  blocking-unresolved tier == unresolved and the row is candidate-mass
                                                    (no-cop-out rule: blocks the
                                                     country's coverage claim)
  documentation-only  '(category)' in outlet name   (measured but not one outlet)
  optional            everything else               (perspective/context value;
                                                     never gates coverage)

Output: data/<country>/collection-gate-v1.csv
Rerun after any census change; the gate file is a derived view, the census
stays the source of truth.
"""
import csv
import sys
from pathlib import Path

DATA = Path(__file__).resolve().parent.parent

CENSUS_FILES = {
    "lebanon": DATA / "lebanon" / "outlet-census-v2.csv",
    "germany": DATA / "germany" / "outlet-census-v1.csv",
    "us": DATA / "us" / "outlet-census-v1.csv",
    "israel": DATA / "israel" / "outlet-census-v1.csv",
}


def derive(row: dict) -> tuple[str, str]:
    tier = row["tier"].strip().lower()
    medium = row["medium"].strip().lower()
    outlet = row["outlet"].strip()
    blob = (row.get("tier_rationale", "") + " " + row.get("notes", "")).lower()

    if "(category)" in outlet.lower():
        return "documentation-only", "category row, not a single outlet"
    if "wire" in medium:
        return "required-baseline", "wire baseline (distribution-corpus design)"
    if tier == "mass":
        return "required", "reach gate (mass tier)"
    if "role-based representative" in row.get("tier_rationale", "").lower():
        return "required-representative", "documented representative of a mass-level category (project decision)"
    if tier == "unresolved" and "candidate mass" in blob.replace("candidate-mass", "candidate mass"):
        return "blocking-unresolved", "candidate-mass unresolved (no-cop-out rule)"
    if tier == "unresolved":
        return "optional", "unresolved below mass candidacy; resolve or leave optional"
    return "optional", f"{tier} tier: perspective/context value, does not gate coverage"


def main() -> None:
    for country, path in CENSUS_FILES.items():
        if not path.exists():
            print(f"!! missing census: {path}", file=sys.stderr)
            continue
        with path.open(encoding="utf-8", newline="") as f:
            rows = list(csv.DictReader(f))
        out_path = path.parent / "collection-gate-v1.csv"
        with out_path.open("w", encoding="utf-8", newline="") as f:
            w = csv.writer(f)
            w.writerow(["outlet", "tier", "collection_gate", "gate_reason", "derived_from"])
            for r in rows:
                gate, reason = derive(r)
                w.writerow([r["outlet"], r["tier"], gate, reason, path.name])
        counts: dict[str, int] = {}
        for r in rows:
            g, _ = derive(r)
            counts[g] = counts.get(g, 0) + 1
        print(f"{country}: {out_path.name} <- {path.name}  {dict(sorted(counts.items()))}")


if __name__ == "__main__":
    main()
