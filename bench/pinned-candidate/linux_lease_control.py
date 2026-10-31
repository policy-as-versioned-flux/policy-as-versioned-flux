"""Fixed TEST_ONLY native Linux lease control. Import is inert.

No model, production profile, acquired inference runtime or permission is created.
Installation and actual privileged execution require separate reviewed authority.
"""
from __future__ import annotations

from typing import Any
import math
import ctypes
import errno
import grp
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import platform
import pwd
import select
import signal
import stat
import struct
import sys
import time

SCHEMA = 'TEST_ONLY-linux-lease-control/v1'
SCENARIOS = ('baseline','boundaries','resources','supervisor-loss','guardian-loss','invalid-evidence')
STORE = '/var/lib/policy-as-versioned-flux-linux-control'
ANCHOR = STORE+'/host.json'
ATTEMPT_SECONDS, CLEANUP_SECONDS, TOTAL_SECONDS = 60,10,900
DEADLINE_SECONDS = 30
MAX_FILES, MAX_BYTES = 4096,256*1024**2
HANDOFFS = ('raw-clone','attached','dropped','armed','ready','descendants')
CHECKS = {'baseline':('paired','limits','network','sources'),
    'boundaries':('writes','privilege','isolation','process','network','exec-inheritance'),
    'resources':('limits','affinity','tmpfs','oom','pids'),
    'supervisor-loss':('descendants','guardian-survived','supervisor-dead'),
    'guardian-loss':HANDOFFS,
    'invalid-evidence':('eof','deadline','ready','source','overflow','observer','incomplete','stale-lock')}
CASES={'baseline':('standard',),'boundaries':('standard',),'resources':('standard','oom','pids'),
       'supervisor-loss':('descendants',),'guardian-loss':HANDOFFS,
       'invalid-evidence':CHECKS['invalid-evidence']}
WRITE_PATHS=('/TEST_ONLY-root-write','/app/actor-config.json','/app/lease.json','/app/paths.json',
    '/app/linux_lease_control_child.py','/evidence/write','/sys/fs/cgroup/cgroup.procs','/sys/fs/cgroup/memory.max')


class CiPrerequisiteUnavailable(ValueError):
    """Known initial capacity absence; carries the actual protected readings."""
    def __init__(self,message:str,facts:dict[str,Any]):
        super().__init__(message);self.facts=facts


class CiPrincipalRejected(ValueError):
    """CI-only diagnostic for an observed refusal, never neutral absence."""
    def __init__(self, reason:str, facts:dict[str,Any]):
        super().__init__(reason)
        self.facts=facts


def finite(value: Any) -> float:
    if type(value) not in (int,float) or not math.isfinite(value):
        raise ValueError('finite actual monotonic timestamp required')
    return float(value)


def network_ok(value: Any) -> bool:
    return (isinstance(value,dict) and value.get('state')=={'NoNewPrivs':'1','Seccomp':'2'}
        and isinstance(value.get('probes'),list) and len(value['probes'])==8
        and {row.get('probe') for row in value['probes'] if isinstance(row,dict)}=={
            'ipv4/tcp','ipv4/udp','ipv6/tcp','ipv6/udp','socket-syscall','io-uring','pidfd-getfd','unix-socketpair'}
        and all(isinstance(row,dict) and type(row.get('errno')) is int and row['errno']==errno.EPERM
                for row in value['probes']))


def denial_ok(value: Any) -> bool:
    return isinstance(value,dict) and value.get('denied') is True and type(value.get('errno')) is int and value['errno'] in (
        errno.EPERM,errno.EACCES,errno.EROFS,errno.ENOENT)


def boundary_checks(value: Any,host_pids:list[int])->dict[str,bool]:
    if not isinstance(value,dict):return dict.fromkeys(('writes','privilege','isolation','process'),False)
    writes=value.get('writes',[])
    def group(name:str,keys:tuple[str,...])->bool:
        actual=value.get(name)
        return (isinstance(actual,dict) and set(actual)==set(keys)
            and all(denial_ok(row) and row['errno']==errno.EPERM for row in actual.values()))
    absent=value.get('host_proc_absent')
    return {'writes':isinstance(writes,list) and len(writes)==len(WRITE_PATHS)
        and {row.get('path') for row in writes if isinstance(row,dict)}==set(WRITE_PATHS)
        and all(denial_ok(row) for row in writes),
        'privilege':group('privilege',('setuid','setgid','setgroups','capset','death-signal')),
        'isolation':group('isolation',('mount','unshare','setns')),
        'process':group('process',('ptrace','process_vm_writev','pidfd_getfd'))
            and isinstance(absent,dict) and set(absent)=={str(pid) for pid in host_pids}
            and all(denied is True for denied in absent.values())}


def kill_owned(identity: Any) -> None:
    if identity.dead():return
    identity.verify()
    signal.pidfd_send_signal(identity.fd,signal.SIGKILL)


def read_bounded(fd:int,deadline:float,maximum:int=4096)->bytes:
    raw=bytearray()
    while time.monotonic()<deadline:
        if select.select([fd],[],[],min(.05,max(0,deadline-time.monotonic())))[0]:
            part=os.read(fd,1)
            if not part:raise ValueError('owned fixture bootstrap EOF')
            raw.extend(part)
            if len(raw)>maximum:raise ValueError('owned fixture bootstrap cap exceeded')
            if part==b'\n':return bytes(raw)
    raise ValueError('owned fixture bootstrap deadline exhausted')


def reap_bootstrap(pid:int,fd:int,deadline:float)->None:
    while time.monotonic()<deadline:
        waited,_=os.waitpid(pid,os.WNOHANG)
        if waited:
            if not select.select([fd],[],[],0)[0]:raise ValueError('reaped bootstrap pidfd still live')
            return
        select.select([fd],[],[],.02)
    raise ValueError('owned bootstrap teardown deadline exhausted')


def drop_fixture(g: Any, uid:int, gid:int, outer_fd:int)->None:
    os.setgroups([]);os.setresgid(gid,gid,gid);os.setresuid(uid,uid,uid)
    g.prctl(4,0);g.prctl(1,signal.SIGKILL)
    g.wait_guardian(outer_fd)
    if os.getresuid()!=(uid,)*3 or os.getresgid()!=(gid,)*3 or os.getgroups():
        os._exit(125)


def close_except(keep:set[int])->None:
    for item in Path('/proc/self/fd').iterdir():
        fd=int(item.name)
        if fd>2 and fd not in keep:
            try:os.close(fd)
            except OSError as error:
                if error.errno!=errno.EBADF:raise


def start_fixture(g: Any, host:dict[str,Any], profile:dict[str,Any], case:str,
                  deadline:float, caller:Any)->dict[str,Any]:
    """Own both fixture processes; guardian pins supervisor only AFTER UID drop."""
    command_r,command_w=os.pipe2(os.O_CLOEXEC)
    event_r,event_w=os.pipe2(os.O_CLOEXEC)
    boot_r,boot_w=os.pipe2(os.O_CLOEXEC)
    terminal_r,terminal_w=os.pipe2(os.O_CLOEXEC)
    outer_fd=os.pidfd_open(os.getpid(),0)
    outer_pid=os.getpid()
    caller_gid=int(g.parse_status(Path(f'/proc/{caller.pid}/status').read_text())['Gid'].split()[0])
    supervisor=os.fork()
    if supervisor==0:
        try:
            control_r,control_w=os.pipe2(os.O_CLOEXEC)
            released_r,released_w=os.pipe2(os.O_CLOEXEC)
            guardian=os.fork()
            if guardian==0:
                try:
                    os.dup2(control_r,0);os.dup2(event_w,1);os.dup2(event_w,2)
                    close_except({released_r,outer_fd,terminal_r})
                    g.prctl(4,0)
                    if select.select([released_r,outer_fd],[],[],10)[0]!=[released_r] or os.read(released_r,1)!=b'G':
                        os._exit(125)
                    os.close(released_r);os.close(outer_fd)
                    supervisor_pid=os.getppid()
                    actual=g.Identity.read(supervisor_pid)
                    request={'authority':g.digest(g.protected_read(ANCHOR)),
                        'profile_sha256':g.digest(g.canonical(profile['config'])),
                        'deadline_monotonic':deadline,'supervisor_pid':supervisor_pid,
                        'supervisor_start':actual['start'],
                        'request':{'input':{'scenario':profile['config']['scenario'],'case':case,
                            'host_pids':[outer_pid,os.getppid(),os.getpid(),caller.pid],
                            'host_cpus':sorted(os.sched_getaffinity(0))},
                            'prompt_utf8':'TEST_ONLY fixed lease control'}}
                    pinned=g.supervisor_identity(host,request)
                    os.setsid();signal.signal(signal.SIGHUP,signal.SIG_IGN)
                    signal.signal(signal.SIGPIPE,signal.SIG_IGN);os.set_blocking(1,False)
                    lease=control_guardian(g,request,host,profile,pinned)
                    lease.control_case=case
                    lease.terminal_fd=terminal_r
                    lease.handoff=g.TrustedHandoff(0,1,lease.wire,lease.work_deadline,pinned)
                    os._exit(lease.run())
                except BaseException as failure:
                    try:os.write(1,g.canonical({'event':'control-bootstrap-failure',
                        'error':type(failure).__name__+': '+str(failure)[:2000]})+b'\n')
                    except OSError:pass
                    os._exit(126)
            os.close(control_r);os.close(released_r)
            close_except({command_r,boot_w,control_w,released_w,outer_fd})
            before=g.Identity.read(os.getpid())
            os.write(boot_w,g.canonical({'stage':'forked','supervisor_pid':os.getpid(),
                'start':before['start'],'guardian_pid':guardian})+b'\n')
            release=select.select([command_r,outer_fd],[],[],min(10,max(0,deadline-time.monotonic())))[0]
            if outer_fd in release or command_r not in release or os.read(command_r,1)!=b'D':os._exit(125)
            drop_fixture(g,caller.uid[0],caller_gid,outer_fd)
            # No Identity snapshot exists for this supervisor before this exact
            # drop. Strict supervisor Identity gains NO transition exception.
            state=g.Identity.read(os.getpid())
            os.write(boot_w,g.canonical({'stage':'dropped','supervisor_pid':os.getpid(),'start':state['start'],'guardian_pid':guardian})+b'\n')
            os.close(boot_w)
            os.write(released_w,b'G');os.close(released_w)
            control_eof=False
            while time.monotonic()<deadline:
                ready=select.select([command_r,outer_fd],[],[],.05)[0]
                if outer_fd in ready:break
                if command_r in ready:
                    value=os.read(command_r,1)
                    if not value:control_eof=True;break
                    if value!=b'C':raise ValueError('closed fixed supervisor protocol')
                    os.write(control_w,value)
            os.close(control_w)
            if control_eof:
                # Isolate actual guardian control EOF from supervisor death.
                # The outer observer later kills/reaps this exact fixture.
                select.select([outer_fd],[],[],max(0,deadline-time.monotonic()))
            # Guardian must remain independently alive after supervisor loss.
            # Normal lifetime can be reaped by the root subreaper after we exit.
            os._exit(0)
        except BaseException as failure:
            try:os.write(boot_w,g.canonical({'stage':'failure',
                'error':type(failure).__name__+': '+str(failure)[:2000]})+b'\n')
            except OSError:pass
            os._exit(126)
    os.close(command_r);os.close(event_w);os.close(boot_w);os.close(outer_fd);os.close(terminal_r)
    bootstrap_fd=os.pidfd_open(supervisor,0)
    bootstrap_start=g.Identity.read(supervisor)['start']
    pinned_guardian=pinned_supervisor=None
    try:
        data=json.loads(read_bounded(boot_r,deadline))
        if data.get('stage')=='failure':raise ValueError('actual fixture bootstrap: '+str(data.get('error')))
        if (data.get('stage')!='forked' or data.get('supervisor_pid')!=supervisor
                or data.get('start')!=bootstrap_start or g.Identity.read(supervisor)['uid']!=[0]*4):
            raise ValueError('owned pre-drop fixture bootstrap identity mismatch')
        pinned_guardian=g.Identity(data['guardian_pid'])
        if pinned_guardian.uid!=[0]*4 or pinned_guardian.ppid!=supervisor:
            raise ValueError('fixture guardian ownership mismatch')
        os.write(command_w,b'D')
        after=json.loads(read_bounded(boot_r,deadline))
        if after.get('stage')=='failure':raise ValueError('actual fixture drop: '+str(after.get('error')))
        if after!={**data,'stage':'dropped'}:raise ValueError('fixed fixture drop handoff changed identity')
        pinned_supervisor=g.Identity(supervisor,bootstrap_start)
        if pinned_supervisor.uid!=[caller.uid[0]]*4:
            raise ValueError('fixture supervisor did not finish exact UID drop')
        os.set_blocking(event_r,False)
        return {'supervisor':pinned_supervisor,'guardian':pinned_guardian,
                'command':command_w,'events':event_r,'terminal':terminal_w}
    except BaseException:
        # This is a direct owned-fork kernel handle used only before the strict
        # post-drop Identity exists. It never grants a credential-transition
        # exception to production supervisor Identity.
        if not select.select([bootstrap_fd],[],[],0)[0]:
            if g.Identity.read(supervisor)['start']!=bootstrap_start:raise ValueError('owned bootstrap PID/start changed')
            signal.pidfd_send_signal(bootstrap_fd,signal.SIGKILL)
        reap_bootstrap(supervisor,bootstrap_fd,deadline)
        if pinned_guardian is not None:
            kill_owned(pinned_guardian);reaped_owned(pinned_guardian,deadline);pinned_guardian.close()
        if pinned_supervisor is not None:pinned_supervisor.close()
        for fd in (command_w,event_r,terminal_w):os.close(fd)
        raise
    finally:os.close(boot_r);os.close(bootstrap_fd)


def start_sentinel(g:Any,caller:Any,deadline:float)->Any:
    ready_r,ready_w=os.pipe2(os.O_CLOEXEC)
    release_r,release_w=os.pipe2(os.O_CLOEXEC)
    outer_fd=os.pidfd_open(os.getpid(),0)
    gid=int(g.parse_status(Path(f'/proc/{caller.pid}/status').read_text())['Gid'].split()[0])
    pid=os.fork()
    if pid==0:
        try:
            close_except({ready_w,outer_fd,release_r})
            ready=select.select([release_r,outer_fd],[],[],min(10,max(0,deadline-time.monotonic())))[0]
            if outer_fd in ready or release_r not in ready or os.read(release_r,1)!=b'D':os._exit(125)
            os.close(release_r)
            drop_fixture(g,caller.uid[0],gid,outer_fd)
            os.write(ready_w,b'S\n');os.close(ready_w)
            select.select([outer_fd],[],[],max(0,deadline-time.monotonic()))
        finally:os._exit(0)
    os.close(ready_w);os.close(outer_fd);os.close(release_r)
    bootstrap_fd=os.pidfd_open(pid,0)
    bootstrap_start=g.Identity.read(pid)['start']
    try:
        os.write(release_w,b'D');os.close(release_w)
        if read_bounded(ready_r,deadline)!=b'S\n':raise ValueError('sentinel drop not confirmed')
        identity=g.Identity(pid)
        if identity.uid!=[caller.uid[0]]*4:raise ValueError('sentinel UID differs')
        return identity
    except BaseException:
        if not select.select([bootstrap_fd],[],[],0)[0]:
            if g.Identity.read(pid)['start']!=bootstrap_start:raise ValueError('owned sentinel bootstrap identity changed')
            signal.pidfd_send_signal(bootstrap_fd,signal.SIGKILL)
        reap_bootstrap(pid,bootstrap_fd,deadline)
        raise
    finally:os.close(ready_r);os.close(bootstrap_fd)


class Recovery:
    """Fixed root observer authority over precisely one owned fixture leaf."""
    def __init__(self,g:Any,host:dict[str,Any],lease:str,facts:dict[str,Any]):
        if len(lease)!=48 or any(c not in '0123456789abcdef' for c in lease):raise ValueError('owned lease identity missing')
        self.g,self.host,self.lease=g,host,lease
        self.name='lease-'+lease
        if facts.get('name')!=self.name:raise ValueError('owned leaf name differs')
        self.parent=host['cgroup_parent'];g.protected_path(self.parent,False)
        self.parentfd=os.open(self.parent,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW|os.O_CLOEXEC)
        self.parent_info=os.fstat(self.parentfd)
        self.fd=os.open(self.name,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW|os.O_CLOEXEC,dir_fd=self.parentfd)
        self.info=os.fstat(self.fd)
        self.mount=int(Path(f'/proc/self/fdinfo/{self.fd}').read_text().split('mnt_id:')[1].split()[0])
        if (self.info.st_dev,self.info.st_ino,self.mount)!=(facts.get('device'),facts.get('inode'),facts.get('mount_id')):
            raise ValueError('independently opened owned leaf identity differs')
        block=(ctypes.c_long*32)();g.libc_call('fstatfs',self.fd,ctypes.byref(block))
        if block[0]!=0x63677270:raise ValueError('recovery leaf is not actual cgroup2')
        self.root=STORE+'/root-'+lease;self.root_info=os.stat(self.root,follow_symlinks=False)
        self.lock=STORE+'/candidate-'+str(host['candidate_uid'])+'.lease'
        self.lock_info=os.stat(self.lock,follow_symlinks=False)
        if g.protected_read(self.lock)!=lease.encode():raise ValueError('owned fixture lease lock differs')
        self.children:dict[int,Any]={};self.removed=False
        self.empty_observed=False

    def verify(self)->None:
        current=os.stat(self.name,dir_fd=self.parentfd,follow_symlinks=False)
        parent=os.stat(self.parent,follow_symlinks=False)
        if ((current.st_dev,current.st_ino)!=(self.info.st_dev,self.info.st_ino)
                or (parent.st_dev,parent.st_ino)!=(self.parent_info.st_dev,self.parent_info.st_ino)
                or int(Path(f'/proc/self/fdinfo/{self.fd}').read_text().split('mnt_id:')[1].split()[0])!=self.mount):
            raise ValueError('owned recovery leaf identity changed')

    def read(self,name:str)->str:
        self.verify()
        if name not in ('cgroup.events','cgroup.procs','memory.events','pids.events','memory.current','memory.peak'):
            raise ValueError('closed recovery observation field')
        fd=os.open(name,os.O_RDONLY|os.O_NOFOLLOW|os.O_CLOEXEC,dir_fd=self.fd)
        try:return os.read(fd,65536).decode().strip()
        finally:os.close(fd)

    def empty(self)->bool:return self.g.key_values(self.read('cgroup.events'))['populated']==0

    def capture(self,pid:int,start:str,stage:str)->None:
        if pid not in self.children:
            identity=self.g.ChildIdentity(pid,self.host['candidate_uid'],self.host['candidate_gid'])
            if identity.start!=start:raise ValueError('owned child start differs')
            self.children[pid]=identity
        identity=self.children[pid]
        if stage=='attached' and identity.phase=='bootstrap':identity.begin_transition()
        if stage=='ready':identity.confirm_candidate()
        identity.verify()

    def descendants(self)->list[dict[str,Any]]:
        result=[]
        for value in self.read('cgroup.procs').split():
            pid=int(value)
            if pid in self.children:continue
            identity=self.g.Identity(pid)
            state=self.g.parse_status(Path(f'/proc/{pid}/status').read_text())
            if identity.uid!=[self.host['candidate_uid']]*4 or os.getsid(pid)!=pid or state['NSpid'].split()[-1]=='1':
                identity.close();raise ValueError('foreign/non-detached fixture descendant')
            self.children[pid]=identity
            result.append({'pid':pid,'start':identity.start,'session':os.getsid(pid),'uid':identity.uid})
        return result

    def scoped_kill(self)->None:
        self.verify()
        fd=os.open('cgroup.kill',os.O_WRONLY|os.O_NOFOLLOW|os.O_CLOEXEC,dir_fd=self.fd)
        try:
            if os.write(fd,b'1')!=1:raise ValueError('short owned recovery kill write')
        finally:os.close(fd)

    def finish(self,deadline:float,guardian_missing:bool)->dict[str,bool]:
        # A kill request is never terminal evidence. Read population and every
        # pinned process separately, reap only owned adopted fixture children.
        if not guardian_missing:
            if not self.empty_observed:raise ValueError('no independent pre-removal empty/dead/reaped witness')
            if Path(self.parent,self.name).exists() or Path(self.root).exists() or Path(self.lock).exists():
                raise ValueError('guardian terminal removal contradicts actual host')
            self.removed=True
            return {'empty':True,'dead':True,'reaped':True,'removed':True}
        while time.monotonic()<deadline:
            for pid,identity in self.children.items():
                if identity.dead():
                    try:os.waitpid(pid,os.WNOHANG)
                    except ChildProcessError:pass
            if self.empty() and all(p.dead() and not Path(f'/proc/{p.pid}').exists() for p in self.children.values()):break
            select.select([],[],[],.02)
        if not self.empty() or any(not p.dead() or Path(f'/proc/{p.pid}').exists() for p in self.children.values()):
            raise ValueError('owned outer teardown empty/dead/reaped proof missing')
        if guardian_missing:
            self.verify();os.rmdir(self.name,dir_fd=self.parentfd)
            for path,expected in ((self.root,self.root_info),(self.lock,self.lock_info)):
                current=os.stat(path,follow_symlinks=False)
                if (current.st_dev,current.st_ino)!=(expected.st_dev,expected.st_ino):
                    raise ValueError('owned recovery scaffolding identity changed')
            os.rmdir(self.root);os.unlink(self.lock)
        self.removed=True
        return {'empty':True,'dead':True,'reaped':True,'removed':True}

    def close(self)->None:
        for identity in self.children.values():identity.close()
        os.close(self.fd);os.close(self.parentfd)

    def witness_empty(self)->None:
        if not self.empty() or any(not p.dead() for p in self.children.values()):
            raise ValueError('independent terminal empty/dead witness missing')
        for pid in self.children:
            try:os.waitpid(pid,os.WNOHANG)
            except ChildProcessError:pass
        if any(Path(f'/proc/{pid}').exists() for pid in self.children):
            raise ValueError('independent terminal reaped witness missing')
        self.empty_observed=True


def validate_descriptor(value: Any) -> dict[str,str]:
    if not isinstance(value,dict) or set(value)!={'schema','scenario'} or value['schema']!=SCHEMA:
        raise ValueError('closed descriptor required; no code/path/principal/caps parameters')
    if value['scenario'] not in SCENARIOS:
        raise ValueError('fixed scenario required')
    return dict(value)


def verify_outer_witness(value:Any)->None:
    if (not isinstance(value,dict) or set(value)!={'empty','dead','reaped','removed'}
            or any(member is not True for member in value.values())):
        raise ValueError('independently observed empty/dead/reaped/removed required')


def terminal_ok(value:Any)->bool:
    return isinstance(value,dict) and set(value)=={'empty','reaped','removed'} and all(x is True for x in value.values())


def _verify_capture_witnesses(value:dict[str,Any],scenario:str,case:str)->None:
    if 'guardian_terminal' not in value:
        raise ValueError('explicit guardian terminal observation required, including expected absence')
    verify_outer_witness(value.get('outer'))
    sentinel=value.get('sentinel',{})
    if (not isinstance(sentinel,dict) or sentinel.get('alive') is not True
            or not isinstance(sentinel.get('before'),dict)
            or sentinel.get('before')!=sentinel.get('after')
            or set(sentinel['before'])!={'pid','start'}
            or type(sentinel['before']['pid']) is not int or sentinel['before']['pid']<=1
            or not isinstance(sentinel['before']['start'],str) or not sentinel['before']['start'].isdigit()):
        raise ValueError('unrelated sentinel identity/liveness changed')
    terminal=value.get('guardian_terminal')
    if terminal is not None and not terminal_ok(terminal):
        raise ValueError('partial guardian terminal is not completion')
    expected_missing=scenario=='guardian-loss' or scenario=='invalid-evidence' and case=='observer'
    if expected_missing and terminal is not None:
        raise ValueError('fixed loss/fault terminal must remain missing')
    if not expected_missing and terminal is None:
        raise ValueError('guardian terminal receipt missing')


def verify_attempt(value:Any,scenario:str,case:str)->dict[str,Any]:
    """Admit this original attempt's existing terminal/sentinel/removal proof."""
    if scenario not in SCENARIOS or case not in CASES[scenario]:raise ValueError('fixed actual attempt required')
    if not isinstance(value,dict):raise ValueError('actual attempt record required')
    ceiling=DEADLINE_SECONDS if scenario=='invalid-evidence' and case=='deadline' else ATTEMPT_SECONDS
    if (not 0<=finite(value.get('finished'))-finite(value.get('started'))<=ceiling
            or value.get('error') is not None or value.get('executed') is not True
            or value.get('scenario')!=scenario or value.get('case')!=case):
        raise ValueError('an actual attempt failed or exceeded its shared ceiling')
    _verify_capture_witnesses(value,scenario,case)
    return {'control_passed':True,'production_capture_accepted':False}


def verify_result(value: Any) -> dict[str,Any]:
    """Pure receipt admission, called only with the outer observer's owned evidence.

    This parser is not an issuer: JSON submitted by an actor never acquires host
    authority. The executing fixed root observer retains the original raw record.
    """
    if not isinstance(value,dict) or value.get('executed') is not True or value.get('error') is not None:
        raise ValueError('unexecuted/skipped/failed control cannot pass')
    scenario=value.get('scenario')
    if not isinstance(scenario,str) or scenario not in SCENARIOS:raise ValueError('fixed scenario required')
    elapsed=finite(value.get('finished'))-finite(value.get('started'))
    attempts=value.get('attempts')
    if not isinstance(attempts,list) or not attempts:raise ValueError('actual attempts missing')
    if [attempt.get('case') for attempt in attempts if isinstance(attempt,dict)]!=list(CASES[scenario]):
        raise ValueError('actual attempt coverage/order incomplete')
    merged={}
    previous=finite(value.get('started'))
    for attempt in attempts:
        if not isinstance(attempt,dict):raise ValueError('actual attempt record required')
        verify_attempt(attempt,scenario,attempt['case'])
        if finite(attempt['started'])<previous or finite(attempt['finished'])>finite(value['finished']):
            raise ValueError('actual attempt timing reset or escaped total ceiling')
        previous=finite(attempt['finished'])
        actual=attempt.get('checks')
        expected=set(CHECKS[scenario]) if scenario in ('baseline','boundaries') else (
            {'limits','affinity','tmpfs'} if scenario=='resources' and attempt['case']=='standard'
            else set(CHECKS[scenario]) if scenario=='supervisor-loss' else {attempt['case']})
        if not isinstance(actual,dict) or set(actual)!=expected or any(x is not True for x in actual.values()):
            raise ValueError('actual attempt checks failed or incomplete')
        merged.update(actual)
    if merged!=value.get('checks'):raise ValueError('aggregate differs from actual attempt checks')
    if not 0<=elapsed<=TOTAL_SECONDS:raise ValueError('shared attempt ceiling exceeded')
    _verify_capture_witnesses(value,scenario,attempts[-1]['case'])
    if any(value.get(name)!=attempts[-1].get(name) for name in ('outer','sentinel','guardian_terminal')):
        raise ValueError('aggregate differs from actual final attempt witnesses')
    checks=value.get('checks')
    if not isinstance(checks,dict) or set(checks)!=set(CHECKS[scenario]) or any(x is not True for x in checks.values()):
        raise ValueError('complete actual scenario checks required')
    return {'control_passed':True,'production_capture_accepted':False,
            'guardian_terminal_missing':value.get('guardian_terminal') is None,'scenario':scenario}


def validate_principal(facts: dict[str,Any]) -> tuple[int,int]:
    """Admit OS-derived facts only; there is deliberately no principal CLI field."""
    uid,gid=facts.get('uid'),facts.get('gid')
    if (facts.get('name')!='nobody' or type(uid) is not int or uid<=0
            or type(gid) is not int or gid<=0 or uid==facts.get('caller_uid')
            or gid==facts.get('caller_gid') or facts.get('uid_names')!=['nobody']
            or len(facts.get('gid_names',[]))!=1 or facts.get('primary_names')!=['nobody']
            or facts.get('supplementary_names')!=[] or facts.get('active') is not False
            or facts.get('home_exposed') is not False):
        raise ValueError('existing nobody identity is unsafe, shared, active or unproved')
    return uid,gid


def validate_ci_principal(facts:dict[str,Any])->tuple[int,int]:
    """Fixed existing CI irc39/39 only; no account selector or fallback."""
    uid,gid=facts.get('uid'),facts.get('gid')
    if (facts.get('name')!='irc' or type(uid) is not int or uid!=39
            or type(gid) is not int or gid!=39 or uid==facts.get('caller_uid')
            or gid==facts.get('caller_gid') or facts.get('uid_names')!=['irc']
            or facts.get('gid_names')!=['irc'] or facts.get('primary_names')!=['irc']
            or facts.get('supplementary_names')!=[] or facts.get('active') is not False
            or facts.get('home_exposed') is not False):
        raise ValueError('fixed CI irc identity is unsafe, shared, active or unproved')
    return uid,gid


def _bootstrap_read(path:str,maximum:int)->bytes:
    """Small fixed-root bootstrap before importing the protected guardian source."""
    target=Path(path)
    for member in (target,*target.parents):
        info=member.lstat()
        if stat.S_ISLNK(info.st_mode) or info.st_uid!=0 or info.st_mode&0o022:
            raise ValueError('mutable fixed control bootstrap path')
        if any(name in os.listxattr(member,follow_symlinks=False)
               for name in ('system.posix_acl_access','system.posix_acl_default')):
            raise ValueError('fixed bootstrap discretionary ACL')
    before=target.lstat()
    if not stat.S_ISREG(before.st_mode) or before.st_nlink!=1 or before.st_mode&0o6000:
        raise ValueError('fixed bootstrap single-link regular source required')
    fd=os.open(path,os.O_RDONLY|os.O_NOFOLLOW|os.O_CLOEXEC)
    try:
        current=os.fstat(fd)
        if (current.st_dev,current.st_ino)!=(before.st_dev,before.st_ino):raise ValueError('fixed bootstrap replaced')
        chunks=[];count=0
        while True:
            part=os.read(fd,min(65536,maximum+1-count))
            if not part:break
            count+=len(part)
            if count>maximum:raise ValueError('fixed bootstrap source byte cap exceeded')
            chunks.append(part)
        return b''.join(chunks)
    finally:os.close(fd)


def _guardian(protected:bool=False) -> Any:
    source=Path(__file__).with_name('linux_guardian.py')
    spec=importlib.util.spec_from_file_location('fixed_linux_lease_guardian',source)
    if spec is None or spec.loader is None:raise ValueError('fixed guardian source missing')
    module=importlib.util.module_from_spec(spec)
    if protected:
        if str(Path(__file__))!=STORE+'/source/linux_lease_control.py':raise ValueError('fixed installed control source required')
        anchor=json.loads(_bootstrap_read(ANCHOR,1024*1024))
        if not isinstance(anchor,dict) or set(anchor)!={'schema','files'} or anchor['schema']!=SCHEMA:
            raise ValueError('closed bootstrap anchor required')
        validate_closure(anchor['files'])
        selected=[row for row in anchor['files'] if row['source']==str(source) and row['target']=='/app/linux_guardian.py']
        if len(selected)!=1:raise ValueError('actual guardian bootstrap source pin missing')
        raw=_bootstrap_read(str(source),1024*1024)
        if hashlib.sha256(raw).hexdigest()!=selected[0]['sha256'] or len(raw)!=selected[0]['bytes']:
            raise ValueError('actual guardian bootstrap source bytes changed')
        exec(compile(raw,str(source),'exec'),module.__dict__)
    else:
        # Portable import seam only. The operational main always takes the
        # independently protected fixed-root path above; no CLI selects this.
        spec.loader.exec_module(module)
    return module


def principal_facts(g: Any, caller: Any) -> dict[str,Any]:
    record=pwd.getpwnam('nobody')
    return _principal_facts(g,caller,record)


def ci_principal_facts(g:Any,caller:Any)->dict[str,Any]:
    try:record=pwd.getpwnam('irc')
    except KeyError as failure:
        raise CiPrerequisiteUnavailable('existing fixed CI irc account absent',{
            'stage':'initial-principal-lookup','name':'irc','operation':'pwd.getpwnam',
            'error_type':type(failure).__name__,'args':list(failure.args)}) from failure
    return _principal_facts(g,caller,record,ci=True)


def _principal_facts(g:Any,caller:Any,record:Any,*,ci:bool=False)->dict[str,Any]:
    users=pwd.getpwall();groups=grp.getgrall()
    caller_state=g.parse_status(Path(f'/proc/{caller.pid}/status').read_text())
    caller_gid=int(caller_state['Gid'].split()[0])
    # candidate_unused checks UID, primary GID and supplementary process groups.
    g.candidate_unused(record.pw_uid,record.pw_gid)
    home=Path(record.pw_dir)
    exposed=False
    if home.exists():
        info=home.stat()
        exposed=(info.st_uid==record.pw_uid and bool(info.st_mode&0o700)
                 or info.st_gid==record.pw_gid and bool(info.st_mode&0o070)
                 or bool(info.st_mode&0o007))
    facts={'name':record.pw_name,'uid':record.pw_uid,'gid':record.pw_gid,
        'caller_uid':caller.uid[0],'caller_gid':caller_gid,
        'uid_names':sorted(p.pw_name for p in users if p.pw_uid==record.pw_uid),
        'gid_names':sorted(p.gr_name for p in groups if p.gr_gid==record.pw_gid),
        'primary_names':sorted(p.pw_name for p in users if p.pw_gid==record.pw_gid),
        'supplementary_names':sorted(name for group in groups if group.gr_gid==record.pw_gid for name in group.gr_mem),
        'active':False,'home_exposed':exposed}
    try:
        if ci:validate_ci_principal(facts)
        else:validate_principal(facts)
    except ValueError as failure:
        if not ci:raise
        caller.verify()
        raise CiPrincipalRejected(str(failure),facts) from failure
    caller.verify()
    return facts


def elf_dependencies(raw: bytes) -> dict[str,Any] | None:
    """Read actual ELF64-LE PT_INTERP/DT_NEEDED; never run ldd or another binary."""
    if not raw.startswith(b'\x7fELF'):return None
    if len(raw)<64 or raw[4:7]!=b'\x02\x01\x01':raise ValueError('supported ELF64-LE required')
    header=struct.unpack_from('<HHIQQQIHHHHHH',raw,16)
    if header[1] not in (62,183) or header[8]!=56 or header[9]>4096:
        raise ValueError('unsupported ELF machine/program headers')
    phoff=header[4]
    loads=[];dynamic=None;interpreter=None
    def span(offset: int, size: int) -> bytes:
        if offset<0 or size<0 or offset+size>len(raw):raise ValueError('ELF segment outside actual bytes')
        return raw[offset:offset+size]
    def text(value: bytes) -> str:
        if b'\0' not in value:raise ValueError('unterminated ELF string')
        return value.split(b'\0',1)[0].decode('ascii')
    for index in range(header[9]):
        item=struct.unpack('<IIQQQQQQ',span(phoff+index*56,56))
        kind,_,offset,address,_,size,_,_=item
        span(offset,size)
        if kind==1:loads.append((address,offset,size))
        if kind==2:
            if dynamic is not None:raise ValueError('ambiguous ELF dynamic segment')
            dynamic=span(offset,size)
        if kind==3:
            if interpreter is not None:raise ValueError('ambiguous ELF interpreter')
            interpreter=text(span(offset,size))
    needed=[];string_address=None;string_size=None
    if dynamic is not None:
        if len(dynamic)%16:raise ValueError('partial ELF dynamic record')
        terminated=False
        for at in range(0,len(dynamic),16):
            tag,value=struct.unpack_from('<qQ',dynamic,at)
            if tag==0:terminated=True;break
            if tag==1:needed.append(value)
            if tag==5:string_address=value
            if tag==10:string_size=value
        if not terminated:raise ValueError('unterminated ELF dynamic records')
    names=[]
    if needed:
        if string_address is None or string_size is None:raise ValueError('ELF needed lacks string table')
        matches=[offset+string_address-address for address,offset,size in loads
                 if address<=string_address and string_address+string_size<=address+size]
        if len(matches)!=1:raise ValueError('ambiguous ELF string-table backing')
        strings=span(matches[0],string_size)
        for offset in needed:
            if offset>=len(strings):raise ValueError('ELF needed outside actual table')
            name=text(strings[offset:])
            if not name or '/' in name:raise ValueError('nonlocal ELF dependency name')
            names.append(name)
    return {'interpreter':interpreter,'needed':names}


def validate_closure(rows: Any) -> dict[str,int]:
    if not isinstance(rows,list) or not rows or len(rows)>MAX_FILES:raise ValueError('bounded actual file closure required')
    targets={};sources=set();total=0
    for row in rows:
        if not isinstance(row,dict) or set(row)!={'source','target','bytes','sha256','elf'}:
            raise ValueError('closed actual closure member required')
        source,target=row['source'],row['target']
        if (not isinstance(source,str) or not isinstance(target,str) or not target.startswith('/')
                or str(Path(target))!=target or '..' in Path(target).parts or target in targets
                or source in sources or type(row['bytes']) is not int or row['bytes']<=0
                or not isinstance(row['sha256'],str) or len(row['sha256'])!=64
                or any(c not in '0123456789abcdef' for c in row['sha256'])):
            raise ValueError('canonical unique actual closure bytes/pins required')
        targets[target]=row;sources.add(source);total+=row['bytes']
    if total>MAX_BYTES:raise ValueError('tiny closure exceeds 256MiB')
    for row in rows:
        elf=row['elf']
        if elf is None:continue
        if not isinstance(elf,dict) or set(elf)!={'interpreter','needed'} or not isinstance(elf['needed'],list):
            raise ValueError('actual ELF dependency facts required')
        if elf['interpreter'] is not None and elf['interpreter'] not in targets:
            raise ValueError('actual ELF interpreter absent from closure')
        for needed in elf['needed']:
            if not isinstance(needed,str) or len([p for p in targets if Path(p).name==needed])!=1:
                raise ValueError('missing or ambiguous actual ELF NEEDED member')
    if '/usr/bin/python3.12' not in targets or targets['/usr/bin/python3.12']['elf'] is None:
        raise ValueError('actual OS Python3.12 ELF required')
    return {'files':len(rows),'bytes':total}


def control_guardian(g: Any, request: dict[str,Any], host: dict[str,Any],
                     profile: dict[str,Any], supervisor: Any) -> Any:
    # Fixed source route, never a production config branch. Backend/paths are
    # protected construction facts beside the exact closed control descriptor.
    validate_descriptor({key:profile['config'][key] for key in ('schema','scenario')})
    class ControlGuardian(g.LeaseMechanics):
        anchor=ANCHOR
        lease_schema=SCHEMA

        def emit(self,event:str,**fields:Any)->None:
            super().emit(event,**fields)
            if (event=='frame' and fields.get('phase')=='generate'
                    and fields.get('body',{}).get('type')=='ready'
                    and profile['config']['scenario']=='resources'):
                if self.control_case=='oom':self.leaf.write('memory.max',str(32*1024**2))
                if self.control_case=='pids':self.leaf.write('pids.max','8')
            if (event=='frame' and fields.get('phase')=='generate'
                    and fields.get('body',{}).get('type')=='ready'
                    and profile['config']['scenario']=='invalid-evidence' and self.control_case=='observer'):
                # Fixed host-only fault, never a candidate-selected operation:
                # invalidate the sampler's own fd. Independent outer custody
                # still owns a different pinned descriptor for recovery.
                os.close(self.leaf.fd);self.leaf.fd=-1

        def sample(self,enforce:bool=True)->None:
            # A separate TEST_ONLY subcase tightens only after unchanged-cap
            # READY. Retain bad samples and aborted production accounting.
            tightened=(profile['config']['scenario']=='resources' and self.phase=='generate'
                       and getattr(self,'control_case',None) in ('oom','pids'))
            super().sample(False if tightened else enforce)

        def teardown_phase(self)->tuple[bool,bool,int|None]:
            result=super().teardown_phase()
            if self.leaf is not None and result[0] and result[1]:
                self.emit('proof',phase=self.phase,facts={'role':'control-empty',
                    'events':{'memory':g.key_values(self.leaf.read('memory.events')),
                              'pids':g.key_values(self.leaf.read('pids.events'))}})
                fd=getattr(self,'terminal_fd',-1)
                if fd<0:raise ValueError('independent terminal observer handle missing')
                until=min(self.deadline,self.cleanup_deadline or self.deadline)
                while time.monotonic()<until:
                    if select.select([fd],[],[],.02)[0]:
                        if os.read(fd,1)!=b'T':raise ValueError('independent terminal observer lost')
                        break
                else:raise ValueError('independent terminal observer deadline exhausted')
            return result

        def liveness(self)->None:
            super().liveness()
            if (self.handoff is not None and self.phase=='generate' and self.child is not None
                    and profile['config']['scenario'] in ('supervisor-loss','guardian-loss')
                    and self.child.identity is not None and self.leaf is not None
                    and not getattr(self,'descendants_observed',False)):
                members=[int(p) for p in self.leaf.read('cgroup.procs').split()]
                if len(members)>1:
                    # Source-appointed checkpoint: inspect the actual kernel
                    # members/session; a child packet cannot trigger this hook.
                    descendants=[]
                    for pid in members:
                        if pid==self.child.pid:continue
                        identity=g.Identity(pid)
                        try:
                            identity.verify()
                            if identity.uid!=[host['candidate_uid']]*4:
                                raise ValueError('detached descendant credentials differ')
                            # fork→setsid is a trusted fixed child-code interval,
                            # not a loss handoff until kernel session agrees.
                            if os.getsid(pid)!=pid:return
                            descendants.append({'pid':pid,'start':identity.start})
                        finally:identity.close()
                    self.emit('proof',phase=self.phase,facts={'role':'control-descendants','members':descendants})
                    self.descendants_observed=True
                    self.handoff.reach('descendants',self.child.identity)

        def run_phase(self,phase:str)->None:
            if self.leaf is None:raise ValueError('control leaf unavailable')
            self.emit('proof',phase=phase,facts={'role':'control-leaf','name':self.leaf.name,
                'device':self.leaf.identity.st_dev,'inode':self.leaf.identity.st_ino,
                'mount_id':self.leaf.mount_id})
            super().run_phase(phase)
    guardian=ControlGuardian()
    guardian._initialize(request,host,profile,supervisor,ATTEMPT_SECONDS)
    return guardian


def _protected_launcher(g:Any,executable:str)->None:
    # An ancestry executable is not a candidate closure member. Only the fixed
    # OS sudo launcher may retain setuid; production protected_path(..., True)
    # still refuses every privileged source copied into a candidate closure.
    info=g.protected_path(executable)
    privileges=info.st_mode & 0o6000
    if (not stat.S_ISREG(info.st_mode) or info.st_nlink!=1
            or 'security.capability' in os.listxattr(executable,follow_symlinks=False)
            or privileges and (executable!='/usr/bin/sudo' or privileges!=0o4000)):
        raise ValueError('unsafe or unrecognised privileged launcher ancestry')


class CallerAncestryError(ValueError):
    """Passive bounded observations of a refused route, never caller authority."""
    def __init__(self, facts: dict[str,Any]):
        super().__init__('ambiguous launcher credential ancestry')
        self.facts=facts


def original_caller(g: Any) -> Any:
    """Actual stable ancestry, never SUDO_UID, environment or request assertions."""
    chain=[];observed=[];visited=set();pid=os.getppid()
    try:
        while pid>1 and pid not in visited:
            visited.add(pid)
            identity=g.Identity(pid);chain.append(identity)
            executable=os.readlink(f'/proc/{pid}/exe')
            _protected_launcher(g,executable)
            observed.append((identity,executable))
            if len(observed)>32:observed.pop(0)
            if identity.uid==[identity.uid[0]]*4 and identity.uid[0]>0:
                for pinned in chain:pinned.verify()
                result=chain.pop()
                return result
            if identity.uid!=[0]*4:
                # These are observations at pin/readlink time, not a successful
                # final chain verification. Keep a bounded tail and the exact
                # omission count; a rejected transition never acquires a caller.
                raise CallerAncestryError({'schema':'TEST_ONLY-caller-ancestry-failure/v1',
                    'observed_ancestors':len(chain),'omitted_prefix':len(chain)-len(observed),
                    'observations':[{'pid':pinned.pid,'start':pinned.start,'ppid':pinned.ppid,
                        'uid':list(pinned.uid),'executable':path[:4096],
                        'executable_truncated':len(path)>4096} for pinned,path in observed]})
            pid=identity.ppid
        raise ValueError('no actual nonroot caller ancestry')
    finally:
        for identity in chain:identity.close()


def load_control_host(g: Any, scenario: str, caller: Any) -> tuple[dict[str,Any],dict[str,Any],dict[str,Any]]:
    return _load_control_host(g,scenario,caller,False)


def load_ci_control_host(g: Any, scenario: str, caller: Any) -> tuple[dict[str,Any],dict[str,Any],dict[str,Any]]:
    """Separate source-appointed fresh-VM laboratory route, never JSON selection."""
    return _load_control_host(g,scenario,caller,True)


def _load_control_host(g: Any, scenario: str, caller: Any, ci:bool) -> tuple[dict[str,Any],dict[str,Any],dict[str,Any]]:
    validate_descriptor({'schema':SCHEMA,'scenario':scenario})
    anchor_raw=g.protected_read(ANCHOR,maximum=1024*1024)
    anchor=json.loads(anchor_raw)
    if not isinstance(anchor,dict) or set(anchor)!={'schema','files'} or anchor['schema']!=SCHEMA:
        raise ValueError('fixed TEST_ONLY anchor schema required')
    rows=anchor['files']
    validate_closure(rows)
    observed=[];inodes=set()
    for row in rows:
        raw=g.protected_read(row['source'],row['sha256'],MAX_BYTES)
        info=g.protected_path(row['source'],True)
        if len(raw)!=row['bytes'] or elf_dependencies(raw)!=row['elf']:
            raise ValueError('actual closure bytes/ELF dependency metadata differ')
        identity=(info.st_dev,info.st_ino)
        if identity in inodes:raise ValueError('ambiguous closure source inode alias')
        inodes.add(identity)
        observed.append(dict(row,device=info.st_dev,inode=info.st_ino))
    by_target={row['target']:row for row in rows}
    fixed_names=('linux_lease_control.py','linux_lease_control_child.py','linux_guardian.py',
                 'linux_runtime_filter.py','linux_network.py','qwen_backend.py','linux_lease_control_entry')
    for name in fixed_names:
        target='/app/'+name
        if target not in by_target or by_target[target]['source']!=STORE+'/source/'+name:
            raise ValueError('fixed installed control support source absent')
    if by_target['/usr/bin/python3.12']['source']!='/usr/bin/python3.12':
        raise ValueError('actual fixed OS interpreter required, no runtime alias')
    if str(Path(__file__))!=STORE+'/source/linux_lease_control.py' or sys.executable!='/usr/bin/python3.12':
        raise ValueError('fixed installed entry and OS interpreter required')
    facts=ci_principal_facts(g,caller) if ci else principal_facts(g,caller)
    uid,gid=validate_ci_principal(facts) if ci else validate_principal(facts)
    parent='/sys/fs/cgroup' if ci else '/sys/fs/cgroup/policy-as-versioned-flux-linux-control'
    g.protected_path(parent,False)
    available=g.parse_set(Path(parent,'cpuset.cpus.effective').read_text()) & os.sched_getaffinity(0)
    if len(available)<2:raise ValueError('two actual eligible CPUs unavailable')
    pins={row['source']:row['sha256'] for row in rows}
    target_pins={row['target']:row['sha256'] for row in rows}
    python=by_target['/usr/bin/python3.12'];script=by_target['/app/linux_lease_control_child.py']
    config={'schema':SCHEMA,'scenario':scenario,'backend':{'python':python['source'],
        'python_sha256':python['sha256'],'script':script['source'],'sha256':script['sha256']}}
    profile={'config':config,'readonly_mounts':[{key:row[key] for key in ('source','target','sha256')} for row in rows],
        'paths':{'schema':SCHEMA,'support_sources':target_pins,'network_module':'/app/linux_network.py',
                 'bootstrap_module':'/app/qwen_backend.py','scenario':scenario}}
    host={'candidate_uid':uid,'candidate_gid':gid,'supervisor_uid':caller.uid[0],
        'cgroup_parent':parent,'cpus':sorted(available)[:2],
        'guardian_python':'/usr/bin/python3.12','guardian_python_sha256':python['sha256'],
        'guardian_entry':STORE+'/source/linux_lease_control.py','support_sources':pins}
    storage=g.storage_paths(host,profile,ANCHOR)
    budget=g.reserve(storage,g.MEMORY+g.RESERVE,False)
    budget['ancestors']=g.observe_ancestors(parent)
    budget['memory_available']=g.effective_memory(budget,parent)
    if (ci and all(type(budget.get(key)) is int and budget[key]>=0 for key in ('memory_available','disk_free'))
            and (budget['memory_available']<g.MEMORY+g.RESERVE or budget['disk_free']<g.DISK)):
        raise CiPrerequisiteUnavailable('actual initial14GiB headroom/5GiB storage unavailable',budget)
    g.validate_reserve(budget,g.MEMORY+g.RESERVE,storage,parent)
    if not {'memory','cpu','cpuset','pids'}<=set(Path(parent,'cgroup.subtree_control').read_text().split()):
        raise ValueError('protected controllers not already enabled')
    g.verify_guardian_closure(host,lambda:caller.verify())
    return host,profile,{'anchor_sha256':g.digest(anchor_raw),'closure':observed,
        'principal':facts,'kernel':platform.release(),'machine':platform.machine(),
        'python':sys.version,'caller':{'pid':caller.pid,'start':caller.start,'uid':caller.uid}}


def reaped_owned(identity:Any,deadline:float)->bool:
    while time.monotonic()<deadline:
        try:
            waited,_=os.waitpid(identity.pid,os.WNOHANG)
            if waited:return identity.dead() and not Path(f'/proc/{identity.pid}').exists()
        except ChildProcessError:
            if identity.dead() and not Path(f'/proc/{identity.pid}').exists():return True
        select.select([identity.fd],[],[],.02)
    return False


def actual_receipt(g:Any,lease:str,phase:str,facts:dict[str,Any],profile:dict[str,Any])->dict[str,Any]:
    role=facts['role']
    if role not in ('sources','native_mappings'):raise ValueError('fixed receipt role required')
    suffix='sources' if role=='sources' else 'native-mappings-'+f"{facts['sequence']:06d}"
    path=STORE+'/receipts/'+lease+'/'+phase+'-'+suffix+'.jsonl'
    raw=g.protected_read(path,facts['sha256'],16*1024**2)
    if len(raw)!=facts['bytes']:raise ValueError('actual protected receipt byte count differs')
    rows=[json.loads(line) for line in raw.splitlines()]
    if len(rows)!=facts['total'] or not rows:raise ValueError('actual protected receipt rows incomplete')
    if role=='sources':
        expected={row['target']:row for row in profile['readonly_mounts']}
        if {row.get('target') for row in rows}!=set(expected):raise ValueError('actual source closure receipt incomplete')
        for row in rows:
            source=expected[row['target']]
            info=g.protected_path(source['source'],True)
            if (row.get('source'),row.get('sha256'),row.get('device'),row.get('inode'))!=(
                    source['source'],source['sha256'],info.st_dev,info.st_ino):
                raise ValueError('actual backing source identity receipt differs')
    return {'path':path,'sha256':g.digest(raw),'bytes':len(raw),'total':len(rows),'role':role}


def assess_attempt(scenario:str,case:str,events:list[dict[str,Any]],observed:dict[str,Any],host:dict[str,Any])->dict[str,bool]:
    """Assess actual bound host/child evidence; child success flags are insufficient."""
    frames=[row['body'] for row in events if row.get('event')=='frame' and row.get('phase')=='generate']
    controls=[row for row in frames if row.get('type')=='control' and row.get('case')==case]
    result=controls[0].get('result',{}) if len(controls)==1 else {}
    ready=[row for row in frames if row.get('type')=='ready']
    proofs=[row.get('facts',{}) for row in events if row.get('event')=='proof']
    ready_proofs=[row for row in proofs if row.get('role')=='ready']
    limits=(len(ready_proofs)==2 and all(row.get('limits',{}).get('memory.max')=='12884901888'
        and row.get('limits',{}).get('memory.swap.max')=='0'
        and row.get('limits',{}).get('pids.max')=='128'
        and row.get('limits',{}).get('cpu.max')=='200000 100000'
        and row.get('tmpfs_bytes')==134217728 for row in ready_proofs))
    failures='\n'.join(str(row.get('error','')) for row in events if row.get('event')=='failure')
    if scenario=='baseline':
        phases=[row for row in events if row.get('event')=='phase_end']
        starts=[row for row in events if row.get('event')=='phase_start']
        return {'paired':len(phases)==2 and [row.get('phase') for row in phases]==['preflight','generate']
            and all(row.get('empty') is True and row.get('reaped') is True and row.get('returncode')==0 for row in phases)
            and len(starts)==2 and starts[0]['pid']!=starts[1]['pid'],
            'limits':limits,'network':len(ready)==1 and network_ok(ready[0].get('network',{}).get('before'))
                and network_ok(result.get('network')),
            'sources':len(observed['receipts'])>=4 and observed.get('source_unchanged') is True}
    if scenario=='boundaries':
        checks=boundary_checks(result,observed['host_pids'])
        checks.update(network=network_ok(result.get('network')),
            **{'exec-inheritance':result.get('exec_returncode')==0 and network_ok(result.get('exec_network'))})
        checks['writes']=checks['writes'] and observed.get('source_unchanged') is True
        return checks
    if scenario=='resources':
        if case=='oom':return {'oom':observed.get('memory_events',{}).get('oom_kill',0)>=1
            and any(row.get('event')=='aborted' for row in events) and bool(failures)}
        if case=='pids':return {'pids':observed.get('pids_events',{}).get('max',0)>=1
            and result.get('errno')==errno.EAGAIN and any(row.get('event')=='aborted' for row in events)}
        tmpfs=result.get('tmpfs',{})
        return {'limits':limits,'affinity':set(result.get('effective_affinity',[]))==set(host['cpus'])
            and set(result.get('effective_affinity',[]))<=set(result.get('requested_affinity',[])),
            'tmpfs':tmpfs.get('bytes')==134217728 and tmpfs.get('errno')==errno.ENOSPC
                and 0<tmpfs.get('written',0)<=134217728 and denial_ok(tmpfs.get('noexec'))
                and tmpfs['noexec'].get('errno')==errno.EACCES
                and any(row.get('event')=='resources' and row.get('facts',{}).get('memory.peak',0)>0 for row in events)}
    if scenario=='supervisor-loss':return {'descendants':bool(observed.get('detached')),
        'guardian-survived':observed.get('guardian_survived') is True,
        'supervisor-dead':observed.get('supervisor_killed') is True and bool(failures)}
    if scenario=='guardian-loss':return {case:observed.get('guardian_killed') is True
        and observed.get('automatic_child_death') is True and observed.get('terminal_missing') is True
        and (case!='descendants' or bool(observed.get('detached')))
        and observed.get('candidate_code_before_release') is False}
    negative={'eof':'handoff control lost','deadline':'deadline','ready':'duplicate child READY',
              'overflow':'frame byte cap','observer':'UNVERIFIED TEARDOWN'}
    if case in negative:return {case:negative[case] in failures and not any(row.get('event')=='done' for row in events)}
    if case=='source':return {case:isinstance(result.get('writes'),list)
        and len(result['writes'])==1 and denial_ok(result['writes'][0]) and observed.get('source_unchanged') is True}
    if case=='incomplete':
        # Deliberately incomplete post-capture observation must be rejected by
        # the same final reader; it is never promoted to production completion.
        refused=False
        actual=dict(observed.get('actual_outer',{}));actual.pop('reaped',None)
        try:verify_outer_witness(actual)
        except ValueError:refused=True
        return {case:refused and observed.get('empty_witness') is True}
    if case=='stale-lock':return {case:observed.get('stale_lock_preserved') is True
        and 'FileExistsError' in failures and not any(row.get('event')=='phase_start' for row in events)}
    return {case:False}


def run_attempt(g:Any,host:dict[str,Any],profile:dict[str,Any],caller:Any,
                case:str,total_deadline:float,directory:Path)->dict[str,Any]:
    """Execute only the fixed fixture. No generic command/principal/path surface."""
    scenario=profile['config']['scenario']
    if case not in CASES[scenario]:raise ValueError('fixed source-appointed subcase required')
    started=time.monotonic();deadline=min(started+ATTEMPT_SECONDS,total_deadline)
    if case=='deadline':deadline=min(deadline,started+DEADLINE_SECONDS)
    if deadline-started<=10:raise ValueError('no finite attempt/teardown reserve remains')
    events=[];observed:dict[str,Any]={'receipts':[],'host_pids':[],
        'candidate_code_before_release':False,'detached':[]}
    error=None;fixture=None;recovery=None;sentinel=None;lease=None;guardian_terminal=None
    sentinel_before=None;sentinel_after=None;outer=None;stale=None;command_open=True
    rawfd=os.open(directory/(scenario+'-'+case+'.jsonl'),os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW,0o400)
    try:
        caller.verify()
        sentinel=start_sentinel(g,caller,deadline)
        sentinel_before={'pid':sentinel.pid,'start':sentinel.start}
        if case=='stale-lock':
            path=STORE+'/candidate-'+str(host['candidate_uid'])+'.lease'
            fd=os.open(path,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW|os.O_CLOEXEC,0o600)
            value=b'TEST_ONLY-owned-stale-lock'
            os.write(fd,value);os.fsync(fd)
            stale=(path,os.fstat(fd),value);os.close(fd)
        fixture=start_fixture(g,host,profile,case,deadline,caller)
        observed['host_pids']=[os.getpid(),fixture['supervisor'].pid,fixture['guardian'].pid,caller.pid]
        sentinel_cgroup=Path(f'/proc/{sentinel.pid}/cgroup').read_text()
        reader=g.FrameReader()
        eof=False;triggered=False
        while time.monotonic()<deadline and not eof:
            caller.verify();sentinel.verify()
            if not select.select([fixture['events']],[],[],.05)[0]:continue
            raw=os.read(fixture['events'],65536)
            if not raw:reader.eof();eof=True;break
            if os.write(rawfd,raw)!=len(raw):raise ValueError('short protected raw control journal write')
            for event in reader.feed(raw):
                events.append(event)
                if event.get('event')=='control-bootstrap-failure':
                    raise ValueError('actual guardian bootstrap: '+str(event.get('error')))
                if event.get('event')=='lease':
                    if lease is not None:raise ValueError('duplicate fixture lease')
                    lease=event.get('lease')
                if lease is None or event.get('lease')!=lease:raise ValueError('foreign fixture event lease')
                if event.get('event')=='proof':
                    facts=event.get('facts',{})
                    role=facts.get('role')
                    if role=='control-leaf':
                        if recovery is None:recovery=Recovery(g,host,lease,facts)
                        else:
                            recovery.verify()
                            if (facts.get('device'),facts.get('inode'))!=(recovery.info.st_dev,recovery.info.st_ino):
                                raise ValueError('phase changed owned leaf identity')
                        if ('/private-'+lease) in sentinel_cgroup or ('/'+recovery.name) in sentinel_cgroup:
                            raise ValueError('unrelated sentinel is inside candidate leaf')
                    if role in ('sources','native_mappings'):
                        observed['receipts'].append(actual_receipt(g,lease,event['phase'],facts,profile))
                    if role=='control-descendants':
                        if recovery is None:raise ValueError('descendant event without owned leaf')
                        actual=recovery.descendants()
                        if not actual or {row['pid'] for row in actual}!={row['pid'] for row in facts.get('members',[])}:
                            raise ValueError('independent detached descendant custody differs')
                        observed['detached'].extend(actual)
                    if role=='control-empty':
                        if recovery is None:raise ValueError('empty receipt without owned leaf')
                        recovery.witness_empty();observed['empty_witness']=True
                        observed['memory_events']=facts['events']['memory']
                        observed['pids_events']=facts['events']['pids']
                        # Independently re-read the kernel counters, not their
                        # root-looking JSON representation alone.
                        if (observed['memory_events']!=g.key_values(recovery.read('memory.events'))
                                or observed['pids_events']!=g.key_values(recovery.read('pids.events'))):
                            raise ValueError('independent terminal kernel events differ')
                        os.write(fixture['terminal'],b'T')
                if event.get('event')=='handoff':
                    if recovery is None:raise ValueError('handoff without independently pinned leaf')
                    stage=event.get('stage')
                    if stage not in HANDOFFS:raise ValueError('foreign handoff stage')
                    recovery.capture(event['pid'],event['start'],stage)
                    target=(event.get('phase')=='generate' and (
                        scenario=='guardian-loss' and stage==case
                        or scenario=='supervisor-loss' and stage=='descendants'))
                    if target:
                        if triggered:raise ValueError('duplicate fixed loss trigger')
                        triggered=True
                        if scenario=='guardian-loss':
                            # Before release, only fixed trusted bootstrap may
                            # run. READY itself is permitted only at ready/work.
                            if stage in ('raw-clone','attached','dropped','armed'):
                                observed['candidate_code_before_release']=any(row.get('event')=='frame'
                                    and row.get('phase')=='generate' for row in events)
                            kill_owned(fixture['guardian']);observed['guardian_killed']=True
                        else:
                            kill_owned(fixture['supervisor']);observed['supervisor_killed']=True
                            fixture['guardian'].verify();observed['guardian_survived']=True
                        continue
                    if (scenario=='invalid-evidence' and case=='eof' and event.get('phase')=='generate'
                            and stage=='ready'):
                        os.close(fixture['command']);command_open=False
                        continue
                    os.write(fixture['command'],b'C')
                if event.get('event') in ('done','aborted'):
                    guardian_terminal={key:event.get(key) for key in ('empty','reaped','removed')}
        if not eof:raise ValueError('shared control attempt deadline exhausted')
        if scenario in ('guardian-loss','supervisor-loss') and not triggered:
            raise ValueError('fixed loss handoff never observed')
        if observed.get('guardian_killed'):
            automatic_deadline=min(deadline,time.monotonic()+5)
            if recovery is None:raise ValueError('guardian loss without pinned child custody')
            while time.monotonic()<automatic_deadline and any(not identity.dead() for identity in recovery.children.values()):
                select.select([],[],[],.02)
            observed['automatic_child_death']=all(identity.dead() for identity in recovery.children.values())
            if not observed['automatic_child_death']:raise ValueError('namespace-init automatic guardian-loss death failed')
        observed['terminal_missing']=guardian_terminal is None
        if guardian_terminal is not None and guardian_terminal!={'empty':True,'reaped':True,'removed':True}:
            raise ValueError('partial guardian terminal')
        sentinel.verify();sentinel_after={'pid':sentinel.pid,'start':sentinel.start}
        if Path(f'/proc/{sentinel.pid}/cgroup').read_text()!=sentinel_cgroup:
            raise ValueError('unrelated sentinel cgroup changed')
        # Kill only the independently pinned fixture supervisor after the cage
        # observation; subreaper adoption lets us actually wait for its guardian.
        kill_owned(fixture['supervisor'])
        if not reaped_owned(fixture['supervisor'],deadline):raise ValueError('owned supervisor not reaped')
        if not fixture['guardian'].dead():kill_owned(fixture['guardian'])
        if not reaped_owned(fixture['guardian'],deadline):raise ValueError('owned guardian not reaped')
        if recovery is not None:
            if guardian_terminal is None:recovery.scoped_kill()
            outer=recovery.finish(deadline,guardian_terminal is None)
        elif stale is not None:
            path,info,value=stale
            current=os.stat(path,follow_symlinks=False)
            observed['stale_lock_preserved']=((current.st_dev,current.st_ino)==(info.st_dev,info.st_ino)
                and g.protected_read(path)==value)
            if not observed['stale_lock_preserved']:raise ValueError('owned stale lock changed')
            os.unlink(path);stale=None
            outer={'empty':True,'dead':True,'reaped':True,'removed':True}
        else:raise ValueError('fixture never acquired verifiable owned kernel state')
        sentinel.verify();sentinel_after={'pid':sentinel.pid,'start':sentinel.start}
        if Path(f'/proc/{sentinel.pid}/cgroup').read_text()!=sentinel_cgroup:
            raise ValueError('unrelated sentinel changed during actual teardown')
        # Rehash actual protected source bytes after candidate attempts. These
        # are the root authority's pins, not supplied by the child result.
        for row in profile['readonly_mounts']:
            if time.monotonic()>=deadline:raise ValueError('attempt deadline during final source rehash')
            g.hash_file(row['source'],row['sha256'])
        observed['source_unchanged']=True
        observed['actual_outer']=outer
        checks=assess_attempt(scenario,case,events,observed,host)
        if any(value is not True for value in checks.values()):raise ValueError('actual scenario evidence failed: '+repr(checks))
    except BaseException as failure:
        error=type(failure).__name__+': '+str(failure)[:2000]
        checks={case:False}
    finally:
        # This backup path never turns a failed attempt green. It is bounded by
        # the SAME attempt deadline and only acts on already pinned own state.
        try:
            if fixture is not None:
                for role in ('supervisor','guardian'):
                    kill_owned(fixture[role]);reaped_owned(fixture[role],deadline)
                if recovery is not None and not recovery.removed:
                    recovery.scoped_kill()
                    recovery.finish(deadline,True)
            if sentinel is not None:
                kill_owned(sentinel)
                if not reaped_owned(sentinel,deadline):raise ValueError('owned sentinel cleanup unverified')
            if stale is not None:
                path,info,value=stale;current=os.stat(path,follow_symlinks=False)
                if (current.st_dev,current.st_ino)!=(info.st_dev,info.st_ino):raise ValueError('owned stale lock changed')
                os.unlink(path)
        except BaseException as failure:
            error=(error+'; ' if error else '')+'UNVERIFIED OUTER TEARDOWN: '+str(failure)[:1000]
        os.fsync(rawfd);os.close(rawfd)
        if recovery is not None:recovery.close()
        if fixture is not None:
            for role in ('supervisor','guardian'):fixture[role].close()
            for field in ('events','terminal','command'):
                if field=='command' and not command_open:continue
                os.close(fixture[field])
        if sentinel is not None:sentinel.close()
    return {'scenario':scenario,'case':case,'executed':True,'started':started,'finished':time.monotonic(),
        'outer':outer,'guardian_terminal':guardian_terminal,'checks':checks,'error':error,
        'observations':observed,'sentinel':{'before':sentinel_before,'after':sentinel_after,
            'alive':sentinel_before is not None and sentinel_before==sentinel_after},
        'production_capture_accepted':False}


def main()->int:
    if len(sys.argv)!=2 or sys.argv[1] not in SCENARIOS:raise ValueError('one fixed scenario argument required')
    scenario=sys.argv[1];started=time.monotonic();total_deadline=started+TOTAL_SECONDS
    if (sys.platform!='linux' or sys.byteorder!='little' or ctypes.sizeof(ctypes.c_void_p)!=8
            or platform.machine() not in ('x86_64','aarch64') or os.getresuid()!=(0,0,0)
            or not sys.flags.isolated or not sys.flags.no_site or not sys.dont_write_bytecode):
        print(json.dumps({'scenario':scenario,'executed':False,'status':'SKIP','reason':'native fixed isolated root control required'}))
        return 77
    g=None;caller=None
    try:
        g=_guardian(protected=True)
        caller=original_caller(g)
        host,profile,prerequisites=load_control_host(g,scenario,caller)
    except (OSError,ValueError,KeyError) as failure:
        if caller is not None:caller.close()
        print(json.dumps({'scenario':scenario,'executed':False,'status':'SKIP','reason':str(failure)[:2000]}))
        return 77
    # Foreground, scoped subreaper is neither a daemon nor a global service.
    g.prctl(4,0);g.prctl(36,1)
    identity=g.Identity(os.getpid())
    parent=Path(STORE,'attempts');g.protected_path(STORE,False)
    try:parent.mkdir(mode=0o700)
    except FileExistsError:g.protected_path(str(parent),False)
    directory=parent/os.urandom(24).hex();directory.mkdir(mode=0o700)
    attempts=[];checks={};error=None
    try:
        for case in CASES[scenario]:
            if time.monotonic()>=total_deadline:raise ValueError('900s total control ceiling exhausted')
            attempt=run_attempt(g,host,profile,caller,case,total_deadline,directory)
            attempts.append(attempt);checks.update(attempt['checks'])
            if attempt['error']:raise ValueError(attempt['error'])
        last=attempts[-1]
        terminal=last['guardian_terminal']
        if scenario=='guardian-loss':terminal=None
        result={'scenario':scenario,'executed':True,'started':started,'finished':time.monotonic(),
            'attempts':attempts,'checks':checks,'outer':last['outer'],'sentinel':last['sentinel'],
            'guardian_terminal':terminal,'error':None,'prerequisites':prerequisites}
        verdict=verify_result(result)
    except BaseException as failure:
        error=type(failure).__name__+': '+str(failure)[:2000]
        result={'scenario':scenario,'executed':True,'started':started,'finished':time.monotonic(),
            'attempts':attempts,'error':error,'prerequisites':prerequisites}
        verdict={'control_passed':False,'production_capture_accepted':False}
    finally:
        identity.close();caller.close()
    raw=g.canonical({'result':result,'verdict':verdict})+b'\n'
    fd=os.open(directory/'result.json',os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW,0o400)
    try:
        if os.write(fd,raw)!=len(raw):raise ValueError('short immutable control result write')
        os.fsync(fd)
    finally:os.close(fd)
    print(json.dumps({'scenario':scenario,'control_passed':verdict['control_passed'],
        'production_capture_accepted':False,'receipt':str(directory/'result.json'),'sha256':g.digest(raw),
        'error':error},sort_keys=True))
    return 0 if verdict['control_passed'] else 1


if __name__=='__main__':raise SystemExit(main())
