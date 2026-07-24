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
from tests.helpers import make_place, seed_db

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


class ExportTest(unittest.TestCase):
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

    def test_json_struktur_und_pflichtfelder(self):
        payload = self._export()
        # Felder, die Workflow (jq) und Frontend erwarten.
        for key in ("count", "generatedAt", "lastScanAt", "lastScanMode",
                    "attribution", "restaurants", "recentChanges"):
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


if __name__ == "__main__":
    unittest.main()
