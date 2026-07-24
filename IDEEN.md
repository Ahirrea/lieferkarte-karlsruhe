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

## Filter nach Küchenstil (Pizza, Thai, Burger, …) ✅ **umgesetzt**

**Ziel:** Die Karte nach Küchenstil filtern können und den Stil im Popup zeigen.

**Datenquelle:** OSM-Tag `cuisine` – kommt beim Overpass-Scan kostenlos mit
(der Query holt bereits alle Tags).

**Umsetzung – Pipeline:**
- `scanner.py`: `_osm_cuisine()` normalisiert das Tag, `normalize_osm()` liest es;
  DB-Spalte `cuisine TEXT` inkl. Migration (`ALTER TABLE ADD COLUMN`, wie bei
  `takeaway`/`opening_hours`).
- `export.py`: Feld `cuisines` in `restaurants.json` – immer eine **Liste**
  (`["pizza","italian"]`), leere Liste = nicht getaggt.
- `web/index.html`: Auswahlliste „🍽️ Alle Küchen" im Kopf, Küchenzeile im Popup,
  Küchenstil zusätzlich im Suchfeld auffindbar („thai", „Italienisch").

**Normalisierung (der Haken):** `cuisine` ist ein Freitext-Tag mit Mehrfachwerten
und wechselnder Schreibweise: `pizza;italian`, `Pizza; Kebab`, `burger, american`,
`Ice Cream`, `coffee-shop`. `_osm_cuisine()` macht daraus eine kanonische,
`;`-getrennte Liste aus kleingeschriebenen Schlüsseln mit `_` statt
Leerzeichen/Bindestrich, verwirft Dubletten und nichtssagende Werte
(`yes`, `no`, `unknown`, `fixme`, `other`). Die Reihenfolge aus OSM bleibt
erhalten (der erste Wert ist meist der Hauptstil).

**Deutsche Bezeichnungen** liegen bewusst im Frontend (`CUISINE_LABELS`), nicht in
der DB: die DB bleibt roh und verlustfrei, Übersetzungen sind Anzeige-Sache. Für
nicht übersetzte Werte greift ein Rückfall (`ice_cream` → „Ice Cream"), damit auch
seltene Stile filterbar bleiben statt zu verschwinden.

**Auswahlliste** baut sich aus den tatsächlich vorhandenen Werten – häufigste
zuerst, mit Anzahl („Pizza (148)"). Ohne getaggte Küchenstile bleibt der Filter
komplett versteckt; die Karte sieht damit unverändert aus, bis der nächste Scan
die Werte einträgt. Bei aktivem Filter fallen ungetaggte Restaurants heraus
(„unbekannt" ist kein Treffer – wie beim Lieferfilter).

**Bewusst nicht gemacht:**
- **Kein `CUISINE_CHANGED` im Änderungsprotokoll.** Umtaggen in OSM
  (`pizza` → `pizza;italian`) ist häufig und für den geplanten Änderungs-Feed
  ohne Aussagekraft – der aktuelle Wert genügt.
- **Keine Synonym-Gruppierung** (`sushi` unter `japanese`, `doner` unter `kebab`).
  Das wäre Interpretation der OSM-Daten; die Liste zeigt, was getaggt ist. Falls
  die Auswahl später zu lang wirkt, ist Gruppieren der nächste Schritt.

**Abdeckung:** noch nicht gemessen – die Spalte ist erst nach dem nächsten
Voll-Scan gefüllt. Zum Nachzählen dann:
`SELECT cuisine, COUNT(*) FROM restaurants WHERE active=1 GROUP BY cuisine ORDER BY 2 DESC;`

---

## Weitere offene Punkte

- **Lieferung/Abholung filtern:** Details + echte Abdeckungszahlen stehen in
  `VOR-VEROEFFENTLICHUNG.md` (Abschnitt „Filter für Abdeckung anpassen").
