# Gap fill, stage 1: extract the missing items from saved pages (brief for delegated agents)

This brief is given verbatim to the external agents (codex, grok) that do stage 1. It is kept
in the repo so the instructions behind the data are on record.

## Project in two sentences

We study how mass-media outlets in Lebanon, Israel, Germany and the US covered the Lebanon
pager and walkie-talkie attacks of 17–18 September 2024, at the level of "what a reader of
outlet X was told". Every record must be traceable to the HTML it came from; nothing in the
data may be written, guessed, translated or summarised by a model.

## What stage 1 is

The recall audit (step 8) listed items each outlet published that our corpus is missing:
`data/<country>/08-recall-audit/gap-manifest.csv`. Almost all of them were already fetched
during the audit, and the HTML is saved locally. Stage 1 turns those saved pages into
candidate records. **It is entirely offline.**

## Hard rules (breaking any of these makes the whole output unusable)

1. **No network.** Run every command with
   `http_proxy=http://127.0.0.1:9 https_proxy=http://127.0.0.1:9`. If something seems to need a
   fetch, record it as a failure with reason `needs_fetch` and move on.
2. **Write only to these paths:**
   - your own new script(s) under `pipeline/05-extraction/round2/` (filenames given in your assignment)
   - `data/<country>/05-extraction/round2/` for your countries (create it)
   - new files under `data/<country>/raw/<outlet>/` whose names start with `r2-`
   Everything else is read-only. In particular never modify or delete: any `corpus.jsonl`,
   `candidates.jsonl` outside `round2/`, `excluded.jsonl`, manifests, anything under
   `08-recall-audit/`, existing raw files, existing scripts, docs, READMEs.
3. **No git commands** of any kind. No package installs. Python 3 standard library only.
4. **Text comes from the HTML, verbatim** (HTML entities unescaped, whitespace collapsed).
   Never translate, paraphrase, summarise, complete or "clean up" wording. Never fill a field
   by guessing. An empty field with a warning is always better than a plausible value.
5. **Dates only from the page itself** (JSON-LD `datePublished`, `article:published_time`,
   visible dateline, Telegram `<time datetime>`), or from the gap manifest's
   `published_date` when the audit verified it (`date_source = "audit-manifest"`). A Wayback
   capture timestamp is never a publication date.
6. **Do not tune the extractor to the gap items.** Tune it only against the regression set
   (rule 8), then run it once on the gap items.
7. **Stop instead of improvising.** If an outlet's extractor cannot pass the regression check,
   do not lower the bar: skip that outlet, explain why in the report, and continue with the
   others.

## Validation you must do and report

8. **Regression against the existing corpus.** For each outlet, take the primary records in
   `data/<country>/06-corpus/corpus.jsonl` that have a non-empty body and a `capture.raw_path`
   (relative to `data/<country>/`). Run your extractor on those raw files and compare to the
   stored `content.body`. Use `difflib.SequenceMatcher` ratio on whitespace-collapsed text
   (cap at the first 3,000 characters of each). Report per outlet: n, median ratio, share ≥ 0.90.
   **Bar: ≥ 80% of records at ≥ 0.90.** The stored bodies are not perfect; known exceptions
   are listed in your assignment. If an outlet misses the bar, look at the worst five and say
   whether the stored body or your extractor is wrong. Say it plainly; do not adjust numbers.
9. **Chrome check.** Across all bodies you extract for one outlet, list any sentence of 6+ words
   that appears in 3 or more bodies with different headlines. Expected: none, apart from bylines
   and agency credits. Report what you find and remove only true page chrome (menus, teasers,
   newsletter prompts, "read more" boxes), by container rules, never by deleting sentences
   one by one.
10. **Spot samples.** For each outlet, put 3 extracted records in the report (headline, date,
    first 200 and last 150 characters of body), chosen with `random.Random(2024)`.

## Output

`data/<country>/05-extraction/round2/candidates.jsonl`, one JSON object per gap-manifest row
(every row gets a record, also failures), with exactly these fields:

| field | content |
|---|---|
| `outlet` | as in the gap manifest |
| `url` | as in the gap manifest |
| `canonical_url` | from the page (`<link rel=canonical>` or `og:url`), Wayback prefix removed; else `url` |
| `gap_status`, `central_or_mention` | copied from the gap manifest |
| `fetch_route` | `live`, `wayback:<14-digit timestamp>`, `our-raw`, or `telegram-live` |
| `source_file` | the cached file you read, relative to `data/<country>/` |
| `raw_path` | the copy you wrote: `raw/<outlet>/r2-<first 16 hex of sha256(url)>.html.gz` (gzip of the exact bytes of `source_file`) |
| `title` | the article headline from the page (JSON-LD `headline`, else `og:title`, else `<h1>`); strip site suffixes like " – ntv.de" |
| `published_at` | `YYYY-MM-DD` or `""` |
| `published_time` | full ISO timestamp as on the page, or `""` |
| `date_source` | where the date came from (`ld-json`, `meta`, `dateline`, `telegram-ts`, `audit-manifest`) or `""` |
| `body_text` | article text, paragraphs joined with `\n` |
| `body_words` | `len(body_text.split())` |
| `extract_method` | the container rule used, e.g. `ld-json`, `container:RichTextStoryBody`, `p-cluster` |
| `document_type_hint` | `article`, `video_page`, `wire_feed`, `teletext`, `telegram_post`, `brief`, `live_ticker`, `newsletter`, `podcast_page`, `liveblog` |
| `paywall` | `true` if the page is a paywall teaser or lead |
| `provider` | for Yahoo pages the content provider shown on the page (AP, Reuters, …); for other outlets a wire credit only if the page states it; else `""` |
| `language` | `ar`, `he`, `en`, `de` by script/stopwords of the body |
| `ok` | `true` if headline and (body or a legitimately headline-only type) were extracted |
| `failure` | `""` or a short reason (`needs_fetch`, `no_container`, `wrong_page`, `empty`, …) |
| `warnings` | list of strings |

Rows whose `gap_status` is `live_blog` or `live_blog_unverified`: write a record with
`ok: false`, `failure: "deferred_liveblog"` and do not extract (stage 2 handles live blogs).

`data/<country>/05-extraction/round2/extraction-report.md` with: counts (rows, ok, failures by
reason, per outlet), the regression table, chrome-check findings, spot samples, every judgment
call you made, and anything you are unsure about. Keep it factual; no claims without numbers.

## Where things are

- Gap manifests: `data/<country>/08-recall-audit/gap-manifest.csv`.
- Cached pages, Germany and US: `data/<country>/08-recall-audit/raw/verify-cache.jsonl` (one JSON
  per fetched item; match by `pipeline/08-recall-audit/recall_audit_common.py:key(url)`; the page is
  `raw_file`, or for `fetch` values `our-raw:<path>` that path; both relative to `data/<country>/`).
- Cached pages, Israel and Lebanon: `data/<country>/08-recall-audit/raw/check-results*.jsonl` (field
  `raw`, relative to `data/<country>/`; match by `recall_audit_il_lb_common.url_key(url)`).
- Existing extraction logic to learn from (read, do not edit): `pipeline/05-extraction/*.py`,
  `pipeline/07-repair/repair_v12.py` (per-outlet container rules that fixed chrome problems),
  `pipeline/06-normalization/normalize_de_us.py` (`strip_boiler`), `pipeline/08-recall-audit/recall_audit_common.py`
  (`extract`), `pipeline/08-recall-audit/recall_audit_il_lb_common.py` (`extract`).
- Record schema and conventions: `docs/methodology/06-normalization.md`. Known outlet quirks:
  `data/<country>/05-extraction/triage-notes.md`, `data/<country>/04-enumeration/notes.md`.

## Finish

When done, reply with a short summary: per-outlet ok/failed counts, regression pass/fail per
outlet, the three most important problems, and the exact paths you wrote.

## Change after round 1 (2026-10-05)

Round 1 showed that the stored corpus bodies are not a clean reference: Spiegel, Bild, Fox and
Yahoo bodies in corpus v1.3.1 still contain page chrome (share bars, audio-player code, video
overlays, key-takeaway boxes). Comparing against them is therefore a diagnostic, not a gate.
Corpus v2 will re-extract every record, old and new, with the validated extractors. The gate
became five automatic checks on every extracted body, with ≥ 95% passing per outlet:

1. no known chrome strings and no sentence repeated across pages,
2. the page description's opening words appear in the first 400 characters,
3. no truncation (sentence-final ending; ≥ 90% of JSON-LD `articleBody` length where present),
4. no sentence of 8+ words repeated within a body,
5. paragraph order as in JSON-LD `articleBody` where present.

Every record below 0.90 against its stored body is classified as `stored_wrong`, `new_wrong` or
`both`, with a quote from the raw page (`round2/regression-adjudication.csv`). The re-extraction of
the existing corpus goes to `round2/reextract-v1.jsonl`.
