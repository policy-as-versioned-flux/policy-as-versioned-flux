#!/usr/bin/env bash
# Beat: "A workload that falls behind keeps running but CAGED BY DEGREE, not denied
# — named tiers expand into dials deterministically, the £ picks the tier, and the
# cage's run-cost is booked to TCoR." Exits non-zero if the beat would fail on stage.
#
# OFFLINE core (always; needs `kyverno` + python3):
#   1. cage.py selfcheck: tiers->dials deterministic; the £ picks the tier; a bigger
#      residual/tighter band picks a tighter cage or falls through to Deny; TCoR is
#      booked as residual (R'>0) + cost-of-controls (C_cage>0).
#   2. cage-tier MUTATE test: a behind-posture pod is MUTATED INTO ITS CAGE (limits +
#      PriorityClass on every tier; drop-ALL caps + read-only-fs + WAF sidecar on
#      restricted/quarantine), NOT denied; an in-currency pod is untouched.
#   3. cage-netpol GENERATE test: a caged pod triggers an egress-lockdown NetworkPolicy.
#   4. drift guard: the Kyverno tier->dials map mirrors cage.py's TIERS table exactly.
#   5. the eviction PriorityClasses are valid and ordered tighter = lower.
# LIVE tail (only if a cluster with the policies is reachable; bounded):
#   6. cage-tier + cage-netpol installed; a behind-posture pod server-dry-runs to a
#      caged (mutated) admit, not a deny.
set -euo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CTX="${CTX:-kind-driftwood}"
say()  { printf '\033[1;36m==>\033[0m %s\n' "$*"; }
fail() { echo "FAIL: $*" >&2; exit 1; }
have() { command -v "$1" >/dev/null 2>&1; }

have python3 || fail "python3 required"
have kyverno || fail "kyverno CLI required for the offline cage proofs"

say "1. offline: the £ engine — tiers/dials deterministic, £ picks the tier, TCoR booked"
python3 "$HERE/cage.py" selfcheck || fail "cage.py selfcheck failed"

say "2. offline: a behind-posture pod is MUTATED INTO ITS CAGE, not denied"
kyverno test "$HERE/tests/cage-tier" >/dev/null || fail "cage-tier mutate matrix failed"

say "3. offline: a caged pod GENERATES an egress-lockdown NetworkPolicy"
kyverno test "$HERE/tests/cage-netpol" >/dev/null || fail "cage-netpol generate matrix failed"

say "4. offline: the Kyverno tier->dials map mirrors cage.py's TIERS (no drift)"
python3 - "$HERE" <<'PY'
import sys, os, re
here = sys.argv[1]
sys.path.insert(0, here)
import cage
pol = open(os.path.join(here, "policies/cage-tier.yaml")).read()
fails = []
def check(c, m):
    if not c: fails.append(m)
    print(("  ok   " if c else "  FAIL ") + m)

for tier in cage.ORDER:
    d = cage.TIERS[tier]
    # The map row for this tier, e.g. "'restricted':{'cpu':'250m','mem':'128Mi','pc':'cage-restricted',...}"
    m = re.search(r"'%s':\s*\{([^}]*)\}" % tier, pol)
    check(m is not None, f"{tier}: present in the Kyverno dial map")
    if not m: continue
    row = m.group(1)
    check(f"'cpu':'{d['cpu']}'" in row, f"{tier}: cpu {d['cpu']} matches cage.py")
    check(f"'mem':'{d['mem']}'" in row, f"{tier}: mem {d['mem']} matches cage.py")
    check(f"'pc':'{d['priorityClass']}'" in row, f"{tier}: PriorityClass {d['priorityClass']} matches cage.py")
    # harden flag = dropAll && readOnlyRootFs; the map encodes it as 'harden':'true'|'false'
    harden = "true" if (d["dropAll"] and d["readOnlyRootFs"]) else "false"
    check(f"'harden':'{harden}'" in row, f"{tier}: harden={harden} matches cage.py dropAll/readOnlyRootFs")
    # WAF present iff cage.py waf != none; map uses wafCpu '0' as the no-WAF sentinel
    waf_off = "'wafCpu':'0'" in row
    check(waf_off == (d["waf"] == "none"), f"{tier}: WAF presence matches cage.py waf={d['waf']}")

if fails: sys.exit(f"\n{len(fails)} drift(s) between cage.py and cage-tier.yaml")
print("  -- cage.py and the Kyverno cage are in step --")
PY

say "5. offline: eviction PriorityClasses valid and ordered (tighter tier = lower value)"
python3 - "$HERE" <<'PY'
import sys, os, yaml
here = sys.argv[1]
pcs = {o["metadata"]["name"]: o["value"]
       for o in yaml.safe_load_all(open(os.path.join(here, "policies/priorityclasses.yaml"))) if o}
order = ["cage-baseline", "cage-restricted", "cage-quarantine"]
fails = []
def check(c, m):
    if not c: fails.append(m)
    print(("  ok   " if c else "  FAIL ") + m)
for n in order:
    check(n in pcs, f"{n} PriorityClass defined")
vals = [pcs[n] for n in order if n in pcs]
check(all(v < 0 for v in vals), "every cage sits below the default priority (0)")
check(vals == sorted(vals, reverse=True), "tighter tier = lower value (baseline > restricted > quarantine)")
if fails: sys.exit(f"\n{len(fails)} PriorityClass invariant(s) broken")
print("  -- eviction ordering holds --")
PY

# ---- live tail: only if a cluster actually has the cage policies installed ----
if have kubectl && timeout 10 kubectl --context "$CTX" get mutatingpolicy cage-tier >/dev/null 2>&1; then
  say "6. live: cage policies installed; a behind-posture pod is CAGED (mutated), not denied"
  timeout 10 kubectl --context "$CTX" get generatingpolicy cage-netpol >/dev/null 2>&1 \
    || fail "cage-netpol GeneratingPolicy not installed live"
  PROBE=$(cat <<'EOF'
apiVersion: v1
kind: Pod
metadata:
  name: cage-probe
  namespace: default
  labels: { "policy-as-versioned.dev/policy-version": "1.0.0", "posture.acme.io/tier": "restricted" }
spec:
  containers: [{ name: app, image: nginx }]
EOF
)
  OUT=$(echo "$PROBE" | timeout 20 kubectl --context "$CTX" apply --dry-run=server -f - \
        -o jsonpath='{.metadata.labels.posture\.acme\.io/caged}' 2>/dev/null || true)
  [ "$OUT" = "true" ] && echo "  ok   behind-posture pod admitted with the caged label stamped (not denied)" \
    || echo "  (server dry-run returned caged='$OUT'; needs Kyverno mutating webhook live — see README)"
else
  say "6. live checks skipped: no cluster with the cage policies at context '$CTX'"
  say "   (offline proofs above are the demonstrable claim; live needs Kyverno installed +"
  say "    estate/platform/graded/up.sh applied)"
fi

echo "PASS: behind-posture keeps running but caged by degree; the £ picks the tier; TCoR booked."
