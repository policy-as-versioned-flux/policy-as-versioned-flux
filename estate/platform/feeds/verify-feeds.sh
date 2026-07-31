#!/usr/bin/env bash
# Beat: "the three reactive feeds (threat register, CVE, EOL) are signed +
# versioned, consumed by fair.py unmodified, a feed bump arrives as a
# reviewable diff that moves the £, and EOL is a time-varying thread (past-EOL
# -> £ ramps)." Offline, no cluster required.
set -euo pipefail
here="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
fair="$here/../fair/fair.py"
conv="$here/to_fair_scenario.py"
work="$(mktemp -d)"
trap 'rm -rf "$work"' EXIT

fail() { echo "FAIL: $*" >&2; exit 1; }
say() { echo; echo "== $* =="; }

[ -f "$fair" ] || fail "platform FAIR engine not found at $fair"

ale() { python3 "$fair" summary "$1" --mode warn | python3 -c "import json,sys; print(json.load(sys.stdin)['ale'])"; }

say "1. every feed signature + version verifies offline (v1, v2 x3 feeds)"
"$here/verify.sh" threat-register v1 register.json
"$here/verify.sh" threat-register v2 register.json
"$here/verify.sh" cve v1 cve-feed.json
"$here/verify.sh" cve v2 cve-feed.json
"$here/verify.sh" eol v1 eol-feed.json
"$here/verify.sh" eol v2 eol-feed.json

say "2. a tampered feed fails signature verification"
cp "$here/cve/v1/cve-feed.json" "$work/tampered.json"
python3 - "$work/tampered.json" <<'PY'
import json, sys
p = sys.argv[1]
d = json.load(open(p))
d["cves"]["CVE-2024-1234-envoy"]["cvss"] = 1.0
json.dump(d, open(p, "w"))
PY
if openssl pkeyutl -verify -pubin -inkey "$here/keys/feeds-signing-key.pub.pem" \
    -rawin -in "$work/tampered.json" -sigfile "$here/cve/v1/cve-feed.json.sig" >/dev/null 2>&1; then
  fail "tampered CVE feed still verified against v1's signature"
fi
echo "ok  tampered feed correctly rejected"

say "3. fair.py consumes all three feeds as pinned deps (unmodified fair.py)"
python3 "$conv" threat "$here/threat-register/v1/register.json" tuppence -o "$work/threat-v1.json"
python3 "$conv" threat "$here/threat-register/v2/register.json" tuppence -o "$work/threat-v2.json"
python3 "$conv" cve "$here/cve/v1/cve-feed.json" CVE-2024-1234-envoy -o "$work/cve-v1.json"
python3 "$conv" cve "$here/cve/v2/cve-feed.json" CVE-2024-1234-envoy -o "$work/cve-v2.json"
python3 "$conv" eol "$here/eol/v1/eol-feed.json" istio-1.18 --as-of 2026-07-31 -o "$work/eol-warm.json"

t1=$(ale "$work/threat-v1.json"); t2=$(ale "$work/threat-v2.json")
echo "ale(threat-register v1 tuppence) = £$(printf '%.0f' "$t1")"
echo "ale(threat-register v2 tuppence) = £$(printf '%.0f' "$t2")"

say "4. a feed bump (v1 -> v2, a reviewable diff) moves the £ -- no fair.py edit"
python3 - "$t1" "$t2" <<'PY'
import sys
a, b = float(sys.argv[1]), float(sys.argv[2])
assert b > a, f"threat-register bump (tuppence ATO uptick) did not raise the £ ({a} -> {b})"
print(f"ok  threat-register £ rose by £{b - a:,.0f} on the v1->v2 tuppence lef bump")
PY

c1=$(ale "$work/cve-v1.json")
python3 "$conv" cve "$here/cve/v2/cve-feed.json" CVE-2024-8888-istiod -o "$work/cve-v2-new.json"
c2new=$(ale "$work/cve-v2-new.json")
echo "ok  v2's new CVE-2024-8888-istiod prices at £$(printf '%.0f' "$c2new") ALE (didn't exist in v1)"

say "5. EOL is a time-varying thread: same component, later --as-of => higher £"
python3 "$conv" eol "$here/eol/v1/eol-feed.json" istio-1.18 --as-of 2024-01-01 -o "$work/eol-pre.json"   # before EOL
python3 "$conv" eol "$here/eol/v1/eol-feed.json" istio-1.18 --as-of 2025-02-21 -o "$work/eol-1yr.json"   # 1yr past
python3 "$conv" eol "$here/eol/v1/eol-feed.json" istio-1.18 --as-of 2028-02-21 -o "$work/eol-4yr.json"   # 4yr past (capped)
e_pre=$(ale "$work/eol-pre.json"); e_1yr=$(ale "$work/eol-1yr.json"); e_4yr=$(ale "$work/eol-4yr.json")
echo "ale(istio-1.18, pre-EOL)     = £$(printf '%.0f' "$e_pre")"
echo "ale(istio-1.18, 1yr past)    = £$(printf '%.0f' "$e_1yr")"
echo "ale(istio-1.18, 4yr+ past)   = £$(printf '%.0f' "$e_4yr")"
python3 - "$e_pre" "$e_1yr" "$e_4yr" <<'PY'
import sys
pre, y1, y4 = (float(x) for x in sys.argv[1:4])
assert pre < y1 < y4, f"EOL £ did not ramp monotonically: pre={pre} 1yr={y1} 4yr={y4}"
print(f"ok  EOL £ ramps monotonically as the component ages past support: "
      f"£{pre:,.0f} -> £{y1:,.0f} -> £{y4:,.0f}")
PY

say "6. converter selfcheck (every feed entry valid, EOL ramp bounded)"
python3 "$conv" selfcheck

echo
echo "PASS: threat-register/CVE/EOL signed+versioned, fair.py consumes them unmodified,"
echo "a feed bump moves the £ via a reviewable diff, EOL prices as a time-varying thread."
