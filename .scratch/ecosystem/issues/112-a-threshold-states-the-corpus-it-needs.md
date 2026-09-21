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
