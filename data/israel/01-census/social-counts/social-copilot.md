I'll launch four parallel research agents, each covering a subset of outlets, to gather social media follower counts with verified handles and sources.









I need to use the actual agent IDs returned, not the names. Waiting for all four research agents to complete.

  │ curl -s -A "Mozilla/5.0" "https://www.ynet.co.il/home/0,7340,L-8,00.html" -o /tmp/ynet.html
  │ 2>&1; wc -l /tmp/ynet.html; grep -oE '(facebook|instagram|twitter|x\.com|tiktok|t\.me|youtube)\.
  │ com/[A-Za-z0-9_./%-]*|t\.me/[A-Za-z0-9_./%-]*' /tmp/ynet.html | sort -u

  │ curl -s -L -A "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)
  │ Chrome/120.0 Safari/537.36" -H "Accept-Language: he" https://www.kan.org.il/ -o /tmp_out2.html
  │ -w "%{http_code}\n"; grep -oE
  │ 'https?://(www\.)?(facebook|instagram|twitter|x|youtube|tiktok)\.com[^"'"'"'
  │ ]*|https?://t\.me/[^"'"'"' ]*' /tmp_out2.html | sort -u

  │ curl -s -L -A "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)
  │ Chrome/120.0 Safari/537.36" -H "Accept-Language: he" https://www.israelhayom.co.il/ -o
  │ /tmp_out1.html -w "%{http_code}\n" ; echo done

  │ curl -s -A "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)
  │ Chrome/120.0 Safari/537.36" "https://www.youtube.com/@TimesofIsrael/about" -o /tmp/x3.html; grep
  │ -o "subscriberCountText[^}]*}" /tmp/x3.html | head -5; echo "---canonical---"; grep -o
  │ '"canonicalBaseUrl":"[^"]*"' /tmp/x3.html | head -2

  │ curl -s -A "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)
  │ Chrome/120.0 Safari/537.36" "https://www.youtube.com/@JerusalemPost/about" -o /tmp/x2.html; grep
  │ -o "subscriberCountText[^}]*}" /tmp/x2.html | head -5; echo "---canonical---"; grep -o
  │ '"canonicalBaseUrl":"[^"]*"' /tmp/x2.html | head -2

  │ curl -s -A "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)
  │ Chrome/120.0 Safari/537.36" "https://www.youtube.com/@maarivonline/about" -o /tmp/x4.html; grep
  │ -o "subscriberCountText[^}]*}" /tmp/x4.html | head -5; echo "---canonical---"; grep -o
  │ '"canonicalBaseUrl":"[^"]*"' /tmp/x4.html | head -2

  │ curl -s -A "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)
  │ Chrome/120.0 Safari/537.36" "https://www.youtube.com/@haaretzcom/about" -o /tmp/x1.html; grep -o
  │ "subscriberCountText[^}]*}" /tmp/x1.html | head -5; echo "---canonical---"; grep -o
  │ '"canonicalBaseUrl":"[^"]*"' /tmp/x1.html | head -2

  │ for q in "i24news" "i24NEWS_EN" "i24NEWSEN" "i24newsEnglish"; do echo "=== $q ==="; curl -s -A
  │ "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0
  │ Safari/537.36" "https://www.youtube.com/@$q/about" -o /tmp/y_$q.html -w "%{http_code}\n"; grep
  │ -o "subscriberCountText[^}]*}" /tmp/y_$q.html | head -3; grep -o '"canonicalBaseUrl":"[^"]*"'
  │ /tmp/y_$q.html | head -1; done

  │ UA="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)
  │ Chrome/120.0 Safari/537.36"
  │ declare -A urls=(
  │ [haaretz_ig]="https://www.instagram.com/haaretzcom/"
  │ [haaretz_tt]="https://www.tiktok.com/@haaretzcom"…

  │ curl -s -A "Mozilla/5.0" -L "https://www.instagram.com/haaretzcom/" -o /tmp/h1.html; grep -o
  │ 'og:description" content="[^"]*"' /tmp/h1.html | head -1

  │ curl -s -A "Mozilla/5.0" -L "https://www.tiktok.com/@haaretzcom" | grep -o
  │ '"UserModule":{"users":{[^}]*}[^}]*}[^}]*}' | head -1
  │ echo "---"
  │ curl -s -A "Mozilla/5.0" -L "https://www.tiktok.com/@haaretzcom" -o - | python3 -c "
  │ import sys,re,json…

  │ curl -s -A "Mozilla/5.0" -L "https://www.tiktok.com/@haaretzcom" > /tmp/tt.html; wc -c
  │ /tmp/tt.html





All four research agents are actively working (32-63 tool calls each so far, gathering and verifying data). I'll wait for completion notifications.

  │ sleep 8
  │ curl -s -A "Mozilla/5.0" -o /tmp/fb_ynetenglish_test.html
  │ "https://www.facebook.com/ynetenglish/" -w "code:%{http_code} size:%{size_download}\n" 2>&1 ||
  │ true
  │ wc -c /tmp/fb_ynetenglish_test.html 2>/dev/null…





Still working (66-145 tool calls each). I'll continue waiting for completion notifications.





Group 3 (Haaretz English, Maariv, Jerusalem Post, Times of Israel, i24NEWS) is done. Still waiting on groups 1, 2, and 4.

  │ sleep 5
  │ curl -s -A "Mozilla/5.0" "https://www.facebook.com/Now14Israel/" -o /tmp_out.html 2>/dev/null ||
  │ true
  │ curl -s -A "Mozilla/5.0" "https://www.facebook.com/Now14Israel/" | tee /dev/null | grep -oE
  │ '"og:title" content="[^"]*"|"og:description" content="[^"]*"'




3 of 4 groups complete. Waiting on Group 1 (Ynet, Ynetnews, N12/Mako, Channel 13, Now 14).


Still waiting on the final group (Ynet, Ynetnews, N12/Mako, Channel 13, Now 14) — it's doing thorough verification (128 tool calls so far). I'll wait for it to complete.


All four research groups are complete. Compiling the consolidated census with all findings, including handle verification and disambiguation notes.

## Israeli News Outlets — Social Media Follower Census
*All access dates: 2026-09-06 (single-snapshot data; counts fluctuate)*

| Outlet | Platform | Handle | Count | As-of | Source URL |
|---|---|---|---|---|---|
| **Ynet (Hebrew)** | Facebook | ynetnews (page titled "ynet") | 1,511,977 | 09-06 | facebook.com/ynetnews |
| | Instagram | @ynetgram | 462K | 09-06 | instagram.com/ynetgram |
| | YouTube | @ynetofficial | 504K | 09-06 | youtube.com/channel/UCpSSzrovhI4fA2PQNItecUA |
| | TikTok | @ynet | 1,701,237 | 09-06 | tiktok.com/@ynet |
| | X/Twitter | @ynetalerts | not found (X hides public counts) | 09-06 | x.com/ynetalerts |
| | Telegram | t.me/ynetalerts | 114,115 | 09-06 | t.me/ynetalerts |
| **Ynetnews (English)** | Facebook | ynetenglish | not found (blocked) | 09-06 | facebook.com/ynetenglish |
| | Instagram | @ynetnews | not found (blocked) | 09-06 | instagram.com/ynetnews |
| | YouTube | — | not found (no channel) | 09-06 | — |
| | TikTok | @ynetnews | 3,900 | 09-06 | tiktok.com/@ynetnews |
| | X/Twitter | @ynetnews | not found | 09-06 | x.com/ynetnews |
| | Telegram | t.me/ynetnewslatest | 843 | 09-06 | t.me/ynetnewslatest |
| **N12 (Ch.12 News)** | Facebook | N12News | 1,163,008 | 09-06 | facebook.com/N12News |
| | Instagram | @n12news | 583K | 09-06 | instagram.com/n12news |
| | YouTube | @israelnews | 107K | 09-06 | youtube.com/channel/UCr2-QsbpVwSd_ksP3gh3ciQ |
| | TikTok | @n12news | 1,373,202 | 09-06 | tiktok.com/@n12news |
| | X/Twitter | @N12News | not found | 09-06 | x.com/N12News |
| | Telegram | t.me/N12_News | 2,251 | 09-06 | t.me/N12_News |
| **Channel 13 News** | Facebook | channel13israel | not found (blocked) | 09-06 | facebook.com/channel13israel |
| | Instagram | @reshettv (network-wide, not news-exclusive) | 360K | 09-06 | instagram.com/reshettv |
| | YouTube | Reshet 13 (network channel) | 272K | 09-06 | youtube.com/channel/UCOyYs3ZtsGMmt3L5eaywsXA |
| | TikTok | @reshet13tv | 457,289 | 09-06 | tiktok.com/@reshet13tv |
| | X/Twitter | @channel13il | not found | 09-06 | x.com/channel13il |
| | Telegram | — | not found | 09-06 | — |
| **Now 14 (עכשיו 14)** | Facebook | now14israel | not found (blocked) | 09-06 | facebook.com/now14israel |
| | Instagram | @now14israel | 180K | 09-06 | instagram.com/now14israel |
| | YouTube | C14 (@C14news) | 485K | 09-06 | youtube.com/channel/UCKEImtWikw9usC1pl_9m1nQ |
| | TikTok | @c14news | 1,156,376 | 09-06 | tiktok.com/@c14news |
| | X/Twitter | @C14_news | not found | 09-06 | x.com/C14_news |
| | Telegram | t.me/c14news (2nd, minor: t.me/Now14israel=173) | 11,167 | 09-06 | t.me/c14news |
| **Kan 11 News (כאן חדשות)** | Facebook | not found | not found | 09-06 | — |
| | Instagram | @kan_news | 285K | 09-06 | instagram.com/kan_news |
| | YouTube | @KAN11NEWS | 800K | 09-06 | youtube.com/@kan11news |
| | X/Twitter | @kann_news (note double-n) | 375.9K | 09-06 | x.com/kann_news |
| | TikTok | not found | not found | 09-06 | — |
| | Telegram | @kann_news | 668 | 09-06 | t.me/s/kann_news |
| **Walla News** | Facebook | wallanews | 884,646 | 09-06 | facebook.com/wallanews |
| | Instagram | @wallanews | 117K | 09-06 | instagram.com/wallanews |
| | YouTube | channel UConF7EQiw1TV-_9nMYy8lg | 6,680 | 09-06 | youtube.com/channel/UConF7EQiw1TV-_9nMYy8lgw |
| | TikTok | @walla.news | 601,900 | 09-06 | tiktok.com/@walla.news |
| | X/Twitter | @WallaNews | 90,157 | 09-06 | x.com/WallaNews |
| | Telegram | not found | not found | 09-06 | — |
| **Israel Hayom** | Facebook | IsraelHayom | 744,891 | 09-06 | facebook.com/IsraelHayom |
| | Instagram | @israelhayom | 225K | 09-06 | instagram.com/israelhayom |
| | YouTube | not found | not found | 09-06 | — |
| | TikTok | @israelhayom (inactive, unclaimed) | not found | 09-06 | tiktok.com/@israelhayom |
| | X/Twitter | @IsraelHayom | not found (suspended) | 09-06 | x.com/IsraelHayom |
| | Telegram | @IsraelHayomNews (unconfirmed official) | 196 (unconfirmed) | 09-06 | t.me/s/IsraelHayomNews |
| **Yedioth Ahronoth** (separate from Ynet) | Facebook | not found (no separate page) | not found | 09-06 | — |
| | Instagram | @yedioth | 306K | 09-06 | instagram.com/yedioth |
| | YouTube | @yedioth | 37.7K | 09-06 | youtube.com/@yedioth |
| | TikTok | not found | not found | 09-06 | — |
| | X/Twitter | @yedioth (inactive, 0 posts) | not meaningfully active | 09-06 | x.com/yedioth |
| | Telegram | not found | not found | 09-06 | — |
| **Haaretz (Hebrew)** | Facebook | haaretz | 349,443 | 09-06 | facebook.com/haaretz |
| | Instagram | @haaretz | 125K | 09-06 | instagram.com/haaretz |
| | YouTube | user/haaretzdaily (shared/bilingual) | 36.1K | 09-06 | youtube.com/user/haaretzdaily |
| | TikTok | @haaretz (org acct; edition ambiguous) | 17.8K | 09-06 | tiktok.com/@haaretz |
| | X/Twitter | @Haaretz (Hebrew bio) | 221.2K | 09-06 | x.com/haaretz |
| | Telegram | @haaretz_news (unconfirmed) | 377 (unconfirmed) | 09-06 | t.me/s/haaretz_news |
| **Haaretz (English)** | Facebook | haaretzcom | 537,252 | 09-06 | facebook.com/haaretzcom |
| | Instagram | @haaretzcom | 141K | 09-06 | instagram.com/haaretzcom |
| | YouTube | @haaretzcom | 36.1K | 09-06 | youtube.com/@haaretzcom |
| | TikTok | not found | not found | 09-06 | — |
| | X/Twitter | @haaretzcom | 591,205 | 09-06 | x.com/haaretzcom |
| | Telegram | not found | not found | 09-06 | — |
| **Maariv** | Facebook | maarivonline | 435,051 | 09-06 | facebook.com/maarivonline |
| | Instagram | @maarivonline | 98K | 09-06 | instagram.com/maarivonline |
| | YouTube | @maarivonline | 5.75K | 09-06 | youtube.com/@maarivonline |
| | TikTok | @maarivonline | 44,819 | 09-06 | tiktok.com/@maarivonline |
| | X/Twitter | @MaarivOnline | 66,125 | 09-06 | x.com/MaarivOnline |
| | Telegram | not found | not found | 09-06 | — |
| **Jerusalem Post** | Facebook | TheJerusalemPost | 1,631,053 | 09-06 | facebook.com/TheJerusalemPost |
| | Instagram | @thejerusalem_post | 305K | 09-06 | instagram.com/thejerusalem_post |
| | YouTube | @TheJerusalem_Post (legacy, low use) | 24 | 09-06 | youtube.com/@TheJerusalem_Post |
| | TikTok | @thejerusalempost | 9,569 | 09-06 | tiktok.com/@thejerusalempost |
| | X/Twitter | @Jerusalem_Post | 898,374 | 09-06 | x.com/Jerusalem_Post |
| | Telegram | not found | not found | 09-06 | — |
| **Times of Israel** | Facebook | TimesofIsrael | 1,393,866 | 09-06 | facebook.com/TimesofIsrael |
| | Instagram | @timesofisrael | 233K | 09-06 | instagram.com/timesofisrael |
| | YouTube | @TimesofIsrael | 57.6K | 09-06 | youtube.com/@TimesofIsrael |
| | TikTok | @timesofisrael | 6,211 | 09-06 | tiktok.com/@timesofisrael |
| | X/Twitter | @TimesofIsrael | 660,361 | 09-06 | x.com/TimesofIsrael |
| | Telegram | @TimesofIsrael | 222 | 09-06 | t.me/s/TimesofIsrael |
| **i24NEWS (English)** | Facebook | i24newsEN | 1,034,004 | 09-06 | facebook.com/i24newsEN |
| | Instagram | @i24news | 130K | 09-06 | instagram.com/i24news |
| | YouTube | @i24NEWS_EN | 671K | 09-06 | youtube.com/i24News |
| | TikTok | not found | not found | 09-06 | — |
| | X/Twitter | @i24NEWS_EN | 208,016 | 09-06 | x.com/i24NEWS_EN |
| | Telegram | @i24NEWS_EN | 376 | 09-06 | t.me/s/i24news_en |
| **Globes** | Facebook | globesnews | 218,873 | 09-06 | facebook.com/globesnews |
| | Instagram | @globesnews | 56K | 09-06 | instagram.com/globesnews |
| | YouTube | not found | not found | 09-06 | — |
| | TikTok | @globesnews | 300 | 09-06 | tiktok.com/@globesnews |
| | X/Twitter | @GlobesEnglish (English arm; Hebrew acct unconfirmed) | 4,087 | 09-06 | x.com/GlobesEnglish |
| | Telegram | @GlobesNews | 10,700 | 09-06 | t.me/GlobesNews |
| **Galei Tzahal / GLZ** | Facebook | glzradio | not found (count blocked) | 09-06 | facebook.com/glzradio |
| | Instagram | @glzradio | 47K | 09-06 | instagram.com/glzradio |
| | YouTube | user/GLZradio | 22.5K | 09-06 | youtube.com/user/GLZradio |
| | TikTok | not found | not found | 09-06 | — |
| | X/Twitter | @GLZRadio | 140,505 | 09-06 | x.com/GLZRadio |
| | Telegram | not found | not found | 09-06 | — |
| **Channel 9 / 9tv** | Facebook | 9tvcoil | 172,030 | 09-06 | facebook.com/9tvcoil |
| | Instagram | @9tv.co.il | 27K | 09-06 | instagram.com/9tv.co.il |
| | YouTube | @israel9tv | 465K | 09-06 | youtube.com/@israel9tv |
| | TikTok | not found | not found | 09-06 | — |
| | X/Twitter | @9tv_israel | 1,858 | 09-06 | x.com/9tv_israel |
| | Telegram | @israel_9 | 144K | 09-06 | t.me/israel_9 |
| **Abu Ali Express** | Telegram (primary) | @abualiexpress | 583,000 | 09-06 | t.me/abualiexpress |
| | X/Twitter | @Abualiexpress | 26,202 | 09-06 | x.com/Abualiexpress |
| | Instagram | @abualiexpress | 534 | 09-06 | instagram.com/abualiexpress |
| | TikTok | @abualiexpress | 2,023 | 09-06 | tiktok.com/@abualiexpress |
| | YouTube | @abualiexpress | 2 | 09-06 | youtube.com/@abualiexpress |
| | Facebook | not found | not found | 09-06 | — |

### Key handle-verification notes / disambiguation
- **N12/Mako**: `n12.co.il` is the canonical distinct news brand (mako.co.il/news redirects there); its social accounts (N12News, n12news) are dedicated, not shared with Mako's general portal.
- **Channel 13**: news section shares identical corporate/network accounts with entertainment content (@reshettv) — no news-exclusive social presence exists, unlike N12.
- **Now 14**: now14.co.il redirects to c14.co.il; verified via Wikidata + official YouTube bio links.
- **Kan News**: correct X handle is `kann_news` (double-n) — `kan_news` on X is an unrelated dormant account. No Facebook/TikTok could be confirmed; Kan's many sub-brands make this uncertain rather than absent.
- **Ynet vs Ynetnews**: confirmed via each site's own JSON-LD `sameAs` schema — genuinely separate account sets (only exception: `@ynetnews` TikTok belongs to English edition, easily confused with Ynet Hebrew).
- **Yedioth Ahronoth**: has its own distinct, verified Instagram/YouTube (self-described as "official channel of Yedioth Ahronoth") separate from Ynet, but no separate Facebook/TikTok/Telegram found.
- **Haaretz Hebrew vs English**: Facebook/Instagram/X cleanly separated by language; YouTube/TikTok appear to be shared/ambiguous between editions.
- **i24NEWS**: French/Arabic regional accounts exist separately and were out of scope.
- **Abu Ali Express**: Telegram-native; verified as the largest/genuine channel via Hebrew Wikipedia and cross-linked bios; noted real impersonator risk (not exhaustively ruled out).
- **X/Twitter counts**: could not be retrieved for Ynet, N12, Channel 13, Now 14 (X no longer exposes public counts without login) — handles confirmed via bios but counts marked "not found."
- Several Facebook like-counts (Ynetnews, Channel 13, Now 14, GLZ) are marked "not found" due to Facebook blocking automated access mid-session, not because pages don't exist — handles are verified via other sources.

