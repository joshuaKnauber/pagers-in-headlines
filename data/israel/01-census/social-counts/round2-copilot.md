I'll research these four areas in parallel, starting with the highest-value primary sources.






SimilarWeb pages are JS-rendered and blocked. Let me try raw HTML and alternative sources (tgstat, socialblade-type, Wikipedia, direct FB/IG pages).








✗ Fetching web content https://data.similarweb.com/api/v1/data?domain=kikar.co.il · url: "https://d…
    403

✗ Fetching web content https://data.similarweb.com/api/v1/data?domain=calcalist.co.il · url: "https…
    code 403

✗ Fetching web content https://data.similarweb.com/api/v1/data?domain=103fm.maariv.co.il · url: "ht…
    status code 403

✗ Fetching web content https://data.similarweb.com/api/v1/data?domain=inn.co.il · url: "https://dat…
    403

✗ Fetching web content https://data.similarweb.com/api/v1/data?domain=bhol.co.il · url: "https://da…
    403









✗ Fetching web content https://www.globes.co.il/news/%D7%9E%D7%93%D7%93_%D7%A6%D7%A4%D7%99%D7%99%D7…
    https://www.globes.co.il/news/%D7%9E%D7%93%D7%93_%D7%A6%D7%A4%D7%99%D7%99%D7%94_2024/ - status
    code 404

✗ Fetching web content https://tgstat.com/en/ratings/channels/israel/news · url: "https://tgstat.co…

✗ Fetching web content https://www.themarker.com/embeds/search-results?q=%D7%A8%D7%99%D7%99%D7%98%D…
    https://www.themarker.com/embeds/search-results?q=%D7%A8%D7%99%D7%99%D7%98%D7%99%D7%A0%D7%92+%D7
    %9E%D7%94%D7%93%D7%95%D7%A8%D7%95%D7%AA+%D7%97%D7%93%D7%A9%D7%95%D7%AA+2024 - status code 400

✗ Fetching web content https://he.wikipedia.org/wiki/%D7%94%D7%95%D7%95%D7%A2%D7%93%D7%94_%D7%94%D7…
    https://he.wikipedia.org/wiki/%D7%94%D7%95%D7%95%D7%A2%D7%93%D7%94_%D7%94%D7%99%D7%A9%D7%A8%D7%9
    0%D7%9C%D7%99%D7%AA_%D7%9C%D7%9E%D7%93%D7%A8%D7%95%D7%92_%D7%A6%D7%A4%D7%99%D7%99%D7%94 - status
    code 404


SimilarWeb/Google/DuckDuckGo are all blocking scripted fetches from my tools. I'll delegate this to specialized research agents (better suited for iterative web search) running in parallel for the four topics.





Four research agents are running in parallel on: (1) digital/social reach for Kikar HaShabbat/Behadrei Haredim/Arutz Sheva/103FM/Calcalist, (2) primary-source verification of 2024 TV news ratings, (3) Arab-Israeli outlet-level audience data, (4) Hebrew Telegram news channel subscriber counts. I'll wait for completion and compile the final sourced table.

✗ Extract social handles from bhol.co.il broader (shell)
  │ curl -s "https://www.bhol.co.il/" -o /tmp_bhol.html 2>/dev/null; curl -s
  │ "https://www.bhol.co.il/" | grep -oE '(facebook\.com|instagram\.com|t\.me)/[A-Za-z0-9_.\/]*' |
  │ sort -u | head -30





All four research agents are still actively working (many tool calls in progress). I'll wait for their completion notifications.

✗ test tmp write (shell)
  │ curl -s
  │ "http://web.archive.org/web/20260609020514if_/https://www.similarweb.com/website/kikar.co.il/"
  │ -o /tmp/kikar.html 2>&1 | head -5
  │ ls -la /tmp/kikar.html 2>/dev/null || echo "no tmp write allowed, using pipe instead"
  │





Telegram agent finished. Waiting on the other three (still actively fetching).

✗ Extract counters block for kikar_hashabbat properly (shell)
  │ curl -s "https://t.me/s/kikar_hashabbat" | python3 -c "
  │ import re,sys
  │ html=sys.stdin.read()
  │ m = re.search(r'tgme_channel_info_counters\">(.*?)</div>\s*<div
  │ class=\"tgme_channel_info_description', html, re.S)…




Three of four done. Waiting on the digital/social reach agent (still deep in fetches).


## Round-2 Evidence Pass — Israel Media Census

**Note on dates:** current date context is 2026-09-06; several "current" figures below reflect that. SimilarWeb, Google/Bing/DuckDuckGo, and Facebook all blocked automated fetching (WAF/login-walls) — noted per row.

### 1. Digital/Social Reach

| Outlet | Metric | Value | Period | Source URL |
|---|---|---|---|---|
| Kikar HaShabbat | Monthly visits (SimilarWeb) | ~4.4M/mo; Global rank #14,717 | May 2026 (archived) | web.archive.org/web/20260609020514/https://www.similarweb.com/website/kikar.co.il/ |
| Kikar HaShabbat | Instagram followers | 29K | Sep 2026 | instagram.com/kikarhashabat |
| Kikar HaShabbat | Facebook/Telegram | Handle confirmed (facebook.com/kikarhashabat); no official Telegram found | Sep 2026 | kikar.co.il site source |
| Behadrei Haredim | Instagram followers | 296 (unusually low) | Sep 2026 | instagram.com/behadreiharedim |
| Behadrei Haredim | Traffic/Telegram | Not found — SimilarWeb blocked; no Telegram in site metadata | Sep 2026 | bhol.co.il |
| Arutz Sheva/INN | Instagram followers | 33K | Sep 2026 | instagram.com/arutz.sheva |
| Arutz Sheva/INN | Telegram | 52 subs — channel appears hacked/defaced, not valid | Sep 2026 | t.me/s/israelnationalnews |
| Arutz Sheva/INN | Traffic | Not found — SimilarWeb blocked | — | — |
| 103FM | Instagram followers | 26K | Sep 2026 | instagram.com/radio103fm |
| 103FM | Traffic/audience | Not found | — | — |
| Calcalist | Instagram | 83K | Sep 2026 | instagram.com/calcalist |
| Calcalist | TikTok | 61.6K | Sep 2026 | tiktok.com/@calcalist |
| Calcalist | Telegram | 30K (self-labeled official channel) | Sep 2026 | t.me/s/calcalist |

**Gaps:** No FB follower counts obtained anywhere (login wall); SimilarWeb traffic unobtainable for bhol.co.il, inn.co.il, calcalist.co.il, 103fm except one Wayback snapshot for kikar.co.il.

### 2. TV News Ratings 2024 — Verification

Official body: **הוועדה הישראלית למדרוג (IARB)**, midrug-tv.org.il — no public data (members/journalists only). Found independent second source confirming Walla figures:

| Outlet | Value | Period | Source |
|---|---|---|---|
| Ch.12 news | 15.9% | 2024 avg | kipa.co.il/תרבות/טלוויזיה/1195226-0/ (pub 2025-01-01) |
| Ch.14 news | 7.4% | 2024 avg | same |
| Ch.13 news | 6.5% | 2024 avg | same |
| Kan 11 news | 4.5% | 2024 avg | same |

Kipa.co.il (separate outlet/byline, Jan 1 2025) matches Walla (b.walla.co.il/item/3712422, Dec 2024) exactly. **Walla figures confirmed**, though both ultimately trace to the same IARB/Kantar panel — no fully independent dataset located.

### 3. Arab-Israeli Media Audience

| Outlet | Metric | Value | Period | Source |
|---|---|---|---|---|
| Makan 33 | TV rating (Arab-sector panel) | 5.5–11% across programs (news bulletin 10.6%) | 2025–2026 | israelhayom.co.il/culture/tv/article/19552995; ice.co.il/tv-rating/... |
| Kul al-Arab (kul-alarab.com, note hyphen) | Facebook | 1.38M likes | Sep 2026 | facebook.com/kulalarabcom |
| Kul al-Arab | Instagram | 173K | Sep 2026 | instagram.com/kulalarab |
| Nas Radio | Facebook | 268K likes | Sep 2026 | facebook.com/nasradio.fm |
| Arab48 | Organic search traffic | 35.6K visits/mo (search only) | Aug 2026 | ahrefstop.com/websites/arab48.com |
| Panet | Traffic | Contradictory (panet.com vs .co.il, ~1.3K–630K/mo across estimators) | 2023–2026 | hypestat.com/info/panet.co.il |
| Hala TV | — | **No data found** (only channel-history pages; searches for followers/ratings returned nothing) | — | — |

"Mysawa" = likely confusion with **Mossawa Center** (advocacy NGO, unrelated to media measurement) — no such audience-tracking entity found. No IDI/Sikkuy/I'lam survey with outlet-level (vs. platform-level) breakdown was accessible.

### 4. Telegram News Channels

| Channel | Subscribers | Date | Operator | Source |
|---|---|---|---|---|
| Abu Ali Express | 582,971 (Wikipedia infobox: ~600K) | Sep 2026 | Anonymous; alleged Gilad Cohen per Haaretz (Kubovich) | tgstat.com/en/channel/@abualiexpress; he.wikipedia.org/wiki/אבו_עלי_אקספרס |
| News0404 | **Not verified** — no confirmed official channel found under tested handles | — | Boaz Golan (website brand, per Wikipedia) | he.wikipedia.org/wiki/חדשות_0404 |
| Others >100K ("Kan News", "N12", "Ch.13/14" guessed handles) | **None confirmed** — all tested handles had <4K subs or were unofficial/hacked | Sep 2026 | — | t.me/s/* (multiple) |

**Bottom line:** Ratings (item 2) is well-corroborated. Social/digital reach (1,3,4) has real but partial data — SimilarWeb/Facebook/search-engine blocking left several traffic and Telegram figures unverifiable; these gaps are flagged rather than filled with guesses.

