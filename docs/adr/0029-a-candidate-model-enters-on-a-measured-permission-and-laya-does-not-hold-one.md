---
status: accepted
---

# A candidate model enters on a measured permission, and Laya does not hold one

Decided 2026-09-22 by the assistant under
[ADR-0025](0025-the-assistant-decides-architecture-and-records-it.md), labelled delegated.
Wayfinder ticket 09, on the map
[Laya, loophole and the trdrbot prior art, measured then decided](../../.scratch/laya-loophole/map.md).
Amends [ADR-0024](0024-the-daily-clock-the-caged-observation-lane-and-the-derived-ledger.md)
point 6 by the note this ADR adds there. Supersedes nothing.

## Context

Laya is a 421M decision model on a ModernBERT-large backbone, published on 2026-09-18 with an
ONNX runtime and a PyPI package. It runs on CPU and needs no API token. The question this map
asked was whether it enters this estate and on what terms.

**Every number below was measured here.** No vendor number decides anything in this ADR, for a
reason ticket 01 established: **no independent evaluation of Laya exists anywhere**. Three
candidate benchmarks were checked and every quality figure the vendor publishes is Convai
measuring Convai. So the bake-off of ticket 04 is the first independent evaluation of this model
on anything, and the weight of a vendor claim here is zero.

Two vendor numbers this map carried at charting time were wrong, and both were corrected by
measurement rather than by argument. The 32.8 ms latency belongs to the multilingual checkpoint,
and the English checkpoint's own published figure of 39.5 ms is a T4 GPU number, while this
estate has no GPU. The calibration error of 0.081 is a mean over 49 suites, 42 of them
multilingual; the same file records 0.207 falling to 0.129 for typed decisions alone.

### What was measured

**It runs, at a pin, offline** (ticket 02). `.scratch/laya-loophole/bench/measure_laya.py` blocks
`socket.connect` for the whole measured run rather than trusting an environment variable.
**169.74 ms p50 and 203.67 ms p99 for one question, 470.8 ms for five**, at 4 threads over 120
timed passes, swept across 1 to 10 threads to show the thread count is not doing the work. One
`answers_sha256` across three processes at two thread counts, so the pin reproduces.

**It loses the bake-off** (ticket 04). Six rows are recorded in `twin/skill-scores.jsonl` at
`model_version: laya-1c5edc17`, on the same six corpus digests `heuristic-0.1.0` was scored on,
with `twin/skills.py` untouched. Each score is stated here with the best constant answer its own
corpus admits, because a score without that bar is not a result:

| metric | Laya | incumbent | best constant answer | n |
| --- | --- | --- | --- | --- |
| `signal-classify` | 0.870 | 1.000 | 0.913 | 23 |
| `evolution-judge` | 0.500 | 1.000 | 0.750 | 4 |
| `causal-claims` | 0.000 | 1.000 | 1.000 | 4 |
| `causal-claims-grade-accuracy` | 1.000 | 1.000 | 0.750 | 4 |
| `gameplay-lens` | 0.333 | 1.000 | 0.333 | 3 |
| `ethics-gate` | 0.200 | 1.000 | 0.800 | 5 |
| `substrate-generator` | not measurable | 1.000 | 1.000 | 3 |

**Five of the six scores are at or below the constant.** The one exception,
`causal-claims-grade-accuracy` at 1.000, bounds at 0.473 on 4 items against a 0.800 threshold, so
it is not measurable in Laya's favour either. `substrate-generator` needs a generated
multi-channel message schedule and Laya emits `output_tokens: 0` on every call; **no row was
written**, because a 0.000 in the score log reads as a quality measurement and is not one. "Not
measurable" and "bad" are different answers and this record keeps them apart.

**Its heads are near-constant.** `act_probability` read exactly 1.000000 on **all 279 calls
across three runs**. Laya answered "admit" on all five `ethics-gate` sensors and "product" on all
four `evolution-judge` organisations. Three constant heads are recorded in
`twin/model-head-readings.yaml` and the permission reads them.

**The incumbent cannot fail either, in two places.** `signal-classify`'s 0.80 threshold sits
under its own corpus's 0.913 majority-class baseline, and `causal-claims`' elasticity constant
`_BASE_MODE` is 0.375, exactly the mean of that corpus's four elasticity labels, inside a
tolerance of 0.15 that covers all four. Neither side of this bake-off has been shown to judge.

## Decision

### 1. Laya does not enter this estate. It is refused by the estate's own rule, not by its score

`twin/model_permission.py` turns the owner's "within thresholds" into ten graded conditions, and
`verify/model-permission/verify-model-permission.sh` grades them on the truth surface. Run on
2026-09-21 it reports **0 of 14 (metric, model version) pairs hold a permission**, and it names
which condition refused each one:

| metric | `laya-1c5edc17` refused by | `heuristic-0.1.0` refused by |
| --- | --- | --- |
| `signal-classify` | 8, 9 | 10 |
| `evolution-judge` | 1, 8, 9 | 10 |
| `causal-claims` | 1, 8, 9 | 8, 9, 10 |
| `causal-claims-grade-accuracy` | 8 | 10 |
| `gameplay-lens` | 1, 8, 9 | 10 |
| `substrate-generator` | 1, 2, 5, 8, 9 | 9, 10 |
| `ethics-gate` | 1, 8, 9 | 10 |

Item 1 is `threshold_cleared`, item 2 `corpus_current`, item 5 `score_recorded`, item 8
`head_varies`, item 9 `beats_constant_baseline`, item 10 `corpus_not_fitted`. Read the refusal as
the rule's output. A refusal that named only the score would be an opinion; this one names the
condition and the number behind it.

### 2. The incumbent heuristic is refused too, on item 10, and that is the strongest thing this ADR says about its own fairness

`heuristic-0.1.0` scores 1.000 on every metric and holds no permission on any of them. It is
graded on the corpus it was fitted on, which `twin/evolution_judge.py`'s own `CORPUS_KIND`
already calls `harness-mechanism`. **A rule that cleared the incumbent and refused the candidate
would be a rule fitted to the answer.** One edit to `CORPUS_KIND`, the day a held-out corpus
exists, lifts the condition for whoever earns it.

### 3. The incumbent's 1.000 gets no more weight than the candidate's number

Ticket 03 measured five of the six thresholds as unfalsifiable on their own corpora: by the rule
of three, a perfect score on 3 items is consistent with a true accuracy of zero. Ticket 05 then
derived the best constant answer for all seven metrics and found **5 of 7 thresholds sit at or
below it**. That number is reported on the gate and deliberately not graded there, because the
corpus is what is short and eco-system ticket 112 owns the sizing.

### 4. A corpus baseline is a condition of entry for any candidate, not a caveat

Every score this estate reports about a model carries the best constant answer its corpus admits
beside it. `twin/model_permission.frozen_field_baseline()` derives that bar by perturbation, with
no skill named in it, and the gate asserts on every run that it reproduces the two numbers ticket
04 measured by hand: 0.913 on `steep` and 1.000 on `edge.elasticity.mode`.

### 5. `act_probability` is refused as a permission signal, and any head like it

A field whose recorded outputs carry one distinct value across a run revokes the permission it
was supposed to grant, whatever that value is. This is condition 8, and it was measured four
times in one model. The same defect appeared in an unrelated tool in the same week: loophole's
judge called 17 of 18 candidates resolvable. **A near-constant head is not a signal, in anyone's
tool or in this estate's.**

### 6. The pin is taken outside the vendor's package, and any entry inherits that condition

`laya.Agent.__init__` (0.3.4, `laya/agent.py:122-128`) calls `snapshot_download` with **no
`revision`**, so the documented entry point can only fetch whatever `main` points at, on a
repository whose `main` moved ten times in two days. `Agent` does accept a local directory, so
the digest is resolved outside the package and the directory is handed in. This is a condition of
entry and not a footnote, because a reader who follows the vendor's README gets an unpinned model
and no error.

### 7. The environment is pinned with the weights, or the numbers are not the numbers

`encoder/config.json` at revision `1c5edc17` declares `transformers_version: 5.0.0` and carries
`rope_parameters` and `layer_types`, which 4.x `ModernBertConfig` does not read. The vendor's
package declares only `transformers>=4.45.0`, so its own metadata permits a build that **loads
the checkpoint and silently gives different numbers**. The bake-off ran in ticket 02's own venv at
`transformers==5.9.0`. Any later measurement states its build.

### 8. The route is declared before the run, and the other route is reported and not recorded

On `evolution-judge` Laya's declared primary route scores 0.500 and its declared `noul`
sensitivity route scores 4 of 4, with the rank order of all four organisations correct and every
one inside 0.095 of its label. Both routes were fixed in code before any result was seen, and 4
items cannot tell them apart at 95%. The honest sentence is that **the continuous head carries
signal where the band classifier does not, and nothing here measures it well enough to enter
on.** Choosing the winner afterwards would be fitting the instrument to a four-item corpus.

### 9. Four things no measurement changes, weighed and recorded

- **The weights repository ships no LICENSE file** at the pinned revision. The Apache 2.0 grant
  rests on the model card's YAML tag and a footer line. The inference code on GitHub does carry a
  full Apache LICENSE; the weights do not.
- **Training data provenance is unpublished.** No corpus, size, method or licence. The vendor's
  own raw file admits AG News and boolq were in the training mix.
- **No independent evaluation exists**, so every quality claim is self-reported.
- **The repository is days old and `main` moves.** Created 2026-09-18, ten moves in two days.

An estate that pins everything and prices every hole has to say what an unprovenanced model
weighs. It weighs this: the four together would not by themselves refuse a model that judged
well, because point 6 closes the pin and the local directory closes the fetch. They set the terms
the model would enter under, and they raise the bar the measurement has to clear. **The
measurement did not clear a lower bar.** So the licence and provenance questions are recorded
here rather than argued, and they are the first things to re-open if point 10's terms are ever
met.

### 10. The terms on which a candidate model may re-enter

This ADR refuses Laya. It does not refuse the class. A candidate model enters when:

1. it holds a permission under `twin/model_permission.py` on the metric it is proposed for, which
   means clearing all ten conditions and not only the threshold;
2. the corpus it is graded on is one it was not fitted on, and is large enough for the threshold
   to be falsifiable at 95% (ticket 03 derived 326 items per skill; eco-system ticket 112 owns
   the sizing);
3. its score is strictly above the best constant answer that corpus admits;
4. every head a permission reads varies across the run;
5. the weights are pinned by digest outside the vendor's package, and the runtime build is pinned
   with them;
6. it enters through `twin/skills.py` as a callable with its own `model_version`, with no new
   harness and no change to `evaluate()`.

Nothing in this list is new doctrine invented for Laya. Items 1 to 4 are the permission, item 5
is point 6 above, and item 6 is how the bake-off itself ran.

### 11. A candidate's recorded scores may not move the incumbent's bar

Recording six Laya rows changed what `verify/twin-evals/verify-twin-evals.sh` graded the
incumbent against: it read the last row of **any** model version, so the heuristic's fresh 1.000
was compared with Laya's 0.870, 0.500, 0.000, 0.333 and 0.200. Five of the seven regression
comparisons were dead, and the incumbent could have fallen from 1.000 to 0.600 and still read
`pass`. Fixed 2026-09-22 in the same ticket: the comparison is scoped to the row's own
`model_version`, with a negative control in both directions. Measuring a candidate must never
loosen the check on the incumbent.

## Options considered

**Does Laya enter?**

- **No, refused by the permission, with terms for re-entry (chosen).** The reasons above.
- **Yes, on the one metric it ties.** Rejected. `causal-claims-grade-accuracy` at 1.000 bounds at
  0.473 on 4 items against a 0.800 threshold, and the metric's own head refused condition 8. An
  entry on a number that cannot be told from chance is the defect this map exists to name.
- **Yes, as a second opinion beside the heuristic, recorded and never acted on.** Rejected, and
  it is the closest call here. It would cost 169.7 ms a question and produce a second number on
  every sweep. But a recorded number is read, and five of its six readings are at or below a
  constant answer. The estate would be publishing a column that means nothing, and the
  `substrate-generator` row would be blank. Eco-system ticket 93's derived probability is the
  place where a continuous head could earn a reading, and nothing can measure that until a
  labelled probability corpus exists.
- **Specialise it on a fitted corpus first, then measure.** Rejected, and ruled out of scope on
  the map for a second reason. Ticket 03 priced the only route with real supply at roughly 57
  backtest organisations for one skill against the four the estate has, and the zero-shot number
  is at or below a constant on five of six metrics, so a fit has nothing to improve on here.

**What refuses it?**

- **The estate's own permission rule (chosen).** It names the condition, it refuses the incumbent
  on the same run, and it lifts itself when a model earns it.
- **The bake-off score alone.** Rejected. A score is an opinion until it carries the bar its
  corpus admits, and this map measured that five of seven thresholds do not carry one.
- **The licence and provenance gaps alone.** Rejected. They are real and recorded in point 9, but
  refusing on them would leave the estate with no measured reason and no rule that could ever
  admit a successor.

## Consequences

- **`twin/skill-scores.jsonl` keeps the six Laya rows.** They are the first independent
  measurement of this model on anything, and deleting a measurement because it was unflattering
  is the defect this estate exists to refuse. `verify-twin-evals.sh` no longer reads them as the
  incumbent's bar (point 11).
- **The seven thresholds stay as they are, and the weakness is published.** 5 of 7 sit at or
  below their own corpus's best constant answer, printed on every
  `verify-model-permission.sh` run, reported and not graded. Eco-system ticket 112 sizes a
  minimum corpus against the baseline rather than against zero.
- **No model holds a permission, so nothing in this estate judges on a GitHub clock.**
  `.claude/skills/classify-and-judge/SKILL.md` and ADR-0024 point 6 keep their sentence, and both
  now say it is a check's output rather than a promise somebody keeps.
- **What this ADR does not claim.** It does not say Laya is a bad model. It says that on this
  estate's seven metrics, on corpora of 3 to 23 items, it was not measurable above a constant
  answer, and that the estate's own rule refuses it. A corpus 326 items long might say something
  else, and nobody can build one here before 2027-08-28, which is when the first label the world
  writes arrives.
- **The hardware question evaporates.** 169.7 ms is an Apple-silicon laptop with 8 performance
  cores, and a GitHub Actions runner is 4 vCPU, so the number would move. Nothing in this estate
  runs Laya on any clock, so the number does not need to be measured. It returns with point 10.

### Evidence

Every number above is reproducible from the map's own assets, which stay in `.scratch/`:

- `.scratch/laya-loophole/bench/measure_laya.py`, `bench/pin.json`, `bench/measured.json` — the
  latency, the pin, the offline proof.
- `.scratch/laya-loophole/bakeoff/` — `run_laya.py`, `score.py`, `predictions.json`,
  `bakeoff.json`, `corpora.json`.
- `twin/skill-scores.jsonl` at `model_version: laya-1c5edc17`, and
  `twin/model-head-readings.yaml`.
- `verify/model-permission/verify-model-permission.sh` and `twin/model_permission.py`.
