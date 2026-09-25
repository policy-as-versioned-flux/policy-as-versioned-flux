"""An adopter declares the grade it prices on (eco-system ticket 141, ADR-0032).

Four things, each planted and each read back off the artefact rather than off the code:

1. the declaration: `appetite.pricing_threshold` on a party artefact is 2 or 3, absent means the
   ladder's 2, and every other value is refused by name;
2. the gate: an amount at grade 3 loads and prices only for a party that declared 3, and every
   overlay that declares nothing behaves exactly as it did, the pocket org included;
3. the weakest grade: every price carries `rests_on_grade`, the one order statistic ADR-0024
   point 6 admits, and the `gating` block says which thresholds were applied and why;
4. a synthetic record never raises a grade: a planted regrade that strengthens an edge on a
   synthetic drill goes red at the pricing gate whatever the file declares, and so does a
   mitigation claim that rests on one.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from twin import evidence, fixtures, pricing, synthetic, verbs
from twin.evidence import EvidenceError
from twin.grades import Capabilities
from twin.model import Overlay
from twin.repo import ModelRepo
from twin.schema import SchemaError, validate

OPERATOR = "the-operator"
PRICED_ORIGIN, REFUSED_ORIGIN = "order-service", "shared-database"
GRADE_3_EDGE = "orgs/pocket/edges/database-slows-orders.yaml"
OPERATOR_FILE = "orgs/pocket/perspectives/the-operator.yaml"

PERSPECTIVE = {
    "id": "planted", "name": "Planted", "party": "employer", "pays": "somebody",
    "ruin": {"insolvency": "a boundary"}, "cash_flow": ["a-component"],
}


def _plant(root: Path, files: dict[str, str], message: str) -> None:
    fixtures._write(root, files)
    fixtures.git(root, "add", "-A")
    fixtures.git(root, "commit", "-q", "-m", message)


def _rewrite(root: Path, rel: str, old: str, new: str) -> None:
    path = root / rel
    text = path.read_text(encoding="utf-8")
    assert old in text, f"{rel} no longer carries {old!r}; this test lost its subject"
    path.write_text(text.replace(old, new), encoding="utf-8", newline="\n")


@pytest.fixture()
def pocket(tmp_path: Path) -> Path:
    return fixtures.build_pocket_org(tmp_path / "pocket")


def _price(root: Path, origin: str, threshold: int | None = None, perspective: str = OPERATOR) -> dict:
    overlay = Overlay.load(ModelRepo.open(root), "pocket", pricing_threshold=threshold)
    return pricing.price(overlay.graph(), overlay.perspectives[perspective], origin,
                         overlay.responses, overlay)


# -- 1. the declaration -----------------------------------------------------------------------


def test_only_two_and_three_can_be_declared() -> None:
    assert evidence.DECLARABLE_THRESHOLDS == (2, 3)
    assert evidence.check_threshold(2) == 2 and evidence.check_threshold(3) == 3


@pytest.mark.parametrize("bad", [1, 4, 5, 0, -3, "3", 3.0, True, False, None, [3], {"grade": 3}])
def test_every_other_threshold_is_refused_by_name(bad: object) -> None:
    with pytest.raises(EvidenceError, match="appetite.pricing_threshold"):
        evidence.check_threshold(bad)


def test_the_declaration_is_read_off_the_party_artefact() -> None:
    assert evidence.declared_threshold(None) == evidence.threshold() == 2
    assert evidence.declared_threshold({}) == 2
    assert evidence.declared_threshold({"appetite": {"tolerance": {"amount": 1, "currency": "GBP"}}}) == 2
    assert evidence.declared_threshold({"appetite": {"pricing_threshold": 2}}) == 2
    assert evidence.declared_threshold({"appetite": {"pricing_threshold": 3}}) == 3


@pytest.mark.parametrize("bad", [1, 4, 5, "3", 3.0, True])
def test_a_declaration_outside_the_admitted_values_is_refused_not_clamped(bad: object) -> None:
    with pytest.raises(EvidenceError, match=r"driftwood/party.yaml: pricing threshold"):
        evidence.declared_threshold({"appetite": {"pricing_threshold": bad}}, where="driftwood/party.yaml")


def test_an_appetite_that_is_not_a_mapping_is_refused() -> None:
    with pytest.raises(EvidenceError, match="appetite is not a mapping"):
        evidence.declared_threshold({"appetite": 3})
    with pytest.raises(EvidenceError, match="is a mapping"):
        evidence.declared_threshold(["appetite"])


def test_may_price_takes_the_declaration_and_never_a_grade_nobody_may_declare() -> None:
    assert evidence.may_price(3) is False
    assert evidence.may_price(3, threshold=3) is True
    assert evidence.may_price(3, threshold=2) is False
    assert evidence.may_price(4, threshold=3) is False
    assert evidence.may_price(5, threshold=3) is False
    with pytest.raises(EvidenceError):
        evidence.may_price(4, threshold=4)


# -- 3. the weakest grade, and what was applied --------------------------------------------------


def test_weakest_is_an_order_statistic_and_nothing_else() -> None:
    assert evidence.weakest(2, 3) == 3
    assert evidence.weakest(3, 2, 1) == 3
    assert evidence.weakest(1, 1) == 1
    assert evidence.weakest(None, 2) == 2
    assert evidence.weakest() is None
    assert evidence.weakest(None) is None
    with pytest.raises(EvidenceError, match="not on the ladder"):
        evidence.weakest(2, 6)


def test_applied_names_the_basis_of_the_thresholds_in_force() -> None:
    default = evidence.applied()
    assert default == {"pricing_threshold": 2, "path_admission_threshold": 2,
                       "basis": evidence.LADDER_DEFAULT}
    declared = evidence.applied(3, 3)
    assert declared["pricing_threshold"] == declared["path_admission_threshold"] == 3
    assert declared["basis"] == evidence.PARTY_DECLARATION
    assert "appetite.pricing_threshold" in declared["basis"]
    # A traversal that passes nothing publishes the ladder alone, exactly as before.
    assert "applied" not in evidence.published()
    assert evidence.published(pricing=3, admission=3)["applied"] == declared
    assert "1-3" in evidence.published(pricing=3, admission=3)["rule"]


# -- 2. the gate, at the source -----------------------------------------------------------------


def test_an_amount_at_grade_three_loads_only_for_a_party_that_declared_three() -> None:
    doc = {**PERSPECTIVE, "values": {"a-component": {"amount": 1.0, "evidence_grade": 3, "basis": "published"}}}
    with pytest.raises(SchemaError, match=r"outside the pricing threshold \(2\)"):
        validate("perspective", doc, "planted")
    with pytest.raises(SchemaError, match="declares appetite.pricing_threshold: 3"):
        validate("perspective", doc, "planted", pricing_threshold=2)
    validate("perspective", doc, "planted", pricing_threshold=3)


def test_a_grade_three_valuation_with_no_amount_is_a_gap_for_a_party_that_declared_three() -> None:
    doc = {**PERSPECTIVE, "values": {"a-component": {"evidence_grade": 3, "basis": "published"}}}
    validate("perspective", doc, "planted")
    with pytest.raises(SchemaError, match="admits a figure and none is declared"):
        validate("perspective", doc, "planted", pricing_threshold=3)


@pytest.mark.parametrize("grade", [4, 5])
def test_an_amount_at_grade_four_or_five_never_loads_for_anybody(grade: int) -> None:
    doc = {**PERSPECTIVE, "values": {"a-component": {"amount": 1.0, "evidence_grade": grade, "basis": "said so"}}}
    for threshold in (None, 2, 3):
        with pytest.raises(SchemaError, match="may not carry an amount for anybody"):
            validate("perspective", doc, "planted", pricing_threshold=threshold)


def test_the_loader_is_refused_a_threshold_nobody_may_declare(pocket: Path) -> None:
    with pytest.raises(EvidenceError, match="appetite.pricing_threshold"):
        Overlay.load(ModelRepo.open(pocket), "pocket", pricing_threshold=4)


def test_the_loader_takes_the_declaration_and_records_it(pocket: Path) -> None:
    """The operator's portal valuation moved to grade 3 with its amount kept: published work."""
    _rewrite(pocket, OPERATOR_FILE, "amount: 400000\n    evidence_grade: 2",
             "amount: 400000\n    evidence_grade: 3")
    fixtures.git(pocket, "add", "-A")
    fixtures.git(pocket, "commit", "-q", "-m", "the portal valuation now rests on published work")
    repo = ModelRepo.open(pocket)
    with pytest.raises(SchemaError, match="declares appetite.pricing_threshold: 3"):
        Overlay.load(repo, "pocket")
    overlay = Overlay.load(repo, "pocket", pricing_threshold=3)
    assert overlay.pricing_threshold == 3
    assert Overlay.load(ModelRepo.open(fixtures.build_pocket_org(pocket.parent / "untouched")), "pocket").pricing_threshold == 2


# -- 2. the gate, at the price ------------------------------------------------------------------


def test_the_pocket_org_prices_exactly_as_before_without_a_declaration(pocket: Path) -> None:
    body = _price(pocket, REFUSED_ORIGIN)
    assert body["impacts"] == []
    reasons = {r["component"]: r["reason"] for r in body["register"]}
    assert reasons["customer-portal"] == pricing.PATH_TOO_WEAK
    assert body["gating"]["applied"] == evidence.applied()
    priced = _price(pocket, PRICED_ORIGIN)
    assert [i["component"] for i in priced["impacts"]] == ["customer-portal"]
    assert priced["impacts"][0]["price"]["attenuated"]["mode"] == 160000.0


def test_a_party_that_declared_three_prices_the_grade_three_path(pocket: Path) -> None:
    """Every route out of shared-database crosses `database-slows-orders` at grade 3."""
    body = _price(pocket, REFUSED_ORIGIN, threshold=3)
    named = {i["component"]: i for i in body["impacts"]}
    assert "customer-portal" in named
    impact = named["customer-portal"]
    assert impact["worst_evidence_grade"] == 3
    assert impact["valuation"]["evidence_grade"] == 2
    # The weaker of the path (3) and the valuation (2): the price rests on grade 3.
    assert impact["rests_on_grade"] == 3
    assert body["gating"]["applied"] == {
        "pricing_threshold": 3, "path_admission_threshold": 3, "basis": evidence.PARTY_DECLARATION,
    }
    assert body["gating"]["pin"] == evidence.pin()  # the ladder itself did not move
    assert "1-3" in body["gating"]["rule"]


def test_every_price_shows_the_weakest_grade_it_rests_on(pocket: Path) -> None:
    body = _price(pocket, PRICED_ORIGIN)
    for impact in body["impacts"]:
        assert impact["rests_on_grade"] == max(impact["worst_evidence_grade"], impact["valuation"]["evidence_grade"])
    credited = [o for o in body["responses"]["priced"] if "credit" in o["mitigation"]]
    assert credited, "the pocket org credits one option; this leg would assert nothing"
    for option in credited:
        mitigation = option["mitigation"]
        assert mitigation["rests_on_grade"] >= mitigation["evidence_grade"]
        assert mitigation["rests_on_grade"] in evidence.EVIDENCE_GRADES
    for option in body["responses"]["priced"]:
        if "reason" in option["mitigation"]:
            assert "rests_on_grade" not in option["mitigation"]


def test_an_amount_at_grade_three_prices_only_for_a_party_that_declared_three(pocket: Path) -> None:
    """The gate re-checks the valuation itself: a grade-3 amount in a file loaded at 3 prices
    under 3 and is a register entry under the default, even when the file could load."""
    _rewrite(pocket, OPERATOR_FILE, "amount: 400000\n    evidence_grade: 2",
             "amount: 400000\n    evidence_grade: 3")
    fixtures.git(pocket, "add", "-A")
    fixtures.git(pocket, "commit", "-q", "-m", "the portal valuation now rests on published work")
    overlay = Overlay.load(ModelRepo.open(pocket), "pocket", pricing_threshold=3)
    body = pricing.price(overlay.graph(), overlay.perspectives[OPERATOR], PRICED_ORIGIN,
                         overlay.responses, overlay)
    impact = next(i for i in body["impacts"] if i["component"] == "customer-portal")
    assert impact["valuation"]["evidence_grade"] == 3 and impact["rests_on_grade"] == 3
    # The same overlay object with its threshold forced back to the default: the loader is not
    # trusted, the gate refuses the amount itself.
    forced = Overlay(**{**overlay.__dict__, "pricing_threshold": 2})
    body = pricing.price(forced.graph(), forced.perspectives[OPERATOR], PRICED_ORIGIN,
                         forced.responses, forced)
    assert "customer-portal" not in {i["component"] for i in body["impacts"]}
    entry = next(r for r in body["register"] if r["component"] == "customer-portal")
    assert entry["reason"] == pricing.VALUATION_TOO_WEAK
    assert "amount" not in entry


def test_the_exposure_carries_the_applied_thresholds_and_the_weakest_grade(
    pocket: Path, caps: Capabilities
) -> None:
    import json

    artefact = verbs.exposure(ModelRepo.open(pocket), caps, "pocket", "portal-availability-2026", None,
                              verbs.command_for("exposure", org="pocket", scenario="portal-availability-2026"))
    body = json.loads(artefact.to_bytes())["body"]
    assert body["gating"]["applied"] == evidence.applied()
    for entry in body["perspectives"]:
        for admitted in entry["admitted"]:
            assert admitted["rests_on_grade"] in evidence.EVIDENCE_GRADES
            assert admitted["rests_on_grade"] >= admitted["evidence_grade"]


def test_the_corroboration_gate_does_not_read_the_declaration(repo: ModelRepo) -> None:
    """A declaration widens what a party may price about the world, never what counts as the
    party having acted: a self-declared-only enactment stays uncorroborated at 3 as at 2."""
    intel = Overlay.load(repo, "intel", pricing_threshold=3)
    claim = {"component": "a-component", "reduction": {"min": 0.1, "mode": 0.2, "max": 0.3},
             "evidence_grade": 3, "basis": "published work, not observed here"}
    priced = [{"component": "a-component", "rests_on_grade": 3,
               "price": {"attenuated": {"min": 100.0, "mode": 200.0, "max": 300.0}}}]
    self_declared = pricing._credit({"option": "report-node-schedule-variance"}, claim, priced, intel)
    assert self_declared["reason"] == pricing.NOT_ENACTED
    corroborated = pricing._credit({"option": "pin-the-tooling-image-set"}, claim, priced, intel)
    assert "reason" not in corroborated
    assert corroborated["rests_on_grade"] == 3  # the claim's own grade 3 is the weakest
    # And the same grade-3 claim earns nothing at all without the declaration.
    default = Overlay.load(repo, "intel")
    assert pricing._credit({"option": "pin-the-tooling-image-set"}, claim, priced, default)["reason"] \
        == pricing.CLAIM_TOO_WEAK


# -- 4. a synthetic record never raises a grade -------------------------------------------------


SYNTHETIC_SIGNAL = """\
id: incident-drill-2026
date: '2026-03-01'
steep: technological
source: The platform team's synthetic incident drill
statement: A forced database slowdown was injected into a rehearsal environment and observed.
provenance:
  observed_by: fixture
  synthetic: true
"""


def test_what_marks_a_record_synthetic() -> None:
    assert synthetic.is_synthetic_record({"substrate": fixtures.ABSENT_SUBSTRATE}) is None
    assert synthetic.is_synthetic_record({"substrate": "sha256:" + "a" * 64 + ":1024"})
    assert synthetic.is_synthetic_record({"provenance": {"observed_by": "fixture"}}) is None
    for marker in synthetic.MARKERS:
        assert marker in synthetic.is_synthetic_record({"provenance": {marker: True}})
    assert synthetic.marker_in("the planted-signal walk") == "planted"
    assert synthetic.marker_in("nothing of the kind") is None
    assert synthetic.marker_in("synthetically") is None  # word boundaries, not substrings


def test_a_planted_regrade_on_a_synthetic_drill_goes_red_whatever_the_file_declares(pocket: Path) -> None:
    """Ticket 30 round 1's shape, reversed by ADR-0032: the grade-3 edge is regraded to 2 on a
    marked synthetic incident record, so the file now says the path prices. It does not."""
    _rewrite(pocket, GRADE_3_EDGE, "evidence_grade: 3", "evidence_grade: 2")
    _plant(pocket, {
        "orgs/pocket/signals/incident-drill-2026.yaml": SYNTHETIC_SIGNAL,
        "orgs/pocket/regrades/database-slows-orders-strengthened.yaml": """\
id: database-slows-orders-strengthened
subject: database-slows-orders
from_grade: 3
to_grade: 2
regraded_on: '2026-03-02'
by_role: model-steward
reason: The drill showed the slowdown reaching the order service, so the mechanism is observed.
evidence: The incident drill incident-drill-2026, run twice in the rehearsal environment.
""",
    }, "strengthen the edge on a synthetic drill")
    for threshold in (None, 3):
        body = _price(pocket, REFUSED_ORIGIN, threshold=threshold)
        assert "customer-portal" not in {i["component"] for i in body["impacts"]}
        entry = next(r for r in body["register"] if r["component"] == "customer-portal")
        assert entry["reason"] == pricing.RESTS_ON_SYNTHETIC
        assert "database-slows-orders-strengthened" in entry["detail"]
        assert "incident-drill-2026" in entry["detail"]
        assert "synthetic" in entry["detail"]
        assert set(entry) <= {"component", "reason", "detail", "depth", "worst_evidence_grade"}
    # The rule reads the record, not the word: the same regrade citing the drill by its marker
    # word alone is refused too.
    _rewrite(pocket, "orgs/pocket/regrades/database-slows-orders-strengthened.yaml",
             "The incident drill incident-drill-2026, run twice",
             "A synthetic incident drill, run twice")
    fixtures.git(pocket, "add", "-A")
    fixtures.git(pocket, "commit", "-q", "-m", "cite the drill by kind")
    entry = next(r for r in _price(pocket, REFUSED_ORIGIN)["register"] if r["component"] == "customer-portal")
    assert entry["reason"] == pricing.RESTS_ON_SYNTHETIC


def test_the_control_case_without_the_synthetic_record_prices(pocket: Path) -> None:
    """The negative control: the identical regrade citing a real record prices, so the refusal
    above is attributable to the synthetic marker and not to the regrade."""
    _rewrite(pocket, GRADE_3_EDGE, "evidence_grade: 3", "evidence_grade: 2")
    _plant(pocket, {
        "orgs/pocket/regrades/database-slows-orders-strengthened.yaml": """\
id: database-slows-orders-strengthened
subject: database-slows-orders
from_grade: 3
to_grade: 2
regraded_on: '2026-03-02'
by_role: model-steward
reason: Three dated incidents showed the slowdown reaching the order service.
evidence: Incident records of 2025-11-02, 2026-01-14 and 2026-02-20.
""",
    }, "strengthen the edge on real records")
    body = _price(pocket, REFUSED_ORIGIN)
    assert "customer-portal" in {i["component"] for i in body["impacts"]}


def test_a_valuation_whose_basis_is_a_synthetic_drill_is_refused(pocket: Path) -> None:
    _rewrite(pocket, OPERATOR_FILE, "Order value lost per hour of portal outage, from repeated incident records.",
             "Order value lost per hour of portal outage, from the synthetic incident drill.")
    fixtures.git(pocket, "add", "-A")
    fixtures.git(pocket, "commit", "-q", "-m", "rest the valuation on a drill")
    body = _price(pocket, PRICED_ORIGIN)
    assert "customer-portal" not in {i["component"] for i in body["impacts"]}
    entry = next(r for r in body["register"] if r["component"] == "customer-portal")
    assert entry["reason"] == pricing.RESTS_ON_SYNTHETIC and "valuation" in entry["detail"]


def test_a_mitigation_claim_resting_on_a_synthetic_record_earns_nothing(repo: ModelRepo) -> None:
    intel = Overlay.load(repo, "intel")
    claim = {"component": "a-component", "reduction": {"min": 0.1, "mode": 0.2, "max": 0.3},
             "evidence_grade": 2, "basis": "the reduction observed in the injected drill"}
    priced = [{"component": "a-component", "rests_on_grade": 2,
               "price": {"attenuated": {"min": 100.0, "mode": 200.0, "max": 300.0}}}]
    result = pricing._credit({"option": "pin-the-tooling-image-set"}, claim, priced, intel)
    assert result["reason"] == pricing.RESTS_ON_SYNTHETIC and "credit" not in result


def test_an_enactment_observed_only_through_a_synthetic_record_does_not_corroborate(scratch_repo: Path) -> None:
    """The reconciler's report is replaced by a synthetic one: the option is still declared
    enacted by its subject, and the second channel now rests on a record marked synthetic."""
    _rewrite(scratch_repo, "orgs/intel/signals/fab-cluster-reconciled-against-pinned-source.yaml",
             "provenance:\n  observed_by: fixture", "provenance:\n  observed_by: fixture\n  injected: true")
    fixtures.git(scratch_repo, "add", "-A")
    fixtures.git(scratch_repo, "commit", "-q", "-m", "the reconciler report was injected by the world simulator")
    intel = Overlay.load(ModelRepo.open(scratch_repo), "intel")
    claim = {"component": "a-component", "reduction": {"min": 0.1, "mode": 0.2, "max": 0.3},
             "evidence_grade": 2, "basis": "an evidenced reduction"}
    priced = [{"component": "a-component", "rests_on_grade": 2,
               "price": {"attenuated": {"min": 100.0, "mode": 200.0, "max": 300.0}}}]
    result = pricing._credit({"option": "pin-the-tooling-image-set"}, claim, priced, intel)
    assert result["reason"] == pricing.RESTS_ON_SYNTHETIC
    assert "enacted-pins-reconciled" in result["detail"]
    assert "credit" not in result
