# 70 — Full-system coherence: confirmatory

**What to build:** The last audit before the subject beats, and it should be **boring**. Continuous checks have been
carrying coherence since ticket 15; this confirms.

**If integration problems are discovered here, the early-detection design has failed** — and that
finding is more important than the fix. Record it as such.

**Blocked by:** 34, 56, 52, 58, 63, 68, 69

**Status:** done (2026-08-15)

**Reading list:** The invariant manifest; the pocket-org worksheet; all three seams. Constitution.

**The audit was not boring. It found two problems, and neither is the failure the brief
anticipated.** Read the findings before the checklist.

The brief says the early-detection design has failed if integration problems turn up here. On
finding 1 it did not, and an earlier draft of this ticket claimed it had. The code review caught
that and the claim is withdrawn: build tickets 64 and 65 both **recorded the shortfall in their own
files** and neither was green. What no ticket, guard or artefact carried was that the shortfall had
an **expiry date**. That is a narrower finding than "early detection failed" and it is still a real
one, because it is the difference between "we are behind" and "there are ten hours left". The
headline finding is time-critical and is now recorded rather than fixed, by the owner's decision.

- [x] Every invariant live, none pending, hashes intact.
      `./bin/twin verify`: `RESULT: 63 passed, 1 failed, 2 skipped (0 pending invariants, 2 skipped
      and not faked)`. All sixteen manifest entries read `state: live` and zero read `pending`.
      `invariant_bodies_match_manifest_hashes` passes, so every live body matches its pinned hash
      and the checks module matches its own. `hash_changes_are_authorised` passes, so no hash moved
      without a citation. `manifest_names_every_invariant` passes, so the constitution and the
      manifest still agree on the set. The one failure is
      `drift_window_is_actually_being_sampled`, which is finding 1 below.
- [x] Pocket-org worksheet green end to end.
      `pytest tests/test_pocket_org.py`: 8 passed. The harness guard
      `worksheet_matches_the_pocket_org` also passes inside `./bin/twin verify`. Every
      hand-computed line matches its artefact, and no line is pending past its build ticket.
      Confirmed absent, not discovered. This is the one part of the audit that was boring, and it
      is the part the plan predicted would be.
- [x] All three seams exercised: artefact CLI golden files, seam-2 properties, seam-3 skill scores.
      Run together rather than trusted separately: `pytest tests/test_pocket_org.py
      tests/test_seam1_cli.py tests/test_seam2_model.py tests/test_seam2_propagation.py
      tests/test_skills.py tests/test_record_skill_scores.py` — 118 passed. Seam 1 is the golden
      files, and `identical_pins_identical_bytes` re-checks them against the committed goldens
      inside `twin verify` ("12 artefacts identical across runs, processes, hash seeds and the
      committed goldens"). Seam 2 is the numerical and structural properties. Seam 3 is the skill
      harness, and `twin/skill-scores.jsonl` holds all seven real entries build ticket 56 recorded,
      each passing its own threshold at 1.0.
- [x] Every capability's depth grade is a computed checklist and the aggregate is published.
      The checklists were computed. **The aggregate was not.** See finding 2 below. Fixed here:
      `Capabilities.aggregate()` computes it, `./bin/twin grade` prints it
      (`aggregate: 39 of 69 across 12 capabilities, 0 at `full``, the `full` count itself counted
      rather than stated), and
      `tests/test_grades.py::test_the_published_aggregate_matches_the_computed_one` fails if
      `twin/README.md`'s published figure ever drifts from the computed one again.
- [x] Any problem found here is recorded together with the ticket that should have caught it.
      Two problems, recorded below and attributed: finding 1 to ticket 65, finding 2 to nobody, for
      the reasons each section gives. Both owning tickets are amended in place, following ticket
      34's precedent of editing the ticket that should have caught it rather than only naming it:
      ticket 65 gains a "Found later" note, and ticket 64 gains a note recording that it was
      **checked and cleared** of this one. Neither is a units defect, a derivation defect or a
      bookkeeping defect, which is what the three earlier audits found. Both are **horizon**
      defects: a fact everybody had, and nobody had the consequence of.
- [x] Extends the invariant suite; never weakens it. Any invariant change names the invariant and cites the authorising decision ticket.
      No constitutional invariant changed. The sixteen manifest entries are untouched, no body hash
      moved, and `hash_changes_are_authorised` passes clean. One **harness** guard was added,
      `flux_coverage_floor_is_still_reachable` (`twin/invariants/harness.py`), which is the class of
      addition ticket 34's precedent allows and ticket 56 used once already. It closes finding 1's
      detection gap. No existing check's body, hash, assertion or threshold was weakened.
      **Two things outside the suite were also tightened, disclosed here because "no invariant
      changed" would otherwise read as "nothing normative changed".** First, the constitution gains
      a section, "A pre-registered threshold needs a reachability guard, not only a liveness one",
      following build ticket 78's precedent of banking a durable lesson there. It adds no invariant
      and the manifest is unchanged, so `manifest_names_every_invariant` still agrees. Second, two
      loaders now refuse inputs they used to accept: `Window.load` refuses a cadence of zero, and
      `Protocol.load` refuses a coverage floor of 1, which is unsatisfiable under a gate that asks
      for coverage *above* it. Both were found by this ticket's own code review, both are
      strengthenings, and neither is reachable from any committed file.
- [x] Declares its depth grade as a **computed checklist** against the owning decision ticket's acceptance criteria — `full` is derived from the checklist, never asserted.
      This ticket ticks no capability criterion. `./bin/twin grade` reports 39 of 69 before and
      after it, now printed by the command rather than re-added by hand. An audit ticket that
      confirms coherence and fixes the gaps it finds has no owning decision ticket to grade
      against, which is the conclusion tickets 34 and 56 both reached for their own slices. This
      ticket's evidence is the run recorded under "Evidence" below, computed rather than typed.

## Finding 1: the shortfall was known, its expiry date was not

**Ticket that should have caught it: 65, and only just.** Not 64, and the first draft of this
section blamed both. See "What this finding is not", below.

`./bin/twin drift` reports **3 reachable samples against the 211 the declared hourly cadence owed
by 2026-08-15**. That is 1% coverage of an open 91-day window. The cause is simple.
`estate/driftwood/drift/window.yaml` declares the probe's operation as an hourly crontab line. **No
such crontab is installed on the machine, and no `probe.log` exists.** Every sample in the log is a
hand-run. The declared operation has never existed.

The consequence is not a slow instrument. It is a dead one:

- `estate/driftwood/drift/verdict.yaml` pre-registers a coverage floor of **90%**, with
  `requires_window_closed: true`.
- The window closes 2026-11-06. It owes 2184 samples in total, so the floor needs 1966 of them.
- Unsampled hours cannot be sampled later. From **2026-08-16T05:00Z** no probing schedule can reach
  the floor.
- After that moment `verdict.decide` returns `unmeasured` for `continuous-state` whatever happens
  next. That branch is build ticket 65's primary falsifier, and it sits on the critical path at
  `65 → 66 → 67 → 68 → 70`.

### What this finding is not

**Neither ticket was green and neither hid anything.** The first draft of this section claimed
"both tickets were green throughout", and that is false. Checked against the files:

- Build ticket 64 reads `Status: instrumented, **NOT MEASURING** — corrected 2026-08-10`. Its AC 2
  is `[~]`, part done, and states the gap in its own words: "**What remains is the schedule** — no
  crontab entry exists, and installing one is the operator's to run, not the twin's."
- Build ticket 65 reads `Status: pre-registered, **VERDICT PENDING**` and records the figure: "build
  ticket 64's window is 9% elapsed at **1% coverage** and closes 2026-11-06."

So early detection worked. The probe's silence was caught on 2026-08-10, a guard was built for it,
and both tickets carry the shortfall on their faces. **The audit discovered no hidden defect here.**

### What it is

Nothing computed that the shortfall would **expire**, or when. Every existing statement of it is a
rate — "1% coverage", "NOT MEASURING", "the probe has stopped" — and a rate reads as recoverable.
The floor is not recoverable, because an unsampled hour cannot be sampled later, and neither guard
was positioned to notice:

- Ticket 64's guard asks "did a sample land in the last day". A daily hand-run satisfies it at 4%
  coverage, and it hands the rest on in its own docstring: "coverage is ticket 65's problem".
- Ticket 65 reads coverage through `requires_window_closed: true`, so the first moment the protocol
  looks at the figure is the first moment nothing can be done about it.

**Ticket 65 is the one that should have caught it**, because it is the ticket that chose the floor.
Pre-registering a threshold against a sampled instrument commits you to a deadline whether or not
you compute it. Ticket 64 is not at fault: it declared a cadence, said plainly that nobody was
keeping it, and had no floor of its own to miss.

**Built here:** `twin/drift.py` `floor_reachable()` computes whether a floor can still be reached at
the declared cadence, and the last moment a probe could start and still reach it. The harness guard
`flux_coverage_floor_is_still_reachable` runs it against the live window and the live protocol's own
floor, on the wall clock, and fails once the floor is gone. `./bin/twin drift` prints the deadline
where the operator already looks. Tests are in `tests/test_verdict.py`, including
`test_the_live_instrument_cannot_reach_the_live_protocols_floor`, which pins the finding to a fixed
clock so it records the date permanently rather than re-deciding it against `now`.

**Not fixed: the probe itself.** The owner was asked during this audit whether to install the
crontab that `window.yaml` declares, and **decided not to**. The finding is recorded instead. So the
honest expected state is:

- `flux_coverage_floor_is_still_reachable` passes until 2026-08-16T05:00Z and fails from then until
  the window closes. That red is correct and is this finding, not a defect in the guard.
- Build ticket 65's `continuous-state` branch will close `unmeasured` on 2026-11-06.
- `point-in-time` therefore cannot be concluded either, because `twin/verdict.py` entails it only
  when both continuous branches are falsified. The elimination path stays closed, which is the
  protection build ticket 65 built working exactly as intended on the outcome it was built for.

The instrument still measured something. Three samples show no drift and no deploy across eight
days. That is not a result at the pre-registered floor and must not be read as one.

## Finding 2: the capability aggregate was the one figure nobody computed

**Ticket that should have caught it: arguably none, which is the finding.** Build ticket 03 is the
nearest owner and it is not really at fault: all five of its acceptance criteria are explicitly
per-capability and none of them mentions an aggregate. The figure belonged to no ticket until this
one's AC 4 asked for it, which is how it went unguarded through three earlier audits.

Build ticket 03 made every depth grade a computed checklist and refused a typed one. It did this per
capability. **The aggregate over the twelve capabilities was never computed anywhere.**
`./bin/twin grade` printed twelve rows and no total, so the published figure in `twin/README.md` was
a human re-adding twelve numbers.

That figure has gone stale twice, and this repository's own files record both times. It was carried
as "32" after it had moved, and build ticket 56 corrected it. It was carried as "35/64" after build
ticket 68 moved it, and the ticket 68 round corrected it. Each correction was made by hand, so each
correction used the mechanism that had already failed twice. `twin/README.md` claimed in the same
paragraph that "this table is its output, not a hand-kept count", which was true of the rows and
false of the total beneath them.

This is a smaller finding than finding 1 and it is the same shape. A mechanism was built for the
parts and never for the whole, and nothing watched the join.

**Built here:** `Capabilities.aggregate()`, printed by `./bin/twin grade`, and
`tests/test_grades.py::test_the_published_aggregate_matches_the_computed_one`, which reads the
figure back out of `twin/README.md` and fails on drift. The number itself was correct today at
39 of 69, so nothing is corrected. Only the mechanism is.

### And then this ticket did it again, in its own write-up

The most useful thing either finding produced. While documenting finding 2, this ticket carried two
hand-derived numbers that contradicted the code it had just written:

- The deadline was written as **2026-08-16T05:24Z** in five places across the ticket, the README and
  a test docstring. `floor_reachable()` returns **05:00Z**. The prose came from an ad-hoc
  calculation using a fractional sample target of 1965.6; the code uses 1966, because a sample
  target is a whole number of samples. **The code was right and the prose was in the same document
  that was arguing against hand-carried numbers.**
- `./bin/twin grade`'s output was quoted as ``none `full``` when it prints ``0 at `full```.

Both were caught by this ticket's own code review, not by re-reading. That is the argument for
finding 2's fix stated better than the fix states it: the failure is not carelessness, and asking
people to be more careful would not have caught either. The `full` count in `cmd_grade` is now
counted rather than stated, for the same reason.

## What the audit confirmed clean

Recorded so the two findings are not read as the whole picture:

- The pocket-org worksheet, every line, end to end. Continuous coherence since ticket 15 held.
- All sixteen invariants live, hashes intact, no unauthorised change, none pending.
- All three seams, run together in one command rather than trusted from separate rounds.
- The full suite, run before this ticket touched anything: 1355 passed and 1 failed, that one
  failure being the drift-probe staleness surfacing at pytest level through
  `test_the_suite_is_green`. Re-run after: 1366 passed, the same one failure.
- `mypy` clean across 139 source files.
- Ticket bookkeeping. The specific gap ticket 34 found once, real committed code against a ticket
  file still reading `ready-for-agent`, does not recur. 68 files read `**Status:** done` and the
  four that do not each carry an honest non-`done` status naming what is missing: 64
  ("instrumented, NOT MEASURING"), 65 ("VERDICT PENDING"), 66 ("PR CHANNEL NOT WIRED") and this
  ticket before it closed.

## The code review, and what it changed

Run on the finished work, two axes, before this ticket closed. It found more than cosmetics and the
record is here rather than folded silently into the diff.

**On the spec axis, it withdrew this ticket's own headline claim.** The first draft asserted "both
tickets were green throughout" and "the early-detection design has failed on its own terms". The
review read tickets 64 and 65 and showed both statements false. That correction is the reason
finding 1 now reads as it does, why ticket 64 carries a clearance note instead of an amendment, and
why the constitution's new section says what it says. **An audit that mis-attributes a finding is
worse than one that finds nothing**, so this is recorded as a finding against this ticket.

**On the standards axis, three real defects in code written an hour earlier:**

- `int(floor * total) + 1` computes a sample target one short whenever the product lands just under
  an integer in binary. `0.29 * 100` is `28.999999999999996`, so the target came out as 29 and
  29/100 is not above 0.29 — a floor this function would report as met and `verdict.decide` would
  refuse. The live `(0.90, 2184)` case was safe, which is exactly why a test now asserts the target
  against `decide`'s own comparison on floors chosen for being inexact.
- `Window.load` never validated the cadence, so a window declaring `every_minutes: 0` divided by a
  zero timedelta. `coverage`'s own guard against it was already unreachable-by-accident. Refused at
  load now, which is the one place all readers pass through.
- `Protocol.load` admitted `minimum_coverage: 1.0`, which no window can ever clear under a gate
  asking for coverage *above* the floor. It would have made the new guard permanently red on a
  window that had not opened.

Plus the two hand-carried numbers described under finding 2, and one guard-behaviour defect
described in its own docstring: an earlier draft returned a **pass** once the window closed, which
would have taken the suite fully green on 2026-11-06 over a measurement that produced no result.

## Evidence

```
./bin/twin verify
  RESULT: 63 passed, 1 failed, 2 skipped (0 pending invariants, 2 skipped and not faked)
  PASS flux_coverage_floor_is_still_reachable: floor 90% still reachable (ceiling 90.4%);
       3/1966 sample(s), start sampling by 2026-08-16T05:00:00+00:00 or it is gone
  FAIL drift_window_is_actually_being_sampled: finding 1, above.

./bin/twin grade
  ==> aggregate: 39 of 69 across 12 capabilities, 0 at `full`

./bin/twin drift
  window       10% elapsed, 3/211 expected samples (1% coverage)
  floor        90% still reachable (ceiling 90.4%); sampling must start by 2026-08-16T05:00:00+00:00

.venv/bin/python -m pytest -q
  1355 passed, 1 failed in 292.14s   (baseline, run before this ticket changed anything)
  1366 passed, 1 failed in 287.12s   (after: the same one failure, plus this ticket's 11 new tests)
  FAILED tests/test_invariant_suite.py::test_the_suite_is_green — the pytest-level surfacing of
  the identical drift-probe staleness ./bin/twin verify reports. Run before and after this
  ticket's own changes and identical each time, so it is unmoved by anything here.

.venv/bin/mypy twin tests conftest.py --ignore-missing-imports --warn-unused-ignores
  Success: no issues found in 139 source files
```
