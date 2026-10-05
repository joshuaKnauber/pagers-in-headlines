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

## Next: v1.3 (planned)

Fixes listed by the recall audit, see
`data/cross-country/08-recall-audit-summary.md`, section "Corpus fixes for v1.3".
