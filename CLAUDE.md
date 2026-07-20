# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Current state: implemented, running on mock data, pre-launch

**The full pipeline exists and works.** These files are all present and functional:

- `scanner.py`, `export.py` — the Python pipeline
- `web/index.html`, `web/restaurants.json` — the frontend and its data
- `data/restaurants.db` — the SQLite store (three tables + 10 mock rows, `mock_001`–`mock_010`)
- `.github/workflows/weekly-scan.yml`, MIT `LICENSE`

What has **not** happened yet is the public launch. The repo is still **private**, running on mock data. The remaining work is launch prep (no code changes required) — tracked in `VOR-VEROEFFENTLICHUNG.md`: switch author email to a GitHub `noreply` address, fill in a real `IMPRESSUM.md`, run a real scan to replace the mock data, then flip the repo public and enable GitHub Pages. (No API key or billing setup — the data source is free.)

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
- **SQLite schema** — three tables: `restaurants` (current state, `place_id` = stable key), `changes` (append-only log: `NEW` / `REMOVED` / `ADDRESS_CHANGED` / `DELIVERY_CHANGED` / `STATUS_CHANGED`), `scan_runs` (per-scan timestamp + request count).
- **export.py** — reads the DB, writes `web/restaurants.json` (`{count, generatedAt, ...}`); the workflow's summary step reads those fields via `jq`.
- **web/** — static Leaflet + OpenStreetMap map. Both the map tiles and the restaurant data come from OpenStreetMap (ODbL), so a single "© OpenStreetMap-Mitwirkende" attribution covers everything.
- **Deployment** — GitHub Pages serves from `main` at repo root, so `web/` assets and the JSON are committed into the repo. The DB is also committed (its history *is* the change log — see `fetch-depth: 0` in the workflow). Under ODbL this is fine; it would have breached Google's terms.

## Commands (once the pipeline exists)

```bash
python3 scanner.py --mock      # fill DB with demo data, no network
python3 scanner.py             # full scan via Overpass: upsert + change + REMOVED detection
python3 scanner.py --light     # refresh without REMOVED detection
python3 export.py              # regenerate web/restaurants.json from the DB
cd web && python3 -m http.server 8000   # preview at http://localhost:8000
```

There is no test suite or linter configured yet.

## Constraints that drive the design

- **Free and republishable is the whole point.** The move off Google Places was to make a *public* repo licit (see top). Don't reintroduce a data source that forbids public redistribution or requires paid per-call SKUs. Overpass is free; be a good citizen (single request per scan, descriptive `User-Agent`, backoff on 429/5xx).
- **Never let an empty/failed scan wipe the DB.** A full scan marks not-seen restaurants as REMOVED. `scanner.py` therefore aborts (leaves the DB untouched) if Overpass fails or returns zero usable places — preserve this guard in any refactor.
- **`--light` mode intentionally does not mark REMOVED.** An incomplete Overpass response must not delete entries; removals are only trusted from the full scan. Preserve this asymmetry.
- **`delivery` comes from the OSM `delivery` tag** (`yes`/`only` → true, `no` → false, untagged → unknown/`NULL`). Coverage is patchy — the frontend must handle `delivery === null` gracefully.
- **Attribution is mandatory (ODbL).** "© OpenStreetMap-Mitwirkende" must stay visible in the frontend footer, the JSON `attribution` field, and IMPRESSUM. Don't remove it.
- **No cookies, no tracking, no analytics, no server-side data collection** is a hard product promise (README + IMPRESSUM). Geolocation stays browser-only. Don't add anything that breaks this.
