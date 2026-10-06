# Collection round 2: gap fill (corpus v2.0)

Round 1 selected articles by words in the headline or URL, so it missed most articles that
discuss the attacks only in the body, and every live blog. The recall audit (step 8) listed
what was missing per outlet. Its gap manifests as they were before round 2 are kept in
`data/<country>/05-extraction/round2/gap-manifest-input.csv`. Round 2 collects those items and
rebuilds the corpus with one validated extractor per outlet.

## Stages

| stage | what | status |
|---|---|---|
| 1 | gap-manifest items, extracted from the pages the audit had already saved (offline) | done, all four countries |
| 2 | live blogs, as timestamped entries from Wayback captures inside Sep 17–24 | done for Germany and the US. Israel and Lebanon have no live blogs: Telegram posts and ticker items are already single items |
| 3 | full re-sweep: outlet-native listings as the manifest of record, selection on the full text | not started |
| 4 | Lebanese long form and TV bulletin intros (An-Nahar, Al-Akhbar PDFs, LBCI/Al-Manar/MTV intros) | not started |

## Who did the work

Extraction code was written by delegated agents under written briefs: codex (GPT-5.6), Grok 4.7
and Claude Sonnet. The briefs are kept verbatim in `docs/agent-briefs/`. Hard rules:
- offline for stage 1; Wayback only, rate-limited, for stage 2
- write access limited to staging folders
- text verbatim from the HTML
- no guessed fields
- stop rather than improvise

Agent output is staging only (`data/<country>/05-extraction/round2/`). The merge into the corpus
and every relevance decision were done in this repository, in
`pipeline/06-normalization/build_corpus_v2.py`. A separate review agent checked the result
before release.

## Validation of the extractors

Comparing new extractions with the stored v1 bodies turned out to be the wrong test. Many v1
bodies still contained page chrome or were cut short:
- Spiegel share bars and audio-player code
- Fox video overlays
- Yahoo key-takeaway boxes
- Al Jadeed text from other stories
- Kikar, N12 and Al-Manar bodies cut at an embedded card or video

So every body, old and new, has to pass six checks:
1. no chrome strings, and no sentence repeated across pages
2. the page description's opening appears in the lead
3. no truncation
4. no sentence repeated within a body
5. paragraph order as in JSON-LD
6. for outlets without JSON-LD, the body holds ≥ 90% of the words in the article container

The bar is 95% per outlet. A failure caused by the publisher's own text, for example a wire
sentence shared across articles or a paragraph the page itself prints twice, counts as a pass
only with a quote from the page.

**Outlets below the bar.** N12 (90%), Kikar (90%) and Makan (94%) stay under it even then:
their failures are news sentences the outlet reuses across articles (N12, Kikar) and a paragraph
printed twice on one page (Makan). They were merged anyway, and this is the disclosure.

**Adjudication.** Every disagreement with a stored v1 body was classified with a quote from the
page. In the final adjudication files the stored body was wrong in 249 cases (Lebanon 22, Israel
100, Germany 79, US 48) and the new extraction in none.

## Relevance and salience

Every record carries `extraction.salience`:
- `central`: the attack is named in the headline or the first 400 characters of the body
- `mention`: named only further down
- `allusive`: refers to the attack without naming it ("the aggression of Tuesday and Wednesday")
- `none`

One rule applies to all countries, using the recall audit's term lists. For Germany and the US
there are two refinements: generic radio words ("Funkgerät", "walkie-talkie") only count in an
item about the region, and "devices", "Geräte" or "Kommunikationstechnik" count next to a blast
or attack word. `extraction.relevance` follows salience: central → strong, mention and allusive →
related, none → context.

Gap items the classifier rates `none`:
- **The audit's evidence is in the article:** `allusive`.
- **A paywall lead or a short capture:** `mention`, with warning `evidence_beyond_captured_text`.
- **Otherwise:** `none`.
- **Read by hand:** 16 records, each recorded with a reason in `MANUAL`.
- **Not added:** six audit false positives that matched on an unrelated radio word (ice-hockey referees, a fire brigade, London's "Walkie Talkie" building, school walkie-talkies).

**Caveats for analysis:**
- **`mention` covers passing references.** A single sentence in an otherwise unrelated story counts, for example a Fox column comparing a campaign to the pager attack. Claim coding has to judge weight.
- **Headline-only records.** 324 Lebanese primary records (38%) have no body: ticker items and briefs. Their salience comes from the headline alone.
- **Live-blog entries.** An entry's `canonical_url` is the blog URL with a fragment, so entries of one blog share a URL key by design.

## Duplicates

- **Within one outlet:** identical bodies (over 20 words) form a cluster with one primary record.
- **Across outlets:** a copy of another outlet's text stays primary and gets `deduplication.same_text_as`, because both readerships saw it (for example Yahoo's copy of a Fox story).
- **Live-blog reposts:** entries an outlet reposts across daily blogs (≥ 80% word overlap) are marked `liveblog_near_duplicate`.
- **Earlier relations are kept:** links from earlier passes (`earlier_version`, `near_duplicate`, `repost`, URL-variant clusters).

## Completeness

Against the audit's reference sets, recall is now close to 100%. **That is circular**: round 2
collected exactly those items, so it says nothing about what no independent route found. Two
signals still mean something:
- N12's extrapolated untitled stratum (overall recall about 44%)
- Yahoo's syndicated items that could not be matched (72%)

A real completeness figure needs stage 3 (a new manifest of record) and a fresh audit.

## Known gaps after stages 1 and 2

- **Live blogs with no entries in the captures:** RND (Tickaroo embed), ABC (client-side shells), NBC (no capture in the window), WELT and Fox (video pages).
- **ZDF's live blog:** an archive gap from Sep 17 12:52 to Sep 22 16:11 UTC; 1 entry recovered.
- **NYT and WaPo live blogs:** only part of their entries appear in each capture.
- **Paywalled items** (NYT, WaPo, Spiegel+, WELTplus): the lead only.
- **Yahoo credits:** 9 Yahoo records carry no provider credit, and 8 local-affiliate AP copies are credited to the affiliate.
- **TV broadcasts:** not covered, apart from teletext (RTL) and the bulletin intros already in the corpus.
