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
def _operations_mode(monkeypatch):
    """Every test in this module asserts what the guard DOES when it is on, never what the default
    is. `enact_guard.decide` opens with `if enact_mode() != "operations": return None` (commit
    9282301, "make enact_guard's disposition refusal a mode, default permissive while building"),
    and the mode defaults to `development`, so thirteen of these had been returning None and
    failing since that commit -- a red suite that made a real regression in the guard
    indistinguishable from the deliberate default. The default itself is asserted by
    `test_the_mode_defaults_to_development` style coverage in the guard's own tests, not here.
    """
    monkeypatch.setenv("TWIN_ENACT_MODE", "operations")


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
    assert "disposes rather than proposes" in decision["permissionDecisionReason"]


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
    # Re-read against the live .estate-clone on 2026-08-29 and updated to what is actually there,
    # rather than left asserting the estate of an earlier wave: the `insurer` party now carries its
    # own gitops/platform/platform-pin.yaml (ticket 36 -- a pure consumer pins the platform without
    # reconciling it), and driftwood's gitops/composed/composed-set.yaml added `driftwood-composed`
    # as a source (ticket 40). Both are real repositories consuming real pins, so both belong here.
    assert {"driftwood", "insurer", "ludlow", "tuppence"} == set(dependency["consumer_repositories"])
    # A repository syncing itself consumes nobody's policy, so it never reaches this list.
    assert {"platform", "nist", "driftwood-composed"} == set(dependency["dependencies"])
    assert dependency["cross_repository_pins"] == 8
    assert dependency["self_sync_pins"] == 3
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
