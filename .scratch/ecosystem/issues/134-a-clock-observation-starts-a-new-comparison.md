# 134 — A clock observation starts a new comparison

Type: task
Status: resolved
Blocked by: none

## Question

Charted 2026-09-24 by the integrator during the v3.3.0 rollout.

`compose/comparison_history.py` `identity()` at platform v3.3.0 hashes every non-hidden file in
the adopter repository outside `composed/`. Its comment says "a source edit deliberately starts a
new comparison". But the adopters' own clocks append to non-hidden files every day:
`drift/samples.jsonl`, `observations/twin-sweep.jsonl` and the lane's captures. ADR-0023 says a
clock appends observations and never declarations, so those files are observations, not source.

The consequences, measured or read on 2026-09-24:

1. After any lane commit, the recorded `comparison-inputs.after` in `composed/HEADER.yaml` no
   longer matches. `compose-check` then fails on every later pull request
   (`RealCompilerLayout.test_composition_bytes_do_not_depend_on_checkout_prefix`), and the
   pre-tag verify in `cut-release.yml` refuses with "comparison history does not match current
   source inputs". Tickets 131 and 132 hit the same failure from a test edit.
2. With replay off, `resolve()` then takes the working tree's header as the "before" (ticket 133),
   so a daily observation can reset what a comparison compares against.
3. Adopters moved to tools v3.3.0 on 2026-09-24, so this starts with their next lane commit.

What this ticket owes:

1. The identity hashes the adopter's declared source inputs only. Decide the rule and record why:
   an allow-list of the inputs the composer reads, or an exclusion of the paths each unit
   declares as its observation lane (the hub's map-surface check already reads those
   declarations).
2. A test at the `compose()` seam: appending a line to a lane file leaves the identity unchanged,
   and editing `party.yaml` changes it.
3. The platform change ships in a tools release, and each adopter moves its tools pin and
   recomposes once. Record what that costs.

## Done

A clock's observation no longer changes the comparison identity, and an adopter's
`compose-check` and pre-tag verify stay green across a lane commit.

## Build, 2026-09-24

Built on 2026-09-24 with ticket 133, in one platform PR:
[platform#39](https://github.com/policy-as-versioned-platform/platform/pull/39), branch
`ticket-134-observation-is-not-source`, based on platform main 38089a6 (v3.3.0). Hub record:
this branch's PR.

### What changed

- `compose/comparison_history.py` `identity()` leaves out the files under each
  `OBSERVATION_LANE` that the adopter's own `.github/workflows/*.yml` declare. It reads what
  the hub grades and no more: a workflow with a `schedule:` trigger, its top-level and job
  `env:` merged as the job sees them. Quoted or unquoted, split on spaces, as the workflows'
  own shell loops read it. (Narrowed in the fix round below. The first build also read step
  env and every workflow.)
- A YAML file inside a lane stays in the identity. The composer reads every `*.yaml` in the
  tree for Namespaces and workloads (`_namespace_facts`), so a lane YAML file is a declaration.
- The sorted lane list is part of the digest. A changed declaration starts a new comparison.
  Before, `.github/` was hidden from the identity, so a lane edit changed nothing.
- A declared lane path outside ADR-0024's observation list refuses by name. So does one that
  is absolute or contains `..`. (The list check is from the fix round below.)
- Migration: `v330_identity()` restates the v3.3.0 formula. It reads each non-YAML lane file
  from the commit that last wrote `composed/HEADER.yaml`. When the recorded `after:` equals
  that value, the record is the same comparison. Verify accepts it as recorded. A fresh
  compose keeps its before and re-stamps only `after:`.

### Decisions

1. Exclude the declared lanes, not an allow-list of composer inputs. (delegated)
   The declaration is the one statement of what a clock may write. ADR-0023 says a clock
   appends observations only, `verify/schedules/lane.py` grades every clock commit against
   that declaration, and `verify/map-surface` grades that a unit owns each declared path.
   An allow-list would have to restate everything the composer reads, and the composer walks
   every `*.yaml` in the tree, so it would be the whole tree again or a second copy that
   drifts. A missing allow-list entry fails silently: a real source edit keeps an old before.
   A missing lane exclusion fails loudly: compose-check goes red.
2. Read the declaration from the adopter's own workflow files in the tree under composition,
   not from the hub. (delegated) The composer runs in the adopter's CI with no hub checkout.
   The hub's check reads `origin/main`, which is the same file once merged.
3. Keep YAML inside a lane in the identity. (delegated) The composer reads it, so it is source.
4. Migrate v3.3.0 records instead of letting the pin move start a new comparison.
   (delegated) Measured without the migration: the recompose moved each adopter's `before`
   to the current state and dropped the open deltas. Tuppence lost `new-untagged-pin` cve
   (241,549.84 GBP) and ludlow lost `new-untagged-pin` eol (772,556.59 GBP) from the live
   comparison. With the migration only `after:` moves.

### Tests, red first, at the `compose()` seam

In `compose/test_comparison_history.py`, run with
`.venv/bin/python -m pytest compose/test_comparison_history.py -n0 -q`:

- Red at v3.3.0, green now: a lane append leaves the identity, the render and verify
  unchanged (3 subtests: a file lane, a directory lane, a new file in a directory lane); a
  changed declaration changes the identity; a bad lane path refuses (3 subtests); verify
  accepts a v3.3.0 record across a lane commit; a fresh compose keeps a v3.3.0 comparison
  and re-stamps only `after:`.
- Green at v3.3.0 and kept: a `party.yaml` edit changes the identity and fails verify; a
  source file beside a lane file is still source; a YAML file in a lane is still source; a
  v3.3.0 record over a changed source still starts a new comparison.
- Final run: 26 passed, 6 subtests passed.

Also run with kyverno 1.18.2 (`python -m unittest` in `compose/`): test_portable_observations
8 OK, test_floor_change 9 OK, test_priority_classes 16 OK, test_machinery_delivery 5 OK.
`composition.py --selfcheck` exited 0 on the first change. A later run failed at
"threat bump, after" with a feeds v2 vendoring refusal. The v3.3.0 selfcheck fails the same
way against the same estate, after the local driftwood clone moved to driftwood main 3f8943d
at 10:26 that day. So the cause is not this change. See Findings.

### Recompose of the three adopters (what the pin move costs)

Fresh GitHub clones in the scratchpad, so no adopter clone was touched. Parents sat at their
pins: platform v3.3.0 38089a68, nist v1.1.0 33a05df1, ico v3.0.0 9d092221, feeds 69c89b07,
insurer v1.0.0 632db22c. Each adopter was checked out detached at origin/main. Tools were
this branch. Kyverno 1.18.2.

| adopter | origin/main | composed/ change | pass 2 == pass 1 | verify after lane append, recomposed | same, not recomposed | v3.3.0 verify after lane append |
| --- | --- | --- | --- | --- | --- | --- |
| driftwood | 3f8943d | HEADER.yaml `after:` only, 1324a548 to 5ac37fc6 | yes | exit 0 | exit 0 | exit 1 |
| tuppence | 8d71d47 | HEADER.yaml `after:` only, 0014c055 to 7c112557 | yes | exit 0 | exit 0 | exit 1 |
| ludlow | 194accc | HEADER.yaml `after:` only, 3e6d5ae3 to c2abbaf0 | yes | exit 0 | exit 0 | exit 1 |

The v3.3.0 refusal is "comparison history does not match current source inputs". So the
cost per adopter is one pin move and one two-line diff in `composed/HEADER.yaml`.

The migrating recompose must come from a full clone. Measured on tuppence: a depth-1 clone
whose one commit already holds a lane commit cannot show the old lane bytes, so verify fails
there under this branch and under v3.3.0 alike. Once the recompose is committed, the identity
leaves the lanes out and depth no longer matters.

### Findings for the integrator

1. The hub's `verify/map-surface/map_surface.py` `LANE_ENV` regex needs a quoted value. It
   misses tuppence's and ludlow's `twin-sweep.yml`, which declare
   `OBSERVATION_LANE: observations/twin-sweep.jsonl` unquoted. Measured: the platform reader
   finds `['drift/samples.jsonl', 'observations/twin-sweep.jsonl']` for both, and the hub
   regex finds `['drift/samples.jsonl']`. Not changed here.
2. compose-check depends on the adopter's own tags, and is already red before this change.
   Tuppence main 8d71d47 records `since: 2026-09-24`, `since_by: v2.0.0 names openbao`. A
   tag-less depth-1 checkout, which is what compose-check uses, recomposes it under v3.3.0
   as `since: null` with a "no signed composed artefact names openbao" limit. So the next
   tuppence compose-check will show drift in `composed/evidence.json` whatever this ticket
   does.
3. `composition.py --selfcheck` at v3.3.0 fails against driftwood main 3f8943d ("two feed
   edges of feeds at v2 both vendor to composed/feeds/feeds/v2").
4. The adopters' `complete-feed-bump.sh` says it composes twice to reach a settled fixpoint
   that drops the transition. Since the comparison history, and now with a committed before,
   the second pass equals the first. The comment is stale. Not changed: ticket 130's builder
   holds the adopter repos.

### Fix round, 2026-09-24

The review passed but found a hole. The platform reader took `OBSERVATION_LANE` from every
workflow and from job and step env, scheduled or not, with no ADR-0024 list. The hub's
`verify/schedules/lane.py` `declared_lane()` reads only scheduled jobs, top-level and job env,
inside `schedules.py` `ALLOW_LIST`. So an adopter could take a source file out of the identity
by declaring it in a dispatched job, and no hub check would see it.

What changed, in the same two PRs:

- Platform `observation_lanes()` now reads a workflow only when its `on:` (or YAML 1.1's
  `True` key) has a `schedule:` entry with a `cron`. It reads each job's env as top level
  merged under job level, as `schedules.py` `_env()` does. It never reads a step env.
- Every declared path must sit inside `OBSERVATION_PATHS`, the platform's copy of ADR-0024
  point 3's list (`talk/truth.log`, `drift/samples.jsonl`, `talk/captures`, `observations`).
  Otherwise compose refuses and names the path, the workflow and the list. A prefix that is
  not a directory boundary (`observations-of-mine/x.jsonl`) is outside it.
- The hub's `verify/schedules/lane.py` now grades the copy. `check_platform_copy()` reads
  `compose/comparison_history.py` on platform `origin/main`, parses `OBSERVATION_PATHS` with
  `ast`, and fails unless it equals `schedules.ALLOW_LIST`. `schedules.py` says beside
  `ALLOW_LIST` that the two change together. Its selfcheck covers equal, missing file,
  unparseable file, missing constant, one path added, one path dropped and a non-literal.
- `compose/README.md` no longer says the after-state hashes every non-hidden source file. It
  names the lane rule, the list and the hub check.
- The `COMPOSER_READS` comment no longer says the composer reads `.yml`. Measured:
  `_namespace_facts` globs `root.rglob("*.yaml")` only. `.yml` stays in the tuple on purpose,
  and the comment now says why.

Decisions in the fix round:

5. Read exactly what the hub grades, no wider and no narrower. (delegated) A declaration the
   hub does not grade is not a promise any check holds, so it cannot take a file out of the
   identity. A dispatched job or a step env declares nothing here.
6. Refuse a scheduled path outside the list; do not drop it. (delegated) The hub's
   `declared_lane()` drops such a path silently and `schedules.py` fails it. The composer has
   no second checker behind it, so it refuses by name.
7. Do not copy the hub's fallback. (delegated) With nothing declared, `declared_lane()` grades
   against the whole ADR list. The composer excludes nothing then. An exclusion must be
   stated. A clock that writes an undeclared path turns compose-check red, which is the loud
   failure decision 1 chose.
8. The platform carries its own copy of the list, and the hub grades it. (delegated) The
   composer runs in the adopter's CI with no hub checkout, so it cannot import the hub's list.
   The hub already reads every unit's `origin/main`, so the drift check lives there, beside the
   list it compares with. It reads platform `main`, which is what the next tools release cuts.

Tests, red first. Platform, `.venv/bin/python -m pytest compose/test_comparison_history.py
-n0 -q`, with the new tests and the first build's `comparison_history.py`: 6 failed, 29
passed, 7 subtests passed. The six are the three cases of "a declaration the hub does not
grade excludes nothing" (a dispatched job, a push job, a step env in a scheduled job, each
declaring `party.yaml notes.txt` or `notes.txt`; each changed the identity away from the
baseline) and the three cases of "a scheduled lane outside the ADR-0024 list refuses by name"
(top level `drift/samples.jsonl party.yaml`, job env `notes.txt`, `observations-of-mine/x.jsonl`;
each composed instead of refusing). With the fix: 29 passed, 13 subtests passed. The existing
fixtures that declared a lane with no `schedule:` trigger now carry one. The changed-declaration
test now adds `talk/truth.log` instead of widening to `drift`, which is outside the list.

With kyverno 1.18.2, `python -m unittest` in `compose/`: test_portable_observations 8 OK,
test_floor_change 9 OK, test_priority_classes 16 OK, test_machinery_delivery 5 OK,
test_comparison_history 29 OK. `composition.py --selfcheck` from the platform worktree exited
0 with "SKIP: .estate-clone/{driftwood,nist,ico,feeds} absent", so it proved nothing here.
Ticket 136 owns its failure against driftwood's main.

Hub: `lane.py selfcheck` exit 0 and `schedules.py selfcheck` exit 0. `platform_copy()` against
platform `origin/main` today returns FAIL ("carries no OBSERVATION_PATHS"), and against this
branch's file returns PASS. `mypy verify/schedules/lane.py` reports the same 4 errors in
`schedules.py` with and without this change, none in `lane.py`.

Recompose, again on fresh clones (`recompose-134b` in the scratchpad), parents at the same
pins as above, kyverno 1.18.2, tools at this branch:

| adopter | origin/main | composed/ change | pass 2 == pass 1 | verify recomposed, after a lane commit | verify not recomposed, after a lane commit | v3.3.0 verify after a lane commit |
| --- | --- | --- | --- | --- | --- | --- |
| driftwood | b5eb409 | HEADER.yaml `after:` only, 1324a548 to 5ac37fc6 | yes | exit 0 | exit 0 | exit 1 |
| tuppence | 8d71d47 | HEADER.yaml `after:` only, 0014c055 to 7c112557 | yes | exit 0 | exit 0 | exit 1 |
| ludlow | 194accc | HEADER.yaml `after:` only, 3e6d5ae3 to c2abbaf0 | yes | exit 0 | exit 0 | exit 1 |

The `after:` values match the first build's, so narrowing the reader changed nothing for the
three adopters. Every lane they declare sits in a scheduled workflow's top-level env and
inside the list. A compose after the lane commit changed no file on any of the three.

Driftwood's main moved to b5eb409 since the first build. That commit is a real clock's lane
commit ("drift sample: five facts on an ephemeral cluster", `drift/samples.jsonl` only). Under
v3.3.0, verify at driftwood's main already exits 1 with "comparison history does not match
current source inputs". Under this branch it exits 0 without a recompose. This is the failure
the ticket names, live on one adopter today.

Findings from the fix round:

5. The hub's `schedules.py` `_allowed()` and `lane.py` `in_lane()` accept
   `observations/../party.yaml`, because they test a string prefix. The platform refuses any
   path with `..`. Not changed here.
6. The hub now holds three copies of the list: `schedules.py` `ALLOW_LIST`,
   `map_surface.py` `LANE_PATHS`, and the platform's. Only the platform's is graded against
   `ALLOW_LIST`. Not changed here.

### What remains

- The platform PR merges first. Until it does, the hub's lane check fails on the missing
  `OBSERVATION_PATHS`, so the hub PR merges after it.
- Waits on the owner: a signed tools release tag that carries this change.
- Then each adopter moves `.github/platform-tools-pin.yaml`, recomposes once from a full clone,
  and merges the two-line diff. The first lane commit after that is the live proof for Done:
  compose-check and the pre-tag verify stay green across it.

## Answer

Resolved 2026-09-24 by platform PR 39, shipped in tools v3.4.0, and hub PR 117.

1. `identity()` leaves out the paths each adopter declares in `OBSERVATION_LANE`, read only from
   scheduled jobs' top-level and job env and only inside the ADR-0024 list. A path outside the
   list refuses by name. The platform carries its own copy of the list, and the hub's
   `verify/schedules/lane.py` fails if it drifts from `schedules.ALLOW_LIST`.
2. **The live proof.** ludlow's `157701b` is a real scheduled drift-sample commit that touches
   only `drift/samples.jsonl`, on top of its v3.4.0 recompose. At `157701b`, verify exits 0
   ("re-renders byte-for-byte") and the recompose-and-diff shows no drift. Before ticket 134, the
   same shape refused with "comparison history does not match current source inputs" (driftwood
   run 35975270740 and ticket 131).
3. A v3.3.0 control on the same commit refused for an earlier reason, the vendored layout that
   ticket 136 changed, so it does not isolate this ticket. The proof rests on item 2.
