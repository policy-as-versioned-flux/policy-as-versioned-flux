#!/usr/bin/env bash
# verify.sh — offline signature + shape check for one versioned feed file.
#
# Usage: verify.sh <feed e.g. threat-register|cve|eol> <version e.g. v1> <filename e.g. register.json>
set -euo pipefail
here="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
feed="${1:?usage: verify.sh <feed> <version> <filename>}"
version="${2:?usage: verify.sh <feed> <version> <filename>}"
file="${3:?usage: verify.sh <feed> <version> <filename>}"
target="$here/$feed/$version/$file"
sig="$target.sig"
pubkey="$here/keys/feeds-signing-key.pub.pem"

[ -f "$target" ] || { echo "FAIL: no feed file at $target"; exit 1; }
[ -f "$sig" ] || { echo "FAIL: no signature at $sig"; exit 1; }

python3 -c "import json,sys; d=json.load(open('$target')); assert d.get('feed_version')=='$version', d.get('feed_version')" \
  || { echo "FAIL: feed_version field doesn't match directory $version"; exit 1; }

openssl pkeyutl -verify -pubin -inkey "$pubkey" -rawin -in "$target" -sigfile "$sig" \
  || { echo "FAIL: signature does not verify for $target"; exit 1; }

echo "ok  $feed/$version signature verified, feed_version matches"
