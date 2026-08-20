# 02 — What counts as a "verdict", given Audit is not a pass

Type: grilling
Status: resolved
Blocked by: none

## Question

`CONTEXT.md` defines the bump by "verdict impact on currently-compliant workloads", and its own
examples show the verdict space is **not binary**:

- a new **`Audit`** policy is **minor** — it cannot fail a compliant workload, but it does newly
  *report* on it;
- an **`Audit` → `Deny` promotion** is **major** — the workload's admission outcome flips.

So a workload has at least three states — admitted-clean, admitted-but-reported, refused — and the
bump depends on which transition occurred, in which direction.

**Decide:**

1. **The verdict lattice.** What are the states, and which transitions are major / minor / patch?
   Admitted→refused is clearly major. Admitted-clean→admitted-reported is the "new Audit policy"
   minor. What about refused→admitted (a widening — patch by the rule, since the passing set grows)?
   What about reported→clean?
2. **Whose compliance counts.** The rule says *currently-compliant* workloads. Is a workload that is
   admitted-but-reported "compliant"? If yes, a new Audit rule on it is minor; if no, the same change
   reads as major. `CONTEXT.md`'s own example says minor — confirm that is the intent and record it.
3. **Unversioned and out-of-scope workloads.** A pod claiming no version, or a version outside the
   supported window, is judged by nothing. Does it enter the corpus at all, and does an
   out-of-scope→in-scope change count as a verdict move?

The answers become the engine's core semantics, so they need to be explicit before anything is built.

## Answer

Resolved by grilling, 2026-08-20. The owner reframed the model twice, and both reframes are better
than the question asked.

**1. Compliant means *admitted*.** `CONTEXT.md` already forces this: **minor** is "an addition that
cannot **fail** an existing compliant workload (e.g. a new `Audit` policy)". An Audit rule that fires
does not fail the workload — it is admitted and reported on. The alternative reading, that reported
means non-compliant, would make every new Audit policy a **major** bump and collapse the lane-keeping
half of the thesis into the gate. Record it explicitly in `CONTEXT.md`; it is currently only
inferable.

**2. There is no separate "refused" verdict class — refusal is the bottom rung.** Owner: *"the pod
stopping is just the implementation of the incoming policy because it does not fit in an available
cage, the cluster nodes cannot support the pod spec."* Confirmed in code: `cage.py`'s
`select_tier(uncaged_ale, tolerance)` walks `ORDER = [baseline, restricted, quarantine]` picking the
loosest cage whose residual fits the band, and returns `deny` only "when even the tightest cage leaves
a residual over the band". Deny is rung four, and the whole ladder is a pure function of
(residual, band).

**3. Every workload is always caged — the *spec of the cage* is what changes.** Owner: *"you're
always caged even if it's a permissive one. It's the spec of the cage that can change."* So there is
no uncaged state and no "clean" rung; the loosest cage is permissive, and `deny` is the degenerate
case where no satisfiable spec exists. What the engine compares is therefore **the cage spec a
workload receives under each version**, uniformly, rather than a verdict enum.

**This is a change, not a description — and the code says so.** `estate/platform/graded/policies/
cage-tier.yaml:41` states: *"Only pods carrying a cage tier get caged. No tier => untouched (a pod in
currency is never caged by this policy)."* Today in-currency workloads are genuinely uncaged, so
there is no spec to compare for exactly the population the semver rule is about. Raised as its own
ticket, with the recursion noted there: adopting always-caged would newly stamp limits, a
priorityClass and a netpol onto every currently-passing pod — **a major bump under the rule this map
is building.**

**4. The bump is institution-relative, and is tagged at worst case.** The rung is chosen against the
consuming org's appetite band, so one version can land a workload on `baseline` at driftwood (£40k)
and `deny` at ludlow (£5k). Semver is a property of the artefact, not the consumer, so: **compute
against the strictest band in the estate and tag that**, and publish the per-institution matrix as
the supporting evidence a reviewer sees on the Renovate PR. Same disease and same cure as the
multi-org map's finding that the forward layer hardcodes a single institution.

**5. Unversioned workloads are a permanent population, not an edge case** — owner: *"there'll always
be COTS products that we must facilitate and support, it won't all be custom build"*, reached via a
policy-dependency shim at the infra decision point, or by policy describing them. Too large for this
map and it changes what "verdict" even means for that population. **Spun out as its own effort** by
the owner's instruction; recorded as a named dependency of the corpus ticket.
