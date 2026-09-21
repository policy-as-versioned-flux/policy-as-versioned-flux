# 03 — A labelled corpus from merged human claims

Type: task (AFK)
Status: resolved
Blocked by: none

## Question

The six skills hold 42 labelled items in total, measured 2026-09-21. The largest corpus is 23
items. No model can be fitted or calibrated on that.

Hand-authoring more labels is circular. A label written to grade a model that replaces a human's
judgement must come from a human's judgement, not from the person building the model.

The honest source already exists. Merged `classify-and-judge` pull requests and the bound rows in
each adopter's `twin/signals.yaml` are real human judgements that somebody reviewed and merged.

1. Build a corpus from those merged claims. Each item cites the merge that produced it.
2. Report the item count per skill.
3. State whether the count supports a per-question-type temperature fit. Laya needs one.
4. If the count is still too small, state what number would be enough, and where it could come
   from.

**Added 2026-09-21, from ticket 01.** There is now a number to measure against. Laya's own
documented fine-tune recipe uses **6,000 labelled decisions over 1,200 cases**, which is 300 items
for each of 20 question schemas. This estate holds 42 items across six skills.

"Not measurable on this corpus" is the expected answer and is a complete result. Report it plainly
if it is true. Do not stretch the corpus to reach a number.

## Done

A corpus builder, a measured item count per skill, and a plain statement of whether the count is
enough. A count that is too small is a valid answer and is recorded as one.

## Notes

This ticket does not need Laya. Run it in parallel with tickets 01 and 02.

## Answer

**Not measurable on this corpus.** The merged human claims give **one** labelled item across all
six skills. The expected answer in the ticket is the true one.

### 1. The corpus builder

`.scratch/laya-loophole/corpus/build_corpus.py` builds it. Run it like this:

```
.venv/bin/python .scratch/laya-loophole/corpus/build_corpus.py --out .scratch/laya-loophole/corpus/corpus.json
```

It reads `origin/main` on each adopter clone, never the working tree. Every clone under
`.estate-clone` was behind its remote when this ticket ran. driftwood was behind by 1 commit,
ludlow and tuppence each by 1. A builder that read the checked-out tree would have reported zero
claim files and zero items, which is a different wrong answer from the right one.

Each item carries the commit that wrote it and the merge commit that accepted it. The one item
cites `ceb3697` and merge `0164cda`, which is driftwood pull request 34.

### 2. The item count per skill

| skill | items from merged human claims |
|---|---|
| signal-classify | 0 |
| evolution-judge | **1** |
| causal-claims | 0 |
| substrate-generator | 0 |
| gameplay-lens | 0 |
| ethics-gate | 0 |
| **total** | **1** |

Three facts produce that table.

**The `classify-and-judge` skill has never produced a merged pull request.** Every merged pull
request on all three adopter repositories was read, 26 on driftwood, 20 on ludlow and 22 on
tuppence. None came from the skill. The estate holds exactly one claim file,
`driftwood/twin/orgs/driftwood/claims/supply-constraint-position-2026-09-09.yaml`. A build ticket
wrote it, eco-system ticket 51, not a classification round.

**A bound row in `twin/signals.yaml` labels none of the six skills.** The three adopters hold 13
bound rows, 5 on driftwood and 4 each on ludlow and tuppence. A row binds a pinned feed version to
a **scenario** id. The `signal-classify` corpus needs a STEEP tag and exactly one component
binding. A grep for `steep` across all three adopter repositories at `origin/main` returns
**nothing**. The row reaches components only through the scenario, and a scenario names several.
So a bound row is a real merged human label for a question none of the six skills asks. Deriving a
STEEP tag from it here would be this ticket authoring the label, which the ticket forbids.

**Adopter overlays carry no graded causal edges.** The three adopters hold 9 edges between them.
Not one carries a `causal:` block, so `causal-claims` gets 0 items and not a small number.

### 3. A per-question-type temperature fit is not possible

`.scratch/laya-loophole/corpus/required_size.py` derives the number. The output is saved beside it
in `required_size.out`.

Ticket 04 must tell an expected calibration error of 0.129 apart from the vendor's headline 0.081.
The gap is 0.048. A measurement whose noise is the size of that gap decides nothing. Set the
standard error at half the gap, 0.024, at the 0.75 accuracy band the benchmark author's own card
warns about. Then:

- **326 items per skill** sizes the whole-set standard error. This is the charitable route.
- **3,260 items per skill** sizes the per-bin error that the calibration estimator really incurs
  over 10 bins. This is the honest route.

Laya's own published recipe uses **300 items per question schema**. Two independent routes reach
the same order of magnitude. That agreement is the strongest evidence in this ticket.

This estate holds 1 merged human label. That is **326 times short** of the charitable floor. Six
skills at 326 each need 1,956 items. The 42 hand-authored items are 14.2 times short of the floor
for a single skill.

### 4. What would be enough, and where it could come from

**The number is 326 per skill for the charitable route, and 3,260 for the honest one.** State
which route any later claim uses.

Four sources were checked. None reaches the number.

1. **A human at a keyboard running `classify-and-judge`.** This is the source the ticket names.
   It has produced zero merged pull requests since the skill shipped. The local clock cannot
   supply the gap. `talk/local-clock.sh` refuses a claim file that carries an override, and
   `twin/schema.py` demands `claimed_by` for an override and for nothing else. So the estate's
   only automatic claim producer is structurally unable to write a human label.
2. **Resolved forecasts.** These are the only labels the world writes rather than a person. The
   estate holds 18 scenarios across the three adopters. The earliest horizon is 2027-08-28, which
   is **341 days** after today. At most 18 items arrive then, and they label a forecast, not any
   of the six skills' outputs.
3. **More backtest organisations from the public record.** This is the only route with real
   supply. The four existing organisations produced 23 `signal-classify` items between them, so
   about 6 items each. Reaching 326 needs roughly 57 organisations. Authorship still sits with
   this estate, so the circularity the ticket names is reduced and not removed.
4. **Ratified machine output.** A merged `binding` or `position` claim carries no `claimed_by` and
   the heuristic under test wrote it. Counting these would measure agreement with the incumbent
   heuristic, not accuracy. The builder counts them and excludes them. The count today is 0, so
   the exclusion changes no number in this ticket. It will matter the first time the skill runs.

### 5. What this ticket found in the estate's own instrument

All six heuristics score 1.0 on their own corpora. The rule of three gives the 95% lower bound on
true accuracy for a perfect score on n items.

| skill | n | threshold | 95% lower bound at 1.0 | verdict |
|---|---|---|---|---|
| signal-classify | 23 | 0.80 | 0.870 | clears its threshold |
| ethics-gate | 5 | 0.80 | 0.400 | cannot clear its own threshold |
| evolution-judge | 4 | 0.75 | 0.250 | cannot clear its own threshold |
| causal-claims | 4 | 0.80 | 0.250 | cannot clear its own threshold |
| gameplay-lens | 3 | 0.65 | 0.000 | cannot clear its own threshold |
| substrate-generator | 3 | 0.80 | 0.000 | cannot clear its own threshold |

**Five of the six thresholds are unfalsifiable on their own corpora.** A perfect score on a 3-item
corpus is consistent with a true accuracy of zero. `twin/skill-thresholds.yaml` states no minimum
corpus size, and `twin/skills.py` refuses only an empty corpus, so a one-item corpus passes today.
This is a measured number for eco-system ticket 112, which ticket 10 graduated as a derived
minimum corpus size. Item 3's method gives that ticket its derivation: pick the effect the
threshold must detect, then size n so the standard error sits inside it.

### Calls recorded as the assistant's, under ADR-0025

**A merged claim is not automatically a human label. Authorship is the test, not merging.**
`twin/schema.py` `_refine_claim` demands `claimed_by`, checked against `twin/roles.yaml`, for an
`override` and for no other kind. So an `override` at grade 4 is a human's attributable judgement,
and a `binding` or `position` at grade 5 is the heuristic's own output that a human reviewed.
Merging is review, not authorship. The builder counts the second group and keeps it out of the
labelled corpus. Without this split the headline count would read 1 today and would silently
become circular the first time `classify-and-judge` runs.

**The builder lives in `.scratch/laya-loophole/corpus/`, not in `twin/`.** This map measures and
decides, and it adopts nothing. Putting a corpus builder in the twin package would be adoption
before ticket 09's ADR. Ticket 04 imports it by path.
