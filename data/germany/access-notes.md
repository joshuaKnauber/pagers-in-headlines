# Germany access verification — notes (step 3, v1, 2026-09-06)

Register: [access-register-v1.csv](access-register-v1.csv). Research:
codex CLI web-search pass (access-research/codex-raw.md) + local fetch
tests and Wayback CDX density (this session; final numbers 2026-09-07).
All 8 mass rows + dpa baseline + RND representative verified. **No
gate-blocking rows; one material direct-access constraint (RND rejects
non-browser clients — Wayback primary, headless direct is an untested
contingency).** CDX density: tagesschau/zdf/ntv/spiegel/t-online/rnd 5,000+
URLs over 30–33 of 33 window days; rtl.de/news 1,328/28; welt.de
1,685/33 (thin — ia_archiver block); bild.de 5,000+ but only 16 days
(spotty — direct primary).

## Route summary

Germany is the easiest country so far: every mass outlet serves 2024
event articles live, free, with real body text (fetch-tested day-of;
p-word counts 700–1,300 per test article). Breaking pager coverage was
outside the plus-paywalls everywhere (BILDplus/SPIEGEL+/WELTplus gate
marked premium pieces; the event-window breaking stream was free).

## Hard cases and findings

1. **RND (rnd.de) blocks non-browser clients** (Akamai; python urllib
   and curl both 403). Primary route = Wayback (CDX density 5,000+ URLs,
   31/33 days). Bonus: RND exposes per-day archive pages
   (`rnd.de/archiv/artikel-DD-MM-YYYY/`) — usable through Wayback
   captures as an enumeration index. Fallback: headless browser.
2. **ZDFheute identity trap (resolved)**: `zdfheute.de` has **zero
   Wayback captures before Oct 2025** — in Sep 2024 the canonical
   archived host was **`zdf.de/nachrichten/...`** (day-of capture of the
   pager article verified at 2024-09-20 under that path; zdf.de density
   5,000+/33 days). Live, both hosts serve the same article today
   (zdf.de redirects to zdfheute.de — the mirror image of the archive
   situation). Direct route primary; enumeration/fallback must use the
   `zdf.de/nachrichten` prefix, never zdfheute.de.
3. **welt.de blocks ia_archiver** → thinnest Wayback density of the
   mass set (1,685 URLs, but all 33 days covered). Direct route works
   and WELT has news/video sitemaps — direct primary, Wayback fallback
   acceptable for headline-evolution checks only.
4. **Depublizierung (public broadcasters)**: less severe than feared —
   both test articles (tagesschau.de Sep 17, zdfheute.de Sep 17) are
   still live in 2026. ARD retention rules vary by format (video
   stricter than text). Both domains have dense Wayback coverage
   (5,000+/33 days) as the day-of source regardless.
5. **dpa** has no public archive (B2B wire). Baseline route = credited
   client copies: t-online ("Von dpa" — itself a gate row), plus
   hz.de and stuttgarter-zeitung.de examples verified by codex. The
   t-online dpa stream doubles as the wire baseline, mirroring
   Lebanon's NNA approach.

## Enumeration hooks (for step 4)

| outlet | hook |
| --- | --- |
| Bild | dated archive page `?archiveDate=2024-09-17` (fetch-tested, 4.7K words of links) + news sitemaps |
| RND | per-day archive pages via Wayback |
| ntv | sequential `articleNNNNNNNN` IDs + sitemaps |
| WELT | numeric `(video\|article)NNNNNNNNN` IDs + sitemaps |
| t-online | sequential `id_NNNNNNNNN` IDs |
| Spiegel | slug + `a-UUID`; no dated sitemap — CDX enumeration |
| Tagesschau | topic slugs `libanon-hisbollah-pager-NNN.html`; CDX enumeration |
| ZDFheute | `-100.html` suffixed slugs; topic pages; CDX enumeration |
| RTL | numeric `idNNNNNNN` slugs; RSS; CDX enumeration |

## Robots/TDM stance (recorded, not a route decision)

Four distinct dimensions per outlet (post-review precision — "crawling
allowed" alone is too broad):

- **Browser-readable**: all 9 sites (RND only via real browser/archive).
- **Generic bot (`User-agent: *`) permitted on articles**: all except
  RND in practice (robots permits, server blocks).
- **Archive bot**: welt.de and bild.de disallow `ia_archiver` — visible
  as thin/spotty Wayback density; others permit.
- **TDM/AI reservation**: all block AI-training bots by name;
  tagesschau.de, t-online.de, rnd.de carry explicit §44b UrhG
  reservations; RND/t-online additionally prohibit automated commercial
  collection in prose.

Route decisions documented per row; archival (Wayback) routes carry the
Internet Archive's own terms.

## Reproduction protocol (review finding 1)

All test fetches: curl/python with UA
`Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/128.0`,
dates 2026-09-06/07, HTTP 200 verified, body measured as words inside
`<p>` tags, event-term counts recorded in register test_result cells.
ZDF host finding demonstrated twice: zdf.de/nachrichten captures
20240920221950 (libanon-pager-explosionen-israel-100) and
20240918064002 (hisbollah-pager-explosionen-100); same slugs under
zdfheute.de have no capture before Oct 2025 (availability API).
