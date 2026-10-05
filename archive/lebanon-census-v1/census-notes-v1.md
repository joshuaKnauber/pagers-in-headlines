# Lebanon outlet census — evidence notes (v1, 2026-09-05)

Companion to [outlet-census-v1.csv](outlet-census-v1.csv). Everything below is
what the evidence says, where it conflicts, and what is still missing. No tier
is final until the conflicts are resolved.

## The structural finding that reframes the census

Arab Barometer Wave VIII (Lebanon report, September 2024, fieldwork 2023–24):

- **53% of Lebanese say social media is their primary source of breaking
  news; television is second at 31%** — the first wave where social passed TV.
  Social is up 14 points since 2022; TV down 18 points.
- The age gradient is extreme: 75% of 18–29-year-olds name social media as
  primary; 53% of the 50+ group still name television.
- Platform usage: WhatsApp 96%, Facebook 82%, YouTube 48%, TikTok 47%,
  Instagram 46%.

Source: [AB8 Lebanon Country Report (PDF)](https://www.arabbarometer.org/wp-content/uploads/AB8-Lebanon-Country-Report-EN.pdf)

Implication: TV audience share alone no longer defines "reach" in Lebanon.
An outlet's distribution on Facebook/WhatsApp is part of its reach, and the
census eventually needs a social-followership evidence column. Not gathered in
this pass.

## TV audience: two vintages, one unresolved conflict

- **Ipsos TAM Q1–Q2 2018** (via MOM outlet pages): Al-Jadeed 35.6%,
  MTV 32.5%, OTV 16.4%, Al-Manar 6.4%, LBCI "missing data".
- **ELKA 2024** (via MOM Lebanon 2024 findings): top-4 TV companies hold
  ~78–80% of the audience; Al-Manar 11%.
- **Conflict:** different renderings of the MOM findings page name different
  top-4 lists (LBCI/Al-Jadeed/MTV/OTV at 78.1% vs. MTV/LBC/Al-Manar/Al-Jadeed
  at 80%) and give LBCI both 25.8% ("market leader") and 13%. Per-outlet 2024
  numbers for MTV, Al-Jadeed, LBCI could not be pinned down from the fetched
  pages.
- **Resolution route:** MOM Lebanon 2024 publishes a full report; get the PDF
  or contact ELKA Lebanon. Until then, mass-tier membership (LBCI, MTV,
  Al-Jadeed, Al-Manar, likely OTV) is solid; the ordering is not.

Sources: [MOM findings](https://lebanon.mom-gmr.org/en/findings/findings/),
[MOM TV database](https://lebanon.mom-gmr.org/en/media/tv/), per-outlet MOM
pages.

## Pan-Arab and international consumption inside Lebanon

Ahrefs (organic-search visits, Lebanon, Aug 2026) top news sites:
aljazeera.net #1 (97.9K/mo), almayadeen.net #2 (69.3K), 961today.com #3
(52.2K), bbc.com #6 (46.4K), almanar.com.lb #8 (34.4K), elnashra.com #9
(34.1K), mtv.com.lb #12 (25K).
Source: [AhrefsTop Lebanon news](https://ahrefstop.com/websites/lebanon/news)

This confirms the audience-side framing: Lebanese digital news consumption is
led by pan-Arab outlets (Al Jazeera, Al Mayadeen), not domestic ones. Caveats:
organic-search visits only (no direct/social/app traffic), and the snapshot is
Aug 2026, not Sep 2024.

- ELKA 2024 explicitly did **not** measure online outlet audiences — there is
  no gold-standard domestic digital measurement.
- No Lebanon-specific TV viewership share found yet for Al Jazeera or
  Al Arabiya (the NU-Q 2017 interactive would have it but did not render).

## Radio and print: measured, and small

ELKA 2024 via MOM findings:

- Only **35%** listen to radio at all; top-4 stations = 54% of that. Largest:
  Radio Liban Libre 7%, Al-Nour 5%, Radio Orient 3%.
- **72%** read no print newspaper; top-4 papers (Annahar, Al-Akhbar, Addiyar,
  L'Orient-Le Jour) = 89% of remaining readership.

Print's absolute reach is small, but print editions matter for the corpus for
a different reason: page placement and full-text preservation (Al-Akhbar
/Issues/ PDFs).

## Known gaps for evidence round 2

1. Per-outlet ELKA 2024 TV shares (MOM report PDF or ELKA directly).
2. Social-media followership/engagement per outlet (Facebook page sizes,
   WhatsApp channel subscribers) — given AB8, this is now the largest reach
   channel and completely undocumented here.
3. Al Jazeera / Al Arabiya TV viewership inside Lebanon (NU-Q Media Use
   surveys; Ipsos pan-Arab measurement if accessible).
4. Domestic digital natives (Lebanon24, Naharnet, LebanonFiles, Lebanon
   Debate): no audience evidence at all yet — SimilarWeb country category
   pages or press-kit claims with low confidence.
5. Publication status check: Addiyar, Al Joumhouria (print market has been
   collapsing; a 2024 top-4 slot may overstate a barely-alive paper).
6. Diaspora consumption is out of scope for the country gate but worth a note:
   961Today's #3 search rank suggests English/diaspora demand.

## Method notes

- "Audience share" (share of viewers) and "reach" (% of population touched)
  are different metrics; sources mix them. Columns record what the source
  said, verbatim, rather than harmonizing prematurely.
- MOM Lebanon 2024 is itself an RSF/SKeyes project; its audience numbers are
  ELKA's, its ownership/affiliation data is its own research — cited for both
  separately.
- Confidence ratings: `high` = consistent recent measurement; `medium` =
  measured but dated, partial, or proxy; `low` = listed/known but unmeasured;
  `none` = no evidence found this pass.
