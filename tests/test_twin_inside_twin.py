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
    # The twin's engine and its adoption (build ticket 63), plus its own attack surface
    # (build ticket 83, AC 2) — three ordinary components, none marked specially.
    assert set(twin_self_overlay.components) == {
        "the-twin-model", "the-twin-adoption", "the-twin-analytical-surface",
    }
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
    # The two adoption responses were costed, among the whole overlay's priced choice set (AC 2,
    # build ticket 83, adds two more responses of its own — see the threat-model tests below).
    priced_ids = {o["option"] for o in entry["responses"]["priced"]}
    assert priced_ids >= {
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
    # Four responses now: the two adoption ones (build ticket 63) and the two threat-model
    # controls this ticket adds (AC 2) — none crosses a declared constraint, so all four price.
    assert len(body["priced"]) == 4


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


# -- AC 2 (build ticket 83): a threat model for the twin, controls priced in the same £ ---------
#
# Decision ticket 10, "as a target": exfiltration, model extraction and sensor poisoning. One
# new component (`the-twin-analytical-surface`) carries all three attack modes; the impact edge
# is honestly graded 3 (literature/domain theory — Tramer et al. 2016, Biggio & Roli 2018), so
# the shock itself stays an unpriced register entry, while the two controls still price in the
# ordinary £ currency, because `twin/options.py` costs a response independent of whether the
# shock it addresses ever prices.


def test_the_threat_surface_is_an_ordinary_component_reachable_by_the_ordinary_verbs(
    tmp_path: Path, twin_self_repo_dir: Path,
) -> None:
    out = tmp_path / "propagate.json"
    assert main([
        "propagate", "--repo", str(twin_self_repo_dir), "--org", ORG,
        "--origin", "the-twin-analytical-surface", "--out", str(out),
    ]) == 0
    body = json.loads(out.read_bytes())["body"]
    # Reaches the-twin-adoption directly, and the-twin-model at depth 2 through the pre-existing
    # adoption-sustains-the-model edge — the same self-referential cycle build ticket 63 closed,
    # walked from a third origin outside it rather than re-entered.
    assert {r["component"] for r in body["reached"]} == {"the-twin-adoption", "the-twin-model"}


def test_the_threat_scenario_runs_and_emits_forecasts(tmp_path: Path, twin_self_repo_dir: Path) -> None:
    out = tmp_path / "bundle.json"
    assert main([
        "run", "--repo", str(twin_self_repo_dir), "--org", ORG,
        "--scenario", "threat-to-the-twin-2026", "--regime", "as-consumed", "--out", str(out),
    ]) == 0
    body = json.loads(out.read_bytes())["body"]
    assert body["forecasts"]


def test_the_threat_controls_are_priced_in_the_ordinary_currency_even_though_the_impact_is_not(
    tmp_path: Path, twin_self_repo_dir: Path,
) -> None:
    out = tmp_path / "price.json"
    assert main([
        "price", "--repo", str(twin_self_repo_dir), "--org", ORG,
        "--origin", "the-twin-analytical-surface", "--out", str(out),
    ]) == 0
    body = json.loads(out.read_bytes())["body"]
    entry = next(p for p in body["perspectives"] if p["perspective"] == "the-twin-sponsor")
    # Honest: the impact itself is graded 3 (literature, not repeated-instance evidence), so it
    # is a register entry, never a zero.
    assert not entry["impacts"]
    register_components = {r["component"] for r in entry["register"]}
    assert "the-twin-adoption" in register_components
    for r in entry["register"]:
        assert r["reason"] == "the-causal-path-is-graded-outside-the-pricing-threshold"
    # The two threat-model controls still price, in the same £ PERT machinery every other
    # response in this system costs through.
    priced = {o["option"]: o for o in entry["responses"]["priced"]}
    for option_id in (
        "restrict-and-log-query-access-to-the-priced-output",
        "attest-provenance-on-every-signal-before-admission",
    ):
        assert priced[option_id]["cost"]["mean"] > 0


def test_the_threat_edges_note_cites_real_published_sources(twin_self_overlay: Overlay) -> None:
    edge = twin_self_overlay.edges["compromise-of-the-analytical-surface-damages-adoption"]
    assert edge["evidence_grade"] == 3  # literature/domain theory — evidence-ladder.yaml
    note = edge["note"]
    assert "Tramer" in note and "USENIX" in note
    assert "Biggio" in note and "Pattern Recognition" in note


# -- AC 4 (build ticket 83): a stated Goodhart/reflexivity position, sensors named gameable ------
#
# Decision ticket 10 Q4 already stated the position in prose (accepted as noise, for now); what
# was missing was a concrete answer to "which sensors are most gameable" against a real, named
# table. This backs it: build ticket 82's `twin/sensors.yaml`, classified by
# `twin/ethics_gate.py`'s own existing machinery, reused rather than re-implemented.


def test_the_named_sensor_table_is_classified_and_most_of_it_is_marked_gameable() -> None:
    from twin.ethics_gate import GOODHART_PROOF, MARKED, classify_named_sensors, sensor_ids

    classified = classify_named_sensors()
    assert {c["sensor"] for c in classified} == set(sensor_ids())
    goodhart_proof = {c["sensor"] for c in classified if c["gameability"] == GOODHART_PROOF}
    marked = {c["sensor"] for c in classified if c["gameability"] == MARKED}
    # The stated position, made concrete: only the structural, aggregate bus-factor sensor is
    # goodhart-proof by construction; every behavioural or individual-level sensor in the table
    # is marked — the safe default — and is therefore the most gameable of the set.
    assert goodhart_proof == {"bus-factor-structural-aggregate"}
    assert marked == set(sensor_ids()) - goodhart_proof
    assert len(marked) == 5


# -- AC 5 (build ticket 83): named misuse of the twin ITSELF, each with its blocking constraint --
#
# Scoped narrower than build ticket 62's governance catalogue (misuse of the twin's machinery
# against some other subject) and distinct from build ticket 82's behavioural catalogue (misuse
# of sensing against the people an org's twin models): this is misuse of the twin by its own
# operator — selectively citing its forecasts, gaming a sensor about its own operation, treating
# its own priced figure as a mandate — decision ticket 10's own worked examples.


def test_misuse_of_the_twin_itself_is_named_with_a_mechanism_each() -> None:
    from twin.misuse import CATALOGUE_PATH, load_catalogue

    doc = load_catalogue(CATALOGUE_PATH)
    ids = {e["id"] for e in doc["entries"]}
    self_misuse_ids = {
        "selectively-cites-the-twins-own-forecast-to-win-an-argument-about-it",
        "games-a-sensor-about-the-twins-own-operation-to-look-healthier-than-it-is",
        "treats-the-twins-own-priced-figure-as-a-binding-instruction",
    }
    assert self_misuse_ids <= ids
    for entry in doc["entries"]:
        if entry["id"] in self_misuse_ids:
            assert entry["risk"].strip()
            assert entry["mechanism"].strip()
            assert entry["source"].strip()
