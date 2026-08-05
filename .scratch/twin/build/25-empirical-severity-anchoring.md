# 25 — Empirical severity anchoring

**What to build:** Anchor the severity distributions to real evidence — Cyentia IRIS, Verizon DBIR-class sources —
so the parameters are defensible rather than illustrative. Separated from ticket 24 because the
implementation and the empirical work are different jobs and each needs its window.

**Blocked by:** 24

**Status:** ready-for-agent

**Reading list:** Decision ticket 09; research 02. Spec story 28.

- [ ] Named public sources with dated citations for each anchored parameter.
- [ ] Anchoring is a versioned artefact, so a re-anchoring is a visible change.
- [ ] Where no defensible anchor exists, the parameter is marked as unanchored rather than quietly assumed.
- [ ] Sensitivity of the headline outputs to each anchor is reported.
- [ ] Extends the invariant suite; never weakens it. Any invariant change names the invariant and cites the authorising decision ticket.
- [ ] Declares its depth grade as a **computed checklist** against the owning decision ticket's acceptance criteria — `full` is derived from the checklist, never asserted.
