# Germany — raw social-count evidence (gathered 2026-09-05)

Per-account source data behind the `social_reach_evidence` column of the
census CSV, addressing the review-1 reproducibility requirement: every count
with exact handle, URL, retrieval date, count type, and source type.

Source types: **live** = fetched from the platform page itself (page
HTML/JSON/og:description); **snippet** = Google-indexed snippet of the
platform page's own counter (may lag weeks); **tracker** = third-party
tracker (Social Blade, vidIQ, etc.).

Gathered by: four Claude lookup groups (broadcasters, tabloid/magazine,
broadsheets, denominators) + codex CLI (alt-media) + grok CLI (public
media/portals). Review-1 (codex, archived in `reviews/`) spot-checked 4 of
these accounts; its Spiegel-Instagram correction is applied below.

## Broadcasters (Claude group; handles verified via footers/platform badges)

| Outlet | Platform | Handle | Count | Type | Source |
|---|---|---|---|---|---|
| Tagesschau | FB | facebook.com/tagesschau | 2,379,812 likes / 2.3M followers | live | https://www.facebook.com/tagesschau |
| Tagesschau | IG | @tagesschau | 7M (Social Blade 6.92M) | live/tracker | https://www.instagram.com/tagesschau/ |
| Tagesschau | YT | @tagesschau | 2.21M | live | https://www.youtube.com/@tagesschau |
| Tagesschau | TikTok | @tagesschau (verified) | 2.6M | live | https://www.tiktok.com/@tagesschau |
| Tagesschau | X | @tagesschau | 5.2M | snippet | https://x.com/tagesschau |
| ZDFheute | FB | facebook.com/ZDFheute | 1,737,747 likes / 1.7M | live | https://www.facebook.com/ZDFheute |
| ZDFheute | IG | @zdfheute | 2M | live | https://www.instagram.com/zdfheute/ |
| ZDFheute | YT | @ZDFheute | ~1.86M | live | https://www.youtube.com/@ZDFheute |
| ZDFheute | TikTok | @zdfheute (verified) | 273.5K | live | https://www.tiktok.com/@zdfheute |
| ZDFheute | X | @ZDFheute | 1.3M | snippet | https://x.com/ZDFheute |
| RTL Aktuell | FB | facebook.com/RTLaktuell | 1,424,907 likes / 1.4M | live | https://www.facebook.com/RTLaktuell |
| RTL Aktuell | IG | @rtlaktuell | 712K | live | https://www.instagram.com/rtlaktuell/ |
| RTL Aktuell | YT | @rtl_aktuell (verified; @rtlaktuell 404s) | ~126K | live | https://www.youtube.com/@rtl_aktuell |
| RTL Aktuell | TikTok | @rtlaktuell (verified) | 821.6K | live | https://www.tiktok.com/@rtlaktuell |
| RTL Aktuell | X | @rtl_aktuell | not sourceable | — | — |
| ntv | FB | facebook.com/ntvNachrichten | 1,202,264 likes / 1.2M (Ad Alliance: 1,201,750 — review-1 corroborated) | live | https://www.facebook.com/ntvNachrichten |
| ntv | IG | @ntv_nachrichten | 644K | live | https://www.instagram.com/ntv_nachrichten/ |
| ntv | YT | @n-tv (⚠ @ntv is Turkish NTV) | 423K | live | https://www.youtube.com/@n-tv |
| ntv | TikTok | @ntv.de (verified; @ntv.nachrichten is fake) | 655.7K | live | https://www.tiktok.com/@ntv.de |
| ntv | X | @ntvde | 951.5K | snippet | https://x.com/ntvde |
| WELT | FB | facebook.com/welt | 1,256,904 likes / 1.2M | live | https://www.facebook.com/welt/ |
| WELT | IG | @welt | 978K | live | https://www.instagram.com/welt/ |
| WELT | YT | @WELTVideoTV (⚠ @welt squatted, 45 subs) | 2.47M (vidIQ corroborated, review-1) | live | https://www.youtube.com/@WELTVideoTV |
| WELT | TikTok | none official (welt.de lists none) | not found | — | — |
| WELT | X | @welt | 2.5M | snippet | https://x.com/welt |

## Tabloid / magazine / portal (Claude group; footers checked)

| Outlet | Platform | Handle | Count | Type | Source |
|---|---|---|---|---|---|
| Bild | FB | facebook.com/bild | 2,941,603 likes | snippet | https://www.facebook.com/bild/ |
| Bild | IG | @bild | ~1M | snippet | https://www.instagram.com/bild/ |
| Bild | YT | @bild | 1.78M | live | https://www.youtube.com/@bild |
| Bild | TikTok | none official (footer lists none; @bild squatted) | not found | — | — |
| Bild | X | @BILD | ~2M | snippet | https://x.com/bild |
| Der Spiegel | FB | facebook.com/derspiegel | 2,239,132 likes (review-1: unverifiable at that precision — treat as ~2.2M) | snippet | https://www.facebook.com/derspiegel/ |
| Der Spiegel | IG | @spiegelmagazin (⚠ @derspiegel IG is not Spiegel) | ~1.6M (review-1 corrected from 2M snippet; HypeAuditor/Instastatistics 1.59–1.6M) | tracker | https://hypeauditor.com/de/instagram/spiegelmagazin/ |
| Der Spiegel | YT | @derspiegel | 2.33M | live | https://www.youtube.com/@derspiegel |
| Der Spiegel | TikTok | @derspiegel | 302.7K | live | https://www.tiktok.com/@derspiegel |
| Der Spiegel | X | @derspiegel | ~3.2M | snippet | https://x.com/derspiegel |
| Focus Online | FB | facebook.com/focus.de | 993,314 likes | snippet | https://www.facebook.com/focus.de/ |
| Focus Online | IG | @focus_online | ~176K | snippet | https://www.instagram.com/focus_online/ |
| Focus Online | YT | @focusonline | 368K | live | https://www.youtube.com/@focusonline |
| Focus Online | TikTok | @focus_online (⚠ @focusonline is a squat) | 70.8K | live | https://www.tiktok.com/@focus_online |
| Focus Online | X | @focusonline | ~796.4K | snippet | https://x.com/focusonline |
| stern | FB | facebook.com/stern | 770,401 likes | snippet | https://www.facebook.com/stern/ |
| stern | IG | @stern | ~396K | snippet | https://www.instagram.com/stern/ |
| stern | YT | @sternde | 180K | live | https://www.youtube.com/@sternde |
| stern | TikTok | @stern_de (⚠ @stern is a private user) | 168.9K | live | https://www.tiktok.com/@stern_de |
| stern | X | @sternde | ~1.2M | snippet | https://x.com/sternde |
| t-online | FB | facebook.com/tonline | 442,982 likes | snippet | https://www.facebook.com/tonline/ |
| t-online | IG | @tonline.de | ~117K | snippet | https://www.instagram.com/tonline.de/ |
| t-online | YT | @tonline | 44.6K | live | https://www.youtube.com/@tonline |
| t-online | TikTok | @tonline.de (verified, dormant: 3 videos) | 1,070 | live | https://www.tiktok.com/@tonline.de |
| t-online | X | @tonline | ~14.6K | snippet | https://x.com/tonline |

## Broadsheets / weeklies (Claude group; footers checked)

| Outlet | Platform | Handle | Count | Type | Source |
|---|---|---|---|---|---|
| ZEIT | FB | facebook.com/zeitonline | 876K followers / 804K likes | snippet | https://www.facebook.com/zeitonline/ |
| ZEIT | IG | @zeit | 2M (live; Google cache showed stale 1M) | live | https://www.instagram.com/zeit/ |
| ZEIT | YT | @zeit (legacy /zeitonline redirects) | 250K | live | https://www.youtube.com/@zeit |
| ZEIT | TikTok | @zeit (verified) | 465.4K | live | https://www.tiktok.com/@zeit |
| ZEIT | X | @zeitonline | 2.3M | snippet | https://x.com/zeitonline |
| SZ | FB | facebook.com/ihre.sz | 824,943 likes | live | https://www.facebook.com/ihre.sz/ |
| SZ | IG | @sz | 986K | live | https://www.instagram.com/sz/ |
| SZ | YT | @sueddeutsche (⚠ @sz squatted) | 26.8K | live | https://www.youtube.com/@sueddeutsche |
| SZ | TikTok | @sueddeutsche (verified; @sz empty) | 62.3K | live | https://www.tiktok.com/@sueddeutsche |
| SZ | X | @SZ | 1.7M | snippet | https://x.com/SZ |
| FAZ | FB | facebook.com/faz | 570,363 likes | live | https://www.facebook.com/faz/ |
| FAZ | IG | @faz | 774K | live | https://www.instagram.com/faz/ |
| FAZ | YT | @faz | 327K | live | https://www.youtube.com/@faz |
| FAZ | TikTok | @faz (verified) | 162.8K | live | https://www.tiktok.com/@faz |
| FAZ | X | @faznet | 891K | snippet | https://x.com/faznet |
| taz | FB | facebook.com/taz.kommune | 322,917 likes | live | https://www.facebook.com/taz.kommune/ |
| taz | IG | @taz.die_tageszeitung | 443K | live | https://www.instagram.com/taz.die_tageszeitung/ |
| taz | YT | @dietageszeitung (⚠ @taz is not the paper) | 27.2K | live | https://www.youtube.com/@dietageszeitung |
| taz | TikTok | @taz.die_tageszeitung | 14.9K | live | https://www.tiktok.com/@taz.die_tageszeitung |
| taz | X | @tazgezwitscher (FROZEN — protected/dormant since taz left X) | 614.8K | snippet | https://x.com/tazgezwitscher |
| Handelsblatt | FB | facebook.com/handelsblatt | 345,564 likes | live | https://www.facebook.com/handelsblatt/ |
| Handelsblatt | IG | @handelsblatt | 569K | live | https://www.instagram.com/handelsblatt/ |
| Handelsblatt | YT | @handelsblattvideo (@handelsblatt 404s) | 171K | live | https://www.youtube.com/@handelsblattvideo |
| Handelsblatt | TikTok | @handelsblatt (verified; relaunched ~Jan 2026) | 13.4K | live | https://www.tiktok.com/@handelsblatt |
| Handelsblatt | X | @handelsblatt | 445.1K | snippet | https://x.com/handelsblatt |

## Public media / portals (grok CLI; official-list/impressum verified)

| Outlet | Platform | Handle | Count | Type | Source |
|---|---|---|---|---|---|
| Deutschlandfunk | FB | facebook.com/deutschlandfunk | 217.1K | snippet | https://www.facebook.com/deutschlandfunk |
| Deutschlandfunk | IG | @deutschlandfunk (HypeAuditor 673,898) | 675K | live/tracker | https://www.instagram.com/deutschlandfunk/ |
| Deutschlandfunk | YT | @deutschlandfunk (channel created Jul 2024) | 8.05K | live | https://www.youtube.com/@deutschlandfunk |
| Deutschlandfunk | TikTok | @moment.mal.dlf (official format account) | 43.7K | live | https://www.tiktok.com/@moment.mal.dlf |
| Deutschlandfunk | X | @DLF (INACTIVE since Jan 2024; 314K at departure per Tagesspiegel) | 277.5K | live | https://x.com/DLF |
| DW (German) | YT | @dwdeutsch | 1.14M | live | https://www.youtube.com/@dwdeutsch |
| DW (German) | X | @dw_deutsch (protected) | 108.1K | tracker | https://x.com/dw_deutsch |
| DW (German) | FB/IG/TikTok | no German-news accounts available/found | not found | — | see grok notes: dw.german FB unavailable; @dwnews IG is English |
| WEB.DE News | FB | facebook.com/WEB.DE | 681K | live | https://www.facebook.com/WEB.DE |
| WEB.DE News | IG | @webde_news | 15.1K | live | https://www.instagram.com/webde_news/ |
| WEB.DE News | X | @WEBDENews (dormant since Jan 2025) | 3,960 | live | https://x.com/WEBDENews |
| GMX News | FB | facebook.com/GMX.DE | 541K | live | https://www.facebook.com/GMX.DE/ |
| GMX News | IG | @gmx_news | 8,434 | live | https://www.instagram.com/gmx_news/ |
| GMX News | TikTok | @gmx_news (bio links gmx.net/impressum) | 20.8K | live | https://www.tiktok.com/@gmx_news |

## Alt-media (codex CLI)

| Outlet | Platform | Handle | Count | Type | Source |
|---|---|---|---|---|---|
| NIUS | FB | facebook.com/stimmedermehrheit | 211K | publisher deck | https://sales.nius.de/ |
| NIUS | IG | @nius.de (official status unconfirmed) | 467K | publisher deck | https://sales.nius.de/ |
| NIUS | YT | @niusde | 586,236 | tracker | https://socialcounts.org/youtube-channel-analytics/UCQGqiGhMjc_p4lZEhSTb12g |
| NIUS | X | @niusde_ | 171,830 | publisher deck | https://sales.nius.de/ |
| Junge Freiheit | IG | @jungefreiheit | 135.7K | tracker | https://socialveins.com/influencer/instagram/jungefreiheit |
| Junge Freiheit | YT | @junge_freiheit | 218K | tracker | https://socialblade.com/youtube/handle/junge_freiheit |
| Tichys Einblick | YT | @TichysEinblick | 354K | tracker | https://vidiq.com/youtube-stats/channel/%40tichyseinblick/ |
| Tichys Einblick | X | @TichysEinblick | 253K | tracker | https://mobile.twstalker.com/TichysEinblick |
| Apollo News | IG | @apollo_news | 52,607 | tracker | https://socialblade.com/instagram/user/apollo_news |
| Apollo News | YT | @apollonewsnet | 291K | tracker | https://socialblade.com/youtube/handle/apollonewsnet |

## Platform denominators (DataReportal, early 2025, ad-reach basis)

Facebook 24.5M · Instagram 31.3M · YouTube 65.5M · TikTok 21.8M · X 21.6M
users in Germany.
