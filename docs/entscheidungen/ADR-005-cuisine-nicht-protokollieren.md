# ADR-005: Küchenstil-Änderungen werden nicht protokolliert

**Status:** akzeptiert (aus `UMGESETZT.md` herausgezogen am 2026-07-25)
**Datum:** 2026-07-25

## Kontext

Die `changes`-Tabelle ist ein Anhang-Protokoll und speist den
„Diese Woche neu"-Feed. Sie hat eine gefährliche Eigenschaft: **wenn eine neue
Spalte eingeführt wird, protokolliert der erste Scan, der das Tag liest, für
jedes betroffene Restaurant eine Änderung auf einmal.**

Das ist schon passiert: der Scan, der erstmals die vorhandenen `takeaway`-Tags
las, schrieb **245 × `TAKEAWAY_CHANGED`** („unbekannt → ja") in einem Rutsch.
Für den Feed sieht das aus wie 245 Neuigkeiten, obwohl sich in der Welt nichts
geändert hat — es wurde nur erstmals hingesehen.

Dieselbe Falle hätte `cuisine` ausgelöst, und zwar noch heftiger: das Tag erlaubt
mehrere Werte in beliebiger Schreibweise (`pizza;italian`, `Ice Cream`,
`coffee-shop`), also würde auch jede Normalisierungsänderung als „Änderung"
durchschlagen.

## Entscheidung

**`cuisine`-Änderungen werden bewusst nicht in `changes` protokolliert.** Der
Küchenstil läuft durch die Pipeline (Scanner normalisiert, Export liefert
`cuisines`, Frontend filtert), aber er erzeugt keine Feed-Einträge.

Ergänzend schützt sich der Feed selbst: `build_feed()` verwirft alles mit dem
Zeitstempel des ersten `scan_runs`-Eintrags (der Erstimport hat alle 883
Restaurants als `NEW` protokolliert — das ist der Anfangsbestand, keine
Neuigkeit) und begrenzt Einträge pro Änderungstyp (`FEED_MAX_PER_TYPE`), wobei
die echte Anzahl in `counts` steht.

## Begründung

Der Feed soll beantworten „was ist neu?". Ein Küchenstil-Tag, das jemand in OSM
nachträgt, ist für die Nutzerin keine Neuigkeit über das Restaurant — es ist eine
Neuigkeit über die Datenlage. Diese Unterscheidung ist der ganze Punkt.

## Verworfene Alternativen

- **`cuisine` normal protokollieren:** hätte den Feed beim ersten Scan mit
  Hunderten Einträgen geflutet und ihn danach mit Normalisierungsrauschen gefüllt.
- **Massen-Ereignisse nachträglich aus `changes` löschen:** würde das
  Anhang-Protokoll umschreiben und die DB-Historie als Wahrheitsquelle beschädigen.
- **Feed ganz weglassen:** er ist eine der beliebteren Funktionen.

## Konsequenzen

- **Jeder neue Änderungstyp löst denselben Massen-Effekt aus** bei dem Scan, der
  das Tag erstmals liest. Wer einen einführt, muss das einplanen — und ihn an
  **zwei** Stellen registrieren: `FEED_TYPE_ORDER` (`export.py`) und
  `FEED_GROUPS` (`web/index.html`). Fehlt eins davon, zeigt das Panel den rohen
  Typ-String als Gruppenüberschrift.
- Wer die `changes`-Tabelle liest, muss **beide** Fallen behandeln: den
  Erstimport und die Massen-Ereignisse bei neuen Spalten.
- Küchenstil-Änderungen sind damit nicht nachvollziehbar. Das ist der akzeptierte
  Preis.
