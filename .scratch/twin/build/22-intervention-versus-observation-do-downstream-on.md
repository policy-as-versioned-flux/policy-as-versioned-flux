# 22 — Intervention versus observation: `do()` downstream-only

**What to build:** **Observation propagates bidirectionally; intervention propagates downstream only.** Learning a
fact updates beliefs everywhere, including about causes. *Doing* a thing does not rewrite its own
causes. This is Pearl's `do()` and it is not a nicety — a system that lets an intervention
back-propagate will cheerfully conclude that taking an action changed the past.

**Blocked by:** 20

**Status:** done (2026-08-07)

All six criteria are met. `Do` and `Observe` are separate frozen types in `twin/primitives.py`;
`severed()` accepts only the first and `updated_beliefs()` only the second, so a swap is a `mypy`
error, and `tests/test_primitives.py` runs the type checker on a deliberate swap rather than
asserting that it would fail. The runtime refusal is kept as well, for a caller that reaches past
the type checker through `Any`, and the emitted intervention is refused outright if it carries any
upstream belief update.

An updated ancestor carries **no magnitude**, deliberately. An authored elasticity is
`d(target)/d(cause)`; inverting it into a diagnostic number needs a prior over the causes that
nothing in this model authors, so an observation names, grades and locates the ancestor and stops
there. That is a refusal, not a gap.

**Mutation review found the upstream walk barely exercised.** Every `observe()` test used
`order-service`, whose single ancestor sits one hop away — so the weakest grade equalled the
strongest, no cycle existed and the default depth was never approached. Three defects passed
unnoticed: `min` where `max` belongs, a cycle guard that only refused to revisit the observed
component, and a depth bound of one. One test on a four-hop chain with two cycles, one of them
never touching the target, kills all three. The emission guard was unwired-able too — deleting
its call left everything green, because nothing reachable through the public API can violate it —
so the harness check now asserts the call site as well as the function.

The type-error test used to `importorskip("mypy")`, which meant this ticket's third criterion
silently declined to run wherever the type checker was absent. It hard-fails now, because
`twin/invariants/__init__.py` says a guard that quietly declines reads as green.

Decision ticket 08 AC 2 stays unchecked. Intervention semantics and structural-only behaviour are
built; the **counterfactual** is abduction to action to prediction, and prediction (fast-forward)
is build ticket 37. Two thirds of a composition is not the composition.

**Reading list:** Decision ticket 08. Spec story 18.

- [x] `do()` and `observe()` are separate operations with different propagation semantics.
- [x] Seam-2 property test: **`do()` leaves upstream beliefs untouched while `observe()` updates them**.
- [x] An attempt to use one where the other is meant is a type error, not a runtime surprise.
- [x] The pocket-org worksheet gains one of each and their differing expected outcomes.
- [x] Extends the invariant suite; never weakens it. Any invariant change names the invariant and cites the authorising decision ticket.
- [x] Declares its depth grade as a **computed checklist** against the owning decision ticket's acceptance criteria — `full` is derived from the checklist, never asserted.
