# Israel step-5 adversarial review

## Verdict

**Fail.**

The corpus has several correct headline counts, but the scoped artifacts contain two extraction defects, a surviving exact-body duplicate, a tagging recall gap, an undocumented median-rounding issue, and one incorrect comparison-table figure.

## Findings

| # | Finding | Evidence | Severity | Suggested fix |
|---|---|---|---|---|
| 1 | Two normalized records retain identical bodies despite the note claiming no exact-body duplicates survived. | `data/israel/normalization-notes.md` says no exact-body duplicates survived. `il_abuali_75840` and `il_abuali_75841` in `data/israel/corpus-v1.jsonl` share body hash `93f5a986...81020`, with empty duplicate-cluster fields. | High | Deduplicate identical Abu Ali posts before analysis, or document why both should remain. |
| 2 | Kikar extraction includes page chrome, related links, and footer text. | `il_kikar_cc202167d1`, `data/israel/raw/kikar/cc202167d19aa8b4.html`. Stored body begins with `"החלפת מצב תצוגה כיכר השבת פנו אלינו"` and ends with `"עוד בצבא וביטחון... כל הזכויות שמורות"`, rather than article text alone. The stored date, `2024-09-18`, does match the raw page date. | High | Restrict extraction to the article container and remove navigation, recommendations, and footer blocks. |
| 3 | N12 extraction includes boilerplate before the article. | `il_n12_aaaa261aca`, `data/israel/raw/n12/aaaa261aca426bf1.html`. Stored body begins `"הדפסה Social-icon..."`; the raw article begins `"בלבנון מדווחים היום..."`. The date matches: `2024-09-17`. | High | Apply the same container and boilerplate-prefix cleanup used for article extraction elsewhere. |
| 4 | The tagging sweep misses clear pager-event items using singular or generic device wording. | In the 30-row untagged Ynet sample from `data/israel/enumeration/ynet-titles-0.csv` and `ynet-titles-1.csv`, these rows are untagged: `b1zo36v6c` ("המכשירים שהתפוצצו"), `bjcjrcc60` ("מכשירי רדיו"), `hygjdfv6a` (Iranian ambassador injured by a device), and `rjvbcko6c` ("פיצוץ מכשיר קשר"). These are event-related items that the listed families did not catch. | High | Add singular and generic device variants, including `מכשיר קשר`, `מכשירים`, `מכשירי רדיו`, and contextual combinations with `התפוצץ/פיצוץ` plus Lebanon or Hezbollah. |
| 5 | The tagging sample also contains clear false positives. | `il_kikar_361888163b`, CSV row URL ending `skpytm`, is a personal anecdote about a pager, not the 2024 event. `il_kikar_4e84dd272c`, URL ending `sk7wr9`, asks whether a booby-trapped pager caused Raisi's helicopter crash, also outside the event corpus. Both are tagged `strong` in `data/israel/enumeration/kikar-titles-0.csv`. A five-row check also included `il_makan_c9d393a825`, whose cartoon is event commentary, and event-related Ynet rows `il_ynet_4e4fba89cf` and `il_ynet_50c8c2a27c`. | Medium | Require event-window and Lebanon/Hezbollah context for generic `ביפר` hits; separate historical or speculative pager references from event coverage. |
| 6 | The body medians in normalization notes are truncated without explanation. | `data/israel/normalization-notes.md` reports Kikar `602w` and N12 `564w`. Recomputed medians from `data/israel/corpus-v1.jsonl` are Kikar `602.5` words across 22 records, and N12 `564.5` words across 10 records. | Low | Report standard medians as `602.5` and `564.5`, or state that medians are truncated. |
| 7 | The Lebanon agentive percentage in the headline table does not reproduce. | `data/analysis/lebanon-israel-comparison-v1.md` reports Lebanon agentive grammar as `45.0`. Using the term families in `data/scripts/build_viz.py` over the 338 primary Lebanon records gives 153/338 = **45.3%**. Israel reproduces at 87/153 = 56.9%. | Medium | Change the Lebanon value to `45.3`, then regenerate dependent prose or explain a different denominator. |

## Checks that reproduced

The following figures did reproduce from the scoped files:

- `corpus-candidates-v1.jsonl`: 138 rows, consisting of 92 strong, 43 related, and 3 fetch-failed records.
- Enumeration counts and tags: Ynet 13,492 with 50 strong and 42 related; N12 4,506 with 7 strong and 5 related; Kikar 5,229 with 20 strong and 2 related; Makan 647 with 2 strong and 10 related; Abu Ali 519 messages with 20 tagged. Sources: `data/israel/enumeration/*titles*.csv` and `abuali-messages.csv`.
- Normalized corpus: 153 primary records, with outlet counts Ynet 90, Kikar 22, Abu Ali 20, Makan 11, and N12 10.
- Document types: 78 articles, 55 `flash_or_lead`, and 20 Telegram posts.
- Languages: 142 Hebrew and 11 Arabic.
- Date coverage: 152 of 153 records dated, with 132 LD+JSON dates and 20 Telegram timestamps.
- Time slots: day_0 34, day_1 60, day_2 21, week_2 10, and first_month 8.

The five raw-page checks found matching dates in all five records, but only the Ynet and Makan samples were clean article-body extractions.
