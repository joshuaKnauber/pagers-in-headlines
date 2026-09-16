I'll dig into the German corpus for non-obvious patterns—tabloid vs public vs broadsheet, dpa wire reuse, attribution, and specialty angles—and back every claim with computed counts. First I'll inspect the data shape and existing analysis notes so I don't restate known findings.I'll sample the German schema and existing notes next so the scripts look for new angles instead of restating the known actor-grammar findings.Schema is clear: 176 primary records. Next I’ll run a first-pass scan for register, wire reuse, Völkerrecht, BAC, attribution, and Hisbollah descriptors.t-online headlines look empty, and WELT/ntv are mostly short flashes. I'll quantify register, wire reuse, and the specialty angles next.A few splits already look real: Bild’s “Terroristen” vs public “Miliz,” empty t-online headlines, and Völkerrecht concentrated in a handful of pieces. I’ll now measure wire reuse and attribution language.Völkerrecht is real but thin: two dedicated explainers plus UN/Türk. I’ll now isolate commentary, dpa clones, and the Bild register so the findings stay specific.Germany’s 176 primary records split into four voices, not one. The interesting part is how cleanly those voices diverge, and how much of the “German” text is actually dpa.

**Corpus.** 176 primary records (124 strong, 52 related). t-online 36, Spiegel 33, Bild 26, RND 21, WELT 16, Tagesschau 15, ZDFheute 15, ntv 12, RTL 2. ~100,700 words. Day 1 (18 Sep) is the volume peak at 54 records, as already established.

---

**1. Bild’s victims are “Hisbollah-Terroristen.” ARD/ZDF’s are “Hisbollah-Miliz,” and they mention civilians.**

`Hisbollah-Terror` appears in **13/26 Bild records (50%)** and **3/150 everywhere else (2%)**: one ntv flash, one t-online digital piece, one WELT commentary. `Terroristen` is in **18/26 Bild (69%)** vs **2/30 Tagesschau+ZDF (7%)**, and those two public-broadcaster hits are quotes of Israeli officials (“Terroristen ins Visier nehmen”), not the paper’s own label for the wounded. `Zivilisten`/`Zivilbevölkerung`: **1/26 Bild (4%)** vs **15/30 public (50%)** vs **17/36 t-online (47%)**. Public default compound is `Hisbollah-Miliz` (18/30). Bild’s device-word is `Piepser`/`Piepeser`, **5/26 headlines**, including a typo, “Hunderte Hisbollah-Piepeser gleichzeitig detoniert” (`ge_bild_9c1c25b60d`). No other outlet puts Piepser in a headline.

The register is not subtle. Bild’s day-1 headline is “2700 Hisbollah-Terroristen verwundet: Enthüllt! Darum schlug Israel jetzt zu” (`ge_bild_a855b7c8d2`). Tagesschau’s day-1 headline is still “Was ist über die Pager-Explosionen im Libanon bekannt?” (`ge_tagesschau_bcdc70bedf`).

**Why interesting / next.** This is the German analog of the Fox “terrorists” inflation, except Bild is not mostly quoting. It is labeling the casualties. Worth a collocate study (Terroristen as victim vs as quoted IDF speech) and a reach-weighted version, because Bild’s unique compound will dominate any unweighted “Germany says terrorists” number.

**Confidence: high**

---

**2. The only signed cheerleading is Bild. WELT’s two commentaries go after Netanyahu. ARD/ZDF send in law professors.**

Bild ran an explicit Kommentar on 19 Sep: “Darf man sich über den Tod von Terroristen freuen?” (`ge_bild_83407de25e`, `/politik/meinung-kommentare-kolumnen/`). Answer in paragraph 4: “Ja.” The piece calls the operation “filmreif,” says the wounded “kein Terrorist mehr sein kann,” and frames it as “ein Beitrag zur langfristigen Deeskalation.”

WELT ran two signed pieces the other way. “Netanjahu verfällt dem Größenwahn der Unbesiegbarkeit” (`ge_welt_06b84d417f`, 19 Sep) grants the Mossad a “beeindruckende Demonstration seiner Macht,” then argues the strategic value is “zweifelhaft” and that Netanyahu’s government “fehlt das strategische Denkvermögen.” “Nasrallahs große Rache muss noch warten” (`ge_welt_ab2f67ce3e`) sits on `/debatte/kommentare/`.

Public broadcasters do not take a stance in their own voice. They commission. ZDF, 19 Sep: “Die Völkerrechts-Frage” (`ge_zdfheute_d886ea02f0`, Daniel Heymann / Alexandra Tadey, Prof. Steiger). Tagesschau, 20 Sep: “Völkerrechtler uneins über Legitimität von Libanon-Angriffen” (`ge_tagesschau_5487e7d8f1`), with Andrew Clapham (war crime / direct attack on civilians), Thomas Burri (“mit relativ hoher Wahrscheinlichkeit” no IHL violation), Stefan Talmon of Bonn (proportionality is complicated). Tagesschau the same week: Peter R. Neumann on “psychologische Kriegsführung” (`ge_tagesschau_af41358963`).

**Why interesting / next.** Three German publics, same event. Tabloid moral permission, conservative-paper strategic doubt, public-broadcaster legal seminar. Compare to US, where the opinion is in the news voice (Fox) rather than in a labeled Kommentar. Also check whether Spiegel’s own signed pieces (Muriel Kalisch “russisches Roulette,” Sascha Lobo “hybride Cyberwar”) actually made it into the corpus. They did not. They leaked in as related-link chrome. See finding 9.

**Confidence: high**

---

**3. Völkerrecht is a German *format*, not a German volume.**

Keyword presence is modest. `Völkerrecht` in **9/176 (5%)**, `Kriegsverbrechen` in **8/176 (5%)**, combined law/war-crime family **19/176 (10.8%)**. US `international law`/`war crime`/`Geneva` is **11/134 (8.2%)**. Israel 0.6%, Lebanon 1.8%. So Germany is not drowning in IHL talk.

What Germany has, and the US corpus does not, is the dedicated explainer with named professors, filed as news. Two of them, on consecutive days, both public broadcasting. The rest of the German hits are Volker Türk at the UN (Spiegel `ge_spiegel_894b2658f7`, “in Nähe von Kriegsverbrechen”), Nabih Berri’s “Massaker und Kriegsverbrechen” quoted in dpa copy, and Josep Borrell’s “schwere, wahllose Kollateralschäden,” which ntv put in a `Der Tag` headline (`ge_ntv_00027abbab`). Bild’s sole Völkerrecht hit is Bou Habib quoted on day 4.

**Why interesting / next.** Do not report “Germany obsessed over international law.” Report “ARD/ZDF ran the IHL seminar, everyone else quoted Türk or Berri.” Next step is to code *who is speaking* in those 19 records (professor vs UN vs Lebanese politician vs journalist). The professor voice is the actual German specialty.

**Confidence: high**

---

**4. About a quarter of all German words are one dpa text, mostly at t-online and RND.**

t-online is the wire baseline the access notes promised. **20/36 t-online records (56%)** carry `provenance.credit=dpa`. Those 20 are **17,344 words, 17.2% of the entire German corpus**. dpa also sits in the first 250 characters of all 20 (image-credit lead, “Quelle: …/dpa”).

RND is not credited dpa. Sentence overlap says otherwise. **83 long sentences** are shared between RND and t-online, the highest outlet pair by far (next is Spiegel×t-online at 41). **10/21 RND articles** share 16–55% of their long sentences with t-online, including the two big day-1 explainers (`ge_rnd_8077ee3c89` 19.7%, `ge_rnd_2976713b85` 18.5%) and later war wrap-ups at 40–54%. Those 10 add another **9,579 words**. Credited dpa + RND-dpa-like = **26.7% of all German words, 30/176 records**.

Tagesschau and ZDF are the opposite. Most of their explainers share **0%** of long sentences with t-online. The Völkerrecht pieces and the NDR/WDR investigation (finding 5) are original. Bild’s tabloid copy is original too, just in a different register.

**Why interesting / next.** Any “Germany said X” percentage that does not split t-online/RND from ARD/ZDF/Bild is partly counting the same dpa paragraph three times. A proper wire-collapse (cluster by shared sentences, keep one dpa canonical) would shrink the German n and move the register numbers. t-online’s empty headlines (finding 9) currently hide how formulaic those 20 dpa leads are.

**Confidence: high**

---

**5. The Hungary/BAC “European connection” is a 48-hour dpa echo. ARD actually reported it. The US covered it more.**

`BAC`/`Ungarn`/`Budapest` is in **26/176 German records (14.8%)**. US: **41/134 (30.6%)**. Gold Apollo/Taiwan: DE 18% vs US 39%. Supply-chain/Lieferkette: DE 7% vs US 25%. The European angle is thinner in German news than in American news.

Timeline is tight. Day 0: almost nothing (1 BAC/Budapest). Day 1: **9 BAC/Budapest, 12 Ungarn, 16 Gold Apollo/Taiwan**, almost all the same Gold Apollo dpa quote (“eine in Ungarn ansässige Firma … BAC”). That sentence is in t-online `ge_tonline_d2f6b18032` / `cc9cc53e70` and RND `ge_rnd_8077ee3c89` / `2976713b85` with near-identical wording.

The one German original is Tagesschau/NDR/WDR on 20 Sep, “Die Spur der explosiven Pager” (`ge_tagesschau_a713846d36`, 1,150 words, byline Lea Busch, Florian Flade, Amir Musawy, Sebastian Pittelkow, Reiko Pinkert). They walk up to the beige house in Zugló, Budapest, read “BAC Consulting” on the mailbox, get the Hungarian government denial (devices “nie in Ungarn”), and push the trail to Bulgaria (Nortech) and Norway. WELT had a paywalled teaser on 27 Sep, “Die mysteriöse Ungarin und die explodierenden Pager” (`ge_welt_1178f16041`, 38-word plus stub). Body is a trailer. We do not have the reporting.

Then 6 Oct, Washington Post overwrite: pagers “heimlich in Israel hergestellt.” Tagesschau `ge_tagesschau_b4b3c4ab8e`, RND `ge_rnd_6aa2c4f81c`, t-online `ge_tonline_d85aeff834`. The Hungary story is closed in one clause: “nicht in Ungarn, wie zwischenzeitlich vermutet worden war, sondern in Israel.”

**Why interesting / next.** The assignment’s “German specialty = European supply chain” does not hold as volume. It holds as one ARD investigation. Read that piece against the WaPo Oct 6 reconstruction and against WELT’s paywalled Ungarin story (if a full capture exists in `raw/welt`). Also drop RND’s “Ungarn soll Millionen-Strafe” related-link as a false positive (`ge_rnd_8b78b3d210`).

**Confidence: high** on the volume/timeline; **medium** on WELT’s unpublished reporting.

---

**6. Day-0 headlines treat Israel as unsayable. Day-1 Bild has already “Enthüllt!” it. Tagesschau is still on “soll laut US-Medien.”**

Of 19 day-0 records, **3 headlines name Israel (16%)**. Bodies already do: **16/19 (84%)**. The three exceptions are RND “Hisbollah droht Israel mit Vergeltung,” RTL “Hisbollah-Miliz wirft Israel Anschläge vor!,” and WELT “Israelischer Geheimdienst soll Pager-Lieferung mit Sprengstoff präpariert haben.” Everyone else headlines the explosion, not the actor: Tagesschau “Neun Tote und 2.750 Verletzte,” ZDF “Pager-Explosionen verletzen Tausende,” Bild “Hunderte Hisbollah-Piepeser gleichzeitig detoniert.”

By day 1 (18 Sep, walkie-talkie wave), Bild is naming the actor as fact plus scoop-voice: “Enthüllt! Darum schlug Israel jetzt zu.” Tagesschau’s attribution headline that same day is still hedged and sourced out: “Israels Geheimdienst soll laut US-Medien hinter Pager-Explosionen stecken” (`ge_tagesschau_a6b7c66884`). ZDF asks the question: “Steckt Israel hinter den Pager-Explosionen im Libanon?” (`ge_zdfheute_5a317882e0`). `soll`/`offenbar`/`steckt` in headlines cluster at Tagesschau, ZDF, Spiegel, WELT. Bild’s hedging word in headlines is approximately none.

US-Medien/NYT as the attribution vehicle is in **21/176 (12%)**, densest at Tagesschau (5/15). That is Germany’s cousin of Israel’s “according to foreign reports,” except here the foreign reports are how you *do* name Israel, not how you avoid naming the IDF.

**Why interesting / next.** Headline agency and body agency are different clocks. A headline-only measure of “who did Germany blame, when?” will show a 24-hour lag that the bodies do not have. Code first-sentence actor vs headline actor for day 0–2. The known no-actor “exploded” grammar (DE 92%) is probably a headline/lead phenomenon sitting on top of bodies that already say Israel.

**Confidence: high**

---

**7. WELT and ntv look big in the record count and almost disappear by word count. They are TV clips.**

WELT is 16/176 records (9%) and **3,645 words (3.6%)**. Median **38 words**. **11/16 are `flash_or_lead`**. **7/16 URLs are `/video`**, **4/16 are `/plus` paywall teasers**. The video teasers are 28–45 words of caption under a WELT TV clip, including the useful-looking “klassische Supply-Chain-Attacke” (`ge_welt_72b6848474`) and the BAC/Budapest quote from Steffen Schwarzkopf (`ge_welt_6a67719386`). Those are not articles.

ntv is 12 records and **781 words (0.8%)**. **8/12 video URLs**. Four are `Der Tag:` TV-log items. Mean 65 words.

Public broadcasters are the opposite shape: Tagesschau 15 records, **10,399 words (10.3%)**, mean 693, all `article`. ZDF 15, **10,900 words (10.8%)**, mean 727, all `article`. t-online is 27.3% of German words on 20% of records.

**Why interesting / next.** Outlet-level percentages that treat a 29-word WELT video caption as equal to a 1,150-word ARD investigation will invent a “WELT covered X” finding that is a presenter sentence. Recompute the register table restricted to `document_type=article` and `word_count>=200`. WELT’s actual text journalism on this story is five articles plus two commentaries.

**Confidence: high**

---

**8. RND booked the former BND president to call it historic. That voice exists nowhere else.**

On 18 Sep RND ran “Ex-BND-Chef nennt Pager-Explosionen ‚herausragende geheimdienstliche Operation‘” (`ge_rnd_6b5c75ac27`). Gerhard Schindler, former BND president, to RND: “äußerst professionelle und herausragende geheimdienstliche Operation, die in die Geschichte der außergewöhnlichen nachrichtendienstlichen Aktionen eingehen wird.” And: “Niemand von euch ist sicher!” `BND` as a string is **3/176, all RND**. Same day, RND interview with Peter R. Neumann: “Eine Operation, über die noch Filme gemacht werden” (`ge_rnd_4477279a80`). Neumann then appears in **9 records** (RND 6, Bild 2, Tagesschau 1). He is the German-speaking talking head who travels.

German elected politics is almost not in the story. `Scholz` **1/176**, `Baerbock` **3/176** (travel advice, contact with counterparts). The domestic hook is Lufthansa. RND dedicated “Lufthansa und Air France stoppen Flüge nach Israel” (`ge_rnd_8b78b3d210`). That is the German “what does this mean for us” piece. It is a flight cancellation.

**Why interesting / next.** Two expert publics again: ex-BND/Neumann (capability, history, psychological warfare) versus Völkerrechtler (IHL, distinction, proportionality). RND sits on the first, ARD/ZDF on the second, Bild on neither (Bild uses “Terror-Experte” to list Hezbollah’s mistakes). A quote-attribution pass, who is allowed to evaluate the operation, would make this table.

**Confidence: high**

---

**9. Data-quality landmines, including Spiegel paywall eating the interesting pieces.**

These are not footnotes. They change several counts above.

- **t-online 36/36 empty headlines.** Credit detector still works (dpa in the image-credit lead). Headline-based measures of t-online are zero by construction. First-sentence proxies exist in the body after “Artikel teilen” (26/36).
- **Spiegel 4 records are paywall walls**, body starts “Sie können den Artikel leider nicht mehr aufrufen.” They include the pieces you would actually want: “Operation »Gold Apollo AR-924«” (`ge_spiegel_56bd1c4430`), “Warum der iranische Botschafter einen Hisbollah-Pager getragen haben soll” (`ge_spiegel_8be8faca25`), “Die Spur der Hisbollah-Pager nach Osteuropa” (`ge_spiegel_176d1e0d56`), and the terror-expert quote piece (`ge_spiegel_eb13e72e65`). Word counts ~310–320 are login chrome.
- **Spiegel `Merkliste` residue in 25/33 bodies.** Three also contain `meinung meinung` related-link duplication, which is why Sascha Lobo and Muriel Kalisch show up inside news articles they did not write.
- **RND `ge_rnd_5147ce635b`**, headline “Israel geht ein hohes Risiko ein,” body is 16 words of crossword ad. **17/21 RND bodies** end with “Das tägliche Kreuzworträtsel.”
- **WELT two commentaries** open with `Inhaltsbereich Hauptnavigation Suche Login Fußbereich 0`.
- **Bild “Haben Sie eine Meinung zu diesem Artikel?”** is in **21/26** bodies. Any `Kommentar`/`Meinung` keyword count on Bild is the CTA, except `ge_bild_83407de25e`, which is a real column.

**Why interesting / next.** Re-extract Spiegel+ from `data/germany/raw/spiegel/` before anyone uses Spiegel n=33 as a broadsheet sample. Four of the five most promising Spiegel headlines are empty. Drop RND crossword-only. Build t-online headlines from the URL slug or og:title in the raw HTML. Until then, Spiegel and t-online headline stats are not usable.

**Confidence: high**

---

**What I would not spend time on.** German politicians (they are not here). RTL (n=2, genuinely thin). A “Germany vs US on BAC” story that ignores the ARD investigation and the dpa clone. Repeating the known 92% agentless-grammar finding without splitting headline from body and Bild from Tagesschau.
