# Israel enumeration — notes (step 4, v1, 2026-09-06)

Script: `pipeline/04-enumeration/enumerate_israel.py`; manifests in this directory.
Window Sep 15 – Oct 17 2024. All four CDX enumerations **complete**
(pagination finished, no caps hit).

| outlet | urls / captures | peak capture day | note |
| --- | --- | --- | --- |
| Ynet | 13,492 | Sep 26 (3,339) | peak is a crawl surge (capture-date artifact — Lebanon lesson: not publication volume) |
| N12 (mako paths) | 4,506 | Sep 18 (310) | peak aligns with the event — organic |
| Kikar | 5,229 | Sep 15 (653) | crawl-schedule artifact |
| Makan | 647 | Sep 16 (121) | modest but complete |
| Abu Ali | 65 snapshots | — | see coverage caveat |

## Key points

1. **Capture-date ≠ publication date** (applied from Lebanon): per-day
   counts above are crawl artifacts where flagged. Publication dates come
   at step 5 from JSON-LD `datePublished`, which both Ynet and mako serve
   in-page (review-verified) — expected date quality: high. Ynet exposes
   no dated archive sitemaps (live rolling feeds only), so there is no
   MTV-style sitemap denominator; the publication denominator will be
   built from dated article pages instead.
2. **Abu Ali coverage corrected**: 65 snapshots covering **20 of 33 days**
   — not continuous. Each rolling-page capture holds only the ~20 latest
   messages, so days without captures may have unarchived messages. The
   register's fallback (live `t.me/s` `?before=` pagination) is therefore
   a real requirement for completeness, not a formality. Extraction must
   measure the per-day message gap explicitly.
3. **Candidate tagging deferred by design**: Israeli article URLs are
   opaque (Ynet alphanumeric, mako hex, Kikar short slugs) — zero slug
   candidates expected and produced. Step 5 runs a title sweep (Ynet/mako
   titles from captures or live pages) with Hebrew families:
   ביפר/ביפרים, מכשירי קשר, איתורית, מבצע, plus register terms
   (מחבלים, פיצוץ/פוצצו).
4. n12.co.il alias URLs (shortlink domain) — canonicalized onto mako
   paths per the access review.

## Next (step 5)

Title sweep over Ynet (13.5K) + mako (4.5K) + Kikar (5.2K) + Makan (647)
via day-of captures or live pages; Abu Ali message extraction from the 65
captures with cross-capture dedup + gap measurement; then extraction of
tagged candidates through the (Lebanon-hardened) pipeline: container
discipline, ticker genre-typing, boilerplate line/prefix QC, publication
dates from JSON-LD.
