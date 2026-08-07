"""Response pricing, mitigation credit, and the join of the causal layer to the £.

Build ticket 30. Seam 2 for the arithmetic and the gates, seam 1 for the emitted artefact. The
hand-computable numbers live in the pocket-org worksheet and are asserted there; what is asserted
here is the behaviour a number alone cannot show — that a refusal carries no figure, that an
unevidenced claim earns nothing rather than a discount, and that no magnitude reopens the gate.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from twin import fixtures, pricing, verbs
from twin.artefact import ArtefactError
from twin.canon import walk_values
from twin.grades import Capabilities
from twin.model import Overlay
from twin.repo import ModelRepo
from twin.schema import SchemaError, validate

OPERATOR, COUNCIL = "the-operator", "the-staff-council"
PRICED_ORIGIN, REFUSED_ORIGIN = "order-service", "shared-database"
RESPONSE = {"id": "r", "name": "R", "addresses": "shared-database",
            "cost": {"min": 1.0, "mode": 2.0, "max": 3.0}}


@pytest.fixture(scope="session")
def pocket_repo_dir(tmp_path_factory: pytest.TempPathFactory) -> Path:
    return fixtures.build_pocket_org(tmp_path_factory.mktemp("pocket") / "repo")


def _priced(repo_dir: Path, caps: Capabilities, origin: str) -> dict:
    return json.loads(
        verbs.price(
            ModelRepo.open(repo_dir), caps, "pocket", origin, None,
            verbs.command_for("price", org="pocket", origin=origin),
        ).to_bytes()
    )["body"]


def _eye(body: dict, perspective: str) -> dict:
    return next(e for e in body["perspectives"] if e["perspective"] == perspective)


def _option(entry: dict, option: str) -> dict:
    return next(o for o in entry["responses"]["priced"] if o["option"] == option)


# -- the join, and the three gates -----------------------------------------------------------


def test_a_price_is_the_declared_valuation_scaled_by_the_influence(pocket_repo_dir: Path, caps) -> None:
    """One authored magnitude per component per eye. There is no severity anywhere."""
    impact = _eye(_priced(pocket_repo_dir, caps, PRICED_ORIGIN), OPERATOR)["impacts"][0]
    assert impact["component"] == "customer-portal"
    assert impact["valuation"]["amount"] == 400000.0
    assert impact["influence"]["attenuated"]["mode"] == 0.4
    assert impact["price"]["attenuated"]["mode"] == 160000.0


def test_the_same_shock_prices_differently_under_each_eye(pocket_repo_dir: Path, caps) -> None:
    """The £ is perspectival right down into the price, and the spread is the headline."""
    body = _priced(pocket_repo_dir, caps, PRICED_ORIGIN)
    row = next(r for r in body["attribution"] if r["component"] == "customer-portal")
    assert row["priced"] == {OPERATOR: 160000.0, COUNCIL: 20000.0}
    assert row["spread"] == 140000.0


def test_a_weakly_graded_path_prices_nothing_and_says_why(pocket_repo_dir: Path, caps) -> None:
    """Every route out of shared-database crosses the grade-3 edge."""
    entry = _eye(_priced(pocket_repo_dir, caps, REFUSED_ORIGIN), OPERATOR)
    assert entry["impacts"] == []
    reasons = {r["component"]: r["reason"] for r in entry["register"]}
    assert reasons["customer-portal"] == pricing.PATH_TOO_WEAK


def test_a_refused_impact_carries_no_figure_not_even_a_zero(pocket_repo_dir: Path, caps) -> None:
    """Zero is a price, and it is the wrong one. 'Cannot price' is not 'worth nothing'."""
    entry = _eye(_priced(pocket_repo_dir, caps, REFUSED_ORIGIN), OPERATOR)
    allowed = {"depth", "worst_evidence_grade", "evidence_grade"}
    figures = [
        (key, value)
        for record in entry["register"]
        for key, value in walk_values(record)
        if isinstance(value, (int, float)) and not isinstance(value, bool) and key not in allowed
    ]
    assert figures == [], f"a refused impact carried {figures}"


def test_an_unattributed_component_is_null_rather_than_zero(pocket_repo_dir: Path, caps) -> None:
    body = _priced(pocket_repo_dir, caps, REFUSED_ORIGIN)
    assert body["attribution"] == []


def test_both_the_composed_and_the_attenuated_price_are_reported(pocket_repo_dir: Path, caps) -> None:
    """An attenuated figure whose un-attenuated form was never shown is unfalsifiable."""
    impact = _eye(_priced(pocket_repo_dir, caps, PRICED_ORIGIN), OPERATOR)["impacts"][0]
    assert set(impact["price"]) == {"composed", "attenuated"}


# -- mitigation credit, gated like the causal claim it is ------------------------------------


def test_an_evidenced_claim_earns_credit_in_the_same_unit_as_the_impact(
    pocket_repo_dir: Path, caps
) -> None:
    entry = _eye(_priced(pocket_repo_dir, caps, PRICED_ORIGIN), OPERATOR)
    rota = _option(entry, "retrain-the-on-call-rota")
    assert rota["cost"]["mean"] == 6000.0
    assert rota["mitigation"]["credit"]["mode"] == 40000.0
    assert rota["mitigation"]["credit"]["mean"] == 40000.0


def test_a_weakly_graded_claim_earns_nothing_rather_than_a_discount(
    pocket_repo_dir: Path, caps
) -> None:
    """The classic unfalsifiability loophole, closed. The larger claim is the weaker one."""
    replica = _option(_eye(_priced(pocket_repo_dir, caps, PRICED_ORIGIN), OPERATOR),
                      "add-a-read-replica")
    assert replica["mitigation"]["evidence_grade"] == 3
    assert replica["mitigation"]["reason"] == pricing.CLAIM_TOO_WEAK
    assert "credit" not in replica["mitigation"]


def test_a_response_claiming_nothing_earns_nothing(pocket_repo_dir: Path, caps) -> None:
    """Silence is not an average reduction. This option survives only the council's pre-filter."""
    bet = _option(_eye(_priced(pocket_repo_dir, caps, PRICED_ORIGIN), COUNCIL),
                  "bet-the-org-on-one-supplier")
    assert bet["mitigation"] == {
        "claims": False,
        "reason": pricing.CLAIMS_NONE,
        "detail": bet["mitigation"]["detail"],
    }


def test_a_claim_against_an_unpriced_impact_earns_nothing(pocket_repo_dir: Path, caps) -> None:
    rota = _option(_eye(_priced(pocket_repo_dir, caps, REFUSED_ORIGIN), OPERATOR),
                   "retrain-the-on-call-rota")
    assert rota["mitigation"]["reason"] == pricing.NOTHING_PRICED_THERE
    assert "credit" not in rota["mitigation"]


def test_a_mitigation_claim_with_no_grade_does_not_load() -> None:
    """Structural, not a review step: there is no slot for an ungraded reduction."""
    for missing in ("evidence_grade", "reduction", "component", "basis"):
        claim = {"component": "c", "reduction": {"min": 0.1, "mode": 0.2, "max": 0.3},
                 "evidence_grade": 2, "basis": "measured"}
        del claim[missing]
        with pytest.raises(SchemaError):
            validate("response", {**RESPONSE, "mitigates": claim}, "planted")


def test_a_reduction_must_be_a_range_not_a_point() -> None:
    """A control that removes 'half' an impact knows that no better than an elasticity does."""
    with pytest.raises(SchemaError):
        validate(
            "response",
            {**RESPONSE, "mitigates": {"component": "c", "reduction": 0.5,
                                       "evidence_grade": 2, "basis": "b"}},
            "planted",
        )


# -- the worked cross-domain comparison ------------------------------------------------------


def test_a_non_technical_lever_prices_below_a_technical_control(pocket_repo_dir: Path, caps) -> None:
    """AC 4, and the reason one unit exists. Neither figure is a ranking."""
    entry = _eye(_priced(pocket_repo_dir, caps, PRICED_ORIGIN), OPERATOR)
    rota = _option(entry, "retrain-the-on-call-rota")
    replica = _option(entry, "add-a-read-replica")
    assert rota["addresses"] != replica["addresses"]
    assert rota["cost"]["mean"] < replica["cost"]["mean"]
    # And nothing in the artefact says which to choose.
    assert "not_a_ranking" in entry["responses"]


# -- the ordering lock still holds -----------------------------------------------------------


def test_an_excluded_option_is_absent_from_the_price_at_any_magnitude(
    pocket_repo_dir: Path, caps
) -> None:
    """The pre-filter runs first here too, and it never reads a cost."""
    entry = _eye(_priced(pocket_repo_dir, caps, PRICED_ORIGIN), OPERATOR)
    priced_ids = {o["option"] for o in entry["responses"]["priced"]}
    removed = {r["option"] for r in entry["responses"]["prefilter"]["removed"]}
    assert removed == {"watch-the-team-quietly", "bet-the-org-on-one-supplier"}
    assert not priced_ids & removed


def test_the_price_body_is_closed(pocket_repo_dir: Path, caps) -> None:
    body = _eye(_priced(pocket_repo_dir, caps, PRICED_ORIGIN), OPERATOR)
    with pytest.raises(ArtefactError, match="undeclared field"):
        pricing.refuse_undeclared_keys({**body, "shadow_price": 1})


def test_a_register_entry_carrying_a_figure_is_refused() -> None:
    with pytest.raises(ArtefactError, match="nowhere to put a figure"):
        pricing.refuse_unpriced_figures(
            {"register": [{"component": "c", "reason": "r", "detail": "d", "price": 1}]}
        )


def test_a_refused_claim_carrying_a_credit_is_refused() -> None:
    with pytest.raises(ArtefactError, match="earns nothing rather than a default"):
        pricing.refuse_unpriced_figures(
            {"responses": {"priced": [
                {"option": "o", "mitigation": {"reason": "too weak", "held": {"credit": 5}}}
            ]}}
        )


# -- seam 1 ----------------------------------------------------------------------------------


def test_the_priced_impact_reproduces_from_its_own_pins(pocket_repo_dir: Path, tmp_path: Path) -> None:
    from twin.cli import main
    from twin.reproduce import reproduce

    out = tmp_path / "priced-impact.json"
    assert main(["price", "--repo", str(pocket_repo_dir), "--org", "pocket",
                 "--origin", PRICED_ORIGIN, "--out", str(out)]) == 0
    assert reproduce(pocket_repo_dir, out).reproduces


def test_naming_no_perspective_prices_every_eye(pocket_repo_dir: Path, caps) -> None:
    """Defaulting to the employer's would be the unstated firm's-£ the design refuses."""
    body = _priced(pocket_repo_dir, caps, PRICED_ORIGIN)
    overlay = Overlay.load(ModelRepo.open(pocket_repo_dir), "pocket")
    assert {e["perspective"] for e in body["perspectives"]} == set(overlay.perspectives)
