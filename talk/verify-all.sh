#!/usr/bin/env bash
# The truth surface. The only citable source of what works.
#
# Discovers every verify*.sh under .estate-clone/ (the eight real unit repos,
# assembled by clone-estate.sh) and verify/ (the hub's cross-party proofs),
# runs each one, and grades it by exit code:
#   0  PASS  observed true
#   3  SKIP  could not look (the script says why on its last line)
#   *  FAIL  observed false, errored, or timed out
# A script neither run nor listed in talk/verify-exclusions.txt with a reason
# is itself a FAIL. A listed exclusion that no longer exists is a FAIL too, so
# the list cannot rot. Nothing is faked: a live tail that cannot see its
# cluster must exit 3, not 0.
#
# THE MANIFEST (ticket 83). talk/verify-manifest.txt classes every discovered
# script (estate-observation, self-proof, simulation, meta) and declares the
# could-not-look it is allowed: `never:` (the runner lacks the instrument) or
# `waits:` (the estate's state has not arrived), each with a pattern its SKIP
# line must match. A script with no manifest line FAILS (its grade cannot be
# placed in the split). A SKIP the manifest does not declare FAILS (a new reason
# for not looking is a red, not a shrug). A `never` script that passes FAILS
# (the ceiling was stale). talk/truth_manifest.py holds the format, the judge
# and the arithmetic; nothing here counts.
#
#   talk/verify-all.sh            offline run; a declared SKIP is not a failure
#   talk/verify-all.sh --live     SKIP counts as FAIL (you asked for live)
#   talk/verify-all.sh --refresh  re-clone the units first
#   talk/verify-all.sh --selfcheck
#       prove the instrument over a fixture of tiny scripts (a pass, a declared
#       skip, a fail, an undeclared skip, a script with no manifest line, an
#       exclusion, a `never` that passes) and assert the TRUTH line's counts.
#       Never runs the estate; its TRUTH line says fixture=1 and is not citable.
#
# Every run ends with one TRUTH line carrying the date, the run number, the
# hub commit, the unit commits, the counts, the split of passes by class, the
# split of skips by kind, and the ceiling (total - excluded - never). Quote that
# line, nothing else. After it, the slowest five scripts by wall-clock time are
# printed, so drift toward the timeout is visible before it happens. Each
# script's full output (not just its last line) lands in talk/captures/<slug>.out,
# named on a FAIL row.
set -u
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT" || exit 2
REQUIRE_LIVE=0; REFRESH=""; SELFCHECK=0
for a in "$@"; do case "$a" in --live) REQUIRE_LIVE=1;; --refresh) REFRESH=--refresh;; --selfcheck) SELFCHECK=1;; esac; done
TIMEOUT="${VERIFY_TIMEOUT:-300}"
EXCL="${VERIFY_EXCLUSIONS:-$ROOT/talk/verify-exclusions.txt}"
MANIFEST="${VERIFY_MANIFEST:-$ROOT/talk/verify-manifest.txt}"
TM="$ROOT/talk/truth_manifest.py"
# VERIFY_SCRIPTS_FROM: a file listing the scripts to run instead of discovering
# them. Fixture mode: no clone, no unit commits, and the TRUTH line says fixture=1.
FIXTURE="${VERIFY_SCRIPTS_FROM:-}"

# ---------------------------------------------------------------- selfcheck
if [ "$SELFCHECK" = 1 ]; then
  t="$(mktemp -d)"; trap 'rm -rf "$t"' EXIT
  mkdir -p "$t/fx"
  printf 'echo "PASS: fine"\nexit 0\n'                              >"$t/fx/verify-a-pass.sh"
  printf 'echo "SKIP: kind cluster fixture is not listed"\nexit 3\n' >"$t/fx/verify-b-declared-skip.sh"
  printf 'echo "FAIL: observed false"\nexit 1\n'                    >"$t/fx/verify-c-fail.sh"
  printf 'echo "SKIP: a brand new reason"\nexit 3\n'                >"$t/fx/verify-d-undeclared-skip.sh"
  printf 'echo "PASS: fine but unlisted"\nexit 0\n'                 >"$t/fx/verify-e-unlisted.sh"
  printf 'echo "helper"\nexit 0\n'                                  >"$t/fx/verify-f-excluded.sh"
  printf 'echo "PASS: the cluster was here after all"\nexit 0\n'    >"$t/fx/verify-g-never-passes.sh"
  printf 'echo "SKIP: a tag is not cut yet"\nexit 3\n'              >"$t/fx/verify-h-waits.sh"
  ls "$t"/fx/verify-*.sh | sort >"$t/scripts.txt"
  cat >"$t/manifest.txt" <<EOF
$t/fx/verify-a-pass.sh | self-proof | -
$t/fx/verify-b-declared-skip.sh | estate-observation | never: kind cluster \w+ is not listed
$t/fx/verify-c-fail.sh | estate-observation | -
$t/fx/verify-d-undeclared-skip.sh | meta | waits: an old reason
$t/fx/verify-g-never-passes.sh | estate-observation | never: kind cluster \w+ is not listed
$t/fx/verify-h-waits.sh | simulation | waits: not cut yet
EOF
  echo "$t/fx/verify-f-excluded.sh | a helper the others call" >"$t/exclusions.txt"
  out="$(env -u GITHUB_RUN_NUMBER VERIFY_SCRIPTS_FROM="$t/scripts.txt" VERIFY_MANIFEST="$t/manifest.txt" \
           VERIFY_EXCLUSIONS="$t/exclusions.txt" VERIFY_CAPDIR="$t/captures" \
           bash "$ROOT/talk/verify-all.sh")"; rc=$?
  good=1
  chk() { printf '%s\n' "$out" | grep -qE -- "$1" || { echo "selfcheck: missing: $1"; good=0; }; }
  [ "$rc" -eq 1 ] || { echo "selfcheck: expected exit 1 (there are fails), got $rc"; good=0; }
  chk 'verify-a-pass.sh +PASS$'
  chk 'verify-b-declared-skip.sh +SKIP \(never\)  SKIP: kind cluster'
  chk 'verify-h-waits.sh +SKIP \(waits\)  SKIP: a tag'
  chk 'verify-c-fail.sh +FAIL \(exit 1\)'
  chk 'verify-d-undeclared-skip.sh +FAIL \(undeclared skip\).*talk/verify-manifest.txt'
  chk 'verify-e-unlisted.sh +FAIL \(no line in talk/verify-manifest.txt; the script passed\)'
  chk '^FAIL manifest\[row\]: .*verify-e-unlisted.sh is discovered but has no line'
  chk 'verify-f-excluded.sh +EXCLUDED  a helper'
  chk 'verify-g-never-passes.sh +PASS \(manifest says never\)'
  chk '^FAIL manifest: .*verify-g-never-passes.sh passed, but talk/verify-manifest.txt says it can never pass'
  chk '^TRUTH .* run=local hub=[0-9a-f]+ units=\[fixture\] pass=1 \[observed=0 self=1 simulated=0 meta=0\] fail=4 skip=2 \[never=1 waits=1\] excluded=1 total=8 ceiling=5 fixture=1$'
  # the same fixture, --live: both declared skips become fails, nothing else moves
  out="$(env -u GITHUB_RUN_NUMBER VERIFY_SCRIPTS_FROM="$t/scripts.txt" VERIFY_MANIFEST="$t/manifest.txt" \
           VERIFY_EXCLUSIONS="$t/exclusions.txt" VERIFY_CAPDIR="$t/captures" \
           bash "$ROOT/talk/verify-all.sh" --live)"
  chk 'verify-b-declared-skip.sh +FAIL \(live required\)'
  chk '^TRUTH .* pass=1 \[observed=0 self=1 simulated=0 meta=0\] fail=6 skip=0 \[never=0 waits=0\] excluded=1 total=8 ceiling=5 live=1 fixture=1$'
  # a manifest line naming a script that is gone, and a bad class: both reported, both fails
  printf '%s\n' "$t/fx/verify-gone.sh | meta | -" "$t/fx/verify-a-pass.sh | unit-test | -" >>"$t/manifest.txt"
  out="$(env -u GITHUB_RUN_NUMBER VERIFY_SCRIPTS_FROM="$t/scripts.txt" VERIFY_MANIFEST="$t/manifest.txt" \
           VERIFY_EXCLUSIONS="$t/exclusions.txt" VERIFY_CAPDIR="$t/captures" \
           bash "$ROOT/talk/verify-all.sh")"
  chk '^FAIL manifest: .*verify-gone.sh is listed in talk/verify-manifest.txt but no longer exists'
  chk "^FAIL manifest: line 8: .*verify-a-pass.sh is listed twice"
  chk '^TRUTH .* fail=6 .* fixture=1$'
  # a unit line whose script this checkout of the unit does not carry: a NOTE, not a fail
  printf '%s\n' ".estate-clone/nowhere/verify-nowhere.sh | meta | -" >>"$t/manifest.txt"
  out="$(env -u GITHUB_RUN_NUMBER VERIFY_SCRIPTS_FROM="$t/scripts.txt" VERIFY_MANIFEST="$t/manifest.txt" \
           VERIFY_EXCLUSIONS="$t/exclusions.txt" VERIFY_CAPDIR="$t/captures" \
           bash "$ROOT/talk/verify-all.sh")"
  chk '^NOTE manifest: \.estate-clone/nowhere/verify-nowhere.sh is listed .* not in this checkout'
  chk '^TRUTH .* fail=6 .* fixture=1$'
  if [ "$good" = 1 ]; then
    echo "PASS: selfcheck: a pass, a declared never, a declared waits, a fail, an undeclared skip, a script with no manifest line, an exclusion and a never that passes each grade as they should, the split and the ceiling add up, --live turns declared skips red, a stale or malformed manifest line is a fail, and a unit line this checkout does not carry is a note"
    exit 0
  fi
  echo "FAIL: selfcheck: the instrument does not grade as documented (see above)"; exit 1
fi

# ---------------------------------------------------------------- the run
if [ -z "$FIXTURE" ]; then
  bash "$ROOT/clone-estate.sh" $REFRESH >/dev/null || { echo "FAIL: could not assemble .estate-clone/ (needs network)" >&2; exit 2; }
fi

# excluded: "path | reason" lines, '#' comments allowed
declare -A reason
prefail=0
while IFS= read -r line; do
  line="${line%%#*}"; [ -z "${line// }" ] && continue
  p="$(echo "${line%%|*}" | xargs)"; r="$(echo "${line#*|}" | xargs)"
  [ -n "$r" ] || { echo "FAIL exclusions: '$p' has no reason"; prefail=$((prefail+1)); }
  [ -e "$p" ] || { echo "FAIL exclusions: '$p' no longer exists, remove it"; prefail=$((prefail+1)); }
  reason["$p"]="$r"
done < "$EXCL"

if [ -n "$FIXTURE" ]; then
  mapfile -t SCRIPTS < "$FIXTURE"
else
  # -L: a builder's worktree symlinks the unit clones in; the clock's are real directories.
  mapfile -t SCRIPTS < <(find -L .estate-clone verify -name 'verify*.sh' -not -path '*/.work/*' -not -path '*/.git/*' | sort)
fi

# the manifest: validated once, in both directions, before anything runs.
# `FAIL manifest:` counts here (a malformed line, a duplicate, a hub line whose
# script is gone). `FAIL manifest[row]:` does not: the script it names gets a
# FAIL row of its own below whatever it exited, and one wrong script is counted
# once. `NOTE manifest:` is a unit line this checkout of the unit does not carry
# -- loud, not fatal, because a unit publishes on its own train.
WORK="$(mktemp -d)"; trap 'rm -rf "$WORK"' EXIT
printf '%s\n' "${SCRIPTS[@]}" >"$WORK/scripts.txt"
manifest_problems="$(python3 "$TM" check "$MANIFEST" --exclusions "$EXCL" --scripts "$WORK/scripts.txt")"
if [ -n "$manifest_problems" ]; then
  printf '%s\n' "$manifest_problems"
  prefail=$((prefail + $(printf '%s\n' "$manifest_problems" | grep -c '^FAIL manifest: ')))
fi
declare -A listed
while IFS= read -r p; do listed["$p"]=1; done < <(python3 "$TM" paths "$MANIFEST")

CAPDIR="${VERIFY_CAPDIR:-$ROOT/talk/captures}"; mkdir -p "$CAPDIR"
RESULTS="$WORK/results.tsv"; : >"$RESULTS"
declare -a durs=()
printf '%-70s %s\n' "SCRIPT" "STATUS"
printf '%s\n' "----------------------------------------------------------------------------"
for s in "${SCRIPTS[@]}"; do
  if [ -n "${reason[$s]:-}" ]; then
    printf '%-70s EXCLUDED  %s\n' "$s" "${reason[$s]}"
    printf '%s\tEXCLUDED\t\n' "$s" >>"$RESULTS"; continue
  fi
  # one capture file per script, full stdout+stderr, beside the TRUTH line (ticket 20 D1/Q2)
  slug="$(echo "$s" | sed -e 's#^\./##' -e 's#/#_#g' -e 's#\.sh$##')"
  cap="$CAPDIR/${slug}.out"; caprel="${cap#"$ROOT"/}"
  SECONDS=0
  timeout "$TIMEOUT" bash "$s" >"$cap" 2>&1; rc=$?
  durs+=("$SECONDS $s")
  last="$(tail -1 "$cap" | cut -c1-160)"
  status=FAIL
  case $rc in
    0) if [ -z "${listed[$s]:-}" ]; then
         printf '%-70s FAIL (no line in talk/verify-manifest.txt; the script passed)  add: %s | <class> | -\n' "$s" "$s"
       elif python3 "$TM" isnever "$MANIFEST" "$s"; then
         # a `never` script that passed: printed as it happened; summarise turns it into a FAIL row
         printf '%-70s PASS (manifest says never)  %s\n' "$s" "$last"; status=PASS
       else
         printf '%-70s PASS\n' "$s"; status=PASS
       fi;;
    3) if [ -z "${listed[$s]:-}" ]; then
         printf '%-70s FAIL (no line in talk/verify-manifest.txt; the script skipped)  %s\n' "$s" "$last"
       elif [ "$REQUIRE_LIVE" = 1 ]; then
         printf '%-70s FAIL (live required)  %s  capture: %s\n' "$s" "$last" "$caprel"
       else
         verdict="$(python3 "$TM" judge "$MANIFEST" "$s" "$last")"; jrc=$?
         if [ "$jrc" -eq 0 ]; then
           printf '%-70s SKIP (%s)  %s\n' "$s" "${verdict#declared }" "$last"; status=SKIP
         else
           printf '%-70s FAIL (undeclared skip)  %s  -- %s  capture: %s\n' "$s" "$last" "${verdict#undeclared: }" "$caprel"
         fi
       fi;;
    124) printf '%-70s FAIL (timeout %ss)  capture: %s\n' "$s" "$TIMEOUT" "$caprel";;
    *) printf '%-70s FAIL (exit %s)  %s  capture: %s\n' "$s" "$rc" "$last" "$caprel";;
  esac
  printf '%s\t%s\t%s\n' "$s" "$status" "$last" >>"$RESULTS"
done

# the counts: computed once, in python, from the rows above and the manifest.
# Extra FAIL rows (a never that passed, a pass with no line) print before the line.
summary="$(python3 "$TM" summarise "$MANIFEST" "$RESULTS" --extra-fail "$prefail")"; src=$?
counts="$(printf '%s\n' "$summary" | tail -1)"
rows="$(printf '%s\n' "$summary" | sed '$d')"
[ -z "$rows" ] || printf '%s\n' "$rows"

# units=[unit=sha ...]. Ticket 77 puts the tag beside each sha here (unit=sha@tag);
# talk/truth_manifest.py's parse_truth keeps each unit's value as text for that.
units=""
if [ -n "$FIXTURE" ]; then
  units="fixture"
else
  for u in .estate-clone/*/; do units="$units ${u#.estate-clone/}"; units="${units%/}=$(git -C "$u" rev-parse --short HEAD 2>/dev/null || echo none)"; done
fi
echo
echo "TRUTH $(date -u +%Y-%m-%dT%H:%MZ) run=${GITHUB_RUN_NUMBER:-local} hub=$(git rev-parse --short HEAD) units=[${units# }] ${counts}$([ "$REQUIRE_LIVE" = 1 ] && echo " live=1")$([ -n "$FIXTURE" ] && echo " fixture=1")"

if [ "${#durs[@]}" -gt 0 ]; then
  echo
  echo "SLOWEST 5 (seconds, wall-clock; timeout is ${TIMEOUT}s):"
  printf '%s\n' "${durs[@]}" | sort -rn | head -5 | awk '{printf "  %4ss  %s\n", $1, $2}'
fi
[ "$src" -eq 0 ] || exit 1
exit 0
