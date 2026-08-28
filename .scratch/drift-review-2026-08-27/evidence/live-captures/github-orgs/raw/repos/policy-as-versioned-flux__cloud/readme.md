# cloud

The cloud plane (PRD §5.1, ADR-0004): harvested OSCAL 800-53r5 catalogue + Crossplane v2 setup.

```
oscal/harvested-from-collie/   the OSCAL catalogue + control-mapping intent, taken as data
                                (see below) -- not a fork of collie's toolchain
```

## What's harvested, and what isn't (ADR-0004)

We **harvest** [`controlplaneio/collie`](https://github.com/controlplaneio/collie) (Apache-2.0)
rather than fork it: take the reusable *IP* (the NIST 800-53r5 catalogue and the RDS/S3 control
mapping *intent*), rebuild the actual policy bodies from scratch against current infrastructure.
collie's OSCAL→policy *generator* (built on the now-dropped Lula 1), its bootstrap, and its
EKS/Terraform wiring are **not** ported.

Harvested from `controlplaneio/collie@d2486af71d4fb416f00ecbd37f34bd675a15ab8d` (2026-07-14),
Apache-2.0, © ControlPlane (`oscal/harvested-from-collie/COLLIE-LICENSE`):

| File | What it is |
|---|---|
| `NIST_SP-800-53_rev5_catalog.yaml` | The full NIST SP 800-53 rev 5 controls + assessment procedures catalogue, in OSCAL. Not collie's own work (it's NIST's official machine-readable release, collie just vendors a copy) -- harvested via collie for convenience/provenance-tracking, same license terms apply to collie's redistribution. |
| `S3-component-definition.yaml`, `RDS-component-definition.yaml` | collie's OSCAL component-definitions: which NIST controls each of its (legacy) Kyverno rules claims to satisfy. This is the *intent* our hand-authored `require-s3-bucket-encryption`/`require-rds-multi-az` policies (in the `policy` repo, `cloud/`) cite by control-id -- the CEL bodies themselves are rebuilt, not translated 1:1 from collie's `ClusterPolicy` YAML, since collie targets a different (older, non-namespaced) Crossplane AWS provider shape than what's current. See each policy's own `rationale.md` for exactly what was kept vs. rebuilt. |
| `NIST_SP-800-53_rev5_S3-baseline_profile.yaml`, `NIST_SP-800-53_rev5_RDS-baseline_profile.yaml` | collie's OSCAL profiles selecting which catalogue controls apply to S3/RDS specifically (a subset of the full catalogue). |

**Not harvested:** collie's OSCAL→Kyverno generator, its Lula 1 wiring, its Terraform/EKS
bootstrap, its `bats` test harness. Dropped per ADR-0004 -- the generator is what's stale (Lula 1
generating legacy `ClusterPolicy`), not the compliance intent it encodes.

## What lands here later

- Current Crossplane v2 + AWS provider-family CRDs installed in KiND, no ProviderConfig/auth/
  reconcile (issue 18).
- C2P `component-definition` mapping NIST controls ↔ this project's own hand-authored policy
  names, and the `result2oscal` collection job turning Kyverno PolicyReports into OSCAL
  assessment-results (issue 20, building on the spike in the hub repo's
  `spikes/c2p-validatingpolicy-oscal/`).

The hand-authored CEL `ValidatingPolicy` bodies that actually cite these controls live in the
[`policy`](https://github.com/policy-as-versioned-flux/policy) repo's `cloud/` directory,
versioned identically to the workload plane (issue 17) -- not duplicated here.
