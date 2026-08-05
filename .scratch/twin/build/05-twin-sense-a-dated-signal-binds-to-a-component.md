# 05 — `twin sense` — a dated signal binds to a component

**What to build:** The first verb, and the first vertical cut through the whole stack: a dated signal enters, is
bound to a component it touches, and a bound-signal artefact comes out of the CLI with its pins.

Deliberately **stub**-graded at every layer. The minimal schema this needs is the seed that ticket
12 formalises — do not attempt the real schema here, and do not let ticket 12 start before this
lands, or two contexts will author two schemas and the merge is a fight.

**Blocked by:** 04

**Status:** ready-for-agent

**Reading list:** Decision ticket 11 (sense-move loop). Spec stories 12, 15.

- [ ] A dated signal file in the repository binds to a named component and emits a bound-signal artefact.
- [ ] The binding is hand-authored as a grade-5 claim file — skills sit upstream of this seam, so from the CLI's view a skill's output is just a committed input.
- [ ] The artefact carries its pins and a stub depth grade.
- [ ] Golden-file test: the same repository ref produces the same artefact bytes.
- [ ] Extends the invariant suite; never weakens it. Any invariant change names the invariant and cites the authorising decision ticket.
- [ ] Declares its depth grade as a **computed checklist** against the owning decision ticket's acceptance criteria — `full` is derived from the checklist, never asserted.
