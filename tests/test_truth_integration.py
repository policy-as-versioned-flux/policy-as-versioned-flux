"""Trusted workflow delivery over real protected Git; API/signing adapters are synthetic.

No fixture can establish real GitHub authorization or certificate issuance. The
workflow seam preserves the original red clock and separately reviews integration.
"""
from __future__ import annotations

import copy
import datetime as dt
import json
import os
from pathlib import Path
import subprocess
from urllib.parse import parse_qs, urlsplit

import pytest
import yaml

from test_truth_delivery import FixtureAPI, git
from talk import observation_delivery as controller

ROOT = Path(__file__).resolve().parents[1]
REPO = controller.REPOSITORY
TODAY = dt.date(2026, 10, 17)


class IntegrationAPI(FixtureAPI):
    def __init__(self, root, remote, run, head):
        super().__init__(root, remote, run, head)
        self.prs = {4: self.pr}
        self.reviewed = []
        self.on_call = None

    def __call__(self, method, path, body=None):
        if self.on_call:
            self.on_call(method, path, body)
        if '/pulls?' in path:
            self.calls.append((method, path, body))
            branch = parse_qs(urlsplit(path).query)['head'][0].split(':', 1)[1]
            return [copy.deepcopy(p) for p in self.prs.values() if p['head']['ref'] == branch]
        if '/git/matching-refs/heads/' in path:
            self.calls.append((method, path, body))
            prefix = path.split('/git/matching-refs/heads/', 1)[1]
            refs = git(self.remote, 'for-each-ref', '--format=%(refname) %(objectname)', 'refs/heads/' + prefix)
            return [{'ref': ref, 'object': {'sha': sha}} for ref, sha in (r.split() for r in refs.splitlines())]
        if path == f'repos/{REPO}/pulls' and method == 'POST':
            self.calls.append((method, path, copy.deepcopy(body)))
            head = git(self.remote, 'rev-parse', 'refs/heads/' + body['head'])
            number = 4 + len(self.prs)
            pr = copy.deepcopy(self.pr)
            pr.update(number=number, state='open', merged=False,
                      head={'sha': head, 'ref': body['head'], 'repo': {'full_name': REPO}})
            self.prs[number] = pr
            return copy.deepcopy(pr)
        if '/pulls/' in path:
            number = int(path.split('/pulls/', 1)[1].split('/', 1)[0])
            self.pr = self.prs[number]
            suffix = path.split(str(number), 1)[1]
            # Reuse the real protected-remote merge adapter at its existing endpoint.
            value = super().__call__(method, f'repos/{REPO}/pulls/4' + suffix, body)
            if method == 'POST' and suffix == '/reviews':
                self.reviewed.append(body['commit_id'])
            self.pr['number'] = number
            return value
        return super().__call__(method, path, body)


@pytest.fixture
def conflict(tmp_path, monkeypatch, request):
    root, remote = tmp_path / 'trusted', tmp_path / 'protected.git'
    root.mkdir()
    git(root, 'init', '-q', '-b', 'main')
    for key, value in [('commit.gpgsign', 'false'), ('core.hooksPath', os.devnull),
                       ('user.name', 'explicit synthetic fixture'), ('user.email', 'fixture@example.invalid')]:
        git(root, 'config', key, value)
    for path, data in {
        '.github/workflows/truth.yml': 'env:\n  OBSERVATION_LANE: "talk/truth.log talk/captures"\n',
        'talk/truth.log': 'TRUTH historical prefix\n', 'talk/captures/gate.out': 'old capture\n',
        'talk/captures/inherited.out': 'signed inherited capture\n',
        'policy.yaml': 'must remain current\n', 'twin/ENACT_MODE': 'development\n',
        'owner.md': '2026-09-24, owner: "agree".\n',
        'twin/ENACT_MODE.why': "mode: development\nuntil: '2026-10-22'\nsaid:\n  - on: '2026-09-24'\n    by: owner\n    words: agree\n    where: owner.md\n",
    }.items():
        out = root / path; out.parent.mkdir(parents=True, exist_ok=True); out.write_text(data)
    git(root, 'add', '.'); git(root, 'commit', '-qm', 'measured synthetic source')
    source = git(root, 'rev-parse', 'HEAD')
    git(root, 'init', '-q', '--bare', '-b', 'main', str(remote))
    git(root, 'remote', 'add', 'origin', str(remote)); git(root, 'push', '-q', 'origin', 'main')
    git(root, 'switch', '-qc', 'observations/truth/100-2')
    line = f'TRUTH 2026-10-17T05:47Z run=418 hub={source[:8]} fail=11\n'
    (root / 'talk/truth.log').write_text('TRUTH historical prefix\n' + line)
    (root / 'talk/captures/gate.out').write_bytes(b'authentic fixture capture\x00\xff\n')
    git(root, 'add', '.'); git(root, '-c', 'user.email=truth@users.noreply.github.com',
        'commit', '-qm', 'truth: record run 418 [skip ci]')
    original = git(root, 'rev-parse', 'HEAD')
    git(root, 'push', '-q', 'origin', 'HEAD:observations/truth/100-2')
    git(root, 'switch', '-q', 'main')
    kind = getattr(request, 'param', 'conflict')
    (root / 'talk/truth.log').write_text('TRUTH historical prefix\n' +
                                       ('' if kind.startswith('clean-') else 'TRUTH concurrent run416\n'))
    (root / 'talk/captures/gate.out').write_text('old capture\n' if kind.startswith('clean-')
                                               else 'newer concurrent capture\n')
    if kind == 'clean-mixed':
        (root / 'talk/captures/inherited.out').write_text('concurrent later capture\n')
    (root / 'talk/captures/new-only.out').write_text('preserve this base-only file\n')
    (root / 'policy.yaml').write_text('current reviewed declaration\n')
    git(root, 'add', '.'); git(root, 'commit', '-qm', 'concurrent reviewed record and declaration')
    base = git(root, 'rev-parse', 'HEAD'); git(root, 'push', '-q', 'origin', 'main')
    git(remote, 'config', 'core.hooksPath', str(remote / 'hooks'))
    hook = remote / 'hooks/update'
    hook.write_text('#!/bin/sh\nif [ "$1" = refs/heads/main ]; then\n'
                    ' test -f reviewed-head || exit 1\n'
                    ' git merge-base --is-ancestor "$(cat reviewed-head)" "$3" || exit 1\nfi\n')
    hook.chmod(0o755)
    run = dict(id=100, run_number=418, run_attempt=2, workflow_id=9, path='.github/workflows/truth.yml',
               head_sha=source, head_branch='main', event='push', status='completed', conclusion='failure',
               repository={'full_name': REPO}, head_repository={'full_name': REPO})
    api = IntegrationAPI(root, remote, run, original)
    monkeypatch.delenv('GH_TOKEN', raising=False); monkeypatch.delenv('GITHUB_TOKEN', raising=False)
    return root, remote, api, original, base, line


def invoke(estate, **options):
    root, _, api, _, _, _ = estate
    return controller.deliver(root, 100, attempt=2, api=api, verify=lambda *a: None, today=TODAY, **options)


def workflow(estate):
    """Run the trusted workflow's configured preparation and review phases."""
    doc = yaml.safe_load((ROOT / '.github/workflows/truth-delivery.yml').read_text())
    if 'prepare' in doc['jobs']:
        root, _, api, _, _, _ = estate
        controller.prepare_truth(root, 100, attempt=2, api=api, verify=lambda *a: None, today=TODAY)
        return invoke(estate, review_integration=True)
    return invoke(estate)


def test_workflow_records_conflicting_original_through_distinct_review(conflict):
    root, remote, api, raw, base, line = conflict
    before = subprocess.run(['git', '-C', str(root), 'cat-file', 'commit', raw], check=True, capture_output=True).stdout
    assert workflow(conflict).startswith('RECORDED')
    assert git(remote, 'show', 'main:talk/truth.log') == 'TRUTH historical prefix\nTRUTH concurrent run416\n' + line.strip()
    assert git(remote, 'show', 'main:policy.yaml') == 'current reviewed declaration'
    assert git(remote, 'show', 'main:talk/captures/new-only.out') == 'preserve this base-only file'
    assert git(remote, 'rev-parse', 'main:talk/captures/gate.out') == git(root, 'rev-parse', raw + ':talk/captures/gate.out')
    assert git(remote, 'rev-parse', 'observations/truth/100-2') == raw
    assert git(remote, 'merge-base', '--is-ancestor', raw, 'main') == ''
    assert subprocess.run(['git', '-C', str(root), 'cat-file', 'commit', raw], check=True, capture_output=True).stdout == before
    integration = next(p for n, p in api.prs.items() if n != 4)
    assert integration['user']['login'] == 'github-actions[bot]'
    assert api.reviewed == [integration['head']['sha']] and api.reviewed[0] != raw
    assert git(root, 'show', '-s', '--format=%P', api.reviewed[0]).split() == [base, raw]
    assert api.prs[4]['state'] == 'open' and not api.prs[4]['merged']
    assert api.run['conclusion'] == 'failure'


def prepare(estate):
    root, _, api, _, _, _ = estate
    return controller.prepare_truth(root, 100, attempt=2, api=api, verify=lambda *a: None, today=TODAY)


def refresh(estate):
    root = estate[0]
    git(root, 'fetch', '-q', 'origin', 'main')
    git(root, 'merge', '-q', '--ff-only', 'origin/main')


def plant_ref(root, remote, ref, head):
    """An explicit external writer installs a fixture object, never a production push."""
    git(remote, 'fetch', '-q', str(root), head)
    git(remote, 'update-ref', ref, head)


@pytest.mark.parametrize('raw_marked_merged', [False, True])
def test_preparation_reuses_exact_candidate_and_recording_is_idempotent(conflict, raw_marked_merged):
    root, remote, api, raw, base, _ = conflict
    assert prepare(conflict).startswith('PREPARED')
    refs = git(remote, 'for-each-ref', '--format=%(refname) %(objectname)')
    assert prepare(conflict).startswith('PREPARED')
    assert git(remote, 'for-each-ref', '--format=%(refname) %(objectname)') == refs
    assert not api.reviewed
    assert len([p for p in api.prs if p != 4]) == 1
    assert invoke(conflict, review_integration=True).startswith('RECORDED')
    if raw_marked_merged:
        api.prs[4].update(merged=True, state='closed', merge_commit_sha=api.prs[5]['merge_commit_sha'])
    refresh(conflict)
    writes = len([c for c in api.calls if c[0] != 'GET'])
    assert prepare(conflict).startswith('RECORDED')
    assert invoke(conflict, review_integration=True).startswith('RECORDED')
    assert len([c for c in api.calls if c[0] != 'GET']) == writes
    assert git(remote, 'rev-parse', 'observations/truth/100-2') == raw


@pytest.mark.parametrize('plant', ['tree', 'parents', 'actor', 'raw-ref', 'declaration'])
def test_untrusted_candidate_and_original_never_receive_approval(conflict, plant):
    root, remote, api, raw, base, _ = conflict
    if plant == 'declaration':
        git(root, 'switch', '-q', '--detach', raw)
        (root / 'policy.yaml').write_text('clock declaration attack\n')
        git(root, 'add', 'policy.yaml'); git(root, '-c', 'user.email=truth@users.noreply.github.com',
                                           'commit', '--amend', '--no-edit', '-q')
        changed = git(root, 'rev-parse', 'HEAD')
        api.prs[4]['head']['sha'] = changed
        plant_ref(root, remote, 'refs/heads/observations/truth/100-2', changed)
        git(root, 'update-ref', 'refs/remotes/origin/observations/truth/100-2', changed)
        git(root, 'switch', '-q', 'main')
        with pytest.raises(controller.Refusal, match='declaration'):
            prepare(conflict)
    else:
        prepare(conflict)
        pr = api.prs[5]
        if plant == 'actor':
            pr['user'] = {'login': 'pavc-other-hand[bot]'}
        elif plant == 'raw-ref':
            git(remote, 'update-ref', 'refs/heads/observations/truth/100-2', base)
        else:
            tree = git(root, 'rev-parse', (base if plant == 'tree' else pr['head']['sha']) + '^{tree}')
            parents = ['-p', base] + ([] if plant == 'parents' else ['-p', raw])
            changed = git(root, '-c', 'user.name=observation delivery',
                          '-c', 'user.email=observation-delivery@users.noreply.github.com',
                          'commit-tree', tree, *parents, '--no-gpg-sign', '-m', 'synthetic candidate attack')
            plant_ref(root, remote, 'refs/heads/' + pr['head']['ref'], changed)
            pr['head']['sha'] = changed
        with pytest.raises((controller.Refusal, ValueError)):
            invoke(conflict, review_integration=True)
    assert not api.reviewed
    assert git(remote, 'rev-parse', 'main') == base


def test_occupied_candidate_ref_is_not_advanced(conflict):
    root, remote, api, raw, base, _ = conflict
    ref = f'refs/heads/integrations/truth/100-2/{base}'
    git(remote, 'update-ref', ref, raw)
    with pytest.raises(ValueError, match='parents'):
        prepare(conflict)
    assert git(remote, 'rev-parse', ref) == raw
    assert not api.reviewed and len(api.prs) == 1


def advance(conflict, text='after preparation\n'):
    root, remote, _, _, base, _ = conflict
    tree = git(root, 'rev-parse', base + '^{tree}')
    changed = git(root, 'commit-tree', tree, '-p', base, '--no-gpg-sign', '-m', text)
    plant_ref(root, remote, 'refs/heads/main', changed)


@pytest.mark.parametrize('when', ['before-review', 'after-approval', 'fresh-checkout'])
def test_default_races_cannot_review_or_merge_a_stale_integration(conflict, when):
    _, remote, api, raw, _, _ = conflict
    prepare(conflict)
    if when == 'after-approval':
        def race(method, path, body):
            if method == 'POST' and path.endswith('/reviews'):
                advance(conflict)
        api.on_call = race
    else:
        advance(conflict)
        if when == 'fresh-checkout':
            refresh(conflict)
    with pytest.raises(controller.Refusal, match='trusted checkout|fresh integration'):
        invoke(conflict, review_integration=True)
    assert not api.prs[5]['merged']
    if when != 'after-approval':
        assert not api.reviewed
    assert git(remote, 'rev-parse', 'observations/truth/100-2') == raw


@pytest.mark.parametrize('raw_marked_merged', [False, True])
def test_default_race_after_last_guard_never_claims_an_unexpected_merge_recorded(conflict, raw_marked_merged):
    root, remote, api, raw, base, _ = conflict
    prepare(conflict)
    def race(method, path, body):
        if method == 'PUT' and path.endswith('/merge'):
            advance(conflict, 'concurrent default after the last guard')
    api.on_call = race
    with pytest.raises(controller.Refusal, match='merge did not conserve'):
        invoke(conflict, review_integration=True)
    # The real local merge happened; a head-pinned server API cannot pin its base.
    # Its unexpected first parent must yield PENDING, never a RECORDED receipt.
    assert api.prs[5]['merged'] and api.prs[5]['merge_commit_sha'] == git(remote, 'rev-parse', 'main')
    assert git(remote, 'show', '-s', '--format=%P', 'main').split()[0] != base
    assert git(remote, 'merge-base', '--is-ancestor', raw, 'main') == ''
    assert git(remote, 'rev-parse', 'observations/truth/100-2') == raw
    refresh(conflict)
    api.on_call = None
    if raw_marked_merged:
        api.prs[4].update(merged=True, state='closed', merge_commit_sha=api.prs[5]['merge_commit_sha'])
    with pytest.raises(controller.Refusal, match='merge did not conserve'):
        prepare(conflict)
    with pytest.raises(controller.Refusal, match='merge did not conserve'):
        invoke(conflict, review_integration=True)


@pytest.mark.parametrize('plant', ['duplicate', 'rewrite'])
def test_duplicate_or_rewritten_default_log_stays_pending(conflict, plant):
    root, remote, api, raw, _, line = conflict
    path = root / 'talk/truth.log'
    path.write_text(path.read_text() + line if plant == 'duplicate' else 'rewritten prefix\n')
    git(root, 'add', 'talk/truth.log'); git(root, 'commit', '-qm', 'synthetic log attack')
    plant_ref(root, remote, 'refs/heads/main', git(root, 'rev-parse', 'HEAD'))
    with pytest.raises(ValueError, match='duplicated|rewrote'):
        prepare(conflict)
    assert not api.reviewed and len(api.prs) == 1


def test_create_only_publication_loses_a_race_without_replacing_the_ref(conflict):
    _, remote, api, raw, base, _ = conflict
    ref = f'refs/heads/integrations/truth/100-2/{base}'
    def race(method, path, body):
        if '/git/matching-refs/' in path:
            # The API read reports absence, then another writer occupies the ref.
            api.on_call = None
            git(remote, 'update-ref', ref, raw)
            return
    # Create the race after absence has been observed by the API adapter.
    original_call = api.__call__
    def transport(method, path, body=None):
        value = original_call(method, path, body)
        race(method, path, body)
        return value
    with pytest.raises(controller.Refusal, match='create-only'):
        controller.prepare_truth(conflict[0], 100, attempt=2, api=transport,
                                 verify=lambda *a: None, today=TODAY)
    assert git(remote, 'rev-parse', ref) == raw
    assert not api.reviewed and len(api.prs) == 1


def test_workflow_uses_separate_narrow_preparer_and_secret_reviewer():
    doc = yaml.safe_load((ROOT / '.github/workflows/truth-delivery.yml').read_text())
    prepare_job, review_job = doc['jobs']['prepare'], doc['jobs']['review']
    assert prepare_job['permissions'] == {'contents': 'write', 'actions': 'read', 'pull-requests': 'write'}
    assert 'environment' not in prepare_job and 'secrets.' not in json.dumps(prepare_job)
    assert 'id-token' not in prepare_job['permissions']
    assert review_job['needs'] == 'prepare' and review_job['environment'] == 'truth-delivery'
    assert doc['permissions'] == {'contents': 'read', 'actions': 'read', 'pull-requests': 'read'}
    for job in [prepare_job, review_job]:
        checkout = job['steps'][0]['with']
        assert checkout['ref'] == '${{ github.event.repository.default_branch }}'
        assert checkout['persist-credentials'] is False and checkout['fetch-depth'] == 0
    assert '--prepare-integration' in prepare_job['steps'][-1]['run']
    assert '--review-integration' in review_job['steps'][-1]['run']


def test_even_a_clean_merge_cannot_adopt_a_manually_duplicated_run(conflict):
    root, remote, api, raw, _, line = conflict
    (root / 'talk/truth.log').write_text(git(root, 'show', raw + ':talk/truth.log') + '\n')
    data = subprocess.run(['git', '-C', str(root), 'show', raw + ':talk/captures/gate.out'],
                          check=True, capture_output=True).stdout
    (root / 'talk/captures/gate.out').write_bytes(data)
    git(root, 'add', '.'); git(root, 'commit', '-qm', 'copy original bytes without original ancestry')
    base = git(root, 'rev-parse', 'HEAD'); plant_ref(root, remote, 'refs/heads/main', base)
    assert controller.truth_integration.mergeable(root, base, raw)
    with pytest.raises(ValueError, match='duplicated'):
        prepare(conflict)
    assert not api.reviewed and len(api.prs) == 1


def test_integration_verifier_pins_the_real_workflow_name_as_seventh_claim(conflict, monkeypatch):
    root, _, api, raw, _, _ = conflict
    commands = []
    def instrument(command, **options):
        commands.append(command)
        return subprocess.CompletedProcess(command, 1)
    monkeypatch.setattr(controller.subprocess, 'run', instrument)
    with pytest.raises(controller.Refusal, match='signature'):
        controller.verify_signature(root, raw, api.run, 'main', require_name=True)
    assert len(commands) == 1
    assert commands[0] == ['gitsign', 'verify', raw,
        f'--certificate-identity=https://github.com/{REPO}/.github/workflows/truth.yml@refs/heads/main',
        '--certificate-oidc-issuer=https://token.actions.githubusercontent.com',
        f'--certificate-github-workflow-sha={api.run["head_sha"]}',
        f'--certificate-github-workflow-repository={REPO}',
        '--certificate-github-workflow-ref=refs/heads/main',
        '--certificate-github-workflow-trigger=push', '--certificate-github-workflow-name=truth']


@pytest.mark.parametrize('conflict', ['clean-identical', 'clean-mixed'], indirect=True)
def test_clean_fastpath_requires_the_complete_signed_capture_snapshot(conflict):
    root, remote, api, raw, base, line = conflict
    assert controller.truth_integration.mergeable(root, base, raw)
    expected = controller.truth_integration.plan(root, base, raw, line, 100, 2)
    identical = git(root, 'rev-parse', raw + ':talk/captures/inherited.out') == git(root, 'rev-parse', base + ':talk/captures/inherited.out')
    assert prepare(conflict).startswith('READY' if identical else 'PREPARED')
    assert invoke(conflict, review_integration=True).startswith('RECORDED')
    assert git(remote, 'rev-parse', 'main^{tree}') == expected.tree
    assert git(remote, 'rev-parse', 'main:talk/captures/inherited.out') == git(root, 'rev-parse', raw + ':talk/captures/inherited.out')
    assert len(api.prs) == (1 if identical else 2)
    refresh(conflict)
    # A genuine later default update must not invalidate the historical receipt.
    (root / 'talk/captures/inherited.out').write_text('legitimate later snapshot\n')
    git(root, 'add', 'talk/captures/inherited.out'); git(root, 'commit', '-qm', 'later reviewed capture snapshot')
    plant_ref(root, remote, 'refs/heads/main', git(root, 'rev-parse', 'HEAD'))
    assert prepare(conflict).startswith('RECORDED')
    assert invoke(conflict, review_integration=True).startswith('RECORDED')


@pytest.mark.parametrize('conflict', ['clean-mixed'], indirect=True)
def test_legacy_raw_merged_metadata_cannot_hide_a_mixed_historical_capture(conflict):
    _, _, api, _, _, _ = conflict
    # The unchanged legacy call reproduces the actual pre-fix mixed snapshot.
    assert invoke(conflict).startswith('RECORDED')
    assert api.prs[4]['merged']
    refresh(conflict)
    with pytest.raises(controller.Refusal, match='merge did not conserve'):
        prepare(conflict)
    with pytest.raises(controller.Refusal, match='merge did not conserve'):
        invoke(conflict, review_integration=True)


def test_custom_header_cannot_impersonate_the_actual_delivery_author(conflict):
    root, remote, api, _, _, _ = conflict
    prepare(conflict)
    pr = api.prs[5]
    data = subprocess.run(['git', '-C', str(root), 'cat-file', 'commit', pr['head']['sha']],
                          check=True, capture_output=True).stdout
    headers, message = data.split(b'\n\n', 1)
    headers = headers.replace(b'author observation delivery <observation-delivery@users.noreply.github.com>',
                              b'author truth surface <truth@users.noreply.github.com>')
    headers += b'\nx-author author observation delivery <observation-delivery@users.noreply.github.com>'
    changed = subprocess.run(['git', '-C', str(root), 'hash-object', '-t', 'commit', '-w', '--stdin'],
                             input=headers + b'\n\n' + message, check=True, capture_output=True).stdout.decode().strip()
    plant_ref(root, remote, 'refs/heads/' + pr['head']['ref'], changed)
    pr['head']['sha'] = changed
    with pytest.raises(ValueError, match='non-measurement'):
        invoke(conflict, review_integration=True)
    assert not api.reviewed
