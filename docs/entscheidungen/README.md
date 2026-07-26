# Entscheidungen (ADRs)

Architektur- und Grundsatzentscheidungen, je Entscheidung eine Datei
(`ADR-<Nr>-<kurz-titel>.md`). Dieser Ordner ist **append-only**: ein ADR wird
nie umgeschrieben. Kehrt eine Entscheidung sich um, entsteht ein **neuer** ADR
und der alte bekommt `Status: ersetzt durch ADR-<Nr>`. So bleibt nachvollziehbar,
was wann warum galt.

Ein ADR entsteht, wenn eine Entscheidung die Architektur ändert oder das Projekt
langfristig bindet (Schritt 5 des [Prozesses](../PROZESS.md)). Weichen innerhalb
einer einzelnen Anforderung bleiben in der Anforderungsdatei.

## Übersicht

| Nr. | Entscheidung | Status | Kern |
|---|---|---|---|
| [ADR-001](./ADR-001-openstreetmap-statt-google-places.md) | OpenStreetMap über Overpass statt Google Places | akzeptiert | Googles Bedingungen verbieten genau das Repo-Modell (speichern, weitergeben, außerhalb einer Google-Karte zeigen). Die ODbL erlaubt es — gegen Pflicht-Attribution. |
| [ADR-002](./ADR-002-kein-backend-daten-im-repo.md) | Kein Backend — DB und JSON ins Repo committen | akzeptiert | Eine wöchentliche Action spielt Server. Null Kosten, kein Ort für Nutzerdaten, und die Git-Historie der DB *ist* das Änderungsprotokoll. |
| [ADR-003](./ADR-003-scan-darf-db-nie-leeren.md) | Ein leerer/fehlgeschlagener Scan darf die DB nie leeren | akzeptiert | Voll-Scan erkennt Entfernungen durch Abwesenheit — also bricht der Scanner bei null Treffern ab, und `--light` markiert bewusst kein `REMOVED`. |
| [ADR-004](./ADR-004-oeffnungszeiten-eigener-parser.md) | Öffnungszeiten: eigener Mini-Parser, fest Europe/Berlin | akzeptiert | Konservativ: unsicher → „unbekannt", nie → „geöffnet". Ein falsches „jetzt offen" schickt jemanden vor eine verschlossene Tür. |
| [ADR-005](./ADR-005-cuisine-nicht-protokollieren.md) | Küchenstil-Änderungen werden nicht protokolliert | akzeptiert | Eine neue Spalte erzeugt beim ersten Scan Massen-Ereignisse (245 × `TAKEAWAY_CHANGED`). Der Feed soll Neuigkeiten zeigen, keine Datenlage. |
| [ADR-006](./ADR-006-pwa-network-first.md) | PWA: `restaurants.json` immer network-first | akzeptiert | Die Daten werden wöchentlich ersetzt. Cache ist reiner Offline-Fallback und wird als solcher gekennzeichnet. `CACHE_VERSION` hochzählen, kein `skipWaiting()`. |
| [ADR-007](./ADR-007-standardfilter-liefert-jetzt.md) | Standardfilter ist „Liefert jetzt" | akzeptiert | Die Karte ist ein Jetzt-Werkzeug, kein Verzeichnis: Default = liefert **und** jetzt geöffnet. Der enge Default ist gewollt — dafür sind Leerzustand und Zurücksetzen-Chip Pflicht. |
| [ADR-008](./ADR-008-karte-im-vollbild-overlay-und-sheets.md) | Karte im Vollbild — Bedienung als Overlay und Bottom Sheets | akzeptiert | Unter 640 px liegt die Bedienung über der Karte statt darüber im Fluss. Vollbild endet, wo die ODbL-Attribution beginnt: die Fußzeile bleibt unverdeckt. Wird mit [A-3](../anforderungen/A-3-header-umbau.md) akzeptiert. |
| [ADR-009](./ADR-009-farbrollen-marke-aktion-zustand.md) | Farbrollen getrennt — Marke, Interaktion, Zustand | akzeptiert | `--accent` trug fünf Rollen. Jetzt drei Token-Ebenen, kein Farbwert außerhalb `:root`, „geschlossen" ist Slate statt Rot. Farbe trägt den Zustand, das Symbol die Fähigkeit — und nie Farbe allein (Rot/Grün liegen 1,03 auseinander). Mit [A-4](../anforderungen/A-4-farbsystem.md) gebaut. |
| [ADR-010](./ADR-010-pin-grammatik-lieferung-und-geschlossen.md) | Pin-Grammatik — Farbe trägt die Lieferung, Größe das „jetzt geschlossen" | ersetzt durch [ADR-011](./ADR-011-pins-wieder-einheitlich.md) | Zwei Achsen auf dem Pin, mehr nicht: Farbe + Strichart = Lieferung (unbekannt gestrichelt), Größe + Füllstärke = sicher geschlossen. Der Umriss bleibt voll deckend, weil „blass" allein 2,59:1 erreicht. Abholung bleibt beim Chip. Mit [A-5](../anforderungen/A-5-pins-nach-zustand.md) gebaut — und am selben Tag zurückgenommen. Die Messwerte bleiben gültig, die Entscheidung nicht. |
| [ADR-011](./ADR-011-pins-wieder-einheitlich.md) | Pins tragen wieder keinen Zustand — zurück zum Leaflet-Standard-Icon | akzeptiert | Kehrt ADR-010 um: die Kreise sahen schlechter aus, und im Standardbild sind ohnehin alle 53 Pins gleich (aufgeweitet 774 von 885 „unbekannt"). Zustände bleiben in Popup, Badges und Filtern; R13 wandert zu [A-2](../anforderungen/A-2-ergebnisliste.md). Die Pin-Achsen sind **geschlossen**, nicht frei. |

## Neuen ADR anlegen

1. Nächste freie Nummer nehmen (dreistellig, `ADR-007`, …). Nummern werden nie
   wiederverwendet.
2. Datei nach dem Muster unten anlegen.
3. Zeile in der Tabelle oben ergänzen.
4. Kehrt der ADR eine frühere Entscheidung um: im alten ADR `Status:` auf
   `ersetzt durch ADR-<Nr>` setzen.
5. **Nur der `Status:` darf sich je ändern, der Text nie.** Erlaubt sind genau
   zwei Übergänge: `vorgeschlagen` → `akzeptiert`, sobald die Entscheidung
   umgesetzt ist, und `akzeptiert` → `ersetzt durch ADR-<Nr>`. Ein ADR darf
   `vorgeschlagen` sein, wenn die Entscheidung getroffen, die beschriebene
   Lösung aber noch nicht gebaut ist.

## Aufbau

```markdown
# ADR-<Nr>: <Titel>

**Status:** vorgeschlagen | akzeptiert | ersetzt durch ADR-<Nr>
**Datum:** <Datum>

## Kontext
<Welche Kräfte wirken? Was war die Ausgangslage?>

## Entscheidung
<Was wird getan — im Aktiv, ein Satz.>

## Begründung
<Warum diese und nicht die Alternativen.>

## Verworfene Alternativen
<je Alternative ein Satz, warum nicht.>

## Konsequenzen
<Was folgt daraus, auch das Unangenehme. Was darf jetzt nicht mehr passieren?>
```

> ADR-001 bis ADR-003 waren bis 2026-07-25 nur als Prosa-Abschnitte in `CLAUDE.md`
> („Constraints that drive the design") festgehalten, ADR-004 bis ADR-006 steckten
> in den „Der Haken"-Absätzen von [`UMGESETZT.md`](../UMGESETZT.md). Die Quelltexte
> sind dort unverändert erhalten.
