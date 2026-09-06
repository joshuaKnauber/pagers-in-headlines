# Lebanon normalization — notes (v1, 2026-09-06)

Script: `data/scripts/normalize_lebanon.py` ·
Output: [corpus-v1.jsonl](corpus-v1.jsonl) (schema `1.1.0-phase1`,
corpus-schema-v1-aligned field groups) +
[normalization-quality.csv](normalization-quality.csv) (every input
record's disposition).

## Result

**354 normalized records, 353 primary** (1 exact-body duplicate collapsed;
43 URL-duplicates and 4 irrelevant excluded upstream with dispositions
recorded).

- **Document types:** 209 articles · 72 live-ticker items · 71 briefs ·
  1 statement. The ticker/brief share (40%) is the Lebanese-coverage genre
  signature — analysis units must respect it (headline-level analysis for
  tickers/briefs, body-level for articles).
- **Languages:** 290 Arabic, 63 English (detected, not assumed).
- **Dates: 323/353 (91%)** — 184 page-meta, 99 sitemap-lastmod, 40
  Al-Manar ID-interpolated (guard added: interpolation only inside the
  Arabic-site modern ID band; english.almanar IDs excluded after two
  wrong pre-event dates surfaced). Undated: 26 MTV + 2 NNA + 2 Al-Manar-EN
  — flagged `date_missing`, recoverable via Wayback capture timestamps in
  a later pass.
- **Wire attribution (lead-based):** Reuters 37 · AFP 7 · NNA 3 — the
  editorial-vs-distribution split is live; 13% of the corpus is
  wire-credited, matching the old audit's expectation of heavy Reuters
  dependence in Lebanese English-language output.
- **Time slots:** day_0 52 → **day_1 124 (peak)** → day_2 60 → decay,
  plus 21 tail records. The walkie-talkie second wave outweighing the
  pager first wave is now a normalized, per-outlet-verifiable fact.

## Known limitations (for the smoke-test analysis to respect)

1. Wire detection is lead-text keyword matching — good precision, unknown
   recall; the analysis should treat `local_or_unspecified` as
   "not-detected", not "confirmed original".
2. `id-interpolated` dates are ±1 day at best; exclude them from
   hour-level claims.
3. Near-duplicate (story-level) clustering is NOT done — only exact body
   hashes. The old pipeline's shingle clustering applies at analysis
   prep if cross-outlet story matching is needed.
4. NNA is 2 records — the state-baseline is thin in phase 1 (its
   enumeration recall was the weakest); treat NNA-based claims
   accordingly.
5. `statement` typing is keyword-narrow (1 record); Nasrallah speech
   items mostly typed article/brief — refine if speech analysis matters.

Next: the smoke-test analysis pass over this file (term families,
attribution timing, ticker-vs-article shares, displacement curve) — its
real job is to catch what this normalization got wrong.
