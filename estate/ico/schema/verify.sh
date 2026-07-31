#!/usr/bin/env bash
# verify.sh — offline signature + shape check for a versioned ico penalty schema.
#
# Usage: verify.sh <version-dir e.g. v1>
set -euo pipefail
here="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
version="${1:?usage: verify.sh <version-dir e.g. v1>}"
schema="$here/$version/penalty-schema.json"
sig="$schema.sig"
pubkey="$here/keys/ico-signing-key.pub.pem"

[ -f "$schema" ] || { echo "FAIL: no schema at $schema"; exit 1; }
[ -f "$sig" ] || { echo "FAIL: no signature at $sig"; exit 1; }

python3 -c "import json,sys; d=json.load(open('$schema')); assert d.get('schema_version')=='$version', d.get('schema_version')" \
  || { echo "FAIL: schema_version field doesn't match directory $version"; exit 1; }

openssl pkeyutl -verify -pubin -inkey "$pubkey" -rawin -in "$schema" -sigfile "$sig" \
  || { echo "FAIL: signature does not verify for $schema"; exit 1; }

echo "ok  $version signature verified, schema_version matches"
