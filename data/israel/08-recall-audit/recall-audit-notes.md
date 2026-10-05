# Israel recall audit (v1, 2026-10-04)

Scope: the five Israeli collection-gate rows (Ynet, N12, Kikar HaShabbat,
Makan, Abu Ali Express) for the audit window Sep 17 to Sep 24 2024 (Israel
dates). Question: of the items each outlet published in the window that mention
the pager or walkie-talkie attacks, how many are in `corpus.jsonl` (primary
records), and why are the others missing?

Files in this directory:

- `reference-set.csv`: 380 verified in-window items that mention the attacks,
  with discovery route, central/mention class, pipeline status and matched
  `document_id`.
- `gap-manifest.csv`: 309 missing items with a working collection route (live
  URL, Wayback capture timestamp, or live `t.me/s` for Abu Ali).
- `raw/`: fetched HTML per outlet, GDELT extract (`gdelt-gkg-hits.csv`), Abu
  Ali live message dump (`abuali-live-messages.csv`, 872 messages Sep 16-25),
  N12 ticker probe (`n12-ticker/`), Kikar homepage probe, CDX lists for Ynet
  sections, task lists, worker outputs, `items.json`, `review-queue.csv`,
  `census-summary.json`, `recall-tables.json`.
- Scripts: `pipeline/08-recall-audit/recall_audit_il_lb_*.py`.

Nothing in the existing corpus, manifests or notes was changed. The Lebanon
notes (`data/lebanon/08-recall-audit/recall-audit-notes.md`) describe the shared
method in more detail; the summary below covers what differs for Israel.

## 1. Method

### Relevance test

Container-first body extraction (JSON-LD `articleBody` for Ynet and mako, the
article container for Kikar and Makan), then a lexical test on headline + body:
strong terms (ביפר*, איתורית/איתוריות, זימונית/זימוניות, ווקי טוקי, גולד אפולו,
איקום; Arabic بيجر/بايجر/أجهزة النداء/ووكي توكي for Makan) count anywhere; weak
terms (מכשירי (ה)קשר, מכשירי (ה)רדיו, המכשירים שהתפוצצו, מתקפת המכשירים; Arabic
لاسلكي / أجهزة الاتصال) count only next to a blast word (פיצוץ, התפוצץ, נפץ...).
Hits within 80 characters count once. **central** = device term in the headline,
or three or more separate body mentions, or a lead mention in an item under
120 words. **mention** = any other substantive body mention. For Abu Ali
posts: central if the device term is in the first 160 characters.

A random sample of 40 missing items was read: all 40 mention the attacks; about
4 of 40 are borderline central/mention. Ynet's habit of contextual leads ("על
רקע פיצוצי הביפרים...") was the reason the lead rule is limited to short items.

### Discovery routes and their independence

| route | what it is | independent? | coverage |
|---|---|---|---|
| `gdelt` | GDELT 2.0 GKG, 1,728 15-min files Sep 17-25 UTC, domain filter | yes | Ynet 1,032 URLs (519 `/news/article/`, 109 Yedioth print `yokra`, ~400 in other sections), mako 677 (of which 114 N12-relevant paths: 108 under `pzm-soldiers`, a mako channel that mirrors N12 news articles under the same `Article-<hex>` IDs), Kikar 190, **Makan 0** |
| `abuali-live` | live `t.me/s/abualiexpress?before=<id>` paging, IDs 75,543 to 76,640 | yes (live Telegram, not Wayback) | 872 messages, complete for the window |
| `websearch` | codex web search for event articles per outlet | yes | Ynet 10, N12 8, Kikar 10 URLs; Makan: none found |
| `cdx-section` | Wayback CDX for Ynet prefixes the manifest excluded: `news/article/yokra` (532 URLs), `economy/article` (932), `digital/article` (35), captured Sep 17-Oct 1 | partly (same archive, different enumeration) | all 1,368 fetched live |
| `manifest-kw` | every untagged manifest item first captured Sep 17-Oct 1 whose title has a Hezbollah/Lebanon/escalation keyword | no (same manifest), tests triage | Ynet 2,441, Kikar 314, N12 214 (176 checked), Makan 88 |
| `manifest-untitled` | N12 manifest items whose sweep title was a Radware block page or empty | no, tests triage | 602 recent-ID items; random 70 checked via Wayback |
| `control` | random untagged, no-keyword items | no, leakage estimate | Ynet 0/191, Kikar 0/143 relevant; none for N12 and Makan (Wayback throughput) |

Media Cloud: the Israeli sources exist (ynet.co.il 41696, mako.co.il 107636,
n12.co.il 1435449, kikar.co.il 830873, kan.org.il 711507, makan.org.il 895410)
but return **zero stories** for Sep 17-24 2024 even for "ישראל" / "لبنان". No
Media Cloud route for Israel.

Wayback throughput was the binding constraint: archive.org repeatedly refused
connections (shared with the parallel Germany/US audit), so the N12 and Makan
strata are samples, not censuses.

### Matching

URLs were normalised to outlet IDs: `ynet:<id>` across sections (IDs are
case-sensitive on the live site, matched case-insensitively), `n12:<hex>` for
any mako path (collapses `news-*` vs `pzm-soldiers` vs `?utm` variants),
`kikar:<shortid>` regardless of section slug (Hebrew section paths included),
`makan:<id>`, `abuali:t.me/abualiexpress/<id>`. Fuzzy headline matching was the
fallback; it changed no status.

## 2. Per-outlet recall

Census recall (corpus records in window / (corpus + missing found +
extrapolated from sampled strata)):

| outlet | corpus central | corpus mention | missing central | missing mention | extrapolated | recall central | recall mention | recall all |
|---|---|---|---|---|---|---|---|---|
| Ynet | 86 | 0 | 72 | 55 | 0 | 54% | 0% | 40% |
| N12 | 7 | 0 | 25 | 25 | ~72 (CI ~30-135) | 22% | 0% | ~5% |
| Kikar | 17 | 0 | 5 | 23 | 0 | 77% | 0% | 38% |
| Makan | 9 | 0 | 1 | 5 | 0 | 90% | 0% | ~58% (**no independent reference**) |
| Abu Ali | 16 | 1 | 85 | 13 | 0 | 16% | 7% | 15% |

Independent-route recall (share of each route's relevant items already in
the corpus):

| outlet | route | central found / in corpus | mention found / in corpus |
|---|---|---|---|
| Ynet | gdelt | 68 / 35 (51%) | 54 / 0 |
| Ynet | websearch | 10 / 6 | 0 / 0 |
| Ynet | cdx-section (yokra, economy, digital) | 5 / 0 | 12 / 0 |
| N12 | gdelt | 16 / 3 (19%) | 17 / 0 |
| N12 | websearch | 6 / 3 | 0 / 0 |
| Kikar | gdelt | 16 / 12 (75%) | 18 / 0 |
| Kikar | websearch | 7 / 5 | 1 / 0 |
| Abu Ali | abuali-live | 103 / 18 | 14 / 1 (corpus posts without a device word are outside this reference) |

Reading the numbers:

- **Mentions-only coverage is zero for every Israeli outlet.** The title sweep
  only picks headlines with device words. Ynet alone has 55 missing
  mention items and 63 missing central items whose headlines are about
  Nasrallah, Gallant's "new phase", the northern front, Hezbollah's response,
  op-eds and Yedioth analyses.
- **N12 is the weakest row and its suspicion is confirmed.** The corpus holds 7
  in-window N12 items. Three separate failures stack: (a) 1,152 of 4,506 N12
  manifest URLs were never title-checked because the live sweep got a Radware
  block page (1,005) or an empty title (147); of a random 70 rechecked, 7 are
  relevant, which scales to ~70 more items; (b) Wayback misses 35% of the N12
  URLs GDELT saw (40 of 114); (c) headline-only triage. The 13 N12-relevant
  items found only under `mako.co.il/pzm-soldiers/` are N12 news articles
  mirrored there, not a different outlet.
- **Ynet's enumeration is good for `/news/article/` (GDELT: 3% of URLs not in the
  manifest) but excluded Yedioth's print edition and non-news sections.** The
  manifest regex `[a-z0-9]{5,12}` drops the 13-character `yokra<digits>` IDs, and
  the prefix drops `economy/`, `digital/`, `health/`, `judaism/`... Of 58
  in-window yokra pieces fetched, 14 mention the attacks (5 central), e.g. "הלם
  קו: חיזבאללה אוסף את השברים" (1,711 words), "חיזבאללה ביום שאחרי: ארגון פצוע
  וחבול", "המשמעות של פגיעה באלפי פעילי חיזבאללה בו-זמנית היא הכרזת מלחמה". The
  live yokra pages carry full text (median 681 words), not paywall leads.
  Economy: 3 mentions among 107 in-window pieces.
- **Kikar** is close to complete for central items (77%, GDELT 75%) and
  misses the weekly roundups and security-news pieces that mention the attacks.
  One central item, the access-register test article
  `security-news/sjyy9g` ("500 מחבלים איבדו את הראיה..."), is in the manifest
  but untagged: its headline has no device word.
- **Makan: no independent reference could be built.** GDELT, Media Cloud and web
  search return nothing for makan.org.il; Cloudflare blocks the live site. The
  figure above only tests triage inside the Wayback manifest (88 keyword titles,
  13 untitled). The manifest itself (647 URLs for 33 days, ~20 a day) is likely a
  fraction of Makan's output; its size is unknown.
- **Abu Ali: the archived capture stream holds 21% of the window's messages**
  (163 of 761 for Sep 17-24; zero captures for Sep 19, 20 and 21). The live
  channel has 117 device-term posts in the window (about 20 are reposts of the
  same text with a photo), the corpus 17. Corpus Abu Ali posts without a device
  word (the v1.2 gloat-stream additions) are outside this reference by design.

## 3. Miss reasons

| reason | Ynet | N12 | Kikar | Makan | Abu Ali |
|---|---|---|---|---|---|
| triage: no device word in headline (body mention) | 101 (63 central) | 22 (9 central) | 27 (4 central) | 6 | |
| triage: sweep title was a Radware block page or empty | | 15 seen (+~70 est.) | | | |
| triage: device word in headline but the swept title differed | 3 | | | | |
| enumeration: Yedioth print `yokra` IDs excluded by regex | 14 | | | | |
| enumeration: outside `/news/article/` (sections) | 9 | | | | |
| enumeration: mako path outside `news-*` / not captured | | 13 | 1 | | |
| capture gap: Telegram message never archived | | | | | 85 |
| in archived stream, not tagged by the pipeline term list | | | | | 13 |

Headline drift: Ynet's `<title>` (what the sweep read) and its JSON-LD headline
differ on many items; e.g. `skb00cdtt0` was swept as "ועכשיו - בולגריה: נורטה
גלובל, החברה המסתורית החדשה בפרשת הפיצוצים" while the article headline reads
"...בפרשת פיצוצי הביפרים". Sweeping the JSON-LD headline would have caught it.

## 4. Live tickers and format gaps

| outlet | ticker | status |
|---|---|---|
| Ynet | מבזקים are ordinary `/news/article/<id>` items | in the manifest; flashes are in the corpus (`flash_or_lead`). No gap |
| N12 | the AJAX endpoint `mako.co.il/AjaxPage?jspName=smartMessages.jsp&count=100&page=1&topic=1` or `topic=2` (message bodies) plus `...&type=index&topic=1` or `2` (message ID lists). Wayback holds 117 captures of these URLs for Sep 17-24 (list in `raw/n12-ticker/smartMessages-captures-cdx.txt`) | **inaccessible as text**: the body payload is base64 of high-entropy bytes (encrypted or obfuscated), decoded client-side. The index variant is plain JSON: sequential message IDs (~1,068,000 on Sep 17 07:45 UTC, 100 per capture), so the ticker's volume is measurable even though its text is not. Decoding needs the mako client JS or a headless render of an archived page |
| Kikar | `kikar.co.il/scoop-news/<id>` | **inaccessible**: 2024 flash IDs (~399,000-409,000) return 404 on the live site (IDs were renumbered; current ~86,000), Wayback holds one `/scoop-news` page capture in the window, and the homepage captures (every 15-30 min) do not embed the flash list (client-loaded) |
| Makan | none found (codex: no addressable ticker or live blog) | unverified |
| Abu Ali | the channel itself | covered live, see above |

## 5. Systematic gaps and fixes

1. **Headline-only triage.** Fix: body-level triage for every in-window URL,
   with the two-tier term list. For Ynet use JSON-LD `headline` + `articleBody`
   (served on live pages; ~4,900 Ynet pages were fetched live during this audit
   without blocks).
2. **N12 sweep never saw 25% of its manifest.** Rerun the N12 sweep through
   Wayback only (the live mako CDN blocks scripted clients with Radware), and
   treat "Radware Block Page" as a fetch failure, not a title.
3. **N12 enumeration.** Add `mako.co.il/pzm-soldiers/Article-*` to the CDX
   enumeration (same hex IDs, collapse by ID), and use GDELT's mako list as a
   second source; 35% of N12 URLs GDELT saw are not in Wayback.
4. **Ynet URL scope.** Allow 13-character `yokra\d+` IDs and enumerate
   `economy/`, `digital/`, `health/`, `judaism/` article prefixes; Yedioth
   print analyses are the closest thing Ynet has to long-form on the event.
5. **Abu Ali.** Replace the 65-capture stream with live `t.me/s/abualiexpress?before=`
   paging (one request per ~20 messages; 55 requests covered Sep 16-25), dedupe
   reposts by text. This also moves the first-pager-post timestamp (Section 7).
6. **Makan.** Find any non-Wayback list of Makan URLs (Kan's sitemap, or a
   browser session past Cloudflare) before drawing conclusions from Makan absences.

## 6. Gap manifest

`gap-manifest.csv`: 309 items, all fetched successfully during the audit.

| outlet | central | mention | route |
|---|---|---|---|
| Ynet | 72 | 55 | live |
| Abu Ali | 85 | 13 | live t.me/s (no Wayback capture exists for 85) |
| N12 | 25 | 25 | Wayback (capture timestamp in file) |
| Kikar | 5 | 23 | live |
| Makan | 1 | 5 | Wayback |

## 7. Corpus records that look wrong on second look

Listed only; nothing was changed.

| document_id | issue |
|---|---|
| il_ynet_35be01752a | different event: Sep 23 report that Israel hacked radio stations and phoned Lebanese residents (evacuation calls), not the device attack |
| il_n12_ae690238dc | mis-typed: "״אחד ביום״: מתקפת הביפרים בלבנון" is a podcast page (8 words), typed `article` |
| il_n12_42fc90d847 | no `published_at` ("הפרשנים: השאלות הגדולות אחרי מבצע פיצוץ הביפרים", 920 words) |
| il_abuali_75669 | probably a separate incident: Saberin report of an explosive charge in a car in Damascus; no device named |
| il_abuali_75657, il_abuali_75668 | 3-word and 2-word captions ("פינוי הנפגעים בביירות.", "אחד נוסף.") that only make sense with their video; fine to keep, but they inflate post counts |
| Abu Ali first-post timing | the corpus' first pager post is 75657 (13:06 UTC) or 75663 (13:19). The live channel shows **75653 at 12:57:18 UTC** ("ראשוני: ... מכשירי זימונית של פעילי חזבאללה התפוצצו בהפעלה מרחוק"), reposted as 75655 (13:02) and 75656 (13:03). It predates N12's 12:59 item. The "N12 beat Abu Ali" finding in the v1.2 notes rests on the capture gap and should be revisited |

## 8. Open problems

- Makan has no independent reference, and Makan's real output volume is unknown.
- N12's untitled-stratum extrapolation rests on 7 relevant of 53 random checks
  (95% CI roughly 5%-25%).
- No N12 or Makan control sample (non-keyword titles) could be checked; Ynet
  (0/191) and Kikar (0/143) suggest leakage there is small.
- N12 ticker payload not decoded; Kikar 2024 flashes appear to be lost.
- The lexical test misses euphemistic or allusive text ("המבצע בלבנון", "המכה");
  everything is a lower bound on what readers saw.
- GDELT is the only independent route for Ynet, N12 and Kikar; it crawls
  mostly news pages, so section and print items are under-sampled in it.
