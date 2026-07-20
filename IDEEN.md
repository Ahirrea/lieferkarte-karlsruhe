# Ideen & Feature-Backlog

Geplante, noch **nicht umgesetzte** Features. Kein Zeitplan – hier wird
festgehalten, was als Nächstes sinnvoll wäre.

---

## Öffnungszeiten anzeigen (+ Bonus: „jetzt geöffnet")

**Ziel:** Zu jedem Restaurant die Öffnungszeiten im Popup anzeigen.
**Bonus:** sichtbar machen (und ggf. filtern), was **gerade jetzt** geöffnet hat.

**Datenquelle:** OSM-Tag `opening_hours` – kommt beim Overpass-Scan kostenlos
mit (der Query holt bereits alle Tags). Die Abdeckung in Karlsruhe ist noch
nicht gemessen; wie bei `delivery`/`takeaway` vermutlich lückenhaft. Vor dem Bau
einmal zählen, sobald das Feld erfasst wird.

**Umsetzung – Pipeline (klein):**
- `scanner.py`: in `normalize_osm()` `opening_hours` aus `tags` lesen; DB-Spalte
  `opening_hours TEXT` ergänzen (+ Migration `ALTER TABLE ADD COLUMN`, wie bei
  `takeaway`).
- `export.py`: Feld `openingHours` in `restaurants.json`.
- `web/index.html`: Öffnungszeiten im Popup ausgeben (als Text).

**Bonus „jetzt geöffnet" – der Haken:** Das OSM-`opening_hours`-Format ist
mächtig und komplex, z. B.
`Mo-Fr 11:00-14:30,17:00-23:00; Sa 17:00-23:00; PH off`.
Ein zuverlässiger „ist gerade offen?"-Check muss dieses Format clientseitig
parsen. Optionen:

- **Eigener Mini-Parser** für die häufigsten Muster (deckt grob die Mehrheit ab,
  aber nicht alle Sonderfälle wie Feiertage `PH`, `sunrise`/`sunset`, Wochen-
  regeln). Leichtgewichtig, ohne Abhängigkeit.
- **Etablierte Lib `opening_hours.js`** (deckt praktisch alles ab). **ABER:**
  muss zur harten Regel „keine externen Requests / statisch / kein Tracking"
  passen → nur **lokal eingebunden (vendored)**, nicht per CDN nachladen.
- Zeitzone/Sommerzeit beachten (Europe/Berlin); die Berechnung läuft im Browser
  des Nutzers (passt zum „kein Server, keine Datenerfassung"-Prinzip).

**Aufwand:** Öffnungszeiten *anzeigen* = klein. „*Jetzt geöffnet*" = mittel
(wegen des Parsings). Beides kann in zwei Schritten kommen.

---

## Weitere offene Punkte

- **Lieferung/Abholung filtern:** Details + echte Abdeckungszahlen stehen in
  `VOR-VEROEFFENTLICHUNG.md` (Abschnitt „Filter für Abdeckung anpassen").
