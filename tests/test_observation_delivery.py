"""Real Git delivery regressions; GitHub and signing are explicit synthetic adapters.

These fixtures demonstrate conservation and ordinary protected merges, not genuine
certificate issuance or live GitHub permission. Authentic payloads informed these
small shapes; no real observations are invented or fixture grades published.
"""
from __future__ import annotations

import copy
import datetime as dt
import importlib
import json
import os
import subprocess
from pathlib import Path

import pytest

TODAY = dt.date(2026, 10, 17)
HUB = 'policy-as-versioned-flux/policy-as-versioned-flux'
PROFILES = [(org, clock) for org in ('driftwood', 'tuppence', 'ludlow')
            for clock in ('drift-sample', 'twin-sweep')]


def git(root, *args, check=True):
    return subprocess.run(['git', '-C', str(root), *args], capture_output=True,
                          check=check).stdout.decode().strip()


def init(root):
    root.mkdir()
    git(root, 'init', '-q', '-b', 'main')
    for key, value in [('commit.gpgsign', 'false'), ('core.hooksPath', os.devnull),
                       ('user.name', 'synthetic fixture'), ('user.email', 'fixture@example.invalid')]:
        git(root, 'config', key, value)


def commit(root, message, email=None):
    git(root, 'add', '-A')
    args = [] if email is None else ['-c', f'user.email={email}']
    git(root, *args, 'commit', '-qm', message)
    return git(root, 'rev-parse', 'HEAD')


def remote(root, path):
    git(root, 'init', '-q', '--bare', '-b', 'main', str(path))
    git(root, 'remote', 'add', 'origin', str(path))
    git(root, 'push', '-q', 'origin', 'main')


def rows(org, clock, source):
    if clock == 'twin-sweep':
        row = dict(adopter_ref=source, feed='forward-intel', moved=False, org=org,
                   run='100', swept_at='2026-10-17T01:00:00Z')
        if org == 'driftwood':
            row.update(proposal='', twin_ref='policy-as-versioned-flux@' + 'a' * 40)
        else:
            row.update(detail='synthetic missing instrument', emitter_exit=3,
                       hub_ref='a' * 40, status='could_not_look', moved=None, twin_pin={'hub_commit': 'a' * 40})
        return {'observations/twin-sweep.jsonl': [row]}
    meta = dict(context='kind-dsample-100', event='schedule', run='100', ts='2026-10-17T01:00:00Z')
    samples = [dict(meta, kind='flux.five-facts/v1', cluster='dsample-100', source=name,
                    party=(org if name == org + '-composed' else name), schema_version=3,
                    pin={}, facts={key: {'observed': None, 'why': 'synthetic could not look'} for key in (
                        'fact_1_ready_at_the_pin_on_the_real_remote',
                        'fact_2_tag_signature_verified_at_the_source_boundary',
                        'fact_3_last_applied_revision_equals_the_pinned_commit',
                        'fact_4_rendered_objects_byte_equal_to_an_offline_render',
                        'fact_5_every_rendered_object_is_in_the_flux_inventory',
                        'fact_6_the_bottom_rung_is_admitted_and_runs',
                        'fact_7_the_bottom_rung_reaches_nothing_while_the_reference_reaches')},
                    falsifiers={key: {'fired': None, 'why': 'synthetic could not look'} for key in (
                        'cluster_side_verification_passes_a_tag_that_identity_pinned_ci_rejects',
                        'verified_source_ready_but_the_object_is_absent_or_unequal_and_unhealed')},
                    reachable=False, reason='fixture',
                    revision='', verdict='COULD-NOT-LOOK')
               for name in (org + '-composed', 'platform', 'nist')]
    workloads = dict(meta, kind='flux.served-workloads/v1', apps_ref='v4.0.0',
                     fact='fact_8_each_served_workload_runs_in_its_cage', observed=None,
                     runner_ceiling={}, why='fixture could not look', workloads=[])
    oscal = dict(meta, kind='flux.oscal-lane/v1', assessment_results={}, risks=[],
                 mapped_served_policy_count=0, missing_risk_observations=[], report_count=0,
                 report_read_errors=[], risk_validation_errors=[], served_policy_count=0,
                 status='could-not-look', unmapped_failed_results=[], unmapped_served_policies=[],
                 why='fixture could not look')
    return {'drift/samples.jsonl': samples, 'drift/workload-samples.jsonl': [workloads],
            'drift/oscal-samples.jsonl': [oscal]}


class API:
    def __init__(self, root, target, hub, org, clock, source, head):
        self.root, self.target, self.hub, self.org, self.clock = root, target, hub, org, clock
        self.repo = f'policy-as-versioned-{org}/{org}'
        self.run = dict(id=100, run_number=17, run_attempt=2, workflow_id=9,
                        path=f'.github/workflows/{clock}.yml', head_sha=source,
                        head_branch='main', event='schedule', status='completed', conclusion='failure',
                        repository={'full_name': self.repo}, head_repository={'full_name': self.repo})
        self.pr = dict(number=4, state='open', merged=False, user={'login': 'github-actions[bot]'},
                       head={'sha': head, 'ref': f'observations/{clock}/100-2', 'repo': {'full_name': self.repo}},
                       base={'ref': 'main', 'repo': {'full_name': self.repo}})
        self.calls, self.approved, self.refuse_merge, self.after = [], False, False, None

    def __call__(self, method, path, body=None):
        self.calls.append((method, path, copy.deepcopy(body)))
        if path == f'repos/{self.repo}': return {'full_name': self.repo, 'default_branch': 'main'}
        if path == f'repos/{HUB}': return {'full_name': HUB, 'default_branch': 'main'}
        if path.endswith('/actions/runs/100/attempts/2'): return copy.deepcopy(self.run)
        if path.endswith('/actions/workflows/' + self.clock + '.yml'):
            return {'id': 9, 'path': self.run['path']}
        if '/pulls?' in path: return [copy.deepcopy(self.pr)]
        if path.endswith('/pulls/4'):
            if self.after: self.after(method, path)
            return copy.deepcopy(self.pr)
        if path == 'graphql':
            if self.after: self.after(method, path)
            return {'data': {'viewer': {'login': 'pavc-other-hand[bot]', 'databaseId': 324560547}}}
        if path.endswith('/reviews'):
            assert body['commit_id'] == self.pr['head']['sha'] and body['event'] == 'APPROVE'
            self.approved = True
            (self.target / 'reviewed-head').write_text(body['commit_id'])
            if self.after: self.after(method, path)
            return {'state': 'APPROVED', 'commit_id': body['commit_id'],
                    'user': {'login': 'pavc-other-hand[bot]', 'id': 324560547}}
        if path.endswith('/merge'):
            assert self.approved and body == {'sha': self.pr['head']['sha'], 'merge_method': 'merge'}
            if self.refuse_merge: return {'merged': False}
            merged = self.root.parent / 'merged'
            git(self.root, 'clone', '-q', str(self.target), str(merged))
            for key, value in [('commit.gpgsign', 'false'), ('core.hooksPath', os.devnull),
                               ('user.name', 'separate fixture reviewer'), ('user.email', 'reviewer@example.invalid')]:
                git(merged, 'config', key, value)
            git(merged, 'merge', '--no-ff', self.pr['head']['sha'], '-m', 'ordinary reviewed merge')
            git(merged, 'push', '-q', 'origin', 'main')
            self.pr.update(state='closed', merged=True, merge_commit_sha=git(merged, 'rev-parse', 'HEAD'))
            return {'merged': True, 'sha': self.pr['merge_commit_sha']}
        raise AssertionError((method, path, body))


@pytest.fixture
def make_estate(tmp_path):
    def make(org='tuppence', clock='twin-sweep'):
        root, hub = tmp_path / 'adopter', tmp_path / 'authority'
        init(root); init(hub)
        (hub / 'twin').mkdir()
        (hub / 'twin/ENACT_MODE').write_text('development\n')
        (hub / 'owner.md').write_text('2026-09-24, owner: "agree".\n')
        (hub / 'twin/ENACT_MODE.why').write_text(
            "mode: development\nuntil: '2026-10-22'\nsaid:\n"
            "  - on: '2026-09-24'\n    by: owner\n    words: agree\n    where: owner.md\n")
        commit(hub, 'current owner authority')
        hub_remote = tmp_path / 'hub.git'; remote(hub, hub_remote)
        (root / '.github/workflows').mkdir(parents=True); (root / 'twin').mkdir()
        (root / 'twin/PIN.yaml').write_text('hub_commit: ' + 'a' * 40 + '\n')
        lanes = ['drift/samples.jsonl', 'drift/workload-samples.jsonl', 'drift/oscal-samples.jsonl'] if clock == 'drift-sample' else ['observations/twin-sweep.jsonl']
        (root / f'.github/workflows/{clock}.yml').write_text('env:\n  OBSERVATION_LANE: "' + ' '.join(lanes) + '"\n')
        # Old row is deliberately not schema-graded: it must be conserved byte for byte.
        first = root / lanes[0]; first.parent.mkdir(exist_ok=True); first.write_bytes(b'{"old":"original bytes", "fail": true}\n')
        source = commit(root, 'measured fixture source')
        target = tmp_path / 'target.git'; remote(root, target)
        git(target, 'config', 'core.hooksPath', str(target / 'hooks'))
        hook = target / 'hooks/update'; hook.write_text('#!/bin/sh\nif [ "$1" = refs/heads/main ]; then\n test -f reviewed-head || { echo GH013 >&2; exit 1; }\n git merge-base --is-ancestor "$(cat reviewed-head)" "$3" || exit 1\nfi\n');hook.chmod(0o755)
        git(root, 'switch', '-qc', f'observations/{clock}/100-2')
        payload = rows(org, clock, source)
        for path, records in payload.items():
            out = root / path; out.parent.mkdir(exist_ok=True)
            with out.open('a') as stream:
                for row in records: stream.write(json.dumps(row, sort_keys=True) + '\n')
        subject = ('drift sample: five facts on an ephemeral cluster [skip ci]' if clock == 'drift-sample' else
                   'twin sweep: observe the forward-intel scenario [skip ci]' if org == 'driftwood' else
                   'twin sweep: record the emitter observation [skip ci]')
        head = commit(root, subject, f'{clock}@policy-as-versioned-{org}.invalid')
        direct = subprocess.run(['git', '-C', str(root), 'push', 'origin', 'HEAD:main'], capture_output=True)
        assert direct.returncode and b'GH013' in direct.stderr
        git(root, 'push', '-q', 'origin', f'HEAD:observations/{clock}/100-2')
        git(root, 'switch', '-q', 'main')
        return root, target, hub_remote, API(root, target, hub_remote, org, clock, source, head), payload
    return make


@pytest.fixture
def shared(monkeypatch, make_estate):
    # Load only after real-Git setup exists at the call site; the original transport
    # regression above independently ran against the published six producer cages.
    module = importlib.import_module('talk.observation_delivery')
    return module


def invoke(shared, estate, monkeypatch, **kwargs):
    root, _, hub, api, _ = estate
    monkeypatch.setattr(shared, 'HUB_URL', str(hub))
    return shared.deliver(root, 100, repository=api.repo, workflow=api.clock, attempt=2,
                          authority_root=root.parent / 'hub-data', api=api,
                          verify=lambda *args: None, today=TODAY, **kwargs)


@pytest.mark.parametrize('org,clock', PROFILES)
def test_six_protected_paths_conserve_original_signed_object_bytes(shared, make_estate, monkeypatch, org, clock):
    estate = make_estate(org, clock); root, target, _, api, payload = estate
    head = api.pr['head']['sha']; before = git(root, 'cat-file', 'commit', head)
    assert invoke(shared, estate, monkeypatch).startswith('RECORDED')
    git(target, 'merge-base', '--is-ancestor', head, 'main')
    assert git(root, 'cat-file', 'commit', head) == before
    for path in payload:
        assert git(target, 'show', 'main:' + path) == git(root, 'show', head + ':' + path)
    assert api.run['conclusion'] == 'failure'


@pytest.mark.parametrize('field,value', [('head_repository', {'full_name': 'foreign/repo'}),
    ('head_branch', 'topic'), ('path', '.github/workflows/foreign.yml'), ('head_sha', '123'),
    ('status', 'in_progress'), ('event', 'pull_request'), ('run_attempt', True), ('id', 101)])
def test_wrong_official_run_stays_pending(shared, make_estate, monkeypatch, field, value):
    estate = make_estate(); estate[3].run[field] = value
    with pytest.raises(shared.Refusal): invoke(shared, estate, monkeypatch)
    assert not estate[3].approved


@pytest.mark.parametrize('plant', ['declaration', 'delete', 'symlink', 'rewrite', 'wrong-author',
                                    'wrong-run', 'wrong-source', 'extra-row', 'wrong-schema'])
def test_original_content_rejected_before_review(shared, make_estate, monkeypatch, plant):
    estate = make_estate(); root, _, _, api, _ = estate
    git(root, 'switch', '-q', 'observations/twin-sweep/100-2')
    path = root / 'observations/twin-sweep.jsonl'
    if plant == 'declaration': (root / 'policy.yaml').write_text('must never execute\n')
    elif plant == 'delete': path.unlink()
    elif plant == 'symlink': path.unlink(); path.symlink_to('../twin/PIN.yaml')
    elif plant == 'rewrite': path.write_text(path.read_text().replace('true', 'false', 1))
    else:
        lines = path.read_text().splitlines(); row = json.loads(lines[-1])
        if plant == 'wrong-run': row['run'] = '101'
        elif plant == 'wrong-source': row['adopter_ref'] = 'f' * 40
        elif plant == 'wrong-schema': row['declaration'] = 'baseline'
        elif plant == 'extra-row': lines.append(lines[-1])
        if plant != 'extra-row': lines[-1] = json.dumps(row)
        path.write_text('\n'.join(lines) + '\n')
    git(root, 'add', '-A'); git(root, '-c', f'user.email={api.clock}@policy-as-versioned-{api.org}.invalid', 'commit', '--amend', '--no-edit', '-q')
    if plant == 'wrong-author': git(root, '-c', 'user.email=foreign@example.invalid', 'commit', '--amend', '--reset-author', '--no-edit', '-q')
    api.pr['head']['sha'] = git(root, 'rev-parse', 'HEAD')
    git(root, 'push', '-q', '--force', 'origin', 'observations/twin-sweep/100-2');git(root, 'switch', '-q', 'main')
    with pytest.raises(shared.Refusal): invoke(shared, estate, monkeypatch)
    assert not api.approved


def advance(remote_root, destination, path='unrelated.md'):
    git(remote_root, 'clone', '-q', str(destination), str(remote_root / 'advance'))
    root = remote_root / 'advance'
    for key, value in [('commit.gpgsign', 'false'), ('core.hooksPath', os.devnull),
                       ('user.name', 'fixture'), ('user.email', 'fixture@example.invalid')]:
        git(root, 'config', key, value)
    (root / path).write_text('operations\n' if path == 'twin/ENACT_MODE' else 'authority changed\n')
    head = commit(root, 'reviewed authority change');(destination / 'reviewed-head').write_text(head)
    git(root, 'push', '-q', 'origin', 'main')


@pytest.mark.parametrize('when,which', [('graphql', 'hub'), ('review', 'hub'), ('graphql', 'adopter'), ('review', 'adopter')])
def test_both_fresh_authorities_rechecked_before_each_mutation(shared, make_estate, monkeypatch, when, which):
    estate = make_estate(); root, target, hub, api, _ = estate
    def change(method, path):
        if (when == 'graphql' and path == 'graphql') or (when == 'review' and path.endswith('/reviews')):
            advance(root.parent, hub if which == 'hub' else target)
    api.after = change
    with pytest.raises(shared.Refusal, match='authority|trusted checkout'):
        invoke(shared, estate, monkeypatch)
    assert api.approved == (when == 'review')
    assert not any(c[0] == 'PUT' for c in api.calls)


def test_expired_hub_window_and_preflight_without_writer(shared, make_estate, monkeypatch):
    estate = make_estate(); api = estate[3]
    assert invoke(shared, estate, monkeypatch, check_only=True).startswith('VERIFIED')
    assert all(c[0] == 'GET' for c in api.calls)
    monkeypatch.setenv('TWIN_ENACT_MODE', 'development')
    with pytest.raises(shared.Refusal, match='window'):
        shared.deliver(estate[0], 100, repository=api.repo, workflow=api.clock, attempt=2,
                       authority_root=estate[0].parent / 'hub-data', api=api, verify=lambda *a: None,
                       today=dt.date(2026, 10, 22))
    assert not api.approved


def test_wrong_pr_actor_signature_and_refused_merge(shared, make_estate, monkeypatch):
    estate = make_estate(); api = estate[3]
    api.pr['user']['login'] = 'foreign[bot]'
    with pytest.raises(shared.Refusal): invoke(shared, estate, monkeypatch)
    api.pr['user']['login'] = 'github-actions[bot]'
    def bad(*args): raise shared.Refusal('wrong signature claims')
    with pytest.raises(shared.Refusal, match='signature'):
        shared.deliver(estate[0], 100, repository=api.repo, workflow=api.clock, attempt=2,
                       authority_root=estate[0].parent / 'hub-data', api=api, verify=bad, today=TODAY)
    assert not api.approved
    api.refuse_merge = True
    with pytest.raises(shared.Refusal, match='pending'): invoke(shared, estate, monkeypatch)
    assert api.approved and not api.pr['merged']


@pytest.mark.parametrize('repo,workflow', [('attacker/repo', 'twin-sweep'), (HUB, 'twin-sweep'),
    ('policy-as-versioned-tuppence/tuppence', 'arbitrary')])
def test_inputs_cannot_create_an_authority_profile(shared, tmp_path, repo, workflow):
    with pytest.raises(shared.Refusal, match='profile'):
        shared.deliver(tmp_path, 100, repository=repo, workflow=workflow, attempt=2)


@pytest.mark.parametrize('plant', ['missing-source', 'extra-workload', 'wrong-event', 'empty-facts', 'malformed-fact'])
def test_drift_profile_requires_three_plus_one_plus_one_valid_rows(shared, make_estate, monkeypatch, plant):
    estate = make_estate('driftwood', 'drift-sample'); root, _, _, api, _ = estate
    git(root, 'switch', '-q', 'observations/drift-sample/100-2')
    path = root / ('drift/workload-samples.jsonl' if plant == 'extra-workload' else 'drift/samples.jsonl')
    lines = path.read_text().splitlines(); row = json.loads(lines[-1])
    if plant == 'missing-source': lines.pop()
    elif plant == 'extra-workload': lines.append(lines[-1])
    else:
        if plant == 'wrong-event': row['event'] = 'workflow_dispatch'
        elif plant == 'empty-facts': row['facts'] = {}
        else: row['facts'] = {'fact_1_ready_at_the_pin_on_the_real_remote': {'observed': 'true', 'why': 'invalid typed observation'}}
        lines[-1] = json.dumps(row)
    path.write_text('\n'.join(lines) + '\n')
    git(root, 'add', '-A');git(root, '-c', f'user.email={api.clock}@policy-as-versioned-{api.org}.invalid', 'commit', '--amend', '--no-edit', '-q')
    api.pr['head']['sha'] = git(root, 'rev-parse', 'HEAD')
    git(root, 'push', '-q', '--force', 'origin', 'observations/drift-sample/100-2');git(root, 'switch', '-q', 'main')
    with pytest.raises(shared.Refusal): invoke(shared, estate, monkeypatch)
    assert not api.approved


def test_changed_pr_head_after_validation_cannot_be_reviewed(shared, make_estate, monkeypatch):
    estate = make_estate(); api = estate[3]
    def change(method, path):
        if path == 'graphql': api.pr['head']['sha'] = api.run['head_sha']
    api.after = change
    with pytest.raises(shared.Refusal, match='head'): invoke(shared, estate, monkeypatch)
    assert not api.approved


def test_existing_pending_ref_head_is_compared_with_official_pr(shared, make_estate, monkeypatch):
    estate = make_estate(); root, _, _, api, _ = estate
    # A remote branch collision/race must not substitute even an ancestor object.
    git(root, 'push', '-q', '--force', 'origin', api.run['head_sha'] + ':refs/heads/observations/twin-sweep/100-2')
    with pytest.raises(shared.Refusal, match='pending ref head'): invoke(shared, estate, monkeypatch)
    assert not api.approved


def test_current_hub_operations_mode_is_not_replaced_by_adopter_or_environment(shared, make_estate, monkeypatch):
    estate = make_estate(); root, _, hub, api, _ = estate
    advance(root.parent, hub, 'twin/ENACT_MODE')
    (root / 'twin/ENACT_MODE').write_text('development\n')
    monkeypatch.setenv('TWIN_ENACT_MODE', 'development')
    with pytest.raises(shared.Refusal, match='window'): invoke(shared, estate, monkeypatch)
    assert not api.approved


def test_observation_crlf_prefix_is_conserved_as_raw_bytes(shared, make_estate, monkeypatch):
    estate = make_estate(); root, target, _, api, _ = estate
    # Rebuild source/candidate with CRLF history: universal-newline conversion
    # would incorrectly let the candidate rewrite a previously signed CRLF row.
    git(root, 'switch', '-qc', 'crlf-source')
    path = root / 'observations/twin-sweep.jsonl';path.write_bytes(b'{"old":"CRLF"}\r\n')
    source = commit(root, 'fixture CRLF source')
    (target / 'reviewed-head').write_text(source);git(root, 'push', '-q', 'origin', 'HEAD:main')
    git(root, 'switch', '-q', 'main');git(root, 'merge', '--ff-only', source)
    git(root, 'switch', '-q', 'observations/twin-sweep/100-2');git(root, 'reset', '--hard', source)
    row = rows('tuppence', 'twin-sweep', source)['observations/twin-sweep.jsonl'][0]
    path.write_bytes(b'{"old":"CRLF"}\n' + (json.dumps(row) + '\n').encode())
    head = commit(root, 'twin sweep: record the emitter observation [skip ci]', 'twin-sweep@policy-as-versioned-tuppence.invalid')
    git(root, 'push', '-q', '--force', 'origin', 'HEAD:observations/twin-sweep/100-2');git(root, 'switch', '-q', 'main')
    api.run['head_sha'] = source;api.pr['head']['sha'] = head
    with pytest.raises(shared.Refusal, match='historical bytes'): invoke(shared, estate, monkeypatch)
    assert not api.approved


@pytest.mark.parametrize('org,clock', PROFILES)
@pytest.mark.parametrize('collision', ['none', 'ancestor', 'same', 'divergent', 'advertisement-race'])
def test_producer_unique_ref_is_create_only_and_original_precedes_pr(make_estate, tmp_path, org, clock, collision):
    estate = make_estate(org, clock); root, target, _, api, _ = estate
    branch = f'observations/{clock}/100-2'; original = api.pr['head']['sha']; source = api.run['head_sha']
    # Existing fixture ref represents the original failed direct push being
    # recovered; remove it before exercising the proposed producer tail.
    git(target, 'update-ref', '-d', 'refs/heads/' + branch)
    if collision in {'ancestor', 'same', 'divergent'}:
        existing = source if collision == 'ancestor' else original
        if collision == 'divergent':
            git(root, 'switch', '-qc', 'collision', source)
            (root / 'unrelated').write_text('existing branch\n');existing = commit(root, 'existing divergent observation')
        git(root, 'push', '-q', 'origin', existing + ':refs/heads/' + branch)
    elif collision == 'advertisement-race':
        # receive-pack creates the ancestor ref before advertising it; only an
        # absence lease, rather than ls-remote or ordinary FF push, refuses it.
        wrapper = tmp_path / 'receive-pack'
        wrapper.write_text('#!/bin/sh\ngit -C "$1" update-ref ' + 'refs/heads/' + branch + ' ' + source + '\nexec git-receive-pack "$@"\n')
        wrapper.chmod(0o755)
        git(root, 'config', 'remote.origin.receivepack', str(wrapper))
    git(root, 'switch', '-q', 'main')
    git(root, 'reset', '--hard', original)
    tools = tmp_path / 'fixture-bin';tools.mkdir()
    gh = tools / 'gh';gh.write_text('#!/bin/sh\nset -eu\n'
        + 'test "$(git --git-dir=' + str(target) + ' rev-parse refs/heads/' + branch + ')" = "' + original + '"\n'
        + 'printf "%s\\n" "$*" > ' + str(tmp_path / 'pr-called') + '\n');gh.chmod(0o755)
    tail = Path(__file__).resolve().parents[1] / 'talk/observation-delivery-producer.sh'
    env = dict(os.environ, PATH=str(tools) + os.pathsep + os.environ['PATH'], DEFAULT_BRANCH='main',
               OBSERVATION_CLOCK=clock, GITHUB_RUN_ID='100', GITHUB_RUN_ATTEMPT='2', GITHUB_REF_NAME='main',
               GITHUB_REPOSITORY=api.repo, RUNNER_TEMP=str(tmp_path), GH_TOKEN='synthetic-no-permission')
    result = subprocess.run(['bash', str(tail)], cwd=root, env=env, capture_output=True)
    before = source
    assert git(target, 'rev-parse', 'main') == before
    assert git(root, 'rev-parse', 'HEAD') == original
    if collision == 'none':
        assert result.returncode == 0 and b'PENDING' in result.stdout
        assert git(target, 'rev-parse', 'refs/heads/' + branch) == original
        assert (tmp_path / 'pr-called').exists()
    else:
        assert result.returncode
        assert (b'stale info' in result.stderr if collision == 'advertisement-race' else b'already exists' in result.stdout)
        assert not (tmp_path / 'pr-called').exists()
        expected = original if collision == 'same' else existing if collision == 'divergent' else source
        assert git(target, 'rev-parse', 'refs/heads/' + branch) == expected


def test_recorded_proof_rejects_a_duplicate_individual_source_row(shared, make_estate, monkeypatch):
    estate = make_estate('driftwood', 'drift-sample'); root, target, _, api, _ = estate
    assert invoke(shared, estate, monkeypatch).startswith('RECORDED')
    head = api.pr['head']['sha'];parent = git(root, 'rev-parse', head + '^')
    evidence = {path: (shared.git(root, 'show', parent + ':' + path, check=False),
                       json.dumps(records[0], sort_keys=True) + '\n' if len(records) == 1 else
                       ''.join(json.dumps(row, sort_keys=True) + '\n' for row in records))
                for path, records in estate[4].items()}
    # This intentionally corrupts only fixture main after the normal merge. The
    # original object/merge stay ancestors, so ancestry alone cannot prove once.
    checkout = root.parent / 'duplicate-row';git(root, 'clone', '-q', str(target), str(checkout))
    for key, value in [('commit.gpgsign', 'false'), ('core.hooksPath', os.devnull),
                       ('user.name', 'fixture'), ('user.email', 'fixture@example.invalid')]:
        git(checkout, 'config', key, value)
    path = checkout / 'drift/samples.jsonl'
    with path.open('a') as stream: stream.write(evidence['drift/samples.jsonl'][1].splitlines(keepends=True)[0])
    commit(checkout, 'fixture duplicate row after delivery');git(checkout, 'push', '-q', 'origin', 'main')
    with pytest.raises(shared.Refusal, match='conserve'):
        shared.recorded(root, api.pr, head, evidence, 'main')


@pytest.mark.parametrize('status,code,moved', [('unchanged', 3, False), ('review_required', 0, True), ('could_not_look', 3, True)])
def test_emitter_status_exit_and_moved_are_one_reading(shared, make_estate, monkeypatch, status, code, moved):
    estate = make_estate(); root, _, _, api, _ = estate
    git(root, 'switch', '-q', 'observations/twin-sweep/100-2')
    path = root / 'observations/twin-sweep.jsonl';lines = path.read_text().splitlines()
    row = json.loads(lines[-1]);row.update(status=status, emitter_exit=code, moved=moved)
    lines[-1] = json.dumps(row);path.write_text('\n'.join(lines) + '\n')
    git(root, 'add', '-A')
    git(root, '-c', 'user.email=twin-sweep@policy-as-versioned-tuppence.invalid', 'commit', '--amend', '--no-edit', '-q')
    api.pr['head']['sha'] = git(root, 'rev-parse', 'HEAD')
    git(root, 'push', '-q', '--force', 'origin', 'observations/twin-sweep/100-2');git(root, 'switch', '-q', 'main')
    with pytest.raises(shared.Refusal): invoke(shared, estate, monkeypatch)
    assert not api.approved
