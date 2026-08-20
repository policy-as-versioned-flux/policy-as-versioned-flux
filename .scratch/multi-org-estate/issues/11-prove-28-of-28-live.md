# 11 — Close talk-spec 15 and 17: prove the posture-gated beat live

Type: task
Status: partial (2026-08-20) — the full posture-gated chain is built, installed, and proven live
  end-to-end. Talk-spec 15 closes for real (done, all 3 ACs live-proven). Talk-spec 17's reach half
  is now live-proven too, but the ticket itself stays partial — its secret/OpenBao half is still
  only offline-proven, per ticket 17's own "do not close" instruction. `verify-all.sh --live` is
  25 pass / 3 fail, not 28/28 — the specific unmet part is named in Comments
Blocked by: 04

## Question

With istiod fixed (ticket 04), close out the rest of the live identity chain and get an honest
28/28.

**Ticket 15 (Kyverno → SPIRE posture projection) has never run.** All three of its ACs are unchecked,
and nothing in the repo installs Kyverno or flux-operator at all — no HelmRelease, no `helm install`,
while `estate/driftwood/README.md` names both as prerequisites. Install them following the existing
five-HelmRelease pattern (`spire`, `istio`, `openbao`, `pomerium`, `dex`), ordered before the posture
layer.

Then the chain that must actually work: Kyverno admits a pod → `stamp-posture` mutate stamps
`posture.acme.io/version` → the posture `ClusterSPIFFEID` matches → the pod gets
`spiffe://acme.internal/posture/2.0.0/...` → the Istio `AuthorizationPolicy` admits it and the OpenBao
`bound_claims` glob releases the secret; a stale or de-postured SVID is refused both.

Note ticket 01 fixes this beat's guard so it can no longer pass by not looking — so a green here will
mean something. Record the real `verify-all.sh --live` count.

## Comments

Partial 2026-08-20. Installed Kyverno + flux-operator as Flux HelmReleases (`estate/platform/engine/`,
new — chart 3.8.2/appVersion 1.18.2 for Kyverno matching ADR-0003's `>=1.18` floor and the `kyverno`
CLI already used offline; ControlPlane's flux-operator via `oci://ghcr.io/controlplaneio-fluxcd/charts/
flux-operator` 0.58.1, no `FluxInstance` created so the cluster's existing vanilla Flux stays untouched
— ADR-0005's guardrail), ordered before the posture layer in `estate/talk/up.sh`. Both live on
`kind-driftwood`, `verify-engine.sh` green offline+live.

**The chain now runs live, start to finish, on `kind-driftwood`** — this is the headline result:
a `teller-current` pod (claims `policy-version 2.0.0`) is admitted by Kyverno, `stamp-posture` mutates
`posture.acme.io/version=2.0.0` onto it (confirmed: pod label), the posture `ClusterSPIFFEID` matches
and spire-controller-manager mints `spiffe://acme.internal/posture/2.0.0/ns/tuppence-reset/sa/
teller-current` (confirmed: `spire-server entry show`, and `pilot-agent request GET certs` on the
pod's own sidecar shows that exact URI signed by SPIRE's real CA — serial matches `spire-bundle`), the
Istio `AuthorizationPolicy` admits it (curl from the pod: **200**), `teller-stale` (claims `1.0.0`) is
refused (curl: **403**). `estate/tuppence/reset/verify-reach-secrets.sh`'s own live tail (step 3, not
hand-run — the packaged script) now passes for real instead of self-skipping. `ping -> pong` (the
ticket-04 leftover) is also live-green now: **200**, was 403 all session.

None of this ran on the first attempt. Getting from "policies installed" to "actually admits over real
mTLS" surfaced four more real, live-only bugs — the project's own thesis (governance tools lie by
showing green ticks) proving out one more time:

1. **The `spiffe://spiffe://...` double-scheme bug ticket 04 named and explicitly left for this
   ticket** — `demo-mtls/authorizationpolicy.yaml` and `tuppence/reset/authorizationpolicy.yaml` both
   wrote `principals: ["spiffe://acme.internal/..."]`; Istio's schema wants the scheme-less
   `<trustDomain>/ns/<ns>/sa/<sa>` form and prepends `spiffe://` itself, so the rendered RBAC matcher
   was the unmatchable `spiffe://spiffe://...`. Fixed in both files; `verify-identity.sh`'s offline
   check updated to assert the scheme-less form (and assert it's *not* double-prefixed);
   `reset/reach.py`'s selfcheck updated to reproduce Istio's own prepend before comparing the two
   surfaces' globs (they're no longer byte-identical strings — Istio's is scheme-less, OpenBao's
   `bound_claims` matches the JWT `sub` claim, which genuinely is the full `spiffe://` URI — the
   invariant checked is "same version prefix", not "same bytes").
2. **`ClusterSPIFFEID` `className` — both `mesh-base` and `posture` were completely inert since the
   day they were first applied.** The spire chart scopes its controller-manager to className
   `<release-namespace>-<release-name>` (`spire-system-spire`) and runs with `handle crs without
   class name: false`. Neither hand-authored `ClusterSPIFFEID` carried a `className`, so neither was
   *ever* reconciled — no error, `.status.stats` just stayed empty forever. The base-identity SVIDs
   the estate had been crediting to `mesh-base` were actually coming from the spire chart's own
   auto-created fallback `ClusterSPIFFEID` (`spire-system-spire-default`, no podSelector, same
   template shape) — confirmed by reading its live spec. Fixed by adding `className: spire-system-spire`
   to both; `.status.stats.entriesToSet` went from unset to matching `podsSelected` immediately.
3. **`mesh-base` and `posture` selectors overlapped, and which entry Envoy ended up presenting was
   non-deterministic.** A posture-managed pod matched both, giving it two live SPIRE entries on the
   identical `(parentID, k8s:pod-uid)` selector; SPIRE creates both fine, but Envoy's SDS "default"
   request only ever returns one. Isolated this properly (not just inferred): with #2 and #4 both
   fixed, deleting and recreating the *same* `teller-current` pod spec repeatedly — same two entries
   each time — flipped the presented identity between base and posture across restarts (confirmed
   live, `pilot-agent request GET certs` on each fresh pod: posture → 200 reach, then base → 403, no
   code change in between). Fixed by making `mesh-base` exclude posture-managed pods
   (`posture.acme.io/version` `DoesNotExist`), so a pod holds exactly one live SPIRE entry and there is
   nothing to flip between — matching `tuppence/reset/README.md`'s own existing description of ticket
   16 ("de-postured → drops to *the* base SVID", singular). Re-verified deterministic across further
   restarts with the exclusion in place.
4. **The actual blocker: `tuppence/reset/workloads.yaml` never carried the
   `inject.istio.io/templates: "sidecar,spire"` annotation.** Ticket 04 added this to `demo-mtls/
   workloads.yaml` and said explicitly it was leaving `tuppence/reset` untouched. Without it, sidecar
   injection silently falls back to the base `sidecar` template's non-CSI `workload-socket` `EmptyDir`,
   and the proxy gets a same-shaped-but-fake cert from istiod's own Citadel CA instead of SPIRE — the
   exact ticket-04 failure mode, reproduced here. Confirmed live: the posture SVID minted correctly
   server-side the whole time, but the pod's *actual* mTLS certificate never carried it, and the
   issuing CA's serial didn't match `spire-bundle`'s. Fixed by adding the annotation to all three
   `tuppence-reset` workloads; the CA serial now matches and the SAN carries `posture/2.0.0`.
5. **A new problem #4 exposed once the posture SVID actually reached the wire:** istiod auto-generates
   each outbound mTLS cluster's expected peer SAN from the destination's Kubernetes ServiceAccount,
   using Istio's own standard `spiffe://<trustDomain>/ns/<ns>/sa/<sa>` shape — regardless of what
   SPIRE actually issues. `customer-accounts-reset`'s real SVID carries the posture-prefixed path, so
   every caller's outbound cluster rejected it at the TLS layer (`CERTIFICATE_VERIFY_FAILED`,
   surfaced as a 503 — the AuthorizationPolicy never even reached). Confirmed via `pilot-agent request
   GET config_dump`: the auto-derived cluster carried `match_subject_alt_names: [exact: "spiffe://
   acme.internal/ns/tuppence-reset/sa/customer-accounts-reset"]`, the un-postured shape. Fixed with a
   new `DestinationRule` (`tuppence/reset/destinationrule.yaml`) overriding `subjectAltNames` to the
   real posture-shaped SAN — `mode: ISTIO_MUTUAL` keeps SDS-provisioned SPIRE certs. (Upstream reports
   say this override isn't honoured for `ISTIO_MUTUAL`; it works as tested here on Istio 1.24 —
   403→200, confirmed live.)

**What's still not independently live-proven, and why (the honest gap):** the OpenBao half of "a
current caller reaches + gets the secret; a stale caller is refused both" — the *reach* half of that
sentence is fully live-proven both ways (200 / 403 above); the *secret* half is proven **offline**
(the glob-agreement + admit/refuse matrix, parsed from the real manifests) and **structurally**
(`verify-identity.sh` confirms OpenBao's jwt auth is wired to SPIRE's OIDC JWKS), but not independently
exercised live end-to-end through an actual `bao write auth/jwt/login`. `verify-reach-secrets.sh`'s own
step 4 self-skips exactly as its own comment says it will: `teller-current`/`teller-stale` run
`curlimages/curl`, which has no `spire-agent` CLI to mint a JWT-SVID, so there's no in-pod tool to
fetch one and hand it to OpenBao. I tried swapping the caller container's image for `spire-agent`
directly (`kubectl debug --copy-to`) to work around this; it hit its own dead end (the `caller`
container in this pod template has no volume mount for the SPIRE workload socket at all — only
`istio-proxy` does — so swapping its image doesn't grant it agent access) and I stopped rather than
restructure the workload just to make a test possible. The underlying mechanism is not in doubt (it's
the identical SPIRE registration entry the now-live-proven X.509 SVID already rides on, just requested
as a JWT instead) but "not in doubt" is exactly the standard ticket 01 exists to reject, so this is
named as unproven, not glossed over.

**`estate/talk/verify-all.sh --live`, the real count: `pass=25 fail=3 skip-live=0`** — not 28/28.
Both `driftwood`/`tuppence`/`ludlow` reconcile beats pass live (the literal "3/3" the ticket asked
for), so all 28 slots ran (none skipped); three that ran came back red:

- `posture-gated reach + secrets (tuppence flagship)` — **PASS**, the ticket's own target beat.
- `identity substrate: SPIRE is Istio's CA, mTLS STRICT` — **PASS** (ping→pong now 200 too).
- `policy is a versioned dependency (coexistence)` — **FAIL**: `require-nonroot-1.0.0 not installed
  live (fan-out incomplete)`. Its live tail (`verify-coexistence.sh:29`) gates on `kubectl get
  validatingpolicy` succeeding, i.e. on Kyverno's CRDs existing — before this ticket that gate always
  failed closed and the check *skipped*; now that Kyverno is installed it correctly *looks* and finds
  the distribution `ResourceSet` fan-out was never applied live. That's real and was always true; it's
  ticket 09/10's live-bring-up territory (`estate/platform/distribution/README.md`'s own "Live
  bring-up — prerequisites" section already named this as separate, out-of-scope work), newly visible
  rather than newly broken. Not fixed here — installing the full version-array fan-out live is a
  materially different, larger task than this ticket's own scope.
- `human/device access plane holds (Pomerium+device SVID)` — **FAIL**: `Pomerium pod not present`.
  Pre-existing and unrelated to this ticket: the `access` namespace and Dex have been live on this
  cluster for 19 days, Pomerium never was (ticket 18/19 territory). This was already red before this
  ticket touched anything; not fixed here.
- `the number is honest today (calibration+integrity)` — **FAIL**: `reflexive selfcheck failed`.
  Ticket 25's already-documented, already-diagnosed bug (`signing_key_present` checks the wrong key
  file); explicitly not this ticket's to fix, same as ticket 01 declined to touch the one
  `wardley.py` vacuity delegated to another in-flight ticket.

So: talk-spec 15 closes for real; talk-spec 17's reach half now closes live too, but the ticket
itself stays partial, since its secret half is still only offline-proven. The honest live count is
25/28 not 28/28, and every point of the gap is named and attributed to the ticket that actually owns
it — which is the more useful number than a false 28/28 would have been.

Files touched: `estate/platform/engine/` (new — `namespaces.yaml`, `kyverno/helmrelease.yaml`,
`flux-operator/helmrelease.yaml`, `up.sh`, `verify-engine.sh`, `README.md`),
`estate/platform/identity/demo-mtls/authorizationpolicy.yaml`,
`estate/platform/identity/spire/clusterspiffeid-mesh.yaml`, `estate/platform/identity/verify-identity.sh`,
`estate/platform/posture/spire/clusterspiffeid-posture.yaml`,
`estate/platform/posture/verify-posture-projection.sh`, `estate/tuppence/reset/authorizationpolicy.yaml`,
`estate/tuppence/reset/destinationrule.yaml` (new), `estate/tuppence/reset/workloads.yaml`,
`estate/tuppence/reset/reach.py`, `estate/tuppence/reset/up.sh`, `estate/talk/up.sh`, plus README
cross-references (`estate/platform/distribution/README.md`, `estate/platform/posture/README.md`,
`estate/tuppence/reset/README.md`).
