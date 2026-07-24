# Datenschutz & Hinweise

Dies ist ein **privates, nicht-kommerzielles Projekt**. Es werden keine
personenbezogenen Daten erhoben, gespeichert oder verarbeitet.

## Datenschutz auf einen Blick

- **Keine Cookies** – weder notwendige noch optionale.
- **Kein Tracking, keine Analyse, keine Werbung.**
- **Keine Formulare, keine Datenerfassung, keine serverseitige Speicherung.**
- Die Seite ist statisch (GitHub Pages) und läuft ohne eigenen Backend-Server.

## Geolocation ("In meiner Nähe")

Wenn du den Browser-Button "In meiner Nähe" nutzt:

- Deine Position wird **nur lokal im Browser** verwendet.
- Sie wird **nicht** an einen Server übertragen.
- Sie wird **nicht** gespeichert.
- Der Browser fragt vorher um Erlaubnis – du kannst ablehnen.

## App-Installation & Offline-Nutzung (PWA)

Die Seite kann als App zum Homescreen hinzugefügt werden. Dafür läuft ein
**Service Worker** im Browser, der Karte, Icons und die Restaurantdaten im
lokalen Browser-Speicher (Cache Storage) ablegt – damit die Karte auch ohne Netz
funktioniert.

- Der Cache liegt **ausschließlich auf deinem Gerät**; es wird nichts an einen
  Server übertragen.
- **Keine Cookies, kein Local-Storage-Profil, keine Kennung** – gespeichert
  werden nur die abgerufenen Dateien selbst.
- Die Restaurantdaten werden immer zuerst frisch geladen; die Kopie aus dem
  Cache kommt nur zum Einsatz, wenn kein Netz verfügbar ist (dann erscheint ein
  Hinweis mit dem Datenstand).
- Bereits angezeigte Kartenkacheln werden begrenzt zwischengespeichert
  (max. 400), damit unterwegs weniger Daten nötig sind. Es wird nichts auf
  Vorrat heruntergeladen.
- Der Cache lässt sich jederzeit löschen: App bzw. Verknüpfung entfernen oder in
  den Browser-Einstellungen die Websitedaten löschen.

## Externe Inhalte

### OpenStreetMap
- **Was:** Restaurantdaten (Name, Adresse, Lieferstatus) **und** Kartenkacheln
- **Betreiber:** OpenStreetMap Foundation
- **Lizenz der Daten:** ODbL (Open Database License)
- **Datenschutzerklärung:** https://wiki.openstreetmap.org/wiki/Privacy_Policy

Die Restaurantdaten werden vorab per Overpass-API abgerufen und statisch
ausgeliefert – beim Aufruf der Seite findet dazu **kein** Live-Request an OSM
statt. Beim Nachladen der Kartenkacheln können die OSM-Tile-Server (wie bei
jeder Kartenbibliothek) technische Zugriffsdaten wie die IP-Adresse erfassen.

## Haftung für Inhalte

Die Inhalte werden mit Sorgfalt gepflegt, ohne Gewähr für Vollständigkeit,
Richtigkeit oder Aktualität. Das gilt besonders für den Lieferstatus, der
automatisiert aus OpenStreetMap übernommen wird und nur so vollständig ist,
wie es die OSM-Community erfasst hat. Für aktuelle Informationen bitte direkt
beim jeweiligen Restaurant nachfragen.

## Externe Links

Diese Seite verlinkt zu Restaurant-Websites. Für den Inhalt fremder Seiten wird
keine Verantwortung übernommen.

## Datenquelle & Attribution

- Restaurantdaten & Kartenkacheln: © OpenStreetMap-Mitwirkende (Lizenz: ODbL)
- Kartensoftware: Leaflet (BSD-2-Clause)

## Fehler melden

Falscher Liefer- oder Abholstatus? Im Popup jedes Restaurants gibt es
**„⚑ Falsche Angabe melden"**. Ein Klick auf **„Text kopieren & OSM-Notiz
öffnen"** legt einen fertigen Meldetext in die **Zwischenablage** (rein lokal
im Browser – die Lieferkarte speichert oder überträgt dabei nichts) und öffnet
den Notiz-Editor von OpenStreetMap. Dort den Text einfügen und absenden – ein
**OSM-Konto ist nicht nötig**. Die OSM-Community pflegt die Korrektur ein, und
beim nächsten wöchentlichen Abgleich übernimmt die Lieferkarte sie automatisch.

Der OSM-Notiz-Editor ist eine externe Seite der OpenStreetMap Foundation mit
eigener [Datenschutzerklärung](https://wiki.openstreetmap.org/wiki/Privacy_Policy).
Alternativ kannst du eine Angabe auch direkt in
[OpenStreetMap](https://www.openstreetmap.org) korrigieren.
