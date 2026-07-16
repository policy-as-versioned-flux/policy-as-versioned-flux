# 02 — ADR: sunset as scheduled proposals, never scheduled application

**What to build:** The decision-of-record for sunset times, written and merged before any sunset implementation. Content per the grilled decision: a `sunset:` date lives on fleet array entries (adoption-scoped — never in the immutable policy release, since sunsetting is a fleet's adoption decision, not a property of the version); dashboards show the countdown; the governance agent opens escalating issues as the date nears; on the date, a machine opens a retirement PR that a human must merge. Nothing timed ever applies — if nobody merges, nothing changes. The ADR must state explicitly that this *extends ADR-0006's boundary deliberately* (ADR-0006 rejects timed enforcement changes; ADR-0002 already sanctions machine-opened PRs — the preserved invariant is "never automerged", not "never machine-initiated"), and that timed *nudges to humans* (escalation issues, weekly nags) are outside ADR-0006's prohibition.

**Blocked by:** None — can start immediately.

**Status:** done

- [x] New ADR in the hub's ADR series, cross-referencing ADR-0002/0006/0007 and the boundary each contributes
- [x] The "scheduled proposals, never scheduled application" invariant stated with its enforcement mechanism (human merge required; branch ruleset already blocks self-merge-free automerge)
- [x] ADR-0006 gains a pointer to the new ADR (append, don't rewrite history)

## Comments

Done 2026-07-16. `docs/adr/0010-sunset-scheduled-proposals-not-application.md` in the hub.

Cross-references: leans on ADR-0002 (Renovate already proves "machine-opened PR, human-merged" is
sanctioned — the invariant it protects is "never automerged," not "never machine-initiated"),
extends ADR-0006 explicitly (draws the boundary between forbidden time-conditional *policy state*
and permitted time-conditional *human reminders* — sunset only ever produces reminders and a
sitting, unmerged proposal), and folds sunset proximity into ADR-0007's existing governance-agent
escalation contract as one more input signal, no new contract shape.

**Enforcement mechanism verified, not assumed:** checked the real fleet repo before writing the
claim rather than taking the ticket's phrasing on faith. `gh api repos/.../fleet/rulesets` shows
only a required-status-check rule (`gate`) -- there's no branch-protection rule literally blocking
self-merge. The actual mechanism is `allow_auto_merge: false` at the repo level (confirmed via `gh
api repos/.../fleet`): GitHub's auto-merge feature can't be configured on any PR in this repo, so
a machine-opened retirement PR can never merge itself once checks pass -- a human has to actually
run `gh pr merge` or click Merge. The ADR states this precisely rather than the looser "branch
ruleset blocks it" framing.

ADR-0006 gains a new "Later extension" section (appended, not rewritten) pointing forward to
ADR-0010. README.md, docs/PRD.md, and CONTEXT.md's decision index/ubiquitous-language section
updated to include ADR-0010.
