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

## Build, 2026-09-22

### The writer

The writer is `monkeypatch_session_signing_key` in `tests/test_intel_beat.py`, added by build
ticket 75 (commit c36e86c). It is a session-scoped fixture. It set `TWIN_SIGNING_KEY` when the
session-scoped `beat` fixture first built, and it undid the key only at session end. Its docstring
said the key was "undone after" the build. It was undone after the session. Under pytest-xdist a
session is one worker. So every test that ran on the same worker after the first `beat` test saw
the key, and `test_an_attestation_sidecar_accompanies_every_artefact` found an agent signature.

The writer is a test fixture, not real code. The harness writer in
`twin/invariants/harness.py` restores the key in a `finally`, and no code under `twin/` sets it.
So no production artefact was signed with a key nobody passed.

How I measured it:

- `pytest -n0 tests/test_intel_beat.py::test_the_sweep_artefact_is_derived_pinned_and_agent_signed
  tests/test_seam1_cli.py::test_an_attestation_sidecar_accompanies_every_artefact` on origin/main
  (ee2df61): 1 failed, 1 passed. The same two tests in the reverse order: 2 passed.
- `pytest -n4 --dist load tests/test_intel_beat.py tests/test_seam1_cli.py` on origin/main, three
  times: 1 failed, 58 passed each time.
- The ticket's own repro paired `test_invariant_suite.py` with `test_seam1_cli.py`. That pair
  holds no session key, which is why it did not reproduce.
- CI logs, read with `gh run view <id> --log-failed`. The test failed on worker gw0 in all six
  runs: 35783841943, 35783864673, 35791783996, 35784226120, 35840322690 and 35841750265. The
  logs run pytest with `-q`, so they do not list what gw0 ran before it. The CI flake depends on
  whether xdist's load schedule hands a `beat` test and this test to the same worker, beat first.

### The fix

- `tests/test_intel_beat.py`: the session fixture is gone. `beat` sets the key inside a
  `pytest.MonkeyPatch.context()` around its three CLI calls, and nowhere else. No beat test needs
  the key after the build. I checked the one that runs `twin verify`: without the key it still
  passes, 1 passed.
- `tests/test_seam1_cli.py`: the sidecar test removes the key itself with
  `monkeypatch.delenv(..., raising=False)`. It now passes with `TWIN_SIGNING_KEY=shell-key` set in
  the shell too (2 passed with the constraint-set test). The two `try`/`finally` writers in the
  same file used `del os.environ[...]`, which removed a key the shell had set instead of restoring
  it. Both now use `monkeypatch`.
- `conftest.py`: a new autouse guard, `_signing_key_does_not_leak`. After every test it compares
  `TWIN_SIGNING_KEY` with the value the worker process started with. If they differ, it restores
  the value and fails that test, naming it. Before the fixture fix, the guard named
  `test_the_sweep_artefact_is_derived_pinned_and_agent_signed` as the leaker (1 error, 2 passed).
  After the fix, the same pair gives 2 passed.

### Decisions

- delegated: fix the fixture that leaks, not only the test that sees the leak. Reason: a key that
  outlives its test signs any later artefact in the worker. The ticket's autouse delete alone would
  hide that from the one test and leave every other test exposed.
- delegated: the sidecar test removes the key with its own `monkeypatch`, not a file-wide autouse
  fixture. Reason: two other tests in `tests/test_seam1_cli.py` set the key on purpose. A per-test
  delete says what the test needs where the assertion is. `tests/test_signing.py` already uses the
  same pattern.
- delegated: a suite-wide guard in `conftest.py` that fails the leaking test. Reason: the ticket
  asks for the writer to be named. The guard names the next one at the test that leaks, on every
  run, instead of at a later test on some runs. It baselines on the value at import, because a
  function-scoped baseline starts after a session fixture has already set the key. The first
  version baselined per test and missed this leak; I measured that and changed it.

### Tests run

All run with `.venv/bin/python -m pytest -p no:cacheprovider` in the ticket worktree.

- Red, on origin/main: the ordered pair above, 1 failed, 1 passed. `-n4 --dist load` on the two
  files, three times: 1 failed, 58 passed each time.
- Green, on this branch: the ordered pair, 2 passed. `-n0` on `tests/test_intel_beat.py`,
  `tests/test_seam1_cli.py` and `tests/test_signing.py`: 80 passed. `-n4 --dist load` on the two
  files, three times: 59 passed each time.
- Full suite once, `-n4`: 1 failed, 2764 passed, 16 skipped. The one failure is
  `test_the_suite_is_green` on invariant 45, `flux_coverage_floor_is_still_reachable`. That is the
  standing red. It also failed in CI runs 35840322690 and 35841750265. The new guard failed no
  test, so no other test leaks the key.
- mypy over `twin tests conftest.py`: no issues found in 199 source files.

### What remains

The Done asks that CI shows the test passing on every run of a branch that changes no signing
code. That needs CI runs after this merges. The flake appeared in 6 of the runs named above, so
the integrator should watch `twin.yml` on the next few branches after merge. The guard would fail
any future leaker by name, on the test that leaks, not on this test. Nothing here waits on the
owner.
