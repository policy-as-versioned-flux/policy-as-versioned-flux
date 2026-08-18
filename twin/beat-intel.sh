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
# The opportunity half of decision ticket 13 AC 7 (build ticket 88) — the same real EUV edge
# step 0c exercises below, wrapped the upside way, replacing the toy `euv-slip-2026` fixture.
OPPORTUNITY_SCENARIO=euv-readiness-wins-the-14a-opportunity

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

say "0b. THE SENSE STEP — a bound signal is an observation, and belief updates both ways (build ticket 80)"
"$TWIN" sense --repo "$WORK/intel" --org "$ORG" --signal tan-14a-customer-guidance-2026-01-23 \
  --out "$OUT/sense.json" || fail "sense failed"
python3 - "$OUT/sense.json" <<'SENSE'
import json, sys
body = json.load(open(sys.argv[1]))["body"]
binding = next(b for b in body["bindings"] if b.get("component") == "leading-edge-foundry-node")
reach = binding["propagation"]
if reach["upstream_traversal"]["walked"] is not True:
    raise SystemExit(f"the upstream walk did not run: {reach['upstream_traversal']}")
upstream = [e["component"] for e in reach["upstream"]]
downstream = [e["component"] for e in reach["downstream"]["reached"]]
# The real causal edge build ticket 81 added (decision ticket 08 AC 5) makes this non-trivial:
# euv-lithography is now a genuine causal ancestor of the bound component, so the observation
# updates belief about it too, with no magnitude — the same diagnostic-direction discipline
# `twin/primitives.py` states for every observation.
if "euv-lithography" not in upstream:
    raise SystemExit(f"expected euv-lithography upstream of the bound component, got {upstream}")
print(f"  signal tan-14a-customer-guidance-2026-01-23 binds leading-edge-foundry-node; the "
      f"observation walk ran both ways and found UPSTREAM {upstream} (the EUV causal edge, "
      f"build ticket 81), DOWNSTREAM "
      f"{downstream or '(none — nothing causal leaves this component yet)'}")
SENSE

say "0c. THE REAL CAUSAL CLAIM — EUV delay -> process-node slip (build ticket 81, decision ticket 08 AC 5)"
"$TWIN" propagate --repo "$WORK/intel" --org "$ORG" --origin euv-lithography \
  --out "$OUT/propagate.json" || fail "propagate failed"
python3 - "$OUT/propagate.json" <<'CAUSAL'
import json, sys
body = json.load(open(sys.argv[1]))["body"]
reached = next((r for r in body["reached"] if r["component"] == "leading-edge-foundry-node"), None)
if reached is None:
    raise SystemExit("euv-lithography's own causal edge did not compose to leading-edge-foundry-node")
primary = next(p for p in reached["paths"] if p["primary"])
if primary["directional_only"]:
    raise SystemExit(f"expected a priceable elasticity, got directional-only: {primary}")
composed = primary["composed"]
print(f"  euv-lithography -> leading-edge-foundry-node: grade {primary['worst_evidence_grade']}, "
      f"{primary['sign']}, composed {composed['min']:.3f}/{composed['mode']:.3f}/{composed['max']:.3f} "
      "— a real, cited, priceable elasticity, the Netflix co-flagship's own Qwikster->churn edge "
      "matched rather than left as this org's one remaining gap")
CAUSAL

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

say "3a. the opportunity half of decision ticket 13 AC 7 — the same real EUV edge, read upside"
"$TWIN" run --repo "$WORK/intel" --org "$ORG" --scenario "$OPPORTUNITY_SCENARIO" --regime as-consumed \
  --out "$OUT/opportunity-bundle.json" >/dev/null || fail "opportunity run failed"
"$TWIN" verify "$OUT/opportunity-bundle.json" --repo "$WORK/intel" \
  || fail "the opportunity bundle did not reproduce from its own pins"

say "3b. the sweep and both standalone runs agree byte-for-byte — nothing here was hand-made"
python3 - "$OUT/sweep.json" "$OUT/forecast-bundle.json" "$OUT/opportunity-bundle.json" <<'CHECK'
import hashlib, json, sys
sweep = json.load(open(sys.argv[1]))["body"]
executions = sweep["executions"]
if len(executions) != 2 or sweep["failures"]:
    raise SystemExit(f"expected two clean executions (fear + opportunity), got {len(executions)}, "
                      f"{len(sweep['failures'])} failure(s)")
by_scenario = {e["scenario"]: e for e in executions}
for scenario, path in (("does-the-14a-bet-land-a-named-customer", sys.argv[2]),
                        ("euv-readiness-wins-the-14a-opportunity", sys.argv[3])):
    standalone_sha256 = hashlib.sha256(open(path, "rb").read()).hexdigest()
    embedded = by_scenario[scenario]["forecast_bundle"]["sha256"]
    if embedded != standalone_sha256:
        raise SystemExit(f"{scenario}: sweep embedded {embedded}, standalone digests to "
                          f"{standalone_sha256} — disagree")
    forecasts = by_scenario[scenario]["body"]["forecasts"]
    probs = sorted({f["probability"] for f in forecasts})
    if len(probs) < 2:
        raise SystemExit(f"{scenario}: expected plural, distinct forecasts, got {probs}")
    print(f"  ok   {scenario}: {len(forecasts)} forecast(s), {len(probs)} distinct: {probs}")
print("  ok   sweep-embedded digests == standalone `twin run` digests, both scenarios")
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
