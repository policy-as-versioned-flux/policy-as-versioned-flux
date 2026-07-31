#!/usr/bin/env bash
# Demonstrates the "regulator change arrives as a reviewable PR" beat: bump
# driftwood's pinned nist catalog tag on a branch and show the diff a human
# reviews before merge. Never pushes or opens the PR itself (propose-never-
# merge rail lives with a human/CI, not this script); it stops at the diff.
#
# Usage: bump-nist-pin.sh v1.1.0
set -euo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"   # estate/driftwood
NEW_TAG="${1:?usage: bump-nist-pin.sh <new-tag, e.g. v1.1.0>}"
FILE="${HERE}/gitops/flux-system/gotk-sync-nist.yaml"

say() { printf '\033[1;36m==>\033[0m %s\n' "$*"; }

BRANCH="bump-nist-${NEW_TAG}"
say "would open PR '$BRANCH': bump pinned nist catalog -> ${NEW_TAG}"

sed -i.bak "s/tag: v[0-9][0-9.]*/tag: ${NEW_TAG}/" "$FILE"

echo
echo "--- diff (this is the PR body a human reviews before merge) ---"
diff -u "${FILE}.bak" "$FILE" | tail -n +3
echo "--- end diff ---"
rm -f "${FILE}.bak"
echo
say "next (human/CI, not this script): commit on '$BRANCH', gitsign, open PR, review, merge"
