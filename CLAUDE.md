# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Current state: live — public repo, real OSM data, weekly scan running

**The full pipeline exists and works.** These files are all present and functional:

- `scanner.py`, `export.py` — the Python pipeline
- `tests/` — stdlib-`unittest` suite for the pipeline invariants (no dependencies)
- `web/index.html`, `web/restaurants.json` — the frontend and its data
- `data/restaurants.db` — the SQLite store (three tables; ~880 active restaurants from real Overpass scans)
- `.github/workflows/weekly-scan.yml`, MIT `LICENSE`

**The launch has happened.** The repo is **public** and GitHub Pages serves the map at <https://ahirrea.github.io/lieferkarte-karlsruhe/web/index.html>; the weekly workflow runs and keeps ~880 real restaurants in `main`. The launch checklist in `VOR-VEROEFFENTLICHUNG.md` is fully ticked off: author email is a GitHub `noreply` address, real OSM data is committed, and (as a private, non-commercial project) there is no Impressum — `DATENSCHUTZ.md` is a personal-data-free privacy/notes page instead. (No API key or billing setup — the data source is free.)

What's still open is **product work, not launch prep**: the roadmap in `README.md` (specs in `IDEEN.md`) and one undecided question in `VOR-VEROEFFENTLICHUNG.md` — the default `delivery` filter only matches ~7 % of restaurants, so the map looks emptier than the data warrants.

**Data source: OpenStreetMap via the Overpass API** (not Google Places). This was a deliberate switch: Google's Maps Platform terms forbid storing paid Places data >30 days, redistributing it, or showing it off a Google map — all of which a public repo with a committed DB/JSON would do. OpenStreetMap is under the **ODbL**, which explicitly permits public (even commercial) redistribution as long as "© OpenStreetMap-Mitwirkende" attribution is shown. That makes the public-repo model licit and free.

`TECHNICAL.md` is the implementation spec — the DB schema, the Overpass query, change-detection rules. Read it (and verify against the actual files) before changing pipeline code.

## Language

The project and all docs are in **German** (it's a public service for Karlsruhe). Keep user-facing strings, commit messages, and new docs in German to match; code identifiers follow the existing docs (e.g. `sync_places`, `normalize_osm`, `fetch_overpass`).

## Architecture (as specified in TECHNICAL.md)

A weekly batch pipeline, no backend server. Data flows one direction:

```
scanner.py  ──> data/restaurants.db ──> export.py ──> web/restaurants.json ──> web/index.html
(Overpass API)   (SQLite)                (DB→JSON)                              (Leaflet map)
```

- **scanner.py** — queries the Overpass API (OpenStreetMap) in a single request, upserts into SQLite keyed on `place_id` (an OSM `type/id`, e.g. `node/12345`), and detects changes vs. the previous scan.
- **SQLite schema** — three tables: `restaurants` (current state, `place_id` = stable key), `changes` (append-only log: `NEW` / `REMOVED` / `ADDRESS_CHANGED` / `DELIVERY_CHANGED` / `TAKEAWAY_CHANGED` / `STATUS_CHANGED`), `scan_runs` (per-scan timestamp + request count).
- **export.py** — reads the DB, writes `web/restaurants.json` (`{count, generatedAt, ...}`); the workflow's summary step reads those fields via `jq`.
- **web/** — static Leaflet + OpenStreetMap map. Both the map tiles and the restaurant data come from OpenStreetMap (ODbL), so a single "© OpenStreetMap-Mitwirkende" attribution covers everything.
- **Deployment** — GitHub Pages serves from `main` at repo root, so `web/` assets and the JSON are committed into the repo. The DB is also committed (its history *is* the change log — see `fetch-depth: 0` in the workflow). Under ODbL this is fine; it would have breached Google's terms.

## Commands

```bash
python3 -m unittest discover -s tests -v   # run the test suite (stdlib only, no install)
python3 scanner.py             # full scan via Overpass: upsert + change + REMOVED detection
python3 scanner.py --light     # refresh without REMOVED detection
python3 export.py              # regenerate web/restaurants.json from the DB
cd web && python3 -m http.server 8000   # preview at http://localhost:8000
```

**Run the tests before pushing any pipeline change.** They use in-memory/temp databases and never touch `data/restaurants.db`; there is no linter configured.

**`export.py` does not migrate the DB.** After adding a column, `init_db()` has to run against the committed `data/restaurants.db` once (`python3 -c "import sqlite3, scanner; c = sqlite3.connect('data/restaurants.db'); scanner.init_db(c); c.close()"`), otherwise a local `python3 export.py` fails on the missing column. In CI this can't happen — the workflow runs `scanner.py` (which migrates) first.

**There is no mock mode.** `scanner.py --mock` and its demo rows were removed once real data replaced them (mock counted as a full scan and would have marked every real restaurant as REMOVED). The scanner only knows full and `--light`; the tests seed their fixtures directly via `sync_places` into temp DBs (`tests/helpers.py`).

## Working in a sandboxed session (Claude Code on the web)

The network policy of a web session blocks both external hosts this project uses, so plan verification accordingly:

- **Overpass is unreachable** (the proxy answers 403 to the CONNECT). No real scan is possible — `python3 scanner.py` will abort by design (and that's the correct behaviour: it leaves the DB untouched). Verify pipeline changes with the unittest suite instead; new columns stay `NULL` until the next Sunday workflow run fills them. Say so plainly rather than implying the data was refreshed.
- **The Leaflet CDN (unpkg) is unreachable**, so `web/index.html` cannot render a real map here — the page hangs at "Lade Restaurants …" because `L` is undefined. To test frontend logic, copy the page into a scratch dir, replace the two unpkg tags with a tiny `L` stub (`map`/`tileLayer`/`layerGroup`/`marker`/`circleMarker`) that collects the markers in `window.__markers`, serve the dir with `python3 -m http.server` and drive it with Playwright. Filter counts (`#count`), option lists and popup HTML are all assertable that way; test both with synthetic data **and** with the real `restaurants.json` (untagged fields must degrade gracefully).
- **Chromium is preinstalled** under `/opt/pw-browsers` — do not run `playwright install`. A freshly npm-installed `playwright` may expect a newer build than the image ships, so launch with `executablePath` pointing at the existing `chromium-*/chrome-linux/chrome`.

## Constraints that drive the design

- **Free and republishable is the whole point.** The move off Google Places was to make a *public* repo licit (see top). Don't reintroduce a data source that forbids public redistribution or requires paid per-call SKUs. Overpass is free; be a good citizen (single request per scan, descriptive `User-Agent`, backoff on 429/5xx).
- **Never let an empty/failed scan wipe the DB.** A full scan marks not-seen restaurants as REMOVED. `scanner.py` therefore aborts (leaves the DB untouched) if Overpass fails or returns zero usable places — preserve this guard in any refactor.
- **`--light` mode intentionally does not mark REMOVED.** An incomplete Overpass response must not delete entries; removals are only trusted from the full scan. Preserve this asymmetry.
- **`delivery` (Lieferung) and `takeaway` (Abholung) come from the OSM tags of the same name** (`yes`/`only` → true, `no` → false, untagged → unknown/`NULL`), parsed via `_osm_yesno`. Both are separate, independent tags. Coverage is patchy (most restaurants are untagged) — the frontend must handle `delivery === null` / `takeaway === null` gracefully. The default filter only acts on `delivery`; `takeaway` currently shows as a popup badge only.
- **`cuisine` (Küchenstil) is normalized in the scanner** (`_osm_cuisine`): the OSM tag allows multiple values in arbitrary spelling (`pizza;italian`, `Ice Cream`, `coffee-shop`) → the DB column holds a canonical `;`-separated list of lowercase keys (`NULL` = untagged); junk values (`yes`/`no`/`unknown`/`fixme`/`other`) and duplicates are dropped. `export.py` emits it as the list `cuisines` (empty list = unknown); the German labels live in the frontend (`CUISINE_LABELS`), the DB stays raw. The frontend's filter dropdown is built from the values actually present and stays hidden while none are tagged. Cuisine changes are deliberately **not** logged in `changes`.
- **Attribution is mandatory (ODbL).** "© OpenStreetMap-Mitwirkende" must stay visible in the frontend footer, the JSON `attribution` field, and DATENSCHUTZ.md. Don't remove it.
- **No cookies, no tracking, no analytics, no server-side data collection** is a hard product promise (README + DATENSCHUTZ.md). Geolocation stays browser-only. Don't add anything that breaks this.
