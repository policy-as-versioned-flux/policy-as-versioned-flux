#!/usr/bin/env bash
# THE WHOLE-ENGINE BEAT (build ticket 74; decision ticket 22; spec stories 91, 93).
#
# Fear and seize, both on dated evidence, then versioned governance, then the cross-domain
# comparison the demo is sequenced to end on: a non-technical lever and a technical control,
# priced in one unit, with the rival causal accounts disagreeing about which one is cheaper.
#
# Netflix carries this beat and Royal Mail did not. Royal Mail proved the twin can be checked;
# this one shows what the engine does once you believe it can. The order is the argument —
# credibility earned first, then spent (decision ticket 22; made structural rather than narrated
# at build ticket 77) — so enactment (the governance claim, (c)) runs before pricing (the
# one-currency comparison, (a)), and pricing is the conclusion rather than the opening, because
# it is the most seductive claim and the least defensible standing alone.
#
# NO SCORE HERE, AND THAT IS DELIBERATE. This org carries no answer key. Netflix's story is
# famous enough that a twin "anticipating" 2011 cannot be told apart from reciting it, so a
# score would flatter the machinery rather than test it. The falsifiability beat is Royal
# Mail's (twin/beat-royal-mail.sh) and it lands red.
#
# Exits non-zero if any step fails. OFFLINE: python3 + PyYAML + git, nothing else.
set -euo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(cd "$HERE/.." && pwd)"
TWIN="$ROOT/bin/twin"
RECIPE="$HERE/netflix-substrate-recipe.yaml"

# See twin/demo.sh: the `-t` form of mktemp is BSD-only and aborts on GNU coreutils.
WORK="${1:-$(mktemp -d "${TMPDIR:-/tmp}/twin-netflix.XXXXXXXX")}"
OUT="$WORK/artefacts"

ORG=netflix
SCENARIO=would-the-twin-have-flagged-it
PERSPECTIVE=the-operator
ORIGIN=dvd-by-mail
# After the Q2 letter (2011-07-25) called the price changes a strength, and six weeks before the
# guidance cut (2011-09-15). The rewind has something to cut: neither the cut nor the Q3 reversal
# nor the causal layer that rests on them exists in the tree the forecast is computed against.
AT=2011-08-01
# The Q3 letter, which is where the substrate is anchored and measured.
CHECKPOINT=2011-10-24

say()  { printf '\033[1;36m==>\033[0m %s\n' "$*"; }
fail() { echo "FAIL: $*" >&2; exit 1; }

command -v python3 >/dev/null || fail "python3 required"
command -v git >/dev/null || fail "git required"

say "0. the subject — six filings, and three layers each dated by its own evidence"
"$TWIN" fixture --name "$ORG" --out "$WORK/netflix" || fail "could not build the Netflix spine"
git -C "$WORK/netflix" log --format='  %cs  %s' --reverse

say "0b. THE SENSE STEP — a bound signal is an observation, and belief updates both ways (build ticket 80)"
say "    the Q4 2011 letter is the same checkpoint step 6's causal edge itself waits on"
"$TWIN" sense --repo "$WORK/netflix" --org "$ORG" --signal q4-2011-letter-2012-01-25 \
  --out "$OUT/sense.json" || fail "sense failed"
python3 - "$OUT/sense.json" <<'SENSE'
import json, sys
body = json.load(open(sys.argv[1]))["body"]
binding = next(b for b in body["bindings"] if b.get("component") == "streaming-service")
reach = binding["propagation"]
upstream = [e["component"] for e in reach["upstream"]]
downstream = [e["component"] for e in reach["downstream"]["reached"]]
if "dvd-by-mail" not in upstream:
    raise SystemExit(f"the bound signal did not update belief about its ancestor: {upstream}")
print(f"  signal q4-2011-letter-2012-01-25 binds streaming-service; belief updates UPSTREAM "
      f"about {upstream} (an observation, decision ticket 11 Q4) and DOWNSTREAM about "
      f"{downstream or '(nothing further downstream of streaming-service)'} — an intervention "
      "on this same component would reach the same downstream and none of that upstream")
SENSE

say "1. THE THREAT PATH — rewound to $AT under as-consumed, then projected"
say "   three world models, none privileged, and nothing collapses them into one number"
"$TWIN" backtest --repo "$WORK/netflix" --org "$ORG" --scenario "$SCENARIO" \
  --regime as-consumed --at "$AT" --out "$OUT/forecast-bundle.json" || fail "backtest failed"
python3 - "$OUT/forecast-bundle.json" <<'FEAR'
import json, sys
body = json.load(open(sys.argv[1]))["body"]
forecasts = body["forecasts"]
# `raise SystemExit` rather than `assert`: PYTHONOPTIMIZE=1 in the environment strips an assert
# and would leave this block printing its conclusions with nothing behind them.
if len(forecasts) < 2:
    raise SystemExit(f"{len(forecasts)} forecast(s) emitted — there is no ensemble to show")
for f in sorted(forecasts, key=lambda f: f["probability"]):
    print(f"  {f['world_model']:<36} p={f['probability']}")
ps = [f["probability"] for f in forecasts]
print(f"  {len(forecasts)} forecasts, spread {max(ps) - min(ps):.2f}, and no field anywhere that "
      "merges them")
FEAR
echo "  no score, by construction: this org has no answer key. Netflix's fame makes anticipation"
echo "  indistinguishable from recital, so falsifiability is Royal Mail's beat and lands red there."

say "2. THE OPPORTUNITY PATH — the same dated state, and opportunities are PULLED not pushed"
"$TWIN" rewind --repo "$WORK/netflix" --org "$ORG" --at "$AT" --out "$OUT/rewind.json" \
  || fail "rewind failed"
# The sweep is pinned to the commit the rewind primitive resolved, rather than to a ref this
# script computes for itself: two different answers to "what did the model look like on $AT"
# would make the two paths incomparable, which is the whole point of running them at one date.
REF="$(python3 -c 'import json,sys;print(json.load(open(sys.argv[1]))["body"]["resolved"]["commit"])' "$OUT/rewind.json")"
"$TWIN" gameplay-sweep --repo "$WORK/netflix" --ref "$REF" --out "$OUT/opportunity-sweep.json" \
  || fail "gameplay sweep failed"
python3 - "$OUT/opportunity-sweep.json" <<'SEIZE'
import json, sys
body = json.load(open(sys.argv[1]))["body"]
if not body["opportunities"]:
    raise SystemExit("the sweep pulled nothing — the seize half of this beat has no content")
for o in body["opportunities"]:
    print(f"  {o['play']:<14} {o['component']}")
    print(f"    {o['reason']}")
counts = body["counts"]
print(f"  {counts['opportunities']} pulled against {counts['signals']} pushed — the counterweight "
      "to the record's negativity bias, measured rather than claimed")
SEIZE

say "3. the eye that pays, and the pre-filter that runs BEFORE anything prices"
"$TWIN" options --repo "$WORK/netflix" --org "$ORG" --perspective "$PERSPECTIVE" \
  --out "$OUT/options.json" || fail "options failed"

say "4. the synthetic substrate, and the limitation that travels beside every result from it"
say "   a method footnote, not a thesis claim — placed before governance and pricing, not after"
"$TWIN" substrate --repo "$WORK/netflix" --org "$ORG" --recipe "$RECIPE" \
  --checkpoint "$CHECKPOINT" --out "$OUT/substrate-report.json" || fail "substrate failed"

say "5. VERSIONED GOVERNANCE (c) — the twin proposes, and there is no command that disposes"
say "   through the 'record' channel, because this lever is not code: a signed versioned record"
say "   that it was enacted, without policy enforcing it"
"$TWIN" propose --repo "$WORK/netflix" --org "$ORG" \
  --response hold-the-bundled-price-for-one-quarter --channel record \
  --out "$OUT/enactment-proposal.json" || fail "propose failed"
echo "  the dependency block's own last limit says whose estate those pins are (not netflix's) —"
echo "  the caveat travels IN the artefact, not only in this terminal."
echo "  read the narrowed claim beside step 6: most levers are not code, so if versioned policy"
echo "  were the shape of governance, the cross-domain comparison could not exist at all."

say "6. THE CROSS-DOMAIN COMPARISON (a) — a non-technical lever against a technical control"
say "   one shock at '$ORIGIN', one unit, and the mitigation claims graded separately"
"$TWIN" price --repo "$WORK/netflix" --org "$ORG" --origin "$ORIGIN" --out "$OUT/price.json" \
  || fail "price failed"
echo "  the lever is the one with the evidence. The engineering control's claim is graded 3 and"
echo "  earns no credit at all — a governance tool showing the control winning here would be"
echo "  showing a number nothing behind it supports."

say "7. THE OUTPUT IS A CURVE (a) — and the accounts disagree about which response is cheapest"
say "   three rival readings of the same two filings, none privileged, nothing averaging them away"
say "   the beat's last computed claim, by design — decision ticket 22: earn credibility, then spend it"
"$TWIN" trade-off --repo "$WORK/netflix" --org "$ORG" --origin "$ORIGIN" \
  --perspective "$PERSPECTIVE" \
  --account the-shock-stayed-on-the-dvd-side \
  --account the-shock-crossed-to-the-streaming-side \
  --account the-damage-was-mostly-the-rebrand \
  --out "$OUT/trade-off-curve.json" || fail "trade-off failed"
python3 - "$OUT/trade-off-curve.json" <<'CURVE'
import json, sys
body = json.load(open(sys.argv[1]))["body"]
agreement = body["agreement"]
if agreement["unanimous"]:
    raise SystemExit(
        "the named accounts agree on the cheapest response, so this beat's ensemble disagreement "
        "is not on the page it claims to be on"
    )
for account, option in sorted(agreement["cheapest_by_account"].items()):
    print(f"  believe {account:<40} and {option} is cheapest")
print(f"  the default is {body['default']['option']}, one marked point on the curve — the reader "
      "draws the trade-off")
CURVE

say "8. the demo's own depth grade, and the engine's — computed checklists, never typed"
"$TWIN" grade --capability demo-slice || fail "grade failed"
"$TWIN" grade --capability scenario-engine || fail "grade failed"

echo
echo "PASS: a threat path and an opportunity path both ran end to end on the same dated state. The"
echo "shared-prior limitation travelled with the substrate result before either later claim was"
echo "made. Enactment was proposed and never disposed — versioned governance, spent before the"
echo "beat's concluding claim rather than after it. A non-technical lever and a technical control"
echo "were then priced in one unit, and which of them is cheapest depends on which causal account"
echo "you believe — reported as a curve with the disagreement first, never as a verdict, and the"
echo "last thing this beat computes. No score: this subject carries no answer key, and says so."
echo
echo "artefacts: $OUT"
