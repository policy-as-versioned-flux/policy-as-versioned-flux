#!/usr/bin/env bash
# Beat: the evidence up-flow is real and RESOLVES end to end.
#
#   PolicyReport (one engine, both planes)
#        -> observation  (result2oscal: the evidence)
#        -> finding       (result2oscal: control satisfied / not-satisfied)
#        -> risk          (../policy/render-exemption.py: deviation-approved, £ facet)
#        -> related-observations  -> BACK to the not-satisfied observation
#
# The join is asserted, not asserted-by-eyeball: the risk's related-observation
# uuid must equal an observation uuid result2oscal emits. Fully offline.
set -euo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
say()  { printf '\033[1;36m==>\033[0m %s\n' "$*"; }
fail() { echo "FAIL: $*" >&2; exit 1; }
have() { command -v "$1" >/dev/null 2>&1; }

have python3 || fail "python3 required"
WORK="$(mktemp -d)"; trap 'rm -rf "$WORK"' EXIT

say "1. result2oscal: PolicyReports -> OSCAL assessment-results (observations + findings)"
python3 "$HERE/result2oscal.py" --json > "$WORK/ar.json" || fail "result2oscal errored"
python3 - "$WORK/ar.json" <<'PY' || fail "assessment-results malformed"
import json, sys
r = json.load(open(sys.argv[1]))["assessment-results"]["results"][0]
assert r["observations"], "no observations"
fmap = {f["target"]["target-id"]: f["target"]["status"]["state"] for f in r["findings"]}
assert fmap.get("nist-800-53:AC-6") == "not-satisfied", fmap
assert fmap.get("nist-800-53:CM-6") == "satisfied", fmap
print(f"   {len(r['observations'])} observations, {len(r['findings'])} findings; "
      f"AC-6 not-satisfied, CM-6 satisfied")
PY

say "2. result2oscal's own asserts (chain resolves by construction)"
python3 "$HERE/result2oscal.py" --selfcheck | sed 's/^/   /'

say "3. the ledger's risk related-observation resolves to a c2p observation (the join)"
python3 "$HERE/../policy/render-exemption.py" --oscal > "$WORK/risks.yaml" || fail "render-exemption errored"
python3 - "$WORK/ar.json" "$WORK/risks.yaml" <<'PY' || fail "up-flow chain does not resolve"
import json, sys, yaml
emitted = {o["uuid"] for o in
           json.load(open(sys.argv[1]))["assessment-results"]["results"][0]["observations"]}
risks = yaml.safe_load(open(sys.argv[2]))["risks"]
for risk in risks:
    linked = risk["related-observations"][0]["observation-uuid"]
    assert linked in emitted, f"risk {risk['uuid'][:8]} points at {linked[:8]}, not emitted"
    # and the £ is carried as a facet under our own system URI
    ale = [f for c in risk["characterizations"] for f in c["facets"]
           if f["name"] == "annualised-loss-expectancy"]
    assert ale and ale[0]["system"].endswith("/gbp"), "no £ facet under a custom system URI"
    print(f"   risk {risk['uuid'][:8]} (£{ale[0]['value']}) -> observation {linked[:8]} RESOLVES")
PY

# --- live tail: only if the OSCAL schema validator (trestle) happens to be present ---
if have trestle; then
  say "4. live: independent OSCAL schema validation via compliance-trestle"
  trestle validate -f "$WORK/ar.json" >/dev/null 2>&1 \
    && say "   assessment-results schema-valid" \
    || say "   (trestle validate reported issues — inspect $WORK/ar.json)"
else
  say "4. schema-validation tail skipped: compliance-trestle CLI not installed"
fi

echo "PASS: PolicyReport -> observation -> finding -> risk -> related-observation resolves end to end."
