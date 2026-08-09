# ADR-013: Die Ergebnisliste ist der barrierefreie Hauptweg — die Karte wird für Tastatur und Screenreader dekorativ

**Status:** vorgeschlagen
**Datum:** 2026-08-09

## Kontext

Die Karte galt im Projekt bisher als „für Tastatur und Screenreader leer" — so
steht es seit dem UI/UX-Review vom Juli 2026 im Befund **R6** und im Ausgangstext
von [A-2](../anforderungen/A-2-ergebnisliste.md). Gemessen am 2026-08-09 gegen
echtes Leaflet 1.9.4 (Chromium, 393 × 851, echte `web/restaurants.json`, 884
Restaurants) ist das Gegenteil der Fall, und zwar in einer Weise, die schlechter
ist als „leer":

| Messung | Wert |
|---|---|
| Marker im DOM (alle Filter aus) | 884 |
| davon fokussierbar (`tabindex="0"`, `role="button"`) | **884** |
| `alt`-Attribut, alle Marker identisch | `"Marker"` |
| Tab-Stopps im ganzen Dokument | 894 — davon **884 Marker (98,9 %)** |
| Tab-Stopps ohne die Karte | 10 |
| Tabs vom fokussierten Marker bis zum Inhalt seines geöffneten Popups | **884** |

Der letzte Wert ist der Kern: `Enter` auf einem Marker öffnet das Popup, aber
Leaflets `popupPane` liegt im DOM **hinter** dem `markerPane`. Wer den Link „Zur
Website & bestellen" per Tastatur erreichen will, muss durch alle übrigen Marker
tabben — im Standardfilter 53, ohne Filter 884. Die Kernschleife des Produkts
(PRD §5, Schritt 3: „Restaurant antippen → direkter Link → bestellen") ist per
Tastatur damit praktisch nicht abschließbar.

Gleichzeitig ist die Zustandsinformation nirgends ohne Interaktion sichtbar
(Befund **R13**). Der Versuch, sie auf die Pins zu legen, ist am 2026-07-26
gescheitert und wurde mit
[ADR-011](./ADR-011-pins-wieder-einheitlich.md) zurückgenommen; dort wurde
festgehalten, dass R13 künftig über die Ergebnisliste zu lösen ist — „eine Liste
hat beliebig viele Worte, ein 20-px-Punkt vier Kanäle, und für Screenreader
existieren farbige Kreise ohnehin nicht".

## Entscheidung

Die Ergebnisliste wird der barrierefreie Hauptweg zu den Daten: sie zeigt
dieselben gefilterten Restaurants wie die Karte, nach Entfernung zur Kartenmitte
sortiert, mit Lieferung, Abholung und „jetzt geöffnet" **in Worten**. Die Karte
verlässt im Gegenzug die Tab-Kette — die Restaurant-Marker bekommen
`keyboard: false` und ein leeres `alt`, sind also für Tastatur und Screenreader
dekorativ. Unter 640 px ist die Liste ein Bottom Sheet, darüber ein dauerhaft
sichtbares Panel rechts neben der Karte.

## Begründung

**Die Karte war nie der barrierefreie Weg, sie sah nur so aus.** 884 gleich
benannte Schaltflächen sind keine Bedienbarkeit, sondern eine Sperre: sie
verlängern jede Tab-Reise durch das Dokument um zwei Größenordnungen und führen
zu einem Popup, dessen Inhalt wiederum 884 Stopps entfernt liegt. Die Alternative
„Marker behalten den Fokus, bekommen aber den Restaurantnamen als `alt`" hebt nur
die Namensgleichheit auf und lässt die beiden strukturellen Probleme stehen.

**Die Liste kann, was der Pin nicht kann.** Sie trägt drei Zustände als Text,
sortiert nach Entfernung, ist scrollbar, durchsuchbar und für Screenreader eine
Liste mit bekannter Semantik. Das ist genau die Begründung, mit der ADR-011 R13
hierher verschoben hat — sie wird jetzt eingelöst.

**Auf dem Desktop ist Platz, auf dem Handy nicht.** Gemessen: ein Panel von
20 rem lässt bei 1280 px noch 960 px Karte (75 %), bei 1920 px 1600 px (83,3 %).
Unter 640 px gilt dagegen unverändert
[ADR-008](./ADR-008-karte-im-vollbild-overlay-und-sheets.md) — die Karte ist das
Vollbild, alles Weitere ist ein Sheet. Ein viertes Element in der Bedienzeile ist
ausgeschlossen und auch nachgemessen: es bricht die Zeile von 44 px auf 96 px,
bei 360 px **und** bei 393 px. Der Öffner sitzt deshalb in `#mapControls`, wo
schon „In meiner Nähe" liegt.

**Der Preis ist benannt, nicht weggeredet.** `keyboard: false` und `alt: ""` sind
Optionen an `L.marker`, und
[ADR-011](./ADR-011-pins-wieder-einheitlich.md) verlangt wörtlich
`L.marker([r.lat, r.lng])` **ohne Optionen**. Diese Entscheidung weicht davon
ausdrücklich ab. Sie kehrt ADR-011 nicht um: dessen Gegenstand ist das
*Aussehen* der Pins („Colouring, resizing or dashing the pins again … needs a new
ADR"), und daran ändert sich nichts — die Pins bleiben Leaflets Standard-Icon,
Pin für Pin identisch. Betroffen ist allein, ob die Karte in der Tab-Kette steht.

## Verworfene Alternativen

- **Marker behalten den Fokus und bekommen `alt: r.name`:** macht aus 884
  gleichnamigen Stopps 884 benannte. Die Karte bleibt 98,7 % der Tab-Kette, und
  der Bestell-Link im geöffneten Popup liegt weiter 884 Tabs entfernt. Behebt das
  Symptom, nicht die Struktur.
- **Nichts an der Karte ändern, nur die Liste dazubauen:** der Befund bliebe zur
  Hälfte stehen, und es gäbe zwei konkurrierende Tastaturwege zu denselben Daten,
  von denen der prominentere der unbrauchbare ist.
- **Popup nach dem Öffnen fokussieren (Fokus-Falle statt Tab-Reise):** löst die
  884 Tabs bis zum Link, nicht aber die 884 Stopps davor, und bringt eine
  Fokus-Verwaltung in einen Popup-Mechanismus, der bewusst nicht modal ist
  ([ADR-008](./ADR-008-karte-im-vollbild-overlay-und-sheets.md)).
- **Eigene, kartenlose Seite `liste.html`:** technisch die sauberste Trennung —
  aber Filterlogik, `openStateNow()` und die URL-Parameter aus A-8 existierten
  dann zweimal und würden auseinanderlaufen. Genau diese Falle beschreibt
  [ADR-004](./ADR-004-oeffnungszeiten-eigener-parser.md) für den
  Öffnungszeiten-Parser: eine zweite Auswertung erzeugt still andere Zahlen.
- **Liste auch auf dem Handy dauerhaft sichtbar (eingeklappte Leiste mit Peek):**
  löst R13 auch mobil ohne Interaktion, widerspricht aber ADR-008 zweifach — „die
  Karte ist das Vollbild" und „Sheets mit mehreren Rastpunkten" ist dort
  ausdrücklich verworfen. Das wäre eine Umkehrung von ADR-008, kein Feinschliff.
- **Liste auch auf dem Desktop nur auf Klick:** hätte die Karte unangetastet
  gelassen, aber R13 bliebe in beiden Pfaden einen Klick entfernt — das
  Standardbild gewänne nichts.

## Konsequenzen

- **Die Liste ist ab jetzt der Ort, an dem Zustände ohne Interaktion sichtbar
  sind.** Wer eine Zustandsinformation neu anzeigen will, baut sie dort ein und
  nicht auf den Pins; die Pin-Achsen bleiben nach ADR-011 geschlossen.
- **Die Karte darf nicht wieder in die Tab-Kette rutschen.** Jeder künftige
  `L.marker`-Aufruf trägt `keyboard: false` und `alt: ""`; ein Patch, der die
  Optionen entfernt, macht 884 Stopps still wieder auf. Das ist eine Prüfzeile im
  Testplan von A-2, keine Absicht.
- **Die Marker-Optionen sind eine benannte Ausnahme von ADR-011s Wortlaut.**
  ADR-011 bleibt in Kraft und unverändert — der Ausnahmegrund ist hier
  festgehalten, damit später niemand `{ keyboard: false, alt: "" }` für einen
  durchgerutschten Verstoß hält und ihn „aufräumt".
- **Es gibt weiterhin genau zwei Layout-Pfade**, aber der Desktop-Pfad hat ab
  jetzt eine Spalte mehr. Jede UI-Änderung ist in beiden zu prüfen, und der
  Desktop-Pfad hat zwei Zustände (Liste offen/zu), weil das Panel abschaltbar
  bleibt.
- **`#mapControls` und `#feed` müssen dem Panel ausweichen.** Beide sind
  `position: fixed` und rechts verankert; über der offenen Liste lägen sie sonst
  auf dem Panel statt auf der Karte.
- **Die Liste zeigt höchstens 300 Zeilen** (Details und die dabei verworfene
  Empfehlung in [A-2](../anforderungen/A-2-ergebnisliste.md), Entscheidung 5).
  Damit können Listenlänge und `#count` auseinanderfallen; die Liste muss den
  Unterschied selbst benennen, sonst wirkt sie unvollständig.
- Kehrt sich „die Karte ist für Tastatur dekorativ" jemals um, braucht das einen
  neuen ADR — nicht ein entferntes Options-Objekt.
