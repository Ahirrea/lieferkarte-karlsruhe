/* Lieferkarte Karlsruhe – Service Worker.
 *
 * Zweck: Die Seite lässt sich zum Homescreen hinzufügen (PWA) und funktioniert
 * auch offline bzw. bei wackeligem Netz. Es wird ausschließlich **gecacht** –
 * kein Tracking, keine Analyse, keine Übertragung von Nutzerdaten. Alles bleibt
 * im Browser (Cache Storage) und lässt sich dort jederzeit löschen.
 *
 * Update-Strategie (wichtig, weil die Daten wöchentlich neu sind):
 *   - restaurants.json  -> "network first": immer erst das Netz fragen, damit
 *     der Sonntags-Scan sofort ankommt; nur ohne Netz kommt die Kopie aus dem
 *     Cache (die Seite zeigt dann einen Hinweis mit dem Datenstand).
 *   - HTML/Manifest     -> "network first" mit Cache-Fallback, damit neue
 *     Versionen der Seite nicht hinter einem alten Cache hängen bleiben.
 *   - Icons/Leaflet     -> "cache first" (versionierte bzw. stabile Dateien).
 *   - Kartenkacheln     -> "cache first" mit Obergrenze (siehe MAX_TILES);
 *     schon besuchte Kacheln kommen aus dem Cache, es wird nichts auf Vorrat
 *     heruntergeladen (Rücksicht auf die kostenlosen OSM-Tile-Server).
 *   - Neue Worker-Version: kein automatisches skipWaiting. Der neue Worker
 *     wartet, die Seite zeigt „Neue Version verfügbar" an und erst ein Klick
 *     schaltet um (Nachricht SKIP_WAITING) – so wird nie mitten im Betrieb
 *     die halbe Seite ausgetauscht.
 *
 * Bei Änderungen an den gecachten Dateien CACHE_VERSION erhöhen – dadurch
 * werden die alten Caches beim Aktivieren aufgeräumt.
 */

const CACHE_VERSION = "v6";
const SHELL_CACHE = `lieferkarte-shell-${CACHE_VERSION}`;
const DATA_CACHE = `lieferkarte-data-${CACHE_VERSION}`;
const TILE_CACHE = `lieferkarte-tiles-${CACHE_VERSION}`;
const CACHES = [SHELL_CACHE, DATA_CACHE, TILE_CACHE];

// Maximale Anzahl gecachter Kartenkacheln (grob ~10–15 MB).
const MAX_TILES = 400;

// Eigene Dateien – müssen vorhanden sein, sonst schlägt die Installation fehl.
const SHELL_FILES = [
  "./",
  "./index.html",
  "./datenschutz.html",
  "./manifest.webmanifest",
  "./icons/favicon-32.png",
  "./icons/apple-touch-icon.png",
  "./icons/icon-192.png",
  "./icons/icon-512.png",
  "./icons/icon-maskable-192.png",
  "./icons/icon-maskable-512.png",
];

// Daten der Karte – gehören in den Daten-Cache (eigene Update-Strategie).
const DATA_FILE = "./restaurants.json";

// Fremddateien (Leaflet vom CDN, inkl. Marker-Grafiken). "Best effort":
// scheitert der Abruf, wird die Installation trotzdem abgeschlossen.
// Die drei Marker-Grafiken müssen mit: die Pins sind seit ADR-011 wieder
// Leaflets Standard-Icon (L.marker), und ohne sie bliebe die Karte offline
// pinlos – die cacheFirst-Regel für unpkg würde sie erst online nachholen.
const CDN_FILES = [
  "https://unpkg.com/leaflet@1.9.4/dist/leaflet.css",
  "https://unpkg.com/leaflet@1.9.4/dist/leaflet.js",
  "https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png",
  "https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon-2x.png",
  "https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png",
];

const TILE_HOST_RE = /(^|\.)tile\.openstreetmap\.org$/;
const CDN_HOST = "unpkg.com";

// ---------------------------------------------------------------------------
// Installieren: Shell + Daten vorab in den Cache legen (offline lauffähig).
// ---------------------------------------------------------------------------
self.addEventListener("install", (event) => {
  event.waitUntil((async () => {
    const shell = await caches.open(SHELL_CACHE);
    await shell.addAll(SHELL_FILES);

    // Restaurantdaten und CDN-Dateien einzeln und fehlertolerant nachladen –
    // ein einzelner Fehler (z. B. CDN kurz weg) darf die Installation nicht
    // scheitern lassen; zur Laufzeit wird sowieso nachgecacht.
    const data = await caches.open(DATA_CACHE);
    await cacheQuietly(data, [DATA_FILE]);
    await cacheQuietly(shell, CDN_FILES);
  })());
});

async function cacheQuietly(cache, urls) {
  await Promise.all(urls.map(async (url) => {
    try {
      const res = await fetch(url, { cache: "no-cache", credentials: "omit" });
      if (res && res.ok) await cache.put(url, res);
    } catch (err) {
      /* offline oder CDN nicht erreichbar – wird zur Laufzeit nachgeholt */
    }
  }));
}

// ---------------------------------------------------------------------------
// Aktivieren: alte Cache-Versionen entfernen und sofort die Kontrolle
// übernehmen (der Wechsel selbst wird von der Seite ausgelöst, s. u.).
// ---------------------------------------------------------------------------
self.addEventListener("activate", (event) => {
  event.waitUntil((async () => {
    const names = await caches.keys();
    await Promise.all(
      names
        .filter((n) => n.startsWith("lieferkarte-") && !CACHES.includes(n))
        .map((n) => caches.delete(n))
    );
    await self.clients.claim();
  })());
});

// Die Seite bittet um den Versionswechsel („Neu laden"-Hinweis).
self.addEventListener("message", (event) => {
  if (event.data && event.data.type === "SKIP_WAITING") self.skipWaiting();
});

// ---------------------------------------------------------------------------
// Anfragen abfangen
// ---------------------------------------------------------------------------
self.addEventListener("fetch", (event) => {
  const req = event.request;
  if (req.method !== "GET") return;

  const url = new URL(req.url);
  if (url.protocol !== "http:" && url.protocol !== "https:") return;

  const sameOrigin = url.origin === self.location.origin;

  // Kartenkacheln: erst Cache, dann Netz (mit Obergrenze).
  if (TILE_HOST_RE.test(url.hostname)) {
    event.respondWith(tileFirst(req));
    return;
  }

  // Leaflet vom CDN: stabile, versionierte URLs -> Cache zuerst.
  if (url.hostname === CDN_HOST) {
    event.respondWith(cacheFirst(req, SHELL_CACHE));
    return;
  }

  if (!sameOrigin) return; // alles Übrige (z. B. Restaurant-Websites) durchlassen

  // Restaurantdaten: immer erst das Netz (wöchentlich neue Daten).
  if (url.pathname.endsWith("/restaurants.json")) {
    event.respondWith(dataNetworkFirst(req));
    return;
  }

  // Seitenaufrufe und übrige eigene Dateien: Netz zuerst, Cache als Rückfall.
  event.respondWith(shellNetworkFirst(req));
});

// --- Strategien -------------------------------------------------------------

async function shellNetworkFirst(request) {
  const cache = await caches.open(SHELL_CACHE);
  try {
    const res = await fetch(request);
    if (res && res.ok) cache.put(request, res.clone()).catch(() => {});
    return res;
  } catch (err) {
    // Offline: Kopie aus dem Cache. `ignoreSearch`, damit auch Aufrufe mit
    // Parametern (z. B. index.html?open=1 aus einer App-Verknüpfung) greifen.
    const hit = await cache.match(request, { ignoreSearch: true });
    if (hit) return hit;
    if (request.mode === "navigate") {
      const fallback = await cache.match("./index.html");
      if (fallback) return fallback;
    }
    throw err;
  }
}

async function dataNetworkFirst(request) {
  const cache = await caches.open(DATA_CACHE);
  try {
    // `cache: "no-store"` setzt bereits die Seite – hier nur weiterleiten.
    const res = await fetch(request);
    if (res && res.ok) cache.put(DATA_FILE, res.clone()).catch(() => {});
    return res;
  } catch (err) {
    const hit = await cache.match(DATA_FILE, { ignoreSearch: true });
    if (!hit) throw err;
    // Markierung, damit die Seite „Offline – Daten vom …" anzeigen kann.
    const headers = new Headers(hit.headers);
    headers.set("X-Lieferkarte-Cache", "hit");
    return new Response(await hit.blob(), {
      status: 200,
      statusText: "OK (Cache)",
      headers,
    });
  }
}

async function cacheFirst(request, cacheName) {
  const cache = await caches.open(cacheName);
  const hit = await cache.match(request);
  if (hit) return hit;
  const res = await corsFetch(request);
  if (res && res.ok) cache.put(request, res.clone()).catch(() => {});
  return res;
}

async function tileFirst(request) {
  const cache = await caches.open(TILE_CACHE);
  const hit = await cache.match(request);
  if (hit) return hit;
  const res = await corsFetch(request);
  if (res && res.ok) {
    cache.put(request, res.clone())
      .then(() => trimCache(cache, MAX_TILES))
      .catch(() => {});
  }
  return res;
}

// Kacheln und CDN-Dateien werden von Leaflet teils als `no-cors` angefragt;
// solche Antworten sind „opaque" und lassen sich schlecht cachen. Beide Server
// erlauben CORS, deshalb hier bewusst als CORS-Anfrage holen – und nur im
// Fehlerfall auf die Originalanfrage zurückfallen.
async function corsFetch(request) {
  if (request.mode !== "no-cors") return fetch(request);
  try {
    const res = await fetch(request.url, { mode: "cors", credentials: "omit" });
    if (res && res.ok) return res;
  } catch (err) {
    /* fällt unten auf die Originalanfrage zurück */
  }
  return fetch(request);
}

// Ältesten Einträge zuerst löschen (cache.keys() liefert in Einfügereihenfolge).
async function trimCache(cache, maxEntries) {
  const keys = await cache.keys();
  if (keys.length <= maxEntries) return;
  await Promise.all(
    keys.slice(0, keys.length - maxEntries).map((k) => cache.delete(k))
  );
}
