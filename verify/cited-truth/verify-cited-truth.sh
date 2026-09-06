#!/usr/bin/env bash
# A cited TRUTH line is a real line whose tree carries the check (eco-system ticket 80 item 1).
#
# THE DEFECT. Fifteen resolved build tickets closed with "its check is in `talk/verify-all.sh`.
# The run that recorded it is the TRUTH line of 2026-08-29". That line is run 7, hub `918022b`,
# graded at 12:03Z on 2026-08-29 -- BEFORE the build it is offered as proof of. Its tree carries
# `verify/party`, `verify/proportionality` and `verify/provenance`, and none of the fifteen
# checks. Correcting fifteen files fixes fifteen files. This script refuses the sixteenth.
#
# WHAT IT GRADES. Every `.scratch/ecosystem/issues/*.md`:
#   1. a paragraph offering a TRUTH line as proof that a check is in the gate must cite a line
#      talk/truth.log actually recorded, whose `hub=` commit this checkout can read, whose TREE
#      carries a check the ticket names -- or the ticket must carry a DATED correction naming
#      that citation;
#   2. a TRUTH figure (`pass= fail= skip= excluded= total= ceiling=`) quoted on the same text
#      line as a run citation must be that run's figure.
#
# It also grades TICKET 80's OTHER NINE CORRECTIONS as a table of literal sentences (item 2's two
# superseded-in-part banners, item 3's five delegated lines and the retired word, item 4's listed
# assistant-made call, item 5's restored GAPS rule 1, item 6's hub-side residue, item 7's two ADR
# notes and the confirmed section, item 8's runbook correction, item 9's unapplied signpost). Each
# fact is either a sentence the record must carry or a sentence it must no longer carry, because a
# correction appended below a claim it never removed leaves the estate saying both things at once,
# which is the shape this ticket exists to end. Item 6's module is graded by platform's own
# `verify-currency.sh`, and item 10 by platform's gate on that repository's pull request: reading
# a working copy of another party's README here would be the proxy this ticket is about.
#
# WHAT IT REFUSES TO GRADE, named because a disclosed limit rots like any other claim:
#   * whether the named check is the RIGHT check for what the ticket built. It grades that the
#     check existed in the tree that was measured: necessary, never sufficient.
#   * anything outside issues/*.md. A figure in map.md, an ADR or the deck is ticket 67(d)'s and
#     verify-demo.sh's question.
#   * a figure with no run citation beside it; a line that says of itself, in those words, that
#     it is `not citable` (or quotes a line carrying the runner's own `fixture=1`); and a
#     citation in a paragraph that is no gate-proof. All three populations are COUNTED and
#     printed on every run, and every exempted line is NAMED by path and line, so what is not
#     graded is on the record instead of being a sentence somebody wrote once.
#   * A NAMED CHECK is a `verify*.sh` matched by path suffix, or a directory the CITED tree
#     carries one under, read from the section the claim is made in with correction paragraphs
#     stripped. A bare `verify/` names nothing. What no text analysis can catch, and what makes
#     rule 1 necessary rather than sufficient: a ticket naming, in its own Answer, a check it
#     does not own that the cited tree happens to carry.
#
# NO COULD-NOT-LOOK, by decision (delegated, ADR-0025, 2026-09-06), following
# verify/can-record/'s call. Everything it reads is in this repository and everything it runs is
# git and python, so each state it could have shrugged in is RED with its own line:
#   * a cited `hub=` commit this checkout cannot resolve -> `unreadable-tree`. In a SHALLOW clone
#     that is every historic commit, which is the honest answer and not a shrug; truth.yml's gate
#     checkout is `fetch-depth: 0`, and this script says so when it finds a shallow one.
#   * a cited line talk/truth.log does not record -> `no-such-line`.
#   * no python, no git, no talk/truth.log, no issues directory -> FAIL here, named.
# So this row's manifest entry declares NO skip pattern, and there is none to declare.
#
# Exit 0 PASS, 1 FAIL. Never 3.
#
#   verify-cited-truth.sh            selfcheck first, then grade the committed record
#   verify-cited-truth.sh selfcheck  selfcheck only: planted defects grade as planted
set -u
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(cd "$HERE/../.." && pwd)"
cd "$ROOT" || { echo "FAIL: cannot enter the hub root"; exit 1; }
PY="$ROOT/.venv/bin/python"; [ -x "$PY" ] || PY="$(command -v python3 || true)"
GRADER="$HERE/cited_truth.py"

[ -n "$PY" ] || { echo "FAIL: no python to read the record with; a runner that has lost its interpreter goes red, it does not shrug"; exit 1; }

if [ "${1:-}" = selfcheck ]; then
  "$PY" "$GRADER" selfcheck || exit 1
  echo "PASS: selfcheck: a carried check passes; a lacking tree, an unreadable commit, an unrecorded line and a disagreeing figure each fail by name; a dated correction disposes and an undated one does not"
  exit 0
fi

bad=0
say() { printf '\033[1;36m==>\033[0m %s\n' "$*"; }

say "0. the grader can fail"
"$PY" "$GRADER" selfcheck || bad=$((bad + 1))

say "1. this checkout can read what a citation points at"
command -v git >/dev/null 2>&1 || { echo "  !! no git: a cited commit's tree cannot be read at all"; bad=$((bad + 1)); }
git -C "$ROOT" rev-parse --git-dir >/dev/null 2>&1 || { echo "  !! not a git checkout: a cited commit's tree cannot be read at all"; bad=$((bad + 1)); }
if [ "$(git -C "$ROOT" rev-parse --is-shallow-repository 2>/dev/null)" = true ]; then
  echo "  !! this is a SHALLOW checkout: every historic hub commit is absent, so no citation can be proved here. truth.yml's gate checkout is fetch-depth: 0; a shallow one is a red, not a shrug"
  bad=$((bad + 1))
fi
[ -f "$ROOT/talk/truth.log" ] || { echo "  !! talk/truth.log is missing: there is no recorded line to resolve a citation against"; bad=$((bad + 1)); }
[ -d "$ROOT/.scratch/ecosystem/issues" ] || { echo "  !! .scratch/ecosystem/issues is missing: there is no record to grade"; bad=$((bad + 1)); }
[ "$bad" -eq 0 ] && echo "  ok   git, talk/truth.log and .scratch/ecosystem/issues are all readable, and the checkout is not shallow"

say "2. every TRUTH line the tickets cite is real, and its tree carries the check it is offered as proof of"
if [ "$bad" -eq 0 ]; then
  "$PY" "$GRADER" grade "$ROOT" || bad=$((bad + 1))
else
  # what step 1 named is what steps 2 and 3 read; running them would print the same fact twice
  # and, before this guard, follow it with a traceback (review F9)
  echo "  not run: step 1 named what is missing"
fi

say "3. ticket 80's other nine corrections are still in the record, and what they removed has not come back"
if [ "$bad" -eq 0 ] || [ -d "$ROOT/docs/adr" ]; then
  "$PY" "$GRADER" record "$ROOT" || bad=$((bad + 1))
else
  echo "  not run: step 1 named what is missing"
fi

echo
if [ "$bad" -eq 0 ]; then
  echo "PASS: every TRUTH line quoted in .scratch/ecosystem/issues/*.md resolves to a line talk/truth.log records, every gate-proof citation names a commit whose tree carries a check the ticket names or carries a dated correction saying it does not, every figure quoted beside its run is that run's figure, and ticket 80's nine record corrections are each still there"
  exit 0
fi
echo "FAIL: $bad check(s) observed false (named above): the record cites a measurement that did not measure the thing"
exit 1
