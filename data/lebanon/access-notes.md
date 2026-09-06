# Lebanon access verification — notes (step 3, v1, 2026-09-05)

Companion to [access-register-v1.csv](access-register-v1.csv). Input was the
gate file (4 required + NNA baseline). **Result: all five gate rows
verified, zero blockers. Lebanon is clear for enumeration (step 4).**

## Route summary

Primary route for all five outlets is **Wayback** (project policy: day-of
captures preserve headline edits and live-blog states), with direct fetch
as fallback for the four TV outlets. Every domain's robots.txt is
permissive with no TDM reservation — the Al Jazeera-style restriction
exists nowhere in the required set.

Verified fetches (2026-09-05):

| outlet | test | words | note |
| --- | --- | --- | --- |
| LBCI | direct, day-0 EN article | 990 | full body |
| MTV | direct, EN article | 349 | full body (short item) |
| Al Jadeed | direct, day-0 AR article | 1,321 | title verified |
| Al-Manar | day-of Wayback capture | 1,724 | full AR body |
| NNA | day-of Wayback capture | 465 | body confirmed |

Event-window capture density (Wayback CDX, Sep 15 – Oct 17 2024, unique
200-OK URLs): LBCI, MTV, Al Jadeed, Al-Manar all ≥8,000 (query cap —
actual density higher); NNA 762.

## Identity findings (the step's main yield)

1. **Al-Manar's 2024 URL structure differs from today's.** Event-era
   articles live at `almanar.com.lb/<numeric-id>` (root-level); the current
   site uses `/article/<id>`. Enumeration (step 4) must target the 2024
   pattern. The `.lb` domain itself was unaffected by the 2021 US seizure
   of Al-Manar's other domain variants and was live throughout the event
   window.
2. **NNA rebuilt its site after the event.** The current site is a JS
   shell (direct fetch yields ~58 words of metadata; its API path is
   robots-disallowed). The 2024 site was server-rendered — day-of Wayback
   captures contain full text, so the archive route is not just preferred
   but the *only* practical text route. Arabic paths
   (`/ar/<category>/<id>/<slug>`) are densely captured; English
   (`/en/news/<id>/<slug>`) exists (the old-manifest URLs) but its capture
   density is a round-2 check before relying on EN.
3. LBCI and Al Jadeed share a CMS (identical robots template, same URL
   pattern `/news/<section>/<id>/<slug>`) — one extractor likely covers
   both.

## Open items (non-blocking)

- Bulletin/broadcast surfaces: verify event-week YouTube uploads survive
  for LBCI/MTV/Al Jadeed; Al-Manar has no YouTube (banned 2021) — its
  broadcast record is site video + Telegram. Web text is the accepted
  primary corpus form per methodology; broadcast surfaces are enrichment.
- NNA English capture density.
- Al Jazeera row is optional-tier and deliberately untested; its known
  robots/TDM restriction only becomes relevant if the perspective panel is
  commissioned, and then only via archive or written permission.

## v1.1 amendments (post-review, copilot CLI, 2026-09-05)

The scoped review reproduced the Al-Manar and NNA claims, confirmed the
verdict (clear for enumeration, zero blockers), and corrected the register:

1. **New route found: `archive.almanar.com.lb`** — Al-Manar's own live
   archive subdomain; old numeric URLs 301 there and it serves full 2024
   text, robots-unrestricted. Recorded as the completeness route (Wayback
   remains primary for day-of version preservation).
2. My "current structure = /article/<id>" claim for Al-Manar was wrong
   (those paths 404) — removed.
3. NNA's rebuild changed the **URL schema**, not just rendering: old
   articles 301 to `/ar/news/<new-id>/<slug>`. 2024 IDs don't map to
   current paths — enumeration must use 2024 patterns exclusively. Also:
   the SPA returns catch-all boilerplate for any path including `/ai.txt`,
   so its ai.txt "200" is a false positive.
4. LBCI robots disallow list completed (`/thewall/` added).
5. Open gap recorded: "no TDM reservation" is verified at robots/ai.txt
   level only; TDM-Reservation HTTP headers were not checked.
6. LBCI's 990-word direct-fetch body count stands (reviewer couldn't
   reproduce with its markdown-simplifying tool; identity and metadata
   confirmed exactly — not disproof, tooling difference noted).

## Method notes

- CDX prefix queries against *current* URL patterns returned empty for
  Al-Manar and NNA — the identity-first rule (pin 2024 patterns before
  querying) was what found the real captures. This confirms the step-3
  procedure ordering.
- Word-count body checks used tag-stripped text; a keyword-presence check
  produced a false alarm on Al Jadeed (article simply didn't contain the
  tested term) — title verification is the more reliable confirmation.
