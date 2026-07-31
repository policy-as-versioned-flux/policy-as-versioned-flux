#!/usr/bin/env bash
# Publish the nist catalog release: seed a real git repo from catalog/, tag it,
# print the tag+commit institutions pin. Idempotent (safe to re-run; re-seeds
# into a fresh .work dir each time). Mirrors driftwood/scripts/up.sh's seeding
# step — same offline-pin convention.
#
# On the real `policy-as-versioned-nist` GitHub remote this tag is
# gitsign-signed (keyless -> Rekor), verified out-of-band via `git verify-tag`
# / Rekor lookup (Flux's GitRepository.spec.verify only speaks OpenPGP). This
# script pins tag+commit for immutability; it does not fake a signature.
set -euo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"   # estate/nist
CATALOG_DIR="${HERE}/catalog"
WORK="${HERE}/.work/seed"
VERSION="$(python3 -c "import json;print(json.load(open('${CATALOG_DIR}/CATALOG_VERSION.json'))['publishedVersion'])")"
TAG="v${VERSION}"

say() { printf '\033[1;36m==>\033[0m %s\n' "$*"; }

say "seeding nist catalog repo @ ${TAG}"
rm -rf "$WORK"; mkdir -p "$WORK"
cp -R "$CATALOG_DIR/." "$WORK/"
git -C "$WORK" init -q -b main
git -C "$WORK" -c user.email=regulator@nist -c user.name=nist add -A
git -C "$WORK" -c user.email=regulator@nist -c user.name=nist commit -q -m "nist 800-53 catalog @ ${VERSION}"
git -C "$WORK" -c user.email=regulator@nist -c user.name=nist tag -a "$TAG" -m "nist catalog ${TAG}"
COMMIT="$(git -C "$WORK" rev-parse HEAD)"

say "published ${TAG} @ ${COMMIT}"
echo "pin: { tag: ${TAG}, commit: ${COMMIT} }"
