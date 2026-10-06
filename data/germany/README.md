# Germany

Outlets collected (step 2 gate): Tagesschau, ZDFheute, RTL, ntv, Bild, Spiegel, WELT, t-online; RND for the regional press; dpa as the wire baseline (no own route, seen through t-online and WELT).

Corpus v2.0: 407 primary records (Tagesschau 80 incl. 56 live-blog entries, WELT 63, Spiegel 62, ntv 60, t-online 49, Bild 39, RND 30, ZDFheute 16, RTL 8), 32 of them `context` (no device wording, mostly escalation coverage).

Read before using:

- Recall figures below are from the audit of corpus v1. Against the same reference set v2 is near 100% by construction (round 2 collected exactly those items); a fresh audit after the stage-3 re-sweep is pending.
- Recall Sep 17–24: 39% overall (ntv 14%, WELT 22%, t-online 64%); 16% for articles that only mention the attacks.
- No live blogs, no dpa newsticker pages, no RTL teletext yet.
- Steps 5 and 6 are documented together in `05-extraction/triage-notes.md`.

## Folders

| folder | what is in it |
|---|---|
| `01-census/` | `outlet-census.csv` (one row per outlet, tier), `census-notes.md` (evidence), `social-counts.md` |
| `02-gate/` | `collection-gate.csv`: which outlets must be collected (derived from the census) |
| `03-access/` | `access-register.csv` and `access-notes.md`: the route used for each gated outlet, `research/` (raw assistant output) |
| `04-enumeration/` | URL manifest per outlet (`<outlet>-urls.csv`), `summary.csv`, `notes.md`; `.<outlet>-slices.done` (CDX resume markers); `copilot-welt-candidates-raw.txt` (LLM-suggested WELT URLs, merged as the curated layer) |
| `05-extraction/` | `candidates.jsonl` (triaged and fetched candidates), `triage-notes.md` (decisions and repair ledgers) |
| `06-corpus/` | `corpus.jsonl` (use `is_primary_record`), `CHANGELOG.md` |
| `08-recall-audit/` | `recall-audit-notes.md`, `reference-set.csv`, `gap-manifest.csv` (missing items, ready to collect) |
| `raw/` | fetched HTML; each record's `capture.raw_path` points here |
| `reviews/` | adversarial reviews, prefixed with the step they reviewed |

Method per step: `docs/methodology/`. Which script produced which file: `data/README.md`.
