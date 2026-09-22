# 06 — Can loophole run with no paid API?

Research note. Written 2026-09-21. Resolves ticket
[06](../issues/06-can-loophole-run-with-no-paid-api.md).

Primary source throughout: the repository source at `brendanhogan/loophole`, default branch `main`,
cloned at `pushed_at` `2026-06-03T14:04:47Z`. Line numbers below are from that tree. Nothing here
rests on the DeepWiki index — see [Note on DeepWiki](#note-on-deepwiki), which is stale and wrong on
the central fact.

loophole was **not run**. This ticket decides the mechanism; ticket 07 runs it.

---

## 1. The seam

**`loophole/llm.py:119` — `create_provider(provider, model, max_tokens, **kwargs)`.**

That factory is the only place a provider is constructed, and every model call in the main loop
passes through the object it returns. The seam has three parts:

| What | Where | Why it matters |
|---|---|---|
| The contract a provider must satisfy | `loophole/llm.py:6-16` — `LLMProvider` Protocol: `call()` at `:12`, `call_messages()` at `:15` | Two methods. That is the whole interface. |
| The factory that dispatches on a name | `loophole/llm.py:119-135`, unknown name raises at `:135` | One `if` branch adds a provider. |
| The single site that invokes the model | `loophole/agents/base.py:23` — `return self.llm.call(system, user_msg, temperature=self.temperature)` | Every main-loop agent funnels here. |

The Anthropic path that costs money is `loophole/llm.py:19-47` (`AnthropicProvider`), constructing
`anthropic.Anthropic()` at `:23` — which reads `ANTHROPIC_API_KEY` and bills the API.

Two call sites bypass `BaseAgent.run` and hit `self.llm.call` directly, so an adapter must satisfy
`call()` itself, not merely `run()`:

- `loophole/agents/judge.py:89` — `Judge.validate()`
- `loophole/chatbot/agents/judge.py:95` — chatbot sub-mode, not used by the main loop

**The seam is already wired for per-role substitution, with no code change.** `config.yaml:5-22`
documents a `model.providers` block keyed by role; `loophole/main.py:44-60` (`_resolve_provider`)
reads it and calls `create_provider` per role; `loophole/main.py:63-79` (`_build_agents`) hands each
role its own provider instance. So the four adversarial roles can be bound to four *separate*
provider objects. That property is what decides question 2.

`README.md:205` confirms the intent: "Each agent role can use a different provider."

## 2. The licence — there is none

**No licence. All rights reserved.** This is the most consequential finding in the note, and it was
not asked about in the form it turned out to take.

Evidence, four independent checks:

| Check | Result |
|---|---|
| `LICENSE` / `COPYING` file at repo root | absent — root tree is `.gitignore`, `.python-version`, `README.md`, `config.yaml`, `examples`, `loophole`, `pyproject.toml`, `sessions`, `uv.lock` |
| GitHub API `repos/brendanhogan/loophole` → `license` field | `null` |
| GitHub API `repos/brendanhogan/loophole/license` | `HTTP 404 Not Found` |
| `pyproject.toml` `license` field / any copyright header in any `.py` or `.md` | absent |

A work with no licence is not public domain. Copyright subsists automatically; absent a grant, the
default is that no use, copying, modification or redistribution is permitted. GitHub's Terms of
Service §D.5 grant only the right to view and to fork *within GitHub* — not to use, modify or
redistribute elsewhere.

What this permits and forbids for the estate:

- **Permitted:** clone and run locally to evaluate it. That is what tickets 06–08 do.
- **Forbidden without the author's grant:** vendoring loophole's source into this repository,
  redistributing it, or shipping a modified fork.
- **Consequence for ticket 08:** loophole source must not be committed into the estate. A fixture
  derived from loophole's *output* is our own work and is unaffected.
- **Consequence for ticket 09:** the ADR cannot recommend adoption-by-vendoring. The honest options
  are run-it-out-of-tree, or ask the author to add a licence.

This also cuts against path (c) below: a reimplementation would necessarily copy
`loophole/prompts.py`, the most creative and most clearly copyrightable part of the work.

## 3. The cost of one round, in turns

Counted by reading `_run_adversarial_loop` at `loophole/main.py:222-390` against the default
`config.yaml` (`cases_per_agent: 3`, `max_rounds: 10`), so six cases per round — three loopholes,
three overreaches.

Each agent method is exactly **one** model call. Verified: `LoopholeFinder.find`
(`loophole_finder.py:39`), `OverreachFinder.find` (`overreach_finder.py:39`), `Judge.evaluate`
(`judge.py:60`), `Judge.validate` (`judge.py:89`), `Legislator.revise` (`legislator.py:54`),
`Legislator.draft_initial` (`legislator.py:49`), `Simplifier.simplify` (`simplifier.py:37`). The
finders emit all three cases in a single call, parsed out by regex at `loophole_finder.py:45-49`.

| Phase | Calls | Source |
|---|---|---|
| Session bootstrap, once | 1 | `main.py:487` `legislator.draft_initial` |
| Per round, phase 1: two finders | 2 | `main.py:236`, `main.py:240` |
| Per round, phase 2: judge each of 6 cases | 6 | `main.py:264` |
| Per case auto-resolved: legislator revises | 6 | `main.py:276` / `main.py:317` |
| Per case auto-resolved, **round 2+ only**: judge validates | 6 | `main.py:278` |

**Round 1: 14 calls.** No validation happens, because `main.py:268` gates on
`state.resolved_cases` being non-empty, which it is not on the first round — control falls to the
`else` at `main.py:311`.

**Round 2 onward: 20 calls** in the steady state where every case auto-resolves and validation
passes.

**Worst case ~26 calls** per round, when validation fails and `_escalate` (`main.py:393`) triggers a
second `legislator.revise` at `main.py:417`.

**A full default 10-round session: roughly 195 calls** (1 + 14 + 9x20). An optional simplification
pass adds 2 (`main.py:181` + `main.py:191`).

Ticket 07 runs one round against one norm document: **14 calls**, since it will be round 1 of a
fresh session.

## 4. Few long calls, not many short ones

Decisively **few long calls**, and this is what makes a `claude -p` adapter workable.

- Every main-loop call is a single stateless `(system, user_message)` pair through
  `LLMProvider.call` (`base.py:23`). There is no conversation object, no turn history, no tool use,
  no streaming dependency.
- `call_messages` — the only multi-turn path — is used at exactly one site, and it is **not** in the
  main loop: `loophole/chatbot/agents/jailbreak.py:151`, the separate chatbot sub-mode.
- Payloads are large and grow monotonically. `LEGISLATOR_REVISE` (`prompts.py`) embeds the moral
  principles, all user clarifications, the **entire current legal code**, the new case, and **all
  previously resolved cases** as binding precedent. `LOOPHOLE_FINDER_USER` embeds the full code plus
  every prior case (`loophole_finder.py:28-36`). `prompts.py` is 10,248 characters of templates
  before any state is interpolated.
- `max_tokens: 4096` on output (`config.yaml:4`).

So the workload is ~20 independent, long, one-shot request/response pairs per round. That is exactly
the shape `claude -p` serves: one process, one prompt, one answer, no session to keep alive.

## 5. The three paths, judged on one criterion

The criterion, from the ticket: **does the adversarial loop stay intact?** A loop where one agent
plays both the loophole finder and the judge proves nothing.

The structural test that follows from that: *are the finder and the judge separated such that the
finder cannot see, anticipate or collude with the judge's reasoning, and cannot approve its own
case?*

### (a) A custom provider that shells out to `claude -p` — **CHOSEN**

**Loop stays intact.** Each role gets its own provider instance (`main.py:63-79`), and every call is
a separate OS process with a fresh context window and a different system prompt. The finder's
context never contains the judge's reasoning; the judge's context never contains the finder's
deliberation, only the emitted `<scenario>` payload. Self-approval is not structurally available.

The objection worth meeting head-on: *the same model weights serve both roles, so is it really
adversarial?* Yes — and note that **the published tool's own default is already exactly this**.
`config.yaml:2` sets one default model, `claude-sonnet-4-20250514`, for all four roles, and
`main.py:58-60` falls all unconfigured roles back to it. Separation in loophole is by prompt and by
process, not by vendor. A `claude -p` adapter reproduces that separation faithfully. It is no weaker
than the published default, which is the benchmark the ADR should be measured against.

Cost: no cash. `claude -p` draws on the Claude Code subscription entitlement, not API credits,
satisfying the owner's 2026-09-21 ruling.

Effort: one class implementing `call()` and `call_messages()`, plus one `if` branch at
`llm.py:119-135`, plus a `providers:` block in `config.yaml`. No change to any agent, prompt, or
loop.

The CLI supplies everything the Protocol needs — verified against `claude --help` on this machine:
`-p/--print`, `--model`, `--system-prompt` / `--append-system-prompt`, `--output-format json`,
`--bare` (skips hooks, LSP, plugin sync, auto-memory), `--strict-mcp-config`, `--disallowed-tools`.

Two honest caveats, both to be recorded in the ticket 09 ADR rather than hidden:

1. **Temperature is lost.** `claude -p` exposes no temperature flag. `config.yaml:24-28` sets the
   finders to 0.9 and the judge to 0.3 deliberately — high diversity for attack, low for
   adjudication. An adapter must silently drop the `temperature` argument. Expect less varied
   attacks and a slightly less deterministic judge. Mitigate by asking for diversity in the system
   prompt; measure, do not assume.
2. **`claude -p` is an agentic harness, not a raw completion endpoint.** It may emit preamble or
   attempt tool use. Two things contain this: run it bare and toolless with the flags above, and
   note that loophole parses by regex over XML tags (`loophole_finder.py:45-49`,
   `_extract_tag` in `judge.py:98` / `legislator.py:64`), so surrounding prose is skipped rather
   than fatal. The parse contract is robust to chatter.

Licence fit: the adapter is a small new file plus a one-line branch, kept out of tree as a local
overlay. This is the smallest licence exposure of the three paths.

### (b) A local Ollama model — **rejected, and it is the subtle trap**

Zero cash and zero code change; it is already supported (`llm.py:98-107`, `config.yaml:13-16`,
`README.md:205`). Structurally the loop is as separated as in (a). On a naive reading it wins.

It fails on the criterion for a reason visible in the source. `_parse_scenarios`
(`loophole_finder.py:43-59`) matches a strict nested XML shape —
`<scenario><description>...</description><explanation>...</explanation></scenario>` — and **returns
an empty list on any malformed output**. There is no error path and no retry. An empty finder result
then flows to `main.py:245-252`, which prints:

> "No failures found! The legal code appears robust against this round of testing."

So a local model too weak to hold the output format produces a **false green** that is
indistinguishable from a genuine robustness result. The adversarial loop has not stayed intact — it
has silently stopped running while still reporting success. That is precisely the failure this
estate's standing rule forbids: *derive what you assert*. A model that cannot attack is not an
adversary, and the harness cannot tell the difference.

The models that could hold the format reliably are large. `config.yaml:15` suggests
`llama3.1:70b` — not runnable at useful speed on this machine for ~20 long, context-growing calls a
round.

Ollama stays available as a *contrast arm* if ticket 07 later wants to measure attack quality
against a weaker adversary. It is not the mechanism.

### (c) Reimplementation as a Claude Code skill — **rejected**

This is the path that breaks the loop, which is the one thing the criterion forbids. A skill runs
inside a single Claude Code session: one context window would hold the legislator, both finders and
the judge. The judge would see the finder's reasoning and could approve its own case. That is
exactly "one agent plays both the loophole finder and the judge", and it proves nothing.

It also discards the session persistence (`session.py`), the HTML report (`visualize.py`), the XML
parse contract, and the prompt engineering in `prompts.py` — and, per section 2, copying those
prompts is the clearest copyright exposure of the three options.

### Verdict

**Path (a).** It is the only one that is free, keeps finder and judge genuinely separated, and
preserves the published tool's own behaviour closely enough that ticket 07's round measures loophole
rather than measuring our reimplementation of it.

## Note on DeepWiki

`mcp__deepwiki__ask_question` on `brendanhogan/loophole` was consulted and is **stale and wrong on
the central fact**. It states: "Currently, only Anthropic models are supported… There is no
indication in the provided code snippets that OpenAI or Ollama are supported," and describes the
seam as "the `LLMClient` class… the `call` method".

At HEAD, `LLMClient` is not a class but a backward-compatibility *function* (`llm.py:138-143`), and
`OpenAIProvider` (`llm.py:50`) and `OllamaProvider` (`llm.py:98`) both exist, with
`openai>=1.0` a declared dependency (`pyproject.toml:8`). Every claim in this note is taken from the
cloned source, not from the index. Recorded because the difference would have changed the answer to
question 2 — a reader trusting DeepWiki would have ruled out path (b) for the wrong reason and never
found the false-green trap that actually rules it out.

## Open questions this note does not settle

- Whether the lost temperature (caveat 1) measurably degrades attack quality. Ticket 07 can observe
  it; it cannot be settled by reading.
- Whether the author will add a licence if asked. That is an owner decision — it touches
  authorisation and a named person — and it gates any adoption-by-vendoring in ticket 09.

## Sources

- Source tree, `github.com/brendanhogan/loophole`, branch `main`, `pushed_at`
  `2026-06-03T14:04:47Z`. Files cited: `loophole/llm.py`, `loophole/main.py`,
  `loophole/agents/base.py`, `judge.py`, `legislator.py`, `loophole_finder.py`,
  `overreach_finder.py`, `simplifier.py`, `loophole/prompts.py`, `config.yaml`, `pyproject.toml`,
  `README.md`.
- GitHub REST API: `/repos/brendanhogan/loophole` (`license: null`),
  `/repos/brendanhogan/loophole/license` (404), `/repos/brendanhogan/loophole/contents/`.
- `claude --help`, Claude Code CLI on this machine, 2026-09-21.
- `mcp__deepwiki__ask_question` on `brendanhogan/loophole` — consulted, found stale, not relied on.
