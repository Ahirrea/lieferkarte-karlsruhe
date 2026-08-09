# Domain Docs

How the engineering skills should consume this repo's domain documentation when
exploring the codebase. This repo is **single-context**.

## Before exploring, read these

- **`docs/PRD.md`** — goals and, more importantly, **non-goals**. An idea that
  touches a non-goal is not dead, but the conflict has to be named explicitly.
- **`docs/entscheidungen/`** — the ADRs. This repo keeps them here, **not** in
  `docs/adr/`. Read the ones that touch the area you are about to work in.
- **`docs/TECHNICAL.md`** — the implementation spec (DB schema, Overpass query,
  change-detection rules). Read it, and verify against the actual files, before
  changing pipeline code.
- **`CONTEXT.md`** at the repo root, if it exists.

If any of these files don't exist, **proceed silently**. Don't flag their
absence; don't suggest creating them upfront. The `/domain-modeling` skill
creates them lazily when terms or decisions actually get resolved.

## File structure

```
/
├── CLAUDE.md                     ← constraints that drive the design
├── docs/
│   ├── PRD.md                    ← why & what, incl. non-goals
│   ├── PROZESS.md                ← idea → refined requirement
│   ├── TECHNICAL.md              ← implementation spec
│   ├── entscheidungen/           ← ADRs, append-only
│   │   ├── README.md             ← overview table, carries each ADR's status
│   │   └── ADR-<NNN>-<slug>.md
│   ├── anforderungen/            ← requirements (see issue-tracker.md)
│   ├── BACKLOG.md                ← tasks (see issue-tracker.md)
│   └── UMGESETZT.md              ← what shipped, and why that way
```

## `docs/entscheidungen/` is append-only

The prose of an ADR is **never rewritten**. The only permitted edits are status
transitions: `vorgeschlagen` → `akzeptiert` once the decision is built, or
`ersetzt durch ADR-<Nr>` when a later ADR reverses it. Reversing a decision means
writing a **new** ADR, not editing the old one — `ADR-011` reversing `ADR-010` is
the worked example.

An ADR's status lives in **two** places: the `Status:` header inside the file and
its row in `docs/entscheidungen/README.md`. Check and update both — they have
drifted apart before.

## Write an ADR when

The decision changes the architecture or binds the project long-term
(`docs/PROZESS.md`, step 5). A decision taken **against** the requirement's own
recommendation gets documented, not smoothed over: record the choice *and* the
rejected recommendation.

## Use the project's vocabulary

The project and all its docs are German. When your output names a domain concept,
use the term the docs use — `Lieferung` / `Abholung` / „jetzt geöffnet",
`Anforderung` vs. `Aufgabe`, `unbekannt` (never „nein" for a `null` tag). Code
identifiers follow the existing docs (`sync_places`, `normalize_osm`,
`fetch_overpass`).

If the concept you need isn't documented yet, that's a signal — either you're
inventing language the project doesn't use (reconsider) or there's a real gap
(note it for `/domain-modeling`).

## Flag ADR conflicts

If your output contradicts an existing ADR, surface it explicitly rather than
silently overriding:

> _Widerspricht ADR-011 (einheitliche Pins) — aber es lohnt sich, das wieder zu
> öffnen, weil …_
