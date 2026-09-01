# 60 — The scheduled observations land in the citable number, and steps 3–4 happen once for real

Type: task (AFK)
Status: claimed
Blocked by: none

## Question

The conversion machinery merged 2026-08-31 but the gate cannot consume it: verify-reconcile calls need_substrate before its cluster-free five-fact sample grading, so it SKIPs in CI before reading drift/samples.jsonl, and verify-e2e-step4 has no sample-reading path. Rewire both so a lane-committed sample grades in the citable run without a cluster. Then watch the first firings (drift-sample 06:20Z, propose-tier 06:47Z, renovate-run, twin-sweep from 2026-09-01): confirm the post-fix propose-tier composes, and when a residual really crosses a band, let the proposal PR open and be human-merged once — the first real step 3. Correct ticket 40's Answer, which cites a four-of-five-facts observation no citable record supports, with a dated note. Done = step 4 and the three verify-reconcile checks grade from a real scheduled sample on a TRUTH line, and one proposal PR has opened and merged.

## Notes

Charted by the ambition review of 2026-08-31. Closes review findings: M7 (gate cannot convert, 2 confirmed findings incl. ticket 40's uncitable citation), M9 (step 3 never real).
Record: [REVIEW-2026-08-31.md](../REVIEW-2026-08-31.md).

## Comments

**2026-09-01, session note (agent, ticket claimed ~09:05Z).** State found and work done:

- The four driftwood clocks exist but none has ever fired on schedule. drift-sample.yml and
  twin-sweep.yml reached driftwood main 2026-08-31 16:23Z (merge bd19e8c); their first cron
  chance was today 06:20Z/07:05Z and both missed. renovate-run.yml (cron 06:11Z) and
  propose-tier.yml (cron 06:47Z) only reached main today at 08:51Z/08:37Z, after their times.
  The estate-wide pattern today is a ~5-hour GitHub schedule delay (platform's 01:23Z fetch
  fired 06:20Z; feeds' 03:17Z fired 08:37Z; the hub's 05:47Z truth fired 10:41Z/11:50Z on the
  two prior days), so the driftwood clocks are expected late today; a background poll watches.
- The post-fix propose-tier composes: the 08:57Z run (pull_request, PR #20 threat-register v2
  merge) re-composed at 2026-09-01 and the proposer returned `[]` — no band crossed, no
  proposal PR, ledger derived from 0 closed-unmerged proposal PRs. Step 3 stays unfired until
  a residual really crosses a band; that is correct behaviour, not a defect.
- Rewires built and tested:
  - verify-reconcile.sh (driftwood, tuppence, ludlow): the five-fact grade runs FIRST,
    cluster-free. A lane FAIL is red with or without a cluster. A lane PASS carries the
    verdict when no local cluster exists. With a local cluster, every live assertion runs
    unchanged. Committed on branch `ticket-60-grade-the-lane-sample` in each
    .estate-clone/<unit>; patches under .scratch/ecosystem/patches/ticket-60/.
  - verify-e2e-step4 (hub): gains grade_lane_sample — with no cluster it grades the adopter's
    lane sample instead of exiting could-not-look. Pushed as hub 031b91a.
  - clone-estate.sh (hub): sets gpg.x509.program=gitsign in every unit clone so
    five-facts.py's %G? attribution can verify the lane commit on the truth runner. Same push.
  - Both no-cluster paths simulated with failing kind/docker stubs: honest combined SKIP now;
    PASS/FAIL comes from the sample once one exists.
- Ticket 40's Answer carries a dated correction: the four-of-five-facts claim is withdrawn.
  No five-fact record exists on driftwood main, and drift-sample.yml had never run on the
  remote when that Answer was written.

**Owner checklist (the enact guard rightly refuses these from the agent):**

1. Publish the three unit branches. In each of .estate-clone/driftwood, .estate-clone/tuppence
   and .estate-clone/ludlow, the branch `ticket-60-grade-the-lane-sample` holds one commit;
   publish it to origin, then open and merge the PR. If a clone was refreshed first, apply the
   matching patch from .scratch/ecosystem/patches/ticket-60/ instead.
2. When a proposal PR opens on driftwood (a residual crossing a band, on the clock), review
   and merge it once — the first real step 3.
3. Nothing else. The sample, the grading and the TRUTH line land on their own clocks.

**2026-09-01, run 18 (09:41Z).** The hub push triggered the gate. `TRUTH 2026-09-01T09:41Z
run=18 hub=031b91a ... pass=57 fail=3 skip=22 excluded=2 total=84`. The rewired step 4 now
grades through the lane path on a citable run: its SKIP reason is "the lane sample cannot stand
in: drift/samples.jsonl carries no five-fact sample yet", which flips to a real grade the moment
drift-sample.yml commits its first record. The three verify-reconcile rows still show the old
substrate-first SKIP because the unit merges are the owner's. The three fails are: the stale
deck (pre-existing, ticket 66's ground) and two new driftwood twin reds that are ticket 61
fallout (party.yaml pins threat-register/v2; the twin's lookup and rendered feed still carry
v1) — graduated as [72 — A feed bump re-renders the twin's derived artefacts](72-a-feed-bump-re-renders-the-twin-s-derived-artefacts.md).

**2026-09-01, the clocks fired (11:34Z–11:41Z).** The driftwood schedules did fire today, ~5.5h
after cron: renovate-run 11:34Z (success, no new bump — v2 is already consumed) and
drift-sample 11:41Z — which FAILED on its first firing ever: `curl: (23) Failure writing output
to destination` on `curl -o kind`. Root cause: the install step downloads into the checkout
cwd, and this repo's own `kind/` directory makes that filename unwritable. A second latent bug
sat in the same shape: `kyverno.yaml` and `flux-operator.yaml` would have been left untracked
in the tree, and the observation cage would then have failed the run as a declaration outside
the lane. One fix covers both: download and apply from `RUNNER_TEMP`. All three adopters carry
the same `kind/` directory and the same workflow, so the fix is committed to all three
`ticket-60-grade-the-lane-sample` branches (second commit; patches updated). Until it merges,
every drift-sample firing dies the same way and no sample can land.

**Owner checklist, sharpened:** each unit branch now carries TWO commits (grade-first
verify-reconcile.sh + the drift-sample RUNNER_TEMP fix). After merging the three PRs, either
wait for the next 06:20Z-cron firing (expect ~5h delay) or fire drift-sample.yml once by hand
from the Actions tab — the grader accepts any lane commit with an Actions run id and the
sampler's signed identity, and the workflow declares workflow_dispatch itself.
