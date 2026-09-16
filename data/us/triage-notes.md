# US triage/extraction/normalization — notes (steps 5+6, v1, 2026-09-14)

Scripts: `extract_de_us.py us` + repair pass → `normalize_de_us.py us`.
Output: corpus-candidates-v1.jsonl (248) → **corpus-v1.jsonl, 138
primary records** (dropped: 61 none, 22 no-capture). Overnight
autonomous run — **adversarial review dispatched but not yet folded
in; treat as freeze-candidate.**

- Outlets: CNN 30 · Yahoo 30 · Fox 23 · NBC 15 · WaPo 12 · CBS 10 ·
  Reuters 8 · ABC 5 · NYT 4 · USA Today 1.
- Routes: live (Fox/CNN/CBS/NBC/USAT/Yahoo/AP), Wayback captures
  (ABC/WaPo/Reuters), per-URL availability→capture (NYT).
- Slots: day_1 peak (33); doc types 137 article · 1 flash_or_lead.

## Repair pass (extraction round 2, same day)

| defect | fix |
| --- | --- |
| NYT: all 17 "no-capture" | bug — fetch helper rejected the availability API's small JSON; fixed → 4 records (live-blog + captures); 13 genuinely uncaptured (consistent with NYT's enforced archive exclusion) |
| Yahoo: 33 GDPR consent shells ("Ihre Datenschutzeinstellungen", German IP) | refetched with Googlebot UA (documented workaround; robots permits article crawl) → 30 records |
| Reuters: 13 captures were archived block pages | availability-API nearest capture instead of publication-date guess → +4 (8 total) |
| USA Today: 6 of 7 curated URLs redirect to section homepage (link rot) | accepted: n=1 (the fetch-verified register URL); USA Today framing shares unusable, reach still counts via Yahoo/Gannett syndication |

## v1.1 amendments (post-review, codex, same night)

Review verdict: fail → fixed and re-normalized same night. Applied:
4 Reuters Wayback-landing pages rejected (new normalize rule);
Yahoo fetch-day nav-ticker prefix cut (the Al Jadeed trap — 2026
headlines were inside 2024 bodies); Reuters gallery/licensing prefix +
related-tail cuts; WaPo branding prefix + Read-more tail cuts; strong
relevance now requires an event term in title/first-1500-chars
(Fox incidental-mention false positives demoted); 36 missing dates
repaired from raw meta. Duplicates verified already-handled
(0 both-primary clusters). **Final: 134 primary.**

## Known limitations

- NYT n=4 and USA Today n=1 — candidates-only outlets at lead depth;
  their rows inform presence, not stable shares.
- Yahoo records are syndicated (USA Today/AP/Reuters/AFP/Yahoo UK
  providers) — provenance analysis must use the wire-credit field, and
  Yahoo's analytical weight is reach, not original text.
- English cannot morphologically split agency ("detonated" counted as
  actor-naming) — cross-language grammar comparisons must caveat the
  US/EN rows.
- "terrorist" as routine Hezbollah descriptor inflates the
  terrorists-measure (Fox 91%) — presence upper bound, same as Germany.

## v1.2 repair pass (2026-09-16, deep-dive review fixes)

Script: `data/scripts/repair_v12.py us`. Driven by the grok deep-dive
(raw report `data/analysis/deep-dive-raw/us-grok-raw.md`), every
defect re-verified against the corpus before fixing.

- **Chrome re-extraction** (109 bodies): fox from `article-body`
  container (kills the 2026 "Right Arrow" nav ticker, 20/23 affected);
  cnn written from paragraph-class nodes, cnn video pages from
  og:description and retyped `video_page` (19/30); yahoo from the
  `<article>` element (kills Top-Stories rail + 2026 Reuters grafs).
- **AMP/desktop dedup** (3 clusters): fox ×2, abc ×1 — non-AMP kept
  primary, `ampdup_*` cluster ids.
- **Yahoo provenance rebuilt** (17 credits from body markers:
  Reuters/AP/AFP/Telegraph/NBC News/USA Today) — Yahoo weighs as
  reach-for-wires, not an original outlet.
- Effect: **131 primary** (was 134). Fox "terrorists" 91% → 66.7%
  (chrome-inflation confirmed); CNN 6.7%.

### v1.2.1 (post-review corrections, same day)

Codex review verdict: fail → fixed same session; see
`data/analysis/reviews/v12-repair-review-codex.md`. Fox newsletter
tails cut (17).
