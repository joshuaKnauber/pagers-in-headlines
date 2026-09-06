# Lebanon smoke-test analysis — findings (v1, 2026-09-06)

Corpus: 338 primary normalized records, 5 outlets, Sep 15 – Oct 17 2024.
Raw tables: smoke-raw.md, timeline-outlet-day.csv, displacement-mtv.csv,
vocabulary-outlet.csv. Single-country pass — all findings are
within-Lebanon; cross-country claims await Germany/US.

## 1. The displacement curve (the fade-story replacement)

Using MTV's complete publication denominator (sitemap-dated total output):

- MTV's total output **doubled on the attack day** (423 articles vs ~190
  baseline) — the event grew the newsroom's output, then each later
  escalation grew it further (Sep 23 air campaign: 760; Sep 28 Nasrallah:
  879; **Oct 1 invasion: 1,029 — the month's maximum**).
- The pager story's share: 3.1% (day 0) → **8.7% peak (day 1)** → 4.5% →
  3.1% → 2.0% → 1.3% → **0.26% on Sep 23** → ≈0 thereafter.
- So the story died in **six days** — not from audience fatigue (output
  kept *rising*) but from displacement by the war it began. "How interest
  fades" is, in Lebanon, "how a story is buried by its own consequences."

## 2. The second wave outran the first

Every outlet peaked on day 1 (walkie-talkie wave), not day 0: corpus-wide
day_0 52 vs day_1 124. LBCI 25→43, MTV 13→38, Al Jadeed 14→23(→32
pre-clean). Al-Manar's peak is **day 2** (17) — the attacked party's own
channel was the *slowest* to peak, consistent with a stunned/considered
institutional response while commercial channels ran tickers.

## 3. The framing spectrum is real and quantified (record-share %, full text)

| family | LBCI | MTV | Al Jadeed | Al-Manar |
|---|---|---|---|---|
| plain "Israel" | 25.5 | 36.8 | **67.8** | 28.6 |
| enemy/Zionist register | 5.5 | 8.0 | 8.5 | **31.0** |
| aggression (عدوان) | 2.7 | 4.8 | 3.4 | **23.8** |
| massacre (مجزرة) | 1.8 | 2.4 | 3.4 | **16.7** |
| martyr (شهيد) | 2.7 | 12.0 | 1.7 | **33.3** |

Al-Manar is a measured outlier on every condemnation-register family —
the pole whose absence invalidated the old corpus, now quantified against
its domestic rivals. Al Jadeed's signature is different: not the enemy
register but **directly naming Israel more than twice as often as anyone**
(its famous editorial line that Israel booby-trapped the devices).

## 4. Agency lives in Arabic grammar (the morphology finding)

انفجار (intransitive: "explosion happened") vs تفجير (transitive:
"someone detonated"):

- **LBCI: 60.9% intransitive vs 36.4% transitive** — the agentless frame.
- **Al-Manar: 61.9% transitive vs 31.0% intransitive** — agency encoded.
- MTV leans transitive (50.4/42.4); Al Jadeed mixed (42.4/30.5).

The anti-Hezbollah channel adopted the grammar that erases the actor; the
Hezbollah channel the grammar that demands one. This measure is invisible
to English-keyword analysis and is a strong candidate for the final page's
within-language framing exhibit.

## 5. The wire register is its own dialect

Reuters/AFP-credited records (n=45) vs local (n=308): intransitive
explosion 71% vs 41; martyr 2% vs 11; enemy register 4% vs 11; crime/
terror 2% vs 8. The distribution corpus is measurably agent-less and
register-neutral **within the same country's pages** — the
editorial-vs-distribution split earns its keep before any cross-country
comparison exists.

## 6. Attribution did not rise monotonically

Share of records naming Israel or the enemy register: day 0 37% → day 1
46% → **day 2 23%** → day 3 37% → day 4 8%. Attribution peaked with the
second wave, then *fell* as coverage pivoted to casualties, funerals, and
speech anticipation. The pilot's assumption (certainty grows over time)
is wrong at daily granularity — attribution tracks *news function*, not
knowledge state. Worth testing in other countries.

## 7. A nuance for later coding: شهيد at MTV

MTV (anti-Hezbollah) still uses "martyr" in 12% of records — Lebanese
convention applies the term to national victims regardless of the
outlet's politics. Cross-country coding must not read شهيد as a
Hezbollah-alignment marker per se; the *rate* (33% vs 12% vs 2.7%)
carries the signal, not the presence.

## QC catches (the smoke test doing its job)

- **Al Jadeed body contamination**: all bodies carried the live site's
  fetch-day breaking-ticker strip (2026 headlines incl. "إسرائيل" —
  inflating its israel_plain to a fake 100%). Fixed via container
  re-extraction (ShortDesc/LongDesc) + ticker-block cuts; 15 video-page
  records correctly collapsed to headline-only duplicates. Lesson
  encoded: live-fetch extraction must never include ticker/recommendation
  widgets — check per-outlet common-prefix/line frequency as standard QC.
- NNA (n=2) unusable for shares — state-baseline claims deferred.
- Al-Manar id-interpolated dates (±1 day) fine at daily grain.

## Limitations

Single country; presence-based keyword families (no position weighting,
no negation handling); tickers/briefs are headline-weight text; Al-Manar
n=42 skews toward statements/flashes; reach-weighting is band-based.
