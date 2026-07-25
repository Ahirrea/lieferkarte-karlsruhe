# A-1 Standardfilter entschärfen

[← Anforderungen](./README.md) · [Prozess](../PROZESS.md)
· Status siehe [Übersicht](./README.md#übersicht)

**User Story:** Als Person, die bestellen will, möchte ich beim Öffnen der Karte
sehen, welche Restaurants es in meiner Nähe überhaupt gibt, um nicht vor einer
fast leeren Karte zu stehen und den Eindruck zu bekommen, es gäbe hier nichts.

**Verfeinert am:** — (Optionen stehen, **Produktentscheidung offen**)
**Bedient PRD:** „Kernschleife" Schritt 1 („Schritt 1 muss ohne Interaktion
nützlich sein")
**Eingeschränkt durch:** [ADR-001](../entscheidungen/ADR-001-openstreetmap-statt-google-places.md)
(die Datenlücken sind die der Quelle und nicht behebbar)

Das ist die **wichtigste offene Entscheidung des Projekts** und blockiert zwei
weitere Anforderungen ([A-5](./A-5-pins-nach-zustand.md),
[A-6](./A-6-clustering-oder-canvas.md)).

## Das Problem

Die Karte filtert per Default „nur mit Lieferservice" (`delivery=yes/only`) und
zeigt damit **63 von 883** Restaurants (7 %). Die 773 ungetaggten sind
**„unbekannt", nicht „liefert nicht"** — die Karte wirkt fälschlich leer.
Abholung ist mit 26 % deutlich besser abgedeckt, wird aber nur als Popup-Badge
gezeigt, nicht gefiltert.

### Tatsächliche Abdeckung (Voll-Scan, 883 aktive Restaurants)

| Tag | ja (`yes`/`only`) | nein (`no`) | ungetaggt |
|---|---|---|---|
| `delivery` (Lieferung) | 63 (7 %) | 47 (5 %) | 773 (87 %) |
| `takeaway` (Abholung) | **237 (26 %)** | 8 (0 %) | 638 (72 %) |

Aufschlüsselung der getaggten Fälle: 43 bieten beides, 20 nur Lieferung,
**194 nur Abholung**.

Zum Nachzählen auf `data/restaurants.db`:

```sql
SELECT delivery, takeaway, COUNT(*) FROM restaurants WHERE active=1
GROUP BY delivery, takeaway;
```

## Andockpunkte im Code

- `web/index.html` — die Filterlogik in `render()`, die Checkboxen im Header, die
  Trefferzahl `#count`, das Popup-HTML mit den Liefer-/Abhol-Badges.
- `export.py` — liefert `delivery` und `takeaway` bereits als `true`/`false`/`null`
  aus; **datenseitig ist alles da**, es fehlt nichts in der Pipeline.
- `scanner.py` (`_osm_yesno`) — `yes`/`only` → true, `no` → false, ungetaggt → `NULL`.

Es handelt sich also ausschließlich um eine Frontend- und Produktentscheidung.

## Spannung zu Nicht-Zielen — und Auflösung

Keine. Alle Optionen bleiben rein clientseitig, ohne Tracking und ohne neue
Datenquelle. Option D verlässt das Projekt (Beiträge nach OSM), verletzt aber
ebenfalls kein Nicht-Ziel.

## Optionen

**A — so lassen.** Nur sicher getaggte Lieferdienste als Default. Sauber im
Sinne von „wir behaupten nichts", aber sehr wenige Treffer, und die Karte
untertreibt ihr eigenes Angebot.

**B — eigener „nur Abholung"-Filter.** Die 237 Abhol-Restaurants gezielt
filterbar machen. Die Daten sind da, seit `takeaway` erfasst wird. Löst aber das
„fast leer"-Gefühl beim ersten Öffnen nicht, weil der Default bleibt.

**C — Default entschärfen.** Standardmäßig **alle** zeigen, Lieferung und
Abholung nur als Badges markieren, optionale Filter für beide. Behebt den
„fast leer"-Effekt am wirksamsten.

**D — zurück beitragen.** Fehlende Tags selbst in OSM ergänzen. Handarbeit, hilft
allen, wirkt aber erst nach dem nächsten Scan und skaliert nicht auf 773 Läden.

## Empfehlung

**C, kombiniert mit B** — und D als nebenherlaufende Fleißarbeit.

Begründung: Die Karte behauptet mit dem heutigen Default etwas Falsches. Sie sagt
implizit „hier gibt es 63 Restaurants", während sie eigentlich „bei 63
Restaurants *wissen wir es*" meint. Ein Default auf „alle" mit ehrlichen Badges
(„liefert" / „Abholung" / „unbekannt") sagt die Wahrheit und ist für die
Nutzerin nützlicher — sie kann bei einem Restaurant, das sie interessiert, selbst
auf der Website nachsehen.

B kommt fast gratis dazu, sobald die Filter ohnehin umgebaut werden, und bedient
die mit 26 % am besten abgedeckte Information.

## Folgen für andere Anforderungen — wichtig

Mit entschärftem Default zeichnet die Karte **883 statt 63 Marker**. Damit wird
[A-6](./A-6-clustering-oder-canvas.md) (Clustering oder Canvas-Renderer) von
„nice to have" zu einer Voraussetzung, und die Aufgabe „Suche drosseln, Popups
faul bauen" (R7 im [Backlog](../BACKLOG.md)) wird dringlich — heute baut `render()`
für **jeden** Marker vorab das komplette Popup-HTML inklusive
`openStateNow()`-Parsing.

[A-5](./A-5-pins-nach-zustand.md) (Pins nach Zustand unterscheiden) lohnt sich
erst nach dieser Entscheidung: vorher steht nicht fest, welche Zustände überhaupt
nebeneinander vorkommen.

## Offen — von der Ideengeberin zu entscheiden

1. Welche Option (Empfehlung: C + B)?
2. Falls C: Wie heißt „ungetaggt" in der Oberfläche? „unbekannt", „nicht
   angegeben" oder gar kein Badge?
3. Sollen die Filter im URL-Zustand landen (siehe
   [A-8](./README.md#übersicht))?

## Definition of Done

- Beim ersten Öffnen ohne Interaktion ist die Karte erkennbar gefüllt.
- `delivery === null` und `takeaway === null` werden nachweislich als
  *unbekannt* dargestellt, nie als *nein*.
- Die Trefferzahl (`#count`) stimmt mit den gezeichneten Markern überein.
- Mit 883 Markern bleibt die Seite auf dem Handy bedienbar (siehe A-6 / R7).
- Test mit synthetischen Daten **und** mit der echten `web/restaurants.json`.

---

> **Herkunft:** Idee 1 aus `backlog/IDEEN.md`, Optionen und Abdeckungstabelle aus
> `VOR-VEROEFFENTLICHUNG.md`, Abschnitt „Offene Entscheidung: Filter für Abdeckung
> anpassen" ([Archiv](../archiv/VOR-VEROEFFENTLICHUNG.md)). Die Kürzel `R…`/`P…`
> in verwandten Punkten stammen aus dem UI/UX-Review vom Juli 2026
> (Mobil-Screenshot, Android/Chrome, 1080 × 2340) und bleiben erhalten, damit
> Rückfragen zuordenbar sind.
