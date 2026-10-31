"""Review regressions on invented traces only; no native/child/backend calls."""
import copy
import pytest
from twin import pdf_native_bridge as bridge, source_native_observation as native, source_metadata as sm
from test_pdf_native_bridge import native_fixture, bundle_fixture


def resequence(observation):
    for i,event in enumerate(observation['events']):event.update(seq=i,at_ns=i*1000)
    observation['events'][-1]['at_ns']=observation['run']['elapsed_ns']


def close_channel(observation,channel,*,interleave,result=0):
    fd={'stdout':1,'stderr':2}[channel]
    eof=next(e for e in observation['events'] if e['kind']=='pipe-eof' and e['data']['channel']==channel)
    observation['events'].remove(eof)
    at=next(i for i,e in enumerate(observation['events']) if e['kind']=='enter' and e['data']['nr']==231)
    entry={'kind':'enter','data':{'nr':3,'args':[fd,0,0,0,0,0],'detail':{}}}
    leave={'kind':'leave','data':{'result':result,'detail':{}}}
    observation['events'][at:at]=[entry,eof,leave] if interleave else [entry,leave,eof]
    if result==0:
        stop=next(e for e in observation['events'] if e['kind']=='exit-stop')
        stop['data']['fds']=[r for r in stop['data']['fds'] if r['fd']!=fd]
    resequence(observation)
    return entry,leave,eof


@pytest.mark.parametrize('channel',['stdout','stderr'])
@pytest.mark.parametrize('interleave',[False,True])
def test_successful_close_binding_survives_permitted_host_eof_interleaving(channel,interleave):
    plan,parent,obs,archive=bundle_fixture()
    entry,leave,eof=close_channel(obs,channel,interleave=interleave)
    native.verify_native_observation(obs,archive,purpose='TEST_ONLY')
    result=bridge._complete_pdf_extraction(plan,parent,obs,archive)
    bridge.verify_pdf_extraction_bundle(plan,parent,result)
    dossier=sm._json(result['receipts'][result['dossier_sha256']]);envelope=sm._json(result['receipts'][dossier['pdf_origin_observation_sha256']])
    assert envelope['streams'][channel]['closure']=={'kind':'explicit-close','enter_seq':entry['seq'],'leave_seq':leave['seq']}
    assert envelope['streams'][channel]['eof_event_seq']==eof['seq']


def move_open_writer_eof(observation,channel,position):
    eof=next(e for e in observation['events'] if e['kind']=='pipe-eof' and e['data']['channel']==channel)
    observation['events'].remove(eof)
    if position=='before-first-write':
        at=next(i for i,e in enumerate(observation['events']) if e['kind']=='enter' and e['data']['nr']==1 and e['data']['args'][0]==3)
        eof['data']['captured_bytes']=0
    else:
        kind='enter' if position=='before-exit' else 'exit-stop'
        at=next(i for i,e in enumerate(observation['events']) if e['kind']==kind and (kind=='exit-stop' or e['data']['nr']==231))
    observation['events'].insert(at,eof);resequence(observation)


OPEN_WRITER_CASES=[('origin','before-first-write')]+[(channel,where) for channel in ('origin','stdout','stderr') for where in ('before-exit','pending-exit')]


@pytest.mark.parametrize('channel,position',OPEN_WRITER_CASES)
def test_original_writer_open_cannot_have_positive_read_eof(channel,position):
    obs,archive=native_fixture();move_open_writer_eof(obs,channel,position)
    with pytest.raises(ValueError,match='closure|EOF'):native.verify_native_observation(obs,archive,purpose='TEST_ONLY')


@pytest.mark.parametrize('channel,position',OPEN_WRITER_CASES)
def test_complete_bundle_cannot_repair_impossible_original_writer_eof(channel,position):
    plan,parent,obs,archive=bundle_fixture();move_open_writer_eof(obs,channel,position)
    with pytest.raises(ValueError,match='closure|EOF'):bridge._complete_pdf_extraction(plan,parent,obs,archive)


@pytest.mark.parametrize('channel',['stdout','stderr'])
@pytest.mark.parametrize('interleave',[False,True])
@pytest.mark.parametrize('result',[-4,-9])
def test_pending_or_observed_failed_close_cannot_supply_eof_causality(channel,interleave,result):
    obs,archive=native_fixture();close_channel(obs,channel,interleave=interleave,result=result)
    with pytest.raises(ValueError,match='closure|EOF'):native.verify_native_observation(obs,archive,purpose='TEST_ONLY')


def test_checked_exit_eof_may_precede_terminal_wait_observation():
    obs,archive=native_fixture()
    exit_seq=next(e['seq'] for e in obs['events'] if e['kind']=='exit-stop')
    for event in obs['events']:
        if event['kind']=='pipe-eof':
            assert event['seq']>exit_seq and event['at_ns']<obs['events'][-1]['data']['wait']['observed_at_ns']
    assert native.verify_native_observation(obs,archive,purpose='TEST_ONLY')['origin_bytes']>0


LIMIT_FIELDS=('input_bytes','stdout_bytes','stderr_bytes','syntax_bytes','wall_seconds','termination_grace_seconds')


@pytest.mark.parametrize('field',LIMIT_FIELDS)
@pytest.mark.parametrize('primitive',['float','bool'])
def test_every_fixed_config_limit_requires_exact_integer_primitive(field,primitive):
    plan,parent,obs,archive=bundle_fixture();config=sm._json(archive[plan['configuration_sha256']])
    config['limits'][field]=float(config['limits'][field]) if primitive=='float' else True
    raw=sm.canonical(config);plan['configuration_sha256']=sm.sha256(raw);archive[sm.sha256(raw)]=raw
    with pytest.raises(ValueError):bridge._validate_plan(plan,parent)


@pytest.mark.parametrize('field',LIMIT_FIELDS)
@pytest.mark.parametrize('primitive',['float','bool'])
def test_native_v2_fixed_limits_also_require_exact_integer_primitive(field,primitive):
    obs,archive=native_fixture();obs['spec']['limits']=copy.deepcopy(obs['spec']['limits'])
    obs['spec']['limits'][field]=float(obs['spec']['limits'][field]) if primitive=='float' else True
    with pytest.raises(ValueError):native.verify_native_observation(obs,archive,purpose='TEST_ONLY')


@pytest.mark.parametrize('channel,position',OPEN_WRITER_CASES)
def test_public_bundle_verifier_rejects_impossible_eof_before_cross_pin_adoption(channel,position):
    plan,parent,obs,archive=bundle_fixture()
    result=bridge._complete_pdf_extraction(plan,parent,obs,archive)
    move_open_writer_eof(obs,channel,position)
    pin=sm.sha256(sm.canonical(obs));result['archive'][pin]=sm.canonical(obs)
    dossier=sm._json(result['receipts'][result['dossier_sha256']]);dossier['native_observation_sha256']=pin
    raw=sm.canonical(dossier);result['dossier_sha256']=sm.sha256(raw);result['receipts'][sm.sha256(raw)]=raw
    index=sm._json(result['receipts'][result['index_sha256']]);index['dossier_sha256']=result['dossier_sha256']
    raw=sm.canonical(index);result['index_sha256']=sm.sha256(raw);result['receipts'][sm.sha256(raw)]=raw
    with pytest.raises(ValueError,match='closure'):bridge.verify_pdf_extraction_bundle(plan,parent,result)


def test_two_host_eofs_may_interleave_with_the_same_successful_pending_close():
    plan,parent,obs,archive=bundle_fixture()
    stderr_entry,stderr_leave,stderr_eof=close_channel(obs,'stderr',interleave=False)
    stdout_entry,stdout_leave,stdout_eof=close_channel(obs,'stdout',interleave=True)
    obs['events'].remove(stderr_eof);obs['events'].insert(obs['events'].index(stdout_eof),stderr_eof);resequence(obs)
    # Two closes move exit-stop to15000ns; preserve a possible wait before cleanup25000ns.
    obs['events'][-1]['data']['wait']['observed_at_ns']=20000
    native.verify_native_observation(obs,archive,purpose='TEST_ONLY')
    result=bridge._complete_pdf_extraction(plan,parent,obs,archive);bridge.verify_pdf_extraction_bundle(plan,parent,result)
    dossier=sm._json(result['receipts'][result['dossier_sha256']]);envelope=sm._json(result['receipts'][dossier['pdf_origin_observation_sha256']])
    for name,entry,leave in [('stdout',stdout_entry,stdout_leave),('stderr',stderr_entry,stderr_leave)]:
        assert envelope['streams'][name]['closure']=={'kind':'explicit-close','enter_seq':entry['seq'],'leave_seq':leave['seq']}


WAIT_CASES=[(0,False),(8999,False),(9000,True),(9001,True),(14000,True),
            (24999,True),(25000,True),(25001,False),(30000,False),(30001,False)]


def assert_wait_fixture_interval(observation):
    assert next(e['at_ns'] for e in observation['events'] if e['kind']=='exit-stop')==9000
    run=observation['run'];assert run['cleanup_started_ns']-run['monotonic_start_ns']==25000
    assert run['elapsed_ns']==30000


@pytest.mark.parametrize('observed_at_ns,accepted',WAIT_CASES)
def test_successful_wait_observation_is_inside_checked_exit_to_cleanup_interval(observed_at_ns,accepted):
    obs,archive=native_fixture();assert_wait_fixture_interval(obs)
    obs['events'][-1]['data']['wait']['observed_at_ns']=observed_at_ns
    if accepted:
        native.verify_native_observation(obs,archive,purpose='TEST_ONLY')
    else:
        with pytest.raises(ValueError):native.verify_native_observation(obs,archive,purpose='TEST_ONLY')


@pytest.mark.parametrize('observed_at_ns,accepted',WAIT_CASES)
def test_completed_bundle_preserves_wait_stage_boundaries_without_ordering_eof_before_wait(observed_at_ns,accepted):
    plan,parent,obs,archive=bundle_fixture();assert_wait_fixture_interval(obs)
    obs['events'][-1]['data']['wait']['observed_at_ns']=observed_at_ns
    if accepted:
        result=bridge._complete_pdf_extraction(plan,parent,obs,archive)
        bridge.verify_pdf_extraction_bundle(plan,parent,result)
        if observed_at_ns==14000:
            assert all(9000<e['at_ns']<observed_at_ns for e in obs['events'] if e['kind']=='pipe-eof')
    else:
        with pytest.raises(ValueError):bridge._complete_pdf_extraction(plan,parent,obs,archive)
