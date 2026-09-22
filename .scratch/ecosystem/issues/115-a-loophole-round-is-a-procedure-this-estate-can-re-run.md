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

## Build, 2026-09-22

Hub PR: https://github.com/policy-as-versioned-flux/policy-as-versioned-flux/pull/89, branch `ticket-115-loophole-procedure`. Hub only. No unit repo changed.

### What was built

- **The harness left `.scratch/`.** It lives in `bench/loophole/` with its own `README.md`, which
  is the written procedure: set up, controls, three rounds, the leak check before `git add`, and
  what to do with the candidates. `bench/loophole/loophole_round.py` and
  `bench/loophole/check_no_prompt_leak.py` hold no loophole source and no loophole prompt. The
  leak check reads 0 runs in both files and in the README.
- **The guards fail the run.** `--bare` is refused by `refuse_forbidden_flags()` before any
  subprocess starts. The failure shape is refused whatever flag caused it: a reply that is not
  JSON, a non-zero exit, or `is_error: true` raises `GuardError` and the harness exits 2. A round
  exits 1 when either counter is above zero or a judge reply has no verdict the upstream judge
  can read. Before any call, `--controls-only` and every round feed ticket 07's five control
  inputs to loophole's own `_parse_scenarios` and exit 3 unless both counters fire where the
  table says. That is `parse_failure_control.py`, now inside the procedure.
- **The prompt-leak check runs inside the procedure.** The harness requires its negative control
  (1287 of 1287 runs) before the round, scans `calls.jsonl` and `candidates.json` after it, and
  scans `summary.json` last. A hit fails the round. The README still asks for the check by hand
  before `git add`, because files can change after the run. It now walks a directory.
- **A round writes down ADR-0030 point 9.** `summary.json` carries `target` (path, the commit
  the harness ran at, the commit that last changed the file, sha256), `harness` (its own sha256
  and the leak check's), `model_served`, `model_calls`, `wall_time_s`, `list_price_usd`,
  `counters`, `candidates`, `prompt_digests`, and `ticket` from `--ticket`. The `"ticket": "07"`
  constant is gone. The harness refuses a target with uncommitted changes, because then no
  commit names its text.
- **The budget is in the README**, beside the procedure: 24 calls, 539.0 s and 1.2416 USD for
  the three ADR-0022 rounds, summed from their `calls.jsonl`. The README says the real cost is
  checking about 18 candidates at roughly half a ticket each.

### The second document, attacked in three rounds

ADR-0026, "a hole is priced, never refused", was attacked in three rounds, one after another,
by following `bench/loophole/README.md`. Its text is from commit `3655bb8f` (the last commit to
touch it); the harness ran at `556669bb` on this branch. Principles are in
`bench/loophole/rounds/adr-0026/principles.md`, each line sourced.

| Round | Clean | Calls | Wall time | List price | Parse failures | Under-production | No verdict | Candidates | Judge resolvable |
|---|---|---|---|---|---|---|---|---|---|
| 1 | yes | 8 | 201.4 s | 0.4849 USD | 0 | 0 | 0 | 6 | 3 |
| 2 | yes | 8 | 205.6 s | 0.4828 USD | 0 | 0 | 0 | 6 | 3 |
| 3 | yes | 8 | 203.6 s | 0.4828 USD | 0 | 0 | 0 | 6 | 5 |
| Total | | 24 | 610.6 s | 1.4505 USD | 0 | 0 | 0 | 18 | 11 |

Every number is read from the three `summary.json` files. Model served: `claude-sonnet-5` on
all 24 calls. loophole clone at `129f7c0e`. Harness sha256 `aea48f73…918c95` on all three.
A round cost about 17% more list price than an ADR-0022 round (0.48 against 0.41 USD); ADR-0026
is 20,489 bytes against ADR-0022's 18,149 on disk, measured with `wc -c`, so the prompt is
longer. That is a plausible cause, not a measured one.

The leak check ran over `bench/loophole/` before the commit that added the rounds:
1287 distinct runs, control 1287 of 1287, 0 leaked runs in every file it walked, including the
nine round files, `principles.md`, the README and both harness files.

**The 18 candidates are not checked against the code.** They are charted as
[ticket 119](119-the-eighteen-unchecked-candidates-against-adr-0026.md).

### The next document

**ADR-0020**, "a missing instrument refuses, a missing behaviour is priced". Delegated. Reasons:
ADR-0026 point 6 classifies every refusal kind on ADR-0020's line, so the line itself has not
been attacked while two documents that rest on it have. Round 3 overreach-4 against ADR-0026
already points at that edge: a catalogue pin that rotted, which is an instrument, met by an
engineer's workaround, which is a behaviour. It is 7,005 bytes against ADR-0026's 20,489
(`wc -c`), so a round's prompt is shorter.

### Decisions (all delegated, ADR-0025)

1. **The home is `bench/`, a new top-level directory for evaluation instruments that are not
   gate checks.** `verify/` is the gate and `tests/` are deterministic checks; putting a
   non-deterministic tool under either would read as ADR-0030 point 8's forbidden shape. `twin/`
   is a participant, not a bench. `.scratch/` is the issue tracker.
2. **The committed rounds live beside the harness in `bench/loophole/rounds/<document>/`.** The
   procedure and its evidence are read together. The ADR-0022 rounds stay in
   `.scratch/laya-loophole/research/` because their summaries and ADR-0030 name those paths.
3. **The `.scratch/` harness copies stay.** ADR-0030's evidence list and ticket 11's
   same-harness-by-sha256 claim point at them. ADR-0030 gets a dated note naming the new home.
4. **The guards are pure functions, tested in `tests/test_loophole_round.py`.** The tests run
   in CI with no clone and no model. They grade the estate's harness, never loophole's output,
   so they do not make loophole a gate check.
5. **A judge reply with no readable verdict fails the round too.** ADR-0030 point 6 names two
   counters; point 5 names this third silent failure. It is the same defect class, so it gets the
   same treatment.
6. **The counter control runs against loophole's real parser at the start of every round.** A
   stand-in parser in the tests cannot notice an upstream parser change; the startup control can,
   and it spends no model call.
7. **The harness refuses `LOOPHOLE_SRC` or `--full-log` inside the project tree**, and runs
   `claude -p` in a temporary directory outside it. ADR-0030 points 1 and 7 become refusals.
8. **The target must be committed.** The summary names a commit, so a dirty file is refused.

### Tests

- `tests/test_loophole_round.py`: red first (26 errors, the module did not exist), then
  `26 passed` with `.venv/bin/python -m pytest tests/test_loophole_round.py -n0 -q`.
- `.venv/bin/python -m mypy twin tests conftest.py --ignore-missing-imports --warn-unused-ignores`:
  `Success: no issues found in 195 source files`. `mypy bench/loophole` is clean too.
- `loophole_round.py --controls-only` against the real clone: `counter control: 5/5`,
  `leak control: 1287/1287`, exit 0. With `LOOPHOLE_SRC` inside the tree, and with `--full-log`
  inside the tree: `GUARD`, exit 2.
- `verify/derived-status/verify-derived-status.sh` on this worktree: PASS, 119 tickets, every
  number names one file.

### Waits on the owner

Nothing. The rounds ran on the subscription the owner authorised on 2026-09-21. Checking the 18
candidates is ticket 119's work.
