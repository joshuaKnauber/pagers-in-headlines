# Lebanon outlet census — evidence notes (v2, 2026-09-05)

Companion to [outlet-census.csv](outlet-census.csv). v2 incorporates the
independent review of v1 (all findings addressed — see the corrections ledger
at the bottom) and adds the social-reach evidence column gathered 2026-09-05.

## Tier rule (v2.1 — amended after review 2 resolved ambiguities)

Evidence is grouped into **axes**; each axis contributes **at most one
signal** (use the strongest item on it; two vintages of the same measurement
are one signal):

- **Axis A — measured audience share** (purpose-built measurement, e.g.
  ELKA). Strong: current (≤3y) share ≥10% of the dominant news medium (TV),
  or current top-4 membership in that medium where the concentration data
  implies an individual share ≥10%. Weak: dated ≥10% share; current 3–10%;
  any share or top-4 standing in a **minor medium** (penetration <50%:
  print 28%, radio 35% — the discount is part of the rule).
- **Axis B — social footprint**: the aggregate follower count across
  verified official accounts on all platforms (a diaspora-inflated upper
  bound). Strong: ≥2M aggregate. Weak: 500K–2M. Below 500K: no signal.
  Region-wide counts of pan-national outlets are **not** an axis-B signal.
- **Axis C — digital consumption ranking** (search-proxy, Ahrefs-class):
  weak only; top-10.
- **Axis D — third-party documented reach** (institutional audits, e.g.
  IFPIM): weak only.

Tiers:

- **mass** = 2 strong signals. *Ban exception:* if platform bans void axis B
  (Al-Manar: Meta/Google bans persist), one current axis-A strong signal
  suffices, documented per row and re-evaluated each round.
- **substantial** = 1 strong, or ≥2 weak, or axis-B aggregate ≥750K.
- **niche** = measured on ≥1 axis, below the substantial bar. For
  minor-medium outlets (print/radio), an ungathered axis B does not block a
  niche tier — it can only revise the tier upward when gathered.
- **context** = role-based inclusion regardless of audience (state agency).
- **unresolved** = a plausibly decisive axis is unmeasured, i.e. the tier
  could change when that evidence is gathered. Any unresolved candidate-mass
  row **blocks the country freeze** (no-cop-out rule).

Resulting tiers: **mass** LBCI, MTV, Al-Jadeed, Al-Manar (ban exception) ·
**substantial** OTV, Annahar, Al-Akhbar, Elnashra, Lebanon24, Megaphone ·
**unresolved** Al Jazeera (candidate mass — freeze-blocking), Al Mayadeen,
Al Arabiya, Sky News Arabia, BBC, Addiyar, 961today.com · everything else
niche/context.

## Structural findings

1. **Social passed TV as the primary breaking-news source.** Arab Barometer
   Wave VIII (fieldwork Feb 12 – Apr 2, 2024): 53% social media vs 31% TV
   (+14 / −18 points vs 2022); 75% of 18–29-year-olds social-first, 53% of
   50+ TV-first. WhatsApp usage 96%, Facebook 82%.
   [AB8 Lebanon report](https://www.arabbarometer.org/wp-content/uploads/AB8-Lebanon-Country-Report-EN.pdf)
2. **Diaspora inflation of social counts.** DataReportal Digital 2025
   Lebanon: population 5.83M, Facebook users 3.15M, Instagram 2.50M, YouTube
   3.19M. MTV's 19M Facebook followers is ~6× the national Facebook base —
   domestic outlets' followings are substantially diaspora/regional. Social
   counts are therefore upper-bound proxies, never in-country reach.
3. **The TV time series (not a conflict).** Ipsos/Vertical Media 2018 vs
   ELKA 2024: LBCI 25.8% → 13%; top-4 changed from LBCI/Al-Jadeed/MTV/OTV
   (78.1%) to LBCI/MTV/Al-Jadeed/Al-Manar (~80%, top-3 ≈ 69%). Al-Manar rose
   6.4% → 11%; OTV fell out. Per-outlet 2024 numbers for MTV and Al-Jadeed
   are still unpublished on the MOM pages fetched.
   [2018 edition](https://lebanon-2018.mom-gmr.org/en/findings/findings/) ·
   [2024 edition](https://lebanon.mom-gmr.org/en/findings/findings/)
4. **Al-Manar's reach is invisible to platform metrics.** Banned from
   YouTube/Instagram (2021), repeated Facebook removals, US domain seizure;
   distributes via Telegram (~200K), WhatsApp phone-broadcast (no public
   count), X (returned Sep 2024). Its 11% ELKA share is the only valid
   reach measure; its social column must never be read as audience size.
5. **Print collapsed and reshuffled.** 72% read no print (ELKA 2024); the
   top-4 changed between editions (Al Joumhouria led 2018 at 22.4%, out of
   top-4 by 2024; L'Orient-Le Jour entered). Print matters to the corpus for
   text/page preservation, not reach.
6. **Digital natives out-reach legacy papers on social** (Lebanon24 828K,
   Elnashra 539K, LebanonFiles 482K, Megaphone 478K IG vs Al Joumhouria 93K,
   Nidaa Al Watan 99K) — while the state agency NNA is negligible (25K).
7. **WhatsApp channels are real distribution** (96% usage): Annahar 313K,
   The961 News 338K, Al Jazeera 1.2M (region-wide). Round 2 should complete
   this column; several outlets use Telegram instead (Al-Akhbar, Al-Manar).

## Pan-Arab outlets: the open question

Digital proxies put Al Jazeera #1 and Al Mayadeen #2 among news sites
consumed in Lebanon (Ahrefs organic-search, Aug 2026), but no
Lebanon-specific TV viewership measurement was found in two passes: NU-Q
asked per-channel viewership only in 2017 (interactive broken; 2019 wave is
platform-level only), and pan-Arab channels are absent from the Ipsos/ArabAd
2021 Lebanese nightly-news top-15 — weak evidence that domestic channels
dominate TV news while pan-Arab consumption is digital-side. All pan-Arab
rows stay `unresolved`; Al Jazeera is candidate-mass and freeze-blocking.
Resolution routes: NU-Q 2017 country tables via Wayback; Ipsos pan-Arab
measurement; MOM Lebanon 2024 full report.

## Inclusion/exclusion rule for foreign entries in digital rankings

Rule: a foreign outlet gets a census row when it (a) appears in a Lebanon
consumption ranking and (b) operates a news service plausibly consumed *as
news* by Lebanese audiences. Applied to the Ahrefs Lebanon news top-12:

| entry | decision | reason |
| --- | --- | --- |
| aljazeera.net (#1), almayadeen.net (#2), bbc.com (#6) | row | news services with Lebanese audience |
| yahoo.com (#4) | exclude | portal traffic, not a news operation targeting Lebanon |
| youm7.com (#5) | exclude | Egyptian domestic tabloid; no Lebanon service; likely geo-attribution noise |
| nytimes.com (#7) | exclude | English international; no Lebanon-specific evidence beyond this proxy; revisit if second signal appears |
| maariv.co.il (#10) | exclude | Israeli domestic daily ranking in Lebanon is implausible — treated as evidence the proxy's geo-attribution is noisy |
| sp-today.com (#11) | exclude | currency-rate site miscategorized as news |

The two implausible entries (maariv, sp-today) are why Ahrefs rank counts
only as a weak signal.

## Social-reach data quality

Gathered 2026-09-05 by four parallel lookups. YouTube/TikTok/WhatsApp counts
are live page fetches (most reliable); Facebook/Instagram counts are
Google-indexed snippets of the pages' own counters (may lag; FB figures mix
"likes" and "followers"). Weakest number: Elnashra Instagram (undated
third-party crawl). Impostor/squatted accounts were detected and avoided for
LBCI, OTV, Al-Jadeed, L'Orient-Le Jour, Al Joumhouria, and Lebanon Debate
(details in CSV notes) — treat any unverified handle as suspect by default.
Counts are a 2026 snapshot, ~2 years after the event window.

## Gaps for round 3

1. Per-outlet ELKA 2024 shares for MTV and Al-Jadeed — MOM Lebanon 2024 full
   report ([country page](https://www.mom-gmr.org/en/countries/lebanon/lebanon/))
   or ELKA directly.
2. Lebanon-specific pan-Arab TV viewership (freeze-blocking for Al Jazeera).
3. Addiyar publication-status check + social counts; 961today.com social
   counts; NNA Instagram count.
3b. Al-Akhbar Facebook page verification (review-2 flag): a newer 145K page
   (recent-format page ID) self-describes as "the official page" — confirm
   whether the 2.09M AlakhbarNews page is current or legacy/migrated.
4. X/Twitter and Telegram columns (only spot values held: Al Joumhouria X
   ~245K, NBN X ~75K, Al-Manar Telegram ~200K, Al-Akhbar Telegram uncounted).
5. Better digital proxy than Ahrefs: SimilarWeb 2024 snapshots via Wayback;
   Cloudflare Radar country domain rankings (historical to 2023).
6. WhatsApp-channel sweep for all rows (96% usage makes this the single most
   Lebanon-relevant social metric).

## Corrections ledger (review 1 → v2)

| finding | action |
| --- | --- |
| 25.8%/78.1% misattributed to ELKA 2024 (actually MOM 2018, Ipsos/Vertical Media) | fixed; recorded as 2018→2024 time series |
| ELKA 2024 per-outlet figures (LBC 13%, Al-Manar 11%) "unavailable" though on page | recorded |
| OTV top-4 membership attributed to 2024 (was 2018) | fixed; OTV out of 2024 top-4, tier substantial |
| Al-Jadeed "most-watched bulletin 2021" unsupported | corrected to #3 (MTV #1, LBCI #2, ArabAd/Ipsos Jun 2021) |
| BBC "#8 all sites mid-2025" unverifiable (actual ~#59) | removed |
| AB8 fieldwork "2023–24" | corrected to Feb 12 – Apr 2, 2024 |
| Annahar 16%-of-print figure missed | added |
| Evidence-free tiers (Tele Liban, Addiyar, Megaphone "niche by design") | Tele Liban/NBN now evidence-based niche (social measured); Addiyar → unresolved; Megaphone → substantial |
| Al Jazeera mass on single Ahrefs point; no mass/substantial criterion | explicit tier rule added; Al Jazeera → unresolved (candidate mass, freeze-blocking) |
| Al-Manar "high" confidence inconsistent with definition | → medium; ban exception documented instead |
| Missing rows: Sky News Arabia, Sawt El Shaab, Lebanon Debate, LebanonFiles | added (+ Voix du Liban, 961today.com) |
| Ahrefs foreign entries admitted inconsistently | explicit inclusion/exclusion rule + table above |
| Megaphone "1M+ Instagram" (review's own reading) | corrected: IFPIM figure is cross-platform aggregate; IG is 478K |
| "961Today" row conflated the961.com with 961today.com | split into two rows (found in social-gathering pass) |

## v2.1 amendments (post-review-2, applied in place with this changelog)

Review 2 (scoped: social-count verification, mechanical tier audit,
regression check) found the **data clean** — 13/14 spot-checked social counts
confirmed on the correct official accounts, zero impostor accounts admitted,
15/15 review-1 ledger entries landed — but found the tier-rule *text*
ambiguous enough to permit contradictory derivations (platform stacking
undefined; minor-medium discount unstated; niche/unresolved boundary
undefined). Amendments:

| review-2 finding | action |
| --- | --- |
| Rule silent on whether multiple platform accounts stack as signals (OTV vs Megaphone contradiction) | Rule restated as axes: one signal per axis; axis B is the cross-platform aggregate. All rationales re-derived; **no tier changed** |
| Minor-medium discount applied but not written (Annahar would be mass as written) | Discount written into axis A definition |
| niche/unresolved boundary undefined | Defined: unresolved = a plausibly decisive axis unmeasured; minor-medium rows exempt from B-blocking |
| MTV YouTube "4M" vs tracker ~3.83M | Corrected to ~3.83M (tracker-checked) |
| Al-Manar ban exception softened by X return (261K since Sep 2024) | Exception retained (Meta/Google bans persist) with explicit re-evaluation trigger in the row |
| Al-Akhbar possible FB page migration (newer 145K "official" page) | Added to round-3 gaps (3b) |

Verdict after amendments: every tier in the CSV is now mechanically derived
from the stated rule (re-derivation checked row by row), with the derivation
quoted in `tier_rationale`. **v2.1 is freezable** pending the documented
round-3 gaps, with Al Jazeera's unresolved candidate-mass status the sole
freeze blocker.

## v2.2 amendment: Al Jazeera blocker resolved (2026-09-05, approved)

The candidate-mass hypothesis rested on a single weak signal (Ahrefs #1,
organic-search-only, documented geo-noise). A dedicated resolution pass
could not recover the direct measurement — NU-Q asked per-channel weekly
viewership in 2017 but published only regional values (Al Jazeera 39%
region-wide); the Lebanon cell sits in unpublished raw data. Instead, four
independent purpose-built sources now **bound Lebanon-specific Al Jazeera
reach below mass plausibility**:

1. NU-Q 2017 (pp. 35–37): 93% of Lebanese say their favorite news
   organization is domestic — the highest of all seven countries (KSA 38%);
   92% privately owned; and Lebanon ranks at the bottom for international
   channels wherever per-country values were published (CNN 8% vs. 25%
   KSA; BBC online 5%).
2. Ipsos/ArabAd 2021: no pan-Arab channel in the Lebanese nightly-news
   top 15.
3. ELKA 2024 (via MOM): the domestic top-4 hold ~80% of TV viewing.
4. AB8 2024: the medium mix is social/TV-domestic-first.

Documented caveats: favorite ≠ reach (NU-Q), and ELKA's measured universe
may exclude pan-Arab satellite channels — which is why the row stays
`unresolved` (candidate **substantial**) rather than being forced to niche.
Consequence: the gate derivation drops `blocking-unresolved` → `optional`;
**Lebanon's coverage claim is no longer blocked**. If Al Jazeera is
collected as an optional perspective row, its robots/TDM restriction still
requires an archive or permission route (step 3). A direct measurement
(NU-Q raw data request) remains welcome but is no longer required.
