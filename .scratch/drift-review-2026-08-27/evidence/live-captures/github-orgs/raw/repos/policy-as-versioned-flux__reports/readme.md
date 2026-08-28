# reports

The reports team's app. Real-estate epic, ticket 08 — the middle case: a real, resolvable,
moderately old Python/Flask dependency tree (Flask 1.1.4, 2020 era — see `requirements.txt`),
correlated with this team's policy version, `2.0.0`.

`k8s/` carries this team's workload manifest: `mycompany.com/policy-version: "2.0.0"` and its
`department` label, this team's own adoption decision.

## Release

Push a `vX.Y.Z` tag; `.github/workflows/release.yml` builds and publishes
`ghcr.io/policy-as-versioned-flux/reports:vX.Y.Z` and prints the digest in the run summary.
