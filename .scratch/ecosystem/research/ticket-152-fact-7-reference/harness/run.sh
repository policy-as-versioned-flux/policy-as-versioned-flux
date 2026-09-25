#!/usr/bin/env bash
# usage: run.sh <adopter> <candidate>
set -uo pipefail
K=${KYVERNO:?set KYVERNO to a kyverno 1.18.2 CLI}; H=$(cd "$(dirname "$0")" && pwd); A=$1; C=$2
P=${PROVE:?set PROVE to the directory holding <adopter>/composed}/$A/composed
O=$H/out/$A-$C; rm -rf $O; mkdir -p $O
MUT="$P/policies/v5.0.0/cage-tier.yaml $P/policies/v5.0.0/stamp-posture.yaml $P/governed-namespace-guard.yaml $P/governed-namespace-holds.yaml $P/orphan-cage.yaml $P/orphan-cage-holds.yaml"
GEN="$P/policies/v5.0.0/cage-netpol.yaml $P/bottom-rung-netpol.yaml"
VAL="$P/orphan-guard.yaml $P/governed-namespace-report.yaml $P/policies/v5.0.0/posture-trust-boundary.yaml $P/policies/v5.0.0/require-nonroot.yaml"
$K apply $MUT --resource $H/$C/pod.json -f $H/$C/values.json --remove-color -t -o $O/mut-all.yaml > $O/mut.log 2>&1
echo "mut exit=$?" >> $O/mut.log
# final mutated pod = last YAML document the CLI wrote; if nothing mutated, the original pod
python3 - "$O" "$H/$C/pod.json" <<'PY'
import sys, yaml, json, os
o, orig = sys.argv[1], sys.argv[2]
docs = []
if os.path.exists(o + "/mut-all.yaml"):
    docs = [d for d in yaml.safe_load_all(open(o + "/mut-all.yaml")) if d]
final = docs[-1] if docs else json.load(open(orig))
json.dump(final, open(o + "/final-pod.json", "w"), indent=1)
PY
$K apply $GEN --resource $O/final-pod.json -f $H/$C/values.json --remove-color -t -o $O/gen.yaml > $O/gen.log 2>&1
echo "gen exit=$?" >> $O/gen.log
$K apply $VAL --resource $O/final-pod.json -f $H/$C/values.json --remove-color -t > $O/val.log 2>&1
echo "val exit=$?" >> $O/val.log
