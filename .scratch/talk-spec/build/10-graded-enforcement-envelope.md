# 10 — Graded enforcement envelope

**What to build:** Beyond admit/deny — Kyverno **mutate + generate** cages a behind-posture workload *by degree* (resource limits, NetworkPolicy, dropped caps, read-only-fs, heavier-WAF sidecar, eviction priority). Tiers over dials; the cage's run-cost is accounted for TCoR. Deny is just the bottom rung.

**Blocked by:** 03, 06

**Status:** ready-for-agent

- [ ] A behind-posture pod is *mutated into its cage*, not denied
- [ ] Named tiers (PSS-style) expand into dial settings deterministically; the £ selects the tier
- [ ] The cage's run-cost is emitted for TCoR
- [ ] `kyverno-test.yaml` asserts the mutation (cage present), not a deny
