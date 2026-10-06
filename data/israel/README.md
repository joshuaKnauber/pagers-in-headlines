# Israel

Outlets collected (step 2 gate): Ynet, N12; Kikar HaShabbat (Haredi), Makan 33 (Arabic) and Abu Ali Express (Telegram) as representatives of their layers.

Corpus v2.0: 470 primary records (Ynet 221, Abu Ali 123, N12 59, Kikar 50, Makan 17), 11 of them `context`.

Read before using:

- Recall figures below are from the audit of corpus v1. Against the same reference set v2 is near 100% by construction (round 2 collected exactly those items); a fresh audit after the stage-3 re-sweep is pending.
- Recall Sep 17–24: Ynet 40%, Kikar 38%, Abu Ali 18%, N12 about 6%; Makan has no independent check.
- Ynet bodies are paywall leads (`flash_or_lead`): analyse by headline and lead.
- Abu Ali's first pager post is 12:57 UTC (message 75653, added in v1.3), two minutes before N12's first item.

## Folders

| folder | what is in it |
|---|---|
| `01-census/` | `outlet-census.csv` (one row per outlet, tier), `census-notes.md` (evidence), `social-counts/` (raw assistant output) |
| `02-gate/` | `collection-gate.csv`: which outlets must be collected (derived from the census) |
| `03-access/` | `access-register.csv` and `access-notes.md`: the route used for each gated outlet |
| `04-enumeration/` | URL manifest per outlet (`<outlet>-urls.csv`), `summary.csv`, `notes.md`; `<outlet>-titles-*.csv` (title sweep), `abuali-captures.csv`, `abuali-messages.csv` |
| `05-extraction/` | `candidates.jsonl` (triaged and fetched candidates), `triage-notes.md` (decisions and repair ledgers) |
| `06-corpus/` | `corpus.jsonl` (use `is_primary_record`), `CHANGELOG.md`, `normalization-notes.md` |
| `08-recall-audit/` | `recall-audit-notes.md`, `reference-set.csv`, `gap-manifest.csv` (missing items, ready to collect) |
| `raw/` | fetched HTML; each record's `capture.raw_path` points here |
| `reviews/` | adversarial reviews, prefixed with the step they reviewed |

Method per step: `docs/methodology/`. Which script produced which file: `data/README.md`.
