"""Exercise observation delivery over real Git objects and a protected fixture remote.

The fixture substitutes GitHub API calls and certificate verification explicitly. Its
commits are unsigned attribution fixtures, never claims of genuine CI signatures.
"""
from __future__ import annotations

import copy
import datetime as dt
import importlib.util
import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
REPO = "policy-as-versioned-flux/policy-as-versioned-flux"
TODAY = dt.date(2026, 10, 5)


def git(root, *args, env=None, check=True):
    return subprocess.run(["git", "-C", str(root), *args], text=True, capture_output=True,
                          check=check, env=env).stdout.strip()


@pytest.fixture
def delivery():
    spec = importlib.util.spec_from_file_location("truth_delivery", ROOT / "talk/truth_delivery.py")
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class FixtureAPI:
    def __init__(self, root, remote, run, head):
        self.root, self.remote, self.run = root, remote, run
        self.latest_run = copy.deepcopy(run)
        self.latest_run["run_attempt"] = 3
        self.repo = {"full_name": REPO, "default_branch": "main"}
        self.workflow = {"id": 9, "path": ".github/workflows/truth.yml"}
        self.pr = {"number": 4, "state": "open", "merged": False,
                   "user": {"login": "github-actions[bot]"},
                   "head": {"sha": head, "ref": "observations/truth/100-2",
                            "repo": {"full_name": REPO}},
                   "base": {"ref": "main", "repo": {"full_name": REPO}}}
        self.installation = {"app_id": 4819564}
        self.calls, self.approved = [], False
        self.mutate_on_read = None
        self.merge_refused = False

    def __call__(self, method, path, body=None):
        self.calls.append((method, path, copy.deepcopy(body)))
        if path == "installation":
            return self.installation
        if path == f"repos/{REPO}":
            return self.repo
        if path.endswith("/actions/runs/100"):
            return self.latest_run
        if "/actions/runs/100/attempts/" in path:
            return self.run
        if path.endswith("/actions/workflows/truth.yml"):
            return self.workflow
        if "/pulls?" in path:
            row = copy.deepcopy(self.pr)
            row.pop("merged")
            row["merged_at"] = "2026-10-05T06:00:00Z" if self.pr["merged"] else None
            return [row]
        if path.endswith("/pulls/4"):
            if self.mutate_on_read:
                self.pr["head"]["sha"] = self.mutate_on_read
            return copy.deepcopy(self.pr)
        if path.endswith("/pulls/4/reviews"):
            assert body == {"commit_id": self.pr["head"]["sha"], "event": "APPROVE",
                            "body": "Verified original signed TRUTH observation and protected delivery."}
            self.approved = True
            (self.remote / "reviewed-head").write_text(body["commit_id"])
            return {"state": "APPROVED", "commit_id": body["commit_id"]}
        if path.endswith("/pulls/4/merge"):
            assert self.approved
            assert body == {"sha": self.pr["head"]["sha"], "merge_method": "merge"}
            if self.merge_refused:
                return {"merged": False, "message": "Merge conflict; PR remains pending"}
            checkout = self.root.parent / "reviewed-merge"
            subprocess.run(["git", "clone", "-q", str(self.remote), str(checkout)],
                           check=True, capture_output=True)
            git(checkout, "config", "commit.gpgsign", "false")
            git(checkout, "config", "core.hooksPath", os.devnull)
            git(checkout, "config", "user.name", "fixture separate reviewer")
            git(checkout, "config", "user.email", "reviewer@example.invalid")
            git(checkout, "merge", "--no-ff", self.pr["head"]["sha"], "-m", "Reviewed observation")
            git(checkout, "push", "origin", "main")
            self.pr.update(merged=True, state="closed", merge_commit_sha=git(checkout, "rev-parse", "HEAD"))
            return {"merged": True, "sha": self.pr["merge_commit_sha"]}
        raise AssertionError(f"unexpected fixture API request {method} {path}")


@pytest.fixture
def estate(tmp_path):
    root, remote = tmp_path / "root", tmp_path / "remote.git"
    root.mkdir()
    subprocess.run(["git", "init", "-q", "-b", "main", str(root)], check=True)
    git(root, "config", "commit.gpgsign", "false")
    git(root, "config", "core.hooksPath", os.devnull)
    git(root, "config", "user.name", "fixture author")
    git(root, "config", "user.email", "author@example.invalid")
    for path in ("talk", ".github/workflows", "twin"):
        (root / path).mkdir(parents=True)
    (root / "talk/truth.log").write_text("TRUTH 2026-10-04T01:00Z run=1 hub=1234567 fail=1\n")
    (root / ".github/workflows/truth.yml").write_text(
        'env:\n  OBSERVATION_LANE: "talk/truth.log talk/captures observations"\n')
    (root / "twin/ENACT_MODE").write_text("development\n")
    (root / "owner.md").write_text('2026-09-24, owner: "agree".\n')
    (root / "twin/ENACT_MODE.why").write_text(
        "mode: development\nuntil: '2026-10-22'\nsaid:\n"
        "  - on: '2026-09-24'\n    by: owner\n    words: agree\n    where: owner.md\n")
    git(root, "add", ".")
    git(root, "commit", "-qm", "measured fixture source")
    measured = git(root, "rev-parse", "HEAD")
    subprocess.run(["git", "init", "-q", "--bare", "-b", "main", str(remote)], check=True)
    git(root, "remote", "add", "origin", str(remote))
    git(root, "push", "-q", "origin", "main")
    # Main updates require an approval for the exact original candidate and a merge
    # retaining it. Direct clock pushes have no approval and are actually refused.
    hook = remote / "hooks/update"
    git(remote, "config", "core.hooksPath", str(remote / "hooks"))
    hook.write_text('#!/bin/sh\nif [ "$1" = refs/heads/main ]; then\n'
                    '  test -f reviewed-head || { echo "GH013: Changes must be made through a pull request" >&2; exit 1; }\n'
                    '  git merge-base --is-ancestor "$(cat reviewed-head)" "$3" || exit 1\nfi\n')
    hook.chmod(0o755)
    git(root, "switch", "-qc", "observations/truth/100-2")
    line = f"TRUTH 2026-10-05T05:47Z run=12 hub={measured[:7]} fail=8\n"
    (root / "talk/truth.log").write_text((root / "talk/truth.log").read_text() + line)
    git(root, "add", "talk/truth.log")
    git(root, "-c", "user.name=truth surface", "-c", "user.email=truth@users.noreply.github.com",
        "commit", "-qm", "truth: record run 12 [skip ci]")
    head = git(root, "rev-parse", "HEAD")
    direct = subprocess.run(["git", "-C", str(root), "push", "origin", "HEAD:main"], capture_output=True)
    assert direct.returncode != 0 and b"GH013" in direct.stderr
    git(root, "push", "-q", "origin", "HEAD:observations/truth/100-2")
    git(root, "switch", "-q", "main")
    run = {"id": 100, "run_number": 12, "run_attempt": 2, "workflow_id": 9,
           "path": ".github/workflows/truth.yml", "head_sha": measured, "head_branch": "main",
           "event": "schedule", "status": "completed", "conclusion": "failure",
           "repository": {"full_name": REPO}, "head_repository": {"full_name": REPO}}
    api = FixtureAPI(root, remote, run, head)
    return root, remote, api, head, line


def invoke(delivery, estate, **kwargs):
    root, _, api, _, _ = estate
    return delivery.deliver(root, 100, attempt=2, api=api, verify=lambda *args: None, today=TODAY, **kwargs)


def test_protected_delivery_retains_original_observation_on_red_clock(delivery, estate):
    root, remote, api, head, line = estate
    assert invoke(delivery, estate).startswith("RECORDED")
    assert git(remote, "merge-base", "--is-ancestor", head, "main") == ""
    assert git(remote, "show", "main:talk/truth.log").endswith(line.strip())
    assert api.run["conclusion"] == "failure"
    count = len([c for c in api.calls if c[0] != "GET"])
    git(remote, "update-ref", "-d", "refs/heads/observations/truth/100-2")
    # A later controller invocation starts from a fresh trusted default checkout.
    git(root, "fetch", "origin", "main")
    git(root, "merge", "--ff-only", "origin/main")
    assert invoke(delivery, estate).startswith("RECORDED")
    assert len([c for c in api.calls if c[0] != "GET"]) == count


@pytest.mark.parametrize("field,value", [
    ("repository", {"full_name": "attacker/hub"}), ("head_repository", {"full_name": "fork/hub"}),
    ("head_branch", "topic"), ("head_sha", "--upload-pack=payload"), ("head_sha", "123"),
    ("workflow_id", 8), ("path", ".github/workflows/other.yml"),
    ("event", "pull_request"), ("status", "in_progress"), ("run_attempt", True),
])
def test_wrong_run_never_reviews(delivery, estate, field, value):
    estate[2].run[field] = value
    with pytest.raises(delivery.Refusal):
        invoke(delivery, estate)
    assert all(c[0] == "GET" for c in estate[2].calls)


@pytest.mark.parametrize("part,field,value", [
    ("head", "ref", "observations/truth/100-1"), ("head", "repo", {"full_name": "fork/hub"}),
    ("base", "ref", "topic"), ("base", "repo", {"full_name": "fork/hub"}),
    ("user", "login", "chrisns"), ("head", "sha", "123"),
])
def test_wrong_pr_never_reviews(delivery, estate, part, field, value):
    estate[2].pr[part][field] = value
    with pytest.raises(delivery.Refusal):
        invoke(delivery, estate)
    assert all(c[0] == "GET" for c in estate[2].calls)


@pytest.mark.parametrize("plant", ["declaration", "symlink", "rewrite", "two-lines", "delete", "executable"])
def test_commit_content_refuses_before_review(delivery, estate, plant):
    root, _, api, _, _ = estate
    git(root, "switch", "-q", "observations/truth/100-2")
    if plant == "declaration":
        (root / "executable.py").write_text("raise RuntimeError('must never execute incoming code')\n")
    elif plant == "symlink":
        (root / "observations").mkdir()
        (root / "observations/link").symlink_to("../twin/ENACT_MODE")
    elif plant == "rewrite":
        p = root / "talk/truth.log"
        p.write_text(p.read_text().replace("fail=1", "fail=0"))
    elif plant == "two-lines":
        p = root / "talk/truth.log"
        p.write_text(p.read_text() + p.read_text().splitlines(keepends=True)[-1])
    elif plant == "delete":
        (root / "talk/truth.log").unlink()
    else:
        (root / "talk/truth.log").chmod(0o755)
    git(root, "add", "-A")
    git(root, "-c", "user.name=truth surface", "-c", "user.email=truth@users.noreply.github.com",
        "commit", "--amend", "--no-edit", "-q")
    api.pr["head"]["sha"] = git(root, "rev-parse", "HEAD")
    git(root, "push", "-q", "--force", "origin", "observations/truth/100-2")
    git(root, "switch", "-q", "main")
    with pytest.raises(delivery.Refusal):
        invoke(delivery, estate)
    assert all(c[0] == "GET" for c in api.calls)


def test_changed_pr_head_is_never_approved(delivery, estate):
    estate[2].mutate_on_read = estate[2].run["head_sha"]
    with pytest.raises(delivery.Refusal, match="head"):
        invoke(delivery, estate)
    assert not estate[2].approved


def test_signature_claims_bind_actual_run_and_failure_stops_review(delivery, estate):
    root, _, api, head, _ = estate
    calls = []
    def refusal(*args):
        calls.append(args)
        raise delivery.Refusal("unsigned or wrong certificate claims")
    with pytest.raises(delivery.Refusal, match="certificate"):
        delivery.deliver(root, 100, attempt=2, api=api, verify=refusal, today=TODAY)
    assert calls == [(root, head, api.run, "main")]
    assert not api.approved


def test_wrong_installation_refuses_mutation(delivery, estate):
    estate[2].installation["app_id"] = 123
    with pytest.raises(delivery.Refusal, match="App"):
        invoke(delivery, estate)
    assert not estate[2].approved


def test_conflict_preserves_pending_record_without_recorded_claim(delivery, estate):
    estate[2].merge_refused = True
    with pytest.raises(delivery.Refusal, match="pending"):
        invoke(delivery, estate)
    assert not estate[2].pr["merged"]
    assert estate[3] != git(estate[1], "rev-parse", "main")


def test_expired_window_and_ambient_override_do_not_merge(delivery, estate, monkeypatch):
    monkeypatch.setenv("TWIN_ENACT_MODE", "development")
    with pytest.raises(delivery.Refusal, match="window"):
        delivery.deliver(estate[0], 100, attempt=2, api=estate[2], verify=lambda *args: None,
                         today=dt.date(2026, 10, 22))
    assert not estate[2].approved


def test_read_only_preflight_needs_no_app_credential(delivery, estate):
    estate[2].installation["app_id"] = 0
    assert invoke(delivery, estate, check_only=True).startswith("VERIFIED")
    assert all(call[0] == "GET" and call[1] != "installation" for call in estate[2].calls)
    assert not estate[2].pr["merged"]


def test_pr_base_race_after_approval_refuses_merge(delivery, estate):
    root, _, api, _, _ = estate
    reads = 0
    def changed(method, path, body=None):
        nonlocal reads
        value = api(method, path, body)
        if method == "GET" and path.endswith("/pulls/4"):
            reads += 1
            if reads == 4:
                value["base"]["ref"] = "topic"
        return value
    with pytest.raises(delivery.Refusal, match="ref"):
        delivery.deliver(root, 100, attempt=2, api=changed, verify=lambda *args: None, today=TODAY)
    assert api.approved and not any(c[0] == "PUT" for c in api.calls)


def test_signature_command_binds_every_measured_claim_and_has_no_bypass(delivery, estate, monkeypatch):
    root, _, api, head, _ = estate
    seen = []
    def inspect(command, **kwargs):
        seen.append(command)
        return subprocess.CompletedProcess(command, 1)
    monkeypatch.setattr(delivery.subprocess, "run", inspect)
    with pytest.raises(delivery.Refusal, match="certificate"):
        delivery.verify_signature(root, head, api.run, "main")
    assert seen == [["gitsign", "verify", head,
        f"--certificate-identity=https://github.com/{REPO}/.github/workflows/truth.yml@refs/heads/main",
        "--certificate-oidc-issuer=https://token.actions.githubusercontent.com",
        f"--certificate-github-workflow-sha={api.run['head_sha']}",
        f"--certificate-github-workflow-repository={REPO}",
        "--certificate-github-workflow-ref=refs/heads/main",
        "--certificate-github-workflow-trigger=schedule"]]


def test_wrong_clock_identity_cannot_relabel_an_observation(delivery, estate):
    root, _, api, _, _ = estate
    git(root, "switch", "-q", "observations/truth/100-2")
    git(root, "commit", "--amend", "--reset-author", "--no-edit", "-q")
    api.pr["head"]["sha"] = git(root, "rev-parse", "HEAD")
    git(root, "push", "-q", "--force", "origin", "observations/truth/100-2")
    git(root, "switch", "-q", "main")
    with pytest.raises(delivery.Refusal, match="clock"):
        invoke(delivery, estate)
    assert not api.approved


def test_completed_attempt_survives_a_later_upstream_rerun(delivery, estate):
    estate[2].latest_run.update(run_attempt=3, status="in_progress", conclusion=None)
    assert invoke(delivery, estate, check_only=True).startswith("VERIFIED")
    routes = [call[1] for call in estate[2].calls]
    assert f"repos/{REPO}/actions/runs/100/attempts/2" in routes
    assert f"repos/{REPO}/actions/runs/100" not in routes


def test_official_attempt_must_match_the_completed_event(delivery, estate):
    with pytest.raises(delivery.Refusal, match="attempt"):
        delivery.deliver(estate[0], 100, attempt=1, api=estate[2],
                         verify=lambda *args: None, today=TODAY)
    assert all(call[0] == "GET" for call in estate[2].calls)


def advance_reviewed_authority(estate):
    """Move the actual fixture remote's main; leave the controller checkout untouched."""
    root, remote, _, _, _ = estate
    update = root.parent / "reviewed-authority-update"
    subprocess.run(["git", "clone", "-q", str(remote), str(update)], check=True, capture_output=True)
    git(update, "config", "commit.gpgsign", "false")
    git(update, "config", "core.hooksPath", os.devnull)
    git(update, "config", "user.name", "fixture source reviewer")
    git(update, "config", "user.email", "source-reviewer@example.invalid")
    (update / "twin/ENACT_MODE").write_text("operations\n")
    record = update / "twin/ENACT_MODE.why"
    record.write_text(record.read_text().replace("mode: development", "mode: operations"))
    git(update, "add", "twin/ENACT_MODE", "twin/ENACT_MODE.why")
    git(update, "commit", "-qm", "Reviewed authority changed to operations")
    (remote / "reviewed-head").write_text(git(update, "rev-parse", "HEAD"))
    git(update, "push", "-q", "origin", "main")


def test_remote_authority_changes_after_metadata_prevent_approval(delivery, estate):
    api = estate[2]
    def changed(method, path, body=None):
        value = api(method, path, body)
        if path == "installation":
            advance_reviewed_authority(estate)
        return value
    with pytest.raises(delivery.Refusal, match="trusted checkout"):
        delivery.deliver(estate[0], 100, attempt=2, api=changed,
                         verify=lambda *args: None, today=TODAY)
    assert not api.approved
    assert not any(call[0] == "PUT" for call in api.calls)


def test_remote_authority_changes_after_approval_prevent_merge(delivery, estate):
    api = estate[2]
    def changed(method, path, body=None):
        value = api(method, path, body)
        if path.endswith("/reviews"):
            advance_reviewed_authority(estate)
        return value
    with pytest.raises(delivery.Refusal, match="trusted checkout"):
        delivery.deliver(estate[0], 100, attempt=2, api=changed,
                         verify=lambda *args: None, today=TODAY)
    assert api.approved
    assert not any(call[0] == "PUT" for call in api.calls)


@pytest.mark.parametrize("method,path,expected", [
    ("GET", f"repos/{REPO}/actions/runs/100/attempts/2", "fixture-reader"),
    ("GET", f"repos/{REPO}/pulls/4", "fixture-reader"),
    ("GET", "installation", "fixture-app"),
    ("POST", f"repos/{REPO}/pulls/4/reviews", "fixture-app"),
    ("PUT", f"repos/{REPO}/pulls/4/merge", "fixture-app"),
])
def test_api_transport_isolates_reader_and_writer_tokens(delivery, monkeypatch, method, path, expected):
    monkeypatch.setenv("GH_TOKEN", "fixture-app")
    monkeypatch.setenv("TRUTH_READ_TOKEN", "fixture-reader")
    monkeypatch.setenv("GITHUB_TOKEN", "fixture-ambient")
    seen = []
    def inspect(command, **kwargs):
        seen.append(kwargs.get("env", {}))
        return subprocess.CompletedProcess(command, 0, stdout="{}")
    monkeypatch.setattr(delivery.subprocess, "run", inspect)
    assert delivery.github_api(method, path, None) == {}
    assert seen[0].get("GH_TOKEN") == expected
    assert "TRUTH_READ_TOKEN" not in seen[0] and "GITHUB_TOKEN" not in seen[0]
    assert set(seen[0].values()) & {"fixture-app", "fixture-reader", "fixture-ambient"} == {expected}
