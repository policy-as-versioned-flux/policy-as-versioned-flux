# 17 — Posture-gated reach + secrets (workload flagship)

**What to build:** `customer-accounts-reset` (`tuppence`) accepts only callers whose SVID attests the current policy version (Istio `AuthorizationPolicy`); OpenBao issues its credential only to current-posture identities. A caller drifting out of currency loses reach **and** its secret — live.

**Blocked by:** 08, 15, and (newly discovered) **14 — identity substrate live** (see below).

**Status:** partial (2026-08-20) — the **reach** half is now live-proven both ways; the **secret**
(OpenBao) half is still only offline-proven both ways. Do not close until the secret half is
independently live-proven too. (Live bring-up 2026-07-31; reach fixed live 2026-08-20, see mo-11.)

- [x] Istio `AuthorizationPolicy` matches `source.principals` on the posture-path prefix — built; ALLOW-only; selects the service; manifests valid (offline).
- [x] OpenBao JWT role gates its secret on the posture path (`bound_claims` glob) — built.
- [~] `verify-*.sh`: a current caller reaches the service + gets the secret; an out-of-currency caller is refused *both* — **reach: DONE live** (2026-08-20, mo-11): current caller `200`, stale caller `403`, confirmed against the real `verify-reach-secrets.sh` live tail, not hand-run. **secret: still offline-only** — `verify-reach-secrets.sh` step 4 self-skips (`teller-current`/`teller-stale` run `curlimages/curl`, no `spire-agent` CLI in-pod to mint a JWT-SVID); the glob-agreement + admit/refuse matrix is proven offline from the real manifests and OpenBao's jwt-auth→SPIRE-OIDC wiring is proven structurally, but no live `bao write auth/jwt/login` has actually run. This is the one remaining unmet criterion.

## Reopened 2026-07-31 — live reach BLOCKED (do not close)

Estate brought up live (`estate/talk/verify-all.sh --live`): **27/28 beats pass; this is the 1 fail.**

- **Negative half works live** — stale / de-postured / lookalike SVIDs are refused reach *and* the secret. The AuthorizationPolicy + OpenBao gating are correct.
- **Positive half cannot run** — the `customer-accounts-reset` / `teller-*` workloads **never start**: pod creation is rejected by the Istio sidecar-injection webhook — `failed calling webhook "…sidecar-injector.istio.io": … istiod …: remote error: tls: internal error`.
- **Root cause is in ticket 14 (identity substrate):** istiod runs with `ENABLE_CA_SERVER=false` + istio-csr and cannot bootstrap its webhook serving cert / CA bundle from SPIRE — istiod logs `Failed to load CA bundle: could not decode pem` → `patching webhook istio-sidecar-injector failed`. No sidecar → no SVID → no reach.
- **Progress made:** fixed the SPIRE chart-0.24.0 breaking value renames (commit `f7f6732`) — SPIRE now installs and all four pods run. The remaining blocker is the **SPIRE → istio-csr → istiod CA wiring**.

**Definition of done (to close):** in `estate/tuppence/reset/verify-reach-secrets.sh` against a real cluster, a current-posture caller gets `200` from `customer-accounts-reset` **and** pulls its OpenBao secret, while an out-of-currency caller is refused both. That requires the istio-csr/SPIRE CA bootstrap (ticket 14) fixed so mesh workloads receive sidecars + SVIDs.

## Comments

- 2026-08-20 (audit mo-02): re-audited. No commit touches `estate/platform/identity/` or `estate/tuppence/reset/` since `f7f6732` (2026-07-31), so ticket 14's blocker is still open and this ticket's live positive path is still unproven — REOPENED status stands. Re-ran `bash estate/tuppence/reset/verify-reach-secrets.sh` offline: still PASSes cleanly (current SVID reaches + gets secret, stale/de-postured/lookalike SVIDs refused both — all *simulated*, not live), matching the ticket's own "offline/negative-proven" framing exactly. No live cluster was available in this audit environment to re-attempt the 2026-07-31 repro. Status and AC ticks left unchanged — this is the other of the two tickets the audit (`.scratch/multi-org-estate/issues/02-tracker-status-audit.md`) already named as honest.
- 2026-08-20 (mo-11): the live positive path is unblocked. Fixing ticket 14's istiod bootstrap (mo-04)
  got ping/pong meshed, but reach here needed four more live-only fixes on top: (1) the
  `spiffe://spiffe://...` double-scheme bug in `authorizationpolicy.yaml` that mo-04 diagnosed on
  `demo-mtls` and explicitly left for this ticket — fixed here too; (2) `ClusterSPIFFEID.className`
  missing on both `mesh-base` and `posture` — neither was ever actually reconciled by
  spire-controller-manager since either was first applied, no error, just silently zero entries
  forever; (3) `tuppence/reset/workloads.yaml` never carried the `inject.istio.io/templates:
  "sidecar,spire"` annotation mo-04 added only to `demo-mtls` — without it the sidecar falls back to
  istiod's own Citadel CA, a same-shaped-but-fake cert that never carries posture; (4) once the real
  posture SVID reached the wire, istiod's *auto-generated* peer-SAN pin on the caller's outbound
  cluster (derived from the destination's plain ServiceAccount, `ns/<ns>/sa/<sa>`) rejected it at the
  TLS layer — fixed with a `DestinationRule` overriding `subjectAltNames` to the real posture-shaped
  SAN. Result: `teller-current` (2.0.0) reaches `customer-accounts-reset` live (`200`); `teller-stale`
  (1.0.0) is refused live (`403`) — both against the real `verify-reach-secrets.sh`, not hand-run.
  The secret (OpenBao) half of this ticket's own AC is **still not independently live-proven** — see
  the Status line and `.scratch/multi-org-estate/issues/11-prove-28-of-28-live.md` for the full
  account and why. Not closing; narrowing what's left.
