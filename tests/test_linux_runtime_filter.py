"""TEST_ONLY cBPF interpreter controls; no filter is installed, no Linux cage is run."""
import importlib.util
from pathlib import Path
import struct

import pytest


def policy():
    spec = importlib.util.spec_from_file_location('TEST_ONLY_runtime_filter',
        Path(__file__).parents[1]/'bench/pinned-candidate/linux_runtime_filter.py')
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec); spec.loader.exec_module(module)
    return module


def interpret(program, nr, arch, arg0=0):
    # Independent minimal classic-BPF interpreter over struct seccomp_data.
    data = struct.pack('<iIQQQQQQQ', nr, arch, 0, arg0, 0, 0, 0, 0, 0)
    accumulator, position = 0, 0
    for _ in range(1000):
        code, yes, no, value = program[position]; position += 1
        if code == 0x20: accumulator = struct.unpack_from('<I', data, value)[0]
        elif code == 0x15: position += yes if accumulator == value else no
        elif code == 0x35: position += yes if accumulator >= value else no
        elif code == 0x45: position += yes if accumulator & value else no
        elif code == 0x06: return value
        else: raise AssertionError('unknown TEST_ONLY interpreter opcode')
    raise AssertionError('nonterminal filter')


@pytest.mark.parametrize('machine,arch,clone,prctl,unshare,mount', [
    ('x86_64', 0xc000003e, 56, 157, 272, 165),
    ('aarch64', 0xc00000b7, 220, 167, 97, 40)])
def test_lockdown_denies_escape_and_death_signal_reset_while_retaining_threads(machine, arch, clone, prctl, unshare, mount):
    program = policy().runtime_filter(machine)
    deny, allow = 0x50001, 0x7fff0000
    assert interpret(program, unshare, arch) == deny
    assert interpret(program, mount, arch) == deny
    assert interpret(program, prctl, arch, 1) == deny  # PR_SET_PDEATHSIG
    assert interpret(program, prctl, arch, 2) == allow  # PR_GET_PDEATHSIG
    assert interpret(program, clone, arch, 0x10000 | 0x100 | 0x200) == allow
    assert interpret(program, clone, arch, 0x10000000 | 17) == deny  # NEWUSER
    assert interpret(program, clone, arch, 0x20000000 | 17) == deny  # NEWPID
    assert interpret(program, 435, arch) == 0x50026  # clone3 ENOSYS, no opaque namespace flags
    assert interpret(program, 468, arch) == 0x50026  # unreviewed future syscall
    assert interpret(program, 0, 0x40000003) == 0x80000000  # foreign ABI KILL_PROCESS


@pytest.mark.parametrize('machine,arch,clone', [('x86_64',0xc000003e,56),('aarch64',0xc00000b7,220)])
def test_every_namespace_flag_and_high_clone_bits_refuse(machine, arch, clone):
    program = policy().runtime_filter(machine)
    for flag in (0x20000,0x2000000,0x4000000,0x8000000,0x10000000,0x20000000,0x40000000,1<<32):
        assert interpret(program, clone, arch, flag|17) == 0x50001
    assert interpret(program, 435, arch, 0) == 0x50026
