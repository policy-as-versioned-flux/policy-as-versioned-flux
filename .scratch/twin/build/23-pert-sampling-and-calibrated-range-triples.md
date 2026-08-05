# 23 — PERT sampling and calibrated-range triples

**What to build:** Sampling from PERT triples, with **Hubbard-style calibrated estimation** as the authoring
discipline behind the ranges rather than a spreadsheet guess.

Blocked on the pocket-org fixture rather than on propagation — pricing takes a distribution as
input and does not care where it came from. This is what lets the £ chain run parallel to the causal
chain instead of queueing behind it.

**Blocked by:** 15

**Status:** ready-for-agent

**Reading list:** Decision ticket 09 (currency and regimes). Spec stories 21, 28.

- [ ] PERT sampling with property tests against known analytic moments.
- [ ] A calibration procedure for authoring triples is documented and used, not assumed.
- [ ] Sampling is seeded and cross-machine reproducible.
- [ ] The pocket-org worksheet's expected price uses these triples and is hand-checkable.
- [ ] Extends the invariant suite; never weakens it. Any invariant change names the invariant and cites the authorising decision ticket.
- [ ] Declares its depth grade as a **computed checklist** against the owning decision ticket's acceptance criteria — `full` is derived from the checklist, never asserted.
