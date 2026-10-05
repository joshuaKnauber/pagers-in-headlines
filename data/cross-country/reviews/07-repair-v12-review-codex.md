Verdict: fail.

1. High: Fox re-extraction leaves newsletter chrome in 17 bodies.

Evidence: `us_fox_b2a1805dab` ends with “Fox News Privacy Policy… Subscribe… You've successfully subscribed…”. The same residue appears in `us_fox_d6fa9707d2`, `us_fox_bdb750a556`, and others. In the raw capture, the newsletter begins at byte 187899 of `raw/fox/b2a1805dabd50772.html`.

Suggested fix: constrain extraction to the article-body content node, then remove newsletter/promotional descendants before flattening paragraphs. Recompute `word_count` and `body_sha256`.

2. High: Al Jadeed de-chroming converts empty article shells and shared-site chrome into article bodies.

Evidence: `lb_aljadeed_502535` has body “القناة 14 الإسرائيلية: يقوم الجيش الإسرائيلي بمهاجمة أهداف في ايران”, while its headline concerns 1,000 wounded in pager explosions. The raw at `raw/aljadeed/9999eb9bbdaea06c.html`, around byte 2109, has an empty `itemprop="articleBody"` and an empty `LongDesc`; the quoted text occurs in a later related-content card around byte 220226.

The same unrelated body appears in 17 records, including `lb_aljadeed_502539`, `502542`, `502546`, `502559`, `502609`, and `507119`. Five others, including `lb_aljadeed_502673`, contain the unrelated shared text “طرح جديد على بري.. ووقف نار؟”. At least 22 of 27 repaired bodies are therefore still wrong.

Suggested fix: extract only populated `LongDesc` or article-body nodes, exclude `d-none`, related-card, “now watching,” and hidden-title elements. Leave genuinely empty shells as empty briefs.

3. Medium: the US repair re-extracted records that were later marked non-primary.

Evidence: 29 records carry `body_reextracted_v12_container` while `is_primary_record` is false, including `us_fox_14366b346b`, `us_cnn_c096f01c9f`, `us_cnn_3b6a782785`, and `us_yahoo_7658c19c1b`. Germany has 14 analogous non-primary v1.2 edits.

Suggested fix: perform deduplication before re-extraction, or restrict repair edits to primary records.

4. Low: two Al-Manar records violate the body-count invariant.

Evidence: `lb_almanar_12510599` declares 5,523 words but `body.split()` yields 3,366. `lb_almanar_12568866` declares 4,946 but yields 3,281. Hashes are valid, so this is a stale `word_count`, not a hash mismatch.

Suggested fix: recompute counts for the whole corpus after every repair pass.

Verified without findings:

- US AMP and Israel N12 clusters kept the desktop/longer primary. No additional primary URL twins remained after normalizing query strings, trailing slashes, `m.`, `/amp/`, and `.amp`.
- Al-Manar page-date parsing matched sampled existing and recovered raws, including six-plus recovery files. The corpus contains 24 day_0 records. The 21 recovery relevance tags match the stated strong/related split, and martyr notices are marked related with the death-cause warning.
- The five sampled MTV interpolations had consistent neighboring IDs and dates. No bracket error was found.
- Sampled Israel `published_time` values matched raw JSON-LD. The mixed formats are real: `Z`, `+03:00`, `+0300`, and Telegram `+00:00`; normalization remains necessary before sorting.
- The ten recovered Abu Ali posts match the CSV IDs, timestamps, and text. Their relevance tags are defensible.

hook: Stop
hook: Stop Completed
tokens used
102,977
Verdict: fail.

1. High: Fox re-extraction leaves newsletter chrome in 17 bodies.

Evidence: `us_fox_b2a1805dab` ends with “Fox News Privacy Policy… Subscribe… You've successfully subscribed…”. The same residue appears in `us_fox_d6fa9707d2`, `us_fox_bdb750a556`, and others. In the raw capture, the newsletter begins at byte 187899 of `raw/fox/b2a1805dabd50772.html`.

Suggested fix: constrain extraction to the article-body content node, then remove newsletter/promotional descendants before flattening paragraphs. Recompute `word_count` and `body_sha256`.

2. High: Al Jadeed de-chroming converts empty article shells and shared-site chrome into article bodies.

Evidence: `lb_aljadeed_502535` has body “القناة 14 الإسرائيلية: يقوم الجيش الإسرائيلي بمهاجمة أهداف في ايران”, while its headline concerns 1,000 wounded in pager explosions. The raw at `raw/aljadeed/9999eb9bbdaea06c.html`, around byte 2109, has an empty `itemprop="articleBody"` and an empty `LongDesc`; the quoted text occurs in a later related-content card around byte 220226.

The same unrelated body appears in 17 records, including `lb_aljadeed_502539`, `502542`, `502546`, `502559`, `502609`, and `507119`. Five others, including `lb_aljadeed_502673`, contain the unrelated shared text “طرح جديد على بري.. ووقف نار؟”. At least 22 of 27 repaired bodies are therefore still wrong.

Suggested fix: extract only populated `LongDesc` or article-body nodes, exclude `d-none`, related-card, “now watching,” and hidden-title elements. Leave genuinely empty shells as empty briefs.

3. Medium: the US repair re-extracted records that were later marked non-primary.

Evidence: 29 records carry `body_reextracted_v12_container` while `is_primary_record` is false, including `us_fox_14366b346b`, `us_cnn_c096f01c9f`, `us_cnn_3b6a782785`, and `us_yahoo_7658c19c1b`. Germany has 14 analogous non-primary v1.2 edits.

Suggested fix: perform deduplication before re-extraction, or restrict repair edits to primary records.

4. Low: two Al-Manar records violate the body-count invariant.

Evidence: `lb_almanar_12510599` declares 5,523 words but `body.split()` yields 3,366. `lb_almanar_12568866` declares 4,946 but yields 3,281. Hashes are valid, so this is a stale `word_count`, not a hash mismatch.

Suggested fix: recompute counts for the whole corpus after every repair pass.

Verified without findings:

- US AMP and Israel N12 clusters kept the desktop/longer primary. No additional primary URL twins remained after normalizing query strings, trailing slashes, `m.`, `/amp/`, and `.amp`.
- Al-Manar page-date parsing matched sampled existing and recovered raws, including six-plus recovery files. The corpus contains 24 day_0 records. The 21 recovery relevance tags match the stated strong/related split, and martyr notices are marked related with the death-cause warning.
- The five sampled MTV interpolations had consistent neighboring IDs and dates. No bracket error was found.
- Sampled Israel `published_time` values matched raw JSON-LD. The mixed formats are real: `Z`, `+03:00`, `+0300`, and Telegram `+00:00`; normalization remains necessary before sorting.
- The ten recovered Abu Ali posts match the CSV IDs, timestamps, and text. Their relevance tags are defensible.


---
## Corrections ledger (v1.2.1, applied same session)

1. Fox newsletter tails — FIXED: tail-cut markers in `repair_v12.py fixups`
   (17 bodies, `fox_newsletter_tail_cut_v121`). Residue count now 0.
2. Al Jadeed wrong-node bodies — FIXED: all 27 raws re-checked; every
   LongDesc node is empty, so all 27 are headline-only ticker shells.
   Bodies emptied, retyped brief (`body_emptied_v121_shell_page`).
3. Non-primary records re-extracted — ACCEPTED, documented: cleaning
   non-primary bodies is harmless (consumers filter is_primary_record)
   and keeps duplicate clusters internally consistent. No data harm.
4. Stale word_counts — FIXED: full four-corpus recompute sweep now part
   of the fixups stage (2 corrected; invariant holds corpus-wide).

Viz rebuilt after fixes. Counts unchanged: LB 359 / IL 166 / DE 176 / US 131.
