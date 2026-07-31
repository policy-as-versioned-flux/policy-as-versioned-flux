#!/usr/bin/env bash
# sign.sh — detached-sign a feed JSON with the shared platform feeds ed25519 key.
#
# ponytail: same repo-local ed25519-via-openssl trust shape as estate/ico/schema/
# sign.sh -- one key for all three feeds here (they're all platform-published),
# vs ico's own key (ico is a separate publishing org). Upgrade path: cosign
# sign-blob against Rekor if a feed artifact needs its own transparency-log entry.
set -euo pipefail
here="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
feed="${1:?usage: sign.sh <feed e.g. threat-register|cve|eol> <version e.g. v1> <filename e.g. register.json>}"
version="${2:?usage: sign.sh <feed> <version> <filename>}"
file="${3:?usage: sign.sh <feed> <version> <filename>}"
target="$here/$feed/$version/$file"
key="$here/keys/feeds-signing-key.pem"

openssl pkeyutl -sign -inkey "$key" -rawin -in "$target" -out "$target.sig"
echo "signed: $target.sig"
