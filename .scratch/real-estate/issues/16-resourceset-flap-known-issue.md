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
admission request landing in that exact window would not be evaluated against those two policies
(though `orphan-guard`'s own allow-list was not observed to drop `'1.0.0'` during any captured
window — it appears to reconcile on a separate path from the per-version `GitRepository`/
`Kustomization` GC). On a project whose whole stated premise is deny-at-admission guarantees, an
enforcement gap — even a sub-second one, recurring roughly hourly — is worth recording precisely
rather than glossed over.

**Practical risk, assessed honestly**: low. The flap window is sub-second, self-heals without
intervention, has never been observed to actually admit a non-compliant workload in this session
(no incident correlates with any of the 24 timestamps), and only affects the specific policy
version whose array entry happens to be processed on the affected reconcile pass. This is a
genuine gap in an always-on guarantee, not a theoretical one — but it is not the kind of gap this
epic's own tooling (Kyverno, Flux Kustomization, `orphan-guard`) can fix, since the bug is in a
different controller's (`flux-operator`'s `ResourceSet` reconciler) own reconcile-loop timing.

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
silently omitted from the epic's record.
