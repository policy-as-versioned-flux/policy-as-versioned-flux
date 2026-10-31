# Tiny native Linux lease control — source only

This harness has not been installed or executed. No Linux target capacity,
privileged helper behavior, actual denial, teardown, Qwen runtime, qualification
or permission follows from its portable tests. Actual execution and installation
require independent source review and a separate bounded assignment. No workflow
is changed by this source.

The fixed `linux_lease_control_entry` accepts one of `baseline`, `boundaries`,
`resources`, `supervisor-loss`, `guardian-loss`, `invalid-evidence`. It launches
literal `/usr/bin/python3.12 -B -I -S` under a cleaned environment into the fixed
root-installed source at `/var/lib/policy-as-versioned-flux-linux-control/source/`.
It exposes no executable, Python payload, UID, path, controller, cap, callback or
command parameter. Existing broader administrator authority is not described as
a narrow sudoers grant. No accounts, controllers, services or infrastructure are
created. This document is not an installation or execution instruction.

The root-owned fixed `host.json` anchor has exactly `schema` and `files`. The
schema is `TEST_ONLY-linux-lease-control/v1`. Each file row has `source`, `target`,
`sha256`, `bytes`, `elf`; `elf` is null for non-ELF, otherwise actual `interpreter`
and `needed` metadata. Both are derived again from actual bytes without running
ldd. The explicit actual closure is bounded to 4096 files/256MiB, contains the
root-owned OS `/usr/bin/python3.12`, its actual standard-library/native closure,
the fixed launcher and the six named source modules. Canonical protected paths,
ACLs, modes, no privilege bits, single-link files, backing inodes, current native
mappings and hashes are checked. Missing/ambiguous/mutable closure refuses; there
is no guessed dependency list, runtime install or fake Qwen asset/manifest. Any
future protected copying/installation needs its own reviewed source wiring.

Actual prerequisites include native Linux64 little endian x86_64/aarch64, an
original nonroot caller derived from stable protected ancestry, an existing
unaliased unused `nobody` UID/GID distinct from root/caller, an inaccessible or
nonexistent home, and protected pre-enabled memory/cpu/cpuset/pids controllers
under the fixed `/sys/fs/cgroup/policy-as-versioned-flux-linux-control` parent.
The ancestry check permits only the canonical protected `/usr/bin/sudo` launcher
to retain setuid; candidate closure validation still rejects all privilege bits.
Require two actual eligible CPUs, 14GiB initial effective host/ancestor headroom,
2GiB recurring reserve outside the 12GiB leaf, and 5GiB on protected backing
storage. Unavailable facts produce explicit refusal/SKIP (77), never PASS, another
identity, controller enabling, a new target or an RSS fallback. The private
read-only file closure/proc namespace and fd closure exclude unrelated host
objects; this is not a global absence-of-nobody-owned-files claim.

`LeaseMechanics` supplies the same production Leaf/Child/bootstrap/READY,
backing-inode mapping, sample and teardown implementations. Production Guardian
still first validates exactly its six reviewed BF16 profiles; production parent
and child validators reject the TEST_ONLY descriptor. Control construction is a
separate fixed source function, never a production config branch. No Actor,
selection, acquired model/runtime, catalogue registration or model RuntimeResult
is issued. Changes to the shared guardian source stale its former source pins;
actual future captures must bind the new exact bytes.

Each attempt has an earlier finite 60s ceiling including its final 10s cleanup;
the deadline subcase tightens it to 30s. All subcases share an earlier finite 900s
outer ceiling. Setup, hashing, phase switching, sampling and cleanup cannot reset
these clocks. These are engineering ceilings, not observed throughput.

The foreground root observer pins its own fork custody, becomes a child
subreaper, and creates an unrelated sentinel under the actual caller UID outside
the leaf. A fixed private bootstrap first reports the newly forked root guardian,
waits for an outer acknowledgment, then drops the fixture supervisor to the exact
caller before strict supervisor Identity is constructed and before guardian
release. Only a raw kernel handle over that direct owned fork is retained for
pre-snapshot failure cleanup; production supervisor Identity retains strict UID
semantics. The sole production credential-transition exception remains the
trusted namespace ChildIdentity. Root/caller identities are never selected by
JSON or environment assertions.

Typed trusted pipes stop only at raw clone, attach, final drop before rearm,
after rearm, actual READY and actual detached-descendant handoffs. Guardian death
is checked before early arm and on both sides of release, including the UID-drop
window. All extra child handles close before exec. No candidate packet appoints
a privileged callback. The outer observer independently observes live leaf
membership/session/start identity before loss; it signals only owned pinned
pidfds. A separate private terminal acknowledgment lets it independently read
empty/dead/reaped state before the guardian removes the leaf, including after
supervisor loss. Missing/partial observer evidence fails closed.

The six actual scenario routes are:

1. Two fresh private children, observed preflight empty/reaped before generation,
   exact limits/mounts/caps/native/source receipts and final removal.
2. Actual root/config/source/evidence/cgroup write attempts, UID/group/capability
   recovery, mount/namespace/death-signal changes, ptrace/process-memory/fd import,
   private host-proc absence, unchanged source bytes, all eight distinct network
   EPERM probes and the same probes after fresh exec of the exact tiny child.
3. Original exact 12GiB/no-swap/128PID/two-CPU READY, effective affinity after a
   full-host mask request, 128MiB tmpfs ENOSPC and genuine ELF noexec EACCES. Two
   separate TEST_ONLY subcases tighten only their own already-READY leaf to 32MiB
   or eight PIDs, retain bad samples/aborted production accounting, and require
   independently read actual OOM/pids kernel events. Tiny allocation proves no
   full model memory viability; production limits are unchanged.
4. Supervisor SIGKILL while actual namespace init and a detached setsid descendant
   live; guardian survival, actual cleanup and unchanged sentinel.
5. Guardian SIGKILL at each fixed handoff; automatic init/descendant death must be
   observed before backup cleanup. Missing guardian terminal remains a refused
   production capture even if independent outer recovery completes.
6. Actual control EOF, deadline, duplicate READY, denied source writes, frame
   overflow, a fixed host sampler-fd fault, deliberately incomplete post-capture
   cleanup evidence and an exclusive owned stale identity lock. Failures/raw
   bytes persist; a kill request or partial receipt cannot pass.

Protected attempt journals and immutable result files retain actual raw frames,
source/anchor/closure/native identities, measured deadlines, denials, kernel
counters, custody and terminal witnesses. The strict reader requires every exact
subcase in order and checks each one's own terminal, sentinel and outer cleanup
witnesses before the aggregate. Expected terminal absence must be explicitly
recorded and is confined to guardian loss and the fixed sampler-fd fault.
SKIP/unexecuted/missing/partial evidence cannot pass.
`production_capture_accepted` is always false. The actual existing Linux matrix
route, target suitability and eventual artifact collection remain separate
reviewed work; no workflow dispatch or provider action is implied.

An observed rejection of the existing CI `nobody` identity remains a failure.
The CI-only diagnostic retains the original account/group/home observations in
the protected `suite/principal.json` refusal record before exporting that failed
outcome. It does not select another account, relax the principal predicate, or
turn unsafe identity into neutral absence. A changed/unproved caller or an
unretained observation still prevents a complete diagnostic export. The ordinary
production principal route retains its existing rejection behavior.
