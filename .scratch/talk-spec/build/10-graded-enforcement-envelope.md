# 10 — Graded enforcement envelope

**What to build:** Beyond admit/deny — Kyverno **mutate + generate** cages a behind-posture workload *by degree* (resource limits, NetworkPolicy, dropped caps, read-only-fs, heavier-WAF sidecar, eviction priority). Tiers over dials; the cage's run-cost is accounted for TCoR. Deny is just the bottom rung.

**Blocked by:** 03, 06

**Status:** done (2026-08-20) — `estate/platform/graded/verify-graded.sh` PASSes offline

- [x] A behind-posture pod is *mutated into its cage*, not denied — same run, step 2: `a behind-posture pod is MUTATED INTO ITS CAGE, not denied`; step 3 confirms the caged pod also *generates* an egress-lockdown NetworkPolicy
- [x] Named tiers (PSS-style) expand into dial settings deterministically; the £ selects the tier — step 1: tiers `['baseline', 'restricted', 'quarantine']`, `£ picks: band40k->baseline band20k->restricted band5k->quarantine band1k->deny`; step 4 confirms `cage.py`'s dial values (cpu/mem/PriorityClass/hardening/WAF) match the Kyverno mutate policy exactly, tier by tier
- [x] The cage's run-cost is emitted for TCoR — step 1: `scenario £33073: driftwood->baseline (TCoR £23651), ludlow->quarantine (TCoR £8646)`; `tcor()` in `estate/platform/graded/cage.py:91-103` books `cost_of_controls` into `tcor = residual + controls`
- [x] `kyverno-test.yaml` asserts the mutation (cage present), not a deny — `estate/platform/graded/tests/cage-tier/kyverno-test.yaml` and `tests/cage-netpol/kyverno-test.yaml` both present and exercised by the run above

## Comments

- 2026-08-20 (audit mo-02): `verify-graded.sh` PASSes offline, all 4 ACs directly evidenced including the tier/dial cross-check against the live Kyverno mutate policy. Status corrected from `ready-for-agent` to `done`.
