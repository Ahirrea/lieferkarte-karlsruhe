"""Tests für scanner.py – die Pipeline-Invarianten.

Nur Standardbibliothek (unittest), passend zum Rest des Projekts – keine
Installation nötig. Ausführen aus dem Repo-Root:

    python3 -m unittest discover -s tests -v

Alle Tests arbeiten mit In-Memory- oder Temporär-Datenbanken; die echte
``data/restaurants.db`` wird nie berührt.
"""

import contextlib
import io
import os
import sqlite3
import sys
import tempfile
import unittest
from unittest import mock

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import scanner

TS1 = "2026-01-01T00:00:00+00:00"
TS2 = "2026-01-02T00:00:00+00:00"
TS3 = "2026-01-03T00:00:00+00:00"


def make_place(pid, **overrides):
    """Vollständiges Place-Dict im Format von normalize_osm / MOCK_PLACES."""
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
        "business_status": None,
    }
    place.update(overrides)
    return place


class OsmYesnoTest(unittest.TestCase):
    """delivery/takeaway-Tags: yes/only -> 1, no -> 0, sonst None."""

    def test_yes_und_only_sind_wahr(self):
        self.assertEqual(scanner._osm_yesno("yes"), 1)
        self.assertEqual(scanner._osm_yesno("only"), 1)

    def test_no_ist_falsch(self):
        self.assertEqual(scanner._osm_yesno("no"), 0)

    def test_ungetaggt_oder_unbekannt_ist_none(self):
        self.assertIsNone(scanner._osm_yesno(None))
        self.assertIsNone(scanner._osm_yesno(""))
        self.assertIsNone(scanner._osm_yesno("Mo-Fr 11:00-14:00"))


class OsmAddressTest(unittest.TestCase):
    def test_vollstaendige_adresse(self):
        tags = {"addr:street": "Kaiserstraße", "addr:housenumber": "42",
                "addr:postcode": "76133", "addr:city": "Karlsruhe"}
        self.assertEqual(scanner._osm_address(tags),
                         "Kaiserstraße 42, 76133 Karlsruhe")

    def test_nur_strasse(self):
        self.assertEqual(scanner._osm_address({"addr:street": "Kaiserstraße"}),
                         "Kaiserstraße")

    def test_keine_adresstags_ergibt_none(self):
        self.assertIsNone(scanner._osm_address({}))


class NormalizeOsmTest(unittest.TestCase):
    def test_node_mit_direkten_koordinaten(self):
        el = {"type": "node", "id": 12345, "lat": 49.01, "lon": 8.40,
              "tags": {"name": "Testpizzeria", "delivery": "yes",
                       "takeaway": "no", "opening_hours": "Mo-Su 11:00-22:00"}}
        norm = scanner.normalize_osm(el)
        self.assertEqual(norm["place_id"], "node/12345")
        self.assertEqual(norm["name"], "Testpizzeria")
        self.assertEqual(norm["lat"], 49.01)
        self.assertEqual(norm["lng"], 8.40)
        self.assertEqual(norm["delivery"], 1)
        self.assertEqual(norm["takeaway"], 0)
        self.assertEqual(norm["opening_hours"], "Mo-Su 11:00-22:00")

    def test_way_nutzt_center_koordinaten(self):
        el = {"type": "way", "id": 777, "center": {"lat": 48.99, "lon": 8.45},
              "tags": {"name": "Flächenrestaurant"}}
        norm = scanner.normalize_osm(el)
        self.assertEqual(norm["place_id"], "way/777")
        self.assertEqual(norm["lat"], 48.99)
        self.assertEqual(norm["lng"], 8.45)

    def test_ungetaggte_liefer_und_abholtags_bleiben_none(self):
        el = {"type": "node", "id": 1, "lat": 49.0, "lon": 8.4,
              "tags": {"name": "Ohne Tags"}}
        norm = scanner.normalize_osm(el)
        self.assertIsNone(norm["delivery"])
        self.assertIsNone(norm["takeaway"])

    def test_website_fallback_auf_contact_website(self):
        el = {"type": "node", "id": 2, "lat": 49.0, "lon": 8.4,
              "tags": {"name": "X", "contact:website": "https://x.example"}}
        self.assertEqual(scanner.normalize_osm(el)["website"], "https://x.example")


class SyncPlacesTest(unittest.TestCase):
    """Änderungserkennung und die REMOVED-Asymmetrie (full vs. --light)."""

    def setUp(self):
        self.conn = sqlite3.connect(":memory:")
        scanner.init_db(self.conn)

    def tearDown(self):
        self.conn.close()

    def _changes(self, pid=None):
        sql = "SELECT place_id, change_type FROM changes"
        args = ()
        if pid:
            sql += " WHERE place_id = ?"
            args = (pid,)
        return self.conn.execute(sql + " ORDER BY id", args).fetchall()

    def _active(self, pid):
        return self.conn.execute(
            "SELECT active FROM restaurants WHERE place_id = ?", (pid,)
        ).fetchone()[0]

    def test_neues_restaurant_loggt_new(self):
        count = scanner.sync_places(self.conn, [make_place("node/1")], "full", TS1)
        self.assertEqual(count, 1)
        self.assertEqual(self._changes(), [("node/1", "NEW")])
        self.assertEqual(self._active("node/1"), 1)

    def test_unveraenderter_rescan_loggt_nichts(self):
        places = [make_place("node/1"), make_place("node/2")]
        scanner.sync_places(self.conn, places, "full", TS1)
        scanner.sync_places(self.conn, places, "full", TS2)
        types = [c[1] for c in self._changes()]
        self.assertEqual(types, ["NEW", "NEW"])  # nur aus dem ersten Scan

    def test_voll_scan_markiert_fehlende_als_removed(self):
        scanner.sync_places(self.conn, [make_place("node/1"), make_place("node/2")],
                            "full", TS1)
        scanner.sync_places(self.conn, [make_place("node/1")], "full", TS2)
        self.assertEqual(self._active("node/2"), 0)
        self.assertIn(("node/2", "REMOVED"), self._changes())

    def test_light_scan_markiert_niemals_removed(self):
        """Kerninvariante: eine unvollständige Antwort darf nichts löschen."""
        scanner.sync_places(self.conn, [make_place("node/1"), make_place("node/2")],
                            "full", TS1)
        scanner.sync_places(self.conn, [make_place("node/1")], "light", TS2)
        self.assertEqual(self._active("node/2"), 1)
        self.assertNotIn(("node/2", "REMOVED"), self._changes())

    def test_wiederauferstehung_loggt_erneut_new(self):
        scanner.sync_places(self.conn, [make_place("node/1")], "full", TS1)
        scanner.sync_places(self.conn, [], "full", TS2)  # node/1 -> REMOVED
        self.assertEqual(self._active("node/1"), 0)
        scanner.sync_places(self.conn, [make_place("node/1")], "full", TS3)
        self.assertEqual(self._active("node/1"), 1)
        types = [c[1] for c in self._changes("node/1")]
        self.assertEqual(types, ["NEW", "REMOVED", "NEW"])

    def test_delivery_aenderung_wird_geloggt(self):
        scanner.sync_places(self.conn, [make_place("node/1", delivery=1)], "full", TS1)
        scanner.sync_places(self.conn, [make_place("node/1", delivery=0)], "full", TS2)
        row = self.conn.execute(
            "SELECT old_value, new_value FROM changes"
            " WHERE change_type = 'DELIVERY_CHANGED'"
        ).fetchone()
        self.assertEqual(row, ("ja", "nein"))

    def test_entfallenes_delivery_tag_loggt_keine_aenderung(self):
        """delivery=None heißt 'unbekannt', nicht 'geändert'."""
        scanner.sync_places(self.conn, [make_place("node/1", delivery=1)], "full", TS1)
        scanner.sync_places(self.conn, [make_place("node/1", delivery=None)], "full", TS2)
        types = [c[1] for c in self._changes()]
        self.assertNotIn("DELIVERY_CHANGED", types)

    def test_takeaway_aenderung_wird_geloggt(self):
        scanner.sync_places(self.conn, [make_place("node/1", takeaway=0)], "full", TS1)
        scanner.sync_places(self.conn, [make_place("node/1", takeaway=1)], "full", TS2)
        types = [c[1] for c in self._changes()]
        self.assertIn("TAKEAWAY_CHANGED", types)

    def test_adressaenderung_wird_geloggt(self):
        scanner.sync_places(self.conn, [make_place("node/1")], "full", TS1)
        scanner.sync_places(
            self.conn,
            [make_place("node/1", address="Neue Straße 9, 76133 Karlsruhe")],
            "full", TS2,
        )
        row = self.conn.execute(
            "SELECT new_value FROM changes WHERE change_type = 'ADDRESS_CHANGED'"
        ).fetchone()
        self.assertEqual(row[0], "Neue Straße 9, 76133 Karlsruhe")


class RunScanGuardTest(unittest.TestCase):
    """Ein fehlgeschlagener oder leerer Scan darf die DB nie anfassen."""

    def setUp(self):
        self.tmpdir = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmpdir.cleanup)
        db_path = os.path.join(self.tmpdir.name, "restaurants.db")
        patcher = mock.patch.object(scanner, "DB_PATH", db_path)
        patcher.start()
        self.addCleanup(patcher.stop)
        # DB mit den Demodaten befüllen (10 Restaurants).
        with contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(scanner.run_scan("mock"), 0)

    def _snapshot(self):
        conn = sqlite3.connect(scanner.DB_PATH)
        try:
            rows = conn.execute(
                "SELECT place_id, active, last_seen FROM restaurants ORDER BY place_id"
            ).fetchall()
            changes = conn.execute("SELECT COUNT(*) FROM changes").fetchone()[0]
            return rows, changes
        finally:
            conn.close()

    def _run_full_expect_abort(self):
        before = self._snapshot()
        with contextlib.redirect_stdout(io.StringIO()), \
             contextlib.redirect_stderr(io.StringIO()):
            self.assertEqual(scanner.run_scan("full"), 1)
        self.assertEqual(self._snapshot(), before)

    def test_overpass_fehler_bricht_ab_und_laesst_db_unveraendert(self):
        with mock.patch.object(scanner, "fetch_overpass",
                               side_effect=RuntimeError("HTTP 504")):
            self._run_full_expect_abort()

    def test_leere_antwort_bricht_ab_und_laesst_db_unveraendert(self):
        with mock.patch.object(scanner, "fetch_overpass", return_value=([], 1)):
            self._run_full_expect_abort()

    def test_nur_unbrauchbare_objekte_brechen_ab(self):
        """Elemente ohne Name/Koordinaten zählen nicht als verwertbarer Scan."""
        elements = [{"type": "node", "id": 1, "lat": 49.0, "lon": 8.4, "tags": {}}]
        with mock.patch.object(scanner, "fetch_overpass",
                               return_value=(elements, 1)):
            self._run_full_expect_abort()


if __name__ == "__main__":
    unittest.main()
