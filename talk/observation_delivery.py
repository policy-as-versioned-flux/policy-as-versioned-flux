#!/usr/bin/env python3
"""Deliver original signed observations through ordinary protected-branch review.

The checkout and workflow are trusted default-branch code. Pending Git objects are
read as data only; this controller never checks them out or executes their programs.
Only completed default-branch runs of the seven closed profiles can be delivered.
A failed measurement still has an observation to conserve. Pending delivery is never reported as recorded.
"""
from __future__ import annotations

import argparse
import datetime as dt
from dataclasses import dataclass
import tempfile
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

try:
    import delivery_truth_integration as truth_integration
except ImportError:
    from talk import truth_integration

ROOT = Path(__file__).resolve().parents[1]
HUB_URL = "https://github.com/policy-as-versioned-flux/policy-as-versioned-flux.git"
REPOSITORY = "policy-as-versioned-flux/policy-as-versioned-flux"
APP_ID = 4819564
# The bot user is a separate GitHub object from App 4819564. Both its public
# user record and a narrow installation-token viewer query bind this identity.
APP_BOT_LOGIN = "pavc-other-hand[bot]"
APP_BOT_USER_ID = 324560547
WORKFLOW = ".github/workflows/truth.yml"
Api = Callable[[str, str, dict[str, Any] | None], Any]
Verifier = Callable[[Path, str, dict[str, Any], str], None]


@dataclass(frozen=True)
class Profile:
    repository: str
    clock: str
    lanes: tuple[str, ...]
    email: str
    subject: str
    payload: str
    events: tuple[str, ...] = ("schedule", "workflow_dispatch")

    @property
    def workflow(self) -> str:
        return f".github/workflows/{self.clock}.yml"

    @property
    def org(self) -> str:
        return self.repository.split("/")[1]


TRUTH = Profile(REPOSITORY, "truth", ("talk/truth.log", "drift/samples.jsonl", "talk/captures", "observations"),
                "truth@users.noreply.github.com", "truth: record run {number} [skip ci]", "truth",
                ("schedule", "push", "workflow_dispatch"))
PROFILES = {(TRUTH.repository, TRUTH.clock): TRUTH}
for _org in ("driftwood", "tuppence", "ludlow"):
    _repository = f"policy-as-versioned-{_org}/{_org}"
    for _clock in ("drift-sample", "twin-sweep"):
        _drift = _clock == "drift-sample"
        _profile = Profile(_repository, _clock,
            ("drift/samples.jsonl", "drift/workload-samples.jsonl", "drift/oscal-samples.jsonl") if _drift
            else ("observations/twin-sweep.jsonl",),
            f"{_clock}@policy-as-versioned-{_org}.invalid",
            "drift sample: five facts on an ephemeral cluster [skip ci]" if _drift else
            "twin sweep: observe the forward-intel scenario [skip ci]" if _org == "driftwood" else
            "twin sweep: record the emitter observation [skip ci]",
            "drift" if _drift else "forward" if _org == "driftwood" else "emitter")
        PROFILES[(_repository, _clock)] = _profile
Evidence = str | dict[str, tuple[str, str]]


def select_profile(repository: str, workflow: str) -> Profile:
    clock = workflow.removeprefix(".github/workflows/").removesuffix(".yml")
    profile = PROFILES.get((repository, clock))
    require(profile is not None, "no trusted observation profile for this repository and workflow")
    assert profile is not None
    return profile


class Refusal(RuntimeError):
    """A missing or changed instrument leaves the original delivery pending."""


def require(condition: bool, reason: str) -> None:
    if not condition:
        raise Refusal(reason)


def mapping(value: Any, name: str) -> dict[str, Any]:
    require(isinstance(value, dict), f"{name} is not a JSON object")
    return dict(value)


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
           if k not in {"GH_TOKEN", "GITHUB_TOKEN", "TRUTH_READ_TOKEN", "PAVC_OTHER_HAND_PRIVATE_KEY"}}
    token = os.environ.get("GH_TOKEN") or os.environ.get("GITHUB_TOKEN")
    if method == "GET":
        token = os.environ.get("TRUTH_READ_TOKEN") or token
    if token:
        env["GH_TOKEN"] = token
    try:
        result = subprocess.run(command, input=None if body is None else json.dumps(body),
                                text=True, capture_output=True, timeout=60, env=env)
        require(result.returncode == 0, f"GitHub API {method} {path} failed; delivery remains pending")
        return json.loads(result.stdout)
    except (OSError, subprocess.TimeoutExpired, json.JSONDecodeError) as error:
        raise Refusal("GitHub API cannot provide valid delivery facts; delivery remains pending") from error


def git(root: Path, *args: str, check: bool = True) -> str:
    # Fetches of this public repository need no reviewer credential. Neither the
    # App token nor a pending object's configuration is handed to Git children.
    env = {k: v for k, v in os.environ.items()
           if k not in {"GH_TOKEN", "GITHUB_TOKEN", "TRUTH_READ_TOKEN", "PAVC_OTHER_HAND_PRIVATE_KEY", "GIT_ASKPASS", "SSH_ASKPASS"}}
    env["GIT_TERMINAL_PROMPT"] = "0"
    try:
        result = subprocess.run(["git", "-c", "credential.helper=", "-c", "core.hooksPath=" + os.devnull,
                                 "-c", "protocol.ext.allow=never", "-C", str(root), *args],
                                capture_output=True, timeout=60, env=env)
        require(not check or result.returncode == 0,
                f"Git {args[0]} cannot establish the original observation; delivery remains pending")
        return result.stdout.decode("utf-8") if result.returncode == 0 else ""
    except (OSError, subprocess.TimeoutExpired, UnicodeError) as error:
        raise Refusal("Git object cannot be read; delivery remains pending") from error


def window(root: Path, today: dt.date) -> None:
    """Reuse the recorded owner's expiry/acknowledgement check, never an env override."""
    try:
        import delivery_enact_record as module
    except ImportError:
        module = None
    spec = importlib.util.spec_from_file_location("delivery_enact_record", ROOT / "verify/enact-record/enact_record.py")
    if module is None:
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


def verify_signature(root: Path, head: str, run: dict[str, Any], default: str, *, profile: Profile = TRUTH,
                     require_name: bool = False) -> None:
    command = ["gitsign", "verify", head,
               f"--certificate-identity=https://github.com/{profile.repository}/{profile.workflow}@refs/heads/{default}",
               "--certificate-oidc-issuer=https://token.actions.githubusercontent.com",
               f"--certificate-github-workflow-sha={run['head_sha']}",
               f"--certificate-github-workflow-repository={profile.repository}",
               f"--certificate-github-workflow-ref=refs/heads/{default}",
               f"--certificate-github-workflow-trigger={run['event']}"]
    if require_name:
        command.append(f'--certificate-github-workflow-name={profile.clock}')
    try:
        env = {k: v for k, v in os.environ.items()
               if k not in {"GH_TOKEN", "GITHUB_TOKEN", "TRUTH_READ_TOKEN", "PAVC_OTHER_HAND_PRIVATE_KEY"}}
        result = subprocess.run(command, cwd=root, capture_output=True, timeout=120, env=env)
        require(result.returncode == 0, "original observation signature or certificate claims failed")
    except (OSError, subprocess.TimeoutExpired) as error:
        raise Refusal("gitsign cannot verify the original observation; delivery remains pending") from error


def facts(api: Api, run_id: int, attempt: int, *, profile: Profile = TRUTH) -> tuple[dict[str, Any], str, str]:
    repo = mapping(api("GET", f"repos/{profile.repository}", None), "repository facts")
    require(repo.get("full_name") == profile.repository, "repository facts name another repository")
    default = repo.get("default_branch")
    require(isinstance(default, str) and bool(default), "repository has no default branch")
    default = str(default)
    # A completed workflow_run payload names its attempt. The latest run endpoint
    # can advance while delivery is queued, so it is not this observation's source.
    run = mapping(api("GET", f"repos/{profile.repository}/actions/runs/{run_id}/attempts/{attempt}", None), "official run")
    workflow = mapping(api("GET", f"repos/{profile.repository}/actions/workflows/{profile.clock}.yml", None), "workflow facts")
    require(positive(run.get("id"), "run id") == run_id, "run id changed")
    require(mapping(run.get("repository"), "run repository").get("full_name") == profile.repository
            and mapping(run.get("head_repository"), "run head repository").get("full_name") == profile.repository,
            "run repository or head repository is foreign")
    require(run.get("path") == profile.workflow and workflow.get("path") == profile.workflow
            and positive(run.get("workflow_id"), "workflow id") == positive(workflow.get("id"), "workflow id"),
            "run is not this repository's truth workflow")
    require(run.get("status") == "completed" and run.get("head_branch") == default,
            "run is not completed on the default branch")
    require(run.get("event") in profile.events, "run event cannot record TRUTH")
    sha(run.get("head_sha"))
    positive(run.get("run_number"), "run number")
    require(positive(run.get("run_attempt"), "run attempt") == attempt,
            "official run attempt does not match the completed delivery event")
    return run, default, f"observations/{profile.clock}/{run_id}-{attempt}"


def validate_pr(pr: dict[str, Any], default: str, branch: str, expected: str | None = None, *, profile: Profile = TRUTH) -> str:
    pr = mapping(pr, "PR facts")
    positive(pr.get("number"), "PR number")
    require(mapping(mapping(pr.get("head"), "PR head").get("repo"), "PR head repository").get("full_name") == profile.repository
            and mapping(mapping(pr.get("base"), "PR base").get("repo"), "PR base repository").get("full_name") == profile.repository,
            "PR repository is foreign")
    require(pr.get("head", {}).get("ref") == branch and pr.get("base", {}).get("ref") == default,
            "PR head or base ref changed")
    require(mapping(pr.get("user"), "PR actor").get("login") == "github-actions[bot]", "PR was not proposed by the clock")
    head = sha(pr.get("head", {}).get("sha"))
    require(expected is None or head == expected, "PR head changed after observation validation")
    require(pr.get("state") == "open" or pr.get("merged") is True, "observation PR is closed unmerged")
    return head


def observation(root: Path, head: str, run: dict[str, Any], default: str, branch: str,
                *, already_merged: bool = False, profile: Profile = TRUTH) -> Evidence:
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
    require(author == [profile.email, profile.email, profile.subject.format(number=run["run_number"])],
            "observation commit is not the original clock's record")
    trusted = mapping(yaml.safe_load((root / profile.workflow).read_text()), "trusted workflow")
    lane = str(mapping(trusted.get("env"), "trusted workflow environment").get("OBSERVATION_LANE", "")).split()
    ceiling = set(profile.lanes)
    require(bool(lane) and set(lane) <= ceiling
            and ("talk/truth.log" in lane if profile.payload == "truth" else set(lane) == ceiling),
            "trusted observation lane is invalid")
    changed = git(root, "diff-tree", "--no-commit-id", "--name-status", "--no-renames", "-r", "-z", parent, head).split("\0")
    changed = changed[:-1]
    require(bool(changed) and len(changed) % 2 == 0, "observation changed-path instrument is invalid")
    for status, path in zip(changed[::2], changed[1::2]):
        require(status in {"A", "M"} and any(path == p or path.startswith(p + "/") for p in lane),
                "observation contains a declaration, deletion or renamed path")
        entry = git(root, "ls-tree", head, "--", path).split()
        require(len(entry) >= 4 and entry[0] == "100644" and entry[1] == "blob",
                "observation contains a symlink, executable or non-file object")
    if profile.payload != "truth":
        require(set(changed[1::2]) == set(profile.lanes), "observation omits or adds a profiled log")
        evidence: dict[str, tuple[str, str]] = {}
        statuses = dict(zip(changed[1::2], changed[::2]))
        for path in profile.lanes:
            prior = "" if statuses[path] == "A" else git(root, "show", f"{parent}:{path}")
            current = git(root, "show", f"{head}:{path}")
            suffix = appended(prior, current)
            evidence[path] = prior, suffix
        validate_payload(root, parent, run, profile, evidence)
        return evidence
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


def recorded(root: Path, pr: dict[str, Any], head: str, line: Evidence, default: str) -> str:
    require(pr.get("merged") is True, "observation PR is still pending")
    merged = sha(pr.get("merge_commit_sha"))
    git(root, "fetch", "--no-tags", "origin", f"refs/heads/{default}:refs/remotes/origin/{default}")
    git(root, "merge-base", "--is-ancestor", head, merged)
    git(root, "merge-base", "--is-ancestor", merged, f"refs/remotes/origin/{default}")
    if isinstance(line, str):
        log = git(root, "show", f"refs/remotes/origin/{default}:talk/truth.log")
        require(log.splitlines(keepends=True).count(line) == 1,
                "default branch does not conserve the exact original TRUTH line")
    else:
        for path, (prefix, suffix) in line.items():
            log = git(root, "show", f"refs/remotes/origin/{default}:{path}")
            require(log.startswith(prefix) and log.count(suffix) == 1
                    and all(log.splitlines(keepends=True).count(row) == 1 for row in suffix.splitlines(keepends=True)),
                    "default branch does not conserve original observation bytes")
    return f"RECORDED original observation {head} through PR #{pr['number']} on {default}"


@dataclass
class Pending:
    run: dict[str, Any]
    default: str
    branch: str
    pr: dict[str, Any]
    original: str
    line: Evidence
    guard: Callable[[], None]


def isolated_writer_skipped(root: Path, run: dict[str, Any], default: str,
                            profile: Profile, api: Api) -> bool:
    """Prove a twin run expected no PR, without reading or executing its artifact."""
    if profile.clock != "twin-sweep" or run.get("conclusion") != "success":
        return False
    source = sha(run["head_sha"])
    git(root, "merge-base", "--is-ancestor", source, "refs/remotes/origin/" + default)

    def data(path: str) -> str:
        entry = git(root, "ls-tree", source, "--", path).split()
        require(len(entry) >= 4 and entry[:2] == ["100644", "blob"],
                "no-writer source declaration is not a regular data file")
        return git(root, "show", f"{source}:{path}")

    workflow = mapping(yaml.load(data(profile.workflow), Loader=yaml.BaseLoader), "source workflow")
    jobs = mapping(workflow.get("jobs"), "source workflow jobs")
    twin = mapping(jobs.get("twin"), "source twin job")
    writer = mapping(jobs.get("write"), "source writer job")
    expected_guard = ("needs.twin.outputs.agent_rung != 'isolated' && "
                      "github.ref_name == github.event.repository.default_branch")
    require(set(jobs) == {"twin", "write"} and writer.get("needs") == "twin"
            and " ".join(str(writer.get("if", "")).split()) == expected_guard
            and mapping(twin.get("outputs"), "source twin outputs").get("agent_rung")
            == "${{ steps.cage.outputs.rung }}", "source workflow has no recognised isolated writer guard")
    evidence = mapping(json.loads(data("composed/evidence.json"), object_pairs_hook=unique_object),
                       "source priced evidence")
    prices = evidence.get("prices")
    require(isinstance(prices, list), "source priced evidence has no prices")
    assert isinstance(prices, list)  # Runtime require() is not a static type guard.
    selected = [row for row in prices if isinstance(row, dict)
                and row.get("kind") == "agent-cage" and row.get("subject") == "twin-agent"]
    require(len(selected) == 1 and selected[0].get("proposed_tier") == "isolated",
            "source does not explicitly price the twin writer at isolated")
    endpoint = (f"repos/{profile.repository}/actions/runs/{run['id']}/attempts/"
                f"{run['run_attempt']}/jobs?per_page=100")
    facts = mapping(api("GET", endpoint, None), "official attempt jobs")
    attempts = facts.get("jobs")
    require(type(facts.get("total_count")) is int and facts["total_count"] == 2
            and isinstance(attempts, list) and len(attempts) == 2,
            "official attempt jobs are incomplete or ambiguous")
    assert isinstance(attempts, list)  # The same validated shape must narrow for mypy.
    by_name: dict[str, dict[str, Any]] = {}
    for item in attempts:
        job = mapping(item, "official attempt job")
        name = job.get("name")
        require(isinstance(name, str) and name in {"twin", "write"} and name not in by_name,
                "official attempt jobs have unknown or duplicate names")
        require(positive(job.get("run_id"), "job run id") == run["id"]
                and positive(job.get("run_attempt"), "job run attempt") == run["run_attempt"]
                and job.get("head_sha") == source and job.get("head_branch") == default
                and job.get("workflow_name") == profile.clock and job.get("status") == "completed",
                "official attempt job is not bound to this completed source run")
        by_name[str(name)] = job
    return by_name["twin"].get("conclusion") == "success" and by_name["write"].get("conclusion") == "skipped"


def pending(root: Path, run_id: int, attempt: int, profile: Profile, api: Api,
            verify: Verifier | None, today: dt.date | None, authority_root: Path | None = None,
            require_name: bool = False) -> Pending | None:
    positive(run_id, "run id")
    positive(attempt, "run attempt")
    run, default, branch = facts(api, run_id, attempt, profile=profile)
    guard = delivery_authority(root, default, today, profile, authority_root, api)
    guard()
    query = urlencode({"state": "all", "head": profile.repository.split("/")[0] + ":" + branch,
                       "base": default, "per_page": 100})
    prs = api("GET", f"repos/{profile.repository}/pulls?{query}", None)
    if prs == [] and isolated_writer_skipped(root, run, default, profile, api):
        return None
    require(isinstance(prs, list) and len(prs) == 1, "expected exactly one pending observation PR")
    require(isinstance(prs[0], dict), "PR list did not provide a delivery record")
    number = positive(prs[0].get("number"), "PR number")
    endpoint = f"repos/{profile.repository}/pulls/{number}"
    # List responses carry merged_at rather than the full PR's merged boolean.
    # Read the authoritative detail before judging either pending or idempotent delivery.
    pr = api("GET", endpoint, None)
    head = validate_pr(pr, default, branch, profile=profile)
    line = observation(root, head, run, default, branch,
                       already_merged=pr.get("merged") is True and not require_name, profile=profile)
    if verify is None:
        verify_signature(root, head, run, default, profile=profile, require_name=require_name)
    else:
        verify(root, head, run, default)
    return Pending(run, default, branch, pr, head, line, guard)


def integration_pr(api: Api, branch: str, default: str) -> dict[str, Any] | None:
    query = urlencode({'state': 'all', 'head': REPOSITORY.split('/')[0] + ':' + branch,
                       'base': default, 'per_page': 100})
    rows = api('GET', f'repos/{REPOSITORY}/pulls?{query}', None)
    require(isinstance(rows, list) and len(rows) <= 1, 'expected at most one exact integration PR')
    if not rows:
        return None
    row = mapping(rows[0], 'integration PR')
    return mapping(api('GET', f'repos/{REPOSITORY}/pulls/{positive(row.get("number"), "PR number")}', None),
                   'integration PR')


def publish_integration(root: Path, branch: str, head: str) -> None:
    """The no-App preparation job may create exactly one absent integration ref."""
    import base64

    env = {key: value for key, value in os.environ.items()
           if key not in {'GH_TOKEN', 'GITHUB_TOKEN', 'TRUTH_READ_TOKEN', 'PAVC_OTHER_HAND_PRIVATE_KEY',
                          'GIT_ASKPASS', 'SSH_ASKPASS'} and not key.startswith('GIT_CONFIG_')}
    token = os.environ.get('GH_TOKEN') or os.environ.get('GITHUB_TOKEN')
    if token:
        encoded = base64.b64encode(('x-access-token:' + token).encode()).decode()
        env.update(GIT_CONFIG_COUNT='1', GIT_CONFIG_KEY_0='http.https://github.com/.extraheader',
                   GIT_CONFIG_VALUE_0='AUTHORIZATION: basic ' + encoded)
    ref = 'refs/heads/' + branch
    try:
        result = subprocess.run(['git', '-c', 'credential.helper=', '-c', 'core.hooksPath=' + os.devnull,
                                 '-c', 'protocol.ext.allow=never', '-C', str(root), 'push',
                                 '--force-with-lease=' + ref + ':', 'origin', head + ':' + ref],
                                capture_output=True, env=env, timeout=60)
        require(result.returncode == 0, 'create-only integration publication refused; original remains pending')
    except (OSError, subprocess.TimeoutExpired) as error:
        raise Refusal('integration publication instrument unavailable; original remains pending') from error


def validate_integration_merge(root: Path, merged: str, plan: truth_integration.Integration, head: str) -> None:
    require(git(root, 'show', '-s', '--format=%P', merged).split() == [plan.base, head]
            and git(root, 'rev-parse', merged + '^{tree}').strip() == plan.tree,
            'ordinary merge did not conserve the reviewed integration tree and parents')


def already_integrated(root: Path, item: Pending, api: Api) -> str | None:
    if not truth_integration.ancestor(root, item.original, 'refs/remotes/origin/' + item.default):
        return None
    assert isinstance(item.line, str)
    log = git(root, 'show', f'refs/remotes/origin/{item.default}:talk/truth.log')
    require(log.splitlines(keepends=True).count(item.line) == 1,
            'default branch does not conserve the exact original TRUTH line once')
    # An earlier PUT can succeed against an unexpected base after the last guard.
    # Ancestry/one row alone must not erase that strict failure on the next retry.
    prefix = f'integrations/truth/{item.run["id"]}-{item.run["run_attempt"]}/'
    refs = api('GET', f'repos/{REPOSITORY}/git/matching-refs/heads/{prefix}', None)
    require(isinstance(refs, list), 'recorded integration ref instrument is invalid')
    verified = False
    for row in refs:
        ref = mapping(row, 'integration ref')
        name = ref.get('ref')
        require(isinstance(name, str) and name.startswith('refs/heads/' + prefix), 'integration ref changed')
        assert isinstance(name, str)
        base = sha(name.removeprefix('refs/heads/' + prefix))
        branch = name.removeprefix('refs/heads/')
        head = sha(mapping(ref.get('object'), 'integration object').get('sha'))
        pr = integration_pr(api, branch, item.default)
        if pr is None or pr.get('merged') is not True:
            continue
        validate_pr(pr, item.default, branch, head)
        plan = truth_integration.plan(root, base, item.original, item.line,
                                      item.run['id'], item.run['run_attempt'])
        plan.validate(root, head)
        merged = sha(pr.get('merge_commit_sha'))
        git(root, 'merge-base', '--is-ancestor', merged, 'refs/remotes/origin/' + item.default)
        validate_integration_merge(root, merged, plan, head)
        verified = True
    if not verified:
        # Clean original PRs retain their direct path, but its historical merge
        # must conserve the full signed capture snapshot, not a mixed Git merge.
        require(item.pr.get('merged') is True, 'recorded integration has no immutable delivery ref receipt')
        merged = sha(item.pr.get('merge_commit_sha'))
        parents = git(root, 'rev-list', '--parents', '-n', '1', merged).split()
        require(len(parents) == 3 and parents[2] == item.original,
                'direct original merge did not conserve the original parent')
        direct = truth_integration.plan(root, parents[1], item.original, item.line,
                                        item.run['id'], item.run['run_attempt'])
        git(root, 'merge-base', '--is-ancestor', merged, 'refs/remotes/origin/' + item.default)
        validate_integration_merge(root, merged, direct, item.original)
        return f'RECORDED original observation {item.original} on {item.default}'
    return f'RECORDED original observation {item.original} on {item.default}'


def prepare_truth(root: Path, run_id: int, *, api: Api = github_api, verify: Verifier | None = None,
                  today: dt.date | None = None, attempt: int = 1) -> str:
    item = pending(root, run_id, attempt, TRUTH, api, verify, today, require_name=True)
    assert item is not None  # TRUTH always requires its original observation.
    item.guard()
    recorded_line = already_integrated(root, item, api)
    if recorded_line:
        return recorded_line
    require(item.pr.get('merged') is not True, 'merged observation needs fresh default authority validation')
    base = git(root, 'rev-parse', 'HEAD').strip()
    assert isinstance(item.line, str)
    plan = truth_integration.plan(root, base, item.original, item.line, run_id, attempt)
    if truth_integration.merged_tree(root, base, item.original) == plan.tree:
        return f'READY original observation {item.original}; ordinary review remains pending'
    matches = api('GET', f'repos/{REPOSITORY}/git/matching-refs/heads/{plan.branch}', None)
    require(isinstance(matches, list) and len(matches) <= 1, 'integration ref instrument is ambiguous')
    if matches:
        match = mapping(matches[0], 'integration ref')
        require(match.get('ref') == 'refs/heads/' + plan.branch, 'integration ref name changed')
        head = sha(mapping(match.get('object'), 'integration ref object').get('sha'))
        git(root, 'fetch', '--no-tags', 'origin', 'refs/heads/' + plan.branch)
        plan.validate(root, head)
    else:
        head = plan.commit(root)
        item.guard()
        fresh = api('GET', f'repos/{REPOSITORY}/pulls/{item.pr["number"]}', None)
        validate_pr(fresh, item.default, item.branch, item.original)
        git(root, 'fetch', '--no-tags', 'origin', 'refs/heads/' + item.branch)
        require(git(root, 'rev-parse', 'FETCH_HEAD').strip() == item.original, 'raw observation ref changed')
        publish_integration(root, plan.branch, head)
    item.guard()
    pr = integration_pr(api, plan.branch, item.default)
    if pr is None:
        pr = mapping(api('POST', f'repos/{REPOSITORY}/pulls', {
            'head': plan.branch, 'base': item.default,
            'title': f'Integrate original TRUTH run {item.run["run_number"]}',
            'body': ('Delivery integration only; not a new measurement.\n\n'
                     f'Original signed observation: {item.original}\n'
                     f'Official run/attempt: {run_id}/{attempt}\nBase: {base}\nExpected tree: {plan.tree}\n'
                     'Preserves the exact signed row and capture blobs through separate App review.\n'),
        }), 'created integration PR')
    validate_pr(pr, item.default, plan.branch, head)
    require(pr.get('merged') is not True, 'integration already merged; retry from fresh default authority')
    return f'PREPARED unsigned delivery integration {head}; PR #{pr["number"]} remains pending separate review'


def deliver(root: Path, run_id: int, *, api: Api = github_api, verify: Verifier | None = None,
            today: dt.date | None = None, check_only: bool = False, attempt: int = 1,
            repository: str = REPOSITORY, workflow: str = WORKFLOW, authority_root: Path | None = None,
            review_integration: bool = False) -> str:
    profile = select_profile(repository, workflow)
    require(not review_integration or profile == TRUTH, 'integration review is restricted to the TRUTH profile')
    item = pending(root, run_id, attempt, profile, api, verify, today, authority_root,
                   require_name=review_integration)
    if item is None:
        return "SKIP: no delivery expected; the explicitly isolated twin writer was skipped; no observation recorded"
    run, default, branch, pr, head, line, guard = (item.run, item.default, item.branch, item.pr,
                                                item.original, item.line, item.guard)
    original = head
    plan = None
    if review_integration:
        recorded_line = already_integrated(root, item, api)
        if recorded_line:
            guard()
            return recorded_line
        base = git(root, 'rev-parse', 'HEAD').strip()
        assert isinstance(line, str)
        plan = truth_integration.plan(root, base, original, line, run_id, attempt)
        integration_branch = f'integrations/truth/{run_id}-{attempt}/{base}'
        candidate = integration_pr(api, integration_branch, default)
        require(candidate is not None or truth_integration.merged_tree(root, base, original) == plan.tree,
                'current default needs fresh integration preparation; original remains pending')
        if candidate is not None:
            assert isinstance(line, str)
            head = validate_pr(candidate, default, integration_branch)
            git(root, 'fetch', '--no-tags', 'origin', 'refs/heads/' + integration_branch)
            require(git(root, 'rev-parse', 'FETCH_HEAD').strip() == head, 'integration ref head changed')
            plan.validate(root, head)
            original_guard = guard

            def integration_guard() -> None:
                original_guard()
                raw_pr = api('GET', f'repos/{REPOSITORY}/pulls/{item.pr["number"]}', None)
                validate_pr(raw_pr, default, item.branch, original)
                git(root, 'fetch', '--no-tags', 'origin', 'refs/heads/' + item.branch)
                require(git(root, 'rev-parse', 'FETCH_HEAD').strip() == original, 'raw observation ref changed')
                assert plan is not None
                plan.validate(root, head)

            guard = integration_guard
            pr, branch = candidate, integration_branch
    endpoint = f'repos/{profile.repository}/pulls/{pr["number"]}'
    fresh = api("GET", endpoint, None)
    validate_pr(fresh, default, branch, head, profile=profile)
    if fresh.get("merged") is True:
        require(not review_integration, 'PR merged after validation; retry from fresh default authority')
        return recorded(root, fresh, original, line, default)
    if check_only:
        guard()
        return f"VERIFIED original observation {original}; PR #{pr['number']} remains pending review"
    # Installation tokens cannot GET /app, and GET /installation is not an
    # identity endpoint. The authenticated viewer query uses the writer token;
    # repository and Actions reads continue to use the separate read-only token.
    identity = api("POST", "graphql", {"query": "query { viewer { login databaseId } }"})
    reason = f"review credential does not establish the existing other-hand App {APP_ID}"
    require(isinstance(identity, dict) and not identity.get("errors"), reason)
    data = identity.get("data")
    require(isinstance(data, dict), reason)
    viewer = data.get("viewer")
    require(isinstance(viewer, dict) and viewer.get("login") == APP_BOT_LOGIN
            and viewer.get("databaseId") == APP_BOT_USER_ID, reason)
    fresh = api("GET", endpoint, None)
    validate_pr(fresh, default, branch, head, profile=profile)
    guard()
    review = mapping(api("POST", endpoint + "/reviews", {"commit_id": head, "event": "APPROVE",
        "body": ("Verified original signed TRUTH observation and protected delivery." if profile == TRUTH
                 else "Verified original signed observation and protected delivery.")}), "review receipt")
    reviewer = review.get("user")
    require(review.get("state") == "APPROVED" and review.get("commit_id") == head
            and isinstance(reviewer, dict) and reviewer.get("login") == APP_BOT_LOGIN
            and reviewer.get("id") == APP_BOT_USER_ID,
            "other-hand review did not approve the original observation head")
    fresh = api("GET", endpoint, None)
    validate_pr(fresh, default, branch, head, profile=profile)
    guard()
    merged = mapping(api("PUT", endpoint + "/merge", {"sha": head, "merge_method": "merge"}), "merge receipt")
    require(merged.get("merged") is True, "ordinary merge was refused; original observation remains pending")
    fresh = api("GET", endpoint, None)
    validate_pr(fresh, default, branch, head, profile=profile)
    require(fresh.get("merge_commit_sha") == merged.get("sha"), "PR merge receipt changed; verify pending delivery")
    if plan is not None:
        git(root, 'fetch', '--no-tags', 'origin', f'refs/heads/{default}:refs/remotes/origin/{default}')
        validate_integration_merge(root, sha(merged['sha']), plan, head)
    return recorded(root, fresh, original, line, default)


def appended(before: str, after: str) -> str:
    require((not before or before.endswith("\n")) and after.startswith(before),
            "observation rewrites historical bytes")
    suffix = after[len(before):]
    require(bool(suffix) and suffix.endswith("\n") and all(suffix.splitlines()),
            "observation does not append complete JSONL rows")
    return suffix


def unique_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        require(key not in result, "observation JSON repeats a field")
        result[key] = value
    return result


def json_rows(text: str) -> list[dict[str, Any]]:
    def invalid(value: str) -> Any:
        raise Refusal("observation JSON contains a non-finite number")
    try:
        rows = [json.loads(line, object_pairs_hook=unique_object, parse_constant=invalid)
                for line in text.splitlines()]
    except json.JSONDecodeError as error:
        raise Refusal("observation JSONL contains a malformed row") from error
    require(all(isinstance(row, dict) for row in rows), "observation JSON row is not an object")
    return rows


def timestamp(row: dict[str, Any], key: str) -> str:
    value = row.get(key)
    require(isinstance(value, str) and re.fullmatch(r"\d{4}-\d\d-\d\dT\d\d:\d\d:\d\dZ", value) is not None,
            "observation timestamp is not UTC")
    try:
        dt.datetime.strptime(str(value), "%Y-%m-%dT%H:%M:%SZ")
    except ValueError as error:
        raise Refusal("observation timestamp is not a real UTC date") from error
    return str(value)


def keys(row: dict[str, Any], required: set[str], optional: set[str] | None = None) -> None:
    require(required <= set(row) <= required | (optional or set()), "observation schema fields do not match its profile")


FACTS = {
    "fact_1_ready_at_the_pin_on_the_real_remote",
    "fact_2_tag_signature_verified_at_the_source_boundary",
    "fact_3_last_applied_revision_equals_the_pinned_commit",
    "fact_4_rendered_objects_byte_equal_to_an_offline_render",
    "fact_5_every_rendered_object_is_in_the_flux_inventory",
    "fact_6_the_bottom_rung_is_admitted_and_runs",
    "fact_7_the_bottom_rung_reaches_nothing_while_the_reference_reaches",
}
FALSIFIERS = {
    "cluster_side_verification_passes_a_tag_that_identity_pinned_ci_rejects",
    "verified_source_ready_but_the_object_is_absent_or_unequal_and_unhealed",
}


def typed_readings(readings: Any, names: set[str], field: str) -> bool:
    return (isinstance(readings, dict) and set(readings) == names
            and all(isinstance(value, dict) and field in value
                    and (value[field] is None or type(value[field]) is bool)
                    and isinstance(value.get("why"), str) for value in readings.values()))


def validate_cloud_sources(root: Path, parent: str, sources: Any) -> None:
    """Bind TU's existing six-field provenance to its measured source's exact pin.

    The collector introduced this field when it began reading the selected cloud
    composition. Historical rows omit it. A tag or current checkout must never
    select the metadata against which an original observation is judged.
    """
    require(isinstance(sources, list), "cloud component sources must be a list")
    documents = list(yaml.safe_load_all(git(root, "show", f"{parent}:gitops/composed/composed-set.yaml")))
    matches = [doc for doc in documents if isinstance(doc, dict)
               and doc.get("kind") == "GitRepository"
               and isinstance(doc.get("metadata"), dict)
               and doc["metadata"].get("name") == "tuppence-composed"]
    require(len(matches) == 1, "cloud component sources have no unique selected composition")
    spec = mapping(matches[0].get("spec"), "selected composition source")
    require(spec.get("url") in ("https://github.com/policy-as-versioned-tuppence/tuppence",
                                "https://github.com/policy-as-versioned-tuppence/tuppence.git"),
            "cloud component sources name a foreign composition repository")
    pin = mapping(spec.get("ref"), "selected composition pin")
    commit = sha(pin.get("commit"))
    tag = pin.get("tag")
    require(isinstance(tag, str) and re.fullmatch(r"v\d+\.\d+\.\d+", tag) is not None,
            "cloud component sources have no selected composition tag")
    assert isinstance(tag, str)
    header = mapping(yaml.safe_load(git(root, "show", f"{commit}:composed/HEADER.yaml")),
                     "selected composition header")
    expected: list[dict[str, str]] = []
    if header.get("cloud-package"):
        cloud = mapping(json.loads(git(root, "show", f"{commit}:composed/CLOUD-PARENT.json")),
                        "cloud component parent")
        require((cloud.get("party"), cloud.get("kind"), cloud.get("name"))
                == ("platform", "implementations", "cloud"),
                "cloud component parent names a different package")
        version = cloud.get("version")
        require(isinstance(version, str) and re.fullmatch(r"\d+\.\d+\.\d+", version) is not None
                and cloud.get("tag") == "cloud/v" + version,
                "cloud component parent has no package version and tag")
        assert isinstance(version, str)
        source = sha(cloud.get("sha"))
        require(header["cloud-package"] == cloud,
                "cloud component parent differs from its selected composition header")
        path = f"composed/cloud/v{version}/component-definition.json"
        component = mapping(json.loads(git(root, "show", f"{commit}:{path}")), "cloud component definition")
        definition = mapping(component.get("component-definition"), "cloud component definition body")
        metadata = mapping(definition.get("metadata"), "cloud component definition metadata")
        # The mapping document has its own content revision, independent of the
        # cloud package. Its exact selected commit/path still binds provenance.
        document_version = metadata.get("version")
        require(isinstance(document_version, str) and bool(document_version.strip()),
                "cloud component definition has no nonblank document version")
        expected = [{"party": "platform", "name": "cloud", "tag": "cloud/v" + version,
                     "sha": source, "composed_tag": tag, "component_definition": path}]
    require(sources == expected, "cloud component sources differ from the immutable selected composition")


def validate_payload(root: Path, parent: str, run: dict[str, Any], profile: Profile,
                     evidence: dict[str, tuple[str, str]]) -> None:
    series = {path: json_rows(suffix) for path, (_, suffix) in evidence.items()}
    for rows in series.values():
        require(all(row.get("run") == str(run["id"]) for row in rows), "observation names another run")
    if profile.payload == "drift":
        require(parent == run["head_sha"], "drift observation is not based on its measured source")
        metadata = {"context", "event", "kind", "run", "ts"}
        for rows in series.values():
            for row in rows:
                timestamp(row, "ts")
                require(row.get("event") == run["event"] and row.get("context") == f"kind-dsample-{run['id']}",
                        "drift observation event or source context is foreign")
        samples = series["drift/samples.jsonl"]
        require(len(samples) == 3 and all(isinstance(row.get("source"), str) for row in samples)
                and {row.get("source") for row in samples}
                == {profile.org + "-composed", "platform", "nist"},
                "drift observation must append exactly three distinct source facts")
        for row in samples:
            keys(row, metadata | {"cluster", "facts", "falsifiers", "party", "pin", "reachable", "reason",
                                  "revision", "schema_version", "source", "verdict"}, {"subjects"})
            require(row.get("kind") == "flux.five-facts/v1" and type(row.get("schema_version")) is int and row["schema_version"] == 3
                    and row.get("cluster") == f"dsample-{run['id']}"
                    and row.get("party") == (profile.org if row["source"] == profile.org + "-composed" else row["source"])
                    and typed_readings(row.get("facts"), FACTS, "observed")
                    and typed_readings(row.get("falsifiers"), FALSIFIERS, "fired")
                    and isinstance(row.get("pin"), dict) and type(row.get("reachable")) is bool
                    and row.get("verdict") in ("PASS", "FAIL", "COULD-NOT-LOOK")
                    and isinstance(row.get("reason"), str) and isinstance(row.get("revision"), str),
                    "five-fact observation schema is invalid")
        workloads = series["drift/workload-samples.jsonl"]
        require(len(workloads) == 1, "drift observation must append one served-workload row")
        row = workloads[0]
        keys(row, metadata | {"apps_ref", "fact", "observed", "runner_ceiling", "why", "workloads"})
        require(row.get("kind") == "flux.served-workloads/v1"
                and row.get("fact") == "fact_8_each_served_workload_runs_in_its_cage"
                and (row.get("observed") is None or type(row.get("observed")) is bool)
                and isinstance(row.get("workloads"), list) and isinstance(row.get("runner_ceiling"), dict)
                and isinstance(row.get("why"), str) and isinstance(row.get("apps_ref"), str),
                "served-workload observation schema is invalid")
        oscals = series["drift/oscal-samples.jsonl"]
        require(len(oscals) == 1, "drift observation must append one OSCAL row")
        row = oscals[0]
        lists = {"missing_risk_observations", "report_read_errors", "risk_validation_errors", "risks",
                 "unmapped_failed_results", "unmapped_served_policies"}
        counts = {"mapped_served_policy_count", "report_count", "served_policy_count"}
        # Only TU's existing collector emits this optional provenance extension.
        optional = {"cloud_component_sources"} if profile.org == "tuppence" else set()
        keys(row, metadata | lists | counts | {"assessment_results", "status", "why"}, optional)
        require(row.get("kind") == "flux.oscal-lane/v1" and isinstance(row.get("assessment_results"), dict)
                and all(isinstance(row.get(key), list) for key in lists)
                and all(type(row.get(key)) is int and row[key] >= 0 for key in counts)
                and row.get("status") in ("observed", "could-not-look") and isinstance(row.get("why"), str),
                "OSCAL observation schema is invalid")
        if "cloud_component_sources" in row:
            validate_cloud_sources(root, parent, row["cloud_component_sources"])
        return
    rows = series["observations/twin-sweep.jsonl"]
    require(len(rows) == 1, "twin observation must append exactly one row")
    row = rows[0]
    keys(row, {"adopter_ref", "feed", "moved", "org", "run", "swept_at"} |
         ({"proposal", "twin_ref"} if profile.payload == "forward" else
          {"detail", "emitter_exit", "hub_ref", "status", "twin_pin"}))
    at = timestamp(row, "swept_at")
    require(row.get("org") == profile.org and row.get("feed") == "forward-intel",
            "twin observation belongs to another adopter or feed")
    measured = sha(row.get("adopter_ref"))
    git(root, "merge-base", "--is-ancestor", run["head_sha"], measured)
    git(root, "merge-base", "--is-ancestor", measured, parent)
    pin = yaml.load(git(root, "show", f"{parent}:twin/PIN.yaml"), Loader=yaml.BaseLoader)
    require(isinstance(pin, dict), "trusted twin source pin is not a mapping")
    hub_commit = sha(pin.get("hub_commit"))
    if profile.payload == "forward":
        require(type(row.get("moved")) is bool
                and row.get("twin_ref") == "policy-as-versioned-flux@" + hub_commit
                and row.get("proposal") == ("twin/forward-intel-" + at[:10] if row["moved"] else ""),
                "forward-intel observation source or proposal is invalid")
    else:
        require(row.get("hub_ref") == hub_commit and isinstance(row.get("twin_pin"), dict)
                and row["twin_pin"].get("hub_commit") == hub_commit
                and row.get("status") in ("unchanged", "review_required", "could_not_look", "could_not_render")
                and type(row.get("emitter_exit")) is int and row["emitter_exit"] in {0, 1, 3}
                and (row.get("moved") is None or type(row.get("moved")) is bool)
                and isinstance(row.get("detail"), str), "emitter observation source or schema is invalid")
        states = {"unchanged": (0, False), "review_required": (1, True),
                  "could_not_look": (3, None), "could_not_render": (1, None)}
        require((row["emitter_exit"], row["moved"]) == states[row["status"]],
                "emitter status, exit and movement do not describe one reading")


class HubAuthority:
    """Read fresh hub mode and its cited prose as Git data, using the pinned validator."""
    def __init__(self, store: Path, api: Api, today: dt.date | None):
        self.store, self.api, self.today = store, api, today
        self.expected: str | None = None
        self.default: str | None = None
        store.mkdir(parents=True, exist_ok=True)
        if not (store / ".git").exists():
            git(store, "init", "-q")

    def __call__(self) -> None:
        repo = mapping(self.api("GET", f"repos/{REPOSITORY}", None), "hub authority facts")
        require(repo.get("full_name") == REPOSITORY and isinstance(repo.get("default_branch"), str),
                "hub mode authority repository facts are invalid")
        default = repo["default_branch"]
        require(self.default is None or self.default == default, "hub default authority changed")
        git(self.store, "check-ref-format", "refs/heads/" + default)
        ref = "refs/remotes/hub/" + default
        git(self.store, "fetch", "--no-tags", HUB_URL, f"refs/heads/{default}:{ref}")
        tip = sha(git(self.store, "rev-parse", ref).strip())
        require(self.expected is None or self.expected == tip,
                "hub authority tip changed; retry from fresh read-only preflight")
        self.default, self.expected = default, tip
        mode = self.data(tip, "twin/ENACT_MODE")
        why = self.data(tip, "twin/ENACT_MODE.why")
        record = yaml.load(why, Loader=yaml.BaseLoader)
        require(isinstance(record, dict) and isinstance(record.get("said"), list),
                "hub mode authority has no acknowledgement record")
        with tempfile.TemporaryDirectory(prefix="observation-authority-") as temporary:
            root = Path(temporary)
            (root / "twin").mkdir()
            (root / "twin/ENACT_MODE").write_text(mode)
            (root / "twin/ENACT_MODE.why").write_text(why)
            for entry in record["said"]:
                require(isinstance(entry, dict), "hub authority acknowledgement is malformed")
                where = str(entry.get("where", ""))
                path = Path(where)
                require(bool(where) and not path.is_absolute() and ".." not in path.parts,
                        "hub authority acknowledgement escapes its repository")
                prose = self.data(tip, where)
                out = root / path
                out.parent.mkdir(parents=True, exist_ok=True)
                out.write_text(prose)
            window(root, self.today or dt.datetime.now(dt.timezone.utc).date())

    def data(self, tip: str, path: str) -> str:
        entry = git(self.store, "ls-tree", tip, "--", path).split()
        require(len(entry) >= 4 and entry[:2] == ["100644", "blob"],
                "hub authority record is not a regular data file")
        return git(self.store, "show", f"{tip}:{path}")


def delivery_authority(root: Path, default: str, today: dt.date | None, profile: Profile,
                       authority_root: Path | None, api: Api) -> Callable[[], None]:
    if profile == TRUTH:
        return lambda: authority(root, default, today)
    require(authority_root is not None, "adopter delivery requires fresh hub mode authority data")
    assert authority_root is not None
    hub = HubAuthority(authority_root, api, today)

    def check() -> None:
        # Both tips are re-read immediately before every approval and merge.
        git(root, "fetch", "--no-tags", "origin", f"refs/heads/{default}:refs/remotes/origin/{default}")
        require(git(root, "rev-parse", "HEAD").strip()
                == git(root, "rev-parse", f"refs/remotes/origin/{default}").strip(),
                "trusted checkout is behind current adopter default authority")
        hub()
    return check


def mint_for(profile: Profile) -> None:
    """Existing immutable mint helper, environment-only key, one repository token."""
    try:
        import delivery_other_hand as helper
    except ImportError:
        from twin import other_hand as helper
    raw = os.environ.pop("PAVC_OTHER_HAND_PRIVATE_KEY", "")
    require(bool(raw), "reviewer environment has no App key; observation remains pending")
    key_file: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(mode="w", dir=os.environ.get("RUNNER_TEMP"), delete=False) as stream:
            key_file = Path(stream.name)
            stream.write(raw)
        del raw
        jwt = helper.app_jwt(str(APP_ID), key_file)
        print("::add-mask::" + jwt, flush=True)
        installation = helper.installation_for_org(jwt, profile.repository.split("/")[0])
        scoped = helper._http("POST", f"/app/installations/{installation}/access_tokens", jwt, {
            "repositories": [profile.org], "permissions": {"contents": "write", "pull_requests": "write"}})
        token = scoped["token"]
        require(isinstance(token, str) and bool(token), "existing App returned no narrow writer token")
        print("::add-mask::" + token, flush=True)
        os.environ["GH_TOKEN"] = token
    except Exception as error:
        raise Refusal("existing App could not mint the caller repository's narrow writer token") from error
    finally:
        if key_file is not None:
            key_file.unlink(missing_ok=True)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-id", type=int, required=True)
    parser.add_argument("--attempt", type=int, required=True)
    parser.add_argument("--repository", default=REPOSITORY)
    parser.add_argument("--workflow", default=WORKFLOW)
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--authority-root", type=Path)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--check-only", action="store_true")
    mode.add_argument("--mint", action="store_true")
    mode.add_argument('--prepare-integration', action='store_true')
    parser.add_argument('--review-integration', action='store_true')
    args = parser.parse_args()
    try:
        options = dict(repository=args.repository, workflow=args.workflow, attempt=args.attempt,
                       authority_root=args.authority_root)
        if args.prepare_integration:
            require(select_profile(args.repository, args.workflow) == TRUTH and not args.review_integration,
                    'integration preparation is restricted to the separate TRUTH preparation job')
            print(prepare_truth(args.root, args.run_id, attempt=args.attempt))
            return 0
        if args.review_integration:
            options['review_integration'] = True
        if args.mint:
            preflight = deliver(args.root, args.run_id, check_only=True, **options)
            if preflight.startswith(("RECORDED", "SKIP: no delivery expected;")):
                print(preflight)
                return 0
            mint_for(select_profile(args.repository, args.workflow))
        print(deliver(args.root, args.run_id, check_only=args.check_only, **options))
        return 0
    except (Refusal, OSError, ValueError, KeyError, TypeError, yaml.YAMLError) as error:
        # API/Git transports deliberately replace error bodies with safe messages.
        print(f"PENDING: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
