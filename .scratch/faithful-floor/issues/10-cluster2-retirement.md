# 10 — cluster2 profile + version retirement

**What to build:** Coexistence's payoff — retirement without a flag day: a second cluster profile (`cluster2`) whose array holds only `>=2.0.0`, proving per-cluster narrowing from the same fleet config; then the retirement story — removing `1.0.0` from a cluster's array prunes its policies and the orphan guard immediately refuses workloads still pinned to it. Demonstrates the corollary: the estate's gate strength equals its weakest installed version, so retiring is a security action.

**Blocked by:** 08 — ResourceSet coexistence matrix, 09 — Orphan guard.

**Status:** done -- issue 08's blocker cleared, all 4 items proven live 2026-07-15

- [x] `cluster1` (all versions) and `cluster2` (`>=2.0.0`) run from the same fleet config with different inputs
- [x] On `cluster2`, a workload pinned to `1.0.0` is denied by the orphan guard; the same workload admits on `cluster1`
- [x] Retiring a version = one reviewed change to the array; policies prune and the guard tightens in the same reconcile
- [x] The silent-ungovernance gap of the 2022 implementation is demonstrably closed

## Comments

2026-07-15: checked whether this is genuinely blocked by 08, or just graph-blocked by convention
(the way issue 07 turned out to be closeable without a new tag). It is genuinely blocked, for the
same mechanical reason as 08, not merely by dependency-graph label:

`cluster2 (>=2.0.0)` as written means *at least* `v2.0.1` and `v2.1.1` both installed -- i.e. two
coexisting versions. Issue 08's root cause (Kyverno flattens every installed ValidatingPolicy's
`objectSelector` into one shared webhook, last-reconciled wins) fires on **any** 2+-version
coexistence, not specifically 3 -- `v2.0.1` and `v2.1.1` are themselves already-tagged and
immutable with the pre-fix `objectSelector` pattern baked in, same as `v1.0.1`. A `cluster2` built
from them today would be exactly as unstable as `cluster1` currently is. Considered narrowing
`cluster2` to a single version (`v2.1.1` alone, trivially `>=2.0.0`, no flattening bug since a
lone version has nothing to conflict with) to sidestep this -- but the checklist's actual
comparison needs `cluster1`'s *own* multi-version admission to be reliable too ("the same workload
admits on cluster1"), and `cluster1` has the identical open instability. Narrowing both sides to
single versions would prove a real but different, narrower claim than what this ticket asks for,
and would cost standing up dedicated new cluster infrastructure to re-derive a fact issue 08
already needs the same new signed tags to establish properly. Not worth it as a substitute for the
real thing.

The one checklist item that doesn't depend on any of this -- "retiring a version = one reviewed
array change, prune + guard-tighten in the same reconcile" -- is already true and already proven
as a general mechanism, just not narrated as a *second-cluster* story specifically: issue 09's
orphan guard is templated from the same `inputs.versions` array as the installed policies (so the
allow-list cannot drift from what's installed), and issue 08's `verify-coexistence.sh` already
exercises prune-on-array-removal (Flux's `prune: true`) as a passing check. Checked that box on
that basis; left the cross-cluster comparison and "gap demonstrably closed" boxes open since they
specifically need the new tags issue 08 is waiting on.

**2026-07-15, closed for real:** issue 08's blocker cleared (new signed tags, real live
coexistence proof). Built `clusters/cluster2/` (own `bootstrap.yaml`/`policy-versions.yaml`, same
self-referential/ResourceSet pattern as cluster1, narrowed to `{2.0.0, 2.2.0}` -- workload-plane
only, deliberately minimal) and `up2.sh`/`down2.sh`. Brought up a real second KiND cluster
(`kind-cluster2`) alongside the existing `kind-cluster1`, both live simultaneously.

`verify-retirement.sh`, run for real against both live clusters at once, all green:
- Confirmed cluster1 has the `1.0.0` line and cluster2 correctly doesn't.
- The exact same Pod (`mycompany.com/policy-version: "1.0.0"`) was refused on cluster2 and
  admitted on cluster1 -- live, simultaneous, cross-cluster differential proof.
- Removed `2.0.0` from cluster2's array (one `yq` array-element removal + re-apply): its policies
  pruned, and a workload pinned to the just-retired `2.0.0` was refused in the same reconcile --
  the orphan guard tightened automatically. Restored cluster2's committed array afterward,
  confirmed it came back.

This is the full retirement-without-a-flag-day story from the ticket description, proven live, not
narrated: narrowing or retiring is a one-line reviewed array change with an immediate, provable
governance consequence -- the silent-ungovernance gap the 2022 implementation had is closed.
