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
2. *`GIT_DIR` in the hook process's environment is scrubbed, not honoured.* The hook's env is not
   the shell's env, so honouring it asserts nothing about the push; and unscrubbed it reached
   both resolutions, which is worse than the ticket's finding: a `GIT_DIR` pointing at a checkout
   of this repository made every bare push in every enactment checkout read as a self-push, and
   one pointing at an enactment checkout made that checkout "our own". The guard now decides from
   the two things the hook payload carries, the command string and the cwd. Scrubbed set is
   `GIT_DIR`, `GIT_WORK_TREE`; `GIT_COMMON_DIR` and `GIT_CONFIG_*` are not scrubbed (not named
   by the finding, and the net is stated as a net).
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

Map line: 65 — enact_guard closes the `--git-dir`/`GIT_DIR` family (M17): options handed to git,
hook env scrubbed, six tests red-then-green, graded by twin.yml pytest.

## Waits on the owner

Nothing. The PR merge is the integrator's, as `pavc-other-hand` (ticket 88).
