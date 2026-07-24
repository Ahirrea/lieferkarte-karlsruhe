"""Gemeinsame Test-Fixtures.

Seit der Mock-Modus aus scanner.py entfernt ist, befüllen die Tests ihre
Temporär-Datenbanken direkt über ``sync_places`` – ohne Netz und ohne die
echte ``data/restaurants.db`` anzufassen.
"""

import os
import sqlite3
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import scanner

TS1 = "2026-01-01T00:00:00+00:00"
TS2 = "2026-01-02T00:00:00+00:00"
TS3 = "2026-01-03T00:00:00+00:00"


def make_place(pid, **overrides):
    """Vollständiges Place-Dict im Format von normalize_osm."""
    place = {
        "place_id": pid,
        "name": f"Restaurant {pid}",
        "address": "Kaiserstraße 1, 76133 Karlsruhe",
        "lat": 49.0,
        "lng": 8.4,
        "website": None,
        "delivery": None,
        "takeaway": None,
        "opening_hours": None,
        "cuisine": None,
        "business_status": None,
    }
    place.update(overrides)
    return place


def seed_db(db_path, places, ts=TS1):
    """Temp-DB anlegen und per Voll-Scan-Semantik mit ``places`` befüllen."""
    conn = sqlite3.connect(db_path)
    try:
        scanner.init_db(conn)
        scanner.sync_places(conn, places, "full", ts)
        conn.execute(
            "INSERT INTO scan_runs (started_at, mode, api_calls, places_found)"
            " VALUES (?, 'full', 1, ?)",
            (ts, len(places)),
        )
        conn.commit()
    finally:
        conn.close()
