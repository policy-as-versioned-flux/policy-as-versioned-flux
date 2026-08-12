"""The refusals — every place the system declines rather than accommodates.

These exist because a mutation review found each of them could be deleted with the whole suite
still green. A refusal nothing asserts is a refusal that will be removed by the next person who
finds it inconvenient, and it will not show up in a diff as a loss.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from twin import fixtures, index, verbs
from twin.cli import main
from twin.index import IndexError_
from twin.model import DirectionError, ModelError, Overlay
from twin.repo import ModelRepo, RepoError
from twin.schema import SchemaError
from twin.verbs import VerbError


def _commit(root: Path, message: str) -> None:
    fixtures.git(root, "add", "-A")
    fixtures.git(root, "commit", "-q", "-m", message)


def _rewrite(root: Path, rel: str, content: str, message: str) -> None:
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    _commit(root, message)


# -- the binding seam ------------------------------------------------------------------------


@pytest.mark.parametrize("grade", [1, 3, 4])
def test_a_binding_claim_below_grade_five_is_refused(scratch_repo: Path, caps, grade: int) -> None:
    """Skills sit upstream of this seam. A claim that is not grade 5 did not come from one."""
    _rewrite(
        scratch_repo,
        "orgs/netflix/claims/bind-price-separation-to-dvd-by-mail.yaml",
        "id: bind-price-separation-to-dvd-by-mail\nkind: binding\n"
        f"signal: price-separation-announced\ncomponent: dvd-by-mail\nevidence_grade: {grade}\n"
        "claimed_by: someone\nevidence: a hunch\nconfidence: 0.9\n",
        "downgrade the binding claim",
    )
    with pytest.raises(VerbError, match="grade 5 by construction"):
        verbs.sense(ModelRepo.open(scratch_repo), caps, "netflix", "price-separation-announced", ["twin"])


# -- the signal schema -----------------------------------------------------------------------


UNDATED = "id: price-separation-announced\nsteep: economic\nsource: s\nstatement: t\nprovenance:\n  observed_by: x\n"
BAD_STEEP = (
    "id: price-separation-announced\ndate: '2011-07-12'\nsteep: vibes\nsource: s\n"
    "statement: t\nprovenance:\n  observed_by: x\n"
)
NO_PROVENANCE = (
    "id: price-separation-announced\ndate: '2011-07-12'\nsteep: economic\nsource: s\nstatement: t\n"
)


@pytest.mark.parametrize(
    ("content", "complaint"),
    [(UNDATED, "date"), (BAD_STEEP, "steep"), (NO_PROVENANCE, "provenance")],
)
def test_a_signal_missing_its_schema_is_refused(
    scratch_repo: Path, caps, content: str, complaint: str
) -> None:
    """Refused at load by the closed schema, not later by the verb — one home for the rule."""
    _rewrite(scratch_repo, "orgs/netflix/signals/price-separation-announced.yaml", content, "degrade the signal")
    with pytest.raises(SchemaError, match=complaint):
        verbs.sense(ModelRepo.open(scratch_repo), caps, "netflix", "price-separation-announced", ["twin"])


def test_an_unquoted_date_is_accepted_and_normalised(scratch_repo: Path, caps) -> None:
    """PyYAML types an unquoted date; whether an author quoted it must not decide the outcome."""
    _rewrite(
        scratch_repo,
        "orgs/netflix/signals/price-separation-announced.yaml",
        "id: price-separation-announced\ndate: 2011-07-12\nsteep: economic\nsource: s\n"
        "statement: t\nprovenance:\n  observed_by: x\n",
        "unquote the date",
    )
    artefact = verbs.sense(
        ModelRepo.open(scratch_repo), caps, "netflix", "price-separation-announced", ["twin"]
    )
    assert json.loads(artefact.to_bytes())["body"]["signal"]["date"] == "2011-07-12"


# -- the direction rule ----------------------------------------------------------------------


LEAK_AS_KEY = "id: leak\nname: Leak\nkind: activity\nadoption:\n  netflix: 0.8\n"
LEAK_IN_PROSE = "id: leak\nname: Leak\nkind: activity\nnote: Built originally for the netflix overlay.\n"
LEAK_AS_PATH = "id: leak\nname: Leak\nkind: activity\nsource: ../orgs/netflix/components/dvd-by-mail.yaml\n"


@pytest.mark.parametrize(
    ("content", "rel"),
    [
        (LEAK_AS_KEY, "world/components/leak.yaml"),
        (LEAK_IN_PROSE, "world/components/leak.yaml"),
        (LEAK_AS_PATH, "world/components/leak.yaml"),
        ("see orgs/netflix/components/dvd-by-mail.yaml\n", "world/notes.md"),
    ],
    ids=["mapping-key", "prose", "relative-path", "non-yaml-file"],
)
def test_the_world_layer_cannot_reference_an_overlay_any_of_these_ways(
    scratch_repo: Path, content: str, rel: str
) -> None:
    _rewrite(scratch_repo, rel, content, "plant a leak")
    with pytest.raises(DirectionError):
        Overlay.load(ModelRepo.open(scratch_repo), "netflix")


def test_the_direction_rule_is_enforced_on_load_not_only_in_the_suite(scratch_repo: Path, tmp_path: Path) -> None:
    """A rule that holds for the fixture and not for your repository is a property of the fixture."""
    _rewrite(scratch_repo, "world/components/leak.yaml", LEAK_IN_PROSE, "plant a leak")
    assert main(["run", "--repo", str(scratch_repo), "--org", "netflix", "--regime", "as-consumed", "--scenario",
                 "dvd-decline-2011", "--out", str(tmp_path / "nope.json")]) == 2
    assert not (tmp_path / "nope.json").exists()


def test_an_overlay_shadowing_a_world_component_does_not_red_light_everyone(scratch_repo: Path) -> None:
    """Shadowing is allowed. One tenant doing it must not fail the direction rule for all tenants."""
    _rewrite(
        scratch_repo,
        "orgs/netflix/components/cloud-compute.yaml",
        "id: cloud-compute\nname: Our own cloud compute\nkind: activity\nevolution: product\nvisibility: 0.5\n",
        "shadow a world component",
    )
    assert Overlay.load(ModelRepo.open(scratch_repo), "intel").org == "intel"


# -- pins that must not move -------------------------------------------------------------------


def test_an_overlay_may_not_pin_the_world_to_a_moving_ref(scratch_repo: Path) -> None:
    """A branch resolves to whatever it points at now, so identical pins would give different bytes."""
    _rewrite(
        scratch_repo,
        "orgs/netflix/meta.yaml",
        "id: netflix\nunit: overlay\norg: netflix\nworld_ref: main\n",
        "pin the world to a branch",
    )
    with pytest.raises(ModelError, match="not an object id"):
        Overlay.load(ModelRepo.open(scratch_repo), "netflix")


def test_a_ref_that_looks_like_a_git_option_is_refused(model_repo_dir: Path) -> None:
    """`git rev-parse` echoes an unrecognised dash-leading argument and exits 0."""
    with pytest.raises(RepoError):
        ModelRepo.open(model_repo_dir, ref="--output=/tmp/twin-should-not-exist")
    assert not Path("/tmp/twin-should-not-exist^{commit}").exists()


def test_a_typo_in_a_ref_fails_rather_than_producing_a_garbage_pin(model_repo_dir: Path) -> None:
    with pytest.raises(RepoError):
        ModelRepo.open(model_repo_dir, ref="HEAD~99")


# -- hostile model repositories ------------------------------------------------------------------


def test_a_yaml_alias_is_refused(scratch_repo: Path) -> None:
    """PyYAML shares alias objects, so nested anchors expand to gigabytes at serialisation."""
    _rewrite(
        scratch_repo,
        "orgs/netflix/signals/price-separation-announced.yaml",
        "id: price-separation-announced\ndate: '2011-07-12'\nsteep: economic\nsource: s\n"
        "statement: t\nprovenance: &p\n  observed_by: x\n  again: *p\n",
        "plant an alias",
    )
    with pytest.raises(RepoError, match="alias"):
        Overlay.load(ModelRepo.open(scratch_repo), "netflix")


def test_malformed_yaml_is_a_refusal_not_a_traceback(scratch_repo: Path, tmp_path: Path) -> None:
    _rewrite(scratch_repo, "world/components/broken.yaml", "id: [unclosed\n", "break a file")
    assert main(["index", "--repo", str(scratch_repo), "--out", str(tmp_path / "idx")]) == 2


def test_a_submodule_under_the_model_root_is_refused(scratch_repo: Path, tmp_path: Path) -> None:
    """`ls-tree -r` does not descend into a gitlink, so the world would load as empty."""
    inner = fixtures.build(tmp_path / "inner")
    fixtures.git(scratch_repo, "-c", "protocol.file.allow=always", "submodule", "add", "-q", str(inner), "vendor")
    _commit(scratch_repo, "add a submodule")
    with pytest.raises(RepoError, match="submodule"):
        ModelRepo.open(scratch_repo)


# -- destructive output paths ----------------------------------------------------------------------


def test_the_index_refuses_to_delete_a_directory_it_did_not_write(repo: ModelRepo, tmp_path: Path) -> None:
    precious = tmp_path / "notes"
    precious.mkdir()
    (precious / "thesis.txt").write_text("years of work", encoding="utf-8")

    with pytest.raises(IndexError_, match="refusing to delete"):
        index.write(repo, precious)
    assert (precious / "thesis.txt").read_text(encoding="utf-8") == "years of work"


def test_the_index_replaces_one_it_did_write(repo: ModelRepo, tmp_path: Path) -> None:
    out = tmp_path / "idx"
    index.write(repo, out)
    first = index.read_digest(out)
    (out / "stale.json").write_text("{}", encoding="utf-8")
    index.write(repo, out)
    assert index.read_digest(out) == first, "a stale file from an earlier build does not survive"


# -- what the review round found ---------------------------------------------------------------


ARTICLE_NINE_VALUES = [
    ("cohort", "staff-on-long-term-sickness"),
    ("cohort", "trade-union-members"),
    ("metric", "health-status"),
    ("metric", "religion"),
]


@pytest.mark.parametrize(("field", "value"), ARTICLE_NINE_VALUES)
def test_article_nine_data_is_refused_as_a_value_not_only_as_a_field_name(
    scratch_repo: Path, field: str, value: str
) -> None:
    """A cohort named for a protected group is an Article 9 record however tidy the field is."""
    from twin.model import BehaviouralOverlay
    from twin.schema import SpecialCategoryError

    doc = {"id": "planted", "cohort": "a-cohort", "metric": "a-metric", "value": 0.5,
           "observed_on": "2024-01-01", field: value}
    _rewrite(
        scratch_repo,
        "orgs/netflix/behavioural/observations/planted.yaml",
        "".join(f"{k}: {v!r}\n" for k, v in doc.items()),
        "plant Article 9 data as a value",
    )
    with pytest.raises(SpecialCategoryError, match="Article 9"):
        BehaviouralOverlay.load(ModelRepo.open(scratch_repo), "netflix")


def test_a_tenant_named_in_world_prose_is_caught_whatever_the_case(scratch_repo: Path) -> None:
    from twin.model import DirectionError

    _rewrite(scratch_repo, "world/components/leak.yaml",
             "id: leak\nname: Leak\nkind: activity\ndescription: Built for Netflix specifically.\n",
             "name a tenant in prose, capitalised")
    with pytest.raises(DirectionError):
        Overlay.load(ModelRepo.open(scratch_repo), "netflix")


def test_a_bundle_from_another_tenant_cannot_be_scored(model_repo_dir: Path, tmp_path: Path, caps) -> None:
    """Propositions live in the shared world layer, so a proposition match is not a tenancy check."""
    repo = ModelRepo.open(model_repo_dir)
    intel = verbs.run(repo, caps, "intel", "euv-slip-2026", "as-consumed",
                      verbs.command_for("run", org="intel", scenario="euv-slip-2026", regime="as-consumed"))
    path = intel.write(tmp_path / "intel-bundle.json")

    with pytest.raises(VerbError, match="never crosses a tenant boundary"):
        verbs.score(repo, caps, "netflix", path, "dvd-decline-2011-resolved", ["twin", "score"])


def test_an_untagged_forecast_does_not_score(model_repo_dir: Path, tmp_path: Path, caps) -> None:
    """Defaulting an absent regime to the one value that scores would let the tag be *deleted*."""
    from twin.canon import canonical_json

    repo = ModelRepo.open(model_repo_dir)
    bundle = verbs.run(repo, caps, "netflix", "dvd-decline-2011", "as-consumed",
                       verbs.command_for("run", org="netflix", scenario="dvd-decline-2011", regime="as-consumed"))
    doc = json.loads(bundle.to_bytes())
    for forecast in doc["body"]["forecasts"]:
        del forecast["regime"]
    path = tmp_path / "untagged.json"
    path.write_bytes(canonical_json(doc))

    card = json.loads(verbs.score(repo, caps, "netflix", path, "dvd-decline-2011-resolved", ["twin", "score"]).to_bytes())
    assert card["body"]["scores"] == []
    assert {u["reason"] for u in card["body"]["unscoreable"]} == {"regime-untagged"}


def test_an_execution_that_declares_itself_ineligible_does_not_score(
    model_repo_dir: Path, tmp_path: Path, caps
) -> None:
    """The bundle's own declaration is read back, not just the per-forecast tag."""
    from twin.canon import canonical_json

    repo = ModelRepo.open(model_repo_dir)
    bundle = verbs.run(repo, caps, "netflix", "dvd-decline-2011", "as-consumed",
                       verbs.command_for("run", org="netflix", scenario="dvd-decline-2011", regime="as-consumed"))
    doc = json.loads(bundle.to_bytes())
    doc["body"]["regime"] = {**doc["body"]["regime"], "declared": "with-hindsight", "scoring_eligible": False}
    path = tmp_path / "ineligible.json"
    path.write_bytes(canonical_json(doc))

    card = json.loads(verbs.score(repo, caps, "netflix", path, "dvd-decline-2011-resolved", ["twin", "score"]).to_bytes())
    assert card["body"]["scores"] == []
    assert {u["reason"] for u in card["body"]["unscoreable"]} == {"regime-disagrees-with-execution"}


def test_a_forecast_with_no_resolvable_outcome_is_unscoreable_and_never_a_zero(
    model_repo_dir: Path, tmp_path: Path, caps
) -> None:
    """A forecast nobody can resolve is not a bad forecast, so it must never carry a number."""
    from twin.canon import canonical_json, walk_values

    repo = ModelRepo.open(model_repo_dir)
    bundle = verbs.run(repo, caps, "netflix", "dvd-decline-2011", "as-consumed",
                       verbs.command_for("run", org="netflix", scenario="dvd-decline-2011", regime="as-consumed"))
    doc = json.loads(bundle.to_bytes())
    for forecast in doc["body"]["forecasts"]:
        forecast["proposition"] = "euv-tool-deliveries-slip-past-2026"
    path = tmp_path / "unresolvable.json"
    path.write_bytes(canonical_json(doc))

    card = json.loads(verbs.score(repo, caps, "netflix", path, "dvd-decline-2011-resolved", ["twin", "score"]).to_bytes())
    assert card["body"]["scores"] == []
    assert {u["reason"] for u in card["body"]["unscoreable"]} == {"no-resolvable-outcome"}
    numbers = [v for _, v in walk_values(card["body"]["unscoreable"]) if isinstance(v, (int, float)) and not isinstance(v, bool)]
    assert numbers == [], f"an unscoreable forecast carried a number: {numbers}"
