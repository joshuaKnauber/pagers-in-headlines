# Germany outlet census — evidence notes (v1, 2026-09-05)

Companion to [outlet-census.csv](outlet-census.csv). Built per
[`01-outlet-census.md`](../../../docs/methodology/01-outlet-census.md);
social-reach lookups were run partly on external CLI agents (codex, grok) due
to session limits — rows note which.

## Medium mix (step 1)

DNR Germany 2025 (HBI, n=2047, fieldwork ~Jan–Feb 2025): TV is the most
important news source for 43%, online sources combined 42% (social media 14%
as most-important); weekly use: 61% linear TV news, 66% online news, 33%
social, 34% radio, 43% any print brand. Medienvielfaltsmonitor 2024
(Mediengewichtungsstudie 2023-II): opinion-forming weight Internet 35.3% >
TV 28.3% > radio 17.1% > newspapers 15.5% > magazines 3.8%.

Unlike Lebanon (social 53% primary), Germany is still TV-plus-brand-websites
territory, with social third. Consequence: axis A (survey brand reach)
carries more of the tier weight here, axis B less.

## Evidence backbone

1. **DNR Germany** ([2025 PDF](https://leibniz-hbi.de/wp-content/uploads/2025/06/AP77_RIDNR25_Deutschland.pdf),
   [2026 PDF](https://leibniz-hbi.de/wp-content/uploads/2026/06/AP83_DNR26_Deutschland.pdf)) —
   per-brand weekly reach, three consistent waves spanning the event
   (2024 fieldwork Jan 2024, pre-event; 2025 post-event; 2026 current).
   Offline 2025: ARD 39, ZDF 32, RTL 23, regional paper 21, ÖR-Regionalradio
   20, ÖR-Regional-TV 19, n-tv 18, Privatradio 16, WELT 12, Stadtanzeiger 8,
   :newstime 7, Bild 7, Spiegel 7, Focus 5. Online 2025: tagesschau.de 17,
   t-online 14, bild.de 14, n-tv.de 13, web.de 12, spiegel.de 11, Focus 10,
   Regional online 10, welt.de 10, gmx 8, heute.de 8, ZEIT 7, SZ 6, rtl.de 5.
   2026 (narrative): tagesschau.de 20, t-online 17, n-tv/bild.de 14; ARD 38,
   ZDF 31, RTL 23 offline. *Caveat: the 2026 report flags a technical problem
   in its social-media items — use 2026 social findings cautiously.*
2. **Medienvielfaltsmonitor 2024** ([PDF](https://www.die-medienanstalten.de/fileadmin/user_upload/die_medienanstalten/Forschung/Medienvielfaltsmonitor/Medienvielfaltsmonitor_2024.pdf)) —
   regulator's opinion-market shares: ARD 20.3, Bertelsmann 11.0, ZDF 7.4,
   Springer 6.8, KKR 6.4 (company level; public-service total 28%). Includes
   Nielsen unique-audience shares for **Jul 2023–Jun 2024** (the pre-event
   year): msn.com 4.5, web.de 3.5, gmx.net 3.0, t-online 2.8, bild.de 1.9,
   focus.de 1.8, zdf.de 1.7, spiegel.de 1.3, stern.de 1.2, rtl.de 1.2,
   tagesschau.de 1.0, n-tv.de 1.0, welt.de 1.0, faz.net 0.8, sz/zeit 0.7.
   *Vintage warning: the PDF bundles pages from several editions (a 2019
   title page appears mid-document); every number was matched to its own
   source line before use.*
3. **Social counts** gathered 2026-09-05 by four Claude lookup groups plus
   codex CLI (alt-media) and grok CLI (public media/portals), all with
   handle verification against site footers/impressums. Platform
   denominators (DataReportal early 2025): Facebook 24.5M, Instagram 31.3M,
   YouTube 65.5M, TikTok 21.8M, X 21.6M users in Germany.

## Germany calibration of the tier rule

Thresholds are country-calibrated before per-row assignment, chosen from the
shape of the measured distribution (clear gaps at ~3M and ~1M aggregate):

- **Axis A strong:** current DNR weekly brand reach ≥10% (offline or online
  list). Weak: 3–10%, or dated ≥10%.
- **Axis B strong:** ≥3M aggregate across verified official accounts.
  Weak: 1–3M. Below 1M: no signal. (Lebanon's 2M/500K bands would make half
  of Germany's mid-field "strong"; the platform base is ~10× larger.)
- **Substantial via B alone:** ≥2M aggregate.
- **Structurally-void-axis exception** (generalizes Lebanon's ban
  exception): when an outlet's distribution model makes axis B
  unrepresentative of reach — platform bans (Al-Manar) or **portal brands**
  whose audience arrives via homepage/app/email rather than social — a
  single current axis-A signal at ≥1.5× the strong threshold (i.e. ≥15%
  reach) carries mass, documented per row.

## Structural findings

1. **Tagesschau dominates both axes** — #1 in survey reach offline and
   online *and* ~19.3M aggregate social (7M Instagram alone), roughly 2–3×
   any commercial brand. German news exposure has a public-service center of
   gravity that Lebanon's fragmented system lacks (MVM: ÖR companies = 28%
   of the opinion market).
2. **The portal pattern.** t-online is the #2 online news brand by survey
   reach (17% in 2026) and #4 of all German websites by Nielsen unique
   audience, yet its social aggregate (~620K) is ~30× smaller than
   comparable brands — its reach is homepage/app-driven. Same for
   web.de/GMX (one 1&1 newsroom, 12%+8% reach, ~1.3M social). Judging German
   outlets by social counts alone would misrank the entire portal layer;
   hence the portal exception. **This is the census's main rule innovation —
   flagged for independent review.**
3. **Aggregators sit above newsrooms in raw traffic.** Nielsen has msn.com
   as Germany's #1 site by unique audience. MSN, Google News, and upday are
   exposure surfaces carrying other outlets' content — excluded from the
   editorial census (exclusion table below) but relevant later as a
   distribution layer.
4. **Frozen X accounts as a German particularity:** taz (615K, protected)
   and Deutschlandfunk (278K, inactive since Jan 2024) left X; their counts
   are fossils and were discounted or footnoted, not treated as live reach.
5. **Alt-media sit below the survey floor but are measurable:** NIUS
   (~1.4M aggregate, partly self-reported), Tichys (~610K + 4.5M
   ad-marketer-reported visits), Apollo (~340K + 5.5M Semrush visits), JF
   (~350K). None appears in any DNR wave's ~60-brand list. All tier niche
   under the calibrated rule; NIUS is the one to re-check next round.
6. **Impostor-handle density was high:** Turkish NTV at @ntv, squatted
   @welt/@sz/@taz/@rtlaktuell/@bild-TikTok, Spiegel's IG living at
   @spiegelmagazin. Every count in the CSV is handle-verified; treat any
   future additions with the same suspicion.

## Inclusion/exclusion decisions

| entry | decision | reason |
| --- | --- | --- |
| MSN, Google News, upday | exclude | aggregators without own newsroom; note as distribution layer |
| web.de / GMX News | one row | measured as two brands but one newsroom (1&1 Mail & Media) |
| Deutsche Welle (German) | context | external state broadcaster; domestic reach out of mission |
| dpa | context | wire baseline, not audience-facing |
| Phoenix, Tagesschau24 | folded | minor ÖR 24h channels inside ARD/ZDF brand rows |
| Regional/local dailies | category row, unresolved | 21% reach as a category; step 2 must pick representative titles or document exclusion |

## Known gaps for round 2

1. **Deutschlandfunk per-brand reach** (ma 2024/2025 Audio) — decisive for
   its tier; category-level ÖR radio is 20–23%.
2. **Regional press decision** — which titles, if any, enter collection
   (RND/Madsack as a syndicated network is the efficient candidate).
3. **Diaspora and non-German-language consumption** (Turkish, Arabic,
   Russian media consumed in Germany) — DNR surveys German-speaking online
   adults only; entirely unmeasured here. Relevant for a Middle East event;
   at minimum document the blind spot on the final page.
4. AGF/AdScanner absolute TV news viewership (Tagesschau ~9–10M/day) as
   axis-A corroboration; IVW print circulation for FAZ/SZ/Zeit rows.
5. DNR 2026 full online brand chart (only the narrative top-4 used here;
   chart pages not yet extracted).
6. P7S1 :newstime social counts (accepted gap; tier ceiling substantial).
7. Al Jazeera-style pan-national check: is there measurable German
   consumption of non-German international brands (BBC, CNN, Al Jazeera)?
   DNR's brand list includes some — verify in the full chart (gap 5).

## v1.1 amendments (post-review-1, applied in place with this changelog)

Review 1 ran on codex CLI with web verification (archived:
[01-census-review-codex-2026-09-05.md](../reviews/01-census-review-codex-2026-09-05.md)).
Verdict: not yet freezable — one mechanical violation, one count error, and
freeze-blocking evidence gaps. All survey citations checked came back
accurate (DNR values, MVM shares, Nielsen shares); social spot-checks were
3/4 accurate.

| finding | action |
| --- | --- |
| :newstime tiered niche with axis B ungathered — violates the unresolved definition | → `unresolved` |
| Spiegel Instagram 2M snippet was stale; live ~1.6M | corrected; aggregate ~9.7M (tier unchanged) |
| t-online portal exception must anchor to vintages ≥15% (2025 value is 14%) | rationale re-anchored to DNR 2024 (16%) + 2026 (17%); tier upheld by reviewer |
| WEB.DE/GMX merged-row substantial | upheld by reviewer; no change |
| Social counts lacked per-account URLs in-repo | full raw evidence table added: [social-counts.md](social-counts.md) |
| DLF ma Audio: reviewer found ~0.47M daily listeners but metric type unpinned | noted in row; stays unresolved until the ma Audio metric is verified |
| Regional public brands (NDR/WDR/MDR) collapsed without stated policy | policy stated below |
| Vintage policy: DNR 2025 fieldwork is post-event | policy stated below |

**Regional-ÖR fold policy:** NDR/WDR/MDR and other Landesrundfunkanstalten
are folded into the ARD row for this study because national/foreign news on
those channels is ARD-produced (Tagesschau/ARD-aktuell) and their shared
online news surface is tagesschau.de. They would need their own rows only if
the study analyzed regional framing differences within Germany, which it
does not. This is a documented fold, not an omission.

**Vintage policy:** DNR 2024 (fieldwork Jan 2024) is the event-period
baseline; DNR 2025/2026 are sensitivity checks. Where 2024 values are known
(text parentheticals) they are in the rows; the full DNR 2024 Germany brand
charts (HBI AP71) remain a round-2 fetch. No current tier flips on any
known 2024-vs-2025 difference (largest: RTL 25→23, t-online 16→14).

**Freeze blockers — status after round 2 (2026-09-05):**

1. ~~DLF resolution~~ **CLOSED**: ma Audio 2025 I gives Deutschlandfunk
   2.46M daily listeners (Tagesreichweite Mo–Fr, record, #6 program) →
   axis A weak + axis B weak → **substantial**. Review-1's 0.47M figure was
   Deutschlandfunk *Kultur* — a misattribution; always pin the brand and
   the metric name in ma Audio data.
2. ~~International-brand check~~ **CLOSED**: the DNR 2025 full-report
   Germany chart (p. 85) shows **CNN at 5% weekly offline** (new niche
   row); BBC and Al Jazeera are absent (below chart floor). Bonus: the full
   chart also revealed **FAZ.NET at 5% online** — below the HBI report's
   truncated top-15 but measured — re-tiering FAZ to **substantial**
   (2 weak). Lesson: the country-report chart and the full-report chart
   have different cutoffs; check both.
3. ~~Regional-press decision~~ **CLOSED by project decision (2026-09-05,
   approved):** RND (RedaktionsNetzwerk Deutschland, Madsack) is included
   as the single representative of the regional-daily layer — one
   syndicated newsroom whose content runs in dozens of regional titles, and
   whose foreign coverage is what most regional readers actually saw. The
   category row moves to `context`. RND's tier (`substantial`) is
   role-based representation, not reach-derived — documented as such.
4. ~~Diaspora-language media~~ **CLOSED as a formal limitation (2026-09-05,
   approved):** This census measures the German-speaking online adult
   population (the DNR sampling frame). News consumption in Turkish,
   Arabic, Russian, and other languages inside Germany is **unmeasured
   here**, and for a Middle East event this plausibly biases the measured
   exposure spectrum. This limitation must be stated on the final
   visualization page and in any methods writeup. It can be reopened with a
   dedicated evidence sweep if the analysis warrants it.

**Census status: FROZEN (v1.2, 2026-09-05).** All review-1 findings
resolved or decided; remaining round-2 items (DNR 2024 full chart, AGF/IVW
corroboration, RND/:newstime social counts) are non-blocking refinements.

## Corrections against Lebanon-census lessons (applied preemptively)

- Every number carries its own vintage; the bundled-editions trap in the MVM
  PDF was caught before any figure was used.
- No tier was assigned without a stated signal; the two rule-tension rows
  (t-online, WEB.DE/GMX) are explicitly flagged for the reviewer rather than
  silently resolved.
- Frozen/inactive social accounts are labeled and discounted.
- Publisher-supplied traffic (NIUS media deck) is recorded but not credited
  as a signal.
