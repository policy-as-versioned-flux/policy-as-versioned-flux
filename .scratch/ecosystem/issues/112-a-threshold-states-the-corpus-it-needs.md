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
