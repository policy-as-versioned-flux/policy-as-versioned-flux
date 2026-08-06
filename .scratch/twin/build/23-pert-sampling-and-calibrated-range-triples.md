# 23 — PERT sampling and calibrated-range triples

**What to build:** Sampling from PERT triples, with **Hubbard-style calibrated estimation** as the authoring
discipline behind the ranges rather than a spreadsheet guess.

Blocked on the pocket-org fixture rather than on propagation — pricing takes a distribution as
input and does not care where it came from. This is what lets the £ chain run parallel to the causal
chain instead of queueing behind it.

**Blocked by:** 15

**Status:** partial (2026-08-06)

Three of six criteria are met: the sampler, its analytic-moment property tests, and the
worksheet line that costs an option from a triple. Three are not, and each names why above.
The ticket is **not** closed, because closing it would make "a calibration procedure, used"
mean "a calibration procedure, filed".

**Reading list:** Decision ticket 09 (currency and regimes). Spec stories 21, 28.

- [x] PERT sampling with property tests against known analytic moments.
- [ ] A calibration procedure for authoring triples is documented and used, not assumed.
      **Half met.** `twin/calibration.md` is documented, its five steps are required by name on read,
      and every artefact that samples pins it by digest. Nothing records an estimator, a date or a
      reference class against a triple, so no triple in this repository has demonstrably been through
      the procedure and none can be. The "used" half needs a schema slot that does not exist.
- [ ] Sampling is seeded and cross-machine reproducible.
      **Half met.** Seeded and repeatable by name rather than by draw order, asserted at seam 2. The
      cross-machine half is the same unproven claim as build ticket 20's third criterion.
- [ ] The pocket-org worksheet's expected price uses these triples and is hand-checkable.
      **Partly met.** Worksheet line 51 is an option **cost** computed from a triple and hand-checkable
      at `(10000 + 4 x 25000 + 70000) / 6 = 30000`. The expected **price** lines (27-29) are still
      pending on build ticket 30 and compose by point estimate, which is the move this ticket rejects.
- [x] Extends the invariant suite; never weakens it. Any invariant change names the invariant and cites the authorising decision ticket.
- [x] Declares its depth grade as a **computed checklist** against the owning decision ticket's acceptance criteria — `full` is derived from the checklist, never asserted.
