# 21 — Signed feeds (threat · CVE · EOL)

**What to build:** The reactive feeds — institution threat register, CVE (trivy/GHSA), EOL (`endoflife.date`) — as signed, versioned upstreams consumed like dependencies; a change arrives as a reviewable PR that re-tunes the £.

**Blocked by:** 02, 07

**Status:** ready-for-agent

- [ ] Threat-register, CVE, EOL feeds signed + versioned; consumed as pinned deps
- [ ] A feed change arrives as a reviewable PR that re-tunes the £
- [ ] EOL treated as a time-varying risk thread (past-EOL → £ ramps)
