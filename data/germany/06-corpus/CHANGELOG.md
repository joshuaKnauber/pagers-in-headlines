# Germany corpus: changelog

`corpus.jsonl` is always the current version. Earlier versions survive only where they were
committed: 52af888 holds Lebanon at 338 primary and Israel v1 at 153 primary; e79be10 holds v1.2.1
for all four countries. Other intermediate versions were not committed. Record schema:
`1.1.0-phase1` throughout.

## v1 / v1.1 (2026-09-14)

Produced by: `pipeline/05-extraction/extract_de_us.py germany`, `pipeline/06-normalization/normalize_de_us.py germany`.

176 primary after the codex review folded in the same night. Ledger: `05-extraction/triage-notes.md`, "QC catches" and "v1.1 amendments".

## v1.2 (2026-09-16)

Produced by: `pipeline/07-repair/repair_v12.py germany`.

176 primary (unchanged). t-online headlines from og:title, RND crossword tails, Bild opinion prompts, WELT navigation and Spiegel residue scrubbed; 4 Spiegel paywall shells retyped `flash_or_lead`. Ledger: `05-extraction/triage-notes.md`, "v1.2 repair pass".

## v1.2.1 (2026-09-16)

Produced by: v1.2.1 fix-ups (`python3 pipeline/07-repair/repair_v12.py fixups`, same day, after the codex review in `data/cross-country/reviews/07-repair-v12-review-codex.md`).

Word counts recomputed; no other change.

## v1.3 (2026-10-05)

Produced by: `pipeline/07-repair/repair_v13.py germany`.

190 records, 172 primary (was 176). Fixes from the recall audit:

- RND: four articles were stored twice because RND changed the slug and headline while updating them (same article ID). The later version (by `dateModified`) is primary; the earlier one is kept with `deduplication.relation = earlier_version` and `version_of`, because readers saw it and the claim catalogue cites some earlier versions.
- 31 `related` records listed by the audit as having no pager, walkie-talkie or device wording → relevance `context` (mostly escalation coverage from Sep 20 on). Three of them do mention the devices; reversed in v1.3.1, leaving 28.
- `ge_tonline_1e9c010a33` retyped `live_blog` (t-online's rolling newsblog, one snapshot). Three ntv `der_tag` entries retyped `live_ticker`.

## v1.3.1 (2026-10-05)

Produced by: `pipeline/07-repair/repair_v13.py fixups`. Review of v1.3 (general-purpose subagent, 2026-10-05): pass with fixes. Applied as `python3 pipeline/07-repair/repair_v13.py fixups`; the v1.3 stages now also skip anything the fix-ups reversed, so replaying all stages from v1.2.1 gives this version.

190 records, 172 primary; 28 `context`.

- Three `context` downgrades reversed: `ge_spiegel_0c74f9ad5e` (page lead: "Im Libanon sind zahlreiche Walkie-Talkies explodiert", now `strong`), `ge_tagesschau_5d524e455b` ("Angriffen auf Kommunikationstechnik der Hisbollah") and `ge_zdfheute_ad2e30a014` ("Explosion von Kommunikationsausrüstung im Libanon"), both `related`. The audit's term list missed these words; `repair_v13.py` now re-checks every record against a wider device pattern before downgrading.
- The five SPIEGEL+ paywall shells (`0c74f9ad5e`, `8be8faca25`, `56bd1c4430`, `eb13e72e65`, `176d1e0d56`) get their lead from the page's meta description as body (18–30 words): what a non-subscriber saw.
- `ge_ntv_5a5721af9d` (a `der_tag` entry typed `flash_or_lead`) retyped `live_ticker`.

## v2.0 (2026-10-06): collection round 2

Produced by: `pipeline/06-normalization/build_corpus_v2.py germany`, from the round-2 staging files in
`05-extraction/round2/` (extractors in `pipeline/05-extraction/round2/`). Method:
`docs/methodology/round2-gap-fill.md`. Reviewed before release (Sonnet subagent, pass with fixes); the fixes
are included in this version.

424 records, 407 primary (was 172).

- Added: 176 gap items (ntv 47, WELT 47 incl. dpa wire-feed pages, Spiegel 29, Bild 13, t-online 13, RND 12, Tagesschau 9, RTL 6 teletext pages) and 58 live-blog entries (Tagesschau 56, ZDF 1, ntv 1). New records have `extraction.round = 2` and warning `added_v2_gapfill` or `added_v2_liveblog`.
- Re-extracted: 162 existing bodies, with the same validated extractor as the new items (warning `body_reextracted_v2`). Headlines unchanged.
- Schema `1.2.0`: `extraction.salience` (central / mention / allusive / none) on every record, and `extraction.relevance` now follows it (central → strong, mention and allusive → related, none → context). `extraction.round`; document type `live_blog_entry` with `publication.liveblog_url`; `deduplication.same_text_as` for a copy of another outlet's text, which stays primary.
- Dates: `published_at` is the date in the outlet's home time zone wherever an exact time is known.
- 79 stored bodies carried chrome (share bars, audio-player code, video overlays) and were re-extracted. Three audit false positives were not added (two ice-hockey pieces, one fire-brigade piece).
