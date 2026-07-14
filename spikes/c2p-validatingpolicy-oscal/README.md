# Spike: C2P `result2oscal` over Kyverno CEL `ValidatingPolicy` reports

**Question (ADR-0009 build precondition).** All OSCAL Compass / Compliance-to-Policy (C2P) testdata
uses legacy Kyverno `ClusterPolicy`. Does C2P v2 correctly consume the PolicyReports produced by a
**CEL `ValidatingPolicy`** (`policies.kyverno.io/v1`, Kyverno ≥1.18) and emit correct OSCAL
assessment-results? This is the one unproven dependency in the measurable pillar.

**Verdict: YES, with a ~6-line collection-time shim.** Verified 2026-07-14 on KiND + Kyverno 1.18.2 +
C2P `v2.0.0-rc.1`.

## What the spike shows

Two `ValidatingPolicy`s (Audit, background scan) map to two NIST controls, with a compliant and a
non-compliant Pod:

| Control | Policy | Pods | Expected |
|---|---|---|---|
| CM-8 | `require-team-label` | `pod-good` (has label), `pod-bad` (missing) | **not-satisfied** (one fail) |
| SC-7 | `disallow-host-network` | both pass | **satisfied** |

### 1. The crux holds
C2P `result2oscal` keys on **`results[].policy` only**, string-equal to the `Check_Id` in the
component-definition. Kyverno writes the policy's own `metadata.name` into `results[].policy` for
**both** ClusterPolicy and ValidatingPolicy — confirmed live: report entries carry
`policy=require-team-label` / `policy=disallow-host-network`, `source=KyvernoValidatingPolicy`,
`rule=null`. Since C2P never reads `rule`/`source`/`kind`, the ValidatingPolicy path just works.

### 2. The one real gap: subject location
Kyverno ≥1.18 emits **per-resource** reports — the subject is in the report's `.scope`, and
`results[].resources` is **`null`**. C2P reads subjects from `results[].resources`
(`cmd/kyverno-plugin/server/result2oscal.go`), so on raw reports it captures **0 subjects** and every
in-scope control defaults to `not-satisfied` — a **false negative** for SC-7.

A ~6-line jq shim at collection time (copy `.scope` into each `results[].resources`) fixes it:

```sh
kubectl -n <ns> get policyreports.wgpolicyk8s.io -o json \
 | jq '.items |= map(.scope as $s | .results |= map(.resources =
        [{apiVersion:$s.apiVersion, kind:$s.kind, namespace:$s.namespace, name:$s.name, uid:$s.uid}]))'
```

| | CM-8 | SC-7 |
|---|---|---|
| RAW reports | not-satisfied | **not-satisfied ✗** |
| SHIMMED reports | not-satisfied ✓ | **satisfied ✓** |

C2P self-validates the OSCAL (oscal-version 1.1.3) before writing.

## Consequence for the build
The C2P collection job (CronJob / Flux `Kustomization`, ADR-0009) includes this scope→resources
normalization. It is declarative jq, not bespoke tooling. The "~50-line shim" ADR-0009 budgeted is
in practice ~6 lines. The risk is retired.

## Run it
```sh
./run.sh          # ~4 min cold: creates KiND, installs Kyverno, runs both, prints verdict, tears down
KEEP=1 ./run.sh   # leave the cluster up
```
Prereqs: docker, kind, kubectl, helm, go ≥1.24, jq, git.
