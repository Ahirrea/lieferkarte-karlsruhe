#!/usr/bin/env python3
"""Lieferkarte Karlsruhe – Export.

Liest ``data/restaurants.db`` und schreibt ``web/restaurants.json`` – das
Datenpaket, das die Leaflet-Karte lädt. Der GitHub-Actions-Workflow liest
``count`` und ``generatedAt`` daraus per ``jq`` für die Job-Summary.

Nur Standardbibliothek – keine externen Pakete nötig.
"""

import json
import os
import sqlite3
import sys
from datetime import datetime, timezone

DB_PATH = os.path.join(os.path.dirname(__file__), "data", "restaurants.db")
OUT_PATH = os.path.join(os.path.dirname(__file__), "web", "restaurants.json")

# Anzahl der jüngsten Änderungen im "Diese Woche neu"-Feed
RECENT_CHANGES_LIMIT = 50


def export():
    if not os.path.exists(DB_PATH):
        print(f"DB nicht gefunden: {DB_PATH}", file=sys.stderr)
        print("  Erst scanner.py laufen lassen (z. B. python3 scanner.py --mock).",
              file=sys.stderr)
        return 1

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        restaurants = []
        for r in conn.execute(
            "SELECT place_id, name, address, lat, lng, website, delivery,"
            " business_status, first_seen, last_seen"
            " FROM restaurants WHERE active = 1 ORDER BY name COLLATE NOCASE"
        ):
            restaurants.append({
                "placeId": r["place_id"],
                "name": r["name"],
                "address": r["address"],
                "lat": r["lat"],
                "lng": r["lng"],
                "website": r["website"],
                "delivery": None if r["delivery"] is None else bool(r["delivery"]),
                "businessStatus": r["business_status"],
                "firstSeen": r["first_seen"],
                "lastSeen": r["last_seen"],
            })

        changes = []
        for c in conn.execute(
            "SELECT place_id, change_type, old_value, new_value, detected_at"
            " FROM changes ORDER BY id DESC LIMIT ?",
            (RECENT_CHANGES_LIMIT,),
        ):
            changes.append({
                "placeId": c["place_id"],
                "type": c["change_type"],
                "oldValue": c["old_value"],
                "newValue": c["new_value"],
                "detectedAt": c["detected_at"],
            })

        last_run = conn.execute(
            "SELECT started_at, mode FROM scan_runs ORDER BY id DESC LIMIT 1"
        ).fetchone()

        payload = {
            "count": len(restaurants),
            "generatedAt": datetime.now(timezone.utc).isoformat(),
            "lastScanAt": last_run["started_at"] if last_run else None,
            "lastScanMode": last_run["mode"] if last_run else None,
            "attribution": "Daten: Google Maps Platform · Karte: © OpenStreetMap-Mitwirkende",
            "restaurants": restaurants,
            "recentChanges": changes,
        }

        os.makedirs(os.path.dirname(OUT_PATH), exist_ok=True)
        with open(OUT_PATH, "w", encoding="utf-8") as fh:
            json.dump(payload, fh, ensure_ascii=False, indent=2)
            fh.write("\n")

        print(f"Geschrieben: {OUT_PATH} ({len(restaurants)} Restaurants, "
              f"{len(changes)} Änderungen).")
        return 0
    finally:
        conn.close()


if __name__ == "__main__":
    sys.exit(export())
