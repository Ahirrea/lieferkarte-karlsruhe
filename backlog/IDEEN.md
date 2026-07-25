# 💡 Ideen

Noch nicht baubar: hier fehlt jeweils eine Produktentscheidung oder ein Entwurf.
Ist die Entscheidung gefallen, zieht der Punkt nach
[`READY-FOR-DEV.md`](READY-FOR-DEV.md).

**Backlog:** 💡 Ideen · [🔨 Ready for Dev](READY-FOR-DEV.md) ·
[✅ Done](DONE.md) · [Übersicht](README.md)

---

### 1. Standardfilter entschärfen (Entscheidung offen)

Die Karte filtert per Default „nur mit Lieferservice" (`delivery=yes/only`) und
zeigt damit **63 von 883** Restaurants (7 %). Die 773 ungetaggten sind
„unbekannt", nicht „liefert nicht" – die Karte wirkt fälschlich leer. Abholung
ist mit 26 % deutlich besser abgedeckt, wird aber nur als Popup-Badge gezeigt.

Vier Optionen (A: so lassen, B: eigener „nur Abholung"-Filter, C: Default auf
„alle" und Liefer-/Abholstatus nur als Badge, D: Tags selbst in OSM ergänzen)
stehen samt Abdeckungstabelle in
[`VOR-VEROEFFENTLICHUNG.md`](../VOR-VEROEFFENTLICHUNG.md), Abschnitt „Filter für
Abdeckung anpassen". **Blockiert [Idee 5](#5-pins-nach-zustand-unterscheiden-r13)**
– und macht R7 ([`READY-FOR-DEV.md`](READY-FOR-DEV.md), „Mittel") dringlicher,
weil dann 883 statt 63 Marker gezeichnet werden.

### 2. Ergebnisliste neben der Karte (R6)

Die Karte ist für Tastatur und Screenreader leer: die `L.marker(…)` tragen kein
`alt`/`title`, die Popup-Inhalte existieren nur im Marker. Vorschlag: dieselben
gefilterten Daten zusätzlich als schlichte `<ul>` unter bzw. neben der Karte.
Löst gleichzeitig „was ist in der Nähe?" und macht „In meiner Nähe" nach
Entfernung sortierbar. Offen ist die Struktur – wo die Liste sitzt und ob sie
auf Mobil einklappbar ist.

### 3. Header-Umbau: eine Zeile + Bottom Sheet (R9)

Der Header frisst 23 % des Bildschirms: Suche, zwei Checkboxen, zwei Buttons und
die Trefferzahl konkurrieren gleichwertig über drei Zeilen, die Zahl landet per
`margin-left: auto` als Waise neben „Diese Woche". Auf Mobil besser: eine Zeile
(Suche + „Filter"-Knopf mit Trefferzahl), der Rest in ein Bottom Sheet. Nebenbei
sind die Buttons ~34 px hoch – unter den empfohlenen 44 px Touch-Target.

Gehört zusammen mit dem **Feed-Panel**, das auf Mobil fast die ganze Karte
verdeckt: als Bottom Sheet mit Griff angenehmer als das schwebende Panel. Beides
ist derselbe Umbau und sollte in einem Rutsch entworfen werden.

### 4. Farbsystem entflechten (R12)

`--accent` bedeutet vier Dinge gleichzeitig: Markenfarbe (H1), Primärlink,
„Jetzt geschlossen" bzw. „geschlossen" in der Zeitentabelle *und* Melde-Flag.
Zustandsfarben gehören von der Markenfarbe getrennt – braucht aber erst einen
eigenen Satz Tokens neben `--accent`.

### 5. Pins nach Zustand unterscheiden (R13)

Ob ein Restaurant liefert, abholen lässt oder gerade geschlossen ist, sieht man
erst nach dem Antippen. Farb- oder Formcodierung (z. B. blass = jetzt
geschlossen) bringt viel pro Blick. Hängt an
**[Idee 1](#1-standardfilter-entschärfen-entscheidung-offen)**: erst mit
entschärftem Standardfilter lohnt die Unterscheidung wirklich, und erst dann
steht fest, welche Zustände überhaupt nebeneinander vorkommen.

### 6. Marker-Clustering oder Canvas-Renderer

Der zweite Teil von R7 – der erste ist ready, siehe
[`READY-FOR-DEV.md`](READY-FOR-DEV.md) (Abschnitt „Mittel"). Mit entschärftem Standardfilter zeichnet die Karte 883 statt 63 Marker. Ob
Clustering (`markercluster`, wäre eine zusätzliche Abhängigkeit) oder ein
Canvas-Renderer (`L.canvas()`, ohne neue Lib) besser passt, ist offen – und
sinnvoll erst zu entscheiden, wenn
[Idee 1](#1-standardfilter-entschärfen-entscheidung-offen) entschieden ist.

### 7. Telefonnummer in die Pipeline

Die OSM-Tags `phone`/`contact:phone` kommen beim Scan kostenlos mit; eine
Nummer im Popup wäre für „schnell bestellen" mindestens so nützlich wie die
Website. Die Spalte existiert in `restaurants` noch nicht. Vor dem Bau: Abdeckung
zählen und entscheiden, ob Änderungen protokolliert werden sollen (Vorsicht,
siehe „Massen-Ereignisse" beim Änderungs-Feed in [`DONE.md`](DONE.md)).

### 8. Küchenstil: Abdeckung prüfen

Die `cuisine`-Pipeline ist [fertig](DONE.md) („Filter nach Küchenstil"), aber in
`data/restaurants.db` sind nach vier Scans (letzter: 2026-07-21) **0 von 883**
aktiven Restaurants getaggt – während `opening_hours` bei 741 gefüllt ist. Für
Karlsruhe sind null Küchenstil-Tags unplausibel; das deutet eher auf ein
Pipeline-Problem als auf fehlende OSM-Daten. Der Filter bleibt so lange
versteckt (das ist gewollt), aber der Befund gehört nachgesehen:

```bash
python3 -c "import sqlite3; c=sqlite3.connect('data/restaurants.db'); \
print(c.execute('SELECT cuisine, COUNT(*) FROM restaurants WHERE active=1 \
GROUP BY cuisine ORDER BY 2 DESC LIMIT 20').fetchall())"
```

### 9. Ausbau von bereits Umgesetztem

Drei bewusst zurückgestellte Erweiterungen – jeweils erst nötig, wenn der
aktuelle Kompromiss nicht mehr reicht:

- **`opening_hours.js` vendoren** (lokal, kein CDN) für die volle
  `opening_hours`-Abdeckung. Aktuell nicht nötig: ~90 % der getaggten Fälle
  wertet der eigene Mini-Parser schon eindeutig aus.
- **Leaflet lokal ins Repo legen** – macht die Offline-Fähigkeit unabhängig vom
  CDN. Bisher genügt der „best effort"-Precache.
- **Küchenstil-Synonyme gruppieren** (`sushi` unter `japanese`, `doner` unter
  `kebab`). Wäre Interpretation der OSM-Daten; erst sinnvoll, wenn die
  Auswahlliste zu lang wirkt.
