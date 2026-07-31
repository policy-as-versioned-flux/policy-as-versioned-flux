# 22 — War-gamer agent (feed → signed PR)

**What to build:** The evolved `governance-agent` collects the feeds, war-games scenarios (incl. human/device attack paths — phishing / stolen laptop / insider — and ransomware/PQ) against current controls, and on proportionality drift opens a **signed** policy PR — proposes, never disposes.

**Blocked by:** 06, 13, 21

**Status:** ready-for-agent

- [ ] Collects the feeds; war-games workload + human/device scenarios
- [ ] On drift, opens a signed policy PR (gitsign → Rekor); never auto-merges
- [ ] The PR carries the version-cross-check gate; the feed→PR seam test asserts propose-never-dispose
