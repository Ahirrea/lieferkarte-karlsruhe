# Lieferkarte Karlsruhe – Technische Dokumentation

Findet Restaurants mit Lieferservice über die **Google Places API (New)**,
speichert sie in SQLite, erkennt Änderungen zwischen Scans und zeigt alles
auf einer Karte (Leaflet + OpenStreetMap, keine Google-Maps-JS-Kosten).

## Architektur

```
scanner.py  ──>  data/restaurants.db  ──>  export.py  ──>  web/restaurants.json
 (Places API)      (SQLite:                                      │
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

## Echter Scan (mit Google Places API)

### 1. Google-Cloud-Projekt Setup

1. [Google Cloud Console](https://console.cloud.google.com/) öffnen
2. Neues Projekt anlegen (z. B. "Lieferkarte Karlsruhe")
3. **Places API (New)** aktivieren:
   - "APIs & Services" → "Library"
   - "Places API" suchen, den mit "(New)" wählen
   - "Enable" klicken
4. **API-Key erzeugen:**
   - "APIs & Services" → "Credentials"
   - "+ Create Credentials" → "API Key"
   - Key kopieren
5. **Key einschränken (WICHTIG):**
   - Key anklicken, "API restrictions" setzen
   - Nur "Places API" (New) erlauben – sonst kann jeder damit andere APIs missbrauchen

### 2. Budget-Alarm setzen (Pflicht!)

Places API mit Atmosphere-Feldern kann bei zu vielen Anfragen schnell teuer werden.

1. Cloud Console → "Billing"
2. Projekt dem Billing Account zuordnen
3. "Budgets and alerts" → "+ CREATE BUDGET"
   - Budget: z. B. 20 EUR/Monat
   - Alert threshold: z. B. 80%, 100%, 120%

### 3. Umgebungsvariable setzen

```bash
export PLACES_API_KEY="dein-api-key-hier"
```

Besser (persistent):
```bash
echo 'export PLACES_API_KEY="dein-key"' >> ~/.bashrc
source ~/.bashrc
```

Oder für GitHub Actions: Siehe Abschnitt "GitHub Actions Workflow" unten.

### 4. Scanner laufen lassen

```bash
# Voll-Scan: Lieferservice-Flag + alle Details (teure SKU, ~0.04 $ / 1.000 Anfragen)
python3 scanner.py

# Günstiger Existenz-Check: nur Adresse/Status, kein delivery-Feld
python3 scanner.py --light

# Demo ohne API-Kosten
python3 scanner.py --mock
```

Dann:
```bash
python3 export.py           # erzeugt web/restaurants.json
cd web && python3 -m http.server 8000
```

## Kostenübersicht

### Preise (Stand Mitte 2026, can change)

| SKU | Enthält | $/1.000 |
|---|---|---|
| Text Search Essentials | nur ID | kostenlos |
| Text Search Pro | Name, Adresse, Koordinaten | ~32 $ |
| Text Search Enterprise | + Öffnungszeiten, Telefon, Website | ~35 $ |
| **Text Search Enterprise+Atmosphere** | **+ `delivery`, Dine-in etc.** | **~40 $** |

### Geschätzte monatliche Kosten für Karlsruhe

- **Suchanfragen pro Voll-Scan:** ~16 Suchabfragen × 3 Seiten ≈ 48 Anfragen
- **Wöchentlicher Voll-Scan:** 4 Wochen × 48 ≈ **192 Anfragen/Monat**
- **Kosten:** (192 / 1.000) × 40 $ ≈ **~8 $/Monat**

Mit täglichem `--light`-Check (günstiger): die teuren Anfragen steigen minimal. Kostenbudget: **10–15 $/Monat** ist realistisch.

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
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0  # komplette History, wichtig für die DB

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.12'

      - name: Run scanner
        env:
          PLACES_API_KEY: ${{ secrets.PLACES_API_KEY }}
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

### 2. API-Key als Secret speichern

1. Repo → Settings → "Secrets and variables" → "Actions"
2. "+ New repository secret"
3. Name: `PLACES_API_KEY`
4. Value: dein Google API-Key
5. Speichern

Der Key wird nur beim Workflow-Lauf sichtbar, nie im Repo oder der History.

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
├── scanner.py                   # Places API Scanner + Change Detection
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

Das `delivery`-Flag ist in der Atmosphere-SKU enthalten, du bezahlst also schon dafür. Kostenlos mitnehmbar:

- `types`: Küchenstil (Pizza, Thai, Burger, etc.)
- `opening_hours`: Öffnungszeiten
- `phone_number`: Telefon
- `wheelchair_accessible`: Rollstuhl-zugänglich
- `rating`: Bewertungsscore

Um sie abzufragen, in `scanner.py` die `FULL_FIELD_MASK` anpassen:

```python
FULL_FIELD_MASK = ",".join([
    "places.id",
    "places.displayName",
    "places.formattedAddress",
    "places.location",
    "places.businessStatus",
    "places.websiteUri",
    "places.delivery",
    "places.types",              # <- hinzufügen
    "places.openingHours",       # <- hinzufügen
    "places.internationalPhoneNumber",  # <- hinzufügen
    "nextPageToken",
])
```

Dann die DB-Schema-Spalten hinzufügen (`ALTER TABLE restaurants ADD COLUMN ...`) und `sync_places()` entsprechend anpassen.

## Häufige Probleme

### "PLACES_API_KEY not set"
```bash
export PLACES_API_KEY="dein-key"
python3 scanner.py
```

### "429 Too Many Requests"
Google drosselt bei zu vielen parallelen Anfragen. `scanner.py` wartet zwischen Pagination-Seiten (`time.sleep(1)`). Falls es trotzdem passiert: Abstand erhöhen oder weniger Seiten pro Query (`max_pages` reduzieren).

### "Restaurant XYZ war hier, jetzt nicht mehr – warum?"
Im Voll-Scan-Modus (~1× pro Woche) werden Restaurants mit `last_seen < scan_timestamp` als "REMOVED" markiert. Im `--light`-Modus (täglich) werden keine Removals erkannt – das ist absichtlich, weil Google manchmal Caching-Delays hat.

### Ist die `restaurants.db` nicht aktuell in GitHub?
GitHub cacht den Workflow-Output. Nach einem Scan:
1. `git log` prüfen – steht dort der neueste Commit?
2. Falls nicht: Workflow manual triggern (Repo → Actions → "Weekly Restaurant Scan" → "Run workflow")

## Googles Caching & Datenspeicherung

Wichtig für Rechtssicherheit:

- **`place_id`:** Darf unbegrenzt gespeichert werden
- **Andere Felder (Name, Adresse, Lieferstatus):** Google möchte, dass du sie nicht länger als **30 Tage** speicherst ohne Refresh
  - Dein wöchentlicher Scan erfüllt das, da du jedes Mal ein Refresh machst
- **Bei Karte zeigen:** Attribution "Daten: Google Maps" ergänzen (steht bereits im Frontend als Meta)

## Lizenz

MIT – du darfst den Code nutzen, ändern, weitergeben. Siehe `LICENSE`.

## Support / Fragen

GitHub Issues oder Discussions im Repo öffnen.
