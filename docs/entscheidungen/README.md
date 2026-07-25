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

## Neuen ADR anlegen

1. Nächste freie Nummer nehmen (dreistellig, `ADR-007`, …). Nummern werden nie
   wiederverwendet.
2. Datei nach dem Muster unten anlegen.
3. Zeile in der Tabelle oben ergänzen.
4. Kehrt der ADR eine frühere Entscheidung um: im alten ADR `Status:` auf
   `ersetzt durch ADR-<Nr>` setzen — das ist die **einzige** erlaubte Änderung an
   einem bestehenden ADR.

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
