"""Pure passive evidence consistency controls; no live authority or OS observations."""
import base64
import copy
import json
import pytest
from test_linux_lease_control_ci_sudo import Kernel,ci


def positive(monkeypatch,count=1):
    model=Kernel(count);endpoint,record=model.run(monkeypatch)
    return record

@pytest.mark.parametrize('mutation',[
    lambda r:r.update(invoker_uid=2002),
    lambda r:r.update(selected_pid=999),
    lambda r:r['snapshots'][1]['identity'].update(ppid=999),
    lambda r:r['snapshots'][-1]['identity'].update(start='999'),
],ids=['summary-uid','summary-pid','parent-edge','reverse-start'])
def test_minimum_contradictory_verified_record_is_refused(monkeypatch,mutation):
    record=positive(monkeypatch);mutation(record)
    with pytest.raises(ValueError):ci.validate_ci_caller_record(record)

@pytest.mark.parametrize('count',[1,2])
def test_unchanged_valid_verified_record(monkeypatch,count):
    ci.validate_ci_caller_record(positive(monkeypatch,count))


def raw_bytes(item):return base64.b64decode(item['base64'],validate=True)
def replace_raw(snapshot,name,data):snapshot['raw'][name]=ci._CallerRoute.raw(data,True)


def change_identity(record,node,*,only_pass=None,**fields):
    """Change both passive parsed fields and their retained byte claims."""
    for snapshot in record['snapshots']:
        if snapshot['node']!=node or only_pass is not None and snapshot['pass']!=only_pass:continue
        identity=snapshot['identity'];identity.update(fields)
        status=raw_bytes(snapshot['raw']['status']).decode('ascii').splitlines()
        replacements={'Pid':str(identity['pid']),'PPid':str(identity['ppid']),'Uid':'\t'.join(map(str,identity['uid']))}
        status=[line.split(':',1)[0]+':\t'+replacements[line.split(':',1)[0]] if line.split(':',1)[0] in replacements else line for line in status]
        replace_raw(snapshot,'status',('\n'.join(status)+'\n').encode())
        text=raw_bytes(snapshot['raw']['stat']).decode('ascii');head,tail=text.rsplit(')',1);parts=tail.split()
        parts[1]=str(identity['ppid']);parts[19]=identity['start']
        replace_raw(snapshot,'stat',(head+') '+' '.join(parts)).encode())


def change_executable(record,node,*,only_pass=None,path=None,**metadata):
    for snapshot in record['snapshots']:
        if snapshot['node']!=node or only_pass is not None and snapshot['pass']!=only_pass:continue
        if path is not None:
            snapshot['executable']['path']=path;replace_raw(snapshot,'exe',path.encode())
        for side in ('named_file','image_file'):snapshot['executable'][side].update(metadata)


def refusal(record):
    record=copy.deepcopy(record);count=record['custody']['opened']['maximum']
    record.update(status='REFUSED',reason='observation-error',invoker_uid=None,selected_pid=None,
        faults=[{'stage':'close','node':0,'operation':'TEST_ONLY-refusal','error_type':'ValueError','errno':None,'message':'TEST_ONLY bounded evidence'}])
    record['custody'].update(closed={'minimum':count,'maximum':count},close_attempts=count,transferred_to_coordinator=0)
    return record

@pytest.mark.parametrize('mutation',[
    lambda r:change_identity(r,0,uid=[1001]*4),
    lambda r:change_identity(r,0,ppid=999),
    lambda r:change_identity(r,1,uid=[1001]*4),
    lambda r:change_identity(r,1,uid=[2002,0,0,0]),
    lambda r:change_identity(r,1,ppid=999),
    lambda r:change_identity(r,2,uid=[2002]*4),
    lambda r:change_executable(r,0,path='/usr/bin/bash'),
    lambda r:change_executable(r,1,path='/usr/bin/bash'),
    lambda r:change_executable(r,2,path='/usr/bin/sudo'),
    lambda r:change_executable(r,0,mode=0o104755),
    lambda r:change_executable(r,1,mode=0o100755),
    lambda r:change_executable(r,1,mode=0o106755),
    lambda r:change_executable(r,2,mode=0o104755),
    lambda r:change_executable(r,2,mode=0o100777),
    lambda r:r.update(next_pid=999),
],ids=['nonroot-self','self-edge','uniform-sudo','mismatched-user','sudo-edge','endpoint-user',
       'self-exe','sudo-exe','endpoint-sudo','self-privileged','sudo-not-setuid','sudo-setgid',
       'endpoint-privileged','mutable-endpoint','next-pid'])
def test_consistent_raw_bytes_cannot_hide_invalid_connected_roles(monkeypatch,mutation):
    record=positive(monkeypatch);mutation(record)
    with pytest.raises(ValueError):ci.validate_ci_caller_record(record)

@pytest.mark.parametrize('mutation',[
    lambda r:change_identity(r,2,uid=[2002,0,0,0]),
    lambda r:change_executable(r,2,inode=999),
],ids=['second-sudo-different-user','second-sudo-different-file'])
def test_two_sudo_nodes_must_share_user_and_protected_file(monkeypatch,mutation):
    record=positive(monkeypatch,2);mutation(record)
    with pytest.raises(ValueError):ci.validate_ci_caller_record(record)

@pytest.mark.parametrize('mutation',[
    lambda r:change_identity(r,1,only_pass=1,start='999'),
    lambda r:change_identity(r,1,only_pass=1,ppid=999),
    lambda r:change_executable(r,1,only_pass=1,inode=999),
    lambda r:change_executable(r,2,only_pass=1,path='/usr/bin/TEST_ONLY-other'),
],ids=['start','parent','image','path'])
def test_complete_raw_consistent_reverse_drift_is_not_verified(monkeypatch,mutation):
    record=positive(monkeypatch);mutation(record)
    with pytest.raises(ValueError):ci.validate_ci_caller_record(record)

@pytest.mark.parametrize('target',['status','stat','exe'])
@pytest.mark.parametrize('status',['VERIFIED','REFUSED'])
def test_complete_raw_inputs_must_agree_with_any_present_parsed_fact(monkeypatch,target,status):
    record=positive(monkeypatch)
    if status=='REFUSED':record=refusal(record)
    snapshot=record['snapshots'][1]
    if target=='status':replace_raw(snapshot,target,b'Pid: 20\nPPid: 30\nUid: 2002 0 0 0\n')
    elif target=='stat':
        raw=raw_bytes(snapshot['raw']['stat']).replace(b'120',b'999');replace_raw(snapshot,target,raw)
    else:replace_raw(snapshot,target,b'/usr/bin/bash')
    with pytest.raises(ValueError):ci.validate_ci_caller_record(record)

@pytest.mark.parametrize('mutation',[
    lambda r:r.update(snapshots=[r['snapshots'][0],r['snapshots'][0]]),
    lambda r:r['snapshots'].__setitem__(slice(0,2),list(reversed(r['snapshots'][:2]))),
    lambda r:r['snapshots'].__setitem__(3,r['snapshots'][-1]),
    lambda r:r['snapshots'][3].update(requested_pid=999,identity=None,executable=None),
    lambda r:r.update(snapshots=[r['snapshots'][0],r['snapshots'][2]]),
],ids=['duplicate','forward-order','reverse-order','replaced-held-pid','forward-gap'])
def test_refused_positions_are_unique_ordered_prefixes(monkeypatch,mutation):
    record=refusal(positive(monkeypatch));mutation(record)
    with pytest.raises(ValueError):ci.validate_ci_caller_record(record)


def test_full_refusal_can_record_actual_late_failure_without_rewriting_clock(monkeypatch):
    record=refusal(positive(monkeypatch));record['finished']=1001.
    ci.validate_ci_caller_record(record)
    assert record['faults'][0]['message']=='TEST_ONLY bounded evidence'

@pytest.mark.parametrize('malformed',['status','stat','exe'])
def test_actual_malformed_partial_refusal_preserves_raw_and_null_facts(monkeypatch,malformed):
    model=Kernel();count=[0]
    def hook(event):
        if event[:3]==('close','internal-reader',20):
            count[0]+=1
            if count[0]==4:
                if malformed=='exe':model.exe_override[20]='relative'
                else:getattr(model,malformed+'_override')[20]='TEST_ONLY malformed raw'
    model.hook=hook
    with pytest.raises(ci.CiCallerError) as raised:model.run(monkeypatch)
    record=raised.value.facts;ci.validate_ci_caller_record(record)
    snapshot=record['snapshots'][-1]
    assert snapshot['raw'][malformed] is not None
    assert snapshot['identity' if malformed!='exe' else 'executable'] is None


def test_actual_unknown_parent_remains_unobserved(monkeypatch):
    model=Kernel();model.open_fail=lambda kind,pid:pid==30
    with pytest.raises(ci.CiCallerError) as raised:model.run(monkeypatch)
    record=raised.value.facts;ci.validate_ci_caller_record(record)
    assert record['next_pid']==30 and len(record['snapshots'])==2
    assert all(snapshot['requested_pid']!=30 for snapshot in record['snapshots'])


def test_actual_reverse_identity_drift_remains_valid_refusal_evidence(monkeypatch):
    model=Kernel()
    def hook(event):
        if event[:3]==('close','image',30):model.nodes[20]['uid']=[2002,0,0,0]
    model.hook=hook
    with pytest.raises(ci.CiCallerError) as raised:model.run(monkeypatch)
    record=raised.value.facts;ci.validate_ci_caller_record(record)
    first=next(s for s in record['snapshots'] if (s['pass'],s['node'])==(0,1))
    last=record['snapshots'][-1]
    assert first['identity']['uid']==[1001,0,0,0] and last['identity']['uid']==[2002,0,0,0]


def test_passive_checker_never_acquires_or_restores_an_identity(monkeypatch):
    record=positive(monkeypatch)
    def forbidden(*args,**kwargs):raise AssertionError('passive validator must not enter acquisition')
    monkeypatch.setattr(ci,'ci_original_caller',forbidden)
    monkeypatch.setattr(ci._CallerRoute,'__init__',forbidden)
    assert ci.validate_ci_caller_record(record) is None
