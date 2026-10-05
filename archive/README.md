# Archive

Material that is no longer used to produce or analyse the data. It is kept
because it records decisions and earlier results. Nothing outside `archive/`
reads from it.

## v1-presence-shares/

The first analysis round (2026-09-06 to 2026-09-16): per-outlet shares of
terms and framings ("terrorists", "martyrs", agentless grammar), timelines, and
four story drafts built on them. Superseded on 2026-10-04 by the claim-level
approach ("what a reader of outlet X was told", `data/cross-country/09-claims/`),
for two reasons:

- Term shares say little about what readers learned. The stories built on them
  were judged weak.
- The recall audit (`data/cross-country/08-recall-audit-summary.md`) showed that
  the corpus holds 5–60% of each outlet's coverage, and almost none of the
  articles that mention the attacks only in the body. Shares computed on that
  sample are not reliable.

| file | what it is |
|---|---|
| `lebanon-smoke/` | first Lebanon-only test run (2026-09-06): timelines, MTV displacement curve, vocabulary per outlet. Computed on corpus v1; re-running today's script on the current corpus gives different numbers |
| `lebanon-israel-comparison-v1.md`, `lebanon-israel-viz-v1.html` | first two-country comparison |
| `pager-coverage-viz.html`, `viz-template.html` | four-country term-share visualisation |
| `deep-dive-findings-v1.html`, `deep-dive-raw/` | grok deep-dive over all corpora (2026-09-16); its defect findings drove the v1.2 repair |
| `stories/` | four story drafts built on the findings above |
| `scripts/build_viz.py` | builds `pager-coverage-viz.html` from the current corpora |
| `scripts/analyze_lebanon_smoke.py` | builds `lebanon-smoke/` |

Some findings in these files were later corrected. Examples: "N12 posted first"
(Abu Ali posted at 12:57 UTC, before N12's 12:59 item), "Al-Manar slowest" and Al Jadeed's 68% "names Israel"
figure (both retracted in v1.2).

## lebanon-census-v1/

Lebanon outlet census v1 (2026-09-05). Replaced the same day by v2
(`data/lebanon/01-census/`), which addressed the first review and added
social-reach evidence.
