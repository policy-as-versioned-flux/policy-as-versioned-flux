"""Exact genuine Git data at observation(); API/authority/signature seams are fixtures.

No pending program is checked out or run. No certificate, public permission,
runtime admission, price or new outcome is established by these tests.
"""
from __future__ import annotations

import copy
import hashlib
import json
import os
from pathlib import Path
import subprocess

import pytest

from talk import observation_delivery as delivery

FIXTURE = Path(__file__).parent / 'fixtures/tu-observation-cloud'
META = json.loads((FIXTURE / 'metadata.json').read_text())
ORIGINAL, PARENT = META['original'], META['parent']
COMPOSITION = META['selected_composition']
BRANCH = 'observations/drift-sample/39031806150-1'
PROFILE = delivery.select_profile('policy-as-versioned-tuppence/tuppence', 'drift-sample')


def git(root, *args, data=None):
    return subprocess.run(['git', '--no-replace-objects', '-C', str(root), *args],
                          input=data, capture_output=True, check=True).stdout


@pytest.fixture
def genuine_objects(tmp_path):
    pack = (FIXTURE / 'objects.pack').read_bytes()
    assert hashlib.sha256(pack).hexdigest() == META['sha256']
    origin, root = tmp_path / 'fixture-origin.git', tmp_path / 'reader'
    for repo, bare in ((origin, True), (root, False)):
        repo.mkdir()
        git(repo, 'init', '-q', '-b', 'main', *(['--bare'] if bare else []))
        git(repo, 'config', 'core.hooksPath', os.devnull)
        git(repo, 'config', 'commit.gpgsign', 'false')
        git(repo, 'unpack-objects', '-q', data=pack)
        directory = repo if bare else repo / '.git'
        # The exact objects form a deliberately bounded fixture, not a canonical public clone.
        (directory / 'shallow').write_text(PARENT + '\n' + COMPOSITION + '\n')
        git(repo, 'update-ref', 'refs/heads/main', PARENT)
        git(repo, 'update-ref', 'refs/heads/' + BRANCH, ORIGINAL)
    git(root, 'remote', 'add', 'origin', str(origin))
    git(root, 'config', 'protocol.file.allow', 'always')
    workflow = root / PROFILE.workflow
    workflow.parent.mkdir(parents=True)
    workflow.write_bytes(git(root, 'show', PARENT + ':' + PROFILE.workflow))
    return root


def evidence(root):
    rows = {}
    for path in PROFILE.lanes:
        before = git(root, 'show', PARENT + ':' + path).decode()
        after = git(root, 'show', ORIGINAL + ':' + path).decode()
        rows[path] = before, delivery.appended(before, after)
    return rows


def prospective_cloud_1_0_1(genuine_objects, monkeypatch):
    """Labelled read adapter, not rewritten signed objects or a live observation.

    The component bytes in the genuine fixture are also the exact published
    cloud1.0.1 mapping. Only the prospective package/header/path view changes.
    """
    root = genuine_objects
    original_git = delivery.git
    old_parent = json.loads(original_git(root, 'show', COMPOSITION + ':composed/CLOUD-PARENT.json'))
    component = original_git(root, 'show', COMPOSITION + ':composed/cloud/v1.0.0/component-definition.json')
    assert hashlib.sha256(component.encode()).hexdigest() == 'cd47fc4a876cf884e8be5931c06366e88b240dcdaf7274ffcac49fb688e3c619'
    cloud = dict(old_parent, version='1.0.1', tag='cloud/v1.0.1',
                 sha='995a281ae9778bafa3a2f1f8600254f8f3e7eabb')
    path = 'composed/cloud/v1.0.1/component-definition.json'
    view = {COMPOSITION + ':composed/CLOUD-PARENT.json': json.dumps(cloud),
            COMPOSITION + ':composed/HEADER.yaml': json.dumps({'cloud-package': cloud}),
            COMPOSITION + ':' + path: component}

    def read(repo, *args):
        if repo == root and len(args) == 2 and args[0] == 'show' and args[1] in view:
            return view[args[1]]
        return original_git(repo, *args)

    monkeypatch.setattr(delivery, 'git', read)
    sources = [{'party': 'platform', 'name': 'cloud', 'tag': 'cloud/v1.0.1',
                'sha': cloud['sha'], 'composed_tag': 'v4.1.1', 'component_definition': path}]
    return sources, view, COMPOSITION + ':' + path


def test_published_cloud_mapping_version_is_independent_of_package(genuine_objects, monkeypatch):
    sources, _, _ = prospective_cloud_1_0_1(genuine_objects, monkeypatch)
    delivery.validate_cloud_sources(genuine_objects, PARENT, sources)


@pytest.mark.parametrize('version', ['mapping-revision-A', '1.0.0'])
def test_document_content_revision_need_not_be_package_semver(genuine_objects, monkeypatch, version):
    sources, view, path = prospective_cloud_1_0_1(genuine_objects, monkeypatch)
    component = json.loads(view[path])
    component['component-definition']['metadata']['version'] = version
    view[path] = json.dumps(component)
    delivery.validate_cloud_sources(genuine_objects, PARENT, sources)


@pytest.mark.parametrize('version', [None, False, 0, [], {}, '', ' \t\n'])
def test_malformed_document_revision_remains_refused(genuine_objects, monkeypatch, version):
    sources, view, path = prospective_cloud_1_0_1(genuine_objects, monkeypatch)
    component = json.loads(view[path])
    component['component-definition']['metadata']['version'] = version
    view[path] = json.dumps(component)
    with pytest.raises(delivery.Refusal, match='nonblank document version'):
        delivery.validate_cloud_sources(genuine_objects, PARENT, sources)


def test_missing_document_revision_remains_refused(genuine_objects, monkeypatch):
    sources, view, path = prospective_cloud_1_0_1(genuine_objects, monkeypatch)
    component = json.loads(view[path])
    del component['component-definition']['metadata']['version']
    view[path] = json.dumps(component)
    with pytest.raises(delivery.Refusal, match='nonblank document version'):
        delivery.validate_cloud_sources(genuine_objects, PARENT, sources)


def test_genuine_original_crosses_observation_without_rewriting_parent_or_blobs(genuine_objects, monkeypatch):
    root = genuine_objects
    before = git(root, 'cat-file', 'commit', ORIGINAL)
    assert b'gpgsig -----BEGIN SIGNED MESSAGE-----' in before
    checked = []

    def frozen_api(method, path, body=None):
        assert method == 'GET' and body is None
        if path == 'repos/' + PROFILE.repository:
            return {'full_name': PROFILE.repository, 'default_branch': 'main'}
        if path.endswith('/actions/runs/39031806150/attempts/1'):
            return copy.deepcopy(META['run'])
        if path.endswith('/actions/workflows/drift-sample.yml'):
            return {'id': META['run']['workflow_id'], 'path': PROFILE.workflow}
        if '/pulls?' in path:
            return [copy.deepcopy(META['pr'])]
        if path.endswith('/pulls/74'):
            return copy.deepcopy(META['pr'])
        raise AssertionError('unexpected fixture API request: ' + path)

    def labelled_signature_boundary(repo, original, run, default):
        # Deliberately not crypto verification. Production verify_signature is untouched.
        assert repo == root and original == ORIGINAL and run == META['run'] and default == 'main'
        checked.append(original)

    monkeypatch.setattr(delivery, 'delivery_authority', lambda *args, **kwargs: lambda: None)
    pending = delivery.pending(root, 39031806150, 1, PROFILE, frozen_api,
                               labelled_signature_boundary, None)
    assert checked == [ORIGINAL]
    assert pending.original == ORIGINAL
    assert pending.line == evidence(root)
    assert git(root, 'cat-file', 'commit', ORIGINAL) == before
    assert git(root, 'rev-parse', ORIGINAL + '^').decode().strip() == PARENT
    for path in PROFILE.lanes:
        assert git(root, 'hash-object', '--stdin', data=git(root, 'show', ORIGINAL + ':' + path)).decode().strip() == \
            git(root, 'rev-parse', ORIGINAL + ':' + path).decode().strip()


def replace_sources(rows, value):
    result = copy.deepcopy(rows)
    prefix, suffix = result['drift/oscal-samples.jsonl']
    row = json.loads(suffix)
    row['cloud_component_sources'] = value
    result['drift/oscal-samples.jsonl'] = prefix, json.dumps(row, sort_keys=True) + '\n'
    return result


@pytest.mark.parametrize('field,value', [
    ('party', 'foreign'), ('name', 'other-package'), ('tag', 'cloud/v9.0.0'),
    ('sha', 'f' * 40), ('composed_tag', 'v9.0.0'),
    ('component_definition', 'composed/cloud/v9.0.0/component-definition.json'),
    ('unknown', 'unexpected')])
def test_each_provenance_field_is_bound_to_the_selected_immutable_source(genuine_objects, field, value):
    rows = evidence(genuine_objects)
    sources = json.loads(rows['drift/oscal-samples.jsonl'][1])['cloud_component_sources']
    sources[0][field] = value
    with pytest.raises(delivery.Refusal, match='cloud component'):
        delivery.validate_payload(genuine_objects, PARENT, META['run'], PROFILE, replace_sources(rows, sources))


@pytest.mark.parametrize('value', [None, {}, 'not a list', [], [None], [True]])
def test_malformed_or_missing_selected_cloud_source_cannot_become_valid_metadata(genuine_objects, value):
    with pytest.raises(delivery.Refusal, match='cloud component'):
        delivery.validate_payload(genuine_objects, PARENT, META['run'], PROFILE,
                                  replace_sources(evidence(genuine_objects), value))


def test_historic_absent_metadata_remains_valid_and_other_profiles_stay_closed(genuine_objects):
    rows = evidence(genuine_objects)
    prefix, suffix = rows['drift/oscal-samples.jsonl']
    row = json.loads(suffix)
    del row['cloud_component_sources']
    old = dict(rows)
    old['drift/oscal-samples.jsonl'] = prefix, json.dumps(row) + '\n'
    delivery.validate_payload(genuine_objects, PARENT, META['run'], PROFILE, old)
    # Explicitly synthetic profile substitution, never a newly observed DW/LU result.
    for org in ('driftwood', 'ludlow'):
        changed = copy.deepcopy(rows)
        prefix, suffix = changed['drift/samples.jsonl']
        samples = [json.loads(line) for line in suffix.splitlines()]
        for sample in samples:
            if sample['source'] == 'tuppence-composed':
                sample.update(source=org + '-composed', party=org)
        changed['drift/samples.jsonl'] = prefix, ''.join(json.dumps(s) + '\n' for s in samples)
        profile = delivery.select_profile(f'policy-as-versioned-{org}/{org}', 'drift-sample')
        with pytest.raises(delivery.Refusal, match='schema fields'):
            delivery.validate_payload(genuine_objects, PARENT, META['run'], profile, changed)


def test_current_tag_ref_head_and_worktree_never_select_provenance(genuine_objects):
    root = genuine_objects
    rows = evidence(root)
    sources = json.loads(rows['drift/oscal-samples.jsonl'][1])['cloud_component_sources']
    # Disposable selector poison, never a public tag or a rewritten original.
    git(root, 'update-ref', 'refs/tags/v4.1.1', PARENT)
    git(root, 'update-ref', 'refs/heads/main', COMPOSITION)
    git(root, 'update-ref', 'refs/remotes/origin/main', COMPOSITION)
    for path in ('gitops/composed/composed-set.yaml', 'composed/HEADER.yaml', 'composed/CLOUD-PARENT.json'):
        destination = root / path
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text('untrusted working-tree fixture')
    delivery.validate_cloud_sources(root, PARENT, sources)


def test_missing_selected_object_refuses_instead_of_using_current_files(genuine_objects):
    root = genuine_objects
    rows = evidence(root)
    sources = json.loads(rows['drift/oscal-samples.jsonl'][1])['cloud_component_sources']
    path = sources[0]['component_definition']
    raw = git(root, 'show', COMPOSITION + ':' + path)
    blob = git(root, 'rev-parse', COMPOSITION + ':' + path).decode().strip()
    destination = root / path
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_bytes(raw)
    (root / '.git/objects' / blob[:2] / blob[2:]).unlink()
    with pytest.raises(delivery.Refusal):
        delivery.validate_cloud_sources(root, PARENT, sources)
