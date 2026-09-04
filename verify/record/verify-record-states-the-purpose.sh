#!/usr/bin/env bash
# The record states the purpose (eco-system ticket 95). OFFLINE, self-proof, meta.
#
# The 2026-09-02 review found that no document said what the estate is for, who receives it, or
# by when. Ticket 75 answered; ticket 95 wrote the answer into NORTH-STAR.md. This script is the
# ticket's check in the gate: it reads NORTH-STAR.md and CONTEXT.md and FAILS if any of the facts
# the ticket named has gone missing, or if a line that attributes something to the owner has lost
# its date.
#
# It grades the RECORD, not the estate: a PASS here means the document says these things, not
# that they are true of the running code. The truth surface grades the code.
#
# Exit 0 PASS, 1 FAIL. Never SKIP: both files are in this repo, so it can always look.
#
#   verify-record-states-the-purpose.sh            selfcheck first, then grade the committed record
#   verify-record-states-the-purpose.sh selfcheck  selfcheck only: strip §0 from a copy and require
#                                                  FAIL; revert principle 2 to the assistant's
#                                                  reading and require FAIL
#
# The no-argument path runs the selfcheck first (as verify-e2e-step7-honesty.sh does), so a
# grader that stops grading fails the gate instead of shipping a quiet PASS.
set -u
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
NORTH_STAR="${RECORD_NORTH_STAR:-$ROOT/NORTH-STAR.md}"   # overridden only by the selfcheck
CONTEXT="$ROOT/CONTEXT.md"
bad=0
ok()   { printf '  ok   %s\n' "$*"; }
fail() { printf '  FAIL %s\n' "$*"; bad=$((bad+1)); }

selfcheck() {
  local t me good=1
  t="$(mktemp -d)"
  me="$ROOT/verify/record/$(basename "${BASH_SOURCE[0]}")"
  awk '/^## 0\. / {skip=1; next} /^## / {skip=0} !skip' "$ROOT/NORTH-STAR.md" >"$t/no-section-0.md"
  sed 's/In the owner.s words (2026-09-02, ticket 75 Q5)/That a refusal is therefore the bottom rung is my reading, not your words./' \
    "$ROOT/NORTH-STAR.md" >"$t/assistant-reading.md"
  # ticket 90: §1 back to the actor claim, and principle 6 with the shelving marker struck out
  sed 's/and every artefact is attestable\. The orgs/and every actor is attestable. The orgs/' \
    "$ROOT/NORTH-STAR.md" >"$t/actor-claim.md"
  sed 's/\*\*The actor half of this principle is SHELVED for this build\*\*/The actor half is fine./' \
    "$ROOT/NORTH-STAR.md" >"$t/unshelved.md"
  RECORD_NORTH_STAR="$t/no-section-0.md" bash "$me" >/dev/null 2>&1 && { echo "selfcheck: a record with no §0 passed"; good=0; }
  RECORD_NORTH_STAR="$t/assistant-reading.md" bash "$me" >/dev/null 2>&1 && { echo "selfcheck: a principle 2 in the assistant's words passed"; good=0; }
  RECORD_NORTH_STAR="$t/actor-claim.md" bash "$me" >/dev/null 2>&1 && { echo "selfcheck: a §1 claiming actor attestation passed"; good=0; }
  RECORD_NORTH_STAR="$t/unshelved.md" bash "$me" >/dev/null 2>&1 && { echo "selfcheck: a principle 6 with no shelving marker passed"; good=0; }
  rm -rf "$t"
  if [ "$good" = 1 ]; then echo "  ok   selfcheck: a record missing §0 fails; a principle 2 in the assistant's words fails; a §1 that claims actor attestation fails; a principle 6 that drops the shelving marker fails"; return 0; fi
  echo "FAIL: selfcheck: the grader does not grade"; return 1
}

if [ "${1:-}" = selfcheck ]; then
  selfcheck || exit 1
  echo "PASS: selfcheck: a record missing §0 fails, a principle 2 in the assistant's words fails, a §1 claiming actor attestation fails, and a principle 6 with no shelving marker fails"; exit 0
fi
if [ -z "${RECORD_NORTH_STAR:-}" ]; then
  echo "0. the grader can fail"
  selfcheck || exit 1
fi

[ -f "$NORTH_STAR" ] || { echo "FAIL: $NORTH_STAR is missing"; exit 1; }
[ -f "$CONTEXT" ] || { echo "FAIL: $CONTEXT is missing"; exit 1; }

# section <n>: the body of NORTH-STAR section n, from its "## n." heading to the next "## ".
section() { awk -v n="$1" '$0 ~ ("^## " n "\\. ") {p=1; next} /^## / {p=0} p' "$NORTH_STAR"; }
# bullet <name>: the body of the CONTEXT.md glossary bullet "- **name**", up to the next bullet.
bullet() { awk -v name="$1" 'index($0, "- **" name "**") == 1 {p=1; print; next} /^- \*\*/ {p=0} p' "$CONTEXT"; }

# want <where> <text> <pattern>: the text must contain the pattern (ERE, case-sensitive).
want() {
  local where="$1" text="$2" pat="$3"
  if printf '%s\n' "$text" | grep -qE -- "$pat"; then ok "$where: $pat"; else fail "$where lacks: $pat"; fi
}
# refuse <where> <text> <pattern>: the text must NOT contain the pattern.
refuse() {
  local where="$1" text="$2" pat="$3"
  if printf '%s\n' "$text" | grep -qE -- "$pat"; then fail "$where still says: $pat"; else ok "$where no longer says: $pat"; fi
}

echo "1. NORTH-STAR §0 answers: what is this for, who receives it, by when"
s0="$(section 0)"
[ -n "$s0" ] || fail "there is no '## 0.' section"
want '§0' "$s0" '\(a\).*touring talk'
want '§0' "$s0" '\(b\).*reference implementation.*ControlPlane'
want '§0' "$s0" '\(c\).*fourth organisation.*open source'
want '§0' "$s0" '\(d\).*written, checkable'
want '§0' "$s0" "when we've got something good, we'll tour it"
want '§0' "$s0" 'circuit'
want '§0' "$s0" 'ticket 75'
want '§0' "$s0" '2026-09-02'

echo "2. NORTH-STAR §4 is the assistant's build order; done is defined"
h4="$(grep -E '^## 4\. ' "$NORTH_STAR" || true)"
[ -n "$h4" ] || fail "there is no '## 4.' heading"
if printf '%s\n' "$h4" | grep -qiE 'build order'; then ok "§4 heading says build order"; else fail "§4 heading does not say build order"; fi
s4="$(section 4)"
want '§4' "$s4" 'not mine'
want '§4' "$s4" 'definition of done'
want '§4' "$s4" 'ticket 75 Q8'
want '§4' "$s4" 'ceiling'
want '§4' "$s4" 'lane fact'
want '§4' "$s4" '2026-09-02'

echo "3. NORTH-STAR §6 records the talk, the theatre and the shelved identity, with dates"
s6="$(section 6)"
want '§6' "$s6" 'byproduct.*marketing tool'
want '§6' "$s6" '2026-07-23'
want '§6' "$s6" 'theatre'
want '§6' "$s6" 'second identity'
want '§6' "$s6" 'AI disposal'
want '§6' "$s6" 'shelved'
want '§6' "$s6" 'ticket 90'
want '§6' "$s6" '2026-09-02'

echo "4. NORTH-STAR §3 principle 2 carries the owner's words, not the assistant's reading"
p2="$(section 3 | grep -E '^2\. ' || true)"
[ -n "$p2" ] || fail "§3 has no principle 2"
refuse 'principle 2' "$p2" 'is my reading, not your words'
want 'principle 2' "$p2" '[Mm]utating admission controller'
want 'principle 2' "$p2" 'ticket 75 Q5'
want 'principle 2' "$p2" '2026-09-02'

echo "4b. NORTH-STAR §1 claims the artefact half, and principle 6 keeps the actor half, shelved"
# Eco-system ticket 90. §1 is the one sentence the whole estate is measured against, so it may
# claim only what a citable run can be observed doing: artefact attestation is graded on every
# run, actor attestation has never been observed. Principle 6 keeps the design and says it is
# shelved, with the date and the ticket, so the shelving is a record and not a deletion.
s1="$(section 1)"
[ -n "$s1" ] || fail "there is no '## 1.' section"
want '§1' "$s1" 'every artefact is attestable'
refuse '§1' "$s1" 'and every actor is attestable\. The orgs'
want '§1' "$s1" 'ticket 90'
want '§1' "$s1" '2026-09-02'
p6="$(section 3 | grep -E '^6\. ' || true)"
[ -n "$p6" ] || fail "§3 has no principle 6"
want 'principle 6' "$p6" 'Every actor is attestable'
want 'principle 6' "$p6" 'SHELVED for this build'
want 'principle 6' "$p6" 'ticket 90'
want 'principle 6' "$p6" '2026-09-0[24]'
want 'principle 6' "$p6" 'verify-exclusions\.txt'
# ...and the exclusions file must actually carry the six, or principle 6 states a shelving the
# gate does not perform. The record and the instrument have to agree.
EXCL="$ROOT/talk/verify-exclusions.txt"
shelved="$(grep -cE '^\S+ \| shelved with the identity plane \(ticket 90\)' "$EXCL" 2>/dev/null || echo 0)"
if [ "$shelved" -ge 6 ]; then ok "talk/verify-exclusions.txt shelves $shelved identity-plane scripts with reasons"
else fail "talk/verify-exclusions.txt shelves $shelved identity-plane scripts; principle 6 says six are"; fi

echo "5. NORTH-STAR §8 points at the sixteen decisions by number"
s8="$(section 8)"
want '§8' "$s8" 'ticket 75'
want '§8' "$s8" '[Ss]ixteen decisions'
missing=0
for n in $(seq 1 16); do
  printf '%s\n' "$s8" | grep -qE "(^|[^0-9])$n\. " || { fail "§8 does not list decision $n"; missing=$((missing+1)); }
done
[ "$missing" -eq 0 ] && ok "§8 lists decisions 1 to 16"

echo "6. every line that attributes something to the owner carries a date"
# The ticket's definition of done, checked mechanically at line grain: the attribution and its
# YYYY-MM-DD must sit on the same line, so a later edit cannot separate them silently. Line grain
# is coarser than sentence grain; a line with two owner sentences and one date passes here.
ATTRIB='\((Owner|owner)[,:]|owner-reasoned|owner-instructed|[Oo]wner said|[Oo]wner.s (words|instruction|call|chain)|[Yy]ou said'
undated="$(grep -nE "$ATTRIB" "$NORTH_STAR" | grep -vE '20[0-9]{2}-[0-9]{2}-[0-9]{2}' || true)"
if [ -z "$undated" ]; then ok "every owner attribution carries a date"; else fail "owner attributions without a date:"; printf '%s\n' "$undated" | sed 's/^/       /'; fi

echo "7. CONTEXT.md's Cage and Multi-version coexistence entries agree with NORTH-STAR"
cage="$(bullet Cage)"
want 'Cage' "$cage" 'ticket 75'
want 'Cage' "$cage" '[Mm]utating admission controller'
want 'Cage' "$cage" 'never because it is deliberately denied'
mv="$(bullet 'Multi-version coexistence')"
want 'Multi-version' "$mv" 'ticket 75 Q3'
want 'Multi-version' "$mv" 'three declared lines'
want 'Multi-version' "$mv" '2022-03-11'

echo
if [ "$bad" -eq 0 ]; then
  echo "PASS: NORTH-STAR states the purpose, the audience, the (absent) date and what done is, claims the artefact half of attestation and records the actor half as shelved with its six scripts excluded by name, every owner line dated; CONTEXT.md agrees"
  exit 0
fi
echo "FAIL: $bad fact(s) the record must state are missing or undated (ticket 95)"
exit 1
