# Round 2 extraction report (germany)

Extractor: `pipeline/05-extraction/round2/extract_cached_de_us.py`. Offline; every candidate's raw copy is a byte-exact gzip of its cached source page.

## Counts

- Gap rows: 196
- ok: 179
- Failures by reason: {'deferred_liveblog': 17}

| outlet | usable | rows | ok | live blogs deferred | other failures |
| --- | --- | ---: | ---: | ---: | ---: |
| bild | yes | 13 | 13 | 0 | 0 |
| ntv | yes | 48 | 47 | 1 | 0 |
| rnd | yes | 21 | 13 | 8 | 0 |
| rtl | yes | 6 | 6 | 0 | 0 |
| spiegel | yes | 30 | 30 | 0 | 0 |
| tagesschau | yes | 15 | 9 | 6 | 0 |
| tonline | yes | 13 | 13 | 0 | 0 |
| welt | yes | 49 | 48 | 1 | 0 |
| zdfheute | yes | 1 | 0 | 1 | 0 |

## Gate: five checks per body

A body passes when all five checks pass; a check that fails on the publisher's own text carries a `publisher_exception` with a page quote and counts as a pass. Bodies counted: the re-extracted corpus pages with a raw file plus the gap pages that produced a body. Gate: at least 95% pass all five, and no fixable `new_wrong`.

| outlet | bodies | all five | rate | no_chrome | lead_present | not_truncated | no_duplication | order | exceptions |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| bild | 39 | 39 | 100.0% | 39/39 | 39/39 | 39/39 | 39/39 | 39/39 | description_is_a_later_sentence=1 |
| ntv | 59 | 59 | 100.0% | 59/59 | 59/59 | 59/59 | 59/59 | 59/59 | sentence_twice_in_article=1 |
| rnd | 35 | 35 | 100.0% | 35/35 | 35/35 | 35/35 | 35/35 | 35/35 | sentence_recurs_across_articles=11 |
| rtl | 8 | 8 | 100.0% | 8/8 | 8/8 | 8/8 | 8/8 | 8/8 | none |
| spiegel | 66 | 66 | 100.0% | 66/66 | 66/66 | 66/66 | 66/66 | 66/66 | sentence_recurs_across_articles=11 |
| tagesschau | 24 | 24 | 100.0% | 24/24 | 24/24 | 24/24 | 24/24 | 24/24 | none |
| tonline | 59 | 59 | 100.0% | 59/59 | 59/59 | 59/59 | 59/59 | 59/59 | sentence_recurs_across_articles=18 |
| welt | 64 | 64 | 100.0% | 64/64 | 64/64 | 64/64 | 64/64 | 64/64 | sentence_recurs_across_articles=7, sentence_twice_in_article=1 |
| zdfheute | 15 | 15 | 100.0% | 15/15 | 15/15 | 15/15 | 15/15 | 15/15 | none |

Lead check as calibrated for Israel/Lebanon: the description's opening words in the first 400 characters pass; a description whose opening words occur nowhere in the body is a rewritten teaser and passes, labelled `description_is_rewrite`; words found only after the first 400 characters fail unless what precedes them is genuine article text (`description_is_a_later_sentence`, with a quote).

`description_is_rewrite` counts: bild rewrite=20, rnd rewrite=2, rtl rewrite=1, spiegel rewrite=7, spiegel on_page_not_in_body=1, tonline rewrite=4.
(`on_page_not_in_body` means the page shows the description's opening words in a prose element that the extractor did not take; these were reviewed by hand.)

## Publisher exceptions used

### bild

- `description_is_a_later_sentence` (lead_present), 1 body: "Die Explosionswellen von detonierten Pagern und Walkie-Talkies schockte am Dienstag und Mittwoch die Terroristen der Hisbollah. Jetzt berichtet „ABC N"

### ntv

- `sentence_twice_in_article` (no_duplication), 1 body: "Im Libanon schmeißen Leute ihre Handys auf die Straße."

### rnd

- `sentence_recurs_across_articles` (no_chrome), 3 bodies: "Das mächtigste Gremium der Vereinten Nationen soll sich nach Angaben aus Diplomatenkreisen am Freitag um 21 Uhr MESZ treffen."
- `sentence_recurs_across_articles` (no_chrome), 3 bodies: "Israels Armee kommentierte die Vorfälle zunächst nicht."
- `sentence_recurs_across_articles` (no_chrome), 3 bodies: "Zeitgleich explodierten im Libanon Hunderte Funkgeräte."
- `sentence_recurs_across_articles` (no_chrome), 2 bodies: "Israelische Agenten hätten die in Taiwan hergestellten Geräte vor der Ankunft im Libanon abgefangen und mit jeweils etwa 25 bis 50 Gramm Sprengstoff b"

### spiegel

- `sentence_recurs_across_articles` (no_chrome), 5 bodies: "Berichte über Verletzte gab es zunächst nicht."
- `sentence_recurs_across_articles` (no_chrome), 3 bodies: "Erst explodieren Pager, tags darauf Walkie-Talkies."
- `sentence_recurs_across_articles` (no_chrome), 3 bodies: "Ihr Martin Knobbe, Leiter des SPIEGEL-Hauptstadtbüros"

### tonline

- `sentence_recurs_across_articles` (no_chrome), 5 bodies: "Berichte über Verletzte gab es zunächst nicht."
- `sentence_recurs_across_articles` (no_chrome), 5 bodies: "Unter den Todesopfern seien ein acht Jahre altes Mädchen und ein elf Jahre alter Junge."
- `sentence_recurs_across_articles` (no_chrome), 3 bodies: "Israel hat sich bislang nicht öffentlich zu den Angriffen bekannt."
- `sentence_recurs_across_articles` (no_chrome), 3 bodies: "Oktober 2023 mehr als 1.200 Menschen in Israel getötet und etwa 250 weitere als Geiseln in den Gazastreifen verschleppt."
- `sentence_recurs_across_articles` (no_chrome), 1 body: "Israel könne erst dann wieder Menschen in Sicherheit in den Norden zurückkehren lassen, wenn der Krieg im Gazastreifen gestoppt werde."
- `sentence_recurs_across_articles` (no_chrome), 1 body: "Rund 3.000 weitere wurden demnach verletzt."

### welt

- `sentence_recurs_across_articles` (no_chrome), 3 bodies: "Unter den Todesopfern seien ein acht Jahre altes Mädchen und ein elf Jahre alter Junge."
- `sentence_recurs_across_articles` (no_chrome), 2 bodies: "Israel könne erst dann wieder Menschen in Sicherheit in den Norden zurückkehren lassen, wenn der Krieg im Gazastreifen gestoppt werde."
- `sentence_recurs_across_articles` (no_chrome), 1 body: "Israel hat sich bislang nicht öffentlich zu den Angriffen bekannt."
- `sentence_recurs_across_articles` (no_chrome), 1 body: "Rund 3.000 weitere wurden demnach verletzt."
- `sentence_twice_in_article` (no_duplication), 1 body: "Der Iran wird von westlichen Regierungen beschuldigt, sowohl Drohnen als auch ballistische Raketen an Russland zu liefern, um sie im Krieg mit der Ukr"

Totals by type: description_is_a_later_sentence=1, sentence_recurs_across_articles=47, sentence_twice_in_article=2.

## Chrome check

Sentences of 6+ words found in 3 or more bodies of one outlet with different headlines were reviewed one by one. Page chrome that turned up was removed by container or paragraph rules, not sentence by sentence; what remains is wire or standing publisher text, listed above as `sentence_recurs_across_articles`.

## Regression diagnostic against stored v1 bodies

Diagnostic only: stored v1 bodies often hold page chrome (share bars, caption blocks, newsletter boxes, player code).

| outlet | n | median ratio | share >= 0.90 |
| --- | ---: | ---: | ---: |
| bild | 26 | 0.880 | 38.5% |
| ntv | 12 | 1.000 | 100.0% |
| rnd | 22 | 0.886 | 31.8% |
| rtl | 2 | 0.807 | 50.0% |
| spiegel | 35 | 0.783 | 17.1% |
| tagesschau | 15 | 0.973 | 86.7% |
| tonline | 46 | 0.946 | 76.1% |
| welt | 16 | 1.000 | 100.0% |
| zdfheute | 15 | 0.946 | 66.7% |

Adjudication of every record below 0.90 (`regression-adjudication.csv`): stored_wrong=79, new_wrong=0, both=0.

## Spot samples

Chosen with `random.Random(2024)` from the gap candidates that have a body.

### bild

- Marschiert Israel jetzt in den Libanon ein? Brenzlige Situation im Norden | 2024-09-21 | article | container:bild
  - first 200: Wenige Tage nach der Pieper-Attacke gegen Tausende Hisbollah-Terroristen, bei der am Dienstag und Mittwoch 37 Menschen getötet und fast 3000 durch explodierende Pager und Walkie-Talkies verletzt wurde
  - last 150: skieren, obwohl es einen totalen Krieg verhindern will. Wir wollen etwas sehr begrenztes, aber nicht das Spiel der Hisbollah mitspielen“, so Shueftan.

- Israel: Israelischer Staatsbürger plante Mord an Netanjahu | 2024-09-19 | article | container:bild
  - first 200: Ein israelischer Staatsbürger soll vom Iran für den Mord an hochrangigen Regierungsvertretern angeworben worden sein. Die Ziele: Ministerpräsident Benjamin Netanjahu, Verteidigungsminister Joav Galant
  - last 150: er viele Hisbollah-Mitglieder. Israel bekannte sich nicht zu dem Angriff, es wird aber weitgehend angenommen, dass das Land hinter der Attacke steckt.

- Hisbollah unter Druck: Israel hat Terroristen „lächerlich“ gemacht | 2024-09-22 | article | container:bild
  - first 200: Wie schwer sind die Hisbollah-Terroristen nach der Angriffswelle aus Israel getroffen? / Die israelische Luftwaffe tötete am Freitag bei Präzisionsschlägen Ibrahim Aqil (62), den Kommandeur einer Elit
  - last 150:  Hisbollah-Kämpfern nun weltweit als wahlloser Angriff auf die libanesische Bevölkerung verkauft wird, ist ein Propaganda-Erfolg für die Terroristen.“

### ntv

- Information aus Sicherheitskreisen: Blufarb: Kommunikationsabbruch schwächt Hisbollah | 2024-09-19 | video_page | meta-description-video
  - first 200: Nach den Pager-Explosionen im Libanon beginnt Israel eine neue Phase des Krieges: Das Land "macht jetzt massiv militärisch Druck", weiß ntv-Korrespondentin Raschel Blufarb. Wann und in welcher Form Is
  - last 150: . Wann und in welcher Form Israel mit einem Gegenschlag zu rechnen hat, ist unklar, doch es brauche nun "Druck der USA für eine diplomatische Lösung".

- Adresse in Budapest: Spur der explosiven Pager - wer steckt hinter BAC Consulting? | 2024-09-18 | article | container:ntv
  - first 200: Woher kamen die Tausenden Pager, die im Libanon explodiert sind? Das Logo der Geräte führt nach Taiwan, von dort aber geht es umgehend zurück nach Budapest. In der ungarischen Hauptstadt findet sich i
  - last 150: n in London tätig. Die angebliche Leiterin der Firma heißt Lea Iman, hat auf Instagram über 80.000 Follower und arbeitet offenbar als DJ und Tänzerin.

- Hisbollah-Kommandeur im Visier: Israel bombardiert erneut Vorort von Beirut | 2024-09-24 | article | container:ntv
  - first 200: Israel verstärkt seine Angriffe auf die Hisbollah und tötet einen führenden Kommandeur in Beirut. Die Eskalation der Gewalt weckt Befürchtungen eines umfassenden Krieges im Nahen Osten. Die USA forder
  - last 150: Hamas im Gazastreifen. Andererseits verweisen Insider darauf, dass die Hisbollah an einem großangelegten Krieg gegen Israel kein Interesse haben kann.

### rnd

- Israels Geheimdienst Mossad: Alles begann mit der Jagd auf Nazi-Mörder | 2024-09-19 | article | container:rnd
  - first 200: Nach dem spektakulären Schlag gegen Hisbollah-Mitglieder im Libanon zollt die Welt dem Mossad Respekt, gemischt mit Schrecken angesichts der vielen Toten und Verstümmelten. Im Dezember feiert der wohl
  - last 150: r werden sollte. Der Fall offenbarte auf drastische Weise und nicht zum letzten Mal die dunkle Seite des Mossad-Motivs „Steh auf und töte ihn zuerst“.

- Armeesprecher Hagari: Getöteter Hisbollah-Kommandeur plante Überfall auf Israel | 2024-09-21 | article | container:rnd
  - first 200: Bei dem israelischen Angriff in Beirut ist auch der Hisbollah-Militärkommandeur Ibrahim Akil getötet worden. Der hochrangigen Kommandeur wollte angeblich mit seiner Miliz in Nordisrael eindringen - äh
  - last 150: Kabinettssitzung laut anwesenden Reportern. „Wir werden so lange daran arbeiten, bis wir es geschafft haben. Wir haben noch einen weiten Weg vor uns.“

- Auftakt für einen neuen Krieg? | 2024-09-19 | article | container:rnd
  - first 200: Die Attacken auf die Hisbollah mithilfe von Funkgeräten deuten Experten als Versuch, einen Krieg zu starten. Brüssel stellt einen Plan für den ukrainischen Winter auf. Und Leverkusen hofft in Rotterda
  - last 150:  israelischen Geheimdienst organisiert wurden, gegenüber dem RND wörtlich eine „äußerst professionelle und herausragende geheimdienstliche Operation“.

### rtl

- Opferzahl im Libanon steigt | 2024-09-19 | teletext | container:rtl
  - first 200: Im Libanon ist die Zahl der Todesopfer nach den mutmaßlich von Israel koordinierten Explosionen technischer Geräte auf 37 gestiegen. Nach Angaben von Gesundheitsminister Firas Abiad sind an beiden Tag
  - last 150: ag später zahlreiche andere technische Geräte, vor allem Walkie-Talkies. Unter den Toten und Verletzten befinden sich zahlreiche Hisbollah-Mitglieder.

- Erneut Explosionen im Libanon | 2024-09-18 | teletext | container:rtl
  - first 200: Nach dem mutmaßlich von Israel koordinierten Angriff im Libanon hat es in der Hauptstadt Beirut und im Land erneut Explosionen gegeben. Sicherheitskreise bestätigten, dass Walkie-Talkies von Hisbollah
  - last 150: enstag waren an mehreren Orten im Libanon gleichzeitig hunderte Pager explodiert. Dabei wurden rund 2.800 Menschen verletzt. Mindestens zwölf starben.

- Hisbollah meldet 32 Tote | 2024-09-19 | teletext | container:rtl
  - first 200: Die Schiitenmiliz Hisbollah im Libanon hat seit der Explosion Hunderter Pager 32 Tote in den eigenen Reihen bestätigt. Die Miliz machte keine Angaben, ob die Mitglieder durch die Explosionen am Dienst
  - last 150: ht die Miliz vor einer ihrer größten Herausforderungen. / Klarheit darüber, wie viele Hisbollah-Mitglieder verletzt oder getötet wurden, gab es nicht.

### spiegel

- Die Lage am Morgen: Der unheimliche E-Krieg | 2024-09-19 | article | container:spiegel
  - first 200: Die Choreografie ist unheimlich, die Methode noch unheimlicher. Vorgestern explodierten im Libanon Pager in Tausenden Hosentaschen, neun Menschen starben, fast 3000 wurden verletzt. Sie sollen, so wir
  - last 150: ine Kündigung? Eine Expertin gibt Antworten. / Ich wünsche Ihnen einen guten Start in den Tag. / Ihr Martin Knobbe, Leiter des SPIEGEL-Hauptstadtbüros

- Attacke der Hisbollah: Israel meldet massiven Raketenbeschuss aus dem Libanon | 2024-09-20 | article | container:spiegel
  - first 200: Die Hisbollah hatte nach der Explosion Tausender Pager Rache angekündigt. Nun sind aus dem Libanon Dutzende Raketen Richtung Nordisrael abgefeuert worden. / Aus dem Libanon sind nach israelischen Mili
  - last 150: etwa 600 Menschen getötet, die meisten davon Hisbollah-Mitglieder. In Israel kamen Armeeangaben zufolge 52 Menschen ums Leben, darunter 26 Zivilisten.

- Pager-Attacke gegen Hisbollah-Mitglieder: Liebesgrüße aus Tel Aviv | 2024-09-20 | article | container:spiegel
  - first 200: Tausendfach explodierten im Libanon Pager, mutmaßlich weil der israelische Geheimdienst sie mit Sprengstoff präparierte. Die Attacke wirkt aus der Zeit gefallen wie James Bond – und war vielleicht des
  - last 150: elische Geheimdienst sie mit Sprengstoff präparierte. Die Attacke wirkt aus der Zeit gefallen wie James Bond – und war vielleicht deshalb so effektiv.

### tagesschau

- Hisbollah-Chef Nasrallah sieht "alle roten Linien überschritten" | 2024-09-19 | article | container:tagesschau
  - first 200: Nach der Explosion Hunderter Kommunikationsgeräte im Libanon hat Hisbollah-Chef Nasrallah einen schweren Schlag gegen seine Miliz eingeräumt. Er warf Israel einen kriminellen Akt vor - und sprach von 
  - last 150: plomaten der USA, Großbritanniens, Deutschlands, Frankreichs und Italiens in Paris mit dem Thema, gleichzeitig tagt der UN-Sicherheitsrat in New York.

- Rüstungsexporte nach Israel: Welche Waffen liefert Deutschland? | 2024-09-19 | article | container:tagesschau
  - first 200: Deutschland zählt zu den wichtigsten Waffenlieferanten für Israel. Trotz Protesten gibt es keinen Exportstopp. Die Rüstungsexporte sind aber deutlich zurückgegangen. / Soll Deutschland Waffen nach Isr
  - last 150: Systemen aus, die im Gazastreifen zum Einsatz kämen. Denn da bestehe - so sagt es Habeck - zumindest der Verdacht, dass Israel Völkerrecht missachtet.

- Israel und Hisbollah weiten gegenseitige Angriffe aus | 2024-09-22 | article | container:tagesschau
  - first 200: Israel und die Hisbollah beschießen sich in den mitunter schwersten Angriffen seit Beginn des Konflikts. Die Vereinten Nationen warnen vor einer Katastrophe. In der libanesischen Bevölkerung herrscht 
  - last 150: re Marschflugkörper auf Israel ab. Ein Sprecher der - wie die Hisbollah - vom Iran geförderten Milizen bezeichnete dies als Unterstützung des Libanon.

### tonline

- Israel plant schon «nächste Phasen» im Kampf gegen Hisbollah | 2024-09-24 | article | container:tonline
  - first 200: Israels heftige Bombardements im nördlichen Nachbarland sind eine neue Eskalationsstufe im Konflikt mit der Hisbollah. Viele Libanesen fliehen in Panik, Israel wappnet sich für mögliche Vergeltung. / 
  - last 150:  die Hisbollah entlang der Grenze nicht präsent sein. Dies wird aber weder von der UN-Beobachtermission noch von der libanesischen Armee durchgesetzt.

- Vom Iran für Morde rekrutiert? - Israeli festgenommen | 2024-09-19 | article | container:tonline
  - first 200: Ein jüdischer Geschäftsmann soll von Vertretern des iranischen Geheimdienstes Geld erhalten haben, um etwa Israels Ministerpräsident Netanjahu zu töten. Gegen ihn wurde nun Anklage erhoben. / In Israe
  - last 150:  als 30 Menschen getötet und mehr als 3000 weitere verletzt, darunter zahlreiche Mitglieder der Hisbollah. Israels bekannte sich nicht zu dem Angriff.

- Armeesprecher: Hisbollah plante Überfall auf Israel | 2024-09-21 | article | container:tonline
  - first 200: Der in Beirut getötete Hisbollah-Militärkommandeur Akil wollte angeblich mit seiner Miliz in Nordisrael eindringen - ähnlich wie die Hamas am 7. Oktober im Süden. Das Risiko eines neuen Kriegs steigt.
  - last 150: Kabinettssitzung laut anwesenden Reportern. "Wir werden so lange daran arbeiten, bis wir es geschafft haben. Wir haben noch einen weiten Weg vor uns."

### welt

- Hunderte Pager explodieren im Libanon - was steckt dahinter? | 2024-09-18 | wire_feed | container:welt
  - first 200: Die Szenen erinnern an Science-Fiction: Plötzlich explodieren hunderte Funkempfänger gleichzeitig an mehreren Orten im Libanon. Tausende werden verletzt. Am nächsten Tag folgt eine zweite Welle. / Hun
  - last 150: Explosion all dieser Geräte besteht natürlich darin, dies als Präventivschlag vor einer größeren Militäroperation zu tun», sagte Guterres in New York.

- Rede des US-Präsidenten bei UN-Generaldebatte: Joe Bidens Amerika verabschiedet sich | 2024-09-24 | article | container:welt
  - first 200: US-Präsident Joe Biden hat seine letzte Rede vor den Vereinten Nationen gehalten. Der 81-Jährige blickt zurück auf ein halbes Jahrhundert, in dem er die Außenpolitik der mächtigsten Nation mitgestalte
  - last 150: UN-Mitarbeiter fürchten. Joe Biden schlägt sein Kapitel zur Weltpolitik an diesem Septemberdienstag zu. Das nächste Kapitel ist eine große Unbekannte.

- Walkie-Talkie-Explosionen: „Es ist auch ein großer psychologischer Schlag gegen die Terroristen“ | 2024-09-18 | video_page | container:welt
  - first 200: „Es gibt die Diskussion, dass Israel Truppen aus dem Gaza-Streifen reduzieren muss“, sagt Nils Kottmann, Redakteur der „Jüdischen Allgemeinen“, im Interview mit Welt TV. „Die Zeit läuft für die Geisel
  - last 150: -Streifen reduzieren muss“, sagt Nils Kottmann, Redakteur der „Jüdischen Allgemeinen“, im Interview mit Welt TV. „Die Zeit läuft für die Geiseln weg.“

## What changed since round 1

The gate is the five body checks, pass rate counted over all five together (exceptions count as passes). A low ratio against a stored v1 body is a diagnostic and is classified in `regression-adjudication.csv`.
Lead check recalibrated as for Israel/Lebanon: a description whose opening words occur nowhere in the body is a rewritten teaser (pass, `description_is_rewrite`). It fails only when the words occur after the first 400 characters, and then a `publisher_exception` is recorded only if the text before them is genuine article text.
Truncation check: closing lines a publisher puts after the last sentence (contributor credits, wire source lines, URL lines, bylines, interview credits, `[Source]` tags, update stamps) are accepted; a bulleted last item without full stop is an exception with a quote; a body that is the page description is accepted unless the publisher cut it with an ellipsis (`page_truncated`).
Order check: a paragraph that occurs several times in the JSON-LD `articleBody` is matched at its first occurrence after the previous match.
Exceptions are verified in code: the quote must occur in the page's visible text or its JSON page state. Cross-page repeated sentences (6+ words, 3+ bodies, different headlines) are chrome when they match a promo pattern, otherwise `sentence_recurs_across_articles`.
Video pages are recognised by URL (`/video/`, `/videos/`, `/mediathek/`) or by a VideoObject without a full article body; their body is the page description. Podcast pages (`radio.foxnews.com`, `/podcast`) likewise.
Titles lose section or type labels the page appends (Bild `| Politik`, Welt `- Video`).
ntv (was unusable, lead_present 28/59): the page-state paragraph widget omits the bold lead text (`storyline_lead_text_leadtext`), which is the page description. The extractor now reads the rendered storyline (lead text, paragraphs, subheads) in document order; the page-state reader stays as fallback.
Spiegel (was unusable, not_truncated 59/66): the seven failures were newsletter sign-offs ("Ich wünsche Ihnen ...", "Ihr Martin Knobbe, Leiter ...") without a full stop. The extractor was right; the check now accepts sign-offs. Spiegel reads `data-area=text`/`multibox` paragraphs plus the RichText lead; paywalled SPIEGEL+ pages give the lead with `paywall: true`.
RND: newsletter call-to-action widgets (`CallToAction`, `NewsletterWidget`), "Mehr zum Thema" teaser blocks and the "Abonnieren Sie auch" footer are left out.
tagesschau: embedded teaser boxes (`teaser-absatz`, role complementary), programme info (`sendungsbezug`), image info (`absatzbild`) and the WhatsApp-channel line are left out. The teaser boxes had been the recurring sentences.
t-online: the X-embed consent layer, "Lesen Sie auch:" link lines and Tagesanbruch newsletter blurbs are left out.
WELT: "Lesen Sie auch" link labels, podcast show boilerplate and a satire footer are left out.
ZDFheute: quote cards (a `<blockquote>` inside a `<figure>`) are kept, the speaker `<figcaption>` is not.

## Judgment calls

Sub-headings are not part of the body, except for ntv (and Fox in the US). Image captions, bylines and teasers are not body.
Spiegel newsletter pages keep their sign-off ("Ihr Martin Knobbe, ..."); the line recurs across newsletter issues and is listed as `sentence_recurs_across_articles`.
t-online keeps its closing note on machine-assisted text (single occurrences).
Stored v1 bodies of bild, spiegel, rnd, tonline and zdfheute contain share bars, player code, caption blocks, +++ tickers and consent text. Every record below 0.90 was checked for stored-only sentences; the stored-only text was chrome, captions, sub-headings or spacing artefacts in all 79 cases.

## Open problems

- Live blogs are deferred (17 rows). Paywalled pages give only the lead (`paywall: true`): Spiegel 7, Bild 1, WELT 1.
- A one-off promo or footer that occurs in fewer than 3 bodies cannot be found automatically; the automatic chrome check only sees recurring text.
