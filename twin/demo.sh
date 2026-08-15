#!/usr/bin/env bash
# THE WALKING SKELETON. One dated signal binds to a component; one scenario execution emits
# forecasts — plural; one recorded outcome scores them. Sense -> run -> score, from a clean
# checkout, with the loop closed before anything is deepened (build ticket 07).
#
# Every capability here is `partial`, meaning at least one acceptance criterion of its owning
# decision ticket and rarely more: each artefact carries the computed depth grade of every
# capability that produced it, and prints exactly which criteria are still unchecked.
#
# Exits non-zero if any step fails. OFFLINE: python3 + PyYAML + git, nothing else.
set -euo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(cd "$HERE/.." && pwd)"
TWIN="$ROOT/bin/twin"

# An explicit `XXXXXXXX` template rather than `mktemp -d -t twin-demo`: BSD mktemp appends the
# random suffix for you, GNU coreutils refuses with "too few X's in template" — so the -t form
# aborts this script on its first line on Linux, which is where CI runs it.
WORK="${1:-$(mktemp -d "${TMPDIR:-/tmp}/twin-demo.XXXXXXXX")}"
MODEL="$WORK/model"
OUT="$WORK/artefacts"

say()  { printf '\033[1;36m==>\033[0m %s\n' "$*"; }
fail() { echo "FAIL: $*" >&2; exit 1; }

command -v python3 >/dev/null || fail "python3 required"
command -v git >/dev/null || fail "git required"

say "0. a clean checkout — the deterministic fixture model repository"
"$TWIN" fixture --out "$MODEL" || fail "could not build the fixture model repository"
git -C "$MODEL" log --oneline

say "1. sense — a dated signal binds to a component through a committed grade-5 claim"
"$TWIN" sense --repo "$MODEL" --org netflix \
  --signal price-separation-announced \
  --out "$OUT/bound-signal.json" || fail "sense failed"

say "2. run — one scenario, three rival world models, three forecasts. Nothing collapses them."
say "   the regime is required and has no default; only as-consumed scores."
"$TWIN" run --repo "$MODEL" --org netflix \
  --scenario dvd-decline-2011 --regime as-consumed \
  --out "$OUT/forecast-bundle.json" || fail "run failed"

say "2b. the same scenario under all three regimes — the two gaps, computed not inferred"
"$TWIN" regimes --repo "$MODEL" --org netflix \
  --scenario dvd-decline-2011 \
  --out "$OUT/regime-gap.json" || fail "regimes failed"

say "2c. an execution with no declared regime is refused, not defaulted"
if "$TWIN" run --repo "$MODEL" --org netflix --scenario dvd-decline-2011 \
     --out "$OUT/should-not-exist.json" >/dev/null 2>&1; then
  fail "an execution ran with no regime"
fi
echo "  ok   refused"

say "3. score — a recorded outcome scores the forecasts, naming them by pin and never by path"
"$TWIN" score --repo "$MODEL" --org netflix \
  --forecast "$OUT/forecast-bundle.json" \
  --outcome dvd-decline-2011-resolved \
  --out "$OUT/score-card.json" || fail "score failed"

say "4. the spread is the point — the scores themselves printed by step 3, worst first"
python3 - "$OUT/score-card.json" <<'PY'
import json, sys
card = json.load(open(sys.argv[1]))["body"]
print(f"  scoring the bundle sha256:{card['subject']['sha256'][:16]}... by pin, not by path")
PY

say "5. the graph — components, people, typed edges, and nothing behavioural anywhere in it"
"$TWIN" graph --repo "$MODEL" --org netflix --out "$OUT/graph.json" >/dev/null || fail "graph failed"
python3 - "$OUT/graph.json" <<'PY'
import json, sys
g = json.load(open(sys.argv[1]))["body"]
print(f"  {len(g['components'])} components, {len(g['people'])} people, {len(g['edges'])} typed edges")
for component, holders in sorted(g["bus_factor"].items()):
    print(f"    bus factor  {component:<22} {', '.join(holders)}")
PY

say "6. the map — rendered from that same graph, with no separate authoring step"
"$TWIN" map --repo "$MODEL" --org netflix || fail "map failed"

say "7. the blast radius — one traversal, two outputs, and the boundary between them visible"
"$TWIN" blast --repo "$MODEL" --org netflix --origin content-delivery-network \
  --out "$OUT/blast-radius.json" >/dev/null || fail "blast failed"
python3 - "$OUT/blast-radius.json" <<'BLAST'
import json, sys
b = json.load(open(sys.argv[1]))["body"]
print(f"  gate: {b['gating']['rule']}")
for e in b["admitted_to_pricing"]:
    print(f"    price     {e['component']:<24} depth {e['depth']}, weakest grade {e['worst_evidence_grade']}")
for e in b["unpriced"]:
    grade = e["worst_evidence_grade"]
    print(f"    unpriced  {e['component']:<24} {e['reason']}"
          + (f" (grade {grade})" if grade is not None else ""))
raw = json.dumps(b)
assert not any(k in raw for k in ('"price":', '"cost":', '"severity":')), "a price leaked in"
print("  the unpriced half is a distinct artefact type, not a price with a null field")
BLAST

say "8. propagation — composed, attenuated and sampled, all three, so attenuation is falsifiable"
"$TWIN" propagate --repo "$MODEL" --org netflix --origin content-delivery-network \
  --out "$OUT/propagation.json" >/dev/null || fail "propagate failed"
python3 - "$OUT/propagation.json" <<'PROP'
import json, sys
b = json.load(open(sys.argv[1]))["body"]
print(f"  {b['attenuation']['rule']}")
for reached in b["reached"]:
    for path in reached["paths"]:
        if path["directional_only"]:
            print(f"    {reached['component']:<24} depth {path['depth']}  direction only, no magnitude")
            continue
        c, a = path["composed"], path["attenuated"]
        print(f"    {reached['component']:<24} depth {path['depth']}  "
              f"composed {c['min']:.3f}/{c['mode']:.3f}/{c['max']:.3f}  x{path['attenuation']}  "
              f"-> {a['min']:.3f}/{a['mode']:.3f}/{a['max']:.3f}  sampled p50 {path['sampled']['p50']:.3f}")
assert b["traversal"]["paths_are_not_aggregated"], "the non-aggregation statement went missing"
for reached in b["reached"]:
    joint = reached.get("joint")
    if joint is None or joint["exact"] is None:
        continue
    assert joint["exact"] <= joint["if_independent"], "the dependence correction went the wrong way"
    shared = ", ".join(joint["shared_edges"]) or "nothing"
    print(f"    joint {reached['component']:<24} {joint['exact']:.4f} against "
          f"{joint['if_independent']:.4f} if independent; shares {shared}")
print("  structural edges do not propagate, and paths are combined by noisy-OR rather than summed")
print("  a shared edge is drawn once per trial, so a common cause is not counted twice — every")
print("  component here is reached by one path, so there is nothing to combine and the two figures")
print("  agree trivially. The diamond that exercises the discount is in the pocket org, step 13")
PROP

say "8b. doing versus learning — an intervention does not rewrite its own causes"
"$TWIN" intervene --repo "$MODEL" --org netflix --component streaming-experience \
  --out "$OUT/intervention.json" >/dev/null || fail "intervene failed"
"$TWIN" observe --repo "$MODEL" --org netflix --component streaming-experience \
  --out "$OUT/observation.json" >/dev/null || fail "observe failed"
python3 - "$OUT/intervention.json" "$OUT/observation.json" <<'DO'
import json, sys
doing = json.load(open(sys.argv[1]))["body"]
learning = json.load(open(sys.argv[2]))["body"]
assert doing["upstream"] == [], "an intervention updated a belief about its own causes"
assert learning["upstream"], "an observation updated nothing upstream"
assert doing["downstream"] == learning["downstream"], "the downstream halves diverged"
print(f"  do({doing['component']}): severs {', '.join(e['edge'] for e in doing['severed'])},"
      f" updates nothing upstream")
print(f"  observe({learning['component']}): severs nothing, updates belief about "
      f"{', '.join(e['component'] for e in learning['upstream'])} — and carries no magnitude there")
print("  the downstream halves are byte-identical: the difference lives above the composition")
DO

say "8c. rewind — the refusals. Every fixture commit shares one date, so a later instant"
say "    resolves to HEAD; the dated-change case is tests/test_primitives.py"
"$TWIN" rewind --repo "$MODEL" --org netflix --at 2026-06-01T00:00:00+00:00 \
  --out "$OUT/rewound-model.json" >/dev/null || fail "rewind failed"
if "$TWIN" rewind --repo "$MODEL" --org netflix --at 1999-01-01 \
     --out "$OUT/should-not-exist.json" >/dev/null 2>&1; then
  fail "a rewind to before the model existed returned an empty state"
fi
echo "  ok   a rewind to before the model existed is refused, not answered with an empty model"

say "9. the pre-filter — a constraint is not a very large price, because a price can be outbid"
"$TWIN" options --repo "$MODEL" --org netflix --perspective the-operator \
  --out "$OUT/priced-option-set.json" || fail "options failed"
python3 - "$OUT/priced-option-set.json" <<'OPT'
import json, sys
b = json.load(open(sys.argv[1]))["body"]
removed = {r["option"] for r in b["prefilter"]["removed"]}
priced = {e["option"] for e in b["priced"]}
assert not removed & priced, "an excluded option was priced"
for record in b["prefilter"]["removed"]:
    numbers = [v for v in record.values() if isinstance(v, (int, float)) and not isinstance(v, bool)]
    assert not numbers, f"a figure survived on {record['option']}: {numbers}"
print(f"  {len(removed)} removed before pricing, carrying no figure; {len(priced)} priced")
print("  the removed options cost almost nothing — the pre-filter never reads a cost")
OPT

say "10. the same scenario under two perspectives — the £ belongs to whoever pays to run the twin"
"$TWIN" exposure --repo "$MODEL" --org netflix --scenario dvd-decline-2011 \
  --out "$OUT/scenario-exposure.json" || fail "exposure failed"

say "10b. the price — the causal layer multiplied by the currency, under every declared eye"
say "     an HR lever and a technical control in one unit; an unevidenced claim earns nothing"
"$TWIN" price --repo "$MODEL" --org netflix --origin content-delivery-network \
  --out "$OUT/priced-impact.json" || fail "price failed"

say "11. the constraint set, published upfront — paperclip risk disclosed rather than discovered"
"$TWIN" constraints --out "$OUT/constraint-set.json" || fail "constraints failed"

say "12. the attestation sidecar, read back — a write-only attestation is not tamper-evidence"
"$TWIN" verify "$OUT/score-card.json" --attestation || fail "the sidecar did not hold"
python3 - "$OUT/score-card.json.att.json" <<'PY'
import json, sys
doc = json.load(open(sys.argv[1]))
doc["human_involvement"] = {"present": True, "signatures": [{"role": "model-steward"}]}
json.dump(doc, open(sys.argv[1] + ".tampered", "w"))
PY
mv "$OUT/score-card.json.att.json" "$OUT/score-card.json.att.json.clean"
mv "$OUT/score-card.json.att.json.tampered" "$OUT/score-card.json.att.json"
if "$TWIN" verify "$OUT/score-card.json" --attestation >/dev/null 2>&1; then
  fail "a derived artefact claiming human involvement was not detected"
fi
echo "  ok   a planted human signature on a derived artefact is a detectable anomaly"
mv "$OUT/score-card.json.att.json.clean" "$OUT/score-card.json.att.json"

say "13. the pocket org — five components, eight edges, checked against a hand-computed worksheet"
"$TWIN" fixture --name pocket --out "$WORK/pocket" >/dev/null || fail "pocket fixture failed"
"$TWIN" worksheet --repo "$WORK/pocket" || fail "the pocket org no longer matches its worksheet"

say "14. reproduce the score card from its pins alone — including the bundle it scored"
"$TWIN" verify "$OUT/score-card.json" --repo "$MODEL" || fail "the score card did not reproduce"

say "15. every object validates against its closed schema, and Article 9 data cannot be written"
"$TWIN" validate --repo "$MODEL" || fail "validation failed"

say "16. the derived index is derived — drop it, rebuild it from git alone"
"$TWIN" index --repo "$MODEL" --out "$WORK/index" || fail "index build failed"
rm -rf "$WORK/index"
"$TWIN" index --repo "$MODEL" --out "$WORK/index" || fail "index rebuild failed"

say "17. determinism — the same command against the same ref, byte for byte"
"$TWIN" run --repo "$MODEL" --org netflix --scenario dvd-decline-2011 --regime as-consumed \
  --out "$OUT/forecast-bundle-again.json" >/dev/null || fail "second run failed"
cmp -s "$OUT/forecast-bundle.json" "$OUT/forecast-bundle-again.json" \
  || fail "the same pins produced different bytes"
echo "  ok   identical bytes"

say "18. a dirty tree is refused — the pin has to describe what you are reading"
echo "# scribble" >> "$MODEL/world/meta.yaml"
if "$TWIN" run --repo "$MODEL" --org netflix --scenario dvd-decline-2011 --regime as-consumed \
     --out "$OUT/should-not-exist.json" >/dev/null 2>&1; then
  fail "a dirty model repository ran anyway"
fi
git -C "$MODEL" checkout -- world/meta.yaml
echo "  ok   refused"

say "19. sweep — every scenario in every org, unconditionally, with no --scenario flag to set"
"$TWIN" sweep --repo "$MODEL" --out "$OUT/sweep.json" || fail "sweep failed"
python3 - "$OUT/sweep.json" <<'SWEEP'
import json, sys
b = json.load(open(sys.argv[1]))["body"]
c = b["counts"]
assert c["executed"] > 0, "the sweep executed nothing"
assert not b["failures"], f"the sweep failed on a fixture scenario: {b['failures']}"
print(f"  {c['executed']} scenario(s) across {c['repos']} repo(s), {c['forecasts']} forecast(s), no --scenario flag")
SWEEP

say "20. the reliability diagram — a population of score cards, pooled, with empty bins shown"
say "    two --score-card flags here, not one: pooling is proved at the seam a caller uses"
"$TWIN" score --repo "$MODEL" --org netflix \
  --forecast "$OUT/forecast-bundle.json" \
  --outcome dvd-decline-2011-resolved \
  --out "$OUT/score-card-2.json" >/dev/null || fail "second score failed"
"$TWIN" reliability --score-card "$OUT/score-card.json" --score-card "$OUT/score-card-2.json" \
  --out "$OUT/reliability-diagram.json" || fail "reliability failed"
python3 - "$OUT/reliability-diagram.json" <<'REL'
import json, sys
b = json.load(open(sys.argv[1]))["body"]
assert len(b["bins"]) == b["bin_count"], "a bin went missing"
assert b["total_scored"] == 6, "two identically-scored cards should pool to double the count"
print(f"  {b['bin_count']} bins over {b['total_scored']} scored forecast(s) from 2 named cards; an empty bin carries a zero count, never a gap")
for entry in b["bins"]:
    lo, hi = entry["range"]
    print(f"    [{lo:.1f}, {hi:.1f})  n={entry['count']}")
REL

say "21. the loss-exceedance curve — VaR beside TVaR, never VaR alone, and the shape boundary refused"
"$TWIN" severity --mu 10.0 --sigma 1.5 --threshold 100000 --xi 0.3 --beta 80000 \
  --alpha 0.9 --alpha 0.95 --alpha 0.99 \
  --out "$OUT/loss-exceedance-curve.json" || fail "severity failed"
python3 - "$OUT/loss-exceedance-curve.json" <<'SEV'
import json, sys
b = json.load(open(sys.argv[1]))["body"]
curve = b["curve"]
assert len(curve) == 3, "one row per named confidence level"
assert all(row["tvar"] >= row["var"] for row in curve), "TVaR must never be smaller than VaR"
print(f"  {len(curve)} confidence level(s), a declared threshold, no severity slot on any component")
for row in curve:
    print(f"    alpha={row['alpha']}  var={row['var']:.2f}  tvar={row['tvar']:.2f}")
SEV

echo
echo "PASS: sense -> run -> score closes the loop from a clean checkout. Forecasts are a list,"
echo "scored by pin; the store is rebuildable from git; identical pins give identical bytes; a"
echo "dirty tree is refused. sweep runs the standing scenario set unconditionally and reliability"
echo "bins the record it produces. severity is the FAIR engine's tail model, standalone, and"
echo "reports TVaR beside VaR rather than VaR alone. Every artefact declares which acceptance"
echo "criteria are still unchecked, so the skeleton cannot quietly become the definition of done."
echo
echo "artefacts: $OUT"
