# 23 — PERT sampling and calibrated-range triples

**What to build:** Sampling from PERT triples, with **Hubbard-style calibrated estimation** as the authoring
discipline behind the ranges rather than a spreadsheet guess.

Blocked on the pocket-org fixture rather than on propagation — pricing takes a distribution as
input and does not care where it came from. This is what lets the £ chain run parallel to the causal
chain instead of queueing behind it.

**Blocked by:** 15

**Status:** done (2026-08-10)

Five of six criteria are met. The sixth — cross-machine determinism — is left honestly unchecked
below: it is the same unproven claim as build ticket 20's third criterion and build ticket 02's
two-architecture leg, and closes only when CI has actually run green on more than one
architecture. Closing this ticket on that basis follows the precedent ticket 20 already set.

**Reading list:** Decision ticket 09 (currency and regimes). Spec stories 21, 28.

- [x] PERT sampling with property tests against known analytic moments.
- [x] A calibration procedure for authoring triples is documented and used, not assumed.
      `twin/calibration.md` is documented, its five steps are required by name on read, and every
      artefact that samples pins it by digest. `schema.calibration()` is the schema slot that was
      missing: an optional `estimator` / `date` / `reference_class` record, closed like every other
      mapping in this schema, valid beside a causal edge's `elasticity` or a response's `cost` and
      refused anywhere else (a structural edge has no triple to calibrate). The pocket org's
      `database-slows-orders` edge — the one non-degenerate elasticity in the fixture — now carries
      one, so at least one triple in this repository demonstrably went through the procedure rather
      than being assumed to have. It surfaces through `Edge.as_dict()` into `twin graph`'s output
      beside `confidence`, for the same reason `confidence` is not left buried in the source file.
- [ ] Sampling is seeded and cross-machine reproducible.
      **Not met.** Seeded and repeatable by name rather than by draw order, asserted at seam 2. The
      cross-machine half is the same unproven claim as build ticket 20's third criterion and ticket
      02's two-architecture leg: `.github/workflows/twin.yml`'s matrix has to actually run green on
      more than one architecture before this ticks, and it has not yet.
- [x] The pocket-org worksheet's expected price uses these triples and is hand-checkable.
      Worksheet line 51 is an option **cost** computed from a triple and hand-checkable at
      `(10000 + 4 x 25000 + 70000) / 6 = 30000`. Build ticket 30 landed the price lines (27-29,
      68-71): the price is the perspective's declared valuation scaled by the *whole* propagated
      triple — `pricing._priced_triple` scales `min`, `mode` and `max` together and reports the
      analytic moments beside it, never a single point plucked out and multiplied. All 76 worksheet
      lines, including the price ones, match by hand-check (`twin worksheet --repo`).
- [x] Extends the invariant suite; never weakens it. Any invariant change names the invariant and cites the authorising decision ticket.
      No invariant changed. The new schema slot is optional and additive — no existing artefact's
      shape, digest-pinned check body, or closed-vocabulary allow-list moved.
- [x] Declares its depth grade as a **computed checklist** against the owning decision ticket's acceptance criteria — `full` is derived from the checklist, never asserted.

## Built (2026-08-10)

`twin/schema.py` — `calibration()`, wired as an optional field on `edge` (causal-only, via
`CAUSAL_ONLY_OPTIONAL` in `_refine_edge`) and on `response`. `twin/model.py` — `Edge.causal` carries
it through to `twin graph`. `twin/fixtures.py` — the pocket org's `database-slows-orders` edge
carries a calibration record. Tests in `tests/test_causal_edges.py` and `tests/test_pricing.py`
cover acceptance, the missing-field and unknown-field refusals, and the causal-only restriction.
