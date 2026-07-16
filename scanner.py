#!/usr/bin/env python3
"""Lieferkarte Karlsruhe – Scanner.

Fragt die Google Places API (New) nach Restaurants mit Lieferservice in
Karlsruhe ab, speichert sie in SQLite (``data/restaurants.db``) und erkennt
Änderungen gegenüber dem vorherigen Scan.

Drei Modi:

    python3 scanner.py --mock     Demodaten, keine API, keine Kosten
    python3 scanner.py            Voll-Scan: delivery-Flag + alle Details (teure SKU)
    python3 scanner.py --light    günstiger Existenz-/Adress-Check, kein delivery,
                                  keine REMOVED-Erkennung

Nur Standardbibliothek – keine externen Pakete nötig (wichtig für CI).
"""

import argparse
import json
import os
import sqlite3
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone

# --------------------------------------------------------------------------
# Konfiguration
# --------------------------------------------------------------------------

DB_PATH = os.path.join(os.path.dirname(__file__), "data", "restaurants.db")

PLACES_ENDPOINT = "https://places.googleapis.com/v1/places:searchText"

# Karlsruhe-Zentrum für den locationBias (Ergebnisse lokal halten)
KARLSRUHE_LAT = 49.0069
KARLSRUHE_LNG = 8.4037
SEARCH_RADIUS_M = 12000.0

# Voll-Scan: enthält das teure delivery-Feld (Enterprise+Atmosphere-SKU)
FULL_FIELD_MASK = ",".join([
    "places.id",
    "places.displayName",
    "places.formattedAddress",
    "places.location",
    "places.businessStatus",
    "places.websiteUri",
    "places.delivery",
    "nextPageToken",
])

# Light-Scan: nur Existenz/Adresse/Status, KEIN delivery -> günstigere SKU
LIGHT_FIELD_MASK = ",".join([
    "places.id",
    "places.displayName",
    "places.formattedAddress",
    "places.location",
    "places.businessStatus",
    "nextPageToken",
])

# Suchabfragen: pro Stadtteil eine Query, ~3 Seiten je Query.
# Kostenmodell (TECHNICAL.md): ~16 Abfragen × 3 Seiten ≈ 48 Anfragen/Voll-Scan.
SEARCH_QUERIES = [
    "Restaurant mit Lieferservice Karlsruhe Innenstadt",
    "Restaurant mit Lieferservice Karlsruhe Südstadt",
    "Restaurant mit Lieferservice Karlsruhe Weststadt",
    "Restaurant mit Lieferservice Karlsruhe Oststadt",
    "Restaurant mit Lieferservice Karlsruhe Nordstadt",
    "Restaurant mit Lieferservice Karlsruhe Mühlburg",
    "Restaurant mit Lieferservice Karlsruhe Durlach",
    "Restaurant mit Lieferservice Karlsruhe Neureut",
    "Restaurant mit Lieferservice Karlsruhe Waldstadt",
    "Restaurant mit Lieferservice Karlsruhe Oberreut",
    "Restaurant mit Lieferservice Karlsruhe Grünwinkel",
    "Restaurant mit Lieferservice Karlsruhe Rüppurr",
    "Pizza Lieferservice Karlsruhe",
    "Sushi Lieferservice Karlsruhe",
    "Asiatischer Lieferservice Karlsruhe",
    "Indischer Lieferservice Karlsruhe",
]

MAX_PAGES = 3            # Seiten pro Query (Pagination)
PAGE_SLEEP_S = 1.0       # Wartezeit zwischen Seiten (gegen 429)

# --------------------------------------------------------------------------
# Datenbank
# --------------------------------------------------------------------------


def init_db(conn):
    """Legt die drei Tabellen an, falls sie noch nicht existieren."""
    conn.executescript(
        """
        CREATE TABLE IF NOT EXISTS restaurants (
            place_id        TEXT PRIMARY KEY,
            name            TEXT,
            address         TEXT,
            lat             REAL,
            lng             REAL,
            website         TEXT,
            delivery        INTEGER,          -- 1/0/NULL (NULL = unbekannt, z. B. Light-Scan)
            business_status TEXT,
            active          INTEGER NOT NULL DEFAULT 1,   -- 0 = als REMOVED markiert
            first_seen      TEXT NOT NULL,
            last_seen       TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS changes (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            place_id    TEXT NOT NULL,
            change_type TEXT NOT NULL,        -- NEW/REMOVED/ADDRESS_CHANGED/DELIVERY_CHANGED/STATUS_CHANGED
            old_value   TEXT,
            new_value   TEXT,
            detected_at TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS scan_runs (
            id           INTEGER PRIMARY KEY AUTOINCREMENT,
            started_at   TEXT NOT NULL,
            mode         TEXT NOT NULL,       -- full/light/mock
            api_calls    INTEGER NOT NULL DEFAULT 0,
            places_found INTEGER NOT NULL DEFAULT 0
        );
        """
    )
    conn.commit()


def log_change(conn, place_id, change_type, old_value, new_value, ts):
    conn.execute(
        "INSERT INTO changes (place_id, change_type, old_value, new_value, detected_at)"
        " VALUES (?, ?, ?, ?, ?)",
        (place_id, change_type, old_value, new_value, ts),
    )


# --------------------------------------------------------------------------
# Places API
# --------------------------------------------------------------------------


def _post_json(url, payload, headers):
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers=headers, method="POST")
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read().decode("utf-8"))


def fetch_query(api_key, query, field_mask):
    """Holt alle Seiten einer Suchabfrage. Gibt (places, api_calls) zurück."""
    places = []
    api_calls = 0
    page_token = None

    for page in range(MAX_PAGES):
        payload = {
            "textQuery": query,
            "languageCode": "de",
            "regionCode": "DE",
            "locationBias": {
                "circle": {
                    "center": {"latitude": KARLSRUHE_LAT, "longitude": KARLSRUHE_LNG},
                    "radius": SEARCH_RADIUS_M,
                }
            },
        }
        if page_token:
            payload["pageToken"] = page_token

        headers = {
            "Content-Type": "application/json",
            "X-Goog-Api-Key": api_key,
            "X-Goog-FieldMask": field_mask,
        }

        try:
            result = _post_json(PLACES_ENDPOINT, payload, headers)
        except urllib.error.HTTPError as exc:
            body = exc.read().decode("utf-8", errors="replace")
            if exc.code == 429:
                print(f"  429 Too Many Requests bei '{query}' – überspringe Rest.",
                      file=sys.stderr)
                break
            print(f"  HTTP {exc.code} bei '{query}': {body}", file=sys.stderr)
            break

        api_calls += 1
        places.extend(result.get("places", []))

        page_token = result.get("nextPageToken")
        if not page_token:
            break
        time.sleep(PAGE_SLEEP_S)  # Google braucht kurz, bis das Token gültig ist

    return places, api_calls


def normalize_place(place, want_delivery):
    """Places-API-Objekt in ein flaches Dict für die DB umwandeln."""
    loc = place.get("location", {})
    delivery = None
    if want_delivery and "delivery" in place:
        delivery = 1 if place.get("delivery") else 0
    return {
        "place_id": place.get("id"),
        "name": (place.get("displayName") or {}).get("text"),
        "address": place.get("formattedAddress"),
        "lat": loc.get("latitude"),
        "lng": loc.get("longitude"),
        "website": place.get("websiteUri"),
        "delivery": delivery,
        "business_status": place.get("businessStatus"),
    }


# --------------------------------------------------------------------------
# Mock-Daten
# --------------------------------------------------------------------------

MOCK_PLACES = [
    {"place_id": "mock_001", "name": "Pizzeria Bella Napoli", "address": "Kaiserstraße 42, 76133 Karlsruhe",
     "lat": 49.0094, "lng": 8.4044, "website": "https://bella-napoli-ka.example", "delivery": 1, "business_status": "OPERATIONAL"},
    {"place_id": "mock_002", "name": "Sushi Karlsruhe Express", "address": "Ludwigsplatz 3, 76133 Karlsruhe",
     "lat": 49.0075, "lng": 8.3968, "website": "https://sushi-ka.example", "delivery": 1, "business_status": "OPERATIONAL"},
    {"place_id": "mock_003", "name": "Curry House Südstadt", "address": "Augartenstraße 12, 76137 Karlsruhe",
     "lat": 48.9985, "lng": 8.4051, "website": "https://curryhouse-ka.example", "delivery": 1, "business_status": "OPERATIONAL"},
    {"place_id": "mock_004", "name": "Burger Bude Weststadt", "address": "Sophienstraße 88, 76135 Karlsruhe",
     "lat": 49.0068, "lng": 8.3805, "website": "https://burgerbude-ka.example", "delivery": 1, "business_status": "OPERATIONAL"},
    {"place_id": "mock_005", "name": "Thai Garden Durlach", "address": "Pfinztalstraße 20, 76227 Karlsruhe",
     "lat": 48.9977, "lng": 8.4712, "website": "https://thaigarden-ka.example", "delivery": 1, "business_status": "OPERATIONAL"},
    {"place_id": "mock_006", "name": "Döner & More Mühlburg", "address": "Rheinstraße 15, 76185 Karlsruhe",
     "lat": 49.0126, "lng": 8.3591, "website": None, "delivery": 1, "business_status": "OPERATIONAL"},
    {"place_id": "mock_007", "name": "Trattoria Oststadt", "address": "Gerwigstraße 5, 76131 Karlsruhe",
     "lat": 49.0113, "lng": 8.4287, "website": "https://trattoria-ost.example", "delivery": 0, "business_status": "OPERATIONAL"},
    {"place_id": "mock_008", "name": "Vietnam Küche Neureut", "address": "Neureuter Hauptstraße 100, 76149 Karlsruhe",
     "lat": 49.0421, "lng": 8.3768, "website": "https://vietnam-neureut.example", "delivery": 1, "business_status": "OPERATIONAL"},
    {"place_id": "mock_009", "name": "Falafel Palast Waldstadt", "address": "Kanzlerstraße 8, 76139 Karlsruhe",
     "lat": 49.0313, "lng": 8.4384, "website": "https://falafel-waldstadt.example", "delivery": 1, "business_status": "OPERATIONAL"},
    {"place_id": "mock_010", "name": "Pasta Fresca Südweststadt", "address": "Ebertstraße 30, 76135 Karlsruhe",
     "lat": 49.0002, "lng": 8.3902, "website": "https://pastafresca-ka.example", "delivery": 1, "business_status": "OPERATIONAL"},
]


# --------------------------------------------------------------------------
# Kern: Scan
# --------------------------------------------------------------------------


def sync_places(conn, places, mode, scan_ts):
    """Upsert der gefundenen Places + Änderungserkennung.

    ``places`` ist eine Liste flacher Dicts (siehe normalize_place / MOCK_PLACES).
    Gibt die Anzahl eindeutiger, verarbeiteter Restaurants zurück.
    """
    want_delivery = mode in ("full", "mock")
    seen_ids = set()

    for p in places:
        pid = p.get("place_id")
        if not pid:
            continue
        seen_ids.add(pid)

        row = conn.execute(
            "SELECT name, address, delivery, business_status, active"
            " FROM restaurants WHERE place_id = ?",
            (pid,),
        ).fetchone()

        if row is None:
            # Neues Restaurant
            conn.execute(
                "INSERT INTO restaurants"
                " (place_id, name, address, lat, lng, website, delivery,"
                "  business_status, active, first_seen, last_seen)"
                " VALUES (?, ?, ?, ?, ?, ?, ?, ?, 1, ?, ?)",
                (pid, p["name"], p["address"], p["lat"], p["lng"], p["website"],
                 p["delivery"], p["business_status"], scan_ts, scan_ts),
            )
            log_change(conn, pid, "NEW", None, p["name"], scan_ts)
            continue

        old_name, old_addr, old_delivery, old_status, old_active = row

        # Adressänderung
        if p["address"] and p["address"] != old_addr:
            log_change(conn, pid, "ADDRESS_CHANGED", old_addr, p["address"], scan_ts)

        # Statusänderung (OPERATIONAL / CLOSED_TEMPORARILY / CLOSED_PERMANENTLY)
        if p["business_status"] and p["business_status"] != old_status:
            log_change(conn, pid, "STATUS_CHANGED", old_status, p["business_status"], scan_ts)

        # Lieferstatus – nur im Voll-Scan geprüft (Light holt das Feld nicht)
        if want_delivery and p["delivery"] is not None and p["delivery"] != old_delivery:
            log_change(conn, pid, "DELIVERY_CHANGED",
                       _delivery_str(old_delivery), _delivery_str(p["delivery"]), scan_ts)

        # Wiederauferstehung: war als REMOVED markiert, jetzt wieder da
        if old_active == 0:
            log_change(conn, pid, "NEW", None, p["name"], scan_ts)

        # Update. Im Light-Modus delivery NICHT überschreiben (Feld nicht abgefragt).
        if want_delivery:
            conn.execute(
                "UPDATE restaurants SET name=?, address=?, lat=?, lng=?, website=?,"
                " delivery=?, business_status=?, active=1, last_seen=? WHERE place_id=?",
                (p["name"], p["address"], p["lat"], p["lng"], p["website"],
                 p["delivery"], p["business_status"], scan_ts, pid),
            )
        else:
            conn.execute(
                "UPDATE restaurants SET name=?, address=?, lat=?, lng=?,"
                " business_status=?, active=1, last_seen=? WHERE place_id=?",
                (p["name"], p["address"], p["lat"], p["lng"],
                 p["business_status"], scan_ts, pid),
            )

    # REMOVED-Erkennung nur im Voll-Scan (mock zählt als voll).
    # Light markiert absichtlich NICHTS als entfernt (Google-Caching-Delays).
    if mode in ("full", "mock"):
        stale = conn.execute(
            "SELECT place_id, name FROM restaurants WHERE active = 1 AND last_seen < ?",
            (scan_ts,),
        ).fetchall()
        for pid, name in stale:
            conn.execute("UPDATE restaurants SET active = 0 WHERE place_id = ?", (pid,))
            log_change(conn, pid, "REMOVED", name, None, scan_ts)

    conn.commit()
    return len(seen_ids)


def _delivery_str(val):
    if val is None:
        return "unbekannt"
    return "ja" if val else "nein"


# --------------------------------------------------------------------------
# Main
# --------------------------------------------------------------------------


def run_scan(mode):
    scan_ts = datetime.now(timezone.utc).isoformat()
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    try:
        init_db(conn)

        api_calls = 0
        if mode == "mock":
            print("Mock-Modus: fülle DB mit Demodaten (keine API-Kosten).")
            places = list(MOCK_PLACES)
        else:
            api_key = os.environ.get("PLACES_API_KEY")
            if not api_key:
                print("PLACES_API_KEY not set", file=sys.stderr)
                print("  export PLACES_API_KEY=\"dein-key\"  (oder --mock nutzen)",
                      file=sys.stderr)
                return 1

            field_mask = FULL_FIELD_MASK if mode == "full" else LIGHT_FIELD_MASK
            want_delivery = mode == "full"
            raw_by_id = {}
            print(f"{mode}-Scan: {len(SEARCH_QUERIES)} Abfragen, max. {MAX_PAGES} Seiten je.")
            for query in SEARCH_QUERIES:
                found, calls = fetch_query(api_key, query, field_mask)
                api_calls += calls
                for place in found:
                    norm = normalize_place(place, want_delivery)
                    if norm["place_id"]:
                        raw_by_id[norm["place_id"]] = norm  # dedupe über Queries hinweg
                print(f"  '{query}': {len(found)} Treffer ({calls} API-Aufrufe)")
            places = list(raw_by_id.values())

        count = sync_places(conn, places, mode, scan_ts)

        conn.execute(
            "INSERT INTO scan_runs (started_at, mode, api_calls, places_found)"
            " VALUES (?, ?, ?, ?)",
            (scan_ts, mode, api_calls, count),
        )
        conn.commit()

        active = conn.execute(
            "SELECT COUNT(*) FROM restaurants WHERE active = 1"
        ).fetchone()[0]
        print(f"Fertig: {count} Restaurants im Scan, {active} aktiv in DB, "
              f"{api_calls} API-Aufrufe.")
        return 0
    finally:
        conn.close()


def main(argv=None):
    parser = argparse.ArgumentParser(description="Lieferkarte Karlsruhe – Scanner")
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--mock", action="store_true",
                       help="Demodaten laden, keine API, keine Kosten")
    group.add_argument("--light", action="store_true",
                       help="günstiger Existenz-/Adress-Check, kein delivery, keine REMOVED-Erkennung")
    args = parser.parse_args(argv)

    if args.mock:
        mode = "mock"
    elif args.light:
        mode = "light"
    else:
        mode = "full"

    return run_scan(mode)


if __name__ == "__main__":
    sys.exit(main())
