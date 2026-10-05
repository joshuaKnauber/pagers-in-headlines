# Step 8: recall audit

Question: of what each outlet published between Sep 17 and Sep 24 2024 that mentions
the pager or walkie-talkie attacks, how much is in the corpus, and why is the rest
missing? The answer bounds every "not in our sample" statement made later.

Outputs per country, in `data/<country>/08-recall-audit/`:

- `reference-set.csv`: verified items with discovery route, central or mention class,
  pipeline status and the matching `document_id` if the item is in the corpus.
- `gap-manifest.csv`: missing items with a working collection route (live URL or
  Wayback capture timestamp). This is the input for the gap fill.
- `recall-audit-notes.md`: method, recall per outlet, causes, fixes, corpus issues.
- `raw/` (not in git): fetched pages and intermediate files. It can be rebuilt, but that
  takes hours of archive.org requests.

Cross-country summary: `data/cross-country/08-recall-audit-summary.md`.

## Discovery routes

The reference set must come from routes the pipeline did not use, or recall is
measured against itself.

| route | used for | independent of the pipeline? |
|---|---|---|
| Media Cloud full-text search | DE, US, Al-Manar | yes: own crawler, matches body text |
| GDELT 2.0 raw GKG files (15-minute dumps) | all | yes for most outlets; not for Yahoo, Fox, NYT, USA Today, whose manifests used GDELT |
| outlet-native dated listings (daily archives, sitemaps) | DE, US, Lebanon (ID census) | yes |
| archived homepages and section pages | DE, US | link-based, but still Wayback |
| live-blog path CDX queries | DE, US | same mechanism as the pipeline, on paths it excluded |
| Abu Ali live Telegram preview | Israel | yes |
| random samples of untitled manifest URLs | Israel, Lebanon | stratified, extrapolated |

## Verification

Every candidate is fetched (from our raw HTML, live, or from Wayback near Sep 20) and
checked on its body text:

- **Mention:** a strong device term (pager, walkie-talkie, Funkgerät, ביפר, بيجر …) or a
  weak device phrase near Lebanon or Hezbollah. Link text and site chrome don't count.
  Site chrome means short paragraphs that recur on 3 or more differently titled pages
  of one outlet.
- **Central:** the term is in the headline, the description or the first ~700 characters.
- **Window:** best available date between Sep 17 and Sep 24. Live blogs count if they
  have a capture in the window.

Israel and Lebanon report census recall: corpus items divided by corpus items plus
missing items found plus an extrapolation for strata that were only sampled. Germany
and the US report reference-set recall. The two are close but not directly comparable.

## Scripts

`pipeline/08-recall-audit/`:

- **Germany, US:**
  - `recall_audit_mediacloud.py`, `_gdelt.py`, `_listings.py`, `_wayback_pages.py`,
    `_liveblogs.py`, `_cnn_live.py`, `_cdx_sections.py`: discovery.
  - `recall_audit_build.py <country> pool|verify|report`: merges the routes, verifies
    the candidates and writes the outputs.
  - `_cdx_refetch.py`: retries failed verifications against status-200 captures.
  - `_analyze.py`, `_us_summary.py`, `_us_yahoo.py`, `_spotcheck.py`: diagnostics.
- **Israel, Lebanon:**
  - `recall_audit_il_lb_gdelt.py`, `_mediacloud.py`, `_abuali.py`: discovery.
  - `_tasks.py`: builds the task lists.
  - `_check.py`: fetches and checks the items.
  - `_build.py`: writes the outputs.
  - `_report.py`: prints the tables.

The `report` and `build` stages are offline and reproduce the stored outputs from
`raw/`.
