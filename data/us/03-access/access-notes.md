# US access verification — notes (step 3, v1, 2026-09-06)

Register: [access-register.csv](access-register.csv). Research:
copilot CLI 5-agent pass (access-research/copilot-raw.md) + local fetch
tests and Wayback CDX density (this session). 9 mass rows + AP/Reuters
baselines. **One partial (NYT bodies), zero unresolved blockers — every
row has a working text route.** CDX density (final, 2026-09-07):
abcnews/nbcnews 5,000+/32 days; cnn.com/2024/09 3,000+/30;
reuters.com/world 3,000+/33; apnews.com/article 3,000+/32; foxnews
1,048/33; cbsnews 1,172/29; wapo 905/29; yahoo/usatoday ~zero
(live-primary); nytimes CDX-blocked (see hard case 1).

## Route summary

Free-and-live: Fox, CNN, CBS, NBC, USA Today, Yahoo News, AP — all
fetch-tested with full bodies (1,000–8,600 p-words). Wayback-primary:
ABC (domain migration), Reuters (allowlist 401), WaPo (edge-blocked
live; day-of captures carry full metered text — tested 902 words 47 min
post-publish). NYT is the one partial row (below).

## Hard cases

1. **NYT — the hardest access case, evidence corrected post-review
   (2026-09-07).** The copilot claim "zero captures until Dec 2025" was
   **wrong** — the review demanded per-URL tests and they overturned it:

   | URL (real, extracted from live-blog capture) | capture |
   | --- | --- |
   | /2024/09/17/.../israel-hezbollah-pagers-explosives.html (flagship) | **20240919000841** |
   | /2024/09/17/.../israel-hezbollah-lebanon-war-impact.html | **20240918225116** |
   | /2024/09/17/.../israel-planted-explosives-in-pagers-sold-to-hezbollah... | none |
   | /live/2024/09/17/world/israel-hamas-war-news | 20240917234632, 6,018 p-words |

   Captured *standard* articles carry **lead-depth text only** (flagship
   capture: 368 p-words of a long investigation — paywall truncation in
   the captured page). Plan of record, three sub-routes: (a) live-blog
   captures = rich day-of hourly text; (b) standard-article captures =
   headline+lead records, the established Ynet flash_or_lead pattern;
   (c) Article Search API (free key) for enumeration + metadata —
   mandatory because **the CDX API itself 403s all nytimes.com
   queries** (captures fetchable per-URL, not enumerable). Licensed
   route (API full access/ProQuest) named if analysis needs full
   bodies. Live fetch 403s remain.
2. **ABC News**: 2024 `abcnews.go.com` wireStory URLs now redirect to
   abcnews.com and 404 — total link rot. Wayback-only for event-window
   content (day-of capture tested ok). Coverage was heavily AP
   wireStory reprints — flag for the wire/original split.
3. **Reuters**: robots is an allowlist; everything else 401s (blanket
   `Disallow: /` for unlisted agents). Day-of Wayback captures carry
   full ungated text (tested 1,847 words; 2024 had at most a free
   registration wall). Wayback primary, no fallback needed for the
   window.
4. **Yahoo News**: near-zero Wayback captures of article pages + 2026
   domain migration (news.yahoo.com → yahoo.com/news). Live route works
   with browser-UA curl (tested 1,054 words; python-urllib gets a thin
   consent/JS shell — EU GDPR consent wall risk from German IP, curl
   follows through). Enumeration is the weak point: rolling sitemap
   only. **Collection rule (post-review):** Yahoo is a
   syndication-discovery source, not an exhaustive archive — collect
   Yahoo pages found via provider tracking (USA Today/Gannett, AP,
   Reuters, AFP, Yahoo News UK bylines), record the provider byline on
   each record, and dedup-cluster against the source outlet's own copy.
   Verified mirror pair: usatoday .../75261807007/ =
   news.yahoo.com/hundreds-hezbollah-pagers-explode-apparent-151059022.html
   (word-for-word). Yahoo's *reach* is the analysis quantity; its text
   is mostly others'.
5. **USA Today**: live route clean, date-in-path URLs, but ~no
   contemporaneous Wayback captures (aggressive bot blocking incl.
   archive crawlers) — live-only row; if pages vanish, Gannett/Yahoo
   syndication mirrors are the fallback.
6. **WaPo**: live fetches time out (edge block) but CDX prefix queries
   work and day-of captures contain full metered text — Wayback
   primary.
7. **CNN transcripts**: `transcripts.cnn.com/date/2024-09-17` is a
   working dated index; per-segment pages carry full transcripts
   (tested 8,515 words, AC360 Sep 17). Best broadcast-text source of
   any TV outlet — collect alongside cnn.com articles. Other TV mass
   outlets (Fox/ABC/CBS/NBC) have no usable daily transcript archive —
   web article stream documented as the collection surface per the
   census's web-text scope, with the broadcast-proxy limitation noted.

## Enumeration hooks (for step 4)

| outlet | hook |
| --- | --- |
| CNN | `cnn.com/2024/09/17/...` date paths + monthly section sitemaps + transcripts date index |
| NYT | `/2024/09/17/` and `/live/2024/09/17/` date paths (via CDX/API) |
| WaPo | `/section/2024/09/17/slug/` date paths via CDX prefix |
| USA Today | `/story/news/world/2024/09/17/.../NNNNNNNNNNN/` date paths, live |
| CBS | dated monthly sitemaps `xml-sitemap/article-2024-09[-2].xml` (verified) |
| NBC | monthly sitemaps `sitemap/nbcnews/sitemap-2024-09-article.xml` (verified) |
| AP | monthly sitemaps back to 2006: `ap-sitemap-202409.xml` (verified) + topic hubs |
| Reuters | date-suffixed slugs `...-2024-09-17/` via CDX |
| Fox | news sitemap types; slug-only URLs — CDX + slug keyword tagging |
| ABC | Wayback CDX only (`wireStory/slug-NNNNNNNNN`) |
| Yahoo | syndication tracking, not enumeration |

## Robots/TDM stance

All outlets allow (or don't effectively prevent) archival-route
collection for the window except as noted; AI-training bots blocked by
name nearly everywhere; NYT cites EU TDM Art. 4 explicitly (active
OpenAI litigation context). **Reuters robots verbatim (fetched
2026-09-07):** named allowlist of ~80 agents, then
`User-agent: * / Allow: /plus/ / Disallow: /` — the blanket block is
robots policy AND separately enforced as HTTP 401 (two distinct facts,
per review). Route decisions documented per row; archival routes carry
IA's terms.

## v1.1 amendments (post-review, codex, 2026-09-07)

Review verdict US: fail-pending-correction → corrected same day. Key
overturn: NYT standard-article captures DO exist per-URL (copilot claim
falsified by availability-API tests) but are lead-depth; NYT plan
rewritten with per-URL evidence table. Reuters robots re-verified
verbatim against live file (reviewer's third-party snapshot was stale).
Yahoo fallback made operational (verified mirror pair + collection
rule). Reproduction protocol: all fetches curl/python UA
`Mozilla/5.0 ... Chrome/128.0`, 2026-09-06/07, words counted inside
`<p>` tags, recorded in register cells.
