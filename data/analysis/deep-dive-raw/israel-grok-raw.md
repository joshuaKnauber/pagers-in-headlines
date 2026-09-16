I'll start by inspecting the Israel corpus schema and sample records, then run targeted Python analyses for the angles you assigned.I'll read the existing comparison notes and a few Israel records so the scripts don't redo work that's already in the file.The known findings are already in the comparison notes. Next I’ll compute Israel-only patterns: attribution formulas, timing, and outlet-level register.Dates in the corpus are often day-only, so I’ll pull timestamps from raw HTML and run a full keyword pass next.Timestamps are recoverable. I'll normalize timezones and run the full keyword and register analysis.The first pass is in. I'll pull the truncated sections and a few article texts that look like they carry the real signal.A few counts still need tightening: hedge-lead headlines, Makan’s Arabic grammar, the walkie-wave clock, and whether N12’s first timestamp is real.I have the counts. One more check on the communications-minister wink and Makan’s delay, then I’ll write the findings.# Israel corpus, deep dive

Primary relevant records: **157** (Ynet 95, Kikar 22, Abu Ali 19, Makan 11, N12 10). Clocks below are recovered from JSON-LD / Telegram timestamps in the raw captures; the normalized `published_at` field is date-only. Blast time is ~15:30 Lebanon/Israel local (12:30 UTC) on 17 Sep 2024.

---

**1. Abu Ali was not first. N12, Ynet, and Kikar all published before the famous 13:19 gloat.**

The triage note says Abu Ali’s `הלכה הזימונית (:` (“the pager is gone (:”) at 13:19 UTC beat every article. The clocks in the raw HTML say otherwise. First tagged records, UTC:

| clock | outlet | id | headline |
|---|---|---|---|
| 12:59 | N12 | `il_n12_aaaa261aca` | “Reports in Lebanon: dozens wounded in explosion of Hezbollah radios” |
| 13:02 | Ynet | `il_ynet_07fe8d62f8` | “Mysterious pager explosion: ‘hundreds of Hezbollah operatives hit’” |
| 13:04 | Kikar | `il_kikar_494070c4cd` | “Thousands of terrorists in Lebanon wounded in the pager explosion” |
| 13:15 | Abu Ali | `il_abuali_75659` | wounded in Dahieh, throw the pagers, fear Israel will hack them |
| 13:19 | Abu Ali | `il_abuali_75663` | “the pager is gone (:” |

N12’s 12:59 UTC is corroborated twice in the page (`2024-09-17T15:59+0300` and `T12:59+0000`). What Abu Ali actually won is register, not speed: the smiley arrives 20 minutes after N12’s clinical wire lead. The capture stream also has an untagged 13:06 post, `פינוי הנפגעים בביירות` (“evacuating the wounded in Beirut”), dropped because it never says pager.

*Why interesting / next:* The “Telegram was first” story is an artifact of date-only `published_at` plus a tagging rule that needs the device word. Re-score the untagged 13:00–14:30 Abu Ali window (Genesis 34, “how many chickens is this on Nasrallah’s revenge index,” “intelligence achievement”) as a gloat-stream, not as a beat-the-wires stream.

**Confidence: high.**

---

**2. The real censorship signature is not “according to foreign reports.” It is Ynet’s `דיווח:` flash prefix, and Kikar simply declines to use it.**

The three-word formula (`דיווחים זרים` / “foreign reports”) hits **3/157 (1.9%)**: `il_ynet_7f8388ca56`, `il_ynet_1e8317cc3a`, `il_kikar_c94cfa701e`. Named Western papers as a source are an order of magnitude commoner: **49/157 (31.2%)**, Ynet **37/95 (39%)**. The workhorse hedge is smaller and more local. **22 of 95 Ynet headlines (23.2%) start with `דיווח` / `דיווחים` (“report/s”); 21 of those 22 are `flash_or_lead` (21/58 flashes, 36%).** Zero Kikar, N12, or Makan headlines use that prefix. Kikar’s day-0 evening headline just names the actor: `רחפן תיעד: המוסד השתלט על משלוח הביפרים ומלכד אותם` (“Drone footage: the Mossad seized the pager shipment and booby-trapped them,” `il_kikar_bcb1abbf76`, 19:17 UTC). Ynet’s Mossad headline the same hour still wants the hedge: `דיווחים: "המוסד מלכד…"` (`il_ynet_4122c02e66`, 18:23 UTC).

The first Ynet article already has Israel as actor in the body, quoted from a Hezbollah source to *Al-Araby Al-Jadeed* (“Israel hacked the operatives’ devices and detonated them”), under a headline that still says `מסתורי` (“mysterious”). Headline and body are running different attribution policies on the same page.

*Why interesting / next:* Code three layers separately: (a) `דיווח:` prefix, (b) named foreign masthead as grammatical subject, (c) unhedged Israeli actor in the headline. Overlay on Germany/US, where “Israel” in the headline is ordinary. The 3.8% “foreign reports” figure in the comparison table is the rarest of the three and will understate the mechanism.

**Confidence: high.**

---

**3. The same leak, two headlines: Ynet’s “forced on Israel” versus Kikar’s “Israel decided.”**

Morning of 18 Sep, both outlets run the “Hezbollah suspected the pagers, detonation at the 90th minute” leak. Ynet, twice, puts Israel in the passive: `פיצוץ הביפרים "נכפה" על ישראל` (“the pager explosion was ‘forced’ on Israel,” `il_ynet_afa3376b86` flash 05:31 UTC and `il_ynet_5f50e1ff3e` article 05:28). Kikar takes the same facts and writes an agent: `וישראל החליטה לפוצץ אותם "בדקה ה-90"` (“and Israel decided to detonate them ‘at the 90th minute’,” `il_kikar_1a02f16d3d`, 08:02 UTC). That is the only day-0/1 headline in the corpus that makes Israel the grammatical subject of `לפוצץ` without a `דיווח` hedge.

A sitting minister then winks. Communications Minister Shlomo Kar’ei tweets Nahum 2:11 (`בוקה ומבוקה ומבולקה`, desolation of Nineveh). Ynet’s flash `il_ynet_869d709b34` (related, 34 words) says the tweet “hints at taking responsibility.” Official silence is the Ynet *headline* on the night of the 17th (`השתיקה של ישראל`, `il_ynet_a1b7ebc0d3`). The minister’s Bible verse and Kikar’s unhedged verb are the two places the official line actually cracks in public.

*Why interesting / next:* Pair every shared leak across Ynet/Kikar/N12 and score hedge vs agent. The “forced on Israel” frame is a specific Israeli invention (reactive, almost victim-adjacent). Check whether German/US copy of the same WSJ/NYT leak keeps that recasting or drops it.

**Confidence: high.**

---

**4. Kikar’s first two headlines call the wounded `מחבלים` (terrorists). Abu Ali and Makan never use the word.**

`מחבל` in body+headline: Kikar **9/22 (40.9%)**, Ynet **12/95 (12.6%)**, N12 **2/10**, Abu Ali **0/19**, Makan **0/11**. In the headline, Kikar uses it on the first two stories of the day, 13:04 and 13:33 UTC: “Thousands of terrorists in Lebanon wounded” and “Footage: a Hezbollah terrorist buying vegetables, and the pager explodes” (`il_kikar_494070c4cd`, `il_kikar_0e0bc3ddb6`). Ynet’s first headline says `פעילי חיזבאללה` (operatives). Abu Ali says `פעילים`. Makan, in Arabic, says `عناصر حزب الله`.

The haredi extras sit next to that: a pager-nostalgia column (`il_kikar_a870a3c508`, “why he and his wife owe a debt of gratitude to… the pager”), a Belarus antisemitism watch that quotes “pager Holocaust” in order to denounce it (`il_kikar_244fafc3e5`), and Rivka Ravitz comparing the pager boast to a terror attack at a train station (`il_kikar_361888163b`). Kikar is not just “more `מבצע`.” It is the only outlet whose opening move is to classify the bodies.

*Why interesting / next:* The comparison table’s Israel “terrorists 14.6%” is a Kikar-weighted blend. Report Kikar and Ynet as two Israeli registers, not one country rate. Abu Ali’s zero is the surprise: the gloating Telegram channel is less likely to say `מחבל` than the haredi news site.

**Confidence: high** on the rates. **Medium** on “Abu Ali avoids the word on purpose”; n=19 short posts, and `פעיל` is its default.

---

**5. Gloating is layered. Abu Ali performs it, N12 curates it, Ynet aestheticizes it, and one Ynet column turns the vegetable-shop blast into a human-rights argument.**

Performed: Abu Ali `il_abuali_75663`, eight words, smiley, 13:19 UTC. The next day `il_abuali_75870` relays Syrian anti-Hezbollah voices calling 17 Sep “a holiday on the calendar,” with the punch line that Hezbollah men are “no longer useful” to their wives.

Curated: N12 `il_n12_fb580dd849` (16:48 UTC, 464 words), headline `לאחר מבצע הביפרים: ברשתות בישראל - צוחקים כרגיל` (“After the pager operation: on Israeli networks, laughing as usual”). The article is a meme roundup (fake Mossad “employee of the month,” two fingers found in Sidon). Gloating becomes a news object, which lets N12 both show the jokes and stand next to them.

Aestheticized: Ynet `il_ynet_3d55d2744e` (18 Sep 07:09 UTC, 1,905 words), `מקורי, מבריק, מפתיע` (“Original, brilliant, surprising: behind the scenes of a ticking time bomb times 4,000”). An IDF officer is quoted: Hezbollah’s immediate state is “shock, fear, and humiliation.”

Moralized: Ynet `il_ynet_39d16c66df` (19 Sep), `יתרון הביפרים: כשהטכנולוגיה מקדמת תרבות זכויות אדם` (“The pager advantage: when technology advances a human-rights culture”). The vegetable shop from Kikar’s terrorist-buying-vegetables video is reused as proof of discrimination: “the ability to hit down to the individual target in a crowded vegetable shop is an achievement that must be boasted of.” Tagged `strong`.

Makan, the Arabic service of the Israeli public broadcaster, does none of this.

*Why interesting / next:* Score gloat as performance / curation / aesthetic / moralization, not as a single “celebratory” dummy. The human-rights column is the one a German or US desk would not print; it is the Israeli-specific move. Check whether Ynet’s English edition carried it.

**Confidence: high** on the four texts. **Medium** that this is a stable outlet split; N12 n=10 is thin, and its title-sweep already skews `מבצע`.

---

**6. The wounded body is an eye and two hands. A child almost never has a name. Kikar does not mention children at all.**

Child/girl terms: **11/157 (7.0%)**. Kikar **0/22**. Child in a headline: **1/157**, Ynet flash `il_ynet_4d4bdc2a66` quoting the Lebanese health minister, “12 dead, including two children.” Makan’s first story (`il_makan_c906716cde`, 00:19 UTC on the 18th, 11 hours after the blast) is the only one whose opening casualty list includes `طفلة` (a girl) as a person who died. Fatima, the named child victim in Lebanese coverage, does not appear in this corpus.

What the corpus does name is the wound. Eye/blindness terms: **34/157 (21.7%)**, including a dedicated Ynet piece on the Iranian ambassador losing an eye (`il_ynet_a91d3b3684`). The later WaPo leak, 6 Oct, makes the wound the design: Ynet `רצינו שהמחבלים ישתמשו בשתי הידיים` (“we wanted the terrorists to use both hands,” `il_ynet_dcfb7e124f`) and `נועדו לפצוע את שתי ידיהם` (“were meant to wound both their hands,” `il_ynet_1fa34b8397`); N12 the same day, `הדרך שבה המוסד הבטיח פגיעה מקסימלית` (“how the Mossad guaranteed maximum damage,” `il_n12_aadc675d4c`). Maiming is speakable. A named dead child is not.

Abu Ali goes further. `il_abuali_75875` (18 Sep) pauses on a Hezbollah martyr poster of Abd al-Mun’im, born 2008, “a 16-year-old boy,” and instructs Israeli hasbara: Gaza’s health ministry would count him as a child; “he is a military operative for all intents. Not a child.”

*Why interesting / next:* Compare, on the same day, Lebanese outlets naming Fatima versus this corpus’s one unnamed `ילדה` inside a Hezbollah quote (`il_ynet_a1b7ebc0d3`) and Makan’s unnamed `طفلة`. The Oct 6 “both hands” leak is a separate story: by week three the Israeli press is comfortable describing the targeting logic in Hebrew, with Mossad in the N12 headline and no `דיווח` hedge.

**Confidence: high** on the counts. **Medium** on “Fatima is absent”; a transliteration I missed is possible, but `פאטמה` / `فاطمة` / `Fatima` returned nothing relevant.

---

**7. On the walkie-talkie afternoon, Ynet spent 19 minutes calling the second wave pagers. Reuters had to correct the desk.**

Second-wave clock, 18 Sep UTC:

- 14:05 Ynet `il_ynet_965a441518` “Lebanon reports: again pager explosions in Dahieh…”
- 14:08 Ynet `il_ynet_50c8c2a27c` “New radio-set attack in Lebanon: 14 dead and 450 wounded”
- 14:24 Ynet `רויטרס: מכשירי הקשר שהתפוצצו עתה ברחבי לבנון אינם ביפרים` (“Reuters: the radios exploding now across Lebanon are not pagers”)

Hebrew `מכשיר קשר` is used for both devices, so a keyword split of this corpus will smear the two waves together. N12 is the outlet that names the structure: `אלה מכשירי הקשר שהתפוצצו בגל השני` (“these are the radios that exploded in the second wave,” `il_n12_6ee25e3b1e` / `il_n12_36b229361f`, 16:18 UTC). Abu Ali is the one that names a model: V180 in Baalbek (`il_abuali_75861`). Makan never makes the distinction. All 11 of its headlines say `لاسلكي` (wireless). Its pager/walkie headline split (walkie **81.8%**, pager **18.2%**) is a language artifact, not a news judgment.

*Why interesting / next:* Hand-code device, don’t regex `מכשיר קשר`. The 19-minute Ynet pager→not-pager flip is a usable exhibit of live confusion. Makan’s `لاسلكي` collapse means the Israeli-Arabic service is not a third Hebrew register. It is a different language system, and it will break any pooled “walkie vs pager” chart.

**Confidence: high.**

---

**8. Makan is the delayed, Arabic, casualty-first Israeli outlet. It is also the noisiest data-quality problem in the file.**

Makan’s first record is 00:19 UTC on 18 Sep, **+709 minutes** after ~15:30 local, a Lebanese health-ministry brief: ~4,000 wounded, nine dead, “among them a girl” (`il_makan_c906716cde`). It never says `מבצע` (0/11) or `מחבל` (0/11). When it names Israel, it does so the way a wire desk names Israel, by putting the foreign paper in the headline: `نيويورك تايمز: إسرائيل هي التي زودت حزب الله بأجهزة اللاسلكي` (“NYT: Israel is the one that supplied Hezbollah with the devices,” `il_makan_6c19321e52`, 19 Sep) and `واشنطن بوست: أجهزة اللاسلكي المتفجرة صنعت في إسرائيل` (“WaPo: the exploding devices were made in Israel,” `il_makan_c528a890f3`, 6 Oct). Agentive `تفجير` rises across the fortnight as `انفجار` falls. **8 of 11 Makan records are tagged `related`, not `strong`.**

Then the contamination: `il_makan_5961802f18` (“Lebanon: 20 killed and 450 wounded in the wireless explosions,” 372 words) has an Archive Team English manifesto as its body (`History is littered with hundreds of conflicts…`). Word count and any keyword hit on that record are junk. N12 has a different defect: `il_n12_6ee25e3b1e` and `il_n12_36b229361f` are the same “second wave” article on two mako paths, both marked `is_primary_record: true`. N12 `il_n12_42fc90d847` has `date_missing` in extraction warnings; the raw timestamp is 17 Sep 22:00 +0300.

*Why interesting / next:* Treat Makan as a separate media system (Israeli, Arabic, public broadcaster, Arab-audience) in any country-level share. Re-extract `il_makan_5961802f18` from the saved HTML. Collapse the N12 URL pair. The Abu Ali tagging rule that dropped Genesis 34 (`il` post 75678, 14:09 UTC, Simeon and Levi killing the males of Shechem “on the third day, when they were in pain”) also belongs here: the most loaded theological gloat in the capture stream is not in the 157.

**Confidence: high** on delay, grammar, and the Archive Team body. **Medium** on reading Makan’s `related` rate as editorial caution rather than title-sweep under-recall.

---

## Data-quality flags (short)

- Clocks are not in the JSONL. Any timing claim has to go back to raw HTML / `abuali-messages.csv`.
- Ynet is **61%** `flash_or_lead` (median 58 words). Country rates overweight Ynet flashes.
- N12 n=10, title-sweep already biased toward `מבצע`.
- Abu Ali tagging required a device word, so the gloat-only posts are missing.
- One Makan body is Archive Team chrome. One N12 article is doubled. One N12 date is missing.
- `provenance.credit = Reuters` (23 records) is citation, not syndication, as the normalization notes already warn.
