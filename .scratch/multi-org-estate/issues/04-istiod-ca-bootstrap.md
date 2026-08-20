# 04 — Fix the istiod CA bootstrap so meshed pods can start

Type: task
Status: open
Blocked by: none

## Question

Make istiod obtain a valid CA bundle and serving cert so the sidecar-injection webhook serves and
meshed workloads start with SPIFFE SVIDs. This unblocks `talk-spec` tickets 15 and 17 and is the
first wall in the 28/28 chain.

**`talk-spec` ticket 14's own diagnosis is wrong and should be corrected as part of this.** It blames
istio-csr. There is no istio-csr or cert-manager anywhere in the repo — the `cacerts` /
`istio-csr-ca-configmap` / `istio-csr-dns-cert` volumes it cites are unconditional `optional: true`
volumes in the stock istiod chart and prove nothing. The estate is actually attempting the documented
[istio.io/SPIRE Workload API socket integration](https://istio.io/latest/docs/ops/integrations/spire/)
— `spiffe-csi-driver` is enabled and `csi.spiffe.io` is wired — decorated with two istio-csr-shaped
settings that don't belong.

**Root cause:** `estate/platform/identity/istio/helmrelease.yaml:57` sets `ENABLE_CA_SERVER: "false"`.
With no istio-csr certs present, istiod never calls `initIstiodCertLoader()`; the bundle watcher stays
empty → `Failed to load CA bundle: could not decode pem` → webhook patch fails → `tls: internal error`.

**Also required (each would still block on its own):**
- add `meshConfig.trustDomain: acme.internal` — SPIRE is `acme.internal`, Istio defaults to
  `cluster.local`, so every `spiffe://acme.internal/...` principal currently fails to match;
- delete `global.caName: SPIRE` (`helmrelease.yaml:52`) — a no-op in 1.24, and see ticket 01: the
  verifier asserts it;
- give the `spire` injection template the `spiffe.io/spire-managed-identity: "true"` label block.

Do **not** install istio-csr: ~1 hour this way versus 1–2 days, three extra deployments and four more
images to pre-seed. Ordering: SPIRE + CSI driver Ready → istiod → workloads.

Verify istiod comes up, the webhook serves, and a meshed pod schedules with an SVID.
