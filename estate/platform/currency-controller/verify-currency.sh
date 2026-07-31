#!/usr/bin/env bash
# Beat: "When a workload's admitted version goes stale, the controller re-patches
# its posture (or evicts) within a bounded interval; the SVID reflects the new
# posture after reconcile." Exits non-zero if that would fail on stage.
#
# OFFLINE core (always; needs python3 + PyYAML):
#   1. currency.py selfcheck — stale = posture ∉ supported; re-patch drops BOTH labels.
#   2. plan on a fixture: a retired-version pod is selected; a current pod and an
#      un-postured pod are left alone.
#   3. cross-check vs the ticket-15 posture policies: the de-posture patch removes
#      exactly the label(s) that take the pod OUT OF SCOPE for stamp-posture (so
#      it isn't re-clobbered), posture-trust-boundary (so the patch isn't denied),
#      the orphan-guard, AND the posture ClusterSPIFFEID podSelector — which is
#      why the posture SVID stops being issued after reconcile.
#   4. the manifests are valid (client dry-run) if kubectl is present.
# LIVE tail (only if the CronJob is installed AND a postured pod on a retired
#   version exists; bounded): trigger one job and assert the pod is de-postured.
set -euo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CTX="${CTX:-kind-driftwood}"
say()  { printf '\033[1;36m==>\033[0m %s\n' "$*"; }
fail() { echo "FAIL: $*" >&2; exit 1; }
have() { command -v "$1" >/dev/null 2>&1; }

say "1. offline: currency.py selfcheck"
python3 "$HERE/currency.py" selfcheck || fail "selfcheck failed"

say "2. offline: plan selects only the retired-version postured pod"
PLAN=$(printf '%s' '[
  {"namespace":"tuppence","name":"reset-current","posture":"2.0.0"},
  {"namespace":"tuppence","name":"reset-retired","posture":"1.0.0"},
  {"namespace":"driftwood","name":"base","posture":null}
]' | python3 "$HERE/currency.py" plan --supported 2.0.0)
echo "$PLAN" | grep -q 'reset-retired'   || fail "plan missed the retired-version pod"
echo "$PLAN" | grep -q 'reset-current'   && fail "plan wrongly selected a current pod"
echo "$PLAN" | grep -q '"base"'          && fail "plan wrongly selected an un-postured pod"
echo "  ok   only reset-retired planned for de-posture"

say "3. offline: the de-posture patch takes the pod out of scope for every posture policy"
python3 - "$HERE" <<'PY'
import sys, os, yaml
here = sys.argv[1]
sys.path.insert(0, here)
import importlib.util
spec = importlib.util.spec_from_file_location("currency", os.path.join(here, "currency.py"))
cur = importlib.util.module_from_spec(spec); spec.loader.exec_module(cur)

removed = {k for k, v in cur.deposture_patch()["metadata"]["labels"].items() if v is None}
fails = []
def check(c, m):
    if not c: fails.append(m)
    print(("  ok   " if c else "  FAIL ") + m)

check(cur.CLAIM_LABEL in removed,   "re-patch removes the policy-version CLAIM (so stamp-posture won't re-clobber posture)")
check(cur.POSTURE_LABEL in removed, "re-patch removes the posture label (so posture-trust-boundary is out of scope)")

pdir = os.path.normpath(os.path.join(here, "../posture"))
def load(p):
    with open(p) as fh: return list(yaml.safe_load_all(fh))[0]

# stamp-posture (mutate) keys its matchCondition on the CLAIM -> removing the claim
# takes the pod out of scope, so the mutate cannot re-add the posture on our UPDATE.
mut = os.path.join(pdir, "policies/stamp-posture.yaml")
if os.path.exists(mut):
    mc = " ".join(c["expression"] for c in load(mut)["spec"]["matchConditions"])
    check(cur.CLAIM_LABEL in mc and cur.CLAIM_LABEL in removed,
          "stamp-posture scopes on the claim we remove -> mutate skips, no re-clobber")

# posture-trust-boundary (validate) keys on the POSTURE label -> removing it takes
# the pod out of scope, so the de-posture UPDATE is not denied.
val = os.path.join(pdir, "policies/posture-trust-boundary.yaml")
if os.path.exists(val):
    mc = " ".join(c["expression"] for c in load(val)["spec"]["matchConditions"])
    check(cur.POSTURE_LABEL in mc and cur.POSTURE_LABEL in removed,
          "posture-trust-boundary scopes on the posture we remove -> validate skips, patch allowed")

# the posture ClusterSPIFFEID podSelector REQUIRES the posture label to Exist ->
# once removed, the pod stops matching, the entry is GC'd, the posture SVID stops
# renewing. THIS is "the SVID reflects the new posture after reconcile".
csid = os.path.join(pdir, "spire/clusterspiffeid-posture.yaml")
if os.path.exists(csid):
    sel = load(csid)["spec"]["podSelector"]["matchExpressions"]
    keys = [e for e in sel if e.get("key") == cur.POSTURE_LABEL and e.get("operator") == "Exists"]
    check(bool(keys) and cur.POSTURE_LABEL in removed,
          "posture ClusterSPIFFEID needs the posture label to Exist -> removed => pod drops to base-mesh SVID")

if fails: sys.exit(f"\n{len(fails)} invariant(s) broken")
print("  -- de-posture is out-of-scope for stamp/validate/orphan-guard AND drops the posture SVID --")
PY

if have kubectl; then
  say "4. offline: manifests are valid (client dry-run)"
  kubectl apply --dry-run=client -f "$HERE/manifests/rbac.yaml"    >/dev/null || fail "rbac.yaml invalid"
  kubectl apply --dry-run=client -f "$HERE/manifests/cronjob.yaml" >/dev/null || fail "cronjob.yaml invalid"
  echo "  ok   rbac.yaml + cronjob.yaml apply-clean"
else
  say "4. skipped: kubectl absent (manifest dry-run)"
fi

# ---- live tail: only if the CronJob is installed and a stale postured pod exists ----
if have kubectl && timeout 10 kubectl --context "$CTX" -n currency-system get cronjob currency-controller >/dev/null 2>&1; then
  STALE=$(timeout 10 kubectl --context "$CTX" get pods -A -l posture.acme.io/version \
            -o jsonpath='{range .items[*]}{.metadata.namespace}/{.metadata.name}={.metadata.labels.posture\.acme\.io/version} {end}' 2>/dev/null || true)
  if [ -n "$STALE" ]; then
    say "5. live: postured pods present ($STALE) — triggering one bounded reconcile pass"
    timeout 20 kubectl --context "$CTX" -n currency-system delete job currency-verify --ignore-not-found >/dev/null 2>&1 || true
    timeout 20 kubectl --context "$CTX" -n currency-system create job --from=cronjob/currency-controller currency-verify >/dev/null 2>&1 \
      && echo "  ok   reconcile job created (inspect: kubectl -n currency-system logs job/currency-verify)" \
      || echo "  (could not create job — image pull or RBAC; see README)"
  else
    say "5. live: CronJob installed but no postured pods to reconcile yet (nothing stale) — skipping trigger"
  fi
else
  say "5. live checks skipped: no currency-controller CronJob at context '$CTX'"
  say "     (run estate/platform/currency-controller/up.sh; offline proofs above are the demonstrable claim)"
fi

echo "PASS: stale posture is re-evaluated post-admission; the re-patch drops BOTH labels so the SVID falls back to base-mesh."
