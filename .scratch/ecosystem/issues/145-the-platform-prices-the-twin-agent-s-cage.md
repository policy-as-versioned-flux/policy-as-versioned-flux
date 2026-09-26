# 145 — The platform prices the twin agent's cage

Type: task
Status: claimed
Blocked by: none

## Question

Graduated 2026-09-25 from grilling ticket 30, decisions 3, 10, 11, 12 and 15 (delegated), and
ADR-0031.

1. **A dial table for the twin-agent class**, beside `graded/cage.py` `TIERS`, with the four rows
   of ticket 30 decision 11 and a reduction and a cost for each rung.
2. **The reductions are derived from the misuse paths each rung closes** (decision 15), each path
   named as a twin-agent row in `twin/ecosystem-misuse-catalogue.yaml`:
   - the writer job pushes a looser declaration: closed at `isolated` only;
   - the writer job merges or tags through REST: closed at `isolated`;
   - a misleading proposal PR is merged by a human: closed at `quarantine`;
   - a model step writes a wrong binding or forecast: closed at `restricted`; about £0 on price,
     because model claims are grade 5 and `price_eligible: false`.
   The run cost of every rung is £0 in cash, and cost stays out of selection.
3. **The scenario** (decision 12): loss magnitude is the gap between the adopter's residual at the
   loosest rung and at the selected rung, over the window until the gate detects the act;
   frequency is a threat-register row feeds publishes.
4. **A new `prices[]` kind** for a subject that is not a pod. The tier fold
   (`wargamer/wargamer.py:249-258`) must key on the subject, so this line never folds into a
   Namespace tier. `verify/pound-seam/pound_seam.py` (exactly one `source: twin` line, known
   sources only) and the handbook's kind list learn the kind.
5. **The adopter's selection policy selects the rung**; the proposer proposes it; a human merges.
   The twin never prices or selects its own cage.

## Notes

The platform release and the adopter recomposes wait for the owner's authorisation. Ticket 143
reads the selected rung.

## Comments

**2026-09-26, claimed and built, owner-instructed.** The owner wrote on 2026-09-25: "i'm afk you
have all the approvals you need to deliver". That authorises feature branches and pull requests in
the hub and the estate repositories; it does not authorise a merge, a push to any main, a tag, a
release or a workflow dispatch, which the integrator does. Three pull requests build this ticket,
one per repository, each on a branch named `ticket-145-agent-cage-price`: platform
(policy-as-versioned-platform/platform), feeds (policy-as-versioned-feeds/feeds) and the hub
(policy-as-versioned-flux/policy-as-versioned-flux). No release is cut here. Every decision the
brief left open is **delegated** (ADR-0025) and recorded below with its reason.

**What the platform PR builds.** `graded/cage.py`: `TWIN_AGENT_TIERS` (its own
`TWIN_AGENT_TABLE_VERSION` 1.0.0), the four rows of ticket 30 decision 11 with what the twin agent
may write, whether a model step runs, whether the local clock runs and a cash `cost` of 0 at every
rung; `infra` is absent. `reduce` is not on the row: `TWIN_AGENT_PATHS` names the four misuse
paths of decision 15 and the loosest rung that closes each, `twin_agent_reduce(rung, reach)`
derives a rung's reduction from what the paths still open at it can land, `twin_agent_residuals`
and `twin_agent_tcor` follow, and `DETECTION_WINDOW` carries the gate's cadence with its source
and assumptions. `compose/composition.py`: `PRICE_KINDS` gains `agent-cage`; `price_twin_agent`
prices ONE line per composition (`source: platform`, `subject: twin-agent`) from the same
composition's `source: twin` line residuals, the window and the register row
`scheduled-agent-misuses-write-credential` at the major the adopter pins, derives each path's
reach off the served tree and the composed prices (`_twin_agent_reach`), and has the adopter's
own selection-policy package pick the rung; a line that cannot be priced is a named could-not-look
on the line. `fair/fair.py`: `pert_mean` and `expected_ale`, the closed-form expectation of the
same compound process `simulate` samples. `wargamer/wargamer.py`: `subject_of`, the Namespace fold
skips any line whose subject is not the Namespace, `wargame_agent_cage` rows and
`_propose_agent_cage`; `wargamer/tier_pr.py` reports those proposals and lands no file for them;
`wargamer/rejection_ledger.py` fingerprints on `source: twin` and `kind: twin`;
`shift-left/tier_binding.py` inherits the subject rule and plants a twin-agent line at every rung
to show the Namespace verdict does not move; `compose/handbook.py` renders the line and names its
inputs; `compose/README.md` and `graded/README.md` document it. Selfchecks extended in every file
touched.

**What the feeds PR builds.** threat-register payload major 4: `payload.schema.v4.json` (a
`threats` map per institution, each row a frequency with its basis and either its own magnitude or
a `magnitude_basis` naming the subscriber), `v4/feed.json` (the headline threat, lef, lm_gbp and
both bases byte-for-byte v3's; the one new row per institution), `bump.yaml` set to `major` with
the reason, `to_fair_scenario.py threat <payload> <party> --threat <row> [--lm lo,mode,hi]` (the
publisher's reader for the row, refusing by name with no magnitude), `verify-feeds.sh` grading the
row's basis, and `fetch/source/threat-register.json` moved to the v4 payload so the scheduled
fetch computes `none` against it. `bump.py` computes `major` for v3 -> v4 under `rule.yaml`.

**What the hub PR builds.** `verify/pound-seam/pound_seam.py`: `KINDS` gains `agent-cage`; leg 3b
grades the line's shape and re-derives its gap, magnitude and amount from the same document; a
new estate leg re-picks the rung through the adopter's own package and runs platform's tier fold
with and without the line; an adopter composed under a platform tag that predates the kind is a
named could-not-look naming the pin. Check 3 still counts `source: twin` lines and stays honest:
the line's source is `platform`. `twin/ecosystem-misuse-catalogue.yaml` version 9 gains the four
twin-agent rows, each naming a mechanism, what its path reaches and why, and which served check
reads the act; they anchor on hub paths and wait on this ticket for the platform side.
`talk/verify-manifest.txt` declares the two new could-not-looks. `CONTEXT.md` gains the
`agent-cage` line under **Cage**. `tests/test_misuse.py` names the twelve rows.

**Decisions, each delegated (ADR-0025).**

1. *The residual at a rung is what the loosest open path can still land; doors onto one loss do
   not add.* The two token paths reach the whole declaration gap (the writer's `contents: write`
   pushes or REST-merges a looser declaration that the gate reads within the window); the proposal
   path reaches none of it past the served pull-request gate, because every adopter's
   `shift-left.yml` runs `tier_binding.py` on every pull request and a merge over a red gate is the
   human's act (ADR-0031 decision 1); the model step reaches no priced figure, because no price
   rests on a grade above 3. Measured consequence: `restricted` AND `quarantine` carry
   `baseline`'s residual and `isolated` collapses it (reduce 0, 0, 0, 1). The £ never selects
   `restricted` or `quarantine` for its own sake; a party that wants either declares it as a floor.
   Reason: a partition of the loss across the doors would need a per-door frequency nothing
   published or signed supplies, and typing one is what decision 15 forbids; the reach reading
   derives every figure from the served tree and the composed prices and names the one path
   (`misleading-proposal-merged-by-a-human`) as could-not-look wherever the served gate is absent.
2. *The frequency row is `published`, grade 3, N x C / M.* N = 1, the one marketplace action each
   served twin-sweep.yml references by floating tag (`actions/checkout@v4`, read at driftwood
   155db9e, tuppence 5deffe6, ludlow b8e14f7 on 2026-09-26); C = 2 (min, mode) to 7 (max), the
   marketplace actions with a published compromise in 2025 (tj-actions/changed-files CVE-2025-30066
   and reviewdog/action-setup CVE-2025-30154, both in CISA's alert of 2025-03-18; the max adds the
   five downstream reviewdog actions Wiz named on 2025-03-17); M = 23,757 marketplace actions
   (Chaiwut and Nikiforakis, "Time for Actions", IEEE SecDev 2025). 8.42e-5 to 2.95e-4 events a
   year. The row's `could_not_look` names what the rate does not count (misuse after a compromise,
   the unpinned hub checkout and `pip install pyyaml`, a maintainer's compromised account, a pwn
   request on the repository's own workflow) and what would close it. Reason: it is the only door
   with a published count over a published population; a per-repository rate exists nowhere
   (GitHub's Octoverse publishes Actions minutes and repository totals, not the population running
   workflows), and forming one from a sample share and a repository total would be a typed number.
3. *The window is the gate's schedule, one day.* `truth.yml` `cron: '47 5 * * *'`, read at hub
   9c3b1f22; it assumes the run fires as scheduled (the ~5h cron delays measured on the estate's
   first firings are not in it), that the loss runs until detection not repair, and that one day is
   the interval's upper bound. Copied into platform's table with its source, because the
   composition cannot read the hub. Reason: decision 12 fixes the window as "until the gate
   detects it", and since ticket 142a lane.py detects a push or a merge by a scheduled identity.
4. *The amount is the closed-form expectation, not the simulated mean.* `fair.simulate` rounds each
   year's event count to an integer, so at 8e-5 events a year it resolves no event in any of its
   10,000 years and returns 0.0 by construction. `fair.expected_ale` is the same process's mean
   (E[N] x E[X] over the PERT means); the line says so (`scenario.annualised_by`) and carries the
   simulated ALE and `p_gt_0` beside it. fair.py's selfcheck shows the two agree within 15% on the
   canonical triple where the count resolves. Reason: reporting the engine's resolution floor as
   the price would be a number about the engine, not the scenario; changing how `simulate` samples
   the count would re-price every line in the estate and is out of this ticket's scope (named
   below as a defect).
5. *The line is carried beside the exposure, never summed into it.* `EXPOSURE_KINDS` is unchanged:
   the gap is a slice of a residual the twin line already carries, and summing it would count it
   twice. Reason: the same rule ticket 84 gave `supersede`.
6. *The rung's declaration is the composed line itself.* No new adopter file: the twin-sweep
   writer job (ticket 143 item 4) reads `prices[kind=agent-cage].proposed_tier` off the served
   `composed/evidence.json`, the compose-check re-derives that document on every pull request, and
   the pull request that recomposes it is the proposal a human merges. `tier_pr.py` reports the
   proposal and lands no edit. Reason: landing a hand-edited rung on a line the compose-check
   re-derives would be a drift the gate refuses, and the adopters' repositories are outside this
   ticket's scope. What 143b reads today, before any pin moves: no rung (the line is a named
   could-not-look), which falls closed to `isolated` (ADR-0022) for all three adopters.
7. *The party's `overlay.floor` clamps the twin-agent rung too.* Reason: a floor is the party's
   own tighten-only statement about how loose any of its cages may be; applying it can only
   tighten. No adopter declares one today.
8. *Every price shows the weakest grade it rests on.* The register row is grade 3; the twin line
   states no grade today (null until ticket 144's payload major), so the line carries
   `rests_on_grade: null` with a basis saying which half is unstated, never a grade this seam
   invents.
9. *The catalogue rows anchor on hub paths and wait on this ticket for the platform side.* An
   anchor into the estate clone resolves against platform's `main`, which does not carry the table
   until the platform PR merges; claiming it before that would be the catalogue asserting a
   defence the estate does not have (the catalogue's own rule). The platform anchors are written
   beside each row as comments; when this ticket resolves, the integrator swaps `waits_on` for
   them, or `verify-misuse.sh` goes red by design.

**Measured, on a throwaway merge of each branch onto its repository's origin/main (platform
541d2aab, feeds ff3ac9a, hub 9c3b1f22), in a planted estate of detached worktrees at driftwood
155db9e, tuppence 5deffe6, ludlow b8e14f7, nist f83126f, ico abcb3a8, insurer 32ea73d, with the
hub venv interpreter.** Baseline on origin/main first: every platform selfcheck rc 0, composition
selfcheck rc 0 with 103 OK lines, feeds verify rc 0 with 72 ok lines, hub pound-seam selfcheck ok,
tests/test_misuse.py 43 passed, verify-misuse PASS with 2 could-not-look. On the branches:
`graded/cage.py selfcheck`, `fair/fair.py selfcheck`, `fair/verify-fair-tail.sh`,
`wargamer/wargamer.py selfcheck`, `wargamer/tier_pr.py selfcheck`, `wargamer/rejection_ledger.py
selfcheck`, `wargamer/verify-wargamer.sh`, `shift-left/tier_binding.py selfcheck`,
`shift-left/verify-tier-binding.sh`, `compose/handbook.py --selfcheck` (57 checks) all rc 0;
feeds `to_fair_scenario.py selfcheck` rc 0, `verify-feeds.sh` rc 0 with 80 ok lines, `bump.py v3
v4` prints `major`, `fetch/threat-register.py --dry-run` computes `none`; hub
`pound_seam.py selfcheck` ok, `tests/test_misuse.py` 43 passed, `verify-misuse.sh` PASS with 6
could-not-look by name (the four new rows wait on this ticket), `verify-tier-binding.sh` PASS over
the real adopters through the changed fold. Composed through the CLI: the real driftwood (register
pin v2) carries one `agent-cage` line, unpriced, naming `threat-register@v2`, the row and this
ticket, proposing no rung; tuppence carries one, unpriced, naming its missing `source: twin` line.
A copy of driftwood with its register pin moved to v4 prices the line at 0.4213 GBP a year: gap
1,290,399.36 GBP (twin-line residual at `baseline` 1,328,352.28 minus at `isolated` 37,952.92)
over 1 day, frequency (8.4186e-05, 8.4186e-05, 2.9465e-04), residuals baseline = restricted =
quarantine = 0.4213 and isolated 0, driftwood's selection policy 1.1.0 picks `baseline` against
its 40,000 GBP band, and platform's tier fold gives the Namespace `isolated` with the line and
without it. Over an estate serving that document, `pound_seam.py check` prints the leg-3b PASS,
the re-pick PASS and no FAIL; over the estate as served today it prints one named SKIP per
adopter ("carries no `agent-cage` line ... composed under platform v4.0.0"), which
`talk/verify-manifest.txt` now declares, and the wrapper exits 3 on that line. The composition
selfcheck on the branch, in the planted estate: rc 0 with 105 OK lines, two of them the new
agent-cage legs (the real driftwood's unpriced line by name; the v4 copy priced at 0.4213 GBP,
`baseline`, the fold unmoved). CI results are appended below after each push.
