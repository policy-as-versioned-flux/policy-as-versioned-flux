# ARCHIVE: what the clean-up of 2026-11-14 put away, and how to bring it back

On 2026-11-14 the owner wrote:

> "Clear up and archive all branches worktrees and repos we don't intend to proceed with, we can always bring back"

This file records what was done. One rule held throughout: nothing was deleted until its commit was read back from a ref on GitHub.

## What was done

| What | Count | Where it is now |
|---|---|---|
| Local work that was on no remote | 69 tips | `refs/archive/local/…` on its own repository |
| Remote branches not merged into `main` | 99 | `refs/archive/heads/<branch>` on the same repository |
| Remote branches already merged into `main` | 429 | In `main`'s history. The commit of each is in `evidence/deleted-branches.tsv` |
| Remote branches deleted, in all | 528 | The two rows above. Eighteen more went later the same day: see "After each `main` was replaced" |
| Repositories archived on GitHub | 6 | Read-only, whole, with every branch and tag |
| Local worktrees removed | 454 | 214 dead registrations in the hub copy and 240 in the local clones, of which 114 still had folders |
| Local branches deleted | every one but `main`, in 13 local repositories | Covered by the first three rows |
| Stale pull requests closed | 9 | Each carries a note naming its archive ref |

The 69 local tips were 41 branches, 15 detached checkouts, 1 stash and 12 snapshots of uncommitted changes. Before they were pushed, every one was searched for keys, tokens and credential files. None was found.

## By repository

Seven repositories stay live.

| Repository | Branches deleted | of which archived first | Local-only tips archived | Branches after the clean-up |
|---|---|---|---|---|
| hub | 315 | 74 | 49 | 2 |
| platform | 73 | 21 | 4 | 4 |
| driftwood | 108 | 2 | 3 | 7 |
| ico | 10 | 0 | 0 | 3 |
| feeds | 20 | 2 | 2 | 9 |
| driftwood/api | 1 | 0 | 1 | 4 |
| driftwood/storefront | 1 | 0 | 1 | 11 |

Six repositories were archived on GitHub: tuppence, tuppence/ledger, ludlow, ludlow/reports, nist and insurer. Their branches were left as they were; an archived repository keeps everything. Nine local-only tips were pushed to them first (tuppence 4, ludlow 3, ledger 1, reports 1). Their scheduled jobs no longer run. The live repositories still read their signed tags, which an archive does not stop.

## Branches that were kept, and why

A branch stayed if running automation looks it up by name, or if a bot's open pull request hangs from it.

- **`observations`** in platform, ico and feeds: the fetch clocks write their readings to it.
- **`fetch/*`** in feeds: the fetch clock treats an existing branch as "a proposal is already open".
- **`release/2.0.x`** in platform: a protected maintenance branch.
- **`renovate/*`** everywhere: Renovate does not raise an update again once its pull request is closed.
- **`wargamer/*`** and one `observations/drift-sample/…` branch in driftwood: heads of open bot pull requests.
- **`distil/record-2026-11-14`** in the hub: the branch that carried this record (gone since pull request 317 merged; its commit is in `main`).

Later the same day every one of these in platform, driftwood, ico and feeds was archived as well, before the old chain left `main`. See "Before the old chain left `main`" below.

## Pull requests closed

Nine ticket pull requests of 2026-09-26 closed when their branches went. Each has a note with its archive ref.

| Repository | Pull requests |
|---|---|
| hub | 142, 143, 150, 152 |
| platform | 46, 48 |
| driftwood | 49, 52 |
| feeds | 9 |

The 61 open pull requests raised by bots were left alone. Four more ticket pull requests of the owner's stay open inside the archived tuppence and ludlow.

## How to bring something back

```sh
# See everything that was archived in a repository
git ls-remote origin 'refs/archive/*'

# A remote branch that was not merged
git fetch origin refs/archive/heads/<branch>:refs/heads/<branch>

# Work that was only on the owner's machine
git fetch origin refs/archive/local/heads/<branch>:refs/heads/<branch>
git fetch origin 'refs/archive/local/*:refs/archive/local/*'   # all of it: detached, wip, stash

# A branch that had been merged: its commit is in evidence/deleted-branches.tsv
git branch <branch> <commit>

# A repository
gh repo unarchive <organisation>/<repository>
```

To reopen a closed pull request, bring its branch back, push it, and press Reopen.

A removed worktree is rebuilt with `git worktree add <path> <ref>`. `evidence/local-manifest.json` maps every old worktree path to its commit. The files of the hub's old worktrees are on the owner's backup disk; the local folders were empty shells and were removed.

## Index files

- `evidence/archive-refs.tsv`: all 187 archive refs of branches and local-only work, with repository, commit and what each is. The five before-simplify refs are in the table below.
- `evidence/deleted-branches.tsv`: all 546 deleted branches, with the commit and where it is kept.
- `evidence/local-manifest.json`: every local worktree and tip in the 13 local repositories, taken before anything was removed.

## The simplification that followed

Later on 2026-11-14 the owner wrote: "Remove all redundant code. Simplify everything". Before any file left a `main`, each of the five core repositories got a ref at its `main` as it stood:

`refs/archive/main/2026-11-14-before-simplify`

| Repository | Commit |
|---|---|
| hub | `ec43f2a60cb0` |
| platform | `7beb1266cd35` |
| driftwood | `34ef5a5bc6f1` |
| ico | `9d584cf0f177` |
| feeds | `838abe583f14` |

Every `repo/path:line` citation in this folder resolves against that ref, except those that start `backup/`, which point at the owner's backup disk. To read a file that has left `main`:

```sh
git fetch origin refs/archive/main/2026-11-14-before-simplify
git show FETCH_HEAD:<path>
```

To put a file or folder back, check it out from that ref and commit it.

### Before the old chain left `main`

Two things were done in platform, driftwood, ico and feeds before any pull request replaced a `main`.

**The old scheduled jobs were switched off**, so that no clock wrote again while the trees changed:

| Repository | Workflow files switched off |
|---|---|
| platform | `fetch.yml` |
| ico | `fetch.yml` |
| feeds | `fetch.yml` |
| driftwood | `drift-sample.yml`, `propose-tier.yml`, `renovate-run.yml`, `twin-sweep.yml` |

No other workflow was switched off. `cut-release.yml` was left on in each repository, as it runs only by dispatch. The new design keeps a file at that path in platform, ico and feeds.

**The tip of every branch but `main` was pushed to `refs/archive/heads/<branch>`** and read back: 19 branches (platform 3, driftwood 6, ico 2, feeds 8). These are the branches the clean-up had kept because the old automation looked them up by name. The `observations` branches hold the fetch clocks' readings, which are on no other ref. Each of the 19 has a row in `evidence/archive-refs.tsv`.

To bring a schedule back, put its workflow file back on `main` from the before-simplify ref, then:

```sh
gh workflow enable <file> -R <organisation>/<repository>
```

### What left each `main`

Each `main` was replaced by pull request, merged by the app. Everything that left is at that repository's before-simplify ref.

| Repository | Files that left | Files that remain | Pull request |
|---|---|---|---|
| hub | 4,905 | 142 | 319, then 320 for the records |
| platform | 693 | 20 | 75 |
| driftwood | 224 | 12 | 132 |
| ico | 31 | 7 | 12 |
| feeds | 91 | 6 | 21 |

### After each `main` was replaced

The branches the old automation used had no reader left. Eighteen were deleted, each only after its tip was checked against its archive ref: platform 2, driftwood 6, ico 2, feeds 8. They are in `evidence/deleted-branches.tsv`. Platform's `release/2.0.x` is archived and stays, because the ruleset forbids deleting it.

Eight pull requests raised by bots closed with them, each with a note naming its archive ref: platform 1; ico 1; driftwood 50, 71, 101, 106, 115 and 129.

Three new tags were cut, each by its repository's own signing workflow, at the commit the new loop had already run against: ico `v5.0.0`, feeds `threat-register/v5.0.0`, platform `policy/v8.0.0`. No old tag was touched.

What remains besides `main`: platform's `release/2.0.x`, and driftwood's `ledger`, which holds the loop's record. The loop makes the branch `loop/rung` or `loop/pins` fresh for each proposal and deletes it on its next run.

## What was not touched

- **Content on `main`** in any repository, by the clean-up itself. The simplification above came after it.
- **Tags.** The clean-up added, moved and removed none. The archive refs are not tags, so no tool that lists tags or branches sees them and no workflow starts because of them. The simplification later cut three new tags, listed above.
- **The hub working copy's files**, including the files moved to the backup disk. Its local `main` is still behind the remote.
- **Scratch files that git ignores** in two local clones (ludlow, 62 MB; nist, 6 MB). They are in no repository and were left in place.
- **The older repositories** in the hub's organisation, which were archived before this, and the 2022 reference organisations.
