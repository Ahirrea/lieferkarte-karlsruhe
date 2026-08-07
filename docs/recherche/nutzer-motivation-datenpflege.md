# Recherche: Wie motiviert man Nutzer einer Karten-App zur Pflege der Restaurantdaten?

> **Recherche vom 2026-08-07.** Input für eine mögliche Anforderung nach
> [docs/PROZESS.md](../PROZESS.md) — **keine Anforderung, keine Entscheidung.**
> Optionen sind mit Belegen aufgeführt; nichts davon ist beschlossen.
>
> **Richtungsentscheidung vom 2026-08-07** (Produktverantwortliche, nach dieser
> Recherche): Der Kanal ist die **OSM-Notiz, strikt accountfrei**. Der Deep-Link
> zu MapComplete ist verworfen — dort registrieren bzw. eine App laden ist zu
> aufwendig, wenn es um schnelles, einfaches Pflegen geht. In Kauf genommen:
> das Abarbeiten der Notiz übernimmt die OSM-Community, nicht die meldende
> Person. Die Verfeinerung zur Anforderung steht noch aus (A-9 in der
> [Übersicht](../anforderungen/README.md)).

## Forschungsfrage

Wie können Nutzer der Lieferkarte Karlsruhe motiviert werden, die Restaurantdaten
zu pflegen — konkret die OSM-Tags `delivery`, `takeaway`, `opening_hours` und
`cuisine`?

Rahmenbedingungen des Projekts (bindend, siehe [PRD](../PRD.md),
[ADR-001](../entscheidungen/ADR-001-openstreetmap-statt-google-places.md),
[ADR-007](../entscheidungen/ADR-007-standardfilter-liefert-jetzt.md)): kein Backend,
keine Accounts, keine Cookies, kein Tracking. Die App kann selbst keine Edits
speichern — Datenpflege heißt zwingend, dass der Nutzer OpenStreetMap selbst
editiert (oder dort eine Notiz hinterlässt) und die Änderung erst nach dem
nächsten wöchentlichen Scan in der App erscheint (Latenz bis zu 7 Tage).
Datenlage: ~87,5 % der Restaurants ohne `delivery`-Tag („unbekannt"), 143 von
885 ohne `opening_hours`. Zielgruppe: Karlsruher Laien, keine OSM-Mapper.

## Quellenlage und Kennzeichnung

- **(P)** = Primärquelle direkt eingesehen (Originalstudie/Abstract der
  Zeitschriftenseite, Quellcode, offizielle Doku/API des Projekts, das die
  Aussage besitzt).
- **(A)** = nur Abstract bzw. Verlagszusammenfassung eingesehen, Volltext nicht
  geprüft.
- **(S)** = Sekundärquelle oder nicht vollständig verifizierbar; entsprechend
  vorsichtig formuliert.

Wörtliche Zitate stehen in der Originalsprache (Englisch), wo die Quelle
englisch ist.

---

## Kernbefunde

### 1. OSM-Contributor-Forschung: Gemeinwohl, „personal but shared need" und lokales Wissen sind die Hauptmotive

Budhathoki & Haythornthwaite befragten 444 OSM-Beitragende zu 39 möglichen
Beitragsmotiven. Als wichtigste Motivatoren identifizierten sie den Beitrag zum
Allgemeinwohl, das Muster des „personal but shared need" aus der
Open-Source-Forschung (ich brauche die Daten selbst — und teile sie), die
Affinität zu Open Source und geographischem Wissen sowie die Teilhabe an der
Community. **(A)** — Abstract und Verlagsangaben der Zeitschriftenseite
eingesehen: Budhathoki, N. R. & Haythornthwaite, C. (2013): *Motivation for
Open Collaboration: Crowd and Community Models and the Case of OpenStreetMap.*
American Behavioral Scientist 57(5), S. 548–575,
[DOI 10.1177/0002764212469364](https://journals.sagepub.com/doi/10.1177/0002764212469364).

Die Studie unterscheidet **„serious mappers" und „casual mappers"** mit
unterschiedlichen Motivprofilen: Für ernsthafte Mapper wiegen
Community-Teilhabe, Lernen und lokales Wissen schwerer; Gelegenheits-Mapper
sind stärker vom Grundsatz freier Kartendaten getrieben und weniger
community-orientiert; Karriere-Motive sind in beiden Gruppen schwach. **(A/S)**
— diese Gruppendifferenzierung stammt aus der Verlagszusammenfassung bzw. der
[ResearchGate-Seite](https://www.researchgate.net/publication/258122986_Motivation_for_Open_Collaboration_Crowd_and_Community_Models_and_the_Case_of_OpenStreetMap)
zur Studie; der Volltext wurde nicht eingesehen.

Einordnung für dieses Projekt: Die Zielgruppe der Lieferkarte entspricht am
ehesten den *casual mappers* — die laut Studie gerade **nicht** über
Community-Bindung erreicht werden, sondern über den Nutzen freier Daten und den
eigenen Bedarf. „Ich will selbst wissen, wer jetzt liefert" ist exakt ein
„personal but shared need".

### 2. Wikipedia-Forschung: Spaß und Ideologie schlagen Karriere und Soziales

Nov befragte 151 Wikipedianer (von 370 angeschriebenen) entlang von acht
Motivkategorien (Protective, Values, Career, Social, Understanding,
Enhancement, Fun, Ideology). Die stärksten Motive waren **Fun und Ideologie**
(freies Wissen); Social-, Karriere- und Schutzmotive waren nachrangig. **(A)** —
Nov, O. (2007): *What Motivates Wikipedians?* Communications of the ACM 50(11),
S. 60–64, [DOI 10.1145/1297797.1297798](https://dl.acm.org/doi/10.1145/1297797.1297798);
Volltext nicht eingesehen, Angaben aus Abstract/[CACM-Seite](https://cacm.acm.org/magazines/2007/11/5534-what-motivates-wikipedians/abstract).

Einordnung: Deckt sich mit Befund 1 — die niederschwellige Beteiligung läuft
über „macht Spaß, ist schnell erledigt" und „freie Daten für alle", nicht über
Reputation oder Karriere. Beides lässt sich ohne Accounts adressieren.

### 3. Citizen-Science-Forschung: Die Mehrheit sind „Dabbler" — Kleinsthäppchen und Feedback zum Wert des Beitrags sind die Design-Hebel

Eveleigh et al. untersuchten das Citizen-Science-Projekt Old Weather (Survey +
Interviews über alle Beitragsniveaus). Kernaussagen aus dem Abstract
(wörtlich): *„In most online citizen science projects, a large proportion of
participants contribute in small quantities."* Vielbeitragende waren *„deeply
engaged by social or competitive features"*, Wenigbeitragende beschrieben
dagegen *„a solitary experience of 'dabbling' in projects for short periods"*.
Empfohlene Designkonsequenz (wörtlich): *„breaking the work into components
which can be tackled without a major commitment of time and effort, and
providing feedback on the quality and value of these contributions."* **(P für
das Abstract)** — Eveleigh, A., Jennett, C., Blandford, A., Brohan, P. & Cox,
A. L. (2014): *Designing for dabblers and deterring drop-outs in citizen
science.* CHI 2014,
[DOI 10.1145/2556288.2557262](https://dl.acm.org/doi/10.1145/2556288.2557262)
(Abstract über die Semantic-Scholar-API verifiziert; Volltext-PDF der
[UCL](https://discovery.ucl.ac.uk/1418573/1/p2985-eveleigh.pdf) war abrufbar,
konnte in dieser Umgebung aber nicht gerendert werden).

Einordnung: Wettbewerbs- und Sozialfeatures wirken auf die *Kerngruppe* — die
dieses Projekt gar nicht ansprechen kann (keine Accounts). Die für die
Lieferkarte relevante Mehrheit („Dabbler") braucht stattdessen: eine einzelne,
in Sekunden erledigbare Aufgabe und eine Rückmeldung, dass der Beitrag etwas
wert war.

### 4. Self-Determination-Theorie: Autonomie und Kompetenz tragen auch ohne Community

Die SDT (Ryan & Deci 2000) benennt drei psychologische Grundbedürfnisse hinter
intrinsischer Motivation: **Autonomie, Kompetenz, soziale Eingebundenheit**
(relatedness). **(P)** — Ryan, R. M. & Deci, E. L. (2000): *Self-Determination
Theory and the Facilitation of Intrinsic Motivation, Social Development, and
Well-Being.* American Psychologist 55(1),
[PDF bei selfdeterminationtheory.org](https://selfdeterminationtheory.org/SDT/documents/2000_RyanDeci_SDT.pdf).

Eine aktuelle Anwendung auf Online-Citizen-Science (Zooniverse-Survey) fand:
Teilnahme hängt primär mit der *Befriedigung* der Bedürfnisse zusammen;
**„Autonomy is the most supported need and relatedness the least"** (wörtlich
aus dem Abstract) — d. h. die Teilnahme funktioniert dort auch, obwohl die
soziale Eingebundenheit am schwächsten bedient wird. **(P für das Abstract)** —
Dowthwaite, L., Spence, A., Lintott, C., Miller, G., Sprinks, J., Blickhan, S.
& Houghton, R. (2024): *Exploring the Relationship between Basic Psychological
Needs and Motivation in Online Citizen Science.* ACM Transactions on Social
Computing 8(1–2), [DOI 10.1145/3702210](https://dl.acm.org/doi/10.1145/3702210).

Einordnung: Das ist die gute Nachricht für ein Produkt ohne Community-Features:
Autonomie („ich entscheide, ob und was ich beitrage") und Kompetenz („ich weiß
etwas über mein Viertel, das der Karte fehlt" — Selbstwirksamkeit) sind die
beiden Bedürfnisse, die eine reine Verlink-Lösung bedienen kann. Eingebundenheit
fällt weg — laut der Zooniverse-Studie das am wenigsten tragende der drei.

### 5. StreetComplete: Das Ein-Frage-Modell ist das Referenzdesign für Laien-Datenpflege — und es fragt `opening_hours`, aber bewusst weder `cuisine` noch `delivery`/`takeaway`

StreetComplete (Android) zeigt offene Datenlücken als „Quests" auf der Karte
und stellt pro Quest genau **eine** Frage in Alltagssprache; die Antwort wird
sofort als Edit ins OSM-Konto des Nutzers hochgeladen. Ziel laut README:
Beiträge von Menschen ermöglichen, *„who do not know anything about OSM tagging
schemes but still want to contribute"*. **(P)** —
[README](https://github.com/streetcomplete/StreetComplete/blob/master/README.md).

Die [Quest-Guidelines](https://github.com/streetcomplete/StreetComplete/blob/master/QUEST_GUIDELINES.md)
**(P)** definieren, was eine gute Frage ausmacht (Auswahl, wörtlich):

- *„Per quest, only **one** thing should need to be answered by the user."*
- *„No knowledge about OpenStreetMap or any other background knowledge must be necessary."*
- *„A quick, straightforward and clear answer must be possible."*
- *„All generated quests need to be actually answerable (no false-positives)."*
- Die Information muss von außen, als Passant, erhebbar sein; Fragen, die zu
  99 % dieselbe Antwort ergeben, gelten als Spam am Nutzer.

**Konkrete Frageformulierungen** (P — aus den Sprachdateien im Repo,
`app/src/commonMain/composeResources/values/strings.xml` bzw. `values-de/`):

| Quest | Englisch | Deutsch |
|---|---|---|
| Öffnungszeiten | „What are the opening hours here?" | „Was sind die Öffnungszeiten von diesem Ort?" |
| Öffnungszeiten ausgeschildert? | „Are the opening hours here signed?" | „Sind die Öffnungszeiten dieses Ortes ausgeschildert?" |
| Re-Survey | „Are these opening hours still correct?" | „Stimmen diese Öffnungszeiten noch?" |
| Vegetarisch | „Any vegetarian items on the menu here?" | — |
| Vegan | „Any vegan items on the menu here?" | — |

Bemerkenswert: Es gibt eine eigene Vorfrage „sind die Öffnungszeiten überhaupt
ausgeschildert?" — das Design plant den Fall „Nutzer kann es nicht wissen"
explizit ein, statt eine Antwort zu erzwingen. Veraltbare Angaben wie
Öffnungszeiten werden periodisch erneut zur Bestätigung vorgelegt (Re-Survey-Quest;
siehe auch [OSM-Wiki zu StreetComplete](https://wiki.openstreetmap.org/wiki/StreetComplete), **P/S**).

**Was StreetComplete *nicht* fragt:** Im Quest-Verzeichnis des Repos
(`app/src/androidMain/kotlin/de/westnordost/streetcomplete/quests/`, 142
Quest-Pakete, per GitHub-Git-Tree-API geprüft, **P**) existiert `diet_type`
(vegetarisch/vegan/halal/koscher/glutenfrei), aber **kein Quest für `cuisine`,
`takeaway` oder `delivery`**. Das passt zu den eigenen Guidelines: `cuisine`
ist eine offene Mehrfachauswahl mit Einordnungsspielraum („ist das jetzt
`turkish` oder `kebab`?") und von außen oft nicht eindeutig erhebbar;
`delivery` ist als Angebot von der Straße aus überhaupt nicht ablesbar. Eine
explizite Maintainer-Begründung je Tag wurde nicht gefunden **(offen, s. u.)**
— die Abwesenheit selbst ist aber im Code verifiziert. Konsequenz für dieses
Projekt: Gerade die zwei wichtigsten Tags der Lieferkarte (`delivery`,
`takeaway`) sind *keine* Passanten-Fragen, sondern **Insider-Wissen von Gästen
und Bestellern** — also genau von der Nutzergruppe dieser App.

### 6. StreetComplete-Gamification: bewusst dosiert — Belohnung ja, Wettbewerb nein

StreetComplete hat seit v19.0 Achievements mit Leveln; erreichte Achievements
schalten Links frei, die den Nutzer an OSM-Projekte heranführen. **(P/S)** —
[OSM-Wiki StreetComplete](https://wiki.openstreetmap.org/wiki/StreetComplete).
Die Designziele formulierte der Maintainer (westnordost/Tobias Zwick) im
Design-Issue selbst: Achievements sollen *„give users some gratification and
thus keep users active longer"*, *„introduce users to OSM"* und *„showcase how
the data contributed is used"*. **(P)** —
[Issue #1715](https://github.com/streetcomplete/StreetComplete/issues/1715).
Ein Zähler gelöster Quests mit Sternsymbol gehört zur Oberfläche (Icons
`ic_star_*.xml` im Repo, **P**; Detailmechanik nicht weiter verifiziert).

Zugleich begrenzt das Projekt Gamification bewusst: Die
[FAQ](https://wiki.openstreetmap.org/wiki/StreetComplete/FAQ) **(P/S,
sinngemäß)** begründet das mit Datenqualität — mehr Wettbewerb korreliere mit
schlampigerem Erheben (etwa pauschale Antworten für ganze Straßenzüge ohne
Vor-Ort-Prüfung). In früheren Diskussionen wird die Sorge zitiert, mehr
Gamification ziehe Nutzer an, denen das „Spiel" wichtiger ist als korrekte
Daten **(S** — aus Suchtreffern zu Maintainer-Aussagen; exakte Fundstelle nicht
gesichert**)**.

Einordnung: Selbst das erfolgreichste Gamification-Beispiel im OSM-Umfeld setzt
auf *Belohnung und Sinnvermittlung*, nicht auf Ranglisten — und warnt vor
Wettbewerb als Qualitätsrisiko. Für die Lieferkarte sind persönliche
Achievements ohnehin unmöglich (keine Accounts, kein localStorage), aber die
beiden übertragbaren Kernideen sind account-los machbar: *zeigen, wie die Daten
genutzt werden* (die Karte selbst tut das) und *kollektiven Fortschritt sichtbar
machen* (z. B. „x von 885 Restaurants haben ein Liefer-Tag").

### 7. MapComplete: Web-Editor ohne eigenes Backend — fragt exakt die vier Tags dieses Projekts und ist pro Restaurant verlinkbar

MapComplete ist eine statische Web-App (wie die Lieferkarte ohne eigenes
Backend), die thematische OSM-Karten zeigt und Laien per Frage-Antwort-Flow
editieren lässt; Nutzer melden sich per **OSM-OAuth** direkt gegen
openstreetmap.org an, Edits gehen ohne Zwischenserver an die OSM-API. **(P)** —
[README](https://github.com/pietervdvn/MapComplete/blob/master/README.md).
Fähigkeiten werden progressiv freigeschaltet (Punkte hinzufügen erst nach
ersten Antworten; eigene Themes ab 50 Changesets usw.), d. h. auch dort wird
der Einstieg bewusst klein gehalten.

Das Theme **`food`** („Restaurants and fast food") fragt genau die Tags dieser
Recherche ab **(P** — Layer-Definition
[assets/layers/food/food.json](https://github.com/pietervdvn/MapComplete/blob/develop/assets/layers/food/food.json)**)**:

- „What kind of food is served here?" → `cuisine`
- „Does this place offer take-away?" → `takeaway`
- „Does {title()} deliver food to your home?" → `delivery`
- „Does this restaurant have a vegetarian option?" → `diet:vegetarian` (u. a.)
- Öffnungszeiten über den eingebauten `opening_hours`-Baustein.

**Deep-Links und Einbettung** **(P** —
[Docs/URL_Parameters.md](https://github.com/pietervdvn/MapComplete/blob/develop/Docs/URL_Parameters.md)**)**:
Theme im Pfad, Position per `lat`/`lon`/`z`, **ein konkretes Objekt per
Hash-Fragment** — z. B.
`https://mapcomplete.org/food?lat=49.0069&lon=8.4037&z=18#node/12345` öffnet
das Restaurant direkt im Editor-Popup. Dazu `language=…` und `fs-*`-Parameter
für iframe-Einbettung (u. a. `fs-enable-login` für einen Read-only-Modus).

Einordnung: Da die Lieferkarte `place_id` als `type/id` (z. B. `node/12345`)
speichert, ist der MapComplete-Deep-Link pro Restaurant **aus den vorhandenen
Daten konstruierbar** — ein Ein-Klick-Weg vom Popup „Lieferung: unbekannt" zum
Formular, das genau diese Frage in Laiensprache stellt. Voraussetzung bleibt
ein (kostenloses) OSM-Konto für den Edit selbst.

### 8. Komplett ohne Account geht nur eines: die OSM-Notiz — und sie ist der niederschwelligste, aber umstrittenste Kanal

**Notiz anlegen geht anonym.** Im Quellcode der OSM-Website hat die
Create-Action nur `setup_user_auth` (optionale Anmeldung), nicht `authorize`
(Pflicht-Anmeldung); anonyme Erstellung wird lediglich per IP-Sperrliste
gefiltert: `raise OSM::APIAccessDenied if current_user.nil? &&
Acl.no_note_comment?(request.remote_ip)`. Kommentieren, Schließen, Wiederöffnen
erfordern dagegen `authorize`, also ein Konto. **(P)** —
[app/controllers/api/notes_controller.rb](https://github.com/openstreetmap/openstreetmap-website/blob/master/app/controllers/api/notes_controller.rb);
API-Endpunkt `POST /api/0.6/notes` laut
[API-v0.6-Wiki](https://wiki.openstreetmap.org/wiki/API_v0.6). Auf der Website
existiert die Route `/note/new` (**P** —
[config/routes.rb](https://github.com/openstreetmap/openstreetmap-website/blob/master/config/routes.rb)),
kombinierbar mit einem `#map=zoom/lat/lon`-Fragment zum Positionieren.

**Anonyme *Kommentare* wurden 2019 abgeschaltet** — Begründung von Frederik
Ramm (OSMF/Operations) am 29.08.2019: Anonyme Kommentare seien *„rarely
useful"*, und massiver Spam/Vandalismus habe das Notes-System regional nahezu
unbrauchbar gemacht; neue anonyme Notizen zu bekämpfen sei leichter als
anonyme Kommentare aufzuräumen. **(P)** —
[Ankündigung auf der talk-Liste](https://lists.openstreetmap.org/pipermail/talk/2019-August/083209.html).
Bis heute läuft eine Community-Debatte, ob anonyme Notizen ganz abgeschafft
gehören („[We don't need anonymous notes](https://community.openstreetmap.org/t/we-dont-need-anonymous-notes/105335)",
**S**). Das [Notes-Wiki](https://wiki.openstreetmap.org/wiki/Notes) **(P/S)**
nennt als Qualitätsmaßstab konkrete, vor Ort verifizierbare Texte („this shop
is closed and does not exist anymore") und warnt vor vagen oder trivialen
Notizen.

**Direktes Editieren erfordert immer ein Konto.** Die Editor-Deep-Link-Route
`openstreetmap.org/edit?editor=id&node=<id>` existiert, aber `site#edit` ruft
`require_user` auf — ohne Login landet man auf der Anmeldeseite. **(P)** —
[app/controllers/site_controller.rb](https://github.com/openstreetmap/openstreetmap-website/blob/master/app/controllers/site_controller.rb).
Der iD-Editor selbst dokumentiert seine URL-Parameter (`#map=zoom/lat/lon`,
`#id=n<id>`, `#comment=…`, `#hashtags=…`, `#source=…`) in
[API.md](https://github.com/openstreetmap/iD/blob/develop/API.md) **(P)** — für
Laien ist iD aber ein voller Editor mit Tagging-Oberfläche, kein
Frage-Antwort-Flow.

### 9. Feedback-Latenz: Das OSM-Ökosystem ist auf Minuten-Feedback gebaut; direkte Studienevidenz „sofortige Sichtbarkeit = Motivator" fehlt, Indizien gibt es

- **OSM selbst ist schnell:** Overpass-Instanzen laufen dem Hauptdatenbestand
  nur *„a couple of minutes"* hinterher **(P** —
  [Overpass-API-Wiki](https://wiki.openstreetmap.org/wiki/Overpass_API)**)**;
  ein Edit ist auf openstreetmap.org sofort im Objekt und binnen Minuten in der
  Karte sichtbar. StreetComplete lädt jede Antwort **sofort** hoch und lässt
  den Quest-Marker unmittelbar verschwinden **(P** — README**)**.
- **Dass Nutzer sichtbares Ergebnis erwarten, zeigt sich indirekt:** Die
  StreetComplete-FAQ muss eigens erklären, dass der *Karten-Hintergrund* der
  App (externe Vektortiles) erst nach ~4 Tagen aktualisiert — eine
  Standard-Nutzerfrage, sonst stünde sie nicht in der FAQ. **(P/S** —
  [FAQ](https://wiki.openstreetmap.org/wiki/StreetComplete/FAQ)**)**
- **Forschungsseitig** ist der nächstliegende Beleg Eveleigh et al. (Befund 3):
  *„providing feedback on the quality and value of these contributions"* als
  explizite Designempfehlung für Gelegenheitsbeitragende; die SDT (Befund 4)
  erklärt den Mechanismus (Kompetenz-Feedback). **Eine kontrollierte Studie,
  die speziell *sofortige* Sichtbarkeit der eigenen Kartenänderung als
  Motivator isoliert, wurde nicht gefunden** — das ist eine Evidenzlücke, keine
  Widerlegung.

Einordnung: Die 7-Tage-Latenz der Lieferkarte ist real, betrifft aber nur die
*eigene App*. Der Edit bzw. die Notiz ist auf openstreetmap.org (und in
MapComplete) **sofort** sichtbar — der Feedback-Moment lässt sich also
auslagern: Bestätigung dort, wo sie sofort passiert, plus ehrliche Ansage
„in dieser Karte ab dem nächsten Sonntags-Scan". Der vorhandene
„Diese Woche neu"-Feed ist zudem ein natürlicher Ort, an dem der eigene
Beitrag eine Woche später *namentlich als Änderung* wieder auftaucht
(`DELIVERY_CHANGED`, `TAKEAWAY_CHANGED` werden bereits geloggt und exportiert —
Projektfakt, siehe [TECHNICAL.md](../TECHNICAL.md)).

---

## Was davon passt auf die Constraints dieses Projekts — und was nicht

### Anwendbar ohne Backend, ohne Accounts

1. **Deep-Links statt eigener Edit-Funktion.** Alle drei Kanäle sind reine
   URLs und damit mit einer statischen PWA kompatibel; die App speichert und
   sammelt nichts:
   - **OSM-Notiz** (`openstreetmap.org/note/new#map=19/<lat>/<lon>`): einziger
     Kanal **ganz ohne Konto** (Befund 8). Niedrigste Hürde, aber
     unstrukturierter Freitext, dessen Qualität die lokale Mapper-Community
     tragen muss — die App sollte den Nutzer zu konkreten Formulierungen
     anleiten (Notes-Wiki-Maßstab), sonst produziert sie genau die Notizen,
     über die die Community streitet.
   - **MapComplete-Food-Theme pro Restaurant**
     (`mapcomplete.org/food?lat=…&lon=…&z=18#<place_id>`): fragt exakt
     `delivery`, `takeaway`, `cuisine`, `opening_hours` in Laiensprache
     (Befund 7); erfordert ein kostenloses OSM-Konto (OAuth), ist dafür ein
     echter, sofort wirksamer Edit. `place_id` liegt im Datenmodell bereits im
     benötigten Format vor.
   - **iD-Editor-Link** (`openstreetmap.org/edit?editor=id&node=…`): technisch
     vorhanden, für die Laien-Zielgruppe aber ungeeignet (Konto + voller
     Editor, Befund 8) — höchstens als „für Fortgeschrittene"-Link.
2. **Fragen nach StreetComplete-Vorbild formulieren** (Befund 5): eine Frage
   pro Interaktion, keine OSM-Begriffe, „weiß nicht / nicht ausgeschildert" als
   legitime Antwort. Die deutschen SC-Formulierungen („Was sind die
   Öffnungszeiten von diesem Ort?") sind erprobte Vorlagen für Hinweistexte im
   Popup. Wichtig ist die SC-Erkenntnis umgekehrt gelesen: `delivery` und
   `takeaway` sind *nicht* von der Straße erhebbar — aber Gäste und Besteller
   wissen es. Die Lieferkarte erreicht genau diese Wissensträger im richtigen
   Moment (Nutzer schaut gerade auf dieses Restaurant, Popup zeigt
   „unbekannt").
3. **Selbstwirksamkeit und Gemeinwohl ansprechen, nicht Pflichtgefühl**
   (Befunde 1, 2, 4): „Du kennst dein Viertel — die Karte noch nicht" adressiert
   Kompetenz und lokales Wissen; „frei für alle, © OpenStreetMap" adressiert
   das Ideologie-/Gemeinwohlmotiv, das bei Casual-Beitragenden trägt. Beides
   braucht weder Konto noch Community-Funktion.
4. **Kollektiven Fortschritt statt persönlicher Punkte zeigen** (Befunde 3, 6):
   ein aus den geladenen Daten berechneter Stand („bei x von 885 Restaurants
   ist bekannt, ob sie liefern") ist account-lose Gamification light und
   deckt sich mit der bestehenden Projektregel, Anteile im UI aus den Daten zu
   berechnen statt sie in Strings einzubacken. Der wöchentliche Scan macht den
   Balken sogar von selbst wachsen.
5. **Feedback-Moment auslagern und Latenz ehrlich benennen** (Befund 9): Der
   Edit/die Notiz ist bei OSM sofort sichtbar; die App kann dorthin verlinken
   und muss die eigene Verzögerung explizit machen („erscheint hier nach dem
   nächsten wöchentlichen Scan, spätestens Sonntag"). Der „Diese Woche
   neu"-Feed schließt die Schleife eine Woche später — der eigene Beitrag
   taucht dort als Änderung wieder auf.

### Nicht anwendbar / fällt weg

- **Persönliche Achievements, Sterne, Level, Streaks** (Befunde 3, 6): brauchen
  gespeicherten Nutzerzustand — Accounts und `localStorage` sind
  ausgeschlossen. URL-Parameter tragen nur ephemeren Filterzustand, keinen
  Verlauf.
- **Leaderboards/Wettbewerb**: technisch unmöglich (kein Backend) und laut
  StreetComplete-Erfahrung sogar ein Datenqualitätsrisiko (Befund 6) — der
  Wegfall ist verschmerzbar, weil Wettbewerb ohnehin nur die Kerngruppe bindet
  (Befund 3), nicht die Dabbler-Zielgruppe.
- **Community-/Sozialfeatures** (Kommentare, Profile, Teams): unmöglich ohne
  Backend; laut Befund 4 das am wenigsten tragende der drei SDT-Bedürfnisse in
  vergleichbaren Kontexten.
- **Sofortige Sichtbarkeit in der eigenen App**: prinzipbedingt nicht ohne
  Architekturänderung (z. B. Live-Overpass-Abfragen), die dem
  Wochen-Batch-Design und ADR-003/ADR-006 widerspräche. Nicht Teil dieser
  Recherche, sie zu empfehlen.
- **Eigenes In-App-Formular, das die Notes-API direkt anspricht** (`POST
  /api/0.6/notes` anonym aus dem Browser): wäre theoretisch backend-frei, ist
  aber ungeprüft (CORS? Spam-Verantwortung? IP geht an OSM statt nur an den
  Tile-Server) und berührt das Produktversprechen mindestens auf der
  Datenschutz-Erklärungsebene — als offene Frage geführt, nicht als Option
  empfohlen.

## Offene Fragen

1. **CORS/Policy der Notes-API für anonyme Browser-POSTs**: Ob ein anonymes
   `POST /api/0.6/notes` direkt aus einer fremden Web-App zulässig und
   community-verträglich wäre, wurde nicht geprüft (technisch wie
   OSM-Etikette). Ohne Prüfung bleibt nur der `note/new`-Link.
2. **Vorbefüllung**: Für `note/new` ist keine Text-Vorbefüllung per URL
   dokumentiert; ob sich der Notiztext (z. B. „Liefert dieses Restaurant?
   Restaurant X, node/…") übergeben lässt, ist offen. Für iD sind
   `#comment`/`#hashtags` dokumentiert, betreffen aber den Changeset, nicht die
   Bedienführung.
3. **MapComplete auf Deutsch**: Der `language`-Parameter ist dokumentiert;
   Umfang und Qualität der deutschen Übersetzung des Food-Themes wurden nicht
   im Einzelnen verifiziert.
4. **Maintainer-Begründung je fehlendem SC-Quest**: Dass StreetComplete
   `cuisine`/`delivery`/`takeaway` nicht fragt, ist im Code verifiziert; eine
   explizite Issue-Diskussion mit Begründung pro Tag wurde nicht gefunden.
5. **Evidenzlücke Feedback-Latenz**: Keine gefundene Studie isoliert *sofortige*
   Sichtbarkeit von Kartenedits als Motivator; die Empfehlung „Feedback geben"
   ist gut belegt (Eveleigh 2014, SDT), die zulässige Verzögerung nicht.
6. **Budhathoki-Volltext**: Die Casual-vs.-Serious-Differenzierung sollte vor
   einer darauf gestützten Anforderung am Volltext geprüft werden (nur
   Abstract/Zusammenfassungen eingesehen).
7. **Wie viele Lieferkarten-Nutzer haben ein OSM-Konto?** Vermutlich fast
   keine — das relativiert jeden Kanal außer der anonymen Notiz und wäre bei
   einer Verfeinerung als Annahme explizit zu machen (messen lässt es sich
   ohne Tracking nicht).
