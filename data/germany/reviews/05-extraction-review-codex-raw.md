# Germany verdict: fail

The count arithmetic is mostly correct, but extraction and deduplication defects remain.

| # | Finding | Evidence | Severity | Fix |
|---|---|---|---|---|
| 1 | Candidate tags use `relevance`, not `manifest_tag`; the requested “none-tagged” sample is undefined as written. | Candidate files contain `relevance=none` for 78 Germany rows, but no `manifest_tag=none`. | Medium | Define the sampling field explicitly. |
| 2 | Spiegel bodies retain substantial page chrome at both ends. | `ge_spiegel_00c96b2041`: body starts `Merkliste hinzufügen...` and ends with `Dialog schließen... Anmelden...`; raw `spiegel/00c96b204192a345.html`. | High | Strip share controls, subscription UI, image/dialog text, and footer residue. |
| 3 | Exact duplicate bodies remain in the corpus, despite deduplication metadata. | `ge_tonline_67835c3fd1` / `ge_tonline_ad3e3c1d92`; `ge_rnd_e494be678a` / `ge_rnd_b4325f0501`; three Spiegel pairs including `ge_spiegel_56bd1c4430` / `ge_spiegel_d46672bed2`. | High | Remove non-primary duplicates from analysis exports, or enforce primary-only consumers. |
| 4 | Shared outlet boilerplate remains widespread. | t-online has repeated image-credit/article-share prefixes and repeated suffixes; Spiegel has repeated share/footer chrome. | High | Add outlet-specific prefix/suffix scrubbing and rerun QC. |
| 5 | The sampled dropped rows showed no clear pager-event false negatives. | Ten `relevance=none` candidates sampled; no definite pager or electronic-device attack article was wrongly dropped. | Low | Keep the result, but repeat after defining the tag field. |
| 6 | Five sampled strong records were mostly relevant. | `ge_welt_1178f16041`, `ge_spiegel_6cd9da63ea`, `ge_bild_15cd3b214e`, `ge_bild_e70264fd0`, `ge_tonline_437b0d9223` all concern the attack or immediate consequences. | Low | No change required for this sample. |
| 7 | Germany language fields passed the five-record spot check. | `ge_tagesschau_bcdc70bedf`, `ge_tagesschau_c4082cd92e`, `ge_tagesschau_da05785628`, `ge_zdfheute_507f288e9f`, `ge_spiegel_00c96b2041` are German text and marked `de`. | Low | No change required. |

Count reconciliation: 282 candidates; 149 strong, 55 related, 78 none; 178 primary corpus records. Primary outlet counts and document-type counts match the notes. The JSONL contains 192 rows total because 14 non-primary duplicate rows remain.

# US verdict: fail

The US corpus has serious extraction contamination, obvious false positives, blank publication dates, and repeated syndicated bodies.

| # | Finding | Evidence | Severity | Fix |
|---|---|---|---|---|
| 1 | Fox extraction starts with unrelated navigation and recommendation content. | `us_fox_b2a1805dab` begins `Russia readies new 500-mile missile...`; the actual article is an assassination-plot story with a pager attack inserted later. Raw: `raw/fox/b2a1805dab50772.html`. | Critical | Reject or re-extract pages when the title/body lead does not match; isolate the article container. |
| 2 | Fox produced a strong false positive. | `us_fox_b2a1805dab` is titled “Iranian Netanyahu assassination plot foiled...” and is not a pager-event article. `us_fox_129e8c6b5c` is a cease-fire article with pager material only late in the body. | High | Require event-specific centrality, not incidental pager mentions. |
| 3 | Yahoo bodies contain navigation and generated-summary UI. | `us_yahoo_0a09f735ca` begins `Return to Homepage Top Stories... Yahoo is using AI to generate key points...`; raw: `raw/yahoo/0a09f735caa54c7c.html`. | Critical | Remove Yahoo shell/key-points blocks and validate article start against headline. |
| 4 | WaPo body includes branding and unrelated related-content tail. | `us_wapo_2219618d3f` begins `Democracy Dies in Darkness` and ends with Israel/Palestinian-history “Read more” material. Raw: `raw/wapo/2219618d3fb45998.html`. | High | Strip branding, recommendation modules, and trailing related links. |
| 5 | Reuters body includes gallery and Wayback/related-page contamination. | `us_reuters_d4ac302ced` begins `Item 1 of 5... Purchase Licensing Rights` and ends with an October 15 unrelated article. Raw: `raw/reuters/d4ac302ced40cae5.html`. | High | Extract only the Reuters article container; remove gallery and “more news” modules. |
| 6 | Reuters primary records are archive pages, not articles. | `us_reuters_25168b08e0` and `us_reuters_eb116e8d25` have headline `Wayback Machine` or blank, blank dates, and bodies beginning `Keep the news in the Wayback Machine...`. | Critical | Exclude archive landing pages and require headline/date/article-body validation. |
| 7 | Exact duplicate CNN bodies remain across primary/non-primary records. | Eleven duplicate clusters, including `us_cnn_008d57bd76` / `us_cnn_4e15eebb46` / `us_cnn_c096f01c9f`; `us_cnn_28967cf7ba` has five records. | High | Enforce primary-only export and cluster-level deduplication. |
| 8 | Yahoo contains an exact duplicate pair. | `us_yahoo_e0525fd211` and `us_yahoo_7658c19c1b`. | High | Deduplicate before corpus analysis. |
| 9 | Publication dates are missing on accepted primary records. | `us_fox_b2a1805dab`, `us_usatoday_5bb547ff5e`, `us_wapo_9157696cb9`, and Reuters archive records have blank `published_at`; Fox raw HTML contains `2024-09-19T10:01:06-04:00`. | High | Extract dates from JSON-LD/meta, or reject records without verifiable publication dates. |
| 10 | Sampled dropped rows included access shells and unrelated aftermath, but no clear pager-event false negative. | Ten `relevance=none` rows included AP `Just a moment...`, WaPo `Access Denied`, USA Today homepage, and Fox unrelated pages. No sampled row was clearly a wrongly dropped pager-attack article. | Medium | Treat access failures separately from true relevance negatives. |
| 11 | Strong-sample review found a false positive. | `us_fox_129e8c6b5c` is a cease-fire article with pager material only in later paragraphs; other sampled strong rows were event-centered. | High | Tighten strong-relevance rules around headline and lead centrality. |

Count reconciliation: 248 candidates; 152 strong, 13 related, 61 none, 22 no-capture; 138 primary corpus records. Primary outlet, slot, and document-type counts match the notes. The JSONL contains 165 rows total because 27 non-primary rows remain.

The language check was only required for Germany and passed. Neither country should be approved for freeze: the US extraction defects are release-blocking, and Germany still has page chrome plus duplicate-body contamination.
