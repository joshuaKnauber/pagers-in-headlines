# israel round 2 extraction

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
| ynet | yes | 221 | 215/221 (97.3%) | 221/221 (100.0%) | 218/221 (98.6%) | 221/221 (100.0%) | 218/221 (98.6%) | 221/221 (100.0%) | 221/221 (100.0%) | 0 |
| n12 | no | 60 | 54/60 (90.0%) | 54/60 (90.0%) | 60/60 (100.0%) | 60/60 (100.0%) | 60/60 (100.0%) | 60/60 (100.0%) | 60/60 (100.0%) | 0 |
| kikar | no | 50 | 45/50 (90.0%) | 46/50 (92.0%) | 49/50 (98.0%) | 50/50 (100.0%) | 50/50 (100.0%) | 50/50 (100.0%) | 50/50 (100.0%) | 0 |
| makan | no | 17 | 16/17 (94.1%) | 17/17 (100.0%) | 17/17 (100.0%) | 17/17 (100.0%) | 16/17 (94.1%) | 17/17 (100.0%) | 17/17 (100.0%) | 0 |
| abuali | yes | 93 | 93/93 (100.0%) | 93/93 (100.0%) | 93/93 (100.0%) | 93/93 (100.0%) | 93/93 (100.0%) | 93/93 (100.0%) | 93/93 (100.0%) | 0 |

**95% gate, all six checks:** pass: ynet, abuali. Do not pass: n12, kikar, makan.

- n12: 54/60 = 90.0%. Failing pages: 6 (by check: no_chrome 6). Of these, 6 fail only because a sentence of the publisher's own text appears in 3 or more articles (check 1) or twice in one article (check 4). Those sentences are inside the article container on the page, so they are not chrome; the failure stays counted and the check was not loosened. Information, not the gate: without the 6 repeated-text pages the rate would be 100.0%.
- kikar: 45/50 = 90.0%. Failing pages: 5 (by check: lead_present 1, no_chrome 4). Of these, 4 fail only because a sentence of the publisher's own text appears in 3 or more articles (check 1) or twice in one article (check 4). Those sentences are inside the article container on the page, so they are not chrome; the failure stays counted and the check was not loosened. Other failures: `il_kikar_361888163b`. Information, not the gate: without the 4 repeated-text pages the rate would be 98.0%.
- makan: 16/17 = 94.1%. Failing pages: 1 (by check: no_duplication 1). Of these, 1 fail only because a sentence of the publisher's own text appears in 3 or more articles (check 1) or twice in one article (check 4). Those sentences are inside the article container on the page, so they are not chrome; the failure stays counted and the check was not loosened. Information, not the gate: without the 1 repeated-text pages the rate would be 100.0%.


## Gap rows

Rows: 301. ok: 301. failed: 0.

| outlet | rows | ok | failed | failure reasons |
|---|---:|---:|---:|---|
| ynet | 127 | 127 | 0 | — |
| n12 | 50 | 50 | 0 | — |
| kikar | 28 | 28 | 0 | — |
| makan | 6 | 6 | 0 | — |
| abuali | 90 | 90 | 0 | — |

Abu Ali `footer_comment_link` true on 81 of 90 gap rows. The trailing footer `כדי להגיב לכתבה לחצו כאן` is removed from body and title.

## Regression diagnostic

Ratio against the stored body, whitespace-collapsed, first 3,000 characters. Not a gate. Rows below 0.90 are in `regression-adjudication.csv`.

| outlet | n (non-empty stored) | median | share ≥ 0.90 |
|---|---:|---:|---:|
| ynet | 221 | 1.000 | 221/221 (100.0%) |
| n12 | 60 | 0.994 | 47/60 (78.3%) |
| kikar | 50 | 0.460 | 2/50 (4.0%) |
| makan | 17 | 1.000 | 17/17 (100.0%) |
| abuali | 93 | 0.928 | 54/93 (58.1%) |

Adjudication: stored_wrong 100, new_wrong 0, both 0.
By outlet: n12 stored_wrong 13, new_wrong 0, both 0; kikar stored_wrong 48, new_wrong 0, both 0; abuali stored_wrong 39, new_wrong 0, both 0.

`il_makan_5961802f18`: the article is the `article-content` paragraphs. The stored body is the `og:description` line. Classification: `stored_wrong`.

## Truncation fix: before and after

Before: the old rule. Kikar read `<p>` up to the first `</article>`, which is the first recommended-story card inside the article, so the text after that card was lost. N12 read the `<p>` nodes of `articleBody` through `</article>` and dropped every `<p>` under 4 words, h4 sub-headings, lists and quote blocks. After: Kikar is every html block of the article's own island (`contentItems`), in order; image and video items (captions, credits) and the recommended-story and next-article payloads are not read. N12 is the whole `articleBody` section in page order (p, h3/h4, ul/ol/li, quote blocks, bubble spans), without figures and captions, players, scripts and the typo-report label. Block text keeps a word that the page splits over two inline `<span>`s whole.

| outlet | pages | median words before | median words after | after > 1.25x before | after < before |
|---|---:|---:|---:|---:|---:|
| kikar | 50 | 134 | 273 | 41 | 4 |
| n12 | 60 | 380 | 416 | 6 | 7 |

Per page, kikar (id: before -> after words):

`il_kikar_0c6a9524ba` 126 -> 157; `il_kikar_0e0bc3ddb6` 122 -> 16; `il_kikar_13671679b8` 111 -> 334; `il_kikar_13b0dde8ca` 38 -> 103; `il_kikar_14dc0a19c0` 156 -> 2516; `il_kikar_1a02f16d3d` 129 -> 755; `il_kikar_1ac017e03f` 80 -> 257; `il_kikar_244fafc3e5` 159 -> 197; `il_kikar_29e9069f80` 144 -> 279; `il_kikar_361888163b` 137 -> 370; `il_kikar_3e79e36d73` 148 -> 235; `il_kikar_494070c4cd` 142 -> 452; `il_kikar_49f3092a6e` 195 -> 332; `il_kikar_4e84dd272c` 32 -> 97; `il_kikar_5cdcb9b74d` 106 -> 552; `il_kikar_5d1e3e6c64` 146 -> 357; `il_kikar_6a30f10d58` 184 -> 488; `il_kikar_6badddcef3` 97 -> 226; `il_kikar_6d7b5f3531` 160 -> 416; `il_kikar_6db24871ed` 177 -> 328; `il_kikar_6dcf890b8d` 144 -> 234; `il_kikar_6e4e7135a2` 149 -> 209; `il_kikar_786735c51c` 35 -> 159; `il_kikar_799595ea13` 171 -> 211; `il_kikar_7eebe1f245` 104 -> 91; `il_kikar_7fd29c5ea9` 153 -> 224; `il_kikar_879a67a526` 145 -> 233; `il_kikar_961c096c9b` 118 -> 313; `il_kikar_99fcbbf3a4` 63 -> 1277; `il_kikar_9c9a5a5651` 181 -> 497; `il_kikar_a0bb73b7f0` 196 -> 422; `il_kikar_a3c1ac80e7` 165 -> 164; `il_kikar_a5de7caca9` 126 -> 341; `il_kikar_a870a3c508` 89 -> 217; `il_kikar_aabf81ec32` 141 -> 666; `il_kikar_aaea8f40fb` 104 -> 279; `il_kikar_aeeede0432` 94 -> 218; `il_kikar_b067effbfb` 123 -> 233; `il_kikar_b9d894e05c` 123 -> 141; `il_kikar_bcb1abbf76` 172 -> 272; `il_kikar_c94cfa701e` 94 -> 234; `il_kikar_c9c67fb992` 114 -> 247; `il_kikar_cc202167d1` 219 -> 274; `il_kikar_ce967787da` 161 -> 278; `il_kikar_d3a1e9eecb` 105 -> 288; `il_kikar_d6e00f2704` 241 -> 396; `il_kikar_d703468d66` 120 -> 114; `il_kikar_d7845b3b06` 81 -> 82; `il_kikar_e0cc9bc44d` 130 -> 483; `il_kikar_eb9350c551` 228 -> 312

Per page, n12 (id: before -> after words):

`il_n12_02520fb7f9` 169 -> 177; `il_n12_08ad9b5493` 388 -> 414; `il_n12_0a5b2f99f1` 389 -> 467; `il_n12_0f576e9b1d` 100 -> 139; `il_n12_12d9f137b1` 253 -> 263; `il_n12_15a860866b` 185 -> 192; `il_n12_193387a0fb` 308 -> 311; `il_n12_27292aa7ef` 442 -> 452; `il_n12_2acde6f9fc` 469 -> 467; `il_n12_2e94a0a351` 53 -> 642; `il_n12_2f30f14e91` 422 -> 428; `il_n12_33d664e870` 37 -> 536; `il_n12_347fc26d28` 370 -> 370; `il_n12_36b229361f` 399 -> 399; `il_n12_38d0626a69` 199 -> 199; `il_n12_3e5c8cc0a7` 401 -> 417; `il_n12_42fc90d847` 920 -> 941; `il_n12_4ba6ea59c3` 297 -> 280; `il_n12_4c0d7d27fa` 766 -> 849; `il_n12_4dc0f20d7a` 267 -> 279; `il_n12_64f167c508` 438 -> 438; `il_n12_6b4a8e9325` 214 -> 214; `il_n12_6ee25e3b1e` 400 -> 400; `il_n12_736f94fca9` 350 -> 350; `il_n12_754d32c052` 596 -> 596; `il_n12_76744d2a92` 341 -> 964; `il_n12_76f727ead4` 464 -> 489; `il_n12_829789f643` 371 -> 371; `il_n12_838df8b562` 443 -> 500; `il_n12_9b01bc3830` 341 -> 382; `il_n12_9cf7909c35` 531 -> 538; `il_n12_9d3c27cce6` 582 -> 593; `il_n12_9f110d7654` 643 -> 648; `il_n12_a4f57d1f60` 417 -> 421; `il_n12_a869f38ee2` 564 -> 589; `il_n12_a8b4489588` 432 -> 437; `il_n12_aaaa261aca` 255 -> 255; `il_n12_aadc675d4c` 764 -> 774; `il_n12_ae690238dc` 8 -> 8; `il_n12_b34caca309` 105 -> 499; `il_n12_b49e5d83f8` 483 -> 528; `il_n12_bec6437287` 150 -> 150; `il_n12_c02759b820` 1397 -> 1398; `il_n12_c5b7aedb1f` 155 -> 148; `il_n12_c9a949c217` 194 -> 193; `il_n12_d0fdeb3979` 232 -> 228; `il_n12_d1c4dc77fb` 361 -> 363; `il_n12_d47355e95d` 329 -> 331; `il_n12_d7f6dbf994` 566 -> 566; `il_n12_d984f894c7` 189 -> 188; `il_n12_dc77d87074` 455 -> 545; `il_n12_e17bf14d31` 227 -> 227; `il_n12_e2fc044fbb` 287 -> 287; `il_n12_eaebf45454` 685 -> 695; `il_n12_ef7c0cb29f` 254 -> 254; `il_n12_ef967a5bd6` 479 -> 498; `il_n12_f3a7ae0178` 825 -> 835; `il_n12_f3acb2550e` 244 -> 244; `il_n12_fb580dd849` 464 -> 660; `il_n12_ffc3325683` 402 -> 367

Pages where the new body is shorter than the old one (the old body held a caption or a short block the new rule leaves out): `il_kikar_0e0bc3ddb6` 122 -> 16; `il_kikar_a3c1ac80e7` 165 -> 164; `il_kikar_d703468d66` 120 -> 114; `il_kikar_7eebe1f245` 104 -> 91; `il_n12_ffc3325683` 402 -> 367; `il_n12_4ba6ea59c3` 297 -> 280; `il_n12_d984f894c7` 189 -> 188; `il_n12_c5b7aedb1f` 155 -> 148; `il_n12_c9a949c217` 194 -> 193; `il_n12_d0fdeb3979` 232 -> 228; `il_n12_2acde6f9fc` 469 -> 467.

Does the body now name the attack? `before` is the old rule, `now` the new one. Match words: ביפר, זימונית, מכשירי (ה)קשר, פיצוץ/פיצוצי (ה)מכשירים. The quote is the first matching sentence of the new body, preferring one the old body did not contain.

| id | where | words before -> now | named before | named now | sentence now in the body |
|---|---|---|---|---|---|
| `il_kikar_eb9350c551` | corpus | 228 -> 312 | no | yes | `לדבריו, ״מדינת ישראל צריכה לפעול מעצמה, ולנצל את המומנטום של מתקפת הביפרים כדי להנחית מכה אנושה על חיזבאללה ולהכריע את ארגון הטרור.` |
| `il_kikar_29e9069f80` | corpus | 144 -> 279 | no | yes | `ההסלמה הביטחונית מתרחשת אחרי פיצוצי הביפרים ומכשירי הקשר של חיזבאללה המיוחסים לישראל.` |
| `il_kikar_6a30f10d58` | corpus | 184 -> 488 | no | yes | `"האויב הישראלי פוצץ אלפי ביפרים וגרם למותם של עשרות ולפציעתם של אלפים.` |
| `il_kikar_d6e00f2704` | corpus | 241 -> 396 | no | yes | `"האויב הישראלי פוצץ אלפי ביפרים וגרם למותם של עשרות ולפציעתם של אלפים.` |
| `il_kikar_14dc0a19c0` | corpus | 156 -> 2516 | no | yes | `רחפן תיעד: המוסד השתלט על משלוח הביפרים ומלכד אותם` |
| `il_kikar_1ac017e03f` | corpus | 80 -> 257 | no | yes | `הזמר החסידי המאתגר מנדל ראטה, עם ביט חמוד על המבצע המיוחד בלבנון המיוחס לישראל בו התפוצצו אלפי מחבלים בעת שקיבלו הודעה למכשיר הביפר שלהם שיוצר בחברה בולגרית שככל הנראה לא באמת קיימת...` |
| `il_kikar_6d7b5f3531` | corpus | 160 -> 416 | no | yes | `בישראל מעריכים כי ארגון הטרור חיזבאללה יגיב ביממה הקרובה לפיצוץ הביפרים ומכשירי הקשר והחיסול הדרמטי בלב הדאחייה, ובשל כך הוחלט על סגירת המרחב האווירי מחדרה צפונה - עד יום שלישי, לצד שורת הנחיות חדשות של פיקוד העורף לתושבי חיפה וצפונה.` |
| `il_kikar_99fcbbf3a4` | corpus | 63 -> 1277 | no | yes | `07:30: ארגון טרור חיזבאללה קיבל אחריות על ירי עשרות רקטות לעבר מתקני רפאל באזור זבולון - צפונית לחיפה בתגובה על "טבח הביפרים ומכשירי הקשר".` |
| `il_kikar_d7845b3b06` | corpus | 81 -> 82 | no | no | not named; only generic radios: `במהלך הלחימה במרחב, לוחמי הנח"ל איתרו אמצעי לחימה בהם נשקים, תחמושת, מחסניות, מכשירי קשר, ווסטים ועוד.` |
| `il_n12_33d664e870` | corpus | 37 -> 536 | no | yes | `מקורות פוליטיים יודעי דבר אמרו לעיתון א-לואא' הלבנוני: "שלב ההסלמה הצבאית החל ביום שלישי עם פיצוץ מכשירי הקשר והושלם אתמול בתקיפה לעבר מפקדי חיזבאללה, במיוחד מפקד כוח רדואן איבראהים עקיל.` |

## container_coverage by outlet

Pass = body words >= 90% of container words. n/a = Telegram, no container on the page, or an empty container (headline-only). `measured` is the number of pages with a non-empty container. Min and median are body/container over those pages.

| outlet | pages | pass | fail | n/a | measured | pass of measured | min | median |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| ynet | 221 | 221 | 0 | 0 | 221 | 221/221 (100.0%) | 0.963 | 1.000 |
| n12 | 60 | 60 | 0 | 0 | 60 | 60/60 (100.0%) | 1.000 | 1.000 |
| kikar | 50 | 50 | 0 | 1 | 49 | 49/49 (100.0%) | 1.000 | 1.000 |
| makan | 17 | 17 | 0 | 0 | 17 | 17/17 (100.0%) | 1.000 | 1.000 |
| abuali | 93 | 93 | 0 | 93 | 0 | n/a | - | - |

No page fails container_coverage.

Truncation found with this check: Kikar and N12, the two the review named, fixed above. Ynet's JSON-LD `articleBody` is the whole article (the body is at least 90% of `ArticleBodyComponent` on every page, minimum in the table). Makan bodies already equal their container.

## What changed since round 1

- The 0.90 regression ratio is a diagnostic. The gate is the six checks above.
- Truncation fix: Kikar and N12 bodies are now the whole article container; Al Manar stops at the balanced `article-content` div. See the next section.
- Gap rows are read from `round2/gap-manifest-input.csv`. Gap rows that the corpus has since accepted are not counted twice in the gate.
- Al Jadeed is no longer `regression_failed`. Empty ShortDesc and LongDesc are `ok` briefs with `headline_only_empty_container`. A non-empty LongDesc is extracted once.
- Every corpus row was re-extracted to `reextract-v1.jsonl`. `corpus.jsonl` was not modified.
- Abu Ali records carry `footer_comment_link`. The trailing comment-link footer is removed from body and title.
- An iframe whose title attribute contains markup is dropped as an element, so its attributes are not article text.

## Open problems

- n12 is unusable: all-six 90.0% because no_chrome is under 95%.
- kikar is unusable: all-six 90.0% because no_chrome is under 95%.
- makan is unusable: all-six 94.1% because no_duplication is under 95%.
- n12 check 1: `בכיר בארגון הטרור כינה את האירוע כ"פרצת האבטחה הגדולה ביותר עד כה".` appears under 3 headlines (e.g. il_n12_aaaa261aca). It is inside the article text on those pages, so it stays.
- n12 check 1: `צה"ל הודיע כי תקף 100 משגרים, בהם כ-1,000 קני שיגור, שהיו מוכנים לשיגור מיידי לשטח מדינת ישראל.` appears under 3 headlines (e.g. il_n12_347fc26d28). It is inside the article text on those pages, so it stays.
- kikar check 1: `"האויב הישראלי פוצץ אלפי ביפרים וגרם למותם של עשרות ולפציעתם של אלפים.` appears under 4 headlines (e.g. il_kikar_aeeede0432). It is inside the article text on those pages, so it stays.
- kikar check 1: `ישראל חצתה את כל הקווים האדומים והתנהלה באופן לא מוסרי", אמר נסראללה.` appears under 4 headlines (e.g. il_kikar_aeeede0432). It is inside the article text on those pages, so it stays.
- kikar check 1: `בדבריו אמר ראש ארגון הטרור כי "האויב הישראלי רצה להרוג 5,000 בני אדם בשתי דקות - מה שקרה זה פשוט טבח" והצהיר: "האם זו הכרזת מלחמה?` appears under 4 headlines (e.g. il_kikar_aeeede0432). It is inside the article text on those pages, so it stays.
- makan check 4: `il_makan_c528a890f3` repeats `وحسب التحقيق، فإن أجهزة اللاسلكي التي تفجرت وهي بحوزة عناصر حزب الله قد تم تصنيعها في إسرائيل عام 2022 ومن ثم تم إدخالها في خط إمداد شركة "أبولو" من تايوان دون…`. Both copies are in the extracted article text, so both stay.
- ynet check 4: `il_ynet_d7725eedf9` repeats `המחשבה על כך שמישהו או מישהי מהם שמעו השבוע שעזה הפכה ל"זירה משנית" כואבת מדי, שוברת לב.`. Both copies are in the extracted article text, so both stay.
- ynet check 4: `il_ynet_9f7914f367` repeats `אין סיכוי שגדעון יתמוך בוועדת חקירה ממשלתית, נאמר לי.`. Both copies are in the extracted article text, so both stay.
- ynet check 4: `il_ynet_9f7914f367` repeats `ההערכה היא שכל עוד ביבי בשלטון, לא תהיה ועדת חקירה ממלכתית.`. Both copies are in the extracted article text, so both stay.
- ynet check 4: `il_ynet_e68574ed60` repeats `גורמים בקיאים אומרים כי הפגישה בקומה מינוס שתיים, עמדה לעסוק ביוזמה לפשיטה לתוך ישראל.`. Both copies are in the extracted article text, so both stay.
- Description opening words occur in the body but not in the first 400 characters: ynet il_ynet_6cac3456ed, kikar il_kikar_361888163b, ynet il_ynet_0e9f721ace, ynet il_ynet_cc4ffeb7d0.

Re-extract: 471 corpus rows, ok 441, no_raw 30.
