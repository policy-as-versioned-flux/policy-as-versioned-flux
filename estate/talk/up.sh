#!/usr/bin/env bash
# Bring the talk estate up for a venue run. Idempotent, offline-safe, audience-
# modular. This is a THIN orchestrator over the per-area up.sh scripts each ticket
# already shipped — it sequences them in dependency order and guards the CLIs.
# It never creates/deletes a cluster itself; the institution up.sh does that, and
# reuses an existing KinD cluster of the same name if one is already there.
#
#   estate/talk/up.sh              # driftwood (teaching default) + the platform
#                                  # layers that carry every live beat
#   estate/talk/up.sh tuppence     # + foreground the fintech room (its cluster)
#   estate/talk/up.sh ludlow       # + foreground the health room (its cluster)
#   estate/talk/up.sh all          # all three institution clusters (beefy laptop)
#   estate/talk/up.sh foreground <inst>   # zero-rebuild re-foreground (kubectx)
#
# Nothing here waits indefinitely: each area's up.sh is already timeout-bounded,
# and a degraded layer (slow/absent image) is reported and stepped over, not hung
# on. Re-run any time to converge.
set -u
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
say()  { echo; echo "==> $*"; }
warn() { echo "  ! $*" >&2; }
need() { command -v "$1" >/dev/null || { echo "MISSING cli: $1" >&2; exit 1; }; }

ctx_of() { echo "kind-$1"; }
foreground() { # <institution> — zero rebuild, just point the room at it
  local inst="$1" ctx; ctx="$(ctx_of "$inst")"
  if kubectl config get-contexts -o name 2>/dev/null | grep -qx "$ctx"; then
    kubectl config use-context "$ctx" >/dev/null && say "foregrounded $inst ($ctx)"
    echo "   narrate: $inst — see estate/talk/RUNBOOK.md 'Audience-modular'"
  else
    warn "$inst cluster not up yet; run: estate/talk/up.sh $inst"
  fi
}

# step <label> <script> [args...] — run an area up.sh, never fatal on a degraded layer
step() {
  local label="$1"; shift
  local script="$1"; shift
  [ -x "$script" ] || { warn "$label: $script missing/!x — skipped"; return 0; }
  say "$label"
  if timeout 600 bash "$script" "$@"; then echo "   ok: $label"; else warn "$label degraded (re-run to converge)"; fi
}

need kind; need kubectl

MODE="${1:-driftwood}"

if [ "$MODE" = foreground ]; then foreground "${2:-driftwood}"; exit 0; fi

# --- base: driftwood cluster carries every platform layer & every live beat ----
step "driftwood: KinD + Flux + signed source + reconcile" "$ROOT/estate/driftwood/scripts/up.sh"

# --- platform layers on the driftwood cluster (dependency order) ---------------
# identity substrate first (SPIRE/Istio/OpenBao), then everything that rides it.
step "platform: identity substrate (SPIRE+Istio+OpenBao)" "$ROOT/estate/platform/identity/up.sh"
step "platform: posture projection (posture/vN in SVID path)" "$ROOT/estate/platform/posture/up.sh"
step "platform: currency controller"                 "$ROOT/estate/platform/currency-controller/up.sh"
step "platform: graded enforcement envelope (cages)" "$ROOT/estate/platform/graded/up.sh"
step "platform: human/device access plane (Pomerium)" "$ROOT/estate/platform/access/up.sh"
step "platform: EUD local prep (vTPM, offline)"      "$ROOT/estate/platform/eud/up.sh"
# tuppence workload flagship (customer-accounts-reset) rides the driftwood substrate
step "tuppence: workload flagship (reach+secrets)"   "$ROOT/estate/tuppence/reset/up.sh"

# --- other institutions (own clusters) — only when the room needs them ----------
case "$MODE" in
  driftwood) : ;;                                  # base is enough for the live beats
  tuppence)  step "tuppence: institution cluster" "$ROOT/estate/tuppence/scripts/up.sh" ;;
  ludlow)    step "ludlow: institution cluster"   "$ROOT/estate/ludlow/scripts/up.sh" ;;
  all)
    step "tuppence: institution cluster" "$ROOT/estate/tuppence/scripts/up.sh"
    step "ludlow: institution cluster"   "$ROOT/estate/ludlow/scripts/up.sh" ;;
  *) warn "unknown target '$MODE' (driftwood|tuppence|ludlow|all|foreground <inst>)"; exit 1 ;;
esac

foreground "${MODE/all/driftwood}"
say "estate up. Assert every beat:  estate/talk/verify-all.sh"
echo "   (add --live once clusters are reconciled to include the reconcile beats)"
