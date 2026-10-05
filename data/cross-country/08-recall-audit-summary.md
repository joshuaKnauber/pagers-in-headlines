# Recall audit: summary across countries (2026-10-04/05)

Question: of what each outlet published between Sep 17 and Sep 24 2024 that mentions
the pager or walkie-talkie attacks, how much is in `corpus.jsonl`, and why is
the rest missing? Per-country detail is in `data/<country>/08-recall-audit/recall-audit-notes.md`.

Two methods were used, so the per-country recall figures are close but not
directly comparable:

- **Lebanon, Israel:** census recall. Corpus items in the window divided by
  (corpus items + missing items found + an extrapolation from sampled strata
  that were not fully checked).
- **Germany, US:** reference-set recall. Items found by independent routes
  (Media Cloud full text, GDELT, outlet-native listings, archived homepages,
  live-blog paths), each verified against its body text, then matched against
  the corpus.

Both split items into **central** (the attack is in the headline, description or
first paragraph) and **mention** (it comes up in the body only).

## Recall per outlet

| country | outlet | central | mention | all | reference strength |
|---|---|---|---|---|---|
| Lebanon | LBCI | 53% | 0% | 45% | medium |
| Lebanon | MTV | 40% | 0% | 33% | medium |
| Lebanon | Al Jadeed | 50% | 0% | 43% | medium |
| Lebanon | Al-Manar | 57% | 10% | 43% (≈29%) | strong (Media Cloud + GDELT) |
| Lebanon | NNA | – | – | – | none |
| Israel | Ynet | 54% | 0% | 40% | medium (GDELT 51%) |
| Israel | N12 | 22% | 0% | ~5% | weak, extrapolated |
| Israel | Kikar | 77% | 0% | 38% | medium |
| Israel | Makan | 90% | 0% | ~58% | none independent |
| Israel | Abu Ali | 16% | 7% | 15% | strong (live channel dump) |
| Germany | Bild | 76% | 20% | 58% | strong |
| Germany | ntv | 19% | 0% | 14% | strong |
| Germany | RND | 62% | 18% | 42% | strong |
| Germany | RTL | 25% | – | 25% | weak (8 items) |
| Germany | Spiegel | 55% | 14% | 44% | strong |
| Germany | Tagesschau | 56% | 12% | 42% | strong |
| Germany | t-online | 82% | 36% | 64% | medium |
| Germany | WELT | 30% | 0% | 22% | strong |
| Germany | ZDFheute | 100% | 75% | 91% | weak (11 items) |
| US | ABC | 7% | 0% | 6% | medium |
| US | AP | 0% | 0% | 0% (fetch bug) | medium |
| US | CBS | 23% | 0% | 19% | medium |
| US | CNN | 61% | 0% | 41% | strong |
| US | Fox | 58% | 40% | 53% | strong |
| US | NBC | 50% | 29% | 45% | strong |
| US | NYT | 5% | 8% | 6% | strong (daily sitemap) |
| US | Reuters | – | – | – | none (not auditable) |
| US | USA Today | 8% | 0% | 5% | medium |
| US | WaPo | – | – | (24%) | none independent (4 items) |
| US | Yahoo | 6% | 1% | 5% | weak (3 of 430 items are Yahoo's own) |

US overall: 21% without Yahoo (78 of 369), 12% with it. Yahoo is almost entirely
syndicated copy (wire services and partner outlets), so its figure is not US recall.

All figures are lower bounds on what readers saw: the relevance tests are lexical
and miss allusive wording ("the operation in Lebanon", "العدوان").

## What the audits agree on

1. **Mentions are almost entirely missing, in every country.** Selection keyed on
   headline or URL words, so articles that discuss the attacks only in the body
   (Nasrallah's speech, the escalation from Sep 20, UN debates) were never
   candidates. These are where many claims (toll updates, condemnations, denials)
   reached readers.
2. **Enumeration lost whole slices.** ntv has no URLs first captured on Sep 21–22,
   WELT was starved by its crawler block, N12 returned block pages for 1,152 URLs,
   MTV has 1,836 slug-less URLs that were never checked, and regexes excluded
   whole sections (WELTplus, dpa newsticker, Tagesschau `/newsticker/`, Ynet
   print sections, Spiegel netzwelt/kultur/panorama).
3. **Live blogs and tickers are missing as a format.** Tagesschau, ZDF, RND,
   t-online, N12, Kikar flashes. Most can only be recovered from in-window
   Wayback captures; live pages now show 2025/26 content.
4. **Missing spellings.** Al-Manar's البايجر and the indefinite أجهزة اتصال were
   not in the term lists.
5. **Paywall teasers were dropped as off-topic** when the teaser lacked an event
   term (Spiegel+, WELTplus).
6. **Fetch failures were recorded as "not relevant".** Every AP candidate was a
   Cloudflare challenge page with an empty body; WaPo, NYT and Reuters
   candidates were "Access Denied" or "no capture" pages. Only 4 of 36 dropped
   US candidates were real rejections. The pipeline needs a block-page check
   before relevance is judged.

## Gap manifests (items ready to collect)

| country | items | notes |
|---|---|---|
| Lebanon | 464 | plus TV bulletin intros (LBCI, Al-Manar, MTV compilation), An-Nahar, Al-Akhbar PDFs |
| Israel | 309 | Abu Ali via live `t.me/s` |
| Germany | 196 | 189 verified + 7 live blogs not readable from capture |
| US | 721 | 312 without Yahoo; incl. 20 ABC live blogs with empty captures |

## Corpus fixes for v1.3 (listed by the audits, not applied yet)

**Lebanon**
- `lb_lbci_797960`: off-topic (wireless earbuds), drop.
- `lb_aljadeed_507118`: different event (Oct 6 radio-interception report), drop or retag.
- Near-duplicate primary pairs: `lb_aljadeed_502815`/`502819`, `lb_aljadeed_502553`/`502564`.
- Missing `published_at`: `lb_mtv_1490054`, `lb_mtv_1490462` (Sep 26–27 by ID),
  `lb_nna_722276` (Sep 18), `lb_nna_722542` (Sep 19), dates in first body line.
- Al-Manar martyr notices (11 records): keep flagged, exclude from "about the attack".

**Israel**
- `il_ynet_35be01752a`: different event (Sep 23 evacuation calls), drop or retag.
- `il_n12_ae690238dc`: podcast page typed `article`, retype.
- `il_n12_42fc90d847`: missing `published_at`.
- `il_abuali_75669`: probably a separate incident (Damascus car charge), retag.
- Abu Ali first post is 75653 at 12:57:18 UTC, before N12's 12:59 item; add it and
  correct the v1.2 "N12 first" note.

**Germany**
- RND duplicate primary pairs (same article ID, two slugs): `8077ee3c89`=`2976713b85`,
  `9bfa7a57f3`=`9839d97395`, `a34b40e8b3`=`01d7465f51`, `e494be678a`=`8a981c41ba`.
- 31 `related` records without any device wording (list in
  `data/germany/08-recall-audit/raw/corpus-issues.csv`): downgrade to context.
- `ge_tonline_1e9c010a33`: rolling newsblog stored as one article; retype `live_blog`.
- ntv `der_tag` ticker entries typed `article`: retype.

**US**
- 7 CNN video pages from Sep 27 to Oct 4 (`988ba91188`, `1d5d0054f9`, `e9df9fa49e`,
  `74950daf60`, `af080302bd`, `7d156f4ba5`, `e25861e961`) and `us_cbs_8d3f0e89ac`:
  no device wording, downgrade to context.
- Out of window: `us_cbs_deca8d7e0f` (Oct 31), `us_nbc_d7d1591943` (Oct 29).
- Out of scope: `us_cbs_b6fde07557` (CBS Chicago local), Yahoo regional and finance
  copies `us_yahoo_6b6ad5ce8c`, `ae4f6eb3f5`, `e4c4db9ea5`.
- `us_yahoo_5f33d95679`: 36-word item typed `article`.
- Re-collect all AP candidates from Wayback (live fetches return Cloudflare pages).

## Next steps

1. v1.3 repair pass with the fixes above.
2. Gap fill with full-text selection: outlet-native listings as the manifest of
   record, topic re-sweep with body check, live blogs split into timestamped
   entries, wire feeds and teletext as their own document type.
3. Re-run the audits, publish a completeness figure per outlet.
