"""TEST_ONLY clean pinned model closures, never estate inputs or reference labels."""
from pathlib import Path

import pytest
import yaml

from twin import fixtures
from twin.repo import ModelRepo
from twin.model import Overlay
from twin.task_inputs import resolve_task_input
from test_task_inputs import protected_request, task_request


@pytest.mark.parametrize('task', ['evolution', 'causal', 'gameplay', 'ethics'])
@pytest.mark.parametrize('count', [19, 21])
def test_registered_task_refuses_changed_model_cardinality_with_honest_new_pins(protected_request, task, count):
    args = task_request(protected_request, task)
    root = args['repo'].model_root
    target = root / 'orgs/driftwood/components/test-only-local-standing.yaml'
    if count == 19:
        target.unlink()
    else:
        target = root / 'orgs/driftwood/components/test-only-extra.yaml'
        target.write_text(yaml.safe_dump({'id': 'test-only-extra', 'name': 'TEST_ONLY new component',
            'kind': 'activity', 'evolution': 'product', 'visibility': .5, 'needs': ['test-only-cloud']}))
    fixtures.git(root, 'add', '--', 'orgs/driftwood/components')
    fixtures.git(root, 'commit', '-q', '-m', 'TEST_ONLY honest different model cardinality')
    repo = ModelRepo.open(root); overlay = Overlay.load(repo, 'driftwood', pricing_threshold=3)
    args['repo'] = repo
    args['protected_job']['model_pins'] = {'model_repo': repo.pin.as_dict(),
        'overlay': overlay.ref.as_dict(), 'world': overlay.world.ref.as_dict()}
    assert len(overlay.world.components) + len(overlay.components) == count
    with pytest.raises(ValueError, match='twenty'):
        resolve_task_input(**args)
