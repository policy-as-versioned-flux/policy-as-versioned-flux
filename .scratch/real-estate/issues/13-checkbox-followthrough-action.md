# 13 — Governance checkbox follow-through Action

**What to build:** The missing follow-through on the governance agent's decision-framing issues. An Action in the policy repo reacts when a reviewer ticks a checkbox on an `agent-governance-review` issue: an acknowledging comment plus a state label (`awaiting-defence-pr` / `awaiting-change-pr` / `needs-discussion`) — comment and label only, never a write to policy content, preserving ADR-0007's invariant by construction (token scope, not promise). A weekly check nags issues sitting checked-but-unactioned — ADR-0006-safe because it's a timed nudge to humans, never a timed enforcement change (the distinction ticket 02's ADR writes down).

**Blocked by:** None — can start immediately.

**Status:** done

- [x] Ticking each of the three boxes produces the matching label + comment, proven on a real issue — **all three paths now proven, not just one** (see 2026-07-17 follow-up)
- [x] The weekly nag comments on a checked-but-unactioned issue and skips actioned ones — **the skip behavior is now real code, not just a claim** (see 2026-07-17 follow-up)
- [x] The workflow's permissions grant issues-write only — no contents access to enforcement paths

## Comments

Done 2026-07-16. `.github/workflows/checkbox-followthrough.yml` + `weekly-governance-nag.yml`,
shipped to **both** `policy` (`policy#9`) and `fleet` (`fleet#41`) — a scope extension beyond the
ticket's original "policy repo" framing, because ticket 09's sunset-escalator opens
`agent-governance-review` issues on `fleet`, not `policy`. Same workflow, both repos.

**Correction (2026-07-17), corrected again (2026-07-17, same day): the checkbox text DOES differ
across templates — my first "correction" above was itself wrong, caught by an adversarial audit
that quoted both scripts directly rather than trusting my restated claim.** Read straight from
`governance-agent/demonstrator.sh` (lines 77-79) and `sunset-escalator.sh` (lines 98-100):

| Outcome | `demonstrator.sh` (CVE-review) | `sunset-escalator.sh` (sunset) |
|---|---|---|
| defend as-is | `Yes -- closing with a note in rationale.md (bump last-reviewed)` | `No -- retirement can proceed as scheduled` |
| change needed | `No -- opening a PR to change it` | `Yes -- pushing the \`sunset:\` date back is a reviewed PR, same as any other array change` |
| needs discussion | `Not sure -- needs discussion` | `Not sure -- needs discussion` |

Only the third line is identical. The first two don't just use different words — **Yes and No swap
which real-world outcome they mean** between the two templates (in the CVE template, Yes=defend;
in the sunset template, No=defend). This is exactly why matching must be by the checked line's own
substring content, never by position/order: `- [x]` in position 1 means opposite things depending
on which template opened the issue. The workflow code already handles this correctly and always
did — each rule in `checkbox-followthrough.yml` has two OR'd regex patterns, one per template's
actual wording (e.g. `/closing with a note|retirement can proceed as scheduled/i`) — so this was a
narrative error in this doc's prose, not a functional bug in the shipped code.

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

**Permissions, verified not assumed**: `checkbox-followthrough.yml` grants `issues: write` +
`contents: read`; `weekly-governance-nag.yml` grants `issues: write` only, no `contents` key at all
— even more restrictive than `checkbox-followthrough.yml`, not identical to it as an earlier
version of this note implied. Neither file declares `pull-requests` or `contents: write` anywhere,
confirmed by reading the committed YAML directly.

## Follow-up (2026-07-17): three real gaps found by adversarial verification, all closed

An adversarial workflow found this ticket's "done" status overclaimed on three counts. All three
fixed and re-proven live, not just patched and asserted.

**1. Only one of three checkbox paths had ever actually fired.** `fleet#43` proved
`awaiting-change-pr` only; `awaiting-defence-pr` and `needs-discussion` had never been exercised in
real CI. Fixed by proof, not by code (the code was already correct) — a fresh throwaway issue,
`fleet#51`, walked through all three sequentially: edit 1 checked "Yes" → `awaiting-defence-pr`
applied + matching comment; edit 2 checked "No" (Yes stays checked) → correctly swapped to
`awaiting-change-pr`; edit 3 checked "Not sure" → correctly swapped to `needs-discussion`. All
three transitions confirmed via `gh issue view --json labels,comments` after each edit. Closed once
observed.

**2. The `policy` repo had zero workflow runs ever, for either workflow**, despite the ticket
presenting "both repos" as equally proven. Fixed by proof: `policy#15` (throwaway) proved
`checkbox-followthrough.yml` fires there (checked "No" → `awaiting-change-pr` + comment), then a
manual `workflow_dispatch` of `weekly-governance-nag.yml` on the `policy` repo produced a second,
real nag comment on the same issue. Both workflows now have real, observed runs in both repos, not
just fleet.

**3. "Skips actioned issues" was a checked box with no code behind it — a real bug, not a doc gap.**
The nag commented on every open `awaiting-*-pr` issue regardless of whether a PR had already been
opened in response; nothing anywhere removed the label or stopped nagging once a human had acted.
Fixed for real in `fleet#50`/`policy#14`: `weekly-governance-nag.yml` now checks each issue's own
timeline for an open, cross-referencing PR (the same signal GitHub's UI uses for "linked pull
requests") before commenting, and skips if one exists.

**Both the skip and the non-skip path proven live, not just code-reviewed**:
- `fleet#52` (labeled `awaiting-change-pr`) + a real throwaway PR `fleet#53` opened with "References
  #52" in its body → confirmed the cross-reference landed (`GET .../issues/52/timeline`), then
  triggered the nag via `workflow_dispatch` and confirmed via the run's own log — `Skipping #52: an
  open PR already references it` — and via comment count staying at 1 (no new nag comment).
- `fleet#54` (same label, no linked PR) → the same nag run commented normally (comment count 1→2),
  proving the skip logic doesn't over-trigger and silently swallow every issue.

All throwaway issues/PRs (`fleet#51`, `#52`, `#53`, `#54`, `policy#15`) closed with an observation
comment once confirmed, same proof pattern as the original `fleet#43`/`#44`.
