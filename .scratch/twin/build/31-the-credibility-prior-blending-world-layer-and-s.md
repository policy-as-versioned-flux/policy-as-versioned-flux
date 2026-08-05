# 31 — The credibility prior: blending world layer and sparse overlay

**What to build:** **Bühlmann–Straub credibility theory**: the industry prior lives in the world layer, sparse
own-data lives in the overlay, and the blend gives a thinly-evidenced org a defensible prior rather
than either a fabricated number or nothing.

This is the capability the world/overlay split exists to enable, and an earlier draft delivered the
split without ever delivering the blend.

**Blocked by:** 4, 23

**Status:** ready-for-agent

**Reading list:** Decision tickets 07, 09; research 02. Spec story 5.

- [ ] Credibility weighting implemented with property tests: weight on own-data rises with own-data volume and falls with own-data variance.
- [ ] An org with no own-data prices from the world prior alone, and says so.
- [ ] The blend is visible in the artefact — which component of the estimate came from where.
- [ ] Re-estimating as own-data accumulates is a normal operation, not a re-authoring.
- [ ] Extends the invariant suite; never weakens it. Any invariant change names the invariant and cites the authorising decision ticket.
- [ ] Declares its depth grade as a **computed checklist** against the owning decision ticket's acceptance criteria — `full` is derived from the checklist, never asserted.
