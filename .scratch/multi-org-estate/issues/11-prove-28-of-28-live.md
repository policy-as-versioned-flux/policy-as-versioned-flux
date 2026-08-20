# 11 — Close talk-spec 15 and 17: prove the posture-gated beat live

Type: task
Status: open
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
