# 02 — Where does the shim sit: procurement, build, or admission?

Type: grilling
Status: resolved
Blocked by: 01

## Question

"A policy dependency shim, perhaps at the infra decision point" — that phrase points earlier than
admission. Settle where the version gets attached, because each option is a different system.

- **Procurement / selection time.** The thing is evaluated when it is *chosen*, and the choice
  carries a declared policy version and a residual-risk figure. Fits the estate's thesis best (the
  debate happens in a PR, not an exemption request) and is the only option that can refuse a product
  before money is spent. But it governs a *decision*, not a running pod.
- **Build / packaging time.** A wrapper chart or kustomize overlay stamps the label as the workload
  is packaged for the estate. Concrete, versionable, signable — and it is a real dependency, so
  Renovate can bump it.
- **Admission time.** A mutating policy stamps a version onto pods matching a declared allow-list.
  Cheapest, but it means the cluster is asserting a compliance claim about a workload nobody
  inspected, which is the kind of unearned green this estate refuses elsewhere.

**Settled upstream and binding here:** the remedy is **wrap it or shim it** — never exempt, never
deny. Also settled: the platform's own five third-party charts are the *leading case*, so whichever
option is chosen must be able to govern istiod, not just a well-behaved vendor app. And note the pair
in the owner's phrasing: a **wrap** (a chart or overlay we control, patching the pod template before
it is applied) and a **shim** (a layer decorating the workload at the infra decision point) may be
two mechanisms rather than one — decide whether both exist and when each applies.

**Decide which, or which combination** — and specifically whether the shim is a real, pinned,
signed artefact in its own right (so a COTS product's governance is itself a versioned dependency)
or a configuration entry in the platform.

Note the interaction with the always-caged decision on the semver map: whatever the shim does, the
COTS workload must end up with a cage spec like everything else.

## Answer

Resolved by grilling, 2026-08-20. **Three sources, layered across the lifecycle — and the allow-list
was explicitly rejected.**

The version for a workload that cannot claim one comes from:

1. **The wrapper, at packaging time.** A chart or overlay we control adds the label, so the COTS
   product becomes a real pinned, signed dependency — the estate's own thesis applied to bought
   software. The version is reviewable in a PR rather than asserted by a cluster, and Renovate can
   bump it.
2. **The procurement record, at selection time.** The decision to adopt the product carries the
   declared policy version — the version exists before anything runs.
3. **The SPIFFE identity, at runtime.** The workload already has a base mesh SVID; the identity it
   presents is derivable and checkable against what was procured and wrapped.

These reinforce rather than compete: **procured → wrapped → identified**, with each stage able to
check the one before. A wrapper claiming a version the procurement record never authorised is
detectable; a running pod whose SVID doesn't match its wrapper is detectable.

**Rejected: a platform-side allow-list mapping workload identity → version at admission.** It was the
cheapest option and the owner declined it, consistently with the estate's standard elsewhere — an
allow-list entry is the platform asserting a compliance claim about software nobody inspected, which
is the unearned green this estate refuses.

**The stamping machinery already exists and is trust-bounded.** `stamp-posture` is an admission-time
`MutatingPolicy` that stamps `posture.acme.io/version` using server-side-apply, so it *overwrites* any
user-supplied value; `posture-trust-boundary` then refuses any pod whose posture doesn't match its
claim ("the SVID path is not forgeable at the label"). So platform-stamps-a-trust-bounded-label is
proven here. What this ticket supplies is the missing input: today `stamp-posture` derives posture
*from the version claim* (`matchConditions: claims-a-policy-version`), and a COTS pod has no claim to
derive from. The wrapper and the procurement record are where the claim comes from instead.
