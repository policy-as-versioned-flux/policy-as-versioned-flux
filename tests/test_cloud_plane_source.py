"""Cloud admission expectations follow the signed package, never moving source."""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import subprocess

import pytest


SCRIPT = Path(__file__).resolve().parents[1] / 'verify/cloud-plane/cloud_plane.py'
SPEC = importlib.util.spec_from_file_location('cloud_plane_source', SCRIPT)
assert SPEC is not None and SPEC.loader is not None
cloud = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(cloud)


def git(repository: Path, *args: str) -> str:
    return subprocess.check_output(['git', '-C', str(repository), *args], text=True).strip()


def commit(repository: Path) -> str:
    git(repository, 'add', '.')
    git(repository, '-c', 'commit.gpgsign=false', '-c', 'user.name=fixture', '-c', 'user.email=fixture@example.invalid', 'commit', '-qm', 'fixture')
    return git(repository, 'rev-parse', 'HEAD')


@pytest.fixture
def source(tmp_path, monkeypatch):
    platform = tmp_path / 'platform'
    tuppence = tmp_path / 'tuppence'
    for repository in (platform, tuppence):
        repository.mkdir()
        git(repository, 'init', '-q')
    package = platform / 'implementations/cloud'
    package.mkdir(parents=True)
    (package / 'VERSION').write_text('1.0.0\n')
    (package / 'crossplane-dials.yaml').write_text('signed-dial-value\n')
    cloud_sha = commit(platform)
    git(platform, '-c', 'tag.gpgsign=false', 'tag', 'cloud/v1.0.0')
    (package / 'crossplane-dials.yaml').write_text('later-unrelated-main-value\n')
    parent = {'party': 'platform', 'kind': 'implementations', 'name': 'cloud',
              'path': 'implementations/cloud', 'tag': 'cloud/v1.0.0',
              'sha': cloud_sha, 'signature_identity': cloud.CLOUD_IDENTITY}
    (tuppence / 'composed').mkdir()
    (tuppence / 'composed/CLOUD-PARENT.json').write_text(json.dumps(parent))
    composed_sha = commit(tuppence)
    git(tuppence, '-c', 'tag.gpgsign=false', 'tag', 'v4.1.0')
    prefix = 'policy-as-versioned.dev/'
    source = {'metadata': {'annotations': {
        prefix + 'gitsign-identity-regexp': cloud.TUPPENCE_IDENTITY,
        prefix + 'gitsign-issuer': 'https://token.actions.githubusercontent.com',
        prefix + 'gitsign-gates': 'flux-system/crossplane-crds,flux-system/cloud-policies,flux-system/cloud-claims'}},
        'spec': {'url': 'https://github.com/policy-as-versioned-tuppence/tuppence',
                 'ref': {'tag': 'v4.1.0', 'commit': composed_sha}}}
    monkeypatch.setattr(cloud, 'PLATFORM', platform)
    monkeypatch.setattr(cloud, 'TUPPENCE', tuppence)
    return source, parent


def signature_cli(monkeypatch, *, success=True):
    real_run = subprocess.run
    calls = []
    def command(args, **kwargs):
        if args[0] != 'gitsign':
            return real_run(args, **kwargs)
        assert args[1] == 'verify-tag'
        assert kwargs['env']['GITSIGN_REKOR_MODE'] == 'offline'
        calls.append(args)
        return subprocess.CompletedProcess(args, 0 if success else 1, '', '')
    monkeypatch.setattr(cloud.subprocess, 'run', command)
    return calls


def test_signed_composed_parent_supplies_the_dials_even_when_main_moves(source, tmp_path, monkeypatch):
    pin, expected = source
    calls = signature_cli(monkeypatch)
    parent, package = cloud.cloud_parent(pin, tmp_path / 'snapshot')
    assert parent == expected
    assert (package / 'crossplane-dials.yaml').read_text() == 'signed-dial-value\n'
    assert [call[2] for call in calls] == ['v4.1.0', 'cloud/v1.0.0']
    assert '--certificate-identity-regexp=' + cloud.TUPPENCE_IDENTITY in calls[0]
    assert '--certificate-identity-regexp=' + cloud.CLOUD_IDENTITY in calls[1]


@pytest.mark.parametrize('fault', ['source-sha', 'source-url', 'signer', 'missing-gate', 'signature'])
def test_unverified_cloud_delivery_is_rejected_before_a_cluster(source, tmp_path, monkeypatch, fault):
    pin, _ = source
    if fault == 'source-sha':
        pin['spec']['ref']['commit'] = '0' * 40
    elif fault == 'source-url':
        pin['spec']['url'] = 'https://github.com/elsewhere/tu-copy'
    elif fault == 'signer':
        pin['metadata']['annotations']['policy-as-versioned.dev/gitsign-identity-regexp'] = '^anything$'
    elif fault == 'missing-gate':
        pin['metadata']['annotations']['policy-as-versioned.dev/gitsign-gates'] = 'flux-system/cloud-policies'
    signature_cli(monkeypatch, success=fault != 'signature')
    with pytest.raises(ValueError):
        cloud.cloud_parent(pin, tmp_path / 'snapshot')


@pytest.mark.parametrize('environment', [{}, {'GITHUB_ACTIONS': 'true', 'RUNNER_ENVIRONMENT': 'self-hosted'}])
def test_hosted_bootstrap_refuses_local_and_self_hosted_execution(tmp_path, environment):
    import os
    env = {key: value for key, value in os.environ.items() if key not in ('GITHUB_ACTIONS', 'RUNNER_ENVIRONMENT')}
    env.update(environment)
    result = subprocess.run(['bash', str(SCRIPT.with_name('hosted-admission.sh'))], env=env, capture_output=True, text=True)
    assert result.returncode == 1
    assert 'local clusters stay off' in result.stderr
