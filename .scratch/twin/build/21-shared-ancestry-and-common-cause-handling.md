# 21 — Shared ancestry and common-cause handling

**What to build:** A common cause must not be double-counted. Two paths that share an ancestor are not two
independent pieces of evidence, and a system that treats them as such manufactures confidence
exactly where it is least warranted.

**Blocked by:** 20

**Status:** done (2026-08-07)

All six criteria are met. Dependence is carried **structurally** rather than by a fitted copula: a
shared edge is drawn once per Monte-Carlo trial, so two paths agree exactly to the extent that they
share edges. Paths are combined by noisy-OR, never added, and the combined figure is emitted beside
the `if_independent` one so the discount is a subtraction rather than a claim. Two limits are
stated in the artefact rather than left implied: a common cause the **graph does not contain** is
not corrected, and the exact inclusion-exclusion form stops at ten paths per component, past which
the figure is sampled only.

**Review found the combined figure had no sign, and the golden worksheet was certifying a wrong
number because of it.** The pocket-org diamond's two routes carried opposite directions — two
negative hops compose to positive, three compose to negative — and noisy-OR on their magnitudes
reported them as reinforcing. Two fixes, because either alone would have hidden the other. The
combined figure now carries a `sign`, and routes that disagree are **not combined at all**:
netting them would subtract and combining them would claim they reinforce, so each path is
reported with its own direction and no single magnitude is invented. And the fixture's second leg
is now positive, so the diamond composes coherently and still has a shared edge to discount.

**Mutation review found the sampled half was unasserted.** The test that claimed to check "the
sampler really does draw a common cause once" compared the sampled mean to the exact one at 2%
tolerance, while the dependence moves that mean by 0.2% — so reverting to per-path independent
sampling passed every test in the repository except the golden-digest tripwire, which gets
re-blessed on any deliberate change. Two replacements, both tolerance-free: on a graph where the
shared edge is the only source of width, the sampled mean must sit **nearer the dependent figure
than the independent one**; and the sampled mean of a diamond must be below that of a disjoint
pair with identical marginals. Three more mutations that used to survive now fail — a hardcoded
directional count, an off-by-one on the exact-form bound, and the bound's last inclusive case.

**It contributes nothing to decision ticket 08 AC 4, and the first draft of this note claimed
otherwise.** Q5's free structural check is a **confounder detector**: shared ancestors of a causal
edge's *two endpoints*, surfacing as candidate common causes. What is built is shared-*edge*
detection among the paths from one origin to one component, which is a path-dependence correction
and a different thing. Nothing in `twin/` computes common ancestors of an edge's endpoints. AC 4
stays unchecked, `causal-layer` stands at 1/5, and the confounder detector is still to build.

The field is named `shares_ancestry` and it is true when two paths share an **edge**. Every pair
of paths shares the origin by construction, and two paths can share an intermediate node without
sharing an edge; neither case reports true. The name is broader than what it measures.

**Reading list:** Decision ticket 08. Spec story 25.

- [x] Shared-ancestry detection over the propagation DAG.
- [x] Seam-2 property test: **shared ancestry does not double-count** — a diamond structure yields strictly less combined influence than two independent paths of the same strength.
- [x] The pocket-org worksheet gains a diamond and its hand-computed expected value.
- [x] Copula or equivalent dependency handling is a declared, documented choice with its assumption stated, not an implicit independence.
- [x] Extends the invariant suite; never weakens it. `no_collapse_mechanism` is strengthened:
      the combined figure is the first aggregate here that could stand in for what it aggregates,
      so every path is asserted to survive beside it. Any invariant change names the invariant and cites the authorising decision ticket.
- [x] Declares its depth grade as a **computed checklist** against the owning decision ticket's acceptance criteria — `full` is derived from the checklist, never asserted.
