# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Current state: documentation-only, pre-implementation

**The code described throughout the docs does not exist yet.** The repo currently contains only Markdown docs, `.gitignore`, and a workflow file. Do not assume the following exist until you have created them or verified they are present:

- `scanner.py`, `export.py` — the Python pipeline
- `web/index.html`, `web/restaurants.json` — the frontend and its data
- `data/restaurants.db` — the SQLite store

The GitHub Actions workflow (`.github/workflows/weekly-scan.yml`) and the MIT `LICENSE` referenced by the docs do exist.

`TECHNICAL.md` is the implementation spec — read it before writing pipeline code, since it defines the DB schema, field masks, change-detection rules, and cost model that the code must honor. When you implement a file, verify it matches the file structure and behavior documented there.

## Language

The project and all docs are in **German** (it's a public service for Karlsruhe). Keep user-facing strings, commit messages, and new docs in German to match; code identifiers follow the existing docs (e.g. `sync_places`, `FULL_FIELD_MASK`).

## Architecture (as specified in TECHNICAL.md)

A weekly batch pipeline, no backend server. Data flows one direction:

```
scanner.py ──> data/restaurants.db ──> export.py ──> web/restaurants.json ──> web/index.html
(Places API)   (SQLite)                (DB→JSON)                              (Leaflet map)
```

- **scanner.py** — queries Google Places API (New), upserts into SQLite keyed on `place_id`, and detects changes vs. the previous scan.
- **SQLite schema** — three tables: `restaurants` (current state, `place_id` = stable key), `changes` (append-only log: `NEW` / `REMOVED` / `ADDRESS_CHANGED` / `DELIVERY_CHANGED` / `STATUS_CHANGED`), `scan_runs` (per-scan timestamp + API-call count for cost tracking).
- **export.py** — reads the DB, writes `web/restaurants.json` (`{count, generatedAt, ...}`); the workflow's summary step reads those fields via `jq`.
- **web/** — static Leaflet + OpenStreetMap map. No Google Maps JS (avoids that SKU); Google data only via the Places API in `scanner.py`.
- **Deployment** — GitHub Pages serves from `main` at repo root, so `web/` assets and the JSON are committed into the repo. The DB is also committed (its history *is* the change log — see `fetch-depth: 0` in the workflow).

## Commands (once the pipeline exists)

```bash
python3 scanner.py --mock      # fill DB with demo data, no API key / no cost
python3 scanner.py             # full scan: delivery flag + all detail fields (expensive SKU)
python3 scanner.py --light     # cheap existence/address check, no delivery field, no REMOVED detection
python3 export.py              # regenerate web/restaurants.json from the DB
cd web && python3 -m http.server 8000   # preview at http://localhost:8000
```

There is no test suite or linter configured yet.

## Constraints that drive the design

- **API cost is the central constraint.** The delivery flag lives in the expensive Places "Enterprise + Atmosphere" SKU (~$40/1000). Budget target is ~10–15 €/month. This is why there are two scan modes (full weekly vs. `--light`), why change detection avoids re-fetching, and why `scan_runs` tracks call counts. Weigh API-call count in any pipeline change.
- **Google's 30-day storage rule.** Only `place_id` may be cached indefinitely; other fields (name, address, delivery status) must be refreshed within 30 days. The weekly full scan is what keeps the repo compliant — don't design flows that let cached fields go stale beyond that.
- **`--light` mode intentionally does not mark REMOVED.** Google has caching delays; removals are only trusted from the full scan. Preserve this asymmetry.
- **`PLACES_API_KEY`** is required for real scans, read from the environment (and from GitHub Actions secrets in CI). It must never be committed — `.gitignore` already blocks the common leak paths.
- **No cookies, no tracking, no analytics, no server-side data collection** is a hard product promise (README + IMPRESSUM). Geolocation stays browser-only. Don't add anything that breaks this.
