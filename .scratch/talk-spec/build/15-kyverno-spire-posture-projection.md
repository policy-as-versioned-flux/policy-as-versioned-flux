# 15 — Kyverno → SPIRE posture projection

**What to build:** Kyverno `mutate` stamps a trust-bounded posture label at admission; a `ClusterSPIFFEID` template bakes posture into the SVID *path* (`spiffe://…/posture/vN/…`). User-supplied posture labels are rejected — the trust-boundary.

**Blocked by:** 03, 14

**Status:** done (2026-08-20) — live-proven end to end on `kind-driftwood` (see mo-11 Comments below)

- [x] A pod admitted under vN gets an SVID whose path carries `posture/vN` — `ClusterSPIFFEID` template check (`verify-posture-projection.sh` step 3): `template carries a /posture/ path segment`, `posture segment LEADS the path (before /ns/)`, `posture path is derived from the Kyverno-stamped label, not free text`
- [x] The posture label is settable only by the trusted Kyverno policy (validate-reject user-supplied `posture.*` + RBAC) — `kyverno test tests/stamp-posture` (step 1) + `kyverno test tests/posture-trust-boundary` (step 2) both pass against the real CEL policy bodies
- [x] Forging the label is refused (verified) — step 2: `posture-trust-boundary DENIES a forged/mismatched posture`

## Comments

- 2026-08-20 (audit mo-02): all 3 ACs are proven by real `kyverno test` runs against the actual CEL policy bodies plus a structural check of the `ClusterSPIFFEID` template — not mocks. Steps 4-6 (live: policies actually installed, a hand-crafted forged pod actually denied at admission, an actual SVID minted) self-skip: `no cluster with the posture policies at context 'kind-driftwood'` (no cluster in this environment, see ticket 02) — and this ticket is blocked by ticket 14, whose Istio↔SPIRE CA bootstrap is still broken live, so nobody has live-proven an admitted pod actually receiving a `posture/vN` SVID yet. Marked `done` on the offline proof (the repo's own house standard for these beats), not `ready-for-agent`, since that undersold real, working code.
- 2026-08-20 (mo-11): live tail now runs and passes for real, not just self-skips. With Kyverno installed
  (this ticket had never had an engine to admit against) and two more live-only bugs fixed (SPIRE
  `ClusterSPIFFEID.className` — this object and the base identity's were both silently unreconciled
  since day one; the base/posture podSelector overlap), a real pod (`teller-current`, claims
  `policy-version 2.0.0`) is admitted by Kyverno, gets `posture.acme.io/version=2.0.0` stamped, and
  receives a SPIRE-signed `spiffe://acme.internal/posture/2.0.0/ns/tuppence-reset/sa/teller-current`
  SVID — confirmed via `spire-server entry show` and `pilot-agent request GET certs` on the pod's own
  sidecar (CA serial matches `spire-bundle`'s). Full account in
  `.scratch/multi-org-estate/issues/11-prove-28-of-28-live.md`.
