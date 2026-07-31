#!/usr/bin/env bash
# sign.sh — detached-sign a penalty-schema.json with the ico ed25519 key.
#
# ponytail: a repo-local ed25519 keypair via openssl, not gitsign/Rekor keyless —
# gitsign attests *commits* (the living war-gamer PR loop); this signs a *file*
# artifact offline, same trust shape, zero external dependency. Upgrade path: swap
# for cosign sign-blob against the same Rekor instance if the artifact needs a
# transparency-log entry of its own.
set -euo pipefail
here="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
version="${1:?usage: sign.sh <version-dir e.g. v1>}"
schema="$here/$version/penalty-schema.json"
key="$here/keys/ico-signing-key.pem"

openssl pkeyutl -sign -inkey "$key" -rawin -in "$schema" -out "$schema.sig"
echo "signed: $schema.sig"
