# ADR-002: Kein Backend — DB und JSON werden ins Repo committet

**Status:** akzeptiert (nachträglich dokumentiert am 2026-07-25)
**Datum:** 2026-07-25

## Kontext

Die Karte braucht aktuelle Daten, aber das Projekt soll **keine laufenden Kosten**
haben und **keine Nutzerdaten erfassen**. Ein Server wäre beides: eine monatliche
Rechnung und eine Stelle, an der man Daten sammeln *könnte*.

Gleichzeitig soll die Abfrage bei Overpass nicht bei jedem Seitenaufruf laufen —
das wäre unhöflich gegenüber einem kostenlosen Dienst und langsam für die Nutzerin.

## Entscheidung

Eine **wöchentliche GitHub Action** übernimmt die Rolle, die sonst ein Server
hätte. Sie ruft Overpass ab, schreibt in `data/restaurants.db` (SQLite),
generiert daraus `web/restaurants.json` und **committet beides nach `main`**.
GitHub Pages liefert aus `main`/Wurzel aus, der Browser lädt eine statische Datei
vom selben Origin.

Die Datenpipeline läuft in einer Richtung:

```
scanner.py → data/restaurants.db → export.py → web/restaurants.json → web/index.html
```

## Begründung

- Null laufende Kosten, kein Server, kein Secret-Handling.
- Kein Ort, an dem Nutzerdaten anfallen könnten — das „keine Cookies, kein
  Tracking"-Versprechen ist damit strukturell erfüllt, nicht nur zugesagt.
- **Die Git-Historie der DB *ist* das Änderungsprotokoll.** Jeder Scan-Commit ist
  ein nachvollziehbarer Datenstand (daher `fetch-depth: 0` im Workflow).
- Ein Ausfall von Overpass bricht die Seite nicht — der letzte Snapshot bleibt.

Unter der ODbL ist das Committen der Daten zulässig; mit Google Places wäre
genau das ein Vertragsbruch gewesen (siehe
[ADR-001](./ADR-001-openstreetmap-statt-google-places.md)).

## Verworfene Alternativen

- **Server oder Serverless-Funktion mit Live-Abruf:** laufende Kosten,
  Laufzeitabhängigkeit, Cold Starts — für wöchentlich wechselnde Daten unnötig.
- **Overpass direkt aus dem Browser:** belastet einen kostenlosen Dienst pro
  Seitenaufruf und macht die Seite von seiner Verfügbarkeit abhängig.
- **Pages über ein Actions-Deployment ausliefern:** würde Snapshots ausliefern und
  damit veraltete Daten zeigen.

## Konsequenzen

- **Die Action committet selbst auf `main`.** Der lokale Stand ist nach einem Lauf
  schnell veraltet — vor dem eigenen Push `git pull --rebase origin main`, sonst
  wird er mit „fetch first" abgelehnt.
- Datenänderungen und Code-Änderungen liegen in derselben Historie. Das ist
  gewollt, macht aber `git log` für `data/` und für Code getrennt lesenswert.
- Der Datenstand ist maximal eine Woche alt. Für Restaurantdaten ausreichend, für
  „hat der Laden jetzt offen?" nicht — deshalb wird `opening_hours` clientseitig
  gegen die aktuelle Zeit ausgewertet (siehe
  [ADR-004](./ADR-004-oeffnungszeiten-eigener-parser.md)).
