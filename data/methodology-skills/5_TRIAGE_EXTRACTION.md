# Step 5: Triage and extraction

Turn enumeration candidates into verified corpus records: fetch every
event-candidate URL via its register route, confirm relevance against
title/body (never the slug alone), and extract the core fields with real
publication dates. Consumes: enumeration manifests (step 4) + access
register routes (step 3). Produces: `data/<country>/corpus-candidates-v1.jsonl`
plus raw HTML under `data/<country>/raw/` (kept out of any published
artifact — copyright boundary per project policy).

## Procedure

1. **Candidate set** = manifest rows with `event_candidate = 1`, plus the
   outputs of any title-sweep for numeric-URL outlets (Al-Manar pattern:
   sweep titles via its archive subdomain, tag by title keywords, then
   feed tagged rows back through this step).
2. **Fetch by register route** (live direct → Wayback for slug outlets;
   archive subdomain for Al-Manar; Wayback-only for NNA), politely paced.
   Save raw HTML with a URL-hash filename; never overwrite.
3. **Extract light fields**: og:title/title, published date
   (article:published_time / JSON-LD / manifest sitemap-lastmod fallback),
   body text via largest-<p>-cluster heuristic. Full schema normalization
   (the corpus-schema-v1 field groups) happens downstream — this step's
   job is verified relevance + dates + text presence.
4. **Relevance tiers**, decided on title+body: `strong` (pager terms,
   native + English), `related` (walkie-talkie/device-attack terms),
   `none` (enumeration false positive — kept in the file as a record of
   triage, excluded from the corpus). A `fetch-failed` tier flags rows
   needing a route retry.
5. **QC gates** before records feed the corpus: body_words above a floor
   (else flag), published_at present (manifest date acceptable with
   `date_source` recorded), and per-outlet strong-count sanity versus the
   old hand-collected corpus.
6. Scoped review as usual (spot-reproduce fetches, audit relevance calls
   on a sample, check date extraction against visible page dates).

## Pitfalls (Lebanon-run findings)

- Numeric-URL outlets need the title sweep *first*; slug keyword tagging
  finds zero candidates there by construction.
- Archive-subdomain pages may strip dates (Al-Manar) — dates then come
  from ID-position or bulletin-title anchors, recorded as such.
- Wayback nearest-capture redirects can serve a capture months away —
  always compare the returned capture timestamp against the requested one.
- Live sites may 301 event-era URLs to redesigned pages with different
  markup (NNA) — extraction must run against the *fetched* body, and the
  route field records which era's markup was parsed.
