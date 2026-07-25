# ADR-003: Ein leerer oder fehlgeschlagener Scan darf die DB nie leeren

**Status:** akzeptiert (nachträglich dokumentiert am 2026-07-25)
**Datum:** 2026-07-25

## Kontext

Ein Voll-Scan bestimmt entfernte Restaurants **durch Abwesenheit**: was Overpass
nicht liefert, gilt als `REMOVED`. Diese Logik ist notwendig — geschlossene
Restaurants sollen verschwinden —, aber sie ist gefährlich: liefert Overpass
wegen Timeout, Rate-Limit oder Serverfehler eine leere oder abgeschnittene
Antwort, würde derselbe Code **alle 883 Restaurants** als entfernt markieren.

Das ist keine theoretische Sorge. Der frühere `--mock`-Modus hat genau das
getan: er zählte als Voll-Scan und hätte jedes echte Restaurant als `REMOVED`
markiert.

## Entscheidung

Zwei Schutzmechanismen, die in jedem Refactoring erhalten bleiben müssen:

1. **`scanner.py` bricht ab und lässt die DB unangetastet**, wenn Overpass
   fehlschlägt oder null verwertbare Orte liefert.
2. **`--light` markiert bewusst kein `REMOVED`.** Entfernungen werden nur dem
   Voll-Scan geglaubt.

Der `--mock`-Modus ist entfernt worden; die Tests setzen ihre Fixtures direkt per
`sync_places` in temporäre DBs (`tests/helpers.py`).

## Begründung

Die Asymmetrie ist Absicht: eine **unvollständige** Antwort darf Einträge nicht
löschen, aber sie darf durchaus neue Daten ergänzen. Deshalb gibt es überhaupt
zwei Modi. Wer sie „vereinheitlicht", nimmt genau den Schutz heraus.

Ein Abbruch ist das richtige Verhalten und keine Störung: er lässt den letzten
guten Stand stehen, und die Seite bleibt funktionsfähig.

## Verworfene Alternativen

- **Immer Voll-Scan-Semantik:** ein einzelner schlechter Overpass-Tag leert die
  Karte.
- **Schwellenwert („löschen nur, wenn weniger als 20 % fehlen"):** willkürlich und
  schwer zu begründen; der harte Abbruch bei null Treffern ist eindeutig.
- **`--mock` behalten:** war die konkrete Fehlerquelle, nicht ihre Lösung.

## Konsequenzen

- **In einer sandboxed Session ist Overpass nicht erreichbar** (der Proxy
  antwortet mit 403 auf das CONNECT). `python3 scanner.py` bricht dann ab — und
  das ist das korrekte Verhalten, nicht ein Fehler der Umgebung. Pipeline-Änderungen
  werden dort mit der unittest-Suite geprüft, nicht mit echten Daten. Neue Spalten
  bleiben `NULL`, bis der nächste Sonntagslauf sie füllt. Das gehört so gesagt,
  statt eine Datenaktualisierung anzudeuten.
- Vor jedem Push von Pipeline-Änderungen: `python3 -m unittest discover -s tests -v`.
