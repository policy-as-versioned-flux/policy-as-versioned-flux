"""Synthetic origin records only: no PDF, converter, child or native observer."""
import copy
import hashlib
import json

import pytest

from twin import pdf_output_origin as p


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'), ensure_ascii=True,
                      allow_nan=False).encode('ascii')


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def packet(events, output=b'AB', *, header=None, footer_updates=None):
    header = header or {'schema':'twin.pdf-output-origin-events/v1',
        'profile':'pdf-text-xpdf-origin/2','emitter_protocol_version':1}
    events = copy.deepcopy(events)
    for seq, event in enumerate(events):
        event['seq'] = seq
    prefix = b''.join(canonical(row) + b'\n' for row in [header] + events)
    footer = {'record':'footer','closed_fragment_count':sum(e['record']=='fragment_close' for e in events),
        'emitted_stdout_bytes':len(output),'emitted_stdout_sha256':digest(output),
        'event_count':len(events),'event_prefix_bytes':len(prefix),
        'event_prefix_sha256':digest(prefix),'intended_exit_code':0}
    footer.update(footer_updates or {})
    return prefix + canonical(footer) + b'\n'


def fragment(text='AB', *, fragment_id=1, first_item=1, page=1):
    raw = text.encode('utf8')
    events = [{'record':'fragment_open','fragment':fragment_id,'page':page,
               'code_bytes':len(raw),'code_sha256':digest(raw)}]
    offset = 0
    for item_id, char in enumerate(text, first_item):
        code = char.encode('utf8')
        events.append({'record':'item','item':item_id,'fragment':fragment_id,
            'code_start':offset,'code_end':offset+len(code),'code_hex':code.hex(),
            'input_scalars':[ord(char)],'scalars':[ord(char)],'taint':'none'})
        offset += len(code)
    events.append({'record':'fragment_close','fragment':fragment_id,'consumed_code_bytes':len(raw)})
    return events


def emit(item, scalar, start, text, *, operation='decoded', reason='source'):
    raw = text.encode('utf8')
    return {'record':'emit','start':start,'end':start+len(raw),'utf8_hex':raw.hex(),
            'origin_item':item,'origin_scalar':scalar,'operation':operation,'reason':reason}


def contiguous(text='AB'):
    events = fragment(text)
    offset = 0
    for item_id, char in enumerate(text, 1):
        events.append(emit(item_id, 0, offset, char))
        offset += len(char.encode('utf8'))
    return events


def test_p01_adjacent_decoded_items_support_one_fragment_word():
    verified = p.check_pdf_origin_events(b'AB', packet(contiguous()))
    assert p.check_pdf_witness(verified, 0, 2) is None
    assert json.loads(verified.description)['scope'] == 'structural-only-no-native-authority'


def deleted_hyphen(*, barrier=True):
    events = fragment('A-B') + [emit(1, 0, 0, 'A')]
    if barrier:
        events.append({'record':'barrier','at':1,'reason':'source-gap'})
    return events + [emit(3, 0, 1, 'B'),
        {'record':'omit','item':2,'scalar':0,'reason':'not-emitted-by-reading-order'}]


def test_p07_p10_deleted_join_refuses_crossing_and_allows_each_endpoint_side():
    verified = p.check_pdf_origin_events(b'AB', packet(deleted_hyphen()))
    with pytest.raises(ValueError):
        p.check_pdf_witness(verified, 0, 2)
    p.check_pdf_witness(verified, 0, 1)
    p.check_pdf_witness(verified, 1, 2)


def test_p15_missing_required_barrier_is_not_repaired_into_eligibility():
    with pytest.raises(ValueError):
        p.check_pdf_origin_events(b'AB', packet(deleted_hyphen(barrier=False)))


@pytest.mark.parametrize('text', ['é', '😀', '中'])
def test_p11_scalar_boundaries(text):
    output = text.encode('utf8')
    verified = p.check_pdf_origin_events(output, packet(contiguous(text), output))
    p.check_pdf_witness(verified, 0, len(output))
    for boundary in range(1, len(output)):
        with pytest.raises(ValueError):
            p.check_pdf_witness(verified, 0, boundary)


@pytest.mark.parametrize('mutation', ['output-hash','prefix-hash','output-length','prefix-length',
    'event-count','fragment-count','exit','extra-footer-field','header-host-binding','noncanonical',
    'duplicate-key','missing-lf','blank-line','unknown-record','unclosed','missing-footer','duplicate-footer'])
def test_p16_p17_p29_closed_canonical_stream(mutation):
    events = contiguous()
    changes = {'output-hash':{'emitted_stdout_sha256':'0'*64},
        'prefix-hash':{'event_prefix_sha256':'0'*64}, 'output-length':{'emitted_stdout_bytes':1},
        'prefix-length':{'event_prefix_bytes':1}, 'event-count':{'event_count':1},
        'fragment-count':{'closed_fragment_count':0}, 'exit':{'intended_exit_code':1},
        'extra-footer-field':{'actual_wait':0}}
    raw = packet(events, footer_updates=changes.get(mutation))
    if mutation=='header-host-binding':
        raw = packet(events, header={'schema':'twin.pdf-output-origin-events/v1',
            'profile':'pdf-text-xpdf-origin/2','emitter_protocol_version':1,'parent_sha256':'a'*64})
    if mutation=='noncanonical': raw = raw.replace(b':', b': ', 1)
    if mutation=='duplicate-key': raw = raw.replace(b'{', b'{"schema":"forged",', 1)
    if mutation=='missing-lf': raw = raw[:-1]
    if mutation=='blank-line': raw = raw.replace(b'\n', b'\n\n', 1)
    if mutation=='unknown-record': events[0]['record']='arbitrary';raw=packet(events)
    if mutation=='unclosed': events.pop(3);raw=packet(events)
    if mutation=='missing-footer': raw=b'\n'.join(raw.splitlines()[:-1])+b'\n'
    if mutation=='duplicate-footer': raw+=raw.splitlines()[-1]+b'\n'
    with pytest.raises(ValueError):
        p.check_pdf_origin_events(b'AB', raw)


@pytest.mark.parametrize('separator,reason', [(' ', 'spacing'), ('\n', 'linebreak'),
    ('\f', 'pagebreak'), ('\ufeff', 'bom'), ('\u202a', 'bidi')])
def test_p03_inserted_formatting_is_always_ineligible(separator, reason):
    output = ('A'+separator+'B').encode('utf8')
    at = 1 + len(separator.encode('utf8'))
    events = fragment() + [emit(1,0,0,'A'),
        emit(0,0,1,separator,operation='generated',reason=reason), emit(2,0,at,'B')]
    verified = p.check_pdf_origin_events(output, packet(events,output))
    with pytest.raises(ValueError): p.check_pdf_witness(verified,0,len(output))
    with pytest.raises(ValueError): p.check_pdf_witness(verified,1,at)
    p.check_pdf_witness(verified,0,1)
    p.check_pdf_witness(verified,at,len(output))


def test_p04_discarded_decoded_space_does_not_bless_generated_equal_space():
    events = fragment('A B') + [emit(1,0,0,'A'),
        emit(0,0,1,' ',operation='generated',reason='spacing'),emit(3,0,2,'B'),
        {'record':'omit','item':2,'scalar':0,'reason':'not-emitted-by-reading-order'}]
    verified = p.check_pdf_origin_events(b'A B',packet(events,b'A B'))
    with pytest.raises(ValueError):p.check_pdf_witness(verified,0,3)


@pytest.mark.parametrize('taint,reason', [('unicode-remap','remap'),('actualtext','actualtext'),
    ('unmapped','unmapped'),('none','mirror')])
def test_p05_p06_modified_and_replacement_output_never_eligible(taint,reason):
    events = fragment('A');events[1]['taint']=taint
    if taint=='unicode-remap':events[1]['input_scalars']=[90]
    events.append(emit(1,0,0,'B' if reason=='mirror' else 'A',operation='modified',reason=reason))
    output=b'B' if reason=='mirror' else b'A'
    verified=p.check_pdf_origin_events(output,packet(events,output))
    with pytest.raises(ValueError):p.check_pdf_witness(verified,0,1)
    events[-1]['operation']='decoded';events[-1]['reason']='source'
    if taint!='none' or output!=b'A':
        with pytest.raises(ValueError):p.check_pdf_origin_events(output,packet(events,output))


def test_p06_fragment_zero_is_only_unmapped_actualtext_replacement():
    item={'record':'item','item':1,'fragment':0,'code_start':0,'code_end':0,'code_hex':'',
          'input_scalars':[88],'scalars':[65],'taint':'actualtext'}
    events=[item,emit(1,0,0,'A',operation='modified',reason='actualtext')]
    verified=p.check_pdf_origin_events(b'A',packet(events,b'A'))
    with pytest.raises(ValueError):p.check_pdf_witness(verified,0,1)
    for field,value in [('taint','none'),('code_hex','41'),('code_start',1),('code_end',1)]:
        wrong=copy.deepcopy(events);wrong[0][field]=value
        with pytest.raises(ValueError):p.check_pdf_origin_events(b'A',packet(wrong,b'A'))


@pytest.mark.parametrize('page',[1,2])
def test_p02_p08_equal_text_from_separate_operands_has_no_eligible_join(page):
    events=fragment('A')+fragment('B',fragment_id=2,first_item=2,page=page)+[
        emit(1,0,0,'A'),{'record':'barrier','at':1,'reason':'fragment'},emit(2,0,1,'B')]
    verified=p.check_pdf_origin_events(b'AB',packet(events))
    with pytest.raises(ValueError):p.check_pdf_witness(verified,0,2)
    events.pop(-2)
    with pytest.raises(ValueError):p.check_pdf_origin_events(b'AB',packet(events))


def test_p09_reorder_and_repeated_decoder_identity_remain_explicit():
    events=fragment('AB')+[emit(2,0,0,'B'),
        {'record':'barrier','at':1,'reason':'scalar-order'},emit(1,0,1,'A')]
    verified=p.check_pdf_origin_events(b'BA',packet(events,b'BA'))
    with pytest.raises(ValueError):p.check_pdf_witness(verified,0,2)
    duplicate=fragment('A')+[emit(1,0,0,'A'),
        {'record':'barrier','at':1,'reason':'duplicate'},
        emit(1,0,1,'A',operation='modified',reason='duplicate')]
    verified=p.check_pdf_origin_events(b'AA',packet(duplicate,b'AA'))
    with pytest.raises(ValueError):p.check_pdf_witness(verified,1,2)
    p.check_pdf_witness(verified,0,1)
    duplicate[-1]['operation']='decoded';duplicate[-1]['reason']='source'
    with pytest.raises(ValueError):p.check_pdf_origin_events(b'AA',packet(duplicate,b'AA'))


def test_duplicate_mirror_bytes_and_duplicate_after_generated_are_ineligible():
    events=fragment('(')+[emit(1,0,0,')',operation='modified',reason='mirror'),
        emit(0,0,1,' ',operation='generated',reason='spacing'),
        {'record':'barrier','at':2,'reason':'duplicate'},
        emit(1,0,2,')',operation='modified',reason='duplicate')]
    verified=p.check_pdf_origin_events(b') )',packet(events,b') )'))
    with pytest.raises(ValueError):p.check_pdf_witness(verified,2,3)


def test_p12_one_to_many_scalar_subsequences_have_exact_order():
    events=fragment('X');events[1].update(input_scalars=[65,66],scalars=[65,66])
    events += [emit(1,0,0,'A'),emit(1,1,1,'B')]
    p.check_pdf_witness(p.check_pdf_origin_events(b'AB',packet(events)),0,2)
    events[-2:]=[emit(1,1,0,'B'),{'record':'barrier','at':1,'reason':'scalar-order'},emit(1,0,1,'A')]
    verified=p.check_pdf_origin_events(b'BA',packet(events,b'BA'))
    with pytest.raises(ValueError):p.check_pdf_witness(verified,0,2)


@pytest.mark.parametrize('change',['gap','overlap','zero','prefix','suffix','wrong-bytes','split-scalar',
    'label','missing-omit','double-omit','omit-emitted','early-omit','wrong-code-hash','code-gap',
    'wrong-taint','missing-item','duplicate-item','duplicate-fragment','bool','surrogate','too-many-scalars'])
def test_p13_p14_full_code_scalar_and_partition_accounting(change):
    events=contiguous();output=b'AB'
    if change=='gap':events[-1]['start']=2
    if change=='overlap':events[-1]['start']=0
    if change=='zero':events[-1]['end']=1
    if change=='prefix':events.pop(-2)
    if change=='suffix':events.pop()
    if change=='wrong-bytes':events[-1]['utf8_hex']='43'
    if change=='split-scalar':
        events=fragment('é')+[emit(1,0,0,'é')];output='é'.encode();events[-1]['end']=1
    if change=='label':events[-1]['eligible']=True
    if change in ('missing-omit','double-omit','omit-emitted','early-omit'):
        events=deleted_hyphen()
        if change=='missing-omit':events.pop()
        if change=='double-omit':events.append(copy.deepcopy(events[-1]))
        if change=='omit-emitted':events[-1]['item']=1
        if change=='early-omit':events.insert(5,{'record':'omit','item':1,'scalar':0,'reason':'not-emitted-by-reading-order'})
    if change=='wrong-code-hash':events[0]['code_sha256']='0'*64
    if change=='code-gap':events[2]['code_start']=0
    if change=='wrong-taint':events[1]['input_scalars']=[90]
    if change=='missing-item':events[-1]['origin_item']=8
    if change=='duplicate-item':events[2]['item']=1
    if change=='duplicate-fragment':events.insert(1,copy.deepcopy(events[0]))
    if change=='bool':events[1]['item']=True
    if change=='surrogate':events[1]['scalars']=[0xd800]
    if change=='too-many-scalars':events[1]['scalars']=[65]*4097
    with pytest.raises(ValueError):p.check_pdf_origin_events(output,packet(events,output))


@pytest.mark.parametrize('limit,value',[('MAX_WIRE_BYTES',10),('MAX_RECORD_BYTES',20),
    ('MAX_EVENTS',1),('MAX_OUTPUT_BYTES',1),('MAX_CODE_BYTES',1),('MAX_SCALARS',0)])
def test_p18_fixed_caps_are_refusals(limit,value,monkeypatch):
    monkeypatch.setattr(p,limit,value)
    with pytest.raises(ValueError):p.check_pdf_origin_events(b'AB',packet(contiguous()))


def test_p19_p20_p29_serialized_maps_and_approval_flags_cannot_adopt_private_map():
    verified=p.check_pdf_origin_events(b'AB',packet(contiguous()))
    for substitute in [json.loads(verified.description),verified.description,
                       {'trusted':True,'index_sha256':'a'*64},p.PdfOriginMap()]:
        with pytest.raises(ValueError):p.check_pdf_witness(substitute,0,2)
    with pytest.raises(TypeError):p.PdfOriginMap(description=verified.description)
    assert not any(hasattr(p,name) for name in ('acquire','adopt','from_json','from_digest','new_native_observation_store'))


def publisher_manifest(path, *, start=0, end=2):
    witness={'member_id':'converted','member_sha256':digest(b'AB'),
             'start_byte':start,'end_byte':end,'text_utf8':b'AB'[start:end].decode()}
    manifest={'members':{'converted':{'id':'converted','sha256':digest(b'AB'),'bytes':2}},
        'observations':{},'statement':{'origin_role':'unestablished'},'visible_excerpts':[]}
    if path=='date':manifest['observations']['date']={'witness':witness}
    if path=='statement':manifest['statement']={'origin_role':'publisher-quotation','witness':witness}
    if path=='excerpt':manifest['visible_excerpts']=[{'origin_role':'publisher-quotation','witness':witness}]
    return manifest


@pytest.mark.parametrize('path',['date','statement','excerpt'])
def test_p21_all_publisher_paths_apply_same_barrier_gate(path):
    verified=p.check_pdf_origin_events(b'AB',packet(deleted_hyphen()))
    with pytest.raises(ValueError):p.check_pdf_publisher_witnesses(verified,publisher_manifest(path),'converted')
    p.check_pdf_publisher_witnesses(verified,publisher_manifest(path,end=1),'converted')


@pytest.mark.parametrize('path',['date','statement','excerpt'])
def test_p22_derived_alias_cannot_strip_selected_member_map(path):
    verified=p.check_pdf_origin_events(b'AB',packet(deleted_hyphen()))
    manifest=publisher_manifest(path)
    manifest['members']['alias']={'id':'alias','sha256':digest(b'AB'),'bytes':2,
                                 'parent':{'member_id':'converted'}}
    witness=(manifest['observations']['date']['witness'] if path=='date' else
             manifest['statement']['witness'] if path=='statement' else manifest['visible_excerpts'][0]['witness'])
    witness['member_id']='alias'
    with pytest.raises(ValueError,match='alias'):p.check_pdf_publisher_witnesses(verified,manifest,'converted')


@pytest.mark.parametrize('field,value',[('sha256','a'*64),('bytes',1),('id','alias')])
def test_selected_member_binding_cannot_substitute_output(field,value):
    verified=p.check_pdf_origin_events(b'AB',packet(contiguous()))
    manifest=publisher_manifest('date');manifest['members']['converted'][field]=value
    with pytest.raises(ValueError):p.check_pdf_publisher_witnesses(verified,manifest,'converted')


def test_p23_p26_old_pdf_profile_and_actual_dependency_gate_remain_held():
    from twin import source_metadata_migration as m
    assert p.PROFILE not in m.PROFILES
    syntax={'schema':'twin.source-extraction-generated-syntax/v1','profile':'pdf-text-xpdf/1',
        'parent_sha256':'a'*64,'output_sha256':digest(b'AB'),'output_bytes':2,'ranges':[],
        'coverage':'complete-generated-syntax'}
    with pytest.raises(ValueError):m._syntax_check(syntax,'pdf-text-xpdf/1','a'*64,b'AB')
    # Structural success never has the actual acquire/resolve or receipt/index fields.
    description=json.loads(p.check_pdf_origin_events(b'AB',packet(contiguous())).description)
    assert not {'authority','index_sha256','actual','receipt','native_observation'} & set(description)


@pytest.mark.parametrize('mutation',['function','code','defaults','config'])
def test_p25_migration_authority_protects_verifier_live_bindings(mutation,monkeypatch):
    from twin import source_metadata as sm,source_metadata_migration as m
    policy={'purpose':'TEST_ONLY','allowed_transforms':[],'reviewer_id':'synthetic','reviewer_role':'source-control'}
    authority=m.freeze_migration_authority('synthetic','synthetic','1',sm.sha256(sm.canonical(policy)),
        policy=policy,layout_config={'schema':'twin.source-legacy-layout/v1','purpose':'TEST_ONLY','transport_contract_sha256':None},
        execution_contract={'schema':'twin.source-migration-execution-contract/v1','purpose':'TEST_ONLY','index_sha256s':[]})
    def replacement(*args):return None
    if mutation=='function':monkeypatch.setattr(p,'check_pdf_witness',replacement)
    if mutation=='code':monkeypatch.setattr(p.check_pdf_witness,'__code__',replacement.__code__)
    if mutation=='defaults':monkeypatch.setattr(p.check_pdf_witness,'__defaults__',(0,))
    if mutation=='config':monkeypatch.setitem(p.HEADER,'emitter_protocol_version',99)
    with pytest.raises(ValueError):authority.verify()


@pytest.mark.parametrize('host_field',['actual_wait','run_id','parent_sha256','config_sha256',
    'executable_sha256','pipe_identity','native_observation_sha256','index_sha256','envelope_sha256'])
def test_p27_p28_p29_host_facts_cannot_be_injected_into_raw_stream(host_field):
    raw=packet(contiguous(),footer_updates={host_field:'forged'})
    with pytest.raises(ValueError):p.check_pdf_origin_events(b'AB',raw)


@pytest.mark.parametrize('output',[b'A',b'ABC',b'AC',b'AB\xff'])
def test_p30_actual_captured_output_must_equal_full_emitter_relation(output):
    with pytest.raises(ValueError):p.check_pdf_origin_events(output,packet(contiguous()))


@pytest.mark.parametrize('field',['native_observation_sha256','pdf_origin_map_sha256','raw_events_sha256'])
def test_p24_stock_nine_key_receipt_cannot_gain_origin_fields(field):
    from test_source_metadata import fixture_import
    from twin import source_metadata as sm
    manifest,archive,receipts,authority=fixture_import()
    policy=sm._json(authority.description)['policy']
    sm.retained_source_checker(manifest,archive,receipts,policy)
    transform=manifest['members']['extraction']['transform']
    receipt=sm._json(receipts[transform['execution_receipt_artifact_sha256']])
    assert len(receipt)==9
    receipt[field]='a'*64
    raw=sm.canonical(receipt);pin=sm.sha256(raw);receipts[pin]=raw
    transform['execution_receipt_artifact_sha256']=pin
    with pytest.raises(ValueError,match='receipt'):sm.retained_source_checker(manifest,archive,receipts,policy)


@pytest.mark.parametrize('path',['date','statement','excerpt'])
def test_p21_each_publisher_path_also_rejects_modified_bytes(path):
    events=fragment('AB');events += [emit(1,0,0,'A'),emit(2,0,1,'B',operation='modified',reason='mirror')]
    verified=p.check_pdf_origin_events(b'AB',packet(events))
    with pytest.raises(ValueError):p.check_pdf_publisher_witnesses(verified,publisher_manifest(path),'converted')


def test_empty_structural_stream_has_no_possible_witness():
    verified=p.check_pdf_origin_events(b'',packet([],b''))
    with pytest.raises(ValueError):p.check_pdf_witness(verified,0,0)


@pytest.mark.parametrize('start,end',[(True,2),(0,False),(-1,1),(0,3),(1,1),(2,1)])
def test_witness_interval_type_and_extent(start,end):
    verified=p.check_pdf_origin_events(b'AB',packet(contiguous()))
    with pytest.raises(ValueError):p.check_pdf_witness(verified,start,end)


@pytest.mark.parametrize('stem,crossing', [('TEST_ONLY-contiguous-fragment',False),
    ('TEST_ONLY-deleted-hyphen',True)])
def test_pinned_constructed_protocol_goldens(stem,crossing):
    from pathlib import Path
    fixture=Path(__file__).parent/'fixtures/TEST_ONLY-pdf-output-origin'
    verified=p.check_pdf_origin_events((fixture/(stem+'.stdout')).read_bytes(),
                                      (fixture/(stem+'.jsonl')).read_bytes())
    if crossing:
        with pytest.raises(ValueError):p.check_pdf_witness(verified,0,2)
    else:p.check_pdf_witness(verified,0,2)


def test_private_map_cannot_be_publicly_constructed_or_duck_typed():
    import dataclasses
    import types
    verified=p.check_pdf_origin_events(b'AB',packet(deleted_hyphen()))
    substitute=types.SimpleNamespace(description=verified.description,_runs=((0,2,True,1),),
        _barriers=frozenset(),_boundaries=frozenset((0,1,2)),_output_bytes=2,_output=b'AB')
    with pytest.raises(ValueError):p.check_pdf_witness(substitute,0,2)
    with pytest.raises(dataclasses.FrozenInstanceError):verified._runs=((0,2,True,1),)
    with pytest.raises(TypeError):p.PdfOriginMap(_runs=((0,2,True,1),))


@pytest.mark.parametrize('field,value',[('_runs',((0,2,True,1),)),('_barriers',frozenset()),
    ('_boundaries',frozenset((0,2))),('_output',b'ZZ'),('description',b'{}'),('_content_sha256','a'*64)])
def test_private_content_fingerprint_detects_individual_custody_drift(field,value):
    verified=p.check_pdf_origin_events(b'AB',packet(deleted_hyphen()))
    # Stronger than the supported immutable-data interface: deliberately simulate
    # one-field corruption without treating arbitrary host tampering as a threat model.
    object.__setattr__(verified,field,value)
    with pytest.raises(ValueError):p.check_pdf_witness(verified,0,2)


@pytest.mark.parametrize('path',['date','statement','excerpt'])
def test_p23_empty_old_pdf_ranges_do_not_bypass_existing_publisher_hold(path,monkeypatch):
    from twin import source_metadata as sm,source_metadata_migration as m
    manifest=publisher_manifest(path)
    manifest['members']['converted'].update(role='derived-extraction',
        parent={'member_id':'original','sha256':'a'*64},transform={'identity':'pdf-text-xpdf'})
    manifest['members']['original']={'id':'original','sha256':'a'*64,'role':'acquired-original'}
    index=sm.canonical({'schema':'twin.source-extraction-custody-index/v1','member_id':'converted'})
    pin=sm.sha256(index)
    # Model already-admitted extraction evidence only; no helper/native invocation.
    # The independent existing witness hold must still run for an empty range map.
    monkeypatch.setattr(m,'_checked_execution',lambda *args:[])
    with pytest.raises(ValueError,match='native generated syntax provenance unestablished'):
        m.migration_source_checker(manifest,{}, {pin:index},{'purpose':'TEST_ONLY'},
            execution_contract={'schema':'twin.source-migration-execution-contract/v1',
                                'purpose':'TEST_ONLY','index_sha256s':[pin]})
