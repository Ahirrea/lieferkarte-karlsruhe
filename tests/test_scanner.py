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
from tests.helpers import TS1, TS2, TS3, make_place, seed_db


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


class OsmCuisineTest(unittest.TestCase):
    """cuisine-Tag: Mehrfachwerte normalisieren, Müll verwerfen."""

    def test_einzelwert_wird_kleingeschrieben(self):
        self.assertEqual(scanner._osm_cuisine("Pizza"), "pizza")

    def test_mehrere_werte_bleiben_semikolon_getrennt(self):
        self.assertEqual(scanner._osm_cuisine("pizza;italian"), "pizza;italian")

    def test_leerzeichen_und_grossschreibung_werden_normalisiert(self):
        self.assertEqual(scanner._osm_cuisine(" Pizza ; Kebab "), "pizza;kebab")

    def test_komma_gilt_auch_als_trenner(self):
        self.assertEqual(scanner._osm_cuisine("burger, american"), "burger;american")

    def test_leerzeichen_und_bindestrich_werden_unterstrich(self):
        self.assertEqual(scanner._osm_cuisine("Ice Cream"), "ice_cream")
        self.assertEqual(scanner._osm_cuisine("coffee-shop"), "coffee_shop")

    def test_dubletten_fallen_weg_reihenfolge_bleibt(self):
        self.assertEqual(scanner._osm_cuisine("pizza;Pizza;italian"), "pizza;italian")

    def test_nichtssagende_werte_werden_verworfen(self):
        self.assertIsNone(scanner._osm_cuisine("yes"))
        self.assertEqual(scanner._osm_cuisine("yes;thai"), "thai")

    def test_ungetaggt_oder_leer_ist_none(self):
        self.assertIsNone(scanner._osm_cuisine(None))
        self.assertIsNone(scanner._osm_cuisine(""))
        self.assertIsNone(scanner._osm_cuisine(";;"))


class NormalizeOsmTest(unittest.TestCase):
    def test_node_mit_direkten_koordinaten(self):
        el = {"type": "node", "id": 12345, "lat": 49.01, "lon": 8.40,
              "tags": {"name": "Testpizzeria", "delivery": "yes",
                       "takeaway": "no", "opening_hours": "Mo-Su 11:00-22:00",
                       "cuisine": "Pizza;italian"}}
        norm = scanner.normalize_osm(el)
        self.assertEqual(norm["place_id"], "node/12345")
        self.assertEqual(norm["name"], "Testpizzeria")
        self.assertEqual(norm["lat"], 49.01)
        self.assertEqual(norm["lng"], 8.40)
        self.assertEqual(norm["delivery"], 1)
        self.assertEqual(norm["takeaway"], 0)
        self.assertEqual(norm["opening_hours"], "Mo-Su 11:00-22:00")
        self.assertEqual(norm["cuisine"], "pizza;italian")

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
        self.assertIsNone(norm["cuisine"])

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

    def _cuisine(self, pid):
        return self.conn.execute(
            "SELECT cuisine FROM restaurants WHERE place_id = ?", (pid,)
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

    def test_cuisine_wird_gespeichert_und_aktualisiert(self):
        scanner.sync_places(self.conn, [make_place("node/1", cuisine="pizza")],
                            "full", TS1)
        self.assertEqual(self._cuisine("node/1"), "pizza")
        scanner.sync_places(self.conn,
                            [make_place("node/1", cuisine="pizza;italian")],
                            "full", TS2)
        self.assertEqual(self._cuisine("node/1"), "pizza;italian")
        # Küchenstil ist bewusst kein Änderungstyp im Protokoll.
        types = [c[1] for c in self._changes()]
        self.assertEqual(types, ["NEW"])

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


class MigrationTest(unittest.TestCase):
    """Nachträglich ergänzte Spalten müssen in Alt-DBs eingezogen werden."""

    # Schema vor den Spalten takeaway/opening_hours/cuisine.
    ALT_SCHEMA = """
        CREATE TABLE restaurants (
            place_id        TEXT PRIMARY KEY,
            name            TEXT,
            address         TEXT,
            lat             REAL,
            lng             REAL,
            website         TEXT,
            delivery        INTEGER,
            business_status TEXT,
            active          INTEGER NOT NULL DEFAULT 1,
            first_seen      TEXT NOT NULL,
            last_seen       TEXT NOT NULL
        );
    """

    def test_alte_db_erhaelt_neue_spalten_und_bleibt_nutzbar(self):
        conn = sqlite3.connect(":memory:")
        self.addCleanup(conn.close)
        conn.executescript(self.ALT_SCHEMA)
        conn.execute(
            "INSERT INTO restaurants (place_id, name, first_seen, last_seen)"
            " VALUES ('node/alt', 'Altbestand', ?, ?)", (TS1, TS1))
        conn.commit()

        scanner.init_db(conn)
        cols = {row[1] for row in conn.execute("PRAGMA table_info(restaurants)")}
        self.assertLessEqual({"takeaway", "opening_hours", "cuisine"}, cols)

        # Nach der Migration lässt sich weiterhin scannen (inkl. cuisine).
        scanner.sync_places(conn, [make_place("node/1", cuisine="thai")], "light", TS2)
        self.assertEqual(
            conn.execute("SELECT cuisine FROM restaurants WHERE place_id='node/1'")
                .fetchone()[0],
            "thai",
        )


class RunScanGuardTest(unittest.TestCase):
    """Ein fehlgeschlagener oder leerer Scan darf die DB nie anfassen."""

    def setUp(self):
        self.tmpdir = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmpdir.cleanup)
        db_path = os.path.join(self.tmpdir.name, "restaurants.db")
        patcher = mock.patch.object(scanner, "DB_PATH", db_path)
        patcher.start()
        self.addCleanup(patcher.stop)
        # DB mit zehn Fixture-Restaurants befüllen (ohne Netz).
        seed_db(db_path, [make_place(f"node/{i}") for i in range(1, 11)])

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
