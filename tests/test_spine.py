"""Spine anchoring and free-running (build ticket 50): the substrate reconciles with the
immutable public spine at every dated checkpoint, and a diff against the spine does not locate
planted signals.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from twin import fixtures, regimes
from twin.grades import Capabilities
from twin.model import Overlay
from twin.repo import ModelRepo
from twin.spine import Spine, SpineError, SpineFact, anchor, diff_against_spine, reconcile, reconcile_at_every_checkpoint
from twin.substrate import SubstrateRecipe
from twin.substrate_generator import generate

_TEMPLATES = (
    "Lunch order chat in #ops.",
    "A long thread about the staging environment.",
    "Expense report chasing.",
    "Sprint planning grumbling.",
)


def _recipe(**overrides: object) -> SubstrateRecipe:
    base: dict[str, object] = {
        "id": "spine-test-recipe", "seed": 7, "templates": _TEMPLATES, "model_version": "toy-model-v1",
    }
    return SubstrateRecipe(**{**base, **overrides})  # type: ignore[arg-type]


def _fact(fact_id: str, date: str, statement: str = "", source: str = "https://example.com/x") -> SpineFact:
    return SpineFact(id=fact_id, date=date, statement=statement or f"statement for {fact_id}", source=source)


@pytest.fixture(scope="session")
def carillion_repo_dir(tmp_path_factory: pytest.TempPathFactory) -> Path:
    return fixtures.build_carillion_org(tmp_path_factory.mktemp("spine-carillion") / "repo")


@pytest.fixture()
def carillion_overlay(carillion_repo_dir: Path) -> Overlay:
    return Overlay.load(ModelRepo.open(carillion_repo_dir), fixtures.CARILLION_ORG)


# -- the spine itself ----------------------------------------------------------------------------


def test_a_spine_with_no_facts_is_refused() -> None:
    with pytest.raises(SpineError, match="no facts"):
        Spine(facts=())


def test_a_spine_with_a_duplicate_fact_id_is_refused() -> None:
    with pytest.raises(SpineError, match="twice"):
        Spine(facts=(_fact("f1", "2017-01-01"), _fact("f1", "2017-06-01")))


def test_from_overlay_reads_the_orgs_own_real_signals(carillion_overlay: Overlay) -> None:
    """AC 1: the spine is not a separate authored format — it is the org's own dated signals."""
    spine = Spine.from_overlay(carillion_overlay)
    assert len(spine.facts) == 8 == len(carillion_overlay.signals)
    assert {f.id for f in spine.facts} == set(carillion_overlay.signals)
    for f in spine.facts:
        original = carillion_overlay.signals[f.id]
        assert f.date == original["date"]
        assert f.statement == original["statement"]
        assert f.source == original["source"]


# -- knowability dates reuse the regime gate, not a look-alike ------------------------------------


def test_at_filters_to_facts_knowable_on_or_before_the_checkpoint() -> None:
    spine = Spine(facts=(_fact("early", "2017-01-01"), _fact("late", "2017-12-01")))
    assert {f.id for f in spine.at("2017-06-01")} == {"early"}
    assert {f.id for f in spine.at("2017-12-01")} == {"early", "late"}
    assert {f.id for f in spine.at("2016-01-01")} == set()


def test_at_reuses_regimes_cutoff_rather_than_a_parallel_date_parser() -> None:
    """Not a look-alike error: the same exception type `regimes.py` raises for every other
    malformed execution date."""
    spine = Spine(facts=(_fact("f1", "2017-01-01"),))
    with pytest.raises(regimes.RegimeError):
        spine.at("2017-01-01T00:00:00Z")


# -- anchoring: additive, verbatim, does not touch what was already there ------------------------


def test_anchor_inserts_known_facts_verbatim_into_the_named_channel() -> None:
    batch = generate(_recipe())
    spine = Spine(facts=(_fact("f1", "2017-01-01", statement="a real dated fact"),))
    anchored_batch = anchor(batch, spine, checkpoint="2017-06-01")
    assert "a real dated fact" in anchored_batch["channels"]["events"]
    assert anchored_batch["anchored"] == [f.as_dict() for f in spine.facts]


def test_anchor_does_not_mutate_the_original_batch() -> None:
    batch = generate(_recipe())
    before = {c: list(lines) for c, lines in batch["channels"].items()}
    spine = Spine(facts=(_fact("f1", "2017-01-01", statement="a real dated fact"),))
    anchor(batch, spine, checkpoint="2017-06-01")
    assert batch["channels"] == before


def test_anchor_refuses_an_unknown_channel() -> None:
    batch = generate(_recipe())
    spine = Spine(facts=(_fact("f1", "2017-01-01"),))
    with pytest.raises(SpineError, match="no channel"):
        anchor(batch, spine, checkpoint="2017-06-01", channel="not-a-real-channel")


def test_anchoring_leaves_free_running_content_untouched() -> None:
    """Where the record is silent the substrate free-runs: anchoring a spine fact does not remove
    or alter any mundane line or planted signal already in the batch."""
    batch = generate(_recipe(planted_signals=("an invented, unattributed anomaly",)))
    spine = Spine(facts=(_fact("f1", "2017-01-01", statement="a real dated fact"),))
    anchored_batch = anchor(batch, spine, checkpoint="2017-06-01")
    for channel, lines in batch["channels"].items():
        for line in lines:
            assert line in anchored_batch["channels"][channel]


# -- reconciliation: checked, not assumed ----------------------------------------------------------


def test_reconcile_succeeds_once_the_batch_carries_every_known_fact() -> None:
    batch = generate(_recipe())
    spine = Spine(facts=(_fact("f1", "2017-01-01", statement="a real dated fact"),))
    anchored_batch = anchor(batch, spine, checkpoint="2017-06-01")
    report = reconcile(anchored_batch, spine, "2017-06-01")
    assert report["reconciled"] == ["f1"]


def test_reconcile_refuses_and_names_a_missing_fact() -> None:
    batch = generate(_recipe())
    spine = Spine(facts=(_fact("f1", "2017-01-01", statement="a real dated fact never inserted"),))
    with pytest.raises(SpineError, match="f1"):
        reconcile(batch, spine, "2017-06-01")


def test_reconcile_does_not_require_the_substrate_to_contain_only_spine_content() -> None:
    """Free-running: extra, un-anchored lines are not a reconciliation failure."""
    batch = generate(_recipe(planted_signals=("an invented anomaly",)))
    spine = Spine(facts=(_fact("f1", "2017-01-01", statement="a real dated fact"),))
    anchored_batch = anchor(batch, spine, checkpoint="2017-06-01")
    # plenty of mundane, un-anchored content survives in the batch alongside the one spine fact
    assert len(anchored_batch["channels"]["events"]) > 1
    reconcile(anchored_batch, spine, "2017-06-01")  # does not raise


def test_reconcile_at_every_checkpoint_runs_once_per_distinct_spine_date(carillion_overlay: Overlay) -> None:
    """AC: 'reconciles with the public spine at every dated checkpoint', not only the last one."""
    spine = Spine.from_overlay(carillion_overlay)
    batch = anchor(generate(_recipe()), spine, checkpoint="2018-01-15")
    reports = reconcile_at_every_checkpoint(batch, spine)
    dates = sorted({f.date for f in spine.facts})
    assert [r["checkpoint"] for r in reports] == dates
    counts = [len(r["reconciled"]) for r in reports]
    assert counts == sorted(counts)  # monotonically non-decreasing as the checkpoint advances
    assert counts[-1] == len(spine.facts)


def test_reconcile_at_every_checkpoint_fails_if_any_one_is_missing(carillion_overlay: Overlay) -> None:
    spine = Spine.from_overlay(carillion_overlay)
    # anchored only up to the sixth checkpoint, so the seventh and eighth are missing
    partial_checkpoint = sorted({f.date for f in spine.facts})[5]
    partial = Spine(facts=tuple(f for f in spine.facts if f.date <= partial_checkpoint))
    batch = anchor(generate(_recipe()), partial, checkpoint=partial_checkpoint)
    with pytest.raises(SpineError):
        reconcile_at_every_checkpoint(batch, spine)


# -- the diff attack: it does not locate the plant -------------------------------------------------


def test_the_diff_attack_does_not_locate_plants(carillion_overlay: Overlay) -> None:
    """Decision ticket 12 Q3: generate-everything-from-the-spine is 'actively dangerous' because a
    planted signal becomes the only thing not anchored to public record — trivially findable by
    diffing. This demonstrates the defence: the substrate free-runs in bulk, so the diff's
    free-running residual holds far more than just the plant.
    """
    recipe = _recipe(planted_signals=("a senior engineer's calendar clears for three unexplained days",))
    batch = generate(recipe)
    plant_line = f"[{batch['focus_entity']}] {batch['plants'][0]['signal']}"
    assert any(plant_line in lines for lines in batch["channels"].values())

    spine = Spine.from_overlay(carillion_overlay)
    anchored_batch = anchor(batch, spine, checkpoint="2018-01-15")
    diff = diff_against_spine(anchored_batch, spine)

    assert len(diff["anchored"]) == len(spine.facts) == 8
    assert plant_line in diff["free_running"]
    # the plant is not the unique unanchored residual: a wide margin of ordinary mundane content
    # sits in free_running beside it, so "everything not in the spine" does not single it out.
    decoys = len(diff["free_running"]) - 1
    assert decoys >= 20, f"only {decoys} non-plant decoy(s) in free_running — the diff attack would work"


def test_over_anchoring_would_have_made_the_plant_the_unique_residual() -> None:
    """The negative case, named directly: if a batch carried *only* the spine plus the plant (the
    'generate-everything-from-the-spine' failure decision ticket 12 Q3 forbids), the diff would
    isolate the plant with certainty. Demonstrated here to show the guard above is measuring a
    real property, not a vacuous one."""
    spine = Spine(facts=(_fact("f1", "2017-01-01", statement="a real dated fact"),))
    over_anchored_batch = {"channels": {"events": ["a real dated fact", "the one planted signal"]}}
    diff = diff_against_spine(over_anchored_batch, spine)
    assert diff["free_running"] == ["the one planted signal"], "an over-anchored batch trivially exposes the plant"


# -- the depth grade: this ticket ticks AC 1 -------------------------------------------------------


def test_the_synthetic_substrate_capability_grade_moves_to_2_of_7() -> None:
    """Build ticket 50 ticks decision ticket 12's AC 1 (the real/synthetic seam, with a
    consistency rule) — the same computed-checklist check `test_substrate_generator.py` already
    runs, re-run here to pin that this ticket moved it and did not move anything else.

    `{1, 5} <= checked`, not `==`: the same subset shape `test_substrate_generator.py`'s own pin
    uses, for the identical reason — asserting exact equality here would go stale the moment a
    later ticket ticks a further criterion, which is exactly what build ticket 51 does next (AC
    2). It is `tests/test_substrate_eval.py::test_the_synthetic_substrate_capability_grade_moves_to_3_of_7`
    that pins the post-51 state, and `test_the_synthetic_substrate_capability_reaches_full_at_build_ticket_87`
    that pins the fully-ticked state. The grade itself is not re-asserted here for the same reason.
    """
    caps = Capabilities.load()
    graded = caps.require("synthetic-substrate")
    assert graded.owning_ticket == "12"
    checked = {c.index for c in graded.criteria if c.checked}
    assert {1, 5} <= checked
