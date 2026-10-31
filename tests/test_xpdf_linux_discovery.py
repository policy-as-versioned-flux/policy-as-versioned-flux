"""TEST_ONLY discovery interfaces; no actual tool/query/native action."""
import importlib.util
import json
from pathlib import Path
from unittest.mock import patch

SCRIPT = Path(__file__).parents[1] / 'bench/pinned-candidate/xpdf-origin/discover_linux_tools.py'
spec = importlib.util.spec_from_file_location('xpdf_discovery', SCRIPT)
assert spec and spec.loader
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


def selection():
    return dict(schema='twin.xpdf-linux-discovery-selection/v1', scope='DISCOVERY_ONLY', source_commit='1' * 40, source_tree='2' * 40,
        workflow_sha256='3' * 64, driver_sha256='4' * 64, bootstrap_selection_sha256='5' * 64,
        query_profile_sha256='80decb0cbcb0780746754311962ce67c36e2c6a73202fbf0a87a7bb9fc4b84b6', limits_profile='discovery-A60/v1',
        expected_row=dict(os='ubuntu-24.04', arch='x86_64-linux'))


def held_bundle():
    selected = selection()
    result = module.discover_linux_tools(selected, Path('/TEST_ONLY/uncreated'))
    payload = {'SELECTION.json': module._json(selected), 'ENVIRONMENT.json': b'{}\n'}
    entries = [dict(path=name, bytes=len(raw), sha256=module._sha(raw), role='metadata') for name, raw in sorted(payload.items())]
    payload['FILES.json'] = module._json(dict(schema='twin.xpdf-linux-discovery-files/v1', entries=entries))
    result['files_manifest_sha256'] = module._sha(payload['FILES.json'])
    payload['RESULT.json'] = module._json(result)
    return payload, result


def test_public_selection_cannot_appoint_discovery_or_touch_the_host(tmp_path):
    with patch('subprocess.Popen', side_effect=AssertionError('no child')), patch('time.monotonic', side_effect=AssertionError('no host clock')):
        result = module.discover_linux_tools({'approved': True, 'scope': 'DISCOVERY_ONLY'}, tmp_path / 'new')
    assert result['inventory_state'] == 'NOT_STARTED'
    assert result['run_identity'] is None and result['original_started'] is None
    assert result['build_hold'] == 'H_PROBE_EXECUTION_UNESTABLISHED'
    assert result['build_complete'] is False and result['native_execution'] is False
    assert result['commands'] == [] and not (tmp_path / 'new').exists()


def test_pure_not_started_bundle_preserves_unknowns_and_has_no_permission():
    bundle, result = held_bundle()
    with patch('subprocess.Popen', side_effect=AssertionError('no child')):
        summary = module.check_discovery_bundle(bundle, result['selection_sha256'])
    assert summary == dict(inventory_state='NOT_STARTED', build_hold='H_PROBE_EXECUTION_UNESTABLISHED', build_complete=False, native_execution=False)


def test_pure_checker_rejects_public_build_authority_in_discovery_data():
    import pytest
    bundle, result = held_bundle()
    result['build_complete'] = True
    bundle['RESULT.json'] = module._json(result)
    with pytest.raises(ValueError):
        module.check_discovery_bundle(bundle, result['selection_sha256'])


def test_accepted_binding_oracle_and_unknown_projection_are_conserved():
    result = dict(selection_sha256='1' * 64, original_started=100, deadline=160, finished=107)
    query = dict(index=0, argv=['/usr/bin/cmake', '--version'], environment={'PATH': '/usr/bin:/bin', 'HOME': '/TEST_ONLY/home'},
        started=101, deadline=106, finished=106, custody={'leader_pid': 42})
    context, command = module._projection(result, query)
    assert command['environment_sha256'] == '68f002428cd50022b9674d92d388c4486d21861c597e26b62d9694c261caf4f9'
    assert module._build._binding(context, command) == 'f49567892b705f59693a53666a1fa611b21473f8a326f1e76c9ca8ec724021a2'
    query.update(started=None, finished=None)
    query['custody']['leader_pid'] = None
    context, command = module._projection(result, query)
    assert command['started'] is None and command['ended'] is None and command['custody']['leader_pid'] is None
    assert context['clock'] == dict(started=100, deadline=160, ended=107)


def test_discovery_data_cannot_fill_the_full_build_review_or_appointment(tmp_path):
    import pytest
    with pytest.raises(ValueError):
        module._build._validate(selection(), module._build._schema('BUILD-SELECTION.schema.json'))
    assert module._build._APPOINTED_EXECUTION is None
    assert module._DISCOVERY_APPOINTMENT is None


def test_duplicate_selection_keys_cannot_be_hidden_by_rehashing():
    import pytest
    bundle, result = held_bundle()
    bundle['SELECTION.json'] = bundle['SELECTION.json'][:-1] + b',"scope":"DISCOVERY_ONLY"}'
    result['selection_sha256'] = module._sha(bundle['SELECTION.json'])
    files = json.loads(bundle['FILES.json'])
    for entry in files['entries']:
        if entry['path'] == 'SELECTION.json': entry.update(bytes=len(bundle['SELECTION.json']), sha256=result['selection_sha256'])
    bundle['FILES.json'] = module._json(files)
    result['files_manifest_sha256'] = module._sha(bundle['FILES.json'])
    bundle['RESULT.json'] = module._json(result)
    with pytest.raises(ValueError, match='duplicate'):
        module.check_discovery_bundle(bundle, result['selection_sha256'])
