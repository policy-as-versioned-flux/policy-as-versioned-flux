# 05 — "Within thresholds" becomes a checkable permission

Type: task
Status: resolved
Blocked by: none

## Question

On 2026-09-21 the owner permitted a model to judge on a GitHub clock, within thresholds. Turn that
condition into something a check can grade.

Today the estate forbids it in two places. `CONTEXT.md` says anything needing judgement is a skill
a human runs. `.claude/skills/classify-and-judge/SKILL.md` sets `disable-model-invocation: true`
and says nothing there ever runs on a GitHub clock.

Design and build the permission:

1. A model may judge on a clock for one skill only when the newest recorded score for that skill
   and that `model_version` clears the versioned threshold in `twin/skill-thresholds.yaml`.
2. The corpus digest of that scoring run must match the corpus in the tree. A stale digest revokes
   the permission.
3. The clock records which `model_version` judged each claim. A claim with no recorded model is
   not a permitted claim.
4. The permission covers judging only. It never covers merging. A judged claim still lands as a
   pull request that a human merges.
5. A skill with no recorded score has no permission. Absence is not consent.

6. **The permission binds at a seam the actor cannot route around.** Added 2026-09-21 from ticket
   10, and it is the most valuable thing that ticket found. The trdrbot prior art has a complete,
   working permission ladder that its own open defect I-68 records as consulted **twice in 89
   decide cycles**, a rate of 2.2%. Its own words: "The refusals that matter are therefore not the
   sizer's; they happen upstream in prose." A permission the caller may decline to consult is not
   a permission. Name the seam, and prove by a check that no path reaches a judged claim without
   crossing it.
7. **Count the refusals.** trdrbot's sibling defect I-16 records that declines are never scored, so
   the blind spot has two halves. A skill that declines to judge must leave a counted row, or the
   permission's real exercise rate is unknowable.

Write a gate check that grades all seven, and wire it into the truth surface.

## Done

The permission rule in code, a gate check, and the check recorded on a citable run.

## Notes

Build this whether or not Laya passes ticket 04. The rule is estate doctrine about any model on a
clock. Laya is only the first candidate to meet it.

The threshold is the weak link, not the mechanism. `twin/skill-thresholds.yaml` already refuses a
lowered threshold with no `authorised_by`. A threshold measured on 4 items is still a threshold
measured on 4 items. Ticket 03 owns that problem. Say so in the check's own output.

**Ticket 10 resolved 2026-09-21, and this ticket is unblocked.** Its verdict on the size ladder was
**leave the mechanism, take its failure**. Items 6 and 7 above carry that failure across. Do not
copy the ladder's shape. The tier counts 0, 5, 15 and 40 are chosen, not derived, and only the 40
has a measured basis.

**Added 2026-09-21, from ticket 04. The answer this ticket was told to wait for.**

8. **`act_probability` is not an escalate signal, and the check must refuse a constant head in
   general.** Ticket 02 measured exactly 1.000000 on 16 calls and handed it on as a hypothesis.
   Ticket 04 ran the model over the estate's own six corpora and read exactly 1.000000 on **all 93
   questions, and on all 279 across three runs**. The distinct-value set is `[1.0]`. Ticket 04 also
   found two more near-constant heads in the same model: "admit" on all five `ethics-gate` sensors
   and "product" on all four `evolution-judge` organisations.
   This is item 6 from the other side. A permission that always says yes is not a permission, and
   a signal that never varies is not a signal. **The check grades the variance of the field a
   permission reads, not only its value.** A head whose recorded outputs carry one distinct value
   across a run revokes the permission it was supposed to grant, whatever that value is.

9. **A threshold cleared below the corpus's own constant baseline does not grant the permission.**
   Item 1 says the newest recorded score must clear the versioned threshold. Ticket 04 measured
   that `signal-classify`'s threshold is 0.80 while "always economic" scores 0.913 on its corpus,
   so Laya's recorded row reads `"passed": true` at 0.870 having caught neither of the two items
   the corpus discriminates on. **Item 1 as written would grant that model a permission.** The
   check computes the best constant answer the corpus admits and refuses a score at or below it.
   The Notes below already say the threshold is the weak link; this is the measured shape of it.

## Answer

**Built, and it grants nothing.** "Within thresholds" is now ten conditions in
`twin/model_permission.py`, a seam in `.claude/skills/classify-and-judge/assets/validate_claim.py`,
and a gate check at `verify/model-permission/verify-model-permission.sh`. On the citable run
below the check is green and **0 of 14 (metric, model version) pairs hold a permission**. Both
models in the score log are refused, each for a measured reason.

### What was built

1. `twin/model_permission.py` — the rule. Each of the ticket's nine items is a named `Condition`
   on the `Permission` the module returns, so a refusal always says which item refused and why.
2. `twin/model-head-readings.yaml` — item 8's record for a model the gate cannot re-run, holding
   ticket 04's three measured constant heads.
3. `twin/record_skill_scores.py` gains `corpus_facts()` and `fitted_models()`. The corpus a
   permission is derived from is now the same corpus the score was recorded on, from one list.
4. **Both** of the clock's validators gain `--clock`, and `talk/local-clock.sh` passes
   `--clock local` on both of its validator invocations. `validate_forecast.py` refuses a
   GitHub-clock forecast outright, because no entry in `twin/skill-thresholds.yaml` governs a
   derived probability and absence is not consent.
5. `tests/test_model_permission.py` — 41 tests at seam 2.
6. `verify/model-permission/verify-model-permission.sh`, in `talk/verify-manifest.txt` as
   `self-proof`.

### The seam (item 6), and why it cannot be routed around

The seam is `validate_claim.py::validate`, and **the clock runs it, not the model**.
`talk/local-clock.sh` already copies the twin package and the skill to a judge tree before the
child model starts, refuses any committed file that is not a `*.claim.yaml`, and runs the
validator over every one of them. A refusal fails the step and the branch is never pushed. That
is the half trdrbot's ladder lacked: its caller chose whether to consult it, and chose not to in
87 of 89 cycles.

The remaining way round was the clock field itself, so **the clock is derived, never believed**.
`derive_clock()` reads `GITHUB_ACTIONS`, `GITHUB_RUN_ID` and `GITHUB_WORKFLOW` from the
environment; a run carrying any of them is a GitHub clock whatever the file or the caller says.
The last lie available is a workflow unsetting a marker, and the check asserts against the
workflow files that none does. This is the same discipline the `--headless` fix applied when the
no-override rule rested on the model declaring itself headless.

Only a `github` clock is governed. A `human` run is the skill's ordinary path and a `local` run
keeps eco-system ticket 92's own terms, so nothing already working changed. That is a scoping
call, and it rests on the owner's own words: the permission he gave on 2026-09-21 was for a
**GitHub** clock, which ADR-0024 and ticket 75 Q10 forbade outright before that.

**"No path" means every path, and the check found the second one by turning red.** The clock's
steps table names two validators, not one: `validate_claim.py` for the `classify` row and
`validate_forecast.py` for the `derive` row. Passing `--clock` to the second broke it, and
`verify/twin-evals/verify-derived-forecast.sh` went red on the gate. That was a real regression
this ticket caused, and it is also the evidence item 6 asked for: a second path to a model-made
artefact existed and did not cross the seam. Both validators now take the flag, and the check
asserts that **every** validator the steps table names accepts it, so a third skill added later
cannot skip the seam by shipping a validator that does not know about it.

### A tenth condition, forced by the first run of the nine

The first run of the nine **granted the incumbent heuristic a permission on five of seven
metrics**. The estate had already said why that is wrong, in its own words:
`twin/evolution_judge.py`'s `CORPUS_KIND` reads `harness-mechanism`, which its own comment
defines as "while every corpus item is one the heuristic was fitted to", and
`verify-twin-evals.sh` prints that word on every run. A score on the corpus the model was fitted
to is not evidence of judgement, so condition 10 refuses it. It is the same defect class as items
8 and 9: a number that cannot come out any other way. One edit to `CORPUS_KIND`, the day a
held-out corpus exists, lifts it. It touches the incumbent alone; a candidate never fitted on
these corpora is untouched.

### Item 9's bar is derived, and it reproduces ticket 04 by an independent route

`frozen_field_baseline()` measures the best constant answer a corpus admits, in three steps and
with nothing hand-listed:

1. **Which fields the scorer reads.** Each leaf of the answer is perturbed to a sentinel across
   the corpus; a leaf whose perturbation changes no item's score is not read, and is granted.
2. **The candidates.** Every distinct value the answers take at that leaf, plus the mean and the
   median where the values are numeric. The mean matters: `causal-claims`' elasticity constant is
   exactly its own corpus's mean.
3. **The score.** One read leaf is frozen at a candidate and every other field is granted from
   the item's own correct answer.

Read it precisely: **the best score a model reaches while holding one field the scorer reads
constant, with every other field granted correct.** A score at or below it means the corpus
cannot show the model doing that field's work.

The method reproduces both numbers ticket 04 measured by hand before this module existed:
`signal-classify` **0.913** on `steep`, and `causal-claims` **1.000** on `edge.elasticity.mode`.
Two independent routes to the same number is the reason to believe either, and the check asserts
the agreement on every run.

### The measured table, 2026-09-21

| metric | `heuristic-0.1.0` | `laya-1c5edc17` |
|---|---|---|
| signal-classify | refused: 10 | refused: 8, 9 |
| evolution-judge | refused: 10 | refused: 1, 8, 9 |
| causal-claims | refused: 8, 9, 10 | refused: 1, 8, 9 |
| causal-claims-grade-accuracy | refused: 10 | refused: 8 |
| gameplay-lens | refused: 10 | refused: 1, 8, 9 |
| substrate-generator | refused: 9, 10 | refused: 1, 2, 5, 8, 9 |
| ethics-gate | refused: 10 | refused: 1, 8, 9 |

`substrate-generator` refuses Laya at items 2 and 5 because ticket 04 recorded no row for it at
all, which is call 16 working: not measurable and bad are different answers.

### A new measured finding: five of seven thresholds cannot detect a model that learned nothing

Ticket 04 found this for `signal-classify`. Deriving the baseline for all seven extends it.

| metric | n | threshold | baseline | frozen field |
|---|---|---|---|---|
| signal-classify | 23 | 0.80 | **0.913** | `steep="economic"` |
| evolution-judge | 4 | 0.75 | **0.750** | `evolution_position=0.55` |
| causal-claims | 4 | 0.80 | **1.000** | `edge.elasticity.mode=0.375` |
| causal-claims-grade-accuracy | 4 | 0.80 | 0.750 | `edge.evidence_grade=3` |
| gameplay-lens | 3 | 0.65 | 0.333 | `opportunities=[]` |
| substrate-generator | 3 | 0.80 | **1.000** | `channels.events` held constant |
| ethics-gate | 5 | 0.80 | **0.800** | `admitted=false` |

`substrate-generator`'s 1.000 is its own finding: the scorer checks that a channel is non-empty
and never checks what is in it, so the corpus does not grade channel content at all.

This is **reported and not graded**, which the ticket's own Notes asked for. The corpus is what
is short: ticket 03 measured 326 items needed per skill against the estate's 42, and eco-system
ticket 112 owns the sizing. Turning it red here would make this check a proxy for a corpus nobody
can grow for 341 days. Item 9 refuses such a score anyway, so no permission rests on a weak
threshold.

### Item 7, and the half trdrbot's I-16 records

A `github`-clock claim file must carry `run.declined`, a list of `{subject, reason}`. An empty
list is an answer and a missing key is refused, because a ladder that never counts its declines
cannot report its own exercise rate. `Exercise.rate` over zero rows is **undefined and says so**,
never 100%. There is no second ledger file: the count lives in the artefact the seam already
reads, so the two cannot drift.

### Two holes found while building, and closed

- **Item 1 read the wrong threshold.** A row in `twin/skill-scores.jsonl` carries the threshold
  as it stood when the run happened. Reading the row's own number would let a raised threshold
  be cleared by a score graded against the old bar. Item 1 now reads
  `twin/skill-thresholds.yaml` in the tree, and refuses a score recorded against a different
  bar. That is item 2's reasoning applied to the bar instead of the corpus.
- **The seam covered one of the two paths.** See above.

### What is still not true

- **No permission is granted, so none has been exercised.** The rule is proved by a fabricated
  model that clears all ten, which the check asserts is granted. Without that positive control a
  rule that refuses everything would pass every negative control there is.
- **The environment derivation is exercised with a synthetic environment.** No real GitHub
  Actions run has crossed this seam, because no model holds a permission to put on one. The only
  remaining lie, a workflow unsetting a marker, is asserted against the workflow files rather
  than observed at run time.
- **0 claim files are at rest** in this checkout and its estate clone, so the estate-wide
  exercise rate is 0 of 0, and the check prints that rather than a rate.
- **`CONTEXT.md` is untouched.** Ticket 09 owns that rewrite, and the map forbids assuming its
  wording. `.claude/skills/classify-and-judge/SKILL.md` gained a dated amendment that describes
  the mechanism and changes no rule: its "nothing here ever runs on a GitHub clock" still stands,
  because nothing holds a permission.

### The citable run

```
TRUTH 2026-09-21T20:50Z run=local hub=10d3b7b enact=development units=[driftwood=6e23dbe@main
feeds=8cb7ae8@main ico=c65b6b2@main insurer=c991160@main ludlow=cd2cc9b@main nist=b9f5fff@main
platform=bbda376@main tuppence=fca6a58@main] pass=70 [observed=18 self=39 simulated=4 meta=9]
fail=17 skip=29 [never=5 waits=24] excluded=8 total=124 ceiling=105
```

`verify/model-permission/verify-model-permission.sh` reads **PASS** on that run.

**Read the counts with care. This is a local run, not a numbered one, and it is not comparable
to run 254.** The last recorded run, 254 on 2026-09-20, reads `pass=83 fail=10 total=125`. The
estate clone on this machine has moved since: platform is at `bbda376@main` where run 254 read
`1d3420e@v3.2.0`, and docker is not reachable here. **8 of the 17 failures are in
`.estate-clone/platform/`** and the rest are hub reds that pre-date this ticket, including the
`regulator-data-mispriced-downstream` standing red `tests/test_misuse.py` names in its own
docstring. Only a scheduled run on the real runner produces a number that compares.

What can be said without that comparison, because it was checked directly:

- **No failing script reads anything this ticket changed.** Each of the ten failing hub scripts
  was grepped for `model_permission`, `validate_claim`, `record_skill_scores`, `local-clock.sh`
  and `verify-manifest`; all ten return zero matches.
- `verify/twin-evals/verify-twin-evals.sh`, which imports `record_skill_scores`, **passes**.
- `.estate-clone/feeds/verify-news-headline-skill.sh`, which runs the claim validator,
  **passes**.
- `verify/twin-evals/verify-derived-forecast.sh` is back to its declared SKIP after the
  regression above was fixed: `fail` fell from 18 to 17 and `skip` rose from 28 to 29 between
  the two runs, which is that one script moving.
- `verify/local-clock/verify-local-clock.sh` skips for the same declared reason as before: the
  marker only exists on the owner's machine.

The test suite: 41 new tests in `tests/test_model_permission.py`, and
`tests/test_local_clock.py`, `tests/test_derived_forecast.py`, `tests/test_skills.py` and
`tests/test_record_skill_scores.py` all pass. Two suite-level reds stand and both pre-date this
ticket: `tests/test_misuse.py::test_the_four_rows_grade_against_this_checkout` (the standing red
its own docstring names) and `tests/test_invariant_suite.py::test_the_suite_is_green` (invariant
44, `drift_window_is_actually_being_sampled`, the drift floor unreachable since 2026-08-16).

### For ticket 09

- The Laya ADR can now say Laya is refused **by the estate's own rule**, on five of the ten
  conditions, and not only that it scored badly.
- The ADR must state that the incumbent is refused too, on item 10. A rule that cleared the
  incumbent and refused the candidate would be a rule fitted to the answer.
- The permission grants judging and never merging, `Permission.covers` is `{"judge"}`, and a
  model makes no `override` and prices nothing. ADR-0024's amendment can cite the code rather
  than restate the rule.
