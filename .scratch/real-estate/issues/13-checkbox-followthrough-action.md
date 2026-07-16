# 13 — Governance checkbox follow-through Action

**What to build:** The missing follow-through on the governance agent's decision-framing issues. An Action in the policy repo reacts when a reviewer ticks a checkbox on an `agent-governance-review` issue: an acknowledging comment plus a state label (`awaiting-defence-pr` / `awaiting-change-pr` / `needs-discussion`) — comment and label only, never a write to policy content, preserving ADR-0007's invariant by construction (token scope, not promise). A weekly check nags issues sitting checked-but-unactioned — ADR-0006-safe because it's a timed nudge to humans, never a timed enforcement change (the distinction ticket 02's ADR writes down).

**Blocked by:** None — can start immediately.

**Status:** ready-for-agent

- [ ] Ticking each of the three boxes produces the matching label + comment, proven on a real issue
- [ ] The weekly nag comments on a checked-but-unactioned issue and skips actioned ones
- [ ] The workflow's permissions grant issues-write only — no contents access to enforcement paths
