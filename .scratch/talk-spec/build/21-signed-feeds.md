# 21 — Signed feeds (threat · CVE · EOL)

**What to build:** The reactive feeds — institution threat register, CVE (trivy/GHSA), EOL (`endoflife.date`) — as signed, versioned upstreams consumed like dependencies; a change arrives as a reviewable PR that re-tunes the £.

**Blocked by:** 02, 07

**Status:** done (2026-08-20) — `estate/platform/feeds/verify-feeds.sh` PASSes offline

- [x] Threat-register, CVE, EOL feeds signed + versioned; consumed as pinned deps — `bash estate/platform/feeds/verify-feeds.sh` verifies all six versioned feed files (`threat-register`/`cve`/`eol` × v1/v2), each `Signature Verified Successfully`; a tampered feed is rejected
- [x] A feed change arrives as a reviewable PR that re-tunes the £ — same run: `threat-register £ rose by £103,565 on the v1->v2 tuppence lef bump`, `v2's new CVE-2024-8888-istiod prices at £241550 ALE (didn't exist in v1)` — no `fair.py` edit, £ moves purely off the versioned feed diff
- [x] EOL treated as a time-varying risk thread (past-EOL → £ ramps) — `ale(istio-1.18, pre-EOL) = £218337`, `1yr past = £436816`, `4yr+ past = £1087666`, ramp `monotonic & capped (1yr=2.00x 2yr=3.00x 10yr=5.00x)` (`eol_ramp()`, `estate/platform/feeds/to_fair_scenario.py:74-89`)

## Comments

- 2026-08-20 (audit mo-02): `verify-feeds.sh` PASSes offline, all 3 ACs directly evidenced with real £ deltas from real signed-feed diffs. Status corrected from `ready-for-agent` to `done`.
