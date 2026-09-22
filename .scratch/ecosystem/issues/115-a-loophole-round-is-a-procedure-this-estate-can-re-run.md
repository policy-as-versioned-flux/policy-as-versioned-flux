# 115 — A loophole round is a procedure this estate can re-run

Type: task
Status: open
Blocked by: none

## Question

Graduated 2026-09-22 from [the Laya and loophole map](../../laya-loophole/map.md), ticket 09.
This is the adoption work
[ADR-0030](../../../docs/adr/0030-loophole-runs-as-an-external-tool-in-rounds-and-the-estate-keeps-the-pointer.md)
creates. Read that ADR first: it fixes the shape, and this ticket only makes the shape re-runnable.

ADR-0030 decides that loophole enters as an **external tool a human runs**, in **three rounds per
document**, and that the estate keeps the pointer and throws the sentence away. What exists today
is a wayfinder asset, not a procedure: `.scratch/laya-loophole/bench/loophole_round.py` ran three
rounds against ADR-0022 and then the map closed. `.scratch/` is the issue tracker. Nobody who
comes to this estate in three months can attack a second document from what is written down.

What this ticket owes:

1. **A home for the harness that is not `.scratch/`.** It holds no loophole source and no
   loophole prompt, and it imports the clone through `LOOPHOLE_SRC`, so moving it distributes
   nothing. Decide where an evaluation instrument that is not a gate check lives, and put it
   there with its own README.
2. **The guards, asserted rather than remembered.** ADR-0030 point 6 names two: `--bare` must
   never appear, because it turns a broken login into "the legal code appears robust" at exit
   code 0; and a clean run needs **two** counters at zero, parse failures and under-production,
   because the `<scenario>` tag counter misses a total format collapse. The harness must fail the
   run on either, and `parse_failure_control.py` is the negative control that already exists.
3. **The prompt-leak check runs before any file is committed.**
   `.scratch/laya-loophole/bench/check_no_prompt_leak.py` finds 1,287 distinct 8-word runs in
   `loophole/prompts.py` and fires on all 1,287 against the source as a negative control. It is
   what keeps ADR-0030 point 7 true, and today it is run by hand.
4. **A round writes down what ADR-0030 point 9 lists**: target document and commit, harness
   sha256, model served, call count, wall time, list price, both counters, every candidate with
   its verdict, and the prompt digests. Fix the `"ticket": "07"` constant while you are there.
5. **The budget is stated where a reader meets it.** 24 calls, about 9 minutes and about 1.24 USD
   at list price for three rounds, absorbed by the subscription — and the real cost, which is the
   deterministic check on about 18 candidates at roughly half a ticket each.
6. **Name the next document.** ADR-0022 has been attacked three times. The estate has 30 ADRs.

What this ticket may not do, from ADR-0030: vendor loophole, fork it, reimplement its prompts,
run it on any clock, or make it a gate check. Its output is non-deterministic. What reaches the
gate is the deterministic check a survivor earns, behind a reviewed pull request.

## Done

A second document is attacked in three rounds by somebody following a written procedure, the two
guards fail the run rather than being remembered, the prompt-leak check runs inside the
procedure, and the harness is not in `.scratch/`.
