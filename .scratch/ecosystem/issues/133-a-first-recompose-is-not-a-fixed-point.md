# 133 — A first recompose is not a fixed point

Type: task
Status: resolved
Blocked by: none

## Question

Charted 2026-09-24 by the integrator from the v3.3.0 rollout on tuppence (PR 36) and its review.

The composer reads the working tree's `composed/` as its "before". On tuppence the first
recompose under v3.3.0 emitted a `new-ungoverned-namespace` delta for `openbao` of
2,315,591.33 GBP. A second pass recorded `openbao` as `recorded` and carried no delta, and passes
two to four were byte-identical. The first builder committed the second pass and so hid the
delta. The fix restored `origin/main`'s `composed/`, recomposed, and kept the delta.

The reviewer found why: when the recorded `comparison-inputs.after` identity does not match the
current identity and replay is false, `resolve()` silently takes the working-tree header and
prices as the "before". So a recompose over a half-written `composed/` reports against itself.

What this ticket owes:

1. The composer's "before" is the last committed artefact, not whatever the working tree holds,
   or a mismatch is refused by name rather than taken silently. Decide which, and record why.
2. A test at the `compose()` seam: two recomposes in a row from a committed artefact produce the
   same deltas as one.

## Done

A recompose is a fixed point from the committed artefact, and a stale working-tree "before" can
no longer hide a delta.

## Build, 2026-09-24

Built on 2026-09-24 with ticket 134, in one platform PR:
[platform#39](https://github.com/policy-as-versioned-platform/platform/pull/39), branch
`ticket-134-observation-is-not-source`, based on platform main 38089a6 (v3.3.0). Ticket 134's
build section has the shared recompose measurement and findings.

### What changed

- `comparison_history.read_committed()` reads `composed/HEADER.yaml` and
  `composed/evidence.json` at HEAD with git.
- `compose()` uses it for a fresh composition in a git work tree. A previous pass's output in
  the working tree is never the "before".
- Verify (`replay_observations=True`) still reads the files on disk, because verify compares
  those bytes.
- A directory that is not a git work tree (test fixtures, scratch copies) keeps the old read.
  A work tree with no commit has committed nothing, which reads as absent. A work tree git
  cannot read refuses by name.

### Decisions

1. The before is the last committed artefact, not a refusal on mismatch. (delegated) A refusal
   would still let a half-written `composed/` decide what a later pass compares against,
   because any pass whose identity matched would take it. Reading HEAD makes every fresh pass
   from the same commit start from the same record, so the answer does not depend on how many
   passes ran or what they left behind. It needs no new flag and no new state.
2. HEAD, not `origin/main`. (delegated) The composer cannot know which remote ref is served, and
   a branch's own earlier commits are part of its history. compose-check recomposes at every
   PR head, so a committed artefact whose identity does not match its own commit already
   shows as drift there. By that reasoning, compose-check would have caught tuppence's
   664967a. This is read from the code, not run.
3. Keep the old read outside git. (delegated) Fixtures and the composition selfcheck compose
   in plain directories and save between passes. There, the files are the only artefact.

### Tests, red first, at the `compose()` seam

In `compose/test_comparison_history.py` `CommittedBefore`, the fixture adopter as a git work
tree with the served artefact committed:

- Red at v3.3.0, green now: a stale working-tree before no longer hides a delta. This is the
  tuppence case: pass one, then another edit, then pass two. At v3.3.0 pass two lost
  `new-ungoverned-namespace`. A half-written `composed/HEADER.yaml` is not read as the before.
  At v3.3.0 that refused.
- Green at v3.3.0 and kept: two recomposes in a row from a committed artefact give the same
  deltas and bytes as one; a committed recompose is the next before.

Measured on the three adopters at origin/main with this branch: pass two was byte-identical
to pass one in each (`diff -rq` on `composed/`).

### What remains

Same route as ticket 134: the platform merge, then the owner's signed tools tag, then three
pin moves, each with one recompose.

## Answer

Resolved 2026-09-24 by platform PR 39, shipped in tools v3.4.0.

1. In a git work tree, a fresh compose reads `composed/HEADER.yaml` and `evidence.json` at HEAD,
   not from the working tree, so a half-written `composed/` can no longer be the "before".
   Verify still reads the files on disk. Outside git, the old read stays, for fixtures.
2. Tests at the `compose()` seam: two recomposes in a row from a committed artefact give the same
   deltas as one, and a stale working-tree "before" no longer hides a delta.
3. **Measured, 2026-09-24.** Each adopter recomposed under v3.4.x from origin/main's committed
   `composed/`, and a second pass was byte-identical. The recompose-and-diff on driftwood
   (2ac5505), tuppence (f1c2619) and ludlow (157701b) exits 0 with no drift.
