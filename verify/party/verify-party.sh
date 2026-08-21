#!/usr/bin/env bash
# Beat: "roles: is data, and it is checked — a risk-bearer with no appetite
# entry, a publisher shipping nothing signed, an adopter pinning nothing are
# all refused." Ticket 03 warned a `roles:` field nothing validates would be
# the estate's fourth assertion that cannot fail; this is the guard that makes
# it fail correctly, plus the proof that merging platform's strict appetite
# band into the shared store (ticket 16 part 2) did not sweep it in as a
# fourth institution. Offline, pure stdlib. Exits non-zero if the beat would
# fail on stage.
set -euo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
say()  { printf '\033[1;36m==>\033[0m %s\n' "$*"; }
fail() { echo "FAIL: $*" >&2; exit 1; }
have() { command -v "$1" >/dev/null 2>&1; }

have python3 || fail "python3 required"

ESTATE="$HERE/../../.estate-clone"
[ -d "$ESTATE/platform" ] || bash "$HERE/../../clone-estate.sh" || fail "could not assemble .estate-clone/ (needs network — see clone-estate.sh)"

say "1. every party's declared roles: match real filesystem evidence"
say "2. the guard actually bites (planted risk-bearer/publisher/adopter violations)"
say "3. platform's appetite band moved into the shared store, still three institutions"
python3 "$HERE/party.py" selfcheck || fail "party role guard selfcheck failed"

echo
echo "PASS: roles: is machine-checked data — platform, nist, ico, driftwood, tuppence"
echo "and ludlow each declare roles the filesystem actually backs up."
