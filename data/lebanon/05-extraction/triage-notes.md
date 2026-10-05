# Lebanon triage + extraction — notes (step 5, v1, 2026-09-06)

Output: [candidates.jsonl](candidates.jsonl) (369
records; grows when the Al-Manar title sweep lands), raw HTML under
`raw/`. Script: `pipeline/05-extraction/extract_lebanon.py` + a container-aware
re-extraction pass.

## Triage yield

369 candidates fetched, **zero fetch failures** (routes: 355 live direct,
11 archive-subdomain, 3 Wayback). Relevance on title+body:
**238 strong, 125 related, 6 none** — a 98% enumeration precision.

Per outlet (strong/related): LBCI 105/39 · MTV 83/49 · Al Jadeed 40/35 ·
Al-Manar 9/1 (pre-sweep) · NNA 1/1. Versus the old hand-collected corpus
(LBCI 4, MTV 5, Al Jadeed 2 event articles) this is a 20–30× depth gain
for the same outlets.

## Extraction quality

- First pass (<p>-cluster) under-extracted MTV and partially LBCI; a
  container-aware second pass over the saved raw (no refetch) fixed 235
  records (`extract_method: container`).
- Post-fix medians (strong+related): Al Jadeed 471 words, Al-Manar 601,
  NNA 178, MTV 84, LBCI 60.
- **LBCI's low median is genuine, not a bug**: its event coverage is
  dominated by breaking/latest-news ticker briefs (dozens of items on Sep
  17–18). These are exactly the "live blog preserves how attribution
  evolved hour-by-hour" material the project audit called high-value —
  they must be typed as ticker items (document_type) in normalization,
  not QC-flagged as failed articles.
- Date coverage: 222/369 records carry published_at (meta/JSON-LD or
  sitemap-lastmod). Peak strong days: Sep 18 (55), Sep 17 (33), Sep 19
  (20), Sep 20 (18) — day-2 peaking matches the two-wave attack (pagers
  Sep 17, walkie-talkies Sep 18).

## v1.1 amendments (post-review, copilot CLI, 2026-09-06)

Review verdict: conditional pass — real defects, none corpus-invalidating.
All fixes applied same day:

| finding | fix |
| --- | --- |
| **65 MTV bodies were the "Most Read" sidebar** (byte-identical boilerplate credited as article text) | MTV re-extracted with sidebar blacklist (`container-v2`); 65 recovered |
| 67 further MTV rows extracted empty | investigated: all 67 are **مباشر live-ticker items** — title-only by design, same genre as LBCI's briefs; typed `doc_type_hint: live_ticker`, zero genuine failures |
| 43 duplicate rows (same article ID, different query strings) inflating counts | deduped: `duplicate_of` marks 43; primary set = 326 |
| UN High Commissioner item mis-tagged `none` | term list extended (device blast, booby-trap, مفخخة); 2 rows retagged `related` |
| "98% enumeration precision" oversold | reframed: it is an internal self-consistency figure (369-pass triage agreeing with slug tagging), not externally validated precision |
| LBCI low-median explanation conflated tickers with duplicates | split: tickers are genre; duplicates were inflation (now removed) |

**Corrected headline numbers (primary records only): 326 records —
208 strong, 114 related, 4 none.** MTV: 126 relevant = 66 live-ticker
items + 60 articles (article median 101 words, 20 ≥150w). LBCI's ticker
interpretation was confirmed by the reviewer via live fetches.

## v1.2: Al-Manar title sweep landed — collection complete (2026-09-06)

The full-manifest title sweep (3,764 titles via archive subdomain, 8
fails) tagged 34 event items; 32 new records extracted and appended.
Among them: **Nasrallah's speeches adopting "مجزرة الثلاثاء ومجزرة
الأربعاء" ("the Tuesday and Wednesday Massacres")** — the
condemnation-pole vocabulary whose absence broke the original corpus —
plus the Iranian ambassador's injury, EU/Ireland condemnations, "terrorist
crime" (Labor Minister Bayram), Kremlin statements, and the Taiwan
prosecutor line. Al-Manar's format mix mirrors the other channels:
wire-flash briefs (~13 words) plus full statements (up to 953 words).

**Final phase-1 Lebanon corpus: 358 primary records — 221 strong,
133 related** (LBCI 79/31, MTV 79/47, Al Jadeed 40/34, Al-Manar 22/20,
NNA 1/1). Collection is complete; next stage is normalization.

## Open

- Al-Manar full title sweep running (3,764 titles via archive subdomain);
  tagged rows get fetched through this step and appended.
- Undated records (~40%) get dates in normalization from raw page
  re-parse or ID-position (Al-Manar).
- Normalization into corpus-schema-v1 (field groups, dedup, wire
  attribution) is the next stage — the old-approach extractor's schema
  applies; records here are its verified input.

## v1.2 repair pass (2026-09-16, deep-dive review fixes)

Scripts: `pipeline/07-repair/repair_v12.py lebanon` +
`pipeline/07-repair/repair_v12_almanar_recover.py` (raw reports in
`archive/v1-presence-shares/deep-dive-raw/`).

- **Al Jadeed de-chromed** (27/59 bodies carried the live site's 2026
  "now watching" strip): container re-extraction + tail-cut at
  recirculation markers. The old body-based "names Israel 67.8%"
  figure was chrome; headline rate is 15.3%, in line with MTV/LBCI.
- **Al-Manar recovery**: the title sweep had left the day-0 Hezbollah
  statement series untagged. 21 items fetched via
  archive.almanar.com.lb (statement series, health-minister toll,
  martyr notices — the notices carry
  `martyr_notice_death_cause_unverified`). All 63 Al-Manar records
  re-dated from the article-meta page dates (real dates were in the
  raws all along; replaces id-interpolated ±1d). **Al-Manar day_0:
  0 → 24 records — the "slowest institutional response" claim was a
  collection artifact and is retracted.**
- 4 press-review digests (الصحافة اليوم / عناوين واسرار الصحف, 82.8%
  of Al-Manar words) retyped `press_review`; build_viz now counts
  their headlines only.
- Al-Manar headline chrome suffix stripped (32). 24/26 undated MTV
  records dated by id-interpolation (unambiguous same-date brackets);
  2 english.almanar records content-dated to Sep 19 (Nasrallah-speech
  references; archive host renders relative dates).
- Effect: **359 primary** (was 338).

### v1.2.1 (post-review corrections, same day)

Codex review verdict: fail → fixed same session; see
`data/cross-country/reviews/07-repair-v12-review-codex.md`. All 27 de-chromed Al Jadeed records were headline-only
shells (empty LongDesc nodes) — bodies emptied, retyped brief. Al Jadeed
body-based shares are dead; its exhibit rates must be headline-based.
