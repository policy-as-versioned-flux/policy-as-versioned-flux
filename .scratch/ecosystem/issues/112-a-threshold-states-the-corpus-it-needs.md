# 112 — A threshold states the corpus it needs

Type: task
Status: open
Blocked by: none

## Question

Graduated 2026-09-21 from [the Laya and loophole map](../../laya-loophole/map.md), ticket 10.

`twin/skill-thresholds.yaml` sets no minimum corpus size. `twin/skills.py` refuses only an empty
corpus, so a one-item corpus passes today. The six real corpora hold 42 labelled items in total:
`signal-classify` 23, `ethics-gate` 5, `evolution-judge` 4, `causal-claims` 4, `gameplay-lens` 3,
`substrate-generator` 3. Measured 2026-09-21.

A threshold of 0.8 on 3 items means the skill may miss nothing. A threshold of 0.75 on 4 items
means it may miss one. Neither number carries the confidence its presence implies.

1. Every threshold states the minimum corpus size it is valid at. A run below that size does not
   pass. It reports "not measurable", which is a third outcome and not a failure.
2. **Derive the number. Never import one.** The prior art's "~50 resolved forecasts" traces to one
   consolidated research document with no formula, no simulation and no citation. Its sibling
   figure of 152 is a real power calculation. Copying ~50 would put all six skills below the bar
   at once, which is a true statement badly arrived at.
3. Lowering a minimum is as visible as lowering a threshold. The existing
   `skill_thresholds_lowered_only_with_citation` check is the pattern.
4. Wire a gate check.

## Done

A stated, derived minimum per threshold, a third "not measurable" outcome in the harness, and a
gate check.

## Notes

This ticket makes several current greens go amber, and that is the point. The truth surface is
allowed to report less confidence than it does today.

## Contribution from the Laya map, ticket 03, 2026-09-21

Item 2 asks for a derivation and forbids an import. [Ticket
03](../../laya-loophole/issues/03-a-labelled-corpus-from-merged-human-claims.md) supplies a method
and runs it. `.scratch/laya-loophole/corpus/required_size.py` is the code.

**The method.** Name the effect the threshold must detect. Size n so the standard error sits at
half that effect. Report the per-bin number as well as the whole-set number, because the estimator
that grades the skill is the binned one.

**The measurement that makes this ticket urgent.** All six heuristics score 1.0 on their own
corpora. The rule of three gives the 95% lower bound on true accuracy for a perfect score on n
items. Five of the six thresholds are unfalsifiable at their current corpus size.

| skill | n | threshold | 95% lower bound at 1.0 | verdict |
|---|---|---|---|---|
| signal-classify | 23 | 0.80 | 0.870 | clears its threshold |
| ethics-gate | 5 | 0.80 | 0.400 | cannot clear its own threshold |
| evolution-judge | 4 | 0.75 | 0.250 | cannot clear its own threshold |
| causal-claims | 4 | 0.80 | 0.250 | cannot clear its own threshold |
| gameplay-lens | 3 | 0.65 | 0.000 | cannot clear its own threshold |
| substrate-generator | 3 | 0.80 | 0.000 | cannot clear its own threshold |

A perfect score on a 3-item corpus is consistent with a true accuracy of zero. That is the
"not measurable" third outcome item 1 asks for, and the table says which five skills report it on
the day this ticket lands.

## Build, 2026-09-22

Built on branch `ticket-112-threshold-states-corpus`. Hub only.

### What landed

- `twin/corpus_size.py` derives the minimum. It is the method from the Laya map's ticket 03,
  moved out of `.scratch/` because the gate runs it. Two routes, and the larger binds:
  1. **Standard error at half the effect.** The effect is `1 - threshold`: every heuristic scores
     1.000, and the threshold exists to catch a fall from there to the floor. The binomial variance
     is taken at its worst inside `[threshold, 1]`.
  2. **The rule of three.** A perfect score's 95% lower bound, `1 - 3/n`, must reach the threshold.
- `twin/skill-thresholds.yaml` states `min_items` on every entry. `twin/skills.py` refuses a file
  whose stated number is not the derived one, above or below, and one that states none.
- `EvalResult.outcome` is `pass`, `fail` or `not-measurable`. Below the minimum the run is not
  measurable whatever it scored. `passed` and `failed` are both false then. `clears_threshold`
  keeps the bare score comparison, which the per-skill guards use to prove a threshold gates
  something. `record_score()` writes `min_items` and `outcome` into each new score row.
- The citation guard now covers `min_items` as well as `threshold`, in
  `skill_eval_harness_is_agnostic_and_thresholds_are_guarded`.
- `verify/twin-evals/verify-corpus-size.sh` is the gate check. It is declared `waits:` in
  `talk/verify-manifest.txt`.
- `verify-twin-evals.sh` prints `NOT MEASURABLE:` for a short metric instead of `PASS:`. A fall
  against the same model version's record still fails a short metric.
- `CONTEXT.md` gains the term **Not measurable**. `twin/README.md`'s seam-3 bullet says the same.

### The derived minimums

Printed by `bash verify/twin-evals/verify-corpus-size.sh` on 2026-09-22.

| threshold | effect | SE route | rule of three | bins | min_items |
|---|---|---|---|---|---|
| 0.80 | 0.20 | 16 | 15 | 1 | 16 |
| 0.75 | 0.25 | 12 | 12 | 1 | 12 |
| 0.65 | 0.35 | 8 | 9 | 1 | 9 |

No threshold derives 50. The per-bin number equals the whole-set number here, because the harness
grades one proportion with one bin. Ticket 03's tenfold factor came from a binned ECE estimate.

### What the gate reports today

The same run. Six of seven metrics are not measurable, so the check is amber (exit 3, declared
`waits:`).

| metric | items | min_items | outcome |
|---|---|---|---|
| signal-classify | 23 | 16 | pass |
| evolution-judge | 4 | 12 | not measurable |
| causal-claims | 4 | 16 | not measurable |
| causal-claims-grade-accuracy | 4 | 16 | not measurable |
| gameplay-lens | 3 | 9 | not measurable |
| substrate-generator | 3 | 16 | not measurable |
| ethics-gate | 5 | 16 | not measurable |

Growing those corpora takes 62 more items, counted as the sum of `min_items - items` over the six
short rows. The two causal-claims metrics share one 4-item corpus, so 12 of those serve both, and
50 distinct items would do. The check turns PASS by itself when they arrive.

### Decisions

- **The minimum is the larger of two routes** (delegated). The standard-error route alone gives 8
  at 0.65, and a perfect 8 of 8 only bounds true accuracy at 0.625, below the bar. The rule of
  three alone gives 15 at 0.8, where the standard error is still above half the effect. Each
  route catches what the other misses.
- **The stated minimum must equal the derived one** (delegated). Below it the threshold claims
  more than the corpus carries. Above it the number was imported. The ~50 is the case the ticket
  names. So `load_thresholds()` refuses both, and a raised minimum means changing the method in
  code, where review sees it.
- **Not measurable is decided before the threshold** (delegated). A zero on three items bounds
  nothing either, so a short run is not measurable whether it scored 1.0 or 0.0.
- **Not measurable is run-level, not item-level** (delegated). The seam is
  `EvalResult.measured_count`. The run outcome reads the items only through `score` and
  `measured_count`. Ticket 118 adds a third item state. That changes the numerator of `score`. It
  moves `measured_count` only if 118 decides such an item should not count toward the corpus size.
- **A fall still fails a short metric in `verify-twin-evals.sh`** (delegated). A fall compares the
  model version against its own record. It is not a claim about the threshold.
- **The amber lives in its own script** (delegated). Folding exit 3 into `verify-twin-evals.sh`
  would have hidden its beats, determinism and feed-lookup passes behind one SKIP.
- **Not measurable is a declared `waits:` SKIP** (delegated). The gate has three outcomes. A corpus
  not yet grown is the estate's own state, which is what `waits:` means.
- **The fixture corpus grew from 5 to 16 items** (delegated). The toy skill proves the harness. A
  fixture that is itself not measurable would prove only the third outcome.
- **The citation guard takes a real baseline now** (delegated). It compared only against HEAD. In
  CI the checkout is HEAD, so a lowering committed in the same diff was never seen. It now uses
  `hash_changes_are_authorised`'s two-branch shape.

### Found on the way

- `twin/skill-thresholds.yaml`'s header named a check `skill_thresholds_lowered_only_with_citation`.
  No check ever had that name. The real one is
  `skill_eval_harness_is_agnostic_and_thresholds_are_guarded`. The header now says so.
- `twin/model_permission.py` condition 1 compares a score with the threshold and does not read
  `min_items`. No permission rests on a short corpus today: conditions 9 and 10 refuse every
  pair, 0 of 14 held on this run of `verify-model-permission.sh`. Reading the minimum in
  condition 1 is a follow-up for the model-permission owner, not built here.
- `verify-model-permission.sh`'s `WEAK THRESHOLDS` line still says ticket 112 "owns the sizing".
  After merge the minimum exists, so that sentence can point here.

### How it was tested

- Red first: `tests/test_corpus_size.py` failed on import and 12 new tests in `tests/test_skills.py`
  failed before `twin/corpus_size.py` and the outcome existed. After the change, the six
  per-skill tests that asserted `passed` on a short corpus went red as the ticket predicted. They
  now assert `clears_threshold`, and `tests/test_record_skill_scores.py` asserts the outcome per
  metric from each row's own `total` and `min_items`.
- `.venv/bin/python -m pytest` over 13 files, `-n0`: 286 passed.
- mypy over `twin tests conftest.py`: no issues in 196 source files.
- `bin/twin verify --only` on eleven touched or adjacent checks: all PASS. A planted uncited
  lowering of gameplay-lens to 0.6 made the citation check FAIL, then the file was restored.
- `bash verify/twin-evals/verify-corpus-size.sh`: exit 3, last line matched by the manifest's
  `waits:` pattern (checked with `talk/truth_manifest.py`'s `judge()`).
- `bash verify/twin-evals/verify-twin-evals.sh`: PASS, with six `NOT MEASURABLE:` lines.
- `bash verify/model-permission/verify-model-permission.sh`: PASS, 0 of 14 pairs granted.

### What remains

Nothing waits on the owner. The corpora are what is short: 50 distinct labelled items across six metrics.
Ticket 03 of the Laya map says where labels can come from and when.
