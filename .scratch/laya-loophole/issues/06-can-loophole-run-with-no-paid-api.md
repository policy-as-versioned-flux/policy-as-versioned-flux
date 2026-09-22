# 06 — Can loophole run with no paid API?

Type: research (AFK)
Status: resolved
Blocked by: none

## Question

On 2026-09-21 the owner instructed: run loophole inside the Claude Code harness, so it is free. No
paid Anthropic API spend. loophole as published calls the Anthropic API directly. Find the
mechanism that satisfies the instruction.

1. Read loophole's provider layer. Name the seam where the model is called, by file and line.
2. Judge three paths and pick the cheapest one that keeps the adversarial loop intact:
   - a custom provider that shells out to `claude -p`,
   - a local Ollama model, which the repository already supports,
   - a reimplementation of the loop as a Claude Code skill.
3. Report the licence. It was not visible on the repository page.
4. Report what one full round costs in turns, not in dollars.
5. Report whether the loop needs many short calls or few long ones. That decides whether a
   `claude -p` adapter is workable.

## Done

A research note under `.scratch/laya-loophole/research/`. It names the seam by file and line, names
the chosen path, and states the licence.

## Notes

Judge the three paths on one criterion: does the adversarial loop stay intact? A loop where one
agent plays both the loophole finder and the judge proves nothing. The HITL rule applies to agents
too.

## Answer (2026-09-21)

Full note: [`research/06-loophole-free-run-path.md`](../research/06-loophole-free-run-path.md).
loophole was not run.

**The seam — `loophole/llm.py:119`, `create_provider()`.** The only place a provider is constructed.
Its contract is the `LLMProvider` Protocol at `llm.py:6-16` (`call()` at `:12`); the model is
invoked at `loophole/agents/base.py:23`. `loophole/agents/judge.py:89` bypasses `BaseAgent.run` and
calls `self.llm.call` directly, so an adapter must implement `call()`, not just `run()`. The paid
path is `AnthropicProvider`, `llm.py:19-47`, keyed at `:23`. Per-role substitution is already wired,
no code change: `config.yaml:5-22` → `main.py:44-60` → `main.py:63-79`.

**Chosen path: (a), a provider that shells out to `claude -p`.** The only one that keeps the loop
adversarial. Each role gets its own provider instance, so every call is a separate process with a
fresh context and a different system prompt — the finder cannot see the judge's reasoning or approve
its own case. No weaker than the published default, which already runs all four roles on one model
(`config.yaml:2`). The CLI supplies what the Protocol needs (`--print`, `--model`,
`--system-prompt`, `--output-format json`, `--bare`). Caveat for ticket 09: `claude -p` has no
temperature flag, so the deliberate 0.9 finder / 0.3 judge split (`config.yaml:24-28`) is lost.

**(b) Ollama rejected** — not for weakness in the abstract, but because `_parse_scenarios`
(`loophole_finder.py:43-59`) returns an empty list on malformed output with no retry, and
`main.py:245-252` then reports "No failures found! The legal code appears robust." A model too weak
to hold the XML format yields a **false green** indistinguishable from a real result. Keep it only
as a contrast arm. **(c) skill reimplementation rejected** — one session would hold finder and judge
in one context window, the exact failure this ticket forbids.

**Licence: none.** No `LICENSE` file, GitHub API `license: null`, `/license` 404, no licence field
in `pyproject.toml`, no copyright header anywhere. No licence means all rights reserved, not public
domain. We may clone and run it to evaluate; we may **not** vendor, redistribute or fork it. Ticket
08 must not commit loophole source, and ticket 09's ADR cannot recommend adoption-by-vendoring
without the author granting a licence.

**Cost in turns:** round 1 is **14 calls**, round 2+ **20**, worst case ~26, a full 10-round session
~195. **Few long calls, not many short ones** — each is one stateless system+user pair,
`max_tokens` 4096, embedding the whole legal code and all resolved cases (`call_messages` is used
only by the chatbot sub-mode, `chatbot/agents/jailbreak.py:151`). That shape is what makes the
`claude -p` adapter workable. Ticket 07's single round costs 14 calls.
