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
#      `regressed` is a FAULT unless the file carries a DATED paragraph naming that red check --
#      and the Answer's own claim cannot be that paragraph, because every Answer names its own
#      check and ticket 80 was defeated this morning by a check that took the fix written into
#      the text it graded as input.
#   3. NO GRADE TABLE YET -> exit 3, SKIP. `talk/captures/_grades.tsv` is written by
#      talk/verify-all.sh and committed by the clock's cage, so it arrives on the first scheduled
#      run of the default branch after this lands. That is a `waits:` in the manifest, not a
#      `never:`: the estate's own state has not arrived, and the day it does this looks.
#
# WHAT IS COUNTED AND NEVER FAILED, printed as numbers on every run so that what is outside the
# derivation moves with the record instead of rotting in a sentence: resolved tickets that name
# no check the table carries (37 of 79 on 2026-09-06 -- the research, grilling and org-setup
# tickets, which no gate check can grade), and named checks that are not rows in the table at all.
#
#   PASS (exit 0)  the record uses the vocabulary, every done ticket has something behind it, and
#                  no ticket claims resolved while a check it names is red and unacknowledged
#   FAIL (exit 1)  one of those is false, named
#   SKIP (exit 3)  no grade table has been recorded yet, or no python
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
[ "$drc" -eq 0 ] || note "a ticket is written resolved while a check it names is red on the newest recorded run, and nothing dated in the ticket says so"

echo
if [ "$bad" -eq 0 ]; then
  echo "PASS: every ticket in .scratch/ecosystem/issues/ carries one Status: line from the tracker's own vocabulary with nothing free-typed after it, every resolved ticket has an Answer and every closed one a dated closure, and every resolved ticket's Status is derived from the grade table the newest recorded run wrote -- no ticket claims resolved while a check it names graded FAIL on that run without a dated line in the ticket naming it"
  exit 0
fi
echo "FAIL: $bad fault(s) -- a ticket's Status: is typed rather than derived (ticket 59)"
exit 1
