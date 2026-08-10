"""`twin verify <artefact>` — recompute from pins (build ticket 10).

This is where determinism-given-pins stops being an aspiration. If an artefact cannot be
recomputed from what it recorded, its attestation is a claim rather than a proof.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from twin import fixtures
from twin.canon import canonical_json
from twin.cli import main
from twin.reproduce import ReproduceError, reproduce
from twin.repo import RepoError

NETFLIX = ["--org", "netflix"]


@pytest.fixture()
def artefacts(model_repo_dir: Path, tmp_path: Path) -> dict[str, Path]:
    out = {
        name: tmp_path / f"{name}.json"
        for name in ("bound-signal", "forecast-bundle", "score-card", "graph", "propagation", "priced-option-set")
    }
    assert main(["sense", "--repo", str(model_repo_dir), *NETFLIX,
                 "--signal", "price-separation-announced", "--out", str(out["bound-signal"])]) == 0
    assert main(["run", "--repo", str(model_repo_dir), *NETFLIX, "--regime", "as-consumed",
                 "--scenario", "dvd-decline-2011", "--out", str(out["forecast-bundle"])]) == 0
    assert main(["score", "--repo", str(model_repo_dir), *NETFLIX,
                 "--forecast", str(out["forecast-bundle"]), "--outcome", "dvd-decline-2011-resolved",
                 "--out", str(out["score-card"])]) == 0
    assert main(["graph", "--repo", str(model_repo_dir), *NETFLIX, "--out", str(out["graph"])]) == 0
    # A sampled artefact reproduces from its pins for the same reason a scored one does: the seed
    # and the draw count are part of the format, not a runtime choice (build tickets 20 and 28).
    assert main(["propagate", "--repo", str(model_repo_dir), *NETFLIX,
                 "--origin", "content-delivery-network", "--out", str(out["propagation"])]) == 0
    assert main(["options", "--repo", str(model_repo_dir), *NETFLIX,
                 "--perspective", "the-operator", "--out", str(out["priced-option-set"])]) == 0
    return out


@pytest.mark.parametrize(
    "kind",
    ["bound-signal", "forecast-bundle", "score-card", "graph", "propagation", "priced-option-set"],
)
def test_every_artefact_reproduces_from_its_pins(model_repo_dir: Path, artefacts: dict[str, Path], kind: str) -> None:
    report = reproduce(model_repo_dir, artefacts[kind])
    assert report.reproduces, report.diff
    assert report.expected == report.actual


def test_reproducing_a_score_card_reproduces_the_chain(model_repo_dir: Path, artefacts: dict[str, Path]) -> None:
    """The card names a bundle by digest. Reproducing the card recomputes that bundle too."""
    report = reproduce(model_repo_dir, artefacts["score-card"])
    assert [link.kind for link in report.chain] == ["forecast-bundle"]
    recorded = json.loads(artefacts["score-card"].read_bytes())["body"]["subject"]["sha256"]
    assert report.chain[0].expected == recorded == report.chain[0].actual


def test_tolerance_is_zero_and_the_quantisation_is_in_the_format(
    model_repo_dir: Path, artefacts: dict[str, Path]
) -> None:
    from twin.scoring import SIGNIFICANT_DIGITS

    report = reproduce(model_repo_dir, artefacts["score-card"]).as_dict()
    assert report["tolerance"] == "none — byte identity"
    assert report["declared_quantisation"] == f"{SIGNIFICANT_DIGITS} significant digits on scores"


def test_a_non_deterministic_operation_is_caught_rather_than_passing_silently(
    model_repo_dir: Path, artefacts: dict[str, Path], monkeypatch: pytest.MonkeyPatch
) -> None:
    """The failure this verb exists for: output that does not depend only on the pins."""
    from twin import verbs

    real = verbs.run
    counter = {"n": 0}

    def drifting(*args, **kwargs):
        counter["n"] += 1
        artefact = real(*args, **kwargs)
        body = {**artefact.body, "scenario": {**artefact.body["scenario"], "question": f"call {counter['n']}"}}
        return type(artefact)(
            kind=artefact.kind, mark=artefact.mark, command=artefact.command,
            pins=artefact.pins, depth=artefact.depth, body=body,
        )

    monkeypatch.setattr(verbs, "run", drifting)
    report = reproduce(model_repo_dir, artefacts["forecast-bundle"])
    assert not report.reproduces
    assert report.diff and "call 1" in report.diff
    assert "recomputed" in report.diff and "recorded" in report.diff


def test_a_tampered_artefact_does_not_reproduce(model_repo_dir: Path, artefacts: dict[str, Path], tmp_path: Path) -> None:
    doc = json.loads(artefacts["forecast-bundle"].read_bytes())
    doc["body"]["forecasts"][0]["probability"] = 0.99
    tampered = tmp_path / "tampered.json"
    tampered.write_bytes(canonical_json(doc))

    report = reproduce(model_repo_dir, tampered)
    assert not report.reproduces
    assert "0.99" in report.diff


def test_a_repository_that_does_not_hold_the_pin_is_refused_rather_than_diffed(
    artefacts: dict[str, Path], tmp_path: Path
) -> None:
    """A pin names a commit and a tree. Not finding them is not a divergence, it is a wrong repo."""
    other = tmp_path / "unrelated"
    other.mkdir()
    fixtures.git(other, "init", "-q", "-b", "main", "--object-format=sha1")
    (other / "readme.md").write_text("not a model repository\n", encoding="utf-8")
    fixtures.git(other, "add", "-A")
    fixtures.git(other, "commit", "-q", "-m", "something else entirely")

    with pytest.raises((ReproduceError, RepoError)):
        reproduce(other, artefacts["forecast-bundle"])


def test_a_repository_whose_history_still_holds_the_pin_reproduces(
    artefacts: dict[str, Path], tmp_path: Path
) -> None:
    """The world moving on does not invalidate an artefact pinned to an earlier commit — that is
    the whole point of pinning rather than pointing."""
    moved_on = fixtures.build(tmp_path / "moved-on")
    fixtures.advance_world(moved_on)
    assert reproduce(moved_on, artefacts["forecast-bundle"]).reproduces


def test_the_cli_reports_reproduce_and_diverge_with_the_right_exit_code(
    model_repo_dir: Path, artefacts: dict[str, Path], tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    assert main(["verify", str(artefacts["score-card"]), "--repo", str(model_repo_dir)]) == 0
    assert "REPRODUCES" in capsys.readouterr().out

    doc = json.loads(artefacts["score-card"].read_bytes())
    doc["body"]["scores"][0]["brier"] = 0.0
    tampered = tmp_path / "tampered.json"
    tampered.write_bytes(canonical_json(doc))

    assert main(["verify", str(tampered), "--repo", str(model_repo_dir)]) == 1
    assert "DIVERGES" in capsys.readouterr().out


def test_verify_without_a_repository_says_why_it_needs_one(
    artefacts: dict[str, Path], capsys: pytest.CaptureFixture[str]
) -> None:
    assert main(["verify", str(artefacts["score-card"])]) == 2
    assert "not where that repository lives" in capsys.readouterr().err


def test_a_card_scored_after_a_later_commit_still_reproduces(model_repo_dir: Path, tmp_path: Path) -> None:
    """The normal case: a forecast is made, then the answer key is committed, then it is scored.

    Replaying the bundle at the *card's* pin instead of the bundle's own would break every one.
    """
    repo_dir = fixtures.build(tmp_path / "later")
    bundle, card = tmp_path / "b.json", tmp_path / "c.json"
    assert main(["run", "--repo", str(repo_dir), *NETFLIX, "--scenario", "dvd-decline-2011",
                 "--regime", "as-consumed",
                 "--out", str(bundle)]) == 0
    fixtures.git(repo_dir, "commit", "-q", "--allow-empty", "-m", "the answer key arrives later")
    assert main(["score", "--repo", str(repo_dir), *NETFLIX, "--forecast", str(bundle),
                 "--outcome", "dvd-decline-2011-resolved", "--out", str(card)]) == 0

    report = reproduce(repo_dir, card)
    assert report.reproduces, report.diff
    assert report.chain[0].reproduces, "the bundle was replayed at the wrong pin"


@pytest.mark.parametrize(
    ("command", "complaint"),
    [
        (["twin", "backtest", "--org", "netflix"], "names no --scenario"),
        (["twin", "run", "--org", "netflix"], "names no --scenario"),
        (["twin", "run", "--scenario", "dvd-decline-2011"], "names no --org"),
        (["twin"], "not a replayable command"),
    ],
)
def test_an_unreplayable_command_is_a_sentence_not_a_traceback(
    model_repo_dir: Path, artefacts: dict[str, Path], tmp_path: Path, command: list[str], complaint: str
) -> None:
    doc = json.loads(artefacts["forecast-bundle"].read_bytes())
    doc["envelope"]["produced_by"]["command"] = command
    broken = tmp_path / "broken.json"
    broken.write_bytes(canonical_json(doc))

    with pytest.raises(ReproduceError, match=complaint):
        reproduce(model_repo_dir, broken)
    assert main(["verify", str(broken), "--repo", str(model_repo_dir)]) == 2


def test_reproducing_leaves_no_temporary_files_behind(model_repo_dir: Path, artefacts: dict[str, Path]) -> None:
    import tempfile

    before = set(Path(tempfile.gettempdir()).glob("twin-replay-*"))
    reproduce(model_repo_dir, artefacts["score-card"])
    assert set(Path(tempfile.gettempdir()).glob("twin-replay-*")) == before
