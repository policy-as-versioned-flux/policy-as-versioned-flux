# 60 — The scheduled observations land in the citable number, and steps 3–4 happen once for real

Type: task (AFK)
Status: prepared
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

**2026-09-01, 12:01Z: propose-tier's first SCHEDULED firing.** Success. It re-composed at
today's date through the pinned platform and returned `[]` — no residual crosses a band, no
proposal PR, ledger derived from 0 closed-unmerged proposal PRs. Same verdict as the 08:57Z
pull_request firing. The proposer is on its clock and composes; the first real step 3 now waits
only on a residual actually crossing a band (a feed bump, an EOL ramp date, or a size change).
The hub's scheduled truth run also fired (run 19, 10:41Z, delayed from 05:47Z cron): same
figures as run 18.

**2026-09-01, 12:31Z: twin-sweep's first scheduled firing failed** — on the ticket 72 defect
(the stale forward-intel feed), not on this ticket's machinery, plus a `bash -e` bug that makes
its own re-render branch unreachable. Both recorded on ticket 72. All four driftwood clocks
have now had their first scheduled firing today: renovate-run green, propose-tier green (no
crossing), drift-sample red (fixed on the branch), twin-sweep red (ticket 72).

**2026-09-01, 14:20Z: the day's watch is complete — Status moves to prepared.** All ten first
scheduled firings across the three adopters are observed and diagnosed:

| clock | driftwood | tuppence | ludlow |
|---|---|---|---|
| renovate-run | green (11:34Z) | green (13:29Z) | green (14:05Z) |
| drift-sample | red, curl 23 (11:41Z) | red, curl 23 (13:32Z) | red, curl 23 (14:07Z) |
| propose-tier | green, no crossing (12:01Z) | red, deleted feeds branch (13:42Z) | red, deleted feeds branch (14:17Z) |
| twin-sweep | red, ticket 72 (12:31Z) | — (none) | — (none) |

Every red is diagnosed and owned: curl 23 is fixed on the three `ticket-60-grade-the-lane-sample`
branches; the deleted-branch reds are ticket 62 (comment added there); twin-sweep is ticket 72.
The AFK half of this ticket is done: both gate rewires are live on the hub (TRUTH run 18 grades
step 4 through the lane path), the three unit rewires plus the drift-sample fix are committed and
patched, propose-tier is confirmed composing on schedule, and ticket 40 carries its correction.

What Done still needs, and cannot happen from this seat: the owner merges the three unit
branches (checklist above); the next drift-sample firing after that lands the first real sample;
the TRUTH run that reads it grades step 4 and the three verify-reconcile checks from it. The
proposal-PR-merged half waits on a residual actually crossing a band. Re-run this ticket after
the merges to verify the first graded sample and then resolve.

**2026-09-01, ~14:30Z: the three PRs are open.** The owner chose the guard's one-run flip
(`development` written to twin/ENACT_MODE for the pushes, restored to `operations` at once, no
diff left). The branches are published and each carries the two commits:

- driftwood: https://github.com/policy-as-versioned-driftwood/driftwood/pull/21
- tuppence: https://github.com/policy-as-versioned-tuppence/tuppence/pull/13
- ludlow: https://github.com/policy-as-versioned-ludlow/ludlow/pull/11

The merge stays the owner's click.

**2026-09-01, ~20:45Z: the first real samples landed.** The owner merged the three PRs
(driftwood #21, tuppence #13, ludlow #11) and the three drift-sample dispatches ran (queued
~6h, the day's Actions delay). Every run committed a signed lane record. The headline: on
driftwood's ephemeral cluster, nist and platform grade ALL FIVE FACTS TRUE — the composed set
in force, from gitsign-verified signed sources, on a cluster reconciling the real remotes.
That is the estate's central claim, observed for the first time.

Two defects, both real, both named, neither this ticket's machinery:

1. **Verifier skew (ticket 73).** driftwood-composed and ludlow-composed fail fact 2:
   "certificate is not yet valid" — the controller verifies at tagger time and the Fulcio
   cert's notBefore postdates it by seconds. Tuppence's tag verified true.
2. **Sampler webhook race (fix on branch `ticket-60-sampler-waits`, all three units).**
   tuppence and ludlow read 16-of-16 composed objects absent because the ResourceSet was
   applied before Kyverno's admission webhook served (dry-run: connection refused) and the
   run sampled before the retry healed. Instrument fault by ticket 54's rule. The fix waits
   for both controllers before applying the composed set, and waits on ResourceSets before
   sampling.

The citable grading run is dispatched (truth run 33557360933). Its TRUTH line grades step 4
and the three verify-reconcile checks from these real samples — FAIL where a fact is false,
which is the design.

**2026-09-01, ~20:55Z: round 2 published (owner approved a second one-run guard flip).**

- driftwood: https://github.com/policy-as-versioned-driftwood/driftwood/pull/22
- tuppence: https://github.com/policy-as-versioned-tuppence/tuppence/pull/14
- ludlow: https://github.com/policy-as-versioned-ludlow/ludlow/pull/12
