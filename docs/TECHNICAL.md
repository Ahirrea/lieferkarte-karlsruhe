# Lieferkarte Karlsruhe – Technische Dokumentation

Findet Restaurants mit Lieferservice über die **Overpass API**
(OpenStreetMap), speichert sie in SQLite, erkennt Änderungen zwischen Scans
und zeigt alles auf einer Karte (Leaflet + OpenStreetMap). Kostenlos, kein
API-Key, und weil OSM unter der ODbL steht, dürfen die Daten öffentlich
weitergegeben werden.

## Architektur

```
scanner.py  ──>  data/restaurants.db  ──>  export.py  ──>  web/restaurants.json
 (Overpass API)    (SQLite:                                      │
                    restaurants,                                  v
                    changes,                                web/index.html
                    scan_runs)                              (Leaflet-Karte)
```

- **restaurants**: aktueller Bestand, `place_id` als stabiler Schlüssel
- **changes**: Änderungsprotokoll (NEW / REMOVED / ADDRESS_CHANGED / DELIVERY_CHANGED / TAKEAWAY_CHANGED / STATUS_CHANGED)
- **scan_runs**: wann lief welcher Scan mit wie vielen API-Aufrufen (Kostenkontrolle)

## Schnellstart (ohne API-Key)

```bash
python3 scanner.py            # Voll-Scan über Overpass (ein Request, kein Key)
python3 export.py             # erzeugt web/restaurants.json
cd web && python3 -m http.server 8000
# -> http://localhost:8000 im Browser öffnen
```

Tests (nur Standardbibliothek, arbeiten mit Temporär-DBs):

```bash
python3 -m unittest discover -s tests -v
```

## Echter Scan (OpenStreetMap/Overpass)

Kein Setup, kein API-Key, keine Anmeldung. Der Scanner stellt eine einzige
Overpass-Abfrage über das komplette Suchgebiet.

### Scanner laufen lassen

```bash
# Voll-Scan: Bestand + Änderungen + REMOVED-Erkennung
python3 scanner.py

# Refresh ohne REMOVED-Erkennung
python3 scanner.py --light
```

Dann:
```bash
python3 export.py           # erzeugt web/restaurants.json
cd web && python3 -m http.server 8000
```

### Overpass-Abfrage

`scanner.py` fragt alle `amenity=restaurant`/`fast_food` im 12-km-Umkreis um
das Karlsruher Zentrum ab (`nwr(around:...)`, `out center tags`). Aus den Tags
werden Name, Adresse (`addr:*`), Koordinaten, `website`/`contact:website`,
`delivery` und `takeaway` (`yes`/`only` → 1, `no` → 0, sonst unbekannt),
`opening_hours` (Rohtext) und `cuisine` (Küchenstil) übernommen.

**`cuisine` wird normalisiert** (`_osm_cuisine()`): OSM erlaubt mehrere Werte in
einem Tag und beliebige Schreibweise (`pizza;italian`, `Pizza; Kebab`,
`burger, american`, `Ice Cream`). In der Spalte `cuisine` steht daraus eine
kanonische, `;`-getrennte Liste kleingeschriebener Schlüssel mit `_` statt
Leerzeichen/Bindestrich (`"pizza;italian"`, `"ice_cream"`); Dubletten und
nichtssagende Werte (`yes`, `no`, `unknown`, `fixme`, `other`) fallen weg,
`NULL` = nicht getaggt. `export.py` gibt das Feld als Liste `cuisines` aus
(leere Liste = unbekannt), die deutschen Bezeichnungen liegen im Frontend
(`CUISINE_LABELS`). Änderungen am Küchenstil werden **nicht** protokolliert
(siehe [`UMGESETZT.md`](./UMGESETZT.md)).

Der Endpoint ist per Umgebungsvariable überschreibbar, falls ein Spiegelserver
nötig wird:

```bash
export OVERPASS_ENDPOINT="https://overpass.kumi.systems/api/interpreter"
```

## Änderungs-Feed („Diese Woche neu …")

`export.py` schreibt neben dem Bestand zwei Sichten auf die `changes`-Tabelle
nach `web/restaurants.json`:

- **`recentChanges`** – die rohen letzten `RECENT_CHANGES_LIMIT` (50) Zeilen,
  ungefiltert. Nur zur Kontrolle/Fehlersuche, wird nicht angezeigt.
- **`feed`** – die anzeigefertige Sicht (`build_feed()`), die
  `web/index.html` im Panel „🆕 Diese Woche" darstellt:

```json
"feed": {
  "since": "2026-07-14T16:07:05+00:00",   // Fensterbeginn
  "until": "2026-07-21T16:07:05+00:00",   // Anker = jüngster Scan
  "windowDays": 7,
  "total": 245,                            // Änderungen im Fenster (ungekappt)
  "counts": { "NEW": 3, "TAKEAWAY_CHANGED": 242 },
  "items": [
    { "placeId": "node/123", "type": "NEW", "name": "…", "address": "…",
      "lat": 49.0, "lng": 8.4, "oldValue": null, "newValue": "…",
      "detectedAt": "2026-07-21T16:07:05+00:00", "active": true }
  ]
}
```

Drei Regeln, die dabei absichtlich so sind:

1. **Zeitfenster ab dem letzten Scan** (`FEED_WINDOW_DAYS = 7`), nicht ab
   „jetzt" – sonst wäre der Feed leer, wenn der Export Tage nach dem Scan läuft.
2. **Der Erstimport bleibt draußen.** Der erste Scan protokolliert jedes
   Restaurant als `NEW`; alles mit dem Zeitstempel des ersten
   `scan_runs`-Eintrags wird ausgeblendet (sonst „883 neu diese Woche").
3. **Pro Änderungsart max. `FEED_MAX_PER_TYPE` (12) Einträge** in `items` –
   `counts` nennt trotzdem die vollständige Zahl, die Anzeige ergänzt „… und N
   weitere". Hält die JSON klein, wenn ein Massen-Ereignis auftritt (z. B. 245
   neu getaggte `takeaway`-Werte auf einen Schlag).

Die Einträge sind mit Name/Adresse/Koordinaten aus `restaurants` angereichert
(LEFT JOIN), damit die Karte sie anspringen kann – auch `REMOVED`-Einträge, die
in `restaurants` nur noch mit `active = 0` stehen und im Bestands-Export fehlen.
`items` ist nach Änderungsart gruppiert (Reihenfolge: `FEED_TYPE_ORDER`),
innerhalb einer Gruppe neueste zuerst.

## Kostenübersicht

**0 €.** Die Overpass-API ist kostenlos und ohne API-Key nutzbar. Ein Scan =
ein HTTP-Request. Overpass bittet lediglich um faire Nutzung (deshalb ein
freundlicher `User-Agent` und Retry-Backoff bei `429`/`504`).

Kein Google-Cloud-Projekt, kein Billing, kein Budget-Alarm mehr nötig – die
frühere `PLACES_API_KEY`-Logik entfällt komplett.

## GitHub Actions Workflow

Damit der Scanner automatisch wöchentlich läuft:

### 1. Datei `.github/workflows/weekly-scan.yml` anlegen

```yaml
name: Weekly Restaurant Scan

on:
  schedule:
    # Jeden Sonntag um 06:00 UTC (07:00 MEZ)
    - cron: '0 6 * * 0'
  workflow_dispatch:  # manuell auch triggerbar

jobs:
  scan:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v5
        with:
          fetch-depth: 0  # komplette History, wichtig für die DB

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.12'

      - name: Run scanner
        run: |
          python3 scanner.py

      - name: Export to JSON
        run: python3 export.py

      - name: Commit & Push
        run: |
          git config --local user.email "action@github.com"
          git config --local user.name "Lieferkarte Scanner"
          git add data/restaurants.db web/restaurants.json
          git diff --cached --quiet || git commit -m "🤖 Weekly scan: $(date -I)"
          git push
```

### 2. Kein Secret nötig

Overpass braucht keinen API-Key – Schritt entfällt. (Die tatsächlich im Repo
verwendete Workflow-Datei bietet zusätzlich `workflow_dispatch` mit
Modus-Auswahl `full`/`light`.)

### 3. GitHub Pages konfigurieren

1. Repo → Settings → "Pages"
2. Source: "Deploy from a branch"
3. Branch: `main`
4. Folder: `/ (root)`
5. Speichern

GitHub baut dann automatisch die Seite bei jedem neuen Commit.

**URL der Live-Seite:** `https://dein-github-username.github.io/lieferkarte-karlsruhe/`

(Falls du es später auf `lieferkarte-karlsruhe.github.io` als eigene Org migrierst, ist das nur ein umbenanntes Repo.)

## PWA („zum Homescreen hinzufügen")

Die Seite ist eine installierbare Progressive Web App und funktioniert offline.
Dafür sind keine Abhängigkeiten und kein Build-Schritt nötig – drei statische
Dateien genügen:

| Datei | Zweck |
|---|---|
| `web/manifest.webmanifest` | Name, Icons, Startadresse, `display: standalone`, Farben, App-Verknüpfungen |
| `web/sw.js` | Service Worker: Precache + Caching-Strategien + Update-Logik |
| `web/icons/*.png` | App-Icons (192/512 normal + maskable, Apple-Touch, Favicon) |

Alle Pfade im Manifest und im Service Worker sind **relativ** (`./…`) – die Seite
liegt auf GitHub Pages unter `/<repo>/web/`, absolute Pfade würden dort ins Leere
zeigen.

### Caching-Strategien (in `web/sw.js`)

| Inhalt | Strategie | Warum |
|---|---|---|
| `restaurants.json` | **network first**, Cache nur als Rückfall | Die Daten sind wöchentlich neu – der Sonntags-Scan muss sofort ankommen. Kommt die Kopie aus dem Cache, setzt der Worker den Header `X-Lieferkarte-Cache: hit`; die Seite zeigt daraufhin „📴 Offline – gespeicherte Daten vom …". |
| HTML / Manifest | **network first** | Eine neue Version der Seite darf nicht hinter einem alten Cache hängen bleiben. |
| Icons, Leaflet (CDN) | **cache first** | Stabile bzw. versionierte URLs. |
| Kartenkacheln (`*.tile.openstreetmap.org`) | **cache first**, max. `MAX_TILES` (400) | Bereits besuchte Kacheln kommen aus dem Cache; es wird nichts auf Vorrat geladen (Rücksicht auf die kostenlosen Tile-Server). |

Leaflet und die Kacheln werden teils als `no-cors` angefragt; solche Antworten
sind „opaque" und schlecht cachebar. Beide Server erlauben CORS, deshalb holt
`corsFetch()` sie bewusst als CORS-Anfrage und fällt nur im Fehlerfall auf die
Originalanfrage zurück.

### Update-Strategie

- Der Worker ruft **kein** `skipWaiting()` beim Installieren. Eine neue Version
  wartet, die Seite zeigt „🔄 Neue Version verfügbar." und erst der Klick
  schickt `SKIP_WAITING` – so wird nie mitten im Betrieb die halbe Seite
  ausgetauscht. Danach löst `controllerchange` einen Reload aus (nur wenn das
  Update auch bestätigt wurde, sonst würde die Erstinstallation neu laden).
- Bei jeder Rückkehr zur App (`visibilitychange`) läuft `registration.update()` –
  wichtig, weil eine installierte App oft wochenlang nicht neu geladen wird.
- **Beim Ändern gecachter Dateien `CACHE_VERSION` in `web/sw.js` erhöhen.** Beim
  Aktivieren löscht der Worker dann alle `lieferkarte-*`-Caches der alten
  Version.

### Icons neu erzeugen

Die PNGs liegen fertig im Repo. Wenn sich das Design ändert:

```bash
python3 tools/make_icons.py     # schreibt web/icons/*.png (nur Standardbibliothek)
```

Das Skript zeichnet das Motiv (Teller + Besteck in `--accent`) geometrisch und
schreibt die PNGs selbst – kein Pillow, kein ImageMagick nötig. Die maskierbaren
Varianten füllen die Fläche komplett und halten das Motiv in der Safe Zone
(mittlere 80 %), damit Android es beliebig zuschneiden kann.

### Testen

`tests/test_pwa.py` prüft rein lesend, dass Manifest und Service Worker zu den
tatsächlich vorhandenen Dateien passen (Icon-Größen aus dem PNG-Header, keine
Precache-Pfade ins Leere, `CACHE_VERSION` gesetzt, kein automatisches
`skipWaiting`). Im Browser lokal prüfen:

```bash
cd web && python3 -m http.server 8000
# -> http://localhost:8000 (localhost gilt als sicherer Kontext, SW läuft)
# DevTools -> Application -> Manifest / Service Workers / Cache Storage
# Offline-Test: DevTools -> Network -> "Offline" -> neu laden
```

Service Worker brauchen HTTPS oder `localhost` – über `file://` lässt sich die
PWA nicht testen.

### Automatisiert im Browser prüfen (optional, Playwright)

Update-Flow, Offline-Pfad und Installierbarkeit lassen sich statisch nicht
prüfen – dafür braucht es einen echten Browser. Playwright ist **bewusst keine
Projekt-Abhängigkeit** (die Suite im Repo läuft nur mit der Standardbibliothek);
so ein Skript gehört außerhalb des Repos hingeschrieben, wenn man am Service
Worker etwas Größeres ändert. Drei Fallen, die dabei Zeit gekostet haben:

- **`context.setOffline(true)` taugt nicht für Service-Worker-Tests.** Die
  Navigation scheitert dann mit `ERR_INTERNET_DISCONNECTED`, bevor der Worker
  überhaupt gefragt wird – der Cache-Fallback sieht damit immer kaputt aus.
  Verlässlich ist, den lokalen Testserver zu beenden: Der `fetch` im Worker
  scheitert, der Cache-Zweig greift – genau wie im Funkloch.
- **Nicht auf `registration.active` warten.** Diese Bedingung ist erfüllt,
  bevor Precache und Aktivierung durch sind (Ergebnis: scheinbar leere Caches,
  scheinbar unkontrollierte Seite – beides nur Timing). Stabil ist das Warten
  auf `navigator.serviceWorker.controller` plus Polling des Cache-Inhalts.
- **Ersatzdateien müssen auch in die Precache-Liste.** Wird Leaflet für den Test
  durch einen lokalen Stub ersetzt (das CDN ist z. B. in einer Sandbox nicht
  erreichbar), muss dieser Stub in `SHELL_FILES` der Testkopie stehen – sonst
  fehlt er offline und der Test misst den falschen Fehler.

Objektive Installierbarkeitsprüfung ohne DevTools-Augenmaß: per CDP
`Page.getAppManifest` (Feld `errors` muss leer sein) und
`Page.getInstallabilityErrors`. `in-incognito` ist dabei erwartbares Rauschen,
weil Playwright-Kontexte inkognito-artig sind.

## Dateistruktur

```
lieferkarte-karlsruhe/
├── README.md                    # Öffentliche Doku (was ist das?)
├── docs/TECHNICAL.md            # Das hier – technische Doku
├── docs/PRD.md                  # Produktziel & Nicht-Ziele
├── docs/anforderungen/          # was als Nächstes gebaut wird (Status lebt dort)
├── docs/entscheidungen/         # ADRs, append-only
├── DATENSCHUTZ.md               # Datenschutz & Hinweise (kein Impressum – privat)
├── index.html                   # Root-Weiterleitung -> web/index.html (für Pages)
├── .nojekyll                    # Pages statisch ausliefern, ohne Jekyll
├── .gitignore                   # was nicht ins Repo kommt
├── scanner.py                   # Overpass-Scanner (OSM) + Change Detection
├── export.py                    # DB → JSON
├── data/
│   └── restaurants.db           # SQLite, mit Tabellen: restaurants, changes, scan_runs
├── tools/
│   └── make_icons.py            # erzeugt web/icons/*.png (nur bei Design-Änderung)
├── web/
│   ├── index.html               # Leaflet-Karte
│   ├── datenschutz.html         # Datenschutz & Hinweise (HTML-Fassung)
│   ├── manifest.webmanifest     # PWA-Manifest (installierbar)
│   ├── sw.js                    # Service Worker (Offline-Cache + Updates)
│   ├── icons/                   # App-Icons (192/512, maskable, Apple-Touch, Favicon)
│   └── restaurants.json         # aktuelles Datenpack (wird von export.py generiert)
└── .github/
    └── workflows/
        └── weekly-scan.yml      # GitHub Actions – wöchentlicher Scan
```

## Felder in der DB erweitern

Overpass liefert alle Tags eines Objekts kostenlos mit – zusätzliche Felder
kosten nichts extra. Nützliche OSM-Tags:

Bereits übernommen: `delivery`, `takeaway`, `opening_hours`, `cuisine`
(siehe „Overpass-Abfrage" oben). Weitere Kandidaten:

- `phone` / `contact:phone`: Telefon
- `wheelchair`: Rollstuhl-Zugänglichkeit (`yes`/`limited`/`no`)
- `outdoor_seating`: Außenbereich (`yes`/`no`)

Um sie zu übernehmen, in `scanner.py` einfach in `normalize_osm()` aus `tags`
lesen (der Query holt bereits alle Tags über `out ... tags`):

```python
"phone": tags.get("phone") or tags.get("contact:phone"),
"wheelchair": tags.get("wheelchair"),
```

Dann die DB-Schema-Spalten hinzufügen (`ALTER TABLE restaurants ADD COLUMN ...`) und `sync_places()` entsprechend anpassen.

## Häufige Probleme

### "Overpass-Abfrage fehlgeschlagen" / 429
Overpass drosselt bei zu häufigen Anfragen. `scanner.py` versucht bei
`429`/`502`/`503`/`504` automatisch erneut (Backoff). Bei anhaltenden Problemen
später erneut laufen lassen oder per `OVERPASS_ENDPOINT` einen Spiegelserver
setzen. Wichtig: Bei endgültigem Fehlschlag **bricht der Scan ab** und lässt die
DB unangetastet – eine leere Antwort wird nie als „alles entfernt" verarbeitet.

### "Restaurant XYZ war hier, jetzt nicht mehr – warum?"
Im Voll-Scan-Modus werden Restaurants mit `last_seen < scan_timestamp` als
"REMOVED" markiert. Im `--light`-Modus werden keine Removals erkannt – das ist
absichtlich, damit eine unvollständige Overpass-Antwort keine Einträge löscht.

### Ist die `restaurants.db` nicht aktuell in GitHub?
GitHub cacht den Workflow-Output. Nach einem Scan:
1. `git log` prüfen – steht dort der neueste Commit?
2. Falls nicht: Workflow manuell triggern (Repo → Actions → "Weekly Restaurant Scan" → "Run workflow")

## Lizenz & Datenherkunft (OpenStreetMap)

Wichtig für Rechtssicherheit:

- **Datenquelle:** OpenStreetMap, lizenziert unter der **ODbL** (Open Database
  License). Weiterverteilung – auch öffentlich und kommerziell – ist erlaubt.
- **Attribution ist Pflicht:** „© OpenStreetMap-Mitwirkende" muss sichtbar sein
  (steht im Frontend-Footer und im `attribution`-Feld der JSON).
- **Share-alike:** Wird die Datenbank verändert und als Datenbank weitergegeben,
  gilt sie ihrerseits als ODbL. Für dieses Projekt unkritisch.
- **Keine 30-Tage-Löschpflicht** wie bei Google – OSM-Daten dürfen dauerhaft
  gespeichert und in der Git-History gehalten werden. Genau deshalb ist der
  öffentliche-Repo-Ansatz hier sauber.

## Lizenz

MIT – du darfst den Code nutzen, ändern, weitergeben. Siehe `LICENSE`.

## Support / Fragen

GitHub Issues oder Discussions im Repo öffnen.
