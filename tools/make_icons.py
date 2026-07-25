#!/usr/bin/env python3
"""Lieferkarte Karlsruhe – App-Icons erzeugen (PWA).

Schreibt die Icons für Manifest, Homescreen und Favicon nach ``web/icons/``.
Bewusst **nur Standardbibliothek** (``zlib``/``struct``) – wie der Rest der
Pipeline soll das Projekt ohne Installation von Paketen laufen. Deshalb wird
das Icon hier geometrisch gezeichnet (Teller + Besteck in der Projektfarbe)
statt aus einer Vorlage skaliert.

Aufruf (nur nötig, wenn sich das Icon-Design ändert – die PNGs liegen im Repo):

    python3 tools/make_icons.py

Kantenglättung über 3x3-Supersampling; Ausgabe ist RGBA-PNG.
"""

import os
import struct
import sys
import zlib

OUT_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                       "web", "icons")

# Projektfarben (identisch zu den CSS-Variablen in web/index.html)
# ACHTUNG: --marke ist an vier Orten gekoppelt und nur gemeinsam änderbar –
# hier, in :root von web/index.html und web/datenschutz.html, in
# manifest.theme_color und in den drei theme-color-Metas. Eine Änderung heißt
# außerdem Icons neu generieren; tests/test_pwa.py prüft den Gleichlauf.
ACCENT = (0xD6, 0x45, 0x41)   # --marke
CREAM = (0xFF, 0xFF, 0xFF)    # Teller/Besteck
BG_LIGHT = (0xF7, 0xF7, 0xF5)  # --bg (Apple-Touch-Icon-Rand)

SUPERSAMPLE = 3

# ---------------------------------------------------------------------------
# Geometrie (Einheitsquadrat 0..1, Ursprung oben links)
# ---------------------------------------------------------------------------
# Alle Formen werden um die Mitte mit `scale` gestaucht. Maskierbare Icons
# (Android) bekommen einen kleineren Wert, damit das Motiv auch nach dem
# Zuschneiden auf einen Kreis (Safe Zone = mittlere 80 %) vollständig sichtbar
# bleibt.

PLATE_OUTER = 0.205   # Teller: Außenradius
PLATE_INNER = 0.135   # Teller: Innenradius (ergibt den weißen Ring)

FORK_X = 0.175        # Gabel links
KNIFE_X = 0.825       # Messer rechts
CUTLERY_TOP = 0.255
CUTLERY_BOTTOM = 0.755


def _rounded_rect(x, y, x0, y0, x1, y1, r):
    """Punkt-in-Rechteck mit runden Ecken."""
    if x < x0 or x > x1 or y < y0 or y > y1:
        return False
    r = min(r, (x1 - x0) / 2, (y1 - y0) / 2)
    cx = min(max(x, x0 + r), x1 - r)
    cy = min(max(y, y0 + r), y1 - r)
    return (x - cx) ** 2 + (y - cy) ** 2 <= r * r


def _circle(x, y, cx, cy, r):
    return (x - cx) ** 2 + (y - cy) ** 2 <= r * r


def _fork(x, y):
    """Gabel: drei Zinken, Kopfstück, Griff."""
    w = 0.030                       # Zinkenbreite
    for dx in (-0.042, 0.0, 0.042):
        if _rounded_rect(x, y, FORK_X + dx - w / 2, CUTLERY_TOP,
                         FORK_X + dx + w / 2, 0.415, w / 2):
            return True
    # Kopfstück, das die Zinken verbindet
    if _rounded_rect(x, y, FORK_X - 0.072, 0.375, FORK_X + 0.072, 0.455, 0.028):
        return True
    # Griff
    return _rounded_rect(x, y, FORK_X - 0.032, 0.43, FORK_X + 0.032,
                         CUTLERY_BOTTOM, 0.032)


def _knife(x, y):
    """Messer: Klinge (oben breiter) + Griff."""
    if _rounded_rect(x, y, KNIFE_X - 0.055, CUTLERY_TOP, KNIFE_X + 0.055,
                     0.50, 0.05):
        return True
    return _rounded_rect(x, y, KNIFE_X - 0.032, 0.47, KNIFE_X + 0.032,
                         CUTLERY_BOTTOM, 0.032)


def _sample(x, y, maskable, opaque_bg):
    """Farbe (r, g, b, a) an der Stelle (x, y) im Einheitsquadrat."""
    if maskable:
        # Volle Fläche: das Betriebssystem schneidet die Form selbst zu.
        inside_bg = True
        scale = 0.78
    else:
        inside_bg = _rounded_rect(x, y, 0.0, 0.0, 1.0, 1.0, 0.22)
        scale = 1.0

    if not inside_bg:
        # Außerhalb: bei Apple-Touch-Icons (kein Alphakanal erwünscht) hell
        # füllen, sonst transparent lassen.
        return (*BG_LIGHT, 255) if opaque_bg else (0, 0, 0, 0)

    # Motiv um die Mitte skalieren
    mx = 0.5 + (x - 0.5) / scale
    my = 0.5 + (y - 0.5) / scale

    if _circle(mx, my, 0.5, 0.5, PLATE_OUTER):
        # Teller als Ring: innen wieder Akzentfarbe
        if _circle(mx, my, 0.5, 0.5, PLATE_INNER):
            return (*ACCENT, 255)
        return (*CREAM, 255)
    if _fork(mx, my) or _knife(mx, my):
        return (*CREAM, 255)
    return (*ACCENT, 255)


def render(size, maskable=False, opaque_bg=False):
    """Icon rendern -> Liste von Zeilen mit RGBA-Bytes."""
    rows = []
    n = SUPERSAMPLE
    step = 1.0 / (size * n)
    for py in range(size):
        row = bytearray()
        for px in range(size):
            r = g = b = a = 0
            for sy in range(n):
                y = (py * n + sy + 0.5) * step
                for sx in range(n):
                    x = (px * n + sx + 0.5) * step
                    cr, cg, cb, ca = _sample(x, y, maskable, opaque_bg)
                    # Vormultipliziert mitteln, damit Kanten nicht ausbleichen.
                    r += cr * ca
                    g += cg * ca
                    b += cb * ca
                    a += ca
            total = n * n
            if a == 0:
                row += b"\x00\x00\x00\x00"
            else:
                row += bytes((round(r / a), round(g / a), round(b / a),
                              round(a / total)))
        rows.append(bytes(row))
    return rows


def write_png(path, rows):
    """Minimaler PNG-Writer (RGBA, 8 Bit, Filter 0)."""
    height = len(rows)
    width = len(rows[0]) // 4
    raw = b"".join(b"\x00" + row for row in rows)

    def chunk(tag, data):
        payload = tag + data
        return (struct.pack(">I", len(data)) + payload
                + struct.pack(">I", zlib.crc32(payload) & 0xFFFFFFFF))

    png = b"\x89PNG\r\n\x1a\n"
    png += chunk(b"IHDR", struct.pack(">IIBBBBB", width, height, 8, 6, 0, 0, 0))
    png += chunk(b"IDAT", zlib.compress(raw, 9))
    png += chunk(b"IEND", b"")

    with open(path, "wb") as fh:
        fh.write(png)
    return len(png)


# name, Größe, maskable, deckender Hintergrund
ICONS = [
    ("icon-192.png", 192, False, False),
    ("icon-512.png", 512, False, False),
    ("icon-maskable-192.png", 192, True, False),
    ("icon-maskable-512.png", 512, True, False),
    # iOS maskiert selbst und mag keine Transparenz -> volle Fläche, kein Alpha.
    ("apple-touch-icon.png", 180, True, True),
    ("favicon-32.png", 32, False, False),
]


def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    for name, size, maskable, opaque_bg in ICONS:
        path = os.path.join(OUT_DIR, name)
        written = write_png(path, render(size, maskable, opaque_bg))
        print(f"Geschrieben: {os.path.relpath(path)} ({size}x{size}, {written} Bytes)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
