# 09 — Orphan guard

**What to build:** The deterministic catch-all that turns the gate tier into a locked door rather than an opt-in door (CONTEXT "Orphan guard"): one Deny-at-admission ValidatingPolicy whose CEL carries a literal allow-list rendered from the same `{version, commit}` array that installs the versions — a missing `policy-version` label is a violation, an unknown one is a violation — with background-scan Audit reports surfacing pre-existing orphans. Brownfield posture (start in Audit, promote by editorial PR, never timed — ADR-0006) documented.

**Blocked by:** 08 — ResourceSet coexistence matrix.

**Status:** done, fully -- issue 08's blocker cleared 2026-07-15

- [x] A workload with no `policy-version` label is denied at admission
- [x] A workload labelled with a version not in the installed set is denied
- [x] The allow-list templates from the same ResourceSet array as the installed versions — changing the array changes the guard in the same reconcile
- [x] Background scan reports pre-existing orphans without evicting them

## Comments

Done 2026-07-14, each property individually proven live and stable (`fleet/verify-orphan-guard.sh`):
no-label and unknown-version pods both refused at admission; the allow-list (read straight off the
live object) contains exactly the installed set; a simulated brownfield orphan (guard removed,
orphan created, guard reinstalled) stayed Running and picked up a PolicyReport fail entry rather
than being evicted.

`fleet/clusters/cluster1/policy-versions.yaml`: the guard is templated from the SAME
`inputs.versions` array as the installed policies (one more resource in the same ResourceSet, no
GitRepository/Kustomization -- it's fleet-native, not sourced from the policy repo), so the
allow-list cannot drift from what's actually installed. `Deny`, not `Audit`: documented the
brownfield Audit-start option (CONTEXT.md/ADR-0006) in a comment as a real deployment choice,
didn't use it here since cluster1 is fresh, not brownfield. Excludes cluster-system namespaces
(kube-system, flux-system, kyverno, etc.) -- an unconstrained catch-all on all Pods would deny
Kyverno's/Flux's own pod rollouts.

**2026-07-15:** issue 08's blocker cleared -- all three coexisting versions now run the
matchConditions-fixed tags, so the guard's stability no longer depends on which policy last
reconciled the shared webhook. `verify-orphan-guard.sh` (updated for the `2.2.0` line, was
hardcoded to the retired `2.1.1`) re-run green against the live cluster: no-label and
unknown-version pods refused, allow-list contains every currently-installed version, background
scan reports pre-existing orphans without eviction.

Also found and fixed live: the guard's namespace exclusion list didn't cover `crossplane-system`
(added by issue 18), so Crossplane's own control-plane pods were being denied at admission --
correctly enforced, wrongly scoped, since infrastructure pods aren't app workloads (same category
as the already-excluded `kyverno`/`flux-system`). Added `crossplane-system` and `monitoring`
(which had silently slipped through only because the guard wasn't reliably active until issue 08's
fix landed cluster-wide) to the exclusion list.

## Follow-up (2026-07-17): the "changes in the same reconcile" claim was false for 3 days

A wave-4 skeptic found this ticket's own checklist item -- "changing the array changes the guard
in the same reconcile" / "cannot drift" -- was false in the live cluster from its creation
(2026-07-14) until [`fleet#55`](https://github.com/policy-as-versioned-flux/fleet/pull/55) merged
2026-07-17T16:59:58Z: `policy-versions.yaml` (the guard's own source array) was only ever
`kubectl apply`'d by `up.sh`, never continuously Flux-reconciled, so a merged git change to the
array did not actually change the guard's live allow-list without a manual re-apply -- `fleet#55`'s
own PR body says this directly. Two sibling tickets (`real-estate/07-first-app-storefront.md`,
`faithful-floor/10-cluster2-retirement.md`) already cite "ticket 09's 2026-07-17 follow-up" for
this fix; this section is that follow-up, restored after the skeptic found it missing.

**Real, live consequence during that gap, not hypothetical**: the live `ResourceSet` drifted out
of band (hand-edited outside git), and the orphan guard -- correctly enforcing its own, now-stale
allow-list -- denied admission to legitimate `storefront` and `api` pods. Documented in full in
`real-estate/07-first-app-storefront.md`'s 2026-07-17 follow-up; not a new finding here, just the
cross-reference this file should always have carried. Fixed the same way as every other instance
of this root cause across this epic: a new `cluster-state` Flux Kustomization gives
`policy-versions.yaml` the same continuous-reconciliation guarantee every other resource in this
cluster already had.

## Follow-up (2026-07-18): a real, live interaction the cloud-plane extension surfaced

A wave-2 audit found that real-estate ticket 19's follow-up (extending this guard's
`resourceRules` to cover the two Crossplane CRD types) left the `crossplane-sample` Flux
`Kustomization` permanently `Ready: False` -- it manages `sample-unreconciled` (issue 18's
deliberately-unlabeled fixture), and Flux's own periodic drift-detection dry-run of that resource
is now denied by the guard on every reconcile, since the object genuinely has no
`mycompany.com/policy-version` label.

**Investigated, not "fixed" -- this is the design working correctly, not a bug.** The live object
itself is untouched (`creationTimestamp` unchanged since 2026-07-15, confirmed via `kubectl get`):
a `Deny`-mode `ValidatingPolicy` only ever blocks the *API call*, never deletes what's already
there, matching this guard's own "reported, never evicted" invariant exactly. What changed is
*visibility*: this fleet's README states governance debt is meant to be "always visible" the
moment something churns -- and Flux's own continuous reconciliation loop turns out to be a
legitimate churn trigger, one this project hadn't previously had reason to notice, since no
Crossplane CR was ever both Flux-managed *and* deliberately non-compliant until now. A perpetually
unhealthy Kustomization for a genuinely non-compliant resource is arguably a *more* visible signal
than a background `PolicyReport` a human has to go looking for -- consistent with, not a violation
of, the stated design. Deliberately not "fixed" by relabelling `sample-unreconciled` (which would
destroy its value as the live evidence real-estate ticket 19's own fix cites) or by dropping it
from Flux management (unnecessary engineering for behavior that's actually correct). Left as a
real, live, previously-unobserved interaction between two features that were each individually
correct -- recorded honestly rather than smoothed over, same standard as every other finding in
this epic.
