# readiness-collector

Offline component answering the CIO's forward question: for a candidate policy version, which
workloads would fail if the estate adopted it? Ticket 10 of the real-estate epic
(`policy-as-versioned-flux/policy-as-versioned-flux` hub,
`.scratch/real-estate/issues/10-readiness-collector.md`).

**Never touches admission. Installs no shadow policies. Pollutes no live PolicyReports.**
Everything is `kyverno apply` against a local dump of live workload manifests — never
`kubectl apply`.

## Mechanism

1. Clone the candidate version's tag from the policy repo.
2. Render each of that tag's policies via `kustomize` (keeps the real `nameSuffix`/labels), then
   strip `matchConditions` (the version-scope CEL gate) via `yq del` — "evaluate everyone as if
   opted in".
3. Dump every live workload carrying `mycompany.com/policy-version`, one resource per file —
   `kyverno apply` silently produces nothing against a `kind: List`-wrapped multi-doc file (found
   live while building this, not assumed from docs).
4. `kyverno apply` the stripped policies against the dump, `--policy-report --output-format json`.
   Exits 1 on any fail (CI-gate semantics) — captured and parsed regardless of exit code.
5. Group results by team (the `app` label already on every workload), publish per-team
   pass/fail counts + a `ready` boolean to a `readiness-<candidate-version>` ConfigMap.

## Usage

```sh
CANDIDATE_TAG=2.2.0 ./run.sh
```

As a `CronJob`, `CANDIDATE_TAG` names the version teams should be asked "are you ready for this?"
— typically the estate's leading version. Requires a `ServiceAccount` permitted to `get`/`list`
Pods cluster-wide and write one ConfigMap (same read-only-plus-one-ConfigMap posture as
`c2p-collector`).

## Self-check

`./verify.sh` — against a real signed tag from the real policy repo, not a mock: a fixture
workload shaped like today's real `ledger` (1.0.0-pinned, no owner annotation) evaluated against
v2.2.0's stripped policies passes the department checks and fails `require-owner-annotation` —
the exact known case ticket 10 names. Requires `git`/`jq`/`yq`/`kustomize`/`kyverno`; skips (not
fails) without them.

## Release

Push a `vX.Y.Z` tag; `.github/workflows/release.yml` builds and publishes
`ghcr.io/policy-as-versioned-flux/readiness-collector:vX.Y.Z` and prints the digest in the run
summary.
