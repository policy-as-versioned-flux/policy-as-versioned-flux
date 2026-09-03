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

**Mode (2026-08-25, repository owner, standing instruction).** This layer's refusal was written
for the twin operating on the world in the ordinary run of things. It is not free while the twin
itself is under active, hands-on construction: every merge became a human clicking a button on a
diff nobody had time to read, which is friction with no accountability behind it — the mistake
that prompted the instruction was an unverified subagent claim, not a missing human hand on the
merge button. So this is now a MODE, not a constant, checked here rather than hidden in an env
var nobody would find: `ENACT_MODE_FILE` (`twin/ENACT_MODE`, one word, checked in) is the durable,
visible default; `TWIN_ENACT_MODE` in the environment overrides it for one run without touching
the file. Absent both, the default is `development` — merges and enactment pushes are admitted.
Set either to `operations` to restore this file's original behaviour unchanged. The harness
invariant `enactment_is_propose_only_at_both_layers` asserts the refusal exists and works by
forcing `operations` mode for its own run, regardless of this file's checked-in default — the
capability stays tested even while the day-to-day default is permissive.

**Mode, amended 2026-08-29 (the eco-system thin slice).** The permissive default is withdrawn
and the fallback flips: absent both `TWIN_ENACT_MODE` and `ENACT_MODE_FILE`, the mode is
`operations` and the refusals bite. Two reasons, neither of them a re-argument of the 2026-08-25
instruction:

1. *The default was failing open in silence.* `decide` returns `None` for everything under
   `development`, so a deleted refusal and the deliberate default were the same observation. The
   thirteen tests that assert what the guard DOES had been red since commit 9282301 and were then
   made green by an autouse fixture that forced `operations` for the test process only — which is
   the tests agreeing with a guard nobody ships. Nothing asserted the shipped default at all.
   Now the tests run the guard as shipped, and `test_the_shipped_default_refuses` asserts the
   fallback itself, so flipping this back to permissive turns the suite red rather than quiet.
2. *The construction window the instruction was written for is the one thing that is now
   forbidden outright.* The thin-slice build brief's first hard rule is "never push, never merge
   a PR, never create a tag" — the owner pushes and merges. So `operations` is not friction
   against the current way of working; it is that way of working, in code.

The escape hatch the 2026-08-25 instruction asked for is untouched and still one word: write
`development` into `twin/ENACT_MODE` (durable, visible in a diff and a `git blame`) or export
`TWIN_ENACT_MODE=development` for one run. What changed is only which way it falls when nobody
has said anything.

**Mode, amended 2026-09-03 (ticket 88; ticket 75 Q6 and Q14, the owner, reasoned).** A third
mode, `other-hand`, and it is the checked-in one. The owner decided that principle 5, "a human
merges", binds for the demonstration, and that for the development window the owner authors and
pushes while the assistant reviews and merges as a second machine identity: the GitHub App
`pavc-other-hand` (App ID 4819564, installed on all nine estate orgs; `twin/other_hand.py` mints
its tokens). The owner's word for it was theatre, and the narrative still says a human merges.

`other-hand` is `operations` with exactly one shape admitted: a disposition command that mints
the app's token in the same command string (`twin.other_hand token`), because that merge goes out
as `pavc-other-hand[bot]` and not under the owner's own token. Every push to an enactment
repository is still refused (the owner pushes), a merge-shaped MCP tool is still refused (it
cannot carry the app's credential), and a bare merge is still refused with a reason that names
this mode. `development` was not chosen: it would have admitted the pushes too, and the owner's
instruction split the two hands on purpose. As with everything in this file, the screen is a net
over the shapes a merge takes here, not a proof; ticket 87's ruleset is the server-side half.
"""

from __future__ import annotations

import json
import os
import re
import shlex
import subprocess
import sys
from pathlib import Path
from typing import Any, NamedTuple

# See the module docstring's "Mode" section. One word, checked in, visible in a diff and a
# `git blame` — not a magic env var nobody would find by reading this file.
ENACT_MODE_FILE = Path(__file__).resolve().with_name("ENACT_MODE")
_MODES = ("development", "operations", "other-hand")


DEFAULT_MODE = "operations"


def enact_mode() -> str:
    """The active mode: `TWIN_ENACT_MODE` in the environment first (a one-run override), then
    `ENACT_MODE_FILE` (the durable default), then `DEFAULT_MODE` when neither says otherwise.

    The fallback is the refusing mode (amended 2026-08-29, see the docstring): an unreadable file,
    a typo in it, and a checkout that lost it are all cases where nobody has said the twin may
    dispose, and a guard that cannot tell must not admit.
    """
    env = os.environ.get("TWIN_ENACT_MODE", "").strip().lower()
    if env in _MODES:
        return env
    try:
        from_file = ENACT_MODE_FILE.read_text(encoding="utf-8").strip().lower()
    except OSError:
        from_file = ""
    return from_file if from_file in _MODES else DEFAULT_MODE

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

# The one shape `other-hand` mode admits: the merge runs with `GH_TOKEN` set, in the SAME shell
# segment, from the app's own token minter (`python -m twin.other_hand token ...` or
# `twin/other_hand.py token ...`). A merge made with that token is attributed to
# `pavc-other-hand[bot]`, the second identity ticket 88 created. Per segment, not per command:
# `echo "twin/other_hand.py token"; gh pr merge 42` mints nothing and would merge under the
# owner's own token, and so would `T=$(... token); GH_TOKEN=$T gh pr merge 42`, where the guard
# cannot see what `$T` holds. The admitted shape is one segment, token minted inline.
OTHER_HAND_TOKEN = re.compile(r"\bGH_TOKEN=[\"']?\$\([^)]*\btwin[./]other_hand(?:\.py)?\s+token\b")
_SHELL_SEGMENT = re.compile(r"\n|;|&&|\|\||\|")


def _merge_is_made_as_the_other_hand(command: str) -> bool:
    """True only if every segment that disposes also mints the app's token inline for that
    segment's `GH_TOKEN`. A command with no disposing segment returns True vacuously; the
    caller only asks after a disposition pattern has already matched somewhere."""
    for segment in _SHELL_SEGMENT.split(command):
        if any(pattern.search(segment) for pattern, _ in DISPOSITION_COMMANDS):
            if not OTHER_HAND_TOKEN.search(segment):
                return False
    return True

DENY = "deny"


class _Locus(NamedTuple):
    """Where the `git push` in a command string actually looks for its repository, and how it
    would reach its remote: the directory it runs in, the `--git-dir` / `--work-tree` it was
    handed, its `-c key=value` overrides, and the `GIT_*` assignments prefixed to it. Everything
    git itself reads before it names a remote, carried as one value so the resolution below hands
    git exactly what the command hands it and guesses at none of git's discovery rules."""

    cwd: str | None
    git_dir: str | None = None
    work_tree: str | None = None
    configs: tuple[str, ...] = ()
    env: tuple[tuple[str, str], ...] = ()


# The hook process's own `GIT_DIR` reaches BOTH resolutions below if it is left alone: one
# pointing at a checkout of this repository turns every bare push in every enactment checkout
# into a self-push, and one pointing at an enactment checkout makes that checkout "our own". So
# it is scrubbed for the first reading of the target and always for the own-repository reading
# (ticket 65). It is NOT ignored: in Claude Code the hook and the Bash tool inherit the same
# process environment (review of 2026-09-03), so a `GIT_DIR` the hook sees is one the push sees
# too, and `_push_target` reads the target a second time with it honoured when the command names
# none of its own. Either reading naming an enactment repository is a refusal.
_SCRUBBED_ENV = ("GIT_DIR", "GIT_WORK_TREE")


def _remote_url(remote: str, at: _Locus, honour_own_env: bool = False) -> str:
    argv = ["git"]
    if at.git_dir is not None:
        argv += ["--git-dir", at.git_dir]
    if at.work_tree is not None:
        argv += ["--work-tree", at.work_tree]
    for config in at.configs:
        argv += ["-c", config]
    argv += ["remote", "get-url", "--push", remote]
    env = {
        key: value for key, value in os.environ.items()
        if honour_own_env or key not in _SCRUBBED_ENV
    }
    env.update(at.env)
    try:
        return subprocess.run(
            argv, cwd=at.cwd or None, env=env,
            capture_output=True, text=True, timeout=5, check=False,
        ).stdout
    except (OSError, subprocess.SubprocessError):
        return ""


_ASSIGNMENT = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*=")


def _words(segment: str) -> list[str]:
    """One shell segment split as the shell would split it: quotes removed, a quoted space kept
    inside its word. A segment shlex cannot parse (an unbalanced quote) falls back to whitespace,
    which is what the first cut always did."""
    try:
        return shlex.split(segment, posix=True)
    except ValueError:
        return segment.split()


def _directory(word: str, relative_to: str | None) -> str:
    """A directory word as the shell would hand it on: tilde expanded, relative to where the
    command stands by then. The tilde is expanded after the quotes are gone, so `"~/x"` is read
    as `~/x` though the shell would not expand it; and `--git-dir=~/x` is expanded though the
    shell would not (git then says fatal and pushes nothing). Both mismatches point the same way,
    a refusal of a push that would not have happened, which is the safe way round -- an empty
    resolution ADMITS, so the guard expands wherever the shell might."""
    path = Path(os.path.expanduser(word))
    if not path.is_absolute():
        path = Path(relative_to or ".") / path
    return str(path)


def _is_git(word: str) -> bool:
    return word == "git" or word.endswith("/git")


def _effective_locus(command: str, cwd: str | None) -> _Locus:
    """The locus of the `git push` in this command: what git would read to find its remote.

    A push names a remote, not a URL, so the remote has to be resolved -- and it resolves in
    whichever repository git is pointed at, which is NOT always the shell's own directory.
    The ways it moves, each observed for real:

      git -C .estate-clone/platform push origin ecosystem/thin-slice        (2026-08-31)
      cd .estate-clone/platform && git push origin ecosystem/thin-slice     (2026-08-31)
      git --git-dir=<enactment>/.git push origin main                       (M17, ticket 65)
      GIT_DIR=<enactment>/.git git push origin main                         (M17, ticket 65)
      git -c remote.origin.pushurl=<enactment> push origin main             (review 2026-09-03)

    Resolved against `cwd` alone, every one of them read the CALLER's `origin` instead; when
    the caller stood in this repository, whose own push is carved out, the guard admitted a
    push to the enactment repositories while reporting nothing.

    **Per segment, not per command** (review of 2026-09-03, blocking). The first cut searched
    the whole string, so `git --git-dir=<hub>/.git log; git push origin main` made in an
    enactment checkout resolved the hub's origin and was admitted. The option, the `-C`, the
    `-c` and the `GIT_*=` prefix are read from the segment that holds the `push` and no other.
    From the segments before it, only what the shell itself carries forward: a `cd` (folded in
    order, each relative to the last, as the shell does) and an `export GIT_*=...`. A bare
    `GIT_DIR=x;` in an earlier segment is a shell variable, not an exported one, and is not
    carried: carrying it would resolve where the push does not go.

    Observed with git 2.55 on 2026-09-03 rather than assumed: `--work-tree` ALONE does not
    move discovery (git still walks up from the cwd), an absent `--git-dir` is fatal so nothing
    resolves and `url` is empty, and a relative `--git-dir` after `-C` is relative to the `-C`
    directory. None of that is re-implemented here: the parsed values are handed to git as the
    same options, in the same environment, in the directory the command moved to -- so what
    the guard resolves is what git would, including the cases git refuses.
    """
    segments = _SHELL_SEGMENT.split(command)
    pushing = next((i for i, s in enumerate(segments) if _PUSH.search(s)), None)
    if pushing is None:
        return _Locus(cwd)

    at = cwd
    env: dict[str, str] = {}
    for before in segments[:pushing]:
        words = _words(before)
        if not words:
            continue
        if words[0] == "cd":
            at = _directory(words[1] if len(words) > 1 else "~", at)
        elif words[0] == "export":
            for word in words[1:]:
                if _ASSIGNMENT.match(word) and word.startswith("GIT_"):
                    name, value = word.split("=", 1)
                    env[name] = os.path.expanduser(value)

    words = _words(segments[pushing])
    git_dir: str | None = None
    work_tree: str | None = None
    configs: list[str] = []
    i = 0
    # Before the `git` word: `env`, a wrapper, and the assignment prefix the shell would hand
    # git as its environment.
    while i < len(words) and not _is_git(words[i]):
        if _ASSIGNMENT.match(words[i]) and words[i].startswith("GIT_"):
            name, value = words[i].split("=", 1)
            env[name] = os.path.expanduser(value)
        i += 1
    i += 1
    # Between `git` and `push`: git's own global options, the ones that move the repository or
    # rewrite the remote. `-C` folds like `cd` does, because git makes each relative to the last.
    while i < len(words) and words[i] != "push":
        word, following = words[i], (words[i + 1] if i + 1 < len(words) else "")
        if word == "-C":
            at = _directory(following, at)
            i += 2
            continue
        if word in ("--git-dir", "--work-tree", "-c"):
            value, i = following, i + 2
        elif word.startswith(("--git-dir=", "--work-tree=")):
            word, value = word.split("=", 1)
            i += 1
        elif word.startswith("-c") and not word.startswith("--"):
            word, value = "-c", word[2:]
            i += 1
        else:
            i += 1
            continue
        if word == "--git-dir":
            git_dir = os.path.expanduser(value)
        elif word == "--work-tree":
            work_tree = os.path.expanduser(value)
        else:
            configs.append(value)
    return _Locus(at, git_dir, work_tree, tuple(configs), tuple(env.items()))


def _normalise(url: str) -> str:
    """`host/org/repo`, lowercased, so an ssh remote and an https one compare equal.

    Compared as a whole repository rather than by the `policy-as-versioned-*` token, because the
    token is an **org** name here and the org holds enactment repositories beside the twin's own:
    `.../policy-as-versioned-flux/policy` and `.../policy-as-versioned-flux/policy-as-versioned-flux`
    share it and are not the same repository at all.
    """
    trimmed = url.strip().rstrip("/")
    if trimmed.endswith(".git"):
        trimmed = trimmed[: -len(".git")]
    trimmed = re.sub(r"^[a-z+]+://", "", trimmed, flags=re.I)
    trimmed = re.sub(r"^[^/@]+@", "", trimmed)
    return trimmed.replace(":", "/", 1).lower()


def _own_repository(cwd: str | None) -> str:
    """This checkout's own push URL — the twin's model, not the world.

    Resolved from this file's location rather than from the caller's `cwd`, or a `cd` into an
    enactment repository would make that repository "our own". Empty when there is no origin, and
    an empty string matches no target, so the refusal stays closed when it cannot tell.
    """
    del cwd
    return _normalise(_remote_url("origin", _Locus(str(Path(__file__).resolve().parents[1]))))


def _push_target(command: str, cwd: str | None) -> str | None:
    """What a `git push` in this command would write to, or `None` if the twin may write there.

    The URL is usually not on the command line — `git push origin main` names a remote, and the
    remote is what has to be resolved, in whichever repository git is pointed at. `git -C <dir>`
    and a leading `cd <dir> &&` both move that repository, and resolving against the caller's own
    `cwd` regardless made the guard read the WRONG remote: on 2026-08-31 it read this repository's
    own origin, matched the self-push carve-out below, and admitted a push to all six enactment
    repositories without a word. `_effective_cwd` closes both; the URL leg still catches the case
    where the target is named outright.

    **The carve-out (2026-08-16, repository owner, standing instruction).** A push to *this*
    repository is admitted. Decision ticket 18 Q1 reads "the twin changes its own model constantly
    and the world never without a human", and this repository is the model: `twin/`, the decision
    record and the fixtures. The enactment repositories are the other `policy-as-versioned-*` ones
    (`-nist`, `-platform`, `-driftwood`, `-tuppence`, `-ludlow`, `-ico`, `-code`), and a push to any
    of those is refused exactly as before. **This is still a weakening**, and naming it as anything
    else would be the "removed refusal that never shows in a diff" the constitution warns about:
    before this, the twin could not write to any remote, so a bad commit needed a human to travel.
    Now it can publish its own model unattended, and only the world is gated. The owner asked for
    that, four times, and the accountability moved to them by that instruction rather than by an
    argument in code.
    """
    found = _PUSH.search(command)
    if not found:
        return None

    # The first non-flag argument after `push` is the target: either a URL outright, or a remote
    # name that has to be resolved. Taken as one argument rather than by scanning the whole
    # command, because the comparison below is against a repository and " main" on the end of it
    # is not one.
    arguments = [t for t in found.group("rest").split() if not t.startswith("-")]
    target = arguments[0] if arguments else "origin"
    if "://" in target or "@" in target or "/" in target:
        urls = [target]
    else:
        # Resolved in the repository git is actually pointed at (`-C`, a `cd` before the push,
        # `--git-dir`, `GIT_DIR=`, `-c remote.*`), never blindly in the caller's own directory
        # -- see _effective_locus. And read a second time with the hook's own `GIT_DIR` honoured
        # when the command names none, because the push inherits that environment too (see
        # _SCRUBBED_ENV): a refusal if either reading names an enactment repository.
        locus = _effective_locus(command, cwd)
        urls = [_remote_url(target, locus)]
        named = locus.git_dir is not None or any(key in dict(locus.env) for key in _SCRUBBED_ENV)
        if not named and any(key in os.environ for key in _SCRUBBED_ENV):
            urls.append(_remote_url(target, locus, honour_own_env=True))

    own: str | None = None
    for url in urls:
        resolved = ENACTMENT_REPOSITORY.search(url)
        if not resolved:
            continue
        # Equality, not a suffix test: `endswith` would admit `evil-github.com/…/policy-as-versioned-flux`.
        if own is None:
            own = _own_repository(cwd)
        if own and _normalise(url) == own:
            continue
        return resolved.group(0)
    return None


def decide(tool_name: str, tool_input: dict[str, Any], cwd: str | None = None) -> str | None:
    """The refusal reason for a disposing tool call, or `None` for everything else.

    Pure, and separated from the hook plumbing so the invariant suite can assert the property
    directly rather than by shelling out to a subprocess and reading its exit code.
    """
    mode = enact_mode()
    if mode == "development":
        return None

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
            if mode == "other-hand":
                if _merge_is_made_as_the_other_hand(command):
                    break
                return (
                    f"`{shape}` under the owner's own token is author-equals-merger. In "
                    "`other-hand` mode a merge is admitted only as the other hand: mint the "
                    "app's token in the same command (`GH_TOKEN=\"$(python -m twin.other_hand "
                    "token --org <org>)\"`), so the merge is attributed to pavc-other-hand[bot] "
                    "(ticket 88; ticket 75 Q6, Q14)."
                )
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
