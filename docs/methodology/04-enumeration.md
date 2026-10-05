# Step 4: Enumeration

Build the denominator: for every gate-required outlet, the list of
candidate article URLs in the observation window, from sources independent
of our own collection effort. Enumeration is what turns "articles per day"
charts from a record of our effort into a measurement of the outlet's
output — and it converts "no coverage that day" into a recorded zero.

Consumes: the access register (step 3) — especially its *event-era URL
patterns*; produces: per-outlet URL manifests + a summary that step 5
(triage/extraction) consumes.

## Windows (two-layer design)

- **Core window, full enumeration:** Sep 15 – Oct 17 2024 (the daily-
  resolution analysis period). Every article-like URL, not just
  event-related ones — the denominator needs the outlet's *total* output.
- **Tail, milestone-anchored:** the documented milestone events (Mossad
  interviews, Katz sanctions, anniversary, …) get their own narrow
  enumeration windows later; the in-between silence is measured by cheap
  count-only queries, not full enumeration.

## Sources, in order

1. **Wayback CDX** (primary): prefix/domain query per outlet restricted to
   the **event-era article pattern from the access register** — never
   today's pattern (step 3 found two of five Lebanese outlets changed URL
   schemas since 2024). Paginate with `resumeKey`; salvage truncated JSON
   pages line-wise; keep first-capture timestamp as a rough
   publication-date proxy (day-of crawling was dense for all required
   Lebanese domains).
2. **GDELT DOC API** (keyword layer): event phrases per domain, native
   language + English, 1 request / 6 s. Catches URLs Wayback missed and
   provides seen-dates; also the cheap full-year volume layer for the tail.
3. **Outlet-native archives** (recall check, per census notes): archived
   sitemaps (fetch the outlet's `newssitemap.xml` *as captured in the
   window*), print-edition indexes (Al-Akhbar `/Issues/`), site search.
   Used to measure enumeration recall, not as the primary list.

## Tagging discipline

`event_candidate` in the manifest is a **recall aid for triage, not a
relevance verdict**: slug-keyword matching (URL-decoded, native-language
terms) plus anything GDELT surfaced. Numeric-URL outlets (Al-Manar) cannot
be slug-tagged — their triage needs title-level data (capture fetch or
GDELT titles). Relevance is decided in step 5 against title/body, never
from the slug alone.

## Implementation

`pipeline/04-enumeration/enumerate_lebanon.py` — outlet configs carry the event-era
`article_re` from the access register. Outputs
`data/<country>/04-enumeration/<outlet>-urls.csv`
(`url, first_capture, source, event_candidate`) and `summary.csv`. Rerun is
idempotent (full rewrite). Record per-outlet whether CDX pagination
completed (`cdx_complete`) — an incomplete enumeration understates the
denominator and must be flagged, not silently accepted.

## Done criteria

- Every gate-required outlet has a manifest with `cdx_complete = True` (or
  a documented reason plus a bounded estimate of what's missing).
- Per-day URL counts exist for the core window (the denominator).
- Event-candidate counts are plausible against the old corpus (an outlet
  we hand-collected 5 articles from should enumerate ≥ that many
  candidates — fewer means the pattern or keywords are wrong).
- Recall spot-check against one outlet-native archive source.
- Scoped review as usual.
