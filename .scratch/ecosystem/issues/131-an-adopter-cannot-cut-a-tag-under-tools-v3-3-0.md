# 131 — An adopter cannot cut a tag under tools v3.3.0

Type: task
Status: open
Blocked by: none

## Question

Charted 2026-09-24 by the integrator. It blocks every adopter tag of the v3.3.0 rollout.

driftwood's `cut-release.yml` run 35975270740 (2026-09-24, version v2.0.0, main at 2fff19d)
refused before it created a tag:

```
MISMATCH: re-composition refused: ['comparison history does not match current source inputs'] []
```

The reviewed branch and main have identical trees (`git diff --stat` is empty), so no lane
commit caused it. The cause is the layout. `cut-release.yml` checks out platform, nist, ico,
feeds, insurer and the platform tools INSIDE the adopter's own checkout (`path: platform`,
`path: nist`, and so on) and runs `platform-tools.py ... verify . --estate-clone .`. The
comparison identity that platform tools v3.2.0 added hashes every non-hidden source file outside
`composed/`, so it hashes those parent checkouts too. `compose-check` in `shift-left.yml` puts the
adopter in a subdirectory beside its parents, and there the identity matches. No adopter has cut
a tag with tools newer than v3.0.0 before, so this never showed.

What this ticket owes:

1. Reproduce the refusal offline with the nested layout, and the pass with the sibling layout.
2. Each adopter's `cut-release.yml` (driftwood, tuppence, ludlow) uses the sibling layout that
   `compose-check` uses, so the pre-tag verify reads the same source inputs the composition did.
3. Decide whether the composer's identity should also refuse to hash a nested git checkout, and
   record why. If yes, that is a platform change for a later tools release, not this ticket.

## Done

A dispatched `cut-release.yml` on each adopter passes its pre-tag verify on the v3.3.0 rollout.

## Build, 2026-09-24

### 1. Reproduced offline

A scratch script cloned each adopter at origin/main from GitHub (driftwood 2fff19d, tuppence
9333d86, ludlow f70abce). It laid out every parent at the tag the adopter pins, and
platform-tools at v3.3.0 (38089a6), in two layouts. Then it ran the pre-tag verify.

| adopter | nested (cut-release.yml today) | sibling (compose-check) |
|---|---|---|
| driftwood | exit 1, `MISMATCH: re-composition refused: ['comparison history does not match current source inputs']` | exit 0, `OK: composed artefact re-renders byte-for-byte from the recorded parent SHAs` |
| tuppence | exit 1, same MISMATCH | exit 0, same OK |
| ludlow | exit 1, same MISMATCH | exit 0, same OK |

Nested ran `python3 .github/scripts/platform-tools.py --tools-dir platform-tools verify . --estate-clone .`
from inside the adopter. Sibling ran `python3 <a>/.github/scripts/platform-tools.py --adopter-dir <a>
--tools-dir platform-tools verify <a> --estate-clone .` from the workspace. The cause sits in
platform-tools `compose/comparison_history.py` `identity()`. It hashes every file under the
adopter except hidden parts, `__pycache__` and `composed/`. So the nested `platform/`, `nist/`,
`ico/`, `feeds/`, `insurer/` and `platform-tools/` trees all enter the identity.

### 2. cut-release.yml uses the sibling layout

One PR per adopter. Each changes `.github/workflows/cut-release.yml` and adds a test class
`CutReleaseLayout` in `.github/tests/test_cut_release_layout.py`. shift-left runs that file after
`tests/test_platform_tools.py`. The first push put the class in `tests/`; the review round below
says why it moved.

- driftwood: https://github.com/policy-as-versioned-driftwood/driftwood/pull/41
- tuppence: https://github.com/policy-as-versioned-tuppence/tuppence/pull/38
- ludlow: https://github.com/policy-as-versioned-ludlow/ludlow/pull/35

The edit: the adopter's own checkout gets `path: <adopter>`. The two local `uses:` values gain the
`./<adopter>/` prefix. `adopter-dir` becomes `<adopter>`. The pin reader, the pin check and the
verify take `<adopter>/` paths. The refuse-existing-tag, sign and push steps get
`working-directory: <adopter>`. No step or job is added or removed, and the step order is the same.

Measured at the PR heads (driftwood 96f40bf, tuppence 28999e1, ludlow c758f22), fetched into
the sibling scratch workspace with every parent at its pinned tag:

- The layout tests failed 3 of 3 against origin/main's `cut-release.yml` (driftwood, measured by
  swapping in that file) and pass after, in each adopter. `.github/tests` runs 4 tests OK in each.
  `tests/test_platform_tools.py`, now identical to main, passes 5 (driftwood), 7 (tuppence) and
  5 (ludlow) with 1 skipped, and passes in full with `PAVF_REAL_ESTATE` set to the workspace.
- Every `run:` step of each edited workflow, except sign and push, ran in the sibling scratch
  workspace and exited 0. That covers the tools check, pin reading, `verify-pinned-checkouts.py`,
  the verify and the tag guard. The tag guard ran in `<adopter>/` at the adopter's HEAD.
- The tag guard refused an existing tag (v1.1.0) from inside `<adopter>/`. From the workspace root,
  `git rev-parse refs/tags/v1.1.0` fails because the root is not a repository, so the guard would
  pass silently. `working-directory` is load-bearing, and the test pins it.

### 3. Should the identity refuse a nested git checkout?

Decision (delegated): yes. A later tools release should make `identity()` refuse, by name, when
it meets a directory holding `.git` under the adopter. It should not skip such a directory
silently. Reasons:

- Today the failure reads "comparison history does not match current source inputs". That
  points at the history, not at the layout. It cost a failed release run to find the cause.
- Skipping nested checkouts would hide which bytes count as source. A vendored tree that is
  meant to count would drop out without a word. A named refusal keeps the identity what it
  claims to be and tells the operator the fix.
- Composition and verify must see the same inputs. A refusal makes a mixed layout fail in both
  places, with the same message.

This is a platform change for a later tools release. It is not charted here. The integrator
charts it with the next free ticket number.

### Decisions

- Delegated: sibling layout with the adopter at `<adopter>/`, copied from compose-check, rather
  than hiding the parents under a dot directory. The dot-directory route would also pass the
  identity, but `platform-tools/` is fixed by the shared composite action, and it would give
  cut-release a third layout no other job uses.
- Delegated: the verify runs from the workspace root, as compose-check does. The tag steps run in
  `<adopter>/` so the tag is created on the adopter's own HEAD.
- Delegated (revised in the review round): the layout test lives in
  `.github/tests/test_cut_release_layout.py`, not `tests/`. `identity()` skips hidden paths, so a
  test of a workflow can change without changing the adopter's source identity. The alternative
  was to recompose in each PR. That would start a new comparison for a test-only edit and meet
  ticket 133's first-pass fixed-point defect. shift-left gains one line to run the new directory.

### Review round

Blocking: the first push added `CutReleaseLayout` to `tests/test_platform_tools.py`. That file is
non-hidden source, so `identity()` hashed it and the recorded comparison history no longer
matched. At the first PR heads (ebca1d7, dab8f59, 8658ef8) the sibling-layout verify printed
`MISMATCH: re-composition refused: ['comparison history does not match current source inputs']`
in all three adopters, and `RealCompilerLayout` failed with `PAVF_REAL_ESTATE` set. I reproduced
both. The first build measured origin/main, not the PR tree.
Fix: the class moved to `.github/tests/test_cut_release_layout.py`, and
`tests/test_platform_tools.py` is back to main byte for byte. A new test in the class asserts the
module sits under a hidden path. shift-left's compose-check step runs `.github/tests` too. At the
new heads the verify prints `OK: composed artefact re-renders byte-for-byte from the recorded
parent SHAs`, exit 0, in all three, and `RealCompilerLayout` passes.

Minor: the heading said 2026-09-22. `gh pr view --json createdAt` gives 2026-09-24 for all three
PRs, so the heading now says 2026-09-24.

Minor: the Measured paragraph did not name the commit it measured. It now names the PR heads, and
every figure in it was re-run at those heads.

### What remains

- The integrator merges the three PRs (any order; they are independent) and dispatches
  `cut-release.yml` on each adopter. Done needs those runs to pass the pre-tag verify. No
  workflow was dispatched in this build.
- Risk for the merge: each PR edits two files under `.github/workflows/`. The `cut-release.yml`
  edit changes two `uses:` values (the `./<adopter>/` prefix) but adds or removes no step. The
  `shift-left.yml` edit adds one test command to an existing step. If GitHub still refuses
  the merge from the app without `workflows` permission, the owner must merge these three.
- The signed tags the dispatches create are the owner's release act under the standing
  development-mode authorisation. Nothing here creates a tag.
