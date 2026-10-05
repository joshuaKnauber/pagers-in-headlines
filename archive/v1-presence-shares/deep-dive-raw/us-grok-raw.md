I'll start by inspecting the US corpus schema and known findings so I can compute outlet-level patterns rather than restate them.I'll sample the US JSONL and existing analysis notes so the scripts stay on primary records and don't rehash known findings.Next I’ll filter to the 134 primary records and compute outlet, sourcing, and vocabulary splits before going after individual outliers.Yahoo's credit field looks under-filled, so I'll check original-outlet strings next and run the framing, sourcing, and casualty searches in parallel.Fox bodies look contaminated with live-site chrome from the fetch day. I’ll quantify that pollution, then keep going on supply chain, legality, and casualties.I’ll write a de-chrome pass in `/tmp` so keyword shares sit on article text, then pull supply-chain, legality, casualty, and Yahoo-origin numbers from that cleaned set.# US corpus deep dive

Primary relevant records: **134** (CNN 30, Yahoo 30, Fox 23, NBC 15, WaPo 12, CBS 10, ABC 5, NYT 4, Reuters 4, USA Today 1). Strong 104 / related 30. All claims below are from `data/us/corpus-v1.jsonl` with in-memory de-chroming of fetch-day nav. No repo files were modified.

---

**1. Half the US corpus is fetch-day chrome. Fox’s 91% “terrorists” number does not survive cleaning.**

67 of 134 primary records (50%) carry September 2026 site chrome inside 2024 article bodies. Fox: 20/23 contain the `Right Arrow Left Arrow` ticker (Houthis, Nepal floods, “narco-terrorist,” BRICS). CNN: 19/30 are video pages stuffed with `data-publish-date="2026-09-14..."` related-video HTML. Yahoo: 22/30 open with a “Top Stories” rail, and 27/30 still contain a 14 Sept 2026 Reuters graf about Trump or Prince Harry’s children.

On raw Fox text, `terrorists?` is in **21/23 (91%)**, matching the known figure. After stripping the ticker it is **12/23 (52%)**. Restrict to strong records and it is **4/11 (36%)**. Related Fox is 12/23 (52%), and 12/12 of those related pieces hit “terrorist” in the raw body, most of them political wrap (Kamala, Bill Maher, UN resolution). CNN written strong, same clean measure: **3/11 (27%)**. The Fox–CNN “terrorists” gap is mostly chrome plus related-share, not a 91-versus-10 descriptor chasm.

*Why interesting / next:* Recompute the published Fox 91% row on de-chromed strong-only text, and decide whether Fox related political pieces belong in the event corpus at all. The known “descriptor-inflated” caveat understates the extraction problem.

**Confidence: high.**

---

**2. CNN’s n=30 is a TV stack. The journalism is 11 written pieces.**

19 of 30 CNN records (63%) are video pages. After cutting the 2026 related-video HTML, those 19 have essentially no `militant`, `civilian`, `child`, `Gold Apollo`, or `US officials` left in the remaining text. 8 of the 19 are coded related and sit on week_2 / first_month Beirut airstrike clips (`us_cnn_e9df9fa49e`, `us_cnn_af080302bd`, `us_cnn_7d156f4ba5`, `us_cnn_e25861e961`).

The 11 written records are all strong. On that subset: **militant 11/11**, Gold Apollo 7/11 (64%), NYT cited 7/11 (64%), children 8/11 (73%), US officials 1/11 (9%), war crime 0/11. CNN’s volume advantage over Fox (30 vs 23) is clip pages, not more reporting. One of those clips, `us_cnn_c755864462` (day_0), is headlined “Exploding pagers injure members of Iran-backed terror group.” That is Fox vocabulary on a CNN video slate. The written desk does not use it.

*Why interesting / next:* Split CNN (and Fox video `us_fox_efad9aad1c`, 36 words) into TV versus written before any outlet-share table. The written CNN desk and the CNN video desk are not the same speaker.

**Confidence: high.**

---

**3. Each US outlet ran its own anonymous “Israel did it” formula. They do not agree on what Washington knew.**

Day_0, CNN already headlined “Israel behind deadly pager explosions…” (`us_cnn_2419d54e73`) and wrote “CNN has learned Tuesday’s explosions were the result of a joint operation between Israel’s intelligence service, Mossad, and the Israeli military.” That sentence is copy-pasted through five CNN written pieces as late as 27 Sept (`us_cnn_ef88109e04`). CNN almost never says “US officials” (1/11 written strong).

Day_1, Fox published its scoop: “A senior U.S. official has confirmed to Fox News that Israel is behind the explosions” (`us_fox_27be0e9bd8`). That exact house phrase is in **7/11 (64%)** of Fox strong records and in **0** records from any other outlet. NBC’s formula is different again: “two U.S. officials told NBC News that Israel was behind the attack” (four strong NBC pieces, e.g. `us_nbc_4e44def839`, `us_nbc_1655bbb14e`). AP’s formula, on ABC and Yahoo, is “An American official said Israel briefed the United States **after** the attack… spoke on the condition of anonymity because they were not authorized” (`us_abc_61d9dac625`, `us_yahoo_9ee477059c`).

CBS then adds a fact nobody else carries. On day_1–day_3 (`us_cbs_5917b2743f`, `us_cbs_859edfb519`, `us_cbs_f113ea27ae`) CBS writes that it “learned that American officials were given a heads-up by Israel about **20 minutes before** the operations began… no specific details.” The same CBS day_1 piece also quotes Blinken, “The United States did not know about nor was it involved.” WaPo’s 5 Oct reconstruction (`us_wapo_9bb5c5a70b`) goes the other way: the US “was not informed of the booby-trapped pagers or the internal debate over whether to trigger them.”

*Why interesting / next:* Align the four formulas on a timeline (CNN learned / Fox senior official / NBC two officials / CBS 20-minute heads-up / WaPo not informed) and see which one later reporting treated as canonical. The 20-minute heads-up versus Blinken’s “did not know” is the unresolved US-knowledge story in this corpus.

**Confidence: high.**

---

**4. The war-crime question is almost absent from flagship news. It lives on Yahoo’s opinion pipe and one NBC piece coded “related.”**

On strong records, `war crime` is in **2/104 (1.9%)**. One is Fox quoting a critic that the attacks “could be considered war crimes or a declaration of war” (`us_fox_5ad65ef2d8`). The other is a Yahoo piece, “Even Leon Panetta Says Israel’s Pager Attack Is ‘Terrorism’” (`us_yahoo_e0525fd211`, day_6), which quotes Panetta on CBS calling it “a form of terrorism” and Volker Türk on booby-trapped everyday objects. CNN written never says “war crime.” It does, once, quote Türk that IHL “prohibits the use of booby traps” (`us_cnn_392a1223af`, day_1).

NBC actually reported the legal debate. `us_nbc_351cd1ae85` (day_2), “Doctors overwhelmed by blast injuries as civilian impact of device explosions sparks outcry,” quotes Human Rights Watch’s Lama Fakih in Beirut: “Whether or not this amounts to a war crime does require further investigation.” That piece is coded **related**, so it drops out of strong-only shares. Yahoo also carries a USA Today opinion, “Pager attack in Lebanon was terrorism. And Americans helped pay for it” (`us_yahoo_1877937746`). Fox related political copy never takes up that argument. The legal register in the US reach set is syndication and opinion, not the evening-news desk.

*Why interesting / next:* Recode `us_nbc_351cd1ae85` (it is about this event). Compare Türk/Panetta/Fakih uptake against Germany, where the war-crime question may have sat in the main news hole.

**Confidence: high** on the counts. **Medium** on “ghettoized,” because CNN’s Türk quote is a quiet IHL mention that a keyword for “war crime” misses.

---

**5. NYT is n=4 in the table and the hidden wire of the rest of the US corpus. Fatima Abdullah is named in three records.**

24 of 104 strong records (23%) cite the New York Times. CNN written: **7/11 (64%)**. USA Today’s only record (`us_usatoday_5bb547ff5e`, day_0) and Yahoo’s day_0 Reuters-style piece (`us_yahoo_cf5fa264e3`) both attribute the Gold Apollo explosive-in-the-pager account to the Times on day_0, before Taiwan or BAC have spoken.

NYT’s own four records include the only victim-named funeral feature in the US set: `us_nyt_4a725a8429` (day_1), “Funeral Is Held for 9-Year-Old Girl Killed in Pager Attack in Lebanon,” Fatima Abdullah, a fourth grader in Saraain, first day of school, English classes. The name appears in **3/134** records. The other two are the same AP funeral graf on ABC (`us_abc_61d9dac625`) and Yahoo (`us_yahoo_9ee477059c`). Everyone else says “a child,” “a girl,” “two children.” Ages do not even agree. USA Today day_0: 8-year-old girl. CBS day_0: “12-year-old girl and an 11-year-old boy.” NBC: 8- or 9-year-old girl and 11-year-old boy.

*Why interesting / next:* Treat NYT as a source layer, not an n=4 outlet. Pull the Times live blog that this corpus could not capture (13 of 17 NYT URLs uncaptured) and see whether Fatima’s name, the Gold Apollo leak, and the “tactical success without a strategic goal” frame (`us_nyt_239261eaa4`) originated there and then spread.

**Confidence: high.**

---

**6. Yahoo is not an outlet. The credit field says otherwise.**

Triage notes already flag Yahoo as syndicated. The credit field still marks **25/30 as `local_or_unspecified` with empty credit**. The actual mix, from URLs, bylines, and leftover copyright lines:

- Reuters exclusives duplicated with the Reuters outlet itself (`us_yahoo_2ffb1b2385` = `us_reuters_d4ac302ced`, Gold Apollo/BAC; `us_yahoo_80d6aea1ea` = `us_reuters_ca1c019c53`, “handed out pagers hours before”).
- AP (`us_yahoo_9ee477059c`).
- AFP on Fortune (`us_yahoo_ae4f6eb3f5`, “originally featured on Fortune.com”).
- Telegraph voice: “The terrible blunder that exposed Hezbollah’s fighters to audacious pager attack” (`us_yahoo_87d0a80097`) and “Israel ‘supplied exploding pagers to Hezbollah’” (`us_yahoo_b8b9170ec9`).
- NBC, word for word: “Why did Israel blow up Hezbollah pagers…” is `us_nbc_4e44def839` and `us_yahoo_0a09f735ca`.
- USA Today opinion and a USA Today fact-check, neither of which is the USA Today n=1 row.

Yahoo is also the only high-reach surface that repeatedly calls the *attack* terrorism (Panetta, USA Today opinion). Fox’s “terrorists” are Hezbollah. Yahoo’s “terrorism” is Israel. That split is a syndication artifact, not a Yahoo editorial line.

*Why interesting / next:* Rebuild `provenance.credit` from byline/copyright, then weight Yahoo as reach for Reuters/AP/Telegraph/USA Today opinion rather than as a 30-record outlet. The Independent live blog on Yahoo says “20 killed, 450 wounded” in the day_1 second wave (`us_yahoo_84cb223cdf`). ABC’s AP live blog of the same event says “14 killed, 450 wounded” (`us_abc_41b079c45e`). Same slot, different wire, different toll.

**Confidence: high.**

---

**7. “Sabotage” is WaPo/ABC. “Spectacular” is Fox. The supply-chain whodunit is a day_1 story Fox mostly declined.**

`sabotage` on strong records: ABC **4/5 (80%)**, WaPo **5/11 (45%)**, USA Today 1/1, Fox **0/11**, CNN **0/22**. WaPo even puts it in the analysis frame: “Pagers attack brings to life long-feared supply chain threat” (`us_wapo_4dc0dfc689`, day_2) and later “intelligence triumph, with uncertain ends” (`us_wapo_3b78674c00`). Fox’s day_1 expert piece is headlined “Israel degrades Iran-backed Hezbollah terrorists in **spectacular** pager explosion operation” (`us_fox_a82ba395ba`). `spectacular` is Fox-only among strong records (2/11). `sophisticated` is in 5/11 Fox strong (45%).

Gold Apollo is already on CNN/Yahoo/USA Today on day_0 via the Times. BAC/Budapest lands day_1, when Gold Apollo’s Hsu Ching-kuang points at the Hungarian licensee (`us_reuters_d4ac302ced`, `us_fox_d61e0e197d`). The British-educated BAC figure (Kristel / Bársony) is a CBS/Yahoo story (`us_cbs_290b338527`, “protected by Hungary’s secret service”; `us_yahoo_8b6d21c426`). Fox strong Gold Apollo is **3/11 (27%)** versus Yahoo 13/26 (50%) and Reuters 3/4. Fox ran the Hungarian-firm item once, then went back to the senior-official formula and the AOC/Sanders/Fetterman wrap (`us_fox_d4a97b5734`, `us_fox_bdb750a556`).

*Why interesting / next:* Code moral register (`sabotage` / `operation` / `spectacular` / `black ops`) as a competing-frame table, not a single “attack vs operation” row. WaPo’s Oct reconstruction (`us_wapo_9bb5c5a70b`) is also the only US piece that dates booby-trapped walkie-talkies to **2015**. That is a decade-long supply-chain story the day_0–day_2 coverage did not have.

**Confidence: high** on the lexical split. **Medium** on “Fox declined” as intent. Fox n_strong=11 is small, and two of those 11 are an AMP/non-AMP pair of the same explainer.

---

**8. Dedup missed AMP twins. Relevance coding demoted the civilian-injury story.**

Exact-duplicate clusters did not collapse AMP versus desktop of the same article. ABC: `us_abc_41b079c45e` and `us_abc_b07e7d99bc` are `.../amp/Technology/wireStory/mideast-tensions-latest-gold-apollo-budapest-company-made-113798936` and the non-AMP twin, both primary, both “Israel-Hamas war latest: 14 killed, 450 wounded…” Fox: `us_fox_14366b346b` (`.amp`, 708 words, clean body) and `us_fox_a46925706f` (desktop, 1232 words, ticker-polluted) of `how-did-hezbollah-pager-explosions-happen-things-know`. Reuters/Yahoo pairs of the same wire also both sit as primary (`us_reuters_d4ac302ced` / `us_yahoo_2ffb1b2385`).

Relevance: Fox related-share 52% is political wrapping. NBC’s civilian/legal piece is related. CNN’s week_2/first_month videos of later Beirut blasts are related and still inflate CNN’s n. USA Today n=1 and NYT n=4 are already flagged as presence-only. Yahoo “children” looks like 88% of strong until you strip the leftover “children of Britain’s Prince Harry” 2026 Reuters graf. After that strip it is 16/26 (62%), still high, but the raw number is not usable.

*Why interesting / next:* AMP/canonical collapse, a chrome-strip pass (Fox ticker, CNN video HTML, Yahoo Top Stories / 2026 Reuters prefixes), and a second look at related/strong on civilian-impact and legal-analysis pieces. Until that happens, outlet percentages in this corpus are partly measuring page chrome and URL variants.

**Confidence: high.**

---

**Data-quality suspicions (summary)**

| Problem | Where | Effect |
|---|---|---|
| 2026 nav ticker prefix | Fox 20/23 | Inflates terrorists, Iran, Trump, “operation” |
| Related-video HTML | CNN 19/30 | Inflates n, empties keyword measures |
| Top Stories + 2026 Reuters grafs | Yahoo ~22–27/30 | Inflates children, Trump; hides original byline |
| AMP vs desktop both primary | ABC pair, Fox pair | Double-counts |
| Credit field empty | Yahoo 25/30 | Hides Telegraph/AP/Reuters/USA Today |
| Related vs strong | Fox politics in; NBC civilian-injury out | Skews framing shares |
| NYT capture | 4 of 17 URLs | Under-counts the outlet that everyone else cites |
