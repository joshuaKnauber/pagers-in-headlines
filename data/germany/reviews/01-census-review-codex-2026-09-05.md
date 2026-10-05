## Overall verdict

No — not yet freezable. The core mass set is broadly credible, but there is one mechanical tier error and several freeze-blocking evidence gaps: regional titles, international/non-German-language reach, Deutschlandfunk, and reproducibility of social counts.

## (a) Citation spot-checks

| Claim checked | Verdict | Evidence |
|---|---|---|
| ARD offline reach: 39% DNR 2025 | Accurate | [DNR Germany 2025, p. 25](https://leibniz-hbi.de/wp-content/uploads/2025/06/AP77_RIDNR25_Deutschland.pdf) |
| tagesschau.de online reach: 17% | Accurate | [DNR Germany 2025](https://leibniz-hbi.de/wp-content/uploads/2025/06/AP77_RIDNR25_Deutschland.pdf) |
| t-online online reach: 14% | Accurate | [DNR Germany 2025](https://leibniz-hbi.de/wp-content/uploads/2025/06/AP77_RIDNR25_Deutschland.pdf) |
| bild.de online reach: 14% | Accurate | [DNR Germany 2025](https://leibniz-hbi.de/wp-content/uploads/2025/06/AP77_RIDNR25_Deutschland.pdf) |
| ARD opinion-market share: 20.3% | Accurate | [Medienvielfaltsmonitor 2024, p. 3](https://www.die-medienanstalten.de/fileadmin/user_upload/die-medienanstalten/Forschung/Medienvielfaltsmonitor/Medienvielfaltsmonitor_2024.pdf) |
| Bertelsmann share: 11.0% | Accurate | [Medienvielfaltsmonitor 2024, p. 3](https://www.die-medienanstalten.de/fileadmin/user_upload/die-medienanstalten/Forschung/Medienvielfaltsmonitor/Medienvielfaltsmonitor_2024.pdf) |
| msn.com Nielsen share: 4.5% | Accurate | [Medienvielfaltsmonitor 2024, p. 15](https://www.die-medienanstalten.de/fileadmin/user_upload/die-medienanstalten/Forschung/Medienvielfaltsmonitor/Medienvielfaltsmonitor_2024.pdf) |
| web.de: 3.5%; t-online: 2.8% | Accurate | [Medienvielfaltsmonitor 2024, p. 15](https://www.die-medienanstalten.de/fileadmin/user_upload/die-medienanstalten/Forschung/Medienvielfaltsmonitor/Medienvielfaltsmonitor_2024.pdf) |
| tagesschau Instagram: approximately 7M | Accurate | Independent tracking showed 6.92M; the official page confirms tagesschau’s very large cross-platform footprint. [Social Blade](https://socialblade.com/instagram/user/tagesschau), [tagesschau](https://www.tagesschau.de/ueber-uns/moderatoren-sprecher/tagesschau-social-media-100.html) |
| DER SPIEGEL Facebook: 2.24M | Unverifiable | Correct official handle is supported, but I found no reliable current count at that precision. [SPIEGEL official brand page](https://gruppe.spiegel.de/spiegel-media/spiegel-media-relaunch-test/marken/der-spiegel) |
| DER SPIEGEL Instagram: 2M | Inaccurate | Correct handle, `@spiegelmagazin`, but current independent checks show about 1.59–1.6M, not 2M. [Instastatistics](https://instastatistics.com/spiegelmagazin), [HypeAuditor](https://hypeauditor.com/de/instagram/spiegelmagazin/) |
| WELT YouTube `@WELTVideoTV`: 2.47M | Accurate | [vidIQ](https://vidiq.com/youtube-stats/channel/@weltvideotv/) confirms the handle and 2.47M subscribers. |
| ntv Facebook: 1.2M | Accurate | Official commercial inventory lists 1,201,750 followers and matching platform figures. [Ad Alliance](https://www.ad-alliance.de/portfolio/video/online-video/brands/ntv) |

The social evidence is materially weaker than the survey evidence: the CSV does not provide an account URL for each count, and several figures rely on undocumented external-agent lookups. Counts should be stored with exact handle, URL, retrieval date, and whether they are followers, likes, or subscribers.

## (b) Tier-rule audit

Applying the stated rule mechanically:

| Outlet | Axis A | Axis B | Rule result | CSV tier | Finding |
|---|---:|---:|---:|---:|---|
| Tagesschau | strong | strong | mass | mass | Follows |
| ZDF heute | strong | strong | mass | mass | Follows |
| RTL Aktuell | strong | strong | mass | mass | Follows |
| ntv | strong | strong | mass | mass | Follows |
| Bild | strong | strong | mass | mass | Follows |
| Der Spiegel | strong | strong | mass | mass | Follows |
| WELT | strong | strong | mass | mass | Follows |
| t-online | strong | none | mass via exception | mass | Follows, but must explicitly anchor exception to 2024/2026 current reach |
| Focus Online | strong | weak | substantial | substantial | Follows |
| WEB.DE / GMX | strong | weak | substantial | substantial | Follows |
| ZEIT | weak | strong | substantial | substantial | Follows |
| Süddeutsche Zeitung | weak | strong | substantial | substantial | Follows |
| FAZ | none | weak | niche | niche | Follows |
| stern | none | weak | niche | niche | Follows |
| Handelsblatt | none | weak | niche | niche | Follows |
| taz | none | weak | niche | niche | Follows |
| :newstime | weak | unmeasured | unresolved | niche | **Violation** |
| Deutschlandfunk | unmeasured | weak | unresolved | unresolved | Follows |
| Deutsche Welle | excluded by mission | weak/non-domestic | context | context | Follows |
| Regional/local dailies | category-level mass | unmeasured | unresolved category | unresolved | Follows |
| NIUS | none | weak | niche | niche | Follows |
| Tichys Einblick | none | below weak | niche | niche | Follows |
| Junge Freiheit | none | below weak | niche | niche | Follows |
| Apollo News | none | below weak | niche | niche | Follows |

The `:newstime` row contradicts the notes’ own definition of unresolved: its unmeasured social axis is plausibly decisive, and the outlet is not a minor-medium exception. It should be `unresolved` until social reach is gathered.

Independent judgment on the flagged rows:

- `t-online`: retain `mass`. It satisfies the portal exception at 16% in DNR 2024 and 17% in DNR 2026, both above the 15% threshold. The row must state that the 2025 value alone is below threshold and that the exception is supported by adjacent vintages.
- `WEB.DE / GMX`: retain `substantial`. Merging them is defensible as a newsroom unit, but combined survey reach must not silently be converted into one outlet-level Axis-A score. The current rule correctly prevents mass status because neither individual brand reaches 15% and aggregate social reach is only weak.

## (c) Omissions and unresolved coverage

- **Regional public broadcasters are materially underrepresented.** The Medienvielfaltsmonitor places NDR Fernsehen, WDR Fernsehen, MDR Fernsehen, NDR 1 Gesamt, and WDR 2 among its leading media offerings. The census collapses these into ARD/category rows. That is acceptable only if the collection protocol explicitly says regional public brands are excluded or folded. [Medienvielfaltsmonitor 2024](https://www.die-medienanstalten.de/fileadmin/user_upload/die-medienanstalten/Forschung/Medienvielfaltsmonitor/Medienvielfaltsmonitor_2024.pdf)

- **Podcasts are named in the DNR instrument but not resolved.** The DNR explicitly names *Lage der Nation*, *Lanz & Precht*, and *Was jetzt?* among podcast examples, but does not provide individual weekly reach in the public country report. They cannot be tiered from that report alone, but they remain a plausible omission for a media-consumption census. [DNR Germany 2025](https://leibniz-hbi.de/wp-content/uploads/2025/06/AP77_RIDNR25_Deutschland.pdf)

- **Deutschlandfunk is not ready for a final tier.** Public ma Audio reporting gives Deutschlandfunk approximately 0.47M daily listeners in ma Audio 2025 I, while Deutschlandfunk Kultur reached 0.52M. Fetch the full ma Audio tables and distinguish the Deutschlandfunk news brand from the wider Deutschlandradio portfolio. [Deutschlandradio ma Audio 2025 I](https://www.deutschlandradio.de/ma-audio-2025-1-100.html)

- **International brands:** I found no public, Germany-specific weekly reach figure sufficient to establish BBC, CNN, Al Jazeera, France 24, or Euronews as mass/substantial under the stated rule. Their omission is therefore not proven wrong, but it remains unresolved. The DNR discusses “international news brands” and names BBC as a trust-checking example, which is not the same as a reach estimate. [DNR Germany 2025 Germany page](https://reutersinstitute.politics.ox.ac.uk/digital-news-report/2025/germany)

- **Turkish, Arabic, and Russian-language media:** no reliable Germany-specific audience evidence was found in this pass. This is a serious blind spot because the DNR sample is German-speaking online adults. The census correctly flags it, but that flag should block “complete census” status for a Lebanon-related study.

- **No obvious DNR-listed national German brand is missing from the primary set**, aside from the explicitly unresolved regional/public-radio and podcast categories. The DNR report names the major included brands and categories, but its public chart does not provide enough detail to clear every international or podcast candidate.

## (d) Evidence-quality judgment and minimal fix set

Using DNR 2025 as the principal current Axis-A source is defensible for a present-day census, but not ideal for a September 2024 event. Its fieldwork occurred in early 2025, after the event and during the 2025 election period. DNR 2024 is the closest pre-event baseline; DNR 2025 is a post-event sensitivity check; DNR 2026 is current context, not event-period evidence.

Better corroboration was available and should be used selectively:

- AGF supports Tagesschau’s 2024 daily TV reach of more than 9.5M. [DWDL reporting AGF data](https://www.dwdl.de/zahlenzentrale/100986/tagesschau_weit_vorn_newsreichweiten_bleiben_stabil/)
- IVW/agma should corroborate print and digital brands such as SPIEGEL, FAZ, SZ, ZEIT, and Bild.
- ma Audio should resolve Deutschlandfunk and podcast/radio reach.

Minimal ranked fix set:

1. Change `:newstime` from `niche` to `unresolved`, or collect its verified social reach.
2. Add exact URLs and retrieval dates for every social account; correct SPIEGEL Instagram from 2M to the verified current value.
3. Resolve the regional-public-brand policy: add representative NDR/WDR/MDR rows or document a principled fold/exclusion rule.
4. Fetch ma Audio data for Deutschlandfunk and relevant news audio.
5. Perform a documented BBC/CNN/Al Jazeera/France 24/Euronews check using Germany-specific evidence.
6. Add a documented diaspora-language limitation or a supplemental Turkish/Arabic/Russian audience sweep.
7. Recalculate event-relevant tiers using DNR 2024 as the historical baseline and DNR 2025/2026 only as sensitivity evidence.

Reviewed files: [Germany census CSV](/Users/jknauber/Documents/Projects/news/data/germany/outlet-census-v1.csv), [census notes](/Users/jknauber/Documents/Projects/news/data/germany/census-notes.md), and [collection method](/Users/jknauber/Documents/Projects/news/data/methodology-skills/1_OUTLET_COLLECTION.md).
