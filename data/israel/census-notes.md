# Israel outlet census — evidence notes (v1, 2026-09-06)

Companion to [outlet-census-v1.csv](outlet-census-v1.csv). Built per
`1_OUTLET_COLLECTION.md`; evidence gathered by codex CLI (measurement
backbone) and copilot CLI (social counts) — raw archives in
[social-counts-raw/](social-counts-raw/). **Not yet reviewed.**

## Medium mix and evidence base

Israel is **not** a DNR market (the old reach file's DNR-based Israeli
tiers were unfounded — re-derived here from scratch). Backbone instead:

1. **Kantar TGI Jan–Dec 2024** — print exposure (Israel Hayom 25.4%
   weekday, Yedioth 17.9%, Haaretz 6.1%) and radio listening (Reshet Bet
   21.0%, Galei Tzahal 20.2% — radio is a major Israeli news medium,
   unlike Lebanon/Germany). Caveat: TGI measures Jewish adults 18+, not
   all residents — a structural bias the census inherits and must state.
2. **IARB TV ratings 2024** (via Walla's annual review) — evening news:
   Channel 12 15.9% (dominant), **Channel 14 7.4% — overtook Channel 13
   (6.5%) during the war**, Kan 11 4.5%. The wartime vintage matters and
   is captured.
3. **IDI survey (early 2024)** — per-brand digital: Ynet primary source
   for 40% (a dominance no outlet in our other censuses matches), N12
   24%, Walla 21%.
4. Ahrefs organic-search rankings (weak corroboration), NEWSru
   Russian-speaker survey, Bar-Ilan Arabic-speaker survey, DataReportal
   denominators (FB 4.90M, IG 4.65M, YT 6.82M, TikTok 4.16M, X 1.01M).

## Israel calibration

Axis A strong = current purpose-built population reach/exposure/rating
≥10%; weak 3–10%. Axis B: strong ≥2M domestic-oriented aggregate; weak
400K–2M; substantial-via-B ≥1.5M. **Export rule** (new, formalizing the
pan-Arab precedent): outlets whose audience is predominantly outside
Israel (JPost — 60% US readers by its own statement; ToI; i24;
Ynetnews-EN; Haaretz-EN) do not get domestic axis-B credit; they carry
`home_system: israel-export` and an `AUDIENCE-MARKET: international`
note. They are candidates for a separate **world-facing panel** — for
this event they are how much of the world consumed Israeli framing, which
is an analytical role of its own, distinct from domestic exposure.

Resulting tiers: **mass (2)** Ynet, Channel 12/N12 ·
**substantial (9)** Channel 14, Channel 13, Kan (radio-led), Walla,
Israel Hayom, Yedioth print, Haaretz, Maariv, Galei Tzahal ·
**niche** Globes, the export set, Channel 9, Abu Ali Express ·
**unresolved** Arabic-language Israeli media (measurement gap).

## Structural findings

1. **Ynet's dominance is extreme** — 40% name it their primary online
   source; no other census country has a single-brand figure like it.
2. **The Israeli spectrum is measurably wide on reach alone**: Channel 14
   (right, pro-government, surging) vs Haaretz (left-liberal) vs Kan
   (public) vs Army Radio (military-operated — institutionally unique for
   an attacker-side census in this event) all clear the substantial bar.
   The no-spectrum-labels rule still holds: reach put them all in.
3. **Radio matters in Israel** (two ~20%-daily stations) — first census
   where radio outlets earn substantial tiers.
4. **Telegram is the uncounted layer**: Abu Ali Express (583K subscribers,
   ~6% of the population, Telegram-native) is the Israeli analog of the US
   creator layer, and our axis rule has no denominator for Telegram.
   Flagged for the reviewer: the rule may undercount this layer.
5. **Two documented subpopulation gaps**: Russian-language (Channel 9 —
   38% of Russian-speaking Israelis; panel-representative decision
   pending) and Arabic-language media for Arab citizens (~20% of the
   population, no outlet-level measurement found — unresolved row,
   Germany-diaspora-style limitation unless a dedicated sweep runs).

## v1.1 amendments (post-review-1, codex CLI, 2026-09-06)

Review verdict: not freezable — strong backbone, both mass rows upheld,
but real omissions and two rule defects. Applied:

| finding | action |
| --- | --- |
| **TV ratings are average-minute audiences, not weekly reach** — my ≥10% threshold misread the metric | **Ratings-conversion rule added**: a nightly-news average rating implies weekly cume ≈2–3×; ratings ≥5% count as axis-A strong (documented conversion). Ch13 and Ch14 re-derive to 1-strong substantial cleanly; Ch12 unchanged |
| Channel 13's network-shared social discount was unquantified | Review option 2 adopted: raw network counts recorded as contaminated, excluded from axis B; tier from A alone |
| **Haredi media layer missing** (13% of population) | Kikar HaShabbat + Behadrei Haredim added (unresolved, candidate substantial); TGI/IDI under-measurement of this community documented |
| TGI-measurable omissions: B'Sheva/Arutz Sheva (7%), 103FM (9.2%), Calcalist (8.8%) | rows added (unresolved, candidate substantial, B ungathered) |
| Abu Ali Express should be collection-required by role | re-tiered **substantial as role-based representative of the Telegram layer** (IDI: 44% get news from Telegram — a mass-level category invisible to the axis rule); gate will derive required-representative |
| Export rule over-broad (language-inferred) | narrowed: requires documented audience split (JPost qualifies) or explicit "no domestic evidence found" wording (ToI, Ynetnews, Haaretz-EN — row added); i24 reclassified mixed with its 2.0% domestic rating retained |
| Walla annual-ratings article is a secondary source with internal contradictions | round-2 item: resolve against a primary IARB table before freeze |
| Ch12/N12 single row risks conflating surfaces | kept as one tier row; collection plan must preserve TV and digital routes separately (noted for step 3) |

**Still blocking freeze (round-2 evidence pass dispatched):** haredi/
B'Sheva/103FM/Calcalist axis-B counts; Walla/IARB primary verification;
Makan 33/Arabic resolution or documented structural exclusion; 0404 and
Telegram-directory candidates.

## v1.2: round-2 evidence resolutions (2026-09-06)

Round-2 pass (copilot; archived in social-counts-raw/round2-copilot.md):

| item | resolution |
| --- | --- |
| Walla-derived IARB ratings | **confirmed** by an independent second outlet (kipa.co.il, Jan 2025, exact match); both trace to the members-only IARB/Kantar panel — best publicly achievable verification, documented as such |
| Haredi layer | **Kikar HaShabbat → substantial** as role-based haredi representative (archived SimilarWeb: ~4.4M visits/mo, far ahead); Behadrei Haredim → niche (social near-absent, traffic unobtainable) |
| B'Sheva/Arutz Sheva, 103FM, Calcalist | axis-B counts came back small → all resolve **niche** (1 weak each); perspective-panel candidacy noted for Arutz Sheva |
| **Arabic layer — partially resolved with real data**: Arab-sector TV panel ratings exist (Makan 33 news bulletin 10.6% within-sector) | **Makan 33 → substantial** as role-based Arabic-language representative; **Kul al-Arab added** (FB 1.38M, cross-border-discounted, niche); Panet contradictory-thin (no row); Hala TV no data. Residual limitation: outlet-level landscape beyond these remains thin — stated, not silent |
| Telegram layer | Abu Ali Express 583K verified via tgstat + Hebrew Wikipedia; **no other Hebrew news channel >100K confirmed** — its representative status strengthened; News0404 unverifiable |

Final tier picture: **mass 2** (Ynet, Ch12/N12) · **substantial 12** ·
**niche 12** · unresolved 0.

**Census status: FROZEN (v1.3, 2026-09-06).** The scoped delta-review
(codex; archived at social-counts-raw/../..; verdict in session records)
regression-confirmed all review-1 fixes, verified the v1.2 tier
resolutions (Makan 33's Arab-sector rating source and the kipa.co.il
ratings corroboration checked live), and returned only three metadata
nits — all applied (Kikar/Makan evidence periods; i24 `home_system:
israel-mixed`). Per the cadence rule, a trivia-only review = freezable.

## Open items / for review

- Adversarial review (standard step 6) not yet run — queue on an external
  CLI. Flags: export rule application, Abu Ali/Telegram treatment,
  Channel 13's network-shared social discount, TGI Jewish-adults frame.
- X counts unobtainable for several outlets (login-walled) — handles
  verified, counts marked not-found.
- Event-window volatility: 2024 annual figures are the backbone; Sep
  17–19 spike measures are an enumeration-stage concern, not census.
- Gate script: add israel to `CENSUS_FILES` when the census freezes.
