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
- **changes**: Änderungsprotokoll (NEW / REMOVED / ADDRESS_CHANGED / DELIVERY_CHANGED / STATUS_CHANGED)
- **scan_runs**: wann lief welcher Scan mit wie vielen API-Aufrufen (Kostenkontrolle)

## Schnellstart (ohne API-Key, mit Demodaten)

```bash
python3 scanner.py --mock     # füllt die DB mit Beispiel-Restaurants
python3 export.py             # erzeugt web/restaurants.json
cd web && python3 -m http.server 8000
# -> http://localhost:8000 im Browser öffnen
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

# Demo ohne Netz
python3 scanner.py --mock
```

Dann:
```bash
python3 export.py           # erzeugt web/restaurants.json
cd web && python3 -m http.server 8000
```

### Overpass-Abfrage

`scanner.py` fragt alle `amenity=restaurant`/`fast_food` im 12-km-Umkreis um
das Karlsruher Zentrum ab (`nwr(around:...)`, `out center tags`). Aus den Tags
werden Name, Adresse (`addr:*`), Koordinaten, `website`/`contact:website` und
`delivery` (`yes`/`only` → 1, `no` → 0, sonst unbekannt) übernommen.

Der Endpoint ist per Umgebungsvariable überschreibbar, falls ein Spiegelserver
nötig wird:

```bash
export OVERPASS_ENDPOINT="https://overpass.kumi.systems/api/interpreter"
```

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

## Dateistruktur

```
lieferkarte-karlsruhe/
├── README.md                    # Öffentliche Doku (was ist das?)
├── TECHNICAL.md                 # Das hier – technische Doku
├── IMPRESSUM.md                 # Impressum & Datenschutz
├── .gitignore                   # was nicht ins Repo kommt
├── scanner.py                   # Overpass-Scanner (OSM) + Change Detection
├── export.py                    # DB → JSON
├── data/
│   └── restaurants.db           # SQLite, mit Tabellen: restaurants, changes, scan_runs
├── web/
│   ├── index.html               # Leaflet-Karte
│   └── restaurants.json         # aktuelles Datenpack (wird von export.py generiert)
└── .github/
    └── workflows/
        └── weekly-scan.yml      # GitHub Actions – wöchentlicher Scan
```

## Felder in der DB erweitern

Overpass liefert alle Tags eines Objekts kostenlos mit – zusätzliche Felder
kosten nichts extra. Nützliche OSM-Tags:

- `cuisine`: Küchenstil (`pizza`, `thai`, `burger`, …)
- `opening_hours`: Öffnungszeiten
- `phone` / `contact:phone`: Telefon
- `wheelchair`: Rollstuhl-Zugänglichkeit (`yes`/`limited`/`no`)
- `takeaway`: Abholung (ergänzend zu `delivery`)

Um sie zu übernehmen, in `scanner.py` einfach in `normalize_osm()` aus `tags`
lesen (der Query holt bereits alle Tags über `out ... tags`):

```python
"cuisine": tags.get("cuisine"),
"opening_hours": tags.get("opening_hours"),
"phone": tags.get("phone") or tags.get("contact:phone"),
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
