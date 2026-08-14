#!/usr/bin/env bash
# The forced-drift latency campaign (build ticket 78).
#
# Runs the four trials declared in `forced-campaign.yaml` — a manual ConfigMap edit outside
# GitOps, a kubectl scale left unreverted, a suspended Kustomization left suspended, and an
# outright resource delete — against the real kind-driftwood cluster, one at a time. After each
# action it samples the cluster every 15 seconds for 30 minutes, using the same unmodified
# `probe.sh` build ticket 64's passive probe calls, so both logs share one sample shape and this
# campaign never edits or depends on ticket 64's own crontab.
#
# This script is the executable form of `forced-campaign.yaml`'s `trials:` list. The two must
# name the same four trial ids — `tests/test_drift.py::test_the_orchestrator_script_runs_exactly_the_declared_trials`
# checks that they do.
#
# Run by hand, holding the kind-driftwood context. Not cron: a bounded, roughly two-hour run
# started deliberately once (see forced-campaign.yaml's `operation`), not a standing probe.
set -uo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CTX="${DRIFT_CONTEXT:-kind-driftwood}"
OUT="${FORCED_CAMPAIGN_SAMPLES:-$HERE/forced-campaign-samples.jsonl}"
PROBE="$HERE/probe.sh"

# Must match forced-campaign.yaml's `resolution:`.
SAMPLE_EVERY_SECONDS=15
WINDOW_MINUTES=30
# Refuse to start a trial with less runway than this before the next hour boundary. A trial takes
# action + 30 minutes of sampling + undo + verify, comfortably under an hour; the margin exists so
# a trial never leaves the cluster divergent when build ticket 64's hourly cron probe fires —
# that would record a forced mechanism event as if it were organic drift.
SAFETY_MARGIN_MINUTES=40

kc() { kubectl --context "$CTX" --request-timeout=20s "$@"; }

log() { printf '%s %s\n' "$(date -u +%FT%TZ)" "$1" >&2; }

minutes_to_next_hour() {
  local min_now secs_now
  min_now="$(date -u +%-M)"
  secs_now="$(date -u +%-S)"
  echo $(( 59 - min_now + (60 - secs_now) / 60 ))
}

wait_for_safe_start_window() {
  while [ "$(minutes_to_next_hour)" -lt "$SAFETY_MARGIN_MINUTES" ]; do
    log "waiting for a safe start window (need >= ${SAFETY_MARGIN_MINUTES}m before the next hour)"
    sleep 60
  done
}

sample_for_window() {
  local end
  end=$(( $(date -u +%s) + WINDOW_MINUTES * 60 ))
  while [ "$(date -u +%s)" -lt "$end" ]; do
    DRIFT_SAMPLES="$OUT" DRIFT_CONTEXT="$CTX" "$PROBE"
    sleep "$SAMPLE_EVERY_SECONDS"
  done
}

# $1 id, $2 action, $3 undo, $4 baseline check (a shell test expression, true when the cluster is
# at declared-state baseline).
run_trial() {
  local id="$1" action="$2" undo="$3" verify="$4"

  log "trial $id: verifying baseline before starting"
  if ! eval "$verify"; then
    log "trial $id: baseline check failed before the trial started; aborting campaign untouched"
    exit 1
  fi

  wait_for_safe_start_window

  log "trial $id: applying the forced action"
  eval "$action"

  log "trial $id: sampling every ${SAMPLE_EVERY_SECONDS}s for ${WINDOW_MINUTES}m -> $OUT"
  sample_for_window

  log "trial $id: applying the pre-recorded undo"
  eval "$undo"

  log "trial $id: verifying baseline restored"
  if ! eval "$verify"; then
    log "trial $id: baseline NOT restored after undo; halting the campaign rather than starting the next trial on a cluster already known to be wrong"
    exit 1
  fi
  log "trial $id: complete, baseline restored"
}

run_trial "configmap-edit-outside-gitops" \
  'kc -n driftwood patch configmap driftwood-live-version --type merge -p "{\"data\":{\"policyVersion\":\"FORCED-DRIFT-TEST\"}}"' \
  'kc -n driftwood patch configmap driftwood-live-version --type merge -p "{\"data\":{\"policyVersion\":\"1.0.0\"}}"' \
  '[ "$(kc -n driftwood get cm driftwood-live-version -o jsonpath="{.data.policyVersion}" 2>/dev/null)" = "1.0.0" ]'

run_trial "scale-left-unreverted" \
  'kc -n flux-system scale deployment git-server --replicas=0' \
  'kc -n flux-system scale deployment git-server --replicas=1 && kc -n flux-system rollout status deployment git-server --timeout=60s' \
  '[ "$(kc -n flux-system get deployment git-server -o jsonpath="{.status.availableReplicas}" 2>/dev/null)" = "1" ]'

run_trial "kustomization-suspended-left-suspended" \
  'kc -n flux-system patch kustomization driftwood --type merge -p "{\"spec\":{\"suspend\":true}}"' \
  'kc -n flux-system patch kustomization driftwood --type merge -p "{\"spec\":{\"suspend\":false}}"' \
  '[ "$(kc -n flux-system get kustomization driftwood -o jsonpath="{.spec.suspend}" 2>/dev/null)" != "true" ]'

run_trial "resource-deleted-outright" \
  'kc -n driftwood delete configmap driftwood-nist-pin' \
  'for i in $(seq 1 30); do kc -n driftwood get cm driftwood-nist-pin >/dev/null 2>&1 && break; sleep 10; done' \
  '[ "$(kc -n driftwood get cm driftwood-nist-pin -o jsonpath="{.data.catalogVersion}" 2>/dev/null)" = "1.0.0" ]'

log "forced-drift latency campaign complete: $OUT"
