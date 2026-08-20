#!/usr/bin/env bash
# Beat: "the ico penalty schema is signed + versioned, and a schema bump changes
# the £ fair.py reports -- without touching fair.py."
# Offline, no cluster required.
set -euo pipefail
here="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
schema_dir="$here/schema"
fair="$here/../platform/fair/fair.py"
work="$(mktemp -d)"
trap 'rm -rf "$work"' EXIT

fail() { echo "FAIL: $*" >&2; exit 1; }

[ -f "$fair" ] || fail "platform FAIR engine not found at $fair"

say() { echo; echo "== $* =="; }

say "1. schema signature + version verify offline (v1, v2)"
"$schema_dir/verify.sh" v1
"$schema_dir/verify.sh" v2

say "2. a tampered schema fails signature verification"
cp "$schema_dir/v1/penalty-schema.json" "$work/tampered.json"
python3 - "$work/tampered.json" <<'PY'
import json, sys
p = sys.argv[1]
d = json.load(open(p))
d["regimes"]["uk-gdpr"]["violation_types"]["higher-tier"]["formula"]["cap_gbp"] = 1
json.dump(d, open(p, "w"))
PY
if openssl pkeyutl -verify -pubin -inkey "$schema_dir/keys/ico-signing-key.pub.pem" \
    -rawin -in "$work/tampered.json" -sigfile "$schema_dir/v1/penalty-schema.json.sig" >/dev/null 2>&1; then
  fail "tampered schema still verified against v1's signature"
fi
echo "ok  tampered schema correctly rejected"

say "3. fair.py consumes the schema as a loss-magnitude input (unmodified fair.py)"
python3 "$schema_dir/to_fair_scenario.py" "$schema_dir/v1/penalty-schema.json" uk-gdpr lower-tier -o "$work/v1.json"
python3 "$schema_dir/to_fair_scenario.py" "$schema_dir/v2/penalty-schema.json" uk-gdpr lower-tier -o "$work/v2.json"
ale_v1=$(python3 "$fair" summary "$work/v1.json" --mode warn | python3 -c "import json,sys; print(json.load(sys.stdin)['ale'])")
ale_v2=$(python3 "$fair" summary "$work/v2.json" --mode warn | python3 -c "import json,sys; print(json.load(sys.stdin)['ale'])")
echo "ale(v1 uk-gdpr/lower-tier warn) = £$(printf '%.0f' "$ale_v1")"
echo "ale(v2 uk-gdpr/lower-tier warn) = £$(printf '%.0f' "$ale_v2")"

say "4. the schema bump (v1 -> v2) actually moved the £ -- one added real fine, no fair.py edit"
python3 - "$ale_v1" "$ale_v2" <<'PY'
import sys
a, b = float(sys.argv[1]), float(sys.argv[2])
assert a != b, f"schema bump did not change the £ (both {a})"
print(f"ok  £ moved by £{b - a:,.0f} on a version-only schema diff")
PY

say "5. one breach can draw several obligation sources; the £ is worst case, not one at a time (ticket 18)"
python3 "$schema_dir/to_fair_scenario.py" build "$schema_dir/v2/penalty-schema.json" uk-gdpr lower-tier \
    --also pci-dss:non-compliance-escalating -o "$work/combined.json"
ale_solo=$(python3 "$fair" summary "$work/v2.json" --mode warn | python3 -c "import json,sys; print(json.load(sys.stdin)['ale'])")
ale_combined=$(python3 "$fair" summary "$work/combined.json" --mode warn | python3 -c "import json,sys; print(json.load(sys.stdin)['ale'])")
echo "ale(uk-gdpr/lower-tier alone)               = £$(printf '%.0f' "$ale_solo")"
echo "ale(uk-gdpr/lower-tier + pci-dss, combined)  = £$(printf '%.0f' "$ale_combined")"
python3 - "$ale_solo" "$ale_combined" <<'PY'
import sys
solo, combined = float(sys.argv[1]), float(sys.argv[2])
assert combined > solo, f"a second obligation source on the same breach did not raise the £ ({combined} <= {solo})"
print(f"ok  £ rose by £{combined - solo:,.0f} once a second regime can draw on the same breach -- fatter, not thinner")
PY

echo
echo "PASS: ico penalty schema signed+versioned, fair.py consumes it unmodified, a schema bump moves the £,"
echo "and a second obligation source on one breach raises it further."
