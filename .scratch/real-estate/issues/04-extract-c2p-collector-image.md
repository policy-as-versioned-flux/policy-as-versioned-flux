# 04 — Extract the c2p-collector into its own repo with a real container image

**What to build:** The OSCAL collection job becomes a component repo that builds and publishes a proper container image to the org's registry, replacing the build-C2P-from-source-every-run CronJob (the ticket-21 tradeoff, now retired). Fleet's CronJob is repointed at the image, pinned by digest — making the collector itself a Renovate-maintainable governed dependency. Collection behaviour (PolicyReports in, shimmed, result2oscal, ConfigMap out) is unchanged; the component carries its own self-check.

**Blocked by:** None — can start immediately.

**Status:** ready-for-agent

- [ ] Component repo with Dockerfile + CI publishing a tagged, digest-addressable image to the org registry
- [ ] Fleet's CronJob runs the pinned image; run time drops from ~4 minutes to seconds-to-start
- [ ] The OSCAL panel still shows the live finding, verified through the Grafana query API
- [ ] The image pin is visible to Renovate as a bumpable dependency
