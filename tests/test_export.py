"""Tests für export.py – DB nach web/restaurants.json.

Nur Standardbibliothek (unittest). Arbeitet komplett in einem
Temporär-Verzeichnis; die echte DB und das echte JSON bleiben unberührt.
"""

import contextlib
import io
import json
import os
import sqlite3
import sys
import tempfile
import unittest
from unittest import mock

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import export
from tests.helpers import TS1, TS2, make_place, seed_db

# Deckt alle drei Zustände von delivery/takeaway (true/false/null) und die
# Sortierung unabhängig von Groß-/Kleinschreibung ab.
FIXTURE_PLACES = [
    make_place("node/1", name="Zebra Grill", delivery=1, takeaway=1,
               opening_hours="Mo-Su 11:00-22:00"),
    make_place("node/2", name="alpha Pizza", delivery=0),
    make_place("node/3", name="Curry Eck", takeaway=0),
    make_place("node/4", name="Beta Sushi", delivery=1,
               website="https://beta-sushi.example"),
]


class ExportCase(unittest.TestCase):
    """Gemeinsames Setup: Temp-DB + Temp-JSON, echte Dateien bleiben unberührt."""

    def setUp(self):
        self.tmpdir = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmpdir.cleanup)
        self.db_path = os.path.join(self.tmpdir.name, "restaurants.db")
        self.out_path = os.path.join(self.tmpdir.name, "web", "restaurants.json")
        for attr, value in (("DB_PATH", self.db_path), ("OUT_PATH", self.out_path)):
            patcher = mock.patch.object(export, attr, value)
            patcher.start()
            self.addCleanup(patcher.stop)
        seed_db(self.db_path, FIXTURE_PLACES)

    def _export(self):
        with contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(export.export(), 0)
        with open(self.out_path, encoding="utf-8") as fh:
            return json.load(fh)


class ExportTest(ExportCase):
    def test_json_struktur_und_pflichtfelder(self):
        payload = self._export()
        # Felder, die Workflow (jq) und Frontend erwarten.
        for key in ("count", "generatedAt", "lastScanAt", "lastScanMode",
                    "attribution", "restaurants", "recentChanges", "feed"):
            self.assertIn(key, payload)
        self.assertEqual(payload["count"], len(FIXTURE_PLACES))
        self.assertEqual(payload["count"], len(payload["restaurants"]))
        self.assertEqual(payload["lastScanMode"], "full")

    def test_odbl_attribution_ist_enthalten(self):
        """ODbL-Pflicht: die OSM-Attribution darf nie verschwinden."""
        payload = self._export()
        self.assertIn("© OpenStreetMap-Mitwirkende", payload["attribution"])

    def test_delivery_und_takeaway_sind_bool_oder_null(self):
        payload = self._export()
        for r in payload["restaurants"]:
            self.assertIn(r["delivery"], (True, False, None))
            self.assertIn(r["takeaway"], (True, False, None))
        # Die Fixtures enthalten bewusst alle drei Fälle.
        self.assertEqual({r["delivery"] for r in payload["restaurants"]},
                         {True, False, None})
        self.assertEqual({r["takeaway"] for r in payload["restaurants"]},
                         {True, False, None})

    def test_entfernte_restaurants_werden_nicht_exportiert(self):
        conn = sqlite3.connect(self.db_path)
        conn.execute("UPDATE restaurants SET active = 0 WHERE place_id = 'node/1'")
        conn.commit()
        conn.close()
        payload = self._export()
        self.assertEqual(payload["count"], len(FIXTURE_PLACES) - 1)
        ids = [r["placeId"] for r in payload["restaurants"]]
        self.assertNotIn("node/1", ids)

    def test_sortierung_nach_name(self):
        payload = self._export()
        names = [r["name"] for r in payload["restaurants"]]
        self.assertEqual(names, ["alpha Pizza", "Beta Sushi", "Curry Eck",
                                 "Zebra Grill"])

    def test_fehlende_db_gibt_fehler_und_schreibt_nichts(self):
        os.remove(self.db_path)
        with contextlib.redirect_stderr(io.StringIO()):
            self.assertEqual(export.export(), 1)
        self.assertFalse(os.path.exists(self.out_path))


class FeedTest(ExportCase):
    """Änderungs-Feed („Diese Woche neu …") – ``feed`` in restaurants.json."""

    def test_erstimport_erscheint_nicht_im_feed(self):
        """Der erste Scan protokolliert jedes Restaurant als NEW – kein Feed-Stoff."""
        feed = self._export()["feed"]
        self.assertEqual(feed["total"], 0)
        self.assertEqual(feed["items"], [])
        self.assertEqual(feed["counts"], {})
        # Das rohe Protokoll enthält die NEW-Zeilen weiterhin.
        self.assertEqual(len(self._export()["recentChanges"]), len(FIXTURE_PLACES))

    def test_neue_und_geaenderte_landen_im_feed(self):
        seed_db(self.db_path, FIXTURE_PLACES + [
            make_place("node/5", name="Neu am Markt", delivery=1),
            make_place("node/2", name="alpha Pizza", delivery=1),   # war 0
        ], ts=TS2)
        feed = self._export()["feed"]

        self.assertEqual(feed["counts"], {"NEW": 1, "DELIVERY_CHANGED": 1})
        self.assertEqual(feed["total"], 2)
        self.assertEqual(feed["until"], TS2)
        self.assertEqual(feed["windowDays"], export.FEED_WINDOW_DAYS)

        neu = feed["items"][0]
        self.assertEqual((neu["type"], neu["placeId"]), ("NEW", "node/5"))
        # Für die Karte angereichert: Name, Adresse, Koordinaten, Zustand.
        self.assertEqual(neu["name"], "Neu am Markt")
        self.assertEqual((neu["lat"], neu["lng"]), (49.0, 8.4))
        self.assertIn("Kaiserstraße", neu["address"])
        self.assertTrue(neu["active"])
        self.assertEqual(neu["detectedAt"], TS2)

        geaendert = feed["items"][1]
        self.assertEqual(geaendert["type"], "DELIVERY_CHANGED")
        self.assertEqual((geaendert["oldValue"], geaendert["newValue"]),
                         ("nein", "ja"))

    def test_entfernte_bleiben_mit_namen_im_feed(self):
        """REMOVED-Einträge fehlen in `restaurants` – der Feed nennt sie trotzdem."""
        seed_db(self.db_path, [p for p in FIXTURE_PLACES
                               if p["place_id"] != "node/1"], ts=TS2)
        payload = self._export()
        self.assertNotIn("node/1", [r["placeId"] for r in payload["restaurants"]])

        removed = [it for it in payload["feed"]["items"] if it["type"] == "REMOVED"]
        self.assertEqual(len(removed), 1)
        self.assertEqual(removed[0]["placeId"], "node/1")
        self.assertEqual(removed[0]["name"], "Zebra Grill")
        self.assertFalse(removed[0]["active"])
        self.assertIsNotNone(removed[0]["lat"])   # anspringbar auf der Karte

    def test_gruppen_reihenfolge_neu_zuerst(self):
        seed_db(self.db_path, [
            make_place("node/2", name="alpha Pizza", delivery=1),          # DELIVERY
            make_place("node/3", name="Curry Eck", takeaway=1),            # TAKEAWAY
            make_place("node/4", name="Beta Sushi", delivery=1,
                       address="Neue Straße 2, 76133 Karlsruhe"),          # ADDRESS
            make_place("node/6", name="Frischling"),                       # NEW
        ], ts=TS2)   # node/1 fehlt -> REMOVED
        typen = [it["type"] for it in self._export()["feed"]["items"]]
        self.assertEqual(typen, ["NEW", "REMOVED", "DELIVERY_CHANGED",
                                 "TAKEAWAY_CHANGED", "ADDRESS_CHANGED"])

    def test_aeltere_aenderungen_fallen_aus_dem_zeitfenster(self):
        seed_db(self.db_path, FIXTURE_PLACES + [make_place("node/5")], ts=TS2)
        spaeter = "2026-03-01T00:00:00+00:00"   # weit mehr als 7 Tage nach TS2
        seed_db(self.db_path, FIXTURE_PLACES + [
            make_place("node/5"), make_place("node/6"),
        ], ts=spaeter)

        feed = self._export()["feed"]
        self.assertEqual(feed["until"], spaeter)
        self.assertEqual(feed["since"], "2026-02-22T00:00:00+00:00")
        # Nur node/6 (aus dem letzten Scan) ist noch im Fenster.
        self.assertEqual([it["placeId"] for it in feed["items"]], ["node/6"])

    def test_massenaenderung_wird_gekappt_zahl_bleibt_vollstaendig(self):
        viele = [make_place(f"node/1{i}") for i in range(export.FEED_MAX_PER_TYPE + 5)]
        seed_db(self.db_path, FIXTURE_PLACES + viele, ts=TS2)
        feed = self._export()["feed"]

        self.assertEqual(feed["counts"]["NEW"], len(viele))
        self.assertEqual(len(feed["items"]), export.FEED_MAX_PER_TYPE)
        self.assertEqual(feed["total"], len(viele))

    def test_feed_ohne_scan_runs_stuerzt_nicht_ab(self):
        """Läuft der Export auf einer DB ohne scan_runs, bleibt der Feed leer."""
        conn = sqlite3.connect(self.db_path)
        conn.execute("DELETE FROM scan_runs")
        conn.commit()
        conn.close()
        payload = self._export()
        self.assertIsNone(payload["lastScanAt"])
        # Ohne scan_runs gibt es keinen Erstimport-Zeitstempel: der jüngste
        # Änderungs-Zeitstempel wird zum Anker, alles im Fenster ist Feed.
        self.assertEqual(payload["feed"]["until"], TS1)
        self.assertEqual(payload["feed"]["counts"], {"NEW": len(FIXTURE_PLACES)})


if __name__ == "__main__":
    unittest.main()
