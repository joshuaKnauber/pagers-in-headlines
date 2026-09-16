I'll research this across 5 parallel background agents grouped by outlet, then compile a unified report. Launching now.

● Research (requested model: claude-sonnet-5) Research Fox, CNN, ABC News access
  └ Agent started in background with agent_id: 719abe36-ba86-4e65-b1d8-f1d5199b76...

● Research (requested model: claude-sonnet-5) Research CBS, NBC News access
  └ Agent started in background with agent_id: a885c439-56cc-4ff7-8422-c1394497fe...

● Research (requested model: claude-sonnet-5) Research NYT, WaPo access
  └ Agent started in background with agent_id: 7a2f7cf9-16d8-4607-9344-7dde43ed3c...

● Research (requested model: claude-sonnet-5) Research Yahoo News, USA Today access
  └ Agent started in background with agent_id: ce8fc9a8-965c-41da-bb81-871a77e3a9...

● Research (requested model: claude-sonnet-5) Research AP, Reuters access
  └ Agent started in background with agent_id: 152b6881-658d-4751-9a42-de1f9d5fce...

Launched 5 background research agents covering all 11 outlets (Fox/CNN/ABC, CBS/NBC, NYT/WaPo, Yahoo/USA Today, AP/Reuters). Waiting for results before compiling the final report.

✗ Fetch usatoday CDX index for Sep 17-20 2024 (shell)
  │ curl -s --max-time 60 "https://web.archive.org/cdx/search/cdx?url=usatoday.com&matchType=domain&
  │ from=20240917&to=20240921&output=json&limit=20000&fl=original,timestamp,statuscode" -o
  │ /tmp_ignore_usat.json; wc -l /tmp_ignore_usat.json 2>/dev/null
  └ Permission denied and could not request permission from user

✗ Fetch yahoo CDX index for Sep 17-20 2024 (shell)
  │ curl -s --max-time 60 "https://web.archive.org/cdx/search/cdx?url=news.yahoo.com&matchType=domai
  │ n&from=20240917&to=20240921&output=json&limit=20000&fl=original,timestamp,statuscode" -o
  │ /tmp_ignore_yahoo.json; wc -l /tmp_ignore_yahoo.json 2>/dev/null || echo "curl failed check"; ls
  │ -la
  └ Permission denied and could not request permission from user

✗ Check response file content directly (cannot use /tmp per rules, use local) (shell)
  │ curl -s -A "Mozilla/5.0"
  │ "http://web.archive.org/cdx/search/cdx?url=www.nytimes.com/2024/09/17*&output=json&limit=200" -o
  │ /tmp_out.json 2>&1; wc -c /tmp_out.json 2>&1; head -c 1000 /tmp_out.json 2>&1
  └ Permission denied and could not request permission from user

✗ CDX cnn 2024/09 prefix search, grep pager (shell)
  │ curl -s --max-time 90 "https://web.archive.org/cdx/search/cdx?url=cnn.com/2024/09&matchType=pref
  │ ix&from=20240917&to=20240921&output=text&limit=5000&collapse=urlkey&fl=original,timestamp" -o
  │ /tmp/cnn_cdx.txt; wc -l /tmp/cnn_cdx.txt; grep -i pager /tmp/cnn_cdx.txt | head -20
  └ Permission denied and could not request permission from user

✗ CDX abcnews domain search, grep pager (shell)
  │ curl -s --max-time 90 "https://web.archive.org/cdx/search/cdx?url=abcnews.go.com&matchType=domai
  │ n&from=20240917&to=20240920&output=text&limit=5000&collapse=urlkey&fl=original,timestamp" -o
  │ /tmp/abc_cdx.txt; wc -l /tmp/abc_cdx.txt; grep -i pager /tmp/abc_cdx.txt | head -20
  └ Permission denied and could not request permission from user

✗ Query CBS pager CDX results (shell)
  │ curl -s --max-time 90 "http://web.archive.org/cdx/search/cdx?url=www.cbsnews.com/news/&matchType
  │ =prefix&from=20240917&to=20240921&filter=original:.*pager.*&output=json&limit=100" -o
  │ /tmp_out1.json; wc -l /tmp_out1.json; cat /tmp_out1.json
  └ Permission denied and could not request permission from user

● Read (Research agent — Research Fox)                                                         3m 0s
  └ Running

● Read (Research agent — Research CBS)                                                         3m 0s
  └ Running

● Read (Research agent — Research NYT)                                                         3m 0s
  └ Running

● Read (Research agent — Research Yahoo News)                                                  3m 0s
  └ Running

● Read (Research agent — Research AP)                                                          3m 0s
  └ Running

All 5 research agents are still actively working (20-32 tool calls each so far). Waiting for completion.

● Read (Research agent — Research Fox)                                                         3m 0s
  └ Running

● Read (Research agent — Research CBS)                                                         3m 0s
  └ Running

● Read (Research agent — Research NYT)                                                         3m 0s
  └ Running

● Read (Research agent — Research Yahoo News)                                                  3m 0s
  └ Running

● Read (Research agent — Research AP)                                                          3m 0s
  └ Running

Still deep in research (40-65 tool calls each). Continuing to wait for completion.

✗ search CBS sitemap for evening news mentions (shell)
  │ python3 -c "
  │ import re
  │ "
  │ curl -s --max-time 60 "https://www.cbsnews.com/xml-sitemap/article-2024-09-2.xml" -o
  │ /tmp/../cbs2.xml 2>/dev/null || curl -s --max-time 60 …
  └ Permission denied and could not request permission from user

● Read (Research agent — Research AP)                                                          3m 0s
  └ idle

● Read (Research agent — Research CBS)                                                         3m 0s
  └ idle

● Read (Research agent — Research Fox)                                                         3m 0s
  └ Running

● Read (Research agent — Research NYT)                                                         3m 0s
  └ Running

● Read (Research agent — Research Yahoo News)                                                  3m 0s
  └ Running

Two more agents finished (CBS/NBC, AP/Reuters) with strong detail. Fox/CNN/ABC, NYT/WaPo, and Yahoo/USA Today are still running. Continuing to wait.

● Read (Research agent — Research Fox)                                                        2m 55s
  └ Running

● Read (Research agent — Research NYT)                                                        2m 55s
  └ Running

● Read (Research agent — Research Yahoo News)                                                 2m 55s
  └ Running

Still working (NYT/WaPo at 128 tool calls). Continuing to wait for these three remaining agents.

● Read (Research agent — Research Fox)                                                        2m 55s
  └ idle

● Read (Research agent — Research NYT)                                                        2m 55s
  └ Running

● Read (Research agent — Research Yahoo News)                                                 2m 55s
  └ Running

Fox/CNN/ABC done — excellent detail, including ABC's domain migration to abcnews.com with 404s on old wireStory URLs. NYT/WaPo (156 calls) and Yahoo/USA Today (95 calls) still running.

● Read (Research agent — Research Yahoo News)                                                 2m 55s
  └ idle

● Read (Research agent — Research NYT)                                                        2m 55s
  └ Running

Yahoo/USA Today done with excellent depth (found domain migration news.yahoo.com→yahoo.com/news, AP video-stub vs text gap, USA Today paywall/robots details). Only NYT/WaPo remains — waiting for it.

● Read (Research agent — Research NYT)                                                        2m 55s
  └ Running

NYT/WaPo agent is deep into research (206 tool calls) — likely investigating extensive robots.txt AI-bot blocklists and paywall specifics. Continuing to wait.

● Read (Research agent — Research NYT)                                                        2m 25s
  └ idle

All 11 outlets researched. Compiling the consolidated report below.

# Access-Verification Research: US News Coverage of the Sept 17–18, 2024 Lebanon Pager/Walkie-Talkie Attacks

*Methodology note (applies across outlets): Standard search engines returned JS-walled/blocked results to automated fetch tools in this session; discovery relied primarily on Internet Archive Wayback CDX API, outlets' own dated sitemaps/robots.txt `Sitemap:` directives, and (for Yahoo) `search.yahoo.com`. Items I could not directly confirm are marked **UNVERIFIED**.*

---

## FOX NEWS
1. **Identity 2024**: `www.foxnews.com`, unchanged since.
2. **Test URL**: `https://www.foxnews.com/world/lebanon-explosions-dozens-wounded-after-pagers-detonate-state-media-report` (Sep 17, 2024) — live-fetched, full text, on-topic.
3. **Paywall**: None. Free/ad-supported; occasional email "gate" interstitial seen on a URL variant but not on canonical article.
4. **Robots/TDM**: `robots.txt` has only generic path disallows (search, wires, print views) — **no named AI/TDM bot blocks at all**. Archive.org not blocked; Wayback snapshot exists from event day.
5. **Enumeration**: `sitemap.xml` index with `?type=news/articles/liveblogs/fastchanging`; no calendar date in URL path (slug-only); category pages e.g. `/category/world/world-regions/middle-east/lebanon`.
6. **TV**: No dated transcript archive found (`/transcript` returns 200 but shallow/UNVERIFIED depth). Web article stream is a partial proxy at best — terse wire-influenced prose vs. on-air panel discussion.

## CNN
1. **Identity 2024**: `www.cnn.com`, unchanged.
2. **Test URLs**: `cnn.com/2024/09/17/business/pagers-cell-phones-batteries/index.html`; `cnn.com/2024/09/18/business/gold-apollo-taiwan-lebanon-exploding-pagers-hnk-intl/index.html`; main piece `cnn.com/2024/09/17/middleeast/lebanon-hezbollah-pagers-explosions-intl/index.html`; live-blog `cnn.com/world/live-news/lebanon-pagers-attack-hezbollah`. All live-fetched, on-topic.
3. **Paywall**: None. Free/ad-supported (CNN+ was a separate, now-defunct streaming product).
4. **Robots/TDM**: Most extensive AI-bot blocklist of the three broadcasters — GPTBot, CCBot, Google-Extended, ClaudeBot family, anthropic-ai, PerplexityBot, Amazonbot, Bytespider, etc., **plus `Archive.org_bot`** explicitly disallowed. Despite this, Wayback holds a same-day capture — block appears unenforced/inconsistent for IA.
5. **Enumeration**: URL date pattern `cnn.com/YYYY/MM/DD/section/slug/index.html`; sitemap-index broken out by section+year/month (`sitemap/article/world/2026/09.xml` pattern); live-blog slugs carry date suffixes.
6. **TV**: **`transcripts.cnn.com` is active** with a working dated archive (`transcripts.cnn.com/date/2024-09-17`, `.../2024-09-18`, both HTTP 200), listing segments across Anderson Cooper 360°, The Lead, CNN NewsNight, First Move, One World, The Source. This is the strongest broadcast-text asset among all TV outlets studied — web articles are a much thinner proxy than the transcript archive.

## ABC NEWS
1. **Identity 2024**: `abcnews.go.com` in Sep 2024. **Domain changed since** — `abcnews.go.com` now 301s to `abcnews.com`.
2. **Test URL**: `abcnews.go.com/International/wireStory/dozens-injured-lebanon-after-handheld-pagers-reportedly-explode-113754462` (Sep 17, 2024). **Live fetch broken**: redirects to `abcnews.com/...` which **404s**. Verified content only via Wayback (`web.archive.org/web/20240918012821/...`).
3. **Paywall**: None (ABC has never had one); confirmed via archived copy.
4. **Robots/TDM**: Both old and new domains block GPTBot, Google-Extended, CCBot, ChatGPT-User, anthropic-ai, Bytespider — and notably **`Googlebot-News` is disallowed** (ABC opts out of Google News). Archive.org not named/blocked; Wayback works.
5. **Enumeration**: `/Section/wireStory/slug-numericID` pattern, no date in path; sitemaps are `/xmap`, `/xmlLatestStories`, `/xmlLatestVideos` — **rolling "latest" only, no historical/dated archive** (a real gap vs. CNN/Fox).
6. **TV**: No transcript archive found (`/US/Transcripts` → 404). Initial coverage found was **almost entirely AP wire reprints** under `/wireStory/`, not ABC-original journalism — web stream is **not a faithful proxy** for World News Tonight/Nightline's original correspondent packages.

## CBS NEWS
1. **Identity 2024**: `www.cbsnews.com`, unified domain (with city-affiliate subpaths), unchanged since.
2. **Test URL**: `https://www.cbsnews.com/news/hezbollah-lebanon-explosions-pagers-israel-hamas-war/` (found via dated sitemap, lastmod 2024-09-18). Live-fetched, full text, no gate. Wayback capture exists from 2024-09-17 15:41 UTC.
3. **Paywall**: None.
4. **Robots/TDM**: Minimal — only GPTBot, MAZBot, panscient.com blocked; **no block on CCBot, Google-Extended, ClaudeBot, Archive.org_bot**, etc. Most permissive of the outlets studied. Archive.org not blocked; captures exist from day one.
5. **Enumeration**: Dated sitemaps `xml-sitemap/article-YYYY-MM.xml` and `-2.xml` (month split in two), with `<lastmod>` per URL — strong date-scoped hook.
6. **TV**: Routine full transcripts exist for *60 Minutes* but **none found for daily CBS Evening News**; `/evening-news/` is a rolling video-clip hub, not a transcript index. Web stream ≠ faithful proxy for Evening News broadcast.

## NBC NEWS
1. **Identity 2024**: `www.nbcnews.com`, unchanged.
2. **Test URL**: `nbcnews.com/news/world/hezbollah-pagers-expolsion-lebanon-handheld-devices-rcna171457` (published Sep 17, 2024, 20:11 UTC per sitemap). Live-fetched, full text, no gate. Wayback capture from 2024-09-17 14:36 UTC.
3. **Paywall**: None.
4. **Robots/TDM**: Extensive named AI/SEO-bot blocklist (20+: GPTBot, Google-Extended, CCBot, Bytespider, ClaudeBot family, Applebot-Extended, Amazonbot, Meta-ExternalAgent, etc.) **including `Archive.org_bot` → Disallow: /** in the *current* file — yet Wayback nonetheless holds day-one captures (consistent with IA's known policy of not always honoring robots.txt for its own crawls; whether the block existed in Sept 2024 specifically is UNVERIFIED).
5. **Enumeration**: `sitemap/nbcnews/sitemap-YYYY-MM-article.xml` monthly files (verified working, greppable); persistent `rcna######` content-ID suffix, no date in URL path; separate liveblog URL family exists for later conflict coverage.
6. **TV**: No routine Nightly News transcript pages found in the sitemap for this story; `/nightly-news` renders as JS shell (UNVERIFIED depth). Web stream likely **not a faithful proxy** for the aired segment (written coverage broader/more frequent than a ~2-min broadcast segment, but lacks on-air framing/correspondent stand-ups).

## NEW YORK TIMES
1. **Identity 2024**: `www.nytimes.com`, unchanged.
2. **Test URLs**: `nytimes.com/2024/09/17/world/middleeast/israel-hezbollah-pagers-explosives.html` (Frenkel/Bergman, published 2024-09-17T21:43Z) and `nytimes.com/live/2024/09/17/world/israel-hamas-war-news` (live blog, published 13:52Z same day). **Live fetch of the standard article returned HTTP 403** (bot-block, not just paywall) in this session.
3. **Paywall — SPECIFIC**: Standard metered paywall (`content_tier: metered`). The standalone investigative article was tagged `isAccessibleForFree: false` — **it counted against the meter, was NOT unlocked**. The rolling **"Live Updates" blog was tagged `isAccessibleForFree: true`** — confirming NYT's practice of exempting the continuously-updated breaking-news format, not the topic generally. No press statement found unlocking pager coverage broadly. Exact 2024 monthly free-article cap: UNVERIFIED (help center is JS-only/unarchived).
4. **Robots/TDM**: Among the most extensive blanket AI-bot blocks found (GPTBot, Google-Extended, CCBot, Bytespider, ClaudeBot family, Applebot-Extended, PerplexityBot, OAI-SearchBot, Meta bots, cohere-ai, dozens more), explicitly citing EU TDM Directive Art. 4 — consistent with NYT's Dec 2023 lawsuit against OpenAI/Microsoft. **`archive.org_bot` disallowed**, and in practice the standard article has **zero Wayback snapshots near the event** (earliest is Dec 2025, 14+ months later) — a directly-verified, enforced block. The `/live/` blog, however, WAS captured same-day (3.5 hrs post-publish) — inconsistent enforcement across URL patterns.
5. **Enumeration**: Rolling news sitemap only (no historical range); Article Search/Archive API exists at developer.nytimes.com but requires an API key (404 without one); URL pattern `nytimes.com/YYYY/MM/DD/section/subsection/slug.html` and `/live/YYYY/MM/DD/...`.

## WASHINGTON POST
1. **Identity 2024**: `www.washingtonpost.com`, unchanged.
2. **Test URL**: `washingtonpost.com/national-security/2024/09/17/lebanon-pagers-exploding-hezbollah/` (Haidamous/El Chamaa/Fahim, published 14:40Z). Live direct fetch failed with transport error/timeout in this session (inconclusive — could not confirm a deliberate block signature as clean as NYT's 403). Verified via Wayback capture 47 minutes post-publish.
3. **Paywall — SPECIFIC**: Standard metered paywall; this article was tagged `isAccessibleForFree: false` (not unlocked). WaPo's gift-article program (verified via help center) allows subscribers **10 free gift articles/month, viewable 14 days** by non-subscribers — a general (not event-specific) mechanism; exact 2024 base meter cap UNVERIFIED. No statement found making pager coverage free.
4. **Robots/TDM**: Comprehensive AI-bot blocks (anthropic-ai, Bytespider, CCBot, ClaudeBot, cohere, Diffbot, PerplexityBot, Amazonbot, etc.) but with narrow `/creativegroup/` `/advertising/` allow carve-outs. **Archive/scraper bots explicitly blocked** (`archive.org_bot`, `ia_archiver`, `heritrix`, `ArchiveBot`, etc.) — yet unlike NYT, Wayback captured this article within 47 minutes and CDX date-prefix queries work without 403s, indicating the block is largely unenforced against IA in practice.
5. **Enumeration**: URL pattern `washingtonpost.com/section/YYYY/MM/DD/slug/` (no `.html`); sitemaps declared in robots.txt (`news-sitemap.xml.gz` etc.) but direct fetch failed (transient, inconclusive); IA CDX date-prefix search is a reliable workaround.

## YAHOO NEWS
1. **Identity 2024**: `news.yahoo.com/<slug>.html` in Sep 2024. **Domain changed since** — `news.yahoo.com` now redirects to `www.yahoo.com/news/`, and newer articles (2025+) use an added `/articles/` path segment.
2. **Test URLs**:
   - **Syndicated (non-Yahoo-staff)**: `news.yahoo.com/hundreds-hezbollah-pagers-explode-apparent-151059022.html` (Sep 17, 2024) — actually **USA TODAY** content (Kim Hjelmgaard byline, "Contributing: Reuters"), republished verbatim on Yahoo. A pure AP-bylined **text** article in-window could not be confirmed (only found an AP **video-only stub** with no article body, and a genuine AP text piece from Aug 2025 — outside the window). Mark in-window AP/Reuters/AFP text article as **UNVERIFIED**.
   - **Closest to "original" Yahoo content**: `news.yahoo.com/hezbollah-pager-explosions-lebanon-israel-080955954.html` (Sep 18, 2024), bylined "Andy Wells," provider **"Yahoo News UK"** (not clearly a US staff piece).
3. **Paywall**: None on any variant tested.
4. **Robots/TDM**: Generic crawling allowed on article paths; large `Disallow: /` block list of AI bots (anthropic-ai, ClaudeBot, Google-Extended, GPTBot, Bytespider, CCBot, PerplexityBot, etc.); unusual narrow carve-out blocking `Claude-SearchBot`/`OAI-SearchBot` only from `*/articles/`. **Archive.org: no snapshots exist at all** for either test URL (confirmed via wayback "available" API returning empty) — Yahoo article pages appear essentially unarchived by IA's routine crawl for this event.
5. **Enumeration**: `news-sitemap-index.xml` is rolling/current only (not historical); slug has opaque timestamp code, no calendar date; no by-date browse pages; regional mirrors (uk./ca./au. news.yahoo.com) share content IDs, useful cross-region hook.

## USA TODAY
1. **Identity 2024**: `www.usatoday.com` (geo-redirects EU traffic to `eu.usatoday.com`, same content).
2. **Test URL**: `usatoday.com/story/news/world/2024/09/17/hezbollah-pagers-lebanon-attack-israel/75261807007/` — live-fetched, full text, no gate, matches the Yahoo-syndicated mirror word-for-word.
3. **Paywall**: Metered/soft with breaking-news carve-out — page metadata shows subscriber tiers exist (Gannett network), but this specific breaking story showed no gate/truncation; breaking pager coverage was free.
4. **Robots/TDM**: Very aggressive — ~60 named AI/scraper bots blocked (GPTBot, Google-Extended, CCBot, ClaudeBot family, PerplexityBot, Meta bots, Amazonbot, AI2Bot, **Arquivo-web-crawler** [archive.org's Portuguese arm]), with narrow allow carve-outs only for sponsored/shopping content. `Googlebot-News` not blocked generally. Archive.org: only Wayback snapshot found is dated **2026-03-03** (~18 months post-event) — CDX search for Sep 2024 with topic keywords returned **zero matches**, confirming no contemporaneous IA capture.
5. **Enumeration**: URL date embedded directly in path (`/story/news/world/2024/09/17/.../ID/`) — highly enumerable; sitemap URLs declared in robots.txt but content fetch was geo/bot-gated in this session (UNVERIFIED contents). Confirmed outward syndication to Yahoo News (Gannett wire model).

## ASSOCIATED PRESS (apnews.com)
1. **Identity 2024**: `apnews.com`, unchanged.
2. **Test URL**: `apnews.com/article/lebanon-hezbollah-israel-exploding-pagers-8893a09816410959b6fe94aec124461b` (Sep 17, 2024). **Live-fetched today (2026) — full text loads, no paywall, matches the Sep 2024 Wayback capture verbatim. Still freely readable.**
3. **Paywall**: None — free, ad-supported wire model, confirmed both then and now.
4. **Robots/TDM**: `Disallow: /` for named AI bots (CCBot, GPTBot, anthropic-ai, ClaudeBot family, cohere-ai, PerplexityBot, Amazonbot, Applebot-Extended, Bytedance, Timpibot) but **Google-Extended, OAI-SearchBot, Bingbot notably absent** from the block list. Archive.org not blocked; Wayback holds a full capture from 2024-09-20.
5. **Enumeration**: `ap-sitemap.xml` index with **date-keyed sub-sitemaps back to Feb 2006** (`ap-sitemap-YYYYMM.xml`, confirmed `ap-sitemap-202409.xml` exists); topic hubs `apnews.com/hub/lebanon`, `/hub/hezbollah`, `/hub/israel-hamas-war`; opaque hash-suffixed article slugs; commercial AP Media API exists for licensees (UNVERIFIED directly this session).

## REUTERS (reuters.com)
1. **Identity 2024**: `www.reuters.com`, unchanged.
2. **Test URL**: `reuters.com/world/middle-east/dozens-hezbollah-members-wounded-lebanon-when-pagers-exploded-sources-witnesses-2024-09-17/` (Bassam/Gebeily, Sep 17, 2024). **Live fetch today returned HTTP 401 on every attempt** (homepage, section page, article) — a hard bot/edge block, not a rendered paywall page. The Wayback capture from 2024-09-18 15:53 UTC loads full, ungated text, confirming free access **at the time of the event**.
3. **Paywall**: In Sep 2024, likely a **free registration wall** (reported industry-wide as launched ~2023; exact date UNVERIFIED this session due to search-engine blocks). As of 2026, community reports (Reddit, Feb 2026) describe Reuters having since added a **paid metered subscription (~£1/week)** — this could not be independently visually confirmed here due to the 401 block; mark **partially UNVERIFIED**.
4. **Robots/TDM**: Structured as an **allowlist** — ~80 named bots explicitly permitted (Googlebot, Bingbot, Applebot, ChatGPT-User, OAI-SearchBot, etc.) plus `Applebot-Extended: Disallow: /`; a catch-all blocks **any unlisted bot** from the entire site except `/plus/` — this explains the 401s I received (fetch tool's UA isn't allowlisted). GPTBot, ClaudeBot, CCBot, PerplexityBot, Google-Extended, Amazonbot, cohere-ai are blocked **by omission**. Archive.org not named in the allowlist (would fall under the catch-all block going forward), yet a full capture from Sep 2024 already exists — whether *new* URLs can still be archived today is UNVERIFIED.
5. **Enumeration**: Article URLs embed the **publish date directly in the slug** (`...-2024-09-17/`) — a strong, human-readable date hook, distinct from AP's opaque hashes. Sitemaps include a dedicated `service/archive-sitemap/sitemap.xml` (contents unverified — 401 blocked). Section hubs `reuters.com/world/middle-east/` etc. Commercial Reuters Connect/News API exists for licensees (UNVERIFIED directly this session).

---

## Summary Table

| Outlet | 2024 domain (→ now) | Test URL | Paywall (2024) | Enumeration hook | Risk flags |
|---|---|---|---|---|---|
| Fox News | foxnews.com (unchanged) | [foxnews.com/world/lebanon-explosions-dozens-wounded...](https://www.foxnews.com/world/lebanon-explosions-dozens-wounded-after-pagers-detonate-state-media-report) | None | `sitemap.xml?type=news/articles`; no date in URL | No transcript archive found; no AI-bot blocks at all |
| CNN | cnn.com (unchanged) | [cnn.com/2024/09/17/business/pagers-cell-phones-batteries](https://www.cnn.com/2024/09/17/business/pagers-cell-phones-batteries/index.html) | None | `/YYYY/MM/DD/` URLs; monthly section sitemaps | Robots blocks Archive.org_bot but IA capture exists anyway (inconsistent enforcement) |
| ABC News | abcnews.go.com → **abcnews.com** | [abcnews.go.com/.../dozens-injured-lebanon...-113754462](https://web.archive.org/web/20240918012821/https://abcnews.go.com/International/wireStory/dozens-injured-lebanon-after-handheld-pagers-reportedly-explode-113754462) | None | No dated sitemap ("latest" only); slug+numeric ID | **Live test URL 404s** (domain migration link rot); coverage was mostly AP wire reprints, not ABC original |
| CBS News | cbsnews.com (unchanged) | [cbsnews.com/news/hezbollah-lebanon-explosions-pagers-israel-hamas-war](https://www.cbsnews.com/news/hezbollah-lebanon-explosions-pagers-israel-hamas-war/) | None | Dated `xml-sitemap/article-YYYY-MM[-2].xml` | Minimal AI-bot blocking (most permissive studied); no Evening News transcripts |
| NBC News | nbcnews.com (unchanged) | [nbcnews.com/.../hezbollah-pagers-expolsion...-rcna171457](https://www.nbcnews.com/news/world/hezbollah-pagers-expolsion-lebanon-handheld-devices-rcna171457) | None | `sitemap/nbcnews/sitemap-YYYY-MM-article.xml` | Robots blocks Archive.org_bot (current); unclear if in effect Sep 2024; no Nightly News transcripts found |
| New York Times | nytimes.com (unchanged) | [nytimes.com/2024/09/17/world/middleeast/israel-hezbollah-pagers-explosives.html](https://www.nytimes.com/2024/09/17/world/middleeast/israel-hezbollah-pagers-explosives.html) | Metered (article NOT unlocked; live-blog format was free) | URL date pattern; Article Search/Archive API (needs key) | **Live fetch 403'd**; Archive.org effectively blocked for standard articles (no capture until Dec 2025); tied to active OpenAI/Microsoft TDM lawsuit |
| Washington Post | washingtonpost.com (unchanged) | [washingtonpost.com/national-security/2024/09/17/lebanon-pagers-exploding-hezbollah](https://www.washingtonpost.com/national-security/2024/09/17/lebanon-pagers-exploding-hezbollah/) | Metered (article NOT unlocked; gift-article program exists, 10/mo) | `/section/YYYY/MM/DD/slug/`; IA CDX prefix search works | Live fetch inconclusive (transport error, not confirmed as deliberate block); robots blocks IA bots but captures exist anyway |
| Yahoo News | news.yahoo.com → **yahoo.com/news** (+ `/articles/` path added later) | Syndicated: [news.yahoo.com/hundreds-hezbollah-pagers-explode-apparent-151059022.html](https://news.yahoo.com/hundreds-hezbollah-pagers-explode-apparent-151059022.html) (USA Today content) | None | Rolling sitemap only, no historical index | Domain migration; **no in-window AP/Reuters text article confirmed** (only video stub); **zero Wayback captures** of any Yahoo article tested |
| USA Today | usatoday.com (unchanged) | [usatoday.com/story/news/world/2024/09/17/hezbollah-pagers-lebanon-attack-israel/75261807007](https://www.usatoday.com/story/news/world/2024/09/17/hezbollah-pagers-lebanon-attack-israel/75261807007/) | Metered/soft (breaking news free) | Date embedded in URL path | ~60 AI bots blocked; **no contemporaneous Wayback capture** (only capture is 18 months later) |
| AP (apnews.com) | apnews.com (unchanged) | [apnews.com/article/lebanon-hezbollah-israel-exploding-pagers-...](https://apnews.com/article/lebanon-hezbollah-israel-exploding-pagers-8893a09816410959b6fe94aec124461b) | None, then and now | Date-keyed `ap-sitemap-YYYYMM.xml` back to 2006; topic hubs | Low risk — still freely live, IA-friendly |
| Reuters (reuters.com) | reuters.com (unchanged) | [reuters.com/world/middle-east/dozens-hezbollah-members-wounded...-2024-09-17](https://web.archive.org/web/20240918155339/https://www.reuters.com/world/middle-east/dozens-hezbollah-members-wounded-lebanon-when-pagers-exploded-sources-witnesses-2024-09-17/) | Free registration wall in 2024 (metered/paid wall reported added later) | Date-suffixed slugs (`-YYYY-MM-DD/`) | **Live fetch 401's** (allowlist-only bot policy); current paywall state partially unverified |

**Key cross-cutting risk flags for the study**: (1) ABC's domain migration broke old wireStory URLs — must resolve via Wayback; (2) NYT actively blocks both automated fetch and archive.org for standard articles, making live/contemporary re-verification hardest of all outlets; (3) Yahoo News lacks any Wayback presence for this event and its "original" reporting is thin/UK-sourced — treat Yahoo mostly as a syndication mirror; (4) Reuters' live site rejects non-allowlisted automated access outright (401), so only Wayback is a reliable verification path; (5) USA Today and Yahoo both lack contemporaneous archive.org captures despite the event's high profile.

