#!/usr/bin/env bash
# Bump the three adopters onto a new platform implementations release.
#
# Run this AFTER platform's `cut-release.yml` has cut the bare `v<major>.<minor>.<patch>`
# implementations tag. It is not the `policy/v*` line: the adopters pin
# `{party: platform, kind: implementations}`, which is the bare tag.
#
# Why the adopters are red until then, and why forcing them would be wrong:
# their CI composes THROUGH the pinned platform tag. At v1.1.1 the party schema
# predates ticket 21 and refuses `size`, `appetite`, `publishes` and
# `reporting_currency` as unknown fields. Publisher releases, then adopter bumps.
# That is NORTH-STAR principle 4, not a fault to work around.
#
# The version is a MAJOR, established by test rather than by judgement: an
# artefact still naming the old `pricing` or `threat` parent kinds is refused by
# the new schema (`'pricing' is not one of ['controls','implementations','feed']`),
# so every existing consumer breaks. See .scratch/ecosystem/HANDOFF-2026-08-31.md.
#
#   bump-adopter-pins.sh v2.0.0
#
# It edits, in each adopter: gitops/platform/platform-pin.yaml (tag and commit
# together, the pair ADR-0001 requires), party.yaml's platform `inherits` entry,
# and then re-renders composed/ so the committed artefact matches its parents.
# It commits nothing and pushes nothing: read the diff, then commit.
set -euo pipefail

TAG="${1:?usage: bump-adopter-pins.sh v<major>.<minor>.<patch>}"
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
ESTATE="$ROOT/.estate-clone"
PLATFORM="$ESTATE/platform"

say() { printf '\033[1;36m==>\033[0m %s\n' "$*"; }
fail() { echo "FAIL: $*" >&2; exit 1; }

# The commit the tag resolves to on the REAL remote, never a local guess.
COMMIT="$(git -C "$PLATFORM" ls-remote --tags origin "refs/tags/${TAG}^{}" | cut -f1)"
[ -n "$COMMIT" ] || COMMIT="$(git -C "$PLATFORM" ls-remote --tags origin "refs/tags/${TAG}" | cut -f1)"
[ -n "$COMMIT" ] || fail "no tag ${TAG} on platform's real remote -- has cut-release.yml run?"
VERSION="${TAG#v}"
say "platform ${TAG} resolves to ${COMMIT}"

for adopter in driftwood tuppence ludlow; do
  dir="$ESTATE/$adopter"
  pin="$dir/gitops/platform/platform-pin.yaml"
  party="$dir/party.yaml"
  [ -f "$pin" ] || fail "$adopter: no $pin"

  say "$adopter: pin -> ${TAG} @ ${COMMIT:0:12}"
  # Both fields together, in the one ref block. Renovate's customManager matches
  # the same pair, so a hand edit and a bot edit produce the same shape.
  python3 - "$pin" "$TAG" "$COMMIT" <<'PY'
import re, sys
path, tag, commit = sys.argv[1], sys.argv[2], sys.argv[3]
text = open(path).read()
new, n = re.subn(r"(\n\s*tag:\s*)v[0-9][^\s#]*(\s*\n\s*commit:\s*)[0-9a-f]{40}",
                 lambda m: f"{m.group(1)}{tag}{m.group(2)}{commit}", text, count=1)
if n != 1:
    raise SystemExit(f"{path}: expected exactly one tag/commit pair, matched {n}")
open(path, "w").write(new)
PY

  say "$adopter: party.yaml platform inherits -> ${VERSION}"
  python3 - "$party" "$VERSION" <<'PY'
import re, sys
path, version = sys.argv[1], sys.argv[2]
text = open(path).read()
new, n = re.subn(r"(party:\s*platform,\s*kind:\s*implementations,\s*version:\s*\")[^\"]+(\")",
                 lambda m: f"{m.group(1)}{version}{m.group(2)}", text, count=1)
if n != 1:
    raise SystemExit(f"{path}: expected one platform implementations entry, matched {n}")
open(path, "w").write(new)
PY
done

say "re-rendering every adopter's composed/ against its new parent"
echo "   run the composition the way compose-check does, then read the diff:"
echo "     python3 $PLATFORM/compose/composition.py compose --adopter-dir $ESTATE/<adopter>"
echo "   and confirm it is byte-for-byte with:"
echo "     bash $PLATFORM/compose/verify-composition.sh"
say "nothing committed and nothing pushed. Read the diff, then commit."
