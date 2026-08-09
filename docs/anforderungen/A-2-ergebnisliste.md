# A-2 Ergebnisliste neben der Karte (R6, R13)

[← Anforderungen](./README.md) · [Prozess](../PROZESS.md)
· Status siehe [Übersicht](./README.md#übersicht)

**User Story:** Als Nutzerin, die per Tastatur, Screenreader oder einfach ohne
Antippen wissen will, wer jetzt liefert, möchte ich dieselben gefilterten
Restaurants als Liste mit Entfernung und Zustand in Worten, um nicht auf 884
gleich benannte Kartenpunkte angewiesen zu sein.

**Verfeinert am:** 2026-08-09
**Bedient PRD:** „Ziele" — im eigenen Umkreis suchbar · „Kernschleife" Schritt 2
und 3 (Umkreis verengen, dann direkt zum Restaurant) · „Erfolgskriterien" —
unter 30 Sekunden zum bestellbaren Restaurant
**Eingeschränkt durch:** [ADR-008](../entscheidungen/ADR-008-karte-im-vollbild-overlay-und-sheets.md)
(zwei Layout-Pfade, Bedienzeile auf drei Elemente fest, Sheet-Zustand flüchtig)
· [ADR-011](../entscheidungen/ADR-011-pins-wieder-einheitlich.md) (Pin-Achsen
geschlossen) · [ADR-007](../entscheidungen/ADR-007-standardfilter-liefert-jetzt.md)
(„unbekannt" ist nie „nein") · [ADR-009](../entscheidungen/ADR-009-farbrollen-marke-aktion-zustand.md)
(Farbrollen, Farbe nie allein) · [ADR-002](../entscheidungen/ADR-002-kein-backend-daten-im-repo.md)
(kein Build-Schritt) · neu: [ADR-013](../entscheidungen/ADR-013-ergebnisliste-ist-der-barrierefreie-hauptweg.md)

## Ausgangstext (aus `backlog/IDEEN.md`, Idee 2)

> Die Karte ist für Tastatur und Screenreader leer: die `L.marker(…)` tragen kein
> `alt`/`title`, die Popup-Inhalte existieren nur im Marker. Vorschlag: dieselben
> gefilterten Daten zusätzlich als schlichte `<ul>` unter bzw. neben der Karte.
> Löst gleichzeitig „was ist in der Nähe?" und macht „In meiner Nähe" nach
> Entfernung sortierbar. Offen ist die Struktur – wo die Liste sitzt und ob sie
> auf Mobil einklappbar ist.

**Zwei Aussagen sind widerlegt, eine ist untertrieben** (alles am 2026-08-09
gegen echtes Leaflet 1.9.4 gemessen, Chromium, echte `web/restaurants.json` mit
884 Restaurants):

- ~~„für Tastatur und Screenreader leer"~~ → **das Gegenteil.** Alle 884 Marker
  sind fokussierbar (`tabindex="0"`, `role="button"`), `Enter` öffnet das Popup.
  Die Karte stellt **884 von 894 Tab-Stopps (98,9 %)**.
- ~~„tragen kein `alt`/`title`"~~ → `title` stimmt, `alt` nicht: Leaflet setzt
  `alt="Marker"` — bei allen 884 identisch. Das ist nicht „kein Name", sondern
  884-mal derselbe.
- „die Popup-Inhalte existieren nur im Marker" → **schlimmer als beschrieben.**
  Leaflets `popupPane` liegt im DOM hinter dem `markerPane`: vom fokussierten
  Marker bis zum Inhalt seines eigenen, gerade geöffneten Popups sind es **884
  Tabs** (im Standardfilter 53). Der Link „Zur Website & bestellen" — Schritt 3
  der Kernschleife — ist per Tastatur praktisch unerreichbar.

Der Ausgangstext stammt aus der Zeit vor A-1, A-3, A-4 und A-5. Die dort
angenommene Oberfläche („`<ul>` unter der Karte") gibt es nicht mehr: unter
640 px ist die Karte seit A-3 das Vollbild, und die Sheet-Mechanik, die A-2
erben soll, existiert bereits.

## Andockpunkte im Code

| Ort | Was dort steht | Rolle für A-2 |
|---|---|---|
| `web/index.html:1671` `render()` | Filterschleife, hängt Marker, ruft `updateCount()` | **der Eingriffspunkt.** Die Treffer werden gesammelt statt nur gezählt und danach an die Liste gegeben. |
| `web/index.html:1712` | `L.marker([r.lat, r.lng]).bindPopup(…)` | bekommt `{ keyboard: false, alt: "" }` — die einzige Änderung an der Karte selbst ([ADR-013](../entscheidungen/ADR-013-ergebnisliste-ist-der-barrierefreie-hauptweg.md)). Aussehen unberührt (ADR-011). |
| `web/index.html:1515` `SHEETS` · `:1524` `openSheet()` · `:1537` `closeSheet()` · `:1564` `initSheetDrag()` | Sheet-Mechanik für Filter und Feed | **wird wiederverwendet**, dritter Nutzer wie in ADR-008 vorgesehen. Braucht dieselbe Breiten-Ausnahme, die `filter` schon hat. |
| `web/index.html:1603` `applyLayout()` | schaltet `#filterPanel` zwischen Sheet und Inline | Muster für die Liste: `role="dialog"` nur im schmalen Pfad, Sichtbarkeit sonst über die Media Query. |
| `web/index.html:1480` `focusPlace(placeId)` | zentriert die Karte, öffnet ein `L.popup` an den Koordinaten | **wird der Klickpfad der Liste** — funktioniert schon heute ohne Marker und damit auch mit A-6. |
| `web/index.html:895` `#mapControls` | ein Knopf („In meiner Nähe"), Geschwister von `#map` | bekommt den **zweiten** Knopf („☰ Liste"). Die Bedienzeile darf ihn nicht aufnehmen (Messung unten). |
| `web/index.html:983` `measureChrome()` | setzt `--footer-h`, `--kopf-h` | bekommt `--liste-b` (gemessene Panelbreite), damit `#mapControls` und `#feed` dem Panel ausweichen. |
| `web/index.html:1329` `popupHtml()` · `:1063` `cuisinesOf()` · `:1058` `cuisineLabel()` · `:1254` `openStateNow()` · `:996` `esc()` | Zustands- und Textbausteine | **alles wiederverwendbar** — die Liste formuliert dieselben drei Zustände in Worten statt in Badges. |
| `web/index.html:1725` `updateCount()` · `:1743` `updateEmptyState()` | Trefferzahl an drei Orten, Leerzustand | bekommt einen vierten Ort (Listenkopf); der Leerzustand gilt auch für die Liste. |
| `web/index.html:1848–1875` URL-Zustand (A-8) | `?delivery=…&q=…` | **unberührt.** Die Liste bekommt keinen Parameter (ADR-008: Sheet-Zustand ist flüchtig). |
| `web/sw.js:27` | `CACHE_VERSION = "v6"` | hochzählen — `index.html` ist vorab gecacht. |

**Wiederverwendbar:** die gesamte Filterlogik, `openStateNow()`, `focusPlace()`,
die komplette Sheet-Mechanik samt Griff, Wischen, `Escape` und Fokusrückgabe,
`cssVar()`, die Farb-Tokens aus A-4. **Es fehlt:** die Liste selbst, die
Entfernungsrechnung, der Öffner in `#mapControls`, das Desktop-Panel und die
Ausweichlogik für `#mapControls`/`#feed`.

**Was ausdrücklich *nicht* fehlt:** eine Pipeline- oder Datenmodell-Änderung.
`scanner.py`, `export.py`, das DB-Schema und `restaurants.json` bleiben
unverändert — alles Nötige steht schon in der JSON.

## Spannung zu Nicht-Zielen — und Auflösung

**1. „Kein Backend, keine laufenden Kosten", kein Build-Schritt (ADR-002).**
Kein Konflikt: keine neue Abhängigkeit, kein npm, kein Bundler. Die
Entfernungsrechnung ist eine Haversine-Formel in acht Zeilen; gemessen
**1,4 ms** für 884 Restaurants inklusive Sortierung bei 4× CPU-Drosselung.

**2. „Keine Cookies, kein Tracking, keine Speicherung."** Unberührt. Sortiert
wird nach der **Kartenmitte**, nicht nach dem Gerätestandort — es wird also
nicht einmal eine Standortfreigabe verlangt. Wer „In meiner Nähe" nutzt, setzt
die Kartenmitte auf die eigene Position; die bleibt wie bisher im Browser. Der
Listenzustand kommt weder in `localStorage` noch in die URL (ADR-008).

**3. Bedienzeile ist auf drei Elemente fest (ADR-008).** Echter Konflikt —
und nachgemessen, statt geglaubt: ein viertes Element in `.controls` bricht die
Zeile von **44 px auf 96 px**, bei 360 px *und* bei 393 px. Aufgelöst: der Öffner
sitzt in `#mapControls` unten rechts, neben „In meiner Nähe". Das ist die
Kartenebene, nicht die Bedienzeile; ADR-008 fixiert die Zeile, nicht die Karte.

**4. „Die Karte ist das Vollbild" (ADR-008).** Gilt unter 640 px unverändert:
dort ist die Liste ein Sheet und nimmt der Karte nichts weg. Über 640 px greift
ADR-008 ausdrücklich nicht („Platznot ist die Begründung für den Umbau — wo sie
fehlt, fehlt auch der Grund"); dort ist das Panel dauerhaft sichtbar und lässt
bei 1280 px noch 75 % Kartenbreite.

**5. Pin-Achsen sind geschlossen (ADR-011).** Kein Konflikt am Aussehen: die
Pins bleiben Leaflets Standard-Icon, Pin für Pin identisch. **Wohl aber am
Wortlaut:** ADR-011 verlangt `L.marker([r.lat, r.lng])` *ohne Optionen*, A-2
setzt `{ keyboard: false, alt: "" }`. Das ist eine benannte, in
[ADR-013](../entscheidungen/ADR-013-ergebnisliste-ist-der-barrierefreie-hauptweg.md)
festgehaltene Ausnahme — sie betrifft die Tab-Kette, nicht die Optik, und darf
später nicht als durchgerutschter Verstoß „aufgeräumt" werden.

**6. Farbrollen (ADR-009), Farbe nie allein.** Kein Konflikt, aber die Regel
bindet: die drei Zustände stehen als **Text** in der Zeile
(„Lieferung: unbekannt"), die Farbe ist reine Zugabe. Verwendet werden
ausschließlich `--zustand-ja` / `--zustand-nein` / `--zustand-unbekannt` aus
`:root`; kein Farbwert außerhalb.

**7. „unbekannt" ist nie „nein" (ADR-007).** Die Liste schreibt es aus — bei
774 von 884 Restaurants (87,6 %) ist `delivery` ungetaggt. Genau deshalb ist
Text die richtige Form: „unbekannt" braucht ein Wort, keine Schattierung.

## Die Messung

Alles am 2026-08-09 gemessen. **Methodisch:** gegen **echtes Leaflet 1.9.4**
(lokal aus der npm-Registry), Chromium 393 × 851 und 1280 × 800, echte
`web/restaurants.json` (Scan vom 2026-08-09, 884 Restaurants, alle mit
Koordinaten). Der `L`-Stub aus `CLAUDE.md` kann keinen einzigen der folgenden
Werte liefern: er erzeugt kein DOM, und Tab-Ketten, Zeilenhöhen und
Frame-Zeiten *sind* DOM. Tempo-Werte zusätzlich mit **4× CPU-Drosselung**
(`Emulation.setCPUThrottlingRate`). Die Screenshots liefen mit echten
OSM-Kacheln — die Lehre aus A-5 ist, dass ein weißer Hintergrund kein Urteil
über das Aussehen erlaubt.

### Was die Karte für die Tastatur heute ist

Ohne offenes Popup gezählt (ein geöffnetes Popup bringt zwei weitere Stopps mit):

| Messung | Handy, alle Filter aus | Desktop, alle Filter aus | Desktop, Standardfilter |
|---|---|---|---|
| Marker im DOM | 884 | 884 | 51 |
| davon fokussierbar | **884** | **884** | **51** |
| Tab-Stopps im Dokument | **894** | **900** | 68 |
| davon Marker | 884 (**98,9 %**) | 884 (98,2 %) | 51 (75,0 %) |
| übrige Stopps | 10 | 16 | 17 |

Dazu, am Handy mit geöffnetem Popup gemessen: vom fokussierten Marker bis zum
Inhalt **seines eigenen** Popups sind es **884 Tabs** (im Standardfilter 53).
`alt` ist bei allen Markern `"Marker"`; der Text im `#map`-Teilbaum lautet
vollständig „+ − Leaflet | © OpenStreetMap-Mitwirkende".

**Nach der Umsetzung** (im Browser simuliert: Marker aus der Tab-Kette, Öffner
und Zeilen dazu):

| | heute | nachher |
|---|---|---|
| Handy, alle Filter aus | 894 | **311** (10 + Öffner + 300 Zeilen) |
| Desktop, alle Filter aus | 900 | **317** |
| Desktop, Standardfilter | 68 | **69** |

Der letzte Wert ist der ehrliche: **im Standardbild wird die Kette nicht kürzer,
sondern einen Stopp länger.** Der Gewinn liegt nicht in der Länge, sondern darin,
was an den Stopps steht — statt lauter gleich benannter „Marker, Schaltfläche",
deren Popup-Inhalt jeweils so viele Tabs entfernt liegt, wie es Treffer gibt,
stehen dort benannte Zeilen mit Name, Entfernung, Adresse und drei Zuständen. Wo
die Kette wirklich schrumpft, ist der aufgeweitete Fall: von 894 bzw. 900 auf
311 bzw. 317.

(Die Trefferzahl im Standardfilter wandert mit der Uhr — die Messungen oben
liegen bei 51 und 53, je nach Minute des Laufs. Nicht die Zahl ist der Befund,
sondern das Verhältnis.)

### Platz in beiden Pfaden

| Viewport | Karte heute | Fußzeile | Sheet-/Panelhöhe | sichtbare Zeilen |
|---|---|---|---|---|
| 360 × 740 | 709,2 px (95,8 %) | 30,8 px | Sheet 512 px | 7,4 |
| 393 × 851 | 820,2 px (96,4 %) | 30,8 px | Sheet 512 px | 7,4 |
| 1280 × 800 | 1280 × 661,3 px | 30,8 px | Panel 661,3 px | 7,8 |

Panelbreite gegen Kartenbreite (Zeilenhöhe median 85 px mit Entfernungsangabe):

| Viewport | Panel 20 rem | Karte | Anteil | Zeilen > 100 px hoch |
|---|---|---|---|---|
| 641 px | 256 px (`clamp`) | 385 px | 60,0 % | 97 von 884 |
| 768 px | 307 px (`clamp`) | 461 px | 60,0 % | ~31 |
| 1024 px | 320 px | 704 px | 68,8 % | 9 von 884 |
| 1280 px | 320 px | 960 px | **75,0 %** | 9 von 884 |
| 1920 px | 320 px | 1600 px | 83,3 % | 9 von 884 |

Ein **viertes Element in der Bedienzeile** bricht sie: 44 px → **96 px**, bei
360 px und bei 393 px gleichermaßen. Die Suche verliert dabei keine Breite (sie
bleibt bei 134,7 bzw. 167,7 px) — die Zeile wird schlicht zweizeilig. Damit ist
ADR-008s Regel „neue Bedienelemente gehören ins Sheet" hier nicht Auslegung,
sondern Messwert.

### Tempo — kein Argument gegen die Liste

4× gedrosselt, Median aus 9 Läufen nach 5 Aufwärmrunden:

| Zeilen | 50 | 100 | 300 | 884 |
|---|---|---|---|---|
| Liste bauen | 2,5 ms | 5,8 ms | **10,7 ms** | 42,0 ms |

Zum Vergleich aus [A-6](./A-6-clustering-oder-canvas.md): 884 **Marker** kosten
im selben Aufbau 386 ms. Scrollen mit 884 Zeilen: Median **16,7 ms**, p95
24,4 ms, **null** Frames über 100 ms. Entfernung rechnen und sortieren für 884
Restaurants: **1,4 ms**. Die Liste ist rechnerisch ein Zehntel des Problems,
das die Marker sind.

### Wie viele Treffer die Liste zeigen müsste

`openStateNow()` lebt nur im Frontend ([ADR-004](../entscheidungen/ADR-004-oeffnungszeiten-eigener-parser.md)),
also im Browser mit gesetzter Uhr ausgewertet:

| Filterzustand | Mi 12:30 | Mi 20:00 | So 12:30 | Sa 03:00 |
|---|---|---|---|---|
| **Standard: liefert + jetzt offen** | 47 | 55 | 43 | **0** |
| nur Lieferung | 64 | 64 | 64 | 64 |
| nur Abholung | 238 | 238 | 238 | 238 |
| Abholung + jetzt offen | 182 | 166 | 136 | 4 |
| nur jetzt offen | **498** | **548** | **427** | 13 |
| **alle Filter aus** | **884** | 884 | 884 | 884 |

Offenzustand aller 884 am Mi 12:30: **498 offen · 179 geschlossen · 207 nicht
auswertbar** (davon 143 ganz ohne `opening_hours`).

### Entfernung ab der Kartenmitte (Standardansicht 49,0069/8,4037, Zoom 12)

| Rang | 1. | 100. | **300.** | 301. | 500. | 884. |
|---|---|---|---|---|---|---|
| Entfernung | 0,03 km | 0,58 km | **1,72 km** | 1,77 km | 4,39 km | 12,01 km |

### Datenlage für die Zeilen

| Feld | gesetzt | fehlt |
|---|---|---|
| Adresse | 658 | **226 (25,6 %)** — davon 159 mit Küchenstil, **67 mit gar nichts** |
| `openingHours` | 741 | 143 |
| Website | 526 (59,5 %) | 358 |
| `delivery` | 64 ja / 46 nein | **774 unbekannt (87,6 %)** |
| `takeaway` | 238 ja / 8 nein | 638 unbekannt |
| Küchenstil | 698 | 186 |

Dazu **40 Namensdubletten** (mehrfach „Nordsee", „KFC", …) — ein Grund mehr,
Entfernung und Adresse in dieselbe Zeile zu schreiben: der Name allein
unterscheidet sie nicht.

## Entscheidungen (mit Begründung)

**1. Unter 640 px ein Bottom Sheet, darüber ein dauerhaft sichtbares Panel.**
Ein Knoten, zwei Darstellungen — dasselbe Muster wie `#filterPanel`. Der Öffner
ist ein zweiter Knopf in `#mapControls` („☰ Liste"), in beiden Pfaden derselbe;
auf dem Desktop schaltet er das Panel ab, wenn jemand die volle Karte will.
*Begründung:* auf dem Desktop ist Platz (75 % Karte bei 1280 px) und **R13 ist
damit im Standardbild ohne Klick gelöst** — genau der Befund, den ADR-011
hierher verschoben hat. Unter 640 px ist kein Platz, und ADR-008 ist dort
eindeutig.
*Verworfen:* auch auf dem Desktop nur auf Klick (Karte bliebe unangetastet, aber
das Standardbild gewänne nichts); mobil dauerhaft sichtbar als eingeklappte
Leiste (kehrt ADR-008 zweifach um: Vollbild und „keine Rastpunkte"); eigene
Seite `liste.html` (Filterlogik und `openStateNow()` existierten zweimal — die
Drift-Falle aus ADR-004).

**2. Sortiert wird nach Entfernung zur Kartenmitte, neu berechnet bei
`moveend`.** Kein Standortzugriff, keine Speicherung, und es beantwortet die
Frage, die der Ausgangstext stellt („was ist in der Nähe?"). Nach „In meiner
Nähe" ist die Kartenmitte die eigene Position, dann stimmt es doppelt.
*Verworfen:* alphabetisch (springt nie, beantwortet aber die Nähe-Frage nicht —
bei 884 Einträgen ist das Alphabet keine Hilfe beim Bestellen); Umschalter
Name/Entfernung (neues Bedien-Inventar für einen Fall, den die Suche abdeckt).

**3. Die Marker verlassen die Tab-Kette** (`keyboard: false`, `alt: ""`), die
Liste wird der Tastaturweg. Begründung und Ausnahme-Charakter gegenüber ADR-011
stehen in [ADR-013](../entscheidungen/ADR-013-ergebnisliste-ist-der-barrierefreie-hauptweg.md).
*Verworfen:* `alt: r.name` bei erhaltenem Fokus (884 benannte statt 884
gleichnamiger Stopps — die Popup-Falle bliebe); nichts ändern (der Befund bliebe
zur Hälfte stehen).
*Ausdrücklich nicht:* `aria-hidden="true"` auf `#map`. Darin liegt Leaflets
Attribution-Control, und die ODbL-Angabe darf für Screenreader nicht
verschwinden.

**4. Ein Klick auf eine Zeile ruft `focusPlace()`** — Karte auf Zoom 17,
Popup an den Koordinaten. Das ist bereits gebaut, funktioniert ohne Marker und
damit auch nach A-6, und es vermeidet eine zweite Fassung von `popupHtml()`.
Der Fokus wandert dabei in das Popup (`tabindex="-1"` auf dem Inhalt), sonst
liegt es im DOM **vor** der Liste und wäre nur rückwärts erreichbar.
*Verworfen:* Details in der Zeile aufklappen (zweite Darstellung derselben
Fakten, die auseinanderläuft); Website-Link direkt in der Zeile (verdoppelt die
Tab-Stopps auf bis zu 600, und 358 Restaurants haben gar keinen).

**5. Die Liste zeigt höchstens 300 Zeilen — gegen die Empfehlung dieser
Anforderung.** Empfohlen war **kein** Deckel: gemessen gibt es kein
Tempo-Argument (884 Zeilen 42 ms, Scrollen ohne einen Frame über 100 ms), und
ein Deckel lässt Listenlänge und `#count` auseinanderlaufen. Die
Produktverantwortung hat nach Vorlage dieser Zahlen den Deckel bei 300 gewählt;
die Entscheidung gilt, und die verworfene Empfehlung steht hier, damit später
nachvollziehbar ist, dass sie gesehen wurde.
*Was für die Entscheidung spricht und erst durch Entscheidung 2 entsteht:* mit
Entfernungssortierung ist der Deckel keine Willkür, sondern ein Radius — bei
Standard-Zoom schneidet er bei **1,72 km** ab, und was dahinter liegt, ist zum
Bestellen ohnehin unerheblich (das 500. Restaurant liegt 4,39 km, das letzte
12,01 km entfernt). Er greift außerdem selten: von sechs gemessenen
Filterzuständen überschreiten nur zwei die 300 („alle Filter aus" mit 884 und
„nur jetzt offen" mit 427–548), **jede Suche und jeder Küchenstil-Filter bleibt
darunter**.
*Bekannter Preis, ausdrücklich akzeptiert:* Liste und `#count` nennen dann
verschiedene Zahlen („300" gegen „884 von 884 angezeigt"). Damit das nicht wie
ein Fehler aussieht, **benennt die Liste den Unterschied selbst**, direkt unter
dem Kopf und nicht am Listenende — mit gerechneten, nicht geschriebenen Zahlen
(`CLAUDE.md`: jede den Nutzern gezeigte Quote gehört in Code).
*Verworfen:* Deckel bei 50 mit Nachladen (zweiter Bedienknopf ohne Messung, die
ihn verlangt).

**6. Die Zeile trägt drei Zeilen Text — Name, Entfernung + Adresse, drei
Zustände in Worten.** Das ist die Einlösung von R13. Fallkette für die zweite
Zeile: Adresse → Küchenstil (deckt 159 der 226 Adresslosen) → nur die
Entfernung (67 Fälle). *Begründung:* 226 fehlende Adressen sind zu viele für ein
„Adresse nicht hinterlegt" in jeder vierten Zeile, und 40 Namensdubletten
verlangen ein zweites Unterscheidungsmerkmal.

**7. Kein URL-Parameter, kein gespeicherter Zustand.** Offen/zu ist flüchtig
(ADR-008, Regel 5); ein geteilter Link zeigt die Karte, nicht eine offene Liste.
Auf dem Desktop ist „offen" der Startzustand, unter 640 px „zu".

## Umfang / Nicht-Umfang

- **Rein:** Listenknoten mit zwei Darstellungen (Sheet ≤ 640 px, Panel > 640 px);
  Öffner in `#mapControls`; Entfernungsrechnung und Sortierung nach Kartenmitte
  mit Neusortierung bei `moveend`; Zeilen mit Name, Entfernung, Adresse/Küche und
  den drei Zuständen in Worten; Deckel bei 300 samt gerechnetem Hinweis;
  `focusPlace()` als Klickpfad inklusive Fokusführung ins Popup;
  `{ keyboard: false, alt: "" }` an den Restaurant-Markern; Ausweichen von
  `#mapControls` und `#feed` vor dem offenen Panel; `map.invalidateSize()` beim
  Umschalten; `CACHE_VERSION` hochzählen.
- **Raus:** Pipeline, DB, JSON (nichts fehlt dort) · Sortier-Umschalter ·
  Website-Link in der Zeile · Details in der Zeile aufklappen · Virtualisierung
  der Liste (gemessen unnötig) · eigene Seite `liste.html` · Dark Mode (bleibt
  Backlog) · Clustering (das ist [A-6](./A-6-clustering-oder-canvas.md); beide
  sind unabhängig, weil `focusPlace()` an Koordinaten hängt) · `aria-hidden` auf
  `#map` · jede Änderung am Aussehen der Pins (ADR-011).

## Spezifikation

### UX-Ablauf und Zustände

1. **Desktop (> 640 px), Start:** Panel rechts neben der Karte, offen. Kopf
   „Ergebnisliste" plus Trefferzahl, darunter die Zeilen, nächstgelegene zuerst.
   Die Karte behält 60–83 % der Breite (Tabelle oben).
2. **Handy (≤ 640 px), Start:** Panel zu, in `#mapControls` liegt „☰ Liste".
   Ein Tipp öffnet es als Bottom Sheet über die bestehende Mechanik: Griff,
   Wischen nach unten schließt, `Escape` schließt, Fokus wandert auf die
   Überschrift und beim Schließen zurück auf den Auslöser.
3. **Filter, Suche, Küchenstil ändern:** Liste und Karte aktualisieren sich im
   selben `render()`. Die Liste zeigt immer genau die Treffer der Karte.
4. **Karte verschieben oder zoomen:** bei `moveend` wird neu sortiert und neu
   gezeichnet (gemessen 1,4 ms + 10,7 ms bei 300 Zeilen, 4× gedrosselt).
5. **Zeile anklicken:** Karte springt auf Zoom 17, Popup öffnet, Fokus geht in
   das Popup. Unter 640 px schließt das Sheet dabei — wie es `focusPlace()`
   heute schon für den Feed tut.
6. **Mehr als 300 Treffer:** die 300 nächstgelegenen; direkt unter dem Kopf eine
   Zeile, die die Zahl und den Radius nennt, beides gerechnet
   („Die 300 nächstgelegenen von 884 Treffern — die übrigen liegen weiter als
   1,7 km von der Kartenmitte entfernt.").
7. **Null Treffer:** die Liste zeigt denselben Text wie `#empty` und den Knopf
   „Alle Restaurants zeigen". Im Standardfilter ist das nachts der Regelfall
   (Sa 03:00 gemessen: 0).
8. **Panel geschlossen (Desktop):** die Karte nimmt die volle Breite,
   `#mapControls` und `#feed` rücken zurück nach rechts.

### Interaktion mit Bestehendem

- **Sheet-Mechanik:** `SHEETS` bekommt einen dritten Eintrag. `openSheet()`
  erzwingt „nur eines gleichzeitig" — für die Liste gilt das **nur unter
  640 px**; darüber ist sie ein Panel mit eigenem Zustand und darf nicht
  zugehen, wenn der Feed geöffnet wird. Das ist dieselbe Ausnahme, die `filter`
  dort schon hat (`s.name === "filter" && !isNarrow()`).
- **`applyLayout()`** setzt `role="dialog"` + `aria-labelledby` nur im schmalen
  Pfad und entfernt beides darüber; beim Überschreiten der Grenze wird ein
  offenes Sheet zum offenen Panel, ohne dass der Fokus ins Leere fällt.
- **`measureChrome()`** setzt zusätzlich `--liste-b` auf die gemessene
  Panelbreite (0 px, wenn zu oder im schmalen Pfad). `#mapControls` und `#feed`
  rechnen ihr `right` daraus.
- **`map.invalidateSize()`** nach jedem Umschalten des Panels — sonst rechnet
  Leaflet mit der alten Breite und die Kacheln stehen falsch.
- **`focusPlace()`** bekommt den Listen-Fall: Sheet schließen (nur schmal),
  Fokus in das Popup statt auf den Kartencontainer. Der Feed-Fall bleibt, wie er
  ist.
- **`#count`** bleibt die eine vorgelesene Trefferzahl (`role="status"`); der
  Listenkopf zeigt dieselbe Zahl still (`aria-hidden`), damit nicht zweimal
  vorgelesen wird.
- **A-6 (Clustering):** unabhängig. `focusPlace()` hängt an Koordinaten, nicht
  am Marker; die in A-6 vorbereitete `zoomToShowLayer`-Kopplung wird **nicht**
  gebraucht. Wird A-6 zuerst gebaut, ändert sich an A-2 nichts und umgekehrt —
  außer der `CACHE_VERSION`, die dann fortlaufend zählt.
- **A-8 (URL-Parameter):** unberührt, kein neuer Parameter.

### Datenmodell und Persistenz

Keine Änderung. Alle Felder stehen in `restaurants.json`; die Entfernung wird
zur Laufzeit gerechnet und nirgends gespeichert.

### Externe Abhängigkeiten und Fallback

Keine neue. Fällt `restaurants.json` aus, greift der bestehende Fehlerpfad
(`#loading` zeigt den Fehler); die Liste bleibt dann leer wie die Karte.

### Randfälle und Fehlerbehandlung

| Fall | Verhalten |
|---|---|
| Genau 300 Treffer | vollständig zeigen; der Hinweis erscheint erst ab 301. |
| Restaurant ohne Adresse (226) | Küchenstil statt Adresse (159 Fälle), sonst nur die Entfernung (67). Nie „Adresse nicht hinterlegt" als Dauertext. |
| Restaurant ohne `opening_hours` (143) | „Öffnungszeit unbekannt" — nie „geschlossen" (ADR-004/ADR-007). |
| `delivery`/`takeaway` = `null` (774 / 638) | „unbekannt", nie „nein". |
| Namensdubletten (40) | Entfernung und Adresse in der zweiten Zeile unterscheiden sie. |
| Null Treffer | Leerzustandstext und „Alle Restaurants zeigen" auch in der Liste. |
| Sehr langer Name (max. 75 Zeichen) | umbricht; Zeilenhöhe wächst von 85 auf bis zu 125 px, gemessen bei 9 von 884 Zeilen (320 px Panel). Kein Abschneiden. |
| Karte wird durch `focusPlace()` bewegt | **nicht** neu sortieren — sonst springt die eben angeklickte Zeile unter dem Finger nach oben und die Scrollposition ist weg. Das `moveend` aus einer Listen-Navigation wird übersprungen. |
| 200 % Zoom / große Schrift | Sheet- und Panelmaße hängen an `rem` und an `--footer-h`; die Fußzeile wird gemessen, nicht geschätzt. |
| Panel offen bei 641 px | Panel 256 px, Karte 385 px (60 %). Eng, aber die Karte bleibt die Mehrheit; abschaltbar über denselben Knopf. |

### Barrierefreiheit

- Die Liste ist `<ul>` mit `<li><button>` je Restaurant — für Screenreader eine
  Liste bekannter Semantik mit Anzahl, überspringbar mit einem Befehl.
- Überschrift `<h2>` mit `tabindex="-1"` als Fokusziel beim Öffnen (wie
  `filterTitle`/`feedTitle`).
- Jede Zeile trägt ihre Information als **Text**, nicht als Farbe: Name,
  Entfernung, Adresse oder Küchenstil, dann „Lieferung: ja/nein/unbekannt ·
  Abholung: … · jetzt geöffnet/geschlossen/Öffnungszeit unbekannt". Die
  `--zustand-*`-Farben sind Zugabe (ADR-009: Farbe nie allein).
- Trefferfläche jeder Zeile ≥ 44 px (A-3-Maß); gemessene Zeilenhöhe 85 px.
- Restaurant-Marker verlassen die Tab-Kette (`keyboard: false`, `alt: ""`).
  **`#map` bekommt kein `aria-hidden`** — dort liegt die ODbL-Attribution.
- Leaflets Zoom-Control und der Kartencontainer bleiben bedienbar; wer die Karte
  mit Pfeiltasten verschieben will, kann das weiter.
- Der Öffner in `#mapControls` trägt ein `aria-label` und `aria-expanded`, das
  Emoji ist `aria-hidden` (A-3-Muster).

### Testplan

Playwright gegen **echtes Leaflet** (der `L`-Stub kann Tab-Ketten und Zeilenhöhen
nicht messen), Handy- **und** Desktop-Viewport, synthetische Daten **und** die
echte `restaurants.json`:

1. **Tab-Kette:** kein Marker ist fokussierbar; Tab-Stopps ohne Filter ≤ 311
   am Handy und ≤ 317 am Desktop (heute 894 bzw. 900).
2. **Marker-Optik unverändert (ADR-011):** jeder Restaurant-Marker ist ein
   `L.marker` mit dem Standard-Icon; `L.circleMarker` nur in `locateMe()`.
3. **Gleichstand Liste/Karte:** für fünf Filterzustände ist die Zeilenzahl gleich
   der Markerzahl — bis zum Deckel, darüber genau 300.
4. **Deckel:** bei 300 Treffern kein Hinweis, bei 301 der Hinweis mit
   **gerechneter** Zahl und **gerechnetem** Radius (kein fester Text).
5. **Sortierung:** die Entfernungen in der Liste sind monoton steigend; nach
   `map.setView()` auf einen anderen Punkt steht ein anderes Restaurant oben.
6. **Keine Neusortierung nach Zeilenklick:** Reihenfolge und Scrollposition
   bleiben, obwohl `moveend` gefeuert hat.
7. **Zustände in Worten:** ein Restaurant mit `delivery === null` zeigt
   „unbekannt", nie „nein"; eines ohne `opening_hours` „Öffnungszeit unbekannt".
8. **Fallkette Adresse:** ein Eintrag ohne Adresse mit Küchenstil zeigt den
   Küchenstil; einer ohne beides zeigt nur die Entfernung.
9. **Sheet-Mechanik (schmal):** Griff, Wischen, `Escape`, Fokus auf die
   Überschrift, Fokusrückgabe an den Auslöser; nur ein Sheet gleichzeitig.
10. **Panel-Eigenständigkeit (breit):** Feed öffnen schließt die Liste **nicht**.
11. **Layout:** `elementFromPoint` in der Mitte des „In meiner Nähe"-Knopfes
    trifft den Knopf, nicht das Panel; Fußzeile und Attribution sind in beiden
    Pfaden und in beiden Panel-Zuständen unverdeckt.
12. **`invalidateSize`:** nach dem Umschalten stimmt `map.getSize().x` mit der
    gemessenen Kartenbreite überein.
13. **Tempo:** 300 Zeilen bauen unter 4× Drosselung < 30 ms; Scrollen ohne Frame
    über 100 ms.
14. **Leerzustand:** bei 0 Treffern zeigen Karte und Liste denselben Text.
15. **Screenshots** in beiden Pfaden, je mit Standardfilter und ohne Filter —
    vier Bilder, mit echten Kacheln, **vorgelegt, bevor die Doku geschrieben
    wird** (die Lehre aus A-5).

**Pipeline-Tests:** `python3 -m unittest discover -s tests -v` muss grün bleiben;
A-2 fasst keinen Pipeline-Code an.

### Doku- und Backlog-Auswirkungen

- **`docs/entscheidungen/ADR-013-…`** ist neu und steht auf `vorgeschlagen` —
  nach der Umsetzung auf `akzeptiert`, **an beiden Orten** (Datei-Header und
  Zeile in `entscheidungen/README.md`; die Falle aus `CLAUDE.md`).
- **`docs/UMGESETZT.md`** nach der Umsetzung, mit den Messwerten.
- **Root-`README.md`**: „Bereits umgesetzt"/„Offen" pflegen — die Liste hing bei
  A-5 zwei Anforderungen hinterher.
- **`docs/BACKLOG.md`**: **R6 und R13 sind mit A-2 erledigt** und dort
  nachzutragen (R13 steht seit dem A-5-Rückbau als „wieder offen"). Der Punkt
  „Anteile und Zahlen im UI aus den Daten rechnen" bekommt mit dem
  Deckel-Hinweis einen weiteren Fall — diesmal von Anfang an gerechnet.
- **`docs/TECHNICAL.md`**: die neue `CACHE_VERSION` im Abschnitt „PWA".
- **`CLAUDE.md`**: der `L`-Stub-Absatz sollte festhalten, dass Tab-Ketten,
  Zeilenhöhen und Fokusreihenfolge **nur** gegen echtes Leaflet messbar sind,
  und dass in einer lokalen Sitzung (anders als in der Web-Sitzung) sowohl die
  npm-Registry als auch `tile.openstreetmap.org` erreichbar sind — Screenshots
  mit echten Kacheln sind dort möglich und für Optik-Urteile Pflicht.
- **`docs/PRD.md`**: die Zahlen unter „Abdeckungsrealität" stammen vom
  2026-07-26 (885 Restaurants); Stand 2026-08-09 sind es **884** mit
  `delivery` 64/46/774, `takeaway` 238/8/638, `cuisine` 698, `opening_hours`
  741. Als Aufgabe in `BACKLOG.md`, nicht hier.

## Definition of Done

- [ ] Kein Restaurant-Marker ist fokussierbar; Tab-Stopps ohne Filter **≤ 311**
      (Handy, heute 894) bzw. **≤ 317** (Desktop, heute 900).
- [ ] Die Marker sehen unverändert aus: `L.marker` mit Standard-Icon, nur
      `keyboard`/`alt` als Optionen; `L.circleMarker` weiter nur in `locateMe()`.
- [ ] Liste und Karte zeigen in fünf geprüften Filterzuständen dieselben
      Restaurants; über 300 Treffern genau 300, mit gerechnetem Hinweis auf Zahl
      und Radius.
- [ ] Sortierung nach Entfernung zur Kartenmitte, monoton steigend, neu bei
      `moveend` — **außer** nach einem Zeilenklick.
- [ ] Jede Zeile nennt Lieferung, Abholung und Öffnungszustand **in Worten**;
      `null` steht als „unbekannt", nie als „nein".
- [ ] Adressloser Eintrag zeigt Küchenstil, notfalls nur die Entfernung.
- [ ] Unter 640 px vollständige Sheet-Mechanik (Griff, Wischen, `Escape`, Fokus
      hin und zurück, nur eines gleichzeitig); über 640 px Panel mit eigenem
      Zustand, das der Feed nicht schließt.
- [ ] `#mapControls` und `#feed` liegen bei offenem Panel über der Karte, nicht
      über der Liste; `map.getSize().x` stimmt nach jedem Umschalten.
- [ ] „© OpenStreetMap-Mitwirkende" sichtbar, Fußzeile unverdeckt, `#map` **ohne**
      `aria-hidden` — in beiden Pfaden und beiden Panel-Zuständen.
- [ ] 300 Zeilen bauen unter 4× Drosselung < 30 ms; Scrollen ohne Frame > 100 ms.
- [ ] Keine Cookies, kein Tracking, kein Speicherzugriff, kein neuer
      URL-Parameter dazugekommen.
- [ ] `CACHE_VERSION` in `web/sw.js` hochgezählt.
- [ ] `python3 -m unittest discover -s tests -v` grün.
- [ ] Vier Screenshots (zwei Pfade × Standardfilter/ohne Filter) mit echten
      Kacheln **der Produktverantwortung vorgelegt, bevor die Doku geschrieben
      wird**.
- [ ] ADR-013 auf `akzeptiert` (Datei **und** `entscheidungen/README.md`), R6 und
      R13 in `BACKLOG.md` abgehakt, Status in `anforderungen/README.md` auf 🏁.

## Umsetzungsschritte

1. Listenknoten in `web/index.html` anlegen (Geschwister von `#map`, in einer
   Hülle, die im schmalen Pfad `display: contents` ist), Öffner in
   `#mapControls`.
2. CSS in **beiden** Pfaden — `display` ausschließlich innerhalb eines
   Pfad-Blocks setzen, Selektoren mit `#listePanel` qualifizieren, damit
   `.controls button` (0,1,1) sie nicht schlägt. Beides sind dokumentierte
   A-3-Fallen.
3. `SHEETS` um den dritten Eintrag ergänzen, Breiten-Ausnahme in `openSheet()`
   und `applyLayout()` nachziehen.
4. Entfernungsrechnung, Sortierung, Zeilenbau; `render()` gibt die Treffer
   weiter, statt sie nur zu zählen.
5. `{ keyboard: false, alt: "" }` an den Marker; `focusPlace()` um Fokusführung
   ins Popup und den Listen-Fall erweitern.
6. `measureChrome()` um `--liste-b`; `#mapControls`/`#feed` daran ausrichten;
   `map.invalidateSize()` beim Umschalten.
7. `CACHE_VERSION` hochzählen.
8. Testplan durchfahren (echtes Leaflet, nicht der `L`-Stub), vier Screenshots
   erzeugen und **vorlegen**.
9. Nach Freigabe: ADR-013 auf `akzeptiert`, Doku und Status nachziehen, die
   PRD-Zahlen als Aufgabe in `BACKLOG.md`.
