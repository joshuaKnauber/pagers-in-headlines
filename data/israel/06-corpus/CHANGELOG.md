# Israel corpus: changelog

`corpus.jsonl` is always the current version. Earlier versions survive only where they were
committed: 52af888 holds Lebanon at 338 primary and Israel v1 at 153 primary; e79be10 holds v1.2.1
for all four countries. Other intermediate versions were not committed. Record schema:
`1.1.0-phase1` throughout.

## v1 (2026-09-06)

Produced by: `pipeline/05-extraction/extract_israel.py`, `pipeline/06-normalization/normalize_israel.py`.

153 primary (commit 52af888). First corpus from the title sweep and Abu Ali message extraction.

## v1.1 (2026-09-06)

Produced by: `pipeline/07-repair/repair_v11_israel.py`, then normalization re-run.

157 primary. Kikar and N12 bodies re-extracted from their article containers (page chrome had inflated term counts), singular-device recall gap (+5 Ynet), Abu Ali capture-overlap duplicate collapsed, 3 non-event strong tags downgraded. Ledger: `05-extraction/triage-notes.md`, "v1.1 amendments"; results in `06-corpus/normalization-notes.md`.

## v1.2 (2026-09-16)

Produced by: `pipeline/07-repair/repair_v12.py israel` (+ inline Abu Ali additions).

166 primary. N12 mako path-twin collapsed, Makan bodies re-extracted, `published_time` recovered for every primary record, +10 Abu Ali posts the device-word rule had dropped. Ledger: `05-extraction/triage-notes.md`, "v1.2 repair pass".

## v1.2.1 (2026-09-16)

Produced by: v1.2.1 fix-ups (`python3 pipeline/07-repair/repair_v12.py fixups`, same day, after the codex review in `data/cross-country/reviews/07-repair-v12-review-codex.md`).

Word counts recomputed; no other change.

## Next: v1.3 (planned)

Fixes listed by the recall audit, see
`data/cross-country/08-recall-audit-summary.md`, section "Corpus fixes for v1.3".
