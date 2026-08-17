#!/usr/bin/env bash
# THE DEMO SEQUENCE (build ticket 77; decision ticket 22).
#
# Decision ticket 22 resolved the thesis order and made it explicit that the order IS the
# argument: (b) falsifiability first, then (c) versioned governance, concluding in (a) the
# one-currency comparison — deliberately last, because it is the most seductive claim and the
# least defensible standing alone. Before this ticket that order was narrated in prose and in
# CI step ordering, both of which can drift silently; this script is the one place it is run and
# checked, and harness guard `the_demo_sequence_earns_credibility_before_it_spends_it` reads this
# file's own text to hold CI to it (build ticket 78's own precedent: no bash parser exists, so an
# orchestrator's consistency with its own declared order is checked against its literal source).
#
# Royal Mail and Intel both carry (b) — falsifiability, retrospective and live-forward — and
# neither calls a pricing verb. Netflix alone carries (c) and (a), and runs last: £ appears
# nowhere before this, the third and final beat.
#
# Exits non-zero if any beat fails. OFFLINE: python3 + PyYAML + git, nothing else (same as every
# beat this runs).
set -euo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Each beat gets its own subdirectory of one work root, so all three sets of artefacts survive
# the run for inspection rather than three scripts colliding in one flat directory.
WORK="${1:-$(mktemp -d "${TMPDIR:-/tmp}/twin-sequence.XXXXXXXX")}"

say()  { printf '\033[1;35m===>\033[0m %s\n' "$*"; }

say "BEAT 1/3 — royal-mail: falsifiability (b), retrospective. THE RESULT IS RED, ON PURPOSE."
bash "$HERE/beat-royal-mail.sh" "$WORK/royal-mail"

say "BEAT 2/3 — intel: falsifiability (b), live and forward. Unscoreable today, and says so."
bash "$HERE/beat-intel.sh" "$WORK/intel"

say "BEAT 3/3 — netflix: versioned governance (c), concluding in the one-currency comparison (a)."
bash "$HERE/beat-netflix.sh" "$WORK/netflix"

echo
echo "PASS: the demo sequence ran b -> b -> c -> a. Royal Mail and Intel both proved the twin can"
echo "be checked, and neither one priced anything. Netflix proposed enactment before it priced a"
echo "response, so the one-currency comparison concluded the sequence rather than opening it —"
echo "the order is the argument, and it is now a script rather than a claim."
echo
echo "artefacts: $WORK"
