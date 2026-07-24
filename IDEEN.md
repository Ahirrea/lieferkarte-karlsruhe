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

## Änderungs-Feed („Diese Woche neu …") ✅ **umgesetzt**

**Ziel:** Zeigen, was sich seit dem letzten Scan geändert hat – neue
Restaurants, verschwundene, geänderte Liefer-/Abhol-/Adressangaben.

> **Stand:** umgesetzt. `export.py` (`build_feed()`) schreibt den Block `feed`
> nach `web/restaurants.json`, `web/index.html` zeigt ihn über den Knopf
> „🆕 Diese Woche" in einem Panel – gruppiert nach Änderungsart, ein Klick
> zentriert die Karte auf das Restaurant und öffnet das Popup (auch wenn der
> Marker gerade weggefiltert ist). Feldbeschreibung: `TECHNICAL.md`.

**Datenquelle:** die `changes`-Tabelle, die `scanner.py` ohnehin bei jedem Scan
füllt – es war also reine Export- + Anzeigearbeit, kein neuer Request.

**Die drei Haken (so gelöst):**

1. **Der Erstimport ist keine Neuigkeit.** Der allererste Scan protokolliert
   *jedes* gefundene Restaurant als `NEW` (hier: 883 Zeilen). Ungefiltert hätte
   der Feed „883 neu diese Woche" gemeldet. Der Feed blendet daher alles aus,
   was am Zeitstempel des ersten `scan_runs`-Eintrags protokolliert wurde.
2. **Massen-Ereignisse.** Kommt ein Feld neu in die Pipeline, ändern sich auf
   einen Schlag hunderte Werte (bei `takeaway`: 245 × „unbekannt → ja"). Pro
   Änderungsart landen deshalb nur `FEED_MAX_PER_TYPE` Einträge in der JSON;
   die vollständige Zahl steht in `counts`, die Anzeige ergänzt „… und N
   weitere".
3. **Zeitfenster ab Scan, nicht ab „jetzt".** Sonst wäre der Feed leer, sobald
   der Export einmal Tage nach dem Scan läuft (oder die Seite länger nicht neu
   gebaut wurde). Anker ist der jüngste `scan_runs`-Zeitstempel.

**Bewusst nicht gemacht:** „neu" heißt *neu in OpenStreetMap erfasst*, nicht
„neu eröffnet" – das lässt sich aus OSM-Daten nicht unterscheiden. Ein Hinweis
dazu steht im Panel, statt eine Aussage zu treffen, die die Daten nicht tragen.

---

## Weitere offene Punkte

- **Lieferung/Abholung filtern:** Details + echte Abdeckungszahlen stehen in
  `VOR-VEROEFFENTLICHUNG.md` (Abschnitt „Filter für Abdeckung anpassen").
