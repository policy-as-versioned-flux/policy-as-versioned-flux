"""Propose-only enactment, in two layers (build ticket 66)."""

from __future__ import annotations

import inspect
import io
import json
import re
from pathlib import Path

import pytest

from twin import enact, enact_guard
from twin.artefact import DERIVED, Artefact, load as load_artefact
from twin.cli import main
from twin.grades import Capabilities
from twin.repo import ModelRepo

@pytest.fixture(autouse=True)
def _as_shipped(monkeypatch):
    """Run the guard AS SHIPPED, not as monkeypatched.

    History, because it is the whole point of this fixture. Commit 9282301 made the refusal a mode
    defaulting to `development`, under which `decide` returns `None` for everything; thirteen tests
    in this module went red and stayed red. They were then made green by this fixture setting
    `TWIN_ENACT_MODE=operations` for the test process -- which asserted a guard nobody ships and
    left the shipped default asserted by nothing at all. The docstring even cited a
    `test_the_mode_defaults_to_development` that did not exist.

    The fix was on the other side (2026-08-29): `enact_guard.DEFAULT_MODE` is now `operations` and
    `twin/ENACT_MODE` says so, so the tests and the guard agree on the SAFE reading. All this
    fixture does now is clear an ambient `TWIN_ENACT_MODE` out of the way, so a shell that happens
    to export one cannot decide what the suite observed. Flip the checked-in mode back to
    `development` and thirteen of these go red again -- deliberately, because that flip is a real
    weakening and a weakening that shows in a test is the only kind anybody notices.
    """
    monkeypatch.delenv("TWIN_ENACT_MODE", raising=False)


NETFLIX = ["--org", "netflix"]
RESPONSE = "expand-the-delivery-network"

# Layer 1 holds unchanged through every one of these, which is the whole reason layer 2 exists.
# A subagent is not in this table: whether a runtime routes a subagent's tool calls through its
# hooks is the runtime's property, and a row here would assert something nothing checks.
DISPOSES = [
    ("Bash", {"command": "gh pr merge 42 --squash"}),
    ("Bash", {"command": "gh api --method PUT repos/o/r/pulls/42/merge"}),
    ("Bash", {"command": "cd /tmp/work && gh pr merge --auto 7"}),
    ("mcp__github__merge_pull_request", {"pullNumber": 42}),
    ("merge_pull_request", {"pullNumber": 42}),
    ("mcp__forge__squash_pull_request", {"pullNumber": 42}),
]

PROPOSES = [
    ("Bash", {"command": "gh pr create --title 'raise the platform pin' --body ..."}),
    ("Bash", {"command": "gh pr view 42"}),
    ("Bash", {"command": "git commit -m 'propose: raise the platform pin'"}),
    ("Read", {"file_path": "twin/enact.py"}),
]


# -- layer 1: the structural absence -----------------------------------------------------------


def test_layer_1_exposes_propose_and_nothing_that_disposes() -> None:
    """An allow-list, not a name screen: `land` or `ship` would give nothing away to a keyword."""
    public = {
        name
        for name, value in vars(enact).items()
        if not name.startswith("_") and inspect.isfunction(value)
        and getattr(value, "__module__", "") == enact.__name__
    }
    assert public == {"propose", "dependency_pins"}


# -- the mode itself: which way it falls when nobody has said anything -------------------------
# The 2026-08-25 instruction made the refusal a mode. Nothing then asserted the mode, so the guard
# shipped permissive and the suite could not tell that from a deleted refusal. These three assert
# the mode as a fact of the repository, so the flip back is a red test rather than a quiet one.


def test_the_shipped_default_refuses(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    """No env, no readable mode file: the guard refuses. Failing closed is the whole property --
    a lost or misspelt ENACT_MODE is nobody having said the twin may dispose."""
    monkeypatch.delenv("TWIN_ENACT_MODE", raising=False)
    monkeypatch.setattr(enact_guard, "ENACT_MODE_FILE", tmp_path / "absent")
    assert enact_guard.enact_mode() == "operations"
    assert enact_guard.decide("Bash", {"command": "gh pr merge 42 --squash"}) is not None

    (tmp_path / "typo").write_text("operatoins\n", encoding="utf-8")
    monkeypatch.setattr(enact_guard, "ENACT_MODE_FILE", tmp_path / "typo")
    assert enact_guard.enact_mode() == "operations"


def test_the_checked_in_mode_is_other_hand_and_still_refuses_pushes_and_bare_merges() -> None:
    """The durable default a checkout actually gets, read off disk rather than off the constant.

    Since 2026-09-03 (ticket 88, ticket 75 Q6/Q14) it is `other-hand`: the owner authors and
    pushes, the assistant merges as the GitHub App `pavc-other-hand`. Everything `operations`
    refused is still refused except one shape, a merge that mints the app's token in the same
    command. Flipping this file back to `operations` or forward to `development` is a red test."""
    assert enact_guard.ENACT_MODE_FILE.read_text(encoding="utf-8").strip() == "other-hand"
    assert enact_guard.enact_mode() == "other-hand"
    assert enact_guard.decide("Bash", {"command": "gh pr merge 42 --squash"}) is not None
    assert enact_guard.decide("Bash", {
        "command": "git push https://github.com/policy-as-versioned-driftwood/driftwood main",
    }) is not None


def _set_mode(monkeypatch: pytest.MonkeyPatch, tmp_path: Path, mode: str) -> None:
    """Point the guard at a temp mode file holding `mode`, with no ambient env override."""
    monkeypatch.delenv("TWIN_ENACT_MODE", raising=False)
    (tmp_path / "ENACT_MODE").write_text(f"{mode}\n", encoding="utf-8")
    monkeypatch.setattr(enact_guard, "ENACT_MODE_FILE", tmp_path / "ENACT_MODE")


def _other_hand_mode(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    _set_mode(monkeypatch, tmp_path, "other-hand")


def test_other_hand_mode_admits_a_merge_only_when_it_is_made_as_the_other_hand(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    """A merge that mints the app's installation token in the same command is the second identity
    merging, and that is the whole point of the mode. A bare merge would go out under the owner's
    own token, author equal to merger, which is the state ticket 87 exists to end."""
    _other_hand_mode(monkeypatch, tmp_path)
    as_other_hand = (
        'GH_TOKEN="$(.venv/bin/python -m twin.other_hand token --org policy-as-versioned-flux)" '
        "gh pr merge 42 --squash"
    )
    assert enact_guard.decide("Bash", {"command": as_other_hand}) is None
    as_other_hand_api = (
        'GH_TOKEN="$(python3 twin/other_hand.py token --org policy-as-versioned-flux)" '
        "gh api -X PUT /repos/o/r/pulls/42/merge"
    )
    assert enact_guard.decide("Bash", {"command": as_other_hand_api}) is None

    bare = enact_guard.decide("Bash", {"command": "gh pr merge 42 --squash"})
    assert bare is not None and "other hand" in bare


def test_other_hand_mode_needs_the_token_minted_in_the_disposing_segment(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    """Naming the minter somewhere in the command is not minting for the merge. The spec review of
    2026-09-03 found the first cut matched the whole string; these are its counter-examples."""
    _other_hand_mode(monkeypatch, tmp_path)
    smuggled = [
        'echo "reminder: twin/other_hand.py token later"; gh pr merge 42 --squash',
        'T=$(python -m twin.other_hand token --org x); GH_TOKEN=$T gh pr merge 42 --squash',
        'python -m twin.other_hand token --org x && gh pr merge 42 --squash',
        'GH_TOKEN="$(python -m twin.other_hand token --org x)" gh pr view 42; gh pr merge 42',
    ]
    for command in smuggled:
        assert enact_guard.decide("Bash", {"command": command}) is not None, command
    # Two disposing segments, both made as the other hand, are admitted.
    both = (
        'GH_TOKEN="$(python -m twin.other_hand token --org x)" gh pr merge 41 --squash && '
        'GH_TOKEN="$(python -m twin.other_hand token --org x)" gh pr merge 42 --squash'
    )
    assert enact_guard.decide("Bash", {"command": both}) is None


def test_other_hand_mode_keeps_every_other_refusal(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    """The mode opens one shape. A merge-shaped MCP tool cannot carry the app's credential, and a
    push to an enactment repository is the owner's act, not the assistant's (ticket 75 Q14)."""
    _other_hand_mode(monkeypatch, tmp_path)
    assert enact_guard.decide("mcp__github__merge_pull_request", {"owner": "o"}) is not None
    assert enact_guard.decide("Bash", {
        "command": "git push https://github.com/policy-as-versioned-nist/nist main",
    }) is not None
    # Naming the token minter does not launder a push: the shape is still a push.
    assert enact_guard.decide("Bash", {
        "command": 'GH_TOKEN="$(python -m twin.other_hand token --org x)" '
                   "git push https://github.com/policy-as-versioned-nist/nist main",
    }) is not None


def test_operations_mode_refuses_even_the_other_hand_merge(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    """`operations` is unchanged: the harness invariant forces it and expects every merge refused."""
    _set_mode(monkeypatch, tmp_path, "operations")
    assert enact_guard.decide("Bash", {
        "command": 'GH_TOKEN="$(python -m twin.other_hand token --org x)" gh pr merge 42',
    }) is not None


@pytest.mark.parametrize("where", ["env", "file"])
def test_development_is_still_the_one_word_escape_hatch(
    where: str, monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    """The 2026-08-25 instruction's hatch is untouched: one word, either place, and the guard is
    off. Asserted so that "we flipped the default" never quietly becomes "we removed the mode"."""
    monkeypatch.delenv("TWIN_ENACT_MODE", raising=False)
    if where == "env":
        monkeypatch.setenv("TWIN_ENACT_MODE", "development")
    else:
        (tmp_path / "ENACT_MODE").write_text("development\n", encoding="utf-8")
        monkeypatch.setattr(enact_guard, "ENACT_MODE_FILE", tmp_path / "ENACT_MODE")
    assert enact_guard.enact_mode() == "development"
    assert enact_guard.decide("Bash", {"command": "gh pr merge 42 --squash"}) is None


# -- layer 2: the tool-call boundary -----------------------------------------------------------


@pytest.mark.parametrize(("tool", "payload"), DISPOSES)
def test_layer_2_refuses_a_merge_through_every_composition_path(tool: str, payload: dict) -> None:
    assert enact_guard.decide(tool, payload) is not None


@pytest.mark.parametrize(("tool", "payload"), PROPOSES)
def test_layer_2_admits_proposing_so_it_is_a_gate_and_not_a_wall(tool: str, payload: dict) -> None:
    assert enact_guard.decide(tool, payload) is None


def test_layer_2_refuses_a_direct_push_to_an_enactment_repository() -> None:
    """Pushing to the enactment repository is disposal without even the pull request."""
    named = "git push https://github.com/policy-as-versioned-platform/platform HEAD:main"
    assert enact_guard.decide("Bash", {"command": named}) is not None


def test_layer_2_resolves_a_bare_remote_rather_than_only_reading_the_command(tmp_path: Path) -> None:
    """`git push origin main` names no URL, so the remote has to be resolved to decide."""
    import subprocess

    work = tmp_path / "consumer"
    work.mkdir()
    subprocess.run(["git", "init", "-q"], cwd=work, check=True)
    subprocess.run(
        ["git", "remote", "add", "origin", "https://github.com/policy-as-versioned-ludlow/ludlow"],
        cwd=work, check=True,
    )
    assert enact_guard.decide("Bash", {"command": "git push origin main"}, str(work)) is not None
    assert enact_guard.decide("Bash", {"command": "git push origin main"}, str(tmp_path)) is None


def _consumer_checkout(root: Path, name: str, org: str) -> Path:
    """A real git checkout whose `origin` is an enactment repository."""
    import subprocess

    work = root / name
    work.mkdir(parents=True)
    subprocess.run(["git", "init", "-q"], cwd=work, check=True)
    subprocess.run(
        ["git", "remote", "add", "origin", f"https://github.com/{org}/{name}"],
        cwd=work, check=True,
    )
    return work


def test_layer_2_resolves_the_remote_where_git_c_points_not_where_the_shell_stands(
    tmp_path: Path,
) -> None:
    """`git -C <dir> push origin <branch>` pushes <dir>'s remote, not the caller's.

    Regression, 2026-08-31, observed for real. The remote was resolved against the
    shell's own directory regardless of `-C`, so running this guard's own repository
    root resolved `origin` to THAT repository -- which the carve-out admits -- and the
    guard passed a push to every enactment repository without printing a word. A
    refusal that silently does not fire is worse than no refusal, because the estate
    was told it had one.
    """
    work = _consumer_checkout(tmp_path, "platform", "policy-as-versioned-platform")
    caller = tmp_path / "caller"
    caller.mkdir()

    command = f"git -C {work} push -u origin ecosystem/thin-slice"
    assert enact_guard.decide("Bash", {"command": command}, str(caller)) is not None


def test_layer_2_resolves_the_remote_after_a_leading_cd(tmp_path: Path) -> None:
    """`cd <dir> && git push origin <branch>` is the same hole without the flag.

    `_push_target`'s docstring named this one as an accepted ceiling and left it open;
    it is closed with the `-C` case, because they are one bug.
    """
    work = _consumer_checkout(tmp_path, "ludlow", "policy-as-versioned-ludlow")
    caller = tmp_path / "caller"
    caller.mkdir()

    command = f"cd {work} && git push origin ecosystem/thin-slice"
    assert enact_guard.decide("Bash", {"command": command}, str(caller)) is not None


def test_a_relative_git_c_resolves_against_the_callers_directory(tmp_path: Path) -> None:
    """A relative `-C` path means what the shell would mean by it."""
    _consumer_checkout(tmp_path / "estate", "ico", "policy-as-versioned-ico")

    command = "git -C estate/ico push origin main"
    assert enact_guard.decide("Bash", {"command": command}, str(tmp_path)) is not None


def test_git_c_into_a_directory_with_no_remote_stays_refused_or_silent_but_never_open(
    tmp_path: Path,
) -> None:
    """An unreadable or remote-less directory must not fall open on a NAMED enactment URL.

    The directory leg only decides where a BARE remote resolves. A URL on the command
    line is still read directly, so a missing directory can never turn a named
    enactment push into an admitted one.
    """
    command = ("git -C " + str(tmp_path / "does-not-exist")
               + " push https://github.com/policy-as-versioned-nist/nist HEAD:main")
    assert enact_guard.decide("Bash", {"command": command}, str(tmp_path)) is not None


# -- the --git-dir family (ticket 65, review finding M17) --------------------------------------
#
# `git --git-dir=<enactment>/.git push origin main` is the `-C` hole wearing a different flag:
# the remote resolves in the repository the option names, not in the shell's directory. So do
# `--git-dir <dir>`, `--work-tree` beside it, and `GIT_DIR=<dir>` in the environment. Observed
# with git 2.55 on 2026-09-03: from a directory that is no repository at all, each of those
# resolves `origin` to the named checkout's remote, and `--work-tree` ALONE does not move
# discovery (git still walks up from the cwd). These four mirror the four `-C` tests above.


@pytest.mark.parametrize("spelling", ["--git-dir={git_dir}", "--git-dir {git_dir}"])
def test_layer_2_resolves_the_remote_where_git_dir_points_not_where_the_shell_stands(
    spelling: str, tmp_path: Path,
) -> None:
    """`git --git-dir=<dir> push origin <branch>` pushes <dir>'s remote, not the caller's.

    Review finding M17 (2026-08-31): this shape resolved against the caller's cwd, matched
    the self-push carve-out when the caller stood in this repository, and was ADMITTED. The
    same class as the `-C` regression, closed the same way.
    """
    work = _consumer_checkout(tmp_path, "platform", "policy-as-versioned-platform")
    caller = tmp_path / "caller"
    caller.mkdir()

    command = f"git {spelling.format(git_dir=work / '.git')} push -u origin ecosystem/thin-slice"
    assert enact_guard.decide("Bash", {"command": command}, str(caller)) is not None


def test_layer_2_resolves_the_remote_where_an_inline_git_dir_env_points(tmp_path: Path) -> None:
    """`GIT_DIR=<dir> git push origin <branch>` is the option spelt as an environment prefix, and
    `--git-dir=<dir> --work-tree=<tree>` is the pair git documents for a detached work tree.
    Both resolve in <dir>; both must be refused."""
    work = _consumer_checkout(tmp_path, "ludlow", "policy-as-versioned-ludlow")
    caller = tmp_path / "caller"
    caller.mkdir()

    prefixed = f"GIT_DIR={work / '.git'} git push origin ecosystem/thin-slice"
    assert enact_guard.decide("Bash", {"command": prefixed}, str(caller)) is not None
    paired = f"git --git-dir={work / '.git'} --work-tree={work} push origin ecosystem/thin-slice"
    assert enact_guard.decide("Bash", {"command": paired}, str(caller)) is not None
    with_env = f"env GIT_DIR={work / '.git'} GIT_WORK_TREE={work} git push origin main"
    assert enact_guard.decide("Bash", {"command": with_env}, str(caller)) is not None


def test_a_relative_git_dir_resolves_against_the_callers_directory(tmp_path: Path) -> None:
    """A relative `--git-dir` means what the shell would mean by it, and after `-C` it means
    what git means by it: relative to the directory `-C` moved to."""
    _consumer_checkout(tmp_path / "estate", "ico", "policy-as-versioned-ico")

    command = "git --git-dir=estate/ico/.git push origin main"
    assert enact_guard.decide("Bash", {"command": command}, str(tmp_path)) is not None
    after_c = "git -C estate --git-dir=ico/.git push origin main"
    assert enact_guard.decide("Bash", {"command": after_c}, str(tmp_path)) is not None


def test_git_dir_into_a_directory_with_no_repository_stays_refused_or_silent_but_never_open(
    tmp_path: Path,
) -> None:
    """An absent `--git-dir` is fatal to git and resolves nothing; a NAMED enactment URL on the
    same command line is still read directly, so it can never turn into an admitted push."""
    absent = tmp_path / "does-not-exist"
    command = (f"git --git-dir={absent} push "
               "https://github.com/policy-as-versioned-nist/nist HEAD:main")
    assert enact_guard.decide("Bash", {"command": command}, str(tmp_path)) is not None
    prefixed = (f"GIT_DIR={absent} git push "
                "https://github.com/policy-as-versioned-nist/nist HEAD:main")
    assert enact_guard.decide("Bash", {"command": prefixed}, str(tmp_path)) is not None


def test_the_hook_processs_own_git_dir_cannot_move_the_resolution(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path,
) -> None:
    """`GIT_DIR` in the guard's OWN environment is not the shell's environment, and it must not
    decide anything. Left unscrubbed it reaches both resolutions: a `GIT_DIR` pointing at a
    checkout of this repository makes every bare push in every enactment checkout read as a
    self-push, and one pointing at an enactment checkout makes that checkout "our own". The
    guard resolves from the command string and the cwd it was handed, and nothing else."""
    own = _consumer_checkout(tmp_path, "policy-as-versioned-flux", "policy-as-versioned-flux")
    work = _consumer_checkout(tmp_path, "nist", "policy-as-versioned-nist")

    monkeypatch.setenv("GIT_DIR", str(own / ".git"))
    assert enact_guard.decide("Bash", {"command": "git push origin main"}, str(work)) is not None

    monkeypatch.setenv("GIT_DIR", str(work / ".git"))
    monkeypatch.setenv("GIT_WORK_TREE", str(work))
    assert enact_guard.decide("Bash", {"command": "git push origin main"}, str(work)) is not None


# -- the carve-out: the twin's own model, and only that ----------------------------------------
#
# 2026-08-16, on the repository owner's standing instruction. Decision ticket 18 Q1 reads "the twin
# changes its own model constantly and the world never without a human", and the push leg had been
# refusing both: this repository is the model. It is a weakening even so — before it, the twin
# could reach no remote at all — and these tests fix how far it goes, because the boundary between
# "its own model" and "the world" is now load-bearing rather than rhetorical.

OWN_REPOSITORY = "https://github.com/policy-as-versioned-flux/policy-as-versioned-flux"
SIBLING_IN_THE_SAME_ORG = "https://github.com/policy-as-versioned-flux/policy"


@pytest.mark.parametrize("url", [OWN_REPOSITORY, OWN_REPOSITORY + ".git",
                                "git@github.com:policy-as-versioned-flux/policy-as-versioned-flux.git"])
def test_a_push_to_the_twins_own_repository_is_admitted(url: str) -> None:
    """The model, not the world. Every remote spelling of it, since an ssh remote and an https one
    are the same repository and a guard that admitted only one form would be a coin toss."""
    assert enact_guard.decide("Bash", {"command": f"git push {url} main"}) is None


def test_a_push_to_a_sibling_repository_in_the_same_org_is_still_refused() -> None:
    """The sharp edge of the carve-out, and the reason it compares whole repositories rather than
    the `policy-as-versioned-*` prefix: that prefix is the **org**, and the org holds the enactment
    repositories beside the twin's own. Matching on it would have opened every one of them."""
    refused = enact_guard.decide("Bash", {"command": f"git push {SIBLING_IN_THE_SAME_ORG} main"})
    assert refused is not None, "the carve-out leaked from the twin's own repository to the org"
    assert "enactment repository" in refused


def test_the_carve_out_is_anchored_to_this_file_not_to_the_callers_directory(tmp_path: Path) -> None:
    """A `cd` into an enactment repository must not make that repository "our own". The guard
    resolves its own origin from `__file__`, so the caller's `cwd` cannot move the boundary."""
    import subprocess

    impostor = tmp_path / "impostor"
    impostor.mkdir()
    subprocess.run(["git", "init", "-q"], cwd=impostor, check=True)
    subprocess.run(
        ["git", "remote", "add", "origin", "https://github.com/policy-as-versioned-nist/nist"],
        cwd=impostor, check=True,
    )
    assert enact_guard.decide("Bash", {"command": "git push origin main"}, str(impostor)) is not None


def test_the_refusal_stays_closed_when_the_guard_cannot_resolve_its_own_origin(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """An unresolvable origin must not read as "everything is our own". Fail closed: with no
    known own repository, every enactment target is refused exactly as it was before."""
    monkeypatch.setattr(enact_guard, "_own_repository", lambda cwd: "")
    assert enact_guard.decide("Bash", {"command": f"git push {OWN_REPOSITORY} main"}) is not None


def _feed(monkeypatch: pytest.MonkeyPatch, payload: str) -> None:
    monkeypatch.setattr("sys.stdin", io.StringIO(payload))


def test_the_hook_emits_a_deny_decision_a_runtime_can_act_on(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture
) -> None:
    _feed(monkeypatch, json.dumps({"tool_name": "Bash", "tool_input": DISPOSES[0][1]}))
    assert enact_guard.main() == 0
    decision = json.loads(capsys.readouterr().out)["hookSpecificOutput"]
    assert decision["permissionDecision"] == enact_guard.DENY
    # The reason text depends on the shipped mode: `operations` says the twin only proposes,
    # `other-hand` says the merge must be made as the other hand. Either is a deny with a reason.
    reason = decision["permissionDecisionReason"]
    assert "disposes rather than proposes" in reason or "other hand" in reason


def test_an_unreadable_payload_identifies_no_tool_call(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture
) -> None:
    """Nothing to refuse is not the same as failing open on the merge path — layer 1 still holds."""
    _feed(monkeypatch, "not json at all")
    assert enact_guard.main() == 0
    assert capsys.readouterr().out == ""


def test_the_call_site_routes_every_tool_name_not_a_merge_shaped_subset() -> None:
    """`decide` can only refuse a call the runtime hands it, so a name-screening matcher would put
    layer 1's rejected technique one level further out, where nothing else would catch it."""
    settings = json.loads((Path(__file__).resolve().parents[1] / ".claude" / "settings.json").read_text())
    matchers = [
        str(group.get("matcher", ""))
        for group in settings["hooks"]["PreToolUse"]
        if any("enact_guard.py" in str(e.get("command", "")) for e in group.get("hooks", []))
    ]
    assert matchers
    for unrevealing in ("land_pull_request", "shortcuts_execute", "Bash"):
        assert any(re.fullmatch(m, unrevealing) for m in matchers)


# -- the proposal ------------------------------------------------------------------------------


@pytest.fixture()
def proposal(model_repo_dir: Path, caps: Capabilities) -> Artefact:
    repo = ModelRepo.open(model_repo_dir)
    return enact.propose(repo, caps, "netflix", RESPONSE, enact.POLICY, ["twin", "propose"])


def test_a_proposal_is_derived_so_no_endorsement_can_be_attached(proposal: Artefact) -> None:
    from twin import attest

    assert proposal.mark == DERIVED
    with pytest.raises(attest.AttestationError):
        attest.build(proposal, [{"identity": "someone@example.invalid"}], material=b"k")


def test_a_proposal_states_both_layers_with_the_failure_mode_of_each(proposal: Artefact) -> None:
    layers = proposal.body["layers"]
    assert [layer["layer"] for layer in layers] == ["structural absence", "tool-call boundary"]
    assert all(layer["holds"] and layer["fails_when"] and layer["cannot_fail_by"] for layer in layers)


def test_a_proposal_carries_the_narrowed_claim(proposal: Artefact) -> None:
    assert "not THE definition of governance" in proposal.body["narrowed_claim"]


def test_the_channel_has_no_default_and_admits_only_the_two_narrowed_roles(
    model_repo_dir: Path, caps: Capabilities
) -> None:
    repo = ModelRepo.open(model_repo_dir)
    with pytest.raises(enact.EnactError, match="not one of"):
        enact.propose(repo, caps, "netflix", RESPONSE, "whatever-is-convenient", ["twin", "propose"])


def test_an_unknown_response_is_refused(model_repo_dir: Path, caps: Capabilities) -> None:
    repo = ModelRepo.open(model_repo_dir)
    with pytest.raises(enact.EnactError, match="no response"):
        enact.propose(repo, caps, "netflix", "no-such-response", enact.RECORD, ["twin", "propose"])


def test_a_response_that_crosses_the_universal_floor_is_refused_not_priced(
    model_repo_dir: Path, caps: Capabilities
) -> None:
    """A proposal is not a second door past the constraint pre-filter.

    `twin options`/`twin price` remove `instrument-viewers-without-telling-them` before anything
    prices it (`no-covert-sensing`, the universal floor). Nothing about that removal used to reach
    `twin propose`, which reads the overlay directly — so the excluded option had a signed,
    derived, priced proposal available to it through a second verb. Asserted on the message naming
    the crossed floor id, not merely on the raised type, so a refusal for the wrong reason (an
    unknown response, an unknown channel) does not satisfy this test.
    """
    repo = ModelRepo.open(model_repo_dir)
    with pytest.raises(enact.EnactError, match="no-covert-sensing"):
        enact.propose(
            repo, caps, "netflix", "instrument-viewers-without-telling-them", enact.RECORD,
            ["twin", "propose"],
        )


def test_the_dependency_pins_are_real_and_report_what_they_do_not_establish(proposal: Artefact) -> None:
    """Consumed by real separate repositories is a claim about files, so it is read from them."""
    dependency = proposal.body["dependency"]
    # NOT a frozen census of the estate any more (2026-08-29). This assertion has been re-pinned
    # by hand at least three times -- insurer's platform pin, driftwood's composed source, then
    # tuppence's and ludlow's -- and each re-pin was a test being dragged along behind a wider
    # estate rather than a test catching anything. Widening the slice to a fourth adopter is the
    # eco-system working; it is not a regression in `dependency_pins`, and a test that goes red on
    # it teaches everyone to re-pin the number without reading why. What is asserted instead is
    # what the docstring above actually claims -- that these are FILES, read, not described:
    # every reported figure is re-derived from the pins themselves, every name resolves to a real
    # directory or a composed source belonging to one, and the floors say the estate did not
    # quietly empty out.
    pins = dependency["pins"]
    consumed = [p for p in pins if p["cross_repository"]]
    assert dependency["cross_repository_pins"] == len(consumed) >= 8
    assert dependency["self_sync_pins"] == len(pins) - len(consumed) >= 3
    assert set(dependency["consumer_repositories"]) == {p["consumer"] for p in consumed}
    assert set(dependency["dependencies"]) == {p["dependency"] for p in consumed}
    # The three adopters and the insurer consume policy they did not write; that is the claim.
    assert {"driftwood", "tuppence", "ludlow", "insurer"} <= set(dependency["consumer_repositories"])
    estate = {p.name for p in enact.ESTATE_DIR.iterdir() if p.is_dir()}
    for name in dependency["consumer_repositories"]:
        assert name in estate, f"{name} is reported as a consumer and is not a repository"
    for name in dependency["dependencies"]:
        # `<adopter>-composed` is that adopter's own rendered set consumed as a source (ticket 40).
        assert name in estate or name.rsplit("-", 1)[0] in estate, name
    # A repository syncing itself consumes nobody's policy, so it never reaches this list.
    assert not [p for p in consumed if p["consumer"] == p["dependency"]]
    assert all(pin["tag"] for pin in dependency["pins"])
    # mo-12 repointed ESTATE_DIR at the live .estate-clone/ clone of the real repos (was the hub's
    # own frozen estate/ mirror). Read live, this now shows mo-10's landed work: every
    # cross-repository pin (nist, platform) carries a real commit line in driftwood/tuppence/
    # ludlow's gitops manifests; each repo's own self-sync GitRepository is still the
    # commented-out placeholder ("pinned at release by the wave-push", not yet done). Verified
    # directly against the clone, not assumed — see mo-12 ticket Comments.
    assert all(pin["commit_pinned"] for pin in dependency["pins"] if pin["cross_repository"])
    # The self-sync placeholders have since been filled in too, so every pin in the live estate
    # now carries a commit and this is no longer the two-sided assertion it was.
    assert all(pin["commit_pinned"] for pin in dependency["pins"] if not pin["cross_repository"])
    assert any("movable name" in limit for limit in dependency["limits"])


def test_propose_emits_from_the_cli(model_repo_dir: Path, tmp_path: Path) -> None:
    out = tmp_path / "enactment-proposal.json"
    code = main([
        "propose", "--repo", str(model_repo_dir), *NETFLIX,
        "--response", RESPONSE, "--channel", enact.RECORD, "--out", str(out),
    ])
    assert code == 0
    body = load_artefact(out)["body"]
    assert body["channel"]["role"] == enact.RECORD
    assert body["disposition"]["state"] == "proposed"
    assert "no path to it" in body["disposition"]["disposed_by"]


def test_the_capability_is_graded_against_decision_ticket_18(caps: Capabilities) -> None:
    grade = caps.require(enact.CAPABILITY)
    assert grade.owning_ticket == "18"
    # Criteria 2 and 4 are build tickets 68 and 67's, ticked beside these two rather than by this
    # ticket. Criterion 5 is build ticket 86's: `_credit()` now consumes the graded action state.
    assert grade.grade == "full"
    assert [c.index for c in grade.criteria if c.checked] == [1, 2, 3, 4, 5]
