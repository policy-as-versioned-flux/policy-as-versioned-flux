#!/usr/bin/env bash
# Clean teardown of the cluster ./up.sh creates. Re-run ./up.sh to recreate.
set -euo pipefail
CLUSTER=cluster1
kind delete cluster --name "$CLUSTER"
