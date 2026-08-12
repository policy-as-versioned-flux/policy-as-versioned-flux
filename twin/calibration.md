# The calibration procedure for authoring a PERT triple

Authored-by-role: model-steward

Build ticket 23, from decision ticket 08 (Q1) and decision ticket 09.

A triple is `min / mode / max`. It is a **90% credible interval with a most-likely value**, not a
spreadsheet guess with two decorations either side. The difference is testable and this document is
the test.

Every artefact that samples a triple pins this file by digest, so a triple in an artefact points at
the discipline that produced it. A step removed from this file is a step no longer required, and
that is a visible change to a versioned document rather than a habit quietly lapsing.

## What the range means

`min` and `max` bound a **90% interval**. The estimator states that the true value falls inside them
nine times in ten. It is not a best case and a worst case, and it is not a bound on what is
physically possible.

`mode` is the single most likely value. It may sit anywhere between the bounds.

A triple where all three points are equal is **degenerate**. It is permitted, it is flagged wherever
it is read, and it says the estimator knows the value to a point. Most of the time that claim is
false, and the flag is what makes it arguable.

## The steps

Each step has an id. The id is what the code requires by name.

### step: absurdity-test

State the range that is obviously too wide. Widen `min` and `max` until you would happily bet on the
interval containing the answer. Most estimators start far too narrow, so this step runs first and
runs deliberately.

### step: equivalent-bet

Ask yourself which you would rather have: a payout if the true value lands inside your interval, or
the same payout on a 90% lottery. If you prefer the lottery, your interval is too narrow. Widen it.
If you prefer the interval, it is too wide. Narrow it. Stop when you are indifferent between them.

### step: name-the-reference-class

Write down what the estimate is a member of. An elasticity between two components in this
organisation is a member of a class — the same relationship elsewhere, the same component under a
different shock, a published series. Name it. An estimate with no reference class is a grade 4 or
grade 5 claim and the evidence ladder must say so.

### step: state-the-decomposition

Write down what the number is made of. An elasticity that decomposes into a rate and a volume is two
estimates, and each one is easier to calibrate than the product. Record the decomposition beside the
triple so a reader can argue with the parts.

### step: record-the-estimator-and-the-date

Name the role that produced the triple and the date it was produced. Both travel with the claim. An
estimate with no date cannot be checked against what happened next, and an estimate with no named
role cannot be calibrated at all.

## What this does not do

It does not make an estimate correct. It makes an estimate **checkable**, and it makes an
overconfident one visible before it is used.

Calibration is a property of an estimator measured over many estimates, not a property of one
triple. This procedure is the authoring discipline. The calibration record itself is the scoring
harness, and it is what eventually says whether the discipline worked.
