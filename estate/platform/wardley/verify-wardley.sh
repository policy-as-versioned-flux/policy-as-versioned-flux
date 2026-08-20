#!/usr/bin/env bash
# Beat: "the AI-Wardley layer maps market intel, FLAGS commoditisation MOVEMENT
# (not mere position), collapses a commoditising attacker-capability into a
# FORWARD signal PER INSTITUTION, and feeds each straight through the war-gamer
# against its own band so proportionality re-tunes BEFORE the threat lands, three
# institutions honestly (possibly) apart -- and the map update is an attestable,
# tamper-evident commit." Offline, no cluster. Needs python3 + openssl.
set -euo pipefail
here="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
pub="$here/../feeds/keys/feeds-signing-key.pub.pem"
fail() { echo "FAIL: $*" >&2; exit 1; }
say() { echo; echo "== $* =="; }

say "1. the market intel + rendered map are signed + verify offline (attestable)"
for f in "$here/intel/market-intel.json" "$here/map/wardley-map.json"; do
  openssl pkeyutl -verify -pubin -inkey "$pub" -rawin -in "$f" -sigfile "$f.sig" >/dev/null \
    || fail "signature did not verify: $f"
  echo "ok  signed + verified: ${f#$here/}"
done

say "2. a tampered map update is rejected (map updates are tamper-evident commits)"
tmp="$(mktemp)"; trap 'rm -f "$tmp"' EXIT
python3 - "$here/map/wardley-map.json" "$tmp" <<'PY'
import json, sys
d = json.load(open(sys.argv[1]))
d["components"][0]["commoditising"] = not d["components"][0]["commoditising"]  # forge a flag
json.dump(d, open(sys.argv[2], "w"))
PY
if openssl pkeyutl -verify -pubin -inkey "$pub" -rawin -in "$tmp" \
     -sigfile "$here/map/wardley-map.json.sig" >/dev/null 2>&1; then
  fail "a tampered Wardley map still verified against the committed signature"
fi
echo "ok  tampered map correctly rejected"

say "3. the map flags commoditisation MOVEMENT, not position"
python3 "$here/wardley.py" map | python3 -c "
import json, sys
m = json.load(sys.stdin)
for c in m['components']:
    flag = 'MOVING' if c['commoditising'] else '  --  '
    print(f\"  [{flag}] {c['id']:26} {c['actor']:20} {c['stage']:9} -> {c['projected_stage']:9} (+{c['movement']})\")
by = {c['id']: c for c in m['components']}
assert by['phishing-kits-aas']['commoditising'], 'a fast product-stage attack must flag as moving'
assert not by['credential-stuffing-aas']['commoditising'], 'already-commodity + stationary must NOT flag'
print('ok  commoditisation is read as MOVEMENT across the horizon, not static position')
"

say "4. the forward signal + war-gamer seam, PER INSTITUTION: forward re-price -> drift -> signed PR"
python3 "$here/wardley.py" wargame | python3 -c "
import json, sys
out = json.load(sys.stdin)  # {org: {rows, proposals, ...}} -- one result per institution
total_drifts = total_props = 0
for org, res in out.items():
    print(f'  -- {org} --')
    for r in res['rows']:
        mark = 'DRIFT' if r['drift'] else '  ok '
        print(f\"    [{mark}] {r['control']:34} {r['deployed']:8} -> {r['implied']}\")
    drifts = [r for r in res['rows'] if r['drift']]
    props = res['proposals']
    assert drifts, f'{org}: the forward signal surfaced no drift'
    assert props, f'{org}: forward drift but no PR proposed'
    for p in props:
        assert p['merged'] is False and p['auto_merge'] is False, 'war-gamer must never merge'
        assert 'cross-check' in p['required_gate'], 'PR must ride the version cross-check gate'
        assert p['signed'] and 'Rekor' in p['identity'], 'PR must carry the attestable identity'
    total_drifts += len(drifts)
    total_props += len(props)
# the band, not the signal, decides -- prove it: driftwood's loose band and ludlow's
# strict one must NOT drift on the identical control set, or this is one org run
# three times wearing different labels, not a per-institution forward layer.
dw_ids = {r['control'] for r in out['driftwood']['rows'] if r['drift']}
lud_ids = {r['control'] for r in out['ludlow']['rows'] if r['drift']}
assert dw_ids != lud_ids, ('driftwood and ludlow must diverge on at least one control', dw_ids, lud_ids)
print(f'ok  {total_drifts} forward drift(s) across {len(out)} institution(s) -> {total_props} signed PR(s), 0 merged, all gated')
"

say "5. the projection + seam asserts (base does NOT drift; the forward bump does)"
python3 "$here/wardley.py" selfcheck || fail "wardley selfcheck failed"

echo
echo "PASS: market intel mapped, commoditisation MOVEMENT flagged, the forward signal"
echo "re-priced ahead of the reactive feeds PER INSTITUTION and fed through the war-gamer"
echo "to a signed, gated, never-merged PR (each institution against its own band) --"
echo "and the map update is a signed, tamper-evident commit."
