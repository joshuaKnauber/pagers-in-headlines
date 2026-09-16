# Israel normalization — notes (v1, 2026-09-06)

Script: `data/scripts/normalize_israel.py` ·
Output: [corpus-v1.jsonl](corpus-v1.jsonl) (schema `1.1.0-phase1`, same
field groups as Lebanon).

## Result (v1.1, post-review rerun)

**157 primary records** (138 from candidates + 19 Abu Ali Telegram
posts; dropped: 2 out-of-window, 3 fetch-failed, 1 Abu Ali exact-body
duplicate collapsed).

- **Outlets:** Ynet 95 · Kikar 22 · Abu Ali 19 · Makan 11 · N12 10.
- **Document types:** 80 articles · 58 flash_or_lead (Ynet paywall
  leads, body <90 words) · 19 telegram_post. The flash_or_lead share
  (37%) is Israel's genre signature, the counterpart of Lebanon's 40%
  ticker/brief share — same rule applies: headline-weight analysis for
  these, body-level for articles.
- **Languages:** 146 Hebrew, 11 Arabic (Makan) — detected, not assumed.
- **Dates: 156/157**, JSON-LD `datePublished` + Telegram timestamps. No
  interpolation anywhere (vs Lebanon's 40 ID-interpolated) — Israeli
  date quality is the best of any country so far.
- **Body medians (post container-repair):** Makan 229w · Kikar 123w ·
  N12 ~400w · Ynet 58w (lead-only by paywall policy). Kikar/N12 medians
  fell sharply from v1 because v1 bodies included page chrome — see
  triage-notes v1.1 ledger.
- **Time slots:** day_0 35 → **day_1 62 (peak)** → day_2 21 → decay,
  10 week_2 + 8 first_month tail. Same day-1 walkie-talkie peak as
  Lebanon.

## Known limitations (for analysis to respect)

1. **"Reuters" credit (23 records) is mostly citation, not
   syndication.** The lead-keyword wire detector fires on "לפי רויטרס" /
   "according to Reuters" — in the Israeli context that is the
   foreign-attribution (censorship-formula) pattern, not wire copy.
   Don't read `provenance.credit` as syndication for Israel without a
   body check.
2. Ynet is 59% of the corpus and lead-weighted — outlet-equal or
   reach-weighted aggregation is mandatory before publishing
   country-level shares; raw corpus shares over-weight Ynet flashes.
3. N12 n=10 (title-sweep recall limit, see triage notes) — its 80%
   "operation" share is directionally real but low-n.
4. Abu Ali records are message-level (median far shorter than articles)
   and cover 20 of 33 days.
5. No story-level clustering (exact-hash dedup only), same as Lebanon.

Used in `data/analysis/lebanon-israel-comparison-v1.md` and the viz doc
(`data/analysis/lebanon-israel-viz-v1.html`).
