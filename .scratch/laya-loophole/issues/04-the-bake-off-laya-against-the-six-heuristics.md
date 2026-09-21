# 04 — The bake-off: Laya against the six heuristics

Type: task (AFK)
Status: open
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
