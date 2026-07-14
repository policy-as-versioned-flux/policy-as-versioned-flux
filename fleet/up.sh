#!/usr/bin/env bash
# One documented command sequence: laptop -> KiND cluster with Flux Operator
# (FluxInstance, ADR-0005) + Kyverno engine (>=1.18, ADR-0003) healthy (issue
# 05). Idempotent -- safe to re-run. Readiness is gated throughout by native
# `kubectl wait` on Ready conditions, never a jsonpath polling loop. CEL
# `healthCheckExprs` (the other half of "wait + CEL health checks") is a Flux
# Kustomization field -- nothing here goes through one yet, since there's no
# GitOps source to sync from until issue 06 wires in the real policy repo.
#
# Prereqs: docker, kind, kubectl, helm. ~3-5 min from cold (varies with image pull speed).
set -euo pipefail
cd "$(dirname "$0")"
CLUSTER=cluster1

echo "== 1. KiND cluster =="
kind get clusters 2>/dev/null | grep -qx "$CLUSTER" || kind create cluster --name "$CLUSTER" --wait 120s

echo "== 2. Flux Operator =="
helm upgrade --install flux-operator oci://ghcr.io/controlplaneio-fluxcd/charts/flux-operator \
  --version 0.55.0 --namespace flux-system --create-namespace --wait --timeout 3m >/dev/null

echo "== 3. FluxInstance (pinned Flux 2.9.2, upstream-alpine) =="
kubectl apply -f flux-instance.yaml >/dev/null
kubectl -n flux-system wait --for=condition=Ready fluxinstance/flux --timeout=5m

echo "== 4. Kyverno engine via a pinned HelmRelease =="
kubectl apply -f infrastructure/kyverno/namespace.yaml >/dev/null
kubectl apply -f infrastructure/kyverno/ >/dev/null
kubectl -n kyverno wait --for=condition=Ready helmrelease/kyverno --timeout=5m

echo "== OK: KiND cluster '$CLUSTER' has Flux Operator + Kyverno healthy =="
kubectl -n kyverno get deploy
