"""TEST_ONLY AST/memory ancestry regressions; never access proc/root or launch a child."""
import ast
import builtins
import hashlib
import json
import stat
from pathlib import Path
from types import SimpleNamespace

import pytest

ROOT = Path(__file__).parents[1]
BENCH = ROOT / 'bench/pinned-candidate'


def selected(path, names, namespace):
    tree = ast.parse(path.read_text())
    nodes = [node for node in tree.body if isinstance(node, (ast.FunctionDef, ast.ClassDef)) and node.name in names]
    exec(compile(ast.Module(body=nodes, type_ignores=[]), str(path), 'exec'), namespace)
    return namespace


def ancestry(uids, *, executable='/usr/bin/sudo', mode=0o4755):
    closed = []
    class Identity:
        def __init__(self, pid):
            self.pid = pid
            self.ppid = pid + 1 if pid - 2 < len(uids) - 1 else 1
            self.start = str(700 + pid)
            self.uid = list(uids[pid - 2])
        def verify(self): pass
        def close(self): closed.append(self.pid)
    os_model = SimpleNamespace(getppid=lambda: 2, readlink=lambda path: executable,
                               listxattr=lambda *a, **k: [])
    guardian = SimpleNamespace(Identity=Identity, protected_path=lambda path:
                              SimpleNamespace(st_mode=stat.S_IFREG | mode, st_nlink=1))
    ns = selected(BENCH/'linux_lease_control.py',
                  {'CallerAncestryError', '_protected_launcher', 'original_caller'},
                  {'Any': object, 'os': os_model, 'stat': stat})
    return ns, guardian, closed


@pytest.mark.parametrize('uids', ([1001, 0, 0, 0], [0, 1001, 0, 0], [1001, 0, 1001, 0]))
def test_ambiguous_ancestry_remains_refused_with_bounded_observed_facts(uids):
    ns, guardian, closed = ancestry([uids, [1001] * 4])
    with pytest.raises(ValueError, match='ambiguous launcher credential ancestry') as raised:
        ns['original_caller'](guardian)
    facts = getattr(raised.value, 'facts', None)
    assert facts is not None, 'original ambiguous refusal lost its actual ancestry observations'
    assert facts == {'schema': 'TEST_ONLY-caller-ancestry-failure/v1',
                     'observed_ancestors': 1, 'omitted_prefix': 0,
                     'observations': [{'pid': 2, 'start': '702', 'ppid': 3,
                                       'uid': uids, 'executable': '/usr/bin/sudo', 'executable_truncated': False}]}
    assert closed == [2]


def test_failure_observation_tail_is_bounded_without_changing_credential_refusal():
    ns, guardian, closed = ancestry([[0] * 4] * 40 + [[1001, 0, 0, 0], [1001] * 4])
    with pytest.raises(ValueError, match='ambiguous') as raised:
        ns['original_caller'](guardian)
    facts = getattr(raised.value, 'facts', None)
    assert facts is not None
    assert facts['observed_ancestors'] == 41 and facts['omitted_prefix'] == 9
    assert len(facts['observations']) == 32
    assert facts['observations'][0]['pid'] == 11 and facts['observations'][-1]['pid'] == 42
    assert closed == list(range(2, 43))


def test_old_all_root_intermediate_and_uniform_nonroot_caller_route_is_preserved():
    ns, guardian, closed = ancestry([[0] * 4, [1001] * 4])
    caller = ns['original_caller'](guardian)
    assert caller.pid == 3 and caller.uid == [1001] * 4 and closed == [2]


def test_mixed_credentials_do_not_make_an_unrecognised_privileged_launcher_acceptable():
    ns, guardian, closed = ancestry([[1001, 0, 0, 0], [1001] * 4], executable='/usr/bin/TEST_ONLY-other')
    with pytest.raises(ValueError, match='unsafe or unrecognised'):
        ns['original_caller'](guardian)
    assert closed == [2]


def suite_model(*, tamper=False, write_failure=False, positive=False, immediate_tamper=False):
    control_ns, guardian, closed = ancestry([[1001, 0, 0, 0], [1001] * 4])
    control = SimpleNamespace(**control_ns)
    # Pre-existing source types are deliberately distinct, never ValueError catch-alls.
    control.CiPrerequisiteUnavailable = type('CiPrerequisiteUnavailable', (Exception,), {})
    memory = {}; reads = []; sent = []; later = []
    store = '/var/lib/policy-as-versioned-flux-linux-control'
    class ModelPath:
        def __init__(self, *parts): self.value = '/'.join(str(part).rstrip('/') for part in parts)
        def __str__(self): return self.value
        def __truediv__(self, part): return ModelPath(self.value, part)
        @property
        def name(self): return self.value.rsplit('/', 1)[-1]
        def mkdir(self, **kwargs): assert kwargs == {'mode': 0o700}
        def read_text(self):
            assert self.value == '/proc/self/stat'
            return '201 (TEST_ONLY) ' + ' '.join(['S', '1'] + ['0'] * 17 + ['77'])
    def canonical(value): return json.dumps(value, sort_keys=True, separators=(',', ':')).encode()
    sha = lambda raw: hashlib.sha256(raw).hexdigest()
    def write_fixed(path, raw):
        if write_failure and str(path).endswith('/caller.json'): raise OSError('TEST_ONLY write failure')
        assert str(path) not in memory
        memory[str(path)] = raw
    def protected_read(path, expected=None, maximum=None):
        reads.append(path)
        raw = memory[path]
        if path.endswith('/caller.json') and ((tamper and reads.count(path)==2) or (immediate_tamper and reads.count(path)==1)): raw += b'changed'
        if expected is not None and sha(raw) != expected: raise ValueError('TEST_ONLY protected bytes differ')
        assert maximum is None or len(raw) <= maximum
        return raw
    guardian.protected_read = protected_read
    members = ('linux_lease_control.py', 'linux_guardian.py')
    start = {'started': 100., 'deadline': 1000., 'source_manifest_sha256': '1' * 64}
    def require_work(now): assert 100. <= now < 990.
    budget = SimpleNamespace(started=100., deadline=1000., require_work=require_work)
    modules = {'ctypes': SimpleNamespace(sizeof=lambda value: 8, c_void_p=object),
               'os': SimpleNamespace(getresuid=lambda: (0, 0, 0), getpid=lambda: 201),
               'platform': SimpleNamespace(machine=lambda: 'x86_64'),
               'sys': SimpleNamespace(platform='linux', byteorder='little', executable='/usr/bin/python3.12',
                                      flags=SimpleNamespace(isolated=True, no_site=True), dont_write_bytecode=True),
               'time': SimpleNamespace(monotonic=lambda: 150.)}
    safe_builtins = dict(vars(builtins))
    safe_builtins['__import__'] = lambda name, *args, **kwargs: modules[name]
    def read_installed(path, maximum):
        if path == store + '/start.json': return canonical(start)
        return b'TEST_ONLY source DATA'
    def forbidden(*args, **kwargs):
        later.append('forbidden')
        raise AssertionError('must not proceed past caller refusal')
    # Caller acquisition itself is exercised through real fixed source bodies
    # in the sibling pure task/FD model. This seam tests protected transport of
    # that actual model refusal, without invoking proc from the AST suite.
    from test_linux_lease_control_ci_sudo import Kernel, ci
    model = Kernel()
    if positive:
        endpoint, facts = model.run(pytest.MonkeyPatch())
        def ci_route(*args, **kwargs): return endpoint, facts
    else:
        model.open_fail = lambda kind, pid: pid == 30
        with pytest.raises(ci.CiCallerError) as observed:
            model.run(pytest.MonkeyPatch())
        def ci_route(*args, **kwargs): raise observed.value
    closed = model.fds
    ns = {'__builtins__': safe_builtins, '__file__': store + '/source/linux_lease_control_ci.py',
          'ci_original_caller': ci_route, 'CiCallerError': ci.CiCallerError,
          'validate_ci_caller_record': ci.validate_ci_caller_record,
          'Any': object, 'Path': ModelPath, 'STORE': store, 'json': json, 'sha': sha,
          'canonical': canonical, 'MEMBERS': members, 'MAX_FILE': 16 * 1024**2,
          'OBSERVATIONS': ('caller',), 'unique_object': dict,
          'SuiteBudget': type('SuiteBudget', (), {'admit': staticmethod(lambda *args, **kwargs: budget)}),
          'PrerequisiteUnavailable': type('PrerequisiteUnavailable', (Exception,), {}),
          'installed_read': read_installed, 'source_manifest': lambda *args: {},
          'check_member': lambda *args: None,
          'installed_module': lambda name, manifest: control if name == 'linux_lease_control.py' else guardian,
          'write_fixed': write_fixed,
          'workflow_context': forbidden, 'admit_ci_root': forbidden, 'discover_closure': forbidden,
          'execute_suite': forbidden,
          'send_export': lambda files, outcome, selected_budget: sent.append((files, outcome, selected_budget))}
    selected(BENCH/'linux_lease_control_ci.py', {'persist_observation', 'owned_exports', 'suite_main'}, ns)
    return ns, sent, memory, reads, later, closed


def test_suite_exports_protected_observed_ancestry_failure_before_any_kernel_admission():
    ns, sent, memory, reads, later, closed = suite_model()
    assert ns['suite_main']() == 1
    assert len(sent) == 1 and later == [] and closed == {}
    files, outcome, budget = sent[0]
    assert outcome['status'] == 'FAIL' and outcome['executed'] is False
    assert outcome['control_passed'] is outcome['production_capture_accepted'] is False
    assert (outcome['started'], outcome['deadline'], outcome['finished']) == (100., 1000., 150.)
    assert 'CI caller ancestry refused' in outcome['reason']
    path = ns['STORE'] + '/ci-evidence/caller.json'
    assert files['suite/caller.json'] == memory[path]
    assert reads.count(path) == 2  # protected readback at observation and again at export
    assert json.loads(files['suite/caller.json'])['snapshots'][1]['identity']['uid'] == [1001, 0, 0, 0]
    assert files['suite/result.json'] == memory[ns['STORE'] + '/result.json']
    assert budget.deadline == 1000.


@pytest.mark.parametrize('change', ('tamper', 'write_failure'))
def test_unretained_or_changed_ancestry_diagnostics_cannot_be_exported_as_complete(change):
    ns, sent, memory, reads, later, closed = suite_model(**{change: True})
    with pytest.raises((ValueError, OSError)):
        ns['suite_main']()
    assert sent == [] and later == [] and closed == {}


@pytest.mark.parametrize('uids', ([0, 0, 0, 0], [1001, 0, 0, 0], [1001, 1001, 1001, 1001]))
def test_actual_identity_uid_parser_conserves_mocked_kernel_field_order(uids):
    source = ast.parse((BENCH/'linux_guardian.py').read_text())
    identity = next(node for node in source.body if isinstance(node, ast.ClassDef) and node.name == 'Identity')
    read = next(node for node in identity.body if isinstance(node, ast.FunctionDef) and node.name == 'read')
    read.decorator_list = []
    parser = next(node for node in source.body if isinstance(node, ast.FunctionDef) and node.name == 'parse_status')
    class ModelPath:
        def __init__(self, value): self.value = value
        def read_text(self):
            if self.value == '/proc/2/status': return 'Name: TEST_ONLY\nUid: ' + '\t'.join(map(str, uids)) + '\n'
            assert self.value == '/proc/2/stat'
            return '2 (TEST_ONLY) ' + ' '.join(['S', '3'] + ['0'] * 17 + ['702'])
    ns = {'Path': ModelPath, 'Any': object}
    exec(compile(ast.Module(body=[parser, read], type_ignores=[]), 'TEST_ONLY identity parser', 'exec'), ns)
    assert ns['read'](2) == {'start': '702', 'ppid': 3, 'uid': uids}


def test_failure_executable_prefix_is_explicitly_bounded_and_never_admitted():
    executable = '/' + 'TEST_ONLY' * 600
    ns, guardian, closed = ancestry([[1001, 0, 0, 0], [1001] * 4], executable=executable, mode=0o755)
    with pytest.raises(ValueError, match='ambiguous') as raised:
        ns['original_caller'](guardian)
    row = raised.value.facts['observations'][0]
    assert row['executable'] == executable[:4096]
    assert row['executable_truncated'] is True and closed == [2]

@pytest.mark.parametrize('change',('normal','tamper','write_failure'))
def test_verified_caller_record_is_protected_before_any_later_phase(change):
    ns,sent,memory,reads,later,remaining=suite_model(positive=True,**({'immediate_tamper':True} if change=='tamper' else {'write_failure':True} if change=='write_failure' else {}))
    if change=='normal':
        # Stop at workflow attribution before any principal/kernel work. The
        # same fixed suite has already persisted and reverified the endpoint.
        with pytest.raises(AssertionError,match='must not proceed'):ns['suite_main']()
        record=json.loads(memory[ns['STORE']+'/ci-evidence/caller.json'])
        assert record['status']=='VERIFIED' and record['selected_pid']==30
        assert reads.count(ns['STORE']+'/ci-evidence/caller.json')==1
        assert later==['forbidden'] and sent==[]
    else:
        # Immediate protected readback or exclusive write fails before any
        # subsequent context/principal/kernel operation.
        with pytest.raises((ValueError,OSError)):ns['suite_main']()
        assert remaining=={} and sent==[] and later==[]


def test_full_uncertain_descriptor_reservation_blocks_diagnostic_writer():
    ns,sent,memory,reads,later,remaining=suite_model()
    original=ns['ci_original_caller']
    def full(*args,**kwargs):
        try:original(*args,**kwargs)
        except ns['CiCallerError'] as error:
            error.facts['custody']['unresolved_ownership_upper_bound']=12
            raise
    ns['ci_original_caller']=full
    with pytest.raises(ValueError,match='no descriptor headroom'):ns['suite_main']()
    assert not memory and not sent and later==[]


def test_refusal_persistence_and_export_use_original_deadline_without_new_work_allowance():
    ns,sent,memory,reads,later,remaining=suite_model()
    ns['__builtins__']['__import__']('time').monotonic=lambda:995.
    assert ns['suite_main']()==1
    assert sent[0][1]['finished']==995. and sent[0][1]['deadline']==1000.
    assert reads.count(ns['STORE']+'/ci-evidence/caller.json')==2
    assert not later and not remaining
