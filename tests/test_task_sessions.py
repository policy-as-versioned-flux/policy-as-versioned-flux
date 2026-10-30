"""TEST_ONLY protected task history; no actual model or permission grant."""
from twin import qualification as q
from twin.task_contracts import TaskContract


def test_preflight_refusal_retains_a_public_snapshot_even_with_invalid_inputs():
    row = {'subject': 'TEST_ONLY-missing', 'issuer': 'TEST_ONLY', 'input': {'schema': 'twin.evolution-input/v2'},
           'context': {}, 'source': {}}
    inputs = q.HostInputs.freeze((row,), ('TEST_ONLY',))
    session = q.Resolver().host_session(inputs)
    job = {'task': 'evolution', 'task_contract_sha256': TaskContract.freeze('evolution').digest,
           'model_version': 'actor-' + '1' * 64, 'organisation': 'driftwood', 'subjects': ['TEST_ONLY-missing']}
    session.bind_task_job(job)
    session.decline_task_run(('TEST_ONLY-missing',), 'TEST_ONLY invalid input, human required')
    snapshot = session.task_snapshot()
    assert snapshot['job'] == job
    assert snapshot['inputs'] == [row]
    assert len(snapshot['attempts']) == len(snapshot['declines']) == 1
    attempt = snapshot['attempts'][0]
    assert attempt['actor_sha256'] == '1' * 64
    assert attempt['capture_sha256'] is None and attempt['raw_available'] is False
    assert attempt['disposition'] == 'refused-before-invocation'
    assert attempt['reason'] == 'TEST_ONLY invalid input, human required'


TASK_CALLS = []


def task_mechanical_runner(payload, config):
    """Open TEST_ONLY literal fixture arithmetic, no empirical model competence."""
    TASK_CALLS.append(payload['context']['as_of'])
    index = int(payload['context']['as_of'][-2:]) - 1
    if config['task'] == 'evolution':
        answer = {'evolution_position': (index % 4) / 3}
    elif config['task'] == 'causal':
        measurement = payload['task']['measurement']
        answer = {'edge': {'from': payload['target']['from'], 'to': payload['target']['to'], 'type': 'influences',
            'sign': 'positive' if index % 2 == 0 else 'negative', 'lag_days': 10 + index * 80,
            'elasticity': {'min': .1, 'mode': .2 + (index % 5) * .1, 'max': .9}, 'evidence_grade': (1, 3, 5)[index % 3]},
            'confounders': [{'id': item['id'], 'status': 'not-ruled-out', 'reason': 'TEST_ONLY structural source retained'}
                           for item in payload['task']['candidate_confounders']],
            'alternatives': ['TEST_ONLY reverse direction remains possible'],
            'units': {'from': measurement['from_unit'], 'to': measurement['to_unit'], 'lag': 'days',
                      'elasticity_definition': measurement['elasticity_definition']}}
    elif config['task'] == 'gameplay':
        pairs = [(play, component) for play in payload['task']['catalogue'] for component in payload['task']['org_components']]
        answer = {'opportunities': [{'play': play, 'component': component, 'reason': 'TEST_ONLY openly authored fixture outcome'}
            for ordinal, (play, component) in enumerate(pairs) if index % 4 and ordinal % 3 == index % 3]}
    else:
        names = ['purpose', 'necessity', 'proportionality']
        stop = None if index % 4 == 0 else names[index % 4 - 1]
        used = names if stop is None else names[:names.index(stop) + 1]
        # The first child admits while the independent original-task DPIA gate
        # denies. These public fixture answers never copy the mandatory gate.
        answer = {'admitted': stop is None, 'ladder': {'stopped_at': stop,
            'rungs': [{'rung': name, 'passed': name != stop, 'justification': 'TEST_ONLY authored fixture judgement'} for name in used]}}
    basis = {'reason': 'TEST_ONLY mechanical control; no semantic competence claim', 'calculations': [],
             'witnesses': [{'path': ['context', 'as_of'], 'quote': payload['context']['as_of']}]}
    if config['task'] == 'gameplay':
        present = {(item['play'], item['component']) for item in answer['opportunities']}
        basis['checks'] = [{'play': play, 'component': component, 'present': (play, component) in present,
            'incumbency_checked': False, 'reason': 'TEST_ONLY complete literal control, not semantic support',
            'witnesses': basis['witnesses']} for play, component in pairs]
    return q.canonical({'schema': f"twin.{config['task']}-response/v1", 'answer': answer, 'basis': basis})


def task_mechanical_parser(raw, config):
    from twin.task_contracts import decode, validate
    from twin.skills import Stated
    value = decode(raw)
    validate(config['task'].title() + 'Response', value)
    if 'decline' in value:
        return Stated(None, value)
    return Stated(value['answer'], value['basis'])


def task_review_store(path, policy, request, decision='pass'):
    """Retained TEST_ONLY reviewer artifact; it is not real reviewer competence."""
    import hashlib
    import json
    from twin.basis_assessment import ReviewStore
    path.mkdir(parents=True, exist_ok=True)
    original = json.loads(request)
    rows = []
    for row in original['rows']:
        rows.append({'id': row['id'], 'subject_digest': q.digest(row),
            'reason': 'TEST_ONLY independently retained software-control review',
            'decisions': {name: decision for name in policy.dimensions}, 'support': {name: {
                'reason': 'TEST_ONLY authored decision; witness membership alone proves no entailment',
                'witnesses': [{'path': ['input', 'context', 'as_of'], 'quote': row['input']['context']['as_of']}]}
                for name in policy.dimensions}})
    record = {'schema': 'twin.task-basis-assessment/v2', 'policy_digest': policy.digest,
        'request_digest': hashlib.sha256(request).hexdigest(), 'issuer': 'TEST_ONLY-task-review', 'rows': rows}
    raw = q.canonical(record)
    (path / 'record.json').write_bytes(raw)
    value = {'schema': 'twin.semantic-review-store/v1', 'entries': [{'request': record['request_digest'],
        'record': 'record.json', 'sha256': hashlib.sha256(raw).hexdigest(), 'issuer': 'TEST_ONLY-task-review',
        'authority': 'TEST_ONLY software authority, not empirical semantic expertise',
        'provenance': 'TEST_ONLY retained artifact, never actual target acquisition'}]}
    target = path / 'store.json'; target.write_bytes(q.canonical(value))
    return ReviewStore(target, hashlib.sha256(target.read_bytes()).hexdigest())


def genuine_task_material(protected_request, tmp_path, task='evolution', count=16, *, runner=None, actor_config=None, support=()):
    """Actual protected software mechanisms on openly authored TEST_ONLY inputs only."""
    import json
    from bench.qualification_controls import reference, basis_holds
    from twin.reference_cases import admit_reference, binding_for
    from twin.task_inputs import resolve_task_input, TaskPolicy, support_sources
    from twin.basis_assessment import BasisPolicy
    from test_task_inputs import task_request
    contract = TaskContract.freeze(task)
    resolved = []
    for index in range(count):
        org = ('driftwood', 'tuppence', 'ludlow')[index % 3]
        args = task_request(protected_request, task, org)
        job = args['protected_job']; packet = json.loads(job['source_packet'])
        packet['subject'] = job['subject'] = f'TEST_ONLY-{task}-{index}'
        packet['as_of'] = job['as_of'] = f'2026-10-{index + 1:02}'
        job['source_packet'] = q.canonical(packet); job['source_pin'] = q.digest(packet)
        resolved.append(resolve_task_input(**args))
    policy = TaskPolicy.freeze(contract, tuple(resolved))
    config = {'purpose': 'TEST_ONLY', 'task': task, 'task_contract_digest': contract.digest}
    if set(actor_config or {}) & set(config):
        raise ValueError('TEST_ONLY fault controls cannot replace protected task config')
    config.update(actor_config or {})
    actor = q.Actor.freeze(runner or task_mechanical_runner, task_mechanical_parser,
        config, support=(*support_sources(), *support))
    contexts = json.loads(policy.description)['contexts']
    first = resolved[0].host_record
    envelope = {'adopters': ['driftwood', 'tuppence', 'ludlow'], 'domains': [first['context']['domain']],
        'capabilities': [first['context']['capability']], 'frames': [first['context']['frame']],
        'sources': [first['context']['source'], *first['context']['source_families']],
        'from': '2026-10-01', 'until': '2026-10-30', 'estate_scope_sha256': first['context']['estate_scope_sha256'],
        'task_contexts': contexts}
    selections = []
    for metric in contract.metrics:
        admissions = []
        for index, item in enumerate(resolved):
            row = item.host_record
            case = json.loads(reference(case_id=row['subject'], org=row['context']['organisation']).packet_bytes)['case']
            case.update(row, id=row['subject'])
            scope = {**row['context'], 'purpose': 'development', 'claim': 'agent-reference-agreement', 'metric': metric}
            case['context'] = scope
            if task == 'evolution':
                case['expected'] = {'evolution_position': (index % 4) / 3}
            elif task == 'causal':
                case['expected'] = {'evidence_grade': (1, 3, 5)[index % 3]}
                if metric == 'causal-claims':
                    case['expected'].update(sign='positive' if index % 2 == 0 else 'negative', lag_days=10 + index * 80,
                                            elasticity_mode=.2 + (index % 5) * .1)
            elif task == 'gameplay':
                pairs = [(play, component) for play in row['input']['task']['catalogue'] for component in row['input']['task']['org_components']]
                case['expected'] = {'opportunities': [[play, component] for ordinal, (play, component) in enumerate(pairs)
                                                     if index % 4 and ordinal % 3 == index % 3]}
            else:
                case['expected'] = {'admitted': index % 4 == 0,
                                   'stopped_at': None if index % 4 == 0 else ('purpose', 'necessity', 'proportionality')[index % 4 - 1]}
            case['basis'] = {'witness': 'TEST_ONLY reference reason, not empirical truth',
                             'source_hashes': {key: value['sha256'] for key, value in row['sources'].items()}}
            source = row['sources']['task_packet']
            case['rights'] = {'statement': 'TEST_ONLY authored declarations and fixture artifacts',
                'evidence': list(row['sources']), 'uses': ['development'], 'covered_sources': list(row['sources'])}
            case['field_support'] = {name: {'meaning': 'TEST_ONLY worked value; no real label authority',
                'sources': ['task_packet'], 'witnesses': [{'source': 'task_packet', 'start': 0,
                    'end': source['bytes'], 'sha256': source['sha256']}]} for name in case['expected']}
            if task == 'gameplay' and not case['expected']['opportunities']:
                case['field_support']['opportunities']['complete_negative_basis'] = 'TEST_ONLY independently authored full pair-domain fixture; no real negative labels'
            case['basis_binding'] = binding_for(case)
            admission = admit_reference(case, scope)
            assert admission.admitted, admission.reasons
            admissions.append(admission)
        population = q.Population.freeze(metric, tuple(admissions), envelope,
            {'status': 'development', 'history': ['TEST_ONLY openly authored software controls'],
             'training_provenance': 'unknown; no empirical cleanliness claim'})
        selections.append(q.Selection.freeze(actor, population, basis_holds,
            review=q.PopulationReview.test_only(population), assessment_policy=BasisPolicy.for_task(task, metric, ('TEST_ONLY-task-review',)),
            task_contract=contract, task_policy=policy))
    group = q.CaptureGroup.freeze(tuple(selections)) if task == 'causal' else None
    core = group.capture() if group else None
    bindings, assessments, captures = [], {}, {}
    scores = tmp_path / 'TEST_ONLY-task-scores.jsonl'
    for selected in selections:
        capture = group.view(selected, core) if group else selected.capture()
        request = selected.assessment_request(capture)
        assessment = task_review_store(tmp_path / ('review-' + selected.population.metric), selected.assessment_policy, request).assess(
            selected.assessment_policy, request)
        selected.record(capture, '2026-10-30T00:00:00Z', scores, assessment)
        bindings.append((selected, capture, assessment)); assessments[selected.population.metric] = assessment
        captures[selected.population.metric] = capture
    resolver = q.Resolver(tuple(bindings), scores, allow_test_only=True)
    host_policy = TaskPolicy.freeze(contract, (resolved[0],))
    inputs = resolved[0].host_inputs()
    job = {'task': task, 'task_contract_sha256': contract.digest, 'model_version': actor.model_version,
        'organisation': first['context']['organisation'], 'subjects': [first['subject']]}
    return {'selections': tuple(selections), 'resolver': resolver, 'inputs': inputs, 'job': job,
            'policy': policy, 'host_policy': host_policy, 'resolved': tuple(resolved), 'actor': actor,
            'captures': captures, 'assessments': assessments, 'group': group, 'core': core, 'scores': scores}


def test_actual_typed_evolution_mechanics_derives_permission_and_reviews_without_second_call(protected_request, tmp_path):
    material = genuine_task_material(protected_request, tmp_path)
    selected = material['selections'][0]
    assert material['resolver'].permission('evolution-judge', material['actor'].model_version).granted
    assert not q.Resolver(((selected, material['captures']['evolution-judge'], material['assessments']['evolution-judge']),),
        material['scores']).permission('evolution-judge', material['actor'].model_version).granted
    session = material['resolver'].host_session(material['inputs']); session.bind_task_job(material['job'])
    before = len(TASK_CALLS)
    result = session.judge('evolution-judge', material['actor'].model_version, material['job']['subjects'][0])
    assert result.receipt is None and len(session.pending_reviews) == 1
    assert len(TASK_CALLS) == before + 1
    pending = session.pending_reviews[0]
    store = task_review_store(tmp_path / 'live-review', selected.assessment_policy, q.canonical(pending['request']))
    result = session.review_pending(pending['request_digest'], store)
    assert result.receipt and result.reason is None
    assert len(TASK_CALLS) == before + 1
    restored = q.HostSession.restore(session.archive(), material['resolver'], task_policy=material['host_policy'])
    assert restored.archive() == session.archive()
    assert len(TASK_CALLS) == before + 1


def test_actual_causal_pair_invokes_once_reviews_both_and_restores_without_reinvocation(protected_request, tmp_path):
    material = genuine_task_material(protected_request, tmp_path, task='causal')
    actor = material['actor'].model_version
    assert all(material['resolver'].permission(metric, actor).granted for metric in TaskContract.freeze('causal').metrics)
    session = material['resolver'].host_session(material['inputs']); session.bind_task_job(material['job'])
    subject = material['job']['subjects'][0]
    before = len(TASK_CALLS)
    single = session.judge('causal-claims', actor, subject)
    assert single.receipt is None and 'paired judgement' in single.reason
    assert len(TASK_CALLS) == before
    result = session.judge_group(actor, subject)
    assert result.receipt is None and len(session.pending_reviews) == 2
    assert len(TASK_CALLS) == before + 1
    pending = session.pending_reviews[0]
    selected = next(item for item in material['selections'] if item.assessment_policy.digest == pending['request']['policy'])
    store = task_review_store(tmp_path / 'live-first', selected.assessment_policy, q.canonical(pending['request']))
    first = session.review_pending(pending['request_digest'], store)
    assert first.receipt is None and len(session.pending_reviews) == 1
    restored = q.HostSession.restore(session.archive(), material['resolver'], task_policy=material['host_policy'])
    assert restored.archive() == session.archive() and len(TASK_CALLS) == before + 1
    pending = restored.pending_reviews[0]
    selected = next(item for item in material['selections'] if item.assessment_policy.digest == pending['request']['policy'])
    store = task_review_store(tmp_path / 'live-second', selected.assessment_policy, q.canonical(pending['request']))
    result = restored.review_pending(pending['request_digest'], store)
    assert result.receipt and result.reason is None and len(TASK_CALLS) == before + 1
    final = q.HostSession.restore(restored.archive(), material['resolver'], task_policy=material['host_policy'])
    assert final.archive() == restored.archive() and len(TASK_CALLS) == before + 1

from test_task_inputs import protected_request


def test_actual_gameplay_empty_judgement_keeps_complete_negative_domain(protected_request, tmp_path):
    material = genuine_task_material(protected_request, tmp_path, task='gameplay')
    assert material['resolver'].permission('gameplay-lens', material['actor'].model_version).granted
    session = material['resolver'].host_session(material['inputs']); session.bind_task_job(material['job'])
    before = len(TASK_CALLS)
    session.judge('gameplay-lens', material['actor'].model_version, material['job']['subjects'][0])
    attempt = session.task_snapshot()['attempts'][0]
    assert attempt['output']['answer'] == {'opportunities': []}
    checks = attempt['output']['basis']['checks']
    expected = {(play, component) for play in material['resolved'][0].payload['task']['catalogue']
                for component in material['resolved'][0].payload['task']['org_components']}
    assert {(item['play'], item['component']) for item in checks} == expected
    assert all(item['present'] is False and item['incumbency_checked'] is False for item in checks)
    assert len(TASK_CALLS) == before + 1 and len(session.pending_reviews) == 1
    pending = session.pending_reviews[0]; selected = material['selections'][0]
    store = task_review_store(tmp_path / 'live-gameplay-review', selected.assessment_policy, q.canonical(pending['request']))
    assert session.review_pending(pending['request_digest'], store).receipt
    restored = q.HostSession.restore(session.archive(), material['resolver'], task_policy=material['host_policy'])
    assert restored.archive() == session.archive() and len(TASK_CALLS) == before + 1


def test_actual_ethics_keeps_child_admit_and_independent_mandatory_dpia_denial(protected_request, tmp_path):
    material = genuine_task_material(protected_request, tmp_path, task='ethics')
    assert material['resolver'].permission('ethics-gate', material['actor'].model_version).granted
    session = material['resolver'].host_session(material['inputs']); session.bind_task_job(material['job'])
    before = len(TASK_CALLS)
    session.judge('ethics-gate', material['actor'].model_version, material['job']['subjects'][0])
    attempt = session.task_snapshot()['attempts'][0]
    assert attempt['output']['answer']['admitted'] is True
    assert attempt['mandatory_gate']['admitted'] is False
    assert set(attempt['mandatory_gate']) == {'admitted', 'source_sha256', 'result_sha256'}
    pending = session.pending_reviews[0]; selected = material['selections'][0]
    store = task_review_store(tmp_path / 'live-ethics-review', selected.assessment_policy, q.canonical(pending['request']))
    assert session.review_pending(pending['request_digest'], store).receipt
    restored = q.HostSession.restore(session.archive(), material['resolver'], task_policy=material['host_policy'])
    assert restored.archive() == session.archive() and len(TASK_CALLS) == before + 1
