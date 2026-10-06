# Round 2 extraction report (us)

Extractor: `pipeline/05-extraction/round2/extract_cached_de_us.py`. Offline; every candidate's raw copy is a byte-exact gzip of its cached source page.

## Counts

- Gap rows: 706
- ok: 663
- Failures by reason: {'deferred_liveblog': 43}

| outlet | usable | rows | ok | live blogs deferred | other failures |
| --- | --- | ---: | ---: | ---: | ---: |
| abc | yes | 67 | 47 | 20 | 0 |
| ap | yes | 20 | 18 | 2 | 0 |
| cbs | yes | 29 | 29 | 0 | 0 |
| cnn | yes | 29 | 21 | 8 | 0 |
| fox | yes | 17 | 16 | 1 | 0 |
| nbc | yes | 17 | 16 | 1 | 0 |
| nyt | yes | 64 | 58 | 6 | 0 |
| reuters | yes | 2 | 2 | 0 | 0 |
| usatoday | yes | 19 | 19 | 0 | 0 |
| wapo | yes | 33 | 28 | 5 | 0 |
| yahoo | yes | 409 | 409 | 0 | 0 |

## Gate: five checks per body

A body passes when all five checks pass; a check that fails on the publisher's own text carries a `publisher_exception` with a page quote and counts as a pass. Bodies counted: the re-extracted corpus pages with a raw file plus the gap pages that produced a body. Gate: at least 95% pass all five, and no fixable `new_wrong`.

| outlet | bodies | all five | rate | no_chrome | lead_present | not_truncated | no_duplication | order | exceptions |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| abc | 52 | 52 | 100.0% | 52/52 | 52/52 | 52/52 | 52/52 | 52/52 | sentence_recurs_across_articles=11, sentence_twice_in_article=6 |
| ap | 36 | 36 | 100.0% | 36/36 | 36/36 | 36/36 | 36/36 | 36/36 | sentence_recurs_across_articles=5, sentence_twice_in_article=1 |
| cbs | 37 | 37 | 100.0% | 37/37 | 37/37 | 37/37 | 37/37 | 37/37 | description_is_a_later_sentence=3 |
| cnn | 77 | 77 | 100.0% | 77/77 | 77/77 | 77/77 | 77/77 | 77/77 | sentence_recurs_across_articles=10 |
| fox | 39 | 39 | 100.0% | 39/39 | 39/39 | 39/39 | 39/39 | 39/39 | description_is_a_later_sentence=2, sentence_recurs_across_articles=7 |
| nbc | 30 | 30 | 100.0% | 30/30 | 30/30 | 30/30 | 30/30 | 30/30 | sentence_recurs_across_articles=4 |
| nyt | 62 | 62 | 100.0% | 62/62 | 62/62 | 62/62 | 62/62 | 62/62 | ends_without_full_stop=2, sentence_recurs_across_articles=5, sentence_twice_in_article=2 |
| reuters | 6 | 6 | 100.0% | 6/6 | 6/6 | 6/6 | 6/6 | 6/6 | none |
| usatoday | 20 | 20 | 100.0% | 20/20 | 20/20 | 20/20 | 20/20 | 20/20 | description_is_a_later_sentence=3, sentence_recurs_across_articles=6 |
| wapo | 40 | 40 | 100.0% | 40/40 | 40/40 | 40/40 | 40/40 | 40/40 | description_is_a_later_sentence=1, sentence_recurs_across_articles=3 |
| yahoo | 437 | 437 | 100.0% | 437/437 | 437/437 | 437/437 | 437/437 | 437/437 | description_is_a_later_sentence=22, ends_without_full_stop=4, sentence_recurs_across_articles=73, sentence_twice_in_article=6 |

Lead check as calibrated for Israel/Lebanon: the description's opening words in the first 400 characters pass; a description whose opening words occur nowhere in the body is a rewritten teaser and passes, labelled `description_is_rewrite`; words found only after the first 400 characters fail unless what precedes them is genuine article text (`description_is_a_later_sentence`, with a quote).

`description_is_rewrite` counts: abc rewrite=1, abc on_page_not_in_body=15, ap rewrite=13, cbs rewrite=8, cnn rewrite=14, fox rewrite=20, nbc rewrite=10, nyt rewrite=4, nyt on_page_not_in_body=3, reuters rewrite=1, usatoday rewrite=12, wapo rewrite=1, wapo on_page_not_in_body=1, yahoo rewrite=106, yahoo on_page_not_in_body=2.
(`on_page_not_in_body` means the page shows the description's opening words in a prose element that the extractor did not take; these were reviewed by hand.)

## Publisher exceptions used

### abc

- `sentence_recurs_across_articles` (no_chrome), 4 bodies: "The explosions came a day after an apparent Israeli attack targeting pagers used by Hezbollah killed at least 12 and wounded nearly 3,000."
- `sentence_recurs_across_articles` (no_chrome), 3 bodies: "Office of the Spokesperson for the Secretary General."
- `sentence_recurs_across_articles` (no_chrome), 2 bodies: "Hezbollah began striking Israel almost immediately after Hamas’ Oct."
- `sentence_recurs_across_articles` (no_chrome), 1 body: "Hezbollah and the Lebanese government blamed Israel for what appeared to be a sophisticated remote attack."
- `sentence_recurs_across_articles` (no_chrome), 1 body: "The Israeli military declined to comment."
- `sentence_twice_in_article` (no_duplication), 3 bodies: "The official spoke on condition of anonymity because he was not authorized to speak to the media."
- `sentence_twice_in_article` (no_duplication), 2 bodies: "Israel says it has killed over 17,000 militants, without providing evidence."
- `sentence_twice_in_article` (no_duplication), 1 body: "Officials pointed the finger at Israel in what appeared to be a sophisticated, remote attack."

### ap

- `sentence_recurs_across_articles` (no_chrome), 3 bodies: "Gaza’s Health Ministry says more than 41,000 Palestinians have been killed in the territory since Hamas’ Oct."
- `sentence_recurs_across_articles` (no_chrome), 1 body: "Israel says it has killed over 17,000 militants, without providing evidence."
- `sentence_recurs_across_articles` (no_chrome), 1 body: "The ministry does not differentiate between fighters and civilians in its count but says a little over half of those killed were women and children."
- `sentence_twice_in_article` (no_duplication), 1 body: "Israel says it has killed over 17,000 militants, without providing evidence."

### cbs

- `description_is_a_later_sentence` (lead_present), 1 body: "Beirut, Lebanon — The Israeli military said it carried out a "targeted strike" in Beirut on Friday, as social media video showed smoke rising from the"
- `description_is_a_later_sentence` (lead_present), 1 body: "Israel and Hezbollah continued to trade hundreds of strikes on Sunday as the sides appear to be spiraling toward an all-out war following months of es"
- `description_is_a_later_sentence` (lead_present), 1 body: "Israel and the militant group Hezbollah continued to trade strikes into Sunday as the death toll from a "targeted attack" by the Israeli military on a"

### cnn

- `sentence_recurs_across_articles` (no_chrome), 10 bodies: "A switch was embedded to detonate them remotely, it added."

### fox

- `description_is_a_later_sentence` (lead_present), 1 body: "Hundreds of pagers that exploded in Lebanon and Syria in an apparent operation targeting members of Hezbollah bore the brand of a Taiwanese company, t"
- `description_is_a_later_sentence` (lead_present), 1 body: "The former chairman of the House Select Committee on the Chinese Communist Party warned about a fast-moving software and technology race between the U"
- `sentence_recurs_across_articles` (no_chrome), 7 bodies: "The Associated Press contributed to this report."

### nbc

- `sentence_recurs_across_articles` (no_chrome), 3 bodies: "This is Morning Rundown, a weekday newsletter to start your day."
- `sentence_recurs_across_articles` (no_chrome), 1 body: "Sign up to The Selection newsletter for hands-on product reviews, expert shopping tips and a look at the best deals and sales each week."

### nyt

- `ends_without_full_stop` (not_truncated), 1 body: "Jordan Chiles Appeals to Swiss Court Over Fight for Olympic Gymnastics Bronze Medal, by Lauren Merola"
- `ends_without_full_stop` (not_truncated), 1 body: "The Fed Makes a Large Rate Cut and Forecasts More to Come, by Jeanna Smialek"
- `sentence_recurs_across_articles` (no_chrome), 3 bodies: "Instead, the message activated the explosives."
- `sentence_recurs_across_articles` (no_chrome), 2 bodies: "Americans head to the polls in less than seven weeks."
- `sentence_twice_in_article` (no_duplication), 1 body: "Here’s what to know about the militant group."
- `sentence_twice_in_article` (no_duplication), 1 body: "Our theme music is by Jim Brunberg and Ben Landsverk of Wonderly."

### usatoday

- `description_is_a_later_sentence` (lead_present), 1 body: "Lebanon has been attacked by something the world has never seen before ‒ a mass sabotage of electronic devices remotely detonated."
- `description_is_a_later_sentence` (lead_present), 1 body: "Qatar Airways has banned pagers and two-way radios from its flights out of Beirut after dozens were killed and thousands injured in Lebanon this week"
- `description_is_a_later_sentence` (lead_present), 1 body: "This story was updated to add new information."
- `sentence_recurs_across_articles` (no_chrome), 3 bodies: "I'm Taylor Wilson, and I'll be back tomorrow with more of The Excerpt from USA TODAY."
- `sentence_recurs_across_articles` (no_chrome), 3 bodies: "This story was updated to add new information."

### wapo

- `description_is_a_later_sentence` (lead_present), 1 body: "Hostilities between Israel and Hezbollah — which have escalated over the past year, to the cusp of all-out war over the past week — are rooted in deca"
- `sentence_recurs_across_articles` (no_chrome), 3 bodies: "Israel estimates Hezbollah has some 150,000 rockets and missiles, including guided missiles and long-range projectiles capable of striking anywhere in"

### yahoo

- `description_is_a_later_sentence` (lead_present), 2 bodies: "Israeli airstrikes targeted Hezbollah weapons sites in southern Lebanon on Monday."
- `description_is_a_later_sentence` (lead_present), 2 bodies: "Pagers and walkie-talkies belonging to Hezbollah members blew up across Lebanon this week."
- `description_is_a_later_sentence` (lead_present), 2 bodies: "This story was updated to add new information."
- `description_is_a_later_sentence` (lead_present), 2 bodies: "Wireless pagers used by Hezbollah militants suddenly exploded across Lebanon on Tuesday."
- `description_is_a_later_sentence` (lead_present), 1 body: "A Lebanese surgeon has described how the sheer volume of severe wounds from two days of exploding device attacks forced him to act "robotic" just to b"
- `description_is_a_later_sentence` (lead_present), 1 body: "BEIRUT, Lebanon, Sept. 20 (UPI) -- Israeli jets carried out a strike Friday targeting a senior Hezbollah military commander in Beirut's southern subur"
- `description_is_a_later_sentence` (lead_present), 1 body: "Beirut, Lebanon — The Israeli military said it carried out a "targeted strike" in Beirut on Friday, as social media video showed smoke rising from the"
- `description_is_a_later_sentence` (lead_present), 1 body: "Electronic pagers across Lebanon exploded simultaneously on Tuesday, killing 12 and wounding more than 2,700. The following day, another wave of explo"
- `description_is_a_later_sentence` (lead_present), 1 body: "From the The Morning Dispatch on The Dispatch"
- `description_is_a_later_sentence` (lead_present), 1 body: "Israeli strikes killed more than 550 people on Monday, Lebanese health officials reported, making it the deadliest day in Lebanon since the 2006 Israe"
- `description_is_a_later_sentence` (lead_present), 1 body: "It seems hard to believe that it’s less than a week since Hezbollah’s communication devices started exploding all across Lebanon."
- `description_is_a_later_sentence` (lead_present), 1 body: "JERUSALEM — Hezbollah and the Lebanese government were quick to blame Israel for the nearly simultaneous detonation of hundreds of pagers used by the"
- `description_is_a_later_sentence` (lead_present), 1 body: "Lebanese Americans in Michigan are in mourning this week after a series of attacks over two days in Lebanon involving pagers and walkie talkies led to"
- `description_is_a_later_sentence` (lead_present), 1 body: "On Tuesday and Wednesday, pagers and small electronic devices belonging to members of Hezbollah exploded across Lebanon. The operation, allegedly carr"
- `description_is_a_later_sentence` (lead_present), 1 body: "Qatar Airways has told passengers they can't take pagers and two-way radios on its flights out of Beirut after dozens were killed and thousands injure"
- `description_is_a_later_sentence` (lead_present), 1 body: "The international "community" and its academic justifiers have claimed that Israel's attacks on Hezbollah communications devices are unlawful. They ar"
- `description_is_a_later_sentence` (lead_present), 1 body: "The situation in the Gaza Strip could not be more dire."
- `description_is_a_later_sentence` (lead_present), 1 body: "This week saw a significant spike in tensions between Israel and the Lebanese militant group Hezbollah, with both sides exchanging heavy fire followin"
- `ends_without_full_stop` (not_truncated), 1 body: "Israel is yet to comment on claims that it was behind a wave of pager and walkie-talkie explosions which killed at least 37 people and injured thousan"
- `ends_without_full_stop` (not_truncated), 1 body: "The group has vowed to 'uniquely punish' Israel"
- `ends_without_full_stop` (not_truncated), 1 body: "r (R-KY), House Oversight Committee Chairman; Antonio Tajani, Italian Foreign Minister; Erik Prince, Blackwater Founder, former U.S. Navy Seal Officer"
- `ends_without_full_stop` (not_truncated), 1 body: "—Casting a wide net"
- `sentence_recurs_across_articles` (no_chrome), 5 bodies: "The Israeli military declined to comment."
- `sentence_recurs_across_articles` (no_chrome), 4 bodies: ""Our goal is to ensure the safe return of Israel's northern communities to their homes."
- `sentence_recurs_across_articles` (no_chrome), 4 bodies: "Israel has not directly commented on the attacks."
- `sentence_recurs_across_articles` (no_chrome), 3 bodies: ""Everyone is in a wait-and-see mode until after the election."
- `sentence_recurs_across_articles` (no_chrome), 3 bodies: ""I consider this situation extremely worrying."
- `sentence_recurs_across_articles` (no_chrome), 3 bodies: ""In light of increased tension in the Middle East and out of an abundance of caution, we are sending a small number of additional U.S."
- `sentence_recurs_across_articles` (no_chrome), 3 bodies: ""We are at the beginning of a new era in this war and we need to adapt ourselves," Gallant said."
- `sentence_recurs_across_articles` (no_chrome), 3 bodies: "An AP photographer in the southern coastal city of Sidon saw a car and a mobile phone shop damaged after devices exploded inside of them."
- `sentence_recurs_across_articles` (no_chrome), 3 bodies: "Office of the Spokesperson for the Secretary General."
- `sentence_recurs_across_articles` (no_chrome), 3 bodies: "The Lebanese Shiite militia Hezbollah blamed Israel for the detonations, threatening retaliation."
- `sentence_recurs_across_articles` (no_chrome), 3 bodies: "The death toll from Friday's Israeli attack on Beirut's southern suburbs, a hotbed of the Hezbollah movement, rose to 45, the Lebanese Health Ministry"
- `sentence_recurs_across_articles` (no_chrome), 3 bodies: "The sound of blasts coincided with Hezbollah mourning some of the people who died in Tuesday's detonations of pagers, which killed 12 and wounded some"
- `sentence_recurs_across_articles` (no_chrome), 3 bodies: "The two sides have been engaged in cross-border warfare since the Gaza conflict erupted last October."
- `sentence_recurs_across_articles` (no_chrome), 3 bodies: "What is Hezbollah and why is it fighting with Israel?"
- `sentence_recurs_across_articles` (no_chrome), 2 bodies: ""A lot of things don't look realistic until we get them done."
- `sentence_recurs_across_articles` (no_chrome), 2 bodies: ""I can tell you that the U.S."
- `sentence_recurs_across_articles` (no_chrome), 2 bodies: ""The Mossad injected a board inside of the device that has explosive material that receives a code."
- `sentence_recurs_across_articles` (no_chrome), 2 bodies: "7 attack by Hamas that sparked the war in Gaza."
- `sentence_recurs_across_articles` (no_chrome), 2 bodies: "A switch was embedded to detonate them remotely, it added."
- `sentence_recurs_across_articles` (no_chrome), 2 bodies: "Among those wounded was Iran's ambassador to Lebanon."
- `sentence_recurs_across_articles` (no_chrome), 2 bodies: "Instead, they were a deadly Trojan horse."
- `sentence_recurs_across_articles` (no_chrome), 2 bodies: "The official spoke on condition of anonymity because he was not authorized to speak to the media."
- `sentence_recurs_across_articles` (no_chrome), 2 bodies: "Unconfirmed reports were circulating that Israel had targeted communications devices used by Hezbollah and was behind the detonations."
- `sentence_recurs_across_articles` (no_chrome), 1 body: "8, the day after a deadly Hamas-led assault in southern Israel triggered the war in Gaza."
- `sentence_recurs_across_articles` (no_chrome), 1 body: "Gaza's Health Ministry says more than 41,000 Palestinians have been killed in the territory since Hamas' Oct."
- `sentence_recurs_across_articles` (no_chrome), 1 body: "Hezbollah began striking Israel almost immediately after Hamas' Oct."
- `sentence_recurs_across_articles` (no_chrome), 1 body: "Iran's ambassador to Lebanon, Mojtaba Amani, was also reportedly injured in the explosion of a pager."
- `sentence_recurs_across_articles` (no_chrome), 1 body: "Israel says it has killed over 17,000 militants, without providing evidence."
- `sentence_recurs_across_articles` (no_chrome), 1 body: "It's very hard to detect it through any means."
- `sentence_recurs_across_articles` (no_chrome), 1 body: "Since then, hundreds have been killed in strikes in Lebanon and dozens in Israel, while tens of thousands on each side of the border have been displac"
- `sentence_recurs_across_articles` (no_chrome), 1 body: "The ministry does not differentiate between fighters and civilians in its count but says a little over half of those killed were women and children."
- `sentence_recurs_across_articles` (no_chrome), 1 body: "Volker Türk told an emergency meeting of the U.N."
- `sentence_twice_in_article` (no_duplication), 2 bodies: "The Israel Defense Forces said on Saturday night it launched two waves of attacks – one attacking about 290 targets, and a second targeting 110 sites"
- `sentence_twice_in_article` (no_duplication), 1 body: "Israel says it has killed over 17,000 militants, without providing evidence."
- `sentence_twice_in_article` (no_duplication), 1 body: "Officials pointed the finger at Israel in what appeared to be a sophisticated, remote attack."
- `sentence_twice_in_article` (no_duplication), 1 body: "The official spoke on condition of anonymity because he was not authorized to speak to the media."
- `sentence_twice_in_article` (no_duplication), 1 body: "There was no immediate confirmation of his death from Hezbollah."

Totals by type: description_is_a_later_sentence=31, ends_without_full_stop=6, sentence_recurs_across_articles=124, sentence_twice_in_article=15.

## Chrome check

Sentences of 6+ words found in 3 or more bodies of one outlet with different headlines were reviewed one by one. Page chrome that turned up was removed by container or paragraph rules, not sentence by sentence; what remains is wire or standing publisher text, listed above as `sentence_recurs_across_articles`.

## Regression diagnostic against stored v1 bodies

Diagnostic only: stored v1 bodies often hold page chrome (share bars, caption blocks, newsletter boxes, player code).

| outlet | n | median ratio | share >= 0.90 |
| --- | ---: | ---: | ---: |
| abc | 5 | 0.949 | 100.0% |
| ap | 17 | 0.999 | 100.0% |
| cbs | 8 | 0.997 | 100.0% |
| cnn | 56 | 1.000 | 100.0% |
| fox | 23 | 0.746 | 4.3% |
| nbc | 14 | 1.000 | 92.9% |
| nyt | 4 | 0.851 | 0.0% |
| reuters | 4 | 0.893 | 25.0% |
| usatoday | 1 | 0.841 | 0.0% |
| wapo | 12 | 0.919 | 66.7% |
| yahoo | 28 | 0.904 | 53.6% |

Adjudication of every record below 0.90 (`regression-adjudication.csv`): stored_wrong=48, new_wrong=0, both=0.

## Spot samples

Chosen with `random.Random(2024)` from the gap candidates that have a body.

### abc

- Taiwanese company Gold Apollo says the pagers that exploded in Lebanon and Syria were made by a company in Budapest | 2024-09-18 | article | page-state:abc
  - first 200: Taiwanese company Gold Apollo says the pagers that exploded in Lebanon and Syria were made by a company in Budapest.
  - last 150: Taiwanese company Gold Apollo says the pagers that exploded in Lebanon and Syria were made by a company in Budapest.

- Hezbollah officials say at least two of its members and a girl were killed when the group's new brand of pagers exploded | 2024-09-17 | article | page-state:abc
  - first 200: Hezbollah officials say at least two of its members and a girl were killed when the group's new brand of pagers exploded.
  - last 150: Hezbollah officials say at least two of its members and a girl were killed when the group's new brand of pagers exploded.

- What is Hezbollah? Lebanon's militant group has long been one of Israel's biggest foes | 2024-09-24 | article | page-state:abc
  - first 200: Israel and Hezbollah's long-simmering border conflict has intensified in recent days, piquing fears of escalation. / Israel and Hezbollah have exchanged hundreds of cross-border strikes in recent days
  - last 150: think there's a better way to do that than an all-out conflict," Kirby said. / ABC News' David Brennan and Julia Reinstein contributed to this report.

### ap

- The US is more hands-off than usual in the Middle East. It fears making things worse | 2024-09-21 | article | container:ap
  - first 200: WASHINGTON (AP) — The Biden administration is taking a more hands-off approach than usual during a week of dramatic escalation between Israel and Hezbollah militants in Lebanon, with top U.S. official
  - last 150: ’re still going to keep the shoulder to the wheel. We’re still going to keep trying on this.” / AP reporter Aamer Madhani contributed from Washington.

- Israel-Hamas war latest: 15 killed overnight in Gaza in multiple attacks | 2024-09-20 | article | container:ap
  - first 200: Palestinian authorities say 15 people were killed overnight in the Gaza Strip in multiple Israeli attacks. / An airstrike early Friday morning in Gaza City hit a family home, killing six people includ
  - last 150: as blamed on Israel, and many of those killed or injured were members of Hezbollah. / Associated Press writer Bassem Mroue contributed to this report.

- Iran's President accuses Israel of seeking wider Mideast war and laying 'traps' to lead Iran into it | 2024-09-23 | article | container:ap
  - first 200: UNITED NATIONS (AP) — Iran’s president accused Israel on Monday of seeking a wider war in the Middle East and laying “traps” to lead his country into a wider conflict. / Masoud Pezeshkian told about t
  - last 150: ebanon last week, which he blamed on Israel, and the assassination of Hamas’ political leader Ismail Haniyeh in Tehran on the eve of his inauguration.

### cbs

- Israeli President Isaac Herzog says "we did not want this war" | 2024-09-22 | article | container:cbs
  - first 200: Washington — Israeli President Isaac Herzog said Sunday that his country "did not want this war" with Hezbollah and ahead of Israel's attacks on Friday that killed a senior commander of the terrorist 
  - last 150: called "boiling hot," presents an "opportunity to go forward and change this situation by finding the right exit and bringing the hostages back home."

- Full transcript of "Face the Nation with Margaret Brennan," Sept. 22, 2024 | 2024-09-22 | article | container:cbs
  - first 200: On this "Face the Nation" broadcast, moderated by Margaret Brennan: / MARGARET BRENNAN: I'm Margaret Brennan in Washington. / And this week on Face the Nation: Our CBS News polling shows new gains for
  - last 150: : We'll be right back. / MARGARET BRENNAN: That's it for us today. Thank you for watching. Until next week, for FACE THE NATION, I'm Margaret Brennan.

- Walkie-talkies explode in Lebanon, according to reports | 2024-09-18 | video_page | meta-description-video
  - first 200: A source close to Lebanon's Hezbollah group told French news agency AFP that walkie-talkies used by the militant group had exploded in Beirut Wednesday. This comes after thousands of pagers exploded o
  - last 150: ands of pagers exploded on Tuesday, killing at least 12 people, according to Lebanon's public health minister. CBS News' Chris Livesay has the latest.

### cnn

- Hezbollah is not Hamas. Can Israel afford another all-out war? | 2024-09-24 | article | container:cnn
  - first 200: After nearly a year of fighting in Gaza, Israel is ramping up hostilities with Hezbollah in Lebanon, with covert operations targeting communications devices and a ferocious bombing campaign that has l
  - last 150: esidents, who have lived close to the frontline for nearly a year, believe that “only a full-scale war can change the reality in the north,” he added.

- Father of American hostage held by Hamas says Lebanon attacks treat ‘agony with more agony’ | 2024-09-19 | article | container:cnn
  - first 200: The father of an American hostage still being held in Gaza by Hamas criticized the deadly attacks in Lebanon that caused pagers and walkie-talkies to explode killing dozens, stating “this pager, missi
  - last 150: tional community to pressure Hamas and release these innocent hostages who are rotting,” he said. / CNN’s Eugenia Yosef and Arlette Saenz contributed.

- Weakened and infiltrated, Hezbollah vows ‘battle without limits’ against Israel | 2024-09-22 | article | container:cnn
  - first 200: An Israeli airstrike reduces a nine-story apartment building in Beirut’s southern suburb to a large mound of rubble. A man covered in dust flails lifelessly in the arms of a rescuer. A corpse in a bod
  - last 150:  / “We are strong in our faith … We are all ready to spill blood for Nasrallah.” / Ben Wedeman, Sarah Sirgany and Charbel Mallo contributed reporting.

### fox

- Morgan Ortagus: Officials Continuing to Criticize Israel's "Brilliant" Pager Operation Are "Political Hacks" | 2024-09-23 | podcast_page | meta-description-podcast
  - first 200: Morgan Ortagus, former spokesperson for the United States Department of State and founder of Polaris National Security, joined the Guy Benson Show to discuss the left's absurd response to Israel's tar
  - last 150:  discuss the left's absurd response to Israel's targeted attacks on Hezbollah-linked pagers. Morgan broke down why the left consistently finds ways to

- Israel Infiltrates Hezbollah Pagers, Where Does A Ceasefire Stand? | 2024-09-20 | podcast_page | meta-description-podcast
  - first 200: Israel's latest intelligence operation infiltrated pagers owned by Hezbollah operatives, causing them to explode in Beirut -- revealing how sophisticated Israel's intelligence capabilities are. As the
  - last 150: ted Israel's intelligence capabilities are. As the world ponders how Israel was able to do this, the other pressing question revolves around how Hezbo

- Robert Davi calls out 'huge disconnect' between Hollywood for Harris and 'rank-and-file' Teamsters for Trump | 2024-09-22 | article | container:fox
  - first 200: It's a tale of two candidates. / While Vice President Kamala Harris continues to reel in mass support from stars like Billie Eilish, Chris Rock, Meryl Streep, Oprah and Taylor Swift, former President 
  - last 150: ulled in support from other Hollywood personalities like George Clooney, Julia Roberts, Ben Stiller, Mark Hamill, Jamie Lee Curtis and rapper Cardi B.

### nbc

- Secretary Blinken comments about exploding pagers in Lebanon | 2024-09-18 | video_page | meta-description-video
  - first 200: Secretary of State Antony Blinken called on "all parties" to avoid escalating the regional conflict caused by the war between Hamas and Israel. Speaking in Cairo, Egypt, Blinken said the U.S. had no k
  - last 150: ad no knowledge of or involvement in "these incidents" in which at least nine people were killed and thousands injured by exploding pagers in Lebanon.

- New reports of explosions in Lebanon one day after pager attacks | 2024-09-18 | video_page | meta-description-video
  - first 200: More device explosions were reported across Lebanon, just one day after pagers belonging to Hezbollah members detonated across the country, killing at least 12 people and injuring nearly 3,000 others.
  - last 150: he country, killing at least 12 people and injuring nearly 3,000 others. NBC News’ Raf Sanchez reports on what appears to be a second wave of attacks.

- Lebanon reels from second day of explosions and Sean 'Diddy' Combs denied bail: Morning Rundown | 2024-09-19 | article | container:nbc
  - first 200: Sean “Diddy” Combs remains jailed after his bond appeal was rejected, in part because of witness intimidation allegations. Israel declares a ‘’new phase’’ of war as Lebanon reels from a second day of 
  - last 150: . Today’s newsletter was curated for you by Elizabeth Robinson. If you’re a fan, please send a link to your family and friends. They can sign up here.

### nyt

- Israel’s Attacks on Hezbollah Have Intensified but Stop Short of All-Out War | 2024-09-20 | article | container:nyt
  - first 200: Israel is attempting a risky strategy, increasing the intensity of its attacks in an attempt to force Hezbollah to back down, while raising the chances of an aggressive response that devolves into a l
  - last 150: f a decisive blow, humiliating Hezbollah and spreading horror through Lebanese society, but so far failing to coerce the militia into changing course.

- What Are Pagers? Devices Exploded Across Lebanon | 2024-09-18 | article | container:nyt
  - first 200: Pagers lack more modern navigation technologies so can be harder to track, but are still widely used in hospitals for their reliable service. / In the 1990s, before the widespread use of cellphones, p
  - last 150: ple, the discs that many restaurants and coffee shops hand to waiting customers to alert them that their order or table is ready use pager technology.

- Pager Attack Highlights Tension Between Israel’s Might and Strategic Fog | 2024-09-19 | article | container:nyt
  - first 200: In Gaza, Lebanon and Iran, Israel has shown it’s capable of extraordinary acts of espionage, but is struggling to define long-term goals, according to Israeli analysts and public figures. / The contra
  - last 150: id Mr. Olmert. “It will make life for Israel much easier to deal with such challenges.” / Rawan Sheikh Ahmad and Johnatan Reiss contributed reporting.

### reuters

- Hezbollah vows to punish Israel after pager explosions across Lebanon | 2024-09-17 | article | container:reuters
  - first 200: BEIRUT, Sept 17 (Reuters) - Militant group Hezbollah promised to retaliate against Israel after accusing it of detonating pagers across Lebanon on Tuesday, killing nine people and wounding nearly 3,00
  - last 150:  the border by the hostilities. / On Tuesday, Israel added to its formal war goals the return of citizens to their homes near the border with Lebanon.

- Exploding radios in Lebanon disrupt its fragile health system, WHO says | 2024-09-19 | article | container:reuters
  - first 200: GENEVA, Sept 19 (Reuters) - Explosions in booby-trapped radios and pagers in Lebanon this week seriously disrupted its fragile health sector, the World Health Organization chief said on Thursday. / Th
  - last 150: ow have the opportunity to make Guinea Worm only the second human disease to be eradicated," he said, referencing the eradication of smallpox in 1980.

### usatoday

- Top Hezbollah commander among those killed in Israeli strike on Lebanon | The Excerpt | 2024-09-23 | article | container:usatoday
  - first 200: On Saturday’s episode of The Excerpt podcast: Tensions continue along the Lebanon-Israel border, as Israel strikes Beirut. USA TODAY Justice Department Correspondent Bart Jansen discusses what the Sec
  - last 150:  pods, and if you're on a smart speaker, just ask for The Excerpt. I'm Taylor Wilson, and I'll be back Monday with more of The Excerpt from USA TODAY.

- Daily Briefing: Kids aren't getting flu shots | 2024-09-19 | article | container:usatoday
  - first 200: The nation recorded one of its worst totals for child deaths from the flu this past season. Unease spreads across Lebanon after attacks on wireless electronic devices caused thousands of injuries. USA
  - last 150: astic containers was once popularized by "Tupperware Parties" in which representatives hosted at-home events show off products to potential customers.

- Israeli charged in Iranian plot to kill Benjamin Netanyahu, officials say | 2024-09-19 | article | container:usatoday
  - first 200: An Israeli businessman was smuggled into Iran to plot the assassination of Prime Minister Benjamin Netanyahu and other top Israeli officials, police and intelligence officials said Thursday, amid risi
  - last 150: s," and "threatening other Israeli citizens activated in the country by the Iranian regime who did not complete requested tasks," the government said.

### wapo

- What is Hezbollah, the group battling Israel in Lebanon? | 2024-09-24 | article | container:wapo
  - first 200: After almost a year of trading fire, Israel and the Lebanese militant group Hezbollah are now engaged in ferocious confrontations that threaten to turn into a full-blown war / BEIRUT — After almost a 
  - last 150: o make political compromises. / He has lived in hiding for years, fearing Israeli assassination, and delivers his speeches from undisclosed locations.

- Hezbollah commander killed in Israeli airstrike was top military official on US wanted list | 2024-09-21 | article | container:wapo
  - first 200: The Hezbollah commander killed in an Israeli airstrike in Beirut’s southern suburbs was one of the Lebanese militant group’s top military officials / BEIRUT — The Hezbollah commander killed in an Isra
  - last 150: ers and drive civilians out of the area. Israel is saying: “If our people (in the north) can’t return, your people (in the suburb) will be displaced.”

- Blinken says surprise escalations threaten to derail talks for a cease-fire in Gaza | 2024-09-18 | article | container:wapo
  - first 200: U.S. Secretary of State Antony Blinken has expressed frustration at surprise escalations that threaten to derail efforts to broker a cease-fire deal in Gaza / CAIRO — U.S. Secretary of State Antony Bl
  - last 150:  of his hardline coalition government, with some members opposed to any deal with the Palestinians. / Ahmed Hatem in Cairo contributed to this report.

### yahoo

- News Analysis: An imperiled Hezbollah faces the prospect of all-out war with Israel | 2024-09-24 | article | container:yahoo
  - first 200: Thousands of its members wounded and at least two dozen killed when their pagers and walkie-talkies exploded. One of its key operatives assassinated in an airstrike that pulverized an eight-story buil
  - last 150: ctators to the hostilities and downplayed the dangers. / "We would sit and drink coffee, watching the two sides trade fire," she said. "Now it's war."

- Japan firm says it stopped making walkie-talkies used in Lebanon blasts | 2024-09-19 | article | container:yahoo
  - first 200: A Japanese handheld radio manufacturer has distanced itself from walkie-talkies bearing its logo that exploded in Lebanon, saying it discontinued production of the devices a decade ago. / At least 20 
  - last 150: Arcidiacono said she knew nothing about the explosions. “I don’t make the pagers. I am just the intermediate. I think you got it wrong," she told NBC.

- Israel is quite right to pre-empt an onslaught, and act accordingly | 2024-09-22 | article | container:yahoo
  - first 200: Amid the drama of Israel's devastating booby traps and precision air strikes against Hezbollah, it is easy to lose sight of what is really at stake. With ex-diplomats and academic experts filling the 
  - last 150: r ceasefires that help the terrorists to regroup, Britain and other allies should applaud Israel's decisive action – for it is the only path to peace.

## What changed since round 1

The gate is the five body checks, pass rate counted over all five together (exceptions count as passes). A low ratio against a stored v1 body is a diagnostic and is classified in `regression-adjudication.csv`.
Lead check recalibrated as for Israel/Lebanon: a description whose opening words occur nowhere in the body is a rewritten teaser (pass, `description_is_rewrite`). It fails only when the words occur after the first 400 characters, and then a `publisher_exception` is recorded only if the text before them is genuine article text.
Truncation check: closing lines a publisher puts after the last sentence (contributor credits, wire source lines, URL lines, bylines, interview credits, `[Source]` tags, update stamps) are accepted; a bulleted last item without full stop is an exception with a quote; a body that is the page description is accepted unless the publisher cut it with an ellipsis (`page_truncated`).
Order check: a paragraph that occurs several times in the JSON-LD `articleBody` is matched at its first occurrence after the previous match.
Exceptions are verified in code: the quote must occur in the page's visible text or its JSON page state. Cross-page repeated sentences (6+ words, 3+ bodies, different headlines) are chrome when they match a promo pattern, otherwise `sentence_recurs_across_articles`.
Video pages are recognised by URL (`/video/`, `/videos/`, `/mediathek/`) or by a VideoObject without a full article body; their body is the page description. Podcast pages (`radio.foxnews.com`, `/podcast`) likewise.
Titles lose section or type labels the page appends (Bild `| Politik`, Welt `- Video`).
ABC (was unusable, lead_present 37/52, no_duplication 46/52): the old lead rule was stricter than the calibration and the duplicated sentences are real repeats between datelines of AP rolling stories. `provider: AP` only when the URL is `/wireStory/` or the page credits AP.
AP (was unusable, not_truncated 31/34): the failures ended on "Follow AP's war coverage at <URL>" or a contributor credit. The two AP video pages are now video pages with the description as body.
CNN: the 3 `new_wrong` and the blocked status came from video pages whose only text is a one-line slate ("X joins The Lead"). The description is now the body of video pages. The 5 Things promo lines and the newsletter editor's note are cut.
NYT: the access-wall `<noscript>` text, the "Our coverage" link guide (`#styln-guide`), the author-bio block (`bottom-of-article`) and newsletter call-to-action lines are left out. Captures that show the access wall get `paywall: true` and the warning `page_truncated_by_access_wall`.
WaPo: every `font-copy` paragraph plus the deck; the photo caption, byline block and the "History" promo are not taken. Paywalled captures give the description with `paywall: true`.
Yahoo: the provider comes from `data/us/08-recall-audit/raw/yahoo-providers.csv` (column `provider_name`; round 1 read a column that does not exist, so no provider was ever set). Syndication footers (Telegraph offers, "Read the original article ...", newsletter and app prompts, Nexstar copyright line), section labels ("Best of Rolling Stone") and photo credits are dropped as whole paragraphs. Key-takeaway boxes and the "Return to Homepage" ticker stay out.
Fox: author-bio blocks are left out; `radio.foxnews.com` podcast pages give the description. NBC: the byline bio block is left out. USA Today: podcast-player boilerplate, newsletter and subscription prompts are left out. CBS: the transcript promo line is left out.
Language is assigned from the dominant script (Hebrew or Arabic tweet text inside an English body no longer makes it `he`/`ar`).

## Judgment calls

Author bios and byline blocks (Fox `author-bio`, NBC `byline`, NYT `bottom-of-article`) are not body. Contributor credits that are paragraphs of the story are kept.
NBC Morning Rundown pages keep their own newsletter text, including the sign-up line for The Selection (4 bodies, listed as recurring); Yahoo copies of them have the prompts cut.
CNN video pages with a one-line slate keep that slate as body (stored v1 does the same).
One hand-registered exception: the Yahoo "Sunday shows preview" page ends on a guest list without a full stop (`ends_without_full_stop`, quote in the exception list).
Of 48 records below 0.90 against v1, all are `stored_wrong`: stored bodies carry captions, "Share full article" blocks, "Our Coverage" guides, Yahoo key-point boxes, Fox video overlays and promo text; the new body had no article text that the stored body lacks except leads and decks.

## Open problems

- Live blogs are deferred (43 rows). Paywalled or lead-only captures: NYT 19, WaPo 5 (see `paywall`).
- Yahoo syndicates dozens of outlets; footers and promos that occur in fewer than 3 bodies are only caught by the generic patterns in `BOILER_RE`. Expect a few left over.
- CBS `Face the Nation` transcript: the guest list (short list items) is not in the body.
- ABC page-state bodies and AP rolling stories contain repeated background paragraphs that are in the publisher's text.
