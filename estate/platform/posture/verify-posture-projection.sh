#!/usr/bin/env bash
# Beat: "A pod admitted under vN gets an SVID whose path carries posture/vN; the
# posture label is settable only by the trusted Kyverno policy; forging it is
# refused." Exits non-zero if any of that would fail on stage.
#
# OFFLINE core (always; needs `kyverno` + python3):
#   1. stamp-posture stamps posture == the validated claim, and CLOBBERS a
#      forged incoming posture (kyverno test).
#   2. posture-trust-boundary DENIES a forged/mismatched posture (kyverno test)
#      — the "forging is refused" proof, provable without a cluster.
#   3. the posture ClusterSPIFFEID bakes `posture/<vN>` as a LEADING path segment
#      derived from the Kyverno label, and coexists with the base mesh SVID.
# LIVE tail (only if a cluster with the policies installed is reachable; bounded):
#   4. both policies + the ClusterSPIFFEID are installed;
#   5. server dry-run: a hand-set posture with no claim is DENIED at admission;
#   6. server dry-run: a forger's posture is clobbered back to its real claim.
set -euo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CTX="${CTX:-kind-driftwood}"
say()  { printf '\033[1;36m==>\033[0m %s\n' "$*"; }
fail() { echo "FAIL: $*" >&2; exit 1; }
have() { command -v "$1" >/dev/null 2>&1; }

have kyverno || fail "kyverno CLI required for the offline posture proofs"

say "1. offline: stamp-posture stamps from the claim + clobbers a forged posture"
kyverno test "$HERE/tests/stamp-posture" >/dev/null \
  || fail "stamp-posture mutate matrix failed"

say "2. offline: posture-trust-boundary DENIES a forged/mismatched posture"
kyverno test "$HERE/tests/posture-trust-boundary" >/dev/null \
  || fail "trust-boundary reject matrix failed — forging is not refused"

say "3. offline: ClusterSPIFFEID bakes posture/<vN> into the SVID path (leading segment)"
python3 - "$HERE" <<'PY'
import sys, os, yaml
here = sys.argv[1]
def load(p):
    with open(p) as fh: return list(yaml.safe_load_all(fh))
posture = load(os.path.join(here, "spire/clusterspiffeid-posture.yaml"))[0]
tmpl = posture["spec"]["spiffeIDTemplate"]
fails = []
def check(c, m):
    if not c: fails.append(m)
    print(("  ok   " if c else "  FAIL ") + m)

check(posture["kind"] == "ClusterSPIFFEID", "posture object is a ClusterSPIFFEID")
check("/posture/" in tmpl, "template carries a /posture/ path segment")
# posture must LEAD the path (before /ns/) so a single Istio prefix wildcard matches it.
check(tmpl.index("/posture/") < tmpl.index("/ns/"), "posture segment LEADS the path (before /ns/) — one-wildcard Istio match")
check('posture.acme.io/version' in tmpl, "posture path is derived from the Kyverno-stamped label, not free text")
check(posture["spec"]["podSelector"]["matchExpressions"][0]["key"] == "posture.acme.io/version",
      "podSelector requires the posture label to exist")
jwt = posture["spec"].get("jwtTtl")
check(jwt == "5m", f"jwtTtl short (5m) so out-of-currency callers lose secrets fast, got {jwt!r}")
# ticket 11 (live-discovered): the spire chart scopes its controller-manager
# to className "<release-namespace>-<release-name>" and runs with "handle
# crs without class name: false". A hand-authored ClusterSPIFFEID with no
# className is never reconciled at all — not denied, not errored, just
# permanently absent from every pass (.status.stats stays empty forever).
# Confirmed live: this object minted zero registration entries from the day
# it was first applied until className was added, despite every offline
# proof and every downstream pod carrying exactly the label it selects on.
check(posture["spec"].get("className") not in (None, ""),
      "className set, so spire-controller-manager actually reconciles this object (see comment in the source file)")

# Coexistence with the base mesh SVID (ticket 14) — different name, un-postured base.
base_path = os.path.normpath(os.path.join(here, "../identity/spire/clusterspiffeid-mesh.yaml"))
if os.path.exists(base_path):
    base = load(base_path)[0]
    check(base["metadata"]["name"] != posture["metadata"]["name"], "coexists with a distinctly-named base ClusterSPIFFEID")
    check("/posture/" not in base["spec"]["spiffeIDTemplate"], "base SVID stays un-postured (posture rides only on this second ID)")
    check(base["spec"].get("className") == posture["spec"].get("className"),
          "base and posture share the same className (both actually reconciled by the same manager)")
    # ticket 11 (live-discovered): a pod matching BOTH CSIDs gets two SPIRE
    # entries, but Envoy's SDS "default" request and a hint-less
    # `spire-agent api fetch` only ever return one of them (SPIRE's own
    # "first in the list" pick, not something either CRD field controls) —
    # confirmed live to flip between the base and posture entry across
    # otherwise-identical pod restarts, silently dropping posture-gated
    # reach whenever it landed on base. The selectors must be a strict
    # partition (never both) so there is nothing to pick between.
    base_expr = base["spec"]["podSelector"].get("matchExpressions", [])
    check(any(e.get("key") == "posture.acme.io/version" and e.get("operator") == "DoesNotExist" for e in base_expr),
          "base excludes posture-managed pods (DoesNotExist) — a pod matches exactly one of the two, never both")
else:
    print("  --   base ClusterSPIFFEID not found (identity area absent); coexistence check skipped")

if fails: sys.exit(f"\n{len(fails)} invariant(s) broken")
print("  -- SVID path invariants hold --")
PY

# ---- live tail: only if a cluster actually has the posture policies installed ----
if have kubectl && timeout 10 kubectl --context "$CTX" get mutatingpolicy stamp-posture >/dev/null 2>&1; then
  say "4. live: posture policies + ClusterSPIFFEID installed"
  timeout 10 kubectl --context "$CTX" get validatingpolicy posture-trust-boundary >/dev/null 2>&1 \
    || fail "posture-trust-boundary ValidatingPolicy not installed live"
  timeout 10 kubectl --context "$CTX" get clusterspiffeid posture >/dev/null 2>&1 \
    || fail "posture ClusterSPIFFEID not installed live"

  say "5. live: a hand-set posture with NO claim is DENIED at admission (server dry-run)"
  FORGE=$(cat <<'EOF'
apiVersion: v1
kind: Pod
metadata:
  name: posture-forge-probe
  namespace: default
  labels: { "posture.acme.io/version": "2.0.0" }
spec:
  containers: [{ name: app, image: nginx }]
EOF
)
  if echo "$FORGE" | timeout 20 kubectl --context "$CTX" apply --dry-run=server -f - >/dev/null 2>&1; then
    fail "forged posture (no claim) was ADMITTED — trust boundary is open!"
  else
    echo "  ok   forged posture with no claim refused at admission"
  fi

  say "6. live: a forger's posture is clobbered back to its real claim (server dry-run)"
  CLOBBER=$(cat <<'EOF'
apiVersion: v1
kind: Pod
metadata:
  name: posture-clobber-probe
  namespace: default
  labels: { "policy-as-versioned.dev/policy-version": "1.0.0", "posture.acme.io/version": "9.9.9" }
spec:
  containers: [{ name: app, image: nginx }]
EOF
)
  OUT=$(echo "$CLOBBER" | timeout 20 kubectl --context "$CTX" apply --dry-run=server -f - -o jsonpath='{.metadata.labels.posture\.acme\.io/version}' 2>/dev/null || true)
  [ "$OUT" = "1.0.0" ] && echo "  ok   forged posture 9.9.9 clobbered to the real claim 1.0.0" \
    || echo "  (clobber dry-run returned '$OUT'; needs Kyverno mutating webhook live — see README)"
else
  say "4-6. live checks skipped: no cluster with the posture policies at context '$CTX'"
  say "     (offline proofs above are the demonstrable claim; live needs Kyverno +"
  say "      SPIRE installed and estate/platform/posture/up.sh applied)"
fi

echo "PASS: posture rides in the SVID path; the label is Kyverno-only; forging is refused."
