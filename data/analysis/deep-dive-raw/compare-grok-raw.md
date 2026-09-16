I'll start by inspecting the corpus schema and known findings, then run cross-country Python analysis on the four JSONL files.I'll inspect the schema and existing analysis, then compute story-beat, casualty, quote, and vocabulary comparisons across the four corpora.Schema is clear. Next I’ll filter to primary relevant records and run the story-beat, casualty, quote, decay, and vocabulary comparisons.The first pass is too noisy: US body length and loose terms inflate hits. I’ll tighten the patterns and check for extraction contamination.The four corpora are not covering the same event. They are covering four different events that happened to share some exploding hardware. Same-story tests on Fatima, Gold Apollo, Nasrallah, the funeral-wave, and the death toll make that concrete.

**Filter:** primary records, `relevance` in {strong, related}. n = LB 338, IL 157, DE 176, US 134. Body-keyword rates for the US (mean article 1,160 words) and Lebanon (mean article 278 words, 122/338 empty ticker bodies) are not comparable. Headline rates and named-entity hits are the cleaner evidence. US/DE "related" records bleed later-war coverage into the pager corpus; I flag that where it matters.

---

### 1. Fatima Abdullah is a New York story. Beirut did not name her.

The 9-year-old girl who became the Western human face of the attack is named in **3/134 US records (2.2%)**, including a dedicated NYT funeral piece (`us_nyt_4a725a8429`, day_1, "Funeral Is Held for 9-Year-Old Girl Killed in Pager Attack in Lebanon"). ABC (`us_abc_61d9dac625`) names her at the funeral. Yahoo (`us_yahoo_9ee477059c`) copies the ABC graf.

Lebanon names her **once**, buried inside an Al-Manar newspaper digest (`lb_almanar_12484837`, day_1, 3,353 words, "الصحافة اليوم: 18-9-2024"): "الشهداء ابن النائب علي عمار محمد مهدي (40 سنة) والطفلة فاطمة جعفر عبدالله" ("the martyrs include MP Ali Ammar's son Mohammad Mahdi, 40, and the little girl Fatima Jaafar Abdullah"). No dedicated story. No headline. MTV's funeral piece (`lb_mtv_1485572`) names four "martyrs" including **scout child Mohammad Bilal Kanj**, not Fatima. LBCI English (`lb_lbci_796442`) leads with the MP's son and calls her "10-year-old" via AFP, in the Bekaa, unnamed.

Israel's one "פאטמה" hit is a false positive: Iranian spokeswoman Fatemeh Mohajirani (`il_ynet_c37ebc84bf`, 18 words). Germany never names her. Spiegel gets as close as "Zwei Kinder unter Opfern der Pager-Explosionen" (`ge_spiegel_1ab085ff34`). Child-in-headline counts: US 2, LB 1, IL 1, DE 1.

**Why interesting / next:** Lebanese coverage treats child deaths as a count ("طفلان") and names political-family victims. US coverage names the girl and stages the funeral. Pull the Al-Manar digest vs NYT side by side, and check the 9 vs 10 year-old / Saraain vs Bekaa discrepancy. Do not read "children" in US bodies (72/134) as signal. Fox/Yahoo related-rails dump "children" from unrelated stories.

**Confidence:** high on the named-entity split. Medium on the age/place discrepancy (single AFP graf vs NYT correspondent in Saraain).

---

### 2. The supply chain is an export story. LBCI's English desk is a fifth country.

Tight Gold Apollo / BAC hits (not the loose Taiwan/Hungary net):

| | body+headline | in headline |
|---|---|---|
| US | 45/134 (**33.6%**) | **2** (both the Reuters BAC wire) |
| DE | 25/176 (14.2%) | 2 |
| IL | 21/157 (13.4%) | **0** |
| LB | 26/338 (7.7%) | 8 |

The 8 Lebanese headlines are almost all LBCI, and half are the English-language desk running the wire in parallel (`lb_lbci_796586`, `796626`, `796688`). Arabic Gold Apollo is 16/275 (5.8%); English is 10/63 (15.9%). Device-count "4,000/5,000" appears in **47/134 US (35%)** vs **5/338 LB (1.5%)**. The phrase "supply chain" is in 32/134 US records and 3 US headlines (`us_cnn_28967cf7ba` "mysterious supply chain stretching from Taiwan"; `us_yahoo_ae4f6eb3f5`). Lebanon's equivalent is LBCI English asking "Did Israel infiltrate the global supply chain?" (`lb_lbci_797305`).

Spiegel, on day_0, titled the whole event **Operation »Gold Apollo AR-924«** (`ge_spiegel_56bd1c4430`, 2024-09-17). That is branding the attack after the device model before Gold Apollo had even issued its denial. The body is paywall chrome, so we cannot read what they actually wrote.

**Why interesting / next:** Distant desks need a detective plot. The victim country's Arabic desks do not. LBCI English is behaving like a small AP, not like MTV or Al-Manar. Split the Lebanese corpus by language before any cross-country vocab work. Check whether Spiegel's day_0 title is reconstruction after the fact or a real Sep 17 framing (ld-json says Sep 17, but the body is a 30-day linkwall).

**Confidence:** high on the rate split. Speculative on Spiegel's day_0 title reflecting actual day_0 knowledge.

---

### 3. Germany ran the legality story. Nobody else did, as a story.

Three dedicated international-law pieces, all public-broadcaster or Spiegel, none of them "related" bleed:

- ZDF, day_2: "Pager-Explosionen im Libanon: Die Völkerrechts-Frage" (`ge_zdfheute_d886ea02f0`, 665 words). Opens: "War das erlaubt?"
- Tagesschau, day_3: "Völkerrechtler uneins über Legitimität von Libanon-Angriffen" (`ge_tagesschau_5487e7d8f1`, 1,013 words)
- Spiegel, day_4: "Uno-Menschenrechtschef rückt Pager-Attacke in Nähe von Kriegsverbrechen" (`ge_spiegel_894b2658f7`), quoting Volker Türk: "Gewalt mit der Absicht, Terror unter der Zivilbevölkerung zu verbreiten, ist ein Kriegsverbrechen"

The US equivalents are two Yahoo *opinion* pieces (`us_yahoo_1877937746` "Pager attack in Lebanon was terrorism. And Americans helped pay for it."; `us_yahoo_e0525fd211` "Even Leon Panetta Says Israel’s Pager Attack Is 'Terrorism'"), against Fox's "spectacular pager explosion operation" (`us_fox_a82ba395ba`). Lebanon's health minister calls it a war crime in an MTV ticker (`lb_mtv_1486283`: "أبيض: ما حدث نعتبره جريمة حرب لأن معظم المصابين... هم من المدنيين"), not in an explainer. Israel has no legality-explainer headline. Kikar ran "Documentation: Hezbollah terrorist buying vegetables, and the pager explodes" (`il_kikar_0e0bc3ddb6`).

**Why interesting / next:** German public broadcasting treated the event as a legal puzzle. US treated it as either terrorism-or-not opinion or as an intel coup. Code "is this a war crime?" as a story-function, not a keyword. Tagesschau vs Fox vs Kikar on day_0–day_3 is a three-way exhibit.

**Confidence:** high.

---

### 4. Nasrallah is a quoted figure abroad, a ticker at Al-Manar, and a calendar item in Israel.

Records naming Nasrallah (or "secretary-general" / Hisbollah-Chef): LB **16/338 (4.7%)**, IL 26/157 (16.6%), DE 75/176 (42.6%), US 64/134 (47.8%). Headline: LB 5, IL 5, DE 6, US 6.

The 5 Lebanese headlines are 1 LBCI ticker plus 4 Al-Manar briefs quoting the speech, including the naming formula he wanted: "سنتبنى تسمية مجزرة الثلاثاء ومجزرة الاربعاء" / "We will adopt the names Tuesday massacre and Wednesday massacre" (`lb_almanar_12494649`, day_3, empty body). MTV, LBCI Arabic, and Al Jadeed barely mention him.

Israel scheduled him. Ynet flash, day_1: "אחרי פיצוץ הביפרים: נסראללה ינאם מחר ב-17:00" / "After the pager explosion: Nasrallah will speak tomorrow at 17:00" (`il_ynet_2662c441b6`, 30 words). N12 day_2: "החל נאום נסראללה" / "Nasrallah's speech has begun" (`il_n12_ffc3325683`). US headlines never put his name on a pager story. They quote the "declaration of war" line inside 1,000-word roundups.

**Why interesting / next:** The attacked party's leader is least present in the attacked country's commercial media. Al-Manar is doing speech-distribution, not news. Israel is doing event TV. Distant media are doing a Hezbollah-character insert. Outlet-level, not country-level: drop Al-Manar and Lebanese Nasrallah nearly vanishes.

**Confidence:** high.

---

### 5. The death toll in the headline never agreed, and the health minister is a citation for export.

Headline death numbers (pager/walkie, not later airstrikes):

- **Lebanon** tracks the health minister's running tally in real time: 8 (`lb_lbci_796455`, day_0, English) → 12 (`lb_lbci_796667`, day_1) → 9 then 14 then 32 combined on Al-Manar day_2 (`lb_almanar_12488005`, `12488412`, `12492053`) → MTV day_4 splits it "12 martyrs in the pager blast and 27 in the wireless-device blast" (`lb_mtv_1486647`).
- **Israel** freezes on **9 dead** in day_0/day_1 headlines (`il_ynet_12a58ccc24`, `il_ynet_10b5fdd863`). Walkie-wave headlines then say 14 (`il_ynet_50c8c2a27c`, `il_abuali_75867`). They do not publish the combined 32/37.
- **Germany/US** almost never put the pager death toll in the headline. US ABC/Yahoo file the second wave as "Israel-Hamas war latest: 14 killed, 450 wounded" (`us_abc_41b079c45e`, `us_yahoo_84cb223cdf`). DE headline death numbers on day_6 are airstrike counts (Spiegel "Fast 500 Tote", RND "100 Tote"), not pagers.

The Lebanese health minister (Firas Abyad / الأبيض) is named in **51/176 DE (29%)** and **32/134 US (23.9%)**, against **12/338 LB (3.6%)** and 6/157 IL (3.8%). Distant copy uses him as the casualty-source formula ("Lebanon's health minister said..."). Lebanese copy uses him as a ticker: "الأبيض: 25 شهيداً و608 جرحى" (`lb_mtv_1485838`). Same man, different news function.

**Why interesting / next:** Do not average "the death toll the country reported." Israel stopped updating. Lebanon kept a ledger. US/DE outsourced the number to a named minister and moved on. Reconstruct a day-by-day number-in-lede table. The 9 vs 12 vs 32 vs 37 spread is the finding.

**Confidence:** high on headlines. Medium on lede number extraction (regex catches adjacent-day airstrike 37s).

---

### 6. Israel killed the casualty story on day 3 and came back with "1,500 blinded terrorists."

Time-slot share, all primary records:

| | day_0 | day_1 | day_2 | day_3 | day_4+ |
|---|---|---|---|---|---|
| LB | 15.4% | 34.0% | 16.6% | **10.9%** | 14.2% |
| IL | 22.3% | 39.5% | 13.4% | **2.5%** (4 records) | 21.7% |
| DE | 10.8% | 30.7% | 15.9% | 9.1% | **33.5%** |
| US | 10.4% | 29.9% | 17.9% | 13.4% | 28.4% |

The known day_1 peak is real. What is new is Israel's **day_3 collapse**: 4 records, all spy-plot. Ynet "The mystery of the shell companies, the vanished Indian hi-tech man" (`il_ynet_895142082c`). Ynet flash quoting Taiwan's economy minister (`il_ynet_34804fbedf`). Kikar "the pager attack was planned for at least 15 years" (`il_kikar_13b0dde8ca`). Makan Arabic on Taiwan questioning Gold Apollo's boss (`il_makan_ce489390ca`). Zero casualty updates.

Then week_2, Israel returns with a military-effect frame nobody else led: "כ-1,500 מחבלי חיזבאללה התעוורו או איבדו יד" / "~1,500 Hezbollah terrorists blinded or lost a hand" (`il_ynet_3e0ef50525`, Reuters pickup). Kikar: "a Hezbollah source: we lost 1,500 fighters" (`il_kikar_a5de7caca9`). Lebanon has **one** MTV Reuters pickup (`lb_mtv_1489095`). NYT's late take is the opposite judgment: "Israel’s Pager Attack Was a Tactical Success Without a Strategic Goal" (`us_nyt_239261eaa4`).

DE's fat tail is mostly **related-war bleed** (Nasrallah killing, airstrikes). Strong-only day_4+ is LB 15.3%, DE 15.3%, US 18.3%, **IL 24.3%**. Israel is the one that actually came back to the pager story, as a success feature.

**Why interesting / next:** The attacker-side attention curve is two-humped: breaking news, then "how we did it / what it cost them." Victim-side is a ledger that gets buried. Plot strong-only curves, not all-records. The 1,500 figure is a Reuters number that Israel turned into a headline and Lebanon did not.

**Confidence:** high on the day_3 count and the 1,500 headlines. Medium on interpreting DE's raw tail (related coding).

---

### 7. Same funeral, two stories. Blood tents vs walkie-on-video.

Day_1, Al Jadeed ran a 47-word tweet-story: "بالفيديو - لحظة انفجار جهاز لاسلكي أثناء تشييع في الضاحية الجنوبية" / "On video: the moment a wireless device exploded during a funeral in the southern suburbs" (`lb_aljadeed_502746`). The second wave is the news. The funeral is the location.

The same day, US headlines are the funeral as human-interest: NYT's Fatima piece, ABC "Explosions witnessed at Beirut funeral for Hezbollah members and a child" (`us_abc_61d9dac625`), Yahoo "Blast heard near site of Beirut funeral" (`us_yahoo_5f33d95679`). Funeral-in-headline: US 3, LB 2, IL 1, DE 0. Body "funeral" in US (38/134) is not usable (chrome).

Al-Manar, also day_1, ran the civic-response story that exists nowhere else: "اقبال كثيف على التبرع بالدم في المناطق اللبنانية اسناداً لجرحى العدوان الصهيوني" / "Heavy turnout for blood donation across Lebanese regions in support of the wounded of the Zionist aggression" (`lb_almanar_12483099`). Mosque loudspeakers, tents on Hadi Nasrallah highway. Blood-donation hits: LB 5, DE 7, US 3, **IL 0**. MTV compared the injuries to the 2020 port blast: "إصابات تفجيرات البيجر أشدّ من انفجار المرفأ" (`lb_mtv_1485664`). Israel has no port-blast comparison.

**Why interesting / next:** "Hospital overwhelm" as a Western scene-setter (NBC `us_nbc_351cd1ae85` "Doctors overwhelmed by blast injuries") is not the same story as Al-Manar's blood tents or MTV's port-blast comparison. Code civic-response vs medical-horror vs funeral-as-victim vs funeral-as-second-wave-location as four functions.

**Confidence:** high.

---

### 8. You are not comparing articles. Plus the corpora are dirty in different ways.

Document-type mix:

| | article | short form |
|---|---|---|
| LB | 190 (56%) | brief 76 (22%) + live_ticker 72 (21%) |
| IL | 80 (51%) | flash_or_lead 58 (37%) + telegram 19 (12%) |
| DE | 151 (86%) | flash_or_lead 25 (14%) |
| US | 133 (**99%**) | 1 flash |

Mean article word count: US 1,160 · DE 661 · IL 376 · LB 278. A US "record" is a 1,100-word roundup that mentions Gaza (79/104 strong US records), Iran, Biden, and the supply chain because that is the template. A Lebanese "record" is often a 0-word ticker. Provenance.credit says wire share is similar (LB 14%, IL 15%, DE 14%, US 13%). That is a lie about news culture. t-online is **20/36 dpa (56%)**. Spiegel is 0/33 credited. Yahoo is tagged 5/30 wired and is clearly more than that.

Gaza wrapping is the US file name. Headline "Israel-Hamas war latest" on the walkie-talkie day (`us_abc_41b079c45e`, `us_yahoo_84cb223cdf`). LB Gaza/Hamas in body: 16/338 (4.7%). The victim country did not file this under Gaza.

**Data-quality suspicions (do not skip these):**

1. **US related-rail chrome.** "slowdown" in 55/134 records (Fox/Yahoo/CNN sidebar: "AI leaders urge development slowdown"). "Trump" in 71/134, mostly rails. Yahoo opinion body opens with "Student suspended over cup of coffee / Trump responds to AI slowdown" (`us_yahoo_1877937746`). Body-keyword comparison against US is unsafe until de-chromed. Headlines still work.
2. **t-online: 36/36 empty headlines** (20.5% of the German corpus). Bodies start with image captions and "Artikel teilen".
3. **Spiegel paywall residue.** 4/33 bodies contain "Sie können den Artikel leider nicht mehr aufrufen." `ge_spiegel_56bd1c4430` is one of them.
4. **Lebanon: 122/338 empty bodies** (all ticker/brief, as designed) and **30 records with no time_slot and no published_at** (26 MTV). Those 30 are real pager stories ("من هي المرأة الغامضة...", "بلغاريا تتبرّأ...") sitting outside the decay curve.
5. **Fox 12/23 are `related`**, including "Kamala's rehashing Joe's dirty tricks" (`us_fox_d6fa9707d2`) and Bill Maher (`us_fox_460f7d8edb`). They inflate US Israel/Hezbollah/Hamas rates.
6. **False friends that bit this pass:** Arabic عين (eye / same), German Nachricht (message / news), `BAC` matching "backed" in "Iran-backed." CBS's 10/10 "Iran-backed" is real formula, not chrome. Fox's is mixed.

**Why interesting / next:** Any country-level percentage that is not headline-restricted or named-entity-restricted will mostly measure document length and chrome. De-chrome Fox/Yahoo/CNN, recover t-online titles from the first sentence, date the 30 MTV orphans, and split Lebanon English vs Arabic before the next comparison round.

**Confidence:** high on the type/length split and the chrome. High that provenance.credit undercounts syndication.

---

**If I had to pick two follow-ups for the team:** (a) Fatima vs Mohammad Bilal Kanj vs Ali Ammar's son as a named-victim coding task, and (b) de-chrome the US bodies, because right now every US-vs-everyone keyword table is partly a sidebar.
