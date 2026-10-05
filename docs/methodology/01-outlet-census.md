# Step 1: Outlet census

Build the list of news outlets that account for most news exposure of people
in one country, with documented audience evidence for every row. This census
is the foundation the later steps consume: access verification (step 2) must
prove a text route for every mass-tier outlet, and the final coverage claim
("country X is covered") is a diff against this census.

Worked example: [`lebanon/01-census/outlet-census.csv`](../../data/lebanon/01-census/outlet-census.csv)
and [`census-notes.md`](../../data/lebanon/01-census/census-notes.md) (v1 of both is in `archive/lebanon-census-v1/`).

## Principles

1. **Audience-side, not publisher-side.** The census asks "what do people in
   this country consume", not "what is headquartered here". Pan-national and
   international outlets belong in the census when consumption evidence puts
   them there (Lebanon: Al Jazeera and Al Mayadeen lead digital consumption).
   Record each outlet's home system separately so one outlet can appear in
   several countries' censuses without double-counting in analysis.
2. **No assumptions — evidence or blank.** Every audience claim carries its
   source, URL, measurement period, and a confidence rating. If no evidence
   was found, the row says so (`confidence: none`, `tier_candidate:
   unresolved`). An unresolved tier is a work item, not a guess.
3. **Record verbatim, harmonize later.** Sources mix "audience share" (share
   of viewers) with "reach" (share of population). Quote what the source
   said. Premature harmonization hides errors.
4. **Conflicts are findings.** When two sources (or two renderings of one
   source) disagree, record both with a note. Do not silently pick one.
5. **Tiers gate collection, so under-claiming beats over-claiming.** A wrongly
   assigned mass tier costs collection effort; a wrongly *missed* mass outlet
   invalidates the country's coverage claim. Omission is the worst failure
   mode — spend the extra search pass hunting for what is missing, not
   polishing what is found.

## Output artifacts

Per country, in `data/<country>/`:

- `outlet-census.csv` — one row per outlet (schema below).
- `census-notes.md` — the evidence narrative: sources used, structural
  findings about the media system, conflicts and their resolution routes,
  method caveats, and the explicit gap list for the next evidence round.

Version both files (`-v1`, `-v2`) instead of editing in place once a version
has been reviewed.

### CSV schema

| column | content |
| --- | --- |
| `outlet` | Common name (note major sub-brands in `notes`) |
| `medium` | `tv`, `print`, `online`, `radio`, `wire`, or combinations (`tv+online`) |
| `home_system` | Where the outlet belongs editorially: the country, `pan-<region>`, or `international` |
| `languages` | Space-separated ISO codes |
| `ownership_or_affiliation` | Owner and political alignment **with the source that documents it** — this column must be sourced research (e.g. Media Ownership Monitor), never our own judgment |
| `audience_evidence` | Verbatim numbers with metric named, e.g. "ELKA 2024 via MOM: 11% of TV audience" |
| `evidence_period` | Year(s) of the measurements, not of the census |
| `evidence_source` | Named source(s), semicolon-separated, matching order of URLs |
| `evidence_url` | URL(s), semicolon-separated |
| `confidence` | `high` / `medium` / `low` / `none` (definitions below) |
| `tier_candidate` | `mass` / `substantial` / `niche` / `context` / `unresolved` |
| `notes` | Conflicts, caveats, access flags, follow-ups |

### Confidence ratings

- `high` — consistent, recent, purpose-built audience measurement.
- `medium` — measured, but dated, partial, or a proxy metric.
- `low` — outlet is documented (e.g. listed in an ownership database) but its
  audience is unmeasured.
- `none` — no evidence found this pass.

### Tier rule

Write the threshold rule down **before** assigning tiers, then apply it
mechanically. Template (calibrate thresholds per country in the notes file;
worked example: `data/lebanon/01-census/census-notes.md`):

- Group evidence into **axes**, each contributing at most one signal (the
  strongest item on it; two vintages of one measurement are one signal):
  **A** measured audience share (purpose-built), **B** social footprint
  (cross-platform aggregate of verified official accounts — platforms never
  stack as separate signals), **C** digital consumption rankings (weak only),
  **D** third-party documented reach (weak only).
- Strong: current purpose-built share ≥ ~10% of the dominant medium (incl.
  top-N membership implying ≥10%); axis-B aggregate ≥ ~2M. Weak: dated or
  smaller shares; **any** share in a minor medium (<50% penetration — write
  the discount into the rule, don't apply it silently); axis-B 500K–2M;
  proxy rank.
- `mass` = 2 strong. `substantial` = 1 strong, or ≥2 weak, or axis-B
  aggregate ≥ ~750K. `niche` = measured, below. `context` = role-based.
  `unresolved` = a plausibly decisive axis is unmeasured (tier could change
  when gathered); minor-medium rows are exempt from B-blocking.
- Exception, documented per row and re-evaluated each round: when platform
  bans void axis B, one current axis-A strong signal can carry `mass`.
- Region-wide counts of pan-national outlets are **not** country signals.
  An `unresolved` candidate-mass row blocks the country freeze.
- After writing the rule, re-derive every row from it mechanically and quote
  the derivation in `tier_rationale` — a tier the rule can't produce is
  either a wrong tier or an incomplete rule (review 2 in Lebanon found both).

## Procedure

### 1. Establish the medium mix first

Before ranking outlets, find out *how* the country consumes news: TV vs.
online vs. social vs. print vs. radio shares, ideally with age breakdown.
This determines which evidence matters and how much. Lebanon flipped the
census design: Arab Barometer showed 53% get breaking news primarily from
social media (TV 31%), so TV ratings alone would describe the older half of
the population.

Sources in rough order of preference:
- Reuters Institute Digital News Report (annual, ~48 markets, includes
  per-outlet weekly reach — if the country is a DNR market, it may carry most
  of the census on its own).
- Regional academic surveys (Arab Barometer, NU-Q "Media Use in the Middle
  East", Afrobarometer, Latinobarómetro, Eurobarometer).
- DataReportal "Digital <Country>" for internet/social platform penetration.

### 2. Find the audience-measurement backbone per medium

- **TV/radio:** the national ratings provider (Ipsos, Nielsen, Kantar, or a
  local body — Lebanon: Ipsos TAM historically, ELKA 2024). Trade-press
  articles often republish ratings that are otherwise paywalled.
- **Ownership + audience combined:** RSF's Media Ownership Monitor
  (mom-gmr.org) where it exists — it documents ownership and political
  affiliation (which we must never assert ourselves) and often republishes
  audience shares with the measurement source named.
- **Digital:** SimilarWeb / Semrush / Ahrefs country rankings. Treat as
  proxies and say which metric (Ahrefs = organic search visits only; misses
  direct, app, and social traffic — note this in the caveats).
- **Social (usually the biggest gap):** per-outlet follower/engagement counts
  on the platforms the medium-mix data says matter. Expect to gather this in
  a second evidence round; list it in the gap list rather than skipping it
  silently.

### 3. Enumerate candidates wide, audience-side

Union of: every outlet the measurement sources mention; pan-national and
international outlets appearing in the country's digital rankings; the state
news agency and public broadcaster (as `context` baseline even when audience
is marginal); known digital natives from ownership databases. Also check the
project's prior audit registry (`old-approach/`) — but never let "we already
collected it" justify a census row: that is publisher-side reasoning.

### 4. Fill rows, then hunt omissions explicitly

After filling what the sources give, run a dedicated search pass for what is
*not* there yet: "most watched news channel <country> <recent year>", the
country's top-websites lists, platform-specific news channels. The Lebanon
census found Al Manar's mass tier (11%) only because the concentration data
was fetched directly — no domestic outlet list would have flagged it as a
must-have.

### 5. Write the notes file

Structural findings first (what reframes the census), then per-medium
evidence with sources, then conflicts with their resolution route, then the
numbered gap list for round 2, then method caveats. The notes file is what
makes the census auditable — a reviewer must be able to re-walk every claim.

### 6. Independent review

Spawn a reviewer that did not build the census, with instructions to
(a) re-fetch the load-bearing citations and verify the numbers, (b) hunt
independently for omitted high-reach outlets, (c) check tier assignments
against the no-assumptions rule, (d) assess the proxies themselves. Fold the
findings into `-v2` of both files, with a corrections ledger mapping every
finding to its fix.

Review cadence: one adversarial review per version that changes tiers,
**scoped to the delta** (new evidence classes, re-tiering, and a regression
check that the previous review's findings were actually fixed). A version
whose review yields only trivia is freezable — that is the defined stopping
point; do not review forever.

### 7. Done criteria for this step

- Every mass and substantial `tier_candidate` is backed by ≥ `medium`
  confidence evidence.
- The top of every medium the mix data says matters (per step 1) is either
  represented or explicitly in the gap list.
- All conflicts are recorded with a resolution route.
- Independent review completed and incorporated.
- The gap list is concrete enough that round 2 is a task list, not a
  re-research.

Unresolved tiers may remain — they carry into step 2 as open items, and any
outlet that could plausibly be mass-tier must be resolved before the country's
coverage claim is made.

A frozen census feeds **step 2 (collection gate)** —
[`02-collection-gate.md`](02-collection-gate.md) — which mechanically derives
which rows are load-bearing for collection. Tiers here are evidence
classifications; whether an outlet must be collected is decided there, by
script, never by hand.

## Pitfalls hit in Lebanon (check for these every time)

- **Stale data living next to fresh data in one source:** MOM outlet pages
  carried Ipsos 2018 shares while the findings page cited ELKA 2024. Check
  the vintage of every number, not of the website.
- **Two editions of one source can masquerade as a conflict:** MOM Lebanon
  publishes a 2018 edition (lebanon-2018.mom-gmr.org, Ipsos data) and a 2024
  edition (lebanon.mom-gmr.org, ELKA data) with contradictory top-4 lists and
  LBCI at 25.8% vs 13%. Census v1 recorded this as one source contradicting
  itself; the independent review traced it to two editions — meaning the
  "conflict" was actually a resolved time series (LBCI declined). Before
  recording a conflict, confirm both numbers really come from the same
  edition and measurement.
- **Survey waves drop questions:** NU-Q asked per-channel TV viewership in
  2017 but only platform-level questions in 2019. The newest wave of a survey
  is not automatically the best evidence for a specific claim.
- **"Share" vs "reach" confusion** — see principle 3.
- **A medium can be measured and still small:** Lebanese print has clean
  top-4 concentration numbers (89%) but 72% read no print at all. Absolute
  penetration decides the tier, not the neatness of the within-medium data.
- **Print outlets may be zombies:** a 2024 readership rank can overstate a
  barely-alive paper. Verify publication status before collection.
- **Digital rankings answer a different question than TV ratings:** don't
  average them into one number; keep per-medium evidence separate and let the
  tier synthesis happen in the open, in the notes file.
- **Social counts are minefields:** squatted/impostor handles carrying the
  outlet's name (Lebanon: fake LBCI, OTV, Al-Jadeed YouTube channels found);
  similarly-named but unaffiliated outlets (the961.com vs 961today.com);
  aggregate cross-platform claims read as single-platform numbers; and
  region-wide counts of pan-national outlets. Verify handles via the outlet's
  own website footer, and prefer live-fetched counts over search snippets.
- **Domestic follower counts include the diaspora:** MTV Lebanon has ~6× more
  Facebook followers than Lebanon has Facebook users. Always record the
  platform's national user base (DataReportal) beside the counts.
- **Platform bans invert the metric:** a sanctioned outlet (Al-Manar) can be
  mass-reach with a near-zero mainstream social footprint. Check *why* a
  count is small before reading it as audience size.
