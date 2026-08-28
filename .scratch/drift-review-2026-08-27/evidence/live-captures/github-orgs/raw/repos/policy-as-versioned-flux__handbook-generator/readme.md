# handbook-generator

Generates the policy handbook from any policy checkout + tag. Extracted from the `policy` repo
(ticket 05 of the real-estate epic, `policy-as-versioned-flux/policy-as-versioned-flux` hub,
`.scratch/real-estate/issues/05-extract-handbook-generator.md`) — everything the handbook shows is
read straight out of the given tag's tree via git plumbing, so it can never drift from what that
tag actually enforces, and it isn't tied to living inside the repo it reads from.

```sh
./generate.sh <policy-checkout-path> <tag> [--with-summaries]
```

`--with-summaries` weaves in agent-authored plain-language summaries (a real `claude -p` call per
policy), cached in **this component's own** `.cache/`, keyed by a hash of the exact `rationale.md`
content that produced each summary.

## Why the cache moved here, not just the generator

The cache is a derived artifact of policy *content* (each entry is keyed by a hash of a specific
`rationale.md`), but it isn't policy content itself — ticket 05's constraint was "the policy repo
keeps only what belongs to policy content," and a cached English paraphrase of a rationale doesn't
qualify. Moving it here also matches this component's own new shape: a generic tool invoked
against *any* policy checkout, not bound to living inside one specific repo.

## Freshness gate

```sh
./verify-fresh.sh <policy-checkout-path> <tag>
```

Fails loudly (non-zero exit, one `STALE` line per offender) if any policy's current `rationale.md`
content doesn't match a cached summary's hash — "stale summaries cannot ship," the property that
had to survive the move from the policy repo intact. Run this before publishing a handbook that
includes `--with-summaries` output.

## Self-check

`./verify.sh` — against a real signed tag from the real policy repo (not a mock): proves
`generate.sh` produces the correct handbook structure, and proves the freshness gate genuinely
fails on a missing cache entry and genuinely passes once a hash-matched one exists — without ever
calling `claude -p` (the cache *contract* is what's under test, not the summarizer itself).

## What this doesn't do

A generated handbook (with or without `--with-summaries`) is "a summary of the rationale a human
wrote, not a substitute for a human deciding whether the policy still holds" — the last-mile gap
CONTEXT.md names as an acknowledged open problem this component only attempts to mitigate, not
close. **Correction (2026-07-18, wave-2 audit)**: this disclosure, and the CI-wiring gap below,
lived in the `policy` repo's own README before this component was extracted (real-estate ticket
05) and were never carried over — a reader of this repo alone had no way to know either was true.
Running with `--with-summaries` in CI needs an `ANTHROPIC_API_KEY` secret only the org owner can
add; no CI workflow in this repo does so today (there's no `.github/workflows/` here at all) --
named as a real residual gap, not silently skipped.
