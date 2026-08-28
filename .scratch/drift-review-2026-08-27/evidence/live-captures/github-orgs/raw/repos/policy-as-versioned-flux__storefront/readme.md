# storefront

The storefront team's app. Real-estate epic, ticket 07 — the tracer bullet for the whole consumer
story: a real (minimal) old-Angular static build behind nginx, with a genuine, deliberately stale
npm dependency tree (Angular 9, early 2020 — see `package.json`), served under policy version
2.2.0.

This team's own repo, own reconcile cadence, own tags — Renovate (via the org preset) opens real
PRs against this repo's stale dependencies; this repo's own release tags are what fleet's
`GitRepository` tracks, independent of every other team.

`k8s/` carries this team's workload manifest: the `mycompany.com/policy-version` label (this
team's adoption decision, made here, not planted by the platform) and its `department` label.

## Release

Push a `vX.Y.Z` tag; `.github/workflows/release.yml` builds and publishes
`ghcr.io/policy-as-versioned-flux/storefront:vX.Y.Z` and prints the digest in the run summary.
