# 03 — A labelled corpus from merged human claims

Type: task (AFK)
Status: open
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
