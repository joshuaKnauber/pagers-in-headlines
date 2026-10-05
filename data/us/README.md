# US

Outlets collected (step 2 gate): Fox, CNN, ABC, CBS, NBC, NYT, WaPo, Yahoo News, USA Today; AP and Reuters as wire baselines.

Corpus v1.2.1: 131 primary records (CNN 30, Yahoo 30, Fox 21, NBC 15, WaPo 12, CBS 10, ABC 4, NYT 4, Reuters 4, USA Today 1). No AP records: every AP candidate fetch returned a Cloudflare challenge page.

Read before using:

- Recall Sep 17–24: 21% without Yahoo (Fox 53%, NBC 45%, CNN 41%; ABC, NYT, USA Today 5–6%). Reuters and WaPo could not be measured.
- Yahoo is almost all syndicated copy: treat Yahoo's own items and the syndicated feed separately.
- No live blogs or newsletters yet; video pages only from CNN.
- Steps 5 and 6 are documented together in `05-extraction/triage-notes.md`.

## Folders

| folder | what is in it |
|---|---|
| `01-census/` | `outlet-census.csv` (one row per outlet, tier), `census-notes.md` (evidence), `social-counts/` (raw assistant output) |
| `02-gate/` | `collection-gate.csv`: which outlets must be collected (derived from the census) |
| `03-access/` | `access-register.csv` and `access-notes.md`: the route used for each gated outlet, `research/` (raw assistant output) |
| `04-enumeration/` | URL manifest per outlet (`<outlet>-urls.csv`), `summary.csv`, `notes.md`; `.<outlet>-slices.done` (CDX resume markers); `codex-candidates*.txt` (LLM-suggested URLs for Fox, Yahoo, NYT, USA Today, WaPo, Reuters, merged as the curated layer) |
| `05-extraction/` | `candidates.jsonl` (triaged and fetched candidates), `triage-notes.md` (decisions and repair ledgers) |
| `06-corpus/` | `corpus.jsonl` (use `is_primary_record`), `CHANGELOG.md` |
| `08-recall-audit/` | `recall-audit-notes.md`, `reference-set.csv`, `gap-manifest.csv` (missing items, ready to collect) |
| `raw/` | fetched HTML; each record's `capture.raw_path` points here |
| `reviews/` | adversarial reviews, prefixed with the step they reviewed |

Method per step: `docs/methodology/`. Which script produced which file: `data/README.md`.
