I'll start by inspecting the Lebanon corpus schema and volume, then run targeted Python analysis for outlet register, day-0 tickers, attribution, and the second device wave.Existing Lebanon analysis notes should tell me what's already claimed, so I can go past those and inspect the JSONL schema next.Known findings are already mapped; next I’ll sample records and run a deeper script for tickers, victims, attribution, and outlet register.Al-Manar’s empty day_0 looks like either silence or a collection hole — I’ll check the enumeration files and then run lexical analysis.Al-Manar’s day-0 “silence” looks like a triage miss, not real silence. Next I’ll quantify register, victims, tickers, and the second wave from the corpus itself.Al Jadeed’s Israeli-media hits look like leftover ticker chrome. I’ll verify that, then reconstruct the day-0 sequence and compare how each outlet names Hezbollah.I have enough computed evidence to write the findings. A few of them revise earlier Lebanon claims rather than repeating them.# Lebanon deep dive: findings beyond the known splits

Corpus: 338 primary `strong`/`related` records in `data/lebanon/corpus-v1.jsonl` (MTV 125, LBCI 110, Al Jadeed 59, Al-Manar 42, NNA 2). Headline-only rates used wherever bodies are unsafe. Al-Manar titles from `data/lebanon/enumeration/almanar-titles.csv` used only to diagnose collection holes, and flagged as such.

---

### 1. Al-Manar was not silent on day 0. The title sweep dropped Hezbollah's own statement.

The corpus has **0 Al-Manar records in `day_0`**. That is a tagging hole, not a stunned newsroom. `almanar-titles.csv` still holds the first pager flash and a run of official Hezbollah statements, all left `relevance=""`.

| ID | Tag | Headline (tr.) |
|---|---|---|
| `12481735` | untagged | "Pagers explode in the hands of their carriers in several Lebanese regions" |
| `12482087` | untagged | Hezbollah: "around 3:30 Tuesday afternoon" pagers with "workers in various Hezbollah units and institutions" exploded |
| `12482351` | untagged | Hezbollah: after reviewing the facts, "we hold the Israeli enemy fully responsible for this sinful assault" |
| `12482153` | untagged | Hezbollah warns against rumors that "serve the Zionist enemy's psychological warfare" |

The first Al-Manar sentence is as agentless as LBCI's opener. Attribution to Israel arrives several flashes later, after an announced investigation. The known "Al-Manar peaked day 2 / slowest institutional response" claim is at least partly an artifact of these misses plus `id-interpolated` dates (±1 day on 40/42 records).

**Why interesting / next.** Recover the untagged cluster (also the `تزف الشهيد` named-martyr obituaries around `12483066`–`12483880`) and re-time Al-Manar against LBCI/MTV sequential IDs. If the 3:30pm timestamp is Hezbollah's own clock, it is the best public timing we have.

**Confidence:** high (the titles exist; the corpus gap is real). Medium on how much a refill would move the day-2 peak.

---

### 2. Al Jadeed's famous "names Israel 68%" is leftover 2026 ticker chrome.

Smoke-test notes said Al Jadeed body contamination was fixed. It was not. **27/59** Al Jadeed bodies still contain the live site's "now watching" strip, including `2026-06-27` copy about President Aoun calling Trump, and **27/59** still carry the identical `معاريف) 09:41 "بيت الحلم راح"` sidebar. Israel appears in **40/59** bodies but only **9/59 headlines (15.3%)**. The known 67.8% `israel_plain` figure is exactly 40/59.

Headline-only "Israel" across outlets, where chrome cannot reach:

| Outlet | Headline Israel |
|---|---|
| Al Jadeed | 9/59 = **15.3%** |
| MTV | 18/125 = **14.4%** |
| LBCI | 12/110 = **10.9%** |
| Al-Manar | 3/42 = **7.1%** |

Al Jadeed's real day-0 signature is not naming Israel. It is relaying wires without naming anyone: Reuters 1,000 wounded (`lb_aljadeed_502535`), WSJ new shipment (`lb_aljadeed_502542`), AP lithium overheating (`lb_aljadeed_502546`). Israel enters Al Jadeed *headlines* on day 1 (`lb_aljadeed_502751`, Axios: "Israel detonated thousands of devices").

**Why interesting / next.** Recompute every Lebanon body-based share with a chrome stripper, or switch the exhibit to headlines. The "Al Jadeed names Israel twice as often" talking point should not ship.

**Confidence:** high.

---

### 3. Day 0's master frame is "security breach," copied from one Reuters-Hezbollah quote. LBCI's English headline then strips the Israeli hedge.

LBCI's first item, `lb_lbci_796392` (Arabic ticker, empty body): "Preliminary information about an explosion of wireless devices known as pager or Beeper in the hands of their owners among Hezbollah elements, following estimates that the cause may be an Israeli breach, and a large number of injuries (photo)."

The next three commercial copies of the same Reuters quote, all day 0:

- `lb_lbci_796397` — "A Hezbollah official to Reuters: detonating the devices constitutes 'the biggest security breach so far'"
- `lb_mtv_1482861` — same quote, MTV ticker
- `lb_aljadeed_502514` — same quote, Al Jadeed article

**12/52 (23.1%)** of day-0 headlines are wire-voiced (Reuters/Axios/WSJ/AP). That falls to **2/56 (3.6%)** on day 2.

LBCI then translates its own opener into English as `lb_lbci_796393`. The **headline** becomes agentless: "Wireless communication devices (pagers or beepers) used by Hezbollah members explode, causing numerous injuries: Preliminary reports." The **body** puts the Israeli-breach estimate back. Arabic leads with the hedge; English headlines erase it.

**Why interesting / next.** Code first-mention of Israel by language edition, not by outlet. Check whether LBCI English is written for a wire/export audience that will not put "Israeli breach" in a hed until a named Western source does.

**Confidence:** high.

---

### 4. MTV scare-quotes "the party." Al-Manar says "the resistance." That split is cleaner than martyr/massacre.

Headline naming of the attacked organization, not the already-known شهيد/مجزرة rates:

| Form | MTV | LBCI | Al Jadeed | Al-Manar |
|---|---|---|---|---|
| `حزب الله` / Hezbollah | 21/125 (16.8%) | 27/110 (24.5%) | 11/59 (18.6%) | 3/42 (7.1%) |
| quoted `"الحزب"` | **6/125** | 0 | 0 | 0 |
| quoted `"حزب الله"` | **7/125** | 0 | 0 | 0 |
| `المقاومة` (the resistance) | 0 | 0 | 0 | **4/42 (9.5%)** |
| `عناصر` (elements) | 4 | 6 | 3 | **0** |
| `العدو`/`الصهيون` in headline | **0** | 2/110 | 0 | **7/42 (16.7%)** |

MTV examples: `lb_mtv_1482897` "the biggest security breach… detonation of Pager devices belonging to 'the party'"; `lb_mtv_1485468` "Another day of terror… explosion of 'the party's' wireless devices"; `lb_mtv_1486127` "'The party' contains the walkie-talkie blows… 'no return for the north's residents'!"

Al-Manar never once headlines `عناصر`. Its enemy-register in headlines survives even after dropping the four `الصحافة اليوم` roundups (7/38 = 18.4%). Commercial Arabic almost never puts `العدو` in a hed.

**Why interesting / next.** Scare-quotes vs `المقاومة` vs `عناصر` is a within-Lebanon exhibit that does not depend on body text. Pair it with the grammar finding (تفجير/انفجار) rather than restating martyr rates.

**Confidence:** high.

---

### 5. Named victims on commercial TV are elites. Al-Manar's human-interest piece is a blood-donation story. The named-fighter obituaries were collected and then dropped.

Day-0/1 people who get a headline:

- MP Ali Ammar's son killed: MTV `lb_mtv_1483949` "Martyrdom of MP Ali Ammar's son in the explosion of a pager"; LBCI English `lb_lbci_796442` "Hezbollah parliamentarian's son killed in Israeli breach; pager explosion kills 10-year-old girl."
- MP Hassan Fadlallah's son: LBCI Arabic `lb_lbci_796468` (injured); LBCI English `lb_lbci_796516` walks it back, "death reports false."
- Iranian ambassador Mojtaba Amani: MTV `lb_mtv_1482901` (Reuters via Mehr, day 0); Al Jadeed `lb_aljadeed_502660` "lost one of his eyes" (day 1); MTV `lb_mtv_1484222` via NYT, both eyes.
- 10-year-old girl in the Bekaa, father's pager: **LBCI English only** (`lb_lbci_796442`, AFP relatives). No Arabic LBCI headline names her. MTV's Asharq reprint `lb_mtv_1485664` later says two children, 8 and 11, among 12 dead.
- Scout child Muhammad Bilal Kanj, buried with Ammar's son: MTV `lb_mtv_1485572` (day 1, Rawdat al-Hawra Zaynab, Ghobeiry).

Al-Manar's distinctive human-interest record in the corpus is not a named child. It is `lb_almanar_12483099` (day 1, 331 words): "Heavy turnout for blood donation in Lebanese regions in support of the wounded of the Zionist aggression." Mosque minarets, tents on the Hadi Nasrallah highway, a kilometre of cars outside Nabatieh government hospital.

The named combat-death notices (`المقاومة الإسلامية تزف الشهيد…`, IDs `12483066`, `12483880` = Muhammad Mahdi Ali Ammar) sit in the title file, untagged.

**Why interesting / next.** The commercial victim hierarchy is MP family → ambassador's eye → generic "thousands wounded." Al-Manar replaces faces with solidarity logistics. Pull the dropped martyr notices and see whether Al-Manar named pager dead as fighters on day 0 while commercial TV named them as sons of MPs.

**Confidence:** high.

---

### 6. Nasrallah's speech is an Al-Manar flash-sliced event. Commercial TV barely headlined it.

Nasrallah in **headlines**: Al-Manar **4/42**, LBCI **2/110**, MTV **0/125**, Al Jadeed **0/59**.

What those records actually are:

- Al-Manar day 3, four consecutive empty-body briefs quoting the speech: `lb_almanar_12494561` (crossed every red line), `12494583` (civilian device, women and children among the dead), `12494605` ("he assumed 4,000 pagers… he intended to kill 4,000 people in one minute"), `12494649` ("we will adopt the names Tuesday Massacre and Wednesday Massacre").
- LBCI English `lb_lbci_796613` (day 1): "Nasrallah to speak Thursday at 5 p.m." Scheduling, not content.
- LBCI Arabic `lb_lbci_797005` (day 2 ticker): "Nasrallah: Hezbollah's senior leaders do not carry the pager model that exploded." A leak/preview, not the speech.
- Al Jadeed `lb_aljadeed_502973` (day 2, 850-word bulletin intro) is the one commercial record that actually transcribes the speech: "we took a large and harsh blow," "war is give and take," Israel "will not return the north's residents."
- MTV never headlines him. He appears inside reprinted analyses (`lb_mtv_1487198` quoting him that the blow is "large, security-wise and humanly, unprecedented").

**Why interesting / next.** The naming "Tuesday/Wednesday Massacre" is Hezbollah's, delivered as Al-Manar ticker slices, then almost unused by the three commercial channels. Compare to Israel-side "operation" uptake. Also: Al Jadeed's bulletin intro is literary spoken Arabic with slashes. Different genre from its wire-relay articles.

**Confidence:** high.

---

### 7. The second wave is a local-visual story. The first wave is a wire-attribution story. One Al Jadeed video captures the overlap: a walkie exploding at a pager funeral.

Device terms in headlines:

| Slot | n | pager in hed | walkie/Icom in hed |
|---|---|---|---|
| day_0 (17 Sep) | 52 | 34 (65.4%) | 20 (38.5%) |
| day_1 (18 Sep) | 115 | 62 (53.9%) | 53 (46.1%) |
| day_2 | 56 | 30 (53.6%) | 28 (50.0%) |

Even on walkie day, more headlines still say "pager." What *is* new on day 1 is place-name, camera, leftover-device disposal:

- `lb_aljadeed_502746` "On video: the moment a wireless device exploded during a funeral in the southern suburbs" (Twitter embed, 18 Sep).
- `lb_aljadeed_502819` / `502815` Clemenceau, reporter on scene.
- `lb_lbci_796779` "The army detonates a wireless device found in the AUB parking lot."
- `lb_almanar_12488687` / `12488720` army detonates a device in Clemenceau, traffic diverted.
- MTV `lb_mtv_1485469` "the devices that exploded are Icom V82"; `lb_mtv_1485468` "Another day of terror."
- Axios via MTV `lb_mtv_1485547`: today's blasts came after an assessment that Hezbollah's investigation of yesterday would expose the walkie-talkie breach. That is the only causal link the corpus draws between the two waves.

Day 0's competing technical frame dies in one record: Al Jadeed `lb_aljadeed_502546`, "AP, citing sources close to Hezbollah: the new devices have lithium batteries and appear to have exploded from overheating." By day 3 the chemistry has flipped to PETN (`lb_aljadeed_503070`).

**Why interesting / next.** Sequence the day-1 tickers against funeral times. If the walkie wave hit a pager funeral, that is the most compressed image in the corpus. Also worth a still: leftover devices being blown in civilian space (AUB, Clemenceau) as the state's on-camera response.

**Confidence:** high.

---

### 8. Al-Manar does use Israeli-sourced copy. It labels the source "enemy circles." And 80% of its words are four newspaper roundups.

`lb_almanar_12486674` (day 2, 1,097 words): "Enemy circles ask after the 'pager device detonations'… how will that return the north's residents? And readiness awaiting the resistance's reply." Body opens "after the unprecedented aggression in the history of the conflict between the Islamic resistance in Lebanon and the Israeli enemy," then walks through Yedioth's Ron Ben-Yishai. `lb_almanar_12497377` (day 3 brief, empty body): "Yedioth Ahronoth, citing US intelligence sources: Israel planned the pager-detonation operation for 15 years."

That is Israeli-sourced framing with the polarity inverted, not a refusal to touch Israeli copy. MTV's one Haaretz ticker (`lb_mtv_1484199`, day 1) does the uninverted version: "Haaretz: US reports say Israel detonated the pagers in Lebanon via text messages."

Measurement warning, because it distorts every Al-Manar body share already in circulation: four `الصحافة اليوم` / press-review dumps (`lb_almanar_12484837` 3,353 words; `12510599` 5,523; `12510720` 673; `12568866` 4,946) = **14,495 of 17,989 Al-Manar article words (80.6%)**. Of the other 38 Al-Manar records, 28 are empty-body briefs. 32/42 headlines still carry site chrome, `– موقع قناة المنار – لبنان`. Treat Al-Manar as a headline-and-flash corpus plus four giant scrapbooks.

**Why interesting / next.** Code "Israeli outlet cited as enemy" as its own attribution type, against Israel's "according to foreign reports." And drop the roundups from any rate that uses body text.

**Confidence:** high.

---

### 9. MTV's most vivid human-interest copy is not MTV's. Health Minister Abiad, not Nasrallah, is the civilianizing voice on commercial TV.

MTV published two original-voice tickers in the whole corpus (`معلومات mtv`): geographic spread on day 0 (`lb_mtv_1482889`, south / Naameh / Sidon) and the eye-injury count on day 2 (`lb_mtv_1485832`: "more than 500 eye injured from the pager detonations, 300 of them lost their sight completely"). A week-2 Reuters ticker, `lb_mtv_1489095`, escalates that to "1,500 Hezbollah elements blinded or lost their hands."

The essays that *sound* like MTV's Dahieh coverage are reprints:

- `lb_mtv_1485665` "The pager massacre: when the virus invaded the Dahieh!" is Zainab Hammoud in *Al-Akhbar* ("I saw Judgment Day with my own eyes").
- `lb_mtv_1485664` "Pager-detonation injuries more severe than the port explosion" is Lina Saleh in *Asharq Al-Awsat* (amputations, blindness, two children among 12 dead).
- `lb_mtv_1485673` and `lb_mtv_1485677` are also Asharq.

Health Minister Firas Abiad is the recurring civilian frame on MTV/Al-Manar, not on LBCI/Al Jadeed headlines: `lb_mtv_1486283` (day 3) "Abiad: we consider what happened a war crime because most of those injured by the device detonations are civilians"; `lb_almanar_12486652` "four of the pager-detonation victims are health-sector workers"; `lb_mtv_1486647` (day 4) 12 dead from pagers, 27 from walkies, 2,078 hospital operations. Al Jadeed's expert Nabil/Nabeh Awadah says the same thing from the other direction in a headline (`lb_aljadeed_502673`): "those who carry the pager are not Hezbollah fighters but ordinary elements and administrators." The body of that record is chrome. Trust the hed only.

**Why interesting / next.** Abiad's "most of the wounded are civilians" vs Hezbollah's untagged "workers in units and institutions" vs commercial `عناصر حزب الله` is three grades of combatant/civilian coding inside one country. MTV as a reprint desk also means "MTV said massacre/virus" is sometimes "Al-Akhbar said it, MTV clipped it."

**Confidence:** high on reprints and Abiad. Medium on the 500/300 eye figures (single undated-quality MTV ticker, no body).

---

## Data-quality flags (do not ignore these in the next pass)

1. **Al Jadeed bodies are still contaminated.** 27/59 carry 2026 live-ticker chrome. Any Al Jadeed body share for Israel, Israeli media, or "attack" is unsafe. Headlines are usable.
2. **Al-Manar title sweep missed at least 11 pager items**, including the day-0 Hezbollah statement series. Corpus Al-Manar starts on interpolated Sep 18.
3. **Al-Manar dates are `id-interpolated` on 40/42 records** (±1 day). Do not use them for hour-level or even confident day_0 vs day_1 claims until the missed IDs are dated from homepage captures.
4. **Al-Manar text mass is four roundups.** Body-based vocab for Al-Manar is mostly Lebanese newspaper paste, not Al-Manar's voice.
5. **100% of live_tickers have empty bodies** (MTV 66/66, LBCI 6/6). LBCI 21/30 briefs also empty. Day-0 "minute-by-minute" is a **headline sequence**, not a timestamped live blog. Numeric IDs preserve order within outlet; `published_at` is date-only.
6. **MTV: 26/125 records have no date** (`date_missing`), including likely day-0 items such as `lb_mtv_1482848` "The Israeli army detonates Hezbollah elements' wireless devices by high technology in more than one place in the southern suburbs."
7. **NNA is 2 records.** Ignore for shares.
8. **LBCI is 40% English (44/110).** Mixing EN+AR in one outlet rate hides the bilingual split in finding 3.

The usable day-0 ticker tape is LBCI Arabic IDs `796392` → `796548` and MTV `1482853` → `1484093`, plus Al Jadeed's wire stack `502509`–`502623`. Al-Manar's real tape is still sitting in the titles file.
