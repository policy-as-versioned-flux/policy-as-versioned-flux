# 30 — ADR-0011 and the `CONTEXT.md` edits

Type: task
Status: done (2026-08-24)
Blocked by: 22, 26

Source: [`spec.md`](../spec.md), *Two documents are owed*, and *What the gate measures*.

## What to build

A reader who never runs the gate can still learn what it promises.

**ADR-0011 records the gate.** It computes the bump, refuses a weaker declaration, permits a stronger
one, and has no override. Cross-reference ADR-0002, which makes the reviewed pull request the only way
a new version lands.

**`CONTEXT.md` gains three things and nothing else.**

1. One sentence defining reset on bump. The historical `2.1.1` fails that rule, correctly.
2. One entry naming the `platform-machinery` class, so a reader knows which policies the platform tag
   numbers rather than a claim.
3. The record that compliant means admitted. An Audit rule that fires reports and does not refuse.
   Today that is only inferable.

**Do not put gate jargon in `CONTEXT.md`.** *Hole*, *proved exclusion* and *predicate expression* belong
to one gate. `CONTEXT.md` is the thesis glossary. Those terms live in the gate's own README.

## Acceptance criteria

- [x] ADR-0011 exists and records the gate.
- [x] ADR-0011 states that there is no override, and why.
- [x] ADR-0011 cross-references ADR-0002.
- [x] `CONTEXT.md` defines reset on bump in one sentence.
- [x] `CONTEXT.md` names the `platform-machinery` class.
- [x] `CONTEXT.md` records that compliant means admitted.
- [x] `CONTEXT.md` gains nothing else.
- [x] *Hole*, *proved exclusion* and *predicate expression* appear in the gate's README, not in `CONTEXT.md`.

## Comments

Shipped in `hub` (this repo) at `c297835` (cs-30) — `docs/adr/0011-release-gate-computes-the-bump.md` and `CONTEXT.md`.
