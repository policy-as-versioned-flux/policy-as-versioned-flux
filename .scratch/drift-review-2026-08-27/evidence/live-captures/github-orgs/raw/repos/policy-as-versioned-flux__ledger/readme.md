# ledger

The ledger team's app. Real-estate epic, ticket 08 — deliberately the laggard: a real, resolvable
`log4j-core:2.14.1` dependency (Log4Shell-era, CVE-2021-44228 — see `pom.xml`), correlated with
this team's old policy version, `1.0.0`. Run live on KiND, not a fixture — the vulnerability
scanner has genuine signal here.

Plain JDK `HttpServer`, no framework — the point of this app is the log4j dependency, not the web
stack.

`k8s/` carries this team's workload manifest: `mycompany.com/policy-version: "1.0.0"` and its
`department` label, this team's own adoption decision.

## Release

Push a `vX.Y.Z` tag; `.github/workflows/release.yml` builds and publishes
`ghcr.io/policy-as-versioned-flux/ledger:vX.Y.Z` and prints the digest in the run summary.
