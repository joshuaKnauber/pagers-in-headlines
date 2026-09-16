# US enumeration — notes (step 4, v1, 2026-09-14)

Script: `data/scripts/enumerate_de_us.py` + direct whole-window prefix
pass for WaPo/Reuters + codex curated passes. Window Sep 15 – Oct 17
2024. **59,003 URLs across 11 outlets; 248 tagged candidates.**

| outlet | urls | source | candidates | note |
| --- | --- | --- | --- | --- |
| AP | 27,363 | monthly sitemaps (curl) | 23 | complete; wire-baseline denominator |
| CBS | 14,510 | dated monthly sitemaps | 13 | complete |
| CNN | 7,697 | CDX (2024 date-path prefix) | 64 | richest candidate set; transcripts route separate |
| ABC | 5,635 | CDX | 5 | wireStory URLs; low candidate count — recall check parked |
| NBC | 3,333 | monthly sitemaps | 17 | complete |
| Reuters | 200 | CDX section prefixes + curated | 17 | world/business/tech prefixes (domain query 504s) |
| WaPo | 177 | CDX section prefixes + curated | 21 | /world prefix failed → curated covers; nat-sec/tech/investigations enumerated |
| Yahoo | 35 | curated + GDELT | 35 | syndication-discovery source by design (register rule) |
| Fox | 29 | curated + GDELT | 29 | IA captures Fox too sparsely for a denominator — candidates-only outlet |
| NYT | 17 | curated + GDELT | 17 | CDX API 403s all NYT queries; per-URL availability at extraction |
| USA Today | 7 | curated | 7 | no archive presence; live-only |

## Denominator design

Complete-output denominators exist for AP, CBS, NBC (sitemaps) — the
US displacement/volume analyses use those. Fox/Yahoo/USA Today/NYT are
**candidates-only** outlets (no complete manifest possible without
APIs/licensing); their analysis role is framing shares, not volume.

## Method notes / pitfalls hit

1. Same nginx-504-as-HTTP-200 trap as Germany (see germany notes) —
   WaPo/Reuters domain-wide queries never survived it; **whole-window
   section-prefix queries** (9 total instead of 102 sliced) got through.
2. apnews.com blocks python-urllib TLS fingerprints (403) but serves
   curl with a browser UA — fetch fallback added.
3. GDELT rate-limited to near-unusability; codex curated passes
   (3 rounds) supplied the recall layer for Fox/NYT/Yahoo/USA Today/
   WaPo/Reuters: 90 curated URLs total.
4. ABC's 5 candidates look thin for a mass outlet — its coverage was
   heavily AP wireStory reprints; a slug-recall check (hezbollah-slug
   sample) is parked for round 2.

Next (step 5): live routes for Fox/CNN/CBS/NBC/USA Today/Yahoo/AP;
Wayback captures for ABC/WaPo/Reuters; NYT per-URL availability →
capture (lead-depth accepted per register).
