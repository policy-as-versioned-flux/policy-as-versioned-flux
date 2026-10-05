#!/usr/bin/env python3
"""Deliver an original signed TRUTH observation through ordinary protected-branch review.

The checkout and workflow are trusted default-branch code. Pending Git objects are
read as data only; this controller never checks them out or executes their programs.
Only a completed, default-branch truth run can be delivered. A failed gate still
has an observation to conserve. Pending delivery is never reported as recorded.
"""
from __future__ import annotations

import argparse
import datetime as dt
import importlib.util
import json
import os
import re
import subprocess
import sys
from pathlib import Path
from typing import Any, Callable
from urllib.parse import urlencode

import yaml

ROOT = Path(__file__).resolve().parents[1]
REPOSITORY = "policy-as-versioned-flux/policy-as-versioned-flux"
APP_ID = 4819564
WORKFLOW = ".github/workflows/truth.yml"
Api = Callable[[str, str, dict[str, Any] | None], Any]
Verifier = Callable[[Path, str, dict[str, Any], str], None]


class Refusal(RuntimeError):
    """A missing or changed instrument leaves the original delivery pending."""


def require(condition: bool, reason: str) -> None:
    if not condition:
        raise Refusal(reason)


def positive(value: Any, name: str) -> int:
    require(type(value) is int and value > 0, f"{name} is not a positive integer")
    return int(value)


def sha(value: Any) -> str:
    require(isinstance(value, str) and re.fullmatch(r"[0-9a-f]{40}", value) is not None,
            "head SHA is not a full Git object id")
    return str(value)


def github_api(method: str, path: str, body: dict[str, Any] | None = None) -> Any:
    """Keep read-only Actions facts separate from the existing App's write rights."""
    command = ["gh", "api", "--method", method, path]
    if body is not None:
        command.extend(["--input", "-"])
    env = {k: v for k, v in os.environ.items()
           if k not in {"GH_TOKEN", "GITHUB_TOKEN", "TRUTH_READ_TOKEN"}}
    token = os.environ.get("GH_TOKEN") or os.environ.get("GITHUB_TOKEN")
    if method == "GET" and path.lstrip("/") != "installation":
        token = os.environ.get("TRUTH_READ_TOKEN") or token
    if token:
        env["GH_TOKEN"] = token
    try:
        result = subprocess.run(command, input=None if body is None else json.dumps(body),
                                text=True, capture_output=True, timeout=60, env=env)
        require(result.returncode == 0, f"GitHub API {method} failed; delivery remains pending")
        return json.loads(result.stdout)
    except (OSError, subprocess.TimeoutExpired, json.JSONDecodeError) as error:
        raise Refusal("GitHub API cannot provide valid delivery facts; delivery remains pending") from error


def git(root: Path, *args: str, check: bool = True) -> str:
    # Fetches of this public repository need no reviewer credential. Neither the
    # App token nor a pending object's configuration is handed to Git children.
    env = {k: v for k, v in os.environ.items()
           if k not in {"GH_TOKEN", "GITHUB_TOKEN", "TRUTH_READ_TOKEN", "GIT_ASKPASS", "SSH_ASKPASS"}}
    env["GIT_TERMINAL_PROMPT"] = "0"
    try:
        result = subprocess.run(["git", "-c", "credential.helper=", "-c", "core.hooksPath=" + os.devnull,
                                 "-c", "protocol.ext.allow=never", "-C", str(root), *args],
                                text=True, capture_output=True, timeout=60, env=env)
        require(not check or result.returncode == 0,
                f"Git {args[0]} cannot establish the original observation; delivery remains pending")
        return result.stdout if result.returncode == 0 else ""
    except (OSError, subprocess.TimeoutExpired, UnicodeError) as error:
        raise Refusal("Git object cannot be read; delivery remains pending") from error


def window(root: Path, today: dt.date) -> None:
    """Reuse the recorded owner's expiry/acknowledgement check, never an env override."""
    spec = importlib.util.spec_from_file_location("delivery_enact_record", ROOT / "verify/enact-record/enact_record.py")
    require(spec is not None and spec.loader is not None, "development window instrument is missing")
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    faults = module.check(root, today)
    require((root / "twin/ENACT_MODE").read_text().strip() == "development" and not faults,
            "recorded development window is invalid or expired; observation remains pending")


def authority(root: Path, default: str, today: dt.date | None) -> None:
    """A moved default tip needs a fresh trusted checkout, never pending code execution."""
    git(root, "check-ref-format", f"refs/heads/{default}")
    git(root, "fetch", "--no-tags", "origin", f"refs/heads/{default}:refs/remotes/origin/{default}")
    require(git(root, "rev-parse", "HEAD").strip()
            == git(root, "rev-parse", f"refs/remotes/origin/{default}").strip(),
            "trusted checkout is behind current default authority; retry pending delivery from a fresh checkout")
    window(root, today or dt.datetime.now(dt.timezone.utc).date())


def verify_signature(root: Path, head: str, run: dict[str, Any], default: str) -> None:
    command = ["gitsign", "verify", head,
               f"--certificate-identity=https://github.com/{REPOSITORY}/{WORKFLOW}@refs/heads/{default}",
               "--certificate-oidc-issuer=https://token.actions.githubusercontent.com",
               f"--certificate-github-workflow-sha={run['head_sha']}",
               f"--certificate-github-workflow-repository={REPOSITORY}",
               f"--certificate-github-workflow-ref=refs/heads/{default}",
               f"--certificate-github-workflow-trigger={run['event']}"]
    try:
        env = {k: v for k, v in os.environ.items()
               if k not in {"GH_TOKEN", "GITHUB_TOKEN", "TRUTH_READ_TOKEN"}}
        result = subprocess.run(command, cwd=root, capture_output=True, timeout=120, env=env)
        require(result.returncode == 0, "original observation signature or certificate claims failed")
    except (OSError, subprocess.TimeoutExpired) as error:
        raise Refusal("gitsign cannot verify the original observation; delivery remains pending") from error


def facts(api: Api, run_id: int, attempt: int) -> tuple[dict[str, Any], str, str]:
    repo = api("GET", f"repos/{REPOSITORY}", None)
    require(repo.get("full_name") == REPOSITORY, "repository facts name another repository")
    default = repo.get("default_branch")
    require(isinstance(default, str) and bool(default), "repository has no default branch")
    # A completed workflow_run payload names its attempt. The latest run endpoint
    # can advance while delivery is queued, so it is not this observation's source.
    run = api("GET", f"repos/{REPOSITORY}/actions/runs/{run_id}/attempts/{attempt}", None)
    workflow = api("GET", f"repos/{REPOSITORY}/actions/workflows/truth.yml", None)
    require(positive(run.get("id"), "run id") == run_id, "run id changed")
    require(run.get("repository", {}).get("full_name") == REPOSITORY
            and run.get("head_repository", {}).get("full_name") == REPOSITORY,
            "run repository or head repository is foreign")
    require(run.get("path") == WORKFLOW and workflow.get("path") == WORKFLOW
            and positive(run.get("workflow_id"), "workflow id") == positive(workflow.get("id"), "workflow id"),
            "run is not this repository's truth workflow")
    require(run.get("status") == "completed" and run.get("head_branch") == default,
            "run is not completed on the default branch")
    require(run.get("event") in {"schedule", "push", "workflow_dispatch"}, "run event cannot record TRUTH")
    sha(run.get("head_sha"))
    positive(run.get("run_number"), "run number")
    require(positive(run.get("run_attempt"), "run attempt") == attempt,
            "official run attempt does not match the completed delivery event")
    return run, default, f"observations/truth/{run_id}-{attempt}"


def validate_pr(pr: dict[str, Any], default: str, branch: str, expected: str | None = None) -> str:
    positive(pr.get("number"), "PR number")
    require(pr.get("head", {}).get("repo", {}).get("full_name") == REPOSITORY
            and pr.get("base", {}).get("repo", {}).get("full_name") == REPOSITORY,
            "PR repository is foreign")
    require(pr.get("head", {}).get("ref") == branch and pr.get("base", {}).get("ref") == default,
            "PR head or base ref changed")
    require(pr.get("user", {}).get("login") == "github-actions[bot]", "PR was not proposed by the clock")
    head = sha(pr.get("head", {}).get("sha"))
    require(expected is None or head == expected, "PR head changed after observation validation")
    require(pr.get("state") == "open" or pr.get("merged") is True, "observation PR is closed unmerged")
    return head


def observation(root: Path, head: str, run: dict[str, Any], default: str, branch: str,
                *, already_merged: bool = False) -> str:
    git(root, "check-ref-format", f"refs/heads/{default}")
    git(root, "check-ref-format", f"refs/heads/{branch}")
    refs = [f"refs/heads/{default}:refs/remotes/origin/{default}"]
    if not already_merged:
        refs.append(f"refs/heads/{branch}:refs/remotes/origin/{branch}")
    git(root, "fetch", "--no-tags", "origin", *refs)
    if not already_merged:
        require(git(root, "rev-parse", f"refs/remotes/origin/{branch}").strip() == head,
                "pending ref head changed after PR validation")
    parents = git(root, "rev-list", "--parents", "-n", "1", head).split()
    require(len(parents) == 2, "observation is not one original non-merge commit")
    parent = parents[1]
    git(root, "merge-base", "--is-ancestor", parent, f"refs/remotes/origin/{default}")
    git(root, "merge-base", "--is-ancestor", run["head_sha"], parent)
    author = git(root, "show", "-s", "--format=%ae%x00%ce%x00%s", head).strip().split("\0")
    require(author == ["truth@users.noreply.github.com", "truth@users.noreply.github.com",
                       f"truth: record run {run['run_number']} [skip ci]"],
            "observation commit is not the original clock's record")
    trusted = yaml.safe_load((root / WORKFLOW).read_text())
    lane = str(trusted.get("env", {}).get("OBSERVATION_LANE", "")).split()
    ceiling = {"talk/truth.log", "drift/samples.jsonl", "talk/captures", "observations"}
    require(bool(lane) and set(lane) <= ceiling and "talk/truth.log" in lane, "trusted observation lane is invalid")
    changed = git(root, "diff-tree", "--no-commit-id", "--name-status", "--no-renames", "-r", "-z", parent, head).split("\0")
    changed = changed[:-1]
    require(bool(changed) and len(changed) % 2 == 0, "observation changed-path instrument is invalid")
    for status, path in zip(changed[::2], changed[1::2]):
        require(status in {"A", "M"} and any(path == p or path.startswith(p + "/") for p in lane),
                "observation contains a declaration, deletion or renamed path")
        entry = git(root, "ls-tree", head, "--", path).split()
        require(len(entry) >= 4 and entry[0] == "100644" and entry[1] == "blob",
                "observation contains a symlink, executable or non-file object")
    old = git(root, "show", f"{parent}:talk/truth.log")
    new = git(root, "show", f"{head}:talk/truth.log")
    require((not old or old.endswith("\n")) and new.startswith(old), "TRUTH record rewrites previous observations")
    suffix = new[len(old):]
    require(suffix.endswith("\n") and len(suffix.splitlines()) == 1 and suffix.startswith("TRUTH "),
            "observation does not append exactly one TRUTH line")
    number = re.findall(r"(?:^|\s)run=(\S+)", suffix)
    hub = re.findall(r"(?:^|\s)hub=([0-9a-f]+)(?=\s|$)", suffix)
    require(number == [str(run["run_number"])] and len(hub) == 1
            and 7 <= len(hub[0]) <= 40 and run["head_sha"].startswith(hub[0]),
            "TRUTH line does not name the measured run and source SHA")
    return suffix


def recorded(root: Path, pr: dict[str, Any], head: str, line: str, default: str) -> str:
    require(pr.get("merged") is True, "observation PR is still pending")
    merged = sha(pr.get("merge_commit_sha"))
    git(root, "fetch", "--no-tags", "origin", f"refs/heads/{default}:refs/remotes/origin/{default}")
    git(root, "merge-base", "--is-ancestor", head, merged)
    git(root, "merge-base", "--is-ancestor", merged, f"refs/remotes/origin/{default}")
    log = git(root, "show", f"refs/remotes/origin/{default}:talk/truth.log")
    require(log.splitlines(keepends=True).count(line) == 1, "default branch does not conserve the exact original TRUTH line")
    return f"RECORDED original observation {head} through PR #{pr['number']} on {default}"


def deliver(root: Path, run_id: int, *, api: Api = github_api, verify: Verifier = verify_signature,
            today: dt.date | None = None, check_only: bool = False, attempt: int = 1) -> str:
    positive(run_id, "run id")
    positive(attempt, "run attempt")
    run, default, branch = facts(api, run_id, attempt)
    authority(root, default, today)
    query = urlencode({"state": "all", "head": REPOSITORY.split("/")[0] + ":" + branch,
                       "base": default, "per_page": 100})
    prs = api("GET", f"repos/{REPOSITORY}/pulls?{query}", None)
    require(isinstance(prs, list) and len(prs) == 1, "expected exactly one pending observation PR")
    require(isinstance(prs[0], dict), "PR list did not provide a delivery record")
    number = positive(prs[0].get("number"), "PR number")
    endpoint = f"repos/{REPOSITORY}/pulls/{number}"
    # List responses carry merged_at rather than the full PR's merged boolean.
    # Read the authoritative detail before judging either pending or idempotent delivery.
    pr = api("GET", endpoint, None)
    head = validate_pr(pr, default, branch)
    line = observation(root, head, run, default, branch, already_merged=pr.get("merged") is True)
    verify(root, head, run, default)
    fresh = api("GET", endpoint, None)
    validate_pr(fresh, default, branch, head)
    if fresh.get("merged") is True:
        return recorded(root, fresh, head, line, default)
    if check_only:
        authority(root, default, today)
        return f"VERIFIED original observation {head}; PR #{pr['number']} remains pending review"
    installation = api("GET", "installation", None)
    require(installation.get("app_id") == APP_ID, "review credential is not the existing other-hand App")
    fresh = api("GET", endpoint, None)
    validate_pr(fresh, default, branch, head)
    authority(root, default, today)
    review = api("POST", endpoint + "/reviews", {"commit_id": head, "event": "APPROVE",
        "body": "Verified original signed TRUTH observation and protected delivery."})
    require(review.get("state") == "APPROVED" and review.get("commit_id") == head,
            "other-hand review did not approve the original observation head")
    fresh = api("GET", endpoint, None)
    validate_pr(fresh, default, branch, head)
    authority(root, default, today)
    merged = api("PUT", endpoint + "/merge", {"sha": head, "merge_method": "merge"})
    require(merged.get("merged") is True, "ordinary merge was refused; original observation remains pending")
    fresh = api("GET", endpoint, None)
    validate_pr(fresh, default, branch, head)
    require(fresh.get("merge_commit_sha") == merged.get("sha"), "PR merge receipt changed; verify pending delivery")
    return recorded(root, fresh, head, line, default)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-id", type=int, required=True)
    parser.add_argument("--attempt", type=int, required=True)
    parser.add_argument("--check-only", action="store_true")
    args = parser.parse_args()
    try:
        print(deliver(ROOT, args.run_id, attempt=args.attempt, check_only=args.check_only))
        return 0
    except (Refusal, OSError, ValueError, KeyError, TypeError, yaml.YAMLError) as error:
        # API/Git transports deliberately replace error bodies with safe messages.
        print(f"PENDING: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
