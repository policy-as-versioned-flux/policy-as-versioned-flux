"""TEST_ONLY pure/external protocol controls. No helper/kernel/runtime execution."""
import importlib.util
import json
from pathlib import Path
import unittest

PATH = Path(__file__).resolve().parents[1]/'bench/pinned-candidate/linux_guardian.py'
spec = importlib.util.spec_from_file_location('linux_guardian_source_test', PATH)
assert spec is not None and spec.loader is not None
guardian = importlib.util.module_from_spec(spec)
if PATH.exists(): spec.loader.exec_module(guardian)

class GuardianProtocolTests(unittest.TestCase):
    def test_fragmented_external_child_bytes_cannot_mint_host_events(self):
        reader = guardian.FrameReader(64, 256)
        self.assertEqual(reader.feed(b'{"event":"done"'), [])
        packets = reader.feed(b',"lease":"fake"}\n')
        writer = guardian.Wire('a'*48)
        wrapped = writer.frame('preflight', packets[0])
        self.assertEqual(json.loads(wrapped), {'event':'frame','lease':'a'*48,
            'phase':'preflight','body':{'event':'done','lease':'fake'}})
        reader.eof()
        reader.feed(b"{\"unfinished\":")
        with self.assertRaises(ValueError): reader.eof()

    def test_external_mount_snapshot_cannot_hide_writable_alias_or_host_proc(self):
        fixture = ('1 0 0:1 / / ro,nosuid,nodev - tmpfs tmpfs ro\n'
            '2 1 0:2 / /proc ro,nosuid,nodev,noexec - proc proc ro\n'
            '3 1 0:3 / /attempt rw,nosuid,nodev,noexec - tmpfs tmpfs rw,size=131072k\n'
            '4 1 8:1 /snapshot/python /python ro,nosuid,nodev - ext4 /dev/test ro\n')
        self.assertEqual(guardian.inspect_mounts(fixture, {'/python'})['root_readonly'], True)
        with self.assertRaisesRegex(ValueError, 'writable'):
            guardian.inspect_mounts(fixture.replace('/python ro,nosuid', '/python rw,nosuid'), {'/python'})
        with self.assertRaisesRegex(ValueError, 'undeclared'):
            guardian.inspect_mounts(fixture+'5 1 0:4 / /host ro - proc proc ro\n', {'/python'})

    def test_closed_request_rejects_path_authority_and_wrong_identity_type(self):
        fixture = {'authority':'a'*64,'profile_sha256':'b'*64,
            'request':{'input':{'TEST_ONLY':'arbitrary'},'prompt_utf8':'TEST_ONLY prompt'},
            'supervisor_pid':17,'supervisor_start':'42','deadline_monotonic':10000.}
        self.assertEqual(guardian.validate_request(fixture), fixture)
        for extra in ('command','candidate_uid','cgroup_parent'):
            with self.assertRaises(ValueError): guardian.validate_request(dict(fixture, **{extra:'/TEST_ONLY'}))
        with self.assertRaises(ValueError): guardian.validate_request(dict(fixture, supervisor_pid=True))
        with self.assertRaises(ValueError): guardian.validate_request(dict(fixture,
            request=dict(fixture['request'],expected_label='TEST_ONLY forbidden extra')))

    def test_kernel_resource_snapshot_requires_exact_quota_cpuset_swap_and_reserve(self):
        fixture = {'limits':{'memory.max':'12884901888','memory.swap.max':'0','pids.max':'128',
            'cpu.max':'200000 100000','cpu.max.burst':'0','cpuset.cpus.effective':'2,4',
            'cpuset.mems.effective':'0'}, 'memory.current':100, 'memory.peak':200,
            'memory.swap.current':0,'pids.current':1,'memory.events':{'max':0,'oom':0,'oom_kill':0},
            'reserve':{'memory_available':3000000000,'host_memory_available':3000000000,
                'ancestors':synthetic_ancestor_rows(),'disk_free':6000000000,
                'storage':[{'path':'/TEST_ONLY/anchor','device':7,'inode':17,'disk_free':6000000000}]}}
        guardian.validate_resources(fixture, {2,4})
        for changed in ({'memory.swap.current':1}, {'pids.current':129},
                {'limits':dict(fixture['limits'], **{'cpuset.cpus.effective':'2-4'})},
                {'limits':dict(fixture['limits'], **{'cpu.max':'max 100000'})},
                {'memory.events':{'oom_kill':1}},
                {'reserve':{'memory_available':100,'disk_free':6000000000}}):
            with self.assertRaises(ValueError): guardian.validate_resources(dict(fixture, **changed), {2,4})

    def test_teardown_receipt_requires_all_actual_kernel_witnesses(self):
        self.assertEqual(guardian.teardown_receipt(False, True, True, True),
            {'empty':True,'reaped':True,'removed':True})
        for witnesses in ((True,True,True,True),(False,False,True,True),
                (False,True,False,True),(False,True,True,False),(0,True,True,True)):
            with self.assertRaises(ValueError): guardian.teardown_receipt(*witnesses)

    def test_external_journal_rejects_fragment_overflow_and_keeps_terminal_capacity(self):
        reader=guardian.FrameReader(16,40)
        with self.assertRaisesRegex(ValueError, 'frame'):
            reader.feed(b'1234567890123456')
        reader=guardian.FrameReader(16,20)
        self.assertEqual(reader.feed(b'{}\n{}\n{}\n{}\n{}\n{}\n'), [{}]*6)
        with self.assertRaisesRegex(ValueError, 'journal'):reader.feed(b'{}\n')
        wire=guardian.Wire('a'*48)
        wire.total=guardian.MAX_STDOUT-32768
        with self.assertRaises(ValueError):wire.frame('generate',{'type':'token','index':0,'id':7})
        self.assertEqual(json.loads(wire.event('failure',error='TEST_ONLY overflow'))['event'],'failure')

    def test_protected_profile_cannot_widen_reviewed_numerical_or_decode_settings(self):
        config={'profile':'signal-linux-bf16-v1','max_input_tokens':4096,'max_new_tokens':512,
            'threads':2,'interop_threads':1,'timeout_seconds':900,
            'linux_profile':{'model_id':'Qwen/Qwen3-4B-Instruct-2507',
                'revision':'cdbee75f17c01a7cc42f958dc650907174af0554',
                'model_manifest_sha256':'409410d7d41d7e62aafb27c18f049fe3c62d66383b3a5b89d5fadfd3b773fd7e',
                'chat_template_sha256':'64f85b198065d0fba2a81f37e10ed68161ce2c19a754c7100e67e0ca2ee9c326',
                'runtime_manifest_sha256':'a'*64,'dtype':'torch.bfloat16','device':'cpu','attention':'eager',
                'do_sample':False,'num_beams':1,'num_return_sequences':1,'seed':0,'use_cache':True,
                'cache_implementation':'dynamic','eos_token_ids':[151645,151643],'pad_token_id':151643}}
        guardian.validate_reviewed_profile(config)
        for changed in ({'max_new_tokens':513},{'threads':True},{'timeout_seconds':901},
                {'context_tokens':8192},{'linux_profile':dict(config['linux_profile'],device='cuda')}):
            with self.assertRaises(ValueError): guardian.validate_reviewed_profile(dict(config,**changed))


def test_shared_parent_deadline_cannot_reset_after_privileged_setup_or_widen_profile():
    assert guardian.attempt_deadlines(1000.,900,1050.) == (1040.,1050.)
    assert guardian.attempt_deadlines(1000.,900,3000.) == (1890.,1900.)
    for deadline in (999.,1005.,float('nan'),float('inf'),True,'1050'):
        with unittest.TestCase().assertRaises(ValueError):
            guardian.attempt_deadlines(1000.,900,deadline)


def test_actual_admission_and_sampling_use_all_protected_backing_storage(monkeypatch):
    """Evaluate the actual reserve call sites with synthetic OS filesystem facts only."""
    import ast
    from types import SimpleNamespace
    tree = ast.parse(PATH.read_text())
    calls = [node for node in ast.walk(tree) if isinstance(node, ast.Call)
        and isinstance(node.func, ast.Name) and node.func.id == 'reserve']
    assert len(calls) == 1  # Both public admission and sampling use the same budget reader.
    surfaces = ('/TEST_ONLY/anchor', '/TEST_ONLY/snapshot')
    free_blocks = dict.fromkeys(surfaces, 3*1024**2)
    def filesystem(path):
        return SimpleNamespace(f_frsize=4096, f_bavail=free_blocks.get(path, 0))
    class MemoryInfo:
        def __init__(self, path): assert path == '/proc/meminfo'
        def read_text(self): return 'MemAvailable: 33554432 kB\n'
    monkeypatch.setattr(guardian, 'Path', MemoryInfo)
    monkeypatch.setattr(guardian, 'protected_path', lambda path, regular: SimpleNamespace(st_dev=7, st_ino=17))
    descriptors = {}
    def opened(path, flags):
        descriptors[len(descriptors)+10] = path
        return len(descriptors)+9
    monkeypatch.setattr(guardian, 'os', SimpleNamespace(statvfs=filesystem, open=opened,
        fstat=lambda fd: SimpleNamespace(st_dev=7, st_ino=17),
        fstatvfs=lambda fd: filesystem(descriptors[fd]), close=lambda fd: None,
        O_RDONLY=0, O_DIRECTORY=0, O_NOFOLLOW=0, O_CLOEXEC=0))
    for call in calls:
        namespace = {'reserve': guardian.reserve, 'parent': '/sys/fs/cgroup/TEST_ONLY',
            'self': SimpleNamespace(parent_path='/sys/fs/cgroup/TEST_ONLY', storage_paths=surfaces),
            'MEMORY': guardian.MEMORY, 'RESERVE': guardian.RESERVE, 'minimum':guardian.MEMORY+guardian.RESERVE}
        result = eval(compile(ast.Expression(call), str(PATH), 'eval'), namespace)
        assert result['disk_free'] == 12884901888
        assert {row['path'] for row in result['storage']} == set(surfaces)
    # A second backing filesystem losing space cannot hide behind the first.
    import pytest
    free_blocks['/TEST_ONLY/snapshot'] = 0
    for call in calls:
        if len(call.args) == 3:
            result = eval(compile(ast.Expression(call), str(PATH), 'eval'), namespace)
            assert result['disk_free'] == 0
            assert result['storage'][1]['disk_free'] == 0
        else:
            with pytest.raises(ValueError, match='disk unavailable'):
                eval(compile(ast.Expression(call), str(PATH), 'eval'), namespace)


def test_storage_scope_is_derived_from_anchor_and_complete_protected_closure():
    host = {'guardian_entry':'/TEST_ONLY/entry/guardian', 'guardian_python':'/TEST_ONLY/python/bin/python',
        'support_sources':{'/TEST_ONLY/support/filter.py':'a'*64},
        'cgroup_parent':'/sys/fs/cgroup/TEST_ONLY'}
    profile = {'readonly_mounts':[{'source':'/TEST_ONLY/assets/weights', 'target':'/model/weights'},
        {'source':'/TEST_ONLY/runtime/libtorch.so', 'target':'/runtime/libtorch.so'}]}
    assert guardian.storage_paths(host, profile) == (
        '/TEST_ONLY/assets', '/TEST_ONLY/entry', '/TEST_ONLY/python/bin',
        '/TEST_ONLY/runtime', '/TEST_ONLY/support', '/run/policy-as-versioned-flux-candidate')


def test_observed_storage_cannot_omit_a_backing_filesystem_or_hide_its_exhaustion():
    import pytest
    facts = {'limits':{'memory.max':'12884901888','memory.swap.max':'0','pids.max':'128',
        'cpu.max':'200000 100000','cpu.max.burst':'0','cpuset.cpus.effective':'2,4',
        'cpuset.mems.effective':'0'}, 'memory.current':100,'memory.peak':200,
        'memory.swap.current':0,'pids.current':1,'memory.events':{},
        'reserve':{'memory_available':3000000000,'host_memory_available':3000000000,
                'ancestors':synthetic_ancestor_rows(),'disk_free':6000000000,
            'storage':[{'path':'/TEST_ONLY/anchor','device':7,'inode':17,'disk_free':6000000000}]}}
    with pytest.raises(ValueError, match='storage'):
        guardian.validate_resources(facts, {2,4}, ('/TEST_ONLY/anchor','/TEST_ONLY/snapshot'))
    facts['reserve']['storage'].append({'path':'/TEST_ONLY/snapshot','device':8,'inode':18,'disk_free':6000000000})
    guardian.validate_resources(facts, {2,4}, ('/TEST_ONLY/anchor','/TEST_ONLY/snapshot'))
    facts['reserve']['storage'][1]['disk_free'] = 0
    with pytest.raises(ValueError, match='storage'):
        guardian.validate_resources(facts, {2,4}, ('/TEST_ONLY/anchor','/TEST_ONLY/snapshot'))


def test_host_ready_cannot_accept_dumpable_child_with_otherwise_valid_kernel_state():
    """Actual READY function with synthetic proc/OS boundaries; no helper/kernel call."""
    import ast
    import hashlib
    import pytest
    from types import SimpleNamespace
    source = ast.parse(PATH.read_text())
    names = {'verify_ready','host_mappings','inspect_mounts','parse_status','observe_nondumpability'}
    functions = [node for node in source.body if isinstance(node, ast.FunctionDef) and node.name in names]
    status = '\n'.join(['Uid: 65534 65534 65534 65534','Gid: 65534 65534 65534 65534',
        'Groups:', 'NSpid: 100 1','NoNewPrivs: 1','Seccomp: 2','Seccomp_filters: 2',
        *(key+': 00000000' for key in ('CapEff','CapPrm','CapInh','CapAmb','CapBnd'))])
    mounts = ('1 0 0:1 / / ro,nosuid,nodev - tmpfs tmpfs ro\n'
        '2 1 0:2 / /proc ro,nosuid,nodev,noexec - proc proc ro\n'
        '3 1 0:3 / /attempt rw,nosuid,nodev,noexec - tmpfs tmpfs rw,size=131072k\n')
    owner = [65534]  # TEST_ONLY post-exec dumpable=1 yields candidate-owned proc members.
    class FakePath:
        def __init__(self, path): self.path = path
        def read_text(self):
            return {'/proc/100/status':status,'/proc/100/mountinfo':mounts,'/proc/100/maps':''}[self.path]
        def stat(self):
            assert self.path in ('/proc/100/mem','/proc/100/auxv')
            return SimpleNamespace(st_uid=owner[0],st_gid=owner[0])
        def read_bytes(self):
            assert self.path == '/proc/100/exe'
            return b'TEST_ONLY interpreter'
        def iterdir(self):
            assert self.path == '/proc/100/fd'
            return []
    def readlink(path):
        if path.endswith('/ns/user'): return 'TEST_ONLY-same-user-namespace'
        return 'TEST_ONLY-'+path
    namespace = {'Path':FakePath,'Any':object,'Callable':object,'digest':lambda raw: hashlib.sha256(raw).hexdigest(),
        'os':SimpleNamespace(readlink=readlink,getsid=lambda pid: pid,getpgid=lambda pid: pid,
            statvfs=lambda path: SimpleNamespace(f_blocks=32768,f_frsize=4096))}
    module = ast.Module(body=[ast.ImportFrom(module='__future__',names=[ast.alias(name='annotations')],level=0),
        *functions],type_ignores=[])
    exec(compile(ast.fix_missing_locations(module),str(PATH),'exec'),namespace)
    attached,_,_ = synthetic_attached_child()
    identity = attached.identity
    child = SimpleNamespace(identity=identity)
    leaf = SimpleNamespace(identity=SimpleNamespace(st_dev=7,st_ino=17),mount_id=5,name='lease-TEST_ONLY',
        read=lambda name: '100',verify_limits=lambda: {})
    host = {'candidate_uid':65534,'candidate_gid':65534}
    profile = {'readonly_mounts':[],'config':{'backend':{'python_sha256':hashlib.sha256(b'TEST_ONLY interpreter').hexdigest()}}}
    with pytest.raises(ValueError, match='dumpab'):
        namespace['verify_ready'](child,host,profile,leaf,lambda: None)
    owner[0] = 0
    facts = namespace['verify_ready'](child,host,profile,leaf,lambda: None)
    assert facts['nondumpability']['proc_owners'] == {'mem':{'uid':0,'gid':0},'auxv':{'uid':0,'gid':0}}


def synthetic_attached_child():
    """Actual launch/Identity decisions with only synthetic OS process boundaries."""
    import ast
    from types import SimpleNamespace
    source = ast.parse(PATH.read_text())
    nodes = [node for node in source.body if isinstance(node, ast.ClassDef)
        and node.name in ('Identity','ChildIdentity','Child')]
    state = {'uid':[0]*4,'gid':[0]*4,'start':'TEST_ONLY-start','ppid':99,'dead':False}
    descriptors = [10]
    def pipe(flags):
        descriptors[0] += 2
        return descriptors[0]-1,descriptors[0]
    def write(fd, raw):
        assert raw == b'A'
        state['gid'] = [65534]*4
        state['uid'] = [65534]*4
        return 1
    class Proc:
        def __init__(self, path): self.path = path
        def read_text(self):
            assert self.path == '/proc/100/status'
            return 'Uid: '+' '.join(map(str,state['uid']))+'\nGid: '+' '.join(map(str,state['gid']))+'\nGroups:\n'
    namespace = {'Path':Proc,'parse_status':guardian.parse_status,
        'os':SimpleNamespace(pipe2=pipe,pidfd_open=lambda *args:71,getpid=lambda:99,
            close=lambda fd:None,set_blocking=lambda *args:None,write=write,O_CLOEXEC=0),
        'select':SimpleNamespace(select=lambda *args:([71] if state['dead'] else [],[],[])),
        'platform':SimpleNamespace(machine=lambda:'x86_64'),'signal':SimpleNamespace(SIGCHLD=17),
        'ctypes':SimpleNamespace(CDLL=lambda *args,**kw:SimpleNamespace(syscall=lambda *args:100)),
        'CLONE_NEWNS':0x20000,'CLONE_NEWPID':0x20000000}
    future = ast.ImportFrom(module='__future__',names=[ast.alias(name='annotations')],level=0)
    exec(compile(ast.fix_missing_locations(ast.Module(body=[future,*nodes],type_ignores=[])),str(PATH),'exec'),namespace)
    namespace['Identity'].read = staticmethod(lambda pid:{key:state[key] for key in ('uid','start','ppid')})
    child = namespace['Child']('preflight','/TEST_ONLY/root')
    leaf = SimpleNamespace(fd=80,parentfd=81,write=lambda *args:None,read=lambda name:'100',verify_limits=lambda:None)
    child.launch({'candidate_uid':65534,'candidate_gid':65534},{},{},leaf)
    return child,namespace,state


def test_required_root_to_candidate_drop_preserves_pinned_child_liveness():
    child,namespace,state = synthetic_attached_child()
    assert child.identity.pid == 100 and child.identity.start == 'TEST_ONLY-start'
    child.identity.verify()


def synthetic_budget_leaf(monkeypatch):
    """Synthetic host, storage and cgroup OS reads for the actual Leaf.sample seam."""
    from pathlib import PurePosixPath
    from types import SimpleNamespace
    parent = '/sys/fs/cgroup/TEST_ONLY'
    controls = ('cgroup.procs','cgroup.threads','cgroup.subtree_control','memory.max','memory.current')
    files = {parent+'/cgroup.procs':'',parent+'/cgroup.threads':'',
        parent+'/cgroup.subtree_control':'memory cpu cpuset pids',
        parent+'/memory.max':str(16*1024**3),parent+'/memory.current':str(15*1024**3),
        '/sys/fs/cgroup/cgroup.procs':'','/sys/fs/cgroup/cgroup.threads':'',
        '/sys/fs/cgroup/cgroup.subtree_control':'memory cpu cpuset pids'}
    class HostPath(PurePosixPath):
        def read_text(self):
            if str(self) == '/proc/meminfo':return 'MemAvailable: 33554432 kB\n'
            value = files[str(self)]
            if isinstance(value,Exception):raise value
            return value
        def exists(self):return str(self) in files
    replaced = [False]
    def metadata(path, regular):
        return SimpleNamespace(st_dev=7,st_ino=18 if replaced[0] and str(path)==parent else 17)
    monkeypatch.setattr(guardian,'Path',HostPath)
    monkeypatch.setattr(guardian,'protected_path',metadata)
    monkeypatch.setattr(guardian,'os',SimpleNamespace(open=lambda *args:10,
        close=lambda fd:None,fstat=lambda fd:SimpleNamespace(st_dev=7,st_ino=17),
        fstatvfs=lambda fd:SimpleNamespace(f_bavail=3*1024**2,f_frsize=4096),
        O_RDONLY=0,O_DIRECTORY=0,O_NOFOLLOW=0,O_CLOEXEC=0))
    leaf = guardian.Leaf.__new__(guardian.Leaf)
    leaf.parent_path = parent
    leaf.storage_paths = ('/TEST_ONLY/anchor','/TEST_ONLY/snapshot')
    leaf.ancestor_identities = None
    leaf.cpus = {2,4}
    leaf.read_limits = lambda: {'memory.max':'12884901888','memory.swap.max':'0','pids.max':'128',
        'cpu.max':'200000 100000','cpu.max.burst':'0','cpuset.cpus.effective':'2,4','cpuset.mems.effective':'0'}
    leaf.read = lambda name: {'memory.current':'100','memory.peak':'200','memory.events':'max 0\noom 0\noom_kill 0',
        'memory.swap.current':'0','cpu.stat':'usage_usec 1','cgroup.events':'populated 0','pids.current':'0'}[name]
    return leaf,files,replaced


def test_sample_conserves_effective_finite_ancestor_budget_before_refusing(monkeypatch):
    import pytest
    leaf,files,_ = synthetic_budget_leaf(monkeypatch)
    facts = leaf.sample(None,None)
    assert facts['reserve']['memory_available'] == 1024**3
    assert facts['reserve']['host_memory_available'] == 32*1024**3
    assert facts['reserve']['ancestors'][0]['memory.current'] == str(15*1024**3)
    with pytest.raises(ValueError,match='reserve'):
        guardian.validate_resources(facts,{2,4},leaf.storage_paths)


def test_each_phase_refuses_low_ancestor_before_any_child_launch(monkeypatch):
    import pytest
    from types import SimpleNamespace
    leaf,files,_ = synthetic_budget_leaf(monkeypatch)
    class ForbiddenChild:
        def __init__(self,*args):raise AssertionError('child construction reached without renewed headroom')
    monkeypatch.setattr(guardian,'Child',ForbiddenChild)
    for phase in ('preflight','generate'):
        instance = guardian.Guardian.__new__(guardian.Guardian)
        instance.leaf,instance.root = leaf,'/TEST_ONLY/root'
        instance.lease = 'a'*48
        instance.host = {'candidate_uid':65534,'candidate_gid':65534}
        instance.profile = {}
        instance.request = {'authority':'b'*64,'profile_sha256':'c'*64}
        instance.liveness = lambda:None
        with pytest.raises(guardian.ResourceAdmissionError) as failure:
            instance.run_phase(phase)
        assert failure.value.facts['memory_available'] == 1024**3
        assert failure.value.facts['ancestors'][0]['memory.current'] == str(15*1024**3)


def synthetic_ancestor_rows():
    """TEST_ONLY unlimited fixture, no assertion of a real cgroup/control authority."""
    common = {'cgroup.procs':{'device':7,'inode':17},'cgroup.threads':{'device':7,'inode':17},
        'cgroup.subtree_control':{'device':7,'inode':17}}
    return [{'path':'/sys/fs/cgroup/TEST_ONLY','device':7,'inode':17,
        'controls':dict(common,**{'memory.max':{'device':7,'inode':17},'memory.current':{'device':7,'inode':17}}),
        'subtree_control':'memory cpu cpuset pids','memory.max':'max','memory.current':'100'},
        {'path':'/sys/fs/cgroup','device':7,'inode':17,'controls':common,
        'subtree_control':'memory cpu cpuset pids','memory.max':None,'memory.current':None}]


def test_child_transition_never_weakens_supervisor_or_pinned_lifetime():
    import pytest
    child,namespace,state = synthetic_attached_child()
    child.identity.verify()
    child.identity.confirm_candidate()
    for field,value in (('uid',[0]*4),('uid',[17]*4),('gid',[17]*4),
                        ('start','TEST_ONLY-foreign-start'),('dead',True)):
        original = state[field]
        state[field] = value
        with pytest.raises(ValueError):child.identity.verify()
        state[field] = original
    supervisor = namespace['Identity'](100)
    state['uid'] = [17]*4
    with pytest.raises(ValueError,match='pinned process identity'):supervisor.verify()


def test_child_must_cross_exact_attach_transition_before_ready():
    import pytest
    child,namespace,state = synthetic_attached_child()
    # A newly pinned bootstrap cannot start with preemptively changed credentials.
    with pytest.raises(ValueError,match='trusted root bootstrap'):
        namespace['ChildIdentity'](100,65534,65534)
    state['uid'],state['gid'] = [0]*4,[0]*4
    identity = namespace['ChildIdentity'](100,65534,65534)
    with pytest.raises(ValueError,match='attach transition'):identity.confirm_candidate()
    state['uid'],state['gid'] = [65534]*4,[65534]*4
    with pytest.raises(ValueError,match='phase'):identity.verify()
    state['uid'],state['gid'] = [0]*4,[0]*4
    identity.begin_transition()
    state['gid'] = [65534]*4
    identity.verify()
    with pytest.raises(ValueError,match='incomplete'):identity.confirm_candidate()
    state['uid'] = [17]*4
    with pytest.raises(ValueError,match='unexpected'):identity.verify()
    state['uid'] = [65534]*4
    identity.confirm_candidate()
    identity.verify()


def test_running_full_leaf_requires_reserve_outside_leaf_not_inside_it(monkeypatch):
    import pytest
    leaf,files,_ = synthetic_budget_leaf(monkeypatch)
    files[leaf.parent_path+'/memory.current'] = str(14*1024**3)
    read = leaf.read
    leaf.read = lambda name:str(12*1024**3) if name in ('memory.current','memory.peak') else read(name)
    sample = leaf.sample(None,None)
    assert sample['reserve']['memory_available'] == 2*1024**3
    guardian.validate_resources(sample,{2,4},leaf.storage_paths,leaf.parent_path)
    with pytest.raises(guardian.ResourceAdmissionError):leaf.admit()  # A new phase needs the full14GiB.
    files[leaf.parent_path+'/memory.max'] = 'max'
    assert leaf.admit()['memory_available'] == 32*1024**3


def test_unknown_unreadable_or_changed_ancestor_refuses_with_raw_budget(monkeypatch):
    import pytest
    leaf,files,replaced = synthetic_budget_leaf(monkeypatch)
    files[leaf.parent_path+'/memory.max'] = 'max'
    leaf.admit()
    files[leaf.parent_path+'/memory.current'] = 'unknown'
    with pytest.raises(guardian.ResourceAdmissionError) as failure:leaf.sample(None,None)
    assert failure.value.facts['ancestors'][0]['memory.current'] == 'unknown'
    files[leaf.parent_path+'/memory.current'] = PermissionError('TEST_ONLY current unreadable')
    with pytest.raises(guardian.ResourceAdmissionError,match='unreadable'):leaf.admit()
    files[leaf.parent_path+'/memory.current'] = '100'
    replaced[0] = True
    with pytest.raises(guardian.ResourceAdmissionError,match='identity changed') as failure:leaf.admit()
    assert failure.value.facts['ancestors'][0]['inode'] == 18


def test_guardian_retains_bad_ancestor_sample_before_resource_refusal(monkeypatch):
    import pytest
    leaf,files,_ = synthetic_budget_leaf(monkeypatch)
    instance = guardian.Guardian.__new__(guardian.Guardian)
    instance.leaf,instance.child,instance.last_sample,instance.phase = leaf,None,None,'generate'
    records = []
    instance.emit = lambda event,**fields:records.append(dict(event=event,**fields))
    with pytest.raises(ValueError,match='reserve'):instance.sample()
    assert records[0]['event'] == 'resources'
    assert records[0]['facts']['reserve']['memory_available'] == 1024**3
    assert records[0]['facts']['reserve']['ancestors'][0]['memory.current'] == str(15*1024**3)


def test_low_backing_disk_is_retained_in_admission_and_sample(monkeypatch):
    import pytest
    from types import SimpleNamespace
    leaf,files,_ = synthetic_budget_leaf(monkeypatch)
    files[leaf.parent_path+'/memory.max'] = 'max'
    guardian.os.fstatvfs = lambda fd:SimpleNamespace(f_bavail=0,f_frsize=4096)
    with pytest.raises(guardian.ResourceAdmissionError) as failure:leaf.admit()
    assert failure.value.facts['disk_free'] == 0
    sample = leaf.sample(None,None)
    assert sample['reserve']['storage'][1]['disk_free'] == 0
    with pytest.raises(ValueError,match='reserve'):guardian.validate_resources(sample,{2,4},leaf.storage_paths,leaf.parent_path)
