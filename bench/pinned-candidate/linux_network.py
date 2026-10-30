"""Install a Linux socket-denial filter in a dedicated, unprivileged child.

This is a network control, not a general process/filesystem sandbox or a model run.
No filter is installed on import. Install before threads/runtime imports, with no
inherited sockets or io_uring descriptors. The filter persists across fork/exec.
Kernel ABI references: https://www.kernel.org/doc/html/next/userspace-api/seccomp_filter.html
and Linux v6.16 include/uapi/{linux/{audit,seccomp}.h,asm-generic/unistd.h}.
"""
from __future__ import annotations

import argparse
import ctypes
import errno
import hashlib
import json
import os
from pathlib import Path
import platform
import socket
import subprocess
import sys
from typing import Any


class _Filter(ctypes.Structure):
    _fields_ = [('code', ctypes.c_ushort), ('jt', ctypes.c_ubyte),
                ('jf', ctypes.c_ubyte), ('k', ctypes.c_uint32)]


class _Program(ctypes.Structure):
    _fields_ = [('length', ctypes.c_ushort), ('filter', ctypes.POINTER(_Filter))]


def _profile() -> tuple[int, int, int]:
    if (sys.platform != 'linux' or ctypes.sizeof(ctypes.c_void_p) != 8
            or sys.byteorder != 'little'):
        raise RuntimeError('requires a native 64-bit Linux process')
    profiles = {'x86_64': (0xC000003E, 41, 53), 'aarch64': (0xC00000B7, 198, 199)}
    if platform.machine() not in profiles:
        raise RuntimeError('unsupported Linux syscall architecture')
    return profiles[platform.machine()]


def _state() -> dict[str, str]:
    return dict(line.split(':', 1) for line in Path('/proc/self/status').read_text().splitlines()
                if ':' in line)


def install_network_denial() -> dict[str, Any]:
    """Irreversibly constrain this child; refuse unsupported or unsafe launch state."""
    arch, socket_nr, pair_nr = _profile()
    before = {key: value.strip() for key, value in _state().items()}
    if os.geteuid() == 0 or any(int(before[key], 16) != 0
                              for key in ('CapEff', 'CapPrm', 'CapInh', 'CapAmb')):
        raise RuntimeError('requires an unprivileged Linux child without effective capabilities')
    if len(list(Path('/proc/self/task').iterdir())) != 1:
        raise RuntimeError('install before creating runtime threads')
    for entry in list(Path('/proc/self/fd').iterdir()):
        try:
            target = os.readlink(entry)
        except FileNotFoundError:  # the directory iterator's own descriptor has closed
            continue
        if target.startswith('socket:') or 'io_uring' in target:
            raise RuntimeError('inherited socket/io_uring descriptor refuses installation')
    # seccomp_data offsets: nr=0, arch=4. Validate ABI before interpreting syscall numbers.
    kill, denied, allow = 0x80000000, 0x00050000 | errno.EPERM, 0x7FFF0000
    instructions = [(0x20, 0, 0, 4), (0x15, 1, 0, arch), (0x06, 0, 0, kill),
                    (0x20, 0, 0, 0)]
    if arch == 0xC000003E:
        # x32 shares AUDIT_ARCH_X86_64. Refuse its bit and legacy 512..547 ABI aliases.
        instructions += [(0x35, 0, 2, 512), (0x35, 1, 0, 548), (0x06, 0, 0, kill),
                         (0x45, 0, 1, 0x40000000), (0x06, 0, 0, kill)]
    # No new sockets, socketpair, io_uring network operations, or imported remote descriptors.
    for number in (socket_nr, pair_nr, 425, 438):
        instructions += [(0x15, 0, 1, number), (0x06, 0, 0, denied)]
    instructions.append((0x06, 0, 0, allow))
    filters = (_Filter * len(instructions))(*(_Filter(*row) for row in instructions))
    program = _Program(len(filters), filters)
    libc = ctypes.CDLL(None, use_errno=True)
    libc.prctl.argtypes = [ctypes.c_int, ctypes.c_ulong, ctypes.c_ulong,
                          ctypes.c_ulong, ctypes.c_ulong]
    libc.prctl.restype = ctypes.c_int
    if libc.prctl(38, 1, 0, 0, 0) != 0:  # PR_SET_NO_NEW_PRIVS
        raise OSError(ctypes.get_errno(), 'cannot set no_new_privs')
    address = ctypes.cast(ctypes.pointer(program), ctypes.c_void_p).value
    if libc.prctl(22, 2, address, 0, 0) != 0:  # PR_SET_SECCOMP, SECCOMP_MODE_FILTER
        raise OSError(ctypes.get_errno(), 'cannot install network filter')
    return {'policy': 'linux-socket-denial/v1', 'architecture': platform.machine(),
            'filter_sha256': hashlib.sha256(bytes(filters)).hexdigest()}


def _probes() -> list[dict[str, Any]]:
    _, socket_nr, _ = _profile()
    observed = []
    for family, family_name in [(socket.AF_INET, 'ipv4'), (socket.AF_INET6, 'ipv6')]:
        for kind, kind_name in [(socket.SOCK_STREAM, 'tcp'), (socket.SOCK_DGRAM, 'udp')]:
            try:
                with socket.socket(family, kind):
                    pass
                actual_errno = 0
            except OSError as error:
                actual_errno = error.errno if error.errno is not None else -1
            observed.append({'probe': family_name + '/' + kind_name, 'errno': actual_errno})
    libc = ctypes.CDLL(None, use_errno=True)
    libc.syscall.restype = ctypes.c_long
    for name, number, args in [('raw-socket', socket_nr, (2, 1, 0)),
                               ('io-uring', 425, (0, 0)),
                               ('pidfd-getfd', 438, (-1, 0, 0))]:
        ctypes.set_errno(0)
        result = libc.syscall(ctypes.c_long(number), *args)
        observed.append({'probe': name, 'errno': ctypes.get_errno() if result == -1 else 0})
        if name == 'raw-socket' and result >= 0:
            os.close(result)
    try:
        left, right = socket.socketpair()
        left.close()
        right.close()
        actual_errno = 0
    except OSError as error:
        actual_errno = error.errno if error.errno is not None else -1
    observed.append({'probe': 'unix-socketpair', 'errno': actual_errno})
    return observed


def _observed() -> dict[str, Any]:
    record: dict[str, Any] = {
        'state': {key: _state()[key].strip() for key in ('NoNewPrivs', 'Seccomp')},
        'probes': _probes()}
    if record['state'] != {'NoNewPrivs': '1', 'Seccomp': '2'}:
        raise RuntimeError('kernel filter state not observed')
    if any(row['errno'] != errno.EPERM for row in record['probes']):
        raise RuntimeError('actual socket/syscall denial control failed: ' + json.dumps(record))
    return record


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument('--control', action='store_true')
    mode.add_argument('--probe', action='store_true')
    args = parser.parse_args()
    try:
        _profile()
        if args.probe:
            record = _observed()
        else:
            # Show that the disposable process initially has a working local socket syscall.
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM):
                pass  # creation only: no connection, listener, packet or external contact
            policy = install_network_denial()
            record = dict(_observed(), policy=policy)
            child = subprocess.run([sys.executable, '-I', str(Path(__file__).resolve()), '--probe'],
                                   stdin=subprocess.DEVNULL, capture_output=True, text=True,
                                   timeout=10, check=False)
            if child.returncode != 0:
                raise RuntimeError('exec child control failed: ' + child.stderr + child.stdout)
            record['exec_child'] = json.loads(child.stdout)
        print(json.dumps(record, sort_keys=True))
        return 0
    except (OSError, RuntimeError) as error:
        print(json.dumps({'refused': str(error)}))
        return 2


if __name__ == '__main__':
    raise SystemExit(main())
