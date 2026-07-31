# 15 — Kyverno → SPIRE posture projection

**What to build:** Kyverno `mutate` stamps a trust-bounded posture label at admission; a `ClusterSPIFFEID` template bakes posture into the SVID *path* (`spiffe://…/posture/vN/…`). User-supplied posture labels are rejected — the trust-boundary.

**Blocked by:** 03, 14

**Status:** ready-for-agent

- [ ] A pod admitted under vN gets an SVID whose path carries `posture/vN`
- [ ] The posture label is settable only by the trusted Kyverno policy (validate-reject user-supplied `posture.*` + RBAC)
- [ ] Forging the label is refused (verified)
