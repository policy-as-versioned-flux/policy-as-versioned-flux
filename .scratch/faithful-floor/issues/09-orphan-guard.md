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
