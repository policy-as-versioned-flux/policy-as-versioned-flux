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
#   - an ASIDE (ticket 48) -- a capture-reading slide that is not one of the
#     seven steps -- carries a status that is not the run's grade for its
#     script, a figure its capture does not carry, or a claim at all when the
#     run wrote no capture for it;
#   - the phrase lint hits a phrase CONTEXT.md's `## Words a slide may not use`
#     table refuses. The list is READ FROM THAT TABLE and is not typed into any
#     script: from ticket 47 until ticket 48 four phrases were hard-coded in
#     talk/build_deck.py, derived from nothing and answerable to no decision,
#     which is the defect class every review of this estate finds. Matching is
#     done with markdown emphasis stripped, because the phrase this lint exists
#     for last shipped as `Deny is the *bottom* rung`. Every OTHER use of the
#     word gate is printed as a human review item and is not a failure: the
#     truth surface keeps the name (ticket 03) and ADR-0011 keeps release gate;
#   - the committed talk/deck.md is not the generated file, names no recorded
#     run, or does not carry the same beat and aside MARKERS as a rebuild from
#     the run it names -- every check above is run over the committed file as
#     well. Markers, not bytes: that is weaker than "is what the rebuild
#     produces" and the gap is a named ceiling below;
#   - a section 4 step check exists on disk but this run wrote no capture for it;
#   - a quoted TRUTH line is not the line that recorded the run the deck names.
#
# Named ceilings, so nobody mistakes what this observes:
#   - headers, dates, tags, step numbers, ticket and ADR references, the deck's
#     own run/hub stamp and the "$ bash <script>" command line are OUTSIDE the
#     figure check;
#   - the grade comes from talk/captures/_grades.tsv, the per-script table the
#     run itself wrote from the EXIT CODES it saw (ticket 59), and from the
#     capture's last line NEVER -- see the paragraph below on a run that
#     recorded no grade, which replaced that fallback (ticket 48 review F1).
#     The two are compared whenever the last line carries a verdict of its own,
#     and disagreement is a failure. The last line alone was the rule until
#     ticket 48 and it is a proxy: 30 of run 184's 119 captures end on a line
#     carrying no verdict, 16 of them in the continuation of a multi-line one,
#     and run 186 is 30 of 120 with the same 16. One is the Monte Carlo capture
#     this deck now reads, which reads back FAIL off a script that exited 0.
#     On both runs, 32 scripts are graded differently by the table and by the
#     last line.
#     A run that recorded NO grade for a script -- no table at all, or a table
#     with no row for it -- is a COULD NOT LOOK named on the slide, never a
#     grade read off the last line (ticket 48 review F1). Both halves matter,
#     and the second is the durable one: six of run 186's own 120 captures
#     have no row in that run's table, so a run that HAS a table still reaches
#     this. As of run 207 (2026-09-09), 46 of the 57 runs talk/truth.log
#     records carry no table at all, and every scheduled run since 181 has
#     carried one -- so that count is moving and is dated here rather than
#     stated as a standing fact. Nothing reads it.
#     WHAT THE FIGURE RULE BINDS, and what it does not. A figure passes when
#     the same run of digits appears anywhere in the slide's own capture. That
#     is provenance -- this run printed this token -- and it is not meaning. A
#     digit run inside a hash or a count of something else licenses the figure,
#     so a green here is not a semantic guarantee (ticket 48 review F7).
#     Step 7's table is read as a third, independently produced opinion;
#   - an aside whose capture the named run did not write is a COULD NOT LOOK
#     (exit 3) and never a pass. It is not red: an extra read the run did not
#     produce is not a fault in the deck and not a fault in the estate. The
#     seven steps keep the stricter rule -- a step check on disk with no
#     capture is a missing observation and red -- because those seven are what
#     the estate promises and an aside is not;
#   - WHAT THE COMMITTED-DECK COMPARISON BINDS (ticket 48 review F8). The
#     committed deck is compared with a rebuild by MARKERS -- the `beat step=N
#     status=X` and `aside name=Y status=Z` comments -- and not byte for byte,
#     because the two `built HH:MMZ` stamps differ on every rebuild. So a
#     sentence hand-edited into the committed deck survives if it carries no
#     figure and no refused phrase. Measured: `Driftwood's cage was approved by
#     the regulator and signed off by the board.` inserted into a slide passes
#     this check at exit 0. What IS bound is every status, every figure against
#     its own capture, the quoted TRUTH line and the refused vocabulary. A
#     green here does not mean nobody wrote a sentence into the deck by hand;
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

python3 talk/build_deck.py --check "$TMP/deck.md" >"$TMP/rebuild" 2>&1; rc=$?
sed 's/^/  /' "$TMP/rebuild"
case "$rc" in
  0) ;;
  3) # Two different could-not-looks, and the sentence must not say the wrong one. A capture the
     # run never wrote is one thing; a capture it wrote and never graded is another (ticket 48
     # review F1), and calling the second "wrote no capture for" would be a false sentence in the
     # place this check exists to keep true.
     why="$(grep -m1 'could not look  ' "$TMP/rebuild" | sed 's/^ *could not look  //')"
     case "$why" in
       *"recorded no grade for"*) what="recorded no grade for" ;;
       *)                         what="wrote no capture for" ;;
     esac
     echo "SKIP: a deck of this run's captures names a read this run $what, so it could not be graded whole: $why"
     exit 3 ;;
  *) echo "FAIL: the built deck does not survive its own checks"; exit 1 ;;
esac

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
markers() { grep -oE 'beat step=[0-9]+ status=[A-Z]+|aside name=[a-z0-9-]+ status=[A-Z]+' "$1"; }
if ! diff <(markers talk/deck.md) <(markers "$TMP/named.md") >"$TMP/d" 2>&1; then
  echo "  the committed deck's beats differ from a rebuild of run $named:"; sed 's/^/    /' "$TMP/d"
  echo "FAIL: talk/deck.md has been hand edited; run python3 talk/build_deck.py"; exit 1
fi
echo "ok  the committed talk/deck.md is the generated file, with the same beats as a rebuild of run $named"

# The one that mattered: every check above ran against the REBUILD. Nothing ran
# against the file a reader actually opens, so a hand-edited figure, a forged
# TRUTH headline and a rewritten could-not-look reason all passed (review
# 2026-08-29). So the deck's own checks are run over the committed file as
# well, against the captures of the run it names.
python3 talk/build_deck.py --check talk/deck.md >"$TMP/committed" 2>&1; rc=$?
sed 's/^/  /' "$TMP/committed"
case "$rc" in
  0) echo "ok  the committed talk/deck.md survives the figure, status, headline and phrase checks against run $named" ;;
  3) if grep -q '^  could not look  ' "$TMP/committed"; then
       why="$(grep -m1 '^  could not look  ' "$TMP/committed" | sed 's/^ *could not look  //')"
       case "$why" in
         *"recorded no grade for"*) what="run $named recorded no grade for" ;;
         *)                         what="whose capture run $named never wrote" ;;
       esac
       echo "SKIP: the committed talk/deck.md names a read $what, so it could not be graded whole: $why"
       exit 3
     fi
     echo "SKIP: run $named's recording commit became unreachable between two reads; run this check again"
     exit 3 ;;
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
echo "PASS: a deck builds from this run's captures and survives its checks, every section 4 step check that exists on disk produced a capture, the committed talk/deck.md is the generated file describing recorded run $named, carries the same beat and aside markers as a rebuild from that run's committed captures, and survives the figure, status, headline and phrase checks against that run: its seven beats are the section 4 steps in order carrying run $named's own grades as run $named's own _grades.tsv recorded them, its asides each carry that run's grade for the script each names and were all read from a capture that run wrote, every figure on a beat or an aside is a figure in that slide's capture and no figure sits on a slide with no capture behind it, its quoted TRUTH line is the line that recorded run $named, and no phrase CONTEXT.md's refused-vocabulary table names appears anywhere in it"
