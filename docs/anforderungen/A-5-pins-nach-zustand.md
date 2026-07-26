# A-5 Pins nach Zustand unterscheiden (R13)

[← Anforderungen](./README.md) · [Prozess](../PROZESS.md)
· Status siehe [Übersicht](./README.md#übersicht)

**User Story:** Als Nutzerin möchte ich auf der Karte sehen, welche Restaurants liefern, abholen lassen oder gerade geschlossen sind, ohne jeden Pin antippen zu müssen.

**Verfeinert am:** 2026-07-26
**Bedient PRD:** „Kernschleife" Schritt 1
**Eingeschränkt durch:**
[ADR-009](../entscheidungen/ADR-009-farbrollen-marke-aktion-zustand.md)
(die Zustandstokens und die Regel „Farbe nie allein"),
[ADR-007](../entscheidungen/ADR-007-standardfilter-liefert-jetzt.md)
(„unbekannt" nie wie ein „nein"),
[ADR-008](../entscheidungen/ADR-008-karte-im-vollbild-overlay-und-sheets.md)
(zwei Layout-Pfade, Bedienzeile fest auf drei Elemente)
· **Ergebnis:**
~~[ADR-010](../entscheidungen/ADR-010-pin-grammatik-lieferung-und-geschlossen.md)~~
→ [ADR-011](../entscheidungen/ADR-011-pins-wieder-einheitlich.md)

> ## ⛔ Am 2026-07-26 umgesetzt und am selben Tag zurückgenommen
>
> Die Produktverantwortung hat die fertigen Pins auf dem Telefon angesehen und
> **abgelehnt**: die dunkelgrün gefüllten Kreise wirken schwerer und unruhiger
> als der vertraute blaue Leaflet-Tropfen. Entschieden wurde ein **vollständiger
> Rückbau** der Optik —
> [ADR-011](../entscheidungen/ADR-011-pins-wieder-einheitlich.md) kehrt ADR-010
> um, das damit auf `ersetzt durch ADR-011` steht. Die Pins sind wieder
> `L.marker`, ohne Farbe, ohne Größenabstufung, ohne Legende.
>
> Das ging **gegen die Empfehlung dieser Anforderung** und wird deshalb hier
> festgehalten statt geglättet. Zwei Zahlen aus dieser Datei stützen die
> Entscheidung allerdings selbst: im Standardfilter sind alle **53 von 885**
> sichtbaren Pins zwangsläufig identisch (grün, offen — genau danach filtert
> ADR-007), und aufgeweitet sind **774 von 885** (87,5 %) grau gestrichelt.
> Der optische Preis fällt also im Hauptbild an, der Nutzen im Randbild.
>
> **Was bleibt:** die Messungen unten (64/47/774 · 427/248/210 · die
> Kontrastwerte) sind unverändert gültig und für die nächste Idee
> wiederverwendbar. Ebenso bleiben die beiden unsichtbaren Tempo-Verbesserungen
> (`BERLIN_FMT` einmal statt je Aufruf, Zeitauswertung hinter den billigen
> Filtern) — sie haben mit dem Aussehen nichts zu tun.
>
> **Was offen ist:** Befund **R13** („Zustand nur nach Antippen sichtbar"). Er
> wird nicht erneut über die Pins gelöst — die Pin-Achsen sind nach ADR-011
> geschlossen, nicht frei —, sondern über
> [A-2](./A-2-ergebnisliste.md): eine Liste hat beliebig viele Worte, ein
> 20-px-Punkt vier Kanäle, und für Screenreader existieren farbige Kreise
> ohnehin nicht.

## Ausgangstext (aus `backlog/IDEEN.md`, Idee 5)

> Ob ein Restaurant liefert, abholen lässt oder gerade geschlossen ist, sieht man
> erst nach dem Antippen. Farb- oder Formcodierung (z. B. blass = jetzt
> geschlossen) bringt viel pro Blick. Hängt an
> **[A-1](./A-1-standardfilter-entschaerfen.md)**: erst mit entschärftem
> Standardfilter lohnt die Unterscheidung wirklich, und erst dann steht fest, welche
> Zustände überhaupt nebeneinander vorkommen.
>
> Braucht außerdem [A-4](./A-4-farbsystem.md): solange `--accent` vier Bedeutungen
> trägt, ist keine Farbe für „Zustand" frei.

**Nachtrag 2026-07-25 (aus der A-4-Verfeinerung):** ~~A-4 ist entschieden und
liefert die Grundlage.~~ → **A-4 ist am 2026-07-25 umgesetzt**; die Tokens und
`cssVar()` stehen im Code. Drei Vorgaben binden A-5
([ADR-009](../entscheidungen/ADR-009-farbrollen-marke-aktion-zustand.md)):

1. **Pins dürfen nur den `--zustand-*`-Satz benutzen** (`ja` grün, `nein` slate,
   `unbekannt` grau) — nicht `--marke` und nicht `--aktion`.
2. **Farbe allein darf den Zustand nie tragen.** Die Zustandsfarben liegen nur
   1,92 auseinander — Form, Größe oder Symbol muss mit. Die Idee „blass = jetzt
   geschlossen" geht in die richtige Richtung, weil sie Helligkeit statt Farbton
   nutzt.
3. **Blau ist verbraucht:** ein Pin kann nicht „blau = Abholung" und
   „grün/slate = offen/zu" gleichzeitig sagen.

**Nachgemessen am 2026-07-26** — die Zahlen des Nachtrags stammten vom Scan am
2026-07-21 und sind eine Woche alt. Korrigiert, nicht übernommen:

| Angabe im Ausgangstext | gemessen 2026-07-26 |
|---|---|
| ~~883 aktiv~~ | **885** |
| ~~Lieferung 63 ja / 47 nein / 773 unbekannt~~ | **64 / 47 / 774** (87,5 % unbekannt) |
| ~~Abholung 237 / 8 / 638~~ | **238 / 8 / 639** (72,2 % unbekannt) |
| „unbekannt ist der Hauptfall" | bestätigt — bei **609** Restaurants (68,8 %) ist **beides** ungetaggt |

Die Aussagen des Nachtrags halten also alle; nur die Zahlen wandern wöchentlich.
Die drei Kontrastwerte aus ADR-009 (1,92 · 1,03 · die Tokenfarben) haben sich
gegen `web/index.html` reproduzieren lassen.

## Andockpunkte im Code

| Vorhanden | Wo | Taugt wofür |
|---|---|---|
| `cssVar(name, fallback)` | `web/index.html` | Tokenfarbe in JS lesen — genau das, was Leaflet für Vektor-Pins braucht. `locateMe()` ist die Vorlage. |
| `openStateNow(raw)` | `web/index.html` | `true` / `false` / `null` für „jetzt geöffnet". Wird von `render()` ohnehin für den Filter gerufen — das Ergebnis lässt sich für den Pin mitnehmen. |
| `.badge-yes/-no/-unknown` | `web/index.html` | Die **Form-Grammatik**, die der Pin erbt: gefüllt gegen gestrichelten Umriss. |
| `--zustand-ja/-nein/-unbekannt` | `:root` | Die einzigen erlaubten Pin-Farben. |
| `render()` | `web/index.html` | Eine Stelle erzeugt alle Marker (`L.marker(...).bindPopup(...)`). |
| `#filterPanel` + `openSheet()` | `web/index.html` | Der Ort für die Legende: ein Knoten, beide Layout-Pfade. |

**Was fehlte:** eine Pin-Stilfunktion, die Legende, und der Wechsel von
`L.marker` (Bild-Icon vom CDN) auf `L.circleMarker` (SVG). **Keine
Pipeline-Änderung** — `delivery` und `opening_hours` stehen längst in DB und
JSON, es wird nichts nachgescannt und nichts migriert.

## Spannung zu Nicht-Zielen — und Auflösung

- **„Karte ist ein Jetzt-Werkzeug, kein Verzeichnis"
  ([ADR-007](../entscheidungen/ADR-007-standardfilter-liefert-jetzt.md)).** Beim
  Standardfilter „Liefert jetzt" sehen **alle** Pins gleich aus (grün, volle
  Größe) — die Unterscheidung greift erst, wenn jemand die Filter aufweitet.
  *Auflösung:* genau dieser Weg ist nach ADR-007 der übliche (der nächtliche
  Leerzustand bietet „Alle Restaurants zeigen" an), und dort stehen dann 885
  Punkte nebeneinander. A-5 ist die Antwort auf den aufgeweiteten Zustand, nicht
  auf den Default — kein Grund, den Default anzufassen.
- **„unbekannt nie wie ein nein"** (ADR-007). 774 Pins sind „Lieferung
  unbekannt". *Auflösung:* eigene Farbe **und** eigene Form (gestrichelt); die
  Abwertung „klein und blass" trifft ausschließlich, was sicher geschlossen ist.
- **Bedienzeile fest auf drei Elemente**
  ([ADR-008](../entscheidungen/ADR-008-karte-im-vollbild-overlay-und-sheets.md)).
  Die Legende ist ein viertes Bedienelement. *Auflösung:* Sie geht ins
  Filter-Sheet, nicht in die Zeile — genau der Weg, den ADR-008 für neue
  Elemente vorschreibt.
- **Kein Tracking, keine Speicherung.** Unberührt: die Pin-Darstellung ist reine
  Anzeige, kein Zustand, kein URL-Parameter.

## Entscheidungen (mit Begründung)

Alle drei Weichen wurden am 2026-07-26 der Empfehlung folgend entschieden. Die
ausführliche Fassung samt verworfener Alternativen steht in
[ADR-010](../entscheidungen/ADR-010-pin-grammatik-lieferung-und-geschlossen.md).

**1. Die Pin-Farbe trägt die *Lieferung*** (64 grün / 47 slate / 774 grau) —
nicht die Sammelachse „Lieferung oder Abholung" (258 / 18 / 609).
*Begründung:* Die Sammelachse sähe lebendiger aus, aber **194 der 258 grünen
Pins liefern nicht**, sie lassen nur abholen. Auf einer Karte namens
„Lieferkarte" wäre Grün dann in drei von vier Fällen die falsche Auskunft.
*Verworfen außerdem:* Abholung als Symbol im Pin (mehrfarbige Emoji brechen die
Farbrollen, bei 20 px unlesbar, 885 DOM-Knoten).

**2. Abgewertet wird nur, was sicher geschlossen ist** (248 von 885) — die 210
Restaurants mit unklaren oder fehlenden Zeiten bleiben unverändert.
*Begründung:* Alles andere zeigte ein „unbekannt" als Absage (ADR-007). Der Pin
behauptet damit nie „offen", nur „nicht bekannt zu"; die Legende sagt das auch
so.
*Verworfen:* dreistufige Öffnungsachse (3 × 3 = neun Pin-Varianten).

**3. Die Legende steht im Filter-Sheet** — ein Knoten für beide Layout-Pfade.
*Begründung:* Ein Farbcode, den man nur durchs Antippen lernt, ist Dekoration —
und Antippen ist genau das, was A-5 abschaffen soll.
*Verworfen:* Karten-Overlay (kostet dauerhaft die Fläche, die A-3 gerade
zurückgewonnen hat) und „gar keine Legende".

**4. Technik: `L.circleMarker` statt `L.divIcon`** (keine Weiche für die
Produktverantwortung, aber die folgenreichste technische Festlegung).
*Begründung:* Der gestrichelte Umriss ist in SVG ein Attribut und kostet nichts;
`divIcon` bräuchte eigenes Markup und 885 DOM-Knoten. Nebeneffekt: mit
Vektor-Pins ist [A-6](./A-6-clustering-oder-canvas.md) künftig
`preferCanvas: true` — eine Zeile.

## Umfang / Nicht-Umfang

- **Rein:** Pin-Darstellung nach Lieferzustand und „jetzt geschlossen" ·
  Legende in beiden Layout-Pfaden · Standort-Marker formlich abgesetzt ·
  Aufräumen der nicht mehr benutzten Marker-Grafiken im Service Worker.
- **Raus:** Abholung auf dem Pin (bleibt Chip, Badge, Popup) · Küchenstil auf
  dem Pin · Clustering/Canvas ([A-6](./A-6-clustering-oder-canvas.md)) ·
  Screenreader-Zugang zur Karte ([A-2](./A-2-ergebnisliste.md)) · Dark Mode
  (P3 im [Backlog](../BACKLOG.md)) · jede Pipeline-Änderung.

## Spezifikation

### Zustände und Darstellung

| Lieferung | offen **oder** unbekannt | sicher geschlossen |
|---|---|---|
| **ja** (`delivery === true`) | `--zustand-ja`, r 10, Füllung 0,85, durchgezogen | `--zustand-ja`, **r 7**, Füllung **0,2** |
| **nein** (`=== false`) | `--zustand-nein`, r 10, Füllung 0,85, durchgezogen | `--zustand-nein`, **r 7**, Füllung **0,2** |
| **unbekannt** (`null`) | `--zustand-unbekannt`, r 10, Füllung 0,12, **gestrichelt** (`3 3`) | `--zustand-unbekannt`, **r 7**, Füllung **0**, gestrichelt |

Der **Umriss** ist in allen sechs Fällen 2 px breit und **voll deckend**
(`opacity: 1`). Das ist keine Kosmetik: reine Deckkraft — die Idee „blass" aus
dem Ausgangstext — erreicht gemessen nur **2,59:1** (`--zustand-ja` bei 60 % auf
heller Kachel) und reißt die 3:1-Grenze für grafische Objekte (WCAG 1.4.11).
Voll deckend erreicht `--zustand-ja` über die üblichen Kachelfarben
**4,07–6,53:1**; über alle drei Zustandsfarben liegt die Spanne bei
**3,32–12,52:1**, schlechtester Fall „unbekannt" auf Wasser mit **3,32:1**.

### Interaktion mit Bestehendem

- **Popup unverändert.** Die Badges sagen dasselbe wie der Pin — gleiche Farben,
  gleiche Form-Grammatik. Sie bleiben faul gebaut (R7).
- **Filter unverändert.** `FILTER_DEFAULTS` wird nicht angefasst.
- **`render()`** wertet die Öffnungszeiten jetzt **nach** den billigen Filtern
  aus (statt an dritter Stelle): das Ergebnis dient Filter *und* Pin, und
  `openStateNow()` läuft nur noch für Restaurants, die alles andere überstanden
  haben.
- **`berlinNow()`** baut den `Intl.DateTimeFormat` **einmal** statt bei jedem
  Aufruf. Gemessen an derselben Fassung, nur ohne diese Änderung: **62,9 ms**
  gegen **5,6 ms** für 885 Pins (Median aus 3 × 20 Durchläufen nach 20
  Aufwärmrunden).
- **Standort-Marker** (`locateMe()`) wird ein großer, dünn gefüllter Ring
  (r 13, Füllung 0,15) statt eines Punkts (r 8, Füllung 0,6): seit die
  Restaurants Kreise sind, reicht „rot" nicht mehr — Marken-Rot gegen
  Zustands-Grün hat 1,03 Helligkeitsabstand.
- **`web/sw.js`:** `CACHE_VERSION` auf `v5`; die drei Leaflet-Marker-Grafiken
  fliegen aus `CDN_FILES`, weil `L.marker` nirgends mehr entsteht.

### Legende

Ein Knoten `#legende` im Filter-Sheet, vier Einträge. Die Farbmuster erzeugt
`buildLegend()` als Inline-SVG aus **derselben** `pinStyle()`-Tabelle wie die
Marker — Karte und Legende können nicht auseinanderlaufen. Der Anteil „nicht
eingetragen" wird aus den geladenen Daten berechnet (`updateLegendShare()`),
nicht in den Text geschrieben: er ändert sich mit jedem Sonntags-Scan.

- **unter 640 px:** gestapelte Liste im Sheet, unter den Chips, über „Mehr". Der
  Sheet-Körper scrollt — die Legende liegt unterhalb der Faltung und ist durch
  Scrollen erreichbar.
- **ab 640 px:** eine eigene volle Zeile in der Bedienzeile. `order: 1` schiebt
  sie hinter Zähler und Feed-Knopf; ohne das stünde sie mitten in der Zeile,
  weil `#filterPanel` im DOM vor beiden liegt.
- `display` steht ausschließlich in den beiden Pfad-Blöcken, nie in einer
  gemeinsamen Basisregel (ADR-008).

### Randfälle

| Fall | Verhalten |
|---|---|
| `openingHours` fehlt (143) oder ist unlesbar (67) | Pin wie „offen" — volle Größe, volle Füllung. Kein „geschlossen"-Look. |
| `delivery === null` (774) | Grau **und** gestrichelt. Nie wie „nein". |
| Restaurant ohne Koordinaten | Fällt wie bisher vor dem Zeichnen heraus. |
| Tokens nicht auflösbar (`cssVar` liefert "") | Fallback auf die `:root`-Werte, wie bei `--marke` in `locateMe()`. |
| Leere Trefferliste | Unverändert der Leerzustand aus A-1. |
| Alte `restaurants.json` ohne `delivery` | `undefined` ist weder `true` noch `false` → „unbekannt". Degradiert tragfähig. |

### Barrierefreiheit

- Jede Achse ist **doppelt codiert**: Lieferung über Farbe *und* Strichart,
  „geschlossen" über Größe *und* Füllstärke. Keine Aussage hängt am Farbton.
- Umriss-Kontrast ≥ 3:1 auf allen üblichen Kachelfarben (gemessen 3,32–12,52:1).
- Die Legendenmuster sind `aria-hidden`; die Aussage trägt der Text.
- **Bewusste Lücke:** Für Screenreader bleibt die Karte leer — Pins sind SVG
  ohne Beschriftung. Das war vorher genauso und ist der Kern von
  [A-2](./A-2-ergebnisliste.md); A-5 verschlechtert es nicht, löst es aber auch
  nicht.
- **Bewusste Verschlechterung:** Die Trefferfläche sinkt von 25 × 41 px
  (Leaflet-Standard-Icon) auf 20 px, bei geschlossenen auf 14 px. Begründung in
  [ADR-010](../entscheidungen/ADR-010-pin-grammatik-lieferung-und-geschlossen.md).

### Testplan

Python-Suite (59 Tests) muss grün bleiben, obwohl die Pipeline unberührt ist.
Frontend über Playwright mit dem `L`-Stub, der die Marker samt Optionen
einsammelt — **36 Prüfungen**, synthetische Daten *und* die echte
`restaurants.json`, beide Layout-Pfade, dazu Screenshots (Zustand allein hätte
in A-3 drei Defekte durchgelassen):

1. Sechs synthetische Restaurants decken alle Kombinationen ab (ja/nein/unbekannt
   × offen/zu/Zeiten unbekannt) — Farbe, Radius, Füllung, Strichart je Pin.
2. Kein Pin trägt `--marke` oder `--aktion`; kein `L.marker` mehr.
3. Umriss-Kontrast gegen fünf typische Kachelfarben ≥ 3:1.
4. Legende: vier Einträge, SVG-Muster, Farben identisch zu den Pins,
   gestrichelt bei „unbekannt", r 7 beim „geschlossen"-Muster, Anteil aus den
   Daten.
5. Echte Daten: 885 Pins, Verteilung plausibel, `render()`-Dauer, keine
   JS-Fehler, Standardfilter zeigt ausschließlich grüne Pins voller Größe.
6. Schmaler Pfad: Legende bei geschlossenem Sheet unsichtbar, im offenen Sheet
   scrollbar erreichbar, **nicht durchklickbar** (`elementFromPoint`), Sheet
   weiterhin über der Fußzeile, Breitenwechsel in beide Richtungen.

### Doku-/Backlog-Auswirkungen

- Neuer [ADR-010](../entscheidungen/ADR-010-pin-grammatik-lieferung-und-geschlossen.md).
- `docs/TECHNICAL.md`: Abschnitt „Farbrollen" bekommt die Pin-Grammatik; die
  Zeile „künftig die Pins" ist eingelöst.
- `docs/UMGESETZT.md`: Eintrag mit dem Haken.
- `docs/BACKLOG.md`: R13 abgehakt, die R7-Messung auf 885 aktualisiert.
- [A-6](./A-6-clustering-oder-canvas.md) wird billiger (`preferCanvas: true`),
  [A-2](./A-2-ergebnisliste.md) erbt die Pflicht zur Textfassung der Zustände.

## Definition of Done

Am 2026-07-26 vollständig erfüllt — und mit dem Rückbau nach
[ADR-011](../entscheidungen/ADR-011-pins-wieder-einheitlich.md) wieder ungültig.
Die Optik-Zeilen sind deshalb **gestrichen mit ihrem Ersatz**, nicht gelöscht;
die drei Zeilen ohne Bezug zur Optik gelten unverändert weiter (und wurden beim
Rückbau erneut geprüft).

- ~~[x] Pin-Darstellung wie in der Tabelle oben, alle sechs Kombinationen
      geprüft.~~ → Alle Pins sind wieder Leaflets Standard-Icon; geprüft, dass
      **885 von 885** `L.marker` ohne Style-Optionen sind.
- ~~[x] Nur `--zustand-*` auf den Pins; kein `--marke`/`--aktion`, kein
      `--accent`/`--ok` (per `grep` geprüft), kein Farbwert außerhalb `:root`
      außer den `cssVar()`-Fallbacks.~~ → Auf den Pins liegt **kein** Token mehr;
      `pinTokens()` ist weg, `cssVar()` bleibt mit dem einen `--marke`-Fallback
      in `locateMe()`. Kein Farbwert außerhalb `:root` — weiter per `grep`
      geprüft.
- ~~[x] `delivery === null` ist grau **und** gestrichelt, nie „nein".~~ → Steht
      unverändert in **Badge und Popup** (ADR-007/ADR-009 sind unberührt); der
      Pin sagt dazu nichts mehr.
- ~~[x] Nur sicher geschlossene Restaurants werden abgewertet; unklare Zeiten
      bleiben unverändert.~~ → Kein Restaurant wird auf der Karte mehr
      abgewertet.
- ~~[x] Umriss-Kontrast ≥ 3:1 auf allen geprüften Kachelfarben.~~ → Entfällt: es
      gibt kein selbstgezeichnetes grafisches Objekt mehr, für das WCAG 1.4.11
      greift. (Der Wert bleibt für die nächste Idee dokumentiert: 3,32–12,52:1.)
- ~~[x] Legende in beiden Layout-Pfaden sichtbar und aus derselben Funktion wie
      die Pins erzeugt.~~ → Legende restlos entfernt (DOM, CSS, JS); geprüft,
      dass die Zeichenkette `legende` im ganzen Dokument nicht mehr vorkommt.
- [x] Tests grün: `python3 -m unittest discover -s tests -v` (59, kein Python
      berührt) und die Playwright-Prüfungen, mit synthetischen **und** echten
      Daten — beim Rückbau **27 Prüfungen** in beiden Layout-Pfaden.
- [x] Beide Layout-Pfade geprüft, inklusive Screenshots; `#map` unter 640 px
      unverändert bei 96,1 % (360 px).
- [x] „© OpenStreetMap-Mitwirkende" weiterhin sichtbar (Fußzeile, Attribution
      auf der Karte, JSON-Feld).
- ~~[x] `CACHE_VERSION` auf `v5` hochgezählt.~~ → Der Rückbau ändert wieder
      vorgecachte Dateien, also weiter hoch auf **`v6`** (nie zurück auf `v4`).
- [x] Keine Cookies, kein Tracking, kein `localStorage` dazugekommen.
- ~~[x] Doku aktualisiert, Status in der [Übersicht](./README.md#übersicht) auf
      🏁 erledigt.~~ → Status auf **🗑 verworfen**; ADR-011 neu, ADR-010 auf
      `ersetzt durch`.

## Umsetzungsschritte

Die sieben Schritte waren am 2026-07-26 alle erledigt (✅) — und sind mit
ADR-011 wieder zurückgebaut (↩). Die Liste bleibt stehen, weil sie zeigt, was
der Rückbau anfassen musste:

1. ~~`PIN`-Tabelle, `pinTokens()`, `pinStyle()`, `pinSwatch()`, `buildLegend()`,
   `updateLegendShare()` in `web/index.html`.~~ ↩ alle sechs entfernt.
2. ~~`render()` auf `L.circleMarker` umstellen, Öffnungszustand einmal berechnen
   und durchreichen.~~ ↩ wieder `L.marker`. Die Zeitauswertung **bleibt** hinter
   den billigen Filtern, jetzt zusätzlich kurzgeschlossen über `f.open` — nur
   der Filter braucht das Ergebnis noch, nicht mehr jeder Pin.
3. `BERLIN_FMT` einmalig bauen. ✅ **bleibt** (rein technisch, 62,9 → 5,6 ms).
4. ~~Legenden-Markup ins Filter-Sheet, CSS je Layout-Pfad.~~ ↩ Markup und beide
   CSS-Blöcke entfernt.
5. ~~Standort-Marker als Ring.~~ ↩ wieder Punkt (Radius 8, Füllung 0,6) —
   zulässig, weil die Restaurants wieder Tropfen sind, der Unterschied also
   auch ohne Farbwahrnehmung über die Form trägt.
6. ~~`sw.js`: `CACHE_VERSION` `v5`, Marker-Grafiken raus.~~ ↩ `v6`, die drei
   Marker-Grafiken wieder rein (ohne sie wäre die Karte offline pinlos).
7. Prüfen (Playwright, Screenshots, Python-Suite), Doku und ADR. ✅ erneut.
