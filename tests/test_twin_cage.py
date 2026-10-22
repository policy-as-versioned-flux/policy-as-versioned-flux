"""Static workflow inputs only; no actor capability or live-workflow proof.

Writer source is the two real reviewed programs; unrelated reader facts below
are explicit fixtures. Every assertion crosses the production grade interface.
"""
from __future__ import annotations

import importlib.util
import hashlib
import copy
import json
import os
import shutil
from pathlib import Path
import subprocess
import sys
import tempfile
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


class TwinCageCLI(unittest.TestCase):
    """Real CLI over synthetic origin/main; never a live capability experiment."""

    def setUp(self) -> None:
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        self.estate = Path(directory.name)
        self.hub = self.estate / 'hub'
        shutil.copytree(HERE, self.hub / 'verify/twin-cage')
        for relative in ('talk/local-clock.sh', 'twin/enact_guard.py',
                         'talk/observation-delivery-producer.sh'):
            destination = self.hub / relative
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(ROOT / relative, destination)
        self.environment = dict(os.environ, GIT_CONFIG_GLOBAL='/dev/null',
                                GIT_CONFIG_NOSYSTEM='1', GIT_TERMINAL_PROMPT='0',
                                PYTHONDONTWRITEBYTECODE='1')
        for organization in ('driftwood', 'tuppence', 'ludlow'):
            repo = self.estate / organization
            repo.mkdir()
            workflow, files = fixture(organization)
            files[WORKFLOW] = yaml.safe_dump(workflow, sort_keys=False)
            for path, content in files.items():
                target = repo / path
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_text(content)
            self.git(organization, 'init', '-b', 'main')
            self.publish(organization)

    def git(self, organization: str, *arguments: str) -> str:
        result = subprocess.run(
            ['git', '-c', 'core.hooksPath=/dev/null', '-c', 'commit.gpgsign=false',
             '-c', 'user.name=Static fixture', '-c', 'user.email=fixture@example.invalid',
             '-C', str(self.estate / organization), *arguments],
            env=self.environment, text=True, capture_output=True, check=True)
        return result.stdout.strip()

    def publish(self, organization: str) -> None:
        self.git(organization, 'add', '.')
        self.git(organization, 'commit', '-m', 'Labelled static served-workflow fixture')
        self.git(organization, 'update-ref', 'refs/remotes/origin/main',
                 self.git(organization, 'rev-parse', 'HEAD'))

    def check(self) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, '-B', str(self.hub / 'verify/twin-cage/twin_cage.py'), 'check',
             '--estate', str(self.estate)], env=self.environment, text=True, capture_output=True)

    def test_dated_native_receipt_discharges_the_measured_capability_obligation(self) -> None:
        result = self.check()
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(result.stdout.splitlines(), [
            'PASS: driftwood served twin workflow fits its priced rung dials',
            'PASS: tuppence served twin workflow fits its priced rung dials',
            'PASS: ludlow served twin workflow fits its priced rung dials',
            'PASS: local-clock sandbox: macOS Claude Code 2.1.308 on 2026-10-22 blocked three tested rebuilt-environment routes and outside-directory Read',
            'LIMIT: dated source-bound measurement; other routes, hosts and native versions are not established; no fresh live test was run'])
        self.assertEqual(result.stderr, '')

    def test_served_workflow_fault_stays_red_with_a_valid_native_receipt(self) -> None:
        workflow, _ = fixture('driftwood')
        workflow['jobs']['twin']['permissions'] = {'contents': 'write'}
        (self.estate / 'driftwood' / WORKFLOW).write_text(yaml.safe_dump(workflow, sort_keys=False))
        self.publish('driftwood')
        result = self.check()
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertEqual(result.stdout.splitlines(), [
            'FAIL: driftwood served twin cage: twin job holds capabilities beyond contents: read',
            'PASS: tuppence served twin workflow fits its priced rung dials',
            'PASS: ludlow served twin workflow fits its priced rung dials',
            'PASS: local-clock sandbox: macOS Claude Code 2.1.308 on 2026-10-22 blocked three tested rebuilt-environment routes and outside-directory Read',
            'LIMIT: dated source-bound measurement; other routes, hosts and native versions are not established; no fresh live test was run'])
        self.assertEqual(result.stderr, '')


    def rewrite_proof(self, name: str, data: bytes) -> None:
        """Update the untrusted envelope too, so outcome tests reach admission."""
        proof = self.hub / 'verify/twin-cage/proofs/native-20261022'
        (proof / name).write_bytes(data)
        receipt = json.loads((proof / 'receipt.json').read_bytes())
        receipt['files'][name] = hashlib.sha256(data).hexdigest()
        (proof / 'receipt.json').write_text(json.dumps(receipt))

    def assert_receipt_refused(self, diagnostic: str) -> None:
        result = self.check()
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn('FAIL: local-clock native capability receipt:', result.stdout)
        self.assertIn(diagnostic, result.stdout)
        self.assertNotIn('PASS: local-clock sandbox:', result.stdout)
        self.assertEqual(result.stderr, '')

    def test_missing_and_modified_native_proof_remain_red(self) -> None:
        proof = self.hub / 'verify/twin-cage/proofs/native-20261022'
        path = proof / 'bash-tool-messages.jsonl'
        saved = path.read_bytes()
        path.unlink()
        self.assert_receipt_refused('bash-tool-messages.jsonl')
        path.write_bytes(saved + b'\n')
        self.assert_receipt_refused('native proof hash changed')

    def test_cage_guard_and_executed_probe_drift_remain_red(self) -> None:
        for relative in ('talk/local-clock.sh', 'twin/enact_guard.py',
                         'verify/twin-cage/proofs/native-20261022/probe-stream.py',
                         'verify/twin-cage/proofs/native-20261022/probe-filetool.py'):
            with self.subTest(relative=relative):
                path = self.hub / relative
                saved = path.read_bytes()
                path.write_bytes(saved + b'\n# changed source\n')
                self.assert_receipt_refused('changed')
                path.write_bytes(saved)

    def test_rehashed_probe_still_requires_the_actually_executed_source(self) -> None:
        proof = self.hub / 'verify/twin-cage/proofs/native-20261022'
        name = 'probe-stream.py'
        self.rewrite_proof(name, (proof / name).read_bytes() + b'\n# a different probe\n')
        self.assert_receipt_refused('executed probe source binding changed')

    def test_broken_positive_control_cannot_earn_a_capability_pass(self) -> None:
        proof = self.hub / 'verify/twin-cage/proofs/native-20261022'
        data = json.loads((proof / 'unsandboxed-control.json').read_bytes())
        data['rebuilt_keychain_route'] = {'exit': 1, 'nonempty_output': False}
        self.rewrite_proof('unsandboxed-control.json', json.dumps(data).encode())
        self.assert_receipt_refused('unsandboxed controls')

    def test_successful_escape_cannot_hide_in_a_rehashed_receipt(self) -> None:
        proof = self.hub / 'verify/twin-cage/proofs/native-20261022'
        name = 'bash-tool-messages.jsonl'
        events = [json.loads(line) for line in (proof / name).read_bytes().splitlines()]
        measured = json.loads(events[1]['message']['content'][0]['content'])
        measured['rebuilt_keychain_route'] = {'exit': 0, 'nonempty_output': True}
        text = json.dumps(measured)
        events[1]['message']['content'][0]['content'] = text
        events[1]['tool_use_result']['stdout'] = text
        self.rewrite_proof(name, ('\n'.join(json.dumps(event) for event in events) + '\n').encode())
        self.assert_receipt_refused('tested escape succeeded')

    def test_unexpected_extra_native_tool_actions_are_refused(self) -> None:
        proof = self.hub / 'verify/twin-cage/proofs/native-20261022'
        name = 'bash-tool-messages.jsonl'
        data = (proof / name).read_bytes()
        self.rewrite_proof(name, data + data.splitlines(keepends=True)[0])
        self.assert_receipt_refused('unexpected extra or missing tool actions')

    def test_native_version_is_bound_to_the_measured_environment(self) -> None:
        path = self.hub / 'verify/twin-cage/proofs/native-20261022/receipt.json'
        data = json.loads(path.read_bytes())
        data['environment']['native_binary'] = 'Claude Code unmeasured-version'
        path.write_text(json.dumps(data))
        self.assert_receipt_refused('environment or schema changed')


class TwinObservationTransport(unittest.TestCase):
    def test_reviewed_observation_transport_is_not_a_declaration_proposal(self) -> None:
        for organization in ('driftwood', 'tuppence', 'ludlow'):
            with self.subTest(organization=organization):
                workflow, files = fixture(organization)
                self.assertEqual(grade(workflow, files, organization), [])

    def test_proposal_command_whitespace_does_not_bypass_rung_guards(self) -> None:
        for organization in ('driftwood', 'tuppence', 'ludlow'):
            for command in ('gh  pr create', 'gh\tpr create', 'gh pr\tcreate',
                            'gh \\\n  pr create'):
                with self.subTest(organization=organization, command=command):
                    workflow, files = fixture(organization)
                    publisher = next(s for s in workflow['jobs']['write']['steps']
                                     if 'DELIVERY_BRANCH=' in s.get('run', ''))
                    self.assertEqual(publisher['run'].count('gh pr create'), 1)
                    publisher['run'] = publisher['run'].replace('gh pr create', command)
                    self.assertIn('proposal step runs outside baseline/restricted',
                                  grade(workflow, files, organization))

    def test_unknown_proposal_whitespace_still_requires_both_rung_guards(self) -> None:
        guards = ("", "steps.cage.outputs.rung == 'baseline'",
                  "steps.cage.outputs.rung == 'restricted'",
                  "steps.cage.outputs.rung == 'baseline' || steps.cage.outputs.rung == 'restricted'")
        commands = ('gh  pr create', 'gh\tpr create', 'gh \\\n  pr create',
                    'git  checkout -b proposal', 'git\tcheckout \\\n  -b proposal')
        for organization in ('driftwood', 'tuppence', 'ludlow'):
            for command in commands:
                for condition in guards:
                    with self.subTest(organization=organization, command=command, condition=condition):
                        workflow, files = fixture(organization)
                        writer = workflow['jobs']['write']
                        cage_step = next(s for s in writer['steps'] if s.get('id') == 'cage')
                        writer['steps'] = [cage_step, {'run': command, 'if': condition}]
                        faults = grade(workflow, files, organization)
                        if condition == guards[-1]:
                            self.assertEqual(faults, [])
                        else:
                            self.assertIn('proposal step runs outside baseline/restricted', faults)

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

    def test_program_metadata_preserves_scalar_types(self) -> None:
        for organization in ('driftwood', 'tuppence', 'ludlow'):
            for wrong_depth in (False, 0.0):
                with self.subTest(organization=organization, wrong_depth=wrong_depth):
                    workflow, files = fixture(organization)
                    checkout = next(s for s in workflow['jobs']['write']['steps']
                                    if str(s.get('uses', '')).startswith('actions/checkout@'))
                    self.assertIs(type(checkout['with']['fetch-depth']), int)
                    checkout['with']['fetch-depth'] = wrong_depth
                    self.assertIn('proposal step runs outside baseline/restricted',
                                  grade(workflow, files, organization))


if __name__ == '__main__':
    unittest.main()
