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

### Correction (review)

The paragraphs above overstate the diff and contradict themselves: they say "dropped the
`matchConditions` gate entirely" and "the policy now matches every pod", then separately claim
sub-question (1) — do unversioned/COTS workloads also default to baseline — "stays open". Both
cannot be true: a gate-less policy matching every pod has already answered "yes" for unversioned
workloads in code, whatever the prose says. Ticket 02 answer #5 is about a different question (does
an unversioned pod enter the *semver engine's corpus*), not about whether this admission-time
mutation touches it — conflating the two let the ticket claim a deferral the shipped code did not
make.

Fixed: `cage-tier.yaml` keeps a `matchConditions` gate, but scopes it on presence of
`policy-as-versioned.dev/policy-version` (`claims-a-policy-version`) rather than on presence of a
cage tier. This is the same self-scoping convention `../posture/policies/stamp-posture.yaml`
already uses for the same label, not a new pattern. Effect: every pod that claims a policy version
is caged (in-currency defaults to `baseline`, unchanged from above); a pod claiming no version at
all — kube-system, Kyverno's own pods, Flux's controllers, cert-manager, any COTS workload — is
unmatched, not caged. Sub-question (1) is now genuinely deferred to the COTS effort, because the
code, not just the comment, leaves that population untouched.

Added `unclaimed-system` to `tests/cage-tier/resources.yaml` — a pod with no
`policy-as-versioned.dev/policy-version` label at all (the `in-currency` fixture keeps that label,
so it was never a test of this path). Expected and confirmed `skip`. `kyverno test
estate/platform/graded/tests/cage-tier` is now 5/5 pass; `verify-graded.sh` still exits 0.

No live-cluster verification of cluster-critical pods was needed for this fix: the gate is a CEL
`matchConditions` expression on label presence, so kube-system/Kyverno/Flux/cert-manager pods are
structurally unmatched regardless of live state, the same way they were unmatched by the pre-ticket
`carries-a-cage-tier` gate. That guarantee held before this branch and holds after; only the *middle*
state (this branch prior to the fix, with no gate at all) put it at risk, and that state does not
ship.
