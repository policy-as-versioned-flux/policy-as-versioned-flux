"""TEST_ONLY receipt/ancestry controls; no kernel or privileged operation occurs."""
import copy
import stat
from pathlib import Path
from types import SimpleNamespace

import pytest

from test_linux_lease_control import control


def receipt(scenario):
    cases = {
        'baseline': [('standard', ('paired', 'limits', 'network', 'sources'))],
        'boundaries': [('standard', ('writes', 'privilege', 'isolation', 'process', 'network', 'exec-inheritance'))],
        'resources': [('standard', ('limits', 'affinity', 'tmpfs')), ('oom', ('oom',)), ('pids', ('pids',))],
        'supervisor-loss': [('descendants', ('descendants', 'guardian-survived', 'supervisor-dead'))],
        'guardian-loss': [(case, (case,)) for case in ('raw-clone', 'attached', 'dropped', 'armed', 'ready', 'descendants')],
        'invalid-evidence': [(case, (case,)) for case in ('eof', 'deadline', 'ready', 'source', 'overflow', 'observer', 'incomplete', 'stale-lock')],
    }[scenario]
    attempts = []
    checks = {}
    for index, (case, names) in enumerate(cases):
        identity = {'pid': 701 + index, 'start': str(91 + index)}
        terminal = None if scenario == 'guardian-loss' or (scenario == 'invalid-evidence' and case == 'observer') else {'empty': True, 'reaped': True, 'removed': True}
        attempt = {'case': case, 'scenario': scenario, 'executed': True, 'error': None,
            'started': 100.0 + 10 * index, 'finished': 110.0 + 10 * index,
            'outer': {'empty': True, 'dead': True, 'reaped': True, 'removed': True},
            'sentinel': {'before': dict(identity), 'after': dict(identity), 'alive': True},
            'guardian_terminal': terminal, 'checks': dict.fromkeys(names, True)}
        attempts.append(attempt)
        checks.update(attempt['checks'])
    last = attempts[-1]
    return {'executed': True, 'scenario': scenario, 'error': None, 'started': 100.0,
        'finished': last['finished'], 'attempts': attempts, 'checks': checks,
        **copy.deepcopy({name: last[name] for name in ('outer', 'sentinel', 'guardian_terminal')})}


@pytest.mark.parametrize('scenario', ('baseline', 'boundaries', 'resources', 'supervisor-loss', 'guardian-loss', 'invalid-evidence'))
def test_complete_synthetic_control_receipts_preserve_production_refusal(scenario):
    result = control().verify_result(receipt(scenario))
    assert result['control_passed'] is True
    assert result['production_capture_accepted'] is False


@pytest.mark.parametrize('absence', ('missing', 'null', 'empty'))
def test_aggregate_checks_cannot_replace_actual_subcase_records(absence):
    value = receipt('guardian-loss')
    if absence == 'missing':
        value.pop('attempts')
    else:
        value['attempts'] = None if absence == 'null' else []
    with pytest.raises(ValueError, match='attempt'):
        control().verify_result(value)


@pytest.mark.parametrize('index', (0, 1, 2))
def test_each_resource_attempt_requires_its_own_guardian_terminal(index):
    value = receipt('resources')
    value['attempts'][index]['guardian_terminal'] = None
    with pytest.raises(ValueError, match='terminal'):
        control().verify_result(value)


@pytest.mark.parametrize('scenario', ('resources', 'guardian-loss', 'invalid-evidence'))
def test_later_sentinel_cannot_hide_an_earlier_lost_sentinel(scenario):
    value = receipt(scenario)
    value['attempts'][0]['sentinel']['alive'] = False
    with pytest.raises(ValueError, match='sentinel'):
        control().verify_result(value)


def test_guardian_loss_cannot_acquire_a_subcase_production_terminal():
    value = receipt('guardian-loss')
    value['attempts'][0]['guardian_terminal'] = {'empty': True, 'reaped': True, 'removed': True}
    with pytest.raises(ValueError, match='terminal'):
        control().verify_result(value)


@pytest.mark.parametrize('scenario', ('guardian-loss', 'invalid-evidence'))
def test_intentional_missing_terminal_must_still_be_explicitly_recorded(scenario):
    value = receipt(scenario)
    value['attempts'][0].pop('guardian_terminal')
    with pytest.raises(ValueError, match='terminal'):
        control().verify_result(value)


def test_source_denial_cannot_hide_missing_terminal_inside_negative_scenario():
    value = receipt('invalid-evidence')
    value['attempts'][3]['guardian_terminal'] = None
    with pytest.raises(ValueError, match='terminal'):
        control().verify_result(value)


@pytest.mark.parametrize('scenario', ('baseline', 'boundaries', 'resources', 'supervisor-loss', 'guardian-loss', 'invalid-evidence'))
def test_partial_terminal_is_never_a_complete_subcase_witness(scenario):
    value = receipt(scenario)
    value['attempts'][0]['guardian_terminal'] = {'empty': True, 'reaped': True}
    with pytest.raises(ValueError, match='terminal'):
        control().verify_result(value)


def test_aggregate_cannot_substitute_a_different_live_sentinel():
    value = receipt('resources')
    value['sentinel'] = {'before': {'pid': 999, 'start': '999'}, 'after': {'pid': 999, 'start': '999'}, 'alive': True}
    with pytest.raises(ValueError, match='aggregate'):
        control().verify_result(value)


@pytest.mark.parametrize('seconds', (30.0, 30.0001, 40.0))
def test_fixed_deadline_subcase_retains_its_stricter_thirty_second_ceiling(seconds):
    value = receipt('invalid-evidence')
    deadline = value['attempts'][1]
    extension = seconds - (deadline['finished'] - deadline['started'])
    deadline['finished'] += extension
    for later in value['attempts'][2:]:
        later['started'] += extension
        later['finished'] += extension
    value['finished'] += extension
    if seconds == 30.0:
        assert control().verify_result(value)['production_capture_accepted'] is False
    else:
        with pytest.raises(ValueError, match='ceiling'):
            control().verify_result(value)


def ancestry(monkeypatch, executable='/usr/bin/sudo', mode=0o4755, owner=0, capabilities=False, links=1, acl=False, symlink=False):
    module = control()
    guardian = module._guardian()
    class Identity:
        def __init__(self, pid):
            self.pid = pid
            self.uid = [0] * 4 if pid == 100 else [1001] * 4
            self.ppid = 99 if pid == 100 else 1
        def verify(self): pass
        def close(self): pass
    def metadata(path):
        name = str(path)
        if name in (executable, '/usr/bin/bash'):
            return SimpleNamespace(st_uid=owner if name == executable else 0,
                st_mode=(stat.S_IFLNK if symlink and name == executable else stat.S_IFREG) | (mode if name == executable else 0o755), st_nlink=links if name == executable else 1)
        return SimpleNamespace(st_uid=0, st_mode=stat.S_IFDIR | 0o755, st_nlink=1)
    monkeypatch.setattr(guardian, 'Identity', Identity)
    monkeypatch.setattr(guardian.os, 'getppid', lambda: 100)
    monkeypatch.setattr(guardian.os, 'readlink', lambda path: executable if str(path) == '/proc/100/exe' else '/usr/bin/bash')
    monkeypatch.setattr(Path, 'lstat', metadata)
    def attributes(path, **kwargs):
        return (['security.capability'] if capabilities else []) + (['system.posix_acl_access'] if acl else []) if str(path) == executable else []
    monkeypatch.setattr(guardian.os, 'listxattr', attributes, raising=False)
    return module, guardian


def test_protected_sudo_ancestry_reaches_caller_without_weakening_candidate_closure(monkeypatch):
    module, guardian = ancestry(monkeypatch)
    caller = module.original_caller(guardian)
    assert caller.pid == 99 and caller.uid == [1001] * 4
    with pytest.raises(ValueError, match='privilege'):
        guardian.protected_path('/usr/bin/sudo', True)


@pytest.mark.parametrize('change', ({'executable': '/usr/bin/TEST_ONLY-other'}, {'mode': 0o6755},
    {'mode': 0o4777}, {'owner': 1001}, {'capabilities': True}, {'links': 2}, {'acl': True}, {'symlink': True}))
def test_launcher_exception_cannot_admit_other_privileged_or_mutable_executables(monkeypatch, change):
    module, guardian = ancestry(monkeypatch, **change)
    with pytest.raises(ValueError):
        module.original_caller(guardian)
