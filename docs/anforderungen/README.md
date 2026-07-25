# Anforderungen

Verfeinerte Ideen — Ergebnis des [Refinement-Prozesses](../PROZESS.md). Rein
technische Aufgaben und kleine Fixes laufen über [`BACKLOG.md`](../BACKLOG.md);
die Trennlinie steht im
[Prozess](../PROZESS.md#anforderung-oder-aufgabe-der-test).

Diese Übersicht ist der Einstieg — und die **einzige Quelle für den Status**: die
Anforderungsdateien selbst führen keinen Status, damit nichts auseinanderlaufen
kann. Eine erledigte Anforderung **bleibt liegen, wo sie ist**; sie ist ab dann
das Protokoll, *warum* es so gelöst wurde. Was bereits umgesetzt ist, steht mit
Begründung in [`UMGESETZT.md`](../UMGESETZT.md).

**Zeile oder Datei?** Eine rohe Idee bleibt eine Zeile in der Tabelle. Erst wenn
mehr dazu steht — Optionen, Zahlen, Querverweise — bekommt sie eine eigene Datei.

**Statuslegende:** `💡 Idee` · `✅ bereit` · `🚧 in Umsetzung` · `🏁 erledigt`
· `🧊 zurückgestellt` · `🗑 verworfen`

## Übersicht

Reihenfolge = was als Nächstes sinnvoll wäre. Kein Zeitplan.

| Nr. | Anforderung | Status | Worum es geht |
|---|---|---|---|
| A-1 | [Standardfilter entschärfen](./A-1-standardfilter-entschaerfen.md) | 💡 Idee — **Entscheidung offen** | Der Default „nur mit Lieferservice" zeigt 63 von 883 Restaurants, weil 87 % in OSM ungetaggt sind — die Karte wirkt fälschlich leer. Vier Optionen samt Abdeckungstabelle, Empfehlung C+B. **Blockiert A-5 und A-6.** |
| A-2 | [Ergebnisliste neben der Karte](./A-2-ergebnisliste.md) | 💡 Idee | Die Karte ist für Tastatur und Screenreader leer. Dieselben gefilterten Daten zusätzlich als Liste — löst gleichzeitig „was ist in der Nähe?". |
| A-3 | [Header-Umbau: eine Zeile + Bottom Sheet](./A-3-header-umbau.md) | 💡 Idee | Der Header frisst 23 % des Bildschirms. Gehört zusammen mit dem Feed-Panel entworfen, das auf Mobil fast die ganze Karte verdeckt. |
| A-4 | [Farbsystem entflechten](./A-4-farbsystem.md) | 💡 Idee | `--accent` bedeutet vier Dinge gleichzeitig. Zustandsfarben gehören von der Markenfarbe getrennt. Voraussetzung für A-5. |
| A-5 | [Pins nach Zustand unterscheiden](./A-5-pins-nach-zustand.md) | 💡 Idee | Liefert / holt ab / gerade geschlossen sieht man erst nach dem Antippen. Hängt an A-1 **und** A-4. |
| A-6 | [Marker-Clustering oder Canvas-Renderer](./A-6-clustering-oder-canvas.md) | 💡 Idee | Mit entschärftem Default zeichnet die Karte 883 statt 63 Marker. Wird durch A-1 von „nice to have" zur Voraussetzung. |
| A-7 | [Telefonnummer in die Pipeline](./A-7-telefonnummer.md) | 💡 Idee | `phone`/`contact:phone` kommen beim Scan gratis mit; für „schnell bestellen" so nützlich wie die Website. Braucht eine neue DB-Spalte. |
| A-8 | Filterzustand teilbar und wiederherstellbar machen | 💡 Idee | Bisher gibt es nur `?open=1` / `?nearby=1`; `?delivery=0&cuisine=thai` passt ins bestehende Muster und verletzt das „keine Cookies"-Versprechen nicht (reine URL-Parameter, keine Speicherung). Sinnvoll erst nach A-1, weil dann erst feststeht, welche Filter es gibt. |

## Abhängigkeiten auf einen Blick

```
A-1 (Standardfilter)  ──┬──►  A-5 (Pins nach Zustand)  ◄──  A-4 (Farbsystem)
                        ├──►  A-6 (Clustering/Canvas)
                        └──►  A-8 (Filter in der URL)
```

**A-1 ist der Flaschenhals.** Solange die Entscheidung offen ist, sind drei
weitere Anforderungen nicht sinnvoll zu verfeinern.

## Neue Anforderung aufnehmen

Schritt 7 des [Refinement-Prozesses](../PROZESS.md):

1. Für eine rohe Idee genügt eine neue Zeile mit Status `💡 Idee`.
2. Zur Verfeinerung [`_vorlage.md`](./_vorlage.md) nach
   `A-<nächste Nr>-<kurz-titel>.md` kopieren und ausfüllen (Nummern werden nicht
   wiederverwendet, auch nicht bei `🗑 verworfen`), dann die Zeile verlinken und
   auf `✅ bereit` setzen.
3. Status ausschließlich hier pflegen — auch später bei `🚧` und `🏁`.

> Diese Liste ersetzt seit 2026-07-25 `backlog/IDEEN.md` und den UX-Teil von
> `backlog/READY-FOR-DEV.md`. Die drei Stufen-Dateien (Ideen → Ready for Dev →
> Done) sind aufgelöst: Statuswechsel sind jetzt ein Wort in der Tabelle oben
> statt eines Textumzugs zwischen Dateien. Die Kürzel `R…`/`P…` aus dem
> UI/UX-Review vom Juli 2026 bleiben erhalten.
