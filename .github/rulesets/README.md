# The review rulesets (ticket 87 item 1)

These four files are the rulesets applied to the nine estate repositories on 2026-09-24. Each was
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

No file carries a bypass actor. GitHub refuses the GitHub Actions integration (app id 15368) as
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
