# Germany recall audit, Sep 17–24 2024 (day 0–7)

Audit run 2026-10-04; report step re-run 2026-10-05 with the site-chrome filter (see the end of section 1.2). Scripts: `pipeline/08-recall-audit/recall_audit_*.py`. Nothing in the corpus, the
manifests or the pipeline notes was changed.

## Bottom line

- The reference set has **309 verified items** that substantively mention the pager or walkie-talkie
  attacks: 218 are centrally about them, 91 only mention them. The corpus holds **120** of them, so
  recall is **0.39 overall, 0.48 for central items and 0.16 for mentions-only items**.
- The corpus is mainly a sample of each outlet's attack-themed articles: pieces whose URLs
  contain attack words and that were captured by Wayback CDX. Background and escalation pieces that
  mention the attacks in the body are mostly missing. So are live blogs and automated wire-feed pages.
  "Not in our sample" must not be read as "the outlet did not say it".
- The two largest gaps are discovery failures, not topic failures:
  - ntv: 48 of 56 items missing. The CDX manifest lost whole days.
  - WELT: 49 of 63 missing. The CDX manifest was starved by WELT's `ia_archiver` block, and the
    enumeration regex excluded the `plus…` and `newsticker/dpa_nt` paths.
- 57 central items that are missing from the manifests have slugs the original keyword tagger would
  have caught (45 "strong" pager-term slugs, 12 "related"), if they had been enumerated.
- The gap manifest lists **196 items** (189 verified, plus 7 live blogs whose entries can't be read
  from the capture). All were fetched in this audit, live or from Wayback.

## 1. Method

### 1.1 Reference routes

Per outlet, candidates came from several discovery routes. The **pool** (809 URLs) is the union of
these routes after a topic filter. Every pool item was then checked against its body text
(section 1.2).

| route | what it sees | independence from the original route |
|---|---|---|
| **Media Cloud** full-text search, `Pager OR Pagern OR … OR Funkgeräte OR Walkie OR "Gold Apollo"`, Sep 17–25 | Body-text matches in Media Cloud's own crawl. Sources: tagesschau.de 21043, zdf.de 40752, rtl.de 179736, n-tv.de 23538, bild.de 22009, spiegel.de 19831, welt.de 20453, t-online.de 40762, rnd.de 1324242 | Fully independent: a different crawler, and full text rather than slugs. |
| **GDELT 2.0 raw translingual GKG** (all 15-min files, Sep 17 00:00 – Sep 25 06:00 UTC, 1,584 files) | Pages with a Lebanon location or Hezbollah organisation extracted from the body, or a topic term in the title | Independent. Germany never used GDELT except the WELT supplement, whose DOC API calls failed. |
| **Outlet-native dated listings** (live) | tagesschau.de/archiv (month pages 1–6), spiegel.de/nachrichtenarchiv (daily), welt.de/schlagzeilen (daily), ntv monthly sitemap, Bild monthly sitemap, RTL monthly sitemap | Independent of CDX. The Bild sitemap differs from the Bild dated archive page used originally, but both are Bild's own complete lists. |
| **RND dated archive** `rnd.de/archiv/artikel-DD-MM-YYYY/` via Wayback | RND's daily list | Independent of the slug-tagged CDX sweep, but still depends on Wayback. |
| **Archived homepages and section pages** (Wayback, 7 timestamps from Sep 17 17:00 to Sep 23 12:00 UTC; 20,860 links) | Front pages and topic/section pages of all 9 outlets | Link-based rather than slug-based, but still depends on Wayback. |
| **Live-blog path CDX** (`tagesschau.de/newsticker/`, `zdf.de/nachrichten/politik/ausland/`, `rnd.de/politik/`, `t-online.de/nachrichten/ausland/`, …) with all capture timestamps | Live blogs and tickers | Same mechanism as the original route (CDX), on paths the original regex excluded. |
| Codex web search for live blogs | Leads only | Most URLs it returned were unverified; only those confirmed by a fetch were kept. |

**Topic filter.** Listing, homepage and GDELT items entered the pool only if the title or URL
contained Libanon, Hisbollah, Nahost, Israel, Beirut, Nasrallah, Pager, Funkgerät, Walkie, Mossad,
Netanjahu, Gallant or Explosion. Items that discuss the attacks without any such word in their title
or slug can be found only by Media Cloud's full-text search (and, for Lebanon locations, GDELT).

### 1.2 Verification

Every pool item was fetched: from our own raw HTML where it existed, otherwise live, otherwise from
Wayback near 2024-09-20. All fetched HTML is under `08-recall-audit/raw/pages/`. The checks:

- **Substantive mention.** The article body (JSON-LD `articleBody`, otherwise `<p>`/`<li>` text inside
  `<article>`) must contain a strong term (pager, piepser, funkgerät, walkie, Gold Apollo), or a weak
  device phrase within 400 characters of Libanon/Hisbollah. Weak phrases are "Explosionen …
  technischer Geräte", "Angriffe auf Kommunikationsgeräte" and similar. Mentions that occur only inside
  link text (teaser and "Mehr zum Thema" links) do not count.
- **Central vs mention.** An item is central if the attack terms are in the headline, the
  description or roughly the first paragraph (the first 700 characters).
- **Window.** The best available date (page JSON-LD, then Media Cloud/listing date, then URL date) must
  fall between Sep 17 and Sep 24. Live blogs count if they were published after Jun 1 2024 and have a
  Wayback capture in the window. They are verified only against in-window captures, never against
  today's live page. Up to three captures (around Sep 19, 21 and 24) are tried.
- **Redirect check.** If the fetched page's canonical URL is another pool item of the same outlet,
  the row is dropped as a duplicate. This happened 3 times: Wayback served one Tagesschau daily blog
  in place of another.
- **Site chrome** (added 2026-10-05, from the US audit). A paragraph of 35 words or fewer that recurs
  on 3 or more differently titled pages of one outlet is treated as a teaser card or "latest" box, and
  attack terms inside it do not count. This removed 5 reference items, all mentions: 3 ntv articles
  whose only attack text was a teaser ("Streit zu Pager-Explosionen vor UN-Sicherheitsrat",
  "Pager-Angriffe auf die Hisbollah…"), the RND Sep 17 ticker and one RND article. Long paragraphs
  are exempt because ntv's "Der Tag" entries reuse the same dpa paragraph as real body text.

The verification earned its keep. 42 Media Cloud "pager" hits were rejected, 37 of them on Bild: unrelated
pages (iPhone 16, football) whose site chrome mentioned the pagers on Sep 18. Spot-checks of 34
mention-only evidence snippets found no false positives after one regex fix: a Shin Bet
"Bombenanschlag … Gerät" sentence had matched.

### 1.3 Matching against our data

URLs were normalised: scheme, `www`/`m`/`amp`, query, fragment, trailing slash, `/amp` and `.amp`
were stripped, and `zdfheute.de` was mapped to `zdf.de/nachrichten`. They were then keyed by the
outlet's stable ID: RTL `idNNN`, ntv `articleNNN`, Bild hex ID, Spiegel `a-UUID`, WELT
`article|plus|video NNN`, t-online `id_NNN`, RND 26-character ID, ZDF `…-1NN.html`. Live blogs are
keyed on the full URL, because RND reuses one ID for every daily ticker. The exception is t-online's
newsblog, which is one rolling page whose slug follows the latest headline, so it keeps its ID.
Unmatched items fell back to fuzzy headline matching (ratio ≥ 0.90).

Status classes, assigned in this order: `in_corpus`, `live_blog`, `in_candidates_dropped`,
`in_manifest_not_candidate`, `not_in_manifest`, `inaccessible`.

## 2. Recall per outlet

| outlet | corpus (all dates) | ref items | in corpus | recall | central: in/ref | recall | mention: in/ref | recall | Media Cloud hits in ref | gap manifest (central) |
|---|---|---|---|---|---|---|---|---|---|---|
| Bild | 26 | 31 | 18 | 0.58 | 16/21 | 0.76 | 2/10 | 0.20 | 22 | 13 (5) |
| ntv | 12 | 56 | 8 | 0.14 | 8/42 | 0.19 | 0/14 | 0.00 | 25 | 48 (34) |
| RND | 21 | 24 | 10 | 0.42 | 8/13 | 0.62 | 2/11 | 0.18 | 19 | 21 (5)¹ |
| RTL | 2 | 8 | 2 | 0.25 | 2/8 | 0.25 | 0/0 | – | 8 | 6 (6) |
| Spiegel | 33 | 54 | 24 | 0.44 | 22/40 | 0.55 | 2/14 | 0.14 | 45 | 30 (18) |
| Tagesschau | 15 | 26 | 11 | 0.42 | 10/18 | 0.56 | 1/8 | 0.12 | 22 | 15 (8)¹ |
| t-online | 36 | 36 | 23 | 0.64 | 18/22 | 0.82 | 5/14 | 0.36 | 7 | 13 (4) |
| WELT | 16 | 63 | 14 | 0.22 | 14/47 | 0.30 | 0/16 | 0.00 | 40 | 49 (33) |
| ZDFheute | 15 | 11 | 10 | 0.91 | 7/7 | 1.00 | 3/4 | 0.75 | 10 | 1 (0) |
| **all** | 176 | **309** | **120** | **0.39** | 105/218 | **0.48** | 15/91 | **0.16** | 198 | 196 |

¹ The gap manifest also includes `live_blog_unverified` rows (RND daily tickers and 2 Tagesschau
daily blogs): blogs that exist in the window but whose captured HTML does not contain the entries.

dpa (required-baseline) has no own route. It enters through t-online's dpa-credited stream and
through WELT's automated dpa newsticker pages (17 reference items, none in the corpus). No separate
recall is computed.

### How independent and how large each reference is

- **Spiegel, Bild, Tagesschau, WELT, ntv, RND**: strong. Each has at least one complete or
  near-complete independent listing (daily archive or sitemap) plus Media Cloud and GDELT.
- **t-online**: medium. There is no native listing: no sitemap, the archive pages 404, and the topic
  pages 404. The reference comes from GDELT, which found 23/23 of our in-window on-topic t-online
  items, plus homepage captures. Media Cloud is thin here (7 hits; it found 5 of our 23 items).
  Mentions-only coverage is under-sampled. Media Cloud would have helped if its t-online source were
  complete.
- **ZDFheute**: weak. The reference has 11 items, and the recall of 0.91 rests on Media Cloud (the
  zdf.de source is sparse: 425 stories in 8 days) and homepage captures. There is no native listing,
  because zdfheute.de's sitemap is current-only. **Treat ZDF recall as unconfirmed.**
- **RTL**: weak and small. 6 of its 8 reference items are rtl.de **HbbTV teletext** pages
  (`/HBBTV/Teletext/Newsde/…`), found only by Media Cloud. RTL's thin text coverage is real for
  articles, but its teletext pages carried the story daily.

Reverse check (`raw/route-coverage.csv`): of our own 130 primary corpus records dated Sep 17–24 that
mention the attacks, the reference routes found 123 (95%). The routes therefore cover the kind of
item the pipeline collects. Their blind spots are formats nobody indexes well: tickers whose entries
load client-side, and video.

## 3. Why items are missing

Status breakdown of the 309 reference items:

| outlet | in_corpus | live_blog | in_candidates_dropped | in_manifest_not_candidate | not_in_manifest | inaccessible |
|---|---|---|---|---|---|---|
| Bild | 18 | 0 | 0 | 12 | 1 | 0 |
| ntv | 8 | 1 | 0 | 7 | 40 | 0 |
| RND | 10 | 1 | 0 | 9 | 4 | 0 |
| RTL | 2 | 0 | 0 | 0 | 6 | 0 |
| Spiegel | 24 | 0 | 1 | 18 | 11 | 0 |
| Tagesschau | 11 | 6 | 0 | 8 | 1 | 0 |
| t-online | 23 | 0 | 0 | 10 | 3 | 0 |
| WELT | 14 | 1 | 0 | 0 | 48 | 0 |
| ZDFheute | 10 | 1 | 0 | 0 | 0 | 0 |
| **total** | **120** | **10** | **1** | **64** | **114** | **0** |

What sits behind each class:

1. **`not_in_manifest`, 114 (discovery gap).** Of these, 57 are central items whose slugs would have
   been tagged (45 "strong", 12 "related"), so this is pure enumeration loss.
   - ntv lost 40. The CDX manifest has **zero URLs first captured on Sep 21 or 22**, and other days are
     thin. Failed CDX slices were not recovered (summary.csv says `complete: NO`).
   - WELT lost 48. The manifest has 60 URLs for a month. The regex excluded `/plus\d+/` (WELTplus)
     and `/newsticker/dpa_nt/` (17 dpa wire pages carrying the story), and the copilot curated layer
     found only 16.
   - Spiegel lost 11, from sections the CDX sweep never returned: netzwelt, kultur, panorama,
     wissenschaft, and the "Lage"/"News des Tages" newsletters.
   - RTL lost 6 teletext pages (outside the `rtl.de/news` prefix). t-online lost `/tv/` video pages.
2. **`in_manifest_not_candidate`, 64 (topic gap).** These were enumerated, but their slugs carry no
   pager word (27 central, 37 mentions-only). Examples: Tagesschau "Hisbollah-Chef Nasrallah sieht
   'alle roten Linien überschritten'", Spiegel "Israels Krieg gegen die Hisbollah: »Weg mit den
   Funkgeräten!«", Bild "Israels legendärer Geheimdienst: So jagt der Mossad…", and every
   Lebanon-escalation piece from Sep 20 onward that recaps the attacks in one or two paragraphs.
3. **`live_blog`, 10 (format gap)**, plus 7 more that exist but couldn't be verified.
   - Tagesschau: 6 daily Nahost live blogs. The enumeration regex excluded `/newsticker/`. Live
     pages from 2024 now redirect to the homepage (depublished), so Wayback is the only route.
   - RND: daily `liveticker-israel-und-nahost-krieg-…-DD-9-2024-<ID>` pages. The corpus holds only
     the Oct 2 version of the shared ID; it was a candidate, dropped as "none". The Sep 18–24
     captures hold only about 300 words because entries load client-side.
   - ZDF: rolling `liveblog-eskalation-nahost-israel-100.html`, verified on the Sep 24 capture; the
     earlier captures are duplicates of a pre-attack Sep 17 12:52 UTC copy.
   - WELT: a video livestream page. ntv: one entry in its Ukraine ticker.
   - t-online's newsblog (id_100491896) is in the corpus as **one snapshot**, typed `article`.
4. **`in_candidates_dropped`, 1 in the window.** Spiegel's "Pager- und Walkie-Talkie-Attacken im
   Libanon: Eskalation auf Knopfdruck" (Sep 19, SPIEGEL+) was dropped because its 353-word paywall
   teaser contained no event term. The URL slug did. A second paywalled Spiegel piece ("Israel spielt
   russisches Roulette", slug `pager-explosionen-im-libanon-…`) failed the same way, but its body
   check also failed here, so it is not in the reference set. Other dropped candidates in the window
   were correctly rejected (no attack mention). The 6 ZDF candidates dropped as "Seite nicht
   gefunden" were fetched live from `zdf.de/nachrichten` instead of `zdfheute.de` or Wayback; none of
   them is in the reference set.
5. **Paywalls.** 19 reference items are paywalled (Spiegel 11, WELT 4, Bild 3, RND 1). Their fetched
   copies hold teaser or lead text only; they are flagged in `gap-manifest.csv`.
6. **`inaccessible`: 0.** Every reference item could be fetched, live or from Wayback.

## 4. Systematic gaps and concrete fixes

1. **Discovery: use outlet-native dated listings as the manifest of record, with CDX as a fallback.**
   They exist and work live today: `spiegel.de/nachrichtenarchiv/artikel-DD.MM.YYYY.html`,
   `welt.de/schlagzeilen/nachrichten-vom-D-M-YYYY.html`, `tagesschau.de/archiv?datum=2024-09-01&pageIndex=N`,
   `n-tv.de/sitemap/sitemap-2024-09.xml.gz`, `bild.de/sitemap-index-202409.xml`,
   `rtl.de/sitemap-index-2024-09.xml`, and RND `rnd.de/archiv/artikel-DD-MM-YYYY/` via Wayback.
   These fix ntv, WELT and most of Spiegel's losses. Also widen the regexes: WELT `plus\d+` and
   `newsticker/dpa_nt`, RTL `HBBTV/Teletext`, Tagesschau `newsticker/`, t-online `/tv/`.
2. **Triage: run a topic-based re-sweep instead of slug tagging.** Tag every manifest URL whose
   title or slug has Libanon/Hisbollah/Nahost/Israel/Beirut, fetch it, and keep it if the body passes
   the substantive-mention rule in 1.2. That recovers the 64 `in_manifest_not_candidate` items. The
   cost is about 10 times more fetches per outlet, which is feasible live.
3. **Relevance on paywalled pages:** when the slug or headline has a strong term and the body is a
   paywall teaser, keep the item as `flash_or_lead` instead of dropping it as "none".
4. **Live blogs: split them into timestamped entries.** Collect each daily Tagesschau blog, the ZDF
   rolling blog, RND daily tickers and t-online's newsblog from **in-window Wayback captures**
   (timestamps are in `gap-manifest.csv`). Store one record per ticker entry, with its own
   timestamp. Never collect a rolling blog from the live site: it now shows 2025/26 content.
   RND tickers need a renderer (headless browser on the capture) or the Arc content API embedded in
   the page.
5. **Wire feeds:** treat WELT's `newsticker/dpa_nt` pages and RTL teletext as a distinct
   `wire_feed` document type. They count toward the dpa baseline and toward "what a WELT/RTL reader
   could see", but at lower prominence than editorial articles.
6. **Pre-flight checks before fetching:** reject Wayback captures that redirect to another URL
   (compare the canonical), and live fetches that 404 or redirect to a section page. These silently
   became relevance "none" in v1.

## 5. Corpus items that look wrong (listed, not fixed)

Full list: `raw/corpus-issues.csv`.

- **Duplicates, both primary (4 pairs, RND):** the same article ID appears under two slugs.
  - `ge_rnd_8077ee3c89` = `ge_rnd_2976713b85`
  - `ge_rnd_9bfa7a57f3` = `ge_rnd_9839d97395`
  - `ge_rnd_a34b40e8b3` = `ge_rnd_01d7465f51`
  - `ge_rnd_e494be678a` = `ge_rnd_8a981c41ba`

  Body hashes differ only because the captures differ.
- **Probably off-topic for "claims about the attacks" (31):** relevance `related`, but no
  pager/walkie/device-explosion wording anywhere. Most are Lebanon-escalation pieces from Sep 20 to
  Oct 14 that matched Hisbollah plus "Explosion"/"Angriff". Examples:
  - Tagesschau `5d524e455b`, `3e11dfa562`, `acc454bb65`
  - ZDF `ad2e30a014`, `abf0602bbd`, `737ed883b1`, `daec71d043`
  - ntv `5a5721af9d`, `baf91ae55e`, `6450aa646b`
  - Bild `953484f50d`, `7218ce32d5`, `bbeb8e6265`, `ed582e9eda`, `c0ffa354ca`
  - Spiegel `8afd32129d`, `0951d16d64`, `4fe239400b`, `632b1030b5`, `72c31d11a3`, `64bca1a110`
  - t-online `1db2910a11`, `03f8fb4003`, `45669949cc`, `bb00a3138a`, `7bed7ecfe6`, `2142c2c186`,
    `822b217caf`
  - RND `4ec3cc60b1`, `956cd36868`

  For claim-presence analysis these should be excluded or downgraded to "context".
- **Empty bodies (5 Spiegel):** `0c74f9ad5e`, `8be8faca25`, `56bd1c4430`, `eb13e72e65`, `176d1e0d56`.
  These are paywall shells (v1.2 retyped four of them `flash_or_lead`); they are headline-only records.
- **Mis-typed:** `ge_tonline_1e9c010a33` is t-online's rolling newsblog (`id_100491896`), stored as one
  `article` snapshot. ntv `der_tag` records are 30–130-word ticker entries; some are typed
  `article`.
- **Dates:** no German record is dated outside Sep 17 – Oct 17. The out-of-window filter in
  normalisation correctly dropped 2020–2023 pages that the CDX sweep had picked up as recaptures.

## 6. Open problems

- ZDF and RTL reference sets are small and lean on Media Cloud. There is no independent complete
  listing for zdf.de 2024 or for t-online, so recall for these three is less certain.
- Mention-only items are under-detected for t-online and ZDF (no complete listing; Media Cloud thin).
  The true mentions-only recall is probably lower than shown.
- RND tickers and the two early-day Tagesschau captures can't be text-verified from Wayback HTML.
- TV broadcasts (Tagesschau 20 Uhr, RTL Aktuell, heute) are outside this text audit; the Mediatheken
  were not checked.
- Media Cloud would have helped most with a complete t-online and zdf.de source, and with
  `live-blog` indexing. It does not index client-side ticker entries either.
