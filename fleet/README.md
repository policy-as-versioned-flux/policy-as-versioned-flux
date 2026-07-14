# fleet

The config repo Flux reconciles (PRD §5.1). Currently just the runtime floor
(issue 05): a KiND cluster, the ControlPlane Flux Operator (`FluxInstance`,
[ADR-0005](https://github.com/policy-as-versioned-flux/policy-as-versioned-flux/blob/main/docs/adr/0005-controlplane-flux-operator-resourceset.md)), and
the Kyverno engine (`>=1.18`, [ADR-0003](https://github.com/policy-as-versioned-flux/policy-as-versioned-flux/blob/main/docs/adr/0003-kyverno-validatingpolicy-cel.md))
installed via a pinned `HelmRelease`. The `ResourceSet` coexistence matrix and
per-version policy sources land in later issues.

```
flux-instance.yaml            FluxInstance -- pinned Flux 2.9.2, upstream-alpine variant
infrastructure/kyverno/       Kyverno engine: Namespace + HelmRepository + HelmRelease
up.sh / down.sh                one command sequence, idempotent, clean teardown+recreate
```

## Run it

```sh
./up.sh     # KiND cluster 'cluster1' -> Flux Operator -> Kyverno, all healthy
./down.sh   # tear down; ./up.sh again recreates cleanly
```

Prereqs: docker, kind, kubectl, helm. Readiness is gated by native
`kubectl wait --for=condition=Ready` throughout, never a jsonpath polling
loop.
