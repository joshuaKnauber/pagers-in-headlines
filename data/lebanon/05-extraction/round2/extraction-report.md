# lebanon round 2 extraction

Offline. Text is copied from the saved HTML. Nothing was translated or filled in by guesswork.

## Gate

An outlet is usable when all six checks pass on at least 95% of its bodies and no `new_wrong` row remains. Bodies are corpus rows with a raw file plus gap rows read from a cached page. `no_raw` rows are not in the denominator.

Check 2, 3 and 5 for headline-only items (empty body, `brief` / `live_ticker`, including Al Jadeed `headline_only_empty_container`): there is no article text, so the description is not required in a body, truncation does not apply, and paragraph order is not applicable.

Telegram posts: the lead is the message (`js-message_text`), not the channel `og:description`. Truncation passes when that whole node was taken; posts often have no final period. Paragraph order is not applicable (no JSON-LD `articleBody`).

Other outlets: check 2 uses `og:description`, then the JSON-LD description, then Al Jadeed ShortDesc. Opening words (first 8, or first 6) must sit in the first 400 characters. A description whose words never occur in the article is a rewritten deck; the check then passes as `description_is_rewrite` unless the JSON-LD `articleBody` lead itself is missing from that window. A deck that does occur, but only after the first 400 characters, fails.

Check 3: a container taken whole is complete even when the page does not end with a period. A wire credit, `المصدر:` / `Source:`, or a trailing year also counts as a finished ending. A recirculation cut must still leave a finished ending. Where JSON-LD `articleBody` is at least 40 characters, the body must be at least 90% of that length.

Check 1 ignores a repeated sentence when that sentence is inside the same page's JSON-LD `articleBody` (the article repeating, not furniture).

Check 6, `container_coverage`: the extracted body must hold at least 90% of the words of the outlet's full article container (Kikar: the article island's text blocks; N12: the whole `itemprop="articleBody"`, h4 and lists included; Makan: `article-content`; LBCI: `LongDesc`; MTV: `articles-report`; Al Jadeed: ShortDesc + LongDesc; Al Manar: the balanced `article-content` div; NNA: `fulltextarticle-container` without the agency sign-off; Ynet: `ArticleBodyComponent`). The container is measured on the page, not by the extraction rule's end marker. Captions, players, scripts, share buttons and the N12 typo-report label are not counted. A page with no such container, or an empty one, passes as not applicable and is counted separately below. Abu Ali (Telegram) is not applicable. Ynet and any page that has a JSON-LD `articleBody` also face check 3 against it.

| outlet | usable | bodies | all six | no_chrome | lead_present | not_truncated | no_duplication | order | container_coverage | new_wrong |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| lbci | yes | 233 | 233/233 (100.0%) | 233/233 (100.0%) | 233/233 (100.0%) | 233/233 (100.0%) | 233/233 (100.0%) | 233/233 (100.0%) | 233/233 (100.0%) | 0 |
| mtv | yes | 341 | 337/341 (98.8%) | 337/341 (98.8%) | 341/341 (100.0%) | 341/341 (100.0%) | 341/341 (100.0%) | 341/341 (100.0%) | 341/341 (100.0%) | 0 |
| aljadeed | yes | 136 | 136/136 (100.0%) | 136/136 (100.0%) | 136/136 (100.0%) | 136/136 (100.0%) | 136/136 (100.0%) | 136/136 (100.0%) | 136/136 (100.0%) | 0 |
| almanar | yes | 121 | 121/121 (100.0%) | 121/121 (100.0%) | 121/121 (100.0%) | 121/121 (100.0%) | 121/121 (100.0%) | 121/121 (100.0%) | 121/121 (100.0%) | 0 |
| nna | yes | 7 | 7/7 (100.0%) | 7/7 (100.0%) | 7/7 (100.0%) | 7/7 (100.0%) | 7/7 (100.0%) | 7/7 (100.0%) | 7/7 (100.0%) | 0 |

**95% gate, all six checks:** pass: lbci, mtv, aljadeed, almanar, nna. Do not pass: none.



## Gap rows

Rows: 464. ok: 464. failed: 0.

| outlet | rows | ok | failed | failure reasons |
|---|---:|---:|---:|---|
| lbci | 124 | 124 | 0 | — |
| mtv | 215 | 215 | 0 | — |
| aljadeed | 62 | 62 | 0 | — |
| almanar | 58 | 58 | 0 | — |
| nna | 5 | 5 | 0 | — |

Al Jadeed gap pages read: 62. Non-empty LongDesc: 36. ShortDesc only: 4. Empty container (`headline_only_empty_container`): 22. Rows with a body: 40.

Where a stored Al Jadeed body is longer than the page, it is ShortDesc plus LongDesc plus a second copy of LongDesc. The page has each field once. Example: `lb_aljadeed_503441` matches short+long+long at 1.000 and short+long at 0.675. The repeated LongDesc is not on the page. Where the container is empty, as on `lb_aljadeed_502514`, the stored paragraph is not in the HTML. Both are `stored_wrong`.
Al Jadeed `stored_wrong`: 0 repeated-LongDesc, 0 empty container. Total 0.

## Regression diagnostic

Ratio against the stored body, whitespace-collapsed, first 3,000 characters. Not a gate. Rows below 0.90 are in `regression-adjudication.csv`.

| outlet | n (non-empty stored) | median | share ≥ 0.90 |
|---|---:|---:|---:|
| lbci | 195 | 1.000 | 195/195 (100.0%) |
| mtv | 172 | 1.000 | 172/172 (100.0%) |
| aljadeed | 70 | 1.000 | 70/70 (100.0%) |
| almanar | 70 | 1.000 | 48/70 (68.6%) |
| nna | 6 | 1.000 | 6/6 (100.0%) |

Adjudication: stored_wrong 22, new_wrong 0, both 0.
By outlet: almanar stored_wrong 22, new_wrong 0, both 0.

LBCI `stored_wrong`: 0 rows where the extra text is inside `class="LongDesc"` (the rest of the article, or a tweet embed including its `— handle date` citation). That text is part of the item as published. 0 rows have an empty stored body and a real LongDesc article. Tags and the next-story block sit after `article_details_end_of_scroll`, outside LongDesc. An empty LongDesc is no longer filled from `itemprop=articleBody`.

## Truncation fix: before and after

Before: Al Manar read the first `article-content` div up to the first `</div>`, which is the wrapper of the first embedded video, so every article with an embedded video lost the text after it. After: the balanced `article-content` div.

| outlet | pages | median words before | median words after | after > 1.25x before | after < before |
|---|---:|---:|---:|---:|---:|
| almanar | 121 | 41 | 129 | 26 | 0 |

Per page, almanar, the 29 pages whose length changed (92 unchanged, not listed) (id: before -> after words):

`lb_almanar_12481977` 567 -> 919; `lb_almanar_12482461` 1405 -> 3119; `lb_almanar_12482516` 76 -> 194; `lb_almanar_12482857` 36 -> 236; `lb_almanar_12487444` 193 -> 591; `lb_almanar_12487763` 37 -> 473; `lb_almanar_12488126` 107 -> 276; `lb_almanar_12488203` 39 -> 182; `lb_almanar_12488269` 40 -> 70; `lb_almanar_12488324` 42 -> 72; `lb_almanar_12488379` 176 -> 311; `lb_almanar_12488544` 130 -> 419; `lb_almanar_12488962` 99 -> 130; `lb_almanar_12492031` 111 -> 358; `lb_almanar_12493384` 173 -> 479; `lb_almanar_12494517` 73 -> 1144; `lb_almanar_12496068` 90 -> 93; `lb_almanar_12497828` 28 -> 370; `lb_almanar_12498895` 32 -> 393; `lb_almanar_12504384` 207 -> 608; `lb_almanar_12504582` 101 -> 159; `lb_almanar_12504604` 195 -> 555; `lb_almanar_12505649` 995 -> 1381; `lb_almanar_12506265` 75 -> 549; `lb_almanar_12509378` 739 -> 1094; `lb_almanar_12509499` 272 -> 275; `lb_almanar_12509598` 148 -> 151; `lb_almanar_12511226` 41 -> 659; `lb_almanar_12512293` 105 -> 261

## container_coverage by outlet

Pass = body words >= 90% of container words. n/a = Telegram, no container on the page, or an empty container (headline-only). `measured` is the number of pages with a non-empty container. Min and median are body/container over those pages.

| outlet | pages | pass | fail | n/a | measured | pass of measured | min | median |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| lbci | 233 | 233 | 0 | 38 | 195 | 195/195 (100.0%) | 1.000 | 1.000 |
| mtv | 341 | 341 | 0 | 169 | 172 | 172/172 (100.0%) | 1.000 | 1.000 |
| aljadeed | 136 | 136 | 0 | 66 | 70 | 70/70 (100.0%) | 1.000 | 1.000 |
| almanar | 121 | 121 | 0 | 51 | 70 | 70/70 (100.0%) | 1.000 | 1.000 |
| nna | 7 | 7 | 0 | 1 | 6 | 6/6 (100.0%) | 1.000 | 1.000 |

No page fails container_coverage.

Other truncation found with this check: Al Manar (fixed above). LBCI, MTV, Al Jadeed and NNA bodies already equal their container (minimum 1.000 in the table).

## What changed since round 1

- The 0.90 regression ratio is a diagnostic. The gate is the six checks above.
- Truncation fix: Kikar and N12 bodies are now the whole article container; Al Manar stops at the balanced `article-content` div. See the next section.
- Gap rows are read from `round2/gap-manifest-input.csv`. Gap rows that the corpus has since accepted are not counted twice in the gate.
- Al Jadeed is no longer `regression_failed`. Empty ShortDesc and LongDesc are `ok` briefs with `headline_only_empty_container`. A non-empty LongDesc is extracted once.
- Every corpus row was re-extracted to `reextract-v1.jsonl`. `corpus.jsonl` was not modified.
- Abu Ali records carry `footer_comment_link`. The trailing comment-link footer is removed from body and title.
- An iframe whose title attribute contains markup is dropped as an element, so its attributes are not article text.
- LBCI body is `class="LongDesc"` only. An empty LongDesc stays empty.

## Open problems

- mtv check 1: `Watch the attached video for more.` appears under 4 headlines (e.g. lb_mtv_1482883). It is inside the article text on those pages, so it stays.

Re-extract: 838 corpus rows, ok 838, no_raw 0.
