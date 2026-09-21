# 07 — One loophole round against a named norm document

Type: task
Status: resolved
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

## Answer (2026-09-21)

Full note: [`research/07-loophole-round-against-adr-0022.md`](../research/07-loophole-round-against-adr-0022.md).

**The round ran. It produced 6 candidates, 3 loophole and 3 overreach, from 8 model calls, with 0
parse failures on both finders and 0 on the judge.** Raw output, every system prompt, every user
message and every response are in `research/07-loophole-round/`.

**The zero is falsifiable.** `.scratch/laya-loophole/bench/parse_failure_control.py` feeds five
shapes through the real upstream parser and the detector fires on two of them: a truncated tag
gives 1 parse failure, and wrong inner tags give 3. **It misses a third shape, and that is stated
rather than hidden.** A model that abandons the format entirely opens no tag, so the parse-failure
count reads 0 and the candidate count reads 0. A second counter, under-production, catches that
case. So a clean run means both counters at zero. This run reads zero on both, for both finders.
Item 6 is met, with its limit named.

**The judge carries the same defect in a second place.** `agents/judge.py:62-63` reads a missing
`<verdict>` tag as the literal verdict "unresolvable". The harness records tag presence. The tag
was present on all 6 calls.

**A finding about this ticket's own run path. `--bare` breaks the run silently, and ticket 06
named it.** `--bare` never reads OAuth, so with no `ANTHROPIC_API_KEY` the call fails with exit
code 0, `subtype: "success"`, `is_error: true` and `result: "Not logged in · Please run /login"`.
The obvious adapter returns that sentence, the parser finds no tags, and loophole prints that the
legal code appears robust. A broken login reads as a clean bill of health. The harness now refuses
a non-zero exit, unparseable stdout, and `is_error: true`. Both guards are proven to fire.

**Item 5 and item 3 conflict, and the harness resolves the conflict rather than choosing a side.**
The conversation log item 3 asks for holds loophole's prompt text verbatim in every system prompt
and every user message, and loophole carries no licence. The committed log therefore holds the
model responses, which are this run's output, plus a sha256 and a length for each prompt. The
unredacted log went to the scratchpad through `--full-log`. A check confirms that no sentence of 8
words or more from `loophole/prompts.py` appears in `calls.jsonl` or `candidates.json`. The
candidates stay reviewable and the digests still bind each response to its exact input.

**Item 7 is met.** The adapter implements `call()`, which is what `agents/judge.py:89` needs.

**Item 8 is met.** The temperature split is lost, and the note states it. `claude -p` has no
temperature flag, so the finder ran at the harness default rather than the published 0.9.

**Item 5 is met.** The harness holds no loophole source and no loophole prompt. It imports the
clone from `LOOPHOLE_SRC`, which stays in the scratchpad.

**Cost: 8 model calls, not the expected 14, and the difference is deliberate.** 14 is 2 finder
calls, 6 judge calls and 6 legislator revise calls. This run made no revise call, so every case is
judged against the same v1 text and the norm document is not rewritten by a model. The Legislator
also never drafted: ADR-0022 is supplied as the legal code. Both departures are recorded in the
note. Wall time 185.8 s. List price 0.4150 USD, attributed by the CLI and not charged, because the
run used the subscription.

**Three further deviations, each measured.** The `max_tokens` cap is not applied, and it would not
have bound, because the largest response was 3,007 output tokens against a 4,096 cap. The served
model is `claude-sonnet-5`, not the published `claude-sonnet-4-20250514`, so the finder is stronger
than the published tool. `claude -p` ran with `--safe-mode`, `--tools ""` and `--strict-mcp-config`,
so no CLAUDE.md, skill, hook or MCP server reached any prompt.

**Side finding: upstream case identifiers collide.** Both finders run before any case is appended
to `state.cases`, so both number their cases 1, 2, 3 in every round. A session then holds two cases
numbered 1, two numbered 2 and two numbered 3, and the case log, the HTML report and the judge's
prior-case text all address cases by that number. The harness adds its own stable key.

**Correction to this ticket's own citation.** Item 6 cited `loophole/loophole_finder.py:43-59`.
The path is `loophole/agents/loophole_finder.py:43-59`. Same lines.

**Nothing is asserted about the six candidates.** They are recorded in
`research/07-loophole-round/candidates.json` with the judge's verdict on each. Five read
resolvable and one, `overreach-5`, reads unresolvable. Ticket 08 decides what survives.
