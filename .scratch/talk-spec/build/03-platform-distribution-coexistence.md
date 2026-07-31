# 03 — Platform distribution + coexistence

**What to build:** Flux fans out coexisting signed policy versions from one version array; a Kyverno `ValidatingPolicy` self-scopes via `matchConditions` (not objectSelector); an orphan-guard rendered from the array; two versions coexist; prune-on-retire.

**Blocked by:** 02

**Status:** ready-for-agent

- [ ] `ResourceSet` fans out policy versions from a single array edit
- [ ] Kyverno `ValidatingPolicy` self-scopes on the policy-version label via `matchConditions`
- [ ] Two signed versions admit side-by-side; a version not in the array cannot run (orphan-guard)
- [ ] Retiring a version prunes it (Flux prune)
- [ ] `verify-coexistence.sh` + `verify-retirement.sh` + `verify-orphan-guard.sh` pass
