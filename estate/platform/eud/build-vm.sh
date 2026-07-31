#!/usr/bin/env bash
# build-vm.sh — idempotent, OFFLINE prep for the two UTM vTPM EUDs (Windows 11,
# Linux). Reads vms/<name>.json, creates the qcow2 disk + swtpm state dir (fast,
# local, no network, no boot), and prints the exact qemu-system-x86_64 + swtpm
# invocation a human runs at the venue to actually boot/install the OS — that
# step needs an ISO + GUI install, so it is a venue step, never run here.
#
# Import the resulting disk into UTM (New VM > Virtualize/Emulate > Existing
# Image) for the GUI, or run headless with the printed qemu command — both use
# the same disk + swtpm socket, so both get the SAME vTPM identity.
set -euo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
STATE="$HERE/state"
say() { printf '\033[1;36m==>\033[0m %s\n' "$*"; }

command -v qemu-img >/dev/null || { echo "MISSING cli: qemu-img (brew install qemu)" >&2; exit 1; }

for spec in "$HERE"/vms/*.json; do
  name=$(python3 -c "import json,sys; print(json.load(open(sys.argv[1]))['name'])" "$spec")
  disk_gib=$(python3 -c "import json,sys; print(json.load(open(sys.argv[1]))['disk_gib'])" "$spec")
  tpm_dir=$(python3 -c "import json,sys; print(json.load(open(sys.argv[1]))['tpm']['state_dir'])" "$spec")

  disk="$STATE/$name.qcow2"
  tpmstate="$HERE/$tpm_dir"
  mkdir -p "$(dirname "$disk")" "$tpmstate"

  if [ -f "$disk" ]; then
    say "$name: disk already exists ($disk) — idempotent, skipping create"
  else
    say "$name: creating ${disk_gib}GiB qcow2 disk"
    qemu-img create -f qcow2 "$disk" "${disk_gib}G" >/dev/null
  fi

  say "$name: venue commands (run these, not this script, to boot)"
  cat <<EOF
  # 1. start the emulated TPM (mints its own EK on first run — the emulated-EK caveat)
  swtpm socket --tpmstate dir=$tpmstate \\
    --ctrl type=unixio,path=$tpmstate/swtpm-sock \\
    --tpm2 --daemon

  # 2. boot the VM with the vTPM attached (UTM's GUI does this under the hood
  #    when you enable "Trusted Platform Module" in a VM's System settings —
  #    import $disk there for the GUI path)
  qemu-system-x86_64 -m $(python3 -c "import json;print(json.load(open('$spec'))['memory_mib'])") \\
    -smp $(python3 -c "import json;print(json.load(open('$spec'))['cpu'])") \\
    -drive file=$disk,if=virtio \\
    -chardev socket,id=chrtpm,path=$tpmstate/swtpm-sock \\
    -tpmdev emulator,id=tpm0,chardev=chrtpm -device tpm-tis,tpmdev=tpm0 \\
    -cdrom "\$ISO_PATH" -boot d
EOF
  echo
done

command -v swtpm >/dev/null || echo "NOTE: swtpm not installed here (brew install swtpm) — the venue commands above need it; disk/state prep above is unaffected."
say "done — disks + swtpm state dirs prepared under $STATE (offline, idempotent). Actual OS install/enrolment is a venue step (see README.md)."
