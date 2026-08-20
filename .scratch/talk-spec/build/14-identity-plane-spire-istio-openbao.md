# 14 — Identity plane: SPIRE + Istio + OpenBao

**What to build:** SPIRE (with `spire-controller-manager`), Istio (SPIRE-integrated), and OpenBao stood up as inherited `platform` machinery — the runtime-identity + secret substrate. Extend ControlPlane's `getting-started-spire-openbao`.

**Blocked by:** 02

**Status:** REOPENED — NOT DONE. Substrate installs but Istio↔SPIRE CA bootstrap is broken live (see below). Blocks ticket 17.

- [x] SPIRE + `spire-controller-manager` issuing SVIDs — installs; all 4 SPIRE pods Running (after the chart fix below). OpenBao running.
- [ ] Istio consuming SPIRE identity — **BROKEN live:** istiod cannot bootstrap its webhook cert / CA bundle from SPIRE.
- [ ] mTLS between meshed workloads on SPIFFE identity — **unmet:** mesh workloads can't get sidecars, so no workload mTLS.
- [x] Delivered as inherited platform machinery (Flux HelmReleases; istio-base/istiod/openbao/spire-crds all `True`).

## Reopened 2026-07-31 — Istio↔SPIRE CA bootstrap BLOCKED (do not close)

Live bring-up (`verify-all.sh --live`) exposed two real bugs in this substrate:

1. **SPIRE chart 0.24.0 breaking value renames — FIXED (commit `f7f6732`).** Chart camelCased its values with hard `fail()` guards (`ca_subject`→`caSubject`, `caSubject.common_name`→`commonName`; the chart's own error text misreports the second as "ca_name"). The HelmRelease used the old snake_case names, so SPIRE never installed. Fixed → SPIRE now installs, all four pods Running.
2. **istio-csr / SPIRE CA bootstrap — STILL BROKEN.** istiod runs with `ENABLE_CA_SERVER=false` + istio-csr (`cacerts` / `istio-csr-ca-configmap` / `istio-csr-dns-cert` volumes) and cannot load its CA bundle from SPIRE: istiod logs `Failed to load CA bundle: could not decode pem` → `patching webhook istio-sidecar-injector failed` → `cert not initialized`. The sidecar-injection webhook then returns `tls: internal error`, so **meshed pods can't be created** → no SVID → no workload mTLS. This blocks ticket 17's live positive path.

**To close:** istiod must obtain a valid CA bundle + serving cert from SPIRE (via istio-csr) so the sidecar-injection webhook serves and meshed workloads start with SPIFFE SVIDs; then ticket 17's `verify-reach-secrets.sh` positive path passes live.

## Comments

- 2026-08-20 (audit mo-02): re-audited. `git log --oneline -- estate/platform/identity/ estate/tuppence/reset/` shows no commit since `f7f6732` (2026-07-31) — the istio-csr/SPIRE CA bootstrap fix described above has not landed, so this REOPENED status is still accurate today. `bash estate/platform/identity/verify-identity.sh` still PASSes its offline structural checks (manifest wiring — `caName: SPIRE`, STRICT mTLS, SPIFFE-principal authz, OpenBao JWT→SPIRE OIDC), consistent with AC1/AC4 staying ticked; this does not contradict the live failure, since the offline check only parses manifests and was never able to catch a runtime CA-bootstrap bug. No live cluster was available in this audit environment (see ticket 02) to re-attempt the live repro. Status and AC ticks left unchanged — this is one of the two tickets the audit (`.scratch/multi-org-estate/issues/02-tracker-status-audit.md`) already named as honest.
