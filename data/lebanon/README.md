# Lebanon

Outlets collected (step 2 gate): LBCI, MTV, Al Jadeed, Al-Manar; NNA as the wire baseline.

Corpus v2.0: 837 primary records (MTV 341, LBCI 233, Al Jadeed 135, Al-Manar 121, NNA 7), 28 of them `context`; 38% are headline-only ticker items and briefs.

Read before using:

- Recall figures below are from the audit of corpus v1. Against the same reference set v2 is near 100% by construction (round 2 collected exactly those items); a fresh audit after the stage-3 re-sweep is pending.
- Recall Sep 17–24: 33–45% per outlet; 10% or less for articles that only mention the attacks in the body. NNA's reference is too thin to trust (29% on 7 items).
- Many records are live-ticker items and briefs: analyse them by headline.
- Al Jadeed: in v2 about half the items have article text; 65 of 135 primary records are headline-only (empty article container on the page).
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
