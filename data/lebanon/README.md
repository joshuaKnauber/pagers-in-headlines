# Lebanon

Outlets collected (step 2 gate): LBCI, MTV, Al Jadeed, Al-Manar; NNA as the wire baseline.

Corpus v1.2.1: 359 primary records (LBCI 110, MTV 125, Al-Manar 63, Al Jadeed 59, NNA 2).

Read before using:

- Recall Sep 17–24: 33–45% per outlet; 10% or less for articles that only mention the attacks in the body. NNA could not be measured.
- Many records are live-ticker items and briefs: analyse them by headline.
- Al Jadeed records are headline-only (bodies were page chrome, removed in v1.2.1).
- Census v1 is in `archive/lebanon-census-v1/`.

## Folders

| folder | what is in it |
|---|---|
| `01-census/` | `outlet-census.csv` (one row per outlet, tier), `census-notes.md` (evidence) |
| `02-gate/` | `collection-gate.csv`: which outlets must be collected (derived from the census) |
| `03-access/` | `access-register.csv` and `access-notes.md`: the route used for each gated outlet |
| `04-enumeration/` | URL manifest per outlet (`<outlet>-urls.csv`), `summary.csv`, `notes.md`; `almanar-titles.csv` (Al-Manar title sweep) |
| `05-extraction/` | `candidates.jsonl` (triaged and fetched candidates), `triage-notes.md` (decisions and repair ledgers) |
| `06-corpus/` | `corpus.jsonl` (use `is_primary_record`), `CHANGELOG.md`, `normalization-notes.md`, `normalization-quality.csv` (disposition of every candidate) |
| `08-recall-audit/` | `recall-audit-notes.md`, `reference-set.csv`, `gap-manifest.csv` (missing items, ready to collect) |
| `raw/` | fetched HTML; each record's `capture.raw_path` points here |
| `reviews/` | adversarial reviews, prefixed with the step they reviewed |

Method per step: `docs/methodology/`. Which script produced which file: `data/README.md`.
