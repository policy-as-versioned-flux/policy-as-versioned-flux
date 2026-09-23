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
