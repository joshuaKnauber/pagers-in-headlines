# Claim catalogue v1: notes

File: `claim-catalogue.jsonl` (81 claims, 32 marked `pilot: true`). This is step 1 only. No outlet × claim matrix has been built.

## Method

1. **Top-down.** I reconstructed what was publicly claimed from Sep 17 to Sep 24, 2024, plus the later reveals: Reuters Sep 20 (pagers handed out hours before the blasts, even after checks), Reuters Sep 25 (about 1,500 fighters out of action; the Reuters URL was not located, so Times of Israel's relay is cited), Reuters Oct 16 (PETN sheet inside the battery), WaPo Oct 5 (Mossad reconstruction, "both hands" design), and Netanyahu's Nov 10 confirmation. A web-research pass supplied the reference URLs and timings in `external_refs` and `first_public`. Where an article is in the corpus (Reuters, WaPo, NYT, the Yahoo syndication of the Panetta item), its canonical URL is used.
2. **Bottom-up.** I read all 832 primary-record headlines in the original Arabic, Hebrew, German and English, read about 30 bodies in full plus several hundred body passages surfaced by keyword sweeps, and ran those sweeps in all four languages for every candidate claim. Several claims exist only because of this pass, for example the Israeli undercount claim, the 19 IRGC dead, Aqil's pager injury, Fadlallah's son, the 500/300 eye figure, the deterrence and "4,000 targeted eliminations" framing, and the Ynet op-ed arguing the attack advanced "human-rights culture".
3. **Atomicity.** Every condemnation is one claim per speaker. Tolls are split by wave and by revision. Competing versions are kept as separate claims (lost eye vs. minor injury; pagers for senior members vs. Nasrallah's "leaders don't carry them"; mostly civilians vs. mostly Hezbollah) so that an annotator can code each one yes or no.
4. **Seed verification.** Every `corpus_seed_examples` id was checked by script (the id exists, is a primary record, and its headline or body matches a claim-specific pattern). I then read every matched passage by eye. Seeds that matched the pattern but not the claim were replaced: `lb_aljadeed_502751` (unnamed Axios sources, not US officials) and `lb_lbci_796733` (civil-defence advice, not "discard devices"). Five claims have one or two seeds because the corpus has only that many. `netanyahu_admits_approval_nov` and `mp_fadlallah_son_killed_false` have none (see below).

Corpus evidence counts. A claim found in the corpus circulated, whether or not a web search turns up an external reference, and no status here was downgraded for lacking one. Example: Abiad's "war crime, because most of the wounded were civilians" is on record only through an MTV ticker (`lb_mtv_1486283`, Sep 20). It is coded `official-claim` with empty `external_refs`. His externally verified wording, "an indiscriminate attack where a lot of civilians were involved", is materially weaker (no "war crime", "a lot" rather than "most"), so it is a separate claim, `abiad_indiscriminate_many_civilians`. I found no corpus seed for it.

`status` values: `confirmed` means established by later reporting or official records. `official-claim` means a statement by a named party, recorded as said. `disputed` means sources conflict. `false` means contradicted by the established mechanism. `later-contradicted` means the speaker's claim was overtaken by later admissions. `unverifiable` means single-source and never corroborated.

`corrects` / `corrected_by` links:
- `toll_pager_revised_12` → `toll_pager_day0_initial`
- `toll_walkie_revised_25_27` → `toll_walkie_day1`
- `mp_fadlallah_son_injured` → `mp_fadlallah_son_killed_false`
- `iran_ambassador_lost_eye` ↔ `iran_ambassador_minor_injury`
- `mossad_planted_explosives` and `petn_in_batteries` → `lithium_battery_overheat`; `mossad_planted_explosives` → `remote_hack_cause`
- `bulgaria_denies_pagers` → `bulgaria_norta_link`
- `made_in_israel_wapo` → `plan_15_years`
- `nasrallah_leaders_not_carrying` → `pagers_for_senior_members`
- `netanyahu_admits_approval_nov` → `herzog_denies_involvement` and `israel_no_comment`

## Deliberately left out

- **Post-Sep 20 war events** (the Aqil strike, Sep 23 strikes, Nasrallah's killing, the ground invasion). They are in the corpus, but they are not claims about the device attacks. Only links back to the attacks are kept (the Rafael "initial response", Aqil's pager injury).
- **Pager-themed jokes and controversies**: Rashida Tlaib cartoon, Chicago alderman post, Girdusky's "beeper" remark on CNN, Belarus "pager holocaust", Israeli social-media humour. These are meta-discourse, not propositions about the event. They could become a separate "reception" layer.
- **Per-country reactions without a legal claim**: Egypt, Jordan, Qatar's emir ("major crime"), Turkey, Hamas and PIJ statements, the Syrian FM, Maduro telling Venezuelans not to accept electronic Christmas gifts, Euro-Med Monitor, WHO. The Belgian deputy PM Petra De Sutter ("massive terror attack") appears only in Ynet and was dropped to stay under 80.
- **Speakers named in the brief but not separable**: Bernie Sanders. His move was arms-sale resolutions and a criticism of Netanyahu, not a statement on the pagers' legality. I found no clean pager-legality quote from him in the corpus.
- **Merged or dropped for size**: the US MQ-4C drone rumour (Abu Ali), explosions in Iraq (Al-Hadath via Ynet), BAC CEO's own "I'm just the intermediary", Taiwan's denial on components, Icom's denial, walkie-talkies bought five months earlier, the second wave "to prevent discovery", the northern-residents war goal, the AP and CNN accounts of when the US was told, the Lebanese UN mission letter (folded into `coded_message_trigger`), IRGC device ban, 95 wounded flown to Iran, Hezbollah's Sep 25 Qader-1 missile at "Mossad HQ", and the NYT/ABC 1-2 oz charge size (kept as a near-miss in `explosive_up_to_3g`).
- **Raisi's helicopter** (Kikar asks whether a booby-trapped pager downed it) is a speculative question headline, not a claim.

## Suspected but not confirmed

- **Hassan Fadlallah's son reported dead.** The web pass traced the false report to AFP, which first said he was killed and then corrected to "alive but injured". LBCI's correction ("death reports false", `lb_lbci_796516`) is the corpus trace. No primary record in the corpus asserts the death. The claim is kept with zero seeds so annotators can catch it in non-primary records or later corpora.
- **Iran's ambassador losing an eye.** This rests on the NYT's IRGC sources. The embassy called the reports false, its Sep 21 statement spoke of a hand injury with the eye "affected", and Amani reappeared on Dec 3 with visible injuries. It stays `disputed`.
- **19 IRGC dead in Syria**, **500 eye injuries / 300 fully blind** (MTV), **Aqil's pager injury** (Haaretz via LBCI/MTV) and **Israeli "real toll much higher"**: each is single-source and uncorroborated.
- **"Use it or lose it" timing.** Al-Monitor and Axios carried it on anonymous sources and nobody confirmed or denied it officially, so `forced_early_suspicion` is `unverifiable`, not `disputed`.
- **Panetta's venue.** The brief places the quote on Face the Nation. The external source is a CBS News Sunday Morning segment, and the corpus seed says only "an interview with CBS News on Sunday". The claim text follows the source.
- **"Planned for 15 years."** WaPo's Oct 5 timeline (walkie-talkies from 2015, pagers from 2022) does not support it. The original ABC source may have meant the wider supply-chain programme, so it is coded `disputed` rather than `false`.
- **Health workers among the dead.** The count varies. Abiad via AFP and Al-Manar say 4, LBCI and HRW say 2, and RND says staff were among the wounded.
- **Timing of US notice.** AP says Israel briefed the US afterwards. t-online, via Axios, says the US was informed beforehand. CNN says the US was told an operation was coming, without details. Washington says it was "not aware in advance". This is unresolved, so the claim was dropped rather than coded.

## Impressions on country-specific vs. universal (not counts)

These come from headline reading and keyword sweeps. The matrix may overturn them.

- **Probably universal, good controls.** Day-0 toll, children among the dead, Hezbollah blames Israel, Mossad planted explosives, Gold Apollo/BAC, "biggest security breach", Gallant's "new phase", the US "not involved" line, the lithium-battery theory on day 0, and the "forced early" leak. All four corpora seem to have each of these.
- **Lebanon-heavy or Lebanon-only.** Running and revised tolls (25/608, 12+27, 2,078 operations), Herzog's denial (it appears only in Lebanese records), Spain, the Rafael "initial response" framing, Al-Manar's martyr notices, Aqil's pager injury, the 500/300 eye figure, Abiad's "war crime because most were civilians", and Nasrallah framed as "severe blow / massacre" rather than "declaration of war". "Declaration of war" is the German, US and Israeli headline.
- **Israel-heavy or Israel-only.** Karhi's verse, ministers ordered to silence, the "4,000 targeted eliminations / deterrence" framing, the undercount claim, 19 IRGC dead, the 1,500 fighters figure (also in Lebanon, but absent from DE and US as far as I can find), victims framed as "terrorists", and the "both hands" design proudly quoted. I found no Türk or Borrell statement in the Israeli corpus.
- **Germany-heavy.** Explainers ("nicht ortbarer Handy-Vorläufer"), consumer fear ("Kann der Geheimdienst auch mein Handy sprengen?"), the legal debate (Völkerrecht pieces, CCW Protocol II, scholars divided), and Bild's "Hisbollah-Terroristen verwundet" framing. No PETN mention found in the German corpus.
- **US-heavy or US-only.** Fatima Abdullah by name (NYT and AP; otherwise a single line in an Al-Manar digest), Panetta's "form of terrorism", AOC's IHL statement, "senior US official says Israel behind", and the iPhone fact-check. The 15-year claim and the Reuters 1,500 figure seem absent from the US corpus even though both originated in US or wire media.
- **Victim identity is the likeliest splitter.** "Most were civilians" appears in Lebanon and in NBC. "Most were Hezbollah/terrorists" appears in Israel, Bild and WaPo. I have not checked how often both appear in the same record.

## Changes after v1

- 2026-10-05 (corpus v1.3): seed `us_yahoo_e4c4db9ea5` removed from `explosive_up_to_3g`. The record was excluded from the corpus as a Yahoo Singapore copy, not Yahoo News US; the claim keeps three seeds. Some seeds point at RND records that v1.3 marked as earlier versions of an article (`deduplication.relation = earlier_version`). They stay valid: readers saw those versions.
