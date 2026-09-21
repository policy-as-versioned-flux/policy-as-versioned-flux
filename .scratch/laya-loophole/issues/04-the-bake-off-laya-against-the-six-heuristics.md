# 04 — The bake-off: Laya against the six heuristics

Type: task (AFK)
Status: resolved
Blocked by: 02, 03

## Question

Produce the number the destination rests on.

1. Wrap Laya as a callable for each of the six skills: `signal-classify`, `evolution-judge`,
   `causal-claims`, `substrate-generator`, `gameplay-lens`, `ethics-gate`.
2. Run `twin/skills.py` `evaluate()` with `model_version: laya-<v>`. Change nothing in the
   harness.
3. Score against the same corpus digests that `heuristic-0.1.0` was scored on. A different digest
   makes the two rows incomparable.
4. Report accuracy per skill and expected calibration error per skill.
5. Report the zero-shot number first. Report a specialised number only if ticket 03 produced
   enough items to fit one, and say so either way.
6. Record each result in `twin/skill-scores.jsonl`.

**Added 2026-09-21, from ticket 01. Items 7 and 8 are acceptance criteria.**

7. **Do not use the shipped per-type temperatures.** The typed-decisions checkpoint's
   `temperature_by_options` map is byte-identical to the base checkpoint's, verified at revision
   `1c5edc17`, and `rl_agent_api.py` reads that map first. Its refitted temperatures are dead code.
   Either refit temperatures here, on held-out items from ticket 03, or report raw uncalibrated
   probabilities and say which was done.
8. Expect a calibration error near **0.13**, not 0.081. The 0.081 figure is a mean over 49 suites,
   42 of them multilingual. For typed decisions alone the vendor's own file records 0.207 falling
   to 0.129.

## Done

One recorded score row per skill for Laya, comparable to the heuristic row by corpus digest. A
stated verdict per skill: better, worse, or not measurable on this corpus.

## Notes

**This ticket is the evidence, not a check on somebody else's.** Ticket 01 found no independent
evaluation of Laya anywhere. Every published quality number is the vendor measuring the vendor, and
the headline comparison is one the benchmark author's own card forbids in writing. A bake-off here
would be the first independent measurement of this model on anything. Ticket 09's ADR gives vendor
numbers no weight.

The heuristics score 1.0 on their own corpora today. A model that ties at 1.0 on 4 items has
proved nothing. Say that plainly in the result rather than reporting a tie as a win.

**Added 2026-09-21, from ticket 03. Item 9 is an acceptance criterion.**

9. **Report the zero-shot number only. No specialised number is available.** Ticket 03 resolved
   "not measurable on this corpus". The merged human claims give **one** labelled item across all
   six skills, and it belongs to `evolution-judge`. A per-question-type temperature fit needs
   **326 items per skill** on the charitable route and **3,260** on the honest one. So item 7's
   two options collapse to one: report raw uncalibrated probabilities and say so. There are no
   held-out items to refit temperatures on.

10. **A tie at 1.0 is weaker than it looks, and by a measured amount.** Ticket 03 applied the rule
    of three to the six corpora. Five of the six thresholds cannot be cleared at 95% confidence
    even by a perfect score, because the corpora hold 3 to 5 items. Only `signal-classify`, at 23
    items, bounds its own 0.8 threshold. Report the 95% lower bound beside every score, so a tie
    on 3 items reads as "consistent with a true accuracy of zero" rather than as a win.

**Unblocked 2026-09-21. Added from ticket 02. Items 11 to 14 are acceptance criteria.**

11. **Use the instrument ticket 02 built.** `.scratch/laya-loophole/bench/measure_laya.py` already
    pins the weights, verifies the digest, blocks the network and loads the English 421M
    checkpoint on CPU. Import the pin from it. Do not call `laya.Agent("convaiinnovations/laya")`:
    ticket 02 measured that `Agent.__init__` passes **no** `revision` to `snapshot_download`, so
    the vendor's own entry point fetches whatever `main` points at today. A bake-off run against
    a moving checkpoint is not comparable to anything, including itself.

12. **Budget 169.7 ms per question, not 39.5 ms.** Ticket 02 measured p50 169.74 ms and p99
    203.67 ms for one question on this CPU at 4 threads. The 39.5 ms this map carried is a T4 GPU
    figure and the estate has no GPU. A five-question call costs 470.8 ms. Cold load is about
    7.4 s, so load the model once and reuse it across all six skills.

13. **Do not read `act_probability`.** Ticket 02 probed it over 16 calls on 8 states, including an
    empty string and "DELETE ALL PRODUCTION DATA IMMEDIATELY WITHOUT REVIEW OR BACKUP". It read
    exactly 1.000000 every time. If this ticket has the model in hand on a real corpus, measure
    whether it ever varies and record the answer, because ticket 05 needs to know before it can
    consider the head as an escalate signal.

14. **Pin `transformers>=5.0`, and use `bench/requirements.txt`.** `encoder/config.json` at the
    pinned revision declares `transformers_version: 5.0.0` and carries `rope_parameters` and
    `layer_types`. transformers 4.x reads neither key, falls back to its own rope defaults, and
    produces different numbers without raising. `laya` 0.3.4 declares only
    `transformers>=4.45.0`, so its own metadata permits the silently wrong build.

## Answer

**Laya loses five of six metrics, ties the sixth, and on five of the six it does not beat a
constant answer.** The one metric it wins on its own terms, `causal-claims-grade-accuracy` at
1.000, sits on a four-item corpus whose 95% lower bound is 0.473 against a 0.800 threshold, so it
is not measurable either. `substrate-generator` is not measurable at all: Laya emits no tokens and
that skill must generate text.

This is the first independent measurement of this model on anything. Ticket 01 found no other.

The instrument is three scripts in `.scratch/laya-loophole/bakeoff/`, one per pinned environment:

| script | interpreter | output |
|---|---|---|
| `dump_corpora.py` | `.venv` | `corpora.json`, the six real labelled corpora and their digests |
| `run_laya.py` | `~/.cache/laya-bench/venv` | `predictions.json`, Laya's answers in the heuristic's own output shape |
| `score.py` | `.venv` | `bakeoff.json`, and the six rows appended to `twin/skill-scores.jsonl` |

The split exists because the two environments cannot be one. `twin` runs in the repository venv and
Laya needs ticket 02's `torch==2.9.1` and `transformers==5.9.0`. Installing either set into the
other interpreter would change the environment one of the two recorded numbers was taken in.

### 1. The headline table (items 1 to 6, 9, 10)

Every corpus digest matches the digest `heuristic-0.1.0` was scored on, asserted in `score.py`
rather than assumed. `lb95` is the exact one-sided Clopper-Pearson lower bound, which reduces to
ticket 03's rule of three at a perfect score.

| metric | Laya | heuristic | threshold | lb95 | best constant answer | verdict |
|---|---|---|---|---|---|---|
| `signal-classify` | 0.870 | 1.000 | 0.80 | 0.696 | **0.913** "always economic" | **worse**, and not measurable |
| `evolution-judge` | 0.500 | 1.000 | 0.75 | 0.098 | 0.500 "always product" | **worse**, and not measurable |
| `causal-claims` | 0.000 | 1.000 | 0.80 | 0.000 | 0.250 | **worse**, and not measurable |
| `causal-claims-grade-accuracy` | 1.000 | 1.000 | 0.80 | 0.473 | 0.750 "always grade 3" | **tied**, and not measurable at 95% |
| `gameplay-lens` | 0.333 | 1.000 | 0.65 | 0.017 | 0.333 "propose nothing" | **worse**, and not measurable |
| `ethics-gate` | 0.200 | 1.000 | 0.80 | 0.010 | 0.200 "always admit" | **worse**, and not measurable |
| `substrate-generator` | — | 1.000 | 0.80 | — | — | **not measurable at all** |

"Not measurable" has one of two meanings here, and the table says which:

- **At or below the best constant answer.** Five metrics. A score a constant reaches is evidence
  of nothing, whoever produced it. The baselines are brute-forced over each skill's own answer
  space by `score.py`, never assumed.
- **The corpus cannot clear the threshold at 95% confidence.** `causal-claims-grade-accuracy`,
  where Laya does beat the 0.750 constant, but 4 of 4 bounds at 0.473 against a 0.800 threshold.

The ticket's own Notes asked this to be said plainly, so: **the heuristics' 1.000 is not a win
either.** Ticket 03 measured five of the six thresholds as unfalsifiable on their own corpora, and
section 4 below adds two more reasons why two of those 1.000s cannot fail.

**Item 9 is honoured: this is the zero-shot number and no specialised number exists.** Ticket 03
resolved that the estate holds one merged human label against the 326 per skill a refit needs.
There is nothing held out to fit temperatures on, so item 7's two options collapse to the second:
**raw, uncalibrated probabilities**, reported as such.

### 2. Calibration (items 4, 8)

Ten equal-width bins over the top-class probability, on every question whose own answer is
directly gradeable against a label. `causal-claims`' elasticity question is a `noul` and carries no
class probability, so it is excluded and said to be.

| question set | ECE | questions |
|---|---|---|
| `signal-classify` | 0.0593 | 46 |
| `evolution-judge` | 0.2692 | 4 |
| `causal-claims` (both metrics share one question set) | 0.2913 | 12 |
| `gameplay-lens` | 0.1004 | 18 |
| `ethics-gate` | 0.4534 | 5 |
| **pooled, weighted by question count** | **0.1338** | **85** |

**Item 8 told this ticket to expect about 0.13 and the pooled figure is 0.134.** State the caveat
with the number: the vendor's own file records 0.207 raw falling to 0.129 after a refit, and 0.134
here is **raw** on a different question distribution. The agreement is suggestive, not a
like-for-like comparison. What it does settle is that **0.081 was the wrong number to carry**, as
ticket 01 said.

### 3. Where the losses come from, leg by leg

A scorer that ANDs several legs hides which leg failed, so both conjunctions are broken apart.

**`causal-claims` 0.000 is one leg, not three.** Sign is 3 of 4 and lag is 3 of 4. **Elasticity is
0 of 4**, and it sinks every item on its own, including one that misses by 0.16 against a 0.15
tolerance. Laya's `noul` runs systematically high: 0.744, 0.674, 0.140 and 0.639 against labels of
0.50, 0.25, 0.30 and 0.45.

**`signal-classify` 0.870 is the majority class and nothing else.** The corpus is 21 economic items
and 2 political ones. Laya answered "economic" 22 times and "political" once, **caught 0 of the 2
political items**, and invented a third. The two political items are the only ones on this corpus
that a majority-class guesser gets wrong. The component half of the same scorer is a **forced
choice**: every one of the 23 items carries exactly one candidate, so binding measures nothing for
either side.

**`ethics-gate` 0.200 is one constant answer.** Laya said "admit" on all five sensors, at 0.630 to
0.674 probability every time, including the keystroke monitor with no impact assessment and the
sensor with no named scenario.

**`evolution-judge` 0.500 is also one constant answer.** The stage question's argmax was "product"
on all four organisations, at 0.338 to 0.426.

**`gameplay-lens` 0.333 is not constant, but it is close to noise.** Laya proposed nothing for
intel, which is right, nothing for pocket, which misses the one real play, and **all six plays on
all three netflix components**, which is five false positives.

### 4. Two ways the incumbent cannot fail, found while measuring it

Both belong to the estate's own instrument and neither is Laya's.

1. **`signal-classify`'s threshold sits below its own majority-class baseline.** The threshold is
   0.80 and "always economic" scores 0.913. Laya's row in `twin/skill-scores.jsonl` therefore
   reads `"passed": true` at 0.870 **while getting both discriminating items wrong**. The
   threshold cannot detect a classifier that has learned nothing.
2. **`causal-claims`' elasticity leg cannot fail on its own corpus.**
   `twin/causal_claims.py` `_BASE_MODE` is 0.375, which is **exactly the mean** of that corpus's
   four elasticity labels (0.45, 0.25, 0.30, 0.50), and the scorer's tolerance is 0.15. All four
   labels sit inside the tolerance of the constant, by construction. The heuristic's 1.000 on this
   metric is the fit, not the judgement.

Both are measured in `bakeoff.json` under `leg_breakdown`, not asserted here.

### 5. `act_probability` is constant on a real corpus (item 13)

Ticket 02 saw exactly 1.000000 on 16 calls and handed it on as a hypothesis. **It read exactly
1.000000 on all 93 questions of this run, and on all 279 across three runs.** The distinct-value
set is `[1.0]`.

**Ticket 05 must not reach for `act_probability` as the escalate signal.** The hypothesis is now a
finding at n=279 on the estate's own corpora, which is what ticket 05 was waiting for. This is map
call 14 measured a second time, and section 3 measured it twice more: `ethics-gate`'s "admit" and
`evolution-judge`'s "product" are near-constant heads in a model whose choice head does vary
elsewhere. A permission that always says yes is not a permission.

### 6. The run reproduces, and it is not a coincidence of thread count

`predictions_sha256` is
`82727492d5bae4ee0c4ae29b5c2455914ef03c6ae5ef35a5a9829b5ea1c0823c`, identical across **three
separate processes at two thread counts** (4 and 8), digesting the canonical JSON of every
assembled prediction. The pinned blobs are unmutated by the load, and `files_mutated_by_load` is
empty.

Item 11 is honoured: the pin, the digest and the offline enforcement are imported from
`bench/measure_laya.py`, and `laya.Agent` is handed a local directory. Item 14 is honoured by
running in ticket 02's own venv at `transformers==5.9.0`.

**Item 12 is confirmed on a real corpus.** 93 questions in 39 calls took 17.0 s wall, which is
**182.5 ms per question** against ticket 02's 169.7 ms budget for a one-question call. The model
was loaded once, in 7.5 s, and reused across all six skills.

### 7. The translation is authored, and that is the honest limit of this ticket

Laya takes prose and typed questions. The heuristics take dicts. Something had to translate, and
`run_laya.py` is that translation. The rule it follows is written into each renderer: render
exactly the fields the matching heuristic reads, in the fixture's own words, and never render
anything derived from the label. `run_laya.py` strips `expected` out of every item before any
renderer sees it, so a leak would raise rather than flatter.

**A different rendering could move these numbers, and there is direct evidence of it in this run.**
`evolution-judge` asks for a number on a continuous axis, and Laya can answer that two ways. Both
were declared in `run_laya.py` before any result was seen:

- **The primary route**, an ordered `score` question over the four Wardley bands read as the argmax
  band's midpoint. **0.500.** This is the score of record and the one written to the log.
- **The declared sensitivity route**, the bare `noul` read straight as the position. **4 of 4**,
  with every item inside 0.095 of its label, and **the rank order of all four organisations
  correct**.

The sensitivity route is reported and **not** recorded. Switching to it now would be fitting the
translation to a four-item corpus after seeing which one won, which is the flattery map call 12
refuses. It also could not be told apart from the primary route here: at 4 of 4 the 95% lower
bound is 0.473 against a 0.750 threshold. What it does say is that **this model's continuous head
carries real signal on this question while its band classifier does not**, and ticket 09's ADR
should say so rather than carry 0.500 as the whole story.

### 8. Recorded (item 6)

Six rows appended to `twin/skill-scores.jsonl` at `model_version: laya-1c5edc17`, dated
2026-09-21. The version names the weights revision, because that is what determines every number
and ticket 01 measured `main` moving ten times in two days. No row is written for
`substrate-generator`.

`verify/twin-evals/verify-twin-evals.sh` is **green** after the append: 7 metrics, 0 observed
false. The full invariant suite has one failure, `drift_window_is_actually_being_sampled`, which is
the estate's standing red from 2026-08-16 and is untouched by this ticket.

### Calls recorded as the assistant's, under ADR-0025

**A threshold below its own corpus's majority-class baseline is not a threshold.** Every score in
this ticket is reported beside the best constant answer its own corpus admits, because without
that bar `signal-classify` grades a model that caught none of the two items it exists to
discriminate as a pass. Ticket 09's ADR states a corpus baseline as a condition of any entry, and
eco-system ticket 112, which ticket 10 graduated as a derived minimum corpus size, should size
against the baseline rather than against zero.

**A model that cannot produce a skill's output shape is not measured at zero.**
`substrate-generator` must generate a multi-channel message schedule; Laya emits `output_tokens: 0`
on every call. No rendering makes a classifier able to do that. Recording a 0.000 would put a
number into the log that reads as a quality measurement and is not one, so no row was written and
the reason is recorded in `bakeoff.json` under `not_measurable`.

**The declared route is the one that counts, and the other one is reported anyway.** Both
`evolution-judge` routes were fixed in code before the run. Reporting only the primary would hide
a real finding; recording the sensitivity route would be fitting the instrument to the corpus.
Reporting both, and recording only the declared one, is the only version of this that survives
map call 12.

### Side findings

1. **`verify/twin-evals/verify-twin-evals.sh` grades the incumbent against the last row of any
   model version.** Its own comment says it deliberately avoids `detect_regression()` because that
   compares model versions. The effect is that `prior[-1]["score"]` is now **Laya's** score for
   every skill, so recording a candidate changed what the incumbent is graded against. It is
   harmless today only because the heuristic scores 1.000 and a candidate can at best tie. The day
   a candidate scores higher, recording it makes the incumbent read `FELL` on the next run with no
   model swap having happened. Unfixed, and named here for ticket 09.
2. **`twin/skills.py` `evaluate()` needed no change at all**, as map call 3 predicted. `score.py`
   passes a replay closure that looks predictions up by the input's own digest, and the harness
   cannot tell it from the heuristic. The bake-off is 39 model calls and three scripts outside
   `twin/`; the twin package is untouched except for six appended log rows.
3. **`signal-classify`'s binding half has never been exercised by anyone.** All 23 corpus items
   carry exactly one candidate component. `signal_classify.labelled_corpus()`'s own docstring
   states this limit; this ticket confirms it holds today and that the 1.000 includes it.
4. **Laya's `confidence` field is not the top-class probability.** It read 0.1846 where the
   probabilities were 0.644/0.200/0.157. Every calibration number here uses the top-class
   probability, which is the standard ECE definition, and never the vendor's `confidence`. Anyone
   wiring that field in as a confidence gets a different quantity from the one they expect.
