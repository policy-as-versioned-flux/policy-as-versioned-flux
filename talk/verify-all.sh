#!/usr/bin/env bash
# The truth surface. The only citable source of what works.
#
# Discovers every verify*.sh under .estate-clone/ (the six real unit repos,
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
#   talk/verify-all.sh            offline run; SKIP is not a failure
#   talk/verify-all.sh --live     SKIP counts as FAIL (you asked for live)
#   talk/verify-all.sh --refresh  re-clone the units first
#
# Every run ends with one TRUTH line carrying the date, the run number, the
# hub commit and the six unit commits. Quote that line, nothing else.
set -u
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT" || exit 2
REQUIRE_LIVE=0; REFRESH=""
for a in "$@"; do case "$a" in --live) REQUIRE_LIVE=1;; --refresh) REFRESH=--refresh;; esac; done
TIMEOUT="${VERIFY_TIMEOUT:-300}"
EXCL="$ROOT/talk/verify-exclusions.txt"

bash "$ROOT/clone-estate.sh" $REFRESH >/dev/null || { echo "FAIL: could not assemble .estate-clone/ (needs network)" >&2; exit 2; }

# excluded: "path | reason" lines, '#' comments allowed
declare -A reason
fail=0
while IFS= read -r line; do
  line="${line%%#*}"; [ -z "${line// }" ] && continue
  p="$(echo "${line%%|*}" | xargs)"; r="$(echo "${line#*|}" | xargs)"
  [ -n "$r" ] || { echo "FAIL exclusions: '$p' has no reason"; fail=$((fail+1)); }
  [ -e "$p" ] || { echo "FAIL exclusions: '$p' no longer exists, remove it"; fail=$((fail+1)); }
  reason["$p"]="$r"
done < "$EXCL"

mapfile -t SCRIPTS < <(find .estate-clone verify -name 'verify*.sh' -not -path '*/.work/*' -not -path '*/.git/*' | sort)

pass=0; skip=0; excluded=0; log="$(mktemp)"
printf '%-70s %s\n' "SCRIPT" "STATUS"
printf '%s\n' "----------------------------------------------------------------------------"
for s in "${SCRIPTS[@]}"; do
  if [ -n "${reason[$s]:-}" ]; then printf '%-70s EXCLUDED  %s\n' "$s" "${reason[$s]}"; excluded=$((excluded+1)); continue; fi
  timeout "$TIMEOUT" bash "$s" >"$log" 2>&1; rc=$?
  last="$(tail -1 "$log" | cut -c1-160)"
  case $rc in
    0) printf '%-70s PASS\n' "$s"; pass=$((pass+1));;
    3) if [ "$REQUIRE_LIVE" = 1 ]; then printf '%-70s FAIL (live required)  %s\n' "$s" "$last"; fail=$((fail+1))
       else printf '%-70s SKIP  %s\n' "$s" "$last"; skip=$((skip+1)); fi;;
    124) printf '%-70s FAIL (timeout %ss)\n' "$s" "$TIMEOUT"; fail=$((fail+1));;
    *) printf '%-70s FAIL (exit %s)  %s\n' "$s" "$rc" "$last"; fail=$((fail+1));;
  esac
done
rm -f "$log"

units=""
for u in .estate-clone/*/; do units="$units ${u#.estate-clone/}"; units="${units%/}=$(git -C "$u" rev-parse --short HEAD)"; done
echo
echo "TRUTH $(date -u +%Y-%m-%dT%H:%MZ) run=${GITHUB_RUN_NUMBER:-local} hub=$(git rev-parse --short HEAD) units=[${units# }] pass=$pass fail=$fail skip=$skip excluded=$excluded total=${#SCRIPTS[@]}$([ "$REQUIRE_LIVE" = 1 ] && echo " live=1")"
[ "$fail" -eq 0 ] || exit 1
exit 0
