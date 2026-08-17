#!/usr/bin/env bash
# THE LIVE, UNRESOLVED, PINNED FORECAST (build ticket 75; decision tickets 06, 22; spec story 92).
#
# The most honest artefact in the demo: a genuine forward forecast where the twin does not know
# the answer either. Emitted through `twin sweep` — the scheduled production line, no scenario
# named at run time — not hand-built for this script. Pinned, signed, and explicitly unscoreable:
# no outcome exists for this proposition, none will be authored by this fixture, and the artefact
# itself says so, with the resolution window and the checking procedure, rather than a placeholder.
#
# Nine real, dated, cited signals carry the spine: the subject's own primary releases where one
# exists, contemporaneous trade-press reporting of the subject's own dated disclosures otherwise —
# graded 2 rather than 1 for exactly that reason. See twin/fixtures.py's own module docstring
# above build_intel_org for the full spine and its citations.
#
# Exits non-zero if any step fails. OFFLINE: python3 + PyYAML + git, nothing else.
set -euo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(cd "$HERE/.." && pwd)"
TWIN="$ROOT/bin/twin"

# See twin/demo.sh: the `-t` form of mktemp is BSD-only and aborts on GNU coreutils.
WORK="${1:-$(mktemp -d "${TMPDIR:-/tmp}/twin-beat.XXXXXXXX")}"
OUT="$WORK/artefacts"
# No mkdir here: `twin ... --out` creates its own parent directory (Artefact.write), the same
# convention beat-royal-mail.sh and beat-netflix.sh rely on.

ORG=intel
SCENARIO=does-the-14a-bet-land-a-named-customer

# AC 1 is "pinned and signed" — demonstrated, not left to whatever the caller's shell happens to
# have exported. `twin verify --attestation` reports HOLDS on an unsigned artefact too (tamper
# evidence, not signing, is what it checks), so step 2 below greps for the agent line by name
# rather than trusting a bare exit code.
export TWIN_SIGNING_KEY="${TWIN_SIGNING_KEY:-intel-beat-demo-key}"

say()  { printf '\033[1;36m==>\033[0m %s\n' "$*"; }
fail() { echo "FAIL: $*" >&2; exit 1; }

command -v python3 >/dev/null || fail "python3 required"
command -v git >/dev/null || fail "git required"

say "0. the live spine — nine real, dated, cited signals, no outcome, ever"
"$TWIN" fixture --name "$ORG" --out "$WORK/intel" || fail "could not build the intel fixture"
git -C "$WORK/intel" log --format='  %cs  %s' --reverse

say "1. the scheduled production line — no --scenario flag exists on this command"
"$TWIN" sweep --repo "$WORK/intel" --out "$OUT/sweep.json" || fail "sweep failed"

say "2. pinned and signed: the sweep artefact's attestation"
"$TWIN" verify "$OUT/sweep.json" --attestation | tee "$OUT/attestation.txt" || fail "attestation check failed"
grep -q "^  agent        [0-9a-f]" "$OUT/attestation.txt" \
  || fail "the sweep artefact carries no agent signature — AC 1 asks for signed, not merely pinned"
grep -q "^HOLDS" "$OUT/attestation.txt" || fail "the attestation does not hold"

say "3. the same forecast, reproduced independently through the ordinary run verb"
"$TWIN" run --repo "$WORK/intel" --org "$ORG" --scenario "$SCENARIO" --regime as-consumed \
  --out "$OUT/forecast-bundle.json" >/dev/null || fail "run failed"
"$TWIN" verify "$OUT/forecast-bundle.json" --repo "$WORK/intel" \
  || fail "the forecast bundle did not reproduce from its own pins"

say "3b. the sweep and the standalone run agree byte-for-byte — nothing here was hand-made"
python3 - "$OUT/sweep.json" "$OUT/forecast-bundle.json" <<'CHECK'
import hashlib, json, sys
sweep = json.load(open(sys.argv[1]))["body"]
standalone_bytes = open(sys.argv[2], "rb").read()
standalone_sha256 = hashlib.sha256(standalone_bytes).hexdigest()
executions = sweep["executions"]
if len(executions) != 1 or sweep["failures"]:
    raise SystemExit(f"expected one clean execution, got {len(executions)}, {len(sweep['failures'])} failure(s)")
embedded = executions[0]["forecast_bundle"]["sha256"]
if embedded != standalone_sha256:
    raise SystemExit(f"sweep embedded {embedded}, standalone run digests to {standalone_sha256} — disagree")
forecasts = executions[0]["body"]["forecasts"]
probs = sorted({f["probability"] for f in forecasts})
if len(probs) < 2:
    raise SystemExit(f"expected plural, distinct forecasts, got {probs}")
print(f"  ok   {len(forecasts)} forecast(s), {len(probs)} distinct probabilities: {probs}")
print(f"  ok   sweep-embedded digest == standalone `twin run` digest ({embedded[:16]}...)")
CHECK

say "4. explicitly unscoreable — published in the artefact's own body, not a placeholder"
python3 - "$OUT/forecast-bundle.json" <<'HONEST'
import json, sys
question = json.load(open(sys.argv[1]))["body"]["scenario"]["question"].lower()
needed = ("unscoreable", "second half of 2026", "first half of 2027", "twin score")
missing = [n for n in needed if n not in question]
if missing:
    raise SystemExit(f"the emitted question is missing: {missing}")
print("  ok   the emitted forecast names its own unscoreability, resolution window and checking procedure")
HONEST

say "5. the refusal is real, checked live, not narrated"
if "$TWIN" score --repo "$WORK/intel" --org "$ORG" --forecast "$OUT/forecast-bundle.json" \
     --outcome any-outcome-at-all --out "$OUT/score-card.json" 2>"$OUT/refusal.txt"; then
  fail "twin score succeeded against an overlay that carries no outcome"
fi
grep -q "no outcome 'any-outcome-at-all' in overlay 'intel' (have: none)" "$OUT/refusal.txt" \
  || fail "score refused for an unexpected reason: $(cat "$OUT/refusal.txt")"
[ -e "$OUT/score-card.json" ] && fail "a score card was written despite the refusal"
echo "  ok   $(cat "$OUT/refusal.txt")"

say "6. the demo's own depth grade — computed, never typed"
"$TWIN" grade --capability scenario-engine || fail "grade failed"

echo
echo "PASS: swept through the scheduled production line, pinned and agent-signed, reproduced"
echo "byte-for-byte through an independent run of the same scenario. The forecast names its own"
echo "unscoreability, its resolution window and its checking procedure in the artefact itself, and"
echo "\`twin score\` genuinely refuses it today — for a different, stated reason than Royal Mail's"
echo "or Netflix's own refusals: this story has not happened yet."
echo
echo "artefacts: $OUT"
