#!/usr/bin/env bash
# Beat (eco-system ticket 59): "ticket Status: is derived from a named check."
#
# NORTH-STAR §5, fourth bullet: "Ticket `Status:` is derived from a named check, in the way
# `twin grade` already derives depth from `twin/capabilities/*.yaml`." twin/grades.py's rule is
# that `full` cannot be TYPED -- it is computed from the owning ticket's acceptance criteria, and
# a stated grade that disagrees with the computed one is refused. No such rule existed for a
# ticket. The ambition review of 2026-08-31 counted sixteen free-typed `Status: open` lines
# (M14); by 2026-09-06 eight tickets free-typed a qualification after the word instead.
#
# THE SERVED ARTEFACT is the `Status:` field of each `.scratch/ecosystem/issues/*.md` -- the line
# a reader, the wayfinder's frontier scan and every review take as the state of the work. THE
# OPERATION that reaches it is a builder typing it. This script is the derivation that field is
# supposed to have.
#
# WHAT IT DERIVES FROM. Not the ticket's prose, and not a capture's last line. talk/verify-all.sh
# grades a script by its EXIT CODE, and a capture's last line is only the reason -- 29 of the 107
# captures committed on 2026-09-06 end in the continuation of a multi-line `PASS:` sentence, and
# a prototype that read grades out of them named two tickets wrongly for exactly that reason. So
# the run now records what it graded: `talk/captures/_grades.tsv`, one row per discovered script,
# written by talk/verify-all.sh inside the observation lane the cage already commits, opening
# with that run's own TRUTH line. THAT FILE IS THE OBSERVATION, and it is refused unless the line
# it opens with is the newest one talk/truth.log records.
#
# THREE OUTCOMES, in this order, because a FAIL must not be hidden behind a could-not-look:
#
#   1. THE RECORD, which needs no run. Every ticket carries exactly one `Status:` line, and its
#      value is exactly one word of docs/agents/issue-tracker.md's vocabulary -- open, claimed,
#      prepared, resolved, closed -- with nothing after it. A `resolved` ticket has an `## Answer`
#      section; a `closed` one carries a dated paragraph instead, because a ticket taken out of
#      scope has no answer to append and demanding one would make the record write a fake.
#      Any fault here is a FAIL, on any day, run or no run.
#   2. THE DERIVATION, which needs the run. For each `resolved` ticket, the checks it names in its
#      Answer are looked up in the grade table: any FAIL derives `regressed`, otherwise a PASS
#      derives `resolved`, only could-not-looks derive `resolved-unobserved`, and no check the
#      table carries derives `resolved-ungraded`. A ticket written `resolved` that derives
#      `regressed` is a FAULT unless the file carries a DATED paragraph, in a section AFTER its
#      `## Answer`, naming that red check IN BACKTICKS. Three shapes are refused, each with a
#      test: a dated paragraph INSIDE the Answer (the claim cannot acknowledge itself), one that
#      PREDATES the Answer (a `## Comments` note sits above it in this record and would have
#      disposed of a red found long afterwards), and a bare mention or a URL rather than a
#      backticked path. Ticket 80 was defeated this morning by a check that took the fix written
#      into the text it graded as input.
#   3. NO GRADE TABLE YET -> exit 3, SKIP. `talk/captures/_grades.tsv` is written by
#      talk/verify-all.sh and committed by the clock's cage, so it arrives on the first scheduled
#      run of the default branch after this lands. That is a `waits:` in the manifest, not a
#      `never:`: the estate's own state has not arrived, and the day it does this looks.
#
# WHOSE CHECK IS IT (review, 2026-09-06). Naming a check in an Answer is not owning one. Against
# run 135's REAL grade table the first version named twelve tickets, and nine of them were
# discussing somebody else's red -- ticket 80 quoting 89's check while correcting the record,
# ticket 83 citing driftwood's sweep script as an example of a manifest class, four tickets
# mentioning `verify-schedules.sh` where ticket 57's own Answer says in as many words that
# "ticket 56 owns" the reason it is red. Writing an acknowledgement into each would have put nine
# false ownership statements into the record. Prose cannot separate them; GIT CAN. A check is
# owned by the tickets whose commits touched its file (`git log --full-history -- <path>`, in the
# unit's own repository for a `.estate-clone/` path). Reading the estate's PLURAL subjects is part
# of that rule, not a detail: `Tickets 62 and 77: ...` is the commit that added
# verify-branch-refs.sh and `Tickets 56 and 85: ...` added verify-schedules.sh, so a scan that
# read only `ticket NN` reported both unowned and told four tickets that a check they had built
# was not their own (re-review R2-1). With the plural read the narrowing lands on SEVEN tickets --
# 38, 56, 62, 77, 85, 89, 99 -- and leaves seven red rows named by tickets that own none of them
# (57, 72, 73, 80, 83). The reading itself is ticket 102's `ticket_numbers`, imported from
# verify/cited-truth/cited_truth.py -- one reading for the estate, no fork -- with
# `shared_contract()` declaring executably which of its behaviours this check is built on. A red check a ticket does not own is COUNTED. A check no commit names
# any ticket for is UNOWNABLE and also counted -- inferring an owner from silence is how a false
# ownership statement gets written.
#
# THE ONE-RUN LAG, stated because it would otherwise be found (review F4). talk/verify-all.sh
# writes the grade table AFTER its script loop, so when this script runs inside run N the table on
# disk is the one run N-1's cage committed -- and talk/truth.log's newest line at that moment is
# run N-1's too, so the two agree and the tie holds. What this check grades is therefore the
# record against the PREVIOUS run's grades, one clock tick behind, always self-consistent. A table
# written by `run=local` or a `fixture=1` selfcheck is a could-not-look, not a fault.
#
# WHAT IS COUNTED AND NEVER FAILED, printed as numbers on every run so that what is outside the
# derivation moves with the record instead of rotting in a sentence: resolved tickets that name
# no check of their own the table carries (51 of 79 against run 135), named checks that are not
# rows in the table at all (124), red rows named by a ticket that does not own the check (7) and
# red rows no commit ties to any ticket (0, now that the plural subjects are read).
#
# THIS CHECK IS NOT ITS OWN EVIDENCE (ticket 108, 2026-09-09). Its own grade row is excluded from
# the derivation of the ticket that built it, and counted instead. Without that rule the
# derivation LATCHES: this script fails for any reason, the cage commits FAIL in its own row, and
# on the next run the owning ticket derives `regressed` FROM THAT ROW -- which fails the script
# again, and again, whatever happened to the estate. Runs 186 and 192 both carry
# `verify/derived-status/... FAIL` and by construction no later run could have cleared it. It is
# ticket 108's shape one level up: a check whose own output is its own input. Nothing is less
# safe -- the FAIL still reds the gate by its own exit status on the same day, every OTHER check
# the ticket owns still derives its status, and a ticket left with only this row derives
# `resolved-ungraded`, never `resolved`, so the row is not evidence FOR it either.
#
#   PASS (exit 0)  the record uses the vocabulary, every done ticket has something behind it, and
#                  no ticket claims resolved while a check IT OWNS is red and unacknowledged
#   FAIL (exit 1)  one of those is false, named
#   SKIP (exit 3)  no grade table has been recorded yet, the one on disk was written by a local
#                  or fixture run, or no python
#
#   verify-derived-status.sh            selfcheck, then the record, then the derivation
#   verify-derived-status.sh selfcheck  the pure half only; the record is not read
set -uo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(cd "$HERE/../.." && pwd)"
cd "$ROOT" || { echo "FAIL: cannot enter the hub root"; exit 1; }
say() { printf '\033[1;36m==>\033[0m %s\n' "$*"; }
bad=0
note() { echo "  !! $*"; bad=$((bad + 1)); }

PY="$ROOT/.venv/bin/python"; [ -x "$PY" ] || PY="$(command -v python3 || true)"
[ -n "$PY" ] || { echo "SKIP: no python to read the record with"; exit 3; }
GRADES="$ROOT/talk/captures/_grades.tsv"
ISSUES="$ROOT/.scratch/ecosystem/issues"

say "1. the derivation grades planted tickets and a planted grade table as documented"
"$PY" "$HERE/derived_status.py" selfcheck || note "derived_status.py selfcheck did not pass"

if [ "${1:-}" = "selfcheck" ]; then
  echo
  if [ "$bad" -eq 0 ]; then
    echo "PASS: selfcheck: the vocabulary, the missing Answer, the missing dated closure, the grade table's tie to the newest run, and each of the four derivations grade as planted -- including the three things that must NOT dispose of a red: the Answer's own words, a dated note about another check, and an undated note about the right one"
    exit 0
  fi
  echo "FAIL: selfcheck: the derivation does not grade as documented (see above)"
  exit 1
fi

[ -d "$ISSUES" ] || { echo "FAIL: $ISSUES is missing, so there is no record to derive a status for"; exit 1; }

say "2. every Status: is one word of the tracker's vocabulary, and every done ticket has something behind it"
rec="$("$PY" "$HERE/derived_status.py" record --issues "$ISSUES")"; rrc=$?
printf '%s\n' "$rec"
[ "$rrc" -eq 0 ] || note "the record free-types a Status, or claims a state with nothing behind it"

say "3. the derivation, from the grade table the newest recorded run wrote"
if [ ! -f "$GRADES" ]; then
  # A could-not-look, and it is the whole point of leg 1 running first: a fault in the record is
  # already a FAIL above, so this shrug can never hide one.
  if [ "$bad" -gt 0 ]; then
    echo
    echo "FAIL: $bad fault(s) in the record itself, named above; the derivation from the run could not be attempted because talk/captures/_grades.tsv has not been recorded yet"
    exit 1
  fi
  echo "  talk/captures/_grades.tsv is not in this checkout"
  echo
  echo "SKIP: no run has recorded a grade table yet (talk/captures/_grades.tsv), so no ticket's Status can be derived from a named check; talk/verify-all.sh writes it and the clock's observation cage commits it, so it arrives on the first scheduled run of the default branch after this lands"
  exit 3
fi
der="$("$PY" "$HERE/derived_status.py" report --issues "$ISSUES" --grades "$GRADES" \
         --log "$ROOT/talk/truth.log")"; drc=$?
printf '%s\n' "$der"
if [ "$drc" -eq 3 ]; then
  # A table no clock wrote (review F4, 2026-09-06): `run=local` from a developer's own
  # `bash talk/verify-all.sh`, or `fixture=1` from the gate's selfcheck. It can never be the
  # newest RECORDED run, so grading against it would turn a local gate run red for the crime of
  # having been run at all. Leg 2's faults are already a FAIL above, so this shrug hides nothing.
  if [ "$bad" -gt 0 ]; then
    echo
    echo "FAIL: $bad fault(s) in the record itself, named above; the derivation could not be attempted because the grade table on disk was not written by a clock"
    exit 1
  fi
  echo
  echo "SKIP: the grade table on disk was written by a local or fixture run, which talk/truth.log never records, so no ticket's Status can be derived from it; the first table a clock records replaces it"
  exit 3
fi
[ "$drc" -eq 0 ] || note "a ticket is written resolved while a check it OWNS is red on the run the grade table records, and nothing dated after that ticket's Answer names that check"

echo
if [ "$bad" -eq 0 ]; then
  echo "PASS: every ticket in .scratch/ecosystem/issues/ carries one Status: line from the tracker's own vocabulary with nothing free-typed after it, every resolved ticket has an Answer and every closed one a dated closure, and every resolved ticket's Status is derived from the grade table the newest recorded run wrote -- no ticket claims resolved while a check it names graded FAIL on that run without a dated line in the ticket naming it"
  exit 0
fi
echo "FAIL: $bad fault(s) -- a ticket's Status: is typed rather than derived (ticket 59)"
exit 1
