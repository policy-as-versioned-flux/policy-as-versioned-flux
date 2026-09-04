#!/usr/bin/env bash
# ADR-0026 supersedes ADR-0013, ADR-0017 and ADR-0018 point 3 (eco-system ticket 39). OFFLINE,
# self-proof, meta.
#
# Ticket 15 (2026-08-28) decided that a hole is priced, never refused; ticket 38 (2026-09-03/04)
# built it; ADR-0013 (bare-id key, new-hole refusal, widening refusal, removal refusal), ADR-0017
# (a self-created hole refuses) and ADR-0018 point 3 (a new ungoverned namespace refuses) carried
# the old rules with no supersession note until ticket 38 left dated notes pointing at "ticket
# 39's superseding ADR". This script is ticket 39's check in the gate: it reads docs/adr/ and
# CONTEXT.md and FAILS if ADR-0026 is missing or lacks a required section, if any of the three
# superseded ADRs has lost its dated "Superseded in part" banner naming ADR-0026, if a forward
# reference to an unwritten ADR survives, or if a CONTEXT.md entry still cites ADR-0013 for a
# refusal that is gone or still says a removal refuses.
#
# It grades the RECORD, not the code: a PASS here means the decision is written down and the
# superseded ADRs say so, not that compose/composition.py behaves that way. The code is graded by
# verify/priced-holes/verify-priced-holes.sh (ticket 38); a second grader over the same source
# would drift from the first, so this one deliberately reads no Python. The one place record and
# code are known to differ on 2026-09-04 (the removal refusal, ADR-0026 point 5) is named in the
# ADR's Consequences, and this script requires that naming.
#
# Exit 0 PASS, 1 FAIL. Never SKIP: every file it reads is in this repo, so it can always look.
#
#   verify-adr-supersession.sh            selfcheck first, then grade the committed record
#   verify-adr-supersession.sh selfcheck  selfcheck only: strip ADR-0013's banner from a copy and
#                                         require FAIL; drop ADR-0026's Options considered section
#                                         and require FAIL; point CONTEXT.md's citations back at
#                                         ADR-0013 and require FAIL; drop the removed-control line
#                                         from ADR-0026's refusal-kind classification and require
#                                         FAIL; drop the classification's lead sentence and
#                                         require FAIL
#
# ADR-0026 point 6 must classify every refusal kind composition.py emitted on 2026-09-04 as an
# instrument fault or a behaviour. The list is a fixture in this file (REFUSAL_KINDS), not a read
# of the platform clone, so the check stays offline and never SKIPs.
#
# The no-argument path runs the selfcheck first (as verify-record-states-the-purpose.sh does), so
# a grader that stops grading fails the gate instead of shipping a quiet PASS.
set -u
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
ADR_DIR="${ADR_SUPERSESSION_ADR_DIR:-$ROOT/docs/adr}"     # overridden only by the selfcheck
CONTEXT="${ADR_SUPERSESSION_CONTEXT:-$ROOT/CONTEXT.md}"   # overridden only by the selfcheck
NEW=0026
DATE=2026-09-04
# The refusal kinds compose/composition.py emitted on the platform integration branch on
# 2026-09-04 (every "kind" whose dict carries needs_composition; verify-composition.sh step 1b
# prints nine of these, its 400-character scan window missing the two with the longest detail).
# A FIXTURE, on purpose: this grader reads no platform source, so it can never SKIP, and ADR-0026
# point 6 must classify each of these as an instrument fault or a behaviour. A kind the source
# gains later is a fact for the next ADR and for whoever extends this list.
REFUSAL_KINDS="claim-against-another-partys-policy dangling-claim missing-baseline-file missing-instrument no-controls-parent removed-control restatement-of-non-validating rule-conflict split-diamond unknown-control-id unpriceable-inability"
CLASSIFY_MARKER='Every refusal kind composition emits today, classified'
bad=0
ok()   { printf '  ok   %s\n' "$*"; }
fail() { printf '  FAIL %s\n' "$*"; bad=$((bad+1)); }

selfcheck() {
  local t me good=1 new
  t="$(mktemp -d)"
  me="$ROOT/verify/adr-supersession/$(basename "${BASH_SOURCE[0]}")"
  new="$(ls "$ROOT/docs/adr/$NEW"-*.md 2>/dev/null | head -1)"
  [ -n "$new" ] || { echo "FAIL: selfcheck: no docs/adr/$NEW-*.md to plant defects in"; rm -rf "$t"; return 1; }
  # leg 1: ADR-0013 with its ADR-0026 banner stripped
  mkdir -p "$t/no-banner"; cp "$ROOT"/docs/adr/*.md "$t/no-banner/"
  grep -v "^> \*\*Superseded in part, .*$NEW" "$ROOT"/docs/adr/0013-*.md >"$t/no-banner/$(basename "$ROOT"/docs/adr/0013-*.md)"
  # leg 2: ADR-0026 with its Options considered section removed
  mkdir -p "$t/no-section"; cp "$ROOT"/docs/adr/*.md "$t/no-section/"
  awk '/^## Options considered/ {skip=1; next} /^## / {skip=0} !skip' "$new" >"$t/no-section/$(basename "$new")"
  # leg 3: CONTEXT.md whose ADR-0026 citations point back at ADR-0013
  sed "s/ADR-$NEW/ADR-0013/g" "$ROOT/CONTEXT.md" >"$t/stale-context.md"
  # leg 4: ADR-0026 whose classification no longer names removed-control (the one behaviour)
  mkdir -p "$t/no-kind"; cp "$ROOT"/docs/adr/*.md "$t/no-kind/"
  grep -vE '^ *- `removed-control`: ' "$new" >"$t/no-kind/$(basename "$new")"
  # leg 5: ADR-0026 with the classification lead sentence gone
  mkdir -p "$t/no-classify"; cp "$ROOT"/docs/adr/*.md "$t/no-classify/"
  grep -v "$CLASSIFY_MARKER" "$new" >"$t/no-classify/$(basename "$new")"
  ADR_SUPERSESSION_ADR_DIR="$t/no-banner" bash "$me" >/dev/null 2>&1 && { echo "selfcheck: an ADR-0013 with no ADR-$NEW banner passed"; good=0; }
  ADR_SUPERSESSION_ADR_DIR="$t/no-section" bash "$me" >/dev/null 2>&1 && { echo "selfcheck: an ADR-$NEW with no Options considered passed"; good=0; }
  ADR_SUPERSESSION_CONTEXT="$t/stale-context.md" bash "$me" >/dev/null 2>&1 && { echo "selfcheck: a CONTEXT.md citing ADR-0013 for the refusals passed"; good=0; }
  ADR_SUPERSESSION_ADR_DIR="$t/no-kind" bash "$me" >/dev/null 2>&1 && { echo "selfcheck: an ADR-$NEW that stops classifying removed-control passed"; good=0; }
  ADR_SUPERSESSION_ADR_DIR="$t/no-classify" bash "$me" >/dev/null 2>&1 && { echo "selfcheck: an ADR-$NEW with no refusal-kind classification passed"; good=0; }
  rm -rf "$t"
  if [ "$good" = 1 ]; then echo "  ok   selfcheck: a missing banner fails; a missing section fails; a stale CONTEXT citation fails; an unclassified refusal kind fails; a missing classification fails"; return 0; fi
  echo "FAIL: selfcheck: the grader does not grade"; return 1
}

if [ "${1:-}" = selfcheck ]; then
  selfcheck || exit 1
  echo "PASS: selfcheck: a missing banner fails, a missing section fails, a stale CONTEXT citation fails, an unclassified refusal kind fails, a missing classification fails"; exit 0
fi
if [ -z "${ADR_SUPERSESSION_ADR_DIR:-}${ADR_SUPERSESSION_CONTEXT:-}" ]; then
  echo "0. the grader can fail"
  selfcheck || exit 1
fi

[ -d "$ADR_DIR" ] || { echo "FAIL: $ADR_DIR is missing"; exit 1; }
[ -f "$CONTEXT" ] || { echo "FAIL: $CONTEXT is missing"; exit 1; }

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
# adr <nnnn>: the one file docs/adr/<nnnn>-*.md, or empty.
adr() { ls "$ADR_DIR/$1"-*.md 2>/dev/null | head -1; }
# bullet <name>: the body of the CONTEXT.md glossary bullet "- **name**", up to the next bullet.
bullet() { awk -v name="$1" 'index($0, "- **" name "**") == 1 {p=1; print; next} /^- \*\*/ {p=0} p' "$CONTEXT"; }

echo "1. ADR-$NEW exists, is accepted, and carries the four required sections"
new="$(adr $NEW)"
if [ -z "$new" ]; then
  fail "there is no $ADR_DIR/$NEW-*.md"
  newtext=""
else
  ok "$(basename "$new")"
  [ "$(ls "$ADR_DIR/$NEW"-*.md | wc -l | tr -d ' ')" = 1 ] || fail "more than one $NEW-*.md"
  newtext="$(cat "$new")"
  want "ADR-$NEW" "$newtext" '^status: accepted$'
  for h in 'Context' 'Decision' 'Options considered' 'Consequences'; do
    want "ADR-$NEW" "$newtext" "^## $h\$"
  done
  want "ADR-$NEW" "$newtext" "^Decided $DATE .*ADR-0025.*delegated"
fi

echo "2. ADR-$NEW names the three superseded rules, the four reasons and the removal decision"
if [ -n "$newtext" ]; then
  want "ADR-$NEW" "$newtext" 'ADR-0013'
  want "ADR-$NEW" "$newtext" 'ADR-0017'
  want "ADR-$NEW" "$newtext" 'ADR-0018.*point 3'
  want "ADR-$NEW" "$newtext" 'new-hole refusal|refuses on a \*\*new\*\* hole|new hole refus'
  want "ADR-$NEW" "$newtext" 'widening'
  want "ADR-$NEW" "$newtext" 'self-created hole'
  want "ADR-$NEW" "$newtext" 'ungoverned .*namespace'
  want "ADR-$NEW" "$newtext" '\(source, id\)'
  want "ADR-$NEW" "$newtext" 'bare catalogue id'
  want "ADR-$NEW" "$newtext" 'ticket 15'
  want "ADR-$NEW" "$newtext" 'ADR-0020'
  want "ADR-$NEW" "$newtext" 'ADR-0022'
  want "ADR-$NEW" "$newtext" 'ticket 38'
  want "ADR-$NEW" "$newtext" 'removed-control'
  want "ADR-$NEW" "$newtext" 'removal is priced'
  want "ADR-$NEW" "$newtext" 'missing instrument'
  # the one known record/code gap is named, with the function that still refuses
  want "ADR-$NEW consequences" "$newtext" 'check_selected_set.*still refuses'
  # the unknown-id refusal keeps its code kind; the record says which
  want "ADR-$NEW consequences" "$newtext" 'code kind `unknown-control-id`, not `missing-instrument`'
fi

echo "2b. ADR-$NEW point 6 classifies every refusal kind composition emitted on $DATE (fixture of $(echo $REFUSAL_KINDS | wc -w | tr -d ' '))"
if [ -n "$newtext" ]; then
  want "ADR-$NEW" "$newtext" "$CLASSIFY_MARKER"
  for k in $REFUSAL_KINDS; do
    want "ADR-$NEW classification" "$newtext" "^ *- \`$k\`: (instrument fault|behaviour)"
  done
  want "ADR-$NEW classification" "$newtext" '^ *- `removed-control`: behaviour'
  want "ADR-$NEW classification" "$newtext" '^ *- `unknown-control-id`: instrument fault'
fi

echo "3. ADR-0013, ADR-0017 and ADR-0018 carry a dated Superseded in part banner naming ADR-$NEW"
for old in 0013 0017 0018; do
  f="$(adr $old)"
  if [ -z "$f" ]; then fail "there is no $ADR_DIR/$old-*.md"; continue; fi
  banner="$(grep -E "^> \*\*Superseded in part, $DATE" "$f" | grep -E "\[ADR-$NEW\]\($NEW-[a-z0-9-]+\.md\)" || true)"
  if [ -z "$banner" ]; then fail "ADR-$old has no '> **Superseded in part, $DATE' banner linking [ADR-$NEW]($NEW-*.md)"; continue; fi
  ok "ADR-$old banner dated $DATE links ADR-$NEW"
  target="$(printf '%s\n' "$banner" | sed -nE "s/.*\[ADR-$NEW\]\(($NEW-[a-z0-9-]+\.md)\).*/\1/p" | head -1)"
  [ -f "$ADR_DIR/$target" ] && ok "ADR-$old banner target $target exists" || fail "ADR-$old banner links $target, which does not exist"
  # the banner sits above the title, where the 0014/0015/0016 banners sit
  if [ "$(grep -nE "^> \*\*Superseded in part, $DATE" "$f" | head -1 | cut -d: -f1)" -lt "$(grep -n '^# ' "$f" | head -1 | cut -d: -f1)" ]; then
    ok "ADR-$old banner precedes the title"
  else
    fail "ADR-$old banner is below the title"
  fi
  case $old in
    0013) want "ADR-0013 banner" "$banner" 'new-hole|new hole'; want "ADR-0013 banner" "$banner" 'widening'; want "ADR-0013 banner" "$banner" 'removal'; want "ADR-0013 banner" "$banner" '\(source, id\)';;
    0017) want "ADR-0017 banner" "$banner" 'self-created hole'; want "ADR-0017 banner" "$banner" 'remov';;
    0018) want "ADR-0018 banner" "$banner" '[Pp]oint 3'; want "ADR-0018 banner" "$banner" 'ungoverned';
          # the ADR-0022 banner for §4 is a different supersession and must survive
          if grep -qE '^> \*\*Superseded in part, 2026-08-28\.\*\* §4.*ADR-0022' "$f"; then ok "ADR-0018 keeps its ADR-0022 banner for §4"; else fail "ADR-0018 lost its ADR-0022 banner for §4"; fi;;
  esac
done

echo "4. no ADR still points at an unwritten superseding ADR"
fwd="$(grep -lE "ticket 39's superseding ADR|takes its number when it is written" "$ADR_DIR"/*.md 2>/dev/null || true)"
if [ -z "$fwd" ]; then ok "no forward reference to an unnumbered ADR survives"; else fail "forward reference to an unnumbered ADR in: $(basename "$fwd" | tr '\n' ' ')"; fi

echo "5. CONTEXT.md's Baseline, Control id, Hole and Delta entries cite ADR-$NEW and no longer carry the refusals"
b="$(bullet Baseline)"
[ -n "$b" ] || fail "CONTEXT.md has no Baseline bullet"
want 'Baseline' "$b" "ADR-$NEW"
refuse 'Baseline' "$b" 'ticket 39 supersedes'
refuse 'Baseline' "$b" 'never remove'
want 'Baseline' "$b" 'removal is priced'
c="$(bullet 'Control id')"
[ -n "$c" ] || fail "CONTEXT.md has no Control id bullet"
want 'Control id' "$c" "ADR-$NEW"
want 'Control id' "$c" '\(source, id\)'
want 'Control id' "$c" 'missing instrument'
h="$(bullet Hole)"
[ -n "$h" ] || fail "CONTEXT.md has no Hole bullet"
want 'Hole' "$h" "ADR-$NEW"
refuse 'Hole' "$h" 'removal still refuses'
want 'Hole' "$h" 'removed-control'
d="$(bullet Delta)"
[ -n "$d" ] || fail "CONTEXT.md has no Delta bullet"
want 'Delta' "$d" "ADR-$NEW"

echo
if [ "$bad" -eq 0 ]; then
  echo "PASS: ADR-$NEW records the priced-hole decision; ADR-0013, ADR-0017 and ADR-0018 point 3 carry dated banners naming it; CONTEXT.md cites it and no entry still refuses"
  exit 0
fi
echo "FAIL: $bad fact(s) the record must state about the supersession are missing (ticket 39)"
exit 1
