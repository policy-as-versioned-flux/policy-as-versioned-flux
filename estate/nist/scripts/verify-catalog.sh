#!/usr/bin/env bash
# Fast offline check: the catalog is well-formed OSCAL, its recorded sha256
# matches the file on disk, and the publish script produces a real pinnable
# tag+commit. No network, no cluster.
set -euo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

python3 "${HERE}/scripts/verify_catalog.py"

echo "==> dry-run: publish.sh seeds + tags cleanly"
bash "${HERE}/scripts/publish.sh" >/dev/null
echo "OK: nist catalog verified + publishable"
