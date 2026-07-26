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

## Filter und URL-Parameter (Frontend)

Die Filter im Kopf sind Chips (`aria-pressed`), UND-verknüpft. Vorbelegt ist
**„Liefert jetzt"** = `delivery` + `open`
([ADR-007](./entscheidungen/ADR-007-standardfilter-liefert-jetzt.md)):

| Chip / Feld | Element | Trifft | Standard |
|---|---|---|---|
| 🚴 Lieferung | `#fDelivery` | `delivery === true` | **an** |
| 🥡 Abholung | `#fTakeaway` | `takeaway === true` | aus |
| 🕒 Jetzt geöffnet | `#fOpen` | `openStateNow(openingHours) === true` | **an** |
| 🍽️ Küche | `#cuisine` | Schlüssel in `cuisines` | leer |
| Suche | `#search` | Name, Adresse, Küchenstil (Schlüssel + Label) | leer |

`null` ist bei allen Filtern **kein Treffer** — aber im Popup ausdrücklich
„unbekannt" (`badge-unknown`) und nie „nein".

Der Zustand steht in der URL (`readUrlState()` / `writeUrlState()`, geschrieben
per `history.replaceState`). Geschrieben wird nur, was vom Standard **abweicht**;
`nearby` und unbekannte Parameter bleiben erhalten. Reine Query-Parameter, nichts
wird gespeichert — das „keine Cookies"-Versprechen bleibt unberührt.

| Parameter | Werte | Bedeutung |
|---|---|---|
| `delivery`, `takeaway`, `open` | `1` / `0` | Chip an/aus; fehlt = Standard |
| `cuisine` | Küchenschlüssel | wird erst nach `buildCuisineOptions()` gesetzt |
| `q` | Freitext | Suchfeld |
| `nearby` | `1` | fragt beim Laden den Standort ab (nicht gefiltert) |

Beispiele: `?delivery=0&open=0` = alle Restaurants ·
`?delivery=0&takeaway=1` = was jetzt zur Abholung offen hat. Beide sind auch
App-Verknüpfungen im Manifest.

Bei null Treffern zeigt `#empty` einen Leerzustand mit „Alle Restaurants zeigen".
Das ist beim Standardfilter der Regelfall (nachts liefert niemand) und darf nicht
entfernt werden.

## Farbrollen (Frontend)

Farbe hat **drei getrennte Rollen** mit je eigenem Token-Satz in `:root`
([ADR-009](./entscheidungen/ADR-009-farbrollen-marke-aktion-zustand.md), A-4).
Keine Rolle borgt sich die Farbe einer anderen; `--accent` und `--ok` existieren
nicht mehr.

| Rolle | Tokens | Gilt für |
|---|---|---|
| **Marke** | `--marke` `#d64541` | Markenwort im `h1`, PWA-Icons, `manifest.theme_color`, `theme-color`-Metas. **Nie für einen Zustand.** |
| **Interaktion** | `--aktion` `#b8352f`, `--aktion-hover`, `--aktion-schwach` | Links, Knöpfe, aktive Chips, `.pill`, Melde-Flag |
| **Datenzustand** | `--zustand-ja` / `-ja-bg`, `--zustand-nein` / `-nein-bg`, `--zustand-unbekannt` | Badges, „geschlossen" in der Zeitentabelle, die Karten-Pins ([A-5](./anforderungen/A-5-pins-nach-zustand.md)) |

Dazu neutrale Tokens (`--bg`, `--panel`, `--text`, `--muted`, `--border`,
`--flaeche-hover`, `--auf-farbe`, `--schatten-weich`, `--schatten-stark`) und
zwei eigenständige Amber-Rollen: `--status*` (Betriebsstatus) und `--hinweis*`
(Hinweisleiste).

**Vier bindende Regeln:**

1. **Kein Farbwert außerhalb von `:root`.** Jede CSS-Regel benutzt `var()`.
   Ausnahmen nur, wo kein `var()` möglich ist: die drei `theme-color`-Metas und
   `manifest.webmanifest`. In JavaScript liest `cssVar(name, fallback)` das
   Token (`getComputedStyle` liefert ohne aufgelöste Custom-Properties einen
   Leerstring — daher der Fallback).
2. **Farbe trägt den Zustand, das Symbol trägt die Fähigkeit.** „🥡 Abholung" ist
   ein *Ja* und deshalb grün wie „✔ Lieferservice"; unterschieden werden sie
   durch Symbol und Text. Zwei grüne Badges nebeneinander sind normal, kein
   Fehler. Blau als „Abholung"-Farbe ist verbraucht.
3. **Ein Zustand wird nie allein über Farbe codiert.** Der Helligkeitsabstand
   „ja" gegen „nein" liegt bei 1,92 — besser als die 1,03 von vorher, aber keine
   tragfähige Einzelcodierung. Symbol, Form oder Text muss mit.
4. **„unbekannt" trennt sich von „nein" über die Form.** `.badge-no` ist gefüllt,
   `.badge-unknown` ein gestrichelter Umriss ohne Füllung (Padding um die
   Rahmenbreite reduziert, damit die Badges gleich groß bleiben). „unbekannt" ist
   mit 87,5 % bei Lieferung der **häufigste** Zustand und darf nach
   [ADR-007](./entscheidungen/ADR-007-standardfilter-liefert-jetzt.md) nie wie
   eine Absage aussehen.

Die Badge-Klassen laufen auf der Zustandsachse, nicht auf der Fähigkeitsachse:
`.badge-yes`, `.badge-no`, `.badge-unknown`, dazu `.badge-status` als eigene
Rolle. Alle Text/Flächen-Paare erreichen 4,5:1 (kleiner Text); `header h1` ist
1,2 rem, weil die Markenfarbe auf Weiß nur 4,39:1 schafft und erst als „großer
Text" (≥ 18,66 px fett) die dann geltende 3:1-Schwelle erfüllt.

**Die Markenfarbe ist an vier Orten gekoppelt** — `--marke` in beiden
`:root`-Blöcken, `manifest.theme_color`, die drei `theme-color`-Metas und
`ACCENT` in `tools/make_icons.py`. Sie zu ändern heißt: alle vier anfassen und
die Icons neu erzeugen. `tests/test_pwa.py` prüft den Gleichlauf
Manifest ↔ Meta.

Dark Mode ist damit vorbereitet, aber **nicht gebaut** (P3 im
[Backlog](./BACKLOG.md)): er wäre ein `@media (prefers-color-scheme: dark)`-Block,
der ausschließlich `:root` überschreibt.

### Pin-Grammatik auf der Karte

Die Marker sind seit A-5 **SVG-Kreise** (`L.circleMarker`), kein Bild-Icon mehr,
und tragen genau **zwei Achsen**
([ADR-010](./entscheidungen/ADR-010-pin-grammatik-lieferung-und-geschlossen.md)):

| Lieferung | offen **oder** unbekannt | sicher geschlossen |
|---|---|---|
| **ja** | `--zustand-ja`, r 10, Füllung 0,85 | r 7, Füllung 0,2 |
| **nein** | `--zustand-nein`, r 10, Füllung 0,85 | r 7, Füllung 0,2 |
| **unbekannt** | `--zustand-unbekannt`, r 10, Füllung 0,12, **gestrichelt `3 3`** | r 7, Füllung 0, gestrichelt |

Alles steht in **einer** Tabelle (`PIN`) und **einer** Funktion (`pinStyle()`)
in `web/index.html`. Vier Dinge sind daran bindend:

1. **Der Umriss ist immer voll deckend** (2 px, `opacity: 1`). „Blass" allein —
   die naheliegende Umsetzung von „geschlossen" — erreicht gemessen 2,59:1 und
   reißt die 3:1-Grenze für grafische Objekte (WCAG 1.4.11). Voll deckend sind
   es 3,32–12,52:1 über die üblichen Kachelfarben.
2. **Abgewertet wird nur, was sicher geschlossen ist.** `openStateNow() === null`
   (gemessen 210 von 885) sieht aus wie „offen" — ein „unbekannt" darf nie wie
   eine Absage aussehen ([ADR-007](./entscheidungen/ADR-007-standardfilter-liefert-jetzt.md)).
3. **Die Legende entsteht aus derselben Funktion** (`pinStyle()` → `pinSwatch()`
   → `buildLegend()`), sonst laufen Karte und Erklärung auseinander. Sie liegt
   im Filter-Sheet: unter 640 px als Liste, darüber als eigene Zeile mit
   `order: 1` in der Bedienzeile.
4. **Der Pin ist voll.** Eine dritte Achse braucht einen neuen ADR.

`pinTokens()` liest die drei Farben einmal je `render()` (nicht je Marker —
`getComputedStyle` ist teuer) und hält dieselben Fallbacks wie `:root`. Der
Standort-Marker aus `locateMe()` ist deshalb ein großer, dünn gefüllter Ring
statt eines Punkts: Marken-Rot gegen Zustands-Grün hat nur 1,03
Helligkeitsabstand, die Unterscheidung muss über die Form laufen.

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
  scheitert, der Cache-Zweig greift – genau wie im Funkloch. (Es gibt eine
  zweite, noch verwirrendere Ausprägung: läuft der Worker bereits, kann die
  Navigation *gelingen* und sein eigener `fetch` trotzdem echte Netzdaten
  holen – `X-Lieferkarte-Cache` fehlt dann und der Offline-Hinweis bleibt aus,
  obwohl beides korrekt ist. Auch hier hilft nur, den Server abzuschalten.)
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
