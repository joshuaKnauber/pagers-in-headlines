# Israel corpus: changelog

`corpus.jsonl` is always the current version. Earlier versions survive only where they were
committed: 52af888 holds Lebanon at 338 primary and Israel v1 at 153 primary; e79be10 holds v1.2.1
for all four countries. Other intermediate versions were not committed. Record schema:
`1.1.0-phase1` throughout.

## v1 (2026-09-06)

Produced by: `pipeline/05-extraction/extract_israel.py`, `pipeline/06-normalization/normalize_israel.py`.

153 primary (commit 52af888). First corpus from the title sweep and Abu Ali message extraction.

## v1.1 (2026-09-06)

Produced by: `pipeline/07-repair/repair_v11_israel.py`, then normalization re-run.

157 primary. Kikar and N12 bodies re-extracted from their article containers (page chrome had inflated term counts), singular-device recall gap (+5 Ynet), Abu Ali capture-overlap duplicate collapsed, 3 non-event strong tags downgraded. Ledger: `05-extraction/triage-notes.md`, "v1.1 amendments"; results in `06-corpus/normalization-notes.md`.

## v1.2 (2026-09-16)

Produced by: `pipeline/07-repair/repair_v12.py israel` (+ inline Abu Ali additions).

166 primary. N12 mako path-twin collapsed, Makan bodies re-extracted, `published_time` recovered for every primary record, +10 Abu Ali posts the device-word rule had dropped. Ledger: `05-extraction/triage-notes.md`, "v1.2 repair pass".

## v1.2.1 (2026-09-16)

Produced by: v1.2.1 fix-ups (`python3 pipeline/07-repair/repair_v12.py fixups`, same day, after the codex review in `data/cross-country/reviews/07-repair-v12-review-codex.md`).

Word counts recomputed; no other change.

## v1.3 (2026-10-05)

Produced by: `pipeline/07-repair/repair_v13.py israel`.

169 records, 165 primary (was 166). Fixes from the recall audit:

- Excluded: `il_ynet_35be01752a` (Sep 23 reports of Israel phoning residents to evacuate, a different event) and `il_abuali_75669` (car bomb in Damascus; restored in v1.3.1).
- `il_n12_ae690238dc` retyped `podcast_page`. `il_n12_42fc90d847` dated Sep 17 (article:published_time 22:00 +03:00).
- Added Abu Ali 75653 (Sep 17 12:57:18 UTC), the channel's first pager post, and 75655 and 75656 (stored as reposts with the wrong text; corrected in v1.3.1: they are replies). Source: the live `t.me/s` preview fetched by the recall audit, copied to `raw/abuali/live-a0bedcf293cca3cc.html`.
- Correction: the v1.2 note that N12 (12:59 UTC) beat Abu Ali (13:19) is wrong. Abu Ali posted at 12:57 (75653, not in the Wayback captures). The v1.2 note also misread the corpus it had: 75657 (13:06) and 75659 (13:15, naming זימונית) were already in it.

## v1.3.1 (2026-10-05)

Produced by: `pipeline/07-repair/repair_v13.py fixups`. Review of v1.3 (general-purpose subagent, 2026-10-05): pass with fixes. Applied as `python3 pipeline/07-repair/repair_v13.py fixups`; the v1.3 stages now also skip anything the fix-ups reversed, so replaying all stages from v1.2.1 gives this version.

170 records, 168 primary.

- `il_abuali_75669` restored as `related` with warning `possible_syrian_wave_v131`: posted at 13:35 UTC among the pager posts, and the channel's 75676 (14:03) links explosions in Syria to Hezbollah pagers. Probably the Syrian part of the attack, not a separate incident.
- `il_abuali_75655` and `75656` are replies to 75653, not reposts. v1.3 stored the quoted text of 75653; they now carry their own text ("דוגמא למכשירי הזימונית שהתפוצצו בביירות.", "אלג'זירה מפי מקורותיה: מכשירי הזימונית פוצצו בטכנולוגיה אלחוטית.") and are primary. Cause: the recall audit's Telegram parser read the reply-quote box as the post's text, fixed in `recall_audit_il_lb_abuali.py` (199 of 872 messages affected).
- `il_abuali_75653`: warning `live_text_post_edit_v131`; the live page marks the post as edited, so the stored text is the current wording.
- `il_n12_42fc90d847` `published_time` in N12's `+0300` format.
