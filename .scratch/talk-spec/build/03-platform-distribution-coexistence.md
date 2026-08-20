# 03 — Platform distribution + coexistence

**What to build:** Flux fans out coexisting signed policy versions from one version array; a Kyverno `ValidatingPolicy` self-scopes via `matchConditions` (not objectSelector); an orphan-guard rendered from the array; two versions coexist; prune-on-retire.

**Blocked by:** 02

**Status:** done (2026-08-20) — `verify-coexistence.sh`, `verify-orphan-guard.sh`, `verify-retirement.sh` all PASS offline

- [x] `ResourceSet` fans out policy versions from a single array edit — `estate/platform/distribution/versions.yaml` (single `inputs[0].versions[]` array) + `kustomization.yaml` render it via flux-operator's `ResourceSet`
- [x] Kyverno `ValidatingPolicy` self-scopes on the policy-version label via `matchConditions` — `policies/v1.0.0/require-nonroot.yaml:25` and `v2.0.0/require-nonroot.yaml:25` both use `matchConditions` (comment explicitly rejects `matchConstraints.objectSelector`, "which Kyverno flattens into one shared webhook")
- [x] Two signed versions admit side-by-side; a version not in the array cannot run (orphan-guard) — `bash estate/platform/distribution/verify-coexistence.sh` → `PASS: two signed versions coexist; each judges only what claims it.`; `verify-orphan-guard.sh` → `PASS: only versions the array declares can run; the allow-list is the array.`
- [x] Retiring a version prunes it (Flux prune) — `bash estate/platform/distribution/verify-retirement.sh` → after removing the array element, a pod on the retired version is denied (orphaned by the shrunk array); live Flux-prune step itself needs a cluster (not available here, see ticket 02)
- [x] `verify-coexistence.sh` + `verify-retirement.sh` + `verify-orphan-guard.sh` pass — all three run clean, exit 0, offline

## Comments

- 2026-08-20 (audit mo-02): re-ran all three verify-*.sh individually, all exit 0. Also confirmed `matchConditions` (not `objectSelector`) directly in `estate/platform/distribution/policies/v1.0.0/require-nonroot.yaml` and `v2.0.0/require-nonroot.yaml`. Status corrected from `ready-for-agent` to `done`.
