# A-5 Pins nach Zustand unterscheiden (R13)

[← Anforderungen](./README.md) · [Prozess](../PROZESS.md)
· Status siehe [Übersicht](./README.md#übersicht)

**User Story:** Als Nutzerin möchte ich auf der Karte sehen, welche Restaurants liefern, abholen lassen oder gerade geschlossen sind, ohne jeden Pin antippen zu müssen.

**Verfeinert am:** — (noch nicht verfeinert, Ausgangstext unten)
**Bedient PRD:** „Kernschleife" Schritt 1
**Eingeschränkt durch:** hängt an [A-1](./A-1-standardfilter-entschaerfen.md)

## Ausgangstext (aus `backlog/IDEEN.md`, Idee 5)

Ob ein Restaurant liefert, abholen lässt oder gerade geschlossen ist, sieht man
erst nach dem Antippen. Farb- oder Formcodierung (z. B. blass = jetzt
geschlossen) bringt viel pro Blick. Hängt an
**[A-1](./A-1-standardfilter-entschaerfen.md)**: erst mit entschärftem
Standardfilter lohnt die Unterscheidung wirklich, und erst dann steht fest, welche
Zustände überhaupt nebeneinander vorkommen.

Braucht außerdem [A-4](./A-4-farbsystem.md): solange `--accent` vier Bedeutungen
trägt, ist keine Farbe für „Zustand" frei.

---

> **Noch nicht verfeinert.** Der Abschnitt oben ist der unveränderte Ausgangstext
> aus `backlog/IDEEN.md` (Idee 5) — Bestandsaufnahme, Optionen, Entscheidungen
> und Definition of Done fehlen noch. Der Weg dorthin steht in
> [`PROZESS.md`](../PROZESS.md), der Slash-Command `/anforderung` fährt ihn. Die
> Kürzel `R…`/`P…` stammen aus dem UI/UX-Review vom Juli 2026 (Mobil-Screenshot,
> Android/Chrome, 1080 × 2340) und bleiben erhalten, damit Rückfragen zuordenbar sind.
