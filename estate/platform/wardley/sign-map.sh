#!/usr/bin/env bash
# sign-map.sh -- render the Wardley map from the signed market intel and
# detached-sign both, so a map UPDATE lands as an attestable, reviewable commit
# (ticket 23, third acceptance criterion).
#
# Two layers of attestation, same as the rest of the estate:
#   * offline-verifiable: detached ed25519 sig with the shared platform feeds key
#     (../feeds/keys), verified by verify-wardley.sh with no network.
#   * commit-time keyless: the git commit that lands intel/*.json + map/*.json is
#     gitsign-signed (OIDC -> Fulcio -> Rekor) exactly like the war-gamer's PRs, so
#     the map's provenance is a transparency-log entry. That happens at `git commit`
#     time (the wave-commit step), not here.
#
# ponytail: reuses ../feeds/sign.sh's key + shape rather than a new trust root --
# the Wardley layer is platform-published, same publisher as the reactive feeds.
set -euo pipefail
here="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
key="$here/../feeds/keys/feeds-signing-key.pem"

intel="$here/intel/market-intel.json"
map="$here/map/wardley-map.json"

# Render the map from the (signed) intel, deterministically, then sign both.
python3 "$here/wardley.py" map --intel "$intel" > "$map"

for f in "$intel" "$map"; do
  openssl pkeyutl -sign -inkey "$key" -rawin -in "$f" -out "$f.sig"
  echo "signed: $f.sig"
done
