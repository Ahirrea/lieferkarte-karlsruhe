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
from datetime import datetime, timedelta, timezone

DB_PATH = os.path.join(os.path.dirname(__file__), "data", "restaurants.db")
OUT_PATH = os.path.join(os.path.dirname(__file__), "web", "restaurants.json")

# Rohes Änderungsprotokoll (jüngste Einträge), unabhängig vom Feed-Fenster.
RECENT_CHANGES_LIMIT = 50

# Änderungs-Feed („Diese Woche neu …"): Zeitfenster in Tagen, gerechnet ab dem
# letzten Scan (nicht ab „jetzt" – sonst wäre der Feed leer, wenn der Export
# einmal Tage nach dem Scan läuft).
FEED_WINDOW_DAYS = 7

# Pro Änderungsart in den Feed exportierte Einträge. Die Gesamtzahl steht
# trotzdem in ``counts`` – das Frontend zeigt „… und N weitere". Verhindert,
# dass ein Massen-Ereignis (z. B. 245 neu getaggte takeaway-Werte) den Feed
# und die JSON aufbläht.
FEED_MAX_PER_TYPE = 12

# Reihenfolge der Gruppen im Feed; unbekannte Arten wandern ans Ende.
FEED_TYPE_ORDER = (
    "NEW", "REMOVED", "DELIVERY_CHANGED", "TAKEAWAY_CHANGED",
    "ADDRESS_CHANGED", "STATUS_CHANGED",
)


def _parse_ts(value):
    """ISO-Zeitstempel aus der DB parsen; bei Unfug ``None``."""
    try:
        return datetime.fromisoformat(value)
    except (TypeError, ValueError):
        return None


def build_feed(conn):
    """Kuratiertes Änderungsprotokoll für den „Diese Woche neu"-Feed.

    Anders als ``recentChanges`` (rohe letzte N Zeilen) ist das hier die
    anzeigefertige Sicht:

    - nur Änderungen der letzten ``FEED_WINDOW_DAYS`` Tage, gerechnet ab dem
      jüngsten Scan,
    - **ohne den Erstimport**: der allererste Scan protokolliert jedes
      gefundene Restaurant als ``NEW`` (in diesem Repo 883 Zeilen) – das ist
      keine Neuigkeit, sondern der Anfangsbestand. Alles, was am Zeitstempel
      des ersten ``scan_runs``-Eintrags protokolliert wurde, fällt daher raus,
    - angereichert mit Name/Adresse/Koordinaten aus ``restaurants``, damit die
      Karte die Einträge anzeigen und anspringen kann.
    """
    empty = {"since": None, "until": None, "windowDays": FEED_WINDOW_DAYS,
             "total": 0, "counts": {}, "items": []}

    anchor = conn.execute("SELECT MAX(started_at) AS t FROM scan_runs").fetchone()["t"]
    if not anchor:
        anchor = conn.execute("SELECT MAX(detected_at) AS t FROM changes").fetchone()["t"]
    anchor_dt = _parse_ts(anchor)
    if anchor_dt is None:
        return empty
    since = (anchor_dt - timedelta(days=FEED_WINDOW_DAYS)).isoformat()

    # Zeitstempel des Erstimports (erster Scan). Fehlt die Zeile, gibt es
    # nichts auszublenden – dann zählt allein das Zeitfenster.
    first_scan = conn.execute("SELECT MIN(started_at) AS t FROM scan_runs").fetchone()["t"]

    rows = conn.execute(
        "SELECT c.place_id, c.change_type, c.old_value, c.new_value, c.detected_at,"
        " r.name, r.address, r.lat, r.lng, r.active"
        " FROM changes c LEFT JOIN restaurants r ON r.place_id = c.place_id"
        " WHERE c.detected_at >= ? AND (? IS NULL OR c.detected_at > ?)"
        " ORDER BY c.detected_at DESC, c.id DESC",
        (since, first_scan, first_scan),
    ).fetchall()

    counts = {}
    items = []
    for r in rows:
        change_type = r["change_type"]
        counts[change_type] = counts.get(change_type, 0) + 1
        if counts[change_type] > FEED_MAX_PER_TYPE:
            continue   # Gesamtzahl bleibt in counts, nur die Zeile fehlt
        # Name: aus dem Bestand, sonst aus der protokollierten Änderung
        # (NEW schreibt den Namen nach new_value, REMOVED nach old_value).
        name = r["name"] or r["new_value"] or r["old_value"] or r["place_id"]
        items.append({
            "placeId": r["place_id"],
            "type": change_type,
            "name": name,
            "address": r["address"],
            "lat": r["lat"],
            "lng": r["lng"],
            "oldValue": r["old_value"],
            "newValue": r["new_value"],
            "detectedAt": r["detected_at"],
            "active": bool(r["active"]),
        })

    # Nach Gruppen sortieren; innerhalb einer Gruppe bleibt die Reihenfolge
    # der Abfrage erhalten (neueste zuerst), weil sort() stabil ist.
    def group_key(item):
        try:
            return FEED_TYPE_ORDER.index(item["type"])
        except ValueError:
            return len(FEED_TYPE_ORDER)

    items.sort(key=group_key)

    return {
        "since": since,
        "until": anchor,
        "windowDays": FEED_WINDOW_DAYS,
        "total": sum(counts.values()),
        "counts": counts,
        "items": items,
    }


def export():
    if not os.path.exists(DB_PATH):
        print(f"DB nicht gefunden: {DB_PATH}", file=sys.stderr)
        print("  Erst scanner.py laufen lassen (Voll-Scan über Overpass).",
              file=sys.stderr)
        return 1

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        restaurants = []
        for r in conn.execute(
            "SELECT place_id, name, address, lat, lng, website, delivery, takeaway,"
            " opening_hours, cuisine, business_status, first_seen, last_seen"
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
                "takeaway": None if r["takeaway"] is None else bool(r["takeaway"]),
                "openingHours": r["opening_hours"],
                # Küchenstile als Liste; leer = nicht getaggt (unbekannt).
                "cuisines": r["cuisine"].split(";") if r["cuisine"] else [],
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

        feed = build_feed(conn)

        last_run = conn.execute(
            "SELECT started_at, mode FROM scan_runs ORDER BY id DESC LIMIT 1"
        ).fetchone()

        payload = {
            "count": len(restaurants),
            "generatedAt": datetime.now(timezone.utc).isoformat(),
            "lastScanAt": last_run["started_at"] if last_run else None,
            "lastScanMode": last_run["mode"] if last_run else None,
            "attribution": "Daten & Karte: © OpenStreetMap-Mitwirkende (ODbL)",
            "restaurants": restaurants,
            "recentChanges": changes,
            "feed": feed,
        }

        os.makedirs(os.path.dirname(OUT_PATH), exist_ok=True)
        with open(OUT_PATH, "w", encoding="utf-8") as fh:
            json.dump(payload, fh, ensure_ascii=False, indent=2)
            fh.write("\n")

        print(f"Geschrieben: {OUT_PATH} ({len(restaurants)} Restaurants, "
              f"{len(changes)} Änderungen, {feed['total']} im Feed der letzten "
              f"{FEED_WINDOW_DAYS} Tage).")
        return 0
    finally:
        conn.close()


if __name__ == "__main__":
    sys.exit(export())
