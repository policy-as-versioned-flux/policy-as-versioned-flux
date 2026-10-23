"""Release callsites over real Git objects; external signatures/API are fixtures.

No fixture signature is genuine. No test calls a real signer, network or GitHub.
"""
from __future__ import annotations

import importlib.util
import json
import os
import re
import shlex
import subprocess
import sys
from pathlib import Path

import pytest
import yaml

ROOT = Path(__file__).resolve().parents[1]
REPOSITORY = "policy-as-versioned-flux/policy-as-versioned-flux"


def git(root, *args):
    return subprocess.run(["git", "-C", str(root), *args], check=True,
                          capture_output=True, text=True).stdout.strip()


@pytest.fixture
def release():
    spec = importlib.util.spec_from_file_location("twin_release", ROOT / "talk/twin_release.py")
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


@pytest.fixture
def package(tmp_path, monkeypatch):
    root = tmp_path / "package"
    root.mkdir()
    git(root, "init", "-q", "-b", "main")
    for key, value in {"commit.gpgsign": "false", "tag.gpgsign": "false",
                       "user.name": "unsigned fixture", "user.email": "fixture@example.invalid"}.items():
        git(root, "config", key, value)
    (root / "twin").mkdir()
    (root / "twin/VERSION").write_text("0.1.0\n")
    (root / "twin/__init__.py").write_text('"""fixture package"""\n')
    (root / "bin").mkdir()
    (root / "bin/twin").write_text("#!/bin/sh\nexit 0\n")
    (root / "bin/twin").chmod(0o755)
    git(root, "add", "twin", "bin/twin")
    git(root, "commit", "-qm", "unsigned fixture package")
    git(root, "remote", "add", "origin", f"https://github.com/{REPOSITORY}.git")
    monkeypatch.setenv("GITHUB_REPOSITORY", REPOSITORY)
    monkeypatch.setenv("GITHUB_REF", "refs/heads/main")
    monkeypatch.setenv("GITHUB_WORKFLOW_REF", f"{REPOSITORY}/.github/workflows/cut-release.yml@refs/heads/main")
    monkeypatch.setenv("GITSIGN_REKOR_MODE", "offline")
    return root


def test_first_package_binds_real_git_objects_without_editing_source(release, package, monkeypatch):
    head = git(package, "rev-parse", "HEAD")
    monkeypatch.setattr(release, "remote_refs", lambda root: {"refs/heads/main": head})
    result = release.prepare(package, "0.1.0", head)
    assert result["tag"] == "twin/v0.1.0"
    assert result["source_commit"] == head
    assert result["twin_tree"] == git(package, "rev-parse", "HEAD:twin")
    assert result["entrypoint_blob"] == git(package, "rev-parse", "HEAD:bin/twin")
    assert result["version_basis"] == "initial-publication-no-predecessor"
    assert result["estate_green_claim"] is False
    assert git(package, "status", "--porcelain") == ""


def test_signing_refusal_stops_before_any_push_or_publish(release, package, monkeypatch):
    head = git(package, "rev-parse", "HEAD")
    monkeypatch.setattr(release, "remote_refs", lambda root: {"refs/heads/main": head})
    actual_run = release.run
    calls = []

    def boundary(root, *args):
        calls.append(args)
        if "tag" in args and "-s" in args:
            raise subprocess.CalledProcessError(42, args, stderr="fixture signer refusal")
        if args[0] in {"gitsign", "gh"} or args[:2] == ("git", "push"):
            raise AssertionError("unexpected external operation in refusal fixture")
        return actual_run(root, *args)

    monkeypatch.setattr(release, "run", boundary)
    with pytest.raises(subprocess.CalledProcessError):
        release.cut(package, "0.1.0", head, "first package")
    assert not any("push" in c or c[0] in {"gitsign", "gh"} for c in calls)
    assert git(package, "tag", "--list") == ""


def test_identity_verification_failure_leaves_tag_unpushed(release, package, monkeypatch):
    head = git(package, "rev-parse", "HEAD")
    monkeypatch.setattr(release, "remote_refs", lambda root: {"refs/heads/main": head})
    actual_run = release.run
    calls = []

    def boundary(root, *args):
        calls.append(args)
        if "tag" in args and "-s" in args:
            annotation = args[args.index("-F") + 1]
            return actual_run(root, "git", "-c", "tag.gpgsign=false", "tag", "-a",
                              "twin/v0.1.0", "-F", annotation, head)
        if args[0] == "gitsign":
            raise subprocess.CalledProcessError(43, args, stderr="fixture wrong certificate identity")
        if args[0] == "gh" or args[:2] == ("git", "push"):
            raise AssertionError("unexpected external operation in refusal fixture")
        return actual_run(root, *args)

    monkeypatch.setattr(release, "run", boundary)
    with pytest.raises(subprocess.CalledProcessError):
        release.cut(package, "0.1.0", head, "first package")
    assert not any("push" in c or c[0] == "gh" for c in calls)
    verify = next(c for c in calls if c[0] == "gitsign")
    assert verify == ("gitsign", "verify-tag", "twin/v0.1.0",
                      "--certificate-identity-regexp=" + release.IDENTITY,
                      "--certificate-oidc-issuer=https://token.actions.githubusercontent.com")


@pytest.fixture
def external_processes(release, package, monkeypatch):
    """Fixture unsigned tags stand in only for external signer/verifier responses."""
    head = git(package, "rev-parse", "HEAD")
    refs = {"refs/heads/main": head}
    monkeypatch.setattr(release, "remote_refs", lambda root: dict(refs))
    actual_run = release.run
    remote = package.parent / "unsigned-fixture-remote.git"
    actual_run(package, "git", "init", "--bare", "-q", "--initial-branch=main", str(remote))
    actual_run(package, "git", "push", str(remote), "HEAD:refs/heads/main")
    calls = []

    def boundary(root, *args):
        calls.append(args)
        if "tag" in args and "-s" in args:
            return actual_run(root, "git", "-c", "tag.gpgsign=false", "tag", "-a",
                              "twin/v0.1.0", "-F", args[args.index("-F") + 1], head)
        if args[0] == "gitsign":
            return "FIXTURE verification response; no genuine signature"
        if args[:2] == ("git", "push"):
            local = list(args)
            local[local.index("origin")] = str(remote)
            actual_run(root, *local)
            refs["refs/tags/twin/v0.1.0"] = git(root, "rev-parse", "refs/tags/twin/v0.1.0")
            refs["refs/tags/twin/v0.1.0^{}"] = head
            assert git(remote, "rev-parse", "refs/tags/twin/v0.1.0^{commit}") == head
            return "unsigned fixture tag pushed to local bare remote only"
        if args[:2] == ("git", "fetch"):
            local = list(args)
            local[local.index("origin")] = str(remote)
            return actual_run(root, *local)
        if args[0] == "gh":
            return "FIXTURE external response; no network"
        return actual_run(root, *args)

    monkeypatch.setattr(release, "run", boundary)
    return calls, refs


def test_cut_dispatches_the_verified_exact_tag_then_publish_reverifies(release, package, external_processes, monkeypatch):
    calls, _ = external_processes
    head = git(package, "rev-parse", "HEAD")
    result = release.cut(package, "0.1.0", head, "first package")
    assert result["source_commit"] == head
    assert next(c for c in calls if c[:2] == ("git", "push")) == (
        "git", "push", "--atomic", "origin", "refs/tags/twin/v0.1.0:refs/tags/twin/v0.1.0")
    assert calls[-1] == ("gh", "workflow", "run", "release.yml", "--repo", REPOSITORY,
                         "--ref", "main", "-f", "tag=twin/v0.1.0", "-f", "expected_commit=" + head)
    monkeypatch.setenv("GITHUB_WORKFLOW_REF", f"{REPOSITORY}/.github/workflows/release.yml@refs/heads/main")
    release.publish(package, "twin/v0.1.0", head)
    assert len([c for c in calls if c[0] == "gitsign"]) == 2
    create = calls[-1]
    assert create[:7] == ("gh", "release", "create", "twin/v0.1.0", "--repo", REPOSITORY, "--verify-tag")
    assert create[create.index("--target") + 1] == head


def test_actual_workflow_cut_and_publish_calls_reach_the_same_cli(release, package, external_processes, monkeypatch):
    head = git(package, "rev-parse", "HEAD")
    monkeypatch.chdir(package)
    monkeypatch.setenv("EXPECTED_COMMIT", head)
    monkeypatch.setenv("VERSION", "0.1.0")
    monkeypatch.setenv("MESSAGE", "fixture message with $literal and spaces")
    monkeypatch.setenv("TAG", "twin/v0.1.0")
    for filename, step_name in [("cut-release.yml", "cut the verified initial package"),
                                ("release.yml", "verify and publish the exact tag")]:
        workflow = yaml.safe_load((ROOT / ".github/workflows" / filename).read_text())
        steps = workflow["jobs"][next(iter(workflow["jobs"]))]["steps"]
        command = next(s["run"] for s in steps if s.get("name") == step_name)
        # The real YAML command is the public CLI; environment values remain single args.
        args = shlex.split(command)
        args = [os.environ.get(arg[1:], arg) if arg.startswith("$") else arg for arg in args]
        assert args[:2] == ["python3", "talk/twin_release.py"]
        monkeypatch.setenv("GITHUB_WORKFLOW_REF", f"{REPOSITORY}/.github/workflows/{filename}@refs/heads/main")
        monkeypatch.setattr(sys, "argv", args[1:])
        release.main()


@pytest.mark.parametrize("defect", ["version", "short-sha", "wrong-sha", "dirty", "stale-main",
                                  "remote-tag", "local-tag", "wrong-workflow", "wrong-origin"])
def test_invalid_release_inputs_cannot_sign_or_push(release, package, external_processes, monkeypatch, defect):
    calls, refs = external_processes
    head = git(package, "rev-parse", "HEAD")
    version = "0.1.0"
    if defect == "version":
        version = "0.2.0"
    elif defect == "short-sha":
        head = head[:7]
    elif defect == "wrong-sha":
        head = "0" * 40
    elif defect == "dirty":
        (package / "untracked").write_text("unreviewed")
    elif defect == "stale-main":
        refs["refs/heads/main"] = "0" * 40
    elif defect == "remote-tag":
        refs["refs/tags/twin/v0.1.0"] = head
    elif defect == "local-tag":
        git(package, "tag", "-a", "twin/v0.1.0", "-m", "unsigned fixture")
    elif defect == "wrong-workflow":
        monkeypatch.setenv("GITHUB_WORKFLOW_REF", "foreign workflow")
    elif defect == "wrong-origin":
        git(package, "remote", "set-url", "origin", "https://example.invalid/foreign.git")
    with pytest.raises(release.Refusal):
        release.cut(package, version, head, "fixture release")
    assert not any(c[0] in {"gh", "gitsign"} or "push" in c or "-s" in c for c in calls)


def test_authenticated_manifest_tampering_cannot_publish(release, package, external_processes, monkeypatch):
    calls, refs = external_processes
    head = git(package, "rev-parse", "HEAD")
    manifest = release.prepare(package, "0.1.0", head)
    manifest.update(message="fixture", estate_green_claim=0)
    # Unsigned fixture and explicit external verification response. Even equivalent
    # Python values (0 versus false) are different JSON contract types.
    git(package, "tag", "-a", "twin/v0.1.0", "-m", json.dumps(manifest))
    git(package, "push", str(package.parent / "unsigned-fixture-remote.git"), "refs/tags/twin/v0.1.0")
    refs["refs/tags/twin/v0.1.0"] = git(package, "rev-parse", "refs/tags/twin/v0.1.0")
    refs["refs/tags/twin/v0.1.0^{}"] = head
    monkeypatch.setenv("GITHUB_WORKFLOW_REF", f"{REPOSITORY}/.github/workflows/release.yml@refs/heads/main")
    with pytest.raises(release.Refusal, match="annotation"):
        release.publish(package, "twin/v0.1.0", head)
    assert not any(c[0] == "gh" for c in calls)


def test_remote_tag_object_change_cannot_publish(release, package, external_processes, monkeypatch):
    calls, refs = external_processes
    head = git(package, "rev-parse", "HEAD")
    release.cut(package, "0.1.0", head, "fixture release")
    calls.clear()
    refs["refs/tags/twin/v0.1.0"] = "0" * 40
    monkeypatch.setenv("GITHUB_WORKFLOW_REF", f"{REPOSITORY}/.github/workflows/release.yml@refs/heads/main")
    with pytest.raises(release.Refusal, match="remote tag"):
        release.publish(package, "twin/v0.1.0", head)
    assert not any(c[0] == "gh" for c in calls)


def test_verification_has_no_online_or_test_mode_fallback(release, package, external_processes, monkeypatch):
    calls, _ = external_processes
    head = git(package, "rev-parse", "HEAD")
    monkeypatch.setenv("GITSIGN_REKOR_MODE", "online")
    monkeypatch.setenv("CUT_RELEASE_TEST_MODE", "1")
    with pytest.raises(release.Refusal, match="offline"):
        release.cut(package, "0.1.0", head, "fixture release")
    assert not any("-s" in c or "push" in c or c[0] == "gh" for c in calls)


def test_certificate_subject_accepts_only_the_canonical_main_cut_workflow(release):
    good = f"https://github.com/{REPOSITORY}/.github/workflows/cut-release.yml@refs/heads/main"
    assert re.fullmatch(release.IDENTITY, good)
    for wrong in [good.replace("policy-as-versioned-flux/", "foreign/", 1),
                  good.replace("cut-release.yml", "truth.yml"),
                  good.replace("refs/heads/main", "refs/heads/feature"),
                  good.replace("github.com", "githubXcom"), good + "/suffix"]:
        assert not re.fullmatch(release.IDENTITY, wrong)


def test_cli_retains_the_original_external_verification_failure(release, package, external_processes, monkeypatch, capsys):
    head = git(package, "rev-parse", "HEAD")
    boundary = release.run

    def rejected(root, *args):
        if args[0] == "gitsign":
            raise subprocess.CalledProcessError(43, args, stderr="fixture certificate SAN mismatch")
        return boundary(root, *args)

    monkeypatch.setattr(release, "run", rejected)
    monkeypatch.setattr(sys, "argv", ["twin_release.py", "cut", "--repo", str(package),
                                    "--expected-commit", head, "--message", "fixture"])
    with pytest.raises(SystemExit) as error:
        release.main()
    assert error.value.code == 1
    assert "fixture certificate SAN mismatch" in capsys.readouterr().err
