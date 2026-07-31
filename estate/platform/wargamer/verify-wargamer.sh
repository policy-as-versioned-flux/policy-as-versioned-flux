#!/usr/bin/env bash
# Beat: "the war-gamer collects signed feeds, war-games current controls (workload
# + human/device/ransomware/PQ), and on proportionality drift opens a SIGNED policy
# PR -- proposing, never disposing; the PR carries the version cross-check gate."
# Offline, no cluster. Needs python3; kyverno/gitsign used if present.
set -euo pipefail
here="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
platform="$here/.."
fail() { echo "FAIL: $*" >&2; exit 1; }
say() { echo; echo "== $* =="; }

say "1. the signed feed-change fixture verifies offline (the war-gamer's drift input)"
key="$platform/feeds/keys/feeds-signing-key.pub.pem"
f="$here/fixtures/threat-register/v3/register.json"
openssl pkeyutl -verify -pubin -inkey "$key" -rawin -in "$f" -sigfile "$f.sig" >/dev/null \
  || fail "v3 drift fixture signature did not verify"
echo "ok  threat-register v3 (driftwood skimmer uptick) signed + verified"

say "2. a tampered feed fixture is rejected (integrity of the war-gamer's input)"
tmp="$(mktemp)"; trap 'rm -f "$tmp"' EXIT
python3 - "$f" "$tmp" <<'PY'
import json, sys
d = json.load(open(sys.argv[1]))
d["institutions"]["driftwood"]["lef"] = [1, 1, 1]   # forge the drift away
json.dump(d, open(sys.argv[2], "w"))
PY
if openssl pkeyutl -verify -pubin -inkey "$key" -rawin -in "$tmp" \
     -sigfile "$f.sig" >/dev/null 2>&1; then
  fail "a tampered feed fixture still verified"
fi
echo "ok  tampered feed fixture correctly rejected"

say "3. the feed->PR seam: collect -> war-game -> propose-never-dispose"
python3 "$here/wargamer.py" selfcheck || fail "wargamer selfcheck failed"

say "4. the war-game drift report (enforcement + human/device scenarios)"
python3 "$here/wargamer.py" wargame | python3 -c "
import json, sys
rows = json.load(sys.stdin)
for r in rows:
    mark = 'DRIFT' if r['drift'] else '  ok '
    print(f\"  [{mark}] {r['kind']:11} {r['org']:9} {r['control']:32} {r['deployed']:8} -> {r['implied']}\")
drifts = [r for r in rows if r['drift']]
assert drifts, 'expected at least one drift'
assert any(r['kind']=='enforcement' for r in drifts), 'expected an enforcement drift'
assert any(r['kind']=='scenario' for r in drifts), 'expected a human/device scenario drift'
print(f'ok  {len(drifts)} drift(s): the war-gamer found disproportionate controls to re-tune')
"

say "5. the propose-never-dispose beat (the signed PR, the gate, no merge)"
bash "$here/propose-policy-pr.sh"

echo
echo "PASS: signed feeds collected + integrity-checked, current controls war-gamed"
echo "(workload + human/device + PQ), drift detected, a signed policy PR proposed with"
echo "the version cross-check gate -- and never merged. The war-gamer proposes; a human disposes."
