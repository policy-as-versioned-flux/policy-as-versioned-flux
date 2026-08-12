"""Use-gating and the unpriced structural blast radius (build ticket 19).

Only grades 1-2 may price a scored forecast. The consequence is the second output: when a path is
real but too weakly evidenced to price, the answer is "we know this is connected but cannot price
it" — a first-class result rather than a gap papered over.
"""

from __future__ import annotations

import json

import pytest

from twin import blast, evidence, verbs
from twin.artefact import ArtefactError
from twin.grades import Capabilities
from twin.blast import BELOW_THRESHOLD, NO_MECHANISM, radius
from twin.model import ModelError, Overlay
from twin.repo import ModelRepo
from twin.schema import CAUSAL_EDGE, EVIDENCE_GRADES, STRUCTURAL_EDGE

ORIGIN = "content-delivery-network"


def _body(repo: ModelRepo, caps: Capabilities, org: str = "netflix", origin: str = ORIGIN) -> dict:
    artefact = verbs.blast(repo, caps, org, origin, verbs.command_for("blast", org=org, origin=origin))
    body: dict = json.loads(artefact.to_bytes())["body"]
    return body


def test_only_grades_one_and_two_may_price() -> None:
    assert [g for g in EVIDENCE_GRADES if evidence.may_price(g)] == [1, 2]
    assert evidence.may_price(5) is False


def test_a_well_evidenced_path_is_admitted(repo: ModelRepo, caps: Capabilities) -> None:
    """The positive leg. A gate that admits nothing is a wall, and a wall passes every refusal."""
    admitted = {e["component"]: e for e in _body(repo, caps)["admitted_to_pricing"]}
    assert "streaming-experience" in admitted
    entry = admitted["streaming-experience"]
    assert entry["worst_evidence_grade"] <= evidence.threshold()
    assert all(hop["hop"] == CAUSAL_EDGE for hop in entry["path"])


def test_a_grade_five_only_path_is_unpriced(repo: ModelRepo, caps: Capabilities) -> None:
    """Grade 5 is a model assertion, which is exactly where contamination hides."""
    body = _body(repo, caps)
    assert "brand-goodwill" not in {e["component"] for e in body["admitted_to_pricing"]}
    entry = next(e for e in body["unpriced"] if e["component"] == "brand-goodwill")
    assert entry["worst_evidence_grade"] == 5
    assert entry["reason"] == BELOW_THRESHOLD


def test_a_structural_path_is_reported_with_no_mechanism_claimed(repo: ModelRepo, caps: Capabilities) -> None:
    """Real exposure, no claimed mechanism. Pricing it would manufacture a number."""
    overlay = Overlay.load(repo, "intel")
    reached = radius(overlay.graph(), "euv-lithography")
    unpriced = {e["component"]: e for e in reached["unpriced"]}
    assert unpriced["foundry-services"]["reason"] == NO_MECHANISM
    assert any(hop["hop"] == STRUCTURAL_EDGE for hop in unpriced["foundry-services"]["path"])


def test_the_blast_radius_is_a_distinct_type_with_no_price_slot(repo: ModelRepo, caps: Capabilities) -> None:
    """Not a price with a null field: the body is closed and there is nowhere to put one."""
    artefact = verbs.blast(repo, caps, "netflix", ORIGIN, verbs.command_for("blast", origin=ORIGIN))
    assert artefact.kind == verbs.KIND_BLAST_RADIUS
    price_shaped = {"price", "cost", "loss", "severity", "expected_loss", "gbp", "amount"}
    assert not price_shaped & blast.BODY_KEYS
    with pytest.raises(ArtefactError, match="closed"):
        blast.refuse_undeclared_keys({**artefact.body, "price": 1})


def test_the_threshold_is_published_and_pinned_in_the_artefact(repo: ModelRepo, caps: Capabilities) -> None:
    """Changing what may price is as visible as changing the constraint set."""
    gating = _body(repo, caps)["gating"]
    assert gating["pin"] == evidence.pin()
    assert gating["pin"]["pricing_threshold"] == evidence.threshold()
    assert [g["grade"] for g in gating["grades"]] == list(EVIDENCE_GRADES)
    assert all(g["admits"].strip() for g in gating["grades"])


def test_the_traversal_records_the_limits_it_inherited(repo: ModelRepo, caps: Capabilities) -> None:
    """Reverse-dependency traversal is inherited from /arckit:impact, caveats included."""
    traversal = _body(repo, caps)["traversal"]
    assert traversal["inherited_from"] == "/arckit:impact"
    assert traversal["known_limits"]
    assert isinstance(traversal["truncated"], bool)


def test_an_origin_that_is_not_a_component_is_refused(repo: ModelRepo, caps: Capabilities) -> None:
    with pytest.raises(ModelError, match="no component"):
        verbs.blast(repo, caps, "netflix", "not-a-component", verbs.command_for("blast"))


def test_the_traversal_is_deterministic(repo: ModelRepo, caps: Capabilities) -> None:
    """Two paths of equal rank must not depend on which the walk reached first."""
    assert _body(repo, caps) == _body(repo, caps)
