# 96 — The citable line says whether the twin may write to the world

Type: task (AFK)
Status: resolved
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

## Answer

**Built 2026-09-06** on `ticket-96-the-citable-line-says-the-mode`.

`talk/verify-all.sh` now writes `enact=<mode>` on every TRUTH line it emits, between `hub=` and
`units=`. The word is the mode `twin/enact_guard.py`'s own `enact_mode()` resolves — the same
ladder the guard itself obeys (`TWIN_ENACT_MODE`, then `twin/ENACT_MODE`, then its refusing
default) — so a reader of `talk/truth.log` can tell whether the run they are citing happened with
the enactment refusal on or off.

Proved by running the producer, not by reading it. The gate over a one-script fixture, once per
mode, and once with no override so the checked-in file decides:

```
TRUTH 2026-09-06T07:12Z run=local hub=5af3639 enact=development units=[fixture] pass=1 ...
TRUTH 2026-09-06T07:12Z run=local hub=5af3639 enact=operations units=[fixture] pass=1 ...
TRUTH 2026-09-06T07:12Z run=local hub=5af3639 enact=other-hand units=[fixture] pass=1 ...
--- ambient (twin/ENACT_MODE, no env): enact=development
```

`twin/ENACT_MODE` was not touched: it reads `development` by the owner's standing instruction, and
every mode above was reached with `TWIN_ENACT_MODE`.

**And then by the real gate, on the real surface.** The branch push fired `truth.yml`, which ran
all 109 scripts on the runner and printed:

```
TRUTH 2026-09-06T07:42Z run=114 hub=958a190 enact=development units=[driftwood=96f4d0d@main
feeds=b6eaa0a@main ico=6217c3a@main insurer=9e90e1b@main ludlow=d40b3fb@main nist=b9f5fff@main
platform=e27187e@main tuppence=f7c9f6a@main] pass=69 [observed=16 self=40 simulated=6 meta=7]
fail=11 skip=21 [never=9 waits=12] excluded=8 total=109 ceiling=90
```

Every count is identical to recorded run 113: the field arrived and moved no grade. That line is
NOT citable and is not in `talk/truth.log` — it is a branch run, which under ticket 100 records
nothing and said so ("THIS RUN CANNOT RECORD ITS TRUTH LINE"). It is quoted here from the Actions
log as ticket 100's note allows, and was not written by hand into the record.

### Where the field went, and why (delegated)

**Between `hub=` and `units=`.** Two reasons, and one of them is the ticket's own.

1. `run=`, `hub=` and `enact=` all say what the RUN was; `units=` onward says what it MEASURED.
   The field reads with its own kind, and a reader scanning the head of the line now has the whole
   provenance of the run in one place.
2. `live=1` and `fixture=1` are CONDITIONAL flags — they appear only when set. An unconditional
   field placed after them would have read as a third flag whose absence meant something. Putting
   it in the middle keeps the tail meaning "flags".

It also moved less of the parser surface, which was the ticket's stated consequence of the choice.
Of `verify-all.sh`'s two `$`-anchored selfcheck patterns only ONE names the seam the field was
inserted at (`hub=[0-9a-f]+ units=\[fixture\]`, line 112); the other starts at `pass=` and did not
move. Putting the field at the END would have broken both of those plus the two `fixture=1$`
patterns at lines 126 and 133 — four widenings instead of one. That is a consequence of the
decision, not its reason: the reading order is.

### What an OLD line without the field means (delegated)

**It means "this run does not say", and no parser may treat that as a mode.** `parse_truth` returns
`enact=None` for it, exactly the shape `split`, `skip_split` and `ceiling` already use for lines
that predate ticket 83. Nothing anywhere REQUIRES the field: a parser that did would refuse the 42
lines the log held on the day this landed, which is the record it exists to read. Reading a silent
line as `operations` would be worse than silence — it would assert an authorisation nobody gave.

`unknown` is a fourth word the producer can write, when it could not resolve the mode at all. It is
not a mode either; it is the absence of an answer, and `verify-truth-line.sh` leg 6 turns a
RECORDED `enact=unknown` red, because that is a broken `twin/`, not a mode.

### Reported, never graded (delegated)

Nothing added here makes any mode a failure, compares the mode to a record of who authorised it, or
invents a place where such a record would live. Which mode the estate runs in is the owner's
authorisation and ADR-0025 keeps authorisations with the owner. The alarm on a flip nobody recorded
is **ticket 97**, and the stronger answer that moves the declaration out of the agent's reach is
**ticket 87 item 3**. Both are open, both are the owner's, and this ticket deliberately answers
neither. The one thing leg 6 does turn red is `enact=unknown` on a recorded line, which is a claim
about the instrument and not about the authorisation.

### Which check grades it

- `talk/verify-all.sh --selfcheck` (leg 2 of `verify/truth-line/verify-truth-line.sh`) — the
  PRODUCER. It runs its own fixture gate once at each of `development`, `operations` and
  `other-hand` and asserts the emitted TRUTH line names the mode it ran at, plus the widened
  anchored pattern.
- `verify/truth-line/verify-truth-line.sh` leg 6 — the PARSERS. The field reads back as written
  for all four words, its neighbours (`hub=`, `units=`) and the trailing flags still read, a line
  predating the field reads as `None`, and a recorded `enact=unknown` is red. It also REPORTS how
  many recorded lines carry the mode, which is the checkable form of the disclosed limit below:
  `0 of 42 recorded lines name the mode; the newest, run 113, says nothing (it predates the
  field)`. That number is live and rises one per scheduled run, so it cannot go stale the way a
  sentence saying "none of them do yet" would.
- `tests/test_truth_manifest.py::test_parse_truth_reads_the_enact_mode_and_an_old_line_says_nothing_about_it`
  and `talk/truth_manifest.py selfcheck` — the seam.

### Every parser of a TRUTH line found, and what was done to it

The ticket's list of twelve was written on 2026-09-04 and had grown by three files. Found by
`grep -rl TRUTH` over the whole checkout rather than from the list.

| File | Reads | Change |
|---|---|---|
| `talk/verify-all.sh` | PRODUCER + 4 selfcheck patterns | writes the field; one `$`-anchored pattern widened; new three-mode leg; header and PASS sentence |
| `talk/truth_manifest.py` | `parse_truth`, `measured` | `enact` key (None when absent); format docstring; selfcheck asserts all four words and the old shape |
| `verify/truth-line/verify-truth-line.sh` | legs 4 and 5 via `parse_truth` | new leg 6; header and PASS sentence |
| `talk/build_deck.py` | `line_run`/`line_hub`, `\brun=(\S+)`, `\bhub=(\S+)` | none needed — proved by adding the field to its selfcheck's line and running it |
| `tests/test_build_deck.py` | `RUN1`/`RUN2` fixtures | `RUN2` now carries `enact=other-hand` and `RUN1` does not, so the deck is built and checked over a log holding both shapes |
| `verify/local-clock/local_clock.py` | `^TRUTH\s+(\d{4}-\d{2}-\d{2})T\S+\s+run=local\b` | none — anchored before the insertion point; proved by running |
| `verify/local-clock/verify-local-clock.sh` | runs the above | none; proved by running |
| `verify/can-record/can_record.py` (not on the list) | `startswith("TRUTH ")`, `+TRUTH `, `\brun=(\S+)` | none; proved by running |
| `verify/can-record/verify-can-record.sh` (not on the list) | plants TRUTH-shaped lines in throwaway repos | none; proved by running |
| `tests/test_can_record.py` (not on the list) | fixture lines | none; in the suite run |
| `verify/schedules/schedules.py` | names `talk/truth.log` as an observation path; parses no field | none; proved by running |
| `talk/verify-demo.sh` | `grep '^TRUTH ' \| grep -o 'run=[0-9]*'` | none; proved by running |
| `tests/test_truth_manifest.py`, `tests/test_local_clock.py` | fixture lines | new test in the first; second unchanged |
| `talk/verify-manifest.txt` | row description | says what leg 6 grades and what it refuses to grade |
| `talk/README.md`, `talk/RUNBOOK.md` | prose describing the line | both now describe the field and say it is not a grade |
| `verify/e2e/README.md` | prose; states no field format | none needed |
| `.github/workflows/truth.yml` | `grep '^TRUTH ' gate.out` | none; the whole line is copied verbatim |
| `talk/deck.md` | quotes run 22's line | none; run 22 predates the field |

### Red-first proofs

1. `.venv/bin/python -m pytest tests/test_truth_manifest.py -n0 -q -k enact`
   RED: `E KeyError: 'enact'` (`tests/test_truth_manifest.py:172`), `1 failed, 17 deselected`.
   GREEN: `18 passed in 0.04s` (whole file).
2. `bash talk/verify-all.sh --selfcheck`
   RED, four lines:
   `selfcheck: missing: ^TRUTH .* run=local hub=[0-9a-f]+ enact=[a-z-]+ units=\[fixture\] ...$`
   `selfcheck: a run at TWIN_ENACT_MODE=development printed no 'enact=development' on its TRUTH line`
   (and the same for `operations` and `other-hand`), then
   `FAIL: selfcheck: the instrument does not grade as documented (see above)`.
   GREEN: the PASS sentence, ending `... and a run at each of the three enactment modes prints
   that mode on its own TRUTH line`.

### One hardening, found in review of the diff (delegated)

The hub root reaches python through the ENVIRONMENT (`ENACT_HUB_ROOT`), not interpolated into a
quoted `-c` literal. A checkout under a path containing a quote would not have errored; it would
have quietly written `enact=unknown` on every line — a wrong answer wearing the shape of an honest
one, which is the same failure the exclusion-reason `xargs` bug had. Proved by copying the checkout
to a directory literally named `it's a hub` and running the gate there:

```
TRUTH 2026-09-06T07:23Z run=local hub=958a190 enact=development units=[fixture] pass=1 ...
```

### The recording rule (ticket 100)

No TRUTH line was hand-written into `talk/truth.log`; the log is untouched by this branch. The
change is to the PRODUCER, so `verify/can-record/verify-can-record.sh` was run and passes.

Map line: `- [96 — The citable line says whether the twin may write to the world](issues/96-the-citable-line-says-whether-the-twin-may-write.md) — every TRUTH line the gate emits now carries enact=<mode>, the mode twin/enact_guard.py was at while the run happened, so a reader of talk/truth.log can tell whether the run they cite had the enactment refusal on or off. The field sits between hub= and units= because run, hub and enact all say what the RUN was while units onward says what it MEASURED, and because live=1 and fixture=1 are conditional flags an unconditional field must not be mistaken for; that placement also moved one anchored selfcheck pattern instead of four. The word comes from enact_mode() itself, never re-derived in bash, so the line cannot disagree with the guard it describes; enact=unknown is written when it cannot be resolved at all, and a recorded unknown is red. REPORTED, NEVER GRADED: no mode is a failure, nothing compares the mode to a record of who authorised it, and nothing invents a place where such a record would live — that is ticket 97 and ticket 87 item 3, both open and both the owner's. A line predating the field parses with enact None, "this run does not say", which no parser may read as a mode and none may require: all 42 lines the log held on the day carry none. Graded by talk/verify-all.sh --selfcheck, which runs its own fixture gate once at each of the three modes and reads the emitted line back, and by verify/truth-line/verify-truth-line.sh leg 6, which grades the parsers and reports how many recorded lines name the mode — a live number rather than a disclosure that goes stale.`

## Waits on the owner

Nothing in this ticket. Two neighbouring questions stay open and are deliberately unanswered here:

- **Ticket 97** — the shape of the record that says who authorised the current mode, and whether an
  unrecorded flip should go red.
- **Ticket 87 item 3** — whether `twin/ENACT_MODE` should move out of the agent's reach entirely,
  which is the stronger answer and would close 97.

This ticket makes the mode VISIBLE on the citable line. Neither makes an unrecorded flip FAIL, and
this one deliberately does not either.

## Comments

**2026-09-04.** Half of the review's fix landed with the CI repair: invariant 48
(`enactment_is_propose_only_at_both_layers`) now reads the ambient mode before it forces
`operations` for its own calls, and names it on the detail line `./bin/twin verify` and the
`invariants` CI job already print. That restores a reader-visible report. It does not put the mode
on the citable line, which is what this ticket is for.
