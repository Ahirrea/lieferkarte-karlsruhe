# ✅ Done (Umgesetzt)

Fertig und live. Die Abschnitte bleiben als Kurzprotokoll stehen – interessant
ist jeweils **der Haken**: warum es so gelöst ist und nicht anders.

**Backlog:** [💡 Ideen](IDEEN.md) · [🔨 Ready for Dev](READY-FOR-DEV.md) ·
✅ Done · [Übersicht](README.md)

---

## Öffnungszeiten + „jetzt geöffnet" ✅

**Was:** Öffnungszeiten im Popup, dazu ein Badge „🟢 Jetzt geöffnet" / „🔴 Jetzt
geschlossen" und der optionale Filter „nur jetzt geöffnet".

**Umsetzung:**
- `scanner.py` liest das OSM-Tag `opening_hours` (DB-Spalte `opening_hours TEXT`
  inkl. Migration), `export.py` exportiert `openingHours`.
- `web/index.html` zeigt die Zeiten als Text (Wochentags-Kürzel eingedeutscht,
  eine Regel pro Zeile) und wertet sie in `openStateNow()` aus.

**Der Haken:** Das OSM-Format ist mächtig und komplex
(`Mo-Fr 11:00-14:30,17:00-23:00; Sa 17:00-23:00; PH off`). Gewählt wurde ein
**eigener Mini-Parser** statt einer Lib – leichtgewichtig, keine Abhängigkeit,
kein Request. Er deckt die häufigen Muster ab (Tagesbereiche/-listen, mehrere
Intervalle, Über-Mitternacht wie `Fr 20:00-04:00`, `off`/`closed`, `24/7`) und
ist **bewusst konservativ**: alles Unsichere ergibt „unbekannt" (kein Badge),
statt eine falsche Aussage zu riskieren. Nicht ausgewertet werden offene Zeiten
ohne Ende (`18:30+`), Feiertags-/Ferienregeln (`PH`/`SH` – clientseitig nicht
ermittelbar), Monats-/Wochenregeln, Freitext und `sunrise`/`sunset`.

Die Uhrzeit wird über `Intl` fest in **Europe/Berlin** gerechnet – unabhängig von
der Zeitzone des Nutzers, inklusive Sommer-/Winterzeit, komplett im Browser
(passt zum „kein Server, keine Datenerfassung"-Prinzip).

**Abdeckung:** 741 Restaurants haben Zeiten, davon sind ~90 % eindeutig
auswertbar; ~10 % bleiben „unbekannt". (Volle Abdeckung wäre
[Idee 9](IDEEN.md#9-ausbau-von-bereits-umgesetztem).)

## Filter nach Küchenstil ✅

**Was:** Nach Küchenstil filtern und den Stil im Popup zeigen. Datenquelle ist
das OSM-Tag `cuisine`, das beim Scan kostenlos mitkommt.

**Umsetzung:**
- `scanner.py`: `_osm_cuisine()` normalisiert das Tag, DB-Spalte `cuisine TEXT`
  inkl. Migration.
- `export.py`: Feld `cuisines` in `restaurants.json` – immer eine **Liste**
  (`["pizza","italian"]`), leere Liste = nicht getaggt.
- `web/index.html`: Auswahlliste „🍽️ Alle Küchen" im Kopf, Küchenzeile im
  Popup, Küchenstil zusätzlich über das Suchfeld auffindbar.

**Der Haken – Normalisierung:** `cuisine` ist ein Freitext-Tag mit
Mehrfachwerten und wechselnder Schreibweise (`pizza;italian`, `Pizza; Kebab`,
`burger, american`, `Ice Cream`, `coffee-shop`). `_osm_cuisine()` macht daraus
eine kanonische, `;`-getrennte Liste kleingeschriebener Schlüssel mit `_` statt
Leerzeichen/Bindestrich, verwirft Dubletten und nichtssagende Werte (`yes`, `no`,
`unknown`, `fixme`, `other`). Die OSM-Reihenfolge bleibt erhalten (der erste Wert
ist meist der Hauptstil).

Die **deutschen Bezeichnungen** liegen bewusst im Frontend (`CUISINE_LABELS`),
nicht in der DB: die DB bleibt roh und verlustfrei, Übersetzungen sind
Anzeige-Sache. Für nicht übersetzte Werte greift ein Rückfall (`ice_cream` →
„Ice Cream"), damit auch seltene Stile filterbar bleiben.

Die Auswahlliste baut sich aus den tatsächlich vorhandenen Werten – häufigste
zuerst, mit Anzahl („Pizza (148)"). Ohne getaggte Küchenstile bleibt der Filter
komplett versteckt. Bei aktivem Filter fallen ungetaggte Restaurants heraus
(„unbekannt" ist kein Treffer – wie beim Lieferfilter).

**Bewusst nicht gemacht:** kein `CUISINE_CHANGED` im Änderungsprotokoll –
Umtaggen in OSM (`pizza` → `pizza;italian`) ist häufig und für den Feed ohne
Aussagekraft; der aktuelle Wert genügt. (Zur Abdeckung siehe
[Idee 8](IDEEN.md#8-küchenstil-abdeckung-prüfen).)

## Änderungs-Feed „Diese Woche neu …" ✅

**Was:** Zeigen, was sich seit dem letzten Scan geändert hat – neue Restaurants,
verschwundene, geänderte Liefer-/Abhol-/Adressangaben.

**Umsetzung:** `export.py` (`build_feed()`) schreibt den Block `feed` nach
`web/restaurants.json`, `web/index.html` zeigt ihn über den Knopf „🆕 Diese
Woche" in einem Panel – gruppiert nach Änderungsart; ein Klick zentriert die
Karte auf das Restaurant und öffnet das Popup (auch wenn der Marker gerade
weggefiltert ist). Datenquelle ist die `changes`-Tabelle, die `scanner.py`
ohnehin füllt – reine Export- und Anzeigearbeit, kein neuer Request.
Feldbeschreibung: [`TECHNICAL.md`](../TECHNICAL.md).

**Die drei Haken:**

1. **Der Erstimport ist keine Neuigkeit.** Der allererste Scan protokolliert
   *jedes* Restaurant als `NEW` (hier: 883 Zeilen). Ungefiltert hätte der Feed
   „883 neu diese Woche" gemeldet. Er blendet daher alles aus, was am Zeitstempel
   des ersten `scan_runs`-Eintrags protokolliert wurde.
2. **Massen-Ereignisse.** Kommt ein Feld neu in die Pipeline, ändern sich auf
   einen Schlag hunderte Werte (bei `takeaway`: 245 × „unbekannt → ja"). Pro
   Änderungsart landen deshalb nur `FEED_MAX_PER_TYPE` Einträge in der JSON; die
   vollständige Zahl steht in `counts`, die Anzeige ergänzt „… und N weitere".
3. **Zeitfenster ab Scan, nicht ab „jetzt".** Sonst wäre der Feed leer, sobald
   der Export Tage nach dem Scan läuft. Anker ist der jüngste
   `scan_runs`-Zeitstempel.

**Bewusst nicht gemacht:** „neu" heißt *neu in OpenStreetMap erfasst*, nicht „neu
eröffnet" – das lässt sich aus OSM-Daten nicht unterscheiden. Ein Hinweis dazu
steht im Panel, statt eine Aussage zu treffen, die die Daten nicht tragen.

## PWA „zum Homescreen hinzufügen" ✅

**Was:** Die Karte lässt sich wie eine App auf den Homescreen legen, startet im
Vollbild und funktioniert auch ohne Netz (unterwegs im Funkloch ist eine
Lieferkarte sonst wenig wert).

**Umsetzung – drei statische Dateien**, kein Build-Schritt, keine Abhängigkeit:
- `web/manifest.webmanifest` – Name, Icons, `display: standalone`, Farben und
  zwei App-Verknüpfungen („Jetzt geöffnet" → `?open=1`, „In meiner Nähe" →
  `?nearby=1`).
- `web/sw.js` – Service Worker mit Precache und pro Inhalt passender Strategie.
- `web/icons/*.png` – erzeugt von `tools/make_icons.py` (nur Standardbibliothek).

Dazu im Frontend der `📲 App installieren`-Button (`beforeinstallprompt`, auf iOS
stattdessen die Anleitung übers Teilen-Menü) und eine Hinweisleiste für „Offline
– gespeicherte Daten vom …" bzw. „Neue Version verfügbar". Geprüft wird das
Zusammenspiel von Manifest, Icons und Precache-Liste durch `tests/test_pwa.py`.

**Der Haken – wöchentlich neue Daten:** Ein naiver „cache first"-Worker hätte die
installierte App auf dem Datenstand des Installationstags eingefroren. Deshalb:

- `restaurants.json` läuft **network first** – der Cache greift nur ohne Netz und
  wird dann sichtbar als Offline-Stand ausgewiesen (Datum aus `lastScanAt`).
- Auch HTML/Manifest kommen network first, damit neue Versionen nicht hinter
  einem alten Cache hängen bleiben.
- Eine neue Worker-Version übernimmt **nicht** von selbst (kein `skipWaiting`
  beim Installieren): die Seite fragt erst („Jetzt neu laden").
- Bei jeder Rückkehr zur App wird nach Updates gesucht – eine installierte App
  wird oft wochenlang nicht neu geladen.

**Bewusste Einschränkungen:**
- **Kartenkacheln** werden nur *nachträglich* gecacht (max. 400, cache first) –
  besuchte Gegenden funktionieren offline, es wird aber nichts auf Vorrat
  geladen (Rücksicht auf die kostenlosen OSM-Tile-Server).
- **Leaflet kommt weiterhin vom CDN** (mit `integrity`-Hash), der Worker cacht es
  „best effort" mit. Vendoren wäre der nächste Schritt
  ([Idee 9](IDEEN.md#9-ausbau-von-bereits-umgesetztem)).
- **Keine Push-Nachrichten, keine Background-Sync-Registrierung** – das würde
  dem „kein Tracking, keine Datenerfassung"-Versprechen widersprechen. Der
  Worker cacht ausschließlich, er sendet nichts.
