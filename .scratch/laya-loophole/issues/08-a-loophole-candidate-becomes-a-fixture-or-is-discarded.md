# 08 — A loophole candidate becomes a fixture, or is discarded

Type: task
Status: open
Blocked by: 07

## Question

loophole's output is non-deterministic. Under "derive what you assert" it is a hypothesis, never a
finding. Resolve every candidate ticket 07 produced.

For each candidate, do one of two things:

1. Write a deterministic check that reproduces it. The check is the finding. The candidate was
   only the pointer.
2. Discard it, with a one-line reason.

A candidate that survives lands in the misuse catalogue through a reviewed pull request.

Record the survival rate.

**Added 2026-09-21, from ticket 06.** loophole carries no licence. Do not commit its source, its
prompts, or a paraphrase of its prompts into the estate. A surviving candidate enters the misuse
catalogue as **our own** fixture, written from the scenario it describes, not as copied text.

## Done

Every candidate resolved to a fixture or to a recorded discard. A stated survival rate.

## Notes

The survival rate is the honest verdict on the tool. A rate near zero says the tool generates
noise, and that result is as valuable as a rate near one. Do not tune the run to raise it.

**Added 2026-09-21, from ticket 07.** The six candidates are in
[`research/07-loophole-round/candidates.json`](../research/07-loophole-round/candidates.json), keyed
`loophole-1` to `loophole-3` and `overreach-4` to `overreach-6`. Each carries the scenario, the
explanation and the judge's verdict. Five read resolvable and `overreach-5` reads unresolvable.

Two things this ticket must not do. Do not treat the judge's "resolvable" as evidence that a
candidate is real; it is the same non-deterministic model. Do not copy a scenario's wording into a
fixture; write the fixture from what the scenario describes, because loophole carries no licence
and the model's output was produced under loophole's prompts.

Denominator for the survival rate: 6.
