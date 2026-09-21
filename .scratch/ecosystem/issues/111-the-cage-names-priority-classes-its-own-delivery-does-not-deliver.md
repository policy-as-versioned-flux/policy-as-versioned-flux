# 111 — The cage names priority classes its own delivery does not deliver

Type: task
Status: open
Blocked by: none

## Question

Ticket 86 made the estate's most distinctive claim gradable, and the first citable score is a red.
That is the instrument working. This ticket owns the defect the instrument found, which until now
was named only in ticket 86's "not this ticket's" list and belonged to nobody.

The scheduled sample on driftwood, run 35507849200 of 2026-09-20T11:28:25Z, records:

```
fact_6_the_bottom_rung_is_admitted_and_runs   observed=False
  the cage REFUSED the workload: Error from server (Forbidden): error when creating "STDIN":
  pods "cage-probe" is forbidden: no PriorityClass with name cage-baseline-3-0-0 was found

fact_7_the_bottom_rung_reaches_nothing_...    observed=None
  fact 6 did not deliver a workload running on the cage's bottom rung, so there was nothing to
  measure reach from; fact 6 carries what happened to it
```

Fact 7's could-not-look is correct and is worth keeping: it refuses to grade reach from a workload
that never ran, and it says which fact carries the reason.

**The cause, measured.** Platform ships `priorityclasses.yaml` in every policy version directory it
publishes (v2.0.0, v2.0.1, v3.0.0, v4.0.0, v5.0.0 and vselfcheck; not v1.0.0). Every adopter's
composed tree drops it: `git ls-tree -r composed/` on driftwood's `origin/main` returns no priority
class object at all. Meanwhile the composed `cage-tier` sets `priorityClassName` from its own tier
dial, to one of `cage-baseline-4-0-0`, `cage-restricted-4-0-0`, `cage-quarantine-4-0-0` or
`cage-isolated-4-0-0`, and platform's own `priorityclasses.yaml` for that version defines exactly
those four names.

So the mutating cage writes a `priorityClassName` that nothing in the delivery creates, and the
Priority admission plugin refuses the pod. **A cage that cannot admit a workload is not a cage.**

This is not a probe artefact. It is the served composition, and it means no workload the cage
mutates can run on any adopter, which is a stronger statement than the sample makes.

## A second mismatch, not yet run to ground

The refusal names `cage-baseline-3-0-0`, a 3.0.0-era class, while driftwood's composed tree carries
`composed/policies/v4.0.0/` and nothing else. The Kustomizations the ResourceSet generates are
`composed-v2-0-0`, `composed-v2-0-1` and `composed-v3-0-0`, ranged from platform's declared version
array rather than from what the adopter composed. Establish whether the set of versions INSTALLED
and the set of versions COMPOSED can differ, and if they can, whether that is intended. Do not
assume the priority class fix settles it; a delivery that installs a version the adopter did not
compose is its own question.

## What has to be decided

1. **Who delivers the priority classes.** They are cluster-scoped objects shared across versions
   by name-per-version. Candidates: compose them into each adopter's tree like any other member;
   or deliver them from platform's own Kustomization as part of the engine rather than the policy
   set. Say which, and why the other is wrong, because this decides whether an adopter can install
   a policy version without the platform's cooperation.
2. **Whether the composition should have refused.** A composed set that names an object it does not
   carry is a hole the composer could see at compose time. If it can be caught there, it should be,
   and then this class of defect cannot reach a cluster again.
3. **What the fact should say while it is broken.** It currently reads false, which is right. Check
   nothing downstream reads that false as "the cage does not hold", because what it actually says
   is "the cage never got the chance".

Done = `fact_6` reads true on a scheduled sample for all three adopters, with the priority classes
delivered by whatever route decision 1 picks, and the composer refusing a set that names an object
it does not carry.

## Notes

Charted 2026-09-21. The defect was named in ticket 86's build as not that ticket's and had no owner;
the three adopters' `verify-reconcile.sh` rows and `verify/e2e/verify-e2e-step4-flux-reconciles-cage.sh`
are red on main today and this is what they are red about.

Ticket 86's own record should be read beside this: its first citable score being a red, in the API
server's own words, is what it predicted and is the outcome it asked to be judged by.

Record: ticket 86; ticket 26 (the cage ladder lands); ticket 63; platform
`distribution/policies/v*/priorityclasses.yaml`; each adopter's `composed/policies/v4.0.0/cage-tier.yaml`.
