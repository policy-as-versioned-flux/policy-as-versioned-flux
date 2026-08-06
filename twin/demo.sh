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

WORK="${1:-$(mktemp -d -t twin-demo)}"
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
"$TWIN" run --repo "$MODEL" --org netflix \
  --scenario dvd-decline-2011 \
  --out "$OUT/forecast-bundle.json" || fail "run failed"

say "3. score — a recorded outcome scores the forecasts, naming them by pin and never by path"
"$TWIN" score --repo "$MODEL" --org netflix \
  --forecast "$OUT/forecast-bundle.json" \
  --outcome dvd-decline-2011-resolved \
  --out "$OUT/score-card.json" || fail "score failed"

say "4. the spread is the point — what each world model believed, and what it cost"
python3 - "$OUT/score-card.json" <<'PY'
import json, sys
card = json.load(open(sys.argv[1]))["body"]
key = card["answer_key"]
print(f"  answer key {key['id']}: observed={key['observed']}, resolved {key['resolved_on']},"
      f" contamination {key['contamination']}")
print(f"  scoring the bundle sha256:{card['subject']['sha256'][:16]}... by pin, not by path")
print(f"  rules {', '.join(card['rules'])} ({card['orientation']})")
for s in sorted(card["scores"], key=lambda s: s["brier"]):
    print(f"    {s['world_model']:<28} p={s['probability']:<6} brier={s['brier']:<8.4f}"
          f" log-loss={s['log_loss']:<8.4f} [{s['regime']}]")
for u in card["unscoreable"]:
    print(f"    unscoreable: {u['world_model']} — {u['reason']}")
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

say "7. the attestation sidecar, read back — a write-only attestation is not tamper-evidence"
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

say "8. the pocket org — five components, six edges, checked against a hand-computed worksheet"
"$TWIN" fixture --pocket-org --out "$WORK/pocket" >/dev/null || fail "pocket fixture failed"
"$TWIN" worksheet --repo "$WORK/pocket" || fail "the pocket org no longer matches its worksheet"

say "9. reproduce the score card from its pins alone — including the bundle it scored"
"$TWIN" verify "$OUT/score-card.json" --repo "$MODEL" || fail "the score card did not reproduce"

say "10. every object validates against its closed schema, and Article 9 data cannot be written"
"$TWIN" validate --repo "$MODEL" || fail "validation failed"

say "11. the derived index is derived — drop it, rebuild it from git alone"
"$TWIN" index --repo "$MODEL" --out "$WORK/index" || fail "index build failed"
rm -rf "$WORK/index"
"$TWIN" index --repo "$MODEL" --out "$WORK/index" || fail "index rebuild failed"

say "12. determinism — the same command against the same ref, byte for byte"
"$TWIN" run --repo "$MODEL" --org netflix --scenario dvd-decline-2011 \
  --out "$OUT/forecast-bundle-again.json" >/dev/null || fail "second run failed"
cmp -s "$OUT/forecast-bundle.json" "$OUT/forecast-bundle-again.json" \
  || fail "the same pins produced different bytes"
echo "  ok   identical bytes"

say "13. a dirty tree is refused — the pin has to describe what you are reading"
echo "# scribble" >> "$MODEL/world/meta.yaml"
if "$TWIN" run --repo "$MODEL" --org netflix --scenario dvd-decline-2011 \
     --out "$OUT/should-not-exist.json" >/dev/null 2>&1; then
  fail "a dirty model repository ran anyway"
fi
git -C "$MODEL" checkout -- world/meta.yaml
echo "  ok   refused"

echo
echo "PASS: sense -> run -> score closes the loop from a clean checkout. Forecasts are a list,"
echo "scored by pin; the store is rebuildable from git; identical pins give identical bytes; a"
echo "dirty tree is refused. Every artefact declares which acceptance criteria are still"
echo "unchecked, so the skeleton cannot quietly become the definition of done."
echo
echo "artefacts: $OUT"
