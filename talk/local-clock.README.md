# The local clock -- run instructions

The eco-system has three clocks. Two run on GitHub and never call a model: `truth.yml` on the
hub, and each unit's `fetch` / `renovate-run` / `propose-tier` / `twin-sweep` (ADR-0024). The
third is this one. It runs the steps that need a model, and it runs from **this machine**,
because the model can only run inside Claude Code here (ticket 75 Q10: no tokens exist anywhere
else). Each step calls Claude Code non-interactively with a named skill, and each result lands
as a branch plus a pull-request body -- never a commit to `main`, never a merge, never a tag.

What it is not: citable. A local run appends nothing to `talk/truth.log`. The truth surface
grades only that this clock ran (`verify/local-clock/verify-local-clock.sh` reads the marker it
leaves) and that no rehearsal ever reached a citable path.

## Prerequisites

- macOS with Claude Code installed and logged in as you (`claude --version`; `claude -p "say ok"`
  answers). For an unattended launchd run Claude Code's own docs say an OAuth session may not
  refresh headlessly; if a scheduled run fails to authenticate, run `claude setup-token` once. That
  token lives in your keychain, not in any file here.
- `gh` logged in as you (`gh auth status`) -- only needed for `--push`.
- The estate assembled: `bash clone-estate.sh` (the clock reads `.estate-clone/<adopter>` and
  makes its own worktree under `.estate-clone/<adopter>/.work/local-clock/`).
- The hub venv (`.venv/bin/python`) or a `python3` with pyyaml.

## The one command

```
talk/local-clock.sh --adopter driftwood
```

That runs every step in the table (`talk/local-clock.sh --list-steps`) for driftwood, with the
model, and stops short of pushing. To push and open the pull request under your own login, from a
terminal (not from inside a Claude Code session, where `--push` is refused):

```
talk/local-clock.sh --adopter driftwood --push
```

A run costs real tokens: the probe that confirmed the invocation shape (`claude -p
"/classify-and-judge driftwood" --max-turns 1`) cost about USD 0.29 for one turn, and a full
classify step is many turns. `LOCAL_CLOCK_MAX_TURNS` (default 80) is the cap.

## Flags

- `--adopter UNIT` -- an adopter to run for; repeatable; `all` is driftwood, tuppence and ludlow.
  Default: driftwood, the teaching default.
- `--step NAME` -- only this step; repeatable. Default: every step in order.
- `--inject FILE` -- the world simulator (below). Runs as a rehearsal.
- `--push` -- after a live step commits, push its branch to the adopter's repository and open the
  pull request with `gh`. Refused inside a Claude Code session; refused on a rehearsal.
- `--dry-run` -- make the worktrees and render the prompts, call no model, record every step as
  skipped. Use it to read exactly what the model would be told
  (`.local-clock/runs/<run>/<step>-<adopter>.system.md`); the worktree it made is removed
  again before it exits.
- `--list-steps` -- print the steps table and exit.
- `--help` -- the usage text.

## What it writes

Everything under `.local-clock/` at the hub root, which is gitignored. `<run>` is the run id:
the UTC stamp plus a random suffix, `20260904T101500Z-a1b2c3`, unique on the filesystem even
when two runs start in the same second (the first line of every run prints it).

| path | what |
|---|---|
| `.local-clock/runs/<run>/` | one directory per run: the rendered headless prompt per step, the child's JSON transcript (`*.claude.json`) and stderr, the PR title and body per step, `steps.jsonl`, `marker.json`, and on a rehearsal `injected-signal.json` |
| `.local-clock/last-run.json` | the dated marker the gate grades: when, scheduled or by hand, live or rehearsal, hub commit, each step's status and branch |
| `.local-clock/logs/` | launchd's stdout and stderr when the plist runs it |

And in the adopter's clone: a worktree at `.estate-clone/<adopter>/.work/local-clock/<run>-<step>`
on the branch `local-clock/<step>-<run>` (or `local-clock/rehearsal/<step>-<run>`), carrying
the one commit the model made. It is kept until pushed (`--push` removes it and the local
branch after the PR opens) so you can read the diff first. A step that proposes nothing, and a
dry run, remove their worktree and branch before the run ends, and the run records `fail` if
that removal did not happen. Nothing is written to the adopter's `main`, ever.

## How to read the result

The run prints one line per step: `ok`, `skip` (with why: the skill is not shipped yet, nothing
to propose, dry run), or `fail` (the model left uncommitted work, touched a path outside the
step's allowed paths, committed a file under those paths that is not a `*.claim.yaml`, wrote a
claim file that does not say `headless: true` or claims an override, or wrote one the twin
cannot read). The last line names the marker. Then:

```
cat .local-clock/last-run.json                      # the marker
git -C .estate-clone/driftwood log --oneline main..local-clock/classify-<run>
git -C .estate-clone/driftwood/.work/local-clock/<run>-classify diff main   # the claim file
cat .local-clock/runs/<run>/classify-driftwood.pr-body.md                    # the PR body
verify/local-clock/verify-local-clock.sh            # the gate's view of it
```

A headless claim file says `run.headless: true` and `run.clock: local-clock`, carries bindings
and positions only (grade 5, `price_eligible: false`) and **no override**: an override is a
human's judgement claimed by a role, and nobody was at the keyboard. The clock does not take
the file's word for it: every file the commit carries must be named `*.claim.yaml` (any other
name under `twin/claims` is refused unchecked, because nothing can check it), it requires
`headless: true` in the run block of each, and it runs the skill's `validate_claim.py
--headless` on each, which refuses a file that omits the mark and refuses an override whatever
the file declares. A step that fails any of these is a `fail` with the branch kept; the clock
writes no PR title or body for it, and deletes any title or body the model had already written
to `.local-clock/runs/<run>/<step>-<adopter>.pr-title` and `.pr-body.md`, so nothing in the
run directory reads as a proposal (the transcript `<step>-<adopter>.claude.json` still holds
the model's words). Where the skill would have asked you, the item is left unbound with the
reason in its `evidence`.

Without `--push` the `ok` line prints the exact push-and-PR command for you to run.

## Schedule it (launchd)

The cadence is yours to pick. Render the template with your hour and minute (local time), load it,
and check it is listed:

```
.venv/bin/python verify/local-clock/local_clock.py plist --hour 7 --minute 15 \
  > ~/Library/LaunchAgents/uk.me.cns.pavc.local-clock.plist
launchctl bootstrap gui/$(id -u) ~/Library/LaunchAgents/uk.me.cns.pavc.local-clock.plist
launchctl list | grep uk.me.cns.pavc.local-clock
```

The template (`talk/local-clock.plist`) runs `talk/local-clock.sh --adopter driftwood --push`
with `LOCAL_CLOCK_LAUNCHD=1` so the marker says `scheduled: true`, logs to `.local-clock/logs/`,
and holds no credential. Drop `--push` from the rendered file to keep results local. The gate
grades a scheduled marker older than its period (24h, `LOCAL_CLOCK_PERIOD_HOURS`) plus a day of
slack as a stopped clock; a run by hand is only dated. A sleeping laptop misses its slot: launchd
does not run a missed calendar interval on wake unless the machine was merely asleep for less
than the interval, so expect gaps and read them as gaps.

Run it once by hand, exactly as launchd would:

```
launchctl kickstart gui/$(id -u)/uk.me.cns.pavc.local-clock
```

## How to stop it

```
launchctl bootout gui/$(id -u)/uk.me.cns.pavc.local-clock
rm ~/Library/LaunchAgents/uk.me.cns.pavc.local-clock.plist
```

A run in progress is a `claude` process; `pkill -f 'claude -p /classify'` ends it, and the clock
then reads whatever the model had left, exactly as it does after a normal exit: uncommitted
work is `fail` (worktree kept), nothing written is `skip: nothing to propose` (worktree and
branch removed), and a commit already made is judged on its own terms, as if the model had
finished. Remove leftover worktrees with
`git -C .estate-clone/<adopter> worktree remove --force .estate-clone/<adopter>/.work/local-clock/<run>-<step>`
and the branch with `git -C .estate-clone/<adopter> branch -D local-clock/<step>-<run>`.

## The world simulator (`--inject`)

To rehearse end to end without waiting on the real feeds, hand the same run one dated external
signal -- a headline, a market move, a regulator publish -- as a small YAML or JSON file:

```yaml
date: '2026-09-03'
kind: headline            # headline | market-move | regulator-publish
statement: >-
  Rehearsal: the niobium supply shock, from driftwood's own scenario library.
source: twin/orgs/driftwood/scenarios/niobium-supply-shock-2026.yaml
```

```
talk/local-clock.sh --adopter driftwood --inject signal.yaml
```

Draw rehearsal signals from the adopters' own scenario libraries
(`.estate-clone/<adopter>/twin/orgs/<org>/scenarios/`). A signal naming a real firm, regulator
or person that is not already in that library is yours to choose, not the clock's.

What "rehearsal" does, mechanically: the signal is stamped `injected: true` with when, by what
and from which file, and written only under `.local-clock/` (the stamp refuses any other path);
the branch is named `local-clock/rehearsal/...`; every claim file must carry `injected: true`
on its face, which makes `validate_claim.py` refuse it, so it can never pass a gate; `--push` is
refused; the marker says `mode: rehearsal`. `twin/feed_signal.py` refuses an injected envelope
outright. The gate scans every committed envelope, claim, observation and capture in the hub and
the units for the flag, and one hit is a FAIL: a rehearsal is never cited.

## Adding a step (ticket 93's seam)

`STEPS` in `talk/local-clock.sh` is a table: `name|skill|allowed paths|what`. The `derive` row
is already there, pointing at `/derive-probability`; until `.claude/skills/derive-probability/SKILL.md`
exists the clock records that step as `skip: skill derive-probability not shipped`, by name. Ship
the skill and the row runs. A step whose claim files need a different validator names it in its
own `assets/validate_claim.py`, the way classify-and-judge does.
