# Israel access verification — notes (step 3, v1, 2026-09-06)

Companion to [access-register-v1.csv](access-register-v1.csv). Input: the
gate file (2 required + 3 required-representative). **Result: all five
gate rows verified with day-of body fetches, zero blockers. Israel is
clear for enumeration (step 4).**

Verified fetches (2026-09-06): Ynet day-of article capture (295 words,
SSR); N12 day-of event article via mako.co.il capture (708 words); Kikar
live day-0 event article (1,052 words); Makan day-of Arabic article
capture (392 words); Abu Ali day-of channel-page capture (964 words of
timestamped messages).

## Identity findings

1. **Event-era N12 articles live on mako.co.il** (`news-*/.../Article-
   <hex>.htm`), not n12.co.il — enumeration must target mako patterns,
   with query-string canonicalization (tracking-parameter duplicates).
2. **Ynet and mako homepages are JS shells even in 2024 captures** — the
   homepage-harvest trick (which worked for Al-Manar and Kikar) fails
   there; enumeration goes through article-prefix CDX queries instead.
   Ynet mixes alphanumeric and numeric legacy article IDs.
3. **makan.org.il is behind a Cloudflare managed challenge today** —
   automated direct access is impossible, but the event window has ~3,000
   unique archived captures and article bodies are server-rendered, so
   Wayback is a complete route. Article path:
   `/content/news/makan-news/p-<sec>/<id>/`.
4. **The Abu Ali Telegram-history question resolved better than hoped:**
   `t.me/s/abualiexpress` was archived multiple times per day all through
   the window — a near-continuous, timestamped message stream. Extraction
   needs cross-capture dedup (rolling pages overlap), and live `?before=`
   pagination is the fallback.
5. N12/mako's CDN 403s non-browser clients (even robots.txt) — the direct
   fallback needs browser-grade fetching; Wayback is unaffected.

## Notables

- Kikar's robots.txt *explicitly allows* AI crawlers — the most permissive
  stance encountered in the project.
- Framing preview from the very first Kikar test article: pager casualties
  called "מחבלים" (terrorists) in the headline — the attacker-side
  register the Lebanon↔Israel comparison exists to measure.
- No paywall on any gate row (Haaretz's hard wall is substantial-tier,
  not required).

## Review (copilot, 2026-09-06): register accurate, zero inaccuracies

All three reproduced fetches confirmed (N12 event article with JSON-LD
publisher/date verified; Kikar live day-0 article; Abu Ali capture with 18
timestamped 2024-09-17 messages). Two nuances added by the reviewer:

1. **n12.co.il did exist in the event window — as a shortlink domain**
   that 301-redirects to mako.co.il (verified). Strengthens the identity
   finding; enumeration may treat n12.co.il URLs as aliases to
   canonicalize onto mako paths.
2. **Kikar's robots is nuanced, not just permissive**: it carries
   `Content-Signal: ai-train=no` — AI input/search use allowed, training
   denied. Our collection (research analysis, no model training on the
   text) is consistent with that signal; documented here so the stance is
   recorded precisely rather than as blanket permissiveness.

## Open (non-blocking)

- GDELT was rate-limited throughout — its keyword layer for Israel
  enumeration should run later with long throttles.
- Scoped review of this register queued (external CLI), per methodology.
- Subagent scratch captures in the project root (tg_*.html, ynet.html …,
  from the copilot census run) may be reusable as evidence artifacts but
  are NOT part of the register; do not commit (project decision).
