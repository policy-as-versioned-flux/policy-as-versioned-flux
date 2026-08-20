# 08 — Every workload is always caged, and the code disagrees

Type: task
Status: done
Blocked by: 02

## Question

Settled in *What counts as a "verdict"*: there is no uncaged state. Every workload carries a cage
spec; the loosest is permissive; `deny` is the degenerate case where no satisfiable spec exists. The
semver engine compares **cage specs**, uniformly, across all workloads.

**The implementation contradicts this.** `estate/platform/graded/policies/cage-tier.yaml:41`:

> *"Only pods carrying a cage tier get caged. No tier => untouched (a pod in currency is never caged
> by this policy)."*

So in-currency workloads receive no cage spec at all — and they are precisely the population the
semver rule is about ("currently-compliant workloads"). The engine would be comparing *untouched*
against *untouched* for most of the corpus and seeing no movement where the model says there should
be a spec.

**The job:** make every workload carry a cage spec, with the loosest tier as the permissive default,
so the ladder is total rather than partial. `cage.py`'s `TIERS`/`ORDER` already provide the ladder;
what is missing is that `baseline` is never applied to a pod in currency.

**Know what this costs before doing it.** Applying a permissive baseline to everything newly stamps
`cpu: 500m`, `mem: 256Mi`, a `cage-baseline` priorityClass and a NetworkPolicy onto every currently-
passing pod. Under `CONTEXT.md`'s own rule that is capable of failing a previously-compliant workload
— a pod that cannot schedule under the new limits is refused — so **this change is itself a major
bump**, and it should be released as one. That recursion is a feature: the first real customer of the
computed-semver gate is this change.

Open sub-questions to settle while doing it: does the permissive baseline apply to unversioned
workloads too (interacts with the COTS effort), and does `select_tier` need a fifth, genuinely
no-op tier so that "permissive" and "baseline" are not conflated?

## Comments

Done. `estate/platform/graded/policies/cage-tier.yaml`: dropped the `carries-a-cage-tier`
`matchConditions` gate entirely (`resourceRules` already scopes to pods) and changed the `tier`
variable so a missing *or* unrecognized `posture.acme.io/tier` label both fall through to
`baseline` — the ladder `cage.py` already defines, unchanged. TDD: `tests/cage-tier/` updated first
(the `in-currency` pod moved from an expected `skip` to an expected `pass` patched into the
baseline dials, no self-asserted `tier` label added) — confirmed red against the old policy, then
green after the fix.

**This is a major bump, as flagged.** Every currently-passing, in-currency pod newly receives
`cpu: 500m` / `mem: 256Mi` limits and a `cage-baseline` PriorityClass. Under `CONTEXT.md`'s own
verdict-impact rule that is capable of turning an admitted-clean pod into a refused one (a pod that
cannot schedule under the new limits), so this policy body must release as **major**, not
patch/minor — the first real customer of the computed-semver gate this map is building.

Left open, as the ticket named them: (1) whether the permissive baseline should also apply to
unversioned/COTS workloads — spun out to its own effort per ticket 02's answer #5, so deliberately
not decided here; (2) a fifth, genuinely no-op tier distinct from `baseline` — not added, because
`baseline` *should* cost something for the recursion to be real (a no-op tier would let this ticket
dodge the major-bump consequence it exists to demonstrate). Both are recorded, neither is resolved.

Evidence: `estate/platform/graded/verify-graded.sh` (exit 0, step 2) and
`kyverno test estate/platform/graded/tests/cage-tier` (4/4 pass).
