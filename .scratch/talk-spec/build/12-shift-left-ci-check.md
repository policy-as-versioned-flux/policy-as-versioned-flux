# 12 — Shift-left CI ±1 check

**What to build:** CI resolves the target's supported version window (±1 skew off the ResourceSet array) and runs the target version's real `kyverno apply` offline, so an Audit→Deny flip is caught before merge.

**Blocked by:** 03

**Status:** done (2026-08-20) — `estate/platform/shift-left/verify-shift-left.sh` PASSes offline

- [x] CI reads the version array (±1 skew) and runs `kyverno apply` for the target version offline — `ci-check.py:69` `"""Target ±1 off the declared array (sorted by semver), clipped to the array."""`; run output: `fixtures/workload-compliant.yaml: targets 2.0.0, checking supported window ['1.0.0', '2.0.0']` then real `--- kyverno apply @ v1.0.0 ---` / `@ v2.0.0 ---` invocations
- [x] An Audit→Deny flip fails CI pre-merge; a compliant change passes — `bash estate/platform/shift-left/verify-shift-left.sh`: compliant fixture → `pass: 1, fail: 0` at v2.0.0, `shift-left: ... is compliant across its supported window`; flip fixture → `policy require-nonroot-2-0-0 -> ... failed`, `pass: 0, fail: 1`, `FAIL @ v2.0.0 (non-zero above is expected -- the flip was caught)`. Final line: `shift-left: all offline proofs passed`

## Comments

- 2026-08-20 (audit mo-02): re-ran `verify-shift-left.sh` directly; both halves of the AC (compliant passes, flip fails) shown explicitly in the same run. Status corrected from `ready-for-agent` to `done`.
