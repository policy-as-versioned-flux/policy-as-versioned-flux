# 25 — The generator standing check

Type: task
Status: done (2026-08-24)
Blocked by: 21

Source: [`spec.md`](../spec.md), *Testing Decisions*, and *Signing and verification*.

## What to build

A change to the generator cannot quietly change what a release means. The generator gets one standing
check, not a test suite.

**A generator change re-runs the three known-good bumps.** It is refused if any stops rederiving. That
is the map's own rule applied to the tool. The engine must reproduce a human's correct answer before it
is trusted to give its own.

**A generator change also re-runs the previous release under the new generator.** It prints a line if
the classification would differ. It does not fail. A human decides whether a past release was
mislabelled.

Evidence is pinned to its generator version and never recomputed. An old release keeps the
classification it was signed with.

[Ticket 15](15-the-repair-release.md) is hand-classified, so this check re-runs it once the gate
exists.

## Acceptance criteria

- [x] A pull request that changes the generator re-runs the three known-good bumps.
- [x] The pull request is refused if any known-good bump stops rederiving.
- [x] The same pull request re-runs the previous release under the new generator.
- [x] A differing classification prints a line and does not fail the build.
- [x] Existing evidence files keep their recorded `generator_version` and are never recomputed.
- [x] The check is one standing check, not a per-function test suite.

## Comments

Shipped in `platform` at `c630f5f` (cs-25).
