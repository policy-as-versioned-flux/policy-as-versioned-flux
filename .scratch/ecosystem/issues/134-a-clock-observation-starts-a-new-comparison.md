# 134 — A clock observation starts a new comparison

Type: task
Status: open
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

## Build, 2026-09-22

Built on 2026-09-24 with ticket 133, in one platform PR:
[platform#39](https://github.com/policy-as-versioned-platform/platform/pull/39), branch
`ticket-134-observation-is-not-source`, based on platform main 38089a6 (v3.3.0). Hub record:
this branch's PR.

### What changed

- `compose/comparison_history.py` `identity()` leaves out the files under each
  `OBSERVATION_LANE` that the adopter's own `.github/workflows/*.yml` declare. It reads the
  value at top level, job and step `env:`, quoted or unquoted, split on spaces, as the
  workflows' own shell loops read it.
- A YAML file inside a lane stays in the identity. The composer reads every `*.yaml` in the
  tree for Namespaces and workloads (`_namespace_facts`), so a lane YAML file is a declaration.
- The sorted lane list is part of the digest. A changed declaration starts a new comparison.
  Before, `.github/` was hidden from the identity, so a lane edit changed nothing.
- A declared lane path that is absolute, contains `..`, or sits in `composed/` refuses by name.
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

### What remains

- The platform PR merges.
- Waits on the owner: a signed tools release tag that carries this change.
- Then each adopter moves `.github/platform-tools-pin.yaml`, recomposes once from a full clone,
  and merges the two-line diff. The first lane commit after that is the live proof for Done:
  compose-check and the pre-tag verify stay green across it.
