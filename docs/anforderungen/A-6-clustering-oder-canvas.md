# A-6 Marker-Clustering ab 300 Treffern

[← Anforderungen](./README.md) · [Prozess](../PROZESS.md)
· Status siehe [Übersicht](./README.md#übersicht)

**User Story:** Als Handy-Nutzerin möchte ich, dass die Karte flüssig bleibt,
auch wenn alle Restaurants gezeigt werden — damit ich beim Aufweiten der Filter
nicht auf ein ruckelndes Bild starre.

**Verfeinert am:** 2026-07-26
**Bedient PRD:** „Erfolgskriterien" — unter 30 Sekunden zum Ergebnis; und
„Kernschleife" Schritt 2 (Ansicht verengen, ohne dass die Karte einfriert)
**Eingeschränkt durch:** [ADR-011](../entscheidungen/ADR-011-pins-wieder-einheitlich.md)
(Pin-Achsen geschlossen) · [ADR-009](../entscheidungen/ADR-009-farbrollen-marke-aktion-zustand.md)
(Farbrollen) · [ADR-006](../entscheidungen/ADR-006-pwa-network-first.md) (PWA-Cache)
· [ADR-002](../entscheidungen/ADR-002-kein-backend-daten-im-repo.md) (kein Build-Schritt)
· neu: [ADR-012](../entscheidungen/ADR-012-clustering-ab-schwelle.md)

## Ausgangstext (aus `backlog/IDEEN.md`, Idee 6)

> Der zweite Teil von R7 – der erste ist eine Aufgabe, siehe
> [`BACKLOG.md`](../BACKLOG.md) (Abschnitt „Mittel"). Mit entschärftem
> Standardfilter zeichnet die Karte 883 statt 63 Marker. Ob Clustering
> (`markercluster`, wäre eine zusätzliche Abhängigkeit) oder ein Canvas-Renderer
> (`L.canvas()`, ohne neue Lib) besser passt, ist offen – und sinnvoll erst zu
> entscheiden, wenn [A-1](./A-1-standardfilter-entschaerfen.md) entschieden ist.

**Drei Zahlen und eine Annahme daraus sind überholt** (alles neu gemessen am
2026-07-26, So. 22:48 Berliner Zeit, gegen die echte `web/restaurants.json`):

- ~~883 statt 63 Marker~~ → **885 statt 21**. Der Standardfilter ist nicht
  entschärft worden, sondern enger geworden ([ADR-007](../entscheidungen/ADR-007-standardfilter-liefert-jetzt.md)):
  „liefert **und** jetzt offen" ergibt abends 21, nur „liefert" ergibt 64.
- ~~`L.canvas()`, ohne neue Lib~~ → **technisch versperrt.** `preferCanvas`
  wirkt ausschließlich auf *Vektor*layer. Ein `L.marker` ist immer ein
  DOM-Icon; Canvas hieße `circleMarker` — also genau die Kreise, die
  [ADR-011](../entscheidungen/ADR-011-pins-wieder-einheitlich.md) Stunden
  zuvor abgewählt hat. Kein neuer Feinschliff, sondern eine Umkehrung.
- ~~„sinnvoll erst zu entscheiden, wenn A-1 entschieden ist"~~ → A-1 ist am
  2026-07-25 entschieden; die Blockade ist weg.

## Andockpunkte im Code

| Ort | Was dort steht | Rolle für A-6 |
|---|---|---|
| `web/index.html:924` | `const layer = L.layerGroup().addTo(map);` | **der Eingriffspunkt.** Wird zu zwei Layern (einfach + Cluster) plus Auswahlfunktion. |
| `web/index.html:1661` `render()` | Filterschleife, am Ende `updateCount()` | Marker werden gesammelt statt einzeln gehängt; der Layer wird **nach** dem Zählen gewählt, weil erst dann die Trefferzahl feststeht. |
| `web/index.html:1702` | `L.marker(…).bindPopup(() => popupHtml(r), POPUP_OPTS).addTo(layer)` | bleibt inhaltlich unangetastet — faules Popup (R7) und Standard-Icon (ADR-011) sind gesetzt. Nur `.addTo(layer)` wird zum Sammeln. |
| `web/index.html:1665` | `layer.clearLayers()` | muss **beide** Layer leeren, sonst bleiben beim Umschalten Pins stehen. |
| `web/index.html:1764` `locateMe()` | `L.circleMarker` mit `--marke` | unberührt. Der Standort bleibt der einzige Kreis (ADR-011). |
| `web/index.html:1482` `focusPlace()` | `L.popup().setLatLng().openOn(map)` | unberührt — das Feed-Popup hängt an Koordinaten, nicht am Marker, funktioniert also auch, wenn der Pin in einer Blase steckt. |
| `web/sw.js:58` `CDN_FILES` | fünf Leaflet-Dateien, `CACHE_VERSION = "v6"` | drei Einträge dazu, `v7`. |
| `web/index.html:27–33` | zwei unpkg-Tags mit `integrity` | drei Tags dazu, ebenfalls mit SRI. |

**Wiederverwendbar:** die gesamte Filterlogik, `popupHtml()`, die
URL-Parameter (A-8), `updateCount()`, `updateEmptyState()`. **Es fehlt:** die
Bibliothek, die Layer-Umschaltung, drei Cache-Einträge.

**Was ausdrücklich *nicht* fehlt:** eine Datenmodell- oder Pipeline-Änderung.
`scanner.py`, `export.py`, das DB-Schema und `restaurants.json` bleiben
unverändert — A-6 ist rein visuell.

## Spannung zu Nicht-Zielen — und Auflösung

**1. „Kein Backend, keine laufenden Kosten" (PRD) / kein Build-Schritt (ADR-002).**
Kein Konflikt: `leaflet.markercluster` ist eine statische Datei vom
CDN, genau wie Leaflet selbst. Kein npm im Repo, kein Bundler, kein Server.

**2. Eine neue Fremdabhängigkeit.** Bisher gab es genau eine (Leaflet).
Gewicht gemessen: **8 791 Byte gzip** JS + **690 Byte** CSS gegen Leaflets
42 578 Byte — **+22 %** auf das Kartenpaket. Aufgelöst: der Zugewinn ist
gemessen groß (unten), die Bibliothek ist der De-facto-Standard für genau
diesen Zweck, und sie liegt bei derselben Quelle unter derselben Lizenz-Logik.
Trotzdem eine bindende Entscheidung → [ADR-012](../entscheidungen/ADR-012-clustering-ab-schwelle.md).

**3. Offline-Fähigkeit (ADR-006).** Eine per CDN geladene Bibliothek, die nicht
im `SHELL_CACHE` steht, macht die Karte offline **kaputt** — nicht nur pinlos,
sondern `L.markerClusterGroup` ist `undefined` und `render()` wirft. Aufgelöst:
die drei Dateien gehören in `CDN_FILES`, `CACHE_VERSION` auf `v7`. Das ist
dieselbe Falle, die ADR-011 für die drei Marker-Grafiken festgehalten hat, nur
mit härterer Folge.

**4. Farbrollen (ADR-009): „kein Farbwert außerhalb von `:root`".**
Echter Konflikt, **bewusst in Kauf genommen** — siehe Entscheidung 3. Vier
gemessene Reibungspunkte, nicht einer:

| Reibung | Messwert |
|---|---|
| Farbwerte außerhalb von `:root`, für den vorbereiteten Dark-Mode unerreichbar | **12** |
| Cluster-Grün `rgb(110,204,57)` gegen `--zustand-ja` #1d6b3a — Grün heißt im Projekt „liefert", hier „wenige" | Kontrast **3,22** |
| Heller Ring (α 0,6) über Park-/Waldkacheln — der Blasenrand löst sich auf; WCAG 1.4.11 fordert 3:1 | **1,07** |
| Trefferfläche gegen A-3s Mindestmaß von 44 px | **40 px** |

**Was hier *nicht* das Problem ist,** obwohl es der naheliegende Einwand wäre:
die **Textlesbarkeit trägt**. `--text` auf den drei Blasenfarben, komponiert über
vier typische OSM-Kachelfarben, liegt bei **7,24–11,39:1** — durchgehend über
4,5:1. Der Einwand, mit dem die neutrale Blase empfohlen wurde, hat sich beim
Nachrechnen nicht reproduziert und wird hier ausdrücklich zurückgezogen. Ebenso
ehrlich: der Ring-Wert von 1,07 ist bei der neutralen Blase **nicht besser**
(`--border` gegen Land 1,12) — auf dieser Achse gewinnt keine der Varianten.

**5. Pin-Achsen sind geschlossen (ADR-011).** Kein Konflikt, aber die Grenze
muss benannt sein: Clustering färbt, verkleinert oder strichelt **keinen
Restaurant-Pin**. Es fasst mehrere Pins zu einem Bedienelement zusammen — eine
*Mengen*aussage, keine Zustandsaussage. Unterhalb der Schwelle ist das Bild Pin
für Pin identisch mit heute (verifiziert: DOM in `#map` **81** in beiden Fällen).
Weil die Grenze dünn ist, hält [ADR-012](../entscheidungen/ADR-012-clustering-ab-schwelle.md)
sie fest, statt sie einem späteren Patch zu überlassen.

**6. Kein Tracking, keine Speicherung.** Unberührt. Die Schwelle wird bei jedem
`render()` neu aus der Trefferzahl gerechnet; nichts wird persistiert, kein
URL-Parameter kommt dazu.

## Die Messung

Alles am 2026-07-26 gemessen, Chromium 360 × 740 (Handy-Viewport), gegen die
echte `web/restaurants.json` (885 Restaurants, alle mit Koordinaten).

**Methodisch wichtig — und ein Bruch mit der bisherigen Praxis:** gemessen wurde
gegen **echtes Leaflet 1.9.4**, lokal aus der npm-Registry geholt und neben die
Seite gelegt (unpkg ist in der Web-Sitzung blockiert, die Registry nicht). Der
`L`-Stub aus `CLAUDE.md` **kann diese Anforderung grundsätzlich nicht messen**:
er erzeugt kein DOM, und genau das Erzeugen von 885 DOM-Knoten *ist* die Kosten.
Deshalb ist die Zahl in ADR-011 („`render()` … **0,60 ms** im Standardfilter")
für A-6 nicht belastbar — sie ist als Messung des JS-Anteils korrekt, trägt aber
keine Aussage über Flüssigkeit. Mit echtem Leaflet: **3,3 ms** im Standardfilter,
**116 ms** bei 885 (ungedrosselt).

Die Nutzerin hat kein Rechenzentrum in der Hand, deshalb alle Vergleichswerte
zusätzlich mit **4× CPU-Drosselung** (`Emulation.setCPUThrottlingRate`) als
Näherung an ein Mittelklasse-Telefon.

### Die Optionen bei 885 Markern, 4× gedrosselt

| Variante | Klick → Bild | `render()` | DOM in `#map` | Frame-Median | Frame-p95 | Frames > 100 ms |
|---|---|---|---|---|---|---|
| **heute** (`L.marker`) | 516 ms | 386 ms | 1 810 | 261 ms | 810 ms | 9 von 12 |
| Cluster, einzeln gehängt | 488 ms | 264 ms | 223 | 16,6 ms | 30 ms | 0 von 152 |
| **Cluster, `addLayers()` im Bulk** | **139 ms** | **68 ms** | **223** | **16,7 ms** | **36 ms** | **0 von 142** |
| Sichtfeld-Culling (eigener Code) | 592 ms | 345 ms | 1 692 | 115 ms | 441 ms | 13 von 21 |
| Canvas (`circleMarker`) | 116 ms | 24 ms | 41 | 16,7 ms | 18 ms | 0 von 164 |

Frame-Median 261 ms heißt: beim Zoomen kamen in knapp drei Sekunden **12 Bilder**
an, also ~4 fps. Mit Cluster sind es 142 Bilder bei 16,7 ms — die 60 fps, die das
Gerät hergibt. Das ist der Kern der Anforderung, und er ist kein Gefühl.

**Zwei Optionen sind an der Messung gestorben, nicht an einer Meinung:**

- **Sichtfeld-Culling war die attraktivste Idee** (keine Abhängigkeit, ~15 Zeilen)
  und ist **wertlos**: beim Standard-Zoom 12 liegen **618 von 885** im Bild, mit
  50 % Puffer **820**. Es gibt fast nichts wegzulassen. Gemessen sogar minimal
  *langsamer* als heute (592 gegen 516 ms). Erst ab Zoom 15 (117 von 885) würde
  es tragen — also genau dort, wo es ohnehin flüssig ist.
  Im Bild: Zoom 11 → 820 · 12 → 618 · 13 → 389 · 14 → 261 · 15 → 117.
- **Bulk statt einzeln ist kein Detail:** `addLayers()` gegen 885 × `addTo()`
  halbiert `render()` (68 statt 264 ms). Wer die Bibliothek einbaut und die
  Marker weiter einzeln hängt, holt sich die Abhängigkeit und lässt den halben
  Gewinn liegen.

### Wo das Ruckeln beginnt (Grundlage der Schwelle 300)

Basis-Code, 4× gedrosselt, Datensatz künstlich gekürzt:

| Marker | 25 | 50 | 100 | 150 | 200 | **300** | 450 | 650 | 885 |
|---|---|---|---|---|---|---|---|---|---|
| `render()` | 10,1 | 21,3 | 36,1 | 50,4 | 63,8 | **93,2** | 164,8 | 249,6 | 352,1 |
| Frame-Median | 16,7 | 16,6 | 16,7 | 16,7 | 16,9 | **17,1** | 17,3 | 16,9 | 244,4 |
| Frame-p95 | 18,1 | 18,0 | 24,5 | 36,9 | 40,0 | **56,2** | 153,1 | 311,2 | 394,9 |
| Frames > 100 ms | 0 | 0 | 0 | 0 | 0 | **0** | 4 | 5 | 5 |

**300 ist die letzte gemessene Stufe mit 60 fps und null verworfenen Frames.**
Bei 450 kippen die ersten vier. Die Schwelle ist damit abgelesen, nicht geraten.

### Trefferzahlen je Filterzustand — wie oft die Schwelle überhaupt greift

`openStateNow()` lebt nur im Frontend ([ADR-004](../entscheidungen/ADR-004-oeffnungszeiten-eigener-parser.md)),
also im Browser ausgewertet, nicht in Python nachgebaut:

| Filterzustand | Treffer | ≥ 300? |
|---|---|---|
| **Standard: liefert + jetzt offen** | **21** | nein |
| nur Lieferung | 64 | nein |
| Abholung + jetzt offen | 46 | nein |
| nur jetzt offen | 168 (abends) · **427 mittags** | tagesabhängig |
| nur Abholung | 238 | nein |
| **alle Filter aus** | **885** | ja |

Tagdaten: `delivery` 64 ja / 47 nein / **774 unbekannt** (87,5 %) ·
`takeaway` 238 / 8 / 639 · `opening_hours` bei 742 von 885 gesetzt.

Zwei Folgerungen: **jeder Sucheingriff bleibt unter der Schwelle** (Suche und
Küchenstil-Filter verengen immer), sieht also echte Pins — wer ein bestimmtes
Restaurant sucht, bekommt es nie als Zahl in einer Blase. Und **„nur jetzt
offen" wandert über die Schwelle**: mittags 427 (Messung aus
[ADR-010](../entscheidungen/ADR-010-pin-grammatik-lieferung-und-geschlossen.md)),
abends 168. Dieselbe Filterwahl clustert also mittags und abends nicht — der
bekannte Preis der Entscheidung 1, unten festgehalten.

### Die Schwellen-Variante, praktisch geprüft

Prototyp mit `CLUSTER_AB = 300`, beide Layer, drei Runden hin und her:

| Zustand | Treffer | Blasen | Tropfen | DOM in `#map` |
|---|---|---|---|---|
| Standardfilter | 21 | **0** | **21** | **81** — identisch mit heute |
| alle Filter aus | 885 | 53 | 12 | 169 |
| zurück auf Standard (3 ×) | 21 | 0 | 21 | 81 — keine Reste |

Und bei 885, 4× gedrosselt: `render()` **81,6 ms**, Frame-Median **16,8 ms**,
p95 **38,9 ms**, **null** Frames über 100 ms. Der volle Gewinn, ohne das
Standardbild anzufassen.

## Entscheidungen (mit Begründung)

**1. Geclustert wird erst ab 300 Treffern, nicht immer.**
Das Standardbild bleibt Pin für Pin wie heute. Grund ist die Lehre aus A-5, hier
vorab am Screenshot geprüft: mit „immer clustern" werden aus 21 Tropfen **4
Blasen + 7 Tropfen** — 14 Restaurants verschwinden hinter Zahlen in einer
Ansicht, die mit 3,3 ms nachweislich nicht ruckelt. Voller optischer Preis, null
Gewinn — genau das Muster, an dem A-5 gescheitert ist. Der Schwellwert **300**
ist die letzte Stufe mit 60 fps und null verworfenen Frames (Tabelle oben).
*Verworfen:* „immer clustern" (einfacher und in jeder Ansicht gleich, aber
verschlechtert das Hauptbild), 150 (unnötig früh: clusterte „nur Abholung" mit
238 Treffern, die messbar flüssig sind), 450 (schneidet die Ruckelgrenze
bewusst an — 4 Frames über 100 ms).
*Bekannter Preis, ausdrücklich akzeptiert:* das Verhalten hängt an der
Trefferzahl, „nur jetzt offen" clustert deshalb mittags (427) und abends (168)
unterschiedlich. Das ist schwächer als ADR-011s Einwand gegen filterabhängige
Pins („in keiner Legende erklärbar"), weil eine Blase in **jedem** Filterzustand
dasselbe sagt — „hier sind n Restaurants" — und keine verborgene zweite
Bedeutung trägt. Erklärt werden muss nicht ihr Sinn, nur ihr Auftreten.

**2. `leaflet.markercluster` 1.5.3 vom CDN, Marker per `addLayers()` im Bulk.**
Gemessen 68 statt 264 ms `render()` gegenüber einzelnem Hängen.
*Verworfen:* Sichtfeld-Culling (an der Messung gescheitert, 618 von 885 sind im
Bild); Canvas (`preferCanvas` + `circleMarker`) — die schnellste Variante
überhaupt, aber sie kehrt ADR-011 um und bringt die abgelehnten Kreise zurück.

**3. Die Cluster-Blasen behalten Leaflets Standardfarben — gegen die
Empfehlung dieser Anforderung.** Empfohlen war eine neutrale, zustandsfreie
Blase aus `:root`-Tokens (`--panel` / `--text` / `--border`). Die
Produktverantwortung hat nach Vorlage der vier gemessenen Reibungspunkte
(oben) und der Screenshots das vertraute OSM-Cluster-Bild gewählt und die
Entscheidung auf Rückfrage bestätigt. Damit gilt: `MarkerCluster.Default.css`
wird geladen wie ausgeliefert, und die **12 Farbwerte außerhalb von `:root`
sind eine bewusste, dokumentierte Ausnahme von ADR-009** — festgehalten in
[ADR-012](../entscheidungen/ADR-012-clustering-ab-schwelle.md) samt der
verworfenen Empfehlung, damit später nachvollziehbar bleibt, dass die
Abweichung gesehen und gewollt war und nicht durchgerutscht ist.
*Nicht verhandelbar bleibt die Trefferfläche:* 44 px statt Leaflets 40 px, das
ist A-3s Maß und eine Größen-, keine Farbfrage.

**4. Eigener ADR.** Zwei bindende Züge in einem: die erste Fremdbibliothek neben
Leaflet und eine Regel darüber, was die Karte überhaupt zeichnet. ADR-011
verlangt für jedes Wiederbelegen der Pin-Achsen ausdrücklich einen neuen ADR;
Clustering belegt keine Achse, liegt aber dicht daneben.

## Umfang / Nicht-Umfang

- **Rein:** zwei Layer plus Auswahl nach Trefferzahl in `render()`; Bibliothek
  per CDN mit SRI; drei Einträge in `CDN_FILES` und `CACHE_VERSION` → `v7`;
  Trefferfläche der Blase auf 44 px; barrierefreier Name der Blase;
  Tap auf Blase zoomt hinein, `spiderfyOnMaxZoom` bei Deckungsgleichheit.
- **Raus:** Sichtfeld-Culling (gemessen wertlos) · Canvas/Vektor-Pins (ADR-011)
  · jede Änderung am Aussehen der Restaurant-Pins (ADR-011) · Legende für die
  Blasenfarben (eine Zahl erklärt sich selbst; eine Legende für Mengenstufen
  wäre neues Bedien-Inventar in einer auf drei Elemente festgelegten Zeile,
  ADR-008) · Pipeline, DB, JSON · Cluster-Bedienung in der Ergebnisliste (das
  ist A-2; die Schnittstelle wird unten nur vorbereitet).

## Spezifikation

### UX-Ablauf und Zustände

1. **Unter 300 Treffern** (Standardfilter, jede Suche, jeder Küchenstil-Filter):
   unverändert einzelne Leaflet-Tropfen. Kein sichtbarer Unterschied zu heute.
2. **Ab 300 Treffern** (alle Filter aus; „nur jetzt offen" tagsüber): Blasen mit
   Anzahl, dazu einzelne Tropfen für alles, was allein steht (bei 885 gemessen:
   53 Blasen + 12 Tropfen).
3. **Tap auf eine Blase:** Karte zoomt auf deren Inhalt (`zoomToBoundsOnClick`,
   Standard). Liegen Marker auf demselben Punkt, fächert `spiderfyOnMaxZoom` sie
   beim maximalen Zoom auf.
4. **Beim Hineinzoomen** lösen sich Blasen von selbst auf — Leaflets Verhalten,
   nichts zu bauen.
5. **Überschreiten der Schwelle** durch Filterwechsel: das Bild wechselt zwischen
   Tropfen und Blasen. Der Wechsel passiert im selben `render()` wie die
   Trefferzahl, ist also nicht als eigener Sprung wahrnehmbar.
6. **Leerzustand und Trefferzahl** bleiben unberührt: `updateCount()` zählt
   weiter **Restaurants**, nie Blasen. „885 von 885 angezeigt" bleibt richtig,
   auch wenn nur 65 Symbole liegen.

### Interaktion mit Bestehendem

- **Filter, Suche, URL-Parameter (A-8):** unberührt. Die Schwelle liest nur das
  Ergebnis.
- **`focusPlace()` (Feed-Klick):** funktioniert weiter, weil das Popup an
  Koordinaten hängt, nicht am Marker — geprüft am Code, nicht angenommen. Der
  zugehörige Pin kann dabei in einer Blase stecken; das Popup steht trotzdem an
  der richtigen Stelle. Bewusst so gelassen: der Feed hat immer weniger als 300
  Einträge, der Fall tritt nur bei aufgeweiteten Filtern auf.
- **`locateMe()`:** unberührt. Der Standort-Kreis bleibt das einzige
  Nicht-Tropfen-Symbol neben den Blasen; Blasen sind rund, der Standort ist
  kleiner, gefüllt und in `--marke` — Verwechslung unwahrscheinlich, aber ein
  Punkt für die Sichtprüfung.
- **A-2 (Ergebnisliste):** wird später aus der Liste einen Pin ansteuern wollen.
  Mit Clustering geht das nicht mehr über `openPopup()` allein, sondern über
  `layerCluster.zoomToShowLayer(marker, cb)`. Deshalb hier nur der Hinweis und
  die Bedingung, die A-2 braucht: **die Marker-Objekte müssen erreichbar
  bleiben** (nicht nur ihre Koordinaten). Keine Umsetzung in A-6.
- **Zwei Layout-Pfade (ADR-008):** Blasen liegen im Marker-Pane *innerhalb*
  `#map`, sind also von der Overlay-Regel nicht betroffen — sie sind Leaflets
  eigene Kinder und sollen dessen Pointer-Events bekommen. Zu prüfen ist nur,
  dass eine Blase nicht unter `#mapControls` oder der Fußzeile klemmt.

### Externe Abhängigkeit und Fallback

Drei Dateien, `leaflet.markercluster@1.5.3`, mit SRI (aus dem npm-Tarball
berechnet — **beim Einbau gegen die unpkg-Antwort verifizieren**, in dieser
Sitzung ist unpkg blockiert):

```
leaflet.markercluster.js    sha256-Hk4dIpcqOSb0hZjgyvFOP+cEmDXUKKNE/tT542ZbNQg=
MarkerCluster.css           sha256-YU3qCpj/P06tdPBJGPax0bm6Q1wltfwjsho5TR4+TYc=
MarkerCluster.Default.css   sha256-YSWCMtmNZNwqex4CEw1nQhvFub2lmU7vcCKP+XVwwXA=
```

**Fallback, wenn die Bibliothek nicht lädt** (CDN-Ausfall, SRI-Fehlschlag,
Offline vor dem ersten Cachen): `L.markerClusterGroup` ist `undefined` und
`render()` würde werfen — die Karte wäre komplett leer, schlimmer als heute.
Deshalb **Pflicht:** die Layer-Wahl prüft `typeof L.markerClusterGroup ===
"function"` und fällt sonst dauerhaft auf `layerEinfach` zurück. Dann ruckelt
es bei 885 wie heute, aber alles funktioniert. Die Bedingung wird einmal beim
Start ausgewertet, nicht je `render()`.

### Randfälle und Fehlerbehandlung

| Fall | Verhalten |
|---|---|
| Genau 300 Treffer | Clustern (`>= CLUSTER_AB`), damit die Grenze eindeutig ist. |
| Umschalten hin und her | Beide Layer werden geleert **und** der nicht gewählte von der Karte genommen; verifiziert über drei Runden, keine Reste (DOM 81 → 169 → 81). |
| Bibliothek fehlt | dauerhaft `layerEinfach`, siehe oben. |
| Offener Popup beim Umschalten | Leaflet schließt ihn mit dem Layer. Akzeptiert: das Umschalten setzt einen Filterwechsel voraus, der die Auswahl ohnehin verändert. |
| 0 Treffer | unverändert; Leerzustand greift wie heute, kein Layer trägt etwas. |
| Restaurants ohne Koordinaten | fallen wie heute vor dem Marker-Bau heraus (aktuell 0 von 885). |
| Blase unter Bedienzeile/Fußzeile | Sichtprüfung in beiden Layout-Pfaden. |

### Barrierefreiheit

- Die Blase braucht einen **vorlesbaren Namen**: „*n* Restaurants in diesem
  Bereich" (`aria-label` bzw. `title` auf dem `divIcon`-Inhalt), nicht die nackte
  Zahl. Ohne das ist sie für Screenreader eine Ziffer ohne Bezug.
- **Trefferfläche 44 px** (A-3), nicht Leaflets 40 px — per CSS über die
  Blasenklassen, ohne die Farbwerte anzutasten.
- **Keine Verschlechterung gegenüber heute:** die Karte ist für Screenreader
  ohnehin leer, und A-6 nimmt kein Wort aus Popup, Badge oder Chip weg. Befund
  **R13 bleibt bei A-2** — A-6 löst ihn nicht und beansprucht das nicht.
- Der Zustand „geclustert" wird **nicht** vorgelesen; `#count` nennt weiter
  Restaurants, nicht Symbole, und bleibt damit die verlässliche Auskunft.

### Testplan

Playwright, Handy- **und** Desktop-Viewport, synthetische Daten **und** die echte
`web/restaurants.json`:

1. **Schwelle:** bei 299 Treffern keine Blase und `.leaflet-marker-pane`-Kinder
   == Treffer; bei 300 mindestens eine Blase.
2. **Standardbild unverändert:** mit Standardfilter null Blasen und dieselbe
   DOM-Zahl in `#map` wie ohne die Bibliothek (gemessen 81).
3. **Keine Reste:** drei Runden Standard ↔ alle-aus; danach DOM-Zahl wie am
   Anfang.
4. **Trefferzahl:** `#count` nennt Restaurants, nicht Blasen („885 von 885").
5. **Fallback:** `L.markerClusterGroup` vor dem Laden entfernen → Karte zeichnet
   885 einzelne Marker, kein Fehler in der Konsole.
6. **Tempo:** bei 885 mit 4× Drosselung `render()` unter 150 ms und **kein**
   Frame über 100 ms beim Zoomen.
7. **Trefferfläche** einer Blase ≥ 44 × 44 px (`getBoundingClientRect`).
8. **Layout:** `elementFromPoint` auf der Blasenmitte trifft die Blase, nicht
   `#mapControls`; Fußzeile bleibt unverdeckt. In beiden Pfaden.
9. **Pins bleiben Standard-Icons** (ADR-011): jeder Restaurant-Marker ist ein
   `L.marker` ohne Optionen, `L.circleMarker` nur in `locateMe()`.
10. **Screenshot** in beiden Pfaden, je unter und über der Schwelle — vier Bilder.
    Nicht optional: drei A-3-Defekte waren gegen Zustands-Prüfungen unsichtbar.

**Zwei Dinge, die der `L`-Stub nicht kann** und die deshalb über das lokal
abgelegte echte Leaflet laufen müssen (Weg in dieser Sitzung erprobt, siehe
Doku-Auswirkungen): alles unter „Tempo" und alles unter „Layout". Ein
`markerClusterGroup`-Stub würde die Prüfungen 1–5 formal grün machen und
inhaltlich nichts aussagen.

**Pipeline-Tests:** `python3 -m unittest discover -s tests -v` muss grün bleiben,
ist von A-6 aber nicht betroffen — kein Pipeline-Code wird angefasst.

### Doku- und Backlog-Auswirkungen

- **`docs/entscheidungen/ADR-012-…`** neu, plus Zeile in
  `docs/entscheidungen/README.md` (Status lebt an **beiden** Orten — die Falle
  aus `CLAUDE.md`).
- **`docs/TECHNICAL.md`**: Abschnitt „PWA" um die drei `CDN_FILES` und `v7`
  ergänzen.
- **`docs/UMGESETZT.md`** nach der Umsetzung, mit den Messwerten.
- **Root-`README.md`**: „Bereits umgesetzt"/„Offen" pflegen — die Liste war bei
  A-5 zwei Anforderungen im Rückstand.
- **`docs/BACKLOG.md`**: R7s Nachtrag ergänzen. Dort stehen `L`-Stub-Werte
  (197 ms, 5,6 ms, 0,60 ms) ohne den Hinweis, dass sie **kein DOM** enthalten;
  die echten Zahlen (3,3 ms bzw. 116 ms) gehören daneben. Die Stub-Werte werden
  nicht gelöscht — sie sind als JS-Messung korrekt.
- **`CLAUDE.md`**: der Absatz über den `L`-Stub sollte den hier erprobten Weg
  aufnehmen — echtes Leaflet aus der npm-Registry (erreichbar, anders als
  unpkg) lokal neben die Seite legen, dann sind Marker-DOM, Frames und
  Trefferflächen messbar. Das ist die Lücke, die A-6 überhaupt erst sichtbar
  gemacht hat.
- **Zwei Zahlen-Funde außerhalb von A-6**, als Aufgabe in `BACKLOG.md` statt
  hier: (a) **`docs/PRD.md` sagt „`cuisine` bei 0 %"** — gemessen sind **699 von
  885** getaggt (79 %), die Zahl ist überholt und der Küchenstil-Filter damit
  längst sichtbar. (b) Gegenprobe zu den beiden Filter-Hinweisen im UI: „7 %"
  (64/885 = 7,2 %) und „26 %" (238/885 = 26,9 %) sind **weiterhin korrekt** —
  sie bleiben trotzdem hart im Text und sollten laut `CLAUDE.md` gerechnet
  werden.

## Definition of Done

- [ ] Unter 300 Treffern ist das Bild **unverändert**: null Blasen, DOM-Zahl in
      `#map` wie ohne Bibliothek (81 im Standardfilter).
- [ ] Ab 300 Treffern Blasen; bei 885 gemessen 53 Blasen + 12 Tropfen.
- [ ] Bei 885 mit 4× Drosselung: `render()` **< 150 ms** (Prototyp 81,6 ms) und
      **null** Frames über 100 ms beim Zoomen (heute 9 von 12).
- [ ] Marker werden per **`addLayers()`** gehängt, nicht einzeln.
- [ ] Drei Runden Filter hin und her lassen **keine** Marker zurück.
- [ ] `#count` zählt weiter Restaurants, nicht Blasen.
- [ ] Blase: Trefferfläche **≥ 44 px** und vorlesbarer Name „*n* Restaurants in
      diesem Bereich".
- [ ] Fehlt `L.markerClusterGroup`, zeichnet die Karte einzelne Marker ohne
      Fehler.
- [ ] Restaurant-Pins sind unverändert `L.marker` ohne Optionen (ADR-011);
      `L.circleMarker` nur in `locateMe()`.
- [ ] Drei Dateien in `CDN_FILES`, `CACHE_VERSION` = `v7`, SRI-Hashes gegen die
      echte unpkg-Antwort verifiziert.
- [ ] „© OpenStreetMap-Mitwirkende" sichtbar, Fußzeile unverdeckt, in **beiden**
      Layout-Pfaden.
- [ ] Keine Cookies, kein Tracking, kein Speicher-Zugriff dazugekommen.
- [ ] `python3 -m unittest discover -s tests -v` grün.
- [ ] Vier Screenshots (zwei Pfade × unter/über Schwelle) **der
      Produktverantwortung vorgelegt, bevor die Doku geschrieben wird** — die
      Lehre aus A-5.
- [ ] ADR-012 auf `akzeptiert`, Zeile in `entscheidungen/README.md` mitgezogen,
      Status in `anforderungen/README.md` auf 🏁.

## Umsetzungsschritte

1. Drei `<script>`/`<link>`-Tags mit SRI in `web/index.html`; Hashes gegen die
   unpkg-Antwort prüfen.
2. `layerEinfach` + `layerCluster` + `waehleLayer(anzahl)` anstelle des einen
   `layer`; Bibliotheks-Prüfung für den Fallback.
3. `render()` umbauen: sammeln statt hängen, Layer **nach** dem Zählen wählen,
   `addLayers()` im Cluster-Fall.
4. CSS für die Blasen: nur Trefferfläche auf 44 px und der vorlesbare Name —
   die Farben bleiben Leaflets (Entscheidung 3).
5. `web/sw.js`: drei `CDN_FILES`, `CACHE_VERSION` → `v7`.
6. Testplan durchfahren (echtes Leaflet lokal, nicht der `L`-Stub), Screenshots
   erzeugen und **vorlegen**.
7. Nach Freigabe: ADR-012 auf `akzeptiert`, Doku und Status nachziehen, die zwei
   Zahlen-Funde als Aufgaben in `BACKLOG.md`.
