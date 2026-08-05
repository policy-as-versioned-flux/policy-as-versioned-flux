# 20 — Monte-Carlo propagation, depth attenuation, and the seam-2 harness

**What to build:** Propagation of a signal's consequences through the graph by Monte-Carlo, with **depth attenuation**
so a long chain does not manufacture confidence.

**Seam 2 is established here.** The spec names three test seams and this is the one whose absence is
most dangerous: a propagation defect and a graph-validation defect are indistinguishable at seam 1 —
both surface as "wrong number" — and the Monte-Carlo layer is where a silent statistical error is
most likely and least visible. The harness is deliberately thin: assertions on **numerical and
structural properties**, never on call sequences or object shapes, because code here is disposable
and a test coupled to internals becomes the sunk cost that resists the rewrite.

**Blocked by:** 17, 15

**Status:** ready-for-agent

**Reading list:** Decision ticket 08. Spec: Testing Decisions, seam 2. Spec stories 25, 35.

- [ ] Monte-Carlo composition through typed edges with seeded reproducibility.
- [ ] Seam-2 property test: **attenuation reduces influence with depth**, asserted as a monotonic property across depths rather than a fixed number.
- [ ] Cross-machine determinism holds for the seeded sampler (the ticket-02 two-machine check covers this path).
- [ ] The pocket-org worksheet's propagated influence matches, by hand-check.
- [ ] The seam-2 harness exists as a named boundary that tickets 21 and 22 extend.
- [ ] Extends the invariant suite; never weakens it. Any invariant change names the invariant and cites the authorising decision ticket.
- [ ] Declares its depth grade as a **computed checklist** against the owning decision ticket's acceptance criteria — `full` is derived from the checklist, never asserted.
