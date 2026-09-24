# 132 — The adopter gate does not read an acceptance record

Type: task
Status: resolved
Blocked by: none

## Question

Charted 2026-09-24 by the integrator. Ticket 129 defined the major acceptance record and taught
the hub's `verify/unreviewed-major` check to read it. Each adopter's own gate does not.

On the v3.3.0 rollout PRs (driftwood 40, tuppence 36 and 37, ludlow 33 and 34), the shift-left job
failed with "composed bump is major" for the added policy 5.0.0, although each PR carried
`accepted-majors/platform-5.0.0.yaml`. The integrator merged over that red on the owner's
acceptance of 2026-09-23. A required check that must be merged over on every accepted major
teaches nothing.

What this ticket owes:

1. Each adopter's `adopter-gate.py` (driftwood, tuppence, ludlow) reads `accepted-majors/` at the
   head it grades, with the same matching rule as the hub check (party, publisher and exact
   version), and admits a composed major only when every major it adds is accepted.
2. An unaccepted major still refuses, and a record for another party, publisher or version does
   not count. Tests for each.
3. The hub check and the adopter gates read one format; say where it is defined so the two
   cannot drift.

## Done

A pull request that adds an accepted major passes the adopter gate, and one that adds an
unaccepted major still refuses.

## Build, 2026-09-22

Four pull requests. No workflow file changed in any repository, and `cut-release.yml` was not
touched (ticket 131 owns it).

* driftwood PR 42: https://github.com/policy-as-versioned-driftwood/driftwood/pull/42
* tuppence PR 39: https://github.com/policy-as-versioned-tuppence/tuppence/pull/39
* ludlow PR 36: https://github.com/policy-as-versioned-ludlow/ludlow/pull/36
* hub PR 114: https://github.com/policy-as-versioned-flux/policy-as-versioned-flux/pull/114 (this record, the reader block, the drift check and two fold-agreement cases)

### What changed

1. Each adopter gate reads `accepted-majors/` at the head it grades. driftwood and tuppence read
   it at `--head-ref`. ludlow reads it at `--composed-head-ref`, or at `--new-ref` without it.
   `shift-left.yml` already passes those refs, so no workflow changed.
2. A composed major is admitted only when the pull request retires nothing and every major it adds
   is accepted for that adopter, for `platform`, at that exact version. The composed bump stays
   `major` in every output. driftwood's `--out` result and tuppence's summary carry an `acceptance`
   object. ludlow's rendered comment and tuppence's rendered body say "admitted" or "not admitted"
   and name the record and the commit it was read at.
3. The reader is one block, defined in the hub's `verify/unreviewed-major/unreviewed_major.py`
   between `# >>> major-acceptance reader >>>` and `# <<< major-acceptance reader <<<`. It holds
   `RECORD_DIR`, `RECORD_KIND`, `PUBLISHER`, `acceptance_from_text`, `acceptance_for` and a new
   `acceptance_records_at(repo, ref)`. Each gate carries it byte for byte. The hub's
   `records_at_served_ref` now calls `acceptance_records_at`.
4. The hub check `verify/unreviewed-major` reads each adopter's gate script at `HEAD` and fails the
   adopter whose block differs, naming the first line that does (`reader_drift`).
5. `verify/fold-agreement` gains two cases: `accepted` (4.0.0 arrives with a record for the gate's
   own party, expect adopt, composed major) and `misaddressed` (a record naming 4.0.1, expect
   refuse, composed major).
6. ADR-0011 gains a 2026-09-22 note. CONTEXT.md's "Major acceptance record" names the gates as
   readers.

### Decisions

1. **The composed bump is never lowered** (delegated). Admission is a verdict beside the bump, not a
   different bump. So fold-agreement's comparison of (verdict, composed) still reads one composed
   answer, and a reviewer still sees `major`.
2. **A retirement still refuses, record or not** (delegated). The record format names "the exact
   version string the composed window carries". A retired version is not carried, so no record can
   match it. Accepting a retirement would need a new format, and nothing asks for one.
3. **Every added major must be accepted; one unaccepted major refuses the lot** (delegated). The
   same rule as the hub check, where accepting 5.0.0 does not accept 4.0.0.
4. **Records are read at the head the gate grades, not at the served commit** (delegated). The
   gate grades a pull request. The record lands with the pull request that adds the major, as each
   v3.3.0 rollout's did, so the head is where it is. For driftwood and tuppence the head is GitHub's
   merge commit, which carries the base's records plus the pull request's.
5. **One reader, copied byte for byte and graded, not imported** (delegated). An adopter's CI cannot
   read the hub at run time, and a vendored module file would be a second format a reviewer has to
   diff by hand. A marked block inside the gate script keeps each repository self-contained. The hub
   check compares the served copies on every truth-surface run, so a copy that drifts is a named
   FAIL, not a silent disagreement. Change the block in the hub first, then copy it to the three
   gates in the same round of pull requests.
6. **The decision rule stays per gate; fold-agreement grades it** (delegated). `acceptance_verdict`
   and `acceptance_lines` are the same text in all three gates but sit outside the block, because
   the hub check does not use them. Two new planted cases make the three gates agree on the verdict
   with real cosign, or fail.
7. **This is not the override ADR-0011 bans** (delegated). No bump is recomputed or weakened, no
   workload is carved out, nothing expires. The record is the durable output of the "human review"
   the refusal always asked for: an owner's authorisation in the adopter's own reviewed, signed tree.
8. **Without an adopter directory and a head ref, nothing is admitted** (delegated). driftwood's and
   tuppence's older array-read paths have no adopter tree to read, so a major still refuses there.
   tuppence's Scenario E runs that path and still sees its designed refusal.

### Tests, red then green

How measured: each command below was run in this task, against real repositories, real platform
at tag v3.3.0 (commit `38089a68`) and real cosign v3.1.3.

* Hub, red first. `tests/test_unreviewed_major.py` and `tests/test_fold_agreement.py`, 10 new test
  functions appended before any code: `10 failed, 54 passed`. Green:
  `.venv/bin/python -m pytest tests/test_unreviewed_major.py tests/test_fold_agreement.py tests/test_truth_manifest.py -n0 -q`:
  `82 passed`. `tests/test_real_signature.py` (it imports fold_agreement): `31 passed`.
* `unreviewed_major.py --selfcheck`: 29 `ok` lines, 2 of them new. `fold_agreement.py --selfcheck`: OK.
* mypy (`twin tests conftest.py`): `Success: no issues found in 199 source files`.
* Each gate's `--selfcheck`, red first (`NameError: name 'acceptance_verdict' is not defined`), then
  green. New cases: an accepted record admits; no record, another party, another version, another
  publisher and a malformed record each refuse; a retirement refuses beside an accepted major; a
  second unaccepted major refuses; the records are read at the ref named and a working-tree file is
  not read. tuppence's `render-evidence-comment.py --selfcheck` gained two cases, red then green.
* Each adopter's harness gained scenario J: the real v3.3.0 rollout, base = the merge's first
  parent, head = the merge commit (driftwood `2fff19d`, tuppence `81ef938`, ludlow `c017bb7`), plus
  three variants committed on top of that head in a throwaway clone.
  * Red, before the gate change: driftwood `REFUSED: composed bump is major`, tuppence
    `FAIL: composed bump is major`, ludlow `REFUSE: composed bump is major -- ['5.0.0']`. Each harness
    exited 1 at J.
  * Green: `PLATFORM_REPO=.estate-clone/platform bash scripts/verify-adopter-gate.sh` (ludlow:
    `verify-adopter-gate.sh`) exits 0 in all three. J: accepted admitted, exit 0; record removed,
    naming 5.0.1, naming another party: each exit 1, naming 5.0.0. The other-party refusal names the
    record and whose it is.
* Base = the commit before the rollout merge, head = `origin/main`, gate from each ticket-132 branch,
  then the record removed and the record naming 5.0.1, each committed on top of `origin/main` in a
  throwaway clone (a scratch script, not committed):

  | adopter | base | head | accepted | removed | names 5.0.1 |
  | --- | --- | --- | --- | --- | --- |
  | driftwood | `01210a7` | `2fff19d` | exit 0, admitted | exit 1 | exit 1 |
  | tuppence | `79603fd` | `9333d86` | exit 0, admitted | exit 1 | exit 1 |
  | ludlow | `f299fd1` | `f70abce` | exit 0, admitted | exit 1 | exit 1 |

* Hub checks on a scratch estate (`PAVC_ESTATE_CLONE`), with the three adopters linked to their
  ticket-132 worktrees and every other unit linked to `.estate-clone`:
  * `verify-fold-agreement.sh`: exit 0. Six cases, three gates each; `accepted` all adopt with
    composed `major`, `misaddressed` all refuse with composed `major`.
  * `verify-unreviewed-major-in-window.sh`: exit 1 with 3 FAIL lines, all for the unaccepted 4.0.0
    that ticket 129 already reports. No drift line. Each 5.0.0 line is PASS.
* The same two hub checks on the unchanged `.estate-clone` (the gates without the block):
  fold-agreement exit 1, `case 'accepted': all three answered refuse`; unreviewed-major exit 1 with
  6 observed-false lines, 3 of them the drift line for each adopter. That is why the merge order
  below matters.

### Merge order

The three adopter PRs first, in any order among themselves. Then the hub PR. Merged the other way,
the hub's drift check and fold-agreement's `accepted` case go red on every truth-surface run until
the adopters land. The adopter PRs touch no workflow file, so the merging app can merge them.

### What remains

* **Nothing waits on the owner for this ticket.** The records the gates read already exist (ticket
  129's rollout). Accepting 4.0.0 for any adopter stays the owner's authorisation (ADR-0025) and is
  not part of this ticket; until then the hub check keeps its three 4.0.0 FAIL lines.
* **The first live observation is the next pull request that adds a major.** "Done" says such a
  pull request passes the adopter gate. The v3.3.0 rollout is replayed above through each gate's
  own CLI, in the flag shape `shift-left.yml` uses. No live CI run has yet graded a new accepted
  major, because none is proposed. The adopter PRs themselves move no policy version, so their own
  shift-left runs compose `none` and do not exercise the admission.

## Answer

Resolved 2026-09-24 by driftwood PR 42, tuppence PR 39, ludlow PR 36 and hub PR 114.

1. Each adopter gate reads `accepted-majors/` at the head it grades and admits a composed major
   only when every major it adds is accepted for that adopter, for platform, at that exact
   version. It still prints the bump as major, beside the record it admitted it on.
2. The reader is defined once, in the hub's `verify/unreviewed-major/unreviewed_major.py`
   between its `major-acceptance reader` markers. Each gate carries an exact copy, and the hub
   check fails any adopter whose served copy differs.
3. **Measured.** Over each adopter's own v3.3.0 rollout, the gate exits 0 with
   `acceptance.admitted: true` on `accepted-majors/platform-5.0.0.yaml`, and exits 1 with the
   record removed. On the hub, 5.0.0 grades PASS for all three adopters. 4.0.0 still grades FAIL,
   because the owner accepted 5.0.0 only.

The three adopter PRs also moved each tools pin to platform v3.4.0, re-derived tuppence's and
ludlow's twin signals, and recomposed once.
