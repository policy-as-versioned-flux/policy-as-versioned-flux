# 103 — ico's release gate computes the bump it is about to cut

Type: task (AFK)
Status: open
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
