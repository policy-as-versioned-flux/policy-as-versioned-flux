# 04 — `nist` real OSCAL controls feed

**What to build:** The `nist` repo ships genuine 800-53 OSCAL controls; `driftwood` consumes them as a pinned, signed dependency, so a regulator change arrives as a reviewable PR.

**Blocked by:** 02

**Status:** done (2026-08-20) — `estate/nist/scripts/verify-catalog.sh` PASSes offline

- [x] `nist` publishes real 800-53 OSCAL catalog, versioned + signed — `bash estate/nist/scripts/verify-catalog.sh` → `OK: 1196 controls across 20 groups, sha256 verified, NIST rev 5.2.0 (OSCAL 1.2.2)`; catalog file `estate/nist/catalog/NIST_SP-800-53_rev5.2.0_catalog.json`
- [x] `driftwood` pins a specific signed version — `estate/driftwood/gitops/flux-system/gotk-sync-nist.yaml` pins tag+commit; `estate/driftwood/verify-reconcile.sh` step 4 asserts it reconciles (live-only, not exercised here — see ticket 02)
- [x] A version bump arrives as a reviewable PR — `estate/driftwood/scripts/bump-nist-pin.sh v1.1.0` edits the pin on a branch and prints the diff only; never commits/pushes/opens the PR itself (verified by reading the script — it stops at `diff -u`)

## Comments

- 2026-08-20 (audit mo-02): `verify-catalog.sh` PASSes offline; the "pins a specific signed version" AC leans on the pinned-tag file in `driftwood`'s gitops tree, which is tree-verified but not live-reconciled (no cluster, see ticket 02). Status corrected from `ready-for-agent` to `done`.
