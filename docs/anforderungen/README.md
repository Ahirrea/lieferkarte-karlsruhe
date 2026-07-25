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
| A-1 | [Standardfilter entschärfen](./A-1-standardfilter-entschaerfen.md) | 🏁 erledigt | Entschieden am 2026-07-25 gegen die Empfehlung: Default ist **„Liefert jetzt"** (Lieferung **und** jetzt geöffnet) — die Karte ist ein Jetzt-Werkzeug, kein Verzeichnis ([ADR-007](../entscheidungen/ADR-007-standardfilter-liefert-jetzt.md)). Dazu Chips statt Checkboxen, eigener Abholung-Filter, „unbekannt"-Badges, Leerzustand. |
| A-2 | [Ergebnisliste neben der Karte](./A-2-ergebnisliste.md) | 💡 Idee | Die Karte ist für Tastatur und Screenreader leer. Dieselben gefilterten Daten zusätzlich als Liste — löst gleichzeitig „was ist in der Nähe?". |
| A-3 | [Karte im Vollbild: Overlay + Bottom Sheets](./A-3-header-umbau.md) | ✅ bereit | Der Header frisst gemessen 23,9 % (360 px: 35 %), das Feed-Panel verdeckt 77–88 % der Karte, alle Bedienelemente sind 32,4 px statt 44 px. Entschieden am 2026-07-25 gegen die Empfehlung: **Karten-Overlay ohne Header** unter 640 px ([ADR-008](../entscheidungen/ADR-008-karte-im-vollbild-overlay-und-sheets.md)). Zieht R2/R3/R4 und zwei P3-Punkte aus dem Backlog mit rein. |
| A-4 | [Farbsystem entflechten](./A-4-farbsystem.md) | ✅ bereit | Gemessen trägt `--accent` **fünf** Rollen auf 15 CSS-Stellen, `--ok` zwei, und 8 von 15 Farbpaaren verfehlen 4,5:1. Entschieden am 2026-07-25: drei Token-Ebenen **Marke / Interaktion / Zustand**, „geschlossen" wird Slate statt Rot, alle Kontrastverstöße mit ([ADR-009](../entscheidungen/ADR-009-farbrollen-marke-aktion-zustand.md)). Wird **vor A-3** gebaut und entblockt A-5. |
| A-5 | [Pins nach Zustand unterscheiden](./A-5-pins-nach-zustand.md) | 💡 Idee | Liefert / holt ab / gerade geschlossen sieht man erst nach dem Antippen. Durch A-1 entblockt — die Zustandsmenge steht jetzt fest; wartet auf die Zustandstokens aus A-4 (✅ bereit) und ist ab dann an [ADR-009](../entscheidungen/ADR-009-farbrollen-marke-aktion-zustand.md) gebunden: Farbe trägt den Zustand, nie allein. |
| A-6 | [Marker-Clustering oder Canvas-Renderer](./A-6-clustering-oder-canvas.md) | 💡 Idee | Durch A-1 entblockt, aber **entschärft**: mit dem Default „Liefert jetzt" sind es beim Öffnen ~35 Marker, die 883 sieht nur, wer die Filter abschaltet (883 in 197 ms gemessen). Bleibt „nice to have". |
| A-7 | [Telefonnummer in die Pipeline](./A-7-telefonnummer.md) | 💡 Idee | `phone`/`contact:phone` kommen beim Scan gratis mit; für „schnell bestellen" so nützlich wie die Website. Braucht eine neue DB-Spalte. |
| A-8 | Filterzustand teilbar und wiederherstellbar machen | 🏁 erledigt | Zusammen mit A-1 gebaut: `?delivery=`/`?takeaway=`/`?open=`/`?cuisine=`/`?q=`, geschrieben per `history.replaceState` und nur dort, wo vom Standard abgewichen wird. Reine URL-Parameter, nichts wird gespeichert. `?nearby=1` bleibt erhalten. |

## Abhängigkeiten auf einen Blick

```
A-1 (Standardfilter) 🏁 ─┬──►  A-5 (Pins nach Zustand)  ◄──  A-4 (Farbsystem) ✅
                         ├──►  A-6 (Clustering/Canvas) — entschärft
                         └──►  A-8 (Filter in der URL) 🏁 mitgebaut

A-4 (Farbsystem) ✅ ──────────►  A-3 (Overlay + Sheets) ✅ ──►  A-2 (Ergebnisliste)
                                 erbt die Tokens              erbt die Sheet-Mechanik
```

**Der Flaschenhals ist weg.** A-1 ist am 2026-07-25 entschieden
([ADR-007](../entscheidungen/ADR-007-standardfilter-liefert-jetzt.md)) und
umgesetzt, A-8 gleich mit. A-5 hängt jetzt nur noch an A-4; A-6 ist keine
Voraussetzung mehr, weil der Default eng geblieben ist.

**A-4 kommt vor A-3.** Beide fassen denselben `<style>`-Block an, aber A-4 ändert
kein Layout — in dieser Reihenfolge baut A-3 direkt auf den neuen Farbrollen auf
statt die alten Namen erst zu übernehmen und später zu ersetzen
([ADR-009](../entscheidungen/ADR-009-farbrollen-marke-aktion-zustand.md)).
Praktische Folge: A-4 verbraucht `CACHE_VERSION` `v3`, A-3 rückt auf `v4`.

**A-3 ist keine Voraussetzung für A-2, aber der günstigere Weg dorthin:** die
Bottom-Sheet-Mechanik aus A-3 ist die Hülle, in der die Ergebnisliste auf Mobil
sitzen kann — wer A-2 vorzieht, entwirft dieses Panel zweimal
([ADR-008](../entscheidungen/ADR-008-karte-im-vollbild-overlay-und-sheets.md)).

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
