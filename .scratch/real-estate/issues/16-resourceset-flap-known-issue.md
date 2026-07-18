# 16 — Known issue: `flux-operator`'s ResourceSet controller periodically flaps `policy-1.0.0`

**Found by**: an adversarial verification pass re-checking ticket 09 (2026-07-17/18), not by any
of this epic's own tickets — logged here rather than silently left out of the record, per this
project's own standard for real bugs (see Episode 1's webhook-flattening/go-git sagas in
`docs/HISTORY.md`).

**What's happening, live-confirmed**: `flux-operator`'s ResourceSet controller (`resourceset`
controller, `fluxcd.controlplane.io`, chart-pinned `v0.55.0` per ADR-0005) periodically
garbage-collects and immediately recreates `GitRepository/policy-1.0.0` and its two
`Kustomization`s (`policy-1.0.0-require-department-label`, `policy-1.0.0-require-known-department-label`),
with **no corresponding git change** — the array entry in `clusters/cluster1/policy-versions.yaml`
is untouched throughout. Each flap is a delete immediately followed by a recreate, roughly
0.4–0.6 seconds apart.

**Root-caused as precisely as reasonably possible without upstream source access**: `kubectl -n
flux-system logs deploy/flux-operator` shows 24 occurrences in the retained log buffer since
2026-07-14T15:35, recurring roughly every 20–90 minutes, isolated almost entirely to the `1.0.0`
entry (`2.0.0`: 0 spurious occurrences; `2.2.0`: 1, tied to a real git-driven test during this
session, not spurious). The reconcile that ends in a garbage-collection event consistently takes
noticeably longer (~5s, vs ~100ms for a normal no-op reconcile) — consistent with a transient,
slow reconcile pass computing an incomplete "desired resources" set (missing the `1.0.0` entry for
that one pass), garbage-collecting whatever isn't in that incomplete set, then immediately
self-correcting on the very next reconcile. `1.0.0` is both the array's first element and the only
entry carrying the `sunset:` field (ticket 09) — plausible but unconfirmed as a contributing
factor; genuinely pinning this further would require reading `flux-operator`'s own controller
source, out of scope for this repo.

**Real, live consequence, not hypothetical**: during each ~0.5s window, the two Kyverno
`ValidatingPolicy` objects enforcing labels for policy version `1.0.0` are absent — a workload
admission request landing in that exact window would not be evaluated against those two policies.

**Correction (2026-07-18, a skeptic pass on this very ticket)**: the original write-up claimed
`orphan-guard`'s own allow-list was never observed to drop during a flap, "reconciling on a
separate path" from the per-version objects — implying the cluster-wide catch-all stayed solid
throughout. That's wrong. Live `kubectl get validatingpolicy orphan-guard` shows its own
`creationTimestamp` is fresh (minutes old at check time, not the object's original install time),
and the operator log contains real `"ValidatingPolicy/orphan-guard":"created"` events — not just
`"configured"` (in-place update) — some with no adjacent per-version GC event nearby at all.
`orphan-guard` itself gets deleted and recreated on its own cadence. This is a materially bigger
blast radius than originally documented: during an `orphan-guard` flap window, **zero
policy-version enforcement applies to any pod**, not just the two `1.0.0`-specific gates. Not
currently broken (re-checked minutes after a recreation and it was actively blocking violating
pods again), but the risk statement below is revised to reflect the real scope.

**Likely-related, separately observed while investigating the correction above**: at the same time,
`flux-operator`'s own pod was found actively crash-looping — 5 restarts in the preceding ~40
minutes, `kubectl describe pod` showing repeated liveness/readiness probe failures
(`context deadline exceeded`, i.e. timeouts, not panics) against a tight 1-second probe timeout.
This plausibly explains the flap mechanism better than the original "slow reconcile pass" theory:
every pod restart resets the ResourceSet controller's in-memory reconcile state, and the first
reconcile after a cold start computing an incomplete desired-resource set (before its watch caches
are fully warm) would produce exactly this delete-then-immediately-recreate pattern — for whichever
objects are unlucky enough to be evaluated during that narrow window, which needn't be the same
object every time. Not conclusively proven (didn't have time to correlate all 24 historical flap
timestamps against operator pod restart history before this write-up), but a real, live,
independently-observed fact worth recording rather than treating the two findings as unrelated.

**Practical risk, assessed honestly, revised**: still real, and now known to be somewhat larger in
scope than first documented (cluster-wide during an `orphan-guard` flap, not just two policies).
Still self-heals without intervention, still hasn't been observed to actually admit a
non-compliant workload in this session. If the crash-loop correlation above is right, the flap
frequency plausibly tracks how often `flux-operator`'s pod restarts — which itself may be
sensitive to how much concurrent API load the cluster is under (this session ran an unusually
heavy, sustained adversarial-verification workload immediately before the crash-loop was
observed) rather than being a constant background rate. Worth re-measuring under normal,
non-audit load before treating the "~24 times over 4 days" baseline as representative.

**Status: documented, not fixed — no faithful in-repo fix exists.** This is upstream
`flux-operator`/`fluxcd.controlplane.io` controller behavior, not a defect in this project's own
YAML, Kyverno policies, or Flux configuration (confirmed: the git-declared array is stable and
correct throughout every flap). The two available in-repo mitigations were considered and rejected
as not worth taking for a demo estate: (1) pinning a newer `flux-operator` chart version on the
chance a later release fixed a ResourceSet-controller race — speculative without release-note
access, and non-trivial version churn for an unconfirmed fix; (2) working around it by moving
away from the single-`ResourceSet`-with-nested-array design entirely — a much larger architectural
change that would undermine ADR-0005's whole rationale for using a `ResourceSet` in the first
place. Left as an honestly-recorded, low-risk, upstream-controller limitation for a future session
(or an upstream bug report against `fluxcd.controlplane.io`/`flux-operator`) to pick up, rather than
silently omitted from the epic's record. One candidate worth a future look, given the crash-loop
correlation found above: `up.sh`'s `helm upgrade --install flux-operator` call passes no values
override at all, so the chart's default (tight) liveness/readiness probe timeouts apply as-is —
loosening them via a real Helm values change is a genuine in-repo lever, if a future session
confirms probe-timeout-induced restarts are actually the flap's proximate cause rather than just a
correlated observation.
