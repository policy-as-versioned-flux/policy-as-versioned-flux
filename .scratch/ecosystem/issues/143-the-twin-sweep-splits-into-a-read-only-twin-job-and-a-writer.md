# 143 — The twin sweep splits into a read-only twin job and a writer

Type: task
Status: resolved
Blocked by: 145

## Question

Graduated 2026-09-25 from grilling ticket 30, decisions 7, 8, 9 and 11 (delegated), and
ADR-0031. In each adopter (driftwood, tuppence, ludlow):

1. **The pin.** The sweep checks out the hub at the commit `twin/PIN.yaml` names, not at `main`.
   The adopter moves the pin by a reviewed PR. When the signed `twin/v0.1.0` tag exists, the tag
   replaces the commit.
2. **The split.** The twin job holds `contents: read` and runs the twin code. It hands its
   observation line and its proposal to the writer job as an artifact. The writer job has no hub
   checkout, no twin code and inline shell only; it validates every path in the artifact against
   the observation lane and the proposal paths before it writes.
3. **The network dial.** Every download is pinned by hash, including `pip install pyyaml`.
4. **The rung gate.** The writer's steps follow the rung the adopter's selection policy selected
   (ticket 145): baseline and restricted append an observation and propose; quarantine appends an
   observation only; isolated runs the twin job and writes nothing.
5. **A refused directory is not a move.** tuppence's and ludlow's `.github/scripts/twin-sweep.py`
   record a loader `ModelError` (exit 1) as `moved: true`, review required. Record it as a render
   that could not be made.

## Notes

Blocked by 145 for item 4 only; items 1, 2, 3 and 5 can land first. Adopter tags wait for the
owner's authorisation. Ticket 142's check grades the result.

## Comments

**2026-09-26, owner-instructed.** The owner wrote on 2026-09-25: "i'm afk you have all the approvals
you need to deliver". That authorises feature branches and pull requests in the hub and the estate
repositories; merges, pushes to main, tags, releases and dispatches stay with the integrator.

**What this PR builds (143a: items 1, 2, 3 and 5; item 4 waits).** Three adopter PRs on branch
`ticket-143a-twin-sweep-split`: driftwood #49, tuppence #48, ludlow #45, plus this record:

1. *The pin.* `twin/PIN.yaml` gains `hub_commit: 9c3b1f22dcdafebc0333557f76655014e4be216b`, hub
   `origin/main` when the adopters were built. The twin job reads it at run time with inline shell
   (exactly one `hub_commit:` line, 40 hex), checks the hub out at that commit with
   `actions/checkout` `ref:`, and refuses to run if `git rev-parse HEAD` of the hub checkout is any
   other commit. `ref: main` is gone from all three sweeps. The emitter's `check_twin_pin`
   (`twin_version` against hub `twin/VERSION`) is untouched. The adopter moves the commit by a
   reviewed PR. When the signed `twin/v0.1.0` tag is cut, the tag replaces the commit in the pin and
   in the checkout, and `tag_cut` flips; PIN.yaml says so beside the field.
2. *The split.* Job `twin` holds `contents: read` and nothing else (the workflow default is
   `contents: read` too). It checks the adopter out first at the top of the workspace, reads the
   pin, checks the hub out at it, moves the adopter under `hub/.estate-clone/<adopter>` where the
   emitter walks up to the `twin` package, runs the emitter and (driftwood) the lookup, and uploads
   ONE artifact `twin-sweep-handoff`: `observation.jsonl` (one line) and, on driftwood when the
   render moved, `proposal/twin/forward-intel/v1/feed.json` and `proposal/twin/signals.yaml`. Job
   `write` (`needs: twin`) holds `contents: write` and `id-token: write`, plus `pull-requests: write`
   on driftwood; it has no hub checkout and runs no program from any checkout (git, gh, jq, sed,
   curl, sha256sum and shell only, so the hub's `_PROGRAM` regex finds nothing in it); it downloads
   the artifact into `runner.temp`, then validates before writing: every file in the artifact is
   the observation or a declared proposal path or the run fails naming the file; the observation
   is exactly one JSON object line with the exact key set, `.run` equal to `GITHUB_RUN_ID`, the
   adopter's own `org` and `feed`, a UTC `swept_at`, `adopter_ref` a commit this repository has
   (`git cat-file -e`), and the hub commit equal to the `hub_commit` read from the WRITER'S OWN
   checkout of `twin/PIN.yaml`, not from the artifact (`twin_ref` on driftwood; `hub_ref` and
   `twin_pin.hub_commit` on tuppence and ludlow, whose lines also carry a recorded `status`,
   `emitter_exit` in {0,1,3}, `moved` boolean or null and text `detail`). Only then does it append
   the line, propose (driftwood: copies the two proposal files onto a `twin/forward-intel-<date>`
   branch, commits `-S`, pushes, `gh pr create`, returns to the default branch), and run the same
   observation-cage shell as before, which commits gitsign-signed and pushes `HEAD:main`. On
   tuppence and ludlow the last step re-raises the recorded `emitter_exit` from the validated line,
   so a `could_not_look` still ends the run red and the recorded line is unchanged in shape (it
   gains only what PIN.yaml gained, `twin_pin.hub_commit`); `verify/schedules/clock-owners.yaml`
   keeps mapping those reds to ticket 144.
3. *Hash-pinned downloads.* Every `uses:` is a full commit with the version beside it
   (`actions/checkout` 11d5960a v4.4.0, `actions/upload-artifact` ea165f8d v4.6.2,
   `actions/download-artifact` d3f86a10 v4.3.0, each resolved from the `v4` tag on 2026-09-26);
   `pip install --quiet --require-hashes -r .github/requirements/twin-sweep.txt` installs
   `pyyaml==6.0.3` from a file generated from PyPI's JSON (73 sha256 hashes, one per published
   file); the writer needs no pip at all. gitsign stays a checksummed binary: driftwood keeps its
   `GITSIGN_VERSION`/`GITSIGN_SHA256` env (a test fails when it disagrees with the shared action);
   tuppence and ludlow read the shared action's pin with `sed` as data, because its `install.sh` is
   a program from the checkout.
5. *A refused directory is not a move.* tuppence's and ludlow's `.github/scripts/twin-sweep.py`
   `classify()` records emitter exit 1 as `review_required`, `moved: true` only when the emitter's
   stdout carries its own `--check` sentence ("is not what the overlay renders") and stderr carries
   no traceback; a traceback (the loader's `ModelError`), a `REFUSED:` line or a bare exit 1 is
   `could_not_render`, `moved: null`, with a detail saying nothing is proposed. `gate` still exits
   1 for it, so the run stays non-green. The test asserts the sentence is still in the adopter's
   real emitter. `record --handoff DIR` writes the line for the writer and leaves the ledger alone.

**Not built here: item 4, the rung gate.** It waits for ticket 145 to be served (the platform's
twin-agent dial table and the adopter's selected rung). The writer's steps therefore still run at
the loosest rung on every run, which is what they did before this PR.

**Decisions made while building (delegated, ADR-0025).**
- *The adopter is checked out first at the top of the workspace and moved under the hub after the
  hub checkout.* The pin must be read before the hub is checked out at it, and `actions/checkout`
  deletes the contents of a target directory that is not already a checkout of the same
  repository, so nesting the adopter under `hub/` before `hub/` exists would lose it. A `mv` of a
  finished checkout is cheap and the step then proves the hub is at the pin.
- *The twin job's checkouts carry `persist-credentials: false`.* It pushes nothing.
- *The observation line moves whole through the artifact; the writer rebuilds nothing.* The line
  is produced where the twin code is and validated field by field where the token is; a writer
  that composed its own line from job outputs would be a second author of the record.
- *The composed identity moved, so each adopter PR carries a recompose commit.* The comparison
  identity hashes every non-hidden file, `twin/PIN.yaml` included; `shift-left.yml`'s
  compose-check would otherwise read drift. The recompose is its own commit after the change, as
  tickets 130 and 134 did it, from a workspace laid out as compose-check lays it (platform v4.0.0,
  nist v1.1.0, ico v3.0.0, feeds 69c89b07, insurer v1.0.0, tools v4.0.0 verified by gitsign).
- *tuppence's and ludlow's READMEs are updated* (non-hidden, but the identity had already moved).
- *driftwood's `twin/verify-twin-sweep-moved.sh` reads job `twin`*, the job that carries the step it
  grades.
- *Only the sweep is changed.* Other adopter workflows still pin `actions/checkout@v4` by tag; that
  is outside this ticket and is listed for the integrator.

**Measured offline, 2026-09-26** (each on a throwaway estate under the hub worktree whose adopter
clones serve the branch head as `origin/main`, so `schedules.py` and `lane.py` graded the branch
as the served ref; hub at 9c3b1f22):
- `verify/schedules/verify-schedules.sh` (offline): `PASS: <adopter>/twin-sweep.yml job twin:
  caged as far as this checker reads ... 3 program(s) it runs from its checkout are not read here
  ... (no contents: write)` (2 programs on tuppence and ludlow) and `PASS: <adopter>/twin-sweep.yml
  job write: caged -- no inline shell step in this job stages a declaration or mints a signed
  artefact, and every step is inline shell or an inert uses: action this checker read in full` on
  all three; selfcheck ok. The live half SKIPs offline as it does on main.
- `verify/schedules/verify-lane.sh`: PASS.
- `actionlint` 1.7.12 with shellcheck: clean on all three workflows (as on main).
- driftwood `twin/verify-twin-sweep-moved.sh` in that estate: 3 PASS (fresh copy moved=false,
  stale feed and stale lookup moved=true), 1 SKIP (the moved path has not fired live), as on main.
- driftwood `.github/tests`: 11 OK; tuppence and ludlow `tests/test_twin_clock.py`: 10 OK each,
  including the writer's validation refusing 22 (driftwood) and 18 (tuppence, ludlow) wrong
  handoffs by name and admitting the right ones, the pin step refusing a doubled, short or
  branch-named pin, and item 5's four exit-1 shapes recorded as `could_not_render`.
- `pip download --require-hashes -r` of the requirements file: accepted (the interpreter's own
  wheel among the 73 hashes).
- Recompose: pass 1 changed `composed/HEADER.yaml` only; pass 2 byte-identical.
- CI on each adopter PR (shift-left and compose-check, which run these tests) is part of the
  measurement and is reported in the build result. The first scheduled run after merge is the
  live proof: on driftwood a green run with a new observation line whose `twin_ref` names the
  pinned commit; on tuppence and ludlow a red run whose recorded line is `could_not_look` at the
  pinned commit, as today.


## Answer

**2026-10-18, delivered record reconciled.** The five Question items are served in all three
adopters. Each twin checks out hub commit `5bc47331a536476f3580542be794908f5053f816`
from its own `twin/PIN.yaml` and checks the resulting HEAD; its declared twin version is 0.1.0.
The twin job has read-only contents permission. The inline-shell writer has no hub checkout or
twin code, validates the artifact's paths and the whole observation against its own pin, then
appends that observation unchanged. Action commits, pip requirements and the gitsign download
are hash-pinned. Both jobs read the adopter's selected, priced agent-cage rung: baseline and
restricted allow the existing proposal route, quarantine appends observations only, and isolated
writes nothing. Driftwood proposes only when the render moved; tuppence and ludlow remain the
observation-only instruments described above. Their classifier distinguishes a genuine changed
render from a refused directory or loader traceback, recording the latter as
`could_not_render`, `moved: null`, without a proposal. Ticket 145's selected-rung dependency is
resolved; no later parser/emitter incompatibility was found at these served pins.

The first scheduled runs after the split were on 2026-10-04, all on main, attempt 1, with both
`twin` and `write` jobs successful. Their actual checkout, validated handoff, single appended
ledger line and original observation commit agree:

- [Driftwood run 37204534128](https://github.com/policy-as-versioned-driftwood/driftwood/actions/runs/37204534128),
  source `a1707bb7d13447edaeba85f26c3240cd8884a415`, original
  [2e04b9803a57cd0d61afa3ef2deeca74f749d969](https://github.com/policy-as-versioned-driftwood/driftwood/commit/2e04b9803a57cd0d61afa3ef2deeca74f749d969).
- [Tuppence run 37204848859](https://github.com/policy-as-versioned-tuppence/tuppence/actions/runs/37204848859),
  source `55bf5aa14d80f6cee4c524394d08b244b1461846`, original
  [7b3b0bd7aeb0895a0557a0cb8de6b17bdaba91f2](https://github.com/policy-as-versioned-tuppence/tuppence/commit/7b3b0bd7aeb0895a0557a0cb8de6b17bdaba91f2).
- [Ludlow run 37205184454](https://github.com/policy-as-versioned-ludlow/ludlow/actions/runs/37205184454),
  source `179e4e0d8e754044b07a65933754244352e28ec5`, original
  [035c9b991c5e2d69134737db7967437a62d6f288](https://github.com/policy-as-versioned-ludlow/ludlow/commit/035c9b991c5e2d69134737db7967437a62d6f288).

All three observations name the same pinned hub commit above and report an unchanged render,
`moved: false`; tuppence and ludlow record emitter exit 0. The September 26 final paragraph is
retained as its then-current expectation: those adopters could not look at that time. Their
later successful first scheduled renders fulfill the pinned handoff behavior; reproducing the
old red outcome with changed inputs would discard the actual observation. Official schedule
metadata, both jobs' runtime logs, split/source ancestry, exact ledger-prefix-plus-one-append
proofs and original raw commits are frozen in the October 18 ticket143 contract audit. Each
original signature was separately verified with the genuine production-default gitsign
certificate claims and Rekor, including its repository, workflow, main ref, source and schedule
trigger. That authentication is of the original commit, not a current-schema full historical
delivery receipt.

Recorded [TRUTH run 435](https://github.com/policy-as-versioned-flux/policy-as-versioned-flux/actions/runs/39169162198)
grades `verify/twin-cage/verify-twin-cage.sh` PASS for the three served workflows and their priced
rungs. This is the current check supporting this record, not an invented owned-PASS claim.
Run 435 remains FAILURE with its other four failing rows; the schedules row still fails for
feeds/fetch. This ticket's reconciliation does not dispose of that failure or change a grade.
The live moved path remains unobserved and its separate capture remains SKIP. The future signed
`twin/v0.1.0` tag is still absent, so its replacement of the commit pin remains conditional.
Ticket 142's local live environment resistance is stopped and unmeasured, as the current
capture's LIMIT states. Neither a moved event, a new tag nor a live actor probe is manufactured
to close this delivered split-and-handoff task.
