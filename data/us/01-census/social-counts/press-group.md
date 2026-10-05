I'll research this by delegating to parallel research agents, each covering 2 outlets, to verify handles against outlet sites and gather current follower counts with sources.





I've launched 4 parallel research agents covering NYT/WaPo, WSJ/USA Today, AP/Reuters, and Axios/LA Times. Each will verify official handles via outlet site footers and pull follower counts with sources across Facebook, Instagram, YouTube, TikTok, and X. Waiting for them to complete.

✗ Fetch YouTube about page and grep subscriber count (shell)
  │ curl -s -A "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)
  │ Chrome/120.0 Safari/537.36" "https://www.youtube.com/@AP/about" -o /tmp/yt.html --max-time 30;
  │ grep -o '"subscriberCountText":{"simpleText":"[^"]*"' /tmp/yt.html | head -3; grep -o
  │ '"videoCountText":{"runs":\[{"text":"[^"]*"' /tmp/yt.html | head -3

✗ Fetch X page and grep followers count (shell)
  │ curl -s -A "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)
  │ Chrome/120.0 Safari/537.36" "https://x.com/AP" -o /tmp/x.html --max-time 30; grep -o
  │ 'followers_count[^,]*' /tmp/x.html | head -5; grep -o '"normal_followers_count":[0-9]*'
  │ /tmp/x.html | head -5; wc -l /tmp/x.html





All four research agents are still actively working (many tool calls completed each). I'll wait for completion notifications.





Three agents done; waiting on WSJ/USA Today agent which is still running (128+ tool calls).


Let me try a few targeted fetches to fill remaining gaps (X and YouTube counts) before compiling the final table.

✗ Fetching web content https://vidstats.io/youtube/channel/@AP · url: "https://vidstats.io/youtube/…
    or not known

✗ Fetching web content https://www.notjustanalytics.com/youtube-channel/AP · url: "https://www.notj…





These platforms are JS-gated and won't yield more than the sub-agents already found. I'll finalize the report using their verified data, keeping "not found" where genuinely unavailable.

## Media Census: US Press Social Media Follower Counts
*All counts accessed 2026-09-05 unless otherwise noted*

| Outlet | Platform | Handle | Count | As-of Date | Source URL |
|---|---|---|---|---|---|
| New York Times | Facebook | facebook.com/nytimes | 22,024,897 likes (~22M) | 2026-09-05 | https://www.facebook.com/nytimes |
| New York Times | Instagram | @nytimes | 20,376,208 (~20M) | 2026-09-05 | https://www.instagram.com/nytimes/ |
| New York Times | YouTube | @nytimes | ~5.25M (SocialBlade est.) | 2026-09-05 | https://socialblade.com/youtube/handle/nytimes |
| New York Times | TikTok | @nytimes | ~3.8M (SocialBlade est.) | 2026-09-05 | https://socialblade.com/tiktok/user/nytimes |
| New York Times | X | @nytimes | 53,856,441 | 2026-09-05 | https://x.com/nytimes |
| Washington Post | Facebook | facebook.com/washingtonpost | 7,931,846 likes (~7.9M) | 2026-09-05 | https://www.facebook.com/washingtonpost |
| Washington Post | Instagram | @washingtonpost | 7,596,552 (shown "8M") | 2026-09-05 | https://www.instagram.com/washingtonpost/ |
| Washington Post | YouTube | @washingtonpost | ~2.85M (SocialBlade est.) | 2026-09-05 | https://socialblade.com/youtube/handle/washingtonpost |
| Washington Post | TikTok | @washingtonpost | ~2.0M (SocialBlade est.) | 2026-09-05 | https://socialblade.com/tiktok/user/washingtonpost |
| Washington Post | X | @washingtonpost | 19,311,528 | 2026-09-05 | https://x.com/washingtonpost |
| Wall Street Journal | Facebook | facebook.com/WSJ | 8,057,382 likes | 2026-09-05 | https://www.facebook.com/WSJ/ |
| Wall Street Journal | Instagram | @wsj | ~6M (displayed) | 2026-09-05 | https://www.instagram.com/wsj/ |
| Wall Street Journal | YouTube | @wsj | not found | 2026-09-05 | https://www.youtube.com/@wsj/about |
| Wall Street Journal | TikTok | @wallstreetjournal ⚠️ | 1.1M | 2026-09-05 | https://www.tiktok.com/@wallstreetjournal |
| Wall Street Journal | X | @WSJ | not found | 2026-09-05 | https://x.com/WSJ |
| USA Today | Facebook | facebook.com/usatoday | 10,521,229 likes (~10M) | 2026-09-05 | https://www.facebook.com/usatoday/ |
| USA Today | Instagram | @usatoday | ~4M (displayed) | 2026-09-05 | https://www.instagram.com/usatoday/ |
| USA Today | YouTube | @USATODAY | not found | 2026-09-05 | https://www.youtube.com/@USATODAY/about |
| USA Today | TikTok | @usatoday | 5.4M | 2026-09-05 | https://www.tiktok.com/@usatoday |
| USA Today | X | @USATODAY | not found | 2026-09-05 | https://x.com/USATODAY |
| AP News | Facebook | @APNews | 2,149,865 likes (~2.15M) | 2026-09-05 | https://www.facebook.com/APNews |
| AP News | Instagram | @apnews | ~2M (displayed) | 2026-09-05 | https://www.instagram.com/apnews/ |
| AP News | YouTube | @AP | not found | 2026-09-05 | https://www.youtube.com/@AP |
| AP News | TikTok | @apnews | not found | 2026-09-05 | https://www.tiktok.com/@apnews |
| AP News | X | @AP | not found | 2026-09-05 | https://x.com/AP |
| Reuters | Facebook | @Reuters | 11,179,428 likes (~11.2M) | 2026-09-05 | https://www.facebook.com/Reuters |
| Reuters | Instagram | @reuters | ~6M (displayed) | 2026-09-05 | https://www.instagram.com/reuters/ |
| Reuters | YouTube | @Reuters | not found | 2026-09-05 | https://www.youtube.com/@Reuters |
| Reuters | TikTok | @reuters | not found | 2026-09-05 | https://www.tiktok.com/@reuters |
| Reuters | X | @Reuters | not found | 2026-09-05 | https://x.com/Reuters |
| Axios | Facebook | @axiosnews | 603,189 likes | 2026-09-05 | https://www.facebook.com/axiosnews |
| Axios | Instagram | @axios | ~335K (displayed) | 2026-09-05 | https://www.instagram.com/axios/ |
| Axios | YouTube | @axios | ~114K (displayed) | 2026-09-05 | https://www.youtube.com/@axios/about |
| Axios | TikTok | @axios.com ⚠️ | 10,400 | 2026-09-05 | https://www.tiktok.com/@axios.com |
| Axios | X | @axios | 854,982 | 2026-09-05 | https://x.com/axios |
| LA Times | Facebook | @latimes | 3,043,422 likes | 2026-09-05 | https://www.facebook.com/latimes |
| LA Times | Instagram | @latimes | ~1M (displayed) | 2026-09-05 | https://www.instagram.com/latimes/ |
| LA Times | YouTube | @latimes | ~701K (displayed) | 2026-09-05 | https://www.youtube.com/@latimes/about |
| LA Times | TikTok | @latimes | 750,800 | 2026-09-05 | https://www.tiktok.com/@latimes |
| LA Times | X | @latimes | 3,831,953 | 2026-09-05 | https://x.com/latimes |

**Handle verification notes:**
- **NYT/WaPo:** Confirmed via platform bio/og:title branding + verification badges; could not load nytimes.com/washingtonpost.com footers directly, so no first-party footer cross-check.
- **WSJ:** ⚠️ **`tiktok.com/@wsj` is squatted/inactive** (14 followers, no bio) — real account is `@wallstreetjournal` (1.1M followers), identified by branding/scale, not a first-party link (wsj.com blocked automated fetch).
- **USA Today:** Handles verified via og:title metadata on each platform; usatoday.com footer was JS-rendered, not fetchable.
- **AP:** `@AP` on X confirmed via `twitter:site` meta tag on apnews.com itself (strongest verification). AP runs many topical/regional sister accounts (`@AP_Politics`, `@APBusiness`) — excluded, using only flagship `@AP`/`@APNews`/`@apnews`.
- **Reuters:** reuters.com blocked automated fetch (401); handles verified via platform bios only. Reuters' own X bio flags sister account `@ReutersBiz` for business news — correctly excluded.
- **Axios:** ⚠️ Axios's own site schema lists `facebook.com/axios` and `tiktok.com/@axios`, but both are **broken/inactive** (dead Facebook link; TikTok has 1 follower). Real active accounts are `facebook.com/axiosnews` and `tiktok.com/@axios.com`, confirmed via bio/tagline match. Regional bureau TikToks (`@axioscharlotte`, etc.) correctly excluded.
- **LA Times:** All handles consistently `latimes` across platforms, verified via latimes.com footer links directly. No squatting found. (Site also runs verticals like `latimes_sports`, `latimes_food` — excluded as non-main accounts.)

**Why several X/YouTube cells are "not found":** X no longer exposes follower counts in public page metadata (only post count/join date remain since 2024–2025 changes), and YouTube subscriber counts are buried in client-side JS not reachable via static fetch. Third-party trackers (SocialBlade, Trackalytics, NoxInfluencer, Nitter) were blocked, discontinued, or geofenced during this research session — reported as "not found" per instructions rather than estimated.

