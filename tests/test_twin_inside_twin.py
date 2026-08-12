"""The twin inside the twin (build ticket 63, decision ticket 10): the twin present as an
ordinary component set in its own graph, depth-1 bounded, and adoption modelled as a priced
scenario rather than a note — corporate prediction markets at Google and Ford beat their own
experts by up to a 25% MSE reduction and were killed anyway, by manager incentives and information
control, not by being wrong.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from twin import fixtures
from twin.cli import main
from twin.model import Overlay
from twin.repo import ModelRepo
from twin.schema import SchemaError, validate

ORG = fixtures.TWIN_SELF_ORG


@pytest.fixture(scope="session")
def twin_self_repo_dir(tmp_path_factory: pytest.TempPathFactory) -> Path:
    return fixtures.build_twin_self_org(tmp_path_factory.mktemp("twin-self") / "repo")


@pytest.fixture()
def twin_self_overlay(twin_self_repo_dir: Path) -> Overlay:
    return Overlay.load(ModelRepo.open(twin_self_repo_dir), ORG)


def test_the_fixture_validates_against_its_closed_schema(twin_self_repo_dir: Path) -> None:
    assert main(["validate", "--repo", str(twin_self_repo_dir)]) == 0


# -- AC: the twin appears as components in its own graph, analysable by the normal machinery ---


def test_the_twin_appears_as_ordinary_components_in_its_own_graph(twin_self_overlay: Overlay) -> None:
    assert set(twin_self_overlay.components) == {"the-twin-model", "the-twin-adoption"}
    for component in twin_self_overlay.components.values():
        # An ordinary component: kind is one of the same four kinds any other subject uses, and
        # nothing here marks it specially.
        assert component["kind"] in ("capability", "activity", "practice", "data")


def test_the_twin_starts_life_at_bus_factor_one(tmp_path: Path, twin_self_repo_dir: Path) -> None:
    """"The twin becomes the org's biggest new bus-factor-1 risk" (decision ticket 10, Q1) —
    computed by the same bus_factor() mechanism any other component's holder count uses, read back
    from the emitted graph artefact rather than asserted against internals."""
    out = tmp_path / "graph.json"
    assert main(["graph", "--repo", str(twin_self_repo_dir), "--org", ORG, "--out", str(out)]) == 0
    body = json.loads(out.read_bytes())["body"]
    assert body["bus_factor"]["the-twin-model"] == ["the-twin-maintainer"]


def test_the_twin_is_reachable_by_the_ordinary_verbs(tmp_path: Path, twin_self_repo_dir: Path) -> None:
    """"Subject to its own analysis" — graph, blast and propagate all run on it unmodified, the
    same commands any other org's components take."""
    for verb, out_name in (("graph", "graph.json"), ("blast", "blast.json"), ("propagate", "propagate.json")):
        out = tmp_path / out_name
        args = ["--repo", str(twin_self_repo_dir), "--org", ORG, "--out", str(out)]
        if verb in ("blast", "propagate"):
            args = [verb, "--origin", "the-twin-model", *args]
        else:
            args = [verb, *args]
        assert main(args) == 0, f"{verb} failed against the twin's own graph"
        assert out.exists()


# -- AC: depth is bounded at 1, structurally — a depth-2 attempt fails rather than recursing ---


def test_no_schema_slot_exists_for_a_further_nested_layer() -> None:
    """The structural half of the bound: a component has no field by which a further "twin
    modelling this twin" layer could be attached at all. The schema is closed, so a planted field
    for one is refused at load rather than merely unused."""
    base = {"id": "the-twin-model", "name": "The twin's own engine", "kind": "capability"}
    with pytest.raises(SchemaError):
        validate("component", {**base, "models_graph": {"components": []}}, "planted")
    with pytest.raises(SchemaError):
        validate("component", {**base, "nested_twin": "the-twin-model"}, "planted")


def test_a_depth_two_traversal_is_cut_not_recursed(tmp_path: Path, twin_self_repo_dir: Path) -> None:
    """The traversal half of the bound (decision ticket 10, Q1: "graph traversal detects and cuts
    self-referential cycles"). `the-twin-model` and `the-twin-adoption` close a genuine two-node
    causal cycle; propagating from either reaches the other once and the return leg — the depth-2
    attempt — is cut rather than walked again, by the identical simple-path rule build ticket 21
    gave every cycle in the causal layer. Reported, not silent: `truncated` is true and the limit
    names the cycle."""
    out = tmp_path / "propagate.json"
    assert main([
        "propagate", "--repo", str(twin_self_repo_dir), "--org", ORG,
        "--origin", "the-twin-model", "--out", str(out),
    ]) == 0
    body = json.loads(out.read_bytes())["body"]
    assert [r["component"] for r in body["reached"]] == ["the-twin-adoption"]
    assert body["traversal"]["truncated"] is True
    assert any("cyclic" in limit for limit in body["traversal"]["known_limits"]), body["traversal"]["known_limits"]


def test_the_cycle_survives_from_the_other_origin_too(tmp_path: Path, twin_self_repo_dir: Path) -> None:
    out = tmp_path / "propagate.json"
    assert main([
        "propagate", "--repo", str(twin_self_repo_dir), "--org", ORG,
        "--origin", "the-twin-adoption", "--out", str(out),
    ]) == 0
    body = json.loads(out.read_bytes())["body"]
    assert [r["component"] for r in body["reached"]] == ["the-twin-model"]
    assert body["traversal"]["truncated"] is True


# -- AC: adoption is a modelled scenario with priced responses, not a note ---------------------


def test_adoption_is_a_scenario_that_runs_and_emits_forecasts(tmp_path: Path, twin_self_repo_dir: Path) -> None:
    out = tmp_path / "bundle.json"
    assert main([
        "run", "--repo", str(twin_self_repo_dir), "--org", ORG,
        "--scenario", "adoption-risk-2026", "--regime", "as-consumed", "--out", str(out),
    ]) == 0
    body = json.loads(out.read_bytes())["body"]
    assert body["forecasts"]
    assert body["regime"]["scoring_eligible"] is True


def test_adoption_has_priced_responses_not_just_a_narrative_note(
    tmp_path: Path, twin_self_repo_dir: Path
) -> None:
    out = tmp_path / "price.json"
    assert main([
        "price", "--repo", str(twin_self_repo_dir), "--org", ORG,
        "--origin", "the-twin-model", "--out", str(out),
    ]) == 0
    body = json.loads(out.read_bytes())["body"]
    entry = next(p for p in body["perspectives"] if p["perspective"] == "the-twin-sponsor")
    # The impact itself prices: a real causal path, a real valuation, admitted to a declared
    # cash flow.
    impact = next(i for i in entry["impacts"] if i["component"] == "the-twin-adoption")
    assert impact["price"]["attenuated"]["mode"] > 0
    # Both candidate responses were costed — this is a priced choice set, not prose.
    priced_ids = {o["option"] for o in entry["responses"]["priced"]}
    assert priced_ids == {
        "fund-it-as-a-standing-product-not-a-side-project",
        "publish-full-method-and-content-transparency",
    }
    for option in entry["responses"]["priced"]:
        assert option["cost"]["mean"] > 0


def test_adoption_responses_also_price_through_the_options_prefilter(
    tmp_path: Path, twin_self_repo_dir: Path
) -> None:
    out = tmp_path / "options.json"
    assert main([
        "options", "--repo", str(twin_self_repo_dir), "--org", ORG,
        "--perspective", "the-twin-sponsor", "--out", str(out),
    ]) == 0
    body = json.loads(out.read_bytes())["body"]
    assert len(body["prefilter"]["removed"]) == 0
    assert len(body["priced"]) == 2


# -- AC: the Google/Ford evidence is cited in the scenario's basis -----------------------------


def test_the_google_ford_evidence_is_cited_in_the_scenarios_basis(twin_self_overlay: Overlay) -> None:
    world_model = twin_self_overlay.world_models["documented-corporate-prediction-market-pattern"]
    scenario = twin_self_overlay.scenarios["adoption-risk-2026"]
    assert world_model["id"] in scenario["world_models"]
    note = world_model["note"]
    assert "Google" in note and "Ford" in note
    assert "25%" in note
    assert "academic.oup.com" in note  # the peer-reviewed citation, not just a claim


def test_the_evidence_is_also_a_real_dated_signal_bound_at_a_pricing_grade(
    twin_self_overlay: Overlay,
) -> None:
    signal = twin_self_overlay.signals["cowgill-zitzewitz-2015-corporate-prediction-markets"]
    assert signal["date"] == "2015-10-01"
    assert signal["provenance"]["url"].startswith("https://")
    assert "example.invalid" not in signal["provenance"]["url"]
    claim = twin_self_overlay.claims["bind-cowgill-zitzewitz-2015-corporate-prediction-markets"]
    assert claim["signal"] == signal["id"]
    assert claim["component"] == "the-twin-adoption"
    assert claim["evidence_grade"] == 2  # may_price — evidence-ladder.yaml


def test_the_world_layer_names_no_tenant(twin_self_repo_dir: Path) -> None:
    from twin.model import check_direction

    assert check_direction(ModelRepo.open(twin_self_repo_dir)) == []
