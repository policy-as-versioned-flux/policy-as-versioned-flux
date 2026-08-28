# The end-to-end harness (ticket 52)

The seven steps of [NORTH-STAR](../../NORTH-STAR.md) §4, one verify script each, discovered by
`talk/verify-all.sh` like every other check in the estate.

## The rule

**The harness runs inside the gate. It is never a presenter-run number.**

`talk/verify-all.sh` is the one gate and its TRUTH line is the only citable number (D1, D4,
ADR-0023). These seven scripts are ordinary members of its glob: each is graded on its own exit
code — `0` observed true, `3` could not look, anything else observed false — and each contributes
its own pass/skip/fail to the same TRUTH line as the 60-odd unit scripts. There is no separate
"harness run", no separate score, and nothing here may be quoted on a slide or in a demo except
by way of a scheduled gate run.

Two consequences that are easy to get wrong:

- **A step never turns absence into a pass.** A step that cannot see its fact exits 3 and names,
  on its last line, the thing it could not look at and the ticket that owns it.
- **A step never asserts the old shape to stay green.** When a ticket is mid-flight (26 is
  landing the cage's Kyverno half as this is written), the step exits 3 naming that ticket rather
  than asserting whatever shape happens to be live.

The harness owns no state. It reads the same signed artefacts Flux reads, and it does not write
to any repo, cluster or feed. Steps 2 and 3 work on throwaway copies in directories that are not
git repos at all; step 4 only reads the standing KinD clusters; nothing here opens a PR, applies
a manifest or cuts a tag. `lib.sh` carries a `cluster_up`/`cluster_down` pair for the ephemeral
KinD cluster ticket 40's scheduled workflow will bring up — it deletes itself on exit and never
touches `driftwood`, `tuppence` or `ludlow`.

## The seven steps

| # | Script | What it observes | Owner ticket(s) |
|---|---|---|---|
| 1 | `verify-e2e-step1-regulator-publishes.sh` | ico's newest penalty-schema envelope validates against the feed contract and its version is a tag on the real ico remote | 21 (built); the tag itself waits on `cut-release.yml` |
| 2 | `verify-e2e-step2-renovate-pins-and-reprices.sh` | the single edit a merged Renovate PR makes moves the adopter's `prices[]` through composition, offline | 25 (built) |
| 3 | `verify-e2e-step3-price-crosses-band-pr-opens.sh` | a residual crossing the adopter's own signed appetite band selects a different tier through the adopter's own selection-policy package, and the proposer would open the PR (dry run) | 25 (python half built); the tier landing in force is step 4 |
| 4 | `verify-e2e-step4-flux-reconciles-cage.sh` | on the live cluster: the source is Ready at the commit it pins, the Kustomization applied that same revision, the governed Namespace is in its inventory — then the cage: the served cage policy live, the Namespace's declared tier, and a Running pod wearing it | 26 (the cage's Kyverno half, the Namespace render, the isolated rung), 40 (the signed tag on the real remote), 42 (tuppence and ludlow) |
| 5 | `verify-e2e-step5-twin-forecasts.sh` | which of the twin's five step-5 artefacts exist, by path | 29 |
| 6 | `verify-e2e-step6-provenance.sh` | every published artefact resolves to a tag on its publisher's real remote or is honestly queued; every release workflow's gitsign identity regexp is anchored on its own org/repo; the real Fulcio cert subject matches that regexp with its Rekor entry validated | 21 (the feed contract) plus each unit's own `release.yml`; the insurer's declared quote feed is ticket 36 |
| 7 | `verify-e2e-step7-honesty.sh` | steps 1–6 each report exactly one honest verdict, printed as a table | 52 |

Step 4 is deliberately scoped to `driftwood`. Widening it to `tuppence` and `ludlow` is ticket 42;
set `E2E_ADOPTER` to point steps 4 and 5 at another adopter.

## What step 7 does and does not fail on

Step 7 is a roll-up of *reporting*, not of *results*. It fails only when a step cannot be graded
honestly:

- the step script is missing, hangs, or ends on something that is not `PASS:`/`FAIL:`/`SKIP:`;
- its exit code and its last line disagree;
- it claims `PASS` while that same line names something it could not look at (a green that could
  not look is a red, NORTH-STAR §3.6);
- it exits 0 while its own transcript carries a "could not look" / "NOT OBSERVED" line anywhere,
  not only on the verdict line.

**What it cannot catch, and never could:** a step that simply asserts something FALSE. The hedge
list is a list of confessions, so a `PASS:` line with no confession in it grades as honest however
untrue it is — the OpenBao claim that stood green for 27 days had no hedge word in it. Only the
step's own script, observing the fact instead of a config string, can catch that class. Step 7
checks *reporting*, and its two nets are the confession on the verdict line and the confession
buried in the transcript.

It does **not** fail because a step reports FAIL or SKIP — the gate already grades that step on
its own, and counting the red twice would move the TRUTH line for one fact. Step 7's own grading
has a runnable check: `bash verify-e2e-step7-honesty.sh selfcheck` plants a hedged PASS, an
exit-code mismatch, a non-conforming step and a green whose transcript confesses mid-run, and
requires all four to be caught while an honest SKIP and an honest FAIL pass through. **The
no-argument path runs that selfcheck first**, so a regression in step 7's own grading fails the
step rather than shipping quietly.

## Running it

```sh
bash verify/e2e/verify-e2e-step7-honesty.sh     # all seven, as a table
bash verify/e2e/verify-e2e-step4-flux-reconciles-cage.sh   # one step
bash talk/verify-all.sh                          # the gate, the only citable number
```
