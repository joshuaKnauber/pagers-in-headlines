# Step 6: normalization

Turns the step-5 candidates into one record schema shared by all countries,
`data/<country>/06-corpus/corpus.jsonl` (schema `1.1.0-phase1`).

Scripts: `pipeline/06-normalization/normalize_lebanon.py`, `normalize_israel.py`,
`normalize_de_us.py <germany|us>`. Offline: they read `05-extraction/candidates.jsonl`,
the step-4 manifests and `raw/`, and fetch nothing.

## Record fields

| group | fields | notes |
|---|---|---|
| `source` | `page_publisher`, `country_or_media_system`, `language` | language is detected from the text, not assumed from the outlet |
| `publication` | `published_at`, `date_source`, `time_slot`, `document_type`, `canonical_url` | `time_slot` buckets: day_0, day_1, day_2, …, week_2, first_month |
| `content` | `headline`, `body`, `word_count`, `body_sha256` | |
| `provenance` | `credit`, `content_origin` | wire credits (dpa, AP, Reuters, …) kept separately from the outlet |
| `capture` | `collection_route`, `raw_path` | `raw_path` is relative to `data/<country>/` |
| `extraction` | `method`, `relevance`, `warnings` | relevance `strong` or `related` from step 5 |
| `deduplication` | `exact_duplicate_cluster_id`, `is_primary_record` | analysis uses primary records only |

## Rules

- **Window.** Records dated outside Sep 17 – Oct 17 2024 are dropped. Recaptures of
  older pages that enumeration picked up are caught here.
- **Dates.** In order of preference: page JSON-LD or meta, Telegram timestamps, sitemap
  lastmod, and as a last resort interpolation from sequential article IDs (24 MTV records
  today). `date_source` records which one was used; a `-v12` suffix marks dates repaired
  in step 7.
- **Document type.** `article`, `live_ticker`, `brief`, `flash_or_lead` (paywall leads and
  bodies under about 90 words), `telegram_post`, `press_review`, `video_page`. Lebanese
  coverage is heavy on tickers and briefs, Israeli coverage on paywall leads. These are
  not quality failures; they decide whether an item is analysed by headline or by body.
- **Chrome removal.** Lines that recur in 30% or more of one outlet's bodies are cut
  (Lebanon, Germany, US). For Germany and the US, whose bodies are single lines, a long
  prefix shared by 60% or more of an outlet's bodies is cut as well; that rule came out of
  Al Jadeed, whose live fetches carried a 2026 ticker widget. Israel's chrome was removed
  by container re-extraction (step 7, v1.1).
- **Duplicates.** Records with identical bodies form a cluster with one primary record.
  URL variants (AMP, mobile, path twins) were collapsed later, in the step-7 repairs.

Per-country results and limitations: `data/<country>/06-corpus/normalization-notes.md`
(Lebanon, Israel) and `05-extraction/triage-notes.md` (Germany, US, which document
steps 5 and 6 together). Version history: `06-corpus/CHANGELOG.md`.
