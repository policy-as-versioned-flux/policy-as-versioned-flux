#!/usr/bin/env bash
# Ticket 82. Nine public repositories say what they are: every party.yaml and README carries the
# one disclaimer line (a demonstration party, not the authority it names), the two regulators
# carry DISCLAIMER.md, nist/NOTICE attributes the SP 800-53 catalogue and baselines to NIST as a
# public-domain US Government work and cites the same URL and sha256 values its own provenance
# manifests record, and the hub is Apache-2.0 like the eight units.
# Exit 0 observed true; 3 could not look (no estate, no interpreter); 1 observed false.
# Offline: reads committed files only.
set -uo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$HERE/../.."
PY="$ROOT/.venv/bin/python"
if [ ! -x "$PY" ]; then
  PY=python3
  "$PY" -c 'import yaml' 2>/dev/null || { echo "SKIP: no .venv and python3 lacks pyyaml"; exit 3; }
fi
[ -d "$ROOT/.estate-clone/platform" ] || { echo "SKIP: no .estate-clone/ -- run ./clone-estate.sh first"; exit 3; }

say() { printf '\033[1;36m==>\033[0m %s\n' "$*"; }
say "1. every party.yaml carries the disclaimer as a comment; every README carries it"
say "2. ico and nist carry DISCLAIMER.md; nist/NOTICE cites the catalogue it attributes"
say "3. the hub LICENSE is Apache-2.0 and its README says so"
say "4. the guard bites: each violation planted in a copy is refused, the restored copy passes"
"$PY" "$HERE/disclaimer.py" selfcheck; rc=$?
case $rc in
  0) echo; echo "PASS: all eight parties say they are a demonstration on their signed artefact and their README, the two regulators carry the long form, nist attributes NIST's public-domain work by URL and sha256, and the hub is licensed Apache-2.0 like the units";;
  3) echo "SKIP: disclaimer.py could not look";;
  *) echo "FAIL: disclaimer.py selfcheck observed false (exit $rc)";;
esac
exit "$rc"
