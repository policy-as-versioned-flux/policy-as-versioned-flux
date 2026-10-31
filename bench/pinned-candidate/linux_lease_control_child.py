"""Inert-on-import fixed TEST_ONLY native child; no model/runtime acquisition."""
from __future__ import annotations
import ctypes
import errno
import importlib.util
import json
import os
from pathlib import Path
import signal
import sys
import time
from typing import Any

SCHEMA='TEST_ONLY-linux-lease-control/v1'


def module(path:str,name:str)->Any:
    spec=importlib.util.spec_from_file_location(name,path)
    if spec is None or spec.loader is None:raise ValueError('fixed control module missing')
    result=importlib.util.module_from_spec(spec);spec.loader.exec_module(result)
    return result


def emit(value:dict[str,Any])->None:
    raw=json.dumps(value,sort_keys=True,separators=(',',':'),allow_nan=False).encode()+b'\n'
    if len(raw)>65536:raise ValueError('fixed control frame bound exceeded')
    sys.stdout.buffer.write(raw);sys.stdout.buffer.flush()


def denied(operation:Any)->dict[str,Any]:
    try:operation()
    except OSError as error:return {'denied':True,'errno':error.errno}
    return {'denied':False,'errno':None}


def write_attempt(path:str)->dict[str,Any]:
    def execute()->None:
        fd=os.open(path,os.O_WRONLY|os.O_CREAT|os.O_NOFOLLOW,0o600)
        try:os.write(fd,b'TEST_ONLY denied write')
        finally:os.close(fd)
    return dict(denied(execute),path=path)


def syscall(number:int,*arguments:Any)->None:
    libc=ctypes.CDLL(None,use_errno=True)
    if libc.syscall(number,*arguments)==-1:
        code=ctypes.get_errno();raise OSError(code,os.strerror(code))


def boundaries(request:dict[str,Any],network:Any)->dict[str,Any]:
    paths=('/TEST_ONLY-root-write','/app/actor-config.json','/app/lease.json',
           '/app/paths.json','/app/linux_lease_control_child.py','/evidence/write',
           '/sys/fs/cgroup/cgroup.procs','/sys/fs/cgroup/memory.max')
    machine=os.uname().machine
    numbers={'x86_64':{'mount':165,'unshare':272,'setns':308,'ptrace':101,'process_vm_writev':311,'pidfd_getfd':438},
             'aarch64':{'mount':40,'unshare':97,'setns':268,'ptrace':117,'process_vm_writev':271,'pidfd_getfd':438}}[machine]
    libc=ctypes.CDLL(None,use_errno=True)
    def prctl_death()->None:
        if libc.prctl(1,0,0,0,0)==-1:
            code=ctypes.get_errno();raise OSError(code,os.strerror(code))
    def recover_capability()->None:
        class Header(ctypes.Structure):_fields_=[('version',ctypes.c_uint),('pid',ctypes.c_int)]
        class Data(ctypes.Structure):_fields_=[('effective',ctypes.c_uint),('permitted',ctypes.c_uint),('inheritable',ctypes.c_uint)]
        data=(Data*2)();data[0].effective=data[0].permitted=1<<20
        if libc.capset(ctypes.byref(Header(0x20080522,0)),ctypes.byref(data))==-1:
            code=ctypes.get_errno();raise OSError(code,os.strerror(code))
    privilege={'setuid':denied(lambda:os.setresuid(0,0,0)),
        'setgid':denied(lambda:os.setresgid(0,0,0)),
        'setgroups':denied(lambda:os.setgroups([0])),
        'capset':denied(recover_capability),
        'death-signal':denied(prctl_death)}
    isolation={name:denied(lambda name=name:syscall(numbers[name],0,0,0,0,0,0))
               for name in ('mount','unshare','setns')}
    process={name:denied(lambda name=name:syscall(numbers[name],0,0,0,0,0,0))
             for name in ('ptrace','process_vm_writev','pidfd_getfd')}
    # The actual host PID values must be absent, not merely inaccessible.
    host_proc={str(pid):not Path(f'/proc/{pid}').exists() for pid in request['host_pids']}
    state=Path('/proc/self/status').read_text()
    emit({'type':'observation'})
    if sys.stdin.buffer.readline(32)!=b'continue\n':raise ValueError('protected observation acknowledgement lost')
    # Fresh exec uses only this exact frozen source/mode, never an input command.
    read,write=os.pipe2(os.O_CLOEXEC)
    pid=os.fork()
    if pid==0:
        os.dup2(write,1);os.close(read);os.close(write)
        os.execve('/usr/bin/python3.12',['/usr/bin/python3.12','-B','-I','-S',__file__,'--network-descendant'],dict(os.environ))
    os.close(write)
    raw=b''
    while True:
        part=os.read(read,4096)
        if not part:break
        raw+=part
        if len(raw)>32768:raise ValueError('exec control output bound exceeded')
    os.close(read)
    _,status=os.waitpid(pid,0)
    return {'writes':[write_attempt(path) for path in paths], 'privilege':privilege,
        'isolation':isolation,'process':process,'host_proc_absent':host_proc,
        'network':network.observe_network_denial(),'exec_network':json.loads(raw),
        'exec_returncode':os.waitstatus_to_exitcode(status),'status':state}


def tmpfs_control()->dict[str,Any]:
    before=os.statvfs('/attempt');path='/attempt/tmp/space-control'
    fd=os.open(path,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600)
    count=0;code=None
    try:
        block=b'\0'*(1024*1024)
        while count<135*1024**2:
            try:count+=os.write(fd,block)
            except OSError as error:code=error.errno;break
    finally:os.close(fd);os.unlink(path)
    execute='/attempt/tmp/noexec'
    # A genuine mapped ELF avoids confusing a missing #! interpreter with
    # noexec. If exec succeeds, the expected control-result frame is absent.
    Path(execute).write_bytes(Path('/usr/bin/python3.12').read_bytes());os.chmod(execute,0o700)
    outcome=denied(lambda:os.execve(execute,[execute],{}))
    Path(execute).unlink()
    return {'bytes':before.f_blocks*before.f_frsize,'written':count,'errno':code,'noexec':outcome}


def resource_control(case:str,request:dict[str,Any])->dict[str,Any]:
    if case=='oom':
        # Host first records original 12GiB READY, then tightens this TEST_ONLY
        # leaf to 32MiB. Actual oom_kill must be independently read by the host.
        payload=bytearray(64*1024**2)
        for at in range(0,len(payload),4096):payload[at]=1
        return {'unexpected_oom_survival':True}
    if case=='pids':
        children=[];code=None
        try:
            for _ in range(16):
                try:pid=os.fork()
                except OSError as error:code=error.errno;break
                if pid==0:
                    time.sleep(30);os._exit(0)
                children.append(pid)
        finally:
            for pid in children:os.kill(pid,signal.SIGKILL)
            for pid in children:os.waitpid(pid,0)
        return {'errno':code,'children':len(children)}
    requested=set(request['host_cpus'])
    os.sched_setaffinity(0,requested)
    return {'requested_affinity':sorted(requested),'effective_affinity':sorted(os.sched_getaffinity(0)),
            'tmpfs':tmpfs_control()}


def main()->int:
    if sys.argv[1:]==['--network-descendant']:
        network=module('/app/linux_network.py','fixed_control_network_exec')
        emit(network.observe_network_denial());return 0
    if sys.argv[1:] not in (['--preflight'],['--generate']):raise ValueError('fixed phase required')
    helper=module('/app/qwen_backend.py','fixed_control_bootstrap')
    lease=helper.check_bootstrap()
    if lease.get('schema')!=SCHEMA:raise ValueError('separate TEST_ONLY lease required')
    config=helper.protected_json('/app/actor-config.json')
    if config.get('schema')!=SCHEMA or config.get('scenario') not in (
            'baseline','boundaries','resources','supervisor-loss','guardian-loss','invalid-evidence'):
        raise ValueError('fixed control descriptor required')
    network=module('/app/linux_network.py','fixed_control_network')
    install=network.install_network_denial()
    before=network.observe_network_denial()
    emit({'type':'ready','facts':lease['observed'],'network':{'install':install,'before':before}})
    raw=sys.stdin.buffer.readline(65537)
    if len(raw)>65536 or not raw.endswith(b'\n'):raise ValueError('bounded fixed control input missing')
    envelope=json.loads(raw)
    if set(envelope)!={'input','prompt_utf8'} or envelope['prompt_utf8']!='TEST_ONLY fixed lease control':
        raise ValueError('fixed control input envelope required')
    request=envelope['input']
    if set(request)!={'scenario','case','host_pids','host_cpus'} or request['scenario']!=config['scenario']:
        raise ValueError('closed source-authored control input required')
    if sys.argv[1:] == ['--preflight']:
        emit({'type':'control','case':'preflight','network':before});return 0
    scenario,case=request['scenario'],request['case']
    if scenario in ('supervisor-loss','guardian-loss'):
        pid=os.fork()
        if pid==0:
            os.setsid();time.sleep(50);os._exit(0)
        time.sleep(50)
        raise ValueError('loss control was never triggered')
    if scenario=='boundaries':result=boundaries(request,network)
    elif scenario=='resources':result=resource_control(case,request)
    elif scenario=='invalid-evidence':
        if case=='overflow':
            sys.stdout.buffer.write(b'x'*65537);sys.stdout.buffer.flush();return 0
        if case=='ready':emit({'type':'ready'});return 0
        if case=='deadline':time.sleep(50);return 0
        if case=='source':result={'writes':[write_attempt('/app/linux_lease_control_child.py')]}
        else:result={'case':case}
    else:result={'network':network.observe_network_denial()}
    emit({'type':'control','case':case,'result':result})
    return 0


if __name__=='__main__':
    try:raise SystemExit(main())
    except Exception as error:
        emit({'type':'failure','error':type(error).__name__+': '+str(error)[:1000]})
        raise SystemExit(1)
