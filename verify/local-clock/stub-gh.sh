#!/usr/bin/env bash
# A stand-in for the `gh` binary (ecosystem ticket 92, round 4), so the local clock's --push
# path can be exercised end to end against a throwaway bare origin with no GitHub, no token and
# no network. The clock reaches it through LOCAL_CLOCK_GH. Every call is appended, verbatim, to
# LOCAL_CLOCK_GH_LOG (default: nowhere), which is how a test reads the OPERATION the clock asked
# for. It answers two verbs and nothing else:
#   auth status   exit 0, unless LOCAL_CLOCK_GH_STUB=unauth (then exit 1, as gh does logged out)
#   pr create     print a URL on the reserved .invalid domain -- a stand-in, never a real PR
# This file is a fixture and says so on every line it prints.
set -euo pipefail
printf '%s\n' "$*" >>"${LOCAL_CLOCK_GH_LOG:-/dev/null}"
case "${1:-} ${2:-}" in
  "auth status")
    if [ "${LOCAL_CLOCK_GH_STUB:-ok}" = ok ]; then
      echo "stub-gh: logged in as a fixture identity (this is a stand-in for gh, not GitHub)"; exit 0
    fi
    echo "stub-gh: You are not logged into any GitHub hosts (a stand-in, refusing on purpose)" >&2; exit 1;;
  "pr create")
    echo "https://github.invalid/stub/pull/1";;
  *)
    echo "stub-gh: no stand-in for '$*'" >&2; exit 2;;
esac
