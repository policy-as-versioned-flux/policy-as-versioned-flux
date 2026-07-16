# 02 — ADR: sunset as scheduled proposals, never scheduled application

**What to build:** The decision-of-record for sunset times, written and merged before any sunset implementation. Content per the grilled decision: a `sunset:` date lives on fleet array entries (adoption-scoped — never in the immutable policy release, since sunsetting is a fleet's adoption decision, not a property of the version); dashboards show the countdown; the governance agent opens escalating issues as the date nears; on the date, a machine opens a retirement PR that a human must merge. Nothing timed ever applies — if nobody merges, nothing changes. The ADR must state explicitly that this *extends ADR-0006's boundary deliberately* (ADR-0006 rejects timed enforcement changes; ADR-0002 already sanctions machine-opened PRs — the preserved invariant is "never automerged", not "never machine-initiated"), and that timed *nudges to humans* (escalation issues, weekly nags) are outside ADR-0006's prohibition.

**Blocked by:** None — can start immediately.

**Status:** ready-for-agent

- [ ] New ADR in the hub's ADR series, cross-referencing ADR-0002/0006/0007 and the boundary each contributes
- [ ] The "scheduled proposals, never scheduled application" invariant stated with its enforcement mechanism (human merge required; branch ruleset already blocks self-merge-free automerge)
- [ ] ADR-0006 gains a pointer to the new ADR (append, don't rewrite history)
