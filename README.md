# Pagers In Headlines

How mass media in different countries covered the same event: the
Lebanon pager and walkie-talkie attacks of 17–18 September 2024.

The goal is to show, per outlet, which facts and claims its audience could
have encountered ("what a Bild reader was told"), with a source for every
article, and to compare outlets and countries on that basis.

## Countries and outlets

Lebanon, Israel, Germany, United States. Outlets are chosen per country by
audience reach (what most people consume, not every niche); see each country's
`01-census/`.

## Repository layout

```
docs/methodology/   how each step works, 01-census … 08-recall-audit
pipeline/           scripts, one folder per step (02-gate … 08-recall-audit)
data/
  README.md         which script produced which file
  <country>/        01-census … 08-recall-audit, raw/, reviews/ — README.md in each
  cross-country/    recall-audit summary, claim catalogue (step 9)
archive/            superseded analysis and census versions, with a README saying why
site/               website scaffold (Astro), not in use yet
```

Pipeline steps, in order:

1. **Census.** Which outlets people in the country actually use.
2. **Gate.** Which of those must be collected (derived mechanically from the census).
3. **Access.** How each gated outlet can be reached today: live, Wayback, API.
4. **Enumeration.** Every URL each outlet published in the event window.
5. **Extraction.** Triage the URLs, fetch the event-related ones, parse them.
6. **Normalization.** One record schema for all countries: `06-corpus/corpus.jsonl`.
7. **Repair.** Versioned fixes to the corpus after reviews and the recall audit (v1.1 to v1.3.1).
8. **Recall audit.** How complete the corpus is per outlet, and what is missing.
9. **Claims.** Catalogue of claims made about the attacks, to code per outlet (in progress).

## Data honesty

- The corpus is a sample of what each outlet published online, not the
  full output and not what was broadcast on TV. Step 8 measures how large the
  sample is per outlet.
- Anything not found is reported as "not in our sample", never as "not
  published", unless it was checked against the outlet's own archive.
- Every record keeps its canonical URL, the route it was collected by (live or
  Wayback capture) and the raw HTML it was parsed from.
- Some URL manifests include lists suggested by LLM web searches; they are kept
  and labelled in `04-enumeration/`.

## Status

- Corpus v2.0: Lebanon 837, Israel 470, Germany 407, US 1,015 primary records
  (event window Sep 17 – Oct 17 2024), after collection round 2
  (`docs/methodology/round2-gap-fill.md`): the items the recall audit found missing, live-blog
  entries, and one validated extractor per outlet for old and new records.
- Recall audit done for all four countries
  (`data/cross-country/08-recall-audit-summary.md`): the corpus holds roughly 5–60%
  of each outlet's coverage from Sep 17 to 24, and almost none of the articles that
  mention the attacks only in the body.
- Claim catalogue v1: 81 claims (`data/cross-country/09-claims/`).
- Next: round 2 stage 3 (full re-sweep of outlet listings with full-text selection) and a
  fresh recall audit; then coding claims per outlet.

## Setup

Python 3 (standard library only) and `curl`. Copy `.env.example` to `.env` and fill in
the keys (Media Cloud API, used by the recall audit).
