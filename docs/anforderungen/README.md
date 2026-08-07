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
| A-3 | [Karte im Vollbild: Overlay + Bottom Sheets](./A-3-header-umbau.md) | 🏁 erledigt | Umgesetzt am 2026-07-26 gegen die Empfehlung, wie entschieden: **Karten-Overlay ohne Header** unter 640 px ([ADR-008](../entscheidungen/ADR-008-karte-im-vollbild-overlay-und-sheets.md), jetzt `akzeptiert`). Bedienzeile 205,7 px → **68 px**, Karte 70,9 % → **96,6 %** (360 px: 62,3 % → 96,1 %), alle Bedienelemente **44 px** statt 32,4 px. Filter und Feed sind Bottom Sheets mit gemeinsamer Mechanik. R2/R3/R4 und zwei P3-Punkte mit erledigt. |
| A-4 | [Farbsystem entflechten](./A-4-farbsystem.md) | 🏁 erledigt | Umgesetzt am 2026-07-25: drei Token-Ebenen **Marke / Interaktion / Zustand** ([ADR-009](../entscheidungen/ADR-009-farbrollen-marke-aktion-zustand.md)). `--accent` (fünf Rollen) und `--ok` (zwei) sind weg, kein Farbwert liegt mehr außerhalb von `:root`, „geschlossen" ist Slate statt Rot, „unbekannt" ein gestrichelter Umriss, alle Kontrastpaare ≥ 4,5:1. Entblockt A-5 und liefert A-3 die Tokens. |
| A-5 | [Pins nach Zustand unterscheiden](./A-5-pins-nach-zustand.md) | 🗑 verworfen | Am 2026-07-26 umgesetzt (~~[ADR-010](../entscheidungen/ADR-010-pin-grammatik-lieferung-und-geschlossen.md)~~: Farbe + Strichart = Lieferung, Größe + Füllstärke = geschlossen) und **am selben Tag zurückgenommen** — die Kreise sahen schlechter aus als die blauen Tropfen ([ADR-011](../entscheidungen/ADR-011-pins-wieder-einheitlich.md)). Im Standardbild waren alle 53 Pins ohnehin identisch, aufgeweitet 774 von 885 „unbekannt". Die Messwerte in der Datei bleiben gültig; **R13 ist wieder offen** und wandert zu A-2. |
| A-6 | [Marker-Clustering ab 300 Treffern](./A-6-clustering-oder-canvas.md) | ✅ bereit | Verfeinert am 2026-07-26: ab 300 Treffern fasst `markercluster` die Marker zu Blasen zusammen, darunter bleibt das Bild **unverändert** ([ADR-012](../entscheidungen/ADR-012-clustering-ab-schwelle.md)). Erstmals mit echtem Leaflet gemessen statt mit dem `L`-Stub: bei 885 Frames über 100 ms von 9/12 auf **0/142**, `render()` 386 → 68 ms (4× gedrosselt). Canvas ist durch ADR-011 versperrt, Culling messbar wertlos. |
| A-7 | [Telefonnummer in die Pipeline](./A-7-telefonnummer.md) | 💡 Idee | `phone`/`contact:phone` kommen beim Scan gratis mit; für „schnell bestellen" so nützlich wie die Website. Braucht eine neue DB-Spalte. |
| A-8 | Filterzustand teilbar und wiederherstellbar machen | 🏁 erledigt | Zusammen mit A-1 gebaut: `?delivery=`/`?takeaway=`/`?open=`/`?cuisine=`/`?q=`, geschrieben per `history.replaceState` und nur dort, wo vom Standard abgewichen wird. Reine URL-Parameter, nichts wird gespeichert. `?nearby=1` bleibt erhalten. |
| A-9 | Datenpflege per OSM-Notiz anstoßen | 💡 Idee | Nutzer sollen Datenlücken (`delivery` zu 87,5 % „unbekannt", 143 ohne `opening_hours`) aus der App heraus melden — per **anonymer OSM-Notiz**, strikt accountfrei (Richtungsentscheidung 2026-08-07: MapComplete-/Editor-Deep-Link verworfen, Registrierung ist für schnelles Pflegen zu aufwendig; das Abarbeiten der Notiz übernimmt die OSM-Community). Recherche mit Belegen: [docs/recherche/nutzer-motivation-datenpflege.md](../recherche/nutzer-motivation-datenpflege.md). |

## Abhängigkeiten auf einen Blick

```
A-1 (Standardfilter) 🏁 ─┬──►  A-5 (Pins nach Zustand) 🗑 ◄──  A-4 (Farbsystem) 🏁
                         │     gebaut und zurückgenommen (ADR-011)
                         ├──►  A-6 (Clustering) ✅ verfeinert 2026-07-26; Canvas ist
                         │     durch ADR-011 versperrt, geclustert wird ab 300
                         └──►  A-8 (Filter in der URL) 🏁 mitgebaut

A-4 (Farbsystem) 🏁 ──────────►  A-3 (Overlay + Sheets) 🏁 ──►  A-2 (Ergebnisliste)
                                 erbt die Tokens               erbt die Sheet-Mechanik
                                                               — und erbt von A-5 🗑
                                                               den Befund R13 selbst
```

**Keine Anforderung ist mehr blockiert.** A-1 ist am 2026-07-25 entschieden
([ADR-007](../entscheidungen/ADR-007-standardfilter-liefert-jetzt.md)) und
umgesetzt, A-8 gleich mit; A-4 ist am selben Tag umgesetzt
([ADR-009](../entscheidungen/ADR-009-farbrollen-marke-aktion-zustand.md)). Damit
sind **beide Kanten auf A-5 erledigt** — A-5 ist die nächste Verfeinerung. A-6
ist keine Voraussetzung mehr, weil der Default eng geblieben ist.

**A-6 ist seit 2026-07-26 verfeinert und wartet auf grünes Licht**
([ADR-012](../entscheidungen/ADR-012-clustering-ab-schwelle.md), noch
`vorgeschlagen`). Die Verfeinerung hat den Ausgangstext in zwei Punkten
widerlegt: `L.canvas()` „ohne neue Lib" gibt es nicht — `preferCanvas` wirkt nur
auf Vektorlayer, also wäre es der von
[ADR-011](../entscheidungen/ADR-011-pins-wieder-einheitlich.md) abgewählte
`circleMarker` —, und Sichtfeld-Culling ist messbar wertlos (bei Zoom 12 liegen
618 von 885 im Bild). Erstmals wurde gegen **echtes** Leaflet gemessen statt
gegen den `L`-Stub, der kein DOM erzeugt und die Kosten deshalb nicht sehen kann:
bei 885 Markern und 4× CPU-Drosselung fallen 9 von 12 Frames über 100 ms, mit
Clustering 0 von 142. Das Standardbild (21 Treffer) bleibt dabei unangetastet —
„immer clustern" hätte 14 der 21 Restaurants hinter Zahlen versteckt, ohne dort
etwas zu gewinnen.

**A-5 wurde am 2026-07-26 umgesetzt und am selben Tag zurückgenommen.**
[ADR-010](../entscheidungen/ADR-010-pin-grammatik-lieferung-und-geschlossen.md)
hatte die Pin-Grammatik auf zwei Achsen festgelegt;
[ADR-011](../entscheidungen/ADR-011-pins-wieder-einheitlich.md) kehrt das um,
weil die Kreise schlechter aussahen als Leaflets blaue Tropfen — im Standardbild
waren die 53 sichtbaren Pins ohnehin identisch. Die Pin-Achsen sind seither
**geschlossen, nicht frei**: sie überhaupt wieder zu belegen — farbig, über die
Größe, ganz oder teilweise — braucht einen neuen ADR. Damit sind **vier der acht
Anforderungen erledigt**; offen sind A-2, A-6 (verfeinert, wartet auf Freigabe)
und A-7, verworfen ist A-5.

**Befund R13 ist damit wieder offen** („welche Restaurants liefern / geöffnet
sind, ist nur nach Antippen sichtbar") — und wird nicht erneut über die Pins
gelöst, sondern über **A-2**. Das ist der nächste Schritt und der bessere Weg:
eine Liste hat beliebig viele Worte, ein 20-px-Punkt vier Kanäle, und für
Screenreader existieren farbige Kreise ohnehin nicht.

**A-4 kam vor A-3**, weil beide denselben `<style>`-Block anfassen, A-4 aber kein
Layout ändert: A-3 hat direkt auf den Farbrollen aufgebaut, statt die alten
Namen erst zu übernehmen und später zu ersetzen — und setzt selbst keinen
Farbwert außerhalb von `:root`. Praktische Folge: A-4 hat `CACHE_VERSION` `v3`
verbraucht, A-3 steht auf `v4`. **A-3 ist seit 2026-07-26 umgesetzt**; damit
sind vier der acht Anforderungen erledigt und keine ist mehr blockiert.

**A-2 erbt die Sheet-Mechanik.** Sie war nie durch A-3 blockiert, aber A-3 ist
der günstigere Weg dorthin: `openSheet()` samt Griff, Wischen, Fokus-Führung,
`Escape` und der Regel „nur eines gleichzeitig" ist bewusst wiederverwendbar
gebaut — die Ergebnisliste wird ihr **dritter** Nutzer und braucht keinen
eigenen Panel-Entwurf mehr
([ADR-008](../entscheidungen/ADR-008-karte-im-vollbild-overlay-und-sheets.md)).
Mit dem Rückbau von A-5 kommt eine zweite Erbschaft dazu: A-2 ist jetzt der
**einzige** geplante Weg, einen Zustand ohne Antippen zu zeigen — die drei
Lieferzustände müssen dort in Worten stehen, nicht als Farbe.

**Zwei Layout-Pfade, ab jetzt dauerhaft.** Unter und über 640 px sieht die Seite
verschieden aus; jede künftige UI-Änderung ist in **beiden** zu prüfen. Die
Bedienzeile ist außerdem auf drei Elemente fest — neue Bedienelemente gehören
ins Sheet, sonst wächst sie wieder zu, woran der alte Header gescheitert ist.

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
