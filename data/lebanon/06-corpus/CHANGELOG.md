# Lebanon corpus: changelog

`corpus.jsonl` is always the current version. Earlier versions survive only where they were
committed: 52af888 holds Lebanon at 338 primary and Israel v1 at 153 primary; e79be10 holds v1.2.1
for all four countries. Other intermediate versions were not committed. Record schema:
`1.1.0-phase1` throughout.

## v1 / v1.1 (2026-09-06)

Produced by: `pipeline/06-normalization/normalize_lebanon.py`.

354 records, 338 primary as committed. v1.1 applied the copilot review of step 5, including 43 URL duplicates marked (see `05-extraction/triage-notes.md`, "v1.1 amendments"). `normalization-notes.md` reports 353 primary for the first run; the gap to 338 is not documented.

## v1.2 (2026-09-16)

Produced by: `pipeline/07-repair/repair_v12.py lebanon`, `repair_v12_almanar_recover.py`.

359 primary. Al Jadeed bodies re-extracted from raw; Al-Manar headline chrome stripped, press reviews typed `press_review`, all Al-Manar records re-dated from page dates, 21 day-0/1 items recovered via archive.almanar.com.lb; 24 MTV dates repaired from raw meta. Ledger: `05-extraction/triage-notes.md`, "v1.2 repair pass".

## v1.2.1 (2026-09-16)

Produced by: v1.2.1 fix-ups (`python3 pipeline/07-repair/repair_v12.py fixups`, same day, after the codex review in `data/cross-country/reviews/07-repair-v12-review-codex.md`).

All 27 de-chromed Al Jadeed records turned out to be headline-only shells: bodies emptied, retyped `brief`. Word counts recomputed.

## v1.3 (2026-10-05)

Produced by: `pipeline/07-repair/repair_v13.py lebanon`.

373 records, 356 primary (was 359). Fixes from the recall audit:

- Excluded: `lb_lbci_797960` (wireless earbuds and hearing loss, matched on لاسلكية) and `lb_aljadeed_507118` (Oct 6 Washington Post report on Israel intercepting Hezbollah radio traffic; wrongly called a different event, restored in v1.3.1).
- Near duplicate: `lb_aljadeed_502819` (misspelt repost, "تفـ جير") is now secondary to `lb_aljadeed_502815`. The body of `502815` was iframe markup and is now empty. The audit's second pair, `502553`/`502564`, is not a duplicate: a programme notice and a news brief 17 minutes apart, both kept.
- Dates: `lb_mtv_1490054` → Sep 26 and `lb_mtv_1490462` → Sep 27 (own first capture, bounded by neighbouring IDs' first captures); `lb_nna_722276` → Sep 18 (page dateline); `lb_nna_722542` → Sep 19 (page timestamp).
- `lb_nna_722276` body replaced: the stored body was unrelated English text; the page's own text (Kremlin warning, via AFP) is now the body, language `ar`.
- 10 Al-Manar martyr notices → relevance `context` (they name no device on the page; still useful as named-victim evidence).

## v1.3.1 (2026-10-05)

Produced by: `pipeline/07-repair/repair_v13.py fixups`. Review of v1.3 (general-purpose subagent, 2026-10-05): pass with fixes. Applied as `python3 pipeline/07-repair/repair_v13.py fixups`; the v1.3 stages now also skip anything the fix-ups reversed, so replaying all stages from v1.2.1 gives this version.

374 records, 357 primary.

- `lb_aljadeed_507118` restored (headline-only `brief`, `related`): the headline reports the Washington Post's Oct 5–6 investigation (Israel listened in on Hezbollah walkie-talkies for nine years and kept the option of turning them into bombs). That is the walkie-talkie operation, not a separate event, and Oct 6 is inside the window.
- Empty bodies now carry the hash of the empty string, as in earlier versions; `lb_nna_722542` `published_time` in UTC with `Z`.
- The audit listed 11 martyr notices; only 10 records carry the martyr flag, and those 10 were marked `context`.

## v2.0 (2026-10-06): collection round 2

Produced by: `pipeline/06-normalization/build_corpus_v2.py lebanon`, from the round-2 staging files in
`05-extraction/round2/` (extractors in `pipeline/05-extraction/round2/`). Method:
`docs/methodology/round2-gap-fill.md`. Reviewed before release (Sonnet subagent, pass with fixes); the fixes
are included in this version.

838 records, 837 primary (was 357).

- Added: 464 gap items (MTV 215, LBCI 124, Al Jadeed 62, Al-Manar 58, NNA 5). New records have `extraction.round = 2` and warning `added_v2_gapfill` or `added_v2_liveblog`.
- Re-extracted: 202 existing bodies, with the same validated extractor as the new items (warning `body_reextracted_v2`). Headlines unchanged.
- Schema `1.2.0`: `extraction.salience` (central / mention / allusive / none) on every record, and `extraction.relevance` now follows it (central → strong, mention and allusive → related, none → context). `extraction.round`; document type `live_blog_entry` with `publication.liveblog_url`; `deduplication.same_text_as` for a copy of another outlet's text, which stays primary.
- Dates: `published_at` is the date in the outlet's home time zone wherever an exact time is known.
- Al Jadeed: 38 stored bodies were wrong (LongDesc copied twice, or text from another story); 15 stories that v1 had grouped as duplicates because they shared that wrong text are primary again. Al-Manar: bodies were cut at the first embedded video in v1 (26 pages longer now). 324 primary records (38%) are headline-only: live tickers and briefs without body text; their salience comes from the headline. 11 hand decisions (`MANUAL`).
