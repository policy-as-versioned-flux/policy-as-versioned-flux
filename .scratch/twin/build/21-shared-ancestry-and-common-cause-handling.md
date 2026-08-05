# 21 — Shared ancestry and common-cause handling

**What to build:** A common cause must not be double-counted. Two paths that share an ancestor are not two
independent pieces of evidence, and a system that treats them as such manufactures confidence
exactly where it is least warranted.

**Blocked by:** 20

**Status:** ready-for-agent

**Reading list:** Decision ticket 08. Spec story 25.

- [ ] Shared-ancestry detection over the propagation DAG.
- [ ] Seam-2 property test: **shared ancestry does not double-count** — a diamond structure yields strictly less combined influence than two independent paths of the same strength.
- [ ] The pocket-org worksheet gains a diamond and its hand-computed expected value.
- [ ] Copula or equivalent dependency handling is a declared, documented choice with its assumption stated, not an implicit independence.
- [ ] Extends the invariant suite; never weakens it. Any invariant change names the invariant and cites the authorising decision ticket.
- [ ] Declares its depth grade as a **computed checklist** against the owning decision ticket's acceptance criteria — `full` is derived from the checklist, never asserted.
