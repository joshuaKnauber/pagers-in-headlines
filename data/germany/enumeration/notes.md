# Germany enumeration — notes (step 4, v1, 2026-09-14)

Script: `data/scripts/enumerate_de_us.py` (time-sliced CDX + native
sources); manifests in this directory. Window Sep 15 – Oct 17 2024.
**51,290 URLs across 9 outlets; 282 slug-tagged candidates.**

| outlet | urls | source | candidates | note |
| --- | --- | --- | --- | --- |
| t-online | 14,850 | CDX | 70 | largest manifest (portal volume) |
| Bild | 10,594 | dated archive pages | 29 | **complete daily output** (~340/day) — Germany's displacement denominator |
| Tagesschau | 8,869 | CDX | 26 | |
| ZDFheute | 6,110 | CDX (zdf.de/nachrichten prefix) | 28 | 2024 archive host per access register |
| RND | 4,097 | CDX | 31 | Wayback-primary outlet |
| Spiegel | 2,956 | CDX | 62 | |
| ntv | 2,433 | CDX | 18 | |
| RTL | 1,321 | CDX | 2 | thin candidates = genuinely thin text coverage (TV brand) |
| WELT | 60 | CDX + curated (copilot) | 16 | ia_archiver block starves CDX; curated recall layer |

## Method notes / pitfalls hit

1. **Wayback served nginx-504 pages as HTTP 200** — slices completed
   "+0" and were wrongly marked done. Detection added (HTML body ⇒
   retry); a verification pass re-ran every zero-row slice.
   Recovered: t-online +2,887, Spiegel +240. Lesson is now part of the
   toolkit: *a CDX response starting with `<` is a failure.*
2. Slug tagging (German terms incl. pager/piepser/funkger/walkie/
   gold-apollo + Libanon/Hisbollah×event combos) replaces Israel-style
   title sweeps — German URLs carry descriptive slugs.
3. A handful of tail slices per outlet still failed after retries
   (flagged in `.{outlet}-slices.done` gaps); measured effect is small
   (late-window, low-coverage days) and documented rather than silently
   accepted.
4. GDELT was rate-limited to unusability during the run — the WELT
   supplement came from a copilot curated pass instead.

Next (step 5): extraction via live routes (all outlets except RND →
Wayback), JSON-LD first; body-level relevance retag; chrome QC
(share-bars, EILMELDUNG templates) handled in normalization.
