"""The perspective object and the published constraint set (build tickets 26 and 27).

The £ belongs to whoever pays to run the twin. A union, a regulator or an employee body
instantiates their own perspective rather than inheriting the employer's, and the same scenario
prices differently under each. A perspective may add constraints to the universal floor and has no
way to remove one.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from twin import constraints, evidence, fixtures, verbs
from twin.constraints import ConstraintError
from twin.grades import Capabilities
from twin.repo import ModelRepo
from twin.schema import PARTIES, SchemaError, validate
from twin.verbs import VerbError

PERSPECTIVE = {
    "id": "a-union",
    "name": "A union's own perspective",
    "party": "union",
    "pays": "The members, from their subscriptions.",
    # Where this perspective's money moves. Required since build ticket 29: the £ boundary is
    # derived from a causal path to a declared cash flow, and a perspective naming none would
    # silently inherit somebody else's ledger.
    "cash_flow": ["dvd-by-mail"],
    "values": {
        "dvd-by-mail": {"amount": 1000.0, "evidence_grade": 2, "basis": "Members in distribution."},
        "brand-goodwill": {"evidence_grade": 5, "basis": "A model assertion about worth."},
    },
    "ruin": {"loss-of-livelihood": "Any option risking a member's ability to meet obligations."},
}


def _exposure(repo: ModelRepo, caps: Capabilities, *perspectives: str) -> dict:
    artefact = verbs.exposure(
        repo, caps, "netflix", "dvd-decline-2011", list(perspectives) or None,
        verbs.command_for("exposure", scenario="dvd-decline-2011"),
    )
    body: dict = json.loads(artefact.to_bytes())["body"]
    return body


# -- the perspective (26) ----------------------------------------------------------------------


def test_a_perspective_declares_who_pays_what_they_value_and_their_red_lines() -> None:
    validate("perspective", PERSPECTIVE, "ok")
    validate("perspective", {**PERSPECTIVE, "forbidden": {"no-compulsory-severance": "..."}}, "ok")


def test_a_perspective_with_no_ruin_boundary_is_refused() -> None:
    """Ruin is perspective-relative, so a perspective declaring none inherits somebody else's."""
    with pytest.raises(SchemaError, match="ruin"):
        validate("perspective", {k: v for k, v in PERSPECTIVE.items() if k != "ruin"}, "planted")


@pytest.mark.parametrize("party", PARTIES)
def test_every_party_is_instantiable_on_the_same_footing(party: str) -> None:
    """No field ranks a perspective, so a non-employer needs no privilege to declare one."""
    validate("perspective", {**PERSPECTIVE, "party": party}, "ok")


def test_a_perspective_may_not_override_the_universal_floor() -> None:
    """The demonstrable failing attempt: reuse a floor id and the repository does not load."""
    floor_id = sorted(constraints.floor_ids())[0]
    with pytest.raises(SchemaError, match="may never override the floor"):
        validate("perspective", {**PERSPECTIVE, "forbidden": {floor_id: "..."}}, "planted")
    with pytest.raises(ConstraintError):
        constraints.refuse_floor_override({**PERSPECTIVE, "ruin": {floor_id: "..."}})


def test_the_floor_reaches_every_resolved_constraint_set() -> None:
    resolved = constraints.resolve(PERSPECTIVE)
    ids = {c["id"] for c in resolved["constraints"]}
    assert constraints.floor_ids() <= ids
    assert resolved["floor_is_negotiable"] is False
    assert {c["tier"] for c in resolved["constraints"]} == {"universal", "perspective"}


def test_two_perspectives_price_one_scenario_differently(repo: ModelRepo, caps: Capabilities) -> None:
    body = _exposure(repo, caps)
    figures = body["declared_exposure"]
    assert figures["the-operator"] != figures["the-staff-council"]
    assert body["exposure_spread"] == abs(figures["the-operator"] - figures["the-staff-council"])


def test_the_difference_is_attributable_component_by_component(repo: ModelRepo, caps: Capabilities) -> None:
    body = _exposure(repo, caps)
    rows = {row["component"]: row for row in body["attribution"]}
    assert set(rows) == set(body["scenario"]["components"])
    priced = [row for row in rows.values() if row["spread"] is not None]
    for row in priced:
        values = row["declared_value"]
        assert set(values) == {"the-operator", "the-staff-council"}
        assert row["spread"] == abs(values["the-operator"] - values["the-staff-council"])
    assert sum(row["spread"] for row in priced) == body["exposure_spread"]


def test_a_valuation_outside_the_threshold_is_a_register_entry_with_no_figure(
    repo: ModelRepo, caps: Capabilities
) -> None:
    """The use-gate reaches the one artefact that emits money. Beside the number, never inside it."""
    body = _exposure(repo, caps)
    for entry in body["perspectives"]:
        held = {e["component"]: e for e in entry["register"]}
        assert "brand-goodwill" in held
        assert "amount" not in held["brand-goodwill"] and "declared_value" not in held["brand-goodwill"]
        assert not evidence.may_price(held["brand-goodwill"]["evidence_grade"])
        assert "brand-goodwill" not in {e["component"] for e in entry["admitted"]}
    row = next(r for r in body["attribution"] if r["component"] == "brand-goodwill")
    assert set(row["declared_value"].values()) == {None} and row["spread"] is None


def test_a_valuation_the_evidence_does_not_support_may_not_carry_a_figure() -> None:
    """The rejected shadow price: reputation damage = a number nobody can defend."""
    with pytest.raises(SchemaError, match="may not carry an amount"):
        validate(
            "perspective",
            {**PERSPECTIVE,
             "values": {"brand-goodwill": {"amount": 1.0, "evidence_grade": 5, "basis": "asserted"}}},
            "planted",
        )


def test_a_valuation_inside_the_threshold_must_carry_a_figure() -> None:
    with pytest.raises(SchemaError, match="admits a figure and none is declared"):
        validate(
            "perspective",
            {**PERSPECTIVE, "values": {"dvd-by-mail": {"evidence_grade": 1, "basis": "measured"}}},
            "planted",
        )


def test_a_valuation_with_no_grade_behind_it_is_refused() -> None:
    with pytest.raises(SchemaError, match="shadow price"):
        validate(
            "perspective",
            {**PERSPECTIVE, "values": {"dvd-by-mail": {"amount": 1.0, "basis": "because"}}},
            "planted",
        )


def test_naming_no_perspective_reports_every_one_of_them(repo: ModelRepo, caps: Capabilities) -> None:
    """Defaulting to the operator's would be the unstated firm's-£ the design refuses."""
    everyone = {e["id"] for e in _exposure(repo, caps)["perspectives"]}
    assert everyone == {"the-operator", "the-staff-council"}
    only_one = _exposure(repo, caps, "the-staff-council")["perspectives"]
    assert [e["id"] for e in only_one] == ["the-staff-council"]
    assert only_one[0]["party"] == "employee-body"


def test_an_overlay_with_no_perspective_refuses_rather_than_assuming_one(
    repo: ModelRepo, caps: Capabilities
) -> None:
    with pytest.raises(VerbError, match="declares no perspective"):
        verbs.exposure(repo, caps, "intel", "euv-slip-2026", None, verbs.command_for("exposure"))


def test_the_exposure_says_what_it_is_not(repo: ModelRepo, caps: Capabilities) -> None:
    """A declared valuation, before propagation and severity are joined to the £."""
    body = _exposure(repo, caps)
    assert body["basis"]["kind"] == "declared-valuation"
    assert body["basis"]["propagated"] is False
    assert body["basis"]["severity_sampled"] is False
    # The pre-filter exists and runs in `twin options`; there is no choice set here to filter,
    # because these are valuations of components rather than candidate responses.
    assert body["prefilter"]["applied"] is False
    assert "twin options" in body["prefilter"]["note"]


def test_a_component_nobody_valued_is_null_and_not_zero(repo: ModelRepo, caps: Capabilities, tmp_path: Path) -> None:
    """Zero says 'worth nothing to them', which is a different claim and usually a false one."""
    root = fixtures.build(tmp_path / "partial")
    path = root / "orgs" / "netflix" / "perspectives" / "the-staff-council.yaml"
    text = path.read_text(encoding="utf-8")
    start = text.index("  streaming-experience:\n")
    path.write_text(text[:start] + text[text.index("  dvd-by-mail:\n"):], encoding="utf-8")
    fixtures.git(root, "add", "-A")
    fixtures.git(root, "commit", "-q", "-m", "a perspective that values one component only")

    body = _exposure(ModelRepo.open(root), caps)
    council = next(e for e in body["perspectives"] if e["id"] == "the-staff-council")
    assert council["unvalued"] == ["streaming-experience"]
    assert "streaming-experience" not in {e["component"] for e in council["admitted"]}
    assert "streaming-experience" not in {e["component"] for e in council["register"]}
    assert council["declared_exposure"] == 9000000.0
    row = next(r for r in body["attribution"] if r["component"] == "streaming-experience")
    assert row["declared_value"]["the-staff-council"] is None


# -- the constraint set (27) --------------------------------------------------------------------


def test_the_constraint_set_publishes_both_tiers_and_a_ruin_class() -> None:
    published = constraints.published()
    assert published["universal_floor"]
    classes = {c["class"] for c in published["universal_floor"]}
    assert "ruin" in classes and "forbidden" in classes
    assert set(published["tiers"]) == {"universal", "perspective"}


def test_scope_exclusions_are_published_and_named_individually() -> None:
    exclusions = constraints.published()["scope_exclusions"]
    assert len(exclusions) >= 3
    for entry in exclusions:
        assert entry["id"] and entry["excluded"].strip() and entry["because"].strip()


@pytest.mark.parametrize(
    "position,status",
    [
        ("no-power-layer", "stated"),
        ("exit-cost-asymmetry", "unsolved"),
        ("reflexivity-and-goodhart-on-the-twin", "deferred"),
        ("covert-sensing", "permanently-excluded"),
    ],
)
def test_each_position_is_stated_by_name(position: str, status: str) -> None:
    """'Presumably covered' is how an absence happens, so each is required by name."""
    stated = {p["id"]: p for p in constraints.published()["positions"]}
    assert stated[position]["status"] == status
    assert stated[position]["states"].strip()


def test_covert_sensing_is_permanently_excluded_and_not_deferred() -> None:
    stated = {p["id"]: p for p in constraints.published()["positions"]}
    assert stated["covert-sensing"]["status"] != stated["reflexivity-and-goodhart-on-the-twin"]["status"]


def test_a_constraint_set_missing_a_position_is_refused(tmp_path: Path) -> None:
    path = tmp_path / "constraints.yaml"
    text = constraints.CONSTRAINTS_PATH.read_text(encoding="utf-8")
    path.write_text(text.replace("  - id: exit-cost-asymmetry", "  - id: something-else"), encoding="utf-8")
    with pytest.raises(ConstraintError, match="exit-cost-asymmetry"):
        constraints.load(path)


def test_a_constraint_set_with_an_empty_floor_is_refused(tmp_path: Path) -> None:
    """An empty floor is a twin in which every option has a price."""
    path = tmp_path / "no-floor.yaml"
    text = constraints.CONSTRAINTS_PATH.read_text(encoding="utf-8")
    path.write_text(text.split("universal_floor:")[0] + "universal_floor: []\n" +
                    "scope_exclusions:" + text.split("scope_exclusions:")[1], encoding="utf-8")
    with pytest.raises(ConstraintError, match="no universal floor"):
        constraints.load(path)
