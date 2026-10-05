# US recall audit, Sep 17–24 2024 (day 0–7)

Audit run 2026-10-04/05. Scripts: `pipeline/08-recall-audit/recall_audit_*.py`. Nothing in the corpus, the
manifests or the pipeline notes was changed.


> **Update 2026-10-05 (corpus v1.3).** AP was re-collected from Wayback and 18 AP records added. The
> report was re-run: AP recall is now 15/35 (0.43; central 0.50), and US recall without Yahoo is
> 93/369 (0.25), with Yahoo 114/799 (0.14). `reference-set.csv`, `gap-manifest.csv` and `raw/recall-table.csv`
> reflect this; figures in the text below are from the first run (AP 0/35).

## Bottom line

- The reference set has **799 verified items** that substantively mention the pager or walkie-talkie
  attacks. **430 of them are Yahoo News pages**, and 427 of those are syndicated partner copies
  (Reuters, AP, dpa, AFP, CNN, The Telegraph, The Hill and others). They are not Yahoo's own
  reporting, so the overall figure is given twice:
  - **all outlets: 99 of 799 in the corpus, recall 0.12** (central 0.16, mentions only 0.04);
  - **without Yahoo: 78 of 369, recall 0.21** (central 71/285 = 0.25, mentions only 7/84 = 0.08).
- As in Germany, the corpus is a sample of attack-themed articles, not a record of what each
  outlet published. "Not in our sample" must not be read as "the outlet did not say it". Mentions-only
  coverage, video pages, newsletters and live blogs are almost entirely missing. The US corpus has
  **no live-blog records at all**.
- Four outlets are close to absent, each for a specific reason:
  - **AP, 0 of 35.** All 23 AP candidates were fetched as Cloudflare "Just a moment..." challenge
    pages, so their bodies were empty and relevance became "none". The AP baseline has no documents.
    The same pages can be read from Wayback.
  - **NYT, 4 of 68.** The manifest is 17 hand-curated URLs. NYT's own daily sitemap lists 64 of the
    68 reference items.
  - **ABC, 3 of 50; USA Today, 1 of 20.** Their manifests are an incomplete CDX sweep (ABC) and 7
    curated URLs (USA Today).
- **Reuters was not audited.** No independent route covers reuters.com (section 2). **WaPo's figure
  is not meaningful**: only 4 of its 42 reference items were found by an independent route.
- The gap manifest lists **721 items** (312 outside Yahoo). Nearly all were fetched in this audit,
  live or from Wayback. 21 rows are live blogs whose captures don't show the entries.

## 1. Method

Same scripts and rules as the Germany audit (`data/germany/08-recall-audit/recall-audit-notes.md`,
sections 1.1–1.3); only the US differences are listed here.

### 1.1 Reference routes

The **pool** (1,762 URLs after the topic filter) is the union of these routes. Every pool item was
then checked against its body text.

| route | what it sees | independence from the original route |
|---|---|---|
| **Media Cloud** full-text search, `pager OR pagers OR beeper(s) OR walkie-talkie(s) OR "Gold Apollo"`, Sep 17–25 | Body-text matches. Stories in the window per source: cnn.com 1,952, cbsnews.com 5,140, abcnews.go.com 1,788, usatoday.com 1,736, nytimes.com 1,386, foxnews.com 1,256, nbcnews.com 436, apnews.com 323, reuters.com 106, yahoo.com 51,137, washingtonpost.com **0** | Fully independent. But the WaPo source is empty, Reuters is nearly empty, and NYT is thin. |
| **GDELT 2.0 raw GKG** (all 15-min files, Sep 17 00:00 – Sep 25 06:00 UTC) | Pages with a Lebanon location or Hezbollah organisation extracted from the body, or a topic term in the title | Independent, except for Fox, NYT, Yahoo and USA Today, whose original route was the GDELT DOC API. **GDELT has no washingtonpost.com or abcnews.go.com rows, and for Reuters only jp.reuters.com.** |
| **Outlet-native listings** (live) | NYT daily sitemap `nytimes.com/sitemap/2024/09/DD/`; CNN monthly article, live-story and video sitemaps; Fox article sitemap | Independent of the original routes |
| **Archived homepages and section pages** (Wayback, 3–7 captures Sep 17–20; 7,498 links) | Front and world/Middle East pages of 10 outlets. No usable Reuters captures. | Link-based, but still depends on Wayback |
| **Live-blog path CDX** (`cnn.com/world/live-news/`, `apnews.com/live/`, `abcnews.go.com/International/live-updates/`, `nbcnews.com/news/world/live-blog/`, …) with all capture timestamps | Live blogs | Same mechanism as CDX, on paths the original regexes excluded. The CNN prefixes failed under IA throttling and were re-run by `recall_audit_cnn_live.py`. |
| **CDX section re-run** (`recall_audit_cdx_sections.py`): WaPo per-day prefixes, Reuters section prefixes | Checks whether the original WaPo/Reuters CDX failures hid content | **Not independent**: same mechanism as the original WaPo/Reuters route |
| Codex web search for live blogs | Nothing usable: the Codex session failed on authentication (`raw/codex/liveblogs-us.txt`) | – |

**Topic filter:** the same as in Germany, plus the English terms (lebanon, hezbollah, beirut, mideast,
beeper, exploding, …).

### 1.2 Verification

Verification uses the same rules as in Germany:

- substantive mention in the body, not only in link text;
- central if the attack is in the headline, the description or about the first 700 characters;
- date between Sep 17 and Sep 24;
- live blogs checked only against in-window captures.

The US term list is `pager(s)`, `beeper(s)`, `walkie`, `Gold Apollo`, `Icom`. Weak device phrases
("exploding devices", "handheld radios", "communication devices") count only within 400 characters
of Lebanon/Hezbollah.

Changes made during this audit, all in recall-audit scripts only:

1. **Site-chrome filter** (`recall_audit_build.boilerplate`, `recall_audit_common.assess(skip=…)`).
   A paragraph counts as page furniture if it recurs on three or more differently titled pages of one
   outlet, or on two or more if it is a short headline-like line. Such paragraphs no longer count as a
   mention. This removed **24 false positives**:
   - 11 ABC `live-updates` captures. These are empty shells (60–80 words); their only attack text is
     a teaser card ("Israel had hand in manufacturing pagers that exploded in Lebanon: Source").
   - 13 NYT pages: 7 video pages whose playlist carries "Heightened Anxiety in Lebanon After Wireless
     Device Explosions", and 6 articles from Sep 17–20 whose only mention was a "Device Attacks in
     Lebanon" related-coverage box.

   Media Cloud had also matched 5 of these NYT pages. Its full-text hits include site chrome too.
2. **Second Wayback attempt via 200-status captures** (`recall_audit_cdx_refetch.py`). The default
   lookup replays the capture nearest Sep 20 whatever its status. For Reuters that was usually a 401
   page, for WaPo a 403 or an Akamai "Access Denied" page. The script asks the Wayback timemap for
   200 captures in Sep 17 – Oct 1 and fetches the nearest one. Results:
   - WaPo: 13 of 17 failed items recovered.
   - Reuters: 3 of 14; the other 11 have no 200 capture at all.
   - CBS: 4 video pages; NYT: 1 article.
   - Yahoo: 127 GDELT-only items that now return 404 live were also run; all have 200 captures.
3. **Wayback homepage links re-extracted offline** (`recall_audit_wayback_pages.py us --offline`).
   - Fox pages use protocol-relative links (`//www.foxnews.com/...`). These had been
     turned into `https://www.foxnews.com//www.foxnews.com/...`: 1,767 mangled Fox links, so those
     items could not match anything.
   - ABC story URLs had lost their only stable ID (`?id=NNN`).
   - The fix merged mangled duplicates. The old Fox figure of 20 in-corpus items counted one corpus
     record twice.
4. **Scope and landing pages.** The pool was rebuilt after the scope rules in `recall_audit_common`
   (21:03, Oct 4) had changed. This removed 39 CBS-owned local-station pages (`/chicago/`,
   `/newyork/`, …). It also merged 46 `us.cnn.com` duplicates into their `cnn.com` keys. One-segment
   landing pages (`washingtonpost.com/israel-hamas-war/`) and NYT `news-event/` hubs are now excluded.

### 1.3 Matching

Matching uses the same URL normalisation and stable-ID keys as Germany. The US ID keys are ABC
`-NNNNNNNNN`, NBC `rcnaNNN`, Yahoo `-NNNNNNNNN.html`, USA Today numeric ID and AP 32-hex ID. Other
outlets are keyed on the normalised path. Fuzzy headline matching uses a ratio of at least 0.90.

## 2. Recall per outlet

| outlet | corpus (all dates) | ref items | in corpus | recall | central: in/ref | recall | mention: in/ref | recall | Media Cloud hits in ref | indep. found | gap manifest (central) |
|---|---|---|---|---|---|---|---|---|---|---|---|
| ABC | 4 | 50 | 3 | 0.06 | 3/45 | 0.07 | 0/5 | 0.00 | 46 | 50 | 67 (42)¹ |
| AP | 0 | 35 | 0 | 0.00 | 0/30 | 0.00 | 0/5 | 0.00 | 26 | 35 | 35 (30) |
| CBS | 10 | 36 | 7 | 0.19 | 7/30 | 0.23 | 0/6 | 0.00 | 33 | 36 | 29 (23) |
| CNN | 30 | 49 | 20 | 0.41 | 20/33 | 0.61 | 0/16 | 0.00 | 45 | 49 | 29 (13) |
| Fox | 21 | 36 | 19 | 0.53 | 15/26 | 0.58 | 4/10 | 0.40 | 21 | 32 | 17 (11) |
| NBC | 15 | 31 | 14 | 0.45 | 12/24 | 0.50 | 2/7 | 0.29 | 20 | 31 | 17 (12) |
| NYT | 4 | 68 | 4 | 0.06 | 3/55 | 0.05 | 1/13 | 0.08 | 5 | 68 | 64 (52) |
| Reuters | 4 | 2 | 0 | – | 0/2 | – | – | – | 0 | **0** | 2 (2) |
| USA Today | 1 | 20 | 1 | 0.05 | 1/13 | 0.08 | 0/7 | 0.00 | 20 | 20 | 19 (12) |
| WaPo | 12 | 42 | 10 | (0.24) | 10/27 | (0.37) | 0/15 | (0.00) | 0 | **4** | 33 (17)¹ |
| Yahoo | 30 | 430 | 21 | 0.05 | 19/293 | 0.06 | 2/137 | 0.01 | 73 | 75 | 409 (274) |
| **all** | 131 | **799** | **99** | **0.12** | 90/578 | **0.16** | 9/221 | **0.04** | 289 | 400 | 721 |
| **all without Yahoo** | 101 | **369** | **78** | **0.21** | 71/285 | **0.25** | 7/84 | **0.08** | 216 | 325 | 312 |

"indep. found" is the number of reference items reached by at least one route independent of the
outlet's original enumeration route. Restricted to those items, recall without Yahoo is 69/325 = 0.21.

¹ The gap manifest also has 20 ABC and 1 WaPo `live_blog_unverified` rows: live-blog URLs with
in-window captures whose HTML does not contain the entries. For ABC these are generic
`live-updates/...` shells, many with slugs from earlier in 2024. It is unclear whether any of them
carried the attacks; see section 6.

### Yahoo: what the figure means

`raw/yahoo-providers.csv` (`recall_audit_us_yahoo.py`) reads the provider (`providerId`, provider logo,
byline) from each fetched page:

| Yahoo provider class | ref items | in corpus | central in/ref |
|---|---|---|---|
| Yahoo-original (providerId "Yahoo! News") | 3 | 0 | 0/3 |
| wire: Reuters 48, dpa 44, AP 34, AFP 26, UPI 13, Bloomberg 8 | 173 | 7 | 7/117 |
| copies of audited US outlets: CNN 17, ABC 11, NBC 11, Fox 9, USA Today 7, CBS 3 | 58 | 5 | 5/42 |
| other partners: The Telegraph 38, BBC 21, The Hill 16, LA Times 11, NewsNation 11, … | 195 | 9 | 7/130 |
| provider not readable | 1 | 0 | 0/1 |

The 30 Yahoo corpus records (primary) are almost all syndicated: Reuters 8, AP 3, NBC 3, USA Today 3,
The Telegraph 3, The Independent 3, dpa 1, others 5. One is Yahoo-original. This matches the
collection rule in `access-notes.md`, where Yahoo is a syndication-discovery source, not an archive
to enumerate.

For a "what a Yahoo reader saw" view, recall should be read in two tiers:

1. **Yahoo's own reporting.** It is tiny: 3 items in the reference set, none in the corpus (the one
   Yahoo-original corpus record falls outside the reference).
2. **The syndicated feed.** 427 reference items, of which 21 (0.05) are in the corpus. These items are
   the same text as the provider's own copy. For claims, they should be deduplicated against the
   provider's record and counted as "carried by Yahoo" (exposure), not as separate Yahoo reporting.

Read this way, the Yahoo feed is far broader than the corpus suggests: 44 dpa and 26 AFP items that no
other US outlet in the corpus carries. That breadth is a property of the aggregator, so the "all"
recall above is dominated by Yahoo and should not be quoted as US recall.

A caveat on completeness: 421 of the 430 Yahoo rows come from GDELT, and GDELT was also Yahoo's
original discovery route, so only 75 rows (the Media Cloud hits) are independent.

### Reuters: not audited

There is no independent route to reuters.com for these days:

- Media Cloud's reuters.com source holds 106 stories for Sep 17–25 and no pager hit.
- GDELT has only `jp.reuters.com` rows.
- Wayback has no usable homepage or Middle East section captures.
- Reuters' robots allowlist and HTTP 401 also hit the archive crawler: most September 2024 article
  captures are stored 401 pages. The non-independent CDX re-run found 16 URLs. Only 5 have any 200
  capture, and 2 of those carry the attacks; both are in the table.

As a proxy, Yahoo carried **48 distinct Reuters headlines** on the attacks (34 central). The corpus
has 4 Reuters records plus 8 Yahoo-hosted Reuters copies. Only 4 of the 48 Yahoo-hosted headlines
match one of them. Reuters' recall is therefore well below 0.2, but it cannot be measured with the
routes used here.

### WaPo: figure not meaningful

The routes that should have been independent were all unavailable:

- the Media Cloud washingtonpost.com source is empty for the window;
- GDELT has no washingtonpost.com rows;
- the archived homepages found only 4 items.

The other 38 reference items come from the CDX section re-run, which is the same mechanism as WaPo's
original route. The 0.24 can only show what that route missed; it is not a recall estimate.
13 of the 32 missing WaPo items are AP wire copies (`…/<uuid>_story.html`, AP byline). Without them
WaPo stands at 10/29.

### How large and independent each reference is (other outlets)

- **CNN, Fox, NBC, CBS**: strong. Each has Media Cloud, GDELT and homepage captures. CNN and Fox also
  have their own sitemaps. Reverse check: the routes found 20/20, 19/19, 14/14 and 7/8 of our own
  in-window on-topic records (`raw/route-coverage.csv`).
- **NYT**: strong for articles. The daily sitemap is complete, but Media Cloud is thin (5 hits),
  so mentions-only items rest on the sitemap's topic filter. Our 4 records were all found.
- **AP**: medium. Media Cloud (26 hits), GDELT and homepage captures. AP's sitemap is complete, but
  it is the original route, so it was not reused.
- **ABC, USA Today**: medium. Mostly Media Cloud (ABC 46 of 50, USA Today 20 of 20). ABC's
  reverse check found 3 of 4 own records.

## 3. Why items are missing

Status breakdown of the 799 reference items:

| outlet | in_corpus | live_blog | in_candidates_dropped | in_manifest_not_candidate | not_in_manifest | inaccessible |
|---|---|---|---|---|---|---|
| ABC | 3 | 0 | 0 | 2 | 45 | 0 |
| AP | 0 | 2 | 15 | 18 | 0 | 0 |
| CBS | 7 | 0 | 1 | 5 | 23 | 0 |
| CNN | 20 | 8 | 0 | 19 | 2 | 0 |
| Fox | 19 | 1 | 3 | 0 | 13 | 0 |
| NBC | 14 | 1 | 0 | 6 | 10 | 0 |
| NYT | 4 | 6 | 5 | 0 | 53 | 0 |
| Reuters | 0 | 0 | 1 | 0 | 1 | 0 |
| USA Today | 1 | 0 | 0 | 0 | 19 | 0 |
| WaPo | 10 | 4 | 7 | 0 | 21 | 0 |
| Yahoo | 21 | 0 | 4 | 0 | 405 | 0 |
| **total** | **99** | **22** | **36** | **50** | **592** | **0** |
| total without Yahoo | 78 | 22 | 32 | 50 | 187 | 0 |

1. **`not_in_manifest`, 187 outside Yahoo (discovery gap).** 152 are central. For 101 of those 152
   the original slug tagger would have caught the slug (76 "strong", 25 "related"), so this is
   enumeration loss.
   - **NYT, 53.** The manifest is 17 curated URLs: the NYT CDX API returned 403 to every query in
     September 2026. The daily sitemap `nytimes.com/sitemap/2024/09/DD/` works live and lists 64 of the
     68 reference items. The missing ones:
     - 27 news articles (`/world/middleeast/` and others), e.g. "hezbollah-pager-explosions-lebanon",
       "what-is-pager-hezbollah", "israel-hezbollah-pager-attacks-history",
       "pager-explosions-lebanon-what-we-know";
     - 11 briefing newsletters (`/briefing/`), 6 video pages, 4 opinion pieces, 3 podcast pages
       (The Daily "pagers-explosion-lebanon"), and 2 interactive/card pages.

     Slug test: 31 of the 44 central NYT items had tagger-visible slugs.
   - **ABC, 45.** 34 are AP `wireStory` reprints, 9 are ABC's own story pages and 2 are videos.
     - The ABC manifest is a partial CDX sweep (`complete: NO`). It holds 56–86 wireStory URLs a day,
       far fewer than ABC publishes.
     - 8 wire stories appear twice, under `/US/wireStory/` and `/International/wireStory/` with
       adjacent IDs. Collapsing them leaves 42 items, of which 3 are in the corpus.
     - All 12 ABC own-byline items are missing, e.g. "pagers-exploded-lebanon-syria",
       "reporters-notebook-walkie-talkie-exploded-funeral-lebanon-chaos" and
       "israel-hand-manufacturing-pagers-exploded-lebanon-source".
   - **CBS, 23: all are `/video/` pages.** The CBS manifest uses the article sitemap only, so CBS
     videos (including the daily Evening News / CBS News 24/7 episode pages) are never enumerated. The
     article side is well covered; the 5 enumerated items that were not candidates are covered in
     point 2.
   - **NBC, 10: all are video pages** (`/video/`, `/nightly-news/video/`, `/now/video/`). This is
     the same article-sitemap limit.
   - **USA Today, 19.** The manifest is 7 curated URLs. The enumeration notes say "no archive
     presence; live-only", but all 19 were fetched from Wayback captures of Sep 19–25. Among them are
     5 newsletter or podcast transcripts (The Excerpt, Daily Briefing), an opinion piece, a map and a
     fact-check ("exploding hezbollah devices: pagers, radios, not iPhones").
   - **WaPo, 21.** 13 are AP wire copies, 5 are staff articles and 3 are opinion pieces. The original
     `/world` prefix query failed, and the curated layer did not cover them.
   - **Fox, 13.** 5 Fox News Radio pages (`radio.foxnews.com`), 4 video pages and 4 articles, 3 of
     them mentions-only. The Fox manifest is GDELT-plus-curated by design.
2. **`in_manifest_not_candidate`, 50 (topic gap).** These were enumerated, but their slugs carry no
   pager word (25 central, 25 mentions-only). They come from CNN (19), AP (18), NBC (6) and CBS (5).
   - CNN includes 6 "5 things" newsletters and analyses such as
     "lebanon-hezbollah-hassan-nasrallah-speech-analysis" and "israel-notified-us-lebanon-operation".
   - AP includes "hungarian-company-lebanon", "lebanon-israel-hezbollah-geneva-conventions" and the
     daily "israel-hamas-war-latest-…" pages.
3. **`in_candidates_dropped`, 36 (extraction failures).** Almost none is a real relevance decision:
   - **AP, 15: Cloudflare challenge pages.** All 23 AP candidates were stored as "Just a moment..."
     pages with empty bodies and then rated relevance "none". This is still the case: a curl fetch of
     an AP article today returns 403 with the challenge page. The Wayback copies hold the full text.
     The enumeration notes (Sep 2026) say AP "serves curl with a browser UA", so the behaviour
     changed between enumeration and extraction.
   - **WaPo, 7: Akamai "Access Denied" captures** used at extraction. 200 captures exist for most of
     them.
   - **NYT, 5, and Reuters, 1: "no Wayback capture found via availability API".** The availability
     API returned nothing, but 200 captures exist and were fetched here.
   - **Yahoo, 4:** the live URL 404'd or redirected at extraction.
   - **Fox, 3, and CBS, 1:** genuinely rejected. All are mentions-only pieces whose mention the v1
     relevance terms did not match.
4. **`live_blog`, 22 (format gap), plus 21 that exist but can't be verified.** The US corpus holds no
   live blog.
   - CNN ran a daily `world/live-news/…-09-DD-24` blog every day from Sep 17 to Sep 24 (8 pages).
     The CNN manifest only covered date-path article URLs.
   - Other outlets: NYT has 6 daily `live/2024/09/DD/world/…` pages, WaPo 4 daily "israel-lebanon-hezbollah-hamas-war-news" blogs,
     AP 2 (`live/lebanon-syria-pagers-hezbollah-updates`, which was a candidate dropped by
     Cloudflare, and `live/lebanon-israel-strikes-hamas-war-updates`) and NBC 1.
   - Fox's row is a misclassified "WATCH LIVE" video page.

   In-window capture timestamps for re-collection are in `gap-manifest.csv`.
5. **Paywall flags.** 54 NYT, 28 WaPo and 19 CNN missing items carry `isAccessibleForFree: false`.
   This marks metering, not truncation: the fetched copies have median bodies of 782 (NYT),
   1,174 (WaPo) and 1,028 (CNN) words.
6. **`inaccessible`: 0.** Every reference item could be fetched. Some pool items could not be
   fetched at all: 11 Reuters, 4 WaPo, 10 ABC (4 stories with no 200 capture, 6 live-updates URLs with
   no usable in-window capture), 2 NYT and 1 Yahoo. They are not in the reference set because their mention
   could not be checked.

## 4. Systematic gaps and concrete fixes

1. **AP: treat challenge pages as fetch failures and fetch AP from Wayback.** Add "Just a moment...",
   "Access Denied" and stored 401/403 pages as hard fetch failures before relevance tagging; they
   must never become relevance "none". Then re-collect the AP candidates and the 18 AP
   `in_manifest_not_candidate` items from Wayback 200 captures. Live fetching works only with a real
   browser now. This one fix gives the required wire baseline its first documents.
2. **Discovery: use the listings that exist.**
   - NYT daily sitemap `nytimes.com/sitemap/2024/09/DD/` (works live).
   - CNN monthly sitemaps `cnn.com/sitemap/article|live-story|video/<section>/2024/09.xml`.
   - The CBS and NBC video sitemaps, alongside the article ones.
   - For ABC, USA Today and WaPo, which have no working listing, use Media Cloud story lists
     (ABC, USA Today) as the manifest of record. For WaPo, use per-day CDX prefixes plus Wayback
     timemap 200-capture lookups.
3. **Pick Wayback captures by status, not by time** (WaPo, Reuters, NYT). Use
   `web.archive.org/web/timemap/json?url=…&filter=statuscode:200`. It answered in about 1 s, while
   `/cdx/search/cdx` took about 60 s per URL in this run. The `wayback/available` API missed captures
   that exist.
4. **Topic-based triage** instead of slug tagging, as in Germany. This recovers the 50
   `in_manifest_not_candidate` items: CNN, AP, NBC and CBS have complete manifests where Lebanon and
   Hezbollah slugs are enumerated but never fetched.
5. **Live blogs as timestamped entries.** Collect the 8 CNN, 6 NYT, 4 WaPo and 2 AP daily blogs from
   in-window captures, one record per entry. ABC `live-updates` captures are client-rendered shells;
   they need a renderer or ABC's content API, and some way to tell which slug carried the attacks.
6. **Wire copies as their own document type.** ABC `wireStory`, WaPo `_story.html` and Yahoo
   syndication should be typed `wire_copy`, linked to the provider (AP, Reuters, dpa, AFP) and
   deduplicated against the provider's own record. They count for "what an ABC/WaPo/Yahoo reader
   could see", but not as that outlet's reporting. ABC's `/US/` and `/International/` twins collapse
   to one.
7. **Reuters needs a different route.** Options:
   - a licensed feed or a renderer that passes the 401;
   - Reuters copies on Yahoo, which carried 48 distinct pager headlines, as a recall proxy and text
     source;
   - the 5 Wayback 200 captures found here.

   Without one of these, Reuters should be marked "not measurable" in any comparison.

## 5. Corpus items that look wrong (listed, not fixed)

Full list: `raw/corpus-issues.csv`.

- **Probably off-topic (8).**
  - 7 CNN video records from Sep 27 – Oct 4 about Beirut strikes, 5–35 words each, with no pager or
    device wording: `us_cnn_988ba91188`, `1d5d0054f9`, `e9df9fa49e`, `74950daf60`, `af080302bd`,
    `7d156f4ba5`, `e25861e961`. Relevance "related" came from "explosion" plus Hezbollah.
  - CBS `us_cbs_8d3f0e89ac` (914 words, death toll over 2,000, no attack wording).
- **Out of scope (4).**
  - `us_cbs_b6fde07557` is a CBS Chicago local-station page.
  - Three Yahoo records are other Yahoo properties: `us_yahoo_6b6ad5ce8c` (ca.news.yahoo.com),
    `us_yahoo_ae4f6eb3f5` (finance.yahoo.com) and `us_yahoo_e4c4db9ea5` (sg.news.yahoo.com).
- **Dates outside the collection window (2).** `us_cbs_deca8d7e0f` (Oct 31) and `us_nbc_d7d1591943`
  (Oct 29, a CNN-panel "beeper" story).
- **Short record.** `us_yahoo_5f33d95679` has 36 words.
- **Structural.** These are not per-record errors:
  - no live blogs at all;
  - no AP records although AP is the wire baseline;
  - Yahoo records do not store the content provider, which `recall_audit_us_yahoo.py` recovers from
    the raw HTML.

  Within the corpus, deduplication works: no two primary records share a stable ID or headline. The
  26 non-primary CNN duplicates are correctly flagged.

## 6. Open problems

- **Reuters** cannot be audited with public routes (section 2). **WaPo** has no independent route,
  so its figure only checks the CDX path.
- **Mentions-only items are under-detected** where Media Cloud is thin: NYT (5 hits) and AP (26 hits
  in a 323-story source). NBC's source holds 436 stories in 8 days, which looks incomplete for an
  outlet of its size. The true mentions-only recall is probably lower than shown.
- **ABC live blogs:** 20 `live-updates` URLs have in-window captures, but every capture is an empty
  client-rendered shell. Whether ABC ran a pager-attack live blog could not be established.
- **Yahoo's reference** is mostly GDELT, which was also its original route, so independence is
  limited to the 73 Media Cloud hits. Yahoo-hosted copies expire: 127 GDELT items now 404 live and
  were read from Wayback.
- **The site-chrome filter** (section 1.2) was added after the Germany audit. Re-running the Germany
  report with the current scripts may shift a few Germany rows. Germany outputs were not regenerated.
- **The "central" label means the attack is in the headline, the description or the first ~700
  characters.** For multi-topic formats (podcast rundowns, newsletters, opinion pages with several
  items) it overstates centrality. Two of the 22 spot-checked rows were like this (below).
- **Spot-check** (`raw/spot-check.csv`, `recall_audit_spotcheck.py us`, seed 20241004): 22 rows, two
  per outlet (one central, one mention). For each, the title, the page date and about 1,000
  characters around the matched term were read.
  - **False positives: 0/22.** All rows refer to the Sep 17/18 attacks and are dated Sep 17–24.
  - Two rows are true mentions with a generous "central" label: a USA Today Excerpt podcast whose
    rundown lists the detonations second, and a Fox piece about Harris whose first paragraph recaps
    the attack.
  - One row is a marginal mention: a bracketed "[pagers exploding]" aside in a quote, Fox, Sep 22.
  - Before this sample was drawn, the site-chrome filter had removed 24 false positives (section 1.2).
    Without that filter the false-positive rate on ABC live blogs and NYT video pages would have been
    high.
- TV broadcasts are outside this text audit, as are network video pages beyond their
  headline/description.
