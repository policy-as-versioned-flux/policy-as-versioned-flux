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
