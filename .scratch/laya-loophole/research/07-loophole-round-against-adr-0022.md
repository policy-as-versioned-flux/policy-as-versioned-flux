# 07 — One loophole round against ADR-0022, the cage ladder

Run 2026-09-21. Ticket [07](../issues/07-one-loophole-round-against-a-named-norm-document.md).

**Result: 6 candidates, 3 loophole and 3 overreach, from 8 model calls, with 0 parse failures
on both finders and 0 on the judge.** The zero is falsifiable, because a negative control shows
the detector firing on three malformed shapes. This note asserts nothing about whether any
candidate is real. Ticket 08 decides that.

## What ran

| Item | Value |
| --- | --- |
| Target document | `docs/adr/0022-...md`, 15,760 characters, sha256 `728129b3…4ae1ed` |
| Principles input | `research/07-loophole-round/inputs/principles.md`, sha256 `8d7d9c57…b60726` |
| loophole clone | commit `129f7c0`, in the scratchpad, outside the project tree |
| Harness | `.scratch/laya-loophole/bench/loophole_round.py` |
| Model served | `claude-sonnet-5`, one process per call |
| Model calls | 8 |
| Wall time | 185.8 s |
| List price | 0.4150 USD, attributed but not charged |
| Raw log | `research/07-loophole-round/calls.jsonl`, 40 KB, prompts redacted |

The harness holds no loophole source and no loophole prompt. It imports the clone from
`LOOPHOLE_SRC`. The map's call 5 stands: nothing of loophole entered the project tree.

The principles input is quoted from `CONTEXT.md` and from ADR-0022's own notes. It states 13
principles. None is invented for this run.

### The transport

Each call is one `claude -p` process. The process is stateless, holds no tools, and loads no
CLAUDE.md, skill, hook or MCP server, because the harness passes `--safe-mode`, `--tools ""` and
`--strict-mcp-config`. The finder cannot read the judge's reasoning. The adversarial loop stays
intact, which is the criterion ticket 06 set.

### Deviations from `loophole/main.py`, and their effect

1. **The Legislator never ran.** The published `new` command asks a model to draft the legal code.
   This run supplies ADR-0022 instead, so the target is the estate's real document.
2. **The Legislator never revised.** The published loop rewrites the code after each resolved
   case, so cases 2 to 6 are judged against a document the model wrote. This run holds the code at
   v1, so all six verdicts are about the same text and are comparable. This is why the round cost
   8 calls and not 14. The 14 is 2 finder calls, 6 judge calls and 6 revise calls. The 6 revise
   calls are the ones this run did not make.
3. **The temperature split is lost.** `config.yaml:24-28` sets the finder to 0.9 and the judge to
   0.3. `claude -p` has no temperature flag. The finder is meant to be the creative one, so this
   weakens the round. Ticket 07 item 8 required this statement.
4. **The `max_tokens` cap is not applied.** The published cap is 4,096. The largest response here
   was 3,007 output tokens, so the cap would not have bound. The deviation changed no output.
5. **The model is newer than the published one.** `config.yaml:2` names
   `claude-sonnet-4-20250514`. This run asked for `sonnet` and the harness served
   `claude-sonnet-5`. A stronger finder is not a like-for-like reproduction of the published tool.

## The log the estate may keep, and the one it may not

Ticket 07 item 3 asks for the conversation log, because a candidate with no log is not reviewable.
Ticket 07 item 5 forbids any part of loophole from entering the project tree. **The full log
breaks item 5**, because every system prompt and every user message is loophole's own prompt text
verbatim, and loophole carries no licence.

The harness resolves this rather than choosing a side. By default it logs the model **responses**,
which are this run's output and not loophole's expression, and replaces each prompt with its
sha256 and its length. The unredacted log is written only when `--full-log` names a path, and the
flag's help says to point it outside the tree. This run's unredacted log stayed in the scratchpad.

A check confirms the redaction. No sentence of 8 words or more from `loophole/prompts.py` appears
in `calls.jsonl` or `candidates.json`. The digests still bind each response to the exact prompt
that produced it, so anyone with the clone can reproduce and verify.

**Ticket 09's ADR inherits this.** An unlicensed tool cannot leave a reviewable trail in a repo
that keeps everything. What the estate may keep is the output and a digest of the input.

## The parse-failure audit

Ticket 07 item 6 required that a zero result be told apart from a failed parse. `_parse_scenarios`
at `loophole/agents/loophole_finder.py:43-59` returns an empty list on malformed output, and
`loophole/main.py:245-252` then prints that the legal code appears robust. The ticket cited this
file as `loophole/loophole_finder.py`; the path is `loophole/agents/loophole_finder.py`, same lines.

The harness counts three numbers per finder call.

| Finder | requested | `<scenario>` opens | parsed | parse failures | under-production |
| --- | --- | --- | --- | --- | --- |
| loophole | 3 | 3 | 3 | 0 | 0 |
| overreach | 3 | 3 | 3 | 0 | 0 |

The judge has the same defect in a second place. `agents/judge.py:62-63` reads a missing
`<verdict>` tag as the literal verdict "unresolvable", which then escalates to a human. The
harness records whether the tag was present. It was present on all 6 judge calls.

### The negative control

A zero that cannot fire is not a measurement. `.scratch/laya-loophole/bench/parse_failure_control.py`
feeds five shapes through the real upstream parser. Stored output:
`research/07-loophole-round/parse-failure-control.txt`.

| Input | parsed | opens | parse failures | under-production |
| --- | --- | --- | --- | --- |
| A well-formed, 3 scenarios | 3 | 3 | 0 | 0 |
| B truncated, tag opened and never closed | 1 | 2 | **1** | 1 |
| C wrong inner tags, a weak model | 0 | 3 | **3** | 0 |
| D prose only, no tags at all | 0 | 0 | 0 | **3** |
| E markdown fence round the XML | 1 | 1 | 0 | 2 |

**State the limit plainly. The tag counter alone does not catch row D.** A model that abandons the
format entirely opens no tag, so the parse-failure count reads 0 and the candidate count reads 0.
That is the false green ticket 06 named, and the tag counter misses it. The under-production
counter catches it instead. So the acceptance rule for a clean run is both counters at zero, not
the parse-failure counter alone. This run reads zero on both counters for both finders.

## A finding about the run path itself

**Ticket 06 named `--bare` as part of the `claude -p` invocation. `--bare` breaks the run, and it
breaks it silently.** `--bare` reads Anthropic credentials only from `ANTHROPIC_API_KEY` or an
`apiKeyHelper`, and never from OAuth. This machine has no such key, so the call fails. Measured:

- shell exit code `0`
- `subtype` reads `"success"`
- `is_error` reads `true`
- `result` reads `Not logged in · Please run /login`

An adapter that returns `payload["result"]`, which is the obvious implementation, hands that
sentence to `_parse_scenarios`. The parser finds no tags, returns an empty list, and loophole
prints that the legal code appears robust. **A broken login reads as a clean bill of health.** This
is the estate's own defect class, eco-system ticket 98, reached by a third route.

The harness therefore carries two guards, and both are proven to fire:

1. It refuses a non-zero exit code or unparseable stdout.
2. It refuses `is_error: true`, whatever the exit code says.

Guard 2 was added after the measurement above, and a shim that emits the failing payload proves it
raises rather than returning the error string.

## The six candidates

Recorded, not judged. Full scenario, explanation and judge verdict in
`research/07-loophole-round/candidates.json`.

| Key | Type | One line | Judge |
| --- | --- | --- | --- |
| `loophole-1` | loophole | A party under-declares by never submitting a price line for its risky workload, so the strictest-across-`prices[]` fold never sees it and the Namespace stays at `baseline`. | resolvable |
| `loophole-2` | loophole | A platform-role party declares an `infra` Namespace, then lets third-party workloads run in it. The role check covers who declares, not who deploys. | resolvable |
| `loophole-3` | loophole | Two governed Namespace documents make `apply_tier_declaration()` refuse to write. The refusal is a refusal to update, not a fall to `isolated`, so a stale looser tier keeps serving. | resolvable |
| `overreach-4` | overreach | An on-call engineer cannot run network diagnostics during an incident, because the `isolated` rung strips all reach. | resolvable |
| `overreach-5` | overreach | A benign wiki pod in a Namespace nobody has governed yet lands on the bottom rung and is evicted first. | **unresolvable** |
| `overreach-6` | overreach | A non-platform party's `infra` declaration renders `isolated` silently, with no feedback, and breaks unrelated builds. | resolvable |

The judge called `overreach-5` unresolvable. Its stated reason is that the case attacks a rule the
owner deliberated and defended on 2026-09-02, and that any fix would reintroduce a carve-out that
principle 3 bans. In the published loop that verdict escalates to a human.

## Side finding: upstream case identifiers collide

`_parse_scenarios` numbers a case `state.next_case_id + len(cases)`. Both finders run before any
case is appended to `state.cases`, so in every round both produce the same identifiers. This run
produced loophole cases 1, 2, 3 and overreach cases 1, 2, 3. `main.py` appends all six, and the
session then holds two cases numbered 1, two numbered 2 and two numbered 3. The case log, the HTML
report and the judge's prior-case text all address cases by that number. The harness records the
upstream identifier and adds its own stable key.

## How to run it again

```sh
LOOPHOLE_SRC=<clone outside the tree> <venv>/bin/python \
  .scratch/laya-loophole/bench/loophole_round.py \
  --code   .scratch/laya-loophole/research/07-loophole-round/inputs/adr-0022.md \
  --principles .scratch/laya-loophole/research/07-loophole-round/inputs/principles.md \
  --domain "Kubernetes multi-tenancy posture: which cage a workload runs in" \
  --out    .scratch/laya-loophole/research/07-loophole-round
```

Add `--full-log <path outside the tree>` to keep the prompts. Do not point it inside the repo.

The venv needs `pydantic` only. The finder output is not deterministic, so a second run gives
different candidates.
