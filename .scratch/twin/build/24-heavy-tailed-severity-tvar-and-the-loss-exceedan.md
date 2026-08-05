# 24 — Heavy-tailed severity, TVaR, and the loss-exceedance curve

**What to build:** Lognormal body with a Pareto/GPD tail, **TVaR rather than VaR**, and loss-exceedance curves as the
output shape.

TVaR not VaR is load-bearing: VaR tells you the threshold and says nothing about what lies beyond
it, which is the entire region a risk engine exists to reason about. This is also one of the two
hardest tickets in the plan and gets a window to itself for that reason.

**Blocked by:** 23

**Status:** ready-for-agent

**Reading list:** Decision ticket 09; research 02 (risk and threat SOTA). Spec: Out of Scope (why TabFM was rejected — a single-scalar regression head cannot express this, and ±4σ clipping amputates exactly this tail).

- [ ] Lognormal body + GPD tail composition with the threshold-selection method declared.
- [ ] TVaR implemented with property tests, including behaviour at the shape-parameter boundary where the mean stops existing.
- [ ] Loss-exceedance curve as an artefact type.
- [ ] A test demonstrating that a VaR-shaped summary would have hidden a tail this correctly surfaces.
- [ ] Extends the invariant suite; never weakens it. Any invariant change names the invariant and cites the authorising decision ticket.
- [ ] Declares its depth grade as a **computed checklist** against the owning decision ticket's acceptance criteria — `full` is derived from the checklist, never asserted.
