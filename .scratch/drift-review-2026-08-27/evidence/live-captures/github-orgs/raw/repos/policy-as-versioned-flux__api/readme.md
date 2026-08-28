# api

The api team's app. Real-estate epic, ticket 08 — the good citizen: current Go dependencies (a
single small real router, `go-chi/chi`, latest at time of writing — see `go.mod`), policy version
`2.2.0`. The contrast with ledger's Log4Shell-era log4j is the point: same design, same gates,
very different dependency hygiene, both visible on the estate dashboard.

`k8s/` carries this team's workload manifest: `mycompany.com/policy-version: "2.2.0"` and its
`department` label, this team's own adoption decision.

## Release

Push a `vX.Y.Z` tag; `.github/workflows/release.yml` builds and publishes
`ghcr.io/policy-as-versioned-flux/api:vX.Y.Z` and prints the digest in the run summary.
