# 11 — Does a second round find the same holes?

Type: task
Status: open
Blocked by: 08

## Question

Ticket 07 ran one round and it is one sample. loophole's output is not deterministic, and ticket 07
measured the two things that make that concrete: no temperature flag reaches the finder, and the
served model is newer than the published one. So the six candidates are one draw, not the tool's
answer about ADR-0022.

Run a second round against the same document, at the same pin, with the same inputs, by the same
harness. Then answer one question: **how much of the tool's output is the document, and how much is
the draw?**

1. Run `.scratch/laya-loophole/bench/loophole_round.py` a second time against
   `research/07-loophole-round/inputs/`. Same code sha256, same principles sha256.
2. Record the parse-failure and under-production counters, as ticket 07 did. Both at zero, or the
   run failed.
3. Compare the second round's candidates to the first. Name the overlap. A candidate matches when
   it attacks the same clause for the same reason, not when the words match.
4. State the cost of the second round beside ticket 07's 8 calls, 185.8 s and 0.4150 USD.

## Done

A stated overlap between two rounds. The raw output of round two stored beside round one.

## Notes

This is not a repeat of ticket 08. Ticket 08 asks whether a candidate is real. This ticket asks
whether the tool says the same thing twice. A tool that finds six different holes each time is a
generator, and ticket 09's ADR must say how many rounds a human has to run before the output means
anything.

**Close this out of scope if ticket 08 records a zero survival rate.** A tool that produced nothing
real once does not need its repeatability measured. The map's Out of scope section takes the line.
