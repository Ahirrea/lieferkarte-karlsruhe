"""Tests für die PWA-Dateien (Manifest, Icons, Service Worker).

Nur Standardbibliothek (unittest). Rein lesend – es werden keine Dateien
erzeugt oder verändert; die Icons liegen fertig im Repo (erzeugt mit
``tools/make_icons.py``).

Abgesichert werden genau die Fehler, die man am Schreibtisch nicht sieht,
sondern erst als „Installieren"-Button, der nie erscheint:
Manifest kaputt/unvollständig, Icon-Datei fehlt oder hat eine andere Größe als
angegeben, Service Worker cacht eine Datei, die es nicht gibt.
"""

import json
import os
import re
import struct
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WEB = os.path.join(ROOT, "web")
MANIFEST = os.path.join(WEB, "manifest.webmanifest")
SW = os.path.join(WEB, "sw.js")
INDEX = os.path.join(WEB, "index.html")


def read(path):
    with open(path, encoding="utf-8") as fh:
        return fh.read()


def png_size(path):
    """Breite/Höhe aus dem IHDR-Chunk lesen (ohne Fremdbibliothek)."""
    with open(path, "rb") as fh:
        header = fh.read(24)
    if header[:8] != b"\x89PNG\r\n\x1a\n":
        raise ValueError(f"{path}: keine PNG-Datei")
    if header[12:16] != b"IHDR":
        raise ValueError(f"{path}: IHDR fehlt")
    return struct.unpack(">II", header[16:24])


class ManifestTest(unittest.TestCase):
    def setUp(self):
        self.manifest = json.loads(read(MANIFEST))

    def test_pflichtfelder_fuer_installierbarkeit(self):
        for key in ("name", "short_name", "start_url", "scope", "display",
                    "theme_color", "background_color", "icons"):
            self.assertIn(key, self.manifest)
        self.assertEqual(self.manifest["display"], "standalone")
        # Relative Pfade: die Seite liegt unter /<repo>/web/ auf GitHub Pages,
        # absolute Pfade würden dort ins Leere zeigen.
        self.assertTrue(self.manifest["start_url"].startswith("./"))
        self.assertTrue(self.manifest["scope"].startswith("./"))

    def test_icons_vorhanden_und_in_angegebener_groesse(self):
        for icon in self.manifest["icons"]:
            path = os.path.join(WEB, icon["src"])
            self.assertTrue(os.path.isfile(path), f"Icon fehlt: {icon['src']}")
            width, height = png_size(path)
            self.assertEqual(f"{width}x{height}", icon["sizes"],
                             f"{icon['src']}: Größe weicht vom Manifest ab")
            self.assertEqual(icon["type"], "image/png")

    def test_android_braucht_192_und_512_sowie_maskable(self):
        sizes = {i["sizes"] for i in self.manifest["icons"]}
        self.assertIn("192x192", sizes)
        self.assertIn("512x512", sizes)
        maskable = {i["sizes"] for i in self.manifest["icons"]
                    if i.get("purpose") == "maskable"}
        self.assertIn("512x512", maskable)

    def test_shortcut_ziele_existieren(self):
        for shortcut in self.manifest.get("shortcuts", []):
            page = shortcut["url"].split("?")[0]
            self.assertTrue(os.path.isfile(os.path.join(WEB, page)),
                            f"Shortcut zeigt auf fehlende Datei: {page}")
            for icon in shortcut.get("icons", []):
                self.assertTrue(os.path.isfile(os.path.join(WEB, icon["src"])),
                                f"Shortcut-Icon fehlt: {icon['src']}")

    def test_theme_color_passt_zum_meta_tag_der_seite(self):
        html = read(INDEX)
        meta = re.search(r'<meta name="theme-color" content="([^"]+)"', html)
        self.assertIsNotNone(meta, "theme-color-Meta-Tag fehlt in index.html")
        self.assertEqual(meta.group(1), self.manifest["theme_color"])


class ServiceWorkerTest(unittest.TestCase):
    def setUp(self):
        self.sw = read(SW)

    def test_gecachte_eigene_dateien_existieren(self):
        # Alle "./..."-Pfade in sw.js müssen im web/-Verzeichnis liegen,
        # sonst schlägt cache.addAll() fehl und die Installation bricht ab.
        paths = set(re.findall(r'"\./([^"]*)"', self.sw))
        self.assertTrue(paths, "keine Precache-Pfade in sw.js gefunden")
        for rel in paths:
            if rel == "":
                continue  # "./" = index.html (vom Server geliefert)
            self.assertTrue(os.path.isfile(os.path.join(WEB, rel)),
                            f"sw.js cacht eine fehlende Datei: {rel}")

    def test_cache_version_gesetzt(self):
        self.assertRegex(self.sw, r'const CACHE_VERSION = "v\d+"')

    def test_daten_werden_nicht_aus_dem_cache_bevorzugt(self):
        # Die wöchentlich neuen Daten müssen "network first" laufen, sonst
        # zeigt die installierte App dauerhaft alte Restaurants.
        self.assertIn("dataNetworkFirst", self.sw)
        self.assertIn("restaurants.json", self.sw)

    def test_kein_automatisches_skip_waiting_beim_installieren(self):
        # skipWaiting darf nur auf Nachricht der Seite passieren (Update-Hinweis),
        # nicht ungefragt im install-Handler.
        install = self.sw.split('addEventListener("install"')[1]
        install = install.split('addEventListener("activate"')[0]
        self.assertNotIn("skipWaiting", install)
        self.assertIn("SKIP_WAITING", self.sw)

    def test_kachel_cache_ist_begrenzt(self):
        # Rücksicht auf die kostenlosen OSM-Tile-Server und den Gerätespeicher.
        self.assertRegex(self.sw, r"const MAX_TILES = \d+")
        self.assertIn("trimCache", self.sw)


class IndexHtmlTest(unittest.TestCase):
    def setUp(self):
        self.html = read(INDEX)

    def test_manifest_und_icons_verlinkt(self):
        self.assertIn('<link rel="manifest" href="manifest.webmanifest">', self.html)
        self.assertIn('rel="apple-touch-icon"', self.html)
        self.assertIn('rel="icon"', self.html)

    def test_service_worker_wird_registriert(self):
        self.assertIn('navigator.serviceWorker.register("sw.js")', self.html)

    def test_verlinkte_lokale_dateien_existieren(self):
        for rel in re.findall(r'(?:href|src)="((?!https?:|//|#|mailto:)[^"]+)"',
                              self.html):
            # Template-Literale aus dem Popup-JS (`href="${…}"`) überspringen –
            # geprüft werden nur die statisch verlinkten Dateien.
            if "${" in rel:
                continue
            path = os.path.join(WEB, rel.split("?")[0])
            self.assertTrue(os.path.isfile(path), f"index.html verlinkt fehlende Datei: {rel}")


if __name__ == "__main__":
    unittest.main()
