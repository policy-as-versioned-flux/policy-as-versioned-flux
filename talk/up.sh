#!/usr/bin/env bash
# Bring the talk estate up for a venue run. Idempotent, audience-modular. This
# is a THIN orchestrator over the per-area up.sh scripts each ticket already
# shipped — it sequences them in dependency order and guards the CLIs. It
# never creates/deletes a cluster itself; the institution up.sh does that, and
# reuses an existing KinD cluster of the same name if one is already there.
#
# Post-split (mo-12): the six units below are real, separate GitHub repos, not
# sibling directories of this hub. clone-estate.sh fetches them into
# .estate-clone/ first (network required — see RUNBOOK.md "Internet is now
# assumed"), then this script runs their up.sh scripts exactly as before.
#
#   talk/up.sh              # driftwood (teaching default) + the platform
#                            # layers that carry every live beat
#   talk/up.sh tuppence     # + foreground the fintech room (its cluster)
#   talk/up.sh ludlow       # + foreground the health room (its cluster)
#   talk/up.sh all          # all three institution clusters (beefy laptop)
#   talk/up.sh foreground <inst>   # zero-rebuild re-foreground (kubectx)
#
# Nothing here waits indefinitely: each area's up.sh is already timeout-bounded,
# and a degraded layer (slow/absent image) is reported and stepped over, not hung
# on. Re-run any time to converge.
set -u
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
CLONE="$ROOT/.estate-clone"
say()  { echo; echo "==> $*"; }
warn() { echo "  ! $*" >&2; }
need() { command -v "$1" >/dev/null || { echo "MISSING cli: $1" >&2; exit 1; }; }

ctx_of() { echo "kind-$1"; }
foreground() { # <institution> — zero rebuild, just point the room at it
  local inst="$1" ctx; ctx="$(ctx_of "$inst")"
  if kubectl config get-contexts -o name 2>/dev/null | grep -qx "$ctx"; then
    kubectl config use-context "$ctx" >/dev/null && say "foregrounded $inst ($ctx)"
    echo "   narrate: $inst — see talk/RUNBOOK.md 'Audience-modular'"
  else
    warn "$inst cluster not up yet; run: talk/up.sh $inst"
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

need kind; need kubectl; need git

MODE="${1:-driftwood}"

if [ "$MODE" = foreground ]; then foreground "${2:-driftwood}"; exit 0; fi

say "assembling the six real units into .estate-clone/ (needs network)"
bash "$ROOT/clone-estate.sh" || { warn "clone-estate.sh failed — no network? nothing below can run without it"; exit 1; }

# --- base: driftwood cluster carries every platform layer & every live beat ----
step "driftwood: KinD + Flux + signed source + reconcile" "$CLONE/driftwood/scripts/up.sh"

# --- platform layers on the driftwood cluster (dependency order) ---------------
# identity substrate first (SPIRE/Istio/OpenBao), then the engine (Kyverno +
# flux-operator) the posture policies need, then everything that rides both.
step "platform: identity substrate (SPIRE+Istio+OpenBao)" "$CLONE/platform/identity/up.sh"
step "platform: engine (Kyverno + flux-operator)"     "$CLONE/platform/engine/up.sh"
step "platform: posture projection (posture/vN in SVID path)" "$CLONE/platform/posture/up.sh"
step "platform: graded enforcement envelope (cages)" "$CLONE/platform/graded/up.sh"
# after graded, not before it (eco-system ticket 91): the controller re-cages a
# stale pod into the `isolated` rung, so without cage-tier and cage-netpol on
# the cluster there is no ladder to re-cage into and no NetworkPolicy to hold
# the result -- the patch would land and mean nothing.
step "platform: currency controller (post-admission re-cage)" "$CLONE/platform/currency-controller/up.sh"
step "platform: human/device access plane (Pomerium)" "$CLONE/platform/access/up.sh"
step "platform: EUD local prep (vTPM, offline)"      "$CLONE/platform/eud/up.sh"
# tuppence workload flagship (customer-accounts-reset) rides the driftwood substrate
step "tuppence: workload flagship (reach+secrets)"   "$CLONE/tuppence/reset/up.sh"

# --- other institutions (own clusters) — only when the room needs them ----------
case "$MODE" in
  driftwood) : ;;                                  # base is enough for the live beats
  tuppence)  step "tuppence: institution cluster" "$CLONE/tuppence/scripts/up.sh" ;;
  ludlow)    step "ludlow: institution cluster"   "$CLONE/ludlow/scripts/up.sh" ;;
  all)
    step "tuppence: institution cluster" "$CLONE/tuppence/scripts/up.sh"
    step "ludlow: institution cluster"   "$CLONE/ludlow/scripts/up.sh" ;;
  *) warn "unknown target '$MODE' (driftwood|tuppence|ludlow|all|foreground <inst>)"; exit 1 ;;
esac

foreground "${MODE/all/driftwood}"
say "estate up. Assert every beat:  talk/verify-all.sh"
echo "   (add --live once clusters are reconciled to include the reconcile beats)"
