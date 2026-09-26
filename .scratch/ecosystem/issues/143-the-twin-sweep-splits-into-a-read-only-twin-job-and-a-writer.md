# 143 — The twin sweep splits into a read-only twin job and a writer

Type: task
Status: claimed
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
