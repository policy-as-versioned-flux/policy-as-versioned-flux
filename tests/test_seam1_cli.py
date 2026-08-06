"""Seam 1 — the artefact CLI. The highest boundary in the system, and the primary one.

Assertions are on emitted artefacts, never on internal structure: code here is disposable, and a
test coupled to internals becomes the sunk cost that resists the rewrite.
"""

from __future__ import annotations

import json
import os
from pathlib import Path

import pytest

from twin import fixtures
from twin.cli import main
from twin.invariants.checks import golden_digests

NETFLIX = ["--org", "netflix"]
KEY = "a-test-key"


def _run(repo_dir: Path, *args: str) -> int:
    return main([*args, "--repo", str(repo_dir)])


def _sense(repo_dir: Path, out: Path) -> int:
    return _run(repo_dir, "sense", *NETFLIX, "--signal", "price-separation-announced", "--out", str(out))


def _forecast(repo_dir: Path, out: Path, at: str | None = None) -> int:
    extra = ["--at", at] if at else []
    return _run(repo_dir, "run", *NETFLIX, "--scenario", "dvd-decline-2011", *extra, "--out", str(out))


def _score(repo_dir: Path, bundle: Path, out: Path) -> int:
    return _run(
        repo_dir,
        "score",
        *NETFLIX,
        "--forecast",
        str(bundle),
        "--outcome",
        "dvd-decline-2011-resolved",
        "--out",
        str(out),
    )


def test_sense_emits_a_bound_signal_with_its_pins(model_repo_dir: Path, tmp_path: Path) -> None:
    out = tmp_path / "bound.json"
    assert _sense(model_repo_dir, out) == 0

    doc = json.loads(out.read_bytes())
    assert doc["envelope"]["kind"] == "bound-signal"
    assert doc["envelope"]["mark"] == "derived"
    assert doc["envelope"]["pins"]["model_repo"]["commit"]
    assert doc["envelope"]["pins"]["world"]["tree"]
    assert doc["body"]["signal"]["date"] == "2011-07-12"

    binding = doc["body"]["bindings"][0]
    assert binding["component"] == "dvd-by-mail"
    assert binding["evidence_grade"] == 5, "a hand-authored binding claim is grade 5 by construction"


def test_an_execution_emits_forecasts_plural(model_repo_dir: Path, tmp_path: Path) -> None:
    out = tmp_path / "bundle.json"
    assert _forecast(model_repo_dir, out) == 0

    body = json.loads(out.read_bytes())["body"]
    assert isinstance(body["forecasts"], list)
    assert len(body["forecasts"]) == 3, "three rival world models, three forecasts"
    assert {f["world_model"] for f in body["forecasts"]} == {
        "twin-default",
        "rival-fast-commoditisation",
        "netflix-believed",
    }
    assert "forecast" not in body, "no singular forecast field exists to be read instead of the list"


def test_every_forecast_carries_its_own_pins(model_repo_dir: Path, tmp_path: Path) -> None:
    out = tmp_path / "bundle.json"
    _forecast(model_repo_dir, out)
    for forecast in json.loads(out.read_bytes())["body"]["forecasts"]:
        pins = forecast["pins"]
        assert pins["model_repo"]["commit"] and pins["world"]["commit"] and pins["overlay"]["commit"]
        assert pins["tool"]["version"]


def test_score_names_the_forecast_by_pin_not_by_path(model_repo_dir: Path, tmp_path: Path) -> None:
    bundle, card = tmp_path / "bundle.json", tmp_path / "card.json"
    _forecast(model_repo_dir, bundle)
    assert _score(model_repo_dir, bundle, card) == 0

    raw = card.read_text(encoding="utf-8")
    body = json.loads(raw)["body"]
    assert body["subject"]["sha256"], "the bundle is named by digest"
    assert str(bundle) not in raw and str(tmp_path) not in raw, "no filesystem path leaks into the card"
    assert {s["world_model"] for s in body["scores"]} == {
        "twin-default",
        "rival-fast-commoditisation",
        "netflix-believed",
    }


def test_the_believed_map_scores_worse_than_the_rivals(model_repo_dir: Path, tmp_path: Path) -> None:
    """belief vs revealed is the anticipation failure — the spread has to survive to the score."""
    bundle, card = tmp_path / "bundle.json", tmp_path / "card.json"
    _forecast(model_repo_dir, bundle)
    _score(model_repo_dir, bundle, card)

    scores = {s["world_model"]: s["brier"] for s in json.loads(card.read_bytes())["body"]["scores"]}
    assert scores["netflix-believed"] > scores["twin-default"] > scores["rival-fast-commoditisation"]


def test_identical_pins_produce_identical_bytes(model_repo_dir: Path, tmp_path: Path) -> None:
    first, second = tmp_path / "a.json", tmp_path / "b.json"
    _forecast(model_repo_dir, first)
    _forecast(model_repo_dir, second)
    assert first.read_bytes() == second.read_bytes()


def test_artefacts_match_the_committed_golden_digests(model_repo_dir: Path, tmp_path: Path) -> None:
    """The golden file another architecture's CI run must reproduce."""
    from twin.canon import sha256_hex

    golden = golden_digests()
    assert golden, "no golden digests committed; run `twin verify --bless-goldens`"

    bundle, bound, card = tmp_path / "b.json", tmp_path / "s.json", tmp_path / "c.json"
    _sense(model_repo_dir, bound)
    _forecast(model_repo_dir, bundle)
    _score(model_repo_dir, bundle, card)

    assert sha256_hex(bound.read_bytes()) == golden["bound-signal"]
    assert sha256_hex(bundle.read_bytes()) == golden["forecast-bundle"]
    assert sha256_hex(card.read_bytes()) == golden["score-card"]


def test_an_attestation_sidecar_accompanies_every_artefact(model_repo_dir: Path, tmp_path: Path) -> None:
    out = tmp_path / "bundle.json"
    _forecast(model_repo_dir, out)

    sidecar = json.loads(Path(str(out) + ".att.json").read_bytes())
    from twin.canon import sha256_hex

    assert sidecar["subject"]["sha256"] == sha256_hex(out.read_bytes())
    assert sidecar["mark"] == "derived"
    assert sidecar["human_involvement"] == {"present": False, "signatures": []}
    assert sidecar["produced_by"]["runtime"]["python"], "runtime facts live here, not in the artefact"
    # Unsigned here because the test environment holds no key, and the sidecar says which one
    # is missing rather than carrying a placeholder that reads as signed.
    assert sidecar["agent_signature"] is None
    assert "TWIN_SIGNING_KEY" in sidecar["signature_status"]


def test_the_artefact_carries_no_machine_varying_fact(model_repo_dir: Path, tmp_path: Path) -> None:
    """Anything host-specific would break identical bytes across architectures."""
    import platform

    out = tmp_path / "bundle.json"
    _forecast(model_repo_dir, out)
    raw = out.read_text(encoding="utf-8")
    for leak in (platform.python_version(), platform.machine(), str(tmp_path), str(model_repo_dir)):
        assert leak not in raw


def test_a_dirty_model_repository_is_refused(scratch_repo: Path, tmp_path: Path) -> None:
    (scratch_repo / "world" / "meta.yaml").write_text("id: world\nunit: world\n", encoding="utf-8")
    assert _forecast(scratch_repo, tmp_path / "nope.json") == 2
    assert not (tmp_path / "nope.json").exists()


def test_an_untracked_file_also_counts_as_dirty(scratch_repo: Path, tmp_path: Path) -> None:
    (scratch_repo / "world" / "components" / "sneaked-in.yaml").write_text("id: sneaked\n", encoding="utf-8")
    assert _forecast(scratch_repo, tmp_path / "nope.json") == 2


def test_an_older_ref_reads_the_older_model(scratch_repo: Path, tmp_path: Path) -> None:
    fixtures.advance_world(scratch_repo)
    assert _run(scratch_repo, "index", "--out", str(tmp_path / "idx-head")) == 0
    assert (
        main(["index", "--repo", str(scratch_repo), "--ref", "HEAD~1", "--out", str(tmp_path / "idx-prev")])
        == 0
    )

    head = json.loads((tmp_path / "idx-head" / "world.json").read_bytes())
    prev = json.loads((tmp_path / "idx-prev" / "world.json").read_bytes())
    assert "high-na-euv" in head["components"] and "high-na-euv" not in prev["components"]


def test_an_unbound_signal_does_not_sense(scratch_repo: Path, tmp_path: Path) -> None:
    claim = scratch_repo / "orgs" / "netflix" / "claims" / "bind-price-separation-to-dvd-by-mail.yaml"
    claim.unlink()
    fixtures.git(scratch_repo, "add", "-A")
    fixtures.git(scratch_repo, "commit", "-q", "-m", "drop the binding claim")
    assert _sense(scratch_repo, tmp_path / "nope.json") == 2


def test_a_live_scenario_has_no_answer_key_to_score_against(model_repo_dir: Path, tmp_path: Path) -> None:
    """Intel is the live forward case: a forecast with nothing to score it yet, and that is honest."""
    bundle = tmp_path / "intel.json"
    assert (
        main(
            [
                "run",
                "--repo",
                str(model_repo_dir),
                "--org",
                "intel",
                "--scenario",
                "euv-slip-2026",
                "--out",
                str(bundle),
            ]
        )
        == 0
    )
    assert len(json.loads(bundle.read_bytes())["body"]["forecasts"]) == 3
    assert (
        main(
            [
                "score",
                "--repo",
                str(model_repo_dir),
                "--org",
                "intel",
                "--forecast",
                str(bundle),
                "--outcome",
                "dvd-decline-2011-resolved",
                "--out",
                str(tmp_path / "nope.json"),
            ]
        )
        == 2
    ), "another org's outcome is not visible from this overlay"

    from twin.model import Overlay
    from twin.repo import ModelRepo

    intel = Overlay.load(ModelRepo.open(model_repo_dir), "intel")
    assert "dvd-decline-2011-resolved" not in intel.outcomes
    assert not (set(intel.signals) | set(intel.components)) & {
        "price-separation-announced",
        "dvd-by-mail",
        "streaming-experience",
    }


def test_ambiguous_org_is_refused_rather_than_guessed(
    model_repo_dir: Path, tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """Two overlays, no --org: guessing which tenant you meant is not a service.

    Asserting on the message, not the exit code — silently picking the first overlay also exits
    2, from an unrelated "no such scenario" a few lines later.
    """
    assert (
        main(["run", "--repo", str(model_repo_dir), "--scenario", "dvd-decline-2011",
              "--out", str(tmp_path / "nope.json")])
        == 2
    )
    assert "--org is required" in capsys.readouterr().err
    assert not (tmp_path / "nope.json").exists()


def test_the_scores_are_the_scores(model_repo_dir: Path, tmp_path: Path) -> None:
    """Pinned numerically. Ordering assertions survive swapping the rule for absolute error."""
    bundle, card = tmp_path / "bundle.json", tmp_path / "card.json"
    _forecast(model_repo_dir, bundle)
    _score(model_repo_dir, bundle, card)

    body = json.loads(card.read_bytes())["body"]
    assert body["rules"] == ["brier", "log_loss"] and body["orientation"] == "lower-is-better"
    scores = {s["world_model"]: s for s in body["scores"]}
    assert scores["twin-default"]["brier"] == pytest.approx(0.1444)
    assert scores["rival-fast-commoditisation"]["brier"] == pytest.approx(0.0361)
    assert scores["netflix-believed"]["brier"] == pytest.approx(0.5625)
    assert scores["netflix-believed"]["log_loss"] == pytest.approx(1.38629436112)
    assert {s["regime"] for s in body["scores"]} == {"as-consumed"}


def test_the_same_pins_give_the_same_bytes_from_a_separate_process(model_repo_dir: Path, tmp_path: Path) -> None:
    """Two interpreters under different hash seeds — the only in-repo proxy for two machines."""
    import subprocess
    import sys

    from twin import REPO_DIR
    from twin.canon import sha256_hex

    digests = set()
    for seed in ("0", "1", "524287"):
        out = tmp_path / f"seed-{seed}.json"
        proc = subprocess.run(
            [sys.executable, "-P", "-m", "twin", "run", "--repo", str(model_repo_dir),
             "--org", "netflix", "--scenario", "dvd-decline-2011", "--out", str(out)],
            cwd=str(REPO_DIR),
            env={**os.environ, "PYTHONHASHSEED": seed, "PYTHONPATH": str(REPO_DIR)},
            capture_output=True,
        )
        assert proc.returncode == 0, proc.stderr.decode()
        digests.add(sha256_hex(out.read_bytes()))
    assert len(digests) == 1, "iteration order is reaching the output"


# -- the gate, the perspective and the published constraint set (build tickets 19, 26, 27) ------


def test_blast_emits_the_two_halves_and_names_the_gate(model_repo_dir: Path, tmp_path: Path) -> None:
    out = tmp_path / "blast.json"
    assert _run(model_repo_dir, "blast", *NETFLIX, "--origin", "content-delivery-network",
                "--out", str(out)) == 0

    doc = json.loads(out.read_bytes())
    assert doc["envelope"]["kind"] == "blast-radius"
    assert doc["envelope"]["mark"] == "derived"
    body = doc["body"]
    assert {e["component"] for e in body["admitted_to_pricing"]} == {"streaming-experience"}
    assert {e["component"] for e in body["unpriced"]} == {"brand-goodwill", "dvd-by-mail"}
    assert body["gating"]["pin"]["pricing_threshold"] == 2


def test_exposure_reports_every_perspective_and_the_spread(model_repo_dir: Path, tmp_path: Path) -> None:
    """Naming none must not default to the operator's — that is the unstated firm's-£."""
    out = tmp_path / "exposure.json"
    assert _run(model_repo_dir, "exposure", *NETFLIX, "--scenario", "dvd-decline-2011",
                "--out", str(out)) == 0

    body = json.loads(out.read_bytes())["body"]
    assert set(body["declared_exposure"]) == {"the-operator", "the-staff-council"}
    assert body["exposure_spread"] == 148000000.0
    assert body["prefilter"]["applied"] is False


def test_the_constraint_set_is_authored_and_signed_as_a_role(tmp_path: Path) -> None:
    """The second place in this system where a human declaration is the authority."""
    from twin import attest, sign

    out = tmp_path / "constraint-set.json"
    os.environ[sign.KEY_ENV] = KEY
    try:
        assert main(["constraints", "--out", str(out)]) == 0
    finally:
        del os.environ[sign.KEY_ENV]

    doc = json.loads(out.read_bytes())
    assert doc["envelope"]["mark"] == "authored"
    assert doc["envelope"]["depth"]["grade"] is None
    sidecar = attest.load(attest.sidecar_for(out))
    signatures = sidecar["human_involvement"]["signatures"]
    assert [s["role"] for s in signatures] == ["constraint-owner"]
    assert attest.check(sidecar, out.read_bytes(), sign.signing_key(KEY)) == []


def test_a_derived_artefact_from_a_new_verb_still_refuses_a_human_signature(
    model_repo_dir: Path, tmp_path: Path
) -> None:
    from twin import sign

    out = tmp_path / "blast.json"
    _run(model_repo_dir, "blast", *NETFLIX, "--origin", "content-delivery-network", "--out", str(out))
    os.environ[sign.KEY_ENV] = KEY
    try:
        assert main(["sign", str(out), "--role", "model-steward"]) == 2
    finally:
        del os.environ[sign.KEY_ENV]
