# Ideen & Feature-Backlog

Geplante, noch **nicht umgesetzte** Features. Kein Zeitplan – hier wird
festgehalten, was als Nächstes sinnvoll wäre.

---

## Öffnungszeiten anzeigen (+ Bonus: „jetzt geöffnet")

**Ziel:** Zu jedem Restaurant die Öffnungszeiten im Popup anzeigen. ✅ **umgesetzt**
**Bonus:** sichtbar machen (und ggf. filtern), was **gerade jetzt** geöffnet hat.
✅ **umgesetzt** (siehe „der Haken" unten – bewusst konservativ gelöst).

> **Stand:** Das *Anzeigen* der Öffnungszeiten ist umgesetzt: `scanner.py` liest
> das OSM-Tag `opening_hours` (DB-Spalte `opening_hours TEXT` + Migration),
> `export.py` exportiert `openingHours`, und das Popup zeigt die Zeiten als Text
> (Wochentags-Kürzel eingedeutscht, eine Regel pro Zeile).
>
> **„jetzt geöffnet" ist jetzt auch umgesetzt** – rein clientseitig in
> `web/index.html` (`openStateNow()`), ohne externe Lib und ohne Request. Es
> gibt ein Badge im Popup („🟢 Jetzt geöffnet" / „🔴 Jetzt geschlossen") und
> den optionalen Filter „nur jetzt geöffnet". Die Uhrzeit wird über `Intl` in
> **Europe/Berlin** berechnet (unabhängig von der Zeitzone des Nutzers, inkl.
> Sommer-/Winterzeit). Abdeckung der 741 Restaurants mit Zeiten: ~90 % sind
> eindeutig auswertbar, ~10 % bleiben „unbekannt" (kein Badge).

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

**Bonus „jetzt geöffnet" – der Haken (so gelöst):** Das OSM-`opening_hours`-
Format ist mächtig und komplex, z. B.
`Mo-Fr 11:00-14:30,17:00-23:00; Sa 17:00-23:00; PH off`.
Gewählt wurde der **eigene Mini-Parser** (Option 1) statt der Lib – leicht­
gewichtig, keine Abhängigkeit. Er deckt die häufigen Muster ab
(Tagesbereiche/-listen, mehrere Zeitintervalle, Über-Mitternacht wie
`Fr 20:00-04:00`, `off`/`closed`, `24/7`) und ist **bewusst konservativ**:
alles Unsichere ergibt „unbekannt" (kein Badge), statt eine falsche Aussage zu
riskieren. Konkret nicht ausgewertet:

- **Offene Zeiten** ohne Ende (`18:30+`) – Schließzeit unbekannt → „unbekannt".
- **Feiertage/Ferien** (`PH`/`SH`) – ob heute Feiertag ist, lässt sich
  clientseitig nicht ermitteln → solche Regeln werden ignoriert.
- **Monats-/Wochenregeln** (`May-Sep …`), Freitext (`"by appointment"`),
  `sunrise`/`sunset` → „unbekannt".
- **Zeitzone/Sommerzeit**: über `Intl` fest in **Europe/Berlin** gerechnet,
  unabhängig von der Zeitzone des Nutzers. Läuft komplett im Browser (passt zum
  „kein Server, keine Datenerfassung"-Prinzip).

Falls später die volle Abdeckung gewünscht ist, bliebe als Ausbau die
**vendored `opening_hours.js`** (lokal eingebunden, kein CDN) – aktuell aber
nicht nötig, da ~90 % der getaggten Fälle schon eindeutig auswertbar sind.

**Aufwand:** war wie erwartet – *anzeigen* klein, „*jetzt geöffnet*" mittel
(Parsing). Beide Schritte sind jetzt erledigt.

---

## Weitere offene Punkte

- **Lieferung/Abholung filtern:** Details + echte Abdeckungszahlen stehen in
  `VOR-VEROEFFENTLICHUNG.md` (Abschnitt „Filter für Abdeckung anpassen").
