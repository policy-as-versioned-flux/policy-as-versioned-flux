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

## Build, 2026-09-22

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
`CutReleaseLayout` to `tests/test_platform_tools.py`, the file shift-left already runs.

- driftwood: https://github.com/policy-as-versioned-driftwood/driftwood/pull/41
- tuppence: https://github.com/policy-as-versioned-tuppence/tuppence/pull/38
- ludlow: https://github.com/policy-as-versioned-ludlow/ludlow/pull/35

The edit: the adopter's own checkout gets `path: <adopter>`. The two local `uses:` values gain the
`./<adopter>/` prefix. `adopter-dir` becomes `<adopter>`. The pin reader, the pin check and the
verify take `<adopter>/` paths. The refuse-existing-tag, sign and push steps get
`working-directory: <adopter>`. No step or job is added or removed, and the step order is the same.

Measured:

- The new test class failed 3 of 3 against the old workflow and passes 3 of 3 after, in each adopter.
  The whole `test_platform_tools.py` passes: driftwood 5 run (1 skipped), tuppence 7 run
  (1 skipped), ludlow 5 run (1 skipped). The skip is the existing `PAVF_REAL_ESTATE` class.
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
- Delegated: the layout test lives in `tests/test_platform_tools.py`, because shift-left already
  runs exactly that file.

### What remains

- The integrator merges the three PRs (any order; they are independent) and dispatches
  `cut-release.yml` on each adopter. Done needs those runs to pass the pre-tag verify. No
  workflow was dispatched in this build.
- Risk for the merge: each PR edits a file under `.github/workflows/`. The edit changes two
  `uses:` values (the `./<adopter>/` prefix) but adds or removes no step. If GitHub still refuses
  the merge from the app without `workflows` permission, the owner must merge these three.
- The signed tags the dispatches create are the owner's release act under the standing
  development-mode authorisation. Nothing here creates a tag.
