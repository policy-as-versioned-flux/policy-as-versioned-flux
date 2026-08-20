# 17 — Posture-gated reach + secrets (workload flagship)

**What to build:** `customer-accounts-reset` (`tuppence`) accepts only callers whose SVID attests the current policy version (Istio `AuthorizationPolicy`); OpenBao issues its credential only to current-posture identities. A caller drifting out of currency loses reach **and** its secret — live.

**Blocked by:** 08, 15, and (newly discovered) **14 — identity substrate live** (see below).

**Status:** REOPENED — NOT DONE. Built + offline/negative-proven, but the **live positive path is blocked**. Do not close until it passes live. (Live bring-up 2026-07-31.)

- [x] Istio `AuthorizationPolicy` matches `source.principals` on the posture-path prefix — built; ALLOW-only; selects the service; manifests valid (offline).
- [x] OpenBao JWT role gates its secret on the posture path (`bound_claims` glob) — built.
- [ ] `verify-*.sh`: a current caller reaches the service + gets the secret; an out-of-currency caller is refused *both* — **PARTIAL**: out-of-currency is correctly refused *both* live; **the current caller does NOT reach live** (FAIL). This criterion is unmet.

## Reopened 2026-07-31 — live reach BLOCKED (do not close)

Estate brought up live (`estate/talk/verify-all.sh --live`): **27/28 beats pass; this is the 1 fail.**

- **Negative half works live** — stale / de-postured / lookalike SVIDs are refused reach *and* the secret. The AuthorizationPolicy + OpenBao gating are correct.
- **Positive half cannot run** — the `customer-accounts-reset` / `teller-*` workloads **never start**: pod creation is rejected by the Istio sidecar-injection webhook — `failed calling webhook "…sidecar-injector.istio.io": … istiod …: remote error: tls: internal error`.
- **Root cause is in ticket 14 (identity substrate):** istiod runs with `ENABLE_CA_SERVER=false` + istio-csr and cannot bootstrap its webhook serving cert / CA bundle from SPIRE — istiod logs `Failed to load CA bundle: could not decode pem` → `patching webhook istio-sidecar-injector failed`. No sidecar → no SVID → no reach.
- **Progress made:** fixed the SPIRE chart-0.24.0 breaking value renames (commit `f7f6732`) — SPIRE now installs and all four pods run. The remaining blocker is the **SPIRE → istio-csr → istiod CA wiring**.

**Definition of done (to close):** in `estate/tuppence/reset/verify-reach-secrets.sh` against a real cluster, a current-posture caller gets `200` from `customer-accounts-reset` **and** pulls its OpenBao secret, while an out-of-currency caller is refused both. That requires the istio-csr/SPIRE CA bootstrap (ticket 14) fixed so mesh workloads receive sidecars + SVIDs.

## Comments

- 2026-08-20 (audit mo-02): re-audited. No commit touches `estate/platform/identity/` or `estate/tuppence/reset/` since `f7f6732` (2026-07-31), so ticket 14's blocker is still open and this ticket's live positive path is still unproven — REOPENED status stands. Re-ran `bash estate/tuppence/reset/verify-reach-secrets.sh` offline: still PASSes cleanly (current SVID reaches + gets secret, stale/de-postured/lookalike SVIDs refused both — all *simulated*, not live), matching the ticket's own "offline/negative-proven" framing exactly. No live cluster was available in this audit environment to re-attempt the 2026-07-31 repro. Status and AC ticks left unchanged — this is the other of the two tickets the audit (`.scratch/multi-org-estate/issues/02-tracker-status-audit.md`) already named as honest.
