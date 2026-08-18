#!/usr/bin/env bash
# THE FALSIFIABILITY BEAT (build ticket 72; decision ticket 22; spec stories 90, 93).
#
# Rewind under as-consumed, project, score. The beat that earns the right to make any other
# claim: the viewer does not have to trust the machinery — they watch it be checked.
#
# Royal Mail carries this beat and Netflix cannot. Netflix's story is famous, so a twin
# "anticipating" it is indistinguishable from reciting it, and the contamination pillar would
# undermine the very thesis the demo leads with. Royal Mail's parcels-automation shortfall is
# low-notoriety, and its counterfactual sits inside its own audited filings.
#
# THE RESULT IS RED AND THAT IS THE POINT. The one world model this key carries is the market
# consensus at flotation, which put the shortfall at 0.05. It happened. A demo whose thesis is
# "we can prove when we're wrong" cannot be embarrassed by showing that.
#
# Exits non-zero if any step fails. OFFLINE: python3 + PyYAML + git, nothing else.
set -euo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(cd "$HERE/.." && pwd)"
TWIN="$ROOT/bin/twin"

# See twin/demo.sh: the `-t` form of mktemp is BSD-only and aborts on GNU coreutils.
WORK="${1:-$(mktemp -d "${TMPDIR:-/tmp}/twin-beat.XXXXXXXX")}"
OUT="$WORK/artefacts"

ORG=royal-mail
SCENARIO=would-the-twin-have-flagged-it
KEY=royal-mail-concedes-the-automation-shortfall-2019
# After the FY2017-18 results (2018-05-17) and before the profit warning (2018-10-01), so the
# rewind has something to cut: the warning and the answer key itself are both still in the future.
AT=2018-06-01

say()  { printf '\033[1;36m==>\033[0m %s\n' "$*"; }
fail() { echo "FAIL: $*" >&2; exit 1; }

command -v python3 >/dev/null || fail "python3 required"
command -v git >/dev/null || fail "git required"

say "0. the answer keys — the subject, plus the two legs of the contamination discount"
"$TWIN" fixture --name "$ORG" --out "$WORK/royal-mail" || fail "could not build the Royal Mail key"
"$TWIN" fixture --name carillion --out "$WORK/carillion" || fail "could not build the obscure-key leg"
"$TWIN" fixture --name enron --out "$WORK/enron" || fail "could not build the contamination control"
git -C "$WORK/royal-mail" log --format='  %cs  %s' --reverse

say "1. rewind and project — as-consumed, at $AT, through the ordinary backtest composition"
say "   no backtest-specific code path: this is rewind followed by run (guard: backtest_is_a_pure_composition)"
"$TWIN" backtest --repo "$WORK/royal-mail" --org "$ORG" --scenario "$SCENARIO" \
  --regime as-consumed --at "$AT" --out "$OUT/forecast-bundle.json" || fail "backtest failed"

say "2. the discount legs — Enron (the contamination control) against Carillion (low-notoriety)"
for leg in "carillion:carillion-collapse-resolved" "enron:enron-bankruptcy-resolved"; do
  org="${leg%%:*}"; outcome="${leg#*:}"
  "$TWIN" run --repo "$WORK/$org" --org "$org" --scenario "$SCENARIO" --regime as-consumed \
    --out "$OUT/$org-bundle.json" >/dev/null || fail "$org run failed"
  "$TWIN" score --repo "$WORK/$org" --org "$org" --forecast "$OUT/$org-bundle.json" \
    --outcome "$outcome" --out "$OUT/$org-card.json" >/dev/null || fail "$org score failed"
done
echo "  ok   two score cards; the discount below is measured from them, never hardcoded"

say "3. score against the key, with the contamination discount applied — worst forecast first"
"$TWIN" score --repo "$WORK/royal-mail" --org "$ORG" \
  --forecast "$OUT/forecast-bundle.json" --outcome "$KEY" \
  --discount-enron "$OUT/enron-card.json" --discount-obscure "$OUT/carillion-card.json" \
  --out "$OUT/score-card.json" || fail "score failed"

say "3b. nothing was dropped on the way — every forecast is scored or named unscoreable"
python3 - "$OUT/forecast-bundle.json" "$OUT/score-card.json" <<'RED'
import json, sys
bundle = json.load(open(sys.argv[1]))["body"]
card = json.load(open(sys.argv[2]))["body"]
emitted = len(bundle["forecasts"])
reported = len(card["scores"]) + len(card["unscoreable"])
# The one check left here: it is what makes the line printed below true. The threshold on the
# worst score and the raw-beside-adjusted rule are asserted by the harness guard
# `a_scored_forecast_is_never_silently_dropped`, and repeating them here would be a third copy.
# `raise SystemExit` rather than `assert`, because PYTHONOPTIMIZE=1 in the environment strips an
# assert and would leave this block printing its conclusions with nothing behind them.
if emitted != reported:
    raise SystemExit(f"{emitted} forecast(s) emitted, {reported} reported — one went missing")
worst = max(card["scores"], key=lambda s: s["brier"])
print(f"  {emitted} forecast(s) emitted, {reported} reported, none dropped")
print(f"  the headline: {worst['world_model']} said {worst['probability']}, it happened, "
      f"brier {worst['brier']} — worse than a coin flip, and step 3 printed it above the rest")
print(f"  raw {worst['brier']} survives beside adjusted {worst['adjusted_brier']}: the discount is "
      "additive and inspectable, not a correction applied in place")
RED

say "4. the three regimes — the gaps localise the failure to sensing, interpretation or model"
"$TWIN" regimes --repo "$WORK/royal-mail" --org "$ORG" --scenario "$SCENARIO" --at "$AT" \
  --out "$OUT/regime-gap.json" || fail "regimes failed"

say "4b. the score card reproduces from its own pins — except the discount, which honestly refuses"
"$TWIN" verify "$OUT/forecast-bundle.json" --repo "$WORK/royal-mail" \
  || fail "the forecast bundle did not reproduce"
# The refusal is identified by its own message, not by a non-zero exit: `twin verify` also exits
# non-zero on a missing file or a renamed verb, so a typo'd path here would otherwise "pass" and
# the conclusion below would be printed without ever having been tested.
if "$TWIN" verify "$OUT/score-card.json" --repo "$WORK/royal-mail" >/dev/null 2>"$OUT/refusal.txt"; then
  fail "a discounted score card replayed from pins it does not carry"
fi
grep -q -- "--discount-sha256" "$OUT/refusal.txt" \
  || fail "verify refused the discounted card for some other reason: $(cat "$OUT/refusal.txt")"
echo "  ok   a discount is measured from cards named by path, so it is pinned by digest and"
echo "       the card says so rather than replaying a different number"

say "5. the demo's own depth grade — computed from decision ticket 22, never typed"
say "   every artefact above printed the grades of the capabilities that produced it; this is the"
say "   grade of the beat itself, full since build ticket 91 rendered the artefact decision"
say "   ticket 22 asked for (see twin/demo_slice.py, run as beat-sequence.sh's own final step)"
"$TWIN" grade --capability demo-slice || fail "grade failed"

echo
echo "PASS: rewound under as-consumed, projected, scored against a low-contamination key with the"
echo "contamination discount applied. The score is poor, and step 3 printed it before any better one."
echo "The three-regime gap localises what a failure would be: sensing, interpretation, or model."
echo "Every capability the beat touched declares a computed depth grade, and every one is full."
echo
echo "artefacts: $OUT"
