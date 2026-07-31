# Research: Kyverno → SPIRE posture projection (the non-trodden hand-off)

Type: research
Status: resolved
Blocked by: 16

## Question

De-risk the one non-standard integration in the posture-as-identity design (ticket 16): **how does
policy posture, recorded by Kyverno at admission, become a claim/selector on a workload's
SPIFFE/SPIRE SVID that Istio `AuthorizationPolicy` and OpenBao can gate on?**

Investigate against primary sources (SPIRE/SPIFFE docs, `spiffe/spire-controller-manager`,
`ClusterSPIFFEID` CRD, Istio SPIRE integration, Kyverno mutate/generate + attestation verification,
OpenBao/Vault SPIFFE/JWT/cert auth):

1. SPIRE identity assignment in k8s — workload attestation, selectors, `ClusterSPIFFEID`, how SVID
   SANs/claims/selectors derive from pod/namespace/SA attributes.
2. The realistic hand-off — can Kyverno (generate/mutate) create/patch a `ClusterSPIFFEID` or pod/SA
   labels that the SPIRE controller-manager turns into an SVID selector reflecting posture, or is a
   custom attestor/plugin needed? Options + tradeoffs.
3. Istio `AuthorizationPolicy` matching on SPIFFE identity / claims — can custom posture claims reach
   the authz context (principals, `request.auth.claims`, SVID path segments)?
4. OpenBao/Vault auth of SPIFFE identities + gating secret issuance on a posture attribute.
5. Gaps / bleeding-edge vs solved, and the simplest viable wiring for a KinD demo.

Output: cited findings at `research/16-posture-identity-spire.md` with a feasibility verdict +
recommended wiring, honest about uncertainty.

## Answer (2026-07-23) — resolved

**Feasible on KinD, natively, no custom SPIRE plugin. Posture lives in the SPIFFE ID *path*, not a
claim.** Wiring: Kyverno `mutate` stamps a `posture.<org>/version` label at admission → one
`ClusterSPIFFEID` whose `spiffeIDTemplate` reads the label and bakes posture into the SVID URI
(`spiffe://td/posture/vN/ns/../sa/..`) → `spire-controller-manager` reconciles ≤10s → the signed SVID
URI *is* the posture. **Istio** gates `source.principals: ["spiffe://td/posture/vN/*"]`; **OpenBao**
via a `jwt` role (`bound_claims_type=glob`, `bound_claims={"/sub":"spiffe://td/posture/vN/*"}`);
short-TTL JWT-SVIDs (~5m) for snappy revocation. Full detail + citations:
[`research/16-posture-identity-spire.md`](../research/16-posture-identity-spire.md).

**Two components this forces into the (B) build:**
1. **Currency controller** — Kyverno fires only at admission, so posture is a *snapshot*. A small
   controller must re-evaluate currency and re-patch/evict as versions age. **Thesis-critical:**
   runtime posture must re-tune as the world moves, not freeze at admit.
2. **Posture-label trust-boundary** — the `posture.*` label must be settable only by the trusted
   Kyverno policy (validate-reject user-supplied posture labels + RBAC), else posture is forgeable.

**Head-start:** ControlPlane's own `getting-started-spire-openbao` already does SPIRE JWT-SVID →
OpenBao JWT auth (Linux-local, no controller-manager/KinD) — a proven base to extend. (Sponsor
synergy — worth a nod in the talk.)
