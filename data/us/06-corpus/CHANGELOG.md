# US corpus: changelog

`corpus.jsonl` is always the current version. Earlier versions survive only where they were
committed: 52af888 holds Lebanon at 338 primary and Israel v1 at 153 primary; e79be10 holds v1.2.1
for all four countries. Other intermediate versions were not committed. Record schema:
`1.1.0-phase1` throughout.

## v1 / v1.1 (2026-09-14)

Produced by: `pipeline/05-extraction/extract_de_us.py us`, `pipeline/06-normalization/normalize_de_us.py us`.

134 primary after the extraction repair round and the codex review. Ledger: `05-extraction/triage-notes.md`, "Repair pass" and "v1.1 amendments".

## v1.2 (2026-09-16)

Produced by: `pipeline/07-repair/repair_v12.py us`.

131 primary. Fox, CNN and Yahoo bodies re-extracted from their containers (removes 2026 page chrome), 3 AMP/desktop duplicate pairs collapsed, Yahoo provider credits rebuilt. Ledger: `05-extraction/triage-notes.md`, "v1.2 repair pass".

## v1.2.1 (2026-09-16)

Produced by: v1.2.1 fix-ups (`python3 pipeline/07-repair/repair_v12.py fixups`, same day, after the codex review in `data/cross-country/reviews/07-repair-v12-review-codex.md`).

17 Fox newsletter tails cut. Word counts recomputed.

## v1.3 (2026-10-05)

Produced by: `pipeline/07-repair/repair_v13.py us` and `repair_v13.py ap`.

173 records, 143 primary (was 131). Fixes from the recall audit:

- AP: every AP candidate had been fetched as a Cloudflare challenge page and rated irrelevant. All 23 were re-collected from Wayback (17 from the recall audit's cache, the rest via CDX with status 200), extracted from the `RichTextStoryBody` container, and 18 were added: 17 articles and one video page (headline only). The AP live blog is left for the gap fill, which splits live blogs into entries. Of the other four, three do not mention the attacks and one (Oct 30) is outside the window.
- 7 CNN video pages (Sep 27 – Oct 4) and `us_cbs_8d3f0e89ac` → relevance `context`.
- Excluded: `us_cbs_deca8d7e0f` (Oct 31) and `us_nbc_d7d1591943` (Oct 29), out of window; `us_cbs_b6fde07557` (CBS Chicago local station) and Yahoo Canada, Finance and Singapore copies (`6b6ad5ce8c`, `ae4f6eb3f5`, `e4c4db9ea5`), out of scope.
- `us_yahoo_5f33d95679` (36 words) retyped `brief`.

## v1.3.1 (2026-10-05)

Produced by: `pipeline/07-repair/repair_v13.py fixups`. Review of v1.3 (general-purpose subagent, 2026-10-05): pass with fixes. Applied as `python3 pipeline/07-repair/repair_v13.py fixups`; the v1.3 stages now also skip anything the fix-ups reversed, so replaying all stages from v1.2.1 gives this version.

173 records, 143 primary; 9 `context`.

- `us_abc_fd43fc1794` and `us_yahoo_3820a5161a` credited to AP (`syndicated_or_adapted`): about 99% identical to `us_ap_00afe7047e`.
- The AP editor's note "More explosions have been reported … Follow AP's live updates." cut from the start of `us_ap_924d0a76d1` and `us_ap_3d587773c6`.
- Empty body of `us_ap_3049232971` carries the empty-string hash.

## v2.0 (2026-10-06): collection round 2

Produced by: `pipeline/06-normalization/build_corpus_v2.py us`, from the round-2 staging files in
`05-extraction/round2/` (extractors in `pipeline/05-extraction/round2/`). Method:
`docs/methodology/round2-gap-fill.md`. Reviewed before release (Sonnet subagent, pass with fixes); the fixes
are included in this version.

1076 records, 1015 primary (was 143).

- Added: 615 gap items (Yahoo 364, credited to their providers; NYT 58, ABC 45, CBS 29, WaPo 28, CNN 20, USA Today 19, AP 18, Fox 16, NBC 16, Reuters 2) and 282 live-blog entries, 257 primary (CNN 152, NYT 50, AP 39, WaPo 16); 25 entries are reposts of another entry (exact or ≥ 80% word overlap) and are secondary. New records have `extraction.round = 2` and warning `added_v2_gapfill` or `added_v2_liveblog`.
- Re-extracted: 155 existing bodies, with the same validated extractor as the new items (warning `body_reextracted_v2`). Headlines unchanged.
- Schema `1.2.0`: `extraction.salience` (central / mention / allusive / none) on every record, and `extraction.relevance` now follows it (central → strong, mention and allusive → related, none → context). `extraction.round`; document type `live_blog_entry` with `publication.liveblog_url`; `deduplication.same_text_as` for a copy of another outlet's text, which stays primary.
- Dates: `published_at` is the date in the outlet's home time zone wherever an exact time is known.
- 48 stored bodies were wrong (Fox video overlays, Yahoo key-takeaway boxes, WaPo captions and promos) and were re-extracted. Six Yahoo pages are AP or Telegraph live blogs (`live_blog`). Three audit false positives were not added. Three hand decisions (`MANUAL`).
