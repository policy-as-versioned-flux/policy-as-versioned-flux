#!/usr/bin/env bash
# Assert the EUD beat's structural invariants hold, offline. Two layers:
#   OFFLINE (always) — VM specs parse and declare vTPM 2.0; the tpm-devid
#     template renders a ClusterStaticEntry on the SAME acme.internal root as
#     ticket 18's operator-macbook-device; the access decision engine still
#     refuses a device-SVID-less caller (WHfB-only ≠ device trust).
#   LIVE (best-effort) — qemu-img/swtpm/utmctl presence, driftwood device-SVID
#     entries if the plane is already up. Never blocks; nothing waits.
set -euo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CTX="${CTX:-kind-driftwood}"

echo "== offline: VM specs =="
python3 - "$HERE" <<'PY'
import json, sys, os
root = sys.argv[1]
fails = []
def check(cond, msg):
    print(("  ok   " if cond else "  FAIL ") + msg)
    if not cond: fails.append(msg)

for name in ("windows11-vtpm.json", "linux-vtpm.json"):
    spec = json.load(open(os.path.join(root, "vms", name)))
    check(spec.get("tpm", {}).get("version") == "2.0", f"{name}: TPM 2.0 declared")
    check(spec.get("tpm", {}).get("backend") == "swtpm", f"{name}: swtpm backend (emulated EK, named honestly)")
    check("narration" in spec and "virtual" in spec["narration"], f"{name}: narrated as virtual")
    check(spec.get("disk_gib", 0) > 0 and spec.get("memory_mib", 0) > 0, f"{name}: sane disk/memory sizing")

if fails:
    sys.exit(f"{len(fails)} invariant(s) broken")
print("  -- VM specs hold --")
PY

echo "== offline: tpm-devid enrolment template renders on the ONE estate root =="
python3 - "$HERE" <<'PY'
import subprocess, sys, os
try:
    import yaml
except ImportError:
    sys.exit("PyYAML not available; `pip install pyyaml` to run this check")
root = sys.argv[1]
fails = []
def check(cond, msg):
    print(("  ok   " if cond else "  FAIL ") + msg)
    if not cond: fails.append(msg)

for eud in ("windows11-eud", "linux-eud"):
    out = subprocess.run([os.path.join(root, "tpm-devid-enroll.sh"), eud], capture_output=True, text=True, check=True).stdout
    doc = yaml.safe_load(out)
    check(doc["kind"] == "ClusterStaticEntry", f"{eud}: renders a ClusterStaticEntry")
    sid = doc["spec"]["spiffeID"]
    check(sid == f"spiffe://acme.internal/device/{eud}", f"{eud}: device SVID on the ONE estate root ({sid})")
    check(any(str(s).startswith("tpm_devid:") for s in doc["spec"]["selectors"]),
          f"{eud}: pinned to a tpm_devid selector, same mechanism as ticket 18's operator-macbook-device")

if fails:
    sys.exit(f"{len(fails)} invariant(s) broken")
print("  -- tpm-devid templates hold --")
PY

echo "== offline: WHfB alone does not buy device trust (access.py reused, not re-implemented) =="
"$HERE/../access/access.py" selfcheck
python3 - "$HERE" <<'PY'
import sys, importlib.util
spec = importlib.util.spec_from_file_location("access", __import__("os").path.join(__import__("sys").argv[1], "..", "access", "access.py"))
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
d, why = mod.decide("break-glass", oidc=True, webauthn=True, device_svid=False)
assert d == "DENY", (d, why)
print("  ok   a Windows EUD with WHfB but no device SVID is refused break-glass:", why)
PY

echo "== offline: build-vm.sh is idempotent-safe (dry structure check, no boot) =="
grep -q 'qemu-img create' "$HERE/build-vm.sh" && echo "  ok   build-vm.sh creates disks via qemu-img (no boot/install attempted)"

for c in qemu-img swtpm utmctl; do
  if command -v "$c" >/dev/null 2>&1; then echo "  info $c available"; else echo "  info $c NOT installed (venue prereq; offline checks above don't need it)"; fi
done

echo "== live: driftwood device SVIDs (best-effort, bounded) =="
if command -v kubectl >/dev/null && timeout 10 kubectl --context "$CTX" get ns spire-system >/dev/null 2>&1; then
  for eud in windows11-eud linux-eud; do
    timeout 10 kubectl --context "$CTX" get clusterstaticentry "${eud}-device" >/dev/null 2>&1 \
      && echo "  ok   ${eud}-device SVID applied" \
      || echo "  (not applied yet — venue step: tpm-devid-enroll.sh $eud <fingerprint> | kubectl apply -f -)"
  done
else
  echo "  (identity substrate not reachable; skipped — offline checks above are the ones that must pass)"
fi
echo "verify-eud: done"
