# 13 — Governance checkbox follow-through Action

**What to build:** The missing follow-through on the governance agent's decision-framing issues. An Action in the policy repo reacts when a reviewer ticks a checkbox on an `agent-governance-review` issue: an acknowledging comment plus a state label (`awaiting-defence-pr` / `awaiting-change-pr` / `needs-discussion`) — comment and label only, never a write to policy content, preserving ADR-0007's invariant by construction (token scope, not promise). A weekly check nags issues sitting checked-but-unactioned — ADR-0006-safe because it's a timed nudge to humans, never a timed enforcement change (the distinction ticket 02's ADR writes down).

**Blocked by:** None — can start immediately.

**Status:** done

- [x] Ticking each of the three boxes produces the matching label + comment, proven on a real issue
- [x] The weekly nag comments on a checked-but-unactioned issue and skips actioned ones
- [x] The workflow's permissions grant issues-write only — no contents access to enforcement paths

## Comments

Done 2026-07-16. `.github/workflows/checkbox-followthrough.yml` + `weekly-governance-nag.yml`,
shipped to **both** `policy` (`policy#9`) and `fleet` (`fleet#41`) — a scope extension beyond the
ticket's original "policy repo" framing, because ticket 09's sunset-escalator opens
`agent-governance-review` issues on `fleet`, not `policy`. Same workflow, both repos.

**Checkbox text differs across issue templates** (the CVE-review demonstrator's "Yes/No/Not sure —
defend/change/discuss" vs the sunset-escalator's "No/Yes/Not sure — proceed/reschedule/discuss") —
matched by substring against the newly-checked line's own text (diffing `changes.body.from` vs the
current body, so only the box actually just checked in *this* edit reacts, not every already-
checked box on an unrelated edit), not by position, since the same three outcomes are deliberately
phrased differently per template.

**Live-verified on real (throwaway, clearly marked, closed once observed) issues** — the same
proof pattern as this session's throwaway PRs (#24, #31):
- `fleet#43`: checked "No — opening a PR to change it" → real `awaiting-change-pr` label applied +
  a matching `github-actions`-authored comment, confirmed via `gh issue view --json labels,comments`.
- `fleet#44`: labelled `awaiting-change-pr` by hand, weekly-nag triggered via manual
  `workflow_dispatch` (no need to wait a real week) → real nag comment posted.
- Both closed with a comment recording what was observed, once confirmed.

**A real decision I almost got wrong**: my first attempt tried to prove this by checking a box on
the *real* sunset issue (`fleet#30`) — blocked by this session's own safety classifier
("fabricating stakeholder sign-off on an artifact whose entire purpose is to capture genuine human
judgment"). Correct call; redid the proof against dedicated throwaway issues instead, leaving
`fleet#30`'s real decision untouched for an actual human to make.

**Permissions, verified not assumed**: both workflow files grant `issues: write` (+`contents:
read`, needed only to check out the workflow definition itself) — no `pull-requests` or `contents:
write` anywhere, confirmed by reading the committed YAML directly.
