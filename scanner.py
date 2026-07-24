#!/usr/bin/env python3
"""Lieferkarte Karlsruhe – Scanner.

Fragt Restaurants mit Lieferservice in Karlsruhe über die **Overpass API**
(OpenStreetMap) ab, speichert sie in SQLite (``data/restaurants.db``) und
erkennt Änderungen gegenüber dem vorherigen Scan.

Warum OpenStreetMap statt Google Places?

- **Kostenlos:** kein API-Key, kein Billing, ein Overpass-Aufruf pro Scan.
- **Frei weiterverteilbar:** OSM steht unter der ODbL. Daten dürfen (mit
  Attribution "© OpenStreetMap-Mitwirkende") öffentlich weitergegeben werden –
  genau das, was ein öffentliches Repo + GitHub Pages tun. Bei Google Places
  wäre das durch die Nutzungsbedingungen nicht gedeckt.

Zwei Modi:

    python3 scanner.py            Voll-Scan: Bestand + Änderungen + REMOVED-Erkennung
    python3 scanner.py --light    Refresh ohne REMOVED-Erkennung

Nur Standardbibliothek – keine externen Pakete nötig (wichtig für CI).
"""

import argparse
import json
import os
import sqlite3
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone

# --------------------------------------------------------------------------
# Konfiguration
# --------------------------------------------------------------------------

DB_PATH = os.path.join(os.path.dirname(__file__), "data", "restaurants.db")

# Overpass-Endpoint. Per Umgebungsvariable überschreibbar, falls ein
# Spiegelserver (z. B. https://overpass.kumi.systems/api/interpreter) nötig ist.
OVERPASS_ENDPOINT = os.environ.get(
    "OVERPASS_ENDPOINT", "https://overpass-api.de/api/interpreter"
)

# Freundlicher User-Agent (Overpass-Etikette: identifiziere den Client).
USER_AGENT = "LieferkarteKarlsruhe/1.0 (+https://github.com/Ahirrea/lieferkarte-karlsruhe)"

# Karlsruhe-Zentrum + Radius für die Umkreissuche.
KARLSRUHE_LAT = 49.0069
KARLSRUHE_LNG = 8.4037
SEARCH_RADIUS_M = 12000

# Ein einziger Overpass-QL-Query holt alle Gastro-Objekte im Umkreis.
# ``nwr`` = nodes + ways + relations; ``out center tags`` liefert für Flächen
# einen Mittelpunkt und alle Tags.
OVERPASS_QUERY = f"""
[out:json][timeout:90];
(
  nwr(around:{SEARCH_RADIUS_M},{KARLSRUHE_LAT},{KARLSRUHE_LNG})
     ["amenity"~"^(restaurant|fast_food)$"];
);
out center tags;
"""

REQUEST_TIMEOUT_S = 120
RETRY_SLEEP_S = 5.0     # Wartezeit bei 429/5xx vor erneutem Versuch
MAX_RETRIES = 2

# --------------------------------------------------------------------------
# Datenbank
# --------------------------------------------------------------------------


def init_db(conn):
    """Legt die drei Tabellen an, falls sie noch nicht existieren."""
    conn.executescript(
        """
        CREATE TABLE IF NOT EXISTS restaurants (
            place_id        TEXT PRIMARY KEY,      -- OSM-Schlüssel, z. B. "node/12345"
            name            TEXT,
            address         TEXT,
            lat             REAL,
            lng             REAL,
            website         TEXT,
            delivery        INTEGER,          -- 1/0/NULL (NULL = unbekannt / nicht getaggt) -- Lieferung
            takeaway        INTEGER,          -- 1/0/NULL (NULL = unbekannt / nicht getaggt) -- Abholung
            opening_hours   TEXT,             -- OSM-Tag opening_hours (Rohtext, NULL = nicht getaggt)
            cuisine         TEXT,             -- Küchenstil, normalisiert & ";"-getrennt (NULL = nicht getaggt)
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
            mode         TEXT NOT NULL,       -- full/light
            api_calls    INTEGER NOT NULL DEFAULT 0,
            places_found INTEGER NOT NULL DEFAULT 0
        );
        """
    )
    # Migration: nachträglich ergänzte Spalten in bestehende DBs einziehen
    # (CREATE TABLE IF NOT EXISTS legt sie in Alt-DBs nicht nachträglich an).
    cols = {row[1] for row in conn.execute("PRAGMA table_info(restaurants)")}
    if "takeaway" not in cols:
        conn.execute("ALTER TABLE restaurants ADD COLUMN takeaway INTEGER")
    if "opening_hours" not in cols:
        conn.execute("ALTER TABLE restaurants ADD COLUMN opening_hours TEXT")
    if "cuisine" not in cols:
        conn.execute("ALTER TABLE restaurants ADD COLUMN cuisine TEXT")
    conn.commit()


def log_change(conn, place_id, change_type, old_value, new_value, ts):
    conn.execute(
        "INSERT INTO changes (place_id, change_type, old_value, new_value, detected_at)"
        " VALUES (?, ?, ?, ?, ?)",
        (place_id, change_type, old_value, new_value, ts),
    )


# --------------------------------------------------------------------------
# Overpass API (OpenStreetMap)
# --------------------------------------------------------------------------


def fetch_overpass():
    """Holt alle Restaurants/Imbisse im Umkreis in EINEM Aufruf.

    Gibt ``(elements, api_calls)`` zurück. Wirft bei endgültigem Fehlschlag
    eine Exception – der Aufrufer bricht dann ab, statt einen leeren Scan
    zu verarbeiten (der sonst fälschlich alles als REMOVED markieren würde).
    """
    data = urllib.parse.urlencode({"data": OVERPASS_QUERY}).encode("utf-8")
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "User-Agent": USER_AGENT,
    }

    last_error = None
    for attempt in range(MAX_RETRIES + 1):
        req = urllib.request.Request(
            OVERPASS_ENDPOINT, data=data, headers=headers, method="POST"
        )
        try:
            with urllib.request.urlopen(req, timeout=REQUEST_TIMEOUT_S) as resp:
                result = json.loads(resp.read().decode("utf-8"))
            return result.get("elements", []), 1
        except urllib.error.HTTPError as exc:
            last_error = f"HTTP {exc.code}"
            # 429 (Rate Limit) und 504 (Overpass-Timeout) sind vorübergehend.
            if exc.code in (429, 502, 503, 504) and attempt < MAX_RETRIES:
                print(f"  Overpass {exc.code} – warte {RETRY_SLEEP_S}s und "
                      f"versuche erneut ({attempt + 1}/{MAX_RETRIES}).",
                      file=sys.stderr)
                time.sleep(RETRY_SLEEP_S)
                continue
            raise
        except (urllib.error.URLError, TimeoutError) as exc:
            last_error = str(exc)
            if attempt < MAX_RETRIES:
                print(f"  Overpass-Netzwerkfehler ({last_error}) – warte "
                      f"{RETRY_SLEEP_S}s und versuche erneut.", file=sys.stderr)
                time.sleep(RETRY_SLEEP_S)
                continue
            raise

    raise RuntimeError(f"Overpass-Abfrage fehlgeschlagen: {last_error}")


def _osm_address(tags):
    """Adresse aus addr:*-Tags zusammensetzen (soweit vorhanden)."""
    street = " ".join(t for t in (tags.get("addr:street"),
                                   tags.get("addr:housenumber")) if t)
    city = " ".join(t for t in (tags.get("addr:postcode"),
                                 tags.get("addr:city")) if t)
    return ", ".join(t for t in (street, city) if t) or None


def _osm_yesno(val):
    """OSM-Tag mit yes/only -> 1, no -> 0, sonst unbekannt (None)."""
    if val in ("yes", "only"):
        return 1
    if val == "no":
        return 0
    return None


# Werte im cuisine-Tag, die keinen Küchenstil benennen und deshalb wegfallen.
CUISINE_JUNK = {"yes", "no", "none", "unknown", "fixme", "other", "*"}


def _osm_cuisine(val):
    """OSM-Tag ``cuisine`` in eine kanonische Liste normalisieren.

    OSM erlaubt mehrere Küchenstile in einem Tag, getrennt durch ``;``
    (gelegentlich auch durch ``,``), in beliebiger Schreibweise:
    ``pizza;italian``, ``Pizza; Kebab``, ``ice cream``, ``coffee-shop``.

    Ergebnis ist ein ``;``-getrennter String aus kleingeschriebenen Schlüsseln
    mit ``_`` statt Leerzeichen/Bindestrich (``"pizza;italian"``,
    ``"ice_cream"``) – oder ``None``, wenn nichts Verwertbares übrig bleibt
    (= nicht getaggt / unbekannt). Die Reihenfolge aus OSM bleibt erhalten,
    Dubletten fallen weg.
    """
    if not val:
        return None
    keys = []
    for part in str(val).replace(",", ";").split(";"):
        key = "_".join(part.replace("-", " ").replace("_", " ").lower().split())
        if not key or key in CUISINE_JUNK or key in keys:
            continue
        keys.append(key)
    return ";".join(keys) or None


def normalize_osm(el):
    """OSM-Element in ein flaches Dict umwandeln."""
    tags = el.get("tags", {})

    # Koordinaten: node hat lat/lon direkt, way/relation über 'center'.
    center = el.get("center", {})
    lat = el.get("lat", center.get("lat"))
    lng = el.get("lon", center.get("lon"))

    return {
        "place_id": f"{el['type']}/{el['id']}",
        "name": tags.get("name"),
        "address": _osm_address(tags),
        "lat": lat,
        "lng": lng,
        "website": tags.get("website") or tags.get("contact:website"),
        "delivery": _osm_yesno(tags.get("delivery")),   # Lieferung
        "takeaway": _osm_yesno(tags.get("takeaway")),   # Abholung
        "opening_hours": tags.get("opening_hours"),      # Öffnungszeiten (Rohtext)
        "cuisine": _osm_cuisine(tags.get("cuisine")),    # Küchenstil (normalisiert)
        "business_status": None,   # OSM kennt kein Google-"businessStatus"
    }


# --------------------------------------------------------------------------
# Kern: Scan
# --------------------------------------------------------------------------


def sync_places(conn, places, mode, scan_ts):
    """Upsert der gefundenen Places + Änderungserkennung.

    ``places`` ist eine Liste flacher Dicts (siehe normalize_osm).
    Gibt die Anzahl eindeutiger, verarbeiteter Restaurants zurück.
    """
    seen_ids = set()

    for p in places:
        pid = p.get("place_id")
        if not pid:
            continue
        seen_ids.add(pid)

        row = conn.execute(
            "SELECT name, address, delivery, takeaway, business_status, active"
            " FROM restaurants WHERE place_id = ?",
            (pid,),
        ).fetchone()

        if row is None:
            # Neues Restaurant
            conn.execute(
                "INSERT INTO restaurants"
                " (place_id, name, address, lat, lng, website, delivery, takeaway,"
                "  opening_hours, cuisine, business_status, active, first_seen, last_seen)"
                " VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 1, ?, ?)",
                (pid, p["name"], p["address"], p["lat"], p["lng"], p["website"],
                 p["delivery"], p.get("takeaway"), p.get("opening_hours"),
                 p.get("cuisine"), p["business_status"], scan_ts, scan_ts),
            )
            log_change(conn, pid, "NEW", None, p["name"], scan_ts)
            continue

        old_name, old_addr, old_delivery, old_takeaway, old_status, old_active = row

        # Adressänderung
        if p["address"] and p["address"] != old_addr:
            log_change(conn, pid, "ADDRESS_CHANGED", old_addr, p["address"], scan_ts)

        # Statusänderung (bei OSM i. d. R. leer, daher selten)
        if p["business_status"] and p["business_status"] != old_status:
            log_change(conn, pid, "STATUS_CHANGED", old_status, p["business_status"], scan_ts)

        # Lieferstatus – OSM liefert das delivery-Tag kostenlos mit,
        # daher in jedem Modus geprüft (nur wenn tatsächlich getaggt).
        if p["delivery"] is not None and p["delivery"] != old_delivery:
            log_change(conn, pid, "DELIVERY_CHANGED",
                       _delivery_str(old_delivery), _delivery_str(p["delivery"]), scan_ts)

        # Abholstatus (takeaway) – analog zu delivery.
        new_takeaway = p.get("takeaway")
        if new_takeaway is not None and new_takeaway != old_takeaway:
            log_change(conn, pid, "TAKEAWAY_CHANGED",
                       _delivery_str(old_takeaway), _delivery_str(new_takeaway), scan_ts)

        # Küchenstil (cuisine) wird bewusst NICHT protokolliert: Umtaggen in OSM
        # (z. B. "pizza" -> "pizza;italian") ist häufig und für den
        # Änderungs-Feed ohne Aussagekraft – der aktuelle Wert genügt.

        # Wiederauferstehung: war als REMOVED markiert, jetzt wieder da
        if old_active == 0:
            log_change(conn, pid, "NEW", None, p["name"], scan_ts)

        conn.execute(
            "UPDATE restaurants SET name=?, address=?, lat=?, lng=?, website=?,"
            " delivery=?, takeaway=?, opening_hours=?, cuisine=?, business_status=?,"
            " active=1, last_seen=? WHERE place_id=?",
            (p["name"], p["address"], p["lat"], p["lng"], p["website"],
             p["delivery"], new_takeaway, p.get("opening_hours"),
             p.get("cuisine"), p["business_status"], scan_ts, pid),
        )

    # REMOVED-Erkennung nur im Voll-Scan.
    # --light markiert absichtlich NICHTS als entfernt – ein Refresh soll
    # keine Restaurants löschen, falls die Overpass-Antwort mal unvollständig ist.
    if mode == "full":
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

        print(f"{mode}-Scan: frage Overpass ab ({OVERPASS_ENDPOINT}).")
        try:
            elements, api_calls = fetch_overpass()
        except Exception as exc:  # Netz-/HTTP-Fehler
            print(f"Overpass-Abfrage fehlgeschlagen: {exc}", file=sys.stderr)
            print("  Scan abgebrochen – DB bleibt unverändert.", file=sys.stderr)
            return 1

        places = []
        for el in elements:
            if not el.get("id"):
                continue
            norm = normalize_osm(el)
            # Nur benannte Objekte mit Koordinaten sind sinnvoll anzeigbar.
            if norm["name"] and norm["lat"] is not None and norm["lng"] is not None:
                places.append(norm)

        print(f"  {len(elements)} OSM-Objekte, {len(places)} verwertbar "
              f"(mit Name + Koordinaten).")

        # Schutz: eine leere Antwort niemals als "alle entfernt" verarbeiten.
        if not places:
            print("Keine verwertbaren Objekte erhalten – Scan abgebrochen, "
                  "DB bleibt unverändert.", file=sys.stderr)
            return 1

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
              f"{api_calls} API-Aufruf(e).")
        return 0
    finally:
        conn.close()


def main(argv=None):
    parser = argparse.ArgumentParser(description="Lieferkarte Karlsruhe – Scanner (OpenStreetMap/Overpass)")
    parser.add_argument("--light", action="store_true",
                        help="Refresh ohne REMOVED-Erkennung")
    args = parser.parse_args(argv)

    return run_scan("light" if args.light else "full")


if __name__ == "__main__":
    sys.exit(main())
