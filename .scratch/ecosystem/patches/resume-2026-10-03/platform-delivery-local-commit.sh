#!/usr/bin/env bash
set -euo pipefail
cd /Users/cns/httpdocs/controlplane/policy-as-versioned-flux/.estate-publish/platform
git diff --cached --check
git commit -m 'Prepare security policy 6.0.0 and ecosystem tooling' -m 'Carry reviewed composition, engine, inventory and defensive cloud changes. Keep compatibility policy 7.0.0 frozen but undeclared until the security policy 6.0.0 cut completes; preserve the existing 5.0.0 line.'
git rev-parse HEAD
