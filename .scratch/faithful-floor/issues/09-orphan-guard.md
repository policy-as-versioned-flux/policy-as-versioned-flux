# 09 — Orphan guard

**What to build:** The deterministic catch-all that turns the gate tier into a locked door rather than an opt-in door (CONTEXT "Orphan guard"): one Deny-at-admission ValidatingPolicy whose CEL carries a literal allow-list rendered from the same `{version, commit}` array that installs the versions — a missing `policy-version` label is a violation, an unknown one is a violation — with background-scan Audit reports surfacing pre-existing orphans. Brownfield posture (start in Audit, promote by editorial PR, never timed — ADR-0006) documented.

**Blocked by:** 08 — ResourceSet coexistence matrix.

**Status:** done (this ticket's own checklist; full cross-version stability inherits issue 08's open blocker, see Comments)

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

Same caveat as issue 08: a fully stable run of ALL these checks simultaneously, with all three
versions genuinely coexisting, needs the same new patch tags (v1.0.0/v2.0.0's Kustomizations are
still reconciling from immutable tags carrying the pre-`matchConditions` `objectSelector` pattern,
which destabilizes the *shared* Kyverno webhook cluster-wide, orphan-guard included, until every
policy on the cluster is on the fixed pattern). See issue 08's Comments for the full story and
what's blocked on.
