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
import scanner


class ExportTest(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmpdir.cleanup)
        self.db_path = os.path.join(self.tmpdir.name, "restaurants.db")
        self.out_path = os.path.join(self.tmpdir.name, "web", "restaurants.json")
        for target, attr, value in (
            (scanner, "DB_PATH", self.db_path),
            (export, "DB_PATH", self.db_path),
            (export, "OUT_PATH", self.out_path),
        ):
            patcher = mock.patch.object(target, attr, value)
            patcher.start()
            self.addCleanup(patcher.stop)
        with contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(scanner.run_scan("mock"), 0)

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
        self.assertEqual(payload["count"], len(scanner.MOCK_PLACES))
        self.assertEqual(payload["count"], len(payload["restaurants"]))
        self.assertEqual(payload["lastScanMode"], "mock")

    def test_odbl_attribution_ist_enthalten(self):
        """ODbL-Pflicht: die OSM-Attribution darf nie verschwinden."""
        payload = self._export()
        self.assertIn("© OpenStreetMap-Mitwirkende", payload["attribution"])

    def test_delivery_und_takeaway_sind_bool_oder_null(self):
        payload = self._export()
        for r in payload["restaurants"]:
            self.assertIn(r["delivery"], (True, False, None))
            self.assertIn(r["takeaway"], (True, False, None))
        # Die Mock-Daten enthalten bewusst alle drei Fälle für takeaway.
        takeaways = {r["takeaway"] for r in payload["restaurants"]}
        self.assertEqual(takeaways, {True, None})

    def test_entfernte_restaurants_werden_nicht_exportiert(self):
        conn = sqlite3.connect(self.db_path)
        conn.execute("UPDATE restaurants SET active = 0 WHERE place_id = 'mock_001'")
        conn.commit()
        conn.close()
        payload = self._export()
        self.assertEqual(payload["count"], len(scanner.MOCK_PLACES) - 1)
        ids = [r["placeId"] for r in payload["restaurants"]]
        self.assertNotIn("mock_001", ids)

    def test_sortierung_nach_name(self):
        payload = self._export()
        names = [r["name"] for r in payload["restaurants"]]
        self.assertEqual(names, sorted(names, key=str.casefold))

    def test_fehlende_db_gibt_fehler_und_schreibt_nichts(self):
        os.remove(self.db_path)
        with contextlib.redirect_stderr(io.StringIO()):
            self.assertEqual(export.export(), 1)
        self.assertFalse(os.path.exists(self.out_path))


if __name__ == "__main__":
    unittest.main()
