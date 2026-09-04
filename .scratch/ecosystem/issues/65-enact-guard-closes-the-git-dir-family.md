# 65 — enact_guard closes the --git-dir family

Type: task (AFK)
Status: resolved
Blocked by: none

## Question

git --git-dir=<enactment>/.git push origin main resolves the remote against the caller's cwd, matches the self-push carve-out, and is ADMITTED — the same cwd-dependent class as the fixed -C hole. Extend _effective_cwd to --git-dir and --git-dir= (and --work-tree), scrub or handle GIT_DIR from the environment at the guard boundary, and ship tests that fail against current behaviour, mirroring the four tests the -C fix landed. Done = the probe shapes REFUSE and the tests run in the gate.

## Notes

Charted by the ambition review of 2026-08-31. Closes review findings: M17 (enact_guard --git-dir bypass).
Record: [REVIEW-2026-08-31.md](../REVIEW-2026-08-31.md).

## Answer

**2026-09-03, built (wave 1 of the everything-open build).** Hub only; branch
`ticket-65-enact-guard-closes-the-git-dir-family`, two commits: `c1505e0` (the guard, alone, per
the build brief) and `e124b9c` (the tests).

What was built. `twin/enact_guard.py` gains `_Locus(cwd, git_dir, work_tree)` and
`_effective_locus(command, cwd)`: `_effective_cwd` still does `-C` and a leading `cd`, and the
locus adds `--git-dir=<d>`, `--git-dir <d>`, `--work-tree=<d>`/`--work-tree <d>`, and an inline
`GIT_DIR=<d>`/`GIT_WORK_TREE=<d>` prefix (bare, via `env`, or `export ...;`). `_remote_url` now
takes a locus and hands git the same options, in the directory `-C`/`cd` moved to, with
`GIT_DIR` and `GIT_WORK_TREE` scrubbed from the subprocess environment. `_own_repository` resolves
through the same scrubbed path. Six tests in `tests/test_enact.py` beside the four `-C` tests;
five were red against `main` (the absent-dir one is the property test its `-C` twin is).

Which check grades it. The hub's pytest gate, `.github/workflows/twin.yml` (paths `twin/**`,
`tests/**`), which already runs `tests/test_enact.py`; no `verify-*.sh` runs pytest, and
`talk/verify-all.sh` discovers only `verify*.sh`, so there is nothing new to land in the estate
gate. Verified locally: `.venv/bin/python -m pytest tests/test_enact.py -n0 -q` → 49 passed;
`mypy twin/enact_guard.py` → clean; the hook end-to-end (`python twin/enact_guard.py` on a
PreToolUse payload) denies `git --git-dir=<enactment>/.git push origin main` and
`GIT_DIR=<enactment>/.git git push origin main` from the hub's own directory, and still admits
`git push -u origin <branch>` there; `tests/test_netflix_beat.py -k propose_only` (the harness
invariant `enactment_is_propose_only_at_both_layers`) → 1 passed.

Decisions, all **delegated (ADR-0025)**:

1. *Hand git the parsed options rather than re-implement discovery.* The four `-C` tests fixed
   the resolution DIRECTORY; this family names the git dir and work tree, and git's own rules for
   them (observed with git 2.55 on 2026-09-03: `--work-tree` alone does not move discovery, an
   absent `--git-dir` is fatal, a relative `--git-dir` after `-C` is relative to the `-C` dir)
   are the thing a re-implementation would get wrong. So `_remote_url` runs
   `git [--git-dir D] [--work-tree W] remote get-url --push <remote>` in the effective cwd, and
   the guard resolves exactly what the push would, including the cases git refuses.
2. *`GIT_DIR` in the hook process's environment is scrubbed, not honoured.* **Corrected
   2026-09-04, below: the premise was wrong.** The hook's env is not the shell's env, so
   honouring it asserts nothing about the push; and unscrubbed it reached both resolutions,
   which is worse than the ticket's finding: a `GIT_DIR` pointing at a checkout of this
   repository made every bare push in every enactment checkout read as a self-push, and one
   pointing at an enactment checkout made that checkout "our own". Scrubbed set is `GIT_DIR`,
   `GIT_WORK_TREE`; `GIT_COMMON_DIR` and `GIT_CONFIG_*` are not scrubbed (not named by the
   finding, and the net is stated as a net).
3. *An inline `GIT_DIR=<d> git push` prefix is parsed as a directory move, not refused as
   unparseable.* It is the same class as `-C`: a shape with a known meaning. Refusing it outright
   would be a count-and-deny the brief forbids, and would refuse the hub's own pushes spelt that
   way.
4. *`--work-tree` alone is passed through and does not move the resolution.* That is what git
   does (observed, above). It is therefore not a bypass on its own: the push it names also
   resolves from the cwd, which `-C`/`cd` already cover. Tested paired with `--git-dir`, which is
   the shape git documents for a detached work tree.
5. *No harness probe shape.* The ticket's gate is satisfied by pytest in `twin.yml`; the
   invariant at `harness.py` ~3530 tests merges with no cwd and would need a real enactment
   checkout to probe a push, and ticket 44 edits that file this wave. Kept to pytest, harness
   untouched.

Not done. No verify script (nothing in the estate gate observes this; the hub workflow does). The
harness comment at `harness.py` ~3523 still says the checked-in default is `development`; stale
since 2026-08-29, not this ticket's file to touch this wave.

**2026-09-04, review fixes (two reviews of 2026-09-03, both `request_changes`).** One guard
commit, alone: `2549e7d`. Six more tests in `tests/test_enact.py`, red against the first cut
(6 failed, 49 passed) and green after (55 passed); `mypy twin/enact_guard.py` clean; the harness
invariant `enactment_is_propose_only_at_both_layers` still passes; nineteen hook end-to-end
probes through `python twin/enact_guard.py` give the expected verdict, including the reviewers'
exact shapes.

Blocking 1, *the locus was read from the whole command string.* `git --git-dir=<hub>/.git
log; git push origin main` made in an enactment checkout resolved the hub's origin and was
ADMITTED (so were the `GIT_DIR=` prefix and an `echo GIT_DIR=...` in another segment; `main`
denied all three). `_effective_locus` now splits on `_SHELL_SEGMENT`, as
`_merge_is_made_as_the_other_hand` does, and reads the option, the prefix, `-C` and `-c` from
the segment holding the `push` only. From the segments before it, only what the shell carries
forward: a `cd` (folded in order, each relative to the last) and `export GIT_*=...`. A `cd`
after the push no longer counts, and a bare `GIT_DIR=x;` in an earlier segment is not carried:
it is a shell variable, not an exported one, and carrying it would resolve where the push does
not go. The same edit closes the pre-existing `-C`-in-another-segment ceiling (minor).

Blocking 2, *`GIT_DIR=~/<enactment>/.git git push origin main` was admitted.* zsh and bash
expand the tilde in an assignment prefix; the guard handed git the literal `~/...`, git said
fatal, the resolution was empty, and an empty resolution admits. Segments are now split with
`shlex` and every directory word is passed through `os.path.expanduser`, so the guard resolves
what the shell would. Stated limit, chosen on purpose: the tilde is expanded after the quotes
are gone and in `--git-dir=~/x` too, both of which the shell would NOT expand; each mismatch
points toward refusing a push that would have failed, the safe direction, since the open door
is the empty resolution and not the spurious one.

Decision 2 **corrected, delegated (ADR-0025).** Its premise, "the hook's env is not the
shell's", does not hold for Claude Code: the hook and the Bash tool inherit the same process
environment, so a `GIT_DIR` the hook sees is one the push sees. Scrubbing it and stopping
there read the hub's own origin from the hub, called it a self-push, and admitted a push git
made to the enactment repository (pre-existing on `main` via the own-repository leg, but the
Answer had claimed the opposite). Now: the target is read once with the hook's `GIT_DIR`/
`GIT_WORK_TREE` scrubbed and the command's own prefix applied, and a second time with them
honoured when the command names neither; either reading naming an enactment repository is a
refusal. The own-repository reading stays scrubbed and anchored to this file, so an inherited
`GIT_DIR` can still not make an enactment checkout "our own". `test_the_hook_processs_own_git_dir_cannot_move_the_resolution`
holds unchanged; `test_a_git_dir_shared_between_the_hook_and_the_shell_is_resolved_as_well_not_ignored`
is the new case both ways.

Minors closed in the same edit, because the word parse made them one line each: a quoted
directory with a space is read whole (`--git-dir="/my dir/.git"`, `GIT_DIR='...'`, `-C "..."`);
`git -c remote.origin.pushurl=<enactment>` and the `GIT_CONFIG_COUNT/KEY/VALUE` prefix are
handed to git as the same `-c` and the same environment, so the resolution reads the redirected
remote rather than the checkout's. Every `GIT_*` assignment in the push's segment (and every
exported one before it) reaches the resolution subprocess; only those are passed, since an
arbitrary prefix (`PATH=`) could break the subprocess without changing where git pushes.

Not closed, stated as the net's edge: a `GIT_CONFIG_*` inherited by the hook still reaches both
readings unscrubbed (consistent with the push, which inherits it too); `env -u GIT_DIR git push`
is read as if the unset had not happened (the hook env is honoured, refusal direction); a `cd`
or path holding a `;` inside quotes splits as a segment; `sudo`/`timeout` wrappers are skipped
to the `git` word but their own option parsing is not modelled; a `GIT_DIR` that arrives through
`$VAR`, a subshell or a sourced file is invisible, as before. The commit first lines of
2026-09-03 (76 and 75 chars) exceed the brief's 72; history is not rewritten on a pushed branch,
and the two 2026-09-04 lines are 69 and 62.

**2026-09-04, review fixes round 2 (re-review of the same day, `request_changes`).** One guard
commit, alone: `91b62dd`. Six more tests in `tests/test_enact.py`, red against the round-1 cut
(6 failed, 55 passed) and green after (61 passed); `mypy twin/enact_guard.py` clean; `twin
verify --only enactment_is_propose_only_at_both_layers` → 1 passed; fourteen hook end-to-end
probes through `python twin/enact_guard.py` from the hub's own directory against the real
`.estate-clone/ludlow` give the expected verdict, mismatches 0.

Blocking, *only the first pushing segment was resolved.* The round-1 cut found the first segment
matching `_PUSH` and stopped, so a self-push in front laundered an enactment push behind it:
`git push origin main; git -C <ludlow> push origin main` from the hub was admitted, and so were
`... && cd <ludlow> && git push origin main`, `echo 'git push origin main later'; git -C <ludlow>
push origin main` and the ticket's own family `git push origin main; git --git-dir=<enactment>/.git
push origin main`. The re-reviewer reports `main` denied them; its `_effective_cwd` searched the
whole string for the first `-C` or a leading `cd`, so the `-C` and `cd` shapes were caught by
the over-reach round 1 removed, and round 1 put nothing in its place. `_push_target`
now walks every segment that matches `_PUSH`; each is resolved with its own target argument and
its own loci through `_effective_loci(segments, index, cwd)`, with the `cd`s and exports folded
from the segments before that index; one enactment target among them is the refusal. Test:
`test_every_pushing_segment_is_resolved_not_only_the_first`, seven shapes, with the two-self-push
control admitted.

Minor, *a failing `cd` was folded as a success.* `cd <absent>; git push origin main` from an
enactment checkout resolved in a directory that is no repository, read nothing, and admitted; the
shell's `cd` fails and the push runs where it stood. A `cd` (or `-C`) to something that is not a
directory now yields both loci, folded and unfolded, and either naming an enactment repository
refuses. Test: `test_a_cd_that_would_fail_leaves_the_push_where_the_shell_stood`.

The four sibling shapes the re-reviewer listed, each closed because each cost a few lines, all
**delegated (ADR-0025)**:

1. `PUSHURL=<url> git --config-env=remote.origin.pushurl=PUSHURL push origin main` — read as
   `-c remote.origin.pushurl=<value>`, the value taken from the assignment prefix on the same
   segment, an `export` before it, or the hook's own environment (which the push inherits). An
   unset variable adds no config, as git would add none.
2. `GIT_DIR=<enactment>/.git; export GIT_DIR; git push origin main` — a segment that is only
   assignments is kept as shell variables; `export NAME` promotes one by name; only the exported
   `GIT_*` reach the resolution's environment, as before. The unexported form stays uncarried.
3. `git -c remote.x.url=<url> -c remote.pushdefault=x push` with no target — the target is no
   longer assumed to be `origin`: `_default_remote` reads git's own order, `branch.<b>.pushRemote`,
   `remote.pushDefault`, `branch.<b>.remote`, then `origin`, through the same locus. Observed with
   git 2.55 on 2026-09-04: `git push x` honours a remote that exists only through `-c`, while
   `git remote get-url x` says "No such remote", so `_remote_url` falls back to the config keys the
   push reads (`remote.<x>.pushurl`, then `.url`) when `get-url` names nothing.
4. `bash -c 'cd <enactment> && git push origin main'` — `_commands` lifts the quoted script of a
   `bash|sh|zsh|dash -c` out and reads it as a command of its own at the same cwd; the outer
   command is read with the subshell replaced by `true`, so the script's `cd` does not leak into
   the segments after it. `bash -lc` and the like are matched (`-[A-Za-z]*c[A-Za-z]*`).

Stated limits, the net's edge after round 2: a `cd` in the outer command before `bash -c '...'`
is not folded into the script (the script is read at the caller's cwd; a `cd` inside it is);
`bash -c "$SCRIPT"`, `eval`, a heredoc and a sourced file are invisible, as any `$VAR` is;
`--config-env` reads a variable only from the prefix, an export, or the hook's environment;
`branch.<b>.*` in the push default is read for the branch git reports at the locus, so a
`git checkout` earlier in the same command is not modelled; a `cd` with a trailing `&&` after a
failing target is still read both ways (the `&&` would have stopped the push, refusal direction);
the round-1 limits (`GIT_CONFIG_*` inherited unscrubbed, `env -u`, `;` inside quotes, wrappers
unmodelled) stand. Observed live this round while probing, pre-existing and in the safe
direction: `git -C .estate-clone/ludlow remote get-url --push origin` is refused by the hub's
checked-in hook because `_PUSH`'s `\bpush\b` matches the `--push` flag; a read-only command
refused, not a push admitted, so left as it is.

Map line: 65 — enact_guard closes the `--git-dir`/`GIT_DIR` family (M17): every pushing segment
resolved at its own locus, tilde and quotes as the shell reads them, `-c`/`--config-env`/`GIT_*`
handed to git, push default read from git, `bash -c` scripts read, hook env read both ways;
eighteen tests red-then-green, graded by twin.yml pytest.

## Waits on the owner

Nothing. The PR merge is the integrator's, as `pavc-other-hand` (ticket 88).
