# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Current state: implemented, running on real OSM data, pre-launch

**The full pipeline exists and works.** These files are all present and functional:

- `scanner.py`, `export.py` — the Python pipeline
- `tests/` — stdlib-`unittest` suite for the pipeline invariants (no dependencies)
- `web/index.html`, `web/restaurants.json` — the frontend and its data
- `data/restaurants.db` — the SQLite store (three tables; ~880 active restaurants from real Overpass scans)
- `.github/workflows/weekly-scan.yml`, MIT `LICENSE`

What has **not** happened yet is the public launch. The repo is still **private**. The remaining work is launch prep (no code changes required) — tracked in `VOR-VEROEFFENTLICHUNG.md`: flip the repo public and enable GitHub Pages. Author email is already a GitHub `noreply` address, real OSM data is committed, and (as a private, non-commercial project) there is no Impressum — `DATENSCHUTZ.md` is a personal-data-free privacy/notes page instead. (No API key or billing setup — the data source is free.)

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
- **export.py** — reads the DB, writes `web/restaurants.json` (`{count, generatedAt, ...}`); the workflow's summary step reads those fields via `jq`. It also builds the `feed` block for the „Diese Woche neu"-Panel (`build_feed()`): the `changes` of the last 7 days, **minus the initial import** (the first scan logs every restaurant as `NEW`), capped per change type. Rules documented in `TECHNICAL.md`.
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

**Checking the frontend in a sandboxed session (no CDN):** `web/index.html` loads Leaflet from unpkg.com, which is blocked in the Claude-Code web sandbox (`ERR_TUNNEL_CONNECTION_FAILED`, curl gets a 403 from the proxy). Leaflet then never defines `L`, and the *whole* page script dies on the first `L.map(...)` — so nothing renders and no feature can be inspected. To verify page logic anyway, inject a minimal `L` stub via Playwright's `add_init_script` (methods used: `map/tileLayer/layerGroup/marker/circleMarker/popup`, all chainable). Playwright needs `pip install playwright` and must launch with `executable_path="/opt/pw-browsers/chromium"` (the preinstalled browser build doesn't match the pip version's expected path). The tiles themselves can't be checked this way — only markup, CSS and JS behaviour.

**There is no mock mode.** `scanner.py --mock` and its demo rows were removed once real data replaced them (mock counted as a full scan and would have marked every real restaurant as REMOVED). The scanner only knows full and `--light`; the tests seed their fixtures directly via `sync_places` into temp DBs (`tests/helpers.py`).

## Constraints that drive the design

- **Free and republishable is the whole point.** The move off Google Places was to make a *public* repo licit (see top). Don't reintroduce a data source that forbids public redistribution or requires paid per-call SKUs. Overpass is free; be a good citizen (single request per scan, descriptive `User-Agent`, backoff on 429/5xx).
- **Never let an empty/failed scan wipe the DB.** A full scan marks not-seen restaurants as REMOVED. `scanner.py` therefore aborts (leaves the DB untouched) if Overpass fails or returns zero usable places — preserve this guard in any refactor.
- **`--light` mode intentionally does not mark REMOVED.** An incomplete Overpass response must not delete entries; removals are only trusted from the full scan. Preserve this asymmetry.
- **`delivery` (Lieferung) and `takeaway` (Abholung) come from the OSM tags of the same name** (`yes`/`only` → true, `no` → false, untagged → unknown/`NULL`), parsed via `_osm_yesno`. Both are separate, independent tags. Coverage is patchy (most restaurants are untagged) — the frontend must handle `delivery === null` / `takeaway === null` gracefully. The default filter only acts on `delivery`; `takeaway` currently shows as a popup badge only.
- **The `changes` table has two traps — anything that reads it must handle both.** (1) The **initial import**: the first scan logged all 883 restaurants as `NEW` on a single timestamp. That's the starting inventory, not news — `build_feed()` drops everything at the first `scan_runs` timestamp. (2) **Mass events when a column is introduced**: the scan that first read the existing `takeaway` tags logged 245 × `TAKEAWAY_CHANGED` ("unbekannt → ja") at once. The feed therefore caps items per change type (`FEED_MAX_PER_TYPE`) and reports the true number in `counts`. Adding a new change type (e.g. `CUISINE_CHANGED` for the cuisine filter) will produce the same burst, and the type must be added in **two** places: `FEED_TYPE_ORDER` (`export.py`) and `FEED_GROUPS` (`web/index.html`) — otherwise the panel shows the raw type string as its group heading.
- **Attribution is mandatory (ODbL).** "© OpenStreetMap-Mitwirkende" must stay visible in the frontend footer, the JSON `attribution` field, and DATENSCHUTZ.md. Don't remove it.
- **No cookies, no tracking, no analytics, no server-side data collection** is a hard product promise (README + DATENSCHUTZ.md). Geolocation stays browser-only. Don't add anything that breaks this.
