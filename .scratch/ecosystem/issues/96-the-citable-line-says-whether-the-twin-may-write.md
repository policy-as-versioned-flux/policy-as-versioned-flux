# 96 — The citable line says whether the twin may write to the world

Type: task (AFK)
Status: open
Blocked by: none

## Question

`twin/ENACT_MODE` decides whether the twin may merge and may push to an enactment repository, and
the estate's one citable record does not say which mode produced a run. Carry `enact=<mode>` on
the TRUTH line `talk/verify-all.sh` emits, so a reader of `talk/truth.log` can tell whether the
run they are citing happened with the enactment refusal on or off. Done = every TRUTH line
carries the mode, every parser of that line still passes, and a run under each of the three modes
prints the mode it ran at.

## Notes

Charted 2026-09-04 from the round-2 review of the hub CI repair (PR 26, branch
`ci-2026-09-04-the-hub-tests-itself`); the record is `.scratch/ecosystem/CI-2026-09-04.md`.

**Why it is not a two-line change, which is why it is a ticket and not a commit.** Twelve files
parse a TRUTH line: `verify/local-clock/verify-local-clock.sh`, `verify/local-clock/local_clock.py`,
`verify/schedules/schedules.py`, `verify/truth-line/verify-truth-line.sh`, `verify/e2e/README.md`,
`tests/test_truth_manifest.py`, `tests/test_local_clock.py`, `tests/test_build_deck.py`,
`talk/build_deck.py`, `talk/verify-all.sh`, `talk/truth_manifest.py` and `talk/verify-demo.sh`.
Two of `verify-all.sh`'s own selfcheck patterns are anchored with `$` (lines 112 and 118 as of
`2048ee5`), so a new trailing field breaks them until each is widened deliberately.

**Decide where the field goes.** `live=1` and `fixture=1` already sit at the end and are
conditional. A mode field is unconditional, so it may read better beside `hub=` than after the
optional flags. That choice is the ticket's, and it decides how much of the parser surface moves.

**Do not grade the mode here.** Which mode the estate runs in is the owner's authorisation, and
ADR-0025 keeps authorisations with the owner. This ticket makes the record say what was true. It
does not make a mode a failure. Ticket 97 is the one that adds an alarm, and it alarms on a flip
nobody recorded rather than on a mode.

## Comments

**2026-09-04.** Half of the review's fix landed with the CI repair: invariant 48
(`enactment_is_propose_only_at_both_layers`) now reads the ambient mode before it forces
`operations` for its own calls, and names it on the detail line `./bin/twin verify` and the
`invariants` CI job already print. That restores a reader-visible report. It does not put the mode
on the citable line, which is what this ticket is for.
