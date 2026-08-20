# 08 — `tuppence` + `ludlow` live

**What to build:** The other two institutions on their own KinD clusters, inheriting `platform` as a pinned signed dependency, each with its appetite skin (`ludlow` strictest, `driftwood` loosest, `tuppence` toward-strict).

**Blocked by:** 03, 06

**Status:** PARTIAL — configured, not live-verified; no Docker daemon reachable in this environment (same constraint as ticket 02)

- [ ] `tuppence` + `ludlow` KinD clusters live, inheriting `platform` — **unverified live**: `estate/tuppence/kind/tuppence.yaml`, `estate/ludlow/kind/ludlow.yaml`, and each `scripts/up.sh` exist and mirror driftwood's pattern (`platform-pin.yaml` in each `gitops/platform/`), but none were run (no Docker)
- [x] Each carries its risk skin/appetite (`ludlow` Deny-heavy, `driftwood` Audit-heavy) — `estate/platform/risk/appetite.json`: `driftwood.tolerance=40000` ("loosest"), `tuppence.tolerance=15000` ("toward-strict"), `ludlow.tolerance=5000` ("strictest"); mirrored in each institution's `gitops/apps/risk-appetite-configmap.yaml`
- [ ] All three institutions reconcile healthily — **unverified live**: `estate/{driftwood,tuppence,ludlow}/verify-reconcile.sh` are LIVE-only beats in `estate/talk/verify-all.sh`; `kind get clusters` is empty here

## Comments

- 2026-08-20 (audit mo-02): downgraded from `ready-for-agent` (which implied not-yet-started) to `PARTIAL` — the config/skin is real and correct, but the ticket's actual title ("...live") names a live claim this environment cannot exercise (no Docker daemon). Do not read `PARTIAL` here as "half-built"; read it as "built, live half unproven" — same shape as ticket 02.
