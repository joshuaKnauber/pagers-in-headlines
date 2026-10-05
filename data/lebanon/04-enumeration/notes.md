# Lebanon enumeration — notes (step 4, v1, 2026-09-06)

Manifests in this directory; produced by
`pipeline/04-enumeration/enumerate_lebanon.py` (CDX layer) plus a GDELT merge pass.
Window: Sep 15 – Oct 17 2024. Review pending (codex dispatch).

## Results

| outlet | article URLs | event candidates | peak capture day |
| --- | --- | --- | --- |
| LBCI | 12,527 | 146 | Sep 17 (939) |
| Al Jadeed | 13,565 | 75 | Sep 17 (1,458) |
| MTV | 16,533 | 132 | Sep 23 (1,074) |
| Al-Manar | 3,733 (filtered) | 0 — numeric slugs, needs title triage | Sep 23 (295) |
| NNA | 448 | 2 | Oct 15 (90) |

## The Al-Manar ID-band filter (main methodological finding)

Raw CDX enumeration returned **168,789** numeric URLs — because the
Internet Archive ran **emergency deep-crawls of Al-Manar's entire history
during the war** (Sep 27–Oct 8: 12K–19K old URLs/day with article IDs from
5–9M). Al-Manar's IDs are sequential, and fresh-crawl days advance cleanly
(median 12,471,758 on Sep 15 → 12,591,405 on Oct 10, ≈4.8K IDs/day), so
the event-window *publication* band is **IDs 12,460,000–12,635,000**
(upper bound extrapolated to Oct 17). Filtered manifest: 3,733 URLs
(~110/day — plausible for a wire-heavy TV site). Raw list preserved in
`almanar-urls-raw.csv`.

Corollary: **first-capture date is NOT a publication-date proxy during
back-crawl periods.** For sequential-ID outlets, the ID is the better
ordering; for slug outlets, day-of crawling was dense enough that
first-capture is a rough proxy (flag Sep 23 and Sep 27–Oct 8 as
crawl-surge dates before reading per-day counts as publication counts).

Side-effect worth noting: the step-3 Al-Manar test capture (ID 10391493)
was an *old* article back-crawled on Sep 18 — the route verification
stands, but "day-of capture" there meant capture date, not publication.

## Recall findings

Recall check against the old hand-collected corpus URLs:

- LBCI 2/2, Al Jadeed 4/4 — clean.
- MTV 2/4 and NNA-EN 0/2 **missing — and CDX confirms those four URLs were
  never captured by Wayback at all** (not an enumeration bug; an archive
  coverage hole). Both MTV misses are lowercase `/en/news/...` path
  variants; both NNA misses are English-edition pages (EN is thin overall:
  67 of 448 manifest URLs).

Mitigations, in effect or planned: (a) the GDELT layer knows such URLs
(the old manifests came partly from GDELT discovery) — merged where the
API cooperates; (b) MTV misses are live-site direct-fetchable, so
*collection* recall is unaffected — only the Wayback-derived denominator
undercounts; (c) archived-sitemap enumeration (fetch `newssitemap.xml`
captures from the window) is the next recall source if the review deems
the hole material; (d) NNA English is documented as thin — the Arabic
edition is the primary NNA record.

## v1.1: review verdict and fixes (codex review, 2026-09-06)

Review verdict: manifests are fit as **triage input and captured-URL
lower bounds**, not yet as publication-volume denominators. It verified
the Al-Manar band logic hands-on (in-band captures = event window,
out-of-band = old corpus; slope consistent) and confirmed the Sep 23 MTV
peak is plausible (Israel's broadest air campaign on Lebanon began that
day — 492 reported deaths). Findings → status:

1. ~~Al-Manar Oct 11–17 was extrapolated, not enumerated~~ → **largely
   closed**: the Oct 17 homepage capture gives the observed upper ID
   **12,615,121** (extrapolated ceiling 12,635,000 was safely
   conservative), and daily homepage-capture harvesting added the Oct
   11–13 articles (+29; Oct 14–16 retry running — Wayback rate-limited
   the first pass). Bonus finding: archive.almanar.com.lb pages strip
   publication dates, so ID anchors must come from dated bulletin titles
   or homepage captures, not article pages.
2. **first_capture is NOT a publication proxy anywhere** (review found
   old MTV articles with 2024 first-captures) → per-day counts are
   relabeled *first-capture counts*; real publication dates get filled in
   step 5 extraction (article pages carry them) and become the daily
   denominator. `publication_date`/`date_source` columns to be added then.
3. **Archived-sitemap enumeration promoted from optional to required**
   for MTV and NNA-EN (the 0/4 recall probes can't be generalized, but
   the holes are real) — queued as the next enumeration source.
4. Recall probes to be re-run with query URLs recorded as artifacts.

## v1.2: sitemap source landed for MTV (2026-09-06)

The archived-sitemap route failed in its literal form (MTV's *archived*
monthly sitemaps are empty stubs; Al-Manar's wp-sitemap was never captured
in-window and Wayback silently redirects to 2025+ captures — always check
the returned capture's own timestamp). But MTV's **live**
`sitemaps.mtv.com.lb/archives/2024/sitemap-2024-m9/m10.xml.gz` are the
outlet's own complete monthly archives with `lastmod` dates:

- **+27,885 URLs merged** (MTV manifest: 44,418, covering all of Sep+Oct).
- **Both missing recall URLs recovered** — MTV recall is now 4/4.
- **28,616 rows carry real publication dates** (`date_source =
  sitemap-lastmod`) — MTV is the first outlet with a true publication
  denominator. Peak days self-validate against the war timeline: Oct 1
  (1,029; ground invasion), Sep 28 (879; Nasrallah's death), Sep 23–24.

Remaining per-outlet date/denominator status: MTV done; Al-Manar ordered
by sequential ID (band 12,460,000→observed 12,615,121 on Oct 17; Oct
14–16 bounded undercount documented — homepage captures redirect to
nearest neighbors); LBCI/Al Jadeed/NNA get publication dates in step-5
extraction (LBCI exposes `sitemap-archive.xml` — check it next as a
possible m9/m10-style source for LBCI/Al Jadeed too).

## Open items

- GDELT merge pass: API heavily rate-limited; rerun with 20–30 s throttle
  completed/merged per manifest (see `source` column values `gdelt` /
  `cdx+gdelt`).
- Al-Manar event-candidate tagging requires title-level triage (step 5):
  fetch capture titles for the 3,733 filtered URLs or match against GDELT
  titles; slug tagging is impossible on numeric URLs.
- MTV peak on Sep 23 needs a sanity note (massive Israeli strikes on
  Lebanon that day — plausible real surge; review will check).
