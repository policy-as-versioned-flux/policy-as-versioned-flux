"""TEST_ONLY task/FD model; no proc, children, helpers or privileged operations."""
import ast
import importlib.util
import json
import os
from pathlib import Path
import stat
import sys
from types import SimpleNamespace
import pytest

BENCH=Path(__file__).parents[1]/'bench/pinned-candidate'
SPEC=importlib.util.spec_from_file_location('ci_sudo_test_module',BENCH/'linux_lease_control_ci.py')
ci=importlib.util.module_from_spec(SPEC);sys.modules[SPEC.name]=ci;SPEC.loader.exec_module(ci)
GUARD=ci.STORE+'/source/linux_guardian.py'

class Kernel:
    """Independent ownership table executing unchanged real Identity/protected_path bodies."""
    def __init__(self,sudo=1,uid=1001):
        self.nodes={10:dict(ppid=20,uid=[0]*4,exe='/usr/bin/python3.12',start='110')}
        for index in range(sudo):
            pid=20+index*10
            self.nodes[pid]=dict(ppid=pid+10,uid=[uid,0,0,0],exe='/usr/bin/sudo',start=str(100+pid))
        self.nodes[20+sudo*10]=dict(ppid=1,uid=[uid]*4,exe='/usr/bin/bash',start=str(120+sudo*10))
        self.files={path:self.info(i+90,stat.S_IFREG|(0o4755 if path.endswith('sudo') else 0o755))
                    for i,path in enumerate(('/usr/bin/python3.12','/usr/bin/sudo','/usr/bin/bash'))}
        self.fds={};self.next_fd=100;self.opened=0;self.closed=[];self.peak=0
        self.trace=[];self.clock=150.;self.attrs={};self.dead=set()
        self.open_fail=None;self.close_fail=None;self.read_fail=None
        self.status_override={};self.stat_override={};self.exe_override={};self.image_override={}
        self.paths_read=[];self.hook=lambda event:None
        self.guardian=self.guardian_module()
    @staticmethod
    def info(inode,mode):
        return SimpleNamespace(st_dev=1,st_ino=inode,st_mode=mode,st_uid=0,st_gid=0,st_nlink=1,
                               st_size=17,st_mtime_ns=100,st_ctime_ns=200)
    def event(self,event):self.trace.append(event);self.hook(event)
    def allocate(self,kind,pid=0,payload=b''):
        if self.open_fail and self.open_fail(kind,pid):raise OSError(13,'TEST_ONLY denied')
        fd=self.next_fd;self.next_fd+=1;self.fds[fd]=[kind,pid,payload,0]
        self.opened+=1;self.peak=max(self.peak,len(self.fds));self.event(('open',kind,pid,fd));return fd
    def close(self,fd):
        assert fd in self.fds,'closed an unowned/recycled descriptor'
        self.event(('close',self.fds[fd][0],self.fds[fd][1],fd))
        if self.close_fail and self.close_fail(fd):raise OSError(5,'TEST_ONLY ambiguous close')
        del self.fds[fd];self.closed.append(fd)
    def raw(self,pid,name):
        self.paths_read.append((pid,name));self.event(('raw',pid,name));node=self.nodes[pid]
        if self.read_fail and self.read_fail(pid,name):raise OSError(5,'TEST_ONLY read failure')
        if name=='status':return self.status_override.get(pid,f'Name:\tTEST_ONLY\nPid:\t{pid}\nPPid:\t{node["ppid"]}\nUid:\t'+'\t'.join(map(str,node['uid']))+'\n').encode()
        return self.stat_override.get(pid,f'{pid} (TEST_ONLY) '+' '.join(['S',str(node['ppid'])]+['0']*17+[node['start']])).encode()
    def open(self,path,flags,mode=0o777,*,dir_fd=None):
        if dir_fd is not None:
            assert self.fds[dir_fd][0]=='directory';pid=self.fds[dir_fd][1]
            if path=='exe':return self.allocate('image',pid)
            assert path in ('status','stat');return self.allocate('reader',pid,self.raw(pid,path))
        assert path.startswith('/proc/');return self.allocate('directory',int(path.split('/')[2]))
    def read(self,fd,count):
        kind,pid,raw,offset=self.fds[fd];assert kind=='reader'
        data=raw[offset:offset+count];self.fds[fd][3]+=len(data);return data
    def readlink(self,path,*,dir_fd=None):
        assert path==b'exe' and self.fds[dir_fd][0]=='directory'
        pid=self.fds[dir_fd][1];return self.exe_override.get(pid,self.nodes[pid]['exe']).encode()
    def fstat(self,fd):
        kind,pid,*_=self.fds[fd];assert kind=='image'
        return self.image_override.get(pid,self.files[self.nodes[pid]['exe']])
    def guardian_module(self):
        model=self
        class ModelPath:
            def __init__(self,value):self.value=str(value)
            def __str__(self):return self.value
            def is_absolute(self):return self.value.startswith('/')
            @property
            def parts(self):return Path(self.value).parts
            @property
            def parents(self):return tuple(ModelPath(str(p)) for p in Path(self.value).parents)
            def lstat(self):return model.files.get(self.value,model.info(1,stat.S_IFDIR|0o755))
            def read_text(self):
                _,_,pid,name=self.value.split('/');fd=model.allocate('internal-reader',int(pid))
                try:return model.raw(int(pid),name).decode()
                finally:model.close(fd)
        os_model=SimpleNamespace(pidfd_open=lambda pid,flags:model.allocate('pidfd',pid),close=self.close,
                                 listxattr=lambda path,**kw:self.attrs.get(str(path),[]))
        tree=ast.parse((BENCH/'linux_guardian.py').read_text())
        nodes=[n for n in tree.body if isinstance(n,(ast.ClassDef,ast.FunctionDef)) and n.name in ('Identity','parse_status','protected_path')]
        ns={'__file__':GUARD,'__name__':'fixed_ci_linux_guardian','Any':object,'Path':ModelPath,'os':os_model,'stat':stat,
            'select':SimpleNamespace(select=lambda r,w,x,t:([fd for fd in r if self.fds[fd][1] in self.dead],[],[]))}
        exec(compile(ast.Module(body=nodes,type_ignores=[]),GUARD,'exec'),ns);return SimpleNamespace(**ns)
    def install(self,mp):
        mp.setattr(os,'getpid',lambda:10);mp.setattr(os,'getppid',lambda:self.nodes[10]['ppid'])
        for name in ('open','close','read','readlink','fstat'):mp.setattr(os,name,getattr(self,name))
        mp.setattr(os,'listxattr',lambda path,**kw:self.attrs.get(str(path),[]),raising=False)
        mp.setattr(os,'O_PATH',0o10000000,raising=False)
        import time
        mp.setattr(time,'monotonic',lambda:self.clock)
    def run(self,monkeypatch):
        with monkeypatch.context() as patched:
            self.install(patched)
            return ci.ci_original_caller(self.guardian,1000.,pid=10,start='110')

def test_observed_sudo_shape_can_reach_matching_kernel_endpoint(monkeypatch):
    model=Kernel();endpoint,record=model.run(monkeypatch)
    assert endpoint.pid==30 and endpoint.uid==[1001]*4
    assert record['status']=='VERIFIED' and record['reason']=='matched-one-sudo'
    assert record['custody']['opened']=={'minimum':48,'maximum':48}
    assert record['custody']['closed']=={'minimum':47,'maximum':47}
    assert model.opened==48 and len(model.closed)==47 and model.peak==9
    assert list(model.fds)==[endpoint.fd]

@pytest.mark.parametrize('sudo,uid,expected,peak',[(1,2002,30,9),(2,1001,40,12),(2,2002,40,12)])
def test_one_or_two_sudo_including_nested_same_user(monkeypatch,sudo,uid,expected,peak):
    model=Kernel(sudo,uid);endpoint,record=model.run(monkeypatch)
    assert endpoint.pid==expected and record['invoker_uid']==uid
    assert record['custody']['opened']['minimum']==(48 if sudo==1 else 64)
    assert len(model.fds)==1 and model.peak==peak and len(model.closed)==model.opened-1
    assert all('monitor' not in json.dumps(snapshot) for snapshot in record['snapshots'])
    ci.validate_ci_caller_record(record)


def refused(model,monkeypatch,reason=None):
    with pytest.raises(ci.CiCallerError) as raised:model.run(monkeypatch)
    facts=raised.value.facts
    assert facts['status']=='REFUSED' and facts['selected_pid'] is facts['invoker_uid'] is None
    assert facts['custody']['transferred_to_coordinator']==0
    if reason:assert facts['reason']==reason
    ci.validate_ci_caller_record(facts)
    assert len(model.fds)<=facts['custody']['unresolved_ownership_upper_bound']
    assert model.peak<=12 and facts['custody']['peak_live_upper_bound']<=12
    return facts

@pytest.mark.parametrize('vector',[[0]*4,[0,1001,0,0],[1001,0,1001,0],[1001,0,0,1001],[1001]*4])
def test_other_sudo_uid_vectors_never_match(monkeypatch,vector):
    model=Kernel();model.nodes[20]['uid']=vector;refused(model,monkeypatch,'bad-uid')

@pytest.mark.parametrize('sudo,change,reason',[
    (0,lambda m:None,'unsupported-shape'),
    (2,lambda m:m.nodes[30].update(uid=[2002,0,0,0]),'uid-mismatch'),
    (1,lambda m:m.nodes[30].update(uid=[2002]*4),'uid-mismatch'),
    (1,lambda m:m.nodes[30].update(uid=[0]*4),'uid-mismatch'),
    (1,lambda m:m.nodes[20].update(exe='/usr/bin/bash'),'unsupported-shape'),
    (1,lambda m:m.nodes[20].update(ppid=1),'no-caller'),
    (1,lambda m:m.nodes[20].update(ppid=10),'pid-loop'),
    (1,lambda m:m.nodes[20].update(ppid=20),'pid-loop'),
    (3,lambda m:None,'transition-limit')])
def test_closed_parent_grammar_no_skipping_or_fallback(monkeypatch,sudo,change,reason):
    model=Kernel(sudo);change(model);facts=refused(model,monkeypatch,reason)
    if sudo==3:
        assert len(facts['snapshots'])==4
        assert all(pid!=50 for pid,name in model.paths_read)

@pytest.mark.parametrize('text',['1001 0 0','1001 0 0 0 0','True 0 0 0','-1 0 0 0','4294967295 0 0 0','4294967296 0 0 0','01 0 0 0'])
def test_malformed_raw_uids_are_retained_and_refused(monkeypatch,text):
    model=Kernel();closed=[0]
    def hook(event):
        if event[:3]==('close','internal-reader',20):
            closed[0]+=1
            if closed[0]==4:model.status_override[20]='Pid: 20\nPPid: 30\nUid: '+text+'\n'
    model.hook=hook
    facts=refused(model,monkeypatch)
    assert facts['snapshots'][-1]['requested_pid']==20
    assert facts['snapshots'][-1]['raw']['status']['complete'] is True
    assert facts['snapshots'][-1]['identity'] is None

@pytest.mark.parametrize('field,value', [('st_mode',stat.S_IFREG|0o755),('st_mode',stat.S_IFREG|0o6755),
    ('st_uid',1001),('st_mode',stat.S_IFREG|0o4777),('st_nlink',2),('st_mode',stat.S_IFLNK|0o4755)])
def test_sudo_protected_metadata_is_not_relaxed(monkeypatch,field,value):
    model=Kernel();setattr(model.files['/usr/bin/sudo'],field,value);refused(model,monkeypatch)

@pytest.mark.parametrize('path,attr',[('/usr/bin/sudo','security.capability'),('/usr/bin/sudo','system.posix_acl_access'),
    ('/usr','system.posix_acl_default'),('/usr/bin/bash','security.capability')])
def test_caps_and_acl_refuse_every_ancestry_role(monkeypatch,path,attr):
    model=Kernel();model.attrs[path]=[attr];refused(model,monkeypatch)

@pytest.mark.parametrize('mode',[stat.S_IFREG|0o4755,stat.S_IFDIR|0o755,stat.S_IFREG|0o777])
def test_endpoint_cannot_be_privileged_or_mutable(monkeypatch,mode):
    model=Kernel();model.files['/usr/bin/bash'].st_mode=mode;refused(model,monkeypatch)

@pytest.mark.parametrize('path',['/usr/bin/sudo (deleted)','/usr/bin/../bin/sudo','relative','/usr/bin/TEST_ONLY-other'])
def test_noncanonical_or_unknown_executable_never_admitted(monkeypatch,path):
    model=Kernel();model.exe_override[20]=path;refused(model,monkeypatch)

@pytest.mark.parametrize('field,value',[('st_ino',999),('st_dev',99),('st_size',100),('st_ctime_ns',99)])
def test_actual_image_must_match_named_file(monkeypatch,field,value):
    import copy
    model=Kernel();image=copy.copy(model.files['/usr/bin/sudo']);setattr(image,field,value);model.image_override[20]=image
    refused(model,monkeypatch,'executable-drift')

@pytest.mark.parametrize('change,reason',[
    (lambda m:m.nodes[20].update(start='999'),'identity-drift'),
    (lambda m:m.nodes[20].update(ppid=99),'parent-drift'),
    (lambda m:m.nodes[20].update(uid=[2002,0,0,0]),'identity-drift'),
    (lambda m:m.nodes[20].update(exe='/usr/bin/bash'),'executable-drift'),
    (lambda m:setattr(m.files['/usr/bin/sudo'],'st_size',99),'executable-drift'),
    (lambda m:m.dead.add(20),'identity-drift')])
def test_second_pass_rechecks_held_task_and_image(monkeypatch,change,reason):
    model=Kernel();seen=[False]
    def hook(event):
        if event[:3]==('close','image',30) and not seen[0]:seen[0]=True;change(model)
    model.hook=hook;refused(model,monkeypatch,reason)


def test_final_liveness_sweep_is_required(monkeypatch):
    model=Kernel()
    def hook(event):
        if event[:3]==('close','image',10):model.dead.add(20)
    model.hook=hook;facts=refused(model,monkeypatch,'identity-drift')
    assert facts['final_live']==[True,False,True]

@pytest.mark.parametrize('kind',['directory','pidfd','reader','image'])
def test_missing_kernel_observation_does_not_skip(monkeypatch,kind):
    model=Kernel();model.open_fail=lambda actual,pid:actual==kind and pid==20
    facts=refused(model,monkeypatch);assert any(f['errno']==13 for f in facts['faults'])

@pytest.mark.parametrize('target', ['status','stat','exe'])
def test_raw_caps_are_bounded_prefixes_not_complete_facts(monkeypatch,target):
    model=Kernel();cap={'status':65536,'stat':8192,'exe':4096}[target]
    if target=='exe':model.exe_override[20]='x'*(cap+1)
    else:
        closed=[0]
        def hook(event):
            if event[:3]==('close','internal-reader',20):
                closed[0]+=1
                if closed[0]==4:getattr(model,target+'_override')[20]='x'*(cap+1)
        model.hook=hook
    facts=refused(model,monkeypatch,'evidence-overflow')
    raw=facts['snapshots'][-1]['raw'][target]
    assert raw['bytes']==cap and raw['complete'] is False


def test_only_fixed_installed_guardian_is_accepted(monkeypatch):
    model=Kernel();model.guardian.__file__='/tmp/TEST_ONLY-guardian.py'
    facts=refused(model,monkeypatch,'source-pin');assert model.opened==0 and facts['snapshots']==[]

@pytest.mark.parametrize('binding',[{'pid':11,'start':'110'},{'pid':10,'start':'999'},{'pid':True,'start':'110'}])
def test_protected_start_binding_cannot_select_other_process(monkeypatch,binding):
    model=Kernel()
    with monkeypatch.context() as mp:
        model.install(mp)
        with pytest.raises(ci.CiCallerError):ci.ci_original_caller(model.guardian,1000.,**binding)
    assert not model.fds
    assert all(pid==10 for pid,name in model.paths_read)

@pytest.mark.parametrize('event_kind',['raw','open','close'])
def test_same_original_deadline_bounds_all_acquisition_stages(monkeypatch,event_kind):
    model=Kernel()
    def hook(event):
        if event[0]==event_kind:model.clock=1000.
    model.hook=hook;facts=refused(model,monkeypatch,'deadline');assert facts['deadline']==1000.


def test_opaque_constructor_failure_keeps_intervals_and_no_blind_close(monkeypatch):
    model=Kernel();count=[0]
    def failure(pid,name):
        if pid==20:count[0]+=1
        return pid==20 and count[0]==3
    model.read_fail=failure;facts=refused(model,monkeypatch)
    assert facts['custody']['opened']['minimum']<model.opened<=facts['custody']['opened']['maximum']
    assert facts['custody']['closed']['minimum']<=len(model.closed)<=facts['custody']['closed']['maximum']
    assert facts['custody']['close_attempts'] is None and facts['custody']['unresolved_ownership_upper_bound']>0


def test_constructor_already_closed_pidfd_is_not_closed_again(monkeypatch):
    model=Kernel();count=[0]
    def hook(event):
        if event[:3]==('raw',20,'status'):
            count[0]+=1
            if count[0]==2:model.nodes[20]['uid']=[2002,0,0,0]
    model.hook=hook;facts=refused(model,monkeypatch)
    assert facts['custody']['close_attempts'] is None
    assert len(model.closed)==len(set(model.closed))


def test_close_failure_reserves_slot_and_other_handles_close_once(monkeypatch):
    model=Kernel();failed=[]
    def fault(fd):
        if model.fds[fd][0]=='image' and not failed:failed.append(fd);return True
        return False
    model.close_fail=fault;facts=refused(model,monkeypatch,'descriptor-close')
    assert facts['custody']['close_failures']==1 and facts['custody']['unresolved_ownership_upper_bound']==1
    assert list(model.fds)==failed
    assert sum(event[0]=='close' and event[3]==failed[0] for event in model.trace)==1


def test_environment_never_supplies_uid_or_route(monkeypatch):
    monkeypatch.setenv('SUDO_UID','2002');monkeypatch.setenv('SUDO_USER','TEST_ONLY');monkeypatch.setenv('CI_CALLER','VERIFIED')
    model=Kernel();endpoint,record=model.run(monkeypatch)
    assert endpoint.uid==[1001]*4 and record['invoker_uid']==1001


def test_unobserved_parent_of_actual_one_row_diagnostic_is_not_filled(monkeypatch):
    model=Kernel();model.open_fail=lambda kind,pid:pid==30
    facts=refused(model,monkeypatch)
    assert facts['next_pid']==30 and len(facts['snapshots'])==2
    assert facts['snapshots'][1]['identity']['uid']==[1001,0,0,0]

@pytest.mark.parametrize('mutation',[
    lambda r:r.update(extra=1),lambda r:r.update(started=True),lambda r:r.update(deadline=float('nan')),
    lambda r:r['custody'].update(opened={'minimum':12,'maximum':12}),
    lambda r:r['custody'].update(peak_live_upper_bound=13),
    lambda r:r['custody'].update(closed={'minimum':False,'maximum':47}),
    lambda r:r['snapshots'][0]['raw']['status'].update(base64='!'),
    lambda r:r['snapshots'][0]['raw']['status'].update(sha256='0'*64),
    lambda r:r['snapshots'][0]['raw']['status'].update(bytes=1),
    lambda r:r['snapshots'][0]['raw']['status'].update(complete=False),
    lambda r:r['snapshots'][0].update(extra=None),
    lambda r:r['snapshots'][0]['identity'].update(uid=[True,0,0,0]),
    lambda r:r['snapshots'][0]['identity'].update(start='0110'),
    lambda r:r['snapshots'][0]['executable'].update(extra=0),
    lambda r:r.update(final_live=[True,1,True]),lambda r:r.update(faults=[{}]),
    lambda r:r['snapshots'].pop(),lambda r:r['custody'].update(transferred_to_coordinator=0)])
def test_passive_record_checker_rejects_tamper_and_false_counts(monkeypatch,mutation):
    model=Kernel();endpoint,record=model.run(monkeypatch);mutation(record)
    with pytest.raises((ValueError,TypeError)):ci.validate_ci_caller_record(record)


def test_duplicate_json_fields_refuse_before_structural_check():
    with pytest.raises(ValueError):json.loads('{"status":"VERIFIED","status":"REFUSED"}',object_pairs_hook=ci.unique_object)


def test_passive_records_have_no_import_or_authority_route(monkeypatch):
    model=Kernel()
    with monkeypatch.context() as mp:
        model.install(mp)
        with pytest.raises(TypeError):ci.ci_original_caller(model.guardian,1000.,pid=10,start='110',record={'status':'VERIFIED','selected_pid':30})
    assert model.opened==0


def test_three_sudo_distinct_file_is_refused_without_fourth_ancestor(monkeypatch):
    model=Kernel(2)
    import copy
    def hook(event):
        if event[:3]==('open','image',30):
            image=copy.copy(model.files['/usr/bin/sudo']);image.st_ino=999;model.image_override[30]=image
    model.hook=hook;refused(model,monkeypatch,'executable-drift')


def test_raw_status_and_stat_parent_disagreement_refuses(monkeypatch):
    model=Kernel();model.status_override[20]='Pid: 20\nPPid: 99\nUid: 1001 0 0 0\n'
    refused(model,monkeypatch,'parent-drift')


def test_raw_pid_disagreement_refuses(monkeypatch):
    model=Kernel();model.status_override[20]='Pid: 21\nPPid: 30\nUid: 1001 0 0 0\n'
    refused(model,monkeypatch,'identity-drift')


def test_closed_raw_snapshot_cannot_be_stale_proc_directory(monkeypatch):
    model=Kernel();count=[0]
    def hook(event):
        if event[:3]==('close','internal-reader',20):
            count[0]+=1
            if count[0]==4:model.nodes[20]['start']='999'
    model.hook=hook;refused(model,monkeypatch,'identity-drift')


def test_live_and_cumulative_caps_refuse_before_any_extra_open(monkeypatch):
    model=Kernel()
    with monkeypatch.context() as mp:
        model.install(mp)
        route=ci._CallerRoute(model.guardian,1000.)
        route.owned=set(range(12));route.open_max=12
        with pytest.raises(ValueError):route.open('/proc/20',os.O_RDONLY)
        route.owned=set();route.open_min=route.open_max=64
        with pytest.raises(ValueError):route.open('/proc/20',os.O_RDONLY)
    assert model.opened==0


def test_reverse_pass_releases_old_image_before_next_temporary_or_image(monkeypatch):
    model=Kernel(2);model.run(monkeypatch)
    assert model.peak==12
    # At maximum retention, the next FD event must release the old image.
    active={};reached=False
    for event in model.trace:
        if event[0]=='open':
            if len(active)==12:pytest.fail('opened a thirteenth owned handle')
            active[event[3]]=event[1]
            if len(active)==12:reached=True
        elif event[0]=='close':del active[event[3]]
    assert reached and list(active.values())==['pidfd']


def test_first_read_error_survives_a_secondary_close_fault(monkeypatch):
    model=Kernel();count=[0]
    def hook(event):
        if event[:3]==('close','internal-reader',20):
            count[0]+=1
            if count[0]==4:
                model.close_fail=lambda fd:model.fds[fd][0]=='reader'
    model.hook=hook
    # A bounded raw read fails after opening its descriptor, then close also fails.
    model.close_fail=lambda fd:model.fds[fd][0]=='reader'
    def read(fd,count):raise OSError(22,'TEST_ONLY primary raw read')
    model.read=read
    facts=refused(model,monkeypatch,'descriptor-close')
    assert facts['faults'][0]['errno']==22
    assert any(f['errno']==5 for f in facts['faults'])


def test_coordinator_four_opens_are_real_and_outside_frozen_route_counts(monkeypatch):
    model=Kernel(2);endpoint,record=model.run(monkeypatch);memory={};base={}
    original_open=model.open;original_read=model.read;original_fstat=model.fstat
    class EvidencePath:
        def __init__(self,*parts):self.value='/'.join(str(p).rstrip('/') for p in parts)
        def __str__(self):return self.value
        @property
        def name(self):return self.value.rsplit('/',1)[-1]
        def __truediv__(self,part):return EvidencePath(self.value,part)
        def mkdir(self,**kwargs):assert kwargs=={'mode':0o700}
    def opened(path,flags,mode=0o777,*,dir_fd=None):
        text=str(path)
        if text.startswith(ci.STORE):
            if flags & os.O_WRONLY:
                assert mode==0o400 and text not in memory;memory[text]=b''
                return model.allocate('evidence-writer',payload=text.encode())
            return model.allocate('reader',payload=memory[text])
        return original_open(path,flags,mode,dir_fd=dir_fd)
    def write(fd,raw):
        kind,pid,payload,offset=model.fds[fd];assert kind=='evidence-writer'
        memory[payload.decode()]+=raw;return len(raw)
    def protected_read(path,expected,maximum):
        # Protected filesystem transport is the OS boundary here; actual caller
        # parser/record checks and actual Identity.verify remain production code.
        fd=opened(path,os.O_RDONLY)
        try:
            raw=original_read(fd,maximum+1);assert ci.sha(raw)==expected and len(raw)<=maximum;return raw
        finally:model.close(fd)
    g=SimpleNamespace(protected_read=protected_read)
    ci.validate_ci_caller_record(record)
    with monkeypatch.context() as mp:
        model.install(mp);mp.setattr(os,'open',opened);mp.setattr(os,'write',write);mp.setattr(os,'fsync',lambda fd:None)
        mp.setattr(ci,'Path',EvidencePath)
        ci.persist_observation(g,base,'suite/caller.json',record,budget=ci.SuiteBudget(100.,1000.))
        endpoint.verify()
    assert model.opened==68 and len(model.closed)==67 and len(model.fds)==1
    assert record['custody']['opened']=={'minimum':64,'maximum':64}
    assert record['custody']['closed']=={'minimum':63,'maximum':63}
    assert json.loads(base['suite/caller.json'])==record


def test_production_privileged_closure_remains_refused():
    model=Kernel()
    with pytest.raises(ValueError,match='without privilege'):model.guardian.protected_path('/usr/bin/sudo',True)


def test_inherited_temporary_close_fault_is_not_hidden_or_retried(monkeypatch):
    model=Kernel();failed=[]
    def fault(fd):
        if model.fds[fd][:2]==['internal-reader',20] and not failed:failed.append(fd);return True
        return False
    model.close_fail=fault;facts=refused(model,monkeypatch)
    assert facts['custody']['close_attempts'] is None
    assert facts['custody']['unresolved_ownership_upper_bound']>=1
    assert sum(event[0]=='close' and event[3]==failed[0] for event in model.trace)==1
    assert facts['faults'][0]['errno']==5

@pytest.mark.parametrize('claim',['monitor_role','installed_sudo_version'])
def test_documentation_or_role_labels_cannot_enrol_observed_caller(monkeypatch,claim):
    model=Kernel(2);endpoint,record=model.run(monkeypatch);record[claim]='TEST_ONLY-unsupported-claim'
    with pytest.raises(ValueError):ci.validate_ci_caller_record(record)
