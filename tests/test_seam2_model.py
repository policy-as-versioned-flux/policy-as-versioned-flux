"""Seam 2 — the typed model API, below the CLI.

Justified because a structural defect and a loading defect are indistinguishable at seam 1: both
surface as "wrong artefact". Kept deliberately thin — assertions are on structural properties
(does an overlay stay pinned while the world moves; does one tenant stay invisible to another),
never on call sequences or object shapes.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from twin import fixtures
from twin.model import ModelError, Overlay, World, check_direction, orgs
from twin.repo import ModelRepo
from twin.schema import SchemaError


def test_world_and_overlays_are_separately_versioned_units(repo: ModelRepo) -> None:
    world = repo.unit_ref("world")
    netflix = repo.unit_ref("orgs/netflix")
    intel = repo.unit_ref("orgs/intel")

    assert world.commit != netflix.commit, "the world layer advanced on its own commit"
    assert netflix.tree != intel.tree, "two overlays are distinct content"
    assert netflix.commit == intel.commit, "these two happened to land together; the refs are still independent"


def test_an_overlay_stays_pinned_while_the_world_moves(scratch_repo: Path) -> None:
    before = Overlay.load(ModelRepo.open(scratch_repo), "netflix")
    fixtures.advance_world(scratch_repo)
    after = Overlay.load(ModelRepo.open(scratch_repo), "netflix")

    assert after.world.ref.tree == before.world.ref.tree, "the overlay resolves at its pinned world ref"
    assert "high-na-euv" not in after.world.components
    assert "high-na-euv" in World.load(ModelRepo.open(scratch_repo)).components, "the world did move"


def test_an_overlay_without_a_pinned_world_ref_will_not_load(scratch_repo: Path) -> None:
    """Refused by the meta schema now that meta files are validated, not later by the loader."""
    meta = scratch_repo / "orgs" / "netflix" / "meta.yaml"
    meta.write_text("id: netflix\nunit: overlay\norg: netflix\n", encoding="utf-8")
    fixtures.git(scratch_repo, "add", "-A")
    fixtures.git(scratch_repo, "commit", "-q", "-m", "drop the world pin")

    with pytest.raises((ModelError, SchemaError), match="world_ref"):
        Overlay.load(ModelRepo.open(scratch_repo), "netflix")


def test_a_meta_file_is_validated_like_everything_else(scratch_repo: Path) -> None:
    """The meta schemas existed with no call site, so Article 9 data could sit in one unread."""
    meta = scratch_repo / "orgs" / "netflix" / "meta.yaml"
    meta.write_text(meta.read_text(encoding="utf-8") + "health_status: mostly fine\n", encoding="utf-8")
    fixtures.git(scratch_repo, "add", "-A")
    fixtures.git(scratch_repo, "commit", "-q", "-m", "plant Article 9 data in the meta file")

    with pytest.raises(SchemaError, match="Article 9"):
        Overlay.load(ModelRepo.open(scratch_repo), "netflix")


def test_a_directory_nobody_loads_is_refused_rather_than_ignored(scratch_repo: Path) -> None:
    """Silently ignoring it would let an author think their file is in the model. It is not."""
    stray = scratch_repo / "orgs" / "netflix" / "assets"
    stray.mkdir()
    (stray / "a-database.yaml").write_text("id: a-database\n", encoding="utf-8")
    fixtures.git(scratch_repo, "add", "-A")
    fixtures.git(scratch_repo, "commit", "-q", "-m", "add a directory nothing reads")

    with pytest.raises(ModelError, match="nothing loads assets"):
        Overlay.load(ModelRepo.open(scratch_repo), "netflix")


def test_two_overlays_coexist_with_no_cross_visibility(repo: ModelRepo) -> None:
    assert orgs(repo) == ["intel", "netflix"]
    netflix = Overlay.load(repo, "netflix")
    intel = Overlay.load(repo, "intel")

    assert netflix.world.ref.tree == intel.world.ref.tree, "one shared world layer"
    for other in ("foundry-services", "intel-believed", "foundry-segment-loss-disclosed"):
        assert other not in netflix.components
        assert other not in netflix.world_models
        assert other not in netflix.signals
    with pytest.raises(ModelError, match="no component 'foundry-services'"):
        netflix.component("foundry-services")
    with pytest.raises(ModelError, match="no component 'dvd-by-mail'"):
        intel.component("dvd-by-mail")


def test_an_overlay_may_reference_the_world_layer(repo: ModelRepo) -> None:
    netflix = Overlay.load(repo, "netflix")
    assert netflix.component("content-delivery-network")["id"] == "content-delivery-network"
    assert netflix.components["streaming-experience"]["needs"] == [
        "content-delivery-network",
        "cloud-compute",
    ]


def test_the_world_layer_may_never_reference_an_overlay(repo: ModelRepo, tmp_path: Path) -> None:
    assert check_direction(repo) == []

    planted = fixtures.build(tmp_path / "planted")
    fixtures.plant_world_violation(planted)
    violations = check_direction(ModelRepo.open(planted))
    assert violations and "netflix" in violations[0]


def test_a_world_file_pointing_into_the_overlay_tree_is_caught(tmp_path: Path) -> None:
    planted = fixtures.build(tmp_path / "pointer")
    (planted / "world" / "components" / "pointer.yaml").write_text(
        "id: pointer\nname: Pointer\nsource: orgs/netflix/components/dvd-by-mail.yaml\n", encoding="utf-8"
    )
    fixtures.git(planted, "add", "-A")
    fixtures.git(planted, "commit", "-q", "-m", "point into the overlay tree")

    violations = check_direction(ModelRepo.open(planted))
    assert any("points into the overlay tree" in v for v in violations)


def test_a_dangling_dependency_is_refused_at_load(scratch_repo: Path) -> None:
    component = scratch_repo / "orgs" / "netflix" / "components" / "dvd-by-mail.yaml"
    component.write_text(
        "id: dvd-by-mail\nname: DVD by mail\nkind: activity\nevolution: commodity\n"
        "visibility: 0.85\nneeds:\n  - a-component-that-does-not-exist\n",
        encoding="utf-8",
    )
    fixtures.git(scratch_repo, "add", "-A")
    fixtures.git(scratch_repo, "commit", "-q", "-m", "dangle a dependency")

    with pytest.raises(ModelError, match="does not exist"):
        Overlay.load(ModelRepo.open(scratch_repo), "netflix")
