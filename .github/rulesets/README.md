# The review rulesets (ticket 87 item 1)

These four files describe the rulesets applied to the nine estate repositories on 2026-09-24,
with the main review rule added on 2026-10-04. Each was
applied with `gh api -X POST repos/<owner>/<repo>/rulesets --input <file>`. The ids are recorded
in `.scratch/ecosystem/issues/87-the-forge-enforces-the-review.md`.
`verify/forge-review/verify-forge-review.sh` grades what the forge answers, not these files.
`tests/test_forge_review.py` holds these files to the rules that check demands.

| File | Target | Applied to |
|---|---|---|
| `release-branches-are-reviewed.json` | `refs/heads/release/**` | all nine |
| `release-tags-hold.json` | every tag | all nine |
| `main-is-reviewed.json` | the default branch | nist, ico, feeds, insurer |
| `main-keeps-its-history.json` | the default branch | hub, platform, driftwood, tuppence, ludlow |

No file carries a bypass actor. The September 25 clock-delivery compromise below is historical;
main now requires one approving review on all nine repositories. The hub uses pending PR
delivery as recorded below. Other clock and release writers still need their own delivery repair.

GitHub refuses the GitHub Actions integration (app id 15368) as
a bypass actor on these organisations. It returned HTTP 422, "Actor GitHub Actions integration
must be part of the ruleset source or owner organization", when it was tried on the hub. Every
clock and every release push in the estate uses `GITHUB_TOKEN`. So:

- A default branch a clock pushes to gets no `pull_request` rule yet. That is the hub
  (truth.yml), driftwood, tuppence and ludlow (drift-sample, twin-sweep) and platform
  (cut-release's evidence commit). Those branches carry `deletion` and `non_fast_forward`
  only. Every clock push is a fast-forward, so the clocks keep running.
- Tags carry `update` and `deletion` but not `creation`, because cut-release creates them with
  `GITHUB_TOKEN`. A tag can be pushed by hand. It cannot be moved or deleted. A hand-pushed tag
  carries no cut-release signature, so no identity pin accepts it.
- Release branches carry `creation`, so nobody can create a branch the pins accept. To cut a
  maintenance branch, the owner lifts `release-branches-are-reviewed` on that one repository,
  creates the branch, and puts the ruleset back.
- The same rule refuses one more push. Platform's cut-release has a backfill mode
  (`backfill_evidence_only`) that pushes an evidence commit straight to the branch it runs on.
  Dispatched on a `release/<M>.<m>.x` branch, that push is now refused, because the branch
  needs a pull request. A backfill there goes through a pull request, or the owner lifts the
  ruleset for that run. A normal cut-release on a release branch pushes tags only and is not
  affected.

Closing the gap needs one push identity that can be a bypass actor, such as a GitHub App
installed on every organisation, used by the clock and release lanes and by nothing else. Then
`main-keeps-its-history` becomes `main-is-reviewed` with that app as its one bypass actor. A new
identity is the owner's to create (ADR-0025). Ticket 87 records it as waiting on the owner.

`observation-lane.json` is not here. It is a push ruleset, and GitHub does not allow push
rulesets on public repositories (ADR-0023, amended 2026-09-03).

## Hub observation delivery, 2026-10-05 (delegated, ADR-0025)

Adding required review without changing truth.yml's direct push made run 386 lose its
recording to GH013. The rule stays. truth.yml prepares the original gitsign clock commit
on a unique `observations/truth/<run-id>-<attempt>` ref and opens a PR. A pending PR is
not a recorded observation; only the default-branch log is citable.

`truth-delivery.yml` runs separately after the clock completes, including a red clock.
It checks out trusted default-branch code, never pending code, and verifies run metadata,
original signature claims, lane paths, unchanged preceding TRUTH bytes and the exact PR
head. The existing `pavc-other-hand` App supplies the required review and ordinary merge,
without bypass, squash or rebase. The original signed clock object survives the merge.
Its owner-recorded development mode and expiry gate every mutation. Outside that window,
delivery stays pending for a human; no ambient mode override reopens it.

The existing App private key is an environment secret named `PAVC_OTHER_HAND_PRIVATE_KEY`
in `truth-delivery`, restricted to the current default branch (`main` at deployment). A
read-only validation step runs before the step that reads it. The minted token is scoped
to this hub repository and contents/PR writes. A separate read-only job token reads
official metadata, including the exact Actions attempt; the existing App has no Actions
grant. The writer has no bypass or administration authority. GitHub grants its writes
across this hub, so the trusted
controller enforces the observation paths and exact PR; the token has no path-specific
permission. The key itself still belongs to the existing multi-org App.
No repository secret, gate credential, pending checkout or new identity is introduced.
If the default branch is renamed, update the environment's allowed branch as well.

The workflow may be dispatched with a completed run id and exact attempt to retry a failed delivery.
Before either mutation it refreshes default-branch authority. Any source change since the
trusted checkout leaves delivery pending for retry; stale mode records cannot authorize it. It
refuses a changed head or conflict and never reports recorded until the exact clock object
and line are on main. Pending refs retain the conservation check's failure until delivery.
