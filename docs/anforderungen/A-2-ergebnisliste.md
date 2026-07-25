# A-2 Ergebnisliste neben der Karte (R6)

[← Anforderungen](./README.md) · [Prozess](../PROZESS.md)
· Status siehe [Übersicht](./README.md#übersicht)

**User Story:** Als Nutzerin mit Screenreader oder Tastatur möchte ich die Restaurants auch als Liste erreichen, um die Karte nicht bedienen zu müssen.

**Verfeinert am:** — (noch nicht verfeinert, Ausgangstext unten)
**Bedient PRD:** „Ziele" — im eigenen Umkreis suchbar
**Eingeschränkt durch:** —

## Ausgangstext (aus `backlog/IDEEN.md`, Idee 2)

Die Karte ist für Tastatur und Screenreader leer: die `L.marker(…)` tragen kein
`alt`/`title`, die Popup-Inhalte existieren nur im Marker. Vorschlag: dieselben
gefilterten Daten zusätzlich als schlichte `<ul>` unter bzw. neben der Karte.
Löst gleichzeitig „was ist in der Nähe?" und macht „In meiner Nähe" nach
Entfernung sortierbar. Offen ist die Struktur – wo die Liste sitzt und ob sie
auf Mobil einklappbar ist.

---

> **Noch nicht verfeinert.** Der Abschnitt oben ist der unveränderte Ausgangstext
> aus `backlog/IDEEN.md` (Idee 2) — Bestandsaufnahme, Optionen, Entscheidungen
> und Definition of Done fehlen noch. Der Weg dorthin steht in
> [`PROZESS.md`](../PROZESS.md), der Slash-Command `/anforderung` fährt ihn. Die
> Kürzel `R…`/`P…` stammen aus dem UI/UX-Review vom Juli 2026 (Mobil-Screenshot,
> Android/Chrome, 1080 × 2340) und bleiben erhalten, damit Rückfragen zuordenbar sind.
