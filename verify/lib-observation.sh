#!/usr/bin/env bash
# Sourced, not run (ecosystem ticket 76, "every green rests on an observation").
#
# A hub check with a live tail -- Rekor, SPIRE, a cluster, a CLI that may not be installed --
# had no way to say "the offline half held and the live half was never looked at", so it printed
# a note and asserted PASS anyway. talk/verify-all.sh grades exit 0 as PASS, so the run reported
# a property it had not observed. These three helpers give the tail its third outcome.
#
#   could_not_look <what was not looked at>
#       print it and record it. Never a failure: a check does not FAIL because it could not look.
#   pass_or_skip <claim>
#       the final verdict. Exit 0 with "PASS: <claim>" only when nothing was recorded; otherwise
#       exit 3 with a SKIP: last line naming every tail that could not look.
#   selfcheck_absent <script> <tool>...
#       run the could-not-look branch on a machine that has the instruments: re-run <script> with
#       <tool>... unreachable and require exit 3 with a SKIP: last line. Each PATH directory
#       holding one of the tools is rebuilt as a farm of symlinks to its other entries, so the
#       neighbours stay reachable (python3, with pyyaml, lives beside cosign under homebrew).
#       Callers pass an absolute path to themselves. A no-op inside the child re-run.
#
#       CEILING (measured 2026-09-04, ticket 76 review). The leg re-runs the WHOLE script, so
#       every script that calls it does its work twice, plus the cost of building the PATH
#       symlink farm: verify-provenance.sh takes 19.5s with the leg and 5.5s with it disabled
#       (PAV_SELFCHECK_CHILD=1), a 3.5x. The same doubling applies to verify-proportionality.sh
#       here and to each of the seven computed-semver scripts through .estate-clone/platform/
#       lib.sh. It is paid on every gate run, not only in CI.
#       ponytail: let a script expose its could-not-look branch as one function and re-run only
#       that, or gate the leg behind a flag the gate sets once per wave rather than per script,
#       once the gate's wall-clock is the thing that hurts.
#
# The estate's own copy of this contract is .estate-clone/platform/lib.sh; this is the hub's,
# kept separate because the hub venv, not python3, is the interpreter here.

UNLOOKED=""
UNLOOKED_N=0

could_not_look() {
  echo "  ??   could not look: $*"
  UNLOOKED="${UNLOOKED:+$UNLOOKED; }$*"
  UNLOOKED_N=$((UNLOOKED_N + 1))
}

pass_or_skip() {
  if [ -n "$UNLOOKED" ]; then
    # The verdict is the LAST LINE and verify-all.sh prints it in a table, so the reason is what
    # goes there: the tails that could not look. The claim goes on the line above it.
    echo "  the claim this run did NOT observe in full: $*"
    printf 'SKIP: the offline proof holds; %d live tail(s) could not look, so this run did not observe the claim above -- %s\n' \
      "$UNLOOKED_N" "$UNLOOKED"
    exit 3
  fi
  echo "PASS: $*"
}

selfcheck_absent() {
  local script="$1"; shift
  [ -z "${PAV_SELFCHECK_CHILD:-}" ] || return 0
  local names="$*" hidden=" $* " farm sub dir f keep="" out rc=0 last
  farm="$(mktemp -d)"
  local IFS=:
  for dir in $PATH; do
    sub=""
    for f in "$@"; do if [ -x "$dir/$f" ]; then sub=hide; fi; done
    if [ "$sub" = hide ]; then
      sub="$farm/$(printf '%s' "$dir" | tr / _)"
      mkdir -p "$sub"
      for f in "$dir"/*; do
        case "$hidden" in *" ${f##*/} "*) ;; *) ln -s "$f" "$sub/" 2>/dev/null || true ;; esac
      done
      keep="${keep:+$keep:}$sub"
    else
      keep="${keep:+$keep:}$dir"
    fi
  done
  IFS=$' \t\n'
  out="$(PAV_SELFCHECK_CHILD=1 PATH="$keep" "${BASH:-bash}" "$script" 2>&1)" || rc=$?
  rm -rf "$farm"
  last="$(printf '%s\n' "$out" | tail -1)"
  case "$rc:$last" in
    3:SKIP:*) echo "  ok   selfcheck: with $names unreachable this script exits 3 and its last line is SKIP:" ;;
    *) echo "FAIL: selfcheck: with $names unreachable ${script##*/} exited $rc (want 3), last line: ${last:0:120}"
       exit 1 ;;
  esac
}
