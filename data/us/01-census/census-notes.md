# US outlet census — evidence notes (v1, 2026-09-05)

Companion to [outlet-census.csv](outlet-census.csv). Built per
[`01-outlet-census.md`](../../../docs/methodology/01-outlet-census.md).
Raw per-account social evidence: [social-counts/](social-counts/)
(three lookup groups, run on grok, copilot, and codex CLIs).

## Medium mix (step 1)

DNR US 2025 (fieldwork ~Jan–Feb 2025): any online 76%, TV ~50%, **social
media ~54% and rising (+6pp in one year, passing TV for the first time)**,
print 14%. News podcasts 15%, AI chatbots 7%. Platforms for news: Facebook
32%, YouTube 30%, X 23%, Instagram 16%, TikTok 12%, WhatsApp 10%. Trust 30%
(rank 39/48). 20% pay for online news.

The US sits between Germany (TV-and-brand-site country) and Lebanon
(social-first): social passed TV, but brand reach is still survey-measured
per outlet, so axes A and B carry roughly equal weight — and the US adds a
layer the other censuses didn't need: **personality/creator news** (DNR
measured it directly: Joe Rogan 22%, Tucker Carlson 14% weekly encounter).

## Evidence backbone

1. **DNR 2025 full report, US page (p. 119)** — per-brand weekly reach.
   Offline: Fox 32, CNN 28, local TV 27, ABC 19, CBS 19, BBC 16, NBC/MSNBC
   16, NYT 13, regional paper 12, USA Today 12, local radio ~12, NY Post 9,
   WSJ 9, WaPo 8, **Al Jazeera 7**, NPR 7. Online: CNN 23, Fox 22, **Yahoo
   News 18**, NYT 16, local TV sites 14, BBC 13, USA Today 12, WaPo 10, WSJ
   10, ABC 10, NBC/MSNBC 10, CBS 10, MSN 8, NY Post 8.
   [Full report PDF](https://reutersinstitute.politics.ox.ac.uk/sites/default/files/2025-06/Digital_News-Report_2025.pdf)
2. **Creator measures** — DNR 2025's post-inauguration-week encounter
   question (Rogan 22%, Carlson 14%; Kelly/Owens/Shapiro/Cohen/Pakman named
   without %). Caveat carried in rows: *encountered* ≠ deliberately used.
3. **Social counts** (2026-09-05): grok (TV networks), copilot (press),
   codex (creators/partisan/portals), all with handle verification.
   Platform denominators (DataReportal Jan 2025, ad-reach): Facebook 197M,
   Instagram 172M, YouTube 253M, TikTok 136M (18+), X 104M.

## US calibration of the tier rule

From the measured distribution (clear gaps at ~25M and ~5M aggregate):

- **Axis A strong:** current DNR weekly brand reach ≥10%; weak 3–10%.
  The DNR creator-encounter measure counts as axis-A-class (purpose-built
  survey) but its encounter-vs-use caveat caps any creator at one signal.
- **Axis B strong:** ≥25M aggregate; weak 5–25M; below 5M no signal.
  Substantial-via-B: ≥15M (verified counts only — self-reported and
  brand/personal-mixed aggregates are confidence-discounted, not credited
  upward).
- Portal and ban exceptions as in the Germany/Lebanon rules.

Resulting tiers: **mass (8)** Fox, CNN, ABC, CBS, NBC, NYT, WaPo, Yahoo
News (portal exception, flagged) · **substantial (10)** MS NOW (flagged),
USA Today, WSJ (flagged), BBC, NPR, NY Post, Rogan, Daily Wire/Shapiro,
Tucker Carlson, MeidasTouch · **niche** Newsmax, OAN, Breaking Points, PBS,
LA Times, Axios, Al Jazeera English · **context** AP, Reuters, local-TV
category, regional-newspaper category.

## Structural findings

1. **The market is bifurcated and the census encodes it.** Fox (#1 offline,
   43/40 trust/distrust split) against CNN/legacy networks; a creator layer
   that over-indexes right, young, and low-trust audiences (DNR); and a
   left creator counterweight (MeidasTouch — #1 YouTube podcast chart, out-
   subscribing PBS's entire footprint on YouTube alone). Framing analysis
   should expect the US *within-country* spectrum to be as wide as some
   cross-country comparisons.
2. **The creator layer is census-relevant for this event.** 15% weekly
   podcast news use, Rogan at 22% encounter. For the pager attack these
   sources carried distinct framings (long-form interviews, conspiracy
   adjacency) that no legacy panel captures. First census where the
   creator/podcast layer earns tier rows.
3. **Third portal case:** Yahoo News, 18% online reach with near-zero brand
   social. Portal exception granted (single-source, flagged for review);
   MSN excluded as a non-editorial aggregator (8% reach documented in the
   exclusion note), consistent with Germany.
4. **International brands are measured and real:** BBC 16%/13% (substantial
   on one strong signal), Al Jazeera English 7% (niche) — both
   survey-measured in the US, unlike in the Lebanon census where AJ remains
   the unresolved freeze blocker. The US census cannot resolve Lebanon's AJ
   row, but it demonstrates the measurement is possible where the survey
   frame includes the brand.
5. **The NBC/MSNBC joint measurement** is the US's brand-attribution trap
   (Lebanon had MOM editions; Germany had chart cutoffs): DNR measures them
   as one item, but they are separate companies since the Versant spinoff
   and MSNBC rebranded to MS NOW (Nov 2025). Rows are split with the
   caveat documented on both.
6. **Wire visibility inverts the German pattern:** AP and Reuters are
   consumer brands in the US (Reuters 11.2M Facebook) yet play the same
   upstream-baseline role; both stay `context` for comparability with dpa,
   with a note that apnews.com/reuters.com are also collectable
   consumer-facing surfaces.

## Inclusion/exclusion decisions

| entry | decision | reason |
| --- | --- | --- |
| MSN News (8% DNR online) | exclude | aggregator without newsroom (Germany precedent); documented here |
| Google News / Apple News | exclude | aggregators; Apple News carries licensed content only |
| Local TV news (27% category) | context, no representative | foreign news on local TV is network/wire-syndicated — covered via network + AP rows (differs from Germany's RND decision because US locals do not run a shared original-reporting network for foreign news) |
| Regional/local papers (12%) | context, no representative | foreign coverage predominantly AP; Gannett network carried by USA Today row |
| CNN en Español, CNNBRK, ABC Australia, Fox Business, show-level accounts (Maddow etc.) | excluded from counts | sister/vertical accounts; flagship news brand accounts only |
| Spanish-language US media (Univision, Telemundo) | **GAP — not yet assessed** | see gaps below |

## Known gaps for round 2

1. **Spanish-language media** — Univision and Telemundo have mass-scale US
   audiences and are absent from the DNR chart shown; this is the US
   equivalent of Germany's diaspora blind spot but *measurable* (Nielsen
   rates them). Must be assessed before freeze — likely at least one
   substantial row.
2. WSJ X/YouTube counts (candidate mass); NYT/WaPo YT/TikTok are SocialBlade
   estimates — verify live.
3. Yahoo News corroboration (Comscore top-news-property ranking) for the
   portal exception.
4. Rogan YouTube count (PowerfulJRE) and a decision on brand-vs-personality
   account accounting for the creator rows (Daily Wire vs Shapiro personal).
5. DNR 2024 US page (pre-event vintage) — same vintage policy as Germany.
6. Podcast layer beyond named creators: The Daily (NYT), NPR podcasts —
   probably folded into their parent rows; document.
7. Local TV: revisit only if diaspora-community framing (Arabic-language US
   stations) becomes analytically relevant.

## v1.1 amendments (post-review-1, applied in place with this changelog)

Review 1 ran on grok CLI with live web verification (archived:
[01-census-review-grok-2026-09-05.md](../reviews/01-census-review-grok-2026-09-05.md)).
All 11 required citation checks came back accurate; the tier derivations
were confirmed mechanically sound on gathered evidence. Verdict: not
freezable — blocked by the Spanish-language gap plus vintage and
creator-consistency findings, all now applied:

| finding | action |
| --- | --- |
| **DNR 2024 (event-period) chart not applied** — reviewer extracted p.115: Fox 27/18, CNN 23/17, Yahoo 16, **Newsmax 8/8**, AJ absent | Vintage policy adopted (2024 = event baseline, 2025 = post-event sensitivity — the 2025 Fox/CNN numbers are a post-inauguration bump). No mass row flips. **Newsmax re-tiered niche → substantial** (2024 axis A weak + Pew 8% corroboration); Al Jazeera marked 2025-only |
| Creator graph p.13 has printed values v1 treated as missing (Kelly 14, Owens 13, Shapiro 12, Pakman 7) | **Megyn Kelly and Candace Owens rows added (substantial)** — identical evidence to Carlson must yield identical tiers; Shapiro's 12% cited on the Daily Wire row; Pakman below bar, skipped |
| Transcription errors: NY Post 9/8→8/7, WSJ offline 9→8, local radio 12→10 | corrected |
| Yahoo portal exception single-source flag | retired — ≥15% in two vintages (16% 2024, 18% 2025) |
| Local radio (10-12% category) had no row | context category row added; Hannity/Levin documented as show-level fold, Talkers figures not credited |
| USA Today / WSJ YouTube marked "not found" but on SocialBlade's public US-news list (7.55M / 6.68M) | added as verify-live values; **USA Today = candidate mass** if its YT verifies |
| Newsmax IR discount | confirmed correct by reviewer (25M headline includes Truth Social/Gettr; mainstream ~15M matches) |
| Weather Channel, Substack (platform) | excluded with reasons (below); HuffPost optional niche, not freeze-relevant |

Additional exclusions: The Weather Channel (incidental news, not a
foreign-news newsroom — sports-network logic); Substack (a platform, not an
outlet — Google News analogue; The Free Press awaits a named encounter % or
second signal); MS NOW/NBC joint-measure caveat unchanged (reviewer:
"follows, with caveat").

**Tier summary after v1.1:** mass (9): Fox, CNN, ABC, CBS, NBC, NYT, WaPo,
Yahoo News, **USA Today** (promoted after its 7.55M YouTube count was
live-verified 2026-09-05, closing the review's candidate-mass route) ·
substantial (12): MS NOW, WSJ, BBC, NPR, NY Post, Rogan, Daily Wire,
Carlson, MeidasTouch, Newsmax, Megyn Kelly, Candace Owens · niche: OAN,
Breaking Points, PBS, LA Times, Axios, Al Jazeera English (2025-only) ·
context: AP, Reuters, local TV, local radio, regional papers.

## Freeze blockers

1. ~~Spanish-language media~~ **CLOSED (2026-09-05):** N+ Univision
   (Noticias Univision) and Noticias Telemundo added as **substantial**
   rows. Evidence: Nielsen 2024 (Univision 1.2M / Telemundo 957K average
   evening-news viewers; Univision #1 among US Hispanics 32 years running),
   Pew Mar 2024 (event-adjacent: 24% of Latinos prefer news in Spanish;
   these two are the key providers), social aggregates ~38-39M each but
   cross-border-discounted (Spanish-language accounts serve Latin America
   too; Telemundo's 17.7M TikTok is the largest single-platform count of
   any US news brand outside CNN/ABC). Documented subpopulation-dominance
   note: national tiers understate their importance for diaspora framing.
   **Step-2 alert found by the lookup: Noticias Univision rebranded to
   N+ Univision in Jan 2026 — event-era URLs/handles are legacy; archive
   routes must target the 2024 branding.**
2. ~~USA Today mass-vs-substantial~~ **CLOSED**: @USATODAY YouTube
   live-verified at 7.55M → aggregate ~27.5M verified → mass.

**Census status: FROZEN (v1.2, 2026-09-05).** Both blockers closed;
remaining round-2 items below are non-blocking refinements.
3. Round-2, non-blocking: WSJ X/YT live counts, Kelly/Owens/Rogan social
   columns, Young Turks assessment (6.71M YT, left analogue of Daily Wire),
   NYT/WaPo YT/TikTok live verification (SocialBlade estimates acceptable
   per reviewer for those two rows only).
