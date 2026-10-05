# Data

One folder per country. Inside each, numbered folders follow the pipeline in
order. `raw/` sits next to them because every step from 05 on reads it.

```
data/
  <country>/
    01-census/        which outlets people in the country actually use
    02-gate/          which of those must be collected
    03-access/        how each gated outlet can be reached (live, Wayback, API)
    04-enumeration/   URL manifests: every URL an outlet published in the window
    05-extraction/    candidates.jsonl: manifest URLs triaged as event-related, fetched, parsed
    06-corpus/        corpus.jsonl: the normalized corpus (current version, see CHANGELOG.md)
    08-recall-audit/  how complete the corpus is per outlet, and what is missing
    raw/              fetched HTML, one file per record (record field capture.raw_path)
    reviews/          adversarial reviews, named by the step they reviewed
  cross-country/
    08-recall-audit-summary.md   the four audits side by side
    09-claims/                   claim catalogue (step 9, in progress)
    reviews/                     reviews that covered all countries
```

Step 7 (repair passes) has no data folder: repairs rewrite `06-corpus/corpus.jsonl`
in place and are logged in `06-corpus/CHANGELOG.md`.

Method documents for each step: `docs/methodology/`. Scripts: `pipeline/`.

## Using the corpus

Read `06-corpus/corpus.jsonl` and keep records with
`deduplication.is_primary_record == true`. For questions about the attacks, also drop
`extraction.relevance == "context"` (records that never mention the devices). Current
primary counts (corpus v1.3.1): Lebanon 357, Israel 168, Germany 172, US 143. Records
removed by repairs are in `06-corpus/excluded.jsonl`, with reasons. Before using any count of the form
"outlet X never said Y", check that outlet's recall in `08-recall-audit/`.

## Lineage: what produced each file

Paths are relative to `data/<country>/`. "Manual" means research notes written by
hand or with LLM command-line assistants (raw assistant output is kept next to the
notes); no script regenerates them.

| step | output | produced by | input |
|---|---|---|---|
| 01 | `01-census/outlet-census.csv`, `census-notes.md` | manual research, reviewed (`reviews/01-*`) | audience studies, social counts (`01-census/social-counts*`) |
| 02 | `02-gate/collection-gate.csv` | `pipeline/02-gate/derive_collection_gate.py` | `01-census/outlet-census.csv` |
| 03 | `03-access/access-register.csv`, `access-notes.md` | manual verification (`03-access/research/` holds raw assistant output) | `02-gate/collection-gate.csv` |
| 04 | `04-enumeration/<outlet>-urls.csv`, `summary.csv` | `pipeline/04-enumeration/enumerate_lebanon.py` (LB), `enumerate_israel.py` (IL), `enumerate_de_us.py` (DE, US) | access register routes (Wayback CDX, sitemaps, dated archives, GDELT) |
| 04 | `04-enumeration/.<outlet>-slices.done` | `enumerate_de_us.py` resume markers, pruned by `verify_enum_slices.py` | |
| 04 | `israel/04-enumeration/<outlet>-titles-*.csv` | `pipeline/04-enumeration/title_sweep_israel.py` | `<outlet>-urls.csv` |
| 04 | `israel/04-enumeration/abuali-captures.csv` | `enumerate_israel.py` | Wayback captures of `t.me/s/abualiexpress` |
| 04 | `israel/04-enumeration/abuali-messages.csv` | **no saved script** (inline extraction from the 65 captures) | `abuali-captures.csv` |
| 04 | `lebanon/04-enumeration/almanar-titles.csv` | **no saved script** for the title sweep; tags added by `pipeline/07-repair/repair_v12_almanar_recover.py` | `almanar-urls.csv` |
| 04 | `us/04-enumeration/codex-candidates*.txt`, `germany/04-enumeration/copilot-welt-candidates-raw.txt` | URL lists suggested by LLM web searches (codex, copilot) | merged into the `-urls.csv` manifests by hand as the "curated" layer, see `04-enumeration/notes.md` |
| 05 | `05-extraction/candidates.jsonl`, `raw/` | `pipeline/05-extraction/extract_lebanon.py`, `extract_israel.py`, `extract_de_us.py` | manifests |
| 05 | `israel/05-extraction/candidates.jsonl` (v1.1 bodies) | `pipeline/07-repair/repair_v11_israel.py` | `raw/` |
| 06 | `06-corpus/corpus.jsonl` (v1/v1.1) | `pipeline/06-normalization/normalize_lebanon.py`, `normalize_israel.py`, `normalize_de_us.py` | `candidates.jsonl`, manifests, `raw/`, Abu Ali messages |
| 07 | `06-corpus/corpus.jsonl` (v1.2, v1.2.1) | `pipeline/07-repair/repair_v12.py`, `repair_v12_almanar_recover.py` | the v1.1 corpus, `raw/` |
| 07 | `06-corpus/corpus.jsonl` (v1.3, v1.3.1), `06-corpus/excluded.jsonl` | `pipeline/07-repair/repair_v13.py` | v1.2.1 corpus, `08-recall-audit/raw/corpus-issues.csv`, `raw/`; AP pages from Wayback; Abu Ali live preview |
| 08 | `08-recall-audit/reference-set.csv`, `gap-manifest.csv` | DE, US: `pipeline/08-recall-audit/recall_audit_build.py` (pool, verify, report); IL, LB: `recall_audit_il_lb_tasks.py`, `_check.py`, `_build.py` | independent discovery routes (Media Cloud, GDELT, outlet listings, archived homepages, live-blog paths), corpus, candidates, manifests |
| 08 | `08-recall-audit/recall-audit-notes.md` | written from the outputs above; tables from `recall_audit_analyze.py`, `recall_audit_il_lb_report.py`, `recall_audit_us_summary.py`, `recall_audit_us_yahoo.py` | |
| 09 | `cross-country/09-claims/claim-catalogue.jsonl` | manual research with corpus keyword sweeps, see `claim-catalogue-notes.md` | all four corpora |

Re-running steps 04, 05 and the fetch parts of 08 hits live sites and the Wayback
Machine, so results will differ from the stored files. Steps 02, 06 and the report
parts of 08 are offline and reproduce the stored files exactly. Re-running 06
gives the v1.1 corpus; apply 07 (v1.2 and its fixups, v1.3 and its fixups) afterwards to get the current version.
