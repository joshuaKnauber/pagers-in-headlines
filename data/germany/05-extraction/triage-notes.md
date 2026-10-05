# Germany triage/extraction/normalization — notes (steps 5+6, v1, 2026-09-14)

Scripts: `extract_de_us.py germany` → `normalize_de_us.py germany`.
Output: candidates.jsonl (282) → **corpus.jsonl, 178
primary records** (149 strong + 55 related pre-window-filter; dropped:
78 none, 12 out-of-window). Overnight autonomous run — **adversarial
review dispatched but not yet folded in; treat as freeze-candidate.**

- Outlets: t-online 38 · Spiegel 33 · Bild 26 · RND 21 · WELT 16 ·
  Tagesschau 15 · ZDFheute 15 · ntv 12 · RTL 2.
- Routes: all live except RND (Wayback captures). Zero fetch failures.
- Dates: 203/282 candidates carried JSON-LD/meta dates; window filter
  applied on the dated set.
- Doc types: 153 article · 25 flash_or_lead. Slots: day_1 peak (43).
- Median body 558 words pre-QC.

## QC catches (applied)

1. **Spiegel**: 51 bodies began with a 222-char "EILMELDUNG —
   __proto_headline__" template artifact — auto-LCP strip removed it.
2. **ntv**: share-bar prefix ("Facebook X WhatsApp … Teilen Folgen") +
   "ntv bei Google bevorzugen" residue — SCRUB prefix list + targeted
   regex pass (7 bodies).
3. Bodies are single-line (extractor collapses whitespace), so
   line-frequency boilerplate stripping is inert — the LCP/SCRUB path
   is the effective chrome defense for this pipeline (Israel lesson,
   now generalized).

## v1.1 amendments (post-review, codex, same night)

Review verdict: fail → fixed and re-normalized same night. Spiegel
Merkliste-prefix + Dialog/Mehr-zum-Thema suffix scrubs added; 73
missing dates repaired from raw meta (out-of-window filter then caught
2 more); duplicate-body finding verified as already-handled
(0 both-primary clusters; consumers filter is_primary_record).
**Final: 176 primary.** Residual t-online image-credit prefixes are
caption text, accepted.

## Known limitations

- RTL n=2: its text coverage of the event was genuinely thin (TV
  brand); rtl.de manifest had only 2 slug-candidates of 1,321 URLs.
- Wire credit detection (dpa etc.) is lead-keyword based; t-online's
  dpa stream doubles as the wire baseline per the access register.
- German "Terroristen"/"Terrororganisation" is a routine Hezbollah
  descriptor — the terrorists-measure counts presence, not reference
  target; reach-weighted analysis must treat it as an upper bound.

## v1.2 repair pass (2026-09-16, deep-dive review fixes)

Script: `pipeline/07-repair/repair_v12.py germany` (raw report
`archive/v1-presence-shares/deep-dive-raw/germany-grok-raw.md`).

- **t-online headlines recovered from og:title** (36/36 were empty —
  20% of the corpus was invisible to headline measures).
- Scrubs: RND crossword tails (17/21; one crossword-only body retyped
  flash_or_lead), Bild opinion-CTA (21/26), WELT nav prefix, Spiegel
  Merkliste/meinung residue.
- **Spiegel paywall shells** (4, incl. "Operation »Gold Apollo
  AR-924«"): bodies cleared, retyped flash_or_lead — headline-only
  rows now, honestly typed. Live re-fetch parked (paywall).
- Count unchanged: **176 primary**.

## v1.3 repair pass (2026-10-05, recall-audit fixes)

Script: `pipeline/07-repair/repair_v13.py germany` (`--dry` prints the changes). Source of the fixes: the recall audit, `08-recall-audit/recall-audit-notes.md` and `raw/corpus-issues.csv`. Records that do not belong in the corpus moved to `06-corpus/excluded.jsonl` with an `exclusion.reason`; every touched record carries a `*_v13` warning.

- RND: four articles were stored twice because RND changed the slug and headline while updating them (same article ID). The later version (by `dateModified`) is primary; the earlier one is kept with `deduplication.relation = earlier_version` and `version_of`, because readers saw it and the claim catalogue cites some earlier versions.
- 31 `related` records listed by the audit as having no pager, walkie-talkie or device wording → relevance `context` (mostly escalation coverage from Sep 20 on). Three of them do mention the devices; reversed in v1.3.1, leaving 28.
- `ge_tonline_1e9c010a33` retyped `live_blog` (t-online's rolling newsblog, one snapshot). Three ntv `der_tag` entries retyped `live_ticker`.
- Effect: **172 primary (was 176).**

### v1.3.1 (review fix-ups, same day)

Review of v1.3 (general-purpose subagent, 2026-10-05): pass with fixes. Applied as `python3 pipeline/07-repair/repair_v13.py fixups`; the v1.3 stages now also skip anything the fix-ups reversed, so replaying all stages from v1.2.1 gives this version.

- Three `context` downgrades reversed: `ge_spiegel_0c74f9ad5e` (page lead: "Im Libanon sind zahlreiche Walkie-Talkies explodiert", now `strong`), `ge_tagesschau_5d524e455b` ("Angriffen auf Kommunikationstechnik der Hisbollah") and `ge_zdfheute_ad2e30a014` ("Explosion von Kommunikationsausrüstung im Libanon"), both `related`. The audit's term list missed these words; `repair_v13.py` now re-checks every record against a wider device pattern before downgrading.
- The five SPIEGEL+ paywall shells (`0c74f9ad5e`, `8be8faca25`, `56bd1c4430`, `eb13e72e65`, `176d1e0d56`) get their lead from the page's meta description as body (18–30 words): what a non-subscriber saw.
- `ge_ntv_5a5721af9d` (a `der_tag` entry typed `flash_or_lead`) retyped `live_ticker`.
- Effect: **190 records, 172 primary; 28 `context`.**
