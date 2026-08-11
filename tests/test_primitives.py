"""Seam 2 — the two composable primitives: intervention and time (build tickets 22 and 35).

Asserted at seam 2 rather than seam 1 for the reason propagation is: an intervention that
back-propagated and a graph that was loaded wrong both surface at the CLI as "wrong component in
the list", and the difference between doing and learning is a semantic property that wants
asserting directly.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path
from typing import Any

import pytest

from twin import fixtures
from twin.artefact import ArtefactError
from twin.model import Edge, Graph, Overlay
from twin.primitives import (
    Do,
    Observe,
    PrimitiveError,
    refuse_upstream_under_intervention,
    rewind,
    severed,
    updated_beliefs,
)
from twin.repo import ModelRepo
from twin.schema import CAUSAL_EDGE

POCKET = "pocket"
# Has a cause above it and effects below it, so the downstream halves match and only the upstream
# halves differ — the distinction, isolated.
SUBJECT = "order-service"
WIDE = {"min": 0.2, "mode": 0.5, "max": 0.8}


@pytest.fixture(scope="module")
def pocket_repo(tmp_path_factory: pytest.TempPathFactory) -> Path:
    return fixtures.build_pocket_org(tmp_path_factory.mktemp("pocket") / "repo")


@pytest.fixture()
def graph(pocket_repo: Path):  # noqa: ANN201 - the Graph type is internal to twin.model
    return Overlay.load(ModelRepo.open(pocket_repo), POCKET).graph()


def _causal(ident: str, source: str, target: str, grade: int = 2) -> Edge:
    return Edge(
        id=ident,
        type=CAUSAL_EDGE,
        source=source,
        target=target,
        causal={"sign": "positive", "lag_days": 1, "elasticity": dict(WIDE), "evidence_grade": grade},
    )


def _graph_of(edges: tuple[Edge, ...]) -> Graph:
    """A graph made of the nodes these edges name.

    Built here rather than imported from `tests/test_seam2_propagation.py`: importing one test
    module from another gives mypy the same file under two module names and stops the typecheck
    dead. A few lines beats a package layout.
    """
    names = {e.source for e in edges} | {e.target for e in edges}
    return Graph(
        org="probe",
        components={n: {"id": n, "name": n, "kind": "activity"} for n in sorted(names)},
        people={},
        edges=edges,
    )


def _chain(length: int) -> Graph:
    """`c0 -> c1 -> ... -> cN`, every hop identical. Depth is then the only variable."""
    return _graph_of(tuple(_causal(f"e{i}", f"c{i}", f"c{i + 1}") for i in range(length)))


# -- intervention versus observation (build ticket 22) --------------------------------------


def test_do_leaves_upstream_beliefs_untouched_while_observe_updates_them(graph) -> None:  # noqa: ANN001
    """The property this ticket exists for.

    A system that lets an intervention back-propagate concludes that taking an action changed the
    past. The two operations are asserted against the *same* graph and the same component, so the
    only thing that can differ is the semantics.
    """
    cut = severed(graph, Do(SUBJECT))
    learned, traversal = updated_beliefs(graph, Observe(SUBJECT))

    assert [e["edge"] for e in cut] == ["database-slows-orders"]
    assert [e["component"] for e in learned] == ["shared-database"]
    assert severed(graph, Do("shared-database")) == [], "the origin of the chain has no causes to cut"
    assert updated_beliefs(graph, Observe("shared-database"))[0] == []
    assert traversal["walked"] is True and traversal["truncated"] is False


def test_an_updated_ancestor_is_named_and_graded_and_carries_no_magnitude(graph) -> None:  # noqa: ANN001
    """Inverting an elasticity needs a prior over the causes, and nothing here authors one."""
    entry = updated_beliefs(graph, Observe(SUBJECT))[0][0]

    assert entry["directional_only"] is True
    assert entry["worst_evidence_grade"] == 3 and entry["depth"] == 1
    assert entry["path"], "a direction a reader cannot locate in the graph is not a direction"
    for absent in ("composed", "attenuated", "sampled", "elasticity", "influence"):
        assert absent not in entry


def test_the_upstream_walk_handles_depth_grades_and_cycles(graph) -> None:  # noqa: ANN001
    """The walk asserted on a graph that can actually tell right from wrong.

    Every other `observe()` test here uses `order-service`, whose one ancestor sits at depth 1 on
    a single-hop path. On that graph the weakest grade equals the strongest, no cycle exists, and
    the default depth bound is never approached — so three separate defects would pass unnoticed:
    a `min` where `max` belongs, a missing cycle guard, and a depth bound of one.

    This graph has a four-hop ancestor chain with the weak edge in the middle, and **two** cycles:
    one through the target, and one entirely among the ancestors. The second matters — a guard
    that only refuses to revisit the target passes the first and loops on the second. It uses the
    **default** depth, because that is the value production runs on.
    """
    edges = (
        _causal("near", "b", "target", grade=1),
        _causal("mid", "c", "b", grade=4),
        _causal("far", "d", "c", grade=2),
        _causal("distant", "e", "d", grade=1),
        _causal("loop", "target", "e", grade=1),  # a cycle back over the whole chain
        _causal("eddy", "d", "e", grade=1),  # and a two-node cycle that never touches the target
    )
    found, traversal = updated_beliefs(_graph_of(edges), Observe("target"))

    assert [e["component"] for e in found] == ["b", "c", "d", "e"], "the walk did not reach depth 4"
    depths = {e["component"]: e["depth"] for e in found}
    assert depths == {"b": 1, "c": 2, "d": 3, "e": 4}, (
        f"an ancestor is not at its shortest depth: {depths}. A guard that only refuses to "
        "revisit the observed component would walk the d-e cycle and report d further away "
        "than it is."
    )
    # The weakest grade on the path, not the nearest hop's and not the strongest.
    grades = {e["component"]: e["worst_evidence_grade"] for e in found}
    assert grades == {"b": 1, "c": 4, "d": 4, "e": 4}, f"grades are not the path maxima: {grades}"
    # The cycle terminates: the target is not reported as its own ancestor.
    assert "target" not in depths
    assert traversal["truncated"] is False, "nothing lies beyond, so nothing was cut off"


def test_the_upstream_walk_says_where_it_stopped(graph) -> None:  # noqa: ANN001
    """A bound nobody reports is a bound nobody can allow for.

    `propagate` publishes its depth cap and its truncation flag; the upstream walk has the same
    bound and must say the same thing. Asserted on a chain longer than the bound, because on a
    short graph `truncated: false` is true for a reason that has nothing to do with the code.
    """
    chain = _chain(8)
    found, traversal = updated_beliefs(chain, Observe("c8"), max_depth=3)

    assert [e["component"] for e in found] == ["c5", "c6", "c7"]
    assert traversal["truncated"] is True, "the walk stopped at its bound and did not say so"
    assert traversal["max_depth"] == 3
    assert any("causal hops above" in limit for limit in traversal["known_limits"])

    deep, reached_all = updated_beliefs(chain, Observe("c8"), max_depth=99)
    assert len(deep) == 8
    assert reached_all["truncated"] is False, "nothing was above, so nothing was cut off"


def test_using_one_where_the_other_is_meant_is_refused(graph) -> None:  # noqa: ANN001
    """The runtime half of the type separation, for a caller that reached past the type checker."""
    with pytest.raises(PrimitiveError, match="is an observation"):
        severed(graph, Observe(SUBJECT))  # type: ignore[arg-type]
    with pytest.raises(PrimitiveError, match="is an intervention"):
        updated_beliefs(graph, Do(SUBJECT))  # type: ignore[arg-type]


def test_using_one_where_the_other_is_meant_is_a_type_error(tmp_path: Path) -> None:
    """A type error, not a runtime surprise — asserted by running the type checker, not asserted.

    The refusal above is the belt; this is the braces, and it is the one the ticket asks for. CI
    runs `mypy` over this repository, so a swap that only failed at runtime would ship.

    **Hard-fails rather than skips when mypy is absent.** It used to `importorskip`, which meant
    the only assertion behind build ticket 22's third criterion silently declined to run wherever
    the type checker was not installed — and `twin/invariants/__init__.py` says exactly why that
    is worse than nothing: a guard that quietly declines reads as green. The README documents the
    pinned venv this repository's checks expect; a missing type checker is a setup error and
    should look like one.
    """
    snippet = tmp_path / "swap.py"
    snippet.write_text(
        "from twin.model import Graph\n"
        "from twin.primitives import Do, Observe, severed, updated_beliefs\n"
        "def probe(g: Graph) -> None:\n"
        "    severed(g, Observe('x'))\n"
        "    updated_beliefs(g, Do('x'))\n",
        encoding="utf-8",
    )
    proc = subprocess.run(
        [sys.executable, "-m", "mypy", str(snippet), "--ignore-missing-imports", "--no-error-summary"],
        cwd=str(Path(__file__).resolve().parents[1]),
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )
    report = proc.stdout.decode("utf-8")
    if "No module named mypy" in report:
        raise AssertionError(
            "mypy is not installed, so build ticket 22's type-error criterion is unasserted here. "
            "Install the pinned checks: .venv/bin/pip install 'mypy==1.14.1'"
        )
    assert proc.returncode != 0, f"the type checker accepted the swap:\n{report}"
    assert report.count("arg-type") == 2, f"expected both directions to be rejected:\n{report}"


def test_an_intervention_that_updated_a_belief_upstream_is_refused() -> None:
    """Enforced on the body at emission, not trusted to the walk having been written correctly."""
    body: dict[str, Any] = {"operation": "intervene", "component": SUBJECT, "severed": [], "upstream": []}
    refuse_upstream_under_intervention(body)

    body["upstream"] = [{"component": "shared-database"}]
    with pytest.raises(ArtefactError, match="does not rewrite its own causes"):
        refuse_upstream_under_intervention(body)


def test_an_observation_that_updates_upstream_is_not_refused() -> None:
    """The guard is about intervention. A wall here would delete the other half of the design."""
    refuse_upstream_under_intervention(
        {"operation": "observe", "component": SUBJECT, "upstream": [{"component": "shared-database"}]}
    )


def test_an_intervention_that_records_no_severed_list_at_all_is_refused() -> None:
    body: dict[str, object] = {"operation": "intervene", "component": SUBJECT, "upstream": []}
    with pytest.raises(ArtefactError, match="records no severed edges"):
        refuse_upstream_under_intervention(body)


# -- rewind (build ticket 35) ---------------------------------------------------------------


BEFORE_RECALIBRATION = "2026-03-01T00:00:00+00:00"
AFTER_RECALIBRATION = "2026-09-01T00:00:00+00:00"


@pytest.fixture()
def recalibrated(tmp_path: Path) -> Path:
    """A pocket org whose shared elasticity was widened, in a dated commit."""
    root = fixtures.build_pocket_org(tmp_path / "recalibrated")
    fixtures.recalibrate_the_shared_elasticity(root)
    return root


def _elasticity(repo: ModelRepo) -> dict[str, float]:
    edge = Overlay.load(repo, POCKET).edges["database-slows-orders"]
    return {k: float(v) for k, v in edge["elasticity"].items()}


def test_rewind_produces_a_model_state_rather_than_a_filtered_view(recalibrated: Path) -> None:
    """Abduction. The model as it was, loaded from the commit that was current then.

    The elasticity is the test, not the row count: a filtered view can hide what was added since,
    and it cannot restore a number that was later overwritten. Rewinding to before the
    recalibration must read the old triple, or a backtest through it would score the past using
    today's number and call the result honest.
    """
    assert _elasticity(ModelRepo.open(recalibrated))["max"] == 0.9

    past = rewind(recalibrated, BEFORE_RECALIBRATION)
    assert _elasticity(past)["max"] == 0.7, "rewind returned today's number, so it is a filtered view"
    assert _elasticity(rewind(recalibrated, AFTER_RECALIBRATION))["max"] == 0.9

    # A model state, not a projection: it loads, validates and builds a graph like any other.
    graph = Overlay.load(past, POCKET).graph()
    assert graph.rollups()["causal_edges"] == 4


def test_rewind_composes_with_intervention_without_special_casing(recalibrated: Path) -> None:
    """`do()` at a past time is `do()` against a repository that happens to be open at a commit.

    Nothing in the intervention path knows it is looking at the past, which is what makes this a
    composition of two primitives rather than a third feature.
    """
    past = Overlay.load(rewind(recalibrated, BEFORE_RECALIBRATION), POCKET).graph()
    now = Overlay.load(ModelRepo.open(recalibrated), POCKET).graph()

    for graph in (past, now):
        assert [e["edge"] for e in severed(graph, Do(SUBJECT))] == ["database-slows-orders"]
        assert [e["component"] for e in updated_beliefs(graph, Observe(SUBJECT))[0]] == ["shared-database"]
    # And the composition carries the past model's numbers, not today's — which is the whole
    # reason rewind returns a state rather than a view.
    cut_then = next(e for e in severed(past, Do(SUBJECT)))
    assert cut_then["evidence_grade"] == 3


def test_rewinding_before_the_model_existed_fails_explicitly(pocket_repo: Path) -> None:
    """An empty model is a claim about the organisation, not an answer about the model."""
    with pytest.raises(PrimitiveError, match="did not exist yet"):
        rewind(pocket_repo, "1999-01-01T00:00:00+00:00")


def test_rewind_needs_a_time_and_a_repository(tmp_path: Path, pocket_repo: Path) -> None:
    with pytest.raises(PrimitiveError, match="not a rewind"):
        rewind(pocket_repo, "   ")
    with pytest.raises(PrimitiveError, match="no model repository"):
        rewind(tmp_path / "nowhere", "2026-01-01")


@pytest.mark.parametrize("stamp", ["1968-06-01", "1900-01-01T00:00:00+00:00", "2100-01-01", "3000-06-01"])
def test_a_year_git_cannot_represent_is_refused(recalibrated: Path, stamp: str) -> None:
    """`fromisoformat` accepts these and git does not, which is the dangerous combination.

    Outside roughly 1970-2099 git falls back to `now` and returns the newest commit, so the
    answer would be today's model wearing a date from another century. Parsing successfully is
    therefore not enough: the year has to be one git can compare against.
    """
    with pytest.raises(PrimitiveError, match="git can represent"):
        rewind(recalibrated, stamp)


@pytest.mark.parametrize("stamp", ["not-a-date", "yesterday", "2026-13-45", "last tuesday", "--output=x"])
def test_a_time_git_would_read_as_now_is_refused(recalibrated: Path, stamp: str) -> None:
    """The bug this guard exists for, not a tidiness check.

    `git rev-list --before=not-a-date` exits 0 and returns HEAD. Without this refusal a typo
    would answer a question about the past with today's model, silently — the artefact would
    record the typo as `rewound_to` and the newest commit as what it resolved to.
    """
    with pytest.raises(PrimitiveError, match="ISO 8601"):
        rewind(recalibrated, stamp)
    # And the reason it matters, made concrete: the newest commit is what would have come back.
    assert _elasticity(rewind(recalibrated, AFTER_RECALIBRATION))["max"] == 0.9


def test_a_time_with_no_offset_is_read_as_utc_rather_than_as_the_machine_clock(
    recalibrated: Path,
) -> None:
    """Otherwise the same command rewinds to different commits in different timezones.

    Asserted against a commit **half an hour** either side of the probe rather than two months,
    so an offset of one hour changes the answer. The earlier version used a probe two months from
    any commit, where every plausible misreading landed on the same side and the assertion held
    whatever the code did.

    Machine-independent by construction: it compares a naive time against the same instant
    written with explicit offsets, so it means the same thing on a UTC runner and on a machine an
    hour ahead.

    It asserts the **behaviour**, not one mechanism. Two things deliver it — `_env()` pins
    `TZ=UTC` for the git call, and `parse_moment` stamps the offset — so deleting either alone
    leaves this green. That is honest rather than weak: the guarantee is what callers depend on,
    and it is the guarantee that is asserted.
    """
    # The recalibration commit is at 00:30 UTC. A naive `2026-06-01` is 00:00 UTC, before it.
    assert _elasticity(rewind(recalibrated, "2026-06-01"))["max"] == 0.7
    assert _elasticity(rewind(recalibrated, "2026-06-01T00:00:00+00:00"))["max"] == 0.7
    # Same wall-clock reading an hour behind UTC is 01:00 UTC, after it. If a naive time were
    # read against anything but UTC, the first assertion above would land here instead.
    assert _elasticity(rewind(recalibrated, "2026-06-01T00:00:00-01:00"))["max"] == 0.9
