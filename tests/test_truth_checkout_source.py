"""TEST_ONLY checkout input/refspec replay, not a live actions/checkout execution.

The actual workflow input selects the documented11d5960 actions/checkout v4 path:
input-helper79–95, ref-helper29–37/89–104/151–163, source-provider172–185.
Real Git implements full fetch, conditional targeted refspec and detached/branch checkout;
the unchanged can-record CLI decides whether an actual clock line is stranded. No signer,
GitHub API or marketplace Action runs here. The original hosted trace/private real-object
replay separately proves the branch+eventSHA force-fetch this small fixture models.
"""
from __future__ import annotations

import importlib.util
import os
from pathlib import Path
import subprocess
import sys
from typing import Any

import pytest
import yaml

ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = ROOT / ".github/workflows/truth.yml"
GRADER = ROOT / "verify/can-record/can_record.py"


def _checkout_step() -> dict:
    doc = yaml.safe_load(WORKFLOW.read_text())
    steps = [s for s in doc["jobs"]["gate"]["steps"] if s.get("uses", "").startswith("actions/checkout@")]
    assert len(steps) == 1
    assert steps[0]["with"]["fetch-depth"] == 0
    return steps[0]


def _git(root: Path, env: dict[str, str], *args: str) -> str:
    return subprocess.run(["git", *args], cwd=root, env=env, check=True,
                          capture_output=True, text=True).stdout.strip()


def _checkout_fixture(tmp_path: Path, *, default: str = "main", recorded: bool = True) -> dict[str, Any]:
    env = dict(os.environ, GIT_CONFIG_GLOBAL=str(tmp_path / "gitconfig"), GIT_CONFIG_NOSYSTEM="1",
               GIT_TERMINAL_PROMPT="0", GIT_AUTHOR_NAME="fixture", GIT_COMMITTER_NAME="fixture",
               GIT_AUTHOR_EMAIL="fixture@example.invalid", GIT_COMMITTER_EMAIL="fixture@example.invalid")
    (tmp_path / "gitconfig").write_text("[commit]\n gpgsign = false\n[core]\n hooksPath = /dev/null\n[advice]\n detachedHead = false\n")
    remote = tmp_path / "remote.git"
    _git(tmp_path, env, "init", "-q", "--bare", "-b", default, str(remote))
    work = tmp_path / "publisher"
    _git(tmp_path, env, "clone", "-q", str(remote), str(work))
    (work / "talk").mkdir()
    (work / "talk/truth.log").write_text("TRUTH 1970-01-01T00:00Z run=0 hub=0000000 synthetic=TEST_ONLY\n")
    _git(work, env, "add", "talk/truth.log")
    _git(work, env, "commit", "-qm", "TEST_ONLY source")
    source = _git(work, env, "rev-parse", "HEAD")
    _git(work, env, "push", "-q", "origin", default)
    pending = "observations/truth/fixture-1"
    _git(work, env, "checkout", "-qb", pending)
    with (work / "talk/truth.log").open("a") as stream:
        stream.write(f"TRUTH 1970-01-01T00:01Z run=1 hub={source} synthetic=TEST_ONLY\n")
    clock_env = dict(env, GIT_AUTHOR_EMAIL="truth@users.noreply.github.com",
                     GIT_COMMITTER_EMAIL="truth@users.noreply.github.com")
    _git(work, clock_env, "commit", "-qam", "truth: record run 1 [skip ci]")
    clock = _git(work, env, "rev-parse", "HEAD")
    _git(work, env, "push", "-q", "origin", pending)
    _git(work, env, "checkout", "-q", default)
    if recorded:
        _git(work, env, "merge", "-q", "--no-ff", pending, "-m", "TEST_ONLY normal reviewed merge")
        _git(work, env, "push", "-q", "origin", default)
    default_tip = _git(work, env, "rev-parse", "HEAD")
    reader = tmp_path / "measurement"
    _git(tmp_path, env, "clone", "-q", str(remote), str(reader))
    _git(reader, env, "fetch", "--no-tags", "origin", "+refs/heads/*:refs/remotes/origin/*")

    # Model only the two supported same-repository event inputs, then execute real Git.
    # Missing input follows context.ref+context.sha; explicit github.sha becomes SHA-only.
    configured = _checkout_step()["with"].get("ref", "")
    assert configured in ("", "${{ github.sha }}"), "Update this bounded replay for a different checkout contract"
    ref = f"refs/heads/{default}" if not configured else ""
    if ref and _git(reader, env, "rev-parse", f"refs/remotes/origin/{default}") != source:
        _git(reader, env, "fetch", "--no-tags", "origin", f"+{source}:refs/remotes/origin/{default}")
    if ref:
        _git(reader, env, "checkout", "-q", "-B", default, f"refs/remotes/origin/{default}")
    else:
        _git(reader, env, "checkout", "-q", "--detach", source)
    # No verdict stub: execute the production CLI over the resulting actual Git graph.
    result = subprocess.run([sys.executable, str(GRADER), "stranded", str(reader)],
                            env=env, capture_output=True, text=True)
    detached = subprocess.run(["git", "symbolic-ref", "-q", "HEAD"], cwd=reader, env=env,
                              capture_output=True).returncode == 1
    return {"result": result, "source": source, "clock": clock, "default_tip": default_tip,
            "HEAD": _git(reader, env, "rev-parse", "HEAD"), "detached": detached,
            "read_default": _git(reader, env, "rev-parse", f"refs/remotes/origin/{default}")}


@pytest.mark.parametrize("default", ["main", "trunk"])
def test_actual_workflow_input_keeps_recorded_default_beside_frozen_event_source(tmp_path, default):
    replay = _checkout_fixture(tmp_path, default=default)
    result = replay["result"]
    assert result.returncode == 0, result.stdout + result.stderr
    assert replay["HEAD"] == replay["source"]
    assert replay["read_default"] == replay["default_tip"] != replay["source"]
    assert replay["detached"]


def test_actual_workflow_input_cannot_excuse_a_genuinely_missing_clock_line(tmp_path):
    replay = _checkout_fixture(tmp_path, recorded=False)
    result = replay["result"]
    assert result.returncode == 1 and "run=1" in result.stdout and "line never reached" in result.stdout
    assert replay["HEAD"] == replay["source"] == replay["read_default"]


@pytest.mark.parametrize("case", ["protected-main", "main-behind", "renamed-default", "feature", "forged-feature"])
def test_real_guard_record_and_cage_keep_event_authority_with_detached_HEAD(monkeypatch, case):
    spec = importlib.util.spec_from_file_location("checkout_detached_consumers", GRADER)
    assert spec and spec.loader
    cr = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(cr)
    original_run = subprocess.run
    detached_at_guard: list[str] = []

    def start_detached(args, *positional, **kwargs):
        # Only fixture setup changes. The extracted production workflow shell runs unmodified
        # except its already-declared portable/offline signer substitutions.
        if args[0] == "bash" and Path(args[-1]).name == "guard.sh":
            cwd, env = kwargs["cwd"], kwargs["env"]
            original_run(["git", "checkout", "--detach", "HEAD"], cwd=cwd, env=env,
                         check=True, capture_output=True)
            state = original_run(["git", "symbolic-ref", "-q", "HEAD"], cwd=cwd, env=env,
                                 capture_output=True)
            assert state.returncode == 1
            detached_at_guard.append(str(cwd))
        return original_run(args, *positional, **kwargs)

    monkeypatch.setattr(cr.subprocess, "run", start_detached)
    result = cr.delivery_fixture(WORKFLOW, case=case)
    assert len(detached_at_guard) == 1
    assert result.default_unchanged_until_review
    if case in {"protected-main", "main-behind", "renamed-default"}:
        assert result.cage_rc == 0 and result.pending_pr
        assert result.source_parent_preserved and result.original_commit_preserved
        assert result.durable_original_preserved and result.recorded_after_review
    else:
        assert not result.pending_pr and not result.recorded_after_review
        if case == "forged-feature":
            assert result.can_prepare == "yes" and result.cage_rc == 1
        else:
            assert result.can_prepare == "no" and result.cage_rc == 0
