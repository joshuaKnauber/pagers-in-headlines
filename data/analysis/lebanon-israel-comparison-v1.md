# Lebanon ↔ Israel: first cross-country comparison (v1.1, 2026-09-06)

Corpora: Lebanon 338 primary relevant records (5 outlets) · Israel 157
(4 outlets + Abu Ali Telegram). Same measures, matched per-language term
families. Record-share %, headline + first 6,000 chars of body.
Single-pair comparison — Germany/US pending.

## Headline table

| measure | Lebanon | Israel |
|---|---|---|
| agentless grammar ("explosions happened") | 43.5 | **82.2** |
| agentive grammar ("someone detonated") | 45.0 | 51.6 |
| **operation** | 3.3 | **26.8** |
| attack | 15.4 | 28.0 |
| aggression/massacre/crime register | 10.7 | 5.1 |
| casualties as **terrorists** | 0.6 | **14.6** |
| casualties as **martyrs** | **8.9** | 0.0 |
| "foreign reports" censorship formula | 0.0 | 3.8 |

## Findings

1. **The naming split is total and clean.** "Operation" framing: Israel
   27% vs Lebanon 3%. Casualties: Israel calls them terrorists (15% vs
   0.6%), Lebanon calls them martyrs (9% vs 0.0%). Zero-overlap mirror
   registers — the מבצע/مجزرة divide, quantified.
2. **The agency paradox.** Attacker-side coverage uses *agentless* grammar
   (82%!) far more than victim-side (43.5%) — Israeli mainstream writes
   "פיצוץ הביפרים" (the beeper explosion) under censorship-shaped caution
   even while celebrating the מבצע. Meanwhile the victim side is *more*
   agentive overall, driven by Al-Manar/MTV's تفجير. Grammar tracks
   institutional constraints, not pride — with the ideological poles
   (Kikar ~100% agentive; Al-Manar 62%) breaking their own side's pattern.
3. **The censorship fingerprint exists only on one side**: "according to
   foreign reports" appears in 3.8% of Israeli records and 0.0% of
   Lebanese ones — a measurable, attacker-side-only attribution mechanism.
4. **The day-curves are near-identical** (day-1 peak 40% vs 45%) — the
   walkie-talkie second wave dominated coverage on *both* sides. Whatever
   divides the framing, the attention rhythm was shared.
5. Within-country spectra are as wide as the between-country gap on some
   measures (Kikar↔Ynet on terrorists; Al-Manar↔LBCI on massacre 17↔2) —
   supporting the project's design decision to measure outlets, not
   countries, and weight by reach.

## v1.1 corrections (post adversarial review, codex, 2026-09-06)

The step-5 review (data/israel/reviews/) found extraction and recall
defects; all fixed, table recomputed:

- Kikar/N12 p-cluster bodies carried page chrome (nav, related-links,
  footer) → container re-extraction from saved raw (32 records). This
  had **inflated Israeli "terrorists" from 20.9→14.6** (nav text carried
  מחבל) and nudged most Israeli rows down 2–6 points.
- Title-sweep recall gap: singular/generic device terms (מכשיר קשר,
  מכשירי רדיו) added; +5 Ynet records recovered.
- 1 Abu Ali duplicate post collapsed; 3 event-prompted-but-not-event
  items (pager anecdote, Raisi speculation, cartoon reaction) downgraded
  strong→related.
- Measurement basis stated precisely: body text truncated at 6,000 chars
  (was described as "full available text"); Lebanon figures under this
  basis are unchanged.

All five findings survive the correction; magnitudes shifted, directions
and zero-overlaps did not.

## Caveats

Presence-based keyword shares; Israeli corpus lead-weighted for Ynet
(flash/paywall format); n=157 vs 338; Abu Ali records are message-level;
mixed-language matching uses per-language families (Hebrew "massacre"
register ≈ unused, so the 5.1% Israeli row is mostly quoted terror/crime
mentions — inspect before publishing). Reach-weighting not yet applied to
this table.
