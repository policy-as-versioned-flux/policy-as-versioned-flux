# 72 — A feed bump re-renders the twin's derived artefacts

Type: task (AFK)
Status: resolved (AFK scope built 2026-09-03; the citable bump-commit run waits on the owner)
Blocked by: none

## Question

TRUTH run 18 (2026-09-01T09:41Z, hub 031b91a, driftwood 27f1cf2) shows two new driftwood reds
that are direct fallout of the first real step 2 (ticket 61, PR #20: threat-register v1 → v2 in
one bot commit):

- `verify-twin-overlay.sh`: `twin/forward-intel/v1/feed.json` is not what the overlay renders.
- `verify-twin-scenarios.sh`: the signal lookup has no row for `feeds/feed/threat-register/v2`
  and still carries rows for `v1`, which party.yaml no longer pins.

Ticket 61's postUpgradeTasks completer updates `party.yaml` and `composed/` but leaves the twin's
derived artefacts (the signal-lookup rows and the rendered forward-intel feed) at the old pin.
Every future feed bump will redden the same two checks the same way. Make the completer (or the
same bot commit) re-derive the twin's artefacts from the new pin, and prove it: the next merged
feed-bump PR leaves both checks green on the TRUTH line that reads it. Done = both checks green
on a citable run whose driftwood commit contains a Renovate feed bump.

## Notes

Surfaced by ecosystem ticket 60 while watching the first post-61 truth run. The reds are real
estate defects (ticket 55's rule: every red real, explained, finishable), not instrument faults.
The fix lands in driftwood; the enact guard means the owner pushes and merges it.

**2026-09-01, 12:31Z: the same defect killed twin-sweep's first scheduled firing.** The sweep
step runs `python3 twin/emit-forward-intel.py --check`, which exits 1 on the stale feed, and the
run fails. Two findings:

1. The sweep exists precisely to re-render a moved feed, but it cannot: the job step executes
   under GitHub's default `bash -e`, so the `rc=$?` branch that maps exit 1 to `moved=true` is
   unreachable — any real move aborts the step before the branch runs. The step needs `set +e`
   around the check (the same pattern verify-reconcile.sh uses), or `|| rc=$?`.
2. Even with that fixed, the sweep re-renders the feed but does not touch the signal-lookup
   rows, so the second red (`no row for feeds/feed/threat-register/v2`) needs the completer (or
   the sweep) to re-derive the lookup too.

## Comments

**2026-09-02, review.** Confirmed live on run 33627910027 (2026-09-02T12:04Z): the step runs under `shell: /usr/bin/bash -e {0}` while the body sets only `set -uo pipefail`, so `emit-forward-intel.py --check` exiting 1 aborts before `rc=$?`. The moved branch has never executed. Add a check that the moved path has fired at least once; a branch that has never run is not proven. Record: REVIEW-2026-09-02.md R7, participants/P7.

## Answer — 2026-09-03, built on a local driftwood branch

Branch `ticket-72-a-feed-bump-re-renders-the-twin-s-derived-artefacts` in
`.estate-clone/driftwood` (worktree `.work/ticket-72`), four commits off
`ecosystem/build-2026-09-03`; tickets 64 and 93 stack on it:

- `f286dc6` the signal lookup re-derives from the pin it reads — new
  `.github/scripts/rederive-signals.py` (python3 + pyyaml; `--check`, `--at`, `selfcheck`).
- `9371736` the completer re-renders the twin's artefacts in the bump commit —
  `.github/scripts/complete-feed-bump.sh` gains a tail that runs the re-deriver and the emitter;
  `renovate.json` `postUpgradeTasks.fileFilters` widens to `twin/forward-intel/**` and
  `twin/signals.yaml`. `renovate-run.yml`'s `RENOVATE_ALLOWED_COMMANDS` is unchanged: it is the
  same one command.
- `3e157b3` the sweep's moved path runs under `bash -e`, and is checked — `twin-sweep.yml` and the
  new `twin/verify-twin-sweep-moved.sh`.
- `1797783` feed.json and signals.yaml follow the threat-register v2 pin — the one-off repair
  (`derived_from` version 1 → 2; the lookup row v1 → v2, dated 2026-09-01, the merge of PR #20)
  plus the lookup header naming the completer as its upgrade path.

Hub: this file, and a dated note in ADR-0024's consequences. No hub Python changed, so no mypy.

**Which checks grade it.** `verify-twin-overlay.sh` (assertion 1, `--check` byte-identical) and
`twin/verify-twin-scenarios.sh` (section 8, pins ↔ rows) are the regression tests and both go
green on the branch. `twin/verify-twin-sweep-moved.sh` is the new check the 2026-09-02 review
asked for: it reads the sweep step's own `run:` out of the workflow YAML and executes it under
`bash -e` on planted copies — a fresh copy says `moved=false`, a stale feed and a stale lookup
each say `moved=true` — then reads `observations/twin-sweep.jsonl` for a line with
`"moved": true`. Until the clock writes one it exits 3 with that reason: a branch that has never
run is not proven, and this script is what would have caught the dead branch (run against the
old workflow it fails both stale cases). `verify/schedules/verify-schedules.sh` still grades the
edited sweep job caged.

**Decisions, all delegated (ADR-0025):**

1. **The completer owns the re-derivation; the sweep is the day-after safety net and now carries
   the lookup too.** Ticket 61's rule is that a bump is complete in one commit, and the two
   artefacts are derived from the same `inherits[]` the bump edits. The sweep would have re-rendered
   only the feed, a day later, on a branch nobody had asked for. The sweep's moved reading is now
   "feed render moved OR lookup would be rewritten", and its proposal stages both files.
2. **The lookup rewrite is mechanical and narrow: `pin.version`, the `-<version>-` token in
   `signal.id`, and `signal.at`; `scenario` and `what` are never touched.** Binding a subscription
   to a standing question is a human's judgement and a version bump does not change it. The
   deriver refuses (exit 2, `REFUSED:` last line) a pin with no row (a new subscription needs a
   human row), a row whose pin is gone (declaring the scenario unbound needs a human reason), a
   doubled row, and an id with no version token. The file is edited as text so its comments and
   block scalars survive; a yaml round-trip would flatten both.
3. **`signal.at` becomes the date the row was re-derived, not the pin's `since`.** The brief's
   recommendation was to leave `at` alone; the file's own header and its last hand edit
   (`6a2df16`, platform 1.1.1 → 2.0.1) say the row's date is the date the pin moved, and a row
   saying v2 "since 2026-08-28" would be false. The completer cannot know the merge date, so it
   records the bump date (`--at`, default today UTC) — idempotent, since a row is only rewritten
   when its version differs. The repair commit uses PR #20's real merge date, 2026-09-01.
4. **`derived_from` keeps the pin version.** ADR-0019: a derivation names its inputs. The feed
   re-renders on every bump now, so carrying the version costs nothing and drops nothing.
5. **The completer clones the hub (`main`, depth 1) into `$work` and renders in a copy of the
   overlay inputs at `$work/hub/.estate-clone/driftwood`.** The emitter finds the `twin` package by
   walking up from its own *resolved* path, so a symlink would land it back in Renovate's hub-less
   workdir; a copy of `twin/`, `selection-policy/` and `party.yaml` is the plant
   `verify-twin-overlay.sh` already uses. Depth 1 suffices: the emitter needs code, not history
   (the composed/ clones above it stay full, for the reason ticket 61 found). The only output
   copied back is `feed.json`. Proven with a pyyaml-only interpreter (below): the twin package
   needs nothing else.
6. **Evidence that the moved path fired is a `moved=true` line in `observations/twin-sweep.jsonl`
   on `main`.** The observe step now runs on both paths (moved, proposal branch, run id), and the
   propose step returns to the default branch when it finishes so the cage can append the line.
   The line is an observation, not a declaration — the feed and lookup go to the proposal branch as
   before — so D1 holds and the cage step is unchanged; its HEAD guard stays as defence for a
   propose step that dies midway. Offline-readable jsonl over `gh run list`, because a check that
   needs the network to see whether a branch ran is a check the truth line cannot read.
7. **Widening `fileFilters` onto declaration paths does not breach ADR-0024 D1.** Renovate is a
   proposer: its commit sits on a pull request a human merges, and `renovate-run.yml`'s cage still
   asserts the job checkout stays clean. Recorded as a dated note on ADR-0024.
8. **A refusal from the re-deriver fails the sweep run rather than reading as "not moved".** In
   the sweep step, exit 1 from either check is the moved reading; anything above 1 is a render or
   lookup that could not be made, and that is a red run with the reason in the log — a named hole a
   human fills, never a silent flat series.

**How verified** (from the hub worktree root; `.venv` is the hub's):

```
bash .estate-clone/driftwood/verify-twin-overlay.sh          # 22 pass, 0 fail, 0 could-not-look; PASS
  (in a real-directory estate layout; through the worktree symlink assertion 3 could not see ../platform → 21/0/1)
bash .estate-clone/driftwood/twin/verify-twin-scenarios.sh   # 16 pass, 0 fail, 0 could-not-look; PASS
bash .estate-clone/driftwood/twin/verify-twin-sweep-moved.sh # 3 pass, 0 fail, 1 could-not-look; SKIP: the moved path has not fired live yet
  (same script against HEAD's twin-sweep.yml: 1 pass, 2 fail — the stale feed and stale lookup cases)
python3 .github/scripts/rederive-signals.py selfcheck        # TOTAL: 0 planted case(s) failed (7 fail with the deriver stubbed to a no-op)
verify/schedules/schedules.py check --offline (driftwood)    # twin-sweep.yml job sweep: caged
completer tail, pyyaml-only venv, planted stale feed + v1 row, real hub clone
                                                             # rewrote twin/signals.yaml: v1 -> v2; wrote feed.json (1619 bytes); both byte-identical to the repair
actionlint .github/workflows/twin-sweep.yml                  # ok
```

Not done: `talk/verify-all.sh` (builders do not run it); no `composed/` regenerated; nothing
pushed to driftwood.

## Waits on the owner

- Push `ticket-72-a-feed-bump-re-renders-the-twin-s-derived-artefacts` (or the integration branch
  once merged into it) to `policy-as-versioned-driftwood` and merge its PR; the enact guard refuses
  agent pushes. The first TRUTH run after that merge turns both reds green on the repair commit.
- **The citable run this ticket's Done names**: a TRUTH run whose driftwood commit contains a
  Renovate feed bump with both checks green. That needs a new per-feed tag from `feeds` or a
  re-quote from `insurer` (a human `cut-release.yml` dispatch), Renovate's 06:11 run, and a human
  merge of the Renovate PR. Record the run id and date here when it exists.
- A `workflow_dispatch` of `twin-sweep.yml` after the merge will observe `moved=false` (the feed is
  fresh) and start the series. The `moved=true` line `verify-twin-sweep-moved.sh` waits for arrives
  the first time the overlay or a pin moves under the sweep — ticket 93's probability will move the
  payload, so the proof is likely to come from that merge; merging the `twin/forward-intel-<date>`
  PR it opens is a human act.

Map line: 72 built 2026-09-03 — a feed bump re-derives feed.json and signals.yaml in the bump commit (completer + widened fileFilters); twin-sweep's moved branch, dead under bash -e since written, now runs, proposes both files and appends moved=true observations; verify-twin-sweep-moved.sh could-not-look until it fires live; driftwood branch waits on the owner's push, the bump-commit TRUTH run on the next feed tag.
