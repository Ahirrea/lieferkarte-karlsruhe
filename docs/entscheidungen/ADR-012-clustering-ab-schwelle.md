# ADR-012: Clustering erst ab 300 Treffern — mit Leaflets Standardfarben

**Status:** vorgeschlagen
**Datum:** 2026-07-26

Entscheidung zu [A-6](../anforderungen/A-6-clustering-oder-canvas.md). Ergänzt
[ADR-011](./ADR-011-pins-wieder-einheitlich.md) (Pin-Achsen geschlossen) und
weicht in einem Punkt bewusst von
[ADR-009](./ADR-009-farbrollen-marke-aktion-zustand.md) ab.

## Kontext

Mit dem engen Standardfilter aus
[ADR-007](./ADR-007-standardfilter-liefert-jetzt.md) zeigt die Karte beim Öffnen
21 Restaurants (abends gemessen; mittags ~35). Die 885 sieht nur, wer die Filter
abschaltet — und dort ruckelt es. **Gemessen am 2026-07-26 mit echtem
Leaflet 1.9.4, Handy-Viewport 360 × 740, 4× CPU-Drosselung:**

| | heute (`L.marker`) | mit Clustering (Bulk) |
|---|---|---|
| Klick „alle zeigen" → Bild | 516 ms | **139 ms** |
| `render()` | 386 ms | **68 ms** |
| DOM-Knoten in `#map` | 1 810 | **223** |
| Frame-Median beim Zoomen | 261 ms (~4 fps) | **16,7 ms (60 fps)** |
| Frames über 100 ms | 9 von 12 | **0 von 142** |

**Zur Messmethode, weil sie eine frühere Zahl relativiert:** der `L`-Stub aus
`CLAUDE.md` erzeugt kein DOM, und das Erzeugen von 885 DOM-Knoten *ist* die
Kosten. ADR-011s „`render()` … 0,60 ms im Standardfilter" ist als Messung des
JavaScript-Anteils korrekt, trägt aber keine Aussage über Flüssigkeit. Mit
echtem Leaflet: 3,3 ms im Standardfilter, 116 ms bei 885 (ungedrosselt).
Gemessen wurde deshalb gegen ein lokal abgelegtes echtes Leaflet aus der
npm-Registry — die ist in der Web-Sitzung erreichbar, unpkg nicht.

Zwei naheliegende Wege sind an dieser Messung gescheitert, nicht an einer
Meinung:

- **Sichtfeld-Culling** (keine neue Abhängigkeit, ~15 Zeilen) ist **wertlos**:
  beim Standard-Zoom 12 liegen 618 von 885 im Bild, mit 50 % Puffer 820. Es gibt
  fast nichts wegzulassen; gemessen sogar minimal langsamer als heute
  (592 gegen 516 ms).
- **Canvas** ist die schnellste Variante überhaupt (`render()` 24 ms, DOM 41),
  aber `preferCanvas` wirkt nur auf *Vektor*layer. Ein `L.marker` ist immer ein
  DOM-Icon; Canvas hieße `circleMarker` — also genau die Kreise, die ADR-011
  Stunden zuvor abgelehnt hat. Der Ausgangstext von A-6 („`L.canvas()`, ohne neue
  Lib") beschreibt damit eine Abkürzung, die es nicht gibt.

Bleibt Clustering. Die offene Frage war nicht *ob*, sondern *wann* — und hier
wirkt die Lehre aus [ADR-011](./ADR-011-pins-wieder-einheitlich.md): eine
Gestaltung, die im Standardbild nichts leistet und dort trotzdem als schlechter
empfunden wird, verliert. Mit „immer clustern" werden aus 21 Tropfen **4 Blasen
+ 7 Tropfen** — 14 Restaurants verschwinden hinter Zahlen in einer Ansicht, die
mit 3,3 ms nachweislich flüssig ist. Voller Preis, null Gewinn. Diesmal lag der
Screenshot **vor** der Entscheidung vor, nicht danach.

## Entscheidung

Die Karte fasst Marker zu Blasen zusammen, **sobald 300 oder mehr Restaurants
angezeigt werden**; darunter zeichnet sie unverändert einzelne
Leaflet-Standard-Tropfen. Verwendet wird `leaflet.markercluster` 1.5.3 vom CDN,
die Marker werden per **`addLayers()`** im Bulk gehängt. Die Blasen behalten
**Leaflets Standardfarben**; ihre Trefferfläche wird auf 44 px gebracht.

Bleibt die Bibliothek aus, fällt die Karte dauerhaft auf einzelne Marker zurück.

## Begründung

**300 ist abgelesen, nicht geraten.** Basis-Code, 4× gedrosselt:

| Marker | 150 | 200 | **300** | 450 | 650 | 885 |
|---|---|---|---|---|---|---|
| `render()` | 50,4 ms | 63,8 ms | **93,2 ms** | 164,8 ms | 249,6 ms | 352,1 ms |
| Frame-p95 | 36,9 ms | 40,0 ms | **56,2 ms** | 153,1 ms | 311,2 ms | 394,9 ms |
| Frames > 100 ms | 0 | 0 | **0** | 4 | 5 | 5 |

300 ist die letzte Stufe mit 60 fps und null verworfenen Frames; bei 450 kippen
die ersten vier.

**Das Standardbild bleibt unangetastet — verifiziert, nicht behauptet.** Der
Prototyp liefert im Standardfilter null Blasen und dieselbe DOM-Zahl in `#map`
(81) wie ohne die Bibliothek; nach drei Runden Filter hin und her wieder 81,
keine Reste. Bei 885 gleichzeitig `render()` 81,6 ms, Frame-Median 16,8 ms, null
Frames über 100 ms. Der volle Gewinn ohne den optischen Preis.

**Die Schwelle trifft genau die Problemfälle.** Gemessene Trefferzahlen: Standard
21 · nur Lieferung 64 · Abholung + offen 46 · nur Abholung 238 · nur jetzt offen
168 abends / 427 mittags · alle Filter aus 885. Über der Schwelle liegen nur
„alle Filter aus" und „nur jetzt offen" tagsüber. **Jede Suche und jeder
Küchenstil-Filter bleibt darunter** — wer ein bestimmtes Restaurant sucht,
bekommt es nie als Zahl in einer Blase.

**Warum das trotzdem nicht ADR-011s verworfene Alternative wiederholt.** Dort
wurde „Farbe erst zeigen, wenn die Filter aufgeweitet sind" abgelehnt, weil ein
Pin, dessen *Bedeutung* vom Filterzustand abhängt, in keiner Legende erklärbar
ist. Eine Blase sagt in **jedem** Filterzustand dasselbe — „hier sind n
Restaurants" — und trägt keine verborgene zweite Bedeutung. Erklärt werden muss
nicht ihr Sinn, nur ihr Auftreten. Der akzeptierte Preis: „nur jetzt offen"
clustert mittags (427) und abends (168) unterschiedlich.

**`addLayers()` ist kein Detail:** 68 gegen 264 ms `render()` im Vergleich zu 885
einzelnen `addTo()`. Wer die Abhängigkeit einbaut und einzeln hängt, lässt den
halben Gewinn liegen.

**Die Farbentscheidung fiel gegen die Empfehlung von A-6, und das steht hier,
damit es auffindbar bleibt.** Empfohlen war eine neutrale, zustandsfreie Blase
aus `:root`-Tokens (`--panel` / `--text` / `--border`). Die Produktverantwortung
hat das vertraute OSM-Cluster-Bild gewählt und die Wahl nach Vorlage der
folgenden vier gemessenen Reibungspunkte bestätigt:

| Reibung | Messwert |
|---|---|
| Farbwerte außerhalb von `:root` — Verstoß gegen ADR-009, für den vorbereiteten Dark-Mode unerreichbar | **12** |
| Cluster-Grün `rgb(110,204,57)` gegen `--zustand-ja` #1d6b3a: Grün heißt im Projekt „liefert", auf der Blase „wenige" | Kontrast **3,22** |
| Heller Ring (α 0,6) über Park-/Waldkacheln, WCAG 1.4.11 fordert 3:1 | **1,07** |
| Trefferfläche gegen A-3s Mindestmaß | **40 px** |

Die **12 Farbwerte außerhalb von `:root` sind damit eine bewusste, benannte
Ausnahme von ADR-009**, keine Nachlässigkeit. Zwei Punkte gehören zur
Redlichkeit dazu: der Haupteinwand der Empfehlung — Textlesbarkeit — hat sich
beim Nachrechnen **nicht reproduziert** (`--text` auf den drei Blasenfarben über
vier typische OSM-Kachelfarben: 7,24–11,39:1, durchgehend über 4,5:1) und wird
zurückgezogen; und der Ring-Wert von 1,07 ist bei der neutralen Blase **nicht
besser** (`--border` gegen Land 1,12). Nicht verhandelbar blieb allein die
Trefferfläche: 44 px statt 40 px ist A-3s Maß und eine Größen-, keine Farbfrage.

**Warum überhaupt ein ADR.** Zwei bindende Züge in einem: die erste
Fremdbibliothek neben Leaflet (+8 791 Byte gzip JS auf Leaflets 42 578, also
+22 % aufs Kartenpaket) und eine Regel darüber, was die Karte zeichnet. ADR-011
verlangt für jedes Wiederbelegen der Pin-Achsen ausdrücklich einen neuen ADR;
Clustering belegt keine Achse, liegt aber dicht daneben — und die Ausnahme von
ADR-009 braucht ohnehin einen auffindbaren Ort.

## Verworfene Alternativen

- **Immer clustern:** eine Regel, in jeder Ansicht gleich, leichter erklärbar —
  verschlechtert aber das Standardbild (14 von 21 Restaurants hinter Zahlen) für
  null Gewinn. Am Screenshot abgewählt.
- **Schwelle 150:** clusterte „nur Abholung" (238) und „nur jetzt offen" abends
  (168), beides gemessen flüssig. Unnötig früh.
- **Schwelle 450:** schneidet die Ruckelgrenze bewusst an — dort liegen schon
  4 Frames über 100 ms (p95 153 ms).
- **Sichtfeld-Culling:** an der Messung gescheitert (618 von 885 im Bild bei
  Zoom 12; 592 gegen 516 ms). Wäre erst ab Zoom 15 wirksam — dort, wo es ohnehin
  flüssig ist.
- **Canvas / `preferCanvas` + `circleMarker`:** schnellste Variante, kehrt aber
  ADR-011 um und bringt die abgelehnten Kreise zurück.
- **Marker einzeln in die Cluster-Gruppe hängen:** halber Gewinn (264 statt
  68 ms) für dieselbe Abhängigkeit.
- **Neutrale Blase aus `:root`-Tokens:** die Empfehlung dieser Anforderung, von
  der Produktverantwortung nach Vorlage der Messwerte abgewählt (siehe oben).
- **Legende für die Blasenfarben:** die Zahl erklärt sich selbst, und die
  Bedienzeile ist auf drei Elemente festgelegt
  ([ADR-008](./ADR-008-karte-im-vollbild-overlay-und-sheets.md)).

## Konsequenzen

- **Drei Dateien mehr im Service-Worker-Cache** (`leaflet.markercluster.js`,
  `MarkerCluster.css`, `MarkerCluster.Default.css`), `CACHE_VERSION` → `v7`.
  Sie **müssen** in `CDN_FILES` stehen: fehlt die Bibliothek offline, ist
  `L.markerClusterGroup` `undefined` — härter als die pinlose Karte, vor der
  ADR-011 gewarnt hat. Deshalb zusätzlich der Fallback auf einzelne Marker.
- **Zwei Marker-Layer statt einem.** Beide müssen bei jedem `render()` geleert
  werden, sonst bleiben beim Umschalten Pins stehen.
- **`#count` zählt weiter Restaurants, nie Blasen.** „885 von 885 angezeigt"
  bleibt richtig, auch wenn nur 65 Symbole liegen.
- **A-2 (Ergebnisliste) erbt eine Bedingung:** ein Listeneintrag erreicht seinen
  Pin künftig über `zoomToShowLayer()`, nicht über `openPopup()` allein. Die
  Marker-Objekte müssen erreichbar bleiben.
- **`focusPlace()` bleibt unberührt**, weil das Feed-Popup an Koordinaten hängt.
  Der zugehörige Pin kann in einer Blase stecken; das Popup steht trotzdem
  richtig.
- **Befund R13 bleibt bei A-2.** A-6 löst ihn nicht und beansprucht das nicht:
  eine Blase sagt „hier sind n", nicht „diese liefern".
- **Die Pin-Achsen bleiben geschlossen.** Clustering ist ausdrücklich **keine**
  Erlaubnis, Restaurant-Pins wieder einzufärben, zu verkleinern oder zu
  stricheln — dafür gilt ADR-011 unverändert.
- **Was jetzt nicht passieren darf:** die 12 Cluster-Farbwerte als Präzedenzfall
  für weitere Farben außerhalb von `:root` zu lesen. Die Ausnahme gilt für die
  ausgelieferte Datei einer Fremdbibliothek, nicht für eigenes CSS.
- **Der `L`-Stub reicht für diese Anforderung nicht.** Tempo, Trefferflächen und
  Layout sind nur gegen echtes Leaflet prüfbar (lokal aus der npm-Registry). Ein
  `markerClusterGroup`-Stub macht die Prüfungen formal grün und sagt inhaltlich
  nichts.
