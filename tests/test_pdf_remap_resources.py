"""Public invented DATA and private OS models only; never stage or run a PDF/tool."""
import copy
import pytest
from twin import source_metadata as sm, pdf_comparison_capture as c
from twin import pdf_remap_resources as r
from test_pdf_comparison_capture import prepared_fixture

ROOT='/TEST_ONLY-remap-controls'
IDENTITIES={'identity':[1,710,0o100444,1001,1001,1,10,123,123],
            'a-to-b':[1,711,0o100444,1001,1001,1,10,123,123],
            'a-to-ab':[1,712,0o100444,1001,1001,1,15,123,123]}


def prepared():
    pair,plan,archive=prepared_fixture()
    return r.make_remap_plans(ROOT,copy.deepcopy(IDENTITIES),plan,archive)


def test_three_fixed_external_plans_are_closed_acyclic_data():
    rows=prepared()
    assert len(rows)==3
    literals=[('identity','identity-remap.txt',b'0041 0041\n',18),
              ('a-to-b','a-to-b-remap.txt',b'0041 0042\n',19),
              ('a-to-ab','a-to-ab-remap.txt',b'0041 0041 0042\n',20)]
    for packet,(control,name,raw,index) in zip(rows,literals):
        pair=packet['pair_plan'];plan=packet['comparison_plan'];archive=packet['archive'];resource=pair['resource']
        assert pair['schema']=='TEST_ONLY-pdf-pair-plan/v2' and pair['schedule_index']==index
        assert plan['schema']=='TEST_ONLY-pdf-baseline-plan/v2' and plan['schedule_index']==2*index
        assert resource['control']==control and resource['path']==ROOT+'/'+name
        assert archive[resource['blob']['sha256']]==raw
        assert archive[pair['config']['sha256']]==b'unicodeRemapping '+(ROOT+'/'+name).encode()+b'\n'
        association=sm._json(archive[resource['association_sha256']])
        assert set(association)=={'schema','control','fixture_id','fixture','resource_path','resource_blob','resource_identity','native_config'}
        assert association['resource_identity']==IDENTITIES[control] and association['native_config']==pair['config']
        assert set(resource)=={'schema','control','blob','path','identity','association_sha256'}
    assert rows[0]['pair_plan']['resource']['blob']['sha256']=='77aa81ad83d4b04fd7547b35aae96948468255f69c190e722879863bfeab4bcb'
    assert rows[0]['pair_plan']['config']['sha256']=='10839aaab3ac06b7c3263a97c1c564938f476f9490cfd2a36989baefcb2c22db'


@pytest.mark.parametrize('substitute',[{}, object(), ROOT, sm.sha256(b'public bytes')])
def test_passive_values_cannot_stage_or_cleanup(monkeypatch,substitute):
    def forbidden(*a,**k):raise AssertionError('OS reached from passive DATA')
    monkeypatch.setattr(r.os,'open',forbidden);monkeypatch.setattr(r.time,'monotonic',forbidden)
    with pytest.raises(ValueError):r._stage_remap_resources(substitute,ROOT)
    with pytest.raises(ValueError):r._cleanup_remap_resources(substitute)


from types import SimpleNamespace
import os
import stat
from test_pdf_comparison_capture import authority_model, GuardModel


class OSModel:
    """Private file-description/inode model. No real descriptor or path exists."""
    def __init__(self):
        self.nodes={'/':self.node(1,stat.S_IFDIR|0o755),'/TEST_ONLY':self.node(2,stat.S_IFDIR|0o700)}
        self.fds={};self.nextfd=10;self.nextino=100;self.log=[];self.fail=None;self.short=False
    def node(self,ino,mode,raw=b''):
        return {'ino':ino,'mode':mode,'raw':raw,'uid':1001,'gid':1001,'time':123}
    def path(self,path,dir_fd=None):
        return path if path.startswith('/') else self.fds[dir_fd][0].rstrip('/')+'/'+path
    def check(self,op):
        self.log.append(op)
        if self.fail==op:raise OSError(5,'TEST_ONLY injected failure')
    def open(self,path,flags,mode=0o600,dir_fd=None):
        self.check('open');path=self.path(path,dir_fd)
        assert flags & os.O_NOFOLLOW and flags & os.O_CLOEXEC
        if flags&os.O_CREAT:
            assert flags&os.O_EXCL
            if path in self.nodes:raise FileExistsError(path)
            self.nextino+=1;self.nodes[path]=self.node(self.nextino,stat.S_IFREG|mode)
        if path not in self.nodes:raise FileNotFoundError(path)
        if stat.S_ISLNK(self.nodes[path]['mode']):raise OSError(40,'symlink')
        self.nextfd+=1;self.fds[self.nextfd]=[path,0];return self.nextfd
    def close(self,fd):
        self.log.append(('close',fd));self.fds.pop(fd)
        if self.fail=='close':raise OSError(4,'unknown close disposition')
    def stat(self,path,dir_fd=None,follow_symlinks=False):
        self.check('stat');node=self.nodes[self.path(path,dir_fd)]
        return SimpleNamespace(st_dev=1,st_ino=node['ino'],st_mode=node['mode'],st_uid=node['uid'],st_gid=node['gid'],st_nlink=1 if stat.S_ISREG(node['mode']) else 2,st_size=len(node['raw']),st_mtime_ns=node['time'],st_ctime_ns=node['time'])
    def fstat(self,fd):self.check('fstat');return self.stat(self.fds[fd][0])
    def mkdir(self,path,mode,dir_fd=None):
        self.check('mkdir');path=self.path(path,dir_fd)
        if path in self.nodes:raise FileExistsError(path)
        self.nextino+=1;self.nodes[path]=self.node(self.nextino,stat.S_IFDIR|mode)
    def write(self,fd,raw):
        self.check('write');node=self.nodes[self.fds[fd][0]];count=1 if self.short else len(raw)
        node['raw']+=raw[:count];return count
    def read(self,fd,count):
        self.check('read');entry=self.fds[fd];raw=self.nodes[entry[0]]['raw'][entry[1]:entry[1]+count];entry[1]+=len(raw);return raw
    def fchmod(self,fd,mode):self.check('chmod');node=self.nodes[self.fds[fd][0]];node['mode']=stat.S_IFMT(node['mode'])|mode
    def fsync(self,fd):self.check('fsync')
    def unlink(self,path,dir_fd=None):self.check('unlink');del self.nodes[self.path(path,dir_fd)]
    def rmdir(self,path,dir_fd=None):
        self.check('rmdir');path=self.path(path,dir_fd)
        assert not any(p.startswith(path+'/') for p in self.nodes)
        del self.nodes[path]
    def surface(self):
        values={name:getattr(os,name) for name in ('O_RDONLY','O_WRONLY','O_CREAT','O_EXCL','O_NOFOLLOW','O_CLOEXEC','O_NONBLOCK','O_DIRECTORY')}
        values.update({name:getattr(self,name) for name in ('open','close','stat','fstat','mkdir','write','read','fchmod','fsync','unlink','rmdir')})
        return SimpleNamespace(**values,geteuid=lambda:1001)


def stage_model(monkeypatch):
    _,plan,archive=prepared_fixture();original=authority_model(plan,archive)._session
    clock=[original._started+1];model=OSModel()
    monkeypatch.setattr(r,'os',model.surface());monkeypatch.setattr(r.time,'monotonic',lambda:clock[0]);monkeypatch.setattr(r,'_source_guard',lambda:GuardModel())
    return original,model,clock


def test_fixed_stage_short_writes_retains_all_three_until_known_final_cleanup(monkeypatch):
    original,model,clock=stage_model(monkeypatch);model.short=True
    data=r._stage_remap_resources(original,'/TEST_ONLY/resources')
    assert data['phase']=='COMPLETE_STAGE' and len(data['identities'])==3
    assert [model.nodes['/TEST_ONLY/resources/'+name]['raw'] for _,name,_ in r.RECIPES]==[b'0041 0041\n',b'0041 0042\n',b'0041 0041 0042\n']
    assert all(model.nodes['/TEST_ONLY/resources/'+name]['mode']==0o100444 for _,name,_ in r.RECIPES)
    assert original._retained==2*1048576 and len(model.fds)==2
    assert data['stage_deadline']==original._started+6
    with pytest.raises(ValueError):r._stage_remap_resources(original,'/TEST_ONLY/second')
    clock[0]=original._started+9000
    result=r._cleanup_remap_resources(original)
    assert result['phase']=='REMOVED' and result['final_cleanup_deadline']==original._started+9002
    assert '/TEST_ONLY/resources' not in model.nodes and model.fds=={} and original._stopped
    with pytest.raises(ValueError):r._cleanup_remap_resources(original)


@pytest.mark.parametrize('failure',['open','mkdir','write','read','fstat','chmod','fsync','close'])
def test_stage_fault_is_terminal_no_reset_or_second_close(monkeypatch,failure):
    original,model,clock=stage_model(monkeypatch);model.fail=failure
    with pytest.raises((ValueError,OSError)):r._stage_remap_resources(original,'/TEST_ONLY/resources')
    held=original._technical_state
    assert held is not None and original._stopped
    with pytest.raises(ValueError):original._technical_state=None
    with pytest.raises(ValueError):r._stage_remap_resources(original,'/TEST_ONLY/retry')
    with pytest.raises(ValueError):r._cleanup_remap_resources(original)
    closes=[entry[1] for entry in model.log if type(entry) is tuple and entry[0]=='close']
    assert len(closes)==len(set(closes))
    if failure=='close':assert r._held_stage_data(original)['uncertain_ownership']


@pytest.mark.parametrize('mutation',['null-clock','late-clock','pre-original','storage','stale-root','symlink','wrong-parent-owner','parent-public'])
def test_stage_neighbor_refusals_keep_original_placeholder(monkeypatch,mutation):
    original,model,clock=stage_model(monkeypatch)
    if mutation=='null-clock':clock[0]=float('nan')
    if mutation=='late-clock':clock[0]=original._started+60
    if mutation=='pre-original':clock[0]=original._started-1
    if mutation=='storage':original._retained=c.MAX_SUITE_BYTES
    if mutation=='stale-root':model.nodes['/TEST_ONLY/resources']=model.node(123,stat.S_IFDIR|0o700)
    if mutation=='symlink':model.nodes['/TEST_ONLY']['mode']=stat.S_IFLNK|0o777
    if mutation=='wrong-parent-owner':model.nodes['/TEST_ONLY']['uid']=0
    if mutation=='parent-public':model.nodes['/TEST_ONLY']['mode']=stat.S_IFDIR|0o755
    with pytest.raises((ValueError,OSError)):r._stage_remap_resources(original,'/TEST_ONLY/resources')
    assert original._technical_state is not None and original._stopped
    if mutation in ('null-clock','pre-original','storage'):assert model.log==[]
    if mutation=='stale-root':assert model.nodes['/TEST_ONLY/resources']['ino']==123


@pytest.mark.parametrize('mutation',['active','replacement','deadline','final-null','close-fault','unlink-fault','rmdir-fault'])
def test_final_cleanup_holds_unknown_or_replaced_custody_without_sweep(monkeypatch,mutation):
    original,model,clock=stage_model(monkeypatch);r._stage_remap_resources(original,'/TEST_ONLY/resources')
    if mutation=='active':
        original._next=1;original._used_hosts.add('a'*64);original._active_slot=0;original._target_custody_known=False
    if mutation=='replacement':model.nodes['/TEST_ONLY/resources/identity-remap.txt']['ino']=999
    if mutation=='deadline':clock[0]=original._started+10800
    if mutation=='final-null':clock[0]=float('nan')
    if mutation=='close-fault':model.fail='close'
    if mutation=='unlink-fault':model.fail='unlink'
    if mutation=='rmdir-fault':model.fail='rmdir'
    with pytest.raises((ValueError,OSError)):r._cleanup_remap_resources(original)
    if mutation not in ('close-fault','rmdir-fault'):assert '/TEST_ONLY/resources' in model.nodes
    if mutation=='replacement':assert model.nodes['/TEST_ONLY/resources/identity-remap.txt']['ino']==999
    with pytest.raises(ValueError):r._cleanup_remap_resources(original)


@pytest.mark.parametrize('root',['/','relative','/a/../b','/a//b','/a/./b','/a/','/a b','/a\nb','/a"b','/a\\b','/proc/a','/sys/a','/dev/a','/a/'+('x'*4096)])
def test_noncanonical_technical_roots_refused(root):
    _,plan,archive=prepared_fixture()
    with pytest.raises(ValueError):r.make_remap_plans(root,IDENTITIES,plan,archive)


@pytest.mark.parametrize('mutation',['unknown','bool-inode','zero-inode','mode','link','size','alias-control','wrong-association','v1','wrong-index','wrong-fixture','wrong-config','resource-omission','all-resources'])
def test_closed_plan_neighbor_mutations_refuse(mutation):
    packets=prepared();packet=copy.deepcopy(packets[0]);pair=packet['pair_plan'];plan=packet['comparison_plan'];res=pair['resource'];archive=packet['archive']
    if mutation=='unknown':res['authority']=True
    if mutation=='bool-inode':res['identity'][1]=True
    if mutation=='zero-inode':res['identity'][1]=0
    if mutation=='mode':res['identity'][2]=0o100644
    if mutation=='link':res['identity'][5]=2
    if mutation=='size':res['identity'][6]+=1
    if mutation=='alias-control':res['control']='A-to-B'
    if mutation=='wrong-association':res['association_sha256']=sm.sha256(b'{}');archive[res['association_sha256']]=b'{}'
    if mutation=='v1':pair['schema']='TEST_ONLY-pdf-pair-plan/v1'
    if mutation=='wrong-index':pair['schedule_index']=17
    if mutation=='wrong-fixture':pair['fixture_id']=c.FIXTURES[1][0]
    if mutation=='wrong-config':pair['config']={'sha256':sm.sha256(b''),'bytes':0};archive[sm.sha256(b'')]=b''
    if mutation in ('resource-omission','all-resources'):
        rows=sm._json(archive[plan['candidate_inventory_sha256']]);rows=[row for row in rows if row['path']!=res['path']] if mutation=='resource-omission' else rows+[{'path':packets[1]['pair_plan']['resource']['path'],**packets[1]['pair_plan']['resource']['blob']}]
        archive.update(packets[1]['archive']);raw=sm.canonical(rows);archive[sm.sha256(raw)]=raw;plan['candidate_inventory_sha256']=sm.sha256(raw)
    with pytest.raises((ValueError,KeyError)):r.check_remap_plan(packet)


from test_source_native_observation import call,blob,splice
from twin import source_native_observation as n, pdf_native_bridge as bridge, pdf_output_origin as origin


def read_model():
    packet=prepared()[0];res=packet['pair_plan']['resource'];archive=packet['archive']
    wanted={res['path']:{**res['blob'],'identity':res['identity']},'/work/native-config':{**packet['pair_plan']['config'],'identity':[1,999,0o100444,1001,1001,1,packet['pair_plan']['config']['bytes'],1,1]}}
    events=[{'kind':'start','seq':0,'data':{'fds':[{'fd':0},{'fd':1},{'fd':2},{'fd':3}]}}]
    for path,row in wanted.items():
        for kind,data in call(2,[0,0x80000],{'path':path},4,{'kind':'file','identity':row['identity']})+call(0,[4,4096,row['bytes']+1],result=row['bytes'],detail={'buffer_sha256':row['sha256']})+call(0,[4,4096,1],result=0,detail={'buffer_sha256':sm.sha256(b'')})+call(3,[4]):events.append({'kind':kind,'data':data,'seq':len(events)})
    return {'events':events},archive,wanted


def test_full_original_description_reads_allow_prior_numeric_generation_and_real_eof():
    obs,archive,wanted=read_model();facts=r._full_original_reads(obs,archive,wanted)
    assert [row[0]['generation'] for row in facts.values()]==[0,1]
    assert all(row[0]['offset']==0 for row in facts.values())


@pytest.mark.parametrize('mutation',['unused','partial','zero','error','wrong-hash','wrong-identity','alias','seek','map','reopen','close-error','wrong-path'])
def test_declaration_and_neighbor_reads_do_not_prove_use(mutation):
    obs,archive,wanted=read_model();events=obs['events']
    if mutation=='unused':obs['events']=events[:1]
    if mutation=='partial':events[4]['data']['result']-=1
    if mutation=='zero':events[4]['data']['result']=0
    if mutation=='error':events[4]['data']['result']=-5
    if mutation=='wrong-hash':events[4]['data']['detail']['buffer_sha256']='f'*64
    if mutation=='wrong-identity':events[2]['data']['detail']['identity']=[1]*9
    if mutation=='wrong-path':events[1]['data']['detail']['path']='/other'
    if mutation in ('alias','seek','map'):
        nr,args={'alias':(32,[4]),'seek':(8,[4,0,0]),'map':(9,[0,4096,1,2,4,0])}[mutation]
        events.insert(3,{'seq':99,'kind':'enter','data':{'nr':nr,'args':args+[0]*(6-len(args)),'detail':{}}})
    if mutation=='reopen':events[9]['data']['detail']['path']=events[1]['data']['detail']['path']
    if mutation=='close-error':events[8]['data']['result']=-4
    with pytest.raises(ValueError):r._full_original_reads(obs,archive,wanted)


def origin_wire(control):
    import json
    from pathlib import Path
    records=[json.loads(line) for line in (Path(__file__).parent/'fixtures/TEST_ONLY-pdf-output-origin/TEST_ONLY-contiguous-fragment.jsonl').read_bytes().splitlines()]
    scalars={'identity':[65],'a-to-b':[66],'a-to-ab':[65,66]}[control]
    records[2]['scalars']=scalars;records[2]['taint']='none' if control=='identity' else 'unicode-remap'
    prefix=records[:5];offset=0
    for item,values in ((1,scalars),(2,[66])):
        for scalar,value in enumerate(values):
            raw=chr(value).encode();prefix.append({'record':'emit','seq':len(prefix)-1,'start':offset,'end':offset+len(raw),'origin_item':item,'origin_scalar':scalar,'operation':'modified' if item==1 and control!='identity' else 'decoded','reason':'remap' if item==1 and control!='identity' else 'source','utf8_hex':raw.hex()});offset+=len(raw)
    output=bytes(scalars)+b'B';raw=b''.join(sm.canonical(row)+b'\n' for row in prefix)
    footer={'record':'footer','event_count':len(prefix)-1,'event_prefix_bytes':len(raw),'event_prefix_sha256':sm.sha256(raw),'closed_fragment_count':1,'emitted_stdout_bytes':len(output),'emitted_stdout_sha256':sm.sha256(output),'intended_exit_code':0}
    wire=raw+sm.canonical(footer)+b'\n';origin.check_pdf_origin_events(output,wire)
    return output,wire


def full_control_fixture(index=0):
    """Complete constructed comparative/native replay, no converter/build involved."""
    from test_pdf_native_bridge import bundle_fixture
    from test_pdf_comparison_capture import event_fixture
    native_plan,_,right,right_archive=bundle_fixture();ordinary_pair,ordinary_plan,archive=prepared_fixture();archive.update(right_archive)
    config=sm._json(archive[native_plan['configuration_sha256']]);right_build=config['pdf_origin']['build_identity_sha256'];right_build_data=sm._json(archive[right_build])
    left_build=sm._json(archive[ordinary_pair['build_pair']['pristine_build_sha256']]);left_build['toolchain_recipe_sha256']=right_build_data['toolchain_sha256'];left_build['configuration_recipe_sha256']=right_build_data['build_configuration_sha256']
    left_pin=blob(archive,sm.canonical(left_build));ordinary_pair['build_pair'].update(pristine_build_sha256=left_pin,patched_build_sha256=right_build,same_toolchain_recipe_sha256=right_build_data['toolchain_sha256'])
    ordinary_plan['build_identity_sha256']=left_pin;ordinary_plan['pair_plan_sha256']=blob(archive,sm.canonical(ordinary_pair))
    packet=r.make_remap_plans(ROOT,copy.deepcopy(IDENTITIES),ordinary_plan,archive)[index];archive=packet['archive'];pair=packet['pair_plan'];res=pair['resource']
    config['native_config_sha256']=pair['config']['sha256'];native_plan['configuration_sha256']=blob(archive,sm.canonical(config));native_plan['parent_sha256']=pair['fixture']['sha256'];native_plan['parent_bytes']=pair['fixture']['bytes']
    closure=sm._json(archive[native_plan['implementation_artifact_sha256']]);closure['platform_files']=[{'path':res['path'],**res['blob']}];native_plan['implementation_artifact_sha256']=blob(archive,sm.canonical(closure));native_plan['archive']=archive
    left,left_archive=event_fixture();left_archive.update(archive);right_archive.update(archive)
    output,wire=origin_wire(res['control'])
    for obs,held,patched in ((left,left_archive,False),(right,right_archive,True)):
        plan=native_plan if patched else packet['comparison_plan']
        candidates=({row['path']:row for row in closure['process_files']['files']+closure['platform_files']+closure['driver_files']} if patched else {row['path']:row for row in c._candidate_rows(plan,archive,'/work')})
        if patched:
            for name,raw in [('input',archive[pair['fixture']['sha256']]),('config',archive[native_plan['configuration_sha256']]),('native-config',archive[pair['config']['sha256']])]:candidates['/work/'+name]={'path':'/work/'+name,'sha256':blob(held,raw),'bytes':len(raw)}
        obs['spec']['candidates']=list(candidates.values());obs['spec']['plan_sha256']=sm.sha256(sm.canonical({k:v for k,v in plan.items() if k!='archive'}))
        for i,(path,row) in enumerate(candidates.items()):obs['files'][path]={**row,'identity':copy.deepcopy(res['identity']) if path==res['path'] else [9,100+i,0o100444,1000,1000,1,row['bytes'],1,1]}
        # Preserve original executable map identities, independent of unused candidates.
        for path in ('/bin/tool','/lib/loader'):obs['files'][path]['identity']=copy.deepcopy(right['files'][path]['identity']) if not patched else obs['files'][path]['identity']
        maps=obs['events'][2]['data']['maps']
        for row in maps:row['identity']=obs['files'][row['path']]['identity'][:2]
        next(e for e in obs['events'] if e['kind']=='exit-stop')['data']['maps']=copy.deepcopy(maps)
        for i,e in enumerate(obs['events']):
            if e['kind']=='enter' and e['data']['nr']==1:
                channel=e['data']['args'][0];raw=wire if channel==3 else output
                e['data']['args'][2]=len(raw);e['data']['detail']['buffer_sha256']=blob(held,raw);obs['events'][i+1]['data']['result']=len(raw)
        reads=[]
        for path in (res['path'],'/work/native-config'):
            row=obs['files'][path];reads+=call(2,[0,0x80000],{'path':path},4,{'kind':'file','identity':row['identity']})+call(0,[4,4096,row['bytes']+1],result=row['bytes'],detail={'buffer_sha256':row['sha256']})+call(3,[4])
        splice(obs,reads)
        terminal=obs['events'][-1]['data'];terminal['stdout_sha256']=blob(held,output)
        if patched:terminal['origin_sha256']=blob(held,wire);terminal['origin_bytes']=len(wire)
        for e in obs['events']:
            if e['kind']=='pipe-eof':e['data']['captured_bytes']=len(output) if e['data']['channel']=='stdout' else len(wire) if e['data']['channel']=='origin' else 0
        end=len(obs['events'])*1000;obs['events'][-1]['at_ns']=end;terminal['wait']['observed_at_ns']=next(e['at_ns'] for e in obs['events'] if e['kind']=='exit-stop')+500
        start=obs['run']['monotonic_start_ns'];obs['run'].update(elapsed_ns=end,ended_at='2026-10-31T00:00:00.'+f'{end//1000:06d}'+'+00:00',cleanup_started_ns=start+end,cleanup_deadline_ns=start+end+2*10**9)
        terminal['custody'].update(grace_deadline=(start+end+2*10**9)/10**9,cleanup_ended=(start+end)/10**9)
        if patched:obs['run']['run_id']=n._run_identity(obs['spec'],obs['run'],obs['events'][0]['data'])
    return packet,{'observation':left,'archive':left_archive,'plan':packet['comparison_plan']},{'observation':right,'archive':right_archive,'plan':native_plan}


@pytest.mark.parametrize('index',[0,1,2])
def test_full_pure_replays_and_control_effect_gate_are_data_only(index):
    packet,left,right=full_control_fixture(index)
    result=r.check_remap_control(packet,left,right)
    assert result['qualification']=='NONE' and result['control']==['identity','a-to-b','a-to-ab'][index]
    assert result['stream_exit_equality']=={'stdout':True,'stderr':True,'exit':True}


@pytest.mark.parametrize('mutation',['resource','config','association','build','root','bytes'])
def test_h_requires_independently_preselected_raw_resource_config_and_association(mutation):
    packet=prepared()[0];projection=r.remap_native_projection(packet);evidence=projection['evidence']
    policy:dict={'schema':'twin.native-host-policy/v1','scope':n.SCOPE,'custodian':'TEST_ONLY pure preselection model','not_before':'2026-10-31T00:00:00+00:00','not_after':'2026-10-31T01:00:00+00:00','roots':[ROOT],'writer_control':'trusted-administrator-controlled-interval','evidence_sha256s':sorted(evidence)}
    r.check_remap_host_evidence(packet,policy,evidence)
    if mutation=='root':policy['roots']=['/elsewhere']
    elif mutation=='bytes':evidence[next(iter(evidence))]=b'declared but not selected bytes'
    else:
        key={'resource':packet['pair_plan']['resource']['blob']['sha256'],'config':packet['pair_plan']['config']['sha256'],'association':packet['pair_plan']['resource']['association_sha256'],'build':packet['pair_plan']['build_pair']['pristine_build_sha256']}[mutation]
        policy['evidence_sha256s'].remove(key)
    with pytest.raises(ValueError):r.check_remap_host_evidence(packet,policy,evidence)


def replace_stream(obs,archive,channel,raw):
    for i,e in enumerate(obs['events']):
        if e['kind']=='enter' and e['data']['nr']==1 and e['data']['args'][0]==channel:
            e['data']['args'][2]=len(raw);e['data']['detail']['buffer_sha256']=blob(archive,raw);obs['events'][i+1]['data']['result']=len(raw)
    name={1:'stdout',3:'origin'}[channel];terminal=obs['events'][-1]['data'];terminal[name+'_sha256']=blob(archive,raw)
    if channel==3:terminal['origin_bytes']=len(raw)
    for e in obs['events']:
        if e['kind']=='pipe-eof' and e['data']['channel']==name:e['data']['captured_bytes']=len(raw)


@pytest.mark.parametrize('mutation',['unused','partial-read','wrong-effect','missing-input-A','adverse-stdout','resource-identity','raw-wrapper','unknown-bundle','wrong-plan','wrong-build','wrong-platform','wrong-native-config'])
def test_full_gate_refuses_valid_replay_without_complete_selected_remap_use(mutation):
    packet,left,right=full_control_fixture(1)
    if mutation in ('unused','partial-read'):
        events=left['observation']['events']
        if mutation=='unused':
            del events[4:10]
            for seq,event in enumerate(events):event['seq']=seq
        else:
            data=next(e['data'] for e in events if e['kind']=='leave' and 'buffer_bytes' in e['data']['detail']);data['result']-=1;data['detail']['buffer_bytes']-=1
            raw=left['archive'][data['detail']['buffer_sha256']][:-1];data['detail']['buffer_sha256']=blob(left['archive'],raw)
        c.check_comparison_events(left['observation'],left['archive'],observation_mode='SIMULATED_DATA')
    if mutation in ('wrong-effect','missing-input-A'):
        control='identity' if mutation=='wrong-effect' else 'a-to-b';output,wire=origin_wire(control)
        if mutation=='missing-input-A':
            import json
            rows=[json.loads(line) for line in wire.splitlines()];rows[2]['input_scalars']=[88]
            raw=b''.join(sm.canonical(row)+b'\n' for row in rows[:-1]);rows[-1].update(event_prefix_sha256=sm.sha256(raw),event_prefix_bytes=len(raw));wire=raw+sm.canonical(rows[-1])+b'\n'
            origin.check_pdf_origin_events(output,wire)
        replace_stream(left['observation'],left['archive'],1,output);replace_stream(right['observation'],right['archive'],1,output);replace_stream(right['observation'],right['archive'],3,wire)
    if mutation=='adverse-stdout':replace_stream(left['observation'],left['archive'],1,b'actual comparative mismatch')
    if mutation=='resource-identity':packet['pair_plan']['resource']['identity'][1]+=1
    if mutation=='raw-wrapper':right['plan']['configuration_sha256']=packet['pair_plan']['config']['sha256']
    if mutation=='unknown-bundle':left['actual']=True
    if mutation=='wrong-plan':left['plan']=packet['pair_plan']
    if mutation=='wrong-build':packet['pair_plan']['build_pair']['patched_build_sha256']='b'*64
    if mutation=='wrong-platform':
        closure=sm._json(right['archive'][right['plan']['implementation_artifact_sha256']]);closure['platform_files']=[];right['plan']['implementation_artifact_sha256']=blob(right['archive'],sm.canonical(closure))
    if mutation=='wrong-native-config':
        config=sm._json(right['archive'][right['plan']['configuration_sha256']]);config['native_config_sha256']=blob(right['archive'],b'fallback config');right['plan']['configuration_sha256']=blob(right['archive'],sm.canonical(config))
    with pytest.raises((ValueError,KeyError)):r.check_remap_control(packet,left,right)


def test_wrapper_and_raw_config_are_distinct_earlier_h_pins_and_native_projection_stays_three_fields():
    packet,left,right=full_control_fixture();wrapper=right['archive'][right['plan']['configuration_sha256']];projection=r.remap_native_projection(packet,wrapper)
    assert set(projection['platform_file'])=={'path','sha256','bytes'}
    assert projection['patched_wrapper_sha256']!=projection['native_config_sha256']
    assert len(projection['evidence'])==5
    with pytest.raises(ValueError):r.remap_native_projection(packet,packet['archive'][packet['pair_plan']['config']['sha256']])


def test_negative_identity_times_remain_closed_resource_data_not_native_capability():
    _,plan,archive=prepared_fixture();identities=copy.deepcopy(IDENTITIES);identities['identity'][7:]=[-2,-1]
    packet=r.make_remap_plans(ROOT,identities,plan,archive)[0]
    assert packet['pair_plan']['resource']['identity'][7:]==[-2,-1]


def test_original_stage_deadline_expiry_during_write_cannot_borrow_final_window(monkeypatch):
    original,model,clock=stage_model(monkeypatch);write=model.write
    def late(fd,raw):
        result=write(fd,raw);clock[0]=original._started+6;return result
    model.write=late;monkeypatch.setattr(r,'os',model.surface())
    with pytest.raises(ValueError):r._stage_remap_resources(original,'/TEST_ONLY/resources')
    data=r._held_stage_data(original)
    assert data['phase']=='PRESERVED' and data['stage_deadline']==original._started+6 and data['final_cleanup_deadline'] is None
    assert '/TEST_ONLY/resources' in model.nodes
    with pytest.raises(ValueError):r._cleanup_remap_resources(original)


def test_partial_write_failure_cleanup_uses_original_window_only(monkeypatch):
    original,model,clock=stage_model(monkeypatch);write=model.write;calls=[0]
    def partial(fd,raw):
        calls[0]+=1
        if calls[0]>1:raise OSError(5,'TEST_ONLY')
        return write(fd,raw[:1])
    model.write=partial;monkeypatch.setattr(r,'os',model.surface())
    with pytest.raises(OSError):r._stage_remap_resources(original,'/TEST_ONLY/resources')
    data=r._held_stage_data(original)
    assert data['phase']=='REMOVED' and data['failure']['kind']=='OSError' and data['final_cleanup_deadline'] is None
    assert '/TEST_ONLY/resources' not in model.nodes and model.fds=={}


def test_private_stage_custody_cannot_be_constructed_copied_or_adopted(monkeypatch):
    with pytest.raises(ValueError):r._StageState()
    original,model,clock=stage_model(monkeypatch);data=r._stage_remap_resources(original,'/TEST_ONLY/resources')
    with pytest.raises(ValueError):copy.deepcopy(original._technical_state)
    other,_,_=stage_model(monkeypatch);other._technical_state=data
    with pytest.raises(ValueError):r._cleanup_remap_resources(other)


@pytest.mark.parametrize('operation',['parent-replacement','root-replacement','readback-bytes','readback-identity','write-zero','write-excess','clock-backward'])
def test_first_staging_fault_retains_owned_binding_and_never_adopts_replacement(monkeypatch,operation):
    original,model,clock=stage_model(monkeypatch);write=model.write;read=model.read
    def changed_write(fd,raw):
        result=write(fd,raw)
        if operation=='parent-replacement':model.nodes['/TEST_ONLY']['ino']=999
        if operation=='root-replacement':model.nodes['/TEST_ONLY/resources']['ino']=999
        if operation=='clock-backward':clock[0]=original._started
        return 0 if operation=='write-zero' else len(raw)+1 if operation=='write-excess' else result
    def changed_read(fd,count):
        result=read(fd,count)
        if operation=='readback-bytes' and result:return b'X'+result[1:]
        if operation=='readback-identity':model.nodes[model.fds[fd][0]]['time']+=1
        return result
    model.write=changed_write;model.read=changed_read;monkeypatch.setattr(r,'os',model.surface())
    with pytest.raises(ValueError):r._stage_remap_resources(original,'/TEST_ONLY/resources')
    assert original._stopped and r._held_stage_data(original)['failure'] is not None
    if operation in ('parent-replacement','root-replacement','readback-identity','clock-backward'):
        assert '/TEST_ONLY/resources' in model.nodes


def test_original_description_unit_refuses_failed_intended_open_even_before_valid_retry():
    obs,archive,wanted=read_model();events=[]
    for kind,data in call(2,[0,0x80000],{'path':next(iter(wanted))},-2):events.append({'kind':kind,'data':data,'seq':99})
    obs['events'][1:1]=events
    with pytest.raises(ValueError):r._full_original_reads(obs,archive,wanted)


@pytest.mark.parametrize('exception',[KeyboardInterrupt,SystemExit])
def test_staging_cancellation_preserves_original_exception_and_one_placeholder(monkeypatch,exception):
    original,model,clock=stage_model(monkeypatch)
    error=exception('TEST_ONLY original cancellation')
    def cancel(fd,raw):raise error
    model.write=cancel;monkeypatch.setattr(r,'os',model.surface())
    with pytest.raises(exception) as seen:r._stage_remap_resources(original,'/TEST_ONLY/resources')
    assert seen.value is error and original._stopped
    assert r._held_stage_data(original)['failure']['kind']==exception.__name__
    with pytest.raises(ValueError):r._stage_remap_resources(original,'/TEST_ONLY/retry')
