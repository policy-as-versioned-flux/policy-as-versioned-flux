# 17 — Posture-gated reach + secrets (workload flagship)

**What to build:** `customer-accounts-reset` (`tuppence`) accepts only callers whose SVID attests the current policy version (Istio `AuthorizationPolicy`); OpenBao issues its credential only to current-posture identities. A caller drifting out of currency loses reach **and** its secret — live.

**Blocked by:** 08, 15

**Status:** ready-for-agent

- [ ] Istio `AuthorizationPolicy` matches `source.principals` on the posture-path prefix
- [ ] OpenBao JWT role gates its secret on the posture path (`bound_claims` glob)
- [ ] `verify-*.sh`: a current caller reaches the service + gets the secret; an out-of-currency caller is refused *both*
