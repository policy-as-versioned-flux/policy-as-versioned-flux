#!/usr/bin/env bash
# One sample of driftwood's control state, appended to samples.jsonl (build ticket 64).
#
# Run it on a cadence — see `window.yaml` for the declared one and the crontab line. Every run
# appends exactly one JSON object on one line, and appends it whether or not the cluster answered.
#
# **A run that cannot reach the cluster still writes a sample**, marked `reachable: false`. That is
# the point rather than tidiness: an instrument that writes nothing when it fails produces a log
# indistinguishable from a stable estate, and "no drift observed" over a window that was mostly
# unsampled is not evidence of anything. `reduce.py` reports coverage from these.
#
# The sample is a fact, never a verdict. There is no drift field here and no pass/fail: a drift
# event is a *transition between two samples*, so it cannot be observed by one, and deciding what
# the transitions mean is build ticket 65.
set -uo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CTX="${DRIFT_CONTEXT:-kind-driftwood}"
NS="${DRIFT_NAMESPACE:-driftwood}"
OUT="${DRIFT_SAMPLES:-$HERE/samples.jsonl}"

# UTC, to the second. The interval arithmetic downstream is in seconds and a local-time stamp
# would put a one-hour step in the data twice a year.
now() { date -u +%Y-%m-%dT%H:%M:%SZ; }

# `kubectl` with a short deadline. Without one, an unreachable API server hangs the cron job and
# the next hour's sample never happens either — one outage would eat the whole window.
kc() { kubectl --context "$CTX" --request-timeout=20s "$@" 2>/dev/null; }

# The log is newline-delimited JSON, so a control character in a value would break the *line* and
# `twin/drift.py` would refuse the whole file. Values here are version strings and git revisions,
# and a cluster is authored by people — so control characters are stripped rather than escaped,
# and only backslash and quote are escaped. `tr` rather than a `sed` escape, because `\t` and `\n`
# in a sed pattern are a GNU extension and this runs on whatever the operator's machine has.
json_string() { printf '%s' "$1" | tr -d '\000-\037' | sed 's/\\/\\\\/g; s/"/\\"/g'; }

TS="$(now)"

if ! command -v kubectl >/dev/null 2>&1 || ! kc get ns kube-system >/dev/null; then
  printf '{"ts":"%s","reachable":false,"reason":"%s","subjects":{}}\n' \
    "$TS" "$(json_string "no kubectl, or context ${CTX} did not answer within the deadline")" >> "$OUT"
  exit 0
fi

# The deploy marker. A change to this between two samples is a deploy, and a divergence that
# follows one is a deploy rather than drift — which is exactly the distinction the spec's claim
# rests on.
REVISION="$(kc -n flux-system get kustomization driftwood -o jsonpath='{.status.lastAppliedRevision}')"
READY="$(kc -n flux-system get kustomization driftwood -o jsonpath='{.status.conditions[?(@.type=="Ready")].status}')"
SINCE="$(kc -n flux-system get kustomization driftwood -o jsonpath='{.status.conditions[?(@.type=="Ready")].lastTransitionTime}')"
SUSPENDED="$(kc -n flux-system get kustomization driftwood -o jsonpath='{.spec.suspend}')"

# Observed state, one field per subject in window.yaml. Absent reads as the empty string, which is
# a divergence from any non-empty desired value — a control that has been deleted is total drift
# and must not read as "unchanged".
LIVE_VERSION="$(kc -n "$NS" get cm driftwood-live-version -o jsonpath='{.data.policyVersion}')"
NIST_PIN="$(kc -n "$NS" get cm driftwood-nist-pin -o jsonpath='{.data.catalogVersion}')"
NAMESPACE="$(kc get ns "$NS" -o jsonpath='{.metadata.name}')"

printf '{"ts":"%s","reachable":true,"revision":"%s","ready":"%s","ready_since":"%s","suspended":"%s","subjects":{"driftwood-live-version":"%s","driftwood-nist-pin":"%s","driftwood-namespace":"%s"}}\n' \
  "$TS" \
  "$(json_string "$REVISION")" \
  "$(json_string "$READY")" \
  "$(json_string "$SINCE")" \
  "$(json_string "${SUSPENDED:-false}")" \
  "$(json_string "$LIVE_VERSION")" \
  "$(json_string "$NIST_PIN")" \
  "$(json_string "$NAMESPACE")" >> "$OUT"
