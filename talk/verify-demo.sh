#!/usr/bin/env bash
# The demo check (ticket 47, ticket 20 Q4, ticket 66). Discovered by
# talk/verify-all.sh through the symlink verify/demo/verify-demo.sh, because the
# gate globs .estate-clone/ and verify/ only.
#
# Two decks are graded. A REBUILD from the captures on disk (this run's), and
# the COMMITTED talk/deck.md, which names the recorded run it describes and is
# graded against THAT run's captures, read out of the commit that recorded them.
#
# It refuses when:
#   - talk/build_deck.py cannot build a deck from this run's captures;
#   - a beat cites a capture that is not in the run the deck names;
#   - a beat's status tag is not the grade that run gave that script, or
#     disagrees with the verdict step 7's own capture recorded for that step;
#   - a money amount, percentage or count in a beat body is not in that beat's
#     capture, verbatim, or sits on a beat with no capture behind it;
#   - the beats are not the seven NORTH-STAR section 4 steps, in order;
#   - the phrase lint hits one of exactly four refused phrases: exemption,
#     hourglass, admission gate, deny gate. Every OTHER use of the word gate is
#     printed as a human review item and is not a failure;
#   - the committed talk/deck.md is not the generated file, names no recorded
#     run, or is not what a rebuild from the run it names produces (hand edited
#     or stale) -- every check above is run over the committed file as well;
#   - a section 4 step check exists on disk but this run wrote no capture for it;
#   - a quoted TRUTH line is not the line that recorded the run the deck names.
#
# Named ceilings, so nobody mistakes what this observes:
#   - headers, dates, tags, step numbers, ticket and ADR references, the deck's
#     own run/hub stamp and the "$ bash <script>" command line are OUTSIDE the
#     figure check;
#   - the grade comes from the capture's last line, because the gate keeps the
#     capture and not the exit code. Step 7's table is read as a second,
#     independently produced opinion of the same verdicts;
#   - build order: this script sorts before verify/e2e/ in the gate's glob, so
#     inside a gate run the e2e captures the REBUILD reads are the ones on disk,
#     which may be the previous run's. The rebuild is graded against the
#     captures it can see and quotes no TRUTH line, because this run has none yet;
#   - the committed deck is NOT rebuilt by the clock. truth.yml's observation
#     lane (ADR-0024) is talk/truth.log, talk/captures, drift/samples.jsonl and
#     observations; talk/deck.md is a generated declaration outside it. So the
#     committed deck lags the log by however many runs since someone last ran
#     `python3 talk/build_deck.py` and committed. That lag is not a defect here:
#     the deck is graded against the run it names, not the newest. Before
#     ticket 66 it was graded against "this run", which called every scheduled
#     run whose grades moved a hand edit (runs 14 to 22 all red);
#   - the named run's captures come out of git. If the commit that recorded
#     that run is not reachable (a shallow clone whose history stops after it),
#     this script deepens the clone once, bounded, and otherwise says SKIP with
#     the reason. It never grades the committed deck against the disk;
#   - the marp render is opt-in (DECK_RENDER=1). The gate runs offline and
#     npx @marp-team/marp-cli fetches from the network. Ticket 47 renders it by
#     hand.
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

# The committed deck names the run it describes. Read that name, and find the
# commit that recorded the run: the lane commit whose newest TRUTH line is that
# run's, which also carries that run's captures.
name_out="$(python3 talk/build_deck.py --name talk/deck.md)"; rc=$?
if [ "$rc" = 3 ] && [ "$(git rev-parse --is-shallow-repository)" = true ]; then
  # A shallow checkout (actions/checkout defaults to depth 1) can reach only
  # HEAD's newest run. Deepen once, bounded; a failure to fetch is a SKIP below.
  git fetch -q --deepen=100 origin 2>/dev/null || true
  name_out="$(python3 talk/build_deck.py --name talk/deck.md)"; rc=$?
fi
case "$rc" in
  0) echo "ok  the committed talk/deck.md describes recorded $name_out" ;;
  3) echo "  $name_out"
     echo "SKIP: the committed talk/deck.md names a recorded run whose recording commit this checkout cannot reach; run python3 talk/build_deck.py at a full clone and commit the deck"
     exit 3 ;;
  *) echo "  $name_out"
     echo "FAIL: the committed talk/deck.md describes no recorded run; run python3 talk/build_deck.py and commit it"
     exit 1 ;;
esac
named="${name_out#run=}"; named="${named%% *}"

# Is the committed file what a rebuild from the run IT NAMES produces? Read from
# that run's commit, so a local gate run that has just overwritten talk/captures/
# with its own results cannot make the committed deck look stale (it did, every
# time, from 2026-08-31 until ticket 66). The "built HH:MMZ" stamp makes a
# whole-file diff flaky, so the beat markers are compared and the deck's own
# checks are run over the committed file instead.
python3 talk/build_deck.py --run "$named" --out "$TMP/named.md" >/dev/null || {
  echo "FAIL: the deck does not rebuild from run $named's committed captures"; exit 1; }
if ! diff <(grep -o 'beat step=[0-9]* status=[A-Z]*' talk/deck.md) \
          <(grep -o 'beat step=[0-9]* status=[A-Z]*' "$TMP/named.md") >"$TMP/d" 2>&1; then
  echo "  the committed deck's beats differ from a rebuild of run $named:"; sed 's/^/    /' "$TMP/d"
  echo "FAIL: talk/deck.md has been hand edited; run python3 talk/build_deck.py"; exit 1
fi
echo "ok  the committed talk/deck.md is the generated file, with the same beats as a rebuild of run $named"

# The one that mattered: every check above ran against the REBUILD. Nothing ran
# against the file a reader actually opens, so a hand-edited figure, a forged
# TRUTH headline and a rewritten could-not-look reason all passed (review
# 2026-08-29). So the deck's own checks are run over the committed file as
# well, against the captures of the run it names.
python3 talk/build_deck.py --check talk/deck.md; rc=$?
case "$rc" in
  0) echo "ok  the committed talk/deck.md survives the figure, status, headline and phrase checks against run $named" ;;
  3) echo "SKIP: run $named's recording commit became unreachable between two reads; run this check again"; exit 3 ;;
  *) echo "FAIL: the committed talk/deck.md does not survive its own checks against run $named"; exit 1 ;;
esac

if [ "${DECK_RENDER:-0}" = 1 ]; then
  cp -R talk/diagrams "$TMP/diagrams"   # the deck's images, so marp resolves them
  npx --yes @marp-team/marp-cli@latest --html "$TMP/deck.md" -o "$TMP/deck.html" >/dev/null 2>&1 || {
    echo "FAIL: marp-cli could not render the deck"; exit 1; }
  echo "ok  marp-cli rendered the deck: $(wc -c <"$TMP/deck.html" | tr -d ' ') bytes"
fi

# The PASS line says what was actually observed, and no more. The committed
# deck is graded against the run it names; whether that is the NEWEST run is
# printed, not graded, because the clock does not rebuild the deck.
newest="$(grep '^TRUTH ' talk/truth.log | grep -o 'run=[0-9]*' | tail -1)"; newest="${newest#run=}"
if [ -n "$newest" ] && [ "$newest" != "$named" ]; then
  echo "  note: the newest recorded run is $newest and the committed deck describes run $named; run python3 talk/build_deck.py and commit it to move the deck on (not a failure)"
fi
echo "PASS: a deck builds from this run's captures and survives its checks, every section 4 step check that exists on disk produced a capture, the committed talk/deck.md is the generated file describing recorded run $named, matches a rebuild from that run's committed captures, and survives the figure, status, headline and phrase checks against that run: its seven beats are the section 4 steps in order carrying run $named's own grades, every figure on a beat is a figure in that beat's capture and no figure sits off a beat, its quoted TRUTH line is the line that recorded run $named, and the phrase lint is clean"
