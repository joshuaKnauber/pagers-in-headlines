# Pipeline

Scripts grouped by step. The method behind each step is in `docs/methodology/`, and
`data/README.md` lists which script produced which file.

Steps 1 (census) and 3 (access verification) are research steps with no scripts.

| folder | scripts | network? |
|---|---|---|
| `02-gate/` | `derive_collection_gate.py`: gate status for every census row, from the census fields alone | no |
| `04-enumeration/` | `enumerate_lebanon.py`, `enumerate_israel.py`, `enumerate_de_us.py <germany\|us\|all>`: URL manifests per outlet. `verify_enum_slices.py`: re-opens CDX slices that silently returned Wayback 504 pages. `title_sweep_israel.py`: fetches titles for Israel's opaque article URLs | yes |
| `05-extraction/` | `extract_lebanon.py`, `extract_israel.py <outlet…>`, `extract_de_us.py <germany\|us>`: fetch tagged candidates, save `raw/`, write `candidates.jsonl` | yes |
| `06-normalization/` | `normalize_lebanon.py`, `normalize_israel.py`, `normalize_de_us.py <germany\|us>`: candidates → `corpus.jsonl` | no |
| `07-repair/` | `repair_v11_israel.py`, `repair_v12.py <country>\|fixups [--dry]`, `repair_v12_almanar_recover.py`: versioned repair passes on the corpus | only the Al-Manar recovery |
| `08-recall-audit/` | discovery, verification and report scripts, see `docs/methodology/08-recall-audit.md` | discovery and verify: yes; report: no |

Run scripts from anywhere: each one finds `data/` relative to its own location.

Re-running a network step today gives different results from the stored files: pages
have changed, and Wayback rate limits vary. Re-running `06-normalization` overwrites the
corpus with the pre-repair v1.1 version. Apply `07-repair` afterwards to get the
current version back.

Verified on 2026-10-05, after the restructure: every offline step (02, 06, 07 `--dry`,
08 report and build) reproduces the stored outputs byte for byte.
