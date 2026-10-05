# Step 7: repair passes

A repair pass fixes defects found after normalization, by reviews or analysis, and
rewrites `data/<country>/06-corpus/corpus.jsonl` in place. Every pass gets a version
number, a script in `pipeline/07-repair/`, a ledger section in
`05-extraction/triage-notes.md`, and an entry in `06-corpus/CHANGELOG.md`.

Rules that every pass so far has followed:

- Work from the saved `raw/` HTML. Refetching is allowed only to recover records that
  are missing (the v1.2 Al-Manar recovery) and the new raw files are kept.
- Re-extract from the page's article container rather than patching text. Most defects
  were page chrome (navigation, tickers, newsletter prompts) captured by a fallback
  extractor.
- Every pass gets one adversarial review of its delta. If that review fails, the
  fix-ups are a new minor version (v1.2 → v1.2.1).
- Retract findings that depended on a defect, in the ledger, in so many words (for
  example Al Jadeed's 68% "names Israel" figure, which was body chrome).

| version | scripts | what it fixed |
|---|---|---|
| v1.1 | `repair_v11_israel.py` (Israel); inline fixes in the other countries' review rounds | step-5 review findings: chrome in Kikar and N12 bodies, duplicates, relevance tags |
| v1.2 | `repair_v12.py <country>`, `repair_v12_almanar_recover.py` | the 2026-09-16 deep-dive defects: 2026 chrome in Fox, CNN, Yahoo and Al Jadeed bodies, AMP and path-twin duplicates, t-online headlines, Spiegel paywall shells, Al-Manar dates and day-0 gap, Israeli publication times |
| v1.2.1 | `repair_v12.py fixups` | the review of v1.2: Fox newsletter tails, Al Jadeed bodies that were all chrome, word counts |
| v1.3 | planned | recall-audit findings, see `data/cross-country/08-recall-audit-summary.md` |

`repair_v12.py <country> --dry` prints what it would change without writing.
