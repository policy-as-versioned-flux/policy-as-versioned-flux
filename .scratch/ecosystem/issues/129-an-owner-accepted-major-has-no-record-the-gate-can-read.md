# 129 — An owner-accepted major has no record the gate can read

Type: task
Status: open
Blocked by: none

## Question

Charted 2026-09-23 by the integrator. Ticket 99 (resolved) built the check. Ticket 101 records
the missing input as an owner item. No open ticket owns the build.

`verify/unreviewed-major/verify-unreviewed-major-in-window.sh` FAILs with three lines on run 296.
Each adopter carries policy 4.0.0 in its composed window, and platform's signed evidence at the
adopter's pin records `bump.computed: major`. The check has no input for an owner's acceptance of
a major (`unreviewed_major.py:40-42`), so it clears only when the version leaves the window.
Moving to 5.0.0 does not clear it: `v3.2.0:computed-semver/evidence/5.0.0.json` reads
`{declared: major, computed: major}` too.

What this ticket owes:

1. A record an institution writes to accept a major for itself: which version, by whom, when, at
   the served ref, in the adopter's own repository. Decide its shape and home, and record why.
2. The check reads it and grades an accepted major PASS and an unaccepted one FAIL.
3. Tests for both, and a planted record for another institution or another version that does not
   count.

The acceptance itself is an owner decision per institution. This ticket builds the instrument; it
does not write an acceptance.

## Done

The check can tell an accepted major from an unreviewed one, from a record in the adopter's own
tree, and the tests hold both.

## Build, 2026-09-22

Hub only. No adopter repository changes. The check now reads an acceptance record from the
adopter's own tree at the commit it serves, and grades a carried major accepted or not.

### The record format

One YAML file per accepted major, in the adopter's own repository:

```yaml
# accepted-majors/platform-5.0.0.yaml   (the file name is a convention, not a key)
kind: major-acceptance
party: driftwood          # the institution accepting; must be the adopter whose tree holds it
publisher: platform       # whose policy version
version: 5.0.0            # the exact version string the composed window carries
accepted_by: <a name>     # who accepted it; any non-empty string
accepted_on: 2026-09-23   # the day, an ISO date
# any other key, such as a note or a pull-request link, is carried and ignored
```

The reader and the format live in `verify/unreviewed-major/unreviewed_major.py`
(`acceptance_from_text`, `acceptance_for`, `records_at_served_ref`). The ADR-0011 note of
2026-09-23 and a CONTEXT.md term ("Major acceptance record") record it.

### Decisions

1. **Home: `accepted-majors/` at the root of the adopter's own repository, read at the commit it
   serves** (delegated). The adopter is the risk-bearer (ADR-0015), so the acceptance is its own.
   The record lands only by a reviewed pull request (ADR-0002). The tag that signs the adopter's
   tree signs the record with it (ADR-0012). The check reads it with `git ls-tree` and `git show`
   at `HEAD`, the same served commit it reads `composed/evidence.json` at. A working-tree file, a
   staged file, a file outside `accepted-majors/` and a file in the hub are not read.
2. **Not in `party.yaml`, not in `composed/`** (delegated). Platform's `party/party_artefact.py`
   refuses an unknown top-level field (lines 185-188 at platform `origin/main`, read with
   `git show`), so a new key there is a change to platform's schema. `composed/` is the composer's
   output, re-rendered before a release is cut (driftwood `cut-release.yml`, ticket 18).
3. **One file per major, keyed by content, not by file name** (delegated). Separate files do not
   conflict when two acceptances land at once. The file name is only a convention.
4. **A record counts only for its own party, publisher and exact version** (delegated). A record
   for another institution, another publisher or another version counts for nothing. The FAIL line
   names each record that named the carried version and did not count, and each malformed record,
   so a near miss is visible rather than read as no record.
5. **4.0.0 before the rollout stays FAIL** (delegated, as the task set it). Accepting one major
   accepts no other. While 4.0.0 is still in a window it is red unless a record accepts 4.0.0
   itself. A 5.0.0 record can land before or with the rollout; it turns the 5.0.0 line PASS and
   leaves the 4.0.0 line FAIL. Once the rollout leaves only 5.0.0 in each window, and each adopter
   serves its 5.0.0 record, the check reads PASS for that adopter.
6. **`accepted_by` is not checked against who merged the record** (delegated). The record's
   authority is the reviewed merge that put it at the served commit. The check does not re-grade
   that merge. This is named in the module docstring and the ADR note.
7. **`accepted_on` is parsed, never compared with today** (delegated). A date check would make the
   grade move with the clock and not with the served tree.
8. **No adopter-side schema** (delegated). The format needs no code in any adopter. The hub reader
   is the only consumer. The check adds no new could-not-look reason, so the manifest row's
   `waits:` list is unchanged; only its note changed.

### Tests, red then green

* Red: `tests/test_unreviewed_major.py` with 12 new test functions (17 cases with parametrisation) appended before
  any code: `14 failed, 18 passed`. The three cases that already passed guard that a record for
  another version, another publisher, and an accepted major in one adopter never softens another
  adopter's FAIL.
* Green: `.venv/bin/python -m pytest tests/test_unreviewed_major.py -n0 -q`: `32 passed`.
  With `tests/test_truth_manifest.py`: `50 passed`.
* `unreviewed_major.py --selfcheck`: 7 new planted cases, all `ok`.
* mypy (`twin tests conftest.py`): `Success: no issues found in 199 source files`.
* Real estate, `verify/unreviewed-major/verify-unreviewed-major-in-window.sh`: still 3 FAIL lines,
  exit 1. Each now names the served commit and says no `accepted-majors/` record accepts 4.0.0.
* End to end on a scratch estate (`PAVC_ESTATE_CLONE`), real platform and real cosign: driftwood
  and ludlow cloned at the commits the estate serves, each with one planted fixture record
  committed on top, tuppence linked unchanged. driftwood's record accepts 4.0.0 for driftwood:
  PASS, naming the file, the served commit, `accepted_by` and `accepted_on`. ludlow's record
  accepts 4.0.0 for tuppence: FAIL, and the line names that record and why it does not count.
  tuppence has no record: FAIL. Exit 1, `2 line(s) observed false`. The planted records were
  fixtures in a scratch directory and are not acceptances.

### What remains

* **The integrator writes the three real records**, one per adopter, by reviewed pull request in
  driftwood, tuppence and ludlow, in the format above. The owner accepted policy 5.0.0 for all
  three on 2026-09-23. `accepted_by` names a person, so the integrator uses the name the owner
  gives for it.
* **The rollout to 5.0.0** moves each adopter's pin and re-composes its window. Until 4.0.0 leaves
  a window, that adopter's 4.0.0 line stays FAIL. This ticket does not do the rollout.
* Done holds for the instrument now: the check tells an accepted major from an unreviewed one,
  from a record in the adopter's own tree, and the tests hold both. The check turns green on the
  estate only after the records land and 4.0.0 leaves the windows.
