# 08 — Every workload is always caged, and the code disagrees

Type: task
Status: open
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
