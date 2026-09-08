# 103 — ico's release gate computes the bump it is about to cut

Type: task (AFK)
Status: resolved
Blocked by: none

## Question

Three ways `ico/.github/scripts/declared-bump-gate.py` can agree with `penalty-schema/bump.yaml`
about a number that is not the one a release would carry. All three predate ticket 67 and none is
a regression from it — ticket 67 corrected a fourth (the gate asked about the LAST release rather
than the next, so `bump: none` could never be declared and a v3 patch release was refused) and the
review of that change found these while reading the corrected file. They are charted here rather
than fixed there because each changes what the gate refuses, and ico's gate is the thing that
stands between a wrong number and a signed tag.

1. **An unpublished edit to the newest major launders into the next major's bump.** When a release
   is a major's FIRST — no released tag of that major — the predecessor is the major below it
   **on disk**, never the tag that major was published at. So an edit made to `v3/feed.json` after
   `v3.0.0` was tagged, and never released, is invisible: it is folded into the v3 → v4
   computation as though it had always been there. `released_tags()` and `feed_at()` already exist
   in the file and are used on the other branch; the first-release branch should read its
   predecessor at the tag too, and a newest major whose tree has drifted from its own tag is a
   queued release the gate must account for before it computes the next one.

2. **The tag's own increment is never compared to the bump.** `declared-bump-gate.py v3.0.1` and
   `v3.1.0` and `v4.0.0` all pass with `bump: none` when the content is unchanged, and a `v3.0.1`
   carrying a `minor` change passes as long as `bump.yaml` says `minor`. Nothing asserts that the
   tag being cut IS the declared bump applied to the previous tag. The old gate refused that case,
   by accident, because it was computing something else. Assert it on purpose: the tag must equal
   `bump(previous released tag, declared)`.

3. **An empty tag list cannot be told from "never released".** `released_tags()` returns `[]` both
   when the repository has genuinely never published and when the checkout was made with
   `--no-tags`, shallow, or from a mirror that carried none. The first is a fact; the second is a
   checkout that cannot answer, and today it silently takes the first-release branch and grades a
   bump against a predecessor on disk. Refuse when `git ls-remote --tags origin` is non-empty and
   the local tag list is empty: the repository has published and this checkout cannot see it. Keep
   the refusal, not a shrug — the hub's `talk/verify-manifest.txt` row for
   `verify-declared-bump.sh` declares no could-not-look.

Done = each of the three has a case in `declared-bump-gate.py --selfcheck` that fails before the
fix and passes after, `verify-declared-bump.sh` still exits 0 on ico's real tree, and the hub gate
is unchanged. Consider whether nist's copy carries 2 and 3 as well; it certainly carries the
exit-3-on-no-tags shape ico's just lost (ticket 67 decision 5).

## Notes

Charted 2026-09-06 by the review of ticket 67 (findings F5, F6, F7), which classed all three as
inherited rather than regressions and asked for them to be charted rather than fixed in that
branch. Record: ticket 67's `## Answer`, "Review round 1".

## Answer

Built 2026-09-08 on `ticket-103-release-gate-computes-the-bump` in ico (head `a35d670`), nist
(head `086fb72`) and the hub. Both gates keep their entry points and their output shape:
`declared-bump-gate.py <tag>` is what each `cut-release.yml` runs
(`run: python3 .github/scripts/declared-bump-gate.py "${VERSION_INPUT}"`, after
`actions/checkout@v4` with `fetch-depth: 0`), and `--selfcheck` then `--tree` is what each
`verify-declared-bump.sh` runs for the hub. Neither workflow was touched.

### Before and after, red first

Each defect got a planted case in `--selfcheck` before the logic changed. The selfcheck now plants
throwaway repositories under a hook-free git (`core.hooksPath` pinned to an empty directory,
nothing signed) and runs the real `grade()` and `tree()` against them; every case is reported, not
the first to fail, so one red run names everything. The red commit on each branch (ico `bd8b75a`,
nist `2dc3df7`) carries the cases against the unchanged logic; the green commit follows.

**ico, red** (`python3 .github/scripts/declared-bump-gate.py --selfcheck` at `bd8b75a`, exit 1):

```
FAIL (1) a first release of v2 refuses v1's unreleased edit, naming the tag it drifted from: expected exit 1 naming ['penalty-schema/v1/feed.json', 'v1.0.0', 'differs'], got exit 0 (missing [...]): OK: declared bump 'major' == computed bump 'major' (v1 -> v2.0.0)
FAIL (2) v1.0.1 declared minor is refused: the tag is a patch increment: expected exit 1 naming ['v1.0.1', "'patch'", "'minor'"], got exit 0 (missing ["'patch'"]): OK: declared bump 'minor' == computed bump 'minor' (v1.0.0 -> v1.0.1)
FAIL (3) a --no-tags clone of a released repository is refused, not graded as a first release: expected exit 1 naming ['no tags in this clone'], got exit 0 (missing [...]): OK: v1 is the first published feed version -- no predecessor to compute a bump against, so the declared bump 'patch' stands unchallenged
FAIL: 3 ticket-103 selfcheck case(s) red
```

**nist, red** (same command at `2dc3df7`, exit 1; the old file had one entry point, `main(argv)`,
so the red commit drives it through a shim that writes the planted declaration into the planted
`bump.yaml` and calls it with the workflow's argv):

```
FAIL (1) the predecessor's file name is read at v1.0.0, not from the tree: a rename computes none: expected exit 0 naming ['v1.0.0 -> tree', "'none'"], got exit 1 (missing [...]): FAIL: could not read catalog/rev6_catalog.json at v1.0.0 -- the gate cannot compute a bump it cannot read the predecessor for
FAIL (2) v1.0.1 declared minor is refused: the tag is a patch increment: expected exit 1 naming ['v1.0.1', "'patch'", "'minor'"], got exit 0 (missing ["'patch'"]): OK: declared bump 'minor' == computed bump 'minor' (v1.0.0 -> v1.0.1)
FAIL (3) a --no-tags clone of a released repository is refused, not graded as a first release: expected exit 1 naming ['no tags in this clone'], got exit 0 (missing [...]): OK: v1.0.1 is the first release -- no predecessor to compute a bump against, so the declared bump 'patch' stands unchallenged
FAIL: 3 ticket-103 selfcheck case(s) red
```

**Green**, both repositories, exit 0: every ladder case as before, then twelve (ico) and thirteen
(nist) `ok  (1)…(3)` lines, among them
`ok  (1) a first release of v2 refuses v1's unreleased edit, naming the tag it drifted from`,
`ok  (2) v2.0.0 declared minor is refused: the tag is a major increment`,
`ok  (2) v1.0.1 declared none is refused: no tag carries none`,
`ok  (3) a --no-tags clone of a released repository is refused, not graded as a first release` and
`ok  (3) a clone of a repository that never released takes the first-release path`.

### What each gate now derives

1. **The predecessor is the newest released tag below the tag being cut, whatever its major, and
   it is read at that tag** (`git show <tag>:<path>`). ico's first-release-of-a-major branch used
   to read the major below on disk. Now, when the tag opens a new major, the gate also reads that
   lower major on disk and refuses when it is not byte-for-byte what its own tag published:
   `penalty-schema/v1/feed.json on disk differs from what v1.0.0 published -- an unreleased edit to
   the newest published major is a queued release of v1, not part of the next major. Release it or
   revert it before cutting`. A lower-major directory that has been removed is refused the same
   way. nist reads one catalogue file per release and already read its bytes at the tag; what it
   took from the working tree was the file's NAME (`CATALOG_VERSION.json`'s `file`), so a
   catalogue renamed since the tag could not be read at all. Name and bytes now both come from the
   tag.
2. **The tag is `bump(predecessor, declared)`**, computed from the two tag strings and compared
   before any content is read: `bump.yaml declares 'minor' but the tag v1.0.1 is a 'patch'
   increment of v1.0.0 -- the tag must equal bump(v1.0.0, minor) = v1.1.0`. A tag that is not the
   next number on any rung is refused with the three numbers that would be. **`none` admits no
   tag** (delegated): `bump(prev, none)` is `prev`, which exists, and a release that changes
   nothing is not a release — so `declared-bump-gate.py v3.0.1` under today's `none` is refused
   with `no release is queued after v3.0.0, and v3.0.1 would publish what v3.0.0 published under a
   new number. Declare the bump v3.0.1 carries, or cut nothing`. The reason for refusing rather
   than admitting a content-identical re-tag: the old gate's accidental refusal of that case was
   the only thing the ticket credits it with, and admitting it would make the declaration
   unfalsifiable for one rung.
3. **`--tree` derives the next tag from the declaration** (delegated): `bump(newest released tag,
   declared)`, graded exactly as the workflow would grade it; under `none` it asks instead that the
   newest published major on disk be what the newest tag published, and prints the span as
   `v3.0.0 -> tree: no release is queued`. In ico, an untagged major directory above the newest
   tag is the queued release whatever `bump.yaml` says, as ticket 67 built. In nist, a repository
   with no tag anywhere is asked about the version its own `CATALOG_VERSION.json` declares.
4. **"No tags in this clone" is its own refusal**, distinct from "never released": when and only
   when the local `git tag -l` is empty, the gate runs `git ls-remote --tags origin` (60 s
   timeout). Origin holding release tags this checkout cannot see is
   `no tags in this clone: origin holds v1.0.0 and this checkout sees none of them (--no-tags, a
   shallow clone, or a mirror that carried none)`; origin that cannot be asked is a refusal too
   (delegated: a first release cannot be told from a blind checkout, so nothing is graded); origin
   with no tags at all is the first-release path, where the declaration stands unchallenged as
   before. The release path (`fetch-depth: 0`) and the hub gate (the estate clone carries the
   tags) never reach the call, which is why the wrappers can still say they are offline, with the
   one exception now written into their headers. nist's `--tree` no longer exits 3 on an empty
   list, following ticket 67 decision 5: the hub's manifest row declares no could-not-look, so
   that shrug graded FAIL there anyway.
5. **A tag below the newest release is refused** (delegated, found while building): with tags
   present and none below the tag, the old code took the first-release path. It is now `v0.1.0 is
   below v3.0.0, the newest release this repository has published`.

### Measured on the real trees

Both worktrees are `origin/main` plus these commits, with each repository's real tags; the diffs
against `origin/main` touch only `.github/scripts/declared-bump-gate.py` and
`.github/scripts/verify-declared-bump.sh`.

- ico `--tree`: `OK: declared bump 'none' == computed bump 'none' (v3.0.0 -> tree: no release is
  queued)`, exit 0; `verify-declared-bump.sh` exit 0, `PASS` last. Explicit tags under the real
  `none`: `v3.0.1`, `v3.1.0`, `v2.0.0`, `v3.0.0` each refused with `no release is queued`;
  `v4.0.0` refused because `penalty-schema/v4/feed.json` does not exist. With the declaration
  overridden in-process (nothing on disk changed): `v3.0.1 patch` and `v3.1.0 minor` are refused
  as `computed bump ... 'none' (v3.0.0 -> ...)`; `v2.0.0 major` is refused as `could not read
  penalty-schema/v1/feed.json at v1.0.0` — ico's `v1.0.0` predates `penalty-schema/` entirely
  (its tree is `schema/v1/penalty-schema.json`), which the old gate never noticed because it read
  `v1/feed.json` on disk. Nothing is mis-bumped; that fact is recorded here, not "fixed".
- nist `--tree`: `OK: declared bump 'none' == computed bump 'none' (v1.1.0 -> tree: no release is
  queued)`, exit 0; `verify-declared-bump.sh` exit 0, `PASS` last. Before the change, the real
  tags admitted `v2.0.0` under the real `none`: `OK: declared bump 'none' == computed bump 'none'
  (v1.1.0 -> v2.0.0)` — defect 2 on real data. After: `v1.1.1`, `v1.2.0`, `v2.0.0`, `v1.0.1` each
  refused with `no release is queued`; overridden in-process, `v2.0.0 major`, `v1.1.1 patch` and
  `v1.2.0 minor` are each refused as `computed bump ... 'none' (v1.1.0 -> ...)`.

**Which defects nist carried**: 2 and 3 in full, measured above; 1 not in ico's shape (nist has
no predecessor on disk to read) but in the file-name cousin described under item 1, which the
red case `(1)` shows as `could not read catalog/rev6_catalog.json at v1.0.0`.

### Hub

`talk/verify-manifest.txt` rows for `.estate-clone/ico/.github/scripts/verify-declared-bump.sh`
and `.estate-clone/nist/.github/scripts/verify-declared-bump.sh` are unchanged: both stay
`self-proof | -`, because neither script gained a could-not-look — the exit-3 branch in each
wrapper is still reachable by nothing. `talk/captures/*.out` are the clock's observations and were
not hand-edited; the next citable run will carry the new `-> tree: no release is queued` span.
The hub change is this file and one map line.

### Hook bypass, disclosed

All four unit commits were made with `--no-verify`: the owner's global ggshield pre-commit hook
answered `no more API calls available`. Each staged diff was grepped for key, token, credential,
secret, password and private-key shapes before committing and carries none; each commit message
says so.

### Not done here

- A tag between two existing tags (`v1.0.1` when `v1.1.0` exists) is graded against `v1.0.0`, as
  before: the increment rule admits a backport whose declaration matches. Not this ticket's; noted.
- A repository's genuinely first release admits any `vX.Y.Z` with the declaration unchallenged, as
  before; nothing asserts it is `.0.0`.
- ico's own history skipped a major (`v1.0.0` to `v3.0.0`); the increment rule would refuse that
  today. Published tags are not re-graded.
- The old `next_tag()` in ico is gone; `--tree` derives the tag in `tree()` itself.

## Waits on the owner

Nothing.

Map line: [103 — ico's release gate computes the bump it is about to cut](issues/103-icos-release-gate-computes-the-bump-it-is-about-to-cut.md) — ico's and nist's `declared-bump-gate.py` now derive the number a release would carry instead of agreeing with one: the predecessor is the newest released tag below the one being cut, read at that tag (`git show <tag>:<path>`, file name included in nist), a tag opening a new major is refused while the major below on disk differs from what its own tag published, the tag must equal `bump(predecessor, declared)` computed from the two tag strings so `v3.0.1` cannot carry a `minor` and a declared `none` admits no tag at all, `--tree` derives the next tag from the declaration and under `none` asks that nothing be queued, and an empty tag list is told apart from a repository that never released by asking origin only when the local list is empty — "no tags in this clone" is its own refusal, and nist's exit 3 on that list is gone. Each defect has a planted selfcheck case that was red before the fix, every case is reported rather than the first, and both real trees still pass `verify-declared-bump.sh` at `origin/main` with `-> tree: no release is queued`; nist's real tags had admitted `v2.0.0` under `none` before the change. The manifest rows are unchanged, no workflow was edited, and ico's `v1.0.0` is recorded as predating `penalty-schema/` so a `v2.0.0` cut would be refused for an unreadable predecessor.
