# c2p-collector

Prebuilt, digest-addressable image for the C2P `result2oscal` OSCAL collection glue (ADR-0009 in
the hub). Extracted from the `fleet` repo's build-from-source CronJob (ticket 04 of the
real-estate epic, `.scratch/real-estate/issues/04-extract-c2p-collector-image.md`) — the original
tradeoff (`golang:1.24-alpine`, `git clone` + `go build` every 15-minute run, ~4 minutes observed,
zero registry infra) traded run time for zero build infra; this component moves the build cost
here, once per release, so the live CronJob starts in seconds instead of minutes.

Bakes in `c2pcli` and `kyverno-plugin` (built from
[compliance-to-policy-go](https://github.com/oscal-compass/compliance-to-policy-go) `v2.0.0-rc.1`,
pinned per ADR-0009's pre-GA acceptance), `kubectl` (pinned + checksum-verified), and `jq`.
`run.sh` (the entrypoint) is the same collection logic the original CronJob ran — PolicyReports
in, shimmed (strip the coexistence version suffix, reshape `scope` into `results[].resources`),
`result2oscal`, ConfigMap out — with the build step removed since the binaries are already in the
image.

## Usage

A Kubernetes `CronJob` pointing `image:` at a released tag's digest
(`ghcr.io/policy-as-versioned-flux/c2p-collector@sha256:...`), mounting the
`component-definition.json` this component itself doesn't carry (that's fleet's own security
config, not this component's concern) at `/config/component-definition.json`, with a
`ServiceAccount` permitted to read `policyreports.wgpolicyk8s.io` and write the
`oscal-assessment-results` ConfigMap. See the `fleet` repo's `infrastructure/c2p/` for the real
wiring.

## Self-check

`./verify.sh` — builds the real image and proves, without needing a live cluster: the baked-in
binaries (`c2pcli`, `kyverno-plugin`, `kubectl`, `jq`) are present and runnable, and the
PolicyReport→OSCAL shim transforms a fixture exactly as the live collector does (version suffix
stripped, `scope` reshaped into `resources[]`). Requires `docker`; skips (not fails) without it.

## Release

Push a `vX.Y.Z` tag; `.github/workflows/release.yml` builds and publishes
`ghcr.io/policy-as-versioned-flux/c2p-collector:vX.Y.Z` (public, so a KiND demo cluster can pull
it with no `imagePullSecret`) and prints the resulting digest in the run summary — pin that digest
in the consumer's `CronJob`.
