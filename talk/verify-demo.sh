#!/usr/bin/env bash
# The demo check (ticket 47, ticket 20 Q4). Discovered by talk/verify-all.sh
# through the symlink verify/demo/verify-demo.sh, because the gate globs
# .estate-clone/ and verify/ only.
#
# It refuses the deck when:
#   - talk/build_deck.py cannot build it from this run's captures;
#   - a beat cites a capture that is not in this run;
#   - a beat's status tag is not the grade this run gave that script, or
#     disagrees with the verdict step 7's own capture recorded for that step;
#   - a money amount, percentage or count in a beat body is not in that beat's
#     capture, verbatim, or sits on a beat with no capture behind it;
#   - the beats are not the seven NORTH-STAR section 4 steps, in order;
#   - the phrase lint hits one of exactly four refused phrases: exemption,
#     hourglass, admission gate, deny gate. Every OTHER use of the word gate is
#     printed as a human review item and is not a failure;
#   - the committed talk/deck.md is not the generated file (hand edited) -- every
#     check above is run over the committed file as well as over the rebuild;
#   - a section 4 step check exists on disk but this run wrote no capture for it;
#   - a TRUTH line is quoted that was not recorded at this deck's own commit.
#
# Named ceilings, so nobody mistakes what this observes:
#   - headers, dates, tags, step numbers, ticket and ADR references and the
#     "$ bash <script>" command line are OUTSIDE the figure check;
#   - the grade comes from the capture's last line, because the gate keeps the
#     capture and not the exit code. Step 7's table is read as a second,
#     independently produced opinion of the same verdicts;
#   - build order: this script sorts before verify/e2e/ in the gate's glob, so
#     inside a gate run the e2e captures it reads are the ones on disk, which may
#     be the previous run's. It grades the deck against the captures it can see.
#     The committed deck is built by the scheduled workflow AFTER verify-all.sh
#     finishes, which is where "the live run id is the scheduled one" is kept;
#   - the marp render is opt-in (DECK_RENDER=1). The gate runs offline and
#     npx @marp-team/marp-cli fetches from the network. Ticket 47 renders it by
#     hand and CI renders it on the scheduled run.
set -u
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && git rev-parse --show-toplevel)" || {
  echo "SKIP: not inside a git work tree, cannot locate the hub root"; exit 3; }
cd "$ROOT" || exit 2

command -v python3 >/dev/null || { echo "SKIP: no python3"; exit 3; }
[ -f talk/narration.json ] || { echo "FAIL: talk/narration.json is missing, the deck has no prose"; exit 1; }
ls talk/captures/*.out >/dev/null 2>&1 || {
  echo "SKIP: no captures in talk/captures/, so there is no run to build a deck from; run talk/verify-all.sh first"
  exit 3; }
# Coverage, not non-emptiness. "At least one .out exists" used to be the whole
# assertion: deleting every seven-step capture rendered all seven beats NOCHECK
# ("no check yet, owned by ticket NN") and this script still said PASS, telling
# a reader the check does not exist when the run had failed to produce it.
# build_deck.py --check now refuses a NOCHECK whose script is on disk; this is
# the same question asked before the build, so the reason is legible here too.
missing=""
for s in verify/e2e/verify-e2e-step*.sh; do
  [ -e "$s" ] || continue
  s="${s#./}"; cap="talk/captures/$(echo "${s%.sh}" | tr / _).out"
  [ -f "$cap" ] || missing="$missing $s"
done
if [ -n "$missing" ]; then
  echo "FAIL: these NORTH-STAR section 4 step checks exist on disk but this run wrote no capture for them:$missing"
  exit 1
fi

TMP="$(mktemp -d)"; trap 'rm -rf "$TMP"' EXIT

python3 talk/build_deck.py --selfcheck || { echo "FAIL: build_deck.py selfcheck failed"; exit 1; }
python3 talk/build_deck.py --out "$TMP/deck.md" || { echo "FAIL: the deck does not build from this run's captures"; exit 1; }
echo "ok  the deck builds: $(wc -l <"$TMP/deck.md" | tr -d ' ') lines from $(ls -A talk/captures | grep -c '\.out$') captures"

python3 talk/build_deck.py --check "$TMP/deck.md" || { echo "FAIL: the built deck does not survive its own checks"; exit 1; }

grep -q "GENERATED FILE" talk/deck.md 2>/dev/null || {
  echo "FAIL: talk/deck.md is not the generated file; run python3 talk/build_deck.py"; exit 1; }
if ! diff <(grep -o 'beat step=[0-9]* status=[A-Z]*' talk/deck.md) \
          <(grep -o 'beat step=[0-9]* status=[A-Z]*' "$TMP/deck.md") >"$TMP/d" 2>&1; then
  echo "  the committed deck's beats differ from a rebuild:"; sed 's/^/    /' "$TMP/d"
  echo "FAIL: talk/deck.md has been hand edited or is stale; run python3 talk/build_deck.py"; exit 1
fi
echo "ok  the committed talk/deck.md is the generated file, with the same beats as a rebuild"

# The one that mattered: every check above ran against the REBUILD. Nothing ran
# against the file a reader actually opens, so a hand-edited figure, a forged
# TRUTH headline and a rewritten could-not-look reason all passed (review
# 2026-08-29). A whole-file diff is not the fix -- the rebuild's "built HH:MMZ"
# stamp makes that flaky -- so the deck's own checks are run over the committed
# file as well.
python3 talk/build_deck.py --check talk/deck.md || {
  echo "FAIL: the committed talk/deck.md does not survive its own checks"; exit 1; }
echo "ok  the committed talk/deck.md survives the figure, status, headline and phrase checks"

if [ "${DECK_RENDER:-0}" = 1 ]; then
  cp -R talk/diagrams "$TMP/diagrams"   # the deck's images, so marp resolves them
  npx --yes @marp-team/marp-cli@latest --html "$TMP/deck.md" -o "$TMP/deck.html" >/dev/null 2>&1 || {
    echo "FAIL: marp-cli could not render the deck"; exit 1; }
  echo "ok  marp-cli rendered the deck: $(wc -c <"$TMP/deck.html" | tr -d ' ') bytes"
fi

echo "PASS: the deck is generated from this run's captures, every section 4 step check that exists on disk produced one, the committed file and a rebuild both survive the checks, its seven beats are the section 4 steps in order carrying this run's own grades, every figure on a beat is a figure in that beat's capture and no figure sits off a beat, any quoted TRUTH line is this commit's own, and the phrase lint is clean"
