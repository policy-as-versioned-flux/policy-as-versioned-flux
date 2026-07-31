# 16 — Currency controller

**What to build:** A small controller re-evaluates workload posture *after* admission and re-patches/evicts as policy versions age — runtime re-tuning, so posture isn't a frozen admission snapshot (the gap the SPIRE research flagged).

**Blocked by:** 15

**Status:** ready-for-agent

- [ ] When a workload's admitted version goes stale, the controller re-patches its posture (or evicts) within a bounded interval
- [ ] The SVID reflects the new posture after reconcile
