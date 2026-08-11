"""Contestability as a primary workflow (build ticket 60)."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from twin.artefact import ArtefactError, digest_of_file, load as load_artefact
from twin.challenges import (
    KIND_CHALLENGE,
    KIND_RESOLUTION,
    ChallengeError,
    for_artefact,
    raise_challenge,
    refuse_answering_a_different_claim,
    resolve,
)
from twin.cli import main

NETFLIX = ["--org", "netflix"]


@pytest.fixture()
def graph_path(model_repo_dir: Path, tmp_path: Path) -> Path:
    out = tmp_path / "graph.json"
    assert main(["graph", "--repo", str(model_repo_dir), *NETFLIX, "--out", str(out)]) == 0
    return out


def test_raising_a_challenge_captures_the_claimed_value(graph_path: Path) -> None:
    doc = load_artefact(graph_path)
    sha = digest_of_file(graph_path)
    artefact = raise_challenge(doc, sha, "components[1].evolution", "disputed", ["twin", "challenge"])
    assert artefact.body["claim_path"] == "components[1].evolution"
    assert artefact.body["challenged"] == {"kind": "graph", "sha256": sha, "produced_by": doc["envelope"]["produced_by"]}
    assert artefact.body["status"] == "open"


def test_a_challenge_to_an_unknown_claim_is_refused(graph_path: Path) -> None:
    doc = load_artefact(graph_path)
    sha = digest_of_file(graph_path)
    with pytest.raises(ChallengeError, match="not a claim"):
        raise_challenge(doc, sha, "no.such.path", "disputed", ["twin", "challenge"])


def test_a_challenge_with_no_reason_is_refused(graph_path: Path) -> None:
    doc = load_artefact(graph_path)
    sha = digest_of_file(graph_path)
    with pytest.raises(ChallengeError, match="no reason"):
        raise_challenge(doc, sha, "components[1].evolution", "   ", ["twin", "challenge"])


def test_resolve_inherits_the_challenges_own_claim_path(graph_path: Path) -> None:
    """No parameter on `resolve()` can name a different claim than the challenge itself."""
    doc = load_artefact(graph_path)
    sha = digest_of_file(graph_path)
    challenge = raise_challenge(doc, sha, "components[1].evolution", "disputed", ["twin", "challenge"])
    challenge_doc = json.loads(challenge.to_bytes())
    resolution = resolve(challenge_doc, challenge.digest(), "fixed", ["twin", "resolve-challenge"])
    assert resolution.body["claim_path"] == "components[1].evolution"
    assert resolution.body["challenged"] == challenge.body["challenged"]


def test_resolve_refuses_a_doc_that_is_not_a_challenge(graph_path: Path) -> None:
    doc = load_artefact(graph_path)  # a graph artefact, not a challenge
    with pytest.raises(ChallengeError, match="is not a"):
        resolve(doc, "sha", "response", ["twin", "resolve-challenge"])


def test_a_resolution_naming_a_different_claim_is_refused() -> None:
    """The structural guard's second lock, on a hand-built violation `resolve()` itself cannot
    produce — the same double-lock `refuse_upstream_under_intervention` is for an intervention."""
    challenge_doc = {
        "envelope": {"kind": KIND_CHALLENGE},
        "body": {"claim_path": "priced.the-operator.mode", "challenged": {"kind": "x", "sha256": "y"}},
    }
    planted = {
        "envelope": {"kind": KIND_RESOLUTION},
        "body": {"claim_path": "exposure.declared.the-operator", "response": "the total is fine"},
    }
    with pytest.raises(ArtefactError, match="cannot be answered by pointing at a different claim"):
        refuse_answering_a_different_claim(challenge_doc, planted)


def test_for_artefact_partitions_open_and_resolved(graph_path: Path) -> None:
    doc = load_artefact(graph_path)
    sha = digest_of_file(graph_path)
    open_challenge = raise_challenge(doc, sha, "components[1].evolution", "disputed A", ["twin", "challenge"])
    resolved_challenge = raise_challenge(doc, sha, "components[0].evolution", "disputed B", ["twin", "challenge"])
    resolved_doc = json.loads(resolved_challenge.to_bytes())
    resolution = resolve(resolved_doc, resolved_challenge.digest(), "fixed", ["twin", "resolve-challenge"])

    report = for_artefact(
        sha,
        [json.loads(open_challenge.to_bytes()), json.loads(resolved_challenge.to_bytes())],
        [json.loads(resolution.to_bytes())],
    )
    assert report["has_unresolved_challenges"] is True
    assert [e["claim_path"] for e in report["open"]] == ["components[1].evolution"]
    assert [e["claim_path"] for e in report["resolved"]] == ["components[0].evolution"]


def test_a_challenge_to_a_constituent_is_not_closed_by_a_resolution_to_an_aggregate(graph_path: Path) -> None:
    """The AC, made concrete: a resolution exists on this artefact, but for a *different* claim
    path than the one that was challenged — the challenge must still show as open."""
    doc = load_artefact(graph_path)
    sha = digest_of_file(graph_path)
    constituent_challenge = raise_challenge(
        doc, sha, "components[1].evolution", "this one figure is wrong", ["twin", "challenge"]
    )
    # A resolution for a *different* claim on the same artefact — built directly rather than via
    # resolve(), which is the only way one could ever point at the wrong path.
    unrelated_resolution = {
        "envelope": {"kind": KIND_RESOLUTION},
        "body": {
            "challenge_sha256": "not-the-constituent-challenges-digest",
            "claim_path": "components[0].evolution",
            "response": "unrelated",
        },
    }
    report = for_artefact(sha, [json.loads(constituent_challenge.to_bytes())], [unrelated_resolution])
    assert report["has_unresolved_challenges"] is True
    assert report["open"][0]["claim_path"] == "components[1].evolution"


def test_challenges_only_apply_to_the_artefact_they_named(graph_path: Path) -> None:
    doc = load_artefact(graph_path)
    sha = digest_of_file(graph_path)
    challenge = raise_challenge(doc, sha, "components[1].evolution", "disputed", ["twin", "challenge"])
    report = for_artefact("a-different-artefacts-sha256", [json.loads(challenge.to_bytes())], [])
    assert report["open"] == []
    assert report["resolved"] == []


# -- CLI ---------------------------------------------------------------------------------------


def test_cli_raises_and_signs_a_challenge(graph_path: Path, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("TWIN_SIGNING_KEY", "test-key")
    out = tmp_path / "challenge.json"
    rc = main([
        "challenge", "--artefact", str(graph_path), "--claim-path", "components[1].evolution",
        "--reason", "disputed in a test", "--out", str(out),
    ])
    assert rc == 0
    doc = json.loads(out.read_bytes())
    assert doc["envelope"]["kind"] == KIND_CHALLENGE
    from twin import attest

    sidecar = attest.load(attest.sidecar_for(out))
    assert attest.human_signed(sidecar)


def test_cli_resolve_then_verify_shows_the_status(
    graph_path: Path, tmp_path: Path, monkeypatch: pytest.MonkeyPatch, model_repo_dir: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    monkeypatch.setenv("TWIN_SIGNING_KEY", "test-key")
    challenge_out = tmp_path / "challenge.json"
    assert main([
        "challenge", "--artefact", str(graph_path), "--claim-path", "components[1].evolution",
        "--reason", "disputed in a test", "--out", str(challenge_out),
    ]) == 0

    capsys.readouterr()
    assert main(["verify", str(graph_path), "--repo", str(model_repo_dir), "--challenge", str(challenge_out)]) == 0
    out = capsys.readouterr().out
    assert "OPEN" in out
    assert "components[1].evolution" in out

    resolution_out = tmp_path / "resolution.json"
    assert main([
        "resolve-challenge", "--challenge", str(challenge_out), "--response", "fixed in review",
        "--out", str(resolution_out),
    ]) == 0

    capsys.readouterr()
    assert main([
        "verify", str(graph_path), "--repo", str(model_repo_dir),
        "--challenge", str(challenge_out), "--challenge", str(resolution_out),
    ]) == 0
    out = capsys.readouterr().out
    assert "resolved" in out
    assert "OPEN" not in out


def test_cli_challenge_to_an_unknown_claim_exits_nonzero(graph_path: Path, tmp_path: Path) -> None:
    out = tmp_path / "challenge.json"
    rc = main([
        "challenge", "--artefact", str(graph_path), "--claim-path", "no.such.path",
        "--reason", "x", "--out", str(out),
    ])
    assert rc == 2
    assert not out.exists()
