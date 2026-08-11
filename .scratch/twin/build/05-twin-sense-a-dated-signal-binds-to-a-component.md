# 05 — `twin sense` — a dated signal binds to a component

**What to build:** The first verb, and the first vertical cut through the whole stack: a dated signal enters, is
bound to a component it touches, and a bound-signal artefact comes out of the CLI with its pins.

Deliberately **stub**-graded at every layer. The minimal schema this needs is the seed that ticket
12 formalises — do not attempt the real schema here, and do not let ticket 12 start before this
lands, or two contexts will author two schemas and the merge is a fight.

**Blocked by:** 04

**Status:** done (2026-08-05)

**Reading list:** Decision ticket 11 (sense-move loop). Spec stories 12, 15.

- [x] A dated signal file in the repository binds to a named component and emits a bound-signal artefact.
- [x] The binding is hand-authored as a grade-5 claim file — skills sit upstream of this seam, so from the CLI's view a skill's output is just a committed input.
- [x] The artefact carries its pins and a stub depth grade.
- [x] Golden-file test: the same repository ref produces the same artefact bytes.
- [x] Extends the invariant suite; never weakens it. Any invariant change names the invariant and cites the authorising decision ticket.
- [x] Declares its depth grade as a **computed checklist** against the owning decision ticket's acceptance criteria — `full` is derived from the checklist, never asserted.

## Built (2026-08-05)

`twin/verbs.py` `sense()`.

- A dated, STEEP-tagged, provenanced signal binds to a component through a **committed grade-5 claim
  file**. A claim at any other grade is refused: skills sit upstream of this seam, so from the CLI's
  point of view a skill's output is just input.
- An unbound signal does not sense — it errors rather than emitting an artefact with nothing in it.
- Bindings are emitted as a **list**, even though the ticket says "a component", for the same reason
  forecasts are.

The depth grade is computed rather than typed, and lands at `stub` — which is what this ticket asks for,
arrived at by the checklist rather than by assertion. It reads `stub` because `domain-model` has 0 of 7
criteria ticked, not because anyone wrote the word.

Added after review: a signal now has an enforced schema (dated, STEEP-classed, sourced, provenanced) and
a binding claim below grade 5 is refused. Both were conventions of the fixture before, which is not the
same as a property of the system — a mutation review deleted the grade-5 refusal and the whole suite
stayed green.
