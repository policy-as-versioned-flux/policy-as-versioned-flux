# 52 — The planter/detector/scorer split and actionability horizons

**What to build:** An **enforced** separation between what plants a signal, what detects it, and what scores the
detection — with its limits stated plainly: shared model priors mean synthetic results evidence
**detection mechanics only**, never anticipation of the world.

Every plant carries an **actionability horizon**, so detection after the point of no return scores as
the near-zero option value it actually is. Finding it late is not finding it.

**Blocked by:** 51

**Status:** ready-for-agent

**Reading list:** Decision ticket 12. Spec stories 58, 59.

- [ ] Planter, detector and scorer cannot share state; the split is structural, not procedural.
- [ ] The shared-prior limitation is published with the results, every time, not in a footnote.
- [ ] Every plant carries an actionability horizon; detection is scored against it.
- [ ] A late detection scores near zero and the scoring makes the reason visible.
- [ ] Extends the invariant suite; never weakens it. Any invariant change names the invariant and cites the authorising decision ticket.
- [ ] Declares its depth grade as a **computed checklist** against the owning decision ticket's acceptance criteria — `full` is derived from the checklist, never asserted.
