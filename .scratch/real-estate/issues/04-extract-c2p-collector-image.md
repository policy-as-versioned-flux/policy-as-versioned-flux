# 04 — Extract the c2p-collector into its own repo with a real container image

**What to build:** The OSCAL collection job becomes a component repo that builds and publishes a proper container image to the org's registry, replacing the build-C2P-from-source-every-run CronJob (the ticket-21 tradeoff, now retired). Fleet's CronJob is repointed at the image, pinned by digest — making the collector itself a Renovate-maintainable governed dependency. Collection behaviour (PolicyReports in, shimmed, result2oscal, ConfigMap out) is unchanged; the component carries its own self-check.

**Blocked by:** None — can start immediately.

**Status:** done

- [x] Component repo with Dockerfile + CI publishing a tagged, digest-addressable image to the org registry
- [x] Fleet's CronJob runs the pinned image; run time drops from ~4 minutes to seconds-to-start
- [x] The OSCAL panel still shows the live finding, verified through the Grafana query API
- [x] The image pin is visible to Renovate as a bumpable dependency

## Comments

Done 2026-07-16. `policy-as-versioned-flux/c2p-collector`, tagged `v1.0.0`, published to GHCR
public (`ghcr.io/policy-as-versioned-flux/c2p-collector@sha256:a22fa18438dba108196090fe62d67717eb01f5fec11c112599833f0332900d2a`)
— user confirmed the public-publish decision explicitly (a new decision beyond the pacing
question, gated by this session's own safety classifier).

Bakes in `c2pcli` + `kyverno-plugin` (built from source once, at release time, instead of every
15-minute run) + pinned `kubectl` + `jq`. `run.sh`'s collection logic (PolicyReports in, shimmed,
`result2oscal`, ConfigMap out) is unchanged. Fleet's `cronjob.yaml` now pins the digest; the
`c2p-run-script` ConfigMap generator is gone (the script lives in the image now); resource
requests/limits reduced (512Mi→128Mi request, 1536Mi→256Mi limit) since there's no cold `go build`
to budget for.

**One real snag, resolved rather than routed around:** the workflow's own `GITHUB_TOKEN` cannot
set GHCR package visibility (`PATCH .../packages/container/...` → 404, confirmed in the actual
run log, not assumed) — this needs org-admin-scoped credentials the ephemeral token doesn't carry.
Neither did my own `gh` CLI token (missing `read:packages`/`write:packages`). Asked the user to
set visibility once via the GitHub UI rather than widening my own token's OAuth scope
unnecessarily; confirmed fixed by a clean `docker pull` with zero credentials.

**Live-verified, not just applied:** discovered mid-verification that `infrastructure/c2p` is a
real Flux Kustomization (`c2p`), not a one-shot-applied dir like `policy-versions.yaml`/`apps.yaml`
— an out-of-band `kubectl apply -k` got silently reverted by the next reconcile before I noticed,
so the change had to go through the normal PR→merge→Flux-reconcile path like everything else
GitOps-managed here. Once reconciled: a manually triggered Job ran in seconds (`c2pcli` logs show
~1s from start to "generated finding for rule require-rds-multi-az"), and the OSCAL dashboard
panel was queried live through `/api/ds/query` (the established seam) — real row, `cp-10_smt`,
`not-satisfied`, sourced from the pinned image's run, not a leftover from the old CronJob.

Renovate's native `docker`/OCI-digest manager will see the pinned
`ghcr.io/policy-as-versioned-flux/c2p-collector@sha256:...` line in `cronjob.yaml` out of the box
— no customManager needed, same reasoning as ticket 03's Action pin.

Shipped as `fleet#25` (self-merged, standing authorization).
