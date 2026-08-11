"""Causally-gated admission to the £ (build ticket 29).

The pricing boundary is **derived, not declared**. A perspective says where its money is; nobody
says what is priceable. The paired test is the one that matters: the same reputational impact
prices when a real churn path reaches a cash flow, and comes back as an unpriced blast radius when
it does not.
"""

from __future__ import annotations

import json

import pytest

from twin import admission, evidence, verbs
from twin.admission import GRADED_PATH, IS_CASH_FLOW, NO_CASH_FLOW_DECLARED, NO_GRADED_PATH, admit
from twin.grades import Capabilities
from twin.model import ModelError, Overlay
from twin.repo import ModelRepo
from twin.schema import SchemaError, validate

from test_seam2_propagation import causal, graph_of

ORG = "netflix"
POCKET = "pocket"
OPERATOR = "the-operator"

# The reputational impact and the cash flow a churn path would have to reach.
REPUTATION, SUBSCRIPTIONS = "brand-standing", "subscriptions"
WIDE = {"min": 0.2, "mode": 0.5, "max": 0.8}


def _perspective(cash_flow: list[str]) -> dict:
    return {
        "id": OPERATOR,
        "name": "The operator",
        "party": "employer",
        "pays": "The organisation running the twin.",
        "cash_flow": cash_flow,
        "values": {},
        "ruin": {"insolvency": "A real chance of not meeting obligations."},
    }


# -- the paired property -------------------------------------------------------------------


def test_a_reputation_impact_with_a_churn_path_prices() -> None:
    graph = graph_of((causal("churn", REPUTATION, SUBSCRIPTIONS, WIDE, grade=2),))
    verdict = admit(graph, _perspective([SUBSCRIPTIONS]), REPUTATION)

    assert verdict["admitted"] is True
    assert verdict["basis"] == GRADED_PATH
    assert verdict["reaches"] == SUBSCRIPTIONS
    assert verdict["worst_evidence_grade"] <= evidence.admission_threshold()


def test_the_same_impact_without_a_path_returns_a_blast_radius() -> None:
    graph = graph_of((causal("unrelated", "somewhere", "elsewhere", WIDE),), extra=(REPUTATION, SUBSCRIPTIONS))
    verdict = admit(graph, _perspective([SUBSCRIPTIONS]), REPUTATION)

    assert verdict["admitted"] is False
    assert verdict["reason"] == NO_GRADED_PATH
    assert "blast_radius" in verdict, "a refusal is an answer, not a gap"
    assert verdict["blast_radius"]["origin"] == REPUTATION
    assert "somebody can falsify by evidencing a path" in verdict["detail"]


def test_the_same_path_too_weakly_evidenced_does_not_price() -> None:
    """A path that exists is not a path that counts. Grade 5 is where contamination hides."""
    graph = graph_of((causal("churn", REPUTATION, SUBSCRIPTIONS, WIDE, grade=5),))
    verdict = admit(graph, _perspective([SUBSCRIPTIONS]), REPUTATION)

    assert verdict["admitted"] is False
    assert verdict["reason"] == NO_GRADED_PATH


def test_a_component_that_is_itself_a_cash_flow_needs_no_path() -> None:
    graph = graph_of((causal("churn", REPUTATION, SUBSCRIPTIONS, WIDE),))
    verdict = admit(graph, _perspective([SUBSCRIPTIONS]), SUBSCRIPTIONS)

    assert verdict["admitted"] is True
    assert verdict["basis"] == IS_CASH_FLOW
    assert verdict["path"] == []


def test_a_perspective_declaring_no_cash_flow_prices_nothing() -> None:
    graph = graph_of((causal("churn", REPUTATION, SUBSCRIPTIONS, WIDE),))
    verdict = admit(graph, _perspective([]), REPUTATION)

    assert verdict["admitted"] is False
    assert verdict["reason"] == NO_CASH_FLOW_DECLARED


def test_the_boundary_is_derived_and_cannot_be_declared() -> None:
    """No author can mark an impact priceable: there is no field for it, and no argument either."""
    with pytest.raises(SchemaError, match="closed"):
        validate(
            "perspective",
            {**_perspective([SUBSCRIPTIONS]), "priceable": [REPUTATION]},
            "planted",
        )
    assert "priceable" not in admission.admit.__code__.co_varnames


def test_a_direction_of_travel_matters() -> None:
    """A path *from* the cash flow *to* the impact does not admit it. Causation has a direction."""
    graph = graph_of((causal("backwards", SUBSCRIPTIONS, REPUTATION, WIDE, grade=1),))
    assert admit(graph, _perspective([SUBSCRIPTIONS]), REPUTATION)["admitted"] is False


# -- the published threshold ----------------------------------------------------------------


def test_the_admission_threshold_is_published_beside_the_use_gate() -> None:
    published = evidence.published()
    assert published["pin"]["path_admission_threshold"] == evidence.admission_threshold()
    assert published["pin"]["pricing_threshold"] == evidence.threshold()
    assert "derived from the graph" in published["admission_rule"]


def test_the_two_thresholds_are_read_from_two_different_keys(tmp_path) -> None:
    """They hold the same value today, which is exactly why this needs asserting.

    A reader that fetched `pricing_threshold` under the admission name would pass every other
    test in this file and silently collapse the two gates into one. The only way to see that is
    to move them apart.
    """
    apart = tmp_path / "evidence-ladder.yaml"
    apart.write_text(
        evidence.LADDER_PATH.read_text(encoding="utf-8").replace(
            "path_admission_threshold: 2", "path_admission_threshold: 1"
        ),
        encoding="utf-8",
    )
    assert evidence.threshold(apart) == 2
    assert evidence.admission_threshold(apart) == 1
    assert evidence.pin(apart)["pricing_threshold"] == 2
    assert evidence.pin(apart)["path_admission_threshold"] == 1


def test_a_ladder_with_no_admission_threshold_is_refused(tmp_path) -> None:
    stripped = tmp_path / "evidence-ladder.yaml"
    stripped.write_text(
        "\n".join(
            line
            for line in evidence.LADDER_PATH.read_text(encoding="utf-8").splitlines()
            if not line.startswith("path_admission_threshold:")
        ),
        encoding="utf-8",
    )
    with pytest.raises(evidence.EvidenceError, match="path_admission_threshold"):
        evidence.ladder(stripped)


# -- through the emitted artefact ------------------------------------------------------------


def test_the_pocket_org_admits_one_impact_and_refuses_another(
    tmp_path, caps: Capabilities
) -> None:
    """A grade-2 valuation the use-gate admits and the £ boundary refuses. Two questions."""
    from twin import fixtures

    repo = ModelRepo.open(fixtures.build_pocket_org(tmp_path / "pocket"))
    artefact = verbs.exposure(
        repo, caps, POCKET, "portal-availability-2026", [OPERATOR],
        verbs.command_for("exposure", org=POCKET, scenario="portal-availability-2026"),
    )
    entry = json.loads(artefact.to_bytes())["body"]["perspectives"][0]
    verdicts = {v["component"]: v for v in entry["admission"]}

    assert verdicts["customer-portal"]["basis"] == IS_CASH_FLOW
    assert verdicts["order-service"]["basis"] == GRADED_PATH
    assert verdicts["identity-store"]["admitted"] is False

    priced = {row["component"] for row in entry["admitted"]}
    held = {row["component"]: row for row in entry["register"]}
    assert priced == {"customer-portal", "order-service"}
    assert held["identity-store"]["evidence_grade"] == 2, "the use-gate admitted it"
    assert "no causal path at an adequate grade" in held["identity-store"]["reason"]
    assert "amount" not in held["identity-store"] and "declared_value" not in held["identity-store"]


def test_a_refused_impact_never_reaches_the_figure(tmp_path, caps: Capabilities) -> None:
    from twin import fixtures

    repo = ModelRepo.open(fixtures.build_pocket_org(tmp_path / "pocket"))
    body = json.loads(
        verbs.exposure(
            repo, caps, POCKET, "portal-availability-2026", [OPERATOR],
            verbs.command_for("exposure", org=POCKET, scenario="portal-availability-2026"),
        ).to_bytes()
    )["body"]

    assert body["declared_exposure"][OPERATOR] == 650000, "the refused 90000 stayed out"
    attributed = {row["component"]: row["declared_value"][OPERATOR] for row in body["attribution"]}
    assert attributed["identity-store"] is None, "zero would say 'worth nothing', which is a lie"


def test_a_perspective_naming_a_cash_flow_that_does_not_exist_is_refused(scratch_repo) -> None:
    from twin import fixtures

    path = scratch_repo / "orgs" / "netflix" / "perspectives" / "the-operator.yaml"
    path.write_text(
        path.read_text(encoding="utf-8").replace("  - dvd-by-mail", "  - a-component-that-does-not-exist"),
        encoding="utf-8",
    )
    fixtures.git(scratch_repo, "add", "-A")
    fixtures.git(scratch_repo, "commit", "-q", "-m", "name a cash flow that does not exist")

    with pytest.raises(ModelError, match="names 'a-component-that-does-not-exist' as a cash flow"):
        Overlay.load(ModelRepo.open(scratch_repo), ORG)


def test_a_perspective_with_no_cash_flow_field_will_not_load() -> None:
    """Required for the reason `ruin` is: it would otherwise inherit somebody else's ledger."""
    without = {k: v for k, v in _perspective([SUBSCRIPTIONS]).items() if k != "cash_flow"}
    with pytest.raises(SchemaError, match="cash_flow"):
        validate("perspective", without, "planted")


def test_an_unknown_component_is_a_refusal_not_a_silent_no() -> None:
    graph = graph_of((causal("churn", REPUTATION, SUBSCRIPTIONS, WIDE),))
    with pytest.raises(ModelError, match="no component 'nowhere'"):
        admit(graph, _perspective([SUBSCRIPTIONS]), "nowhere")
