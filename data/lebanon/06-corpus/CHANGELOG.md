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
