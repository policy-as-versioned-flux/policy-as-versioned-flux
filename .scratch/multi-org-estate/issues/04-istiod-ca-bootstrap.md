# 04 — Fix the istiod CA bootstrap so meshed pods can start

Type: task
Status: partial (2026-08-20) — istiod CA bootstrap fixed and live-verified; ping→pong mTLS
  end-to-end still 403s on a separate, pre-existing AuthorizationPolicy bug (see Comments)
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

## Comments

Partial 2026-08-20. All four named fixes landed in `estate/platform/identity/istio/helmrelease.yaml`
and were applied live to `kind-driftwood` (the only cluster running this substrate — `kind-tuppence`
and `kind-ludlow` carry no `istio-system`/`spire-system` namespaces at all; `estate/README.md` and
`estate/platform/identity/README.md` both scope this substrate to driftwood, and ticket 11, blocked
by this one, frames itself as closing out "the rest of the **live identity chain**" on top of it):

1. `pilot.env.ENABLE_CA_SERVER: "false"` deleted (chart default is `true` — confirmed via
   `helm show values oci://gcr.io/istio-release/charts/istiod --version 1.24.0`, and Istio's own
   source, `pilot/pkg/features/pilot.go`: `EnableCAServer = env.Register("ENABLE_CA_SERVER", true, ...)`).
   Live before the fix: `istiod` logged `Failed to load CA bundle: could not decode pem` /
   `patching webhook istio-sidecar-injector failed` every 60s, and the injection webhook 100%-failed
   every pod create for 19 days (`tls: internal error`, then `connection refused` after a fresh
   restart) — reproduced and captured before touching anything.
2. `meshConfig.trustDomain: acme.internal` added (was defaulting to `cluster.local`).
3. `global.caName: SPIRE` deleted — confirmed via `helm show values` that Istio 1.24's own `caName`
   default is `""` and the field is undocumented for SPIRE integration; ticket 01 already flagged it
   a no-op.
4. The `spire` injection template gained the `spiffe.io/spire-managed-identity: "true"` `labels:`
   block, matching istio.io's own SPIRE doc verbatim (fetched and diffed against the repo's existing
   template before editing).

**A fifth fix, inside this ticket's own success bar, not just the four named settings:**
`estate/platform/identity/demo-mtls/workloads.yaml` labelled `ping`/`pong` for SPIRE's
`ClusterSPIFFEID` podSelector but never told Istio's injector to *apply* the custom `spire` template —
that's a separate opt-in, the `inject.istio.io/templates: "sidecar,spire"` pod annotation (istio.io's
own example workload carries it; ours didn't). Without it, injection silently fell back to the base
`sidecar` template's own built-in (non-CSI) `workload-socket` `EmptyDir`, and the proxy got a
same-shaped-but-fake `spiffe://acme.internal/...` cert from istiod's Citadel CA instead of SPIRE —
confirmed by comparing the issuing CA's certificate serial against `spire-bundle`'s: they didn't
match until this annotation was added. Added the annotation to both Deployments; re-verified the
serial now matches SPIRE's root exactly.

**Live-verified on `kind-driftwood`, this run, repeatable (see `verify-identity.sh`, 27/28 live+offline
checks green):**
- istiod: `availableReplicas` ≥ 1, no more CA-bundle errors in its logs.
- the webhook serves: `mutatingwebhookconfiguration istio-sidecar-injector`'s `caBundle` populated
  (1468 bytes, was empty); `ping`/`pong` pods that had sat at `0/2` `FailedCreate` for 19 days now
  inject cleanly and run `2/2`.
- a meshed pod schedules with a **real** SPIFFE SVID: `pilot-agent request GET certs` on `ping`'s and
  `pong`'s sidecars shows a leaf `spiffe://acme.internal/ns/mesh-demo/sa/{ping,pong}` SAN, and the
  issuing CA cert's serial (`23aeb547856a2588903e31f7b4e05d58`) exactly matches
  `spire-bundle`'s (`kubectl -n spire-system get cm spire-bundle -o jsonpath='{.data.bundle\.crt}' |
  openssl x509 -noout -serial`) — SPIRE-issued, not istiod's fallback Citadel CA.

**What's still red, and not this ticket's to fix:** `ping -> pong over SPIFFE mTLS` still 403s.
Both proxies hold genuine SPIRE SVIDs and speak real STRICT mTLS (the TLS handshake succeeds — this
is Envoy's RBAC filter, not a cert failure), but `demo-mtls/authorizationpolicy.yaml`'s
`principals: ["spiffe://acme.internal/ns/mesh-demo/sa/ping"]` carries the full `spiffe://` scheme.
Istio's `AuthorizationPolicy` schema wants the scheme-less `<trustDomain>/ns/<ns>/sa/<sa>` form and
prepends `spiffe://` itself (confirmed against
https://istio.io/latest/docs/reference/config/security/authorization-policy/, whose own example is
`principals: ["cluster.local/ns/default/sa/sleep"]`), so the rendered Envoy RBAC matcher is the
unmatchable `spiffe://spiffe://acme.internal/...` (read straight off `pilot-agent request GET
config_dump` on `pong`). This bug predates this ticket, is outside the four named settings and the
one file the ticket names, and was never exposed before today because nothing ever got this far
live. Left named, not fixed, for ticket 11 ("close out the rest of the live identity chain") — the
same file also carries a matching pattern in `estate/tuppence/reset/authorizationpolicy.yaml`,
not touched here.

Also fixed in passing, discovered while making the new live checks reliable: several
`kubectl ... | grep -q pattern` / `| head -1` lines in `verify-identity.sh`'s live section flip
`FAIL` on a coin-flip — `grep -q`/`head` exit on first match, SIGPIPE-killing the still-writing
`kubectl` on the other end, and `set -o pipefail` turns that into a nonzero pipeline exit regardless
of the match. Reproduced it going red on a cluster that was plainly fine (`SPIRE pods not present`
against a namespace with four SPIRE pods Running). Rewrote every live check to capture kubectl's
output into a variable first, then grep/head the variable — a ticket-01-shaped bug (a gate whose
failure meant nothing), just newly-triggered rather than newly-introduced, since the live branch was
never exercised against a genuinely populated cluster before this ticket.

Also found and worked around, not a code change: `spire-agent` was in `CrashLoopBackOff`
(`x509: certificate signed by unknown authority` against `spire-server`, stale SVID cached in its
pod-lifetime `emptyDir` from before the KinD containers were restarted). Deleted the pod once;
the DaemonSet recreated it clean and it's been `1/1 Running`, 0 restarts, since. Pre-existing
cluster-state flakiness, not a manifest bug — no repo file changed for this.

Files touched: `istio/helmrelease.yaml` (the four named fixes), `demo-mtls/workloads.yaml` (the
fifth), `verify-identity.sh` (updated assertions to match the new config + fixed the SIGPIPE
flakiness + three new live checks), `README.md` and `up.sh` (stale `caName: SPIRE` prose corrected
to match).
