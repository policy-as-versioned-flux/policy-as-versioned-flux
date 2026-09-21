# 07 — One loophole round against a named norm document

Type: task
Status: open
Blocked by: 06

## Question

Run loophole once, properly, against one document.

**The target, decided by the assistant under ADR-0025, with the reason.** The cage ladder in
[ADR-0022](../../../docs/adr/0022-the-cage-ladder-tier-per-namespace-isolated-rung-floor-and-infra.md).
Two reasons. The whole estate rests on it, so a hole in it is the most expensive hole available.
It is stated in prose, which is the only input loophole accepts.

1. Run one full round by the path ticket 06 chose.
2. Capture every candidate loophole case and every candidate overreach case.
3. Keep the conversation log. A candidate with no log is not reviewable.
4. Assert nothing. Ticket 08 decides what survives.

**Added 2026-09-21, from ticket 06's findings. All four are acceptance criteria.**

5. Run from the scratchpad clone only. loophole carries no licence, so nothing of it enters the
   project tree. See the map's call 5.
6. **Tell zero candidates apart from a failed parse.** `_parse_scenarios` at
   `loophole/loophole_finder.py:43-59` returns an empty list on malformed output, and
   `loophole/main.py:245-252` then prints that the legal code appears robust. Count the raw model
   responses and compare that count to the parsed count. A gap is a parse failure, and a parse
   failure is a failed run, never a clean bill of health.
7. Build the `claude -p` adapter against `call()`, not against `BaseAgent.run`.
   `loophole/agents/judge.py:89` calls `self.llm.call` directly and bypasses `run`.
8. Record that the temperature split is lost. `config.yaml:24-28` sets the finder to 0.9 and the
   judge to 0.3, and `claude -p` has no temperature flag. The finder is meant to be the creative
   one. State this limitation in the output, because it weakens the round.

## Done

The raw output stored under `.scratch/laya-loophole/research/`. A count of candidates. The run's
cost in turns, expected to be 14 model calls for one round.

A stated parse-failure count. Zero candidates with zero parse failures is a result. Zero
candidates with any parse failure is a failed run, and the ticket is not done.

## Notes

The estate's doctrine says the bottom rung is "too expensive to run or not functional", and that
there is never an exemption. That is exactly the kind of absolute claim an overreach finder
attacks. Expect it to find cases. Expect most of them to be wrong.
