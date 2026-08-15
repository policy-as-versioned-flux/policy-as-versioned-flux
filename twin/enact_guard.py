#!/usr/bin/env python3
"""Layer 2 of propose-only: the constraint at the tool-call boundary (build ticket 66).

`twin/enact.py` is layer 1 — the twin has no merge code path, and the invariant suite asserts its
public surface against an allow-list. That is a property of `twin/` **as it is today**, and the
twin is an agent. The day it gains a shell tool, an MCP GitHub server or a subagent with `gh`, the
absence still holds and the guarantee is gone, **with no diff to `twin/` at all**. An absence does
not survive composition. A constraint here does, because every one of those paths ends in a tool
call and this runs before each of them — including a subagent's, which is refused at the subagent's
own call rather than at a delegation prompt nobody can read reliably.

**That last clause is a property of the runtime, not of this repository.** Whether a given runner
routes a subagent's tool calls through its hooks is the runner's business; nothing here asserts it,
and the invariant suite deliberately does not pretend to. What this repository can assert is that
`decide` refuses the call whenever it is handed one, and that the registration routes *every* tool
name to it rather than a merge-shaped subset.

**The failure mode of this layer is that it is a call site, and a call site can be forgotten.**
Delete the registration from `.claude/settings.json`, or drive the twin from a runner that does not
honour hooks — a plain `python -c`, a CI job, a different agent runtime — and layer 2 is not there,
in silence. That is exactly why layer 1 stays: an absence has no call site to forget. The two fail
in opposite directions on purpose, and the harness check
`enactment_is_propose_only_at_both_layers` reads the registration back out of `.claude/settings.json`,
so a forgotten call site is a red test rather than an open door.

Stdlib only, and nothing imported from `twin/`: this runs as a plain script from a hook command
line, before and outside the package it guards.

`ponytail:` the command patterns are a net over the shapes a merge actually takes here, not a
proof. A wrapper script named something else, or a REST call hand-rolled through `curl` with a
token, is not matched. The upgrade is a credential that cannot merge — a GitHub App installation
token with `pull_requests: write` and no `contents: write`, which makes the refusal the server's
rather than ours; the shape of this file is what that upgrade would keep.
"""

from __future__ import annotations

import json
import re
import subprocess
import sys
from typing import Any

# Every repository this estate enacts into carries the org prefix — it is the impersonation
# guardrail `estate/README.md` describes, and it doubles as the thing a guard can recognise.
ENACTMENT_REPOSITORY = re.compile(r"policy-as-versioned-[a-z0-9-]+", re.I)

# Disposition, in the shapes it takes on a command line. Matched wherever they appear rather than
# only against an enactment URL: the twin has no business merging any pull request anywhere, so the
# narrower rule would only be a way to be wrong about which repository is which.
DISPOSITION_COMMANDS: tuple[tuple[re.Pattern[str], str], ...] = (
    (re.compile(r"\bgh\s+pr\s+merge\b"), "gh pr merge"),
    (re.compile(r"\bgh\s+api\b[^\n]*\bmerges?\b"), "gh api ... /merge"),
    (re.compile(r"\bgh\s+pr\s+[^\n]*--auto\b"), "gh pr merge --auto (merging on a delay is merging)"),
)

# An MCP GitHub server names the act in the tool name, and the server is somebody else's
# namespace, so this leg cannot be an allow-list the way layer 1's public surface is: the set of
# tool names is unbounded and mostly not ours.
#
# `ponytail:` so this leg **is** a keyword screen, which is the technique layer 1 refuses on
# principle — the difference is that layer 1 could enumerate its own surface and this cannot. It is
# stated as a screen rather than dressed up: `squash_pull_request` is caught because `squash` is
# listed, and a server that calls it `apply_changes` is not caught by anything here. The upgrade is
# the credential named in the module docstring, which does not depend on guessing a verb.
DISPOSITION_TOOL_NAME = re.compile(r"merge|squash|rebase_and_|dispose|land_|ship_", re.I)

_PUSH = re.compile(r"\bgit\b[^\n;&|]*?\bpush\b(?P<rest>[^\n;&|]*)")

DENY = "deny"


def _push_target(command: str, cwd: str | None) -> str | None:
    """What a `git push` in this command would actually write to, or `None` if it is not one.

    The URL is usually not on the command line — `git push origin main` names a remote, and the
    remote is what has to be resolved. `ponytail:` resolved against `cwd`, so a `cd elsewhere &&
    git push` inside one command reads the wrong repository; the URL leg still catches the case
    where the target is named outright.
    """
    found = _PUSH.search(command)
    if not found:
        return None
    named = ENACTMENT_REPOSITORY.search(found.group(0))
    if named:
        return named.group(0)

    tokens = [t for t in found.group("rest").split() if not t.startswith("-")]
    remote = tokens[0] if tokens else "origin"
    try:
        url = subprocess.run(
            ["git", "remote", "get-url", "--push", remote],
            cwd=cwd or None, capture_output=True, text=True, timeout=5, check=False,
        ).stdout
    except (OSError, subprocess.SubprocessError):
        return None
    resolved = ENACTMENT_REPOSITORY.search(url)
    return resolved.group(0) if resolved else None


def decide(tool_name: str, tool_input: dict[str, Any], cwd: str | None = None) -> str | None:
    """The refusal reason for a disposing tool call, or `None` for everything else.

    Pure, and separated from the hook plumbing so the invariant suite can assert the property
    directly rather than by shelling out to a subprocess and reading its exit code.
    """
    if DISPOSITION_TOOL_NAME.search(tool_name or ""):
        return (
            f"{tool_name} disposes rather than proposes. The twin opens pull requests and never "
            "merges them (decision ticket 18 Q1): Article 22 admits no solely-automated "
            "significant decision, a trade-off curve has nothing to auto-execute, and an agent "
            "signature asserts reproducible origin rather than endorsement — so there is nobody "
            "accountable behind an agent-initiated merge. A human disposes, out of band."
        )

    command = str(tool_input.get("command", "")) if isinstance(tool_input, dict) else ""
    if not command:
        return None

    for pattern, shape in DISPOSITION_COMMANDS:
        if pattern.search(command):
            return (
                f"`{shape}` disposes rather than proposes, and the twin only proposes (decision "
                "ticket 18 Q1). Open the pull request and leave it open: a human merges it, and "
                "that hand-off is the accountability, not a formality."
            )

    target = _push_target(command, cwd)
    if target:
        return (
            f"a push to {target} writes to an enactment repository directly, which is disposal "
            "without even the pull request. The twin changes its own model constantly and the "
            "world never without a human (decision ticket 18 Q1)."
        )
    return None


def main(argv: list[str] | None = None) -> int:
    """The PreToolUse hook entry point: a tool call on stdin, a permission decision on stdout.

    A payload that cannot be parsed identifies no tool call, so there is nothing to refuse and the
    call is left alone. That is not this layer failing open on the merge path — layer 1 is still
    there, and the harness asserts both.
    """
    try:
        payload = json.loads(sys.stdin.read() or "{}")
    except (ValueError, OSError):
        return 0

    reason = decide(
        str(payload.get("tool_name", "")), payload.get("tool_input") or {}, payload.get("cwd")
    )
    if reason is None:
        return 0
    print(json.dumps({
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": DENY,
            "permissionDecisionReason": reason,
        }
    }))
    return 0


if __name__ == "__main__":
    sys.exit(main())
