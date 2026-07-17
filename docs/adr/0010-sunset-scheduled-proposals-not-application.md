---
status: accepted
---

# Sunset: scheduled proposals, never scheduled application

A fleet may want to signal, in advance, that it intends to retire a policy version — "we plan to
drop `1.0.0` by 2026-09-01" — so teams still on it have a horizon, not a surprise. This ADR defines
how: a `sunset:` date lives on the **fleet's** array entry for that version (adoption-scoped,
never on the immutable policy release itself — sunsetting when a fleet stops running a version is
that fleet's decision, not a property the version carries forever). As the date approaches:

1. The estate dashboard shows a countdown for that version.
2. The governance agent (ADR-0007) opens escalating issues as the date nears, using sunset
   proximity as one more external signal alongside CVEs and regulatory shifts — extending its
   existing contract, not requiring a new one.
3. **On the date itself, a machine opens a retirement PR** removing that version's array entry.
4. **A human must merge it.** If nobody does, nothing changes — the version stays installed,
   indefinitely, exactly as if no date had ever been set.

Nothing here ever fires a mechanical change to enforcement. The date only ever produces things a
human reads and something a human must click.

## Why this doesn't violate ADR-0006

ADR-0006 forbids **time-conditional policy state** — no expiry embedded in a policy body, no
admission verdict that silently flips because a clock ticked. Its target is specifically the
*engine's* enforcement behaviour: the same manifest against the same policy version must always
produce the same result, independent of when it's evaluated.

A sunset date never touches that. It:

- lives in the **fleet** repo's array (an adoption record), never in the **policy** repo's
  immutable release — the thing ADR-0006 actually constrains;
- never causes an admission verdict to change on its own. The array entry it eventually proposes
  removing only stops applying once a **human-merged PR** removes it — the exact same "reviewed,
  revertible PR, the same unit of debate as any other policy change" mechanism ADR-0006 already
  prescribes for the mea-culpa's "delete-if-undefended" rule;
- produces, on the date, a *proposal* (a PR sitting there, unmerged, changing nothing until
  someone acts) and a stream of *nudges to humans* (dashboard countdown, escalating issues, a
  weekly stale nag on the eventual retirement PR if it sits unmerged — ticket 13's checkbox
  follow-through). None of these are enforcement. ADR-0006 prohibits time-conditional *policy
  state*; it says nothing about time-conditional *human reminders*, which is what all of this is.

So this ADR **deliberately extends ADR-0006's boundary**: it draws the line explicitly between
"timed changes to what gets enforced" (still forbidden, no exception) and "timed prompts to a
human, who may or may not act" (was already implicit — ADR-0007's escalating-issues contract is
exactly this — and is now named as the general pattern sunset also uses).

## Why "machine-opened" isn't new

ADR-0002 already sanctions a machine opening PRs against pinned version arrays: every routine
version bump is a Renovate-opened PR, reviewed and merged by a human, `automerge:false` in every
environment. The retirement PR this ADR adds is the same shape — a machine notices a condition
(here, a date; there, a new upstream tag) and opens a PR proposing a change to the array. **The
invariant ADR-0002 actually protects is "never automerged," not "never machine-initiated."** A
sunset retirement PR sits in exactly the same category as a Renovate bump PR: proposed by
automation, adopted only by a human.

## Enforcement mechanism

Two things make "human must merge" real, not aspirational:

- **`allow_auto_merge: false`** is set at the repo level on `fleet` (and every governed repo) —
  GitHub's auto-merge feature cannot be configured on any PR in these repos, machine-opened or
  not. There is no button a bot can press that merges itself later; someone has to run `gh pr
  merge` (or click Merge) themselves.
- The existing **`require-pr-gate` ruleset** (required status check on `gate`) still applies to a
  retirement PR like any other — pr-gate-check.sh still verifies whatever the resulting array
  state resolves to before a human even considers merging.

Neither mechanism cares who *opened* the PR. Both mechanisms block it from merging *by itself*.

## Consequences

- Fleet array entries gain an optional `sunset: <date>` field. Absence means no countdown, no
  escalation, no retirement PR — opt-in per version, per fleet.
- The governance agent's escalation-issue contract (ADR-0007) gains sunset proximity as an input
  signal alongside CVEs/regulatory shifts; no change to the contract's shape (still: surfaced
  business decisions as issues/PRs, never a direct enforcement edit).
- The retirement PR, once merged, is an ordinary array-entry removal — retirement's existing
  admission-only semantics (see the fleet README) are unchanged: the removed version's workloads
  keep running until their next recreation, then the orphan guard refuses them.
- If a retirement PR sits unmerged past its target date, that's visible governance debt (the
  dashboard countdown goes negative, the weekly nag keeps firing) — never a trigger for anything
  to happen automatically.
