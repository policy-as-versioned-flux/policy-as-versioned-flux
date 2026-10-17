"""Static workflow inputs only; no actor capability or live-workflow proof.

Writer source is the two real reviewed programs; unrelated reader facts below
are explicit fixtures. Every assertion crosses the production grade interface.
"""
from __future__ import annotations

import importlib.util
import copy
import json
from pathlib import Path
import sys
import unittest

import yaml

ROOT = Path(__file__).resolve().parents[1]
HERE = ROOT / 'verify/twin-cage'
sys.path.insert(0, str(HERE))
spec = importlib.util.spec_from_file_location('served_twin_cage', HERE / 'twin_cage.py')
assert spec is not None and spec.loader is not None
cage = importlib.util.module_from_spec(spec)
spec.loader.exec_module(cage)
WORKFLOW = '.github/workflows/twin-sweep.yml'


def fixture(organization: str) -> tuple[dict, dict[str, str]]:
    shape = 'forward' if organization == 'driftwood' else 'emitter'
    contract = yaml.safe_load((HERE / f'writer-{shape}.yaml').read_text().replace(
        '@ORGANIZATION@', organization))
    tail = (ROOT / 'talk/observation-delivery-producer.sh').read_text()
    for step in contract['writer']['steps']:
        if 'run' in step:
            step['run'] = step['run'].replace('@OBSERVATION_TRANSPORT@\n', tail)
    workflow = {'env': contract['environment'], 'defaults': contract['defaults'], 'jobs': {
        'write': contract['writer'],
        'twin': {'permissions': {'contents': 'read'}, 'steps': [
            {'id': 'cage', 'run': 'jq agent-cage twin-agent composed/evidence.json\nrung=isolated'},
            {'id': 'pin', 'run': 'read twin/PIN.yaml; echo hub_commit=...'},
            {'uses': 'actions/checkout@' + 'a' * 40,
             'with': {'repository': cage.HUB, 'ref': '${{ steps.pin.outputs.hub_commit }}'}}]}}}
    files = {'twin/PIN.yaml': 'hub_commit: ' + 'a' * 40 + '\ntag_cut: false\n',
             '.github/requirements/twin-sweep.txt': 'pyyaml==6.0.3 --hash=sha256:' + 'b' * 64,
             'composed/evidence.json': json.dumps({'prices': [
                 {'kind': 'agent-cage', 'subject': 'twin-agent', 'proposed_tier': 'quarantine'}]})}
    return workflow, files


def grade(workflow: dict, files: dict[str, str], organization: str | None) -> list[str]:
    return cage.grade({**files, WORKFLOW: yaml.safe_dump(workflow, sort_keys=False)}, organization)


class TwinObservationTransport(unittest.TestCase):
    def test_reviewed_observation_transport_is_not_a_declaration_proposal(self) -> None:
        for organization in ('driftwood', 'tuppence', 'ludlow'):
            with self.subTest(organization=organization):
                workflow, files = fixture(organization)
                self.assertEqual(grade(workflow, files, organization), [])

    def test_labels_do_not_choose_the_program_class(self) -> None:
        for organization in ('driftwood', 'tuppence', 'ludlow'):
            with self.subTest(organization=organization):
                workflow, files = fixture(organization)
                workflow['name'] = 'not a trusted workflow name'
                writer = workflow['jobs']['write']
                writer['name'] = 'not a trusted writer name'
                for step in writer['steps']:
                    step['name'] = 'not a trusted observation step name'
                self.assertEqual(grade(workflow, files, organization), [])

    def test_organization_is_bound_by_the_served_caller(self) -> None:
        workflow, files = fixture('tuppence')
        for organization in (None, 'foreign', 'driftwood', 'ludlow'):
            with self.subTest(organization=organization):
                self.assertIn('proposal step runs outside baseline/restricted',
                              grade(workflow, files, organization))

    def test_lane_and_effective_environment_cannot_be_widened(self) -> None:
        for organization in ('driftwood', 'tuppence', 'ludlow'):
            for key, value in (
                    ('OBSERVATION_LANE', 'party.yaml'),
                    ('OBSERVATION_LANE', '.'),
                    ('OBSERVATION_LANE', 'observations/twin-sweep.jsonl party.yaml'),
                    ('OBSERVATION_LANE', '${UNRESOLVED_LANE}'),
                    ('OBSERVATION_CLOCK', 'other-clock'),
                    ('DEFAULT_BRANCH', 'other-branch'),
                    ('BASH_ENV', 'unreviewed-shell-program')):
                with self.subTest(organization=organization, key=key, value=value):
                    workflow, files = fixture(organization)
                    workflow['env'][key] = value
                    self.assertIn('proposal step runs outside baseline/restricted',
                                  grade(workflow, files, organization))

    def test_job_step_and_default_overrides_cannot_change_execution(self) -> None:
        for organization in ('driftwood', 'tuppence', 'ludlow'):
            for scope in ('job_env', 'step_env', 'workflow_shell', 'workflow_cwd', 'job_shell'):
                with self.subTest(organization=organization, scope=scope):
                    workflow, files = fixture(organization)
                    writer = workflow['jobs']['write']
                    if scope == 'job_env':
                        writer['env'] = {'OBSERVATION_LANE': 'party.yaml'}
                    elif scope == 'step_env':
                        writer['steps'][-2].setdefault('env', {})['OBSERVATION_LANE'] = 'party.yaml'
                    elif scope == 'workflow_shell':
                        workflow['defaults'] = {'run': {'shell': 'sh'}}
                    elif scope == 'workflow_cwd':
                        workflow['defaults'] = {'run': {'working-directory': '../other'}}
                    else:
                        writer['defaults'] = {'run': {'shell': 'sh'}}
                    self.assertIn('proposal step runs outside baseline/restricted',
                                  grade(workflow, files, organization))

    def test_mixed_and_post_cage_writes_are_not_observation_transport(self) -> None:
        for organization in ('driftwood', 'tuppence', 'ludlow'):
            for change in ('mixed_write', 'post_write', 'before_write', 'stage_declaration'):
                with self.subTest(organization=organization, change=change):
                    workflow, files = fixture(organization)
                    steps = workflow['jobs']['write']['steps']
                    publisher = next(s for s in steps if 'DELIVERY_BRANCH=' in s.get('run', ''))
                    if change == 'mixed_write':
                        publisher['run'] += '\nprintf declaration > party.yaml\n'
                    elif change == 'stage_declaration':
                        publisher['run'] = 'git add -- party.yaml\n' + publisher['run']
                    else:
                        step = {'run': 'printf declaration > party.yaml'}
                        steps.insert(0 if change == 'before_write' else len(steps), step)
                    self.assertIn('proposal step runs outside baseline/restricted',
                                  grade(workflow, files, organization))

    def test_pending_reference_and_original_scope_are_load_bearing(self) -> None:
        changes = (
            ('observations/${OBSERVATION_CLOCK}/', 'declarations/${OBSERVATION_CLOCK}/'),
            ('--force-with-lease="refs/heads/${DELIVERY_BRANCH}:"', '--force'),
            ('ORIGINAL_OBSERVATION="$(git rev-parse HEAD)"', 'ORIGINAL_OBSERVATION=other'),
            ('if [ "${GITHUB_REF_NAME}" != "${DEFAULT_BRANCH}" ]', 'if false'),
            ('git push --force-with-lease=', 'echo --force-with-lease='))
        for organization in ('driftwood', 'tuppence', 'ludlow'):
            for old, new in changes:
                with self.subTest(organization=organization, old=old):
                    workflow, files = fixture(organization)
                    publisher = next(s for s in workflow['jobs']['write']['steps']
                                     if 'DELIVERY_BRANCH=' in s.get('run', ''))
                    self.assertIn(old, publisher['run'])
                    publisher['run'] = publisher['run'].replace(old, new)
                    self.assertIn('proposal step runs outside baseline/restricted',
                                  grade(workflow, files, organization))

    def test_writer_order_and_default_cage_are_load_bearing(self) -> None:
        for organization in ('driftwood', 'tuppence', 'ludlow'):
            workflow, files = fixture(organization)
            steps = workflow['jobs']['write']['steps']
            steps[-2], steps[-1] = steps[-1], steps[-2]
            self.assertIn('proposal step runs outside baseline/restricted',
                          grade(workflow, files, organization))
            workflow, files = fixture(organization)
            workflow['jobs']['write']['if'] = 'true'
            errors = grade(workflow, files, organization)
            self.assertIn('proposal step runs outside baseline/restricted', errors)
            self.assertIn('isolated rung still starts the writer', errors)

    def test_declaration_proposals_still_require_both_rung_guards(self) -> None:
        for replacement in ('true', "steps.cage.outputs.rung == 'baseline'",
                            "steps.cage.outputs.rung == 'restricted'"):
            with self.subTest(replacement=replacement):
                workflow, files = fixture('driftwood')
                declaration = next(s for s in workflow['jobs']['write']['steps']
                                   if 'git checkout -b' in s.get('run', ''))
                declaration['if'] = replacement
                self.assertIn('proposal step runs outside baseline/restricted',
                              grade(workflow, files, 'driftwood'))

    def test_other_writer_constraints_are_still_graded(self) -> None:
        workflow, files = fixture('tuppence')
        original = copy.deepcopy(workflow)
        workflow['jobs']['write']['steps'].append({'uses': 'untrusted/code@' + 'a' * 40})
        self.assertIn('writer executes a non-inert action: untrusted/code@' + 'a' * 40,
                      grade(workflow, files, 'tuppence'))
        workflow = original
        workflow['jobs']['twin']['permissions'] = {'contents': 'write'}
        self.assertIn('twin job holds capabilities beyond contents: read',
                      grade(workflow, files, 'tuppence'))


if __name__ == '__main__':
    unittest.main()
