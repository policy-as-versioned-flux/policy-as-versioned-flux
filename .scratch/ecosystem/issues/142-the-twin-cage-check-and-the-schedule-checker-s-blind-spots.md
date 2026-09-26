# 142 — The twin cage check, and the schedule checker's blind spots

Type: task
Status: claimed
Blocked by: none

## Question

Graduated 2026-09-25 from grilling ticket 30, decisions 8, 14 and 16 (delegated), and ADR-0031.
This ticket carries ticket 30's definition of done: its check is wired into `talk/verify-all.sh`.

1. **The twin cage check.** A new `verify/twin-cage/verify-twin-cage.sh`, discovered by
   `talk/verify-all.sh`. It grades each adopter's served `origin/main`, never the local clone:
   - the twin-agent line in `composed/evidence.json` `prices[]` selects a rung on the ladder;
   - the twin-sweep jobs match that rung's dial row (ticket 30 decision 11): the twin job holds
     `contents: read`; the writer job has no hub checkout and no `uses:` step that is not inert;
     the hub checkout ref equals the commit in `twin/PIN.yaml`; every download is pinned by hash;
     the writer's steps fit the rung, for example no proposal step at `quarantine`;
   - on the hub side, the local-clock child holds no push capability (item 3).
   Until tickets 143 and 145 land, the check FAILs by name on each adopter. That red is the
   point: it measures the served workflow, not the plan.
2. **The schedule checker's blind spots** (`verify/schedules/schedules.py`):
   - `_SIGNED_ARTEFACT` misses `gh api ... pulls/N/merge`, `gh api ... releases`,
     `gh api ... git/refs`, `curl -X PUT .../merge`, `git update-ref` and `git push origin <tag>`;
   - the PASS line "nothing it runs is opaque to this checker" claims more than the check reads:
     it flags only `uses:` actions, and every sweep runs hub Python. Narrow the sentence or widen
     the measurement;
   - it grades each `.estate-clone/<unit>` working tree, not `origin/main`;
   - `lane.py` would grade a REST merge made with a scheduled token as a NOTE, not a FAIL.
3. **The local-clock child holds no push capability** (ticket 30 decision 14): no credential
   helper, no `GH_TOKEN`, `--strict-mcp-config`, a clock-only settings file, and Bash limited to
   named scripts instead of `python3 *`. Measured 2026-09-25: under `operations` the guard admits
   an adopter push made inside `python3 -c 'subprocess.run([...])'`.
4. **Delete the stale row** `driftwood/twin-sweep.yml: ticket: 72` from
   `verify/schedules/clock-owners.yaml`; that clock is green, and the file's own rule says delete.

## Notes

Every item reads the served artefact and the operation that reaches it. Test each fix against the
check as an adversary: a check that reads the text it grades takes the fix as input.

## Comments

**2026-09-25, items 2, 3 and 4 built (142a), owner-instructed.** The owner wrote on
2026-09-25: "i'm afk you have all the approvals you need to deliver". That authorises feature
branches and pull requests, not a merge, a push to main, a tag or a release. This PR builds items
2, 3 and 4 in the hub and nothing in any estate repository. Every decision below that the brief
left open is **delegated** (ADR-0025), with its reason.

**Item 1 is deliberately not built here.** `verify/twin-cage/` lands last, after tickets 143
and 145 are served on each adopter's `origin/main`, so that its first run measures a served cage
and not the plan. What it still needs, for the record: the twin-agent `prices[]` line and the
rung it selects (ticket 145, platform's dial table and the adopter's selection policy); the split
sweep with a `contents: read` twin job, a writer job with no hub checkout and no non-inert `uses:`,
a hub checkout at the `twin/PIN.yaml` commit and every download pinned by hash (ticket 143); the
hub-side reading of item 3 (this PR's `verify/local-clock/verify-local-clock.sh` block 1d4 is what
it will cite); discovery by `talk/verify-all.sh`; and a FAIL by name on each adopter until 143 and
145 land, which is the point.

**Item 2, what changed in `verify/schedules/schedules.py` and `lane.py`, and what was measured.**

- `_SIGNED_ARTEFACT` is now a table of shapes plus a REST reader: `gh api`/`curl` to
  `/pulls/N/merge` or `/merges` in any method spelling (`-X PUT`, `-XPUT`, `--method PUT`,
  `--method=put`, `--request PUT`, none at all: the merge endpoint is a disposal whatever the
  method, so the path alone is the fault); `gh api`/`curl` to `/releases` or `/git/refs` when the
  call writes (a POST/PUT/PATCH/DELETE method, or a body flag, per tool and case-sensitive, because
  curl's `-f` is `--fail`); `\`-continued lines joined and comment lines dropped first; `git
  update-ref`; `git push` of `--tags`, `--follow-tags`, `refs/tags/`, `tag <name>` or a
  version-shaped refspec (`v1.2.3`, `twin/v0.1.0`); the GraphQL mutations `mergePullRequest`,
  `enablePullRequestAutoMerge`, `createRef`, `updateRef`, `deleteRef`, `createRelease`; and `gh
  release edit|delete|delete-asset` beside `create|upload`. The selfcheck probes 34 write shapes
  and 27 read twins (`/pulls/4/files`, `/releases/latest`, `git/ref/tags/v1`, every
  `curl -sSL -o … /releases/download/…` the estate's workflows carry, a comment line naming a
  merge). Nothing is now less safe: only refusals were added, and no scheduled job on any unit's
  `origin/main` trips a new one (measured below).
- The PASS line "nothing it runs is opaque to this checker" is gone. **Decided: narrow the
  sentence, derived from the job, rather than widen the fault.** `called_programs()` enumerates
  what each `run:` step executes from its checkout (`python3 x.py`, `python3 -m pkg`, a heredoc
  `python3 -`, `python3 -c`, `bash x.sh`, `npx pkg`, `./x`) and the line names them with the job's
  permission: "caged as far as this checker reads … N program(s) it runs from its checkout are not
  read here (…), so what they write is bounded by the job's permission (contents: write) and by
  verify-lane.sh's read of what landed, not by this line". A job that runs only inline shell and
  inert actions keeps a plain "caged" line that says every step was read in full. Reason: widening
  would have turned 14 scheduled jobs red at once on 2026-09-25 (the three twin sweeps, three
  propose-tier, three renovate, the five publishers' fetches and the hub's own truth gate) with no
  ticket owning any of them, and would have pre-empted item 1, whose check is what grades the twin
  job's `contents: read` once ticket 143 has split the sweep. The lane grader is the after-the-fact
  read of what a called program lands, and the line now says so.
- Every unit is read at its **served ref**: `served()` fetches `+refs/heads/main:refs/remotes/
  origin/main` (20 s timeout), reads `party.yaml`, `twin/`, `.github/workflows/*` and
  `.github/rulesets/` with `git show`/`git ls-tree` at that sha, never from disk, and prints
  `INFO: <unit>: graded at origin/main@<sha> (fetched now | fetch FAILED (…); as last fetched)`.
  A unit with no `origin/main` is one named SKIP and nothing of it is graded. The collector
  (`clocks`) reads the same way and records the sha. Measured: on 2026-09-25 driftwood, tuppence
  and ludlow's working trees were 2 commits behind `origin/main` and insurer's 7; the old code
  graded those trees.
- `lane.py`: a merge committed by `GitHub <noreply@github.com>` never names who merged.
  **Decided:** a MERGE commit GitHub wrote carries the merging account as its author (measured
  on every unit: all 23+25+23+18+7+4+6+6+79 App merges are authored `pavc-other-hand[bot]`,
  committed GitHub), so a scheduled or automation author is a FAIL from the commit alone,
  offline; `app/pavc-other-hand` is the reviewed second hand (ticket 88, owner-instructed) and is
  a NOTE; a person's merge is out of scope. A SQUASH or REBASE GitHub wrote keeps the proposal's
  author, so for one authored by a scheduled identity the merged pull requests are asked
  (`mergedBy` from `gh pr list`, newest 500 per unit): the collector records them in the clock
  verdict file (`units.<unit>.merges`) so the credential-free gate can read them, an
  authenticated `gh` answers locally, and no source is a named SKIP, never clean. A bot merger
  (`app/…` or `…[bot]`, other than the second hand) is a FAIL; a person is a NOTE. The estate
  today holds no squash or rebase of a scheduled identity's commit on any `main`, so no live line
  changed except the new NOTE per unit counting the second hand's merges.

Measured, `verify-schedules.sh` and `verify-lane.sh` on this branch merged onto origin/main
(hub 501858bb, adopters at driftwood 155db9e, tuppence 5deffe6, ludlow b8e14f7, platform
557c153) against the same scripts on origin/main 32739f18: schedules gained one `INFO: <unit>:
graded at origin/main@<sha> (fetched now)` line per unit (9), every "caged … nothing it runs is
opaque" PASS became the narrowed sentence naming its programs (27 jobs), and no PASS/FAIL/SKIP
status changed for any clock question except the driftwood row below. The three reds
(insurer/fetch.yml, ludlow/twin-sweep.yml, tuppence/twin-sweep.yml) stay red and stay owned by
tickets 77 and 144 in the same words. One run of the branch read `hub/truth.yml` as a 249h-old
run while `gh run list` a minute later showed the 8h-old one; the code path is untouched and the
rerun read 8h: a transient in the API listing, recorded, not a change. Lane: one new NOTE per
unit for the second hand's merges; hub@main's scheduled-commit count moved 88 to 89 because
origin/main gained a truth record between the runs; verdict unchanged (PASS, exit 0).

**Item 3, `talk/local-clock.sh`: the child's inherited environment reaches no push credential.** Measured on this machine
2026-09-25 before writing: `/opt/homebrew/etc/gitconfig` (git's system file here) sets
`credential.helper = osxkeychain`; every estate remote is https; `SSH_AUTH_SOCK` is set and the
agent holds a key; `~/.ssh` holds key files; `~/.git-credentials` exists; gh is logged in through
the login keychain; `GH_TOKEN`/`GITHUB_TOKEN` are unset. With `GH_CONFIG_DIR` at an empty
directory and no variable set, `gh auth status` said "not logged in" and `gh auth token` STILL
printed the owner's keyring credential, so the keychain is reachable to any process running as
the owner. Closed for the child only, by environment: `GIT_ALLOW_PROTOCOL=none` (git refuses
every transport before it looks up a helper or a credential; `-c protocol.allow=always` and
`GIT_CONFIG_*` cannot override it, measured), `GIT_EXEC_PATH` at an empty directory
(`git-remote-https` and `git-credential-osxkeychain` are not found by `/opt/homebrew/bin/git` or
`/usr/bin/git`; every command the child needs is a builtin, measured for status, add, commit,
log, worktree and rev-list), `GIT_CONFIG_NOSYSTEM=1`, `GIT_CONFIG_GLOBAL` at a clock-only file
(empty `credential.helper`, `protocol.allow = never`, signing off, the owner's `core.hooksPath`
carried over so the commit hooks still run) that the clock reads back after the child and
refuses any key written to, `GIT_SSH_COMMAND` at a refusing script, `SSH_AUTH_SOCK`,
`GIT_ASKPASS`, `SSH_ASKPASS` and `GITHUB_TOKEN` unset, `GIT_TERMINAL_PROMPT=0`, `GH_CONFIG_DIR`
empty, and `GH_TOKEN` set to a decoy string GitHub refuses ("Bad credentials", measured),
because gh consults the keyring only when nothing is in its environment. **Decided:** the child
starts `--restricted --tools Bash,Read,Edit,Write,Glob,Grep` (user, project and local settings
ignored, file tools confined to the hub and the worktree), `--strict-mcp-config --mcp-config`
naming no server, and `--settings` at a clock-only file that registers the `PreToolUse`
`twin/enact_guard.py` hook for `.*` (under `--restricted` the hub's own `.claude/settings.json`
is ignored, so the hook must live there), denies the code-running Bash shapes, and turns on
Claude Code's OS sandbox for Bash with no network domain allowed, `strictAllowlist`,
`allowUnsandboxedCommands: false` and `~/.ssh`, `~/.git-credentials`, `~/.config/gh`,
`~/.gitconfig` unreadable to subprocesses (documented for Claude Code 2.1.219+; 2.1.282 is
installed). `Bash(python3 *)` is replaced by the named scripts the two skills run: each row's
validator (from the STEPS table), `python3 -m twin.derived_forecast inputs`, and `python3 -m
twin.market_signals moves`, a new read-only verb that replaces the classify skill's `python3 -
<<'PY'` heredoc, which no named-script rule can admit. Named, not closed: the child runs as the
owner's user, and macOS lets that user read the login keychain and `~/.ssh` (a model that
hand-rolls `ssh -i` or `security` outside git holds the owner's credential); only a separate
user account or the sandbox holding removes that. The sandbox is the one thing the stub harness
cannot measure (it cannot run the real binary); the first live run is its measurement, and a
child that cannot run commands under it fails the step. The clock's own `--push` runs after the
child in the script's own environment and keeps working (harness 1b).

Proved offline, `verify/local-clock/verify-local-clock.sh` block 1d4 with `stub-claude.sh
pushprobe`: a stand-in child running PATH's own `git`, `python3` and `gh` tried an adopter push
from inside `python3 -c 'subprocess.run([...])'` ("transport 'file' not allowed", rc 128), an
https push ("transport 'https' not allowed"), an ssh push ("transport 'ssh' not allowed"),
`ls-remote origin` (refused), `git remote-https` and `git credential-osxkeychain` ("not a git
command"), `gh auth status` (not logged in) and `gh auth token` (the decoy, no `gh*_` string);
the fixture origin's `main` was unmoved and gained no ref; and the stand-in's recorded argv
carried `--restricted`, `--strict-mcp-config`, `--mcp-config`, `--settings` (the file parsed and
asserted: hook for `.*` naming `twin/enact_guard.py`, sandbox on with `allowedDomains: []`) and
an `--allowedTools` without `Bash(python3 *)` and with the four named scripts. Block 1d3 now also
proves the child's `git config --global` lands in the clock-only file and reaches neither the
owner's `~/.gitconfig` nor the clock's own global. 26 runs, exit 0. `tests/test_local_clock.py`
carries the same reading (`test_the_child_holds_no_push_capability`).

**Item 4.** The row `driftwood/twin-sweep.yml: ticket: 72` is deleted from
`verify/schedules/clock-owners.yaml`: ticket 72 reads resolved and the clock is green.
Measured on the served ref: `PASS: driftwood/twin-sweep.yml: last scheduled run 9h ago
(success)` on origin/main 155db9e, and `owners_faults` reports nothing.

Out of scope, seen while measuring and not touched: `insurer/fetch.yml`'s red is owned by
ticket 77, which reads `resolved`, so the FAIL line says "either the fix has not reached a
scheduled run yet, or this red is a new one wearing an old ticket's name" (a re-own or a new
ticket is the integrator's call); tickets 143 and 145 are referenced by the clock-owner rows for
tuppence and ludlow through ticket 144, unchanged.

**2026-09-26, integrator, before merge (delegated).** The round-1 reviewer showed that a child can
rebuild its own environment (`env -u GIT_ALLOW_PROTOCOL GIT_EXEC_PATH=... git -c
credential.helper=osxkeychain push ...`) and reach the owner's keychain. So the item-3 cage removes
the push route from the environment the child inherits; it does not yet remove the capability.
The PASS line and the clock's own lines now say exactly that, and name the limit. What would hold
against a rebuilt environment: the Claude Code sandbox the clock-only settings enable (configured,
not yet measured: the first live run measures it), or a separate OS user for the child. Item 3
stays open on that point until one of them is measured.
