"""TEST_ONLY both-metric permission controls derived from real retained artifacts."""
from twin import qualification as q
from test_task_sessions import genuine_task_material, task_review_store, TASK_CALLS
from test_task_inputs import protected_request


def test_each_failed_causal_metric_independently_blocks_the_pair_before_invocation(protected_request, tmp_path):
    material = genuine_task_material(protected_request, tmp_path, task='causal')
    actor = material['actor'].model_version
    for blocked in ('causal-claims', 'causal-claims-grade-accuracy'):
        bindings = []
        scores = tmp_path / ('blocked-' + blocked + '.jsonl')
        for selected in material['selections']:
            metric = selected.population.metric
            capture = material['captures'][metric]
            assessment = material['assessments'][metric]
            if metric == blocked:
                request = selected.assessment_request(capture)
                store = task_review_store(tmp_path / ('failed-' + metric), selected.assessment_policy, request, 'fail')
                assessment = store.assess(selected.assessment_policy, request)
            selected.record(capture, '2026-10-30T00:00:00Z', scores, assessment)
            bindings.append((selected, capture, assessment))
        resolver = q.Resolver(tuple(bindings), scores, allow_test_only=True)
        assert not resolver.permission(blocked, actor).granted
        other = next(selected.population.metric for selected in material['selections'] if selected.population.metric != blocked)
        assert resolver.permission(other, actor).granted
        session = resolver.host_session(material['inputs']); session.bind_task_job(material['job'])
        before = len(TASK_CALLS)
        result = session.judge_group(actor, material['job']['subjects'][0])
        assert result.receipt is None and 'human required' in result.reason
        assert session.pending_reviews == [] and len(TASK_CALLS) == before
        assert session.task_snapshot()['attempts'][0]['disposition'] == 'refused-before-invocation'
        restored = q.HostSession.restore(session.archive(), resolver, task_policy=material['host_policy'])
        assert restored.archive() == session.archive() and len(TASK_CALLS) == before
