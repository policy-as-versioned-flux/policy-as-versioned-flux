# 118 — A green that rests on luck may not promote

Type: task
Status: open
Blocked by: none

## Question

Graduated 2026-09-21 from [the Laya and loophole map](../../laya-loophole/map.md), ticket 10.

Renumbered from 111 to 118 on 2026-09-22 by
[ticket 117](117-two-tickets-share-the-number-111.md). It took 111 after
[111 — The cage names priority classes its own delivery does not deliver](111-the-cage-names-priority-classes-its-own-delivery-does-not-deliver.md)
had already landed on main, so it is the later of the two.

The skill-eval harness records two states. `twin/skills.py:103` declares
`ItemResult(item_id, passed: bool)`, and `EvalResult.score` is the fraction that passed. A skill
that reached the right answer for the wrong reason is therefore indistinguishable from one that
reasoned correctly. Both raise the score, and the score is what a threshold grades.

The trdrbot prior art solves this with a twelve-line pure function of two booleans,
`attribute(thesis_held, profited)`. It yields five verdicts, and the lucky-win case carries a
learning signal of `None` so the memory update is **skipped** rather than applied at 0.5. That was
measured, not guessed: a 0.5 "learn nothing" signal was dragging every block toward 0.5.

1. Add a third state to `ItemResult`. A right answer whose stated basis is wrong is neither a pass
   nor a fail. Decide the name, record it with the reason, and do not reuse `passed`.
2. Exclude that state from the numerator, not from the denominator. Luck must lower the attributable
   rate, not raise the score.
3. Where a skill's corpus item carries no checkable basis, mark it unscoreable rather than passed.
   `twin/scoring.py:16` already has `ScoreError`, "not scoreable, a refusal", so the estate holds
   the concept and the harness does not.
4. Wire a gate check. A threshold graded on a score that counts luck grades nothing.

## Done

Three states in the harness, the attributable rate recorded beside the score in
`twin/skill-scores.jsonl`, and a gate check that grades it.

## Notes

The estate is **ahead** of the prior art on scoring rules and baselines. `twin/forecast_book.py`
has blindness by construction, co-registration and an external adversarial baseline. Take the
attribution idea only. Do not import the rest.

Licence and attribution: the source is MIT and its copyright line names a real person. Crediting
the idea in public is a named-individual question for ticket 82.

## Build, 2026-09-22

Built on branch `ticket-118-luck-may-not-promote`. Hub only. No unit repository changed.

### What landed

- **Four item verdicts in `twin/skills.py`.** `ItemResult(item_id, verdict)` replaces
  `ItemResult(item_id, passed)`. The verdict comes from `attribute(answer_right, basis_held)`, a
  pure function of two readings:

  | answer right | basis held | verdict |
  |---|---|---|
  | no | any | `wrong` |
  | yes | yes | `right` |
  | yes | no | `wrong-basis` |
  | yes | could not be checked | `unscoreable` |

- **A skill states its basis** by returning `Stated(answer, basis)`. A corpus item may carry a
  `basis`. `evaluate()` scores the answer with the scorer and the basis with `basis_scorer`, which
  defaults to exact match. The harness still names no real skill.
- **Two rates on `EvalResult`.** `score` is right answers less wrong-basis ones, over all items.
  Luck never raises it. On a corpus with no basis it equals the old score, so the log's history
  still compares. `attributable_rate` is `right` items over measured items. It is `None` when
  nothing was measured, never 0.
- **The threshold grades the attributable rate.** `outcome` is `not-measurable` when
  `measured_count` is below `min_items` or the rate is `None`. Otherwise it is `pass` or `fail` on
  the rate. `clears_threshold` keeps the bare score comparison for the per-skill guards.
- **`record_score()` writes** `attributable_rate`, `wrong_basis` and `unscoreable` beside `score`,
  `measured_count` and `total`. `as_dict()` carries the same, and each item as `{"id", "verdict"}`.
- **`twin/skill-scores.jsonl` carries the rate.** One real run of the seven metrics was appended
  with `python -m twin.record_skill_scores` at `2026-09-23T06:42:40Z`, model version
  `heuristic-0.1.0`. The log grew from 13 rows to 20. All seven new rows record
  `attributable_rate: null`, because no real corpus item carries a basis.
- **Model permission condition 1 reads the rate.** `permission_for()` compares the row's
  `attributable_rate` with the tree's threshold, the same way it already read `measured_count`
  and the tree's minimum. A row with no rate, or a null one, is refused. The score must clear the
  bar too, because an honest row's rate never exceeds its score. The live seam in
  `.claude/skills/classify-and-judge/assets/validate_claim.py` calls `permission_for()`, so it
  reads the rate with no change of its own.
- **The gate check** is `verify/twin-evals/verify-attributable-rate.sh`, declared `waits:` in
  `talk/verify-manifest.txt`. Four legs: the verdict table, a planted 16-item fixture, the rate
  reaching record and permission, and the seven real metrics plus the committed log.
- **Adjacent checks follow the rate.** The harness guard
  `skill_eval_harness_is_agnostic_and_thresholds_are_guarded` now also fails a toy skill that is
  right on every item for a wrong stated reason. `verify-corpus-size.sh` counts measured items
  against the minimum. `verify-twin-evals.sh` grades the rate when a row has one.
  `verify-model-permission.sh` gains two item 1 controls: a 0.950 score on a 0.400 rate, and a row
  with no rate.
- **The toy fixture states its basis.** `toy_classifier` returns `Stated(text.upper(), TOY_BASIS)`
  and all 16 toy items carry `TOY_BASIS`, so the fixture proves an attributable pass.
- `CONTEXT.md` gains **Wrong basis** and **Attributable rate**, and its **Not measurable** entry
  says the minimum counts measured items. `twin/README.md`'s seam-3 bullet and the
  `twin/skill-thresholds.yaml` header say the same.

### What the gate reports today

Read off `bash verify/twin-evals/verify-attributable-rate.sh` in the worktree on 2026-09-23. Exit
3, and `talk/truth_manifest.py`'s `judge()` reads the last line as `declared waits`.

| metric | items | measured | unscoreable | score | rate | min_items |
|---|---|---|---|---|---|---|
| signal-classify | 23 | 0 | 23 | 1.000 | none | 16 |
| evolution-judge | 4 | 0 | 4 | 1.000 | none | 12 |
| causal-claims | 4 | 0 | 4 | 1.000 | none | 16 |
| causal-claims-grade-accuracy | 4 | 0 | 4 | 1.000 | none | 16 |
| gameplay-lens | 3 | 0 | 3 | 1.000 | none | 9 |
| substrate-generator | 3 | 0 | 3 | 1.000 | none | 16 |
| ethics-gate | 5 | 0 | 5 | 1.000 | none | 16 |

Every real answer is right and none stands on a checkable basis, so no real metric has a rate.
That moves `signal-classify` from pass to not measurable. `verify-corpus-size.sh` now reports 7 of
7 short where ticket 112 reported 6 of 7; its last line still matches its own `waits:` pattern.
`verify-model-permission.sh` exits 0 and grants 0 of 14 pairs, as before. Item 1 now refuses all
14 pairs, where ticket 112 recorded 12.

The planted fixture, from the same run: a skill right on all 16 items for a wrong stated reason
fails at rate 0.000 and score 0.000. The negative control prints what a two-state harness saw: 16
of 16 right, a pass at 1.000 against 0.80. Sixteen right with four wrong-basis rate 0.800 and pass.
A fifth wrong-basis item rates 0.762 and fails.

### Decisions

- **The third state is named `wrong-basis`** (delegated). It names what the harness observes: the
  stated basis was checked and did not hold. "Lucky" names a cause the harness never measures. A
  skill that learned a shortcut is right on a wrong basis every time, and that is not chance.
- **Four item verdicts, and the Done's three states are the scored ones** (delegated). `right`,
  `wrong` and `wrong-basis` are scored. `unscoreable` is the absence of a score, as
  `not-measurable` is the absence of an outcome. The ticket asks for both the third state and
  unscoreable, and they differ: one is evidence against the skill and the other is no evidence.
- **Item verdicts share no word with run outcomes** (delegated). `right` and `wrong`, not `pass`
  and `fail`. An item verdict can never be read as a run outcome. The two levels stay apart.
- **A wrong-basis item counts toward `measured_count`** (delegated). Its basis was checked and
  failed, so it is measured. Leaving it out would let luck shrink the corpus instead of lowering
  the rate, which is item 2 backwards.
- **An unscoreable item does not count toward `measured_count`** (delegated). Nothing was
  measured. This is what lets item 3 hold: a basis-less corpus cannot pass.
- **A wrong answer is `wrong` whatever its basis, and is measured** (delegated). A wrong answer is
  evidence against the skill with or without a basis. So an unscoreable item can only ever
  withhold evidence for a skill, never add it. The rate on a mixed corpus is therefore biased
  down, never up. A gate that errs, errs toward refusing.
- **The threshold grades the rate, and `score` stays** (delegated). The score now leaves out
  wrong-basis answers, so luck never raises it. On a corpus with no basis it equals the old score,
  so `detect_regression()` and `verify-twin-evals.sh`'s fall check still compare against history.
  The per-skill guards keep `clears_threshold`, which proves a threshold gates something.
- **A skill states its basis with `Stated`, and a skill that states none is unscoreable**
  (delegated). One wrapper keeps the harness agnostic and leaves every existing scorer alone. A
  skill that declines to state a basis can reach not measurable, never pass.
- **The rate is `None`, never 0, when nothing was measured** (delegated). A 0 would give a run
  that measured nothing the same grade as a run of pure luck. The prior art measured that failure.
- **Condition 1 reads the rate the way it reads `measured_count`: off the row** (delegated). The
  permission grades the row, and condition 2 already ties the row's digest to the tree. A row
  written before this ticket has no rate, so its score may rest on luck, and absence is not
  consent. Condition 1 also reads the score, because an honest row's rate never exceeds it: a row
  whose rate clears the bar and whose score does not is not an honest row.
- **Condition 9 stays on the score** (delegated). The frozen-field baseline is computed from
  answers alone, so it compares with the answer score. The rate is already graded at item 1.
- **A fresh heuristic run was appended to the committed log** (delegated). Done asks for the rate
  in `twin/skill-scores.jsonl`. The log is append-only, so the old rows stay as they were. The run
  used the recorder's own entry point, not typed lines.
- **The gate check is its own script, declared `waits:`** (delegated). This follows ticket 112's
  decision. The amber is the estate's own state, a corpus not yet labelled, and folding it into
  `verify-corpus-size.sh` would hide which reason is which.
- **No real corpus gains a basis here** (delegated). Labelling a basis per item is corpus work,
  like growing corpora was for ticket 112. `ethics-gate`'s scorer already folds `stopped_at` into
  the answer, so it is part of the answer, not a stated basis.
- **Take the attribution idea only** (delegated, per the Notes). No code was lifted from the prior
  art. The idea taken is the verdict table and the null that is not 0.5. Crediting the idea in
  public stays with ticket 82, and no person is named here.

### How it was tested

- Red first. 13 new tests in `tests/test_skills.py` failed on import before `attribute`,
  `Stated` and the verdicts existed. Four existing ones failed with them, through `_corpus` and the
  agnostic list. In `tests/test_model_permission.py`, 4 new tests failed against the unchanged
  `twin/model_permission.py`, stashed for the run, and passed with it restored.
- `bash verify/twin-evals/verify-attributable-rate.sh` failed at leg 4 before the log carried the
  rate: `0 of 13 rows carry it`. After the recorder run: `7 of 20 rows carry it`, exit 3.
- `.venv/bin/python -m pytest -n0 -q` over `test_skills`, `test_model_permission`,
  `test_record_skill_scores`, `test_truth_manifest`, `test_corpus_size` and `test_local_clock`: 181
  passed. Then `test_model_permission` alone after one test was strengthened: 52 passed.
  `test_skills` alone after the doc edits: 45 passed.
- The same, over `test_signal_classify`, `test_record_skill_scores`, `test_evolution_judge`,
  `test_gameplay_lens`, `test_ethics_gate`, `test_substrate_generator`, `test_causal_claims`,
  `test_honest_build` and `test_grades`: 183 passed. `test_every_green`: 23 passed.
- mypy over `twin tests conftest.py`: no issues in 197 source files.
- `bin/twin verify --only` on the agnostic guard, the append-only log guard,
  `hash_changes_are_authorised` and the six per-skill guards: 9 passed.
- `verify-twin-evals.sh` exit 0, `UNMEASURED: 7`. `verify-model-permission.sh` exit 0, 0 of 14
  granted. `verify-corpus-size.sh` exit 3, 7 of 7 short, `declared waits`.

### What remains

- **Nothing waits on the owner.**
- **The corpora need bases.** No real item carries a checkable basis, so no real metric has a
  rate. Each skill must return `Stated(answer, basis)` and each corpus item must carry a `basis`
  before any threshold grades anything real. The Laya map's ticket 03 corpus work is where labels
  come from. The check turns PASS by itself when enough items carry bases and every rate clears.
- **The first recording clock run after merge** re-grades both amber checks on the runner. The
  integrator reads that run and records any fall.
