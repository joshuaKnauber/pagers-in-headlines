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

## Next: v1.3 (planned)

Fixes listed by the recall audit, see
`data/cross-country/08-recall-audit-summary.md`, section "Corpus fixes for v1.3".
