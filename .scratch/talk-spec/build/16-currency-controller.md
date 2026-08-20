# 16 — Currency controller

**What to build:** A small controller re-evaluates workload posture *after* admission and re-patches/evicts as policy versions age — runtime re-tuning, so posture isn't a frozen admission snapshot (the gap the SPIRE research flagged).

**Blocked by:** 15

**Status:** done (2026-08-20), offline proof only — `estate/platform/currency-controller/verify-currency.sh` PASSes offline

- [x] When a workload's admitted version goes stale, the controller re-patches its posture (or evicts) within a bounded interval — `currency selfcheck: all asserts passed (stale = posture ∉ supported; re-patch drops BOTH labels)`; step 2: `only reset-retired planned for de-posture` (i.e. only the actually-stale pod is selected); `rbac.yaml`+`cronjob.yaml` (the bounded-interval mechanism) apply cleanly in dry-run
- [x] The SVID reflects the new posture after reconcile — step 3: removing the posture label takes the pod out of scope for `stamp-posture`/`posture-trust-boundary`, and the `ClusterSPIFFEID`'s `podSelector` requires the posture label to Exist, so `removed => pod drops to base-mesh SVID` — live re-mint itself not exercised (no cluster; also blocked transitively by ticket 14, same as ticket 15)

## Comments

- 2026-08-20 (audit mo-02): `verify-currency.sh` PASSes offline; the re-patch logic and its interaction with the posture/orphan-guard policies are genuinely proven, not just asserted. Live tail self-skips (no CronJob installed, no cluster). Status corrected from `ready-for-agent` to `done` on the same offline-proof standard as ticket 15.
