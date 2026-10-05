# Israel triage + extraction — notes (step 5, v1, 2026-09-06)

Output: [candidates.jsonl](candidates.jsonl) (138
records) + [abuali-messages.csv](../04-enumeration/abuali-messages.csv)
(519 messages, 20 tagged), raw HTML under `raw/`. Scripts:
`pipeline/04-enumeration/title_sweep_israel.py` (sharded, resumable) +
`pipeline/05-extraction/extract_israel.py`.

## Title sweep (the step Lebanon didn't need)

Israeli article URLs are opaque (no slugs), so relevance required
fetching every enumerated title. Full-manifest sweeps, no sampling:

| outlet | titles swept | route | tagged (strong/related) | empty titles |
| --- | --- | --- | --- | --- |
| Ynet | 13,492 | wayback captures, 2 shards | 50/42 | 6 |
| N12 (mako) | 4,506 | dual workers: live-reverse + wayback, met mid-list | 7/5 | 147 |
| Kikar | 5,229 | live | 20/2 | 13 |
| Makan | 647 | wayback | 2/10 | 52 |
| Abu Ali | 519 messages from 65 captures | wayback capture stream | 20 tagged | — |

Term families: Hebrew ביפר/ביפרים, איתורית, זימונית, גולד אפולו +
Arabic بيجر + walkie-talkie family. **Pitfall caught during Abu Ali
tagging: bare ווקי substring-matches שיווקי (sponsored content)** —
two-word forms only (ווקי טוקי), retag dropped 44→20.

## Extraction

138 candidates fetched (routes per access register: Ynet/Kikar live,
N12/Makan Wayback): **92 strong, 43 related, 3 fetch-failed**. JSON-LD
carried both `datePublished` and `articleBody` for 92 records (Ynet and
mako serve it in-page, as the access review predicted); 43 fell back to
p-cluster. Dates: 134/138 (97%) — far above Lebanon's step-5 rate, no
interpolation needed.

**Ynet bodies are leads, not failures**: live and capture pages carry
only the JSON-LD lead (37–51 words); `PAYWALL_PLANS` markers confirm
Ynet+ paywalling. Accepted as headline+lead records per the pre-agreed
paywall policy — typed `flash_or_lead` in normalization, analyzed at
headline weight.

Abu Ali's first pager message: Sep 17, 13:19 UTC — "הלכה הזימונית (:"
— minutes after the blasts, before any article in the corpus.

## v1.1 amendments (post-review, codex CLI, 2026-09-06)

Review verdict: fail → all findings fixed same day
(reviews/05-extraction-review-codex-raw.md):

| finding | fix |
| --- | --- |
| Kikar/N12 p-cluster bodies included page chrome (nav/footer/related links) | container re-extraction from saved raw, no refetch (`repair_v11_israel.py`): Kikar `article-content` div, N12 `itemprop="articleBody"` — 32 records fixed, 0 container misses |
| Title sweep missed singular/generic device wording | families extended (מכשיר קשר, מכשירי רדיו, מכשירים שהתפוצצו); stored titles retagged — **+5 Ynet event items recovered**, all confirmed genuine |
| 2 Kikar + 1 Makan strong tags are event-prompted, not event coverage (pager anecdote, Raisi speculation, cartoon reaction) | downgraded strong→related via `RELEVANCE_OVERRIDES` in normalize script |
| 1 Abu Ali message duplicated across overlapping captures | body-hash dedup added for telegram posts |

Chrome contamination had inflated Israeli "terrorists" share 20.9→14.6
(מחבל appeared in Kikar nav text) — the comparison table was corrected
(see archive/v1-presence-shares/lebanon-israel-comparison-v1.md v1.1).

## Known recall limitations (parked, round 2)

1. **N12 is the weak spot: 12 tagged of 4,506.** Title-only sweeping
   misses Hebrew headlines that skip the device word (e.g. "מבצע"
   phrasing without ביפר). A GDELT or body-level recall supplement is
   the parked fix; the 12 collected skew toward the מבצע-celebration
   register, so treat N12 shares as low-n.
2. Makan's 52 empty titles (8%) are Wayback capture gaps, not paywalls.
3. Abu Ali: 65 captures cover 20 of 33 days; uncaptured days may hold
   unarchived messages. Live `t.me/s` pagination is the completeness
   fallback if analysis needs it.

## v1.2 repair pass (2026-09-16, deep-dive review fixes)

Script: `pipeline/07-repair/repair_v12.py israel` + inline Abu Ali add
(raw report `archive/v1-presence-shares/deep-dive-raw/israel-grok-raw.md`).

- **published_time recovered for every primary record** (JSON-LD for
  ynet/kikar/makan/n12; telegram timestamps for abuali). Headline
  finding this enables: N12 12:59 UTC beat Abu Ali's 13:19 — the
  "Telegram was first" reading was a date-granularity artifact.
  Caveat: timestamps carry mixed timezone formats (+0300 vs Z);
  normalize before sorting.
- N12 mako path twin collapsed (`pathdup_*`; n12 10 → 9).
- Makan Archive-Team body replaced from og:description.
- **10 Abu Ali day-0 posts recovered** (13:06–14:09 UTC) that the
  device-word tagging rule had dropped, incl. the Al-Araby attribution
  quote (75665, strong) and the gloat stream (Genesis 34, revenge-
  index — related). `recovered_v12_no_deviceword_rule`.
- Effect: **166 primary** (was 157).
