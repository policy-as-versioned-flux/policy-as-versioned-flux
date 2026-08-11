"""The pocket-org golden fixture and its worksheet (build ticket 15).

The CLI-level check the ticket asks for: build the fixture, run the tool, compare the emitted
artefact against numbers a human worked out by hand. This is the mechanism that catches what a
refusal test cannot — an elasticity that quietly stops being recalibrated, a propagation that
changed and nobody noticed, a triple that is present but wrong.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from twin import attest, fixtures, sign, worksheet
from twin.cli import main

KEY = "a-test-key"


@pytest.fixture(scope="module")
def pocket(tmp_path_factory: pytest.TempPathFactory) -> Path:
    return fixtures.build_pocket_org(tmp_path_factory.mktemp("pocket") / "repo")


def test_the_artefact_matches_the_worksheet(pocket: Path, capsys: pytest.CaptureFixture[str]) -> None:
    assert main(["worksheet", "--repo", str(pocket)]) == 0
    out = capsys.readouterr().out
    assert " differ," in out and "0 differ," in out


def test_every_line_is_either_matched_or_pending_on_an_open_ticket(pocket: Path) -> None:
    from twin.grades import Capabilities
    from twin.repo import ModelRepo

    results = worksheet.check(worksheet.bodies_for(ModelRepo.open(pocket), Capabilities.load()))

    assert len(results) >= 20, "a worksheet this thin would not catch anything"
    assert all(r.ok or r.pending for r in results)
    assert worksheet.overdue(results) == [], "a pending line whose ticket has closed is a silent gap"

    # The contract every later ticket inherits is asserted on the **worksheet's own text**, not on
    # a pending line happening to exist. It did until build ticket 30, which was the last ticket
    # owing one — and an assertion that a pending line exists would then have forced somebody to
    # keep one open to stay green, which is the opposite of what the contract asks for.
    assert "## The contract every later ticket inherits" in worksheet.WORKSHEET_PATH.read_text(
        encoding="utf-8"
    ), "the contract later tickets inherit is written down"


def test_a_changed_elasticity_fails_the_worksheet(tmp_path: Path) -> None:
    """The whole point: a number that drifts is caught, not merely still present."""
    repo = fixtures.build_pocket_org(tmp_path / "drifted")
    path = repo / "orgs" / "pocket" / "edges" / "database-slows-orders.yaml"
    path.write_text(path.read_text(encoding="utf-8").replace("mode: 0.5", "mode: 0.55"), encoding="utf-8")
    fixtures.git(repo, "add", "-A")
    fixtures.git(repo, "commit", "-q", "-m", "drift an elasticity nobody recalibrated")

    assert main(["worksheet", "--repo", str(repo)]) == 1


def test_a_moved_position_fails_the_worksheet(tmp_path: Path) -> None:
    repo = fixtures.build_pocket_org(tmp_path / "moved")
    path = repo / "orgs" / "pocket" / "components" / "customer-portal.yaml"
    path.write_text(path.read_text(encoding="utf-8").replace("visibility: 0.9", "visibility: 0.8"), encoding="utf-8")
    fixtures.git(repo, "add", "-A")
    fixtures.git(repo, "commit", "-q", "-m", "move a component on the map")

    assert main(["worksheet", "--repo", str(repo)]) == 1


def test_the_pocket_org_is_five_components_and_eight_edges(pocket: Path) -> None:
    """Build ticket 21 added the two edges that close the diamond, and nothing else."""
    from twin.model import Overlay
    from twin.repo import ModelRepo

    graph = Overlay.load(ModelRepo.open(pocket), worksheet.POCKET_ORG).graph()
    assert len(graph.components) == 5, "hand-computable means small"
    assert len(graph.edges) == 8
    assert sum(1 for e in graph.edges if e.causal) == 4, "named elasticities"
    # The diamond itself: two routes from the database to the portal, sharing their first hop.
    routes = {
        ("shared-database", "order-service"), ("order-service", "customer-portal"),
        ("order-service", "payment-gateway"), ("payment-gateway", "customer-portal"),
    }
    assert {(e.source, e.target) for e in graph.edges if e.causal} == routes


def test_the_worksheet_declares_the_role_accountable_for_its_numbers() -> None:
    role, lines = worksheet.load()
    assert role in sign.role_ids(), "an unregistered role has nobody accountable behind it"
    assert all(line.ticket for line in lines), "every line names the ticket that asserts it"


def test_the_worksheet_emits_as_an_authored_artefact_and_signs(tmp_path: Path, monkeypatch) -> None:
    """The one place a human number is the authority, marked and signed as such."""
    monkeypatch.setenv(sign.KEY_ENV, KEY)
    out = tmp_path / "worksheet.json"
    assert main(["worksheet", "--emit", str(out)]) == 0

    doc = json.loads(out.read_bytes())
    assert doc["envelope"]["mark"] == "authored"
    assert doc["envelope"]["pins"]["role"] == worksheet.load()[0]

    sidecar = attest.load(attest.sidecar_for(out))
    assert attest.human_signed(sidecar)
    assert sidecar["human_involvement"]["signatures"][0]["role"] == worksheet.load()[0]
    assert attest.check(sidecar, out.read_bytes(), KEY.encode()) == []


def test_a_worksheet_with_no_authoring_role_is_refused(tmp_path: Path) -> None:
    stripped = tmp_path / "unsigned-worksheet.md"
    stripped.write_text(
        worksheet.WORKSHEET_PATH.read_text(encoding="utf-8").replace("Authored-by-role:", "Written by:"),
        encoding="utf-8",
    )
    with pytest.raises(worksheet.WorksheetError, match="Authored-by-role"):
        worksheet.load(stripped)
