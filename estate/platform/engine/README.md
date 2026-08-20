# platform/engine — the admission + fleet controllers

**Ticket 11.** Kyverno (ADR-0003's admission engine) and the ControlPlane
Flux Operator (ADR-0005's install/fleet layer), delivered as Flux
HelmReleases — the same pattern as `identity/` (spire, istio, openbao) and
`access/` (pomerium, dex). Neither was installed anywhere in the repo before
this ticket, even though `estate/driftwood/README.md` and
`estate/platform/distribution/README.md` both name them as prerequisites.

## What's here

| Piece | File | Role |
|---|---|---|
| Kyverno | `kyverno/helmrelease.yaml` | admission controller; installs the `policies.kyverno.io` CRD group (`ValidatingPolicy`, `MutatingPolicy`) every policy in this repo needs |
| flux-operator | `flux-operator/helmrelease.yaml` | installs the `ResourceSet`/`FluxInstance` CRDs `estate/platform/distribution` needs; no `FluxInstance` is created, so the cluster's existing vanilla Flux install is untouched (ADR-0005 guardrail) |

## Ordering

Installed **before** the posture layer (`estate/platform/posture/`), which
ships `MutatingPolicy`/`ValidatingPolicy` objects that need Kyverno's CRDs to
exist first. See `estate/talk/up.sh`.

## Run it

```bash
estate/driftwood/scripts/up.sh      # cluster + Flux must exist first
estate/platform/engine/up.sh        # applies both HelmReleases, bounded reconciles
estate/platform/engine/verify-engine.sh
```
