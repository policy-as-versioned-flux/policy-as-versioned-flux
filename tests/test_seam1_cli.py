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
    return _run(repo_dir, "run", *NETFLIX, "--scenario", "dvd-decline-2011",
                "--regime", "as-consumed", *extra, "--out", str(out))


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
                "--regime",
                "as-consumed",
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
              "--regime", "as-consumed", "--out", str(tmp_path / "nope.json")])
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
             "--org", "netflix", "--scenario", "dvd-decline-2011", "--regime", "as-consumed",
             "--out", str(out)],
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


# -- propagation and the priced choice set (build tickets 20, 23, 28) ---------------------------


def test_propagate_emits_composed_attenuated_and_sampled(model_repo_dir: Path, tmp_path: Path) -> None:
    """All three, side by side. An attenuated figure alone makes the attenuation unfalsifiable."""
    out = tmp_path / "propagation.json"
    assert _run(model_repo_dir, "propagate", *NETFLIX, "--origin", "content-delivery-network",
                "--out", str(out)) == 0

    doc = json.loads(out.read_bytes())
    assert doc["envelope"]["kind"] == "propagation"
    assert doc["envelope"]["mark"] == "derived"
    body = doc["body"]
    assert {r["component"] for r in body["reached"]} == {"streaming-experience", "dvd-by-mail", "brand-goodwill"}

    first = next(p for r in body["reached"] if r["component"] == "streaming-experience" for p in r["paths"])
    assert first["composed"]["mode"] == 0.25, "one hop is the authored triple itself"
    assert first["attenuation"] == 1.0
    assert first["sampled"]["draws"] == 2000
    assert first["may_price"] is True
    assert body["attenuation"]["pin"]["directional_beyond_depth"] == 4
    assert body["calibration"]["document"] == "calibration.md"


def test_propagate_combines_the_paths_and_shows_what_independence_would_have_said(
    model_repo_dir: Path, tmp_path: Path
) -> None:
    """Build ticket 21 at seam 1: the combined figure, and the reference it is a discount from."""
    out = tmp_path / "propagation.json"
    assert _run(model_repo_dir, "propagate", *NETFLIX, "--origin", "content-delivery-network",
                "--out", str(out)) == 0

    body = json.loads(out.read_bytes())["body"]
    joint = next(r for r in body["reached"] if r["component"] == "dvd-by-mail")["joint"]
    # This fixture reaches every component by exactly one path, so the *numbers* here cannot
    # demonstrate the discount — `exact == if_independent` follows from noisy-OR of one term
    # whatever the code does. What seam 1 can assert is that the block is emitted, complete, and
    # says what it is. The discount itself is asserted at seam 2, where a diamond can be built.
    assert joint["paths_combined"] == 1 and joint["shared_edges"] == []
    assert joint["exact"] == joint["if_independent"], "one path, so there is nothing to discount"
    assert joint["double_counting_avoided"] == 0
    assert joint["sign"] in ("positive", "negative")
    assert joint["paths_dropped_by_cap"] == 0
    assert "noisy-OR" in joint["rule"] and "never summed" in joint["rule"]
    assert "conditional on the shared edges" in joint["assumption"]
    assert "drawn once per trial" in body["sampler"]["seeded_by"]


def test_intervene_and_observe_differ_only_upstream(model_repo_dir: Path, tmp_path: Path) -> None:
    """Build ticket 22 at seam 1. Doing a thing does not rewrite its own causes."""
    acted, learned = tmp_path / "intervention.json", tmp_path / "observation.json"
    subject = ["--component", "streaming-experience"]
    assert _run(model_repo_dir, "intervene", *NETFLIX, *subject, "--out", str(acted)) == 0
    assert _run(model_repo_dir, "observe", *NETFLIX, *subject, "--out", str(learned)) == 0

    doing = json.loads(acted.read_bytes())
    learning = json.loads(learned.read_bytes())
    assert doing["envelope"]["kind"] == "intervention"
    assert learning["envelope"]["kind"] == "observation"

    assert doing["body"]["upstream"] == []
    assert [e["edge"] for e in doing["body"]["severed"]] == ["cdn-capacity-lifts-streaming"]
    assert [e["component"] for e in learning["body"]["upstream"]] == ["content-delivery-network"]
    assert learning["body"]["severed"] == []
    # The half that must be identical, asserted as bytes rather than as a count: the two
    # operations differ above the causal composition and nowhere inside it.
    assert doing["body"]["downstream"] == learning["body"]["downstream"]


def test_rewind_emits_the_model_state_at_a_declared_time(model_repo_dir: Path, tmp_path: Path) -> None:
    """Build ticket 35 at seam 1. A model state, and the commit it resolved to."""
    out = tmp_path / "rewound.json"
    assert main(["rewind", *NETFLIX, "--repo", str(model_repo_dir),
                 "--at", "2026-06-01T00:00:00+00:00", "--out", str(out)]) == 0

    doc = json.loads(out.read_bytes())
    assert doc["envelope"]["kind"] == "rewound-model"
    body = doc["body"]
    assert body["rewound_to"] == "2026-06-01T00:00:00+00:00"
    assert body["resolved"]["commit"] == doc["envelope"]["pins"]["model_repo"]["commit"]
    assert body["rollups"]["components"] == len(body["graph"]["components"])
    assert "abduction" in body["abduction"]


def test_rewinding_before_the_model_existed_is_a_sentence(model_repo_dir: Path, tmp_path: Path) -> None:
    assert main(["rewind", *NETFLIX, "--repo", str(model_repo_dir),
                 "--at", "1999-01-01", "--out", str(tmp_path / "rewound.json")]) == 2


def test_options_removes_before_it_prices(model_repo_dir: Path, tmp_path: Path) -> None:
    out = tmp_path / "options.json"
    assert _run(model_repo_dir, "options", *NETFLIX, "--perspective", "the-operator",
                "--out", str(out)) == 0

    doc = json.loads(out.read_bytes())
    assert doc["envelope"]["kind"] == "priced-option-set"
    body = doc["body"]
    assert {e["option"] for e in body["priced"]} == {"expand-the-delivery-network"}
    assert {r["option"] for r in body["prefilter"]["removed"]} == {
        "instrument-viewers-without-telling-them", "stake-the-quarter-on-one-title"
    }
    assert body["prefilter"]["ran_before_pricing"] is True


def test_a_perspective_the_overlay_does_not_hold_is_a_sentence(model_repo_dir: Path, tmp_path: Path) -> None:
    assert _run(model_repo_dir, "options", *NETFLIX, "--perspective", "nobody",
                "--out", str(tmp_path / "options.json")) == 2


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


# -- sweep and the reliability diagram (build ticket 09) --------------------------------------


def test_sweep_runs_every_scenario_with_no_scenario_flag_to_set(model_repo_dir: Path, tmp_path: Path) -> None:
    """There is no `--scenario` on this verb — that absence is the point."""
    out = tmp_path / "sweep.json"
    assert main(["sweep", "--repo", str(model_repo_dir), "--out", str(out)]) == 0

    body = json.loads(out.read_bytes())["body"]
    assert body["counts"] == {"repos": 1, "executed": 2, "failed": 0, "forecasts": 6}


def test_sweep_spans_multiple_repos_named_by_repeated_flag(tmp_path: Path) -> None:
    pocket_dir = fixtures.build_pocket_org(tmp_path / "pocket")
    default_dir = fixtures.build(tmp_path / "default")
    out = tmp_path / "sweep.json"

    assert main([
        "sweep", "--repo", str(default_dir), "--repo", str(pocket_dir), "--out", str(out),
    ]) == 0

    body = json.loads(out.read_bytes())["body"]
    assert body["counts"]["repos"] == 2
    assert body["counts"]["executed"] == 3


def test_reliability_pools_scores_across_named_score_cards(model_repo_dir: Path, tmp_path: Path) -> None:
    bundle, card = tmp_path / "bundle.json", tmp_path / "card.json"
    _forecast(model_repo_dir, bundle)
    assert _score(model_repo_dir, bundle, card) == 0

    out = tmp_path / "reliability.json"
    assert main(["reliability", "--score-card", str(card), "--out", str(out)]) == 0

    body = json.loads(out.read_bytes())["body"]
    assert body["bin_count"] == 10
    assert body["total_scored"] == 3  # the three world models scored above
    assert sum(b["count"] for b in body["bins"]) == 3


def test_reliability_pools_scores_across_two_separately_named_score_cards(
    model_repo_dir: Path, tmp_path: Path
) -> None:
    """The population claim, proven at the seam a caller actually uses — not just the pure function.

    Two independently emitted score cards, named by two repeated `--score-card` flags: the pool
    has to be the union, not whichever file happened to load last.
    """
    bundle = tmp_path / "bundle.json"
    _forecast(model_repo_dir, bundle)
    card_a, card_b = tmp_path / "card-a.json", tmp_path / "card-b.json"
    assert _score(model_repo_dir, bundle, card_a) == 0
    assert _score(model_repo_dir, bundle, card_b) == 0

    out = tmp_path / "reliability.json"
    assert main([
        "reliability", "--score-card", str(card_a), "--score-card", str(card_b), "--out", str(out),
    ]) == 0

    doc = json.loads(out.read_bytes())
    assert doc["body"]["total_scored"] == 6  # 3 world models, from each of two named cards
    assert sum(b["count"] for b in doc["body"]["bins"]) == 6
    assert len(doc["envelope"]["pins"]["score_cards"]) == 2


def test_reliability_refuses_a_forecast_bundle_named_where_a_score_card_belongs(
    model_repo_dir: Path, tmp_path: Path
) -> None:
    bundle = tmp_path / "bundle.json"
    _forecast(model_repo_dir, bundle)
    out = tmp_path / "reliability.json"
    assert main(["reliability", "--score-card", str(bundle), "--out", str(out)]) == 2


def test_reliability_names_its_score_cards_by_digest_not_by_path(
    model_repo_dir: Path, tmp_path: Path
) -> None:
    from twin.canon import sha256_hex

    bundle, card = tmp_path / "bundle.json", tmp_path / "card.json"
    _forecast(model_repo_dir, bundle)
    _score(model_repo_dir, bundle, card)
    out = tmp_path / "reliability.json"
    main(["reliability", "--score-card", str(card), "--out", str(out)])

    raw = out.read_text(encoding="utf-8")
    assert str(card) not in raw and str(tmp_path) not in raw
    doc = json.loads(raw)
    assert doc["envelope"]["pins"]["score_cards"][0]["sha256"] == sha256_hex(card.read_bytes())


# -- the loss-exceedance curve (build ticket 24) -----------------------------------------------

SEVERITY_ARGS = [
    "--mu", "10.0", "--sigma", "1.5", "--threshold", "100000", "--xi", "0.3", "--beta", "80000",
]


def test_severity_reports_var_beside_tvar_at_every_named_confidence_level(tmp_path: Path) -> None:
    out = tmp_path / "curve.json"
    assert main([
        "severity", *SEVERITY_ARGS, "--alpha", "0.9", "--alpha", "0.95", "--alpha", "0.99", "--out", str(out),
    ]) == 0

    body = json.loads(out.read_bytes())["body"]
    curve = body["curve"]
    assert [row["alpha"] for row in curve] == [0.9, 0.95, 0.99]
    for row in curve:
        assert row["tvar"] is not None and row["tvar"] >= row["var"]


def test_severity_names_a_refusal_per_row_rather_than_failing_the_whole_curve(tmp_path: Path) -> None:
    """A confidence level whose VaR falls below the declared tail still emits — as a row that
    names why it carries no TVaR, not as a command failure (mirrors the register-entry pattern
    `twin price` uses: a refusal is a row with a reason, never a silent gap)."""
    out = tmp_path / "curve.json"
    assert main([
        "severity", *SEVERITY_ARGS, "--alpha", "0.5", "--out", str(out),
    ]) == 0

    row = json.loads(out.read_bytes())["body"]["curve"][0]
    assert row["var"] is not None
    assert row["tvar"] is None
    assert "lognormal body" in row["tvar_refused"]


def test_severity_refuses_a_shape_at_the_boundary_where_the_mean_does_not_exist(tmp_path: Path) -> None:
    out = tmp_path / "curve.json"
    assert main([
        "severity", "--mu", "10.0", "--sigma", "1.5", "--threshold", "100000", "--xi", "1.0",
        "--beta", "80000", "--alpha", "0.99", "--out", str(out),
    ]) == 0
    row = json.loads(out.read_bytes())["body"]["curve"][0]
    assert row["tvar"] is None
    assert "does not exist" in row["tvar_refused"]


def test_severity_refuses_a_non_positive_sigma_with_exit_code_two(tmp_path: Path) -> None:
    out = tmp_path / "curve.json"
    assert main([
        "severity", "--mu", "10.0", "--sigma", "0", "--threshold", "100000", "--xi", "0.3",
        "--beta", "80000", "--alpha", "0.99", "--out", str(out),
    ]) == 2
    assert not out.exists()


def test_severity_pins_its_declared_parameters_and_carries_no_severity_slot_on_a_component(
    tmp_path: Path,
) -> None:
    """Standalone, the same shape `reliability` already is: no `--repo`, no `--org`."""
    out = tmp_path / "curve.json"
    main(["severity", *SEVERITY_ARGS, "--alpha", "0.9", "--out", str(out)])
    pins = json.loads(out.read_bytes())["envelope"]["pins"]
    assert pins["severity"]["threshold"] == 100000.0
    assert pins["severity"]["tail_probability"] not in (None, 0.0, 1.0)


# -- positions (build ticket 16) ------------------------------------------------------------


def test_positions_emits_deltas_and_scores_for_a_scenarios_ensemble(model_repo_dir: Path, tmp_path: Path) -> None:
    out = tmp_path / "positions.json"
    assert _run(
        model_repo_dir, "positions", *NETFLIX, "--scenario", "dvd-decline-2011", "--out", str(out)
    ) == 0

    body = json.loads(out.read_bytes())["body"]
    assert body["scenario"]["id"] == "dvd-decline-2011"
    assert {p["id"] for p in body["positions"]} == {
        "twin-default", "rival-fast-commoditisation", "netflix-believed",
    }
    assert len(body["pairwise"]) == 3
    assert body["revealed"]["resolved"] is True
    assert {row["id"] for row in body["against_revealed"]} == {p["id"] for p in body["positions"]}
    assert "actual" not in body, "no field anywhere holds a privileged position"


def test_positions_refuses_an_unknown_scenario(model_repo_dir: Path, tmp_path: Path) -> None:
    out = tmp_path / "positions.json"
    assert _run(
        model_repo_dir, "positions", *NETFLIX, "--scenario", "no-such-scenario", "--out", str(out)
    ) == 2
    assert not out.exists()


# -- credibility (build ticket 31) -----------------------------------------------------------


@pytest.fixture(scope="module")
def pocket_repo_dir(tmp_path_factory: pytest.TempPathFactory) -> Path:
    return fixtures.build_pocket_org(tmp_path_factory.mktemp("pocket") / "repo")


def test_credibility_blends_own_data_with_the_world_prior(pocket_repo_dir: Path, tmp_path: Path) -> None:
    out = tmp_path / "credibility.json"
    assert _run(
        pocket_repo_dir, "credibility", "--org", "pocket",
        "--subject", "identity-store-incident-cost", "--out", str(out),
    ) == 0

    body = json.loads(out.read_bytes())["body"]
    assert body["own_data"]["n"] == 3
    assert 0.0 < body["credibility"]["z"] < 1.0
    assert body["blended"] != body["world_prior"], "own-data present, so the blend moved off the prior"


def test_credibility_with_no_own_data_returns_the_world_prior_exactly(
    pocket_repo_dir: Path, tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    out = tmp_path / "credibility.json"
    assert _run(
        pocket_repo_dir, "credibility", "--org", "pocket",
        "--subject", "payment-fraud-loss", "--out", str(out),
    ) == 0

    body = json.loads(out.read_bytes())["body"]
    assert body["own_data"] == {
        "n": 0, "mean": None, "variance": None,
        "note": "no own-data observations; pricing from the world-layer prior alone",
    }
    world = body["world_prior"]
    assert body["blended"] == {"min": world["min"], "mode": world["mode"], "max": world["max"]}

    printed = capsys.readouterr().out
    assert "world-layer prior alone" in printed, (
        "the CLI summary must show the honest-default note, not a bare None"
    )


def test_credibility_refuses_an_unknown_subject(pocket_repo_dir: Path, tmp_path: Path) -> None:
    out = tmp_path / "credibility.json"
    assert _run(
        pocket_repo_dir, "credibility", "--org", "pocket",
        "--subject", "no-such-subject", "--out", str(out),
    ) == 2
    assert not out.exists()
