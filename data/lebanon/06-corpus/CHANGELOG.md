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

## Next: v1.3 (planned)

Fixes listed by the recall audit, see
`data/cross-country/08-recall-audit-summary.md`, section "Corpus fixes for v1.3".
