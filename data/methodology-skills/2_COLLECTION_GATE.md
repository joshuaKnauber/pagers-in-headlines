# Step 2: Collection gate

Turn a frozen census (step 1) into the machine-readable answer to "which
outlets are load-bearing for collection?" — derived, never hand-assigned.
This is deliberately its own step so the question is settled by rule before
any access work or collection effort is spent.

## How

Run after every census change:

```bash
python3 data/scripts/derive_collection_gate.py
```

The script reads each country's frozen census CSV and writes
`data/<country>/collection-gate-v1.csv`
(columns: `outlet, tier, collection_gate, gate_reason, derived_from`).

## The rules (encoded in the script — the script is the spec)

A row becomes required in exactly four ways:

1. **`required`** — `tier = mass`. The reach gate: these outlets define the
   country's coverage claim.
2. **`required-baseline`** — `wire` in `medium`. The editorial-vs-
   distribution corpus design needs wire baselines (AP, Reuters, dpa, NNA)
   regardless of audience tier.
3. **`required-representative`** — the row's `tier_rationale` documents it
   as the role-based representative of a mass-level category (a recorded
   project decision, e.g. RND for Germany's regional-daily layer).
4. **`blocking-unresolved`** — `tier = unresolved` and candidate-mass
   (no-cop-out rule): not collected yet, but the country's coverage claim
   is blocked until the row is resolved or the exclusion is escalated.

Everything else derives to:

- **`optional`** — substantial/niche/context perspective value. Collected
  if capacity allows; never part of the coverage claim.
- **`documentation-only`** — `(category)` rows: measured context that is
  not a single collectable outlet.

## The unresolved discipline

A plain `unresolved` row (deriving to `optional`) is only legitimate when
its `tier_rationale` **states why mass is excluded** — a structural argument
(minor-medium signal cap, measured axis A below the strong threshold, no
path to two strong signals) or an evidence bound (e.g. Lebanon's four-source
pan-Arab bound). An unresolved row that *cannot* state a mass exclusion is
by definition candidate-mass and must derive `blocking-unresolved`. This
keeps "unresolved" from becoming a quiet parking lot: what stays open is
always and only the substantial-vs-niche question, which gates nothing.

## Fixing a wrong-looking gate

Never edit the gate file. If a derivation looks wrong, either a census
field is wrong (fix the census, with its normal review discipline) or a
rule is incomplete (change the script — the diff is the audit trail). The
`required-representative` rule exists because exactly this happened: RND
derived `optional` until the rule learned to honor documented
representative decisions.

## Done criteria

- Gate files regenerated from the current frozen censuses, with the script
  output (per-country gate counts) recorded in the country notes or commit.
- Every `blocking-unresolved` row has an owner and a resolution route noted
  in the census.
- Step 3 (access verification) consumes only the gate file — its to-do list
  is the `required*` rows plus resolution of `blocking-unresolved` rows.

## Current state (2026-09-05)

- Lebanon: 4 required + NNA baseline. (Al Jazeera's blocking-unresolved
  status was resolved down to candidate-substantial the same day — see
  Lebanon census-notes v2.2 for the four-source bounding argument.)
- Germany: 8 required + dpa baseline + RND representative.
- US: 9 required + AP and Reuters baselines.

27 required rows, zero blockers, across the three frozen censuses. All
three countries are clear for step 3.
