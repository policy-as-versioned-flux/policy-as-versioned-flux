# 02 — Where does the shim sit: procurement, build, or admission?

Type: grilling
Status: open
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

**Decide which, or which combination** — and specifically whether the shim is a real, pinned,
signed artefact in its own right (so a COTS product's governance is itself a versioned dependency)
or a configuration entry in the platform.

Note the interaction with the always-caged decision on the semver map: whatever the shim does, the
COTS workload must end up with a cage spec like everything else.
