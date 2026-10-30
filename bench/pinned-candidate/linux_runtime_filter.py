"""Additional irreversible runtime confinement, installed only by trusted dropped bootstrap.

This complements unchanged linux_network.py; importing/building never installs a filter.
Syscall ABI: Linux v6.16 arch/x86/entry/syscalls/syscall_64.tbl and
include/uapi/asm-generic/unistd.h (https://github.com/torvalds/linux/tree/v6.16).
Native Linux x86_64/aarch64 only; no compat/x32 or unreviewed future syscall ABI.
"""
from __future__ import annotations

import ctypes
import hashlib
import json
import os
from pathlib import Path
import platform
import signal
import sys
from typing import Any

DENY = 0x00050001  # SECCOMP_RET_ERRNO | EPERM
ENOSYS = 0x00050026
ALLOW = 0x7fff0000
KILL = 0x80000000


def runtime_filter(machine: str) -> list[tuple[int, int, int, int]]:
    """Build the pinned cBPF policy without executing privileged/native operations."""
    denied: tuple[int, ...]
    if machine == 'x86_64':
        architecture, clone, prctl = 0xc000003e, 56, 157
        denied = (101, 155, 161, 163, 165, 166, 167, 168, 169, 170, 171, 175, 176,
            179, 246, 248, 249, 250, 272, 298, 300, 303, 304, 308, 310, 311, 312,
            313, 320, 321, 323)
    elif machine == 'aarch64':
        architecture, clone, prctl = 0xc00000b7, 220, 167
        denied = (39, 40, 41, 51, 60, 89, 97, 104, 105, 106, 117, 142, 161, 162,
            217, 218, 219, 224, 225, 241, 262, 264, 265, 268, 270, 271, 272, 273,
            280, 282, 294)
    else:
        raise ValueError('unsupported native runtime filter architecture')
    # New namespace/mount/control APIs share native numbers. pidfd_open remains
    # usable for bootstrap liveness, but pidfd_getfd cannot reach foreign handles.
    denied += (425, 426, 427, 428, 429, 430, 431, 432, 433, 438, 442, 457, 460, 467)
    program = [(0x20, 0, 0, 4), (0x15, 1, 0, architecture), (0x06, 0, 0, KILL),
        (0x20, 0, 0, 0), (0x45, 0, 1, 0x40000000), (0x06, 0, 0, KILL),
        (0x35, 0, 1, 468), (0x06, 0, 0, ENOSYS),
        (0x15, 0, 1, 435), (0x06, 0, 0, ENOSYS)]
    for number in denied:
        program.extend([(0x15, 0, 1, number), (0x06, 0, 0, DENY)])
    # Legacy clone flags are inspectable. Refuse all new namespace bits and
    # nonzero high flags; ordinary pthread clone remains possible within cpuset.
    program.extend([(0x15, 0, 7, clone), (0x20, 0, 0, 20), (0x15, 1, 0, 0),
        (0x06, 0, 0, DENY), (0x20, 0, 0, 16), (0x45, 1, 0, 0x7e020000),
        (0x06, 0, 0, ALLOW), (0x06, 0, 0, DENY)])
    # Parent-death signal is rearmed after UID/GID changes and cannot subsequently
    # be cleared/replaced. PR_GET_PDEATHSIG remains available for actual readback.
    program.append((0x15, 0, 12, prctl))
    program.append((0x20, 0, 0, 16))
    for operation in (1, 8, 35, 36, 0x59616d61):
        program.extend([(0x15, 0, 1, operation), (0x06, 0, 0, DENY)])
    program.extend([(0x06, 0, 0, ALLOW), (0x06, 0, 0, ALLOW)])
    return program


class _Filter(ctypes.Structure):
    _fields_ = [('code', ctypes.c_ushort), ('jt', ctypes.c_ubyte),
                ('jf', ctypes.c_ubyte), ('k', ctypes.c_uint32)]


class _Program(ctypes.Structure):
    _fields_ = [('length', ctypes.c_ushort), ('filter', ctypes.POINTER(_Filter))]


def install_runtime_denial() -> dict[str, Any]:
    """Install only after trusted namespace setup/final drop/PDEATHSIG handoff.

    No source-only test calls this function. Actual native controls and root lease
    lifecycle evidence are prerequisites; a policy digest alone proves none of them.
    """
    if sys.platform != 'linux' or sys.byteorder != 'little' or ctypes.sizeof(ctypes.c_void_p) != 8:
        raise RuntimeError('requires native Linux64 little-endian trusted bootstrap')
    state = dict(line.split(':', 1) for line in Path('/proc/self/status').read_text().splitlines() if ':' in line)
    state = {key: value.strip() for key, value in state.items()}
    if (os.geteuid() == 0 or os.getgroups() or state['NoNewPrivs'] != '1'
            or any(int(state[key], 16) for key in ('CapEff', 'CapPrm', 'CapInh', 'CapAmb', 'CapBnd'))
            or len(list(Path('/proc/self/task').iterdir())) != 1):
        raise RuntimeError('requires final capability/credential drop and a single bootstrap thread')
    libc = ctypes.CDLL(None, use_errno=True)
    death = ctypes.c_int()
    if libc.prctl(2, ctypes.byref(death), 0, 0, 0) or death.value != signal.SIGKILL:
        raise RuntimeError('install only after the actual guardian death signal is armed')
    instructions = runtime_filter(platform.machine())
    array = (_Filter*len(instructions))(*(_Filter(*row) for row in instructions))
    program = _Program(len(instructions), array)
    if libc.prctl(22, 2, ctypes.byref(program), 0, 0):
        raise OSError(ctypes.get_errno(), 'runtime seccomp filter refused')
    current = dict(line.split(':', 1) for line in Path('/proc/self/status').read_text().splitlines() if ':' in line)
    if current['NoNewPrivs'].strip() != '1' or current['Seccomp'].strip() != '2':
        raise RuntimeError('runtime seccomp state not observed after installation')
    return {'policy': 'linux-runtime-confinement/v1', 'architecture': platform.machine(),
        'filter_sha256': hashlib.sha256(json.dumps(instructions, separators=(',', ':')).encode()).hexdigest()}
