#!/usr/bin/env bash
# THE MONEY SHOT. "The same workload lands on a DIFFERENT RUNG in driftwood and in ludlow,
# because their £ differ." One workload, one FAIR scenario, one shared cage body — evaluated
# against each institution's own signed risk-appetite band. The band alone moves the rung.
# Proportionality proven by comparison, not asserted.
#
# ECO-SYSTEM TICKET 89 re-pointed this beat. Until 2026-09-05 it derived `Audit` for driftwood
# and `Deny` for ludlow from the same two bands, and rendered a Deny-shaped ValidatingPolicy to
# prove it. That derivation had no shipped subject: nothing in the estate selects an enforcement
# action from a band any more. `graded/cage.py select_tier` selects a RUNG from the same band,
# `wargamer.select_party_tier` folds a party's priced lines onto one, and `tier_pr.py` lands it
# as a pull request against the governed Namespace manifest. So the beat now grades TIER
# SELECTION, which is the mechanism that ships, and the hub stops carrying a Deny of its own.
# The owner's words (2026-09-02, ticket 75 Q5): something can be unable to run only because it
# does not fit the cage, never because it is deliberately denied.
#
# Exits non-zero if the beat would fail on stage. OFFLINE core (python3; the kyverno CLI for the
# shared cage proof). Optional LIVE tail dry-runs the rendered Namespaces if the per-institution
# kind clusters are reachable — and when a tail could not look, this script exits 3 rather than
# asserting PASS after a parenthetical note (eco-system ticket 76).
set -euo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# Post-split (mo-12): platform is a real, separate GitHub repo, not a sibling
# directory. RISK is now an ordinary pinned dependency, fetched by
# clone-estate.sh into .estate-clone/ rather than reached directly.
ESTATE="$HERE/../../.estate-clone"
RISK="$ESTATE/platform/risk"
GRADED="$ESTATE/platform/graded"
SCEN="$HERE/scenarios/encrypt-at-rest.json"
say()  { printf '\033[1;36m==>\033[0m %s\n' "$*"; }
fail() { echo "FAIL: $*" >&2; exit 1; }
have() { command -v "$1" >/dev/null 2>&1; }

# could_not_look / pass_or_skip / selfcheck_absent: a live tail's third outcome.
. "$HERE/../lib-observation.sh"
SELF="$HERE/${BASH_SOURCE##*/}"
# The two tails that can fail to look: the shared cage proof and the per-cluster dry-run.
TAILS="kyverno kubectl"
# shellcheck disable=SC2086
if [ "${1:-}" = "--selfcheck" ]; then selfcheck_absent "$SELF" $TAILS; exit 0; fi

have python3 || fail "python3 required"
# Run this script's own could-not-look branch before looking at anything, so it is exercised on
# a machine that HAS the instruments rather than only on one that lacks them.
# shellcheck disable=SC2086
selfcheck_absent "$SELF" $TAILS
[ -d "$RISK" ] || bash "$HERE/../../clone-estate.sh" || fail "could not assemble .estate-clone/ (needs network — see clone-estate.sh)"

# field <org> <key> -> pull one value out of that org's £ decision (render.py --json, which is
# graded/cage.py's own `select`, so there is no second selection rule here).
field() { python3 "$HERE/render.py" --json "$1" | python3 -c "import sys,json;print(json.load(sys.stdin)['$2'])"; }

say "0. the cage engine's own asserts (tier table, selection, clamp, TCoR)"
timeout 90 python3 "$GRADED/cage.py" selfcheck >/dev/null || fail "cage.py selfcheck failed"
say "0b. the £ engine's own asserts (band reading, no timer)"
timeout 90 python3 "$RISK/enforce.py" selfcheck >/dev/null || fail "enforce.py selfcheck failed"

say "1. the SAME workload + SAME scenario -> divergent £-selected RUNGS"
dw_tier="$(field driftwood tier)"
lud_tier="$(field ludlow tier)"
[ "$dw_tier" = "baseline" ] || fail "driftwood should select baseline for this workload, got '$dw_tier'"
[ "$lud_tier" = "quarantine" ] || fail "ludlow should select quarantine for this workload, got '$lud_tier'"
[ "$dw_tier" != "$lud_tier" ] || fail "the rungs must differ for the comparison to mean anything"
# Neither rung is a refusal. There is no rung that is one: the bottom of the ladder is
# `isolated`, a running cage with no reach (ADR-0022, eco-system ticket 89).
for t in "$dw_tier" "$lud_tier"; do
  case "$t" in baseline|restricted|quarantine|isolated) ;; *) fail "'$t' is not on the ladder" ;; esac
done

say "2. the £ that DRIVES it — same uncaged residual, different signed bands"
dw_res="$(field driftwood uncaged_residual)"; dw_tol="$(field driftwood tolerance)"
lud_res="$(field ludlow uncaged_residual)"; lud_tol="$(field ludlow tolerance)"
# Same workload, same scenario -> the uncaged residual is IDENTICAL across institutions.
python3 - "$dw_res" "$lud_res" <<'PY' || fail "the uncaged residual differs across orgs — not the same workload"
import sys
a, b = float(sys.argv[1]), float(sys.argv[2])
assert abs(a - b) < 1e-6, f"the uncaged residual must be identical for the shared workload: {a} vs {b}"
PY
# The rung divergence is PURELY the band: the residual a baseline cage leaves fits driftwood's
# band and does not fit ludlow's, so ludlow buys two more rungs of cage for the same workload.
python3 - "$dw_res" "$dw_tol" "$lud_tol" "$GRADED" <<'PY' || fail "the £ does not straddle the two bands"
import sys
sys.path.insert(0, sys.argv[4])
import cage
res, dw_tol, lud_tol = map(float, sys.argv[1:4])
base = cage.caged_residual(res, "baseline")
quar = cage.caged_residual(res, "quarantine")
assert base <= dw_tol, f"a baseline cage leaves £{base:,.0f}, which must fit driftwood's £{dw_tol:,.0f} band"
assert base > lud_tol, f"a baseline cage leaves £{base:,.0f}, which must NOT fit ludlow's £{lud_tol:,.0f} band"
assert quar <= lud_tol, f"a quarantine cage leaves £{quar:,.0f}, which must fit ludlow's £{lud_tol:,.0f} band"
print(f"    uncaged £{res:,.0f}  |  driftwood band £{dw_tol:,.0f}: baseline leaves £{base:,.0f} -> baseline"
      f"  |  ludlow band £{lud_tol:,.0f}: baseline leaves £{base:,.0f}, quarantine leaves £{quar:,.0f} -> quarantine")
PY
[ "${dw_tol%.*}" != "${lud_tol%.*}" ] || fail "the bands must differ for the comparison to mean anything"

say "3. the rendered governed Namespaces carry the £-selected rung (not hand-authored)"
python3 "$HERE/render.py" --check || fail "committed namespaces drifted from the £-derived render"
grep -q "posture.acme.io/tier: $dw_tier" "$HERE/namespaces/proportionality-driftwood.yaml" \
  || fail "driftwood's namespace must declare posture.acme.io/tier: $dw_tier"
grep -q "posture.acme.io/tier: $lud_tier" "$HERE/namespaces/proportionality-ludlow.yaml" \
  || fail "ludlow's namespace must declare posture.acme.io/tier: $lud_tier"
# The declarations are byte-identical EXCEPT the tier and the two org labels — that is the point.
diff_lines="$(diff "$HERE/namespaces/proportionality-driftwood.yaml" "$HERE/namespaces/proportionality-ludlow.yaml" \
  | grep -c '^[<>]' || true)"
# Only the tier + name + part-of + proportionality-org lines differ: 4 lines each side.
[ "$diff_lines" -le 8 ] || fail "the namespaces differ in more than the tier+org lines ($diff_lines) — not the same declaration"
# And this directory ships no policy artefact at all any more (eco-system ticket 89, item 2):
# the template and the rendered files are Namespace declarations. Matched as the KEY at the
# start of a line, because the artefacts carry a dated note about the retirement in their own
# comments, and a note is not a policy. Only the ARTEFACTS are read: prose about the retirement
# is expected in this script and in the README.
if grep -rlnE '^[[:space:]]*validationActions:' "$HERE/namespaces" "$HERE/control" >/dev/null 2>&1; then
  fail "verify/proportionality still renders an enforcement action; the beat grades tier selection now"
fi
if [ -d "$HERE/policies" ]; then
  fail "verify/proportionality/policies/ is back; the Deny-shaped render was retired by eco-system ticket 89"
fi

say "4. the SHARED cage body puts the same pod in two different cages"
if have kyverno; then
  WORK="$(mktemp -d)"; trap 'rm -rf "$WORK"' EXIT
  # kyverno 1.18 populates `namespaceObject` only from a CLI values file's `namespaces:` list
  # (proven 2026-08-28, ADR-0022 consequences), so the two rendered Namespaces go there.
  { echo "apiVersion: cli.kyverno.io/v1alpha1"; echo "kind: Values"; echo "namespaces:";
    python3 - "$HERE" <<'PY'
import sys, yaml
docs = [yaml.safe_load(open(f"{sys.argv[1]}/namespaces/proportionality-{o}.yaml")) for o in ("driftwood", "ludlow")]
print(yaml.safe_dump(docs, default_flow_style=False).rstrip())
PY
  } > "$WORK/values.yaml"
  cat > "$WORK/pods.yaml" <<'YAML'
apiVersion: v1
kind: Pod
metadata:
  name: pii-store
  namespace: proportionality-driftwood
  labels: { "policy-as-versioned.dev/policy-version": "4.0.0" }
spec: { containers: [{ name: app, image: nginx }] }
---
apiVersion: v1
kind: Pod
metadata:
  name: pii-store
  namespace: proportionality-ludlow
  labels: { "policy-as-versioned.dev/policy-version": "4.0.0" }
spec: { containers: [{ name: app, image: nginx }] }
YAML
  timeout 120 kyverno apply "$GRADED/policies/cage-tier.yaml" --resource "$WORK/pods.yaml" \
    -f "$WORK/values.yaml" -o "$WORK/out" > "$WORK/log" 2>&1 \
    || fail "the shared cage refused a pod — a cage must never make a workload inadmissible: $(tail -3 "$WORK/log")"
  grep -qE 'fail: 0, ' "$WORK/log" || fail "the shared cage reported a refusal: $(tail -1 "$WORK/log")"
  out="$WORK/out/pii-store-mutated.yaml"
  [ -f "$out" ] || fail "kyverno wrote no mutated pod at $out"
  # One file, both pods. Each must carry its own namespace's rung and the dials that go with it.
  python3 - "$out" "$dw_tier" "$lud_tier" "$GRADED" <<'PY' || fail "the shared cage did not put the two pods in different cages"
import sys, yaml
sys.path.insert(0, sys.argv[4])
import cage
seen = {}
for doc in yaml.safe_load_all(open(sys.argv[1])):
    if not doc:
        continue
    ns = doc["metadata"]["namespace"]
    seen[ns] = doc
assert len(seen) == 2, f"want both namespaces mutated, got {sorted(seen)}"
for ns, want in (("proportionality-driftwood", sys.argv[2]), ("proportionality-ludlow", sys.argv[3])):
    doc = seen[ns]
    got = doc["metadata"]["labels"]["posture.acme.io/tier"]
    assert got == want, f"{ns}: cage rendered tier {got!r}, the £ selected {want!r}"
    assert doc["metadata"]["labels"]["posture.acme.io/caged"] == "true", ns
    pc = doc["spec"]["priorityClassName"]
    assert pc == cage.TIERS[want]["priorityClass"], f"{ns}: PriorityClass {pc} is not {want}'s"
    app = next(c for c in doc["spec"]["containers"] if c["name"] == "app")
    assert app["resources"]["limits"]["cpu"] == cage.TIERS[want]["cpu"], (ns, app["resources"])
    waf = [c for c in doc["spec"]["containers"] if c["name"] == "waf-sidecar"]
    assert bool(waf) == (cage.TIERS[want]["waf"] != "none"), f"{ns}: WAF sidecar presence wrong for {want}"
print(f"    same pod, same cage body: {sys.argv[2]} dials in driftwood, {sys.argv[3]} dials in ludlow, nothing denied")
PY
else
  could_not_look "no kyverno CLI here, so the shared cage body was never run against the two rendered namespaces -- step 3 read the declarations, it did not evaluate them"
fi

# --- optional LIVE tail: dry-run the rendered Namespaces on their clusters ------
# Each institution is its own tail: proportionality is a claim about BOTH, so one reachable
# cluster does not let the other's absence pass unnamed.
for org in driftwood ludlow; do
  ctx="kind-$org"
  if ! have kubectl; then
    could_not_look "no kubectl here, so $org's rendered namespace was never dry-run on $ctx"
  elif ! kubectl --context "$ctx" version >/dev/null 2>&1; then
    could_not_look "$ctx is not reachable, so $org's rendered namespace was never dry-run there"
  else
    say "5. live($org): the rendered namespace applies clean (server dry-run)"
    timeout 60 kubectl --context "$ctx" apply --dry-run=server \
      -f "$HERE/namespaces/proportionality-$org.yaml" >/dev/null \
      || fail "$org rendered namespace failed server dry-run on $ctx"
    echo "  ok   $org's rendered namespace applies clean on $ctx"
  fi
done

pass_or_skip "same workload, same uncaged £${dw_res%.*} — baseline in driftwood, quarantine in ludlow, because their signed bands differ. Neither is a refusal: the bottom of the ladder is a running cage. Proportionality by comparison."
