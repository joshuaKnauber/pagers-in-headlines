# Lebanon recall audit (v1, 2026-10-04)

Scope: the five Lebanese collection-gate rows (LBCI, MTV, Al Jadeed, Al-Manar,
NNA) for the audit window Sep 17 to Sep 24 2024 (day 0 to day 7, Beirut dates).
Question: of the items each outlet published in the window that mention the
pager or walkie-talkie attacks, how many are in `corpus.jsonl` (primary
records), and why are the others missing?

Files in this directory:

- `reference-set.csv`: 640 verified in-window items that mention the attacks,
  with discovery route, central/mention class, pipeline status and matched
  `document_id`.
- `gap-manifest.csv`: 464 missing items with a working collection route
  (live URL, `archive.almanar.com.lb`, or a Wayback capture timestamp).
- `raw/`: every fetched page (HTML cache per outlet), the GDELT and Media Cloud
  extracts, task lists, worker outputs (`check-results*.jsonl`),
  `items.json` (all checked items with snippets), `review-queue.csv`,
  `manual-review.csv` (my verdicts), `census-summary.json`, `recall-tables.json`.
- Scripts: `pipeline/08-recall-audit/recall_audit_il_lb_*.py` (gdelt, mediacloud, tasks,
  check, build, report, common).

Nothing in the existing corpus, manifests or notes was changed.

## 1. Method

### Relevance test

Every candidate page was fetched and its body extracted with a container-first
extractor (JSON-LD `articleBody`, then the outlet's article container, never
the related-links rail). Relevance is lexical, on headline + body +
meta description, after stripping Arabic diacritics and tatweel:

- strong terms count anywhere: بيجر / بايجر / البيجرز / أجهزة النداء / ووكي توكي /
  غولد أبولو / آيكوم / مجزرة الثلاثاء / مجزرة الأربعاء / العدوان السيبراني, plus
  pager, walkie-talkie, Gold Apollo, Icom, bipeur;
- weak terms (لاسلكي, أجهزة الاتصال/اتصال/الاتصالات, تفجير الأجهزة, الخرق الأمني,
  communication devices, wireless devices) count only if the text also carries
  a blast word (تفجير, انفجار, explosion, attack...).

Hits within 80 characters collapse into one mention. **central** = device term
in the headline, or three or more separate mentions in the body, or a mention
in the first 60 words of an item shorter than 120 words. **mention** = any other
substantive mention. A page whose only mention sits in navigation or
related-links chrome is not counted (the extractor never reads those rails;
Al Jadeed headline-only shells count on headline + description only).

Precision check: a random sample of 40 missing items was read in full. All 40
mention the attacks; about 4 of 40 would be "mention" rather than "central" on
a human read. The lexical test misses euphemistic text: Al-Manar's bulletin
intros ("عدوان صهيوني مكتمل المواصفات") and some NNA statements ("العدوان
الإسرائيلي الذي استهدف لبنان عصر اليوم") never name the device. All bulletin
intros were therefore read and classified by hand (`raw/manual-review.csv`).
Everything below is a **lower bound** on what the outlets published.

### Discovery routes and their independence

| route | what it is | independent of the pipeline? | used for |
|---|---|---|---|
| `gdelt` | GDELT 2.0 GKG, all 1,728 15-minute files (English + translingual) Sep 17 to Sep 25 UTC, filtered by domain | yes (GDELT crawler, not Wayback) | all outlets; thin for Lebanese TV sites (LBCI 84, MTV 27, Al Jadeed 14 URLs; Al-Manar 231 + 109 EN/FR; NNA 0) |
| `mediacloud` | Media Cloud full-text search, Arabic device query, per source | yes (RSS/sitemap ingest) | only Al-Manar has stories in the window (1,250 total; 115 Arabic + 195 EN/FR/ES device hits). LBCI, MTV, Al Jadeed, NNA, Al-Akhbar, Nidaa al-Watan, An-Nahar, L'Orient-Le Jour all return 0 stories for Sep 17-24 |
| `id-census` | every article ID in the outlet's own sequential band that was not in the manifest, fetched live by ID (LBCI 796200-798550, Al Jadeed 502450-504350) | yes (outlet's own ID space, not Wayback) | LBCI 534 IDs (477 real dated items, 57 redirect to the homepage), Al Jadeed 152 IDs (~146 real items) |
| `id-sample` | 800 random Al-Manar IDs from the band 12,479,500-12,520,500 not in the manifest | yes | 790 are 404 (WordPress IDs shared with non-articles); 10 resolve, about half of them image/attachment pages |
| `mtv-slugless` | all 1,836 MTV sitemap URLs dated Sep 17-24 that have no slug | partly (MTV's own sitemap, already in the manifest but never triaged) | full census |
| `manifest-kw` | every untagged in-window manifest item whose slug/title has a Lebanon/Hezbollah/Israel/war keyword (LBCI 1,235, Al Jadeed 1,147, MTV 1,115, Al-Manar 1,126, NNA 38) | no (same manifest), but tests the triage step independently (body, not slug) | full census of the stratum |
| `control` | 150 random in-window untagged items with no keyword per TV outlet | no; estimates leakage outside the keyword stratum | LBCI 5, MTV 4, Al Jadeed 1 of 150 relevant (2, 3, 1 after dropping items GDELT also found; the extrapolation uses these) |
| `websearch` | codex web search for long-form and bulletin-intro sources | yes | Section 6 only |

Media Cloud: tokenisation is exact-form. On Al-Manar, البيجر 38 stories, بيجر 5,
البايجر 47 (Al-Manar's own spelling), "أجهزة الاتصال" 21, اللاسلكي 16, pager 172
(foreign editions). Queries must list the definite and indefinite forms and
both spellings. Media Cloud matches page text including related-link rails: of
115 Arabic Al-Manar hits, 51 contain no device mention in the article itself
(many are headline-only "عاجل" pages whose body node is empty). MC hits need a
body check before use. Had Media Cloud covered the TV sites, it would have
replaced the GDELT and ID-census routes; it does not.

### Matching

URLs were normalised to outlet IDs (`lbci:<id>[/en]`, `mtv:<id>`,
`aljadeed:<id>`, `almanar:[english/]<id>`, `nna:<id>`), which collapses slug,
encoding, query-string and section variants (e.g. LBCI `latest-news` vs
`آخر-الأخبار`, MTV slugged vs sitemap `/news/<id>`). Items without an ID match
fell back to fuzzy headline matching against corpus, candidates and manifest
titles (threshold 0.82); no Lebanese item needed it.

### Recall estimate

For LBCI, MTV, Al Jadeed and Al-Manar the checks above amount to a census of
the window: every in-window manifest item with a keyword, every MTV slugless
item, every LBCI/Al Jadeed ID outside the manifest, plus a control sample for
the rest. So:

    recall = corpus records in window (relevant) /
             (corpus records in window + missing items found + extrapolated control leakage)

Corpus records in the window are classified with the same matcher. Route-specific
recall (share of a route's relevant items already in the corpus) is reported
alongside as an independence check.

## 2. Per-outlet recall

Census recall, Sep 17-24 (counts are items; EN and AR editions count separately):

| outlet | corpus central | corpus mention | missing central | missing mention | control extrapolation | recall central | recall mention | recall all |
|---|---|---|---|---|---|---|---|---|
| LBCI | 104 | 0 | 91 | 33 | 5 | 53% | 0% | 45% |
| MTV | 113 | 0 | 167 | 48 | 12 | 40% | 0% | 33% |
| Al Jadeed | 48 | 0 | 48 | 14 | 3 | 50% | 0% | 43% |
| Al-Manar (Arabic) | 40 | 3 | 30 | 28 | 0 (ID sample: ~50, very rough) | 57% | 10% | 43% (≈29% with the ID-sample estimate) |
| NNA | 2 (undated) | 0 | 4 | 1 | n/a | **no reference** | | |

Route-specific recall (independent routes only):

| outlet | route | central found / in corpus | mention found / in corpus |
|---|---|---|---|
| LBCI | gdelt | 6 / 5 | 7 / 0 |
| LBCI | id-census | 18 / 0 (never captured by Wayback) | 0 / 0 |
| MTV | gdelt | 1 / 1 | 5 / 0 |
| Al Jadeed | gdelt | 1 / 1 | 0 / 0 |
| Al Jadeed | id-census | 7 / 0 | 5 / 0 |
| Al-Manar | mediacloud | 41 / 23 (56%) | 21 / 2 |
| Al-Manar | gdelt | 31 / 9 (29%) | 29 / 3 |
| Al-Manar | id-sample | 1 / 0 | 0 / 0 |
| Al-Manar EN/FR/ES | mediacloud | 0 | 143 / 0 (not body-checked) |

Reading the numbers:

- **The corpus holds essentially no mentions-only items.** All Lebanese triage
  ran on slugs or titles carrying a device word, so an item that discusses the
  attacks under a headline about Nasrallah, the escalation, the hospitals or
  the Security Council is never picked. For "what was an LBCI reader told",
  this is the main bias: day-3-onwards framing pieces are missing.
- **Even centrally-about items are only half in.** Roughly one central item in
  two is missing for LBCI and Al Jadeed, three in five for MTV.
- **Independence caveat.** GDELT barely crawls the Lebanese TV sites, so the
  clean independent samples are tiny (LBCI 13, MTV 6, Al Jadeed 1 relevant).
  The census figures lean on routes that share the pipeline's manifest (they
  test triage, not discovery). Discovery is tested independently only by the
  ID censuses (LBCI, Al Jadeed: complete) and Media Cloud (Al-Manar).
- **Al-Manar extrapolation.** 10 of 800 random non-manifest IDs in the band
  resolve on archive.almanar.com.lb; about half are image or attachment pages
  ("photo_2024-09-18_...", "خريطة 17-09-2024"), about 5 are real briefs. That
  puts roughly 250 unarchived Al-Manar articles in the window (95% CI ~80 to
  ~580) next to ~1,190 in the manifest, i.e. Wayback holds ~80% of Al-Manar's
  output. One of the five real briefs is about the attack on a human read
  (12486432, Abiad on the toll "relative to the size of the attack"; empty body,
  no device word). Scaled up that is on the order of 50 more relevant items, with
  a very wide interval. GDELT (231 URLs) and Media Cloud (115) found no Arabic
  Al-Manar URL outside the manifest, so the unarchived part is mostly low-profile
  briefs.
- **NNA: no independent reference could be built.** Wayback holds about 50 NNA
  article captures for Sep 17-25, GDELT and Media Cloud hold none, the current
  site is a client-rendered app whose article API is robots-disallowed. NNA
  published several hundred items a day; 448 manifest URLs for the whole
  33-day window is a sliver. The 38 keyword items checked gave 5 relevant
  missing items, including Ad-Diyar and Al-Sharq newspaper digests of 2,657 and
  715 words. Any "not in our sample" statement for NNA is uninformative.

## 3. Miss reasons

Reference items not in the corpus (Al-Manar foreign editions excluded):

| reason | LBCI | MTV | Al Jadeed | Al-Manar | NNA |
|---|---|---|---|---|---|
| triage: MTV sitemap URL without slug, never title-checked | | 126 (115 central) | | | |
| triage: no device word in headline/slug (body mention) | 73 (41 central) | 68 (31 central) | 22 (13 central) | 44 (17 central) | 3 |
| triage: device word in headline, slug truncated/different or term list too narrow | 32 | 21 | 28 | 10 | 2 |
| enumeration: never captured by Wayback (found by ID census) | 18 | | 12 | 1 (+~50 est., very rough) | most of the outlet |
| triage: tagged/extracted but dropped | 1 | | | 3 | |

Headline device terms that the slug tagger missed (counts over LBCI/MTV/Al
Jadeed): "communication devices" 27, "pager" in truncated or differing slugs 34,
تفجير أجهزة 16, انفجار أجهزة 15, بيجر/بايجر in differing slugs 25, "device
explosions" 9, "wireless devices" 8, Icom/آيكوم 11, الهجوم السيبراني 4. The
tagger list has أجهزة-الاتصال but not the indefinite أجهزة-اتصال, nothing for
English "communication devices / wireless devices / explosions", and LBCI slugs
are cut at about 70 characters. **Al-Manar's own spelling البايجر is missing
from the title-sweep term list** (it has بيجر/البيجر/بيجرات only): 7 of the 12
Al-Manar titles spelled "بايجر/البايجر/البايجرات" are untagged, among them the
text of Nasrallah's Sep 19 speech (12494517), the health minister's 2,750-wounded
toll (12486630) and the SSNP "عدوان البايجر" statement (12487400).

Language split of missing items: LBCI 81 Arabic / 43 English; MTV 118 / 97.

## 4. Systematic gaps and fixes

1. **Slug triage is the dominant loss.** Fix in step 4/5: for slug outlets,
   stop tagging on slugs. Fetch titles (or bodies) for every in-window URL; the
   live sites take it (this audit fetched ~9,000 Lebanese pages in under two
   hours at ≤2 req/s per host). Tag on headline + body with the two-tier term
   list above, with diacritics stripped.
2. **MTV slugless sitemap URLs.** 1,836 of MTV's in-window sitemap URLs have no
   slug and were never triaged; 126 are relevant. Fix: treat the sitemap as the
   triage list and fetch every URL.
3. **ID-band censuses beat Wayback for LBCI and Al Jadeed.** Both sites resolve
   `/news/x/<id>/x[/ar]` for any ID. The LBCI band held ~477 dated items the
   manifest lacked (Wayback holds ~79% of LBCI's window output); Al Jadeed ~146
   (~92%). Fix: enumerate LBCI and Al Jadeed
   by ID band from the corpus date anchors, not by CDX.
4. **Al-Manar enumeration.** The manifest is a Wayback subset (~80% of articles
   by the ID sample). archive.almanar.com.lb answers 404 fast for non-article
   IDs, so a full band scan (41K IDs, ~3 h at 4 req/s) is cheap. Body-tag with
   diacritics stripped: Al-Manar writes مجزرةِ يومَ الثلاثاءِ with harakat.
5. **Bulletin intros are a format the pipeline never targeted** (Section 6).
   Add them as a fixed daily item per channel.
6. **Mentions-only items** need body-level triage; there is no title fix.
7. **Media Cloud** is only useful for Al-Manar, and only with body checks.
8. **Extraction bug found while auditing** (for the pipeline's extractor too):
   when an article container is empty (Al-Manar "عاجل" pages, LBCI `LongDesc`),
   a slice-to-end-marker fallback picks up the related rail and site chrome.
   Treat an empty container as an empty body.

## 5. Gap manifest

`gap-manifest.csv`: 464 items, all fetched successfully during the audit.

| outlet | central | mention | route |
|---|---|---|---|
| MTV | 167 | 48 | live |
| LBCI | 91 | 33 | live |
| Al Jadeed | 48 | 14 | live (headline-only shells for many) |
| Al-Manar | 30 | 28 | archive.almanar.com.lb (live) |
| NNA | 4 | 1 | Wayback (capture timestamp in file) |

Not in the gap manifest: 143 Al-Manar EN/FR/ES Media Cloud hits (not
body-checked; en-archive/fr-archive.almanar.com.lb return HTTP 421, use Wayback),
and items whose classification was "none" by the lexical test (bulletin intros
excepted, which were read).

Long-form items missing from the corpus worth collecting first (all live):
Al-Manar "الصحافة اليوم" press reviews for Sep 19, 20, 21 (7,756 / 3,835 / 4,886
words) and "عناوين واسرار الصحف" Sep 18; Al-Manar's text of Nasrallah's Sep 19
speech (12494517, 1,144 words, headline "تفجير البايجرات"); LBCI and Al Jadeed full text of Bou Habib's UN
Security Council address (Sep 20-21); MTV analyses "هذه أبرز عمليات الموساد",
"هل خسرت إسرائيل الورقة الرابحة؟", "إسرائيل تحوّل سلعاً تكنولوجية إلى أدوات قتل",
"لبنان ينكشف سياسياً وأمنياً"; Al Jadeed's republished An-Nahar and Al-Joumhouria
leads; NNA's Ad-Diyar and Al-Sharq digests (Wayback).

## 6. Lebanese long-form and TV-text sources

Checked for availability only; nothing was collected into the corpus.

### TV evening-bulletin intros (مقدمات نشرات الأخبار المسائية)

These are the channels' own editorial voice, read on air at the top of the
evening news, and the pipeline has none of them.

| source | URL pattern | Sep 17-24 found | access | in corpus |
|---|---|---|---|---|
| LBCI own intro | `lbcgroup.tv/news/lebanon-news-intro/<id>/مقدمة-النشرة-المسائية-DD-MM-YYYY/ar` (category 74 page is client-rendered; IDs sequential, ID-only URL works) | Sep 18, 19, 20, 21, 22, 23, 24 (Sep 17 not found in the full ID band) | live | 0 |
| Al Jadeed own intro | two daily forms: `aljadeed.tv/news/خاص-الجديد/<id>/مقدمة-النشرة-المسائية-<title>` or `/news/مقدمة-النشرة-المسائية-DD-MM-YYYY`, and `/news/محليات/<id>/مقدمة-نشرة-أخبار-الجديد` (same text twice) | Sep 19, 21, 24 found; other days not located | live (some are headline-only shells) | 1 (Sep 19, محليات copy) |
| Al-Manar own intro | `almanar.com.lb/<id>` titled "مقدمة نشرة أخبار المنار الرئيسية ليوم ..." | all 8 days: 12482516, 12488126, 12495859, 12500237, 12505165, 12509499, 12513327, 12518420 (all in the title manifest) | archive.almanar.com.lb live; the Sep 20 page has an empty body on the archive host, use Wayback | 0 |
| MTV | no own intro article found; MTV republishes a daily compilation "مقدمات نشرات الأخبار المسائية" under `mtv.com.lb/News/من_الصحافة/<id>/...` | Sep 17 (MTV, NBN, Al-Manar, OTV intros) and Sep 24 (+ LBCI, Al Jadeed) | live | 0 |
| NNA compilation | title "مقدمات نشرات الاخبار المسائية ليوم <day> D/M/2024"; current site `nna-leb.gov.lb/ar/news/<new-id>/...` (17 Sep = 398632) | Sep 17 verified (title + description only) | current site serves title and description server-side; body comes from the robots-disallowed `/api/`; 2024-schema pages almost absent from Wayback | 0 |
| NNA republished | Sidonia News `sidonianews.net/article<id>/` (17 Sep = article325257, NBN/MTV/Al-Manar/OTV), Lebanon24 `/news/lebanon/<id>/...` (24 Sep per web search, unverified) | Sep 17 verified | live | 0 |

Classification after reading: Al-Manar Sep 17, 18, 19 central; LBCI Sep 18 and
19 central, Sep 20, 21, 22, 24 mention; Al Jadeed Sep 19 central; MTV
compilation Sep 17 central. Later intros move to the Aqil assassination
(Sep 20) and the Sep 23 air campaign.

### Newspapers

| source | access in Sep 2026 | URL pattern | event-window evidence |
|---|---|---|---|
| Al-Akhbar | web: Cloudflare JS challenge (HTTP 403) for scripted clients. **Daily issue PDFs are open**: `media.al-akhbar.com/PDF_Files/<issue>/alakhbarYYYYMMDD.pdf`, issues 5297 (Sep 17) to 5303 (Sep 24) all HTTP 200, ~2.6 MB each | articles `al-akhbar.com/<Section>/<id>/<slug>`, IDs ~386,900 (Sep 17) to ~387,300 (Sep 25) | GDELT lists 130 Al-Akhbar URLs in the window, e.g. "مجزرة الـ«بايجر»: ترجيح فرضية التفخيخ" (Sep 18), "ما أشبه نهاية «كينغزمان» بهجوم الـ«بيجرز»" (Sep 18), and the Sep 20-21 front pages on "مجزرة البيجر". Wayback CDX for the domain timed out repeatedly; unverified |
| Nidaa al-Watan | web: Cloudflare challenge. Wayback holds 602 article URLs captured Sep 17-25, but the highest ID is 285,974 (June 2024 articles): **no event-window article is archived**. Not in GDELT or Media Cloud | `nidaalwatan.com/article/<id>-<slug>` | none verifiable; web search found only later retrospectives (IDs 346053, 397387). Needs a browser that passes the challenge, or the print edition |
| An-Nahar | **live, open** (HTTP 200 without challenge); body in `div.bodyText.bodyContentMainParent`, JSON-LD headline/description/datePublished; some pages carry premium markers | `annahar.com/arabic/news/<desk>/<region>/<id>/<slug>` (slug required: a wrong slug returns 404); IDs ~241,035 on Sep 17; a second ID space `/arabic/news/<section>/<id>` (~339,xxx) also exists | GDELT lists 108 URLs, 7 with device words in the headline (e.g. "ما هي أجهزة 'بايجر'؟", Sep 17); web search confirms Sep 17-19 event articles. Wayback holds ~12 in window. Best-accessible long-form source |
| L'Orient-Le Jour / L'Orient Today | live: Cloudflare challenge. **Wayback dense**: 4,790 LOLJ and 1,725 L'Orient Today article URLs captured Sep 17-25, 57 and 31 with device words in the slug | `lorientlejour.com/article/<id>/<slug>.html`, `today.lorientlejour.com/article/<id>/<slug>.html`; IDs 1,427,350 to 1,428,600 in window; paywall (`article.php?action=paywall` captures) | e.g. 1427424 "explosions de bipeurs... ce que l'on sait", 1427437 "Thousands across Lebanon injured in Hezbollah pager explosions" |

Indirect route to newspaper text: NNA's "صحف" digests and Al Jadeed's / MTV's
press-lead items republish long passages of Ad-Diyar, Al-Sharq, An-Nahar,
Al-Joumhouria and Al-Akhbar (examples in the gap manifest). They are a cheap
partial substitute, attributed to the paper, but selected by the TV channel or
NNA.

## 7. Corpus records that look wrong on second look

Listed only; nothing was changed.

| document_id | issue |
|---|---|
| lb_lbci_797960 | off-topic: "سماعات الأذن اللاسلكية قد تؤدي إلى فقدان السمع" (wireless earbuds and hearing loss), tagged `related` because of لاسلكية |
| lb_aljadeed_507118 | different topic and outside the window: Oct 6 Washington Post report on Israel intercepting Hezbollah radio traffic for nine years, not the device attack |
| lb_aljadeed_502815 / lb_aljadeed_502819 | near-duplicate pair, both primary: same Clemenceau walkie-talkie brief, one headline spelled "تفـ جير" |
| lb_aljadeed_502553 / lb_aljadeed_502564 | near-duplicate day-0 briefs ("اختراق أمني لاسلكي كبير..."), both primary |
| lb_mtv_1490054, lb_mtv_1490462 | no `published_at`; IDs and first captures place them on Sep 26-27 |
| lb_nna_722276, lb_nna_722542 | no `published_at` (content dates them to Sep 18 and 19); NNA dates sit in the first body line ("الثلاثاء 17 أيلول 2024 الساعة ...") |
| 11 Al-Manar martyr notices (12483066 to 12484254) | already flagged `martyr_notice_death_cause_unverified`; they name no device, so they are not "about the attack" on the page itself |
| lb_almanar press_review records | the 4 digests are in, but the Sep 19, 20, 21 "الصحافة اليوم" digests are not (Section 5) |

## 8. Open problems

- NNA has no usable reference; the API route is robots-disallowed and Wayback is
  nearly empty for the window.
- The lexical test undercounts euphemistic text (Al-Manar, Hezbollah and
  political statements that say "العدوان"). Only bulletin intros were read in
  full; other items rated "none" may still be about the attack.
- Independent discovery for LBCI/MTV/Al Jadeed rests on GDELT samples of 1 to
  13 relevant items. The census figures are sound for triage loss and for
  LBCI/Al Jadeed enumeration, weaker for MTV discovery (MTV's own sitemap is the
  denominator).
- Al-Manar's non-manifest article count rests on ~5 real articles in an 800-ID sample.
- Media Cloud returned zero window stories for every Lebanese source except
  Al-Manar; worth asking Media Cloud whether the TV sites were ingested in 2024
  under other source IDs or collections.
