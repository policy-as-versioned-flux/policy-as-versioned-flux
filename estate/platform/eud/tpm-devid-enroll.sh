#!/usr/bin/env bash
# tpm-devid-enroll.sh — render a ClusterStaticEntry for ONE EUD, on the SAME
# acme.internal root ticket 18 wired for the operator's Mac (which has no TPM;
# see ../access/device/secure-enclave.md). This is that same pattern,
# parameterised per-EUD, for the Windows/Linux vTPM VMs this ticket builds.
#
# Usage: tpm-devid-enroll.sh <eud-name> [tpm-fingerprint]
#   tpm-devid-enroll.sh windows11-eud
#   tpm-devid-enroll.sh linux-eud SHA256:ab12cd34...   # after attesting
#
# With no fingerprint, prints a template with a REPLACE_ placeholder — same as
# ticket 18's device-svid.yaml before enrolment. The real fingerprint comes off
# the SPIRE server log the first time the VM's agent attempts tpm_devid
# attestation (a live step — needs the running VM + a live SPIRE server).
set -euo pipefail
name="${1:?usage: tpm-devid-enroll.sh <eud-name> [tpm-fingerprint]}"
fp="${2:-REPLACE_WITH_ATTESTED_TPM_FINGERPRINT}"

cat <<EOF
# Device SVID for EUD '$name' — same estate root as every workload SVID and as
# ticket 18's operator-macbook entry. Applyable as-is once \$fp is real
# (spire-controller-manager, already running from ticket 14, reconciles it).
apiVersion: spire.spiffe.io/v1alpha1
kind: ClusterStaticEntry
metadata:
  name: ${name}-device
spec:
  spiffeID: spiffe://acme.internal/device/${name}
  parentID: spiffe://acme.internal/spire/agent/tpm_devid/${name}
  selectors:
    - tpm_devid:fingerprint:${fp}
  x509SVIDTTL: 1h
  jwtSVIDTTL: 5m
EOF
