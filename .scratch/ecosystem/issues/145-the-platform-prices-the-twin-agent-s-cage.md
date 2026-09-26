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

**CI, 2026-09-26.** Hub PR #143 (head 0348f96c): the `twin` workflow's `demo`, `typecheck`,
`reproduce-elsewhere` and three `determinism` jobs pass; `tests` and `invariants` fail with
exactly main's standing red (invariant 45, `flux_coverage_floor_is_still_reachable`: 1 failed,
2891 passed on this head and on main 9c3b1f22 run 36210103426; 72 passed, 1 failed on both), so
no failure is this branch's. The branch push also ran the truth workflow (run 350, gate
36213266620): 121 result rows and the same two FAIL rows as main's run 349, none added and none
removed; `verify/misuse/verify-misuse.sh` PASS and `verify/pound-seam/verify-pound-seam.sh` SKIP
(waits) on the line this ticket declares. Platform PR #46 (head ea2f1bb2) and feeds PR #9 (head
b1d9459b) have no pull-request CI in their repositories; their verify scripts ran locally as
recorded above, and the release workflows run them again at the tag.

**2026-09-26, review round 1 fixed, owner-instructed.** The owner wrote on 2026-09-25: "i'm afk you
have all the approvals you need to deliver". Under that authorisation the reviewer's findings on
the three pull requests are addressed on the same branches (platform #46, hub #143; feeds #9 is
unchanged), with no merge, tag, release or dispatch. The blocking finding first, then every minor
one, each accepted; the decisions each fix forced are **delegated** (ADR-0025) and recorded here.

*Blocking, leg 3b measured only the line's own labels.* The PASS claimed the line was priced "at
threat-register@v4's frequency" and "over 1 day(s)" but read both off the line: a line priced at
ten times the row's frequency, or over a thirty-day window, with its amount and residuals recomputed
to match, was green. Leg 3b now measures against served artefacts outside the line: the frequency
against `institutions.<adopter>.threats.scheduled-agent-misuses-write-credential.lef` in the
estate's feeds tree at the version the party's own party.yaml pins (`_agent_register`, the way leg
4 reads ico's weights; a `register_version` on the line that is not the pinned one is a FAIL; a
pinned tree with no row is a SKIP by name), and the window against the interval of the one
`schedule: cron` in the hub's own `.github/workflows/truth.yml`, read from the checkout the check
runs in (`_gate_window`; a fixed hourly, daily or weekly cron derives, any other shape is a SKIP by
name, never a guess). The PASS now states what was read: the cron, the file, the row and its path.
Decision: the register is read at the estate clone's version path (feeds main), the precedent leg 4
set, and the PASS names that path; the portability check reads at the pinned tag and owns that
comparison. Decision: the two new SKIP shapes stay undeclared in talk/verify-manifest.txt, because
neither is reachable on the served estate (the hub's cron is daily and feeds main carries v4 once
PR #9 merges), so either appearing fails the gate by design.

*Minor, the fold skipped any non-Namespace subject.* Only the kind that declares a subject may carry
one: `wargamer.folds_into_namespace` refuses (ValueError, a missing instrument) a line whose subject
is not the one its kind declares, in both directions: a `feed` line hand-carrying `subject:
twin-agent` (which used to drop out of the fold, so a looser declaration graded bound) and an
`agent-cage` line carrying the Namespace's subject or none (which would have caged every pod for
the twin agent's rung). `select_party_tier`, `wargame_cage_tier`, `wargame_agent_cage` and
`tier_binding.bind` share the one rule; planted in both selfchecks; the hub's check_agent_cage
prints the refusal as "platform's tier fold refused this document". Nothing is less safe: a document
that used to fold out a line now refuses to fold at all.

*Minor, P1 and P2 typed 1.0.* `_twin_agent_reach` now reads `.github/workflows/twin-sweep.yml`
(`_served_sweep`): a `schedule:` trigger and a job whose effective permissions grant `contents:
write` derive the whole gap for both token paths, naming the file, the cron and the job on
`reach_basis`; a sweep not served, not scheduled or declaring no `contents: write` is a named
could-not-look, because the token's scope then falls to a repository default the composition cannot
read and a token minted another way is not in the file. Decision: the sweep is identified by the
served file name the ticket, ticket 143 and verify/schedules all use, not by any scheduled workflow
holding a write token (each adopter serves three others: drift-sample, propose-tier, renovate-run,
which are other actors and not this cage's subject). Decision: a rung that leaves a could-not-look
path open has no residual and is not a candidate, so the pick falls closed; measured in the
composition selfcheck: a read-only sweep picks `isolated`, a pull-request gate without the recompose
job picks `quarantine`. P3 now needs both the tier-binding step AND the recompose job that fails on
drift against `composed/` (`_served_pull_request_gate`, matched by what the step does, not a job
name), and names both. On the three served trees every figure is what it was (1.0, 1.0, 0.0, 0.0),
so no price moved; the basis did.

*Minor, `restricted != baseline` hard-coded.* Leg 3b re-derives every residual from the line's own
`reach` through the four paths' closures (`_rederive_agent_residuals`, cage.py's rule restated in
the seam), refuses a `closes` map that is not the decision's and a `reach` that names other paths,
and states in the PASS whether restricted carries baseline's residual rather than requiring it. A
None baseline beside a numeric restricted, consistent with a model path that could not be derived,
is not a FAIL; selecting the rung with no residual still is.

*Minor, the fold-moves FAIL printed the tier only.* It prints the tier without and with the line and
the lines that differ. Unreachable by a document plant now that the fold refuses a malformed subject;
it guards a platform fold that regresses.

*Minor, the agent-cage drift row's confidence.* `tolerance` is None on the row (`old_amount` travels
beside it), so proposer_bounds grades a rung move at STRUCTURAL_CONFIDENCE and reports it whether
the amount rose, held or fell; planted for all four shapes.

*Minor, the selfcheck typed the feeds triple.* It reads the expected `lef` off the register file it
composed against (the estate's v4 or the planted fixture).

*Minor, the handbook's frequency absence on an unpriced line.* A line with no amount reads "no loss
frequency was read for ...: the line could not be priced"; the selfcheck sees the sentence (58
checks).

**Measured, on the branches in the planted estate (platform 541d2aab plus the branch, feeds
ff3ac9a plus the branch, adopters at their served heads), hub venv python.** Platform:
`wargamer.py selfcheck`, `tier_pr.py selfcheck`, `rejection_ledger.py selfcheck`,
`verify-wargamer.sh`, `tier_binding.py selfcheck`, `verify-tier-binding.sh`, `handbook.py
--selfcheck` (58) all rc 0; `composition.py --selfcheck` rc 0 with 106 OK lines, three of them
agent-cage (the real driftwood unpriced by name; the v4 copy at 0.4213 GBP, `baseline`, the fold
unmoved, the reach basis naming twin-sweep.yml, its cron and job and shift-left.yml's two jobs; the
read-only sweep and the gateless copy falling to `isolated` and `quarantine`). Hub: `pound_seam.py
selfcheck` ok with 59 planted cases; `pound_seam.py check` over the estate as served rc 3, 30 PASS,
0 FAIL, four named SKIPs (one agent-cage wait per adopter and the standing switching one;
corrected in review round 2, which had read three); over an estate where driftwood serves a v4-priced document
composed by the fixed composer: 32 PASS, 0 FAIL, the leg-3b PASS naming cron '47 5 * * *' in
.github/workflows/truth.yml, the row at feeds/threat-register/v4/feed.json and every residual
re-derived. Adversarial re-plants through the real check: c (lef x10, amount and residuals
recomputed) 1 FAIL naming the served row; d (window 30 days, magnitude, amount and residuals
recomputed) 1 FAIL naming the served cron; b (subject dropped) 2 FAILs, the fold's refusal among
them; a `feed` line carrying `subject: twin-agent` 1 FAIL, the fold's refusal. `tests/test_misuse.py`
43 passed; `verify-misuse.sh` PASS (6 of 12 by path, the four twin-agent rows wait on this ticket by
name); `verify-tier-binding.sh` PASS over the real adopters through the changed fold. CI results
for the pushed heads are appended below.

**CI, 2026-09-26, review round 1 heads.** Hub PR #143 (head 569f78ea), twin workflow run
36216690922: `demo`, `typecheck`, `reproduce-elsewhere` and the three `determinism` jobs pass;
`tests` and `invariants` fail with exactly main's standing red (invariant 45,
`flux_coverage_floor_is_still_reachable`: `tests/test_invariant_suite.py::test_the_suite_is_green`,
1 failed, 2891 passed, 16 skipped on this head and on main 9c3b1f22 run 36210103426; 72 passed, 1
failed, 2 skipped on both). The branch push also ran the truth workflow (run 351, gate
36216689399, TRUTH hub=569f78e): 121 result rows, 87 PASS, 2 FAIL, 32 SKIP, row for row the same
as main's run 349 (36210103413, hub 9c3b1f2), the same two FAIL rows (`verify/forge-review`,
`verify/schedules`), none added and none removed; `verify/misuse/verify-misuse.sh` PASS and
`verify/pound-seam/verify-pound-seam.sh` SKIP (waits) on the declared agent-cage line. Platform PR
#46 (head ed4f735) and feeds PR #9 (head b1d9459b, unchanged this round) have no pull-request CI in
their repositories; the platform checks ran locally as recorded above.

**2026-09-26, review round 2 fixed, owner-instructed.** The owner wrote on 2026-09-25: "i'm afk you
have all the approvals you need to deliver". Under that authorisation the reviewer's second-round
findings on the three pull requests are addressed on the same branches (platform #46, hub #143;
feeds #9 is unchanged), with no merge, tag, release or dispatch. The blocking finding first, then
every minor one, each accepted; the decisions each fix forced are **delegated** (ADR-0025) and
recorded here with their reason.

*Blocking, the amount measurement ran only under the line's own label.* Leg 3b re-derived the amount
as the PERT-mean frequency times the PERT-mean magnitude only when the line's own
`scenario.annualised_by` said `expectation`; a line labelled `simulation` with its amount a thousand
times the product and its residuals recomputed to match was green, and the record claimed the amount
was re-derived. Now the amount is re-derived on every priced line whatever the label says, and any
`annualised_by` other than `expectation` is refused by name. Decision: refuse the label rather than
believe it, because a simulated mean is not re-derivable in the seam (`fair.simulate` rounds each
year's event count to an integer and resolves no event at this frequency) and the composer writes
`expectation` and nothing else (platform compose/composition.py `price_twin_agent`). Measured: the
reviewer's plant e through the real check over a v4-priced estate is now three FAILs (the label, the
product, and the reviewer's own per-customer restatement); the same amount under `expectation` fails
on the product; an amount that IS the product but labelled `simulation` fails on the label.

*Minor, the reach was believed.* The line's own `reach` was the only input to the residuals the seam
did not read off a served artefact. `_agent_reach` now restates the composer's `_twin_agent_reach`
in the seam (as `_rederive_agent_residuals` restates cage.py): the two token paths off the adopter's
served `.github/workflows/twin-sweep.yml` (a `schedule:` trigger and a job whose effective
permissions grant `contents: write`), the proposal path off the pull-request workflows' own `run`
steps (one running `tier_binding.py`, one recomposing with a drift test on `composed/` followed by a
non-zero exit), the model path off the grades the document's own prices rest on. The line's `reach`
must equal that derivation on every path. Decision: the served document must agree with the served
tree in BOTH directions, so a path the line leaves underived where the tree derives it is also a
FAIL, because the compose-check re-derives the document on every pull request and on a served main
the two can disagree only where that gate was bypassed. A tree the seam cannot read at all (no
adopter directory in the estate clone) is a SKIP by name, undeclared because unreachable. The
residuals are re-derived from the served reach, and the PASS names what was read: the sweep's file,
cron and job, the gate's binding and recompose steps, and that no priced line rests above grade 3.
Consequence: the reviewer's plant q (a None model-path reach on a line whose document carries no
grade-5 price) is now a FAIL, since the composer would not have written it; the round-1 selfcheck
plant for that shape now sits in a context whose served document does rest on a grade above 3.
Measured: plants f (every path 0.0) and f2 (the token paths 0.0) FAIL naming the served sweep's
cron and job; `_agent_reach` on planted trees derives (1.0, 1.0, 0.0, 0.0) for a scheduled sweep
with `contents: write` and a gate with both steps, and None by name for a read-only, unscheduled or
absent sweep, a commented-out or zero-exit drift test, a missing binding step, a push-only gate and
a grade-5 line; on the three served adopter trees it derives what the composer derives (1.0, 1.0,
0.0, 0.0).

*Minor, the tolerance.* `close_rel` (relative 1e-6, absolute 0) now compares the frequency, the
magnitude, the amount and the residuals; the gap keeps `close()` at its residual scale. Measured:
the reviewer's plant l (each frequency point nudged by 5e-7, 0.6 % at the mode, amount and residuals
recomputed) FAILs against the served row.

*Minor, the composer's gate reader read the raw file text.* `_served_pull_request_gate` now reads
each pull-request workflow's steps' `run` blocks with whole comment lines stripped, and a recompose
step is a compose invocation, then a drift TEST on `-- composed/` (`status --porcelain`, `diff
--exit-code` or `diff --quiet`), then a literal non-zero exit after it, in one step; each hit is
named `<file> job <job>` on `reach_basis`. Decision: a plain `git diff -- composed/` piped to a
pager is a print, not a test, and is not matched; reason: every served recompose step prints one
inside its drift block after the porcelain test, so a pattern that matched any `diff` still derived
0.0 with the porcelain line commented out (the first cut of this fix did, and the selfcheck caught
it). Measured: the reviewer's plant2 (driftwood's shift-left.yml with the porcelain line and its
`::error` commented out) now derives None for the proposal path and the pick falls to `quarantine`;
the composition selfcheck plants both that and a drift test whose exit is turned to zero; on the
three served trees every reach figure is what it was, and the basis now names `shift-left.yml job
compose-check` for both steps.

*Minor, "predates the kind" was asserted.* `_kinds_at_pin` reads `PRICE_KINDS` off
`<pin>:compose/composition.py` with `git show` in the estate's platform clone (clone-estate.sh makes
a full clone, tags included), never off its working tree. A pinned tag whose `PRICE_KINDS` lacks the
kind is the declared wait, now stating the tuple it read; one that carries the kind with no line
served is a FAIL (the document was not composed by the composer at the pin); a tag, file or line
that cannot be read is a SKIP worded so the manifest does not match it, undeclared because
unreachable. Decision: no fetch, because the wrapper promises to read committed files only and the
clone is full. Measured: over the estate as served, each adopter's wait names v4.0.0's tuple ending
at `supersede`; the selfcheck builds a tagged repository with git plumbing (no commit hook, no
signature) and reads v4.0.0 without the kind, v5.0.0 with it, and v9.9.9 as a could-not-look;
`talk/truth_manifest.py judge` says `declared waits` for the derived wait and `undeclared` for the
unreadable one.

*Minor, tier_pr's recompose branch was untested.* Selfcheck 4h feeds `run()` an agent-cage line
whose rung moved from `baseline` to `quarantine` beside an unchanged twin line: one landed row of
kind `recompose`, landed "by the next recompose pull request", naming `composed/evidence.json
prices[]` and the move; no `pr create` or `pr edit`; no branch created locally or on the remote; no
file edited; the Namespace declaration on main byte-identical; and with the rung unchanged, no row.

*Minor, the wording.* The round-1 paragraph read "the same three named SKIPs"; the served check
prints four (one agent-cage wait per adopter and the standing switching one). Corrected above.

**Measured, on the branches in the planted estate (platform 541d2aab plus the branch at 0f46233,
feeds ff3ac9a plus the branch at b1d9459, adopters at their served heads driftwood 155db9e, tuppence
5deffe6, ludlow b8e14f7), hub venv python.** Platform: `compose/composition.py --selfcheck` rc 0
with 106 OK lines (the three agent-cage legs: the real driftwood unpriced by name; the v4 copy at
0.4213 GBP a year, `baseline`, the fold unmoved, the basis naming `shift-left.yml job compose-check`
twice; the read-only sweep to `isolated`, and the gateless copy, the commented-out drift test and
the zero-exit drift test each to `quarantine`); `wargamer/tier_pr.py selfcheck` rc 0 with 4h;
`wargamer/wargamer.py`, `wargamer/rejection_ledger.py`, `shift-left/tier_binding.py`,
`graded/cage.py` selfchecks rc 0; `compose/handbook.py --selfcheck` PASS 58; `verify-wargamer.sh`
and `verify-tier-binding.sh` rc 0. Hub, on a throwaway merge of 01be36df onto origin/main c196a3c1:
`pound_seam.py selfcheck` ok with 70 planted cases (59 before); `verify-pound-seam.sh` rc 3 over the
estate as served, 30 PASS, 0 FAIL, 4 SKIP from the check (three derived agent-cage waits naming
v4.0.0's `PRICE_KINDS`, one switching) plus the wrapper's own summary line; over a plant estate where
driftwood, pinned to threat-register v4, was recomposed through the fixed composer: 32 PASS, 0 FAIL,
the leg-3b PASS naming the cron `'47 5 * * *'`, the row at `feeds/threat-register/v4/feed.json`, the
served sweep's cron `'5 7 * * *'` and job `sweep`, both gate steps in `shift-left.yml job
compose-check`, and every residual re-derived from that reach; the reviewer's nineteen plants through
the real check: the pristine document 0 FAIL, and c, d, e, f, f2, g, h, i, j, k, l, m, n, o, p, q, r,
s each red; `tests/test_misuse.py` 43 passed; `verify-misuse.sh` PASS with the four `_agent_reach`
anchors resolving; `verify-tier-binding.sh` PASS. CI results for the pushed heads are appended
below.

**CI, 2026-09-26, review round 2 heads.** Hub PR #143 (code head 01be36df, ticket head f7f78c35):
twin workflow runs 36220384889 (push) and 36220387173 (pull request) on 01be36df and 36220556389 on
f7f78c35: `demo`, `typecheck`, `reproduce-elsewhere` and the three `determinism` jobs pass; `tests`
and `invariants` fail with exactly main's standing red (invariant 45,
`flux_coverage_floor_is_still_reachable`: `tests/test_invariant_suite.py::test_the_suite_is_green`,
1 failed, 2891 passed, 16 skipped; 72 passed, 1 failed, 2 skipped), as on main 9c3b1f22 run
36210103426. The push of 01be36df ran the truth workflow (run 352, gate job 108344667451 of run
36220384882, TRUTH hub=01be36d): pass=87 fail=2 skip=32, 53 verdict rows, verdict for verdict main's
run 349 (36210103413, hub 9c3b1f2), the same two FAIL rows (`verify/forge-review`,
`verify/schedules`), none added and none removed; the only text difference is the pound-seam wait,
now naming v4.0.0's `PRICE_KINDS`; `verify/misuse/verify-misuse.sh` PASS and
`verify/tier-binding/verify-tier-binding.sh` PASS. The ticket-only push of f7f78c35 matched no truth
path and triggered no truth run. Platform PR #46 (head 0f46233) and feeds PR #9 (head b1d9459b,
unchanged) report no pull-request checks in their repositories.
