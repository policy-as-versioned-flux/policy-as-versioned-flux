"""Derived roll-ups (build ticket 13).

An aggregate can never drift from its constituents, because there is no second copy of it: the
roll-up exists for as long as it takes to serialise, and is recomputed on the next read. The
tests assert the three consequences — computed on read, no authored form, and no separate step
between changing a constituent and changing the aggregate.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from twin import fixtures, verbs
from twin.grades import Capabilities
from twin.model import Overlay
from twin.repo import ModelRepo
from twin.schema import RollUpError, ROLLUP_FIELDS, validate


def _rollups(root: Path, org: str = "netflix") -> dict[str, object]:
    return Overlay.load(ModelRepo.open(root), org).graph().rollups()


def test_a_rollup_is_computed_from_its_constituents(repo: ModelRepo, caps: Capabilities) -> None:
    artefact = verbs.graph(repo, caps, "netflix", verbs.command_for("graph", org="netflix"))
    body = json.loads(artefact.to_bytes())["body"]
    rolled = body["rollups"]

    assert rolled["components"] == len(body["components"])
    assert rolled["people"] == len(body["people"])
    assert rolled["edges"] == len(body["edges"])
    assert sum(rolled["components_by_kind"].values()) == rolled["components"]
    assert sum(rolled["edges_by_type"].values()) == rolled["edges"]
    assert rolled["causal_edges"] == sum(1 for e in body["edges"] if e["type"] == "influences")
    assert rolled["components_with_a_named_holder"] == len(body["bus_factor"])
    assert rolled["components_positioned_on_the_map"] == len(body["wardley"]["positions"])


def test_changing_a_constituent_changes_the_rollup_with_no_separate_step(scratch_repo: Path) -> None:
    before = _rollups(scratch_repo)
    path = scratch_repo / "orgs" / "netflix" / "components" / "billing.yaml"
    path.write_text(
        "id: billing\nname: Billing\nkind: capability\nevolution: product\nvisibility: 0.6\n",
        encoding="utf-8",
    )
    fixtures.git(scratch_repo, "add", "-A")
    fixtures.git(scratch_repo, "commit", "-q", "-m", "add a constituent")

    after = _rollups(scratch_repo)
    assert after["components"] == before["components"] + 1  # type: ignore[operator]
    assert after["components_by_kind"]["capability"] == 1  # type: ignore[index]
    assert after["components_positioned_on_the_map"] == before["components_positioned_on_the_map"] + 1  # type: ignore[operator]


@pytest.mark.parametrize("field", ROLLUP_FIELDS)
def test_an_authored_rollup_is_rejected(field: str) -> None:
    """Refused by name inside a free-form mapping; refused by closure everywhere else."""
    doc = {
        "id": "a-signal", "date": "2011-07-12", "steep": "economic", "source": "s",
        "statement": "t", "provenance": {"observed_by": "x", field: 42},
    }
    with pytest.raises(RollUpError, match="Roll-ups are derived"):
        validate("signal", doc, "planted")


def test_a_rollup_has_no_authored_form_in_any_schema() -> None:
    """The closure is the guarantee. The named list above only improves the error message."""
    from twin.schema import SCHEMAS

    for name, schema in SCHEMAS.items():
        declared = set(schema.required) | set(schema.optional)
        assert not declared & set(ROLLUP_FIELDS), f"{name} declares a slot for an authored aggregate"


def test_no_rollup_is_stored_anywhere_a_reader_could_reach_it(repo: ModelRepo, tmp_path: Path) -> None:
    """The derived index is the one store in the system, and it holds no aggregate."""
    from twin import index

    out = index.write(repo, tmp_path / "derived-index")
    for path in sorted(out.rglob("*.json")):
        doc = json.loads(path.read_bytes())
        assert not set(doc) & set(ROLLUP_FIELDS)
        assert "rollups" not in json.dumps(doc)
