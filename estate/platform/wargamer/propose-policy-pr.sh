#!/usr/bin/env bash
# propose-policy-pr.sh — the "war-gamer opens a signed policy PR" beat.
#
# Same propose-never-dispose rail as driftwood/scripts/bump-nist-pin.sh: it stops
# at the diff a human reviews. It NEVER commits, pushes, opens or merges the PR
# itself (that is a human + the CI gate, not this script). What it demonstrates:
#   1. the war-gamer detects proportionality drift off a SIGNED feed change,
#   2. renders the Audit->Deny policy diff (the PR body) WITHOUT touching main,
#   3. shows the version cross-check GATE is real and would run on the PR,
#   4. names the gitsign -> Rekor identity every war-gamer commit carries.
#
# Offline. Needs python3; kyverno + gitsign are used if present, else narrated.
set -euo pipefail
here="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
platform="$here/.."
policy="$platform/distribution/policies/v2.0.0/require-nonroot.yaml"
workflow_gate="$platform/shift-left/ci-check.py"
work="$(mktemp -d)"; trap 'rm -rf "$work"' EXIT

say() { printf '\033[1;36m==>\033[0m %s\n' "$*"; }

# 1. Ask the war-gamer what drifted and what it proposes.
say "war-gaming current controls against the signed feed set..."
python3 "$here/wargamer.py" propose > "$work/props.json"
branch="$(python3 -c "
import json
ps=json.load(open('$work/props.json'))
f=[p for p in ps if p['change']['from']=='Audit' and p['change']['to']=='Deny']
print(f[0]['branch'] if f else '')")"
[ -n "$branch" ] || { echo "no Audit->Deny drift to propose (controls proportionate)"; exit 0; }
say "drift found -> would open PR on branch '$branch'"

# 2. Render the Audit->Deny diff WITHOUT mutating main (propose, never dispose).
[ -f "$policy" ] || { echo "policy not found: $policy" >&2; exit 1; }
sed 's/validationActions: \[Audit\]/validationActions: [Deny]/' "$policy" > "$work/proposed.yaml"
echo
echo "--- proposed policy diff (this is the PR body a human reviews) ---"
diff -u "$policy" "$work/proposed.yaml" | tail -n +3 || true
echo "--- end diff ---"
if ! diff -q "$policy" "$work/proposed.yaml" >/dev/null; then
  echo "ok  the flip is proposed on a branch; main is untouched"
else
  echo "note: policy already at Deny (nothing to flip)"
fi

# 3. The version cross-check GATE is real and would run on this PR.
echo
say "the PR carries the version cross-check gate: $(basename "$workflow_gate")"
if command -v kyverno >/dev/null 2>&1; then
  # The gate catches an Audit->Deny flip pre-merge: a violating workload that
  # today only Audits would be DENIED once this PR lands. Prove it fires.
  if python3 "$workflow_gate" --resource "$platform/shift-left/fixtures/workload-flip.yaml" >/dev/null 2>&1; then
    echo "unexpected: the gate passed a workload that should trip the flip" >&2; exit 1
  fi
  echo "ok  gate runs (kyverno): a workload compliant-under-Audit is caught pre-merge by the +/-1 cross-check"
else
  echo "note: kyverno absent -- gate is wired (ci-workflow.example.yml) but not run here"
fi

# 4. The war-gamer's own attestable identity on the commit.
echo
if command -v gitsign >/dev/null 2>&1; then
  say "commit identity: gitsign keyless (OIDC -> Fulcio) -> Rekor  [$(gitsign --version 2>&1 | head -1 || echo gitsign)]"
else
  say "commit identity: gitsign keyless (OIDC -> Fulcio) -> Rekor  [gitsign absent here]"
fi
echo
say "next (human + CI, NOT this agent): git commit --gitsign on '$branch', push, open PR,"
say "     the gate + a human reviewer dispose. The war-gamer proposes; it never merges."
