# Preparatory multi-feed Standards review — 2026-10-04

Read-only review of authentic tools5 `703eff6aee959843c4160aa54fd03413f62858cc` and the three isolated adopter worktrees. These are mutable preparation trees, not approval of their old source-A heads.

## Hard standards

**No cross-commit contradiction in the established route.** `verify-pinned-checkouts.py:37–46` requires the generic feeds checkout HEAD to equal `gotk-sync-feeds.yaml` threat4 commit `974e73514e0d8d4cad2e6906acf51d1cc27028b3`. `read-pins.py:24–27` reads each explicitly supplied pin; it does not collapse distinct feeds into one commit. Keep that checkout and threat4 tag unchanged.

Ludlow `twin/emit-forward-intel.py:275–305` independently checks the FX tag resolves to its declared commit, verifies the publisher identity and Actions issuer with gitsign, then reads `git show 8c84a66951ce89834f33e008380b2c47f054b7c0:fx/v2/feed.json`. This reads an authenticated Git object, not checkout HEAD. Tools5 `compose/composition.py:606–622,674–701,1073–1081,1958–2003` instead reads declared feed parent worktrees and each price's dated converter; `party.yaml` declares no FX edge. Inventing an FX inherits edge, moving generic HEAD, or relabelling threat4 is unnecessary and would violate existing checks.

**Preparatory gap observed:** all generic HEAD guards pass; Driftwood/Tuppence FX1.1 reads pass, but Ludlow's isolated generic feeds object store presently lacks genuine FX2 tag and commit (both reads exit128). Saved negative JSON; cloud was notified. Import the actual signed FX2 tag/object without changing generic HEAD before local producer replay.

Normal composing jobs already use `fetch-depth: 0`, which fetches all branches/tags before checking out the selected ref. The exact pinned [checkout implementation](https://github.com/actions/checkout/blob/11d5960a326750d5838078e36cf38b85af677262/src/git-source-provider.ts#L158) and [refspec helper](https://github.com/actions/checkout/blob/11d5960a326750d5838078e36cf38b85af677262/src/ref-helper.ts#L5) establish this object closure. Preserve generic HEAD verification; separately verify FX tag/commit/signature when consumed.

The scheduled read job runs only the emitter (`twin-sweep.py:85`). A separately named FX checkout at its own exact commit, full tags/history and a hash-pinned gitsign verifier is legitimate there; it must not claim to satisfy the generic composition parent pin. Cloud is fixing that missing runner dependency.

## Smells

No new hard defect beyond the incomplete local object closure and already assigned scheduled-job dependency gap. Exact new source-A review and clean runner replay remain required; no publication or activation claim follows from this audit.
