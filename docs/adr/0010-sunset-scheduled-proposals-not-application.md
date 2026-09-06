---
status: accepted
---

> **Superseded in part, 2026-08-28 (eco-system ticket 13 D5), written 2026-09-06 (ticket 80
> items 2 and 7).** The **consumer-side `sunset:` field is not carried into the eco-system.**
> Supersede is publisher-side only: the publisher publishes the newer version, a pin behind it is
> priced by the existing EOL ramp from that version's publish date, `revoked[]` stays withdrawal
> priced now, and the adopter's scheduled proposer opens a retirement PR under the dedupe ledger.
> That rule is [ADR-0023](0023-a-clock-appends-observations-and-one-signature-verified-by-a-controller.md)'s
> last decision point; the alternative this ADR's field represents, a dated supersede carried on
> the consumer's own entry, is in ADR-0023's Alternatives as rejected ("two formulas for one
> state"), to be revisited with an explicit `supersedes: {version, eol_date}` if the ramp
> misprices. D5 was put to the owner as a three-lens panel verdict and the owner wrote "I
> agree with you're more advanced reasoning" -- an endorsement of the assistant's reasoning
> and not a reason of the owner's own, so under
> [ADR-0025](0025-the-assistant-decides-architecture-and-records-it.md) point 3 it is
> **delegated**: the assistant's decision, recorded with the reason above, not re-asked.
> Ticket 13 calls it "Decided" against the earlier vocabulary, in which a panel verdict
> ranked above a bare agree; that ranking is what ADR-0025 retired. Record:
> [issues/13](../../.scratch/ecosystem/issues/13-lift-or-retire-the-original-mechanisms.md) D5.
>
> **What survives.** Points 2, 3 and 4 -- escalating issues, a machine opening the retirement PR
> on the date, and a human having to merge it -- and the whole ADR-0006 boundary argument, which
> the eco-system restates as "a clock appends observations, never declarations" (ADR-0023). The
> adopter's sovereignty survives too: an adopter drops a version by an ordinary PR.
>
> **Superseded in part, 2026-07-20 (the owner), written 2026-09-06 (ticket 80 item 2).** Point 1
> ("the estate dashboard shows a countdown") and the dashboard countdown in the Consequences are
> retired with every other dashboard: see [ADR-0008](0008-measurable-layered-ground-truth.md)'s
> banner. The visible governance debt this ADR wanted a countdown for is the truth surface's job.

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
