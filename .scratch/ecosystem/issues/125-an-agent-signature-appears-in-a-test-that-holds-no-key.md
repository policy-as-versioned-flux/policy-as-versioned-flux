# 125 — An agent signature appears in a test that holds no key

Type: task
Status: open
Blocked by: none

## Question

Charted 2026-09-23 by the integrator. It is unfixed.

`tests/test_seam1_cli.py::test_an_attestation_sidecar_accompanies_every_artefact` asserts
`sidecar["agent_signature"] is None`, because the test environment holds no `TWIN_SIGNING_KEY`.
On CI it sometimes finds a signature instead. It failed in four `twin.yml` runs on 2026-09-22:
35783841943, 35783864673 and 35791783996 on the ticket 114 branch, and 35784226120 on the ticket 112
branch. Later runs on the same branches passed. The four runs had no change to `twin/sign.py`,
`twin/attest.py` or the test.

So something in the same pytest-xdist worker sets `TWIN_SIGNING_KEY` and does not restore it, or
reads a stale value. Every writer found by `git grep` restores the variable: the monkeypatch
fixtures, the two `try`/`finally` blocks in `tests/test_seam1_cli.py`, and
`twin/invariants/harness.py` lines 2104 to 2199. Running `tests/test_invariant_suite.py` and
`tests/test_seam1_cli.py` in one process did not reproduce it (66 passed).

What this ticket owes:

1. Find the writer. The likely route is the xdist schedule: run the failing file under
   `-p xdist -n 4 --dist load` with a fixed `-p randomly` seed if the plugin is present, or bisect
   by running each other test file first in one worker.
2. Make the failing test independent of the order: an autouse fixture that removes
   `TWIN_SIGNING_KEY` for the tests that assert its absence.
3. If the writer is real code and not a test, that is a defect in its own right: a key that leaks
   into a later artefact signs it with a key nobody passed.

## Done

The writer is named, the test cannot see a key it did not set, and CI shows the test passing on
every run of a branch that changes no signing code.
