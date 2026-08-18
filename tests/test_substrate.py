"""The substrate recipe format, seeded regeneration, and the authored-or-derived spike
(build ticket 48).
"""

from __future__ import annotations

from pathlib import Path

import pytest

from twin import attest, cli, fixtures, sign, verbs
from twin.artefact import AUTHORED, DERIVED, Artefact
from twin.attest import AttestationError
from twin.blob import BlobRef
from twin.grades import Capabilities
from twin.reproduce import reproduce
from twin.repo import ModelRepo
from twin.substrate import (
    RECIPE_SCHEMA,
    SubstrateRecipe,
    SubstrateRecipeError,
    generate_deterministic,
    generate_non_reproducible,
)

_TEMPLATES = (
    "Lunch order chat in #ops.",
    "A long thread about the staging environment.",
    "Expense report chasing.",
    "Sprint planning grumbling.",
)


def _recipe(**overrides: object) -> SubstrateRecipe:
    base: dict[str, object] = {
        "id": "toy-recipe",
        "seed": 7,
        "templates": _TEMPLATES,
        "model_version": "toy-model-v1",
    }
    return SubstrateRecipe(**{**base, **overrides})  # type: ignore[arg-type]


# -- the recipe format ------------------------------------------------------------------------


def test_the_recipe_format_is_versioned_and_round_trips() -> None:
    recipe = _recipe()
    text = recipe.to_yaml()
    assert RECIPE_SCHEMA in text
    assert SubstrateRecipe.from_yaml(text) == recipe


def test_a_recipe_with_the_wrong_schema_is_refused() -> None:
    with pytest.raises(SubstrateRecipeError, match="not a"):
        SubstrateRecipe.from_yaml("schema: not-a-recipe/v1\nid: x\n")


def test_a_recipe_with_no_templates_is_refused() -> None:
    with pytest.raises(SubstrateRecipeError, match="no templates"):
        SubstrateRecipe.from_yaml(
            f"schema: {RECIPE_SCHEMA}\nid: x\nseed: 1\ntemplates: []\nmodel_version: v1\n"
        )


# -- recipe + seed regenerates a toy substrate --------------------------------------------------


def test_recipe_and_seed_regenerate_the_identical_toy_substrate() -> None:
    recipe = _recipe()
    first = generate_deterministic(recipe)
    second = generate_deterministic(recipe)
    assert first == second
    assert len(first) > 0


def test_a_different_seed_regenerates_different_substrate() -> None:
    a = generate_deterministic(_recipe(seed=7))
    b = generate_deterministic(_recipe(seed=8))
    assert a != b


# -- the content-hash exception, exercised for real ---------------------------------------------


def test_the_content_hash_reference_is_exercised_for_real(scratch_repo: Path) -> None:
    """Build ticket 01 built the reference form and exercised it against nothing (`ABSENT_SUBSTRATE`,
    the empty blob's hash). This is the same mechanism, exercised against real, non-empty bytes
    generated from a recipe, carried through the exact pipeline (`twin sense`) ticket 01 built the
    hook for.
    """
    recipe = _recipe()
    payload = generate_deterministic(recipe)
    ref = BlobRef.of(payload)
    assert ref.size > 0
    assert str(ref) != fixtures.ABSENT_SUBSTRATE

    (scratch_repo / "orgs" / "intel" / "signals" / "toy-substrate-signal.yaml").write_text(
        f"""\
id: toy-substrate-signal
date: '2024-08-02'
steep: economic
source: toy substrate spike
statement: A planted signal inside the toy substrate.
substrate: {ref}
provenance:
  observed_by: fixture
  url: https://example.invalid/fixture/toy-substrate
""",
        encoding="utf-8",
    )
    (scratch_repo / "orgs" / "intel" / "claims" / "bind-toy-substrate-signal.yaml").write_text(
        """\
id: bind-toy-substrate-signal
kind: binding
signal: toy-substrate-signal
component: foundry-services
evidence_grade: 5
claimed_by: fixture-author (human)
evidence: Reading of the toy substrate.
""",
        encoding="utf-8",
    )
    fixtures.git(scratch_repo, "add", "-A")
    fixtures.git(scratch_repo, "commit", "-q", "-m", "toy substrate signal")

    repo = ModelRepo.open(scratch_repo)
    caps = Capabilities.load()
    artefact = verbs.sense(
        repo, caps, "intel", "toy-substrate-signal",
        verbs.command_for("sense", org="intel", signal="toy-substrate-signal"),
    )
    pinned = artefact.pins["substrate"]
    assert BlobRef.parse(pinned) == ref
    assert ref.resolves(payload)


# -- the spike: authored, not derived ------------------------------------------------------------


def test_the_deterministic_generator_reproduces_from_the_identical_recipe() -> None:
    """What "derived" would require, if a generator could actually promise it."""
    recipe = _recipe()
    assert generate_deterministic(recipe) == generate_deterministic(recipe)


def test_the_stand_in_live_generator_does_not_reproduce_from_the_identical_recipe() -> None:
    """The tension ticket 48 names: a live model call cannot promise identical_pins_identical_bytes,
    even given the identical recipe on both calls. Demonstrated, not merely asserted in prose.
    """
    recipe = _recipe()
    first = generate_non_reproducible(recipe)
    second = generate_non_reproducible(recipe)
    assert first != second


def test_twin_verify_reproduces_a_substrate_referencing_artefact_without_regenerating_the_substrate(
    scratch_repo: Path, tmp_path: Path
) -> None:
    """The "twin verify attempt" the ticket asks for. A `sense` artefact pins a real substrate
    reference; `twin verify` recomputes the artefact from its pins and reproduces it cleanly —
    without ever calling a substrate generator, because `reproduce.replay`'s `sense` branch only
    re-reads the committed reference string. The reference participates in derivation; the bytes
    behind it never do — which is exactly why the bytes have to be captured once (authored) rather
    than regenerated on demand.
    """
    recipe = _recipe()
    payload = generate_deterministic(recipe)
    ref = BlobRef.of(payload)

    (scratch_repo / "orgs" / "intel" / "signals" / "toy-substrate-signal.yaml").write_text(
        f"""\
id: toy-substrate-signal
date: '2024-08-02'
steep: economic
source: toy substrate spike
statement: A planted signal inside the toy substrate.
substrate: {ref}
provenance:
  observed_by: fixture
  url: https://example.invalid/fixture/toy-substrate
""",
        encoding="utf-8",
    )
    (scratch_repo / "orgs" / "intel" / "claims" / "bind-toy-substrate-signal.yaml").write_text(
        """\
id: bind-toy-substrate-signal
kind: binding
signal: toy-substrate-signal
component: foundry-services
evidence_grade: 5
claimed_by: fixture-author (human)
evidence: Reading of the toy substrate.
""",
        encoding="utf-8",
    )
    fixtures.git(scratch_repo, "add", "-A")
    fixtures.git(scratch_repo, "commit", "-q", "-m", "toy substrate signal")

    out = tmp_path / "bound-signal.json"
    rc = cli.main(
        [
            "sense", "--repo", str(scratch_repo), "--org", "intel",
            "--signal", "toy-substrate-signal", "--out", str(out),
        ]
    )
    assert rc == 0

    # `payload` is never written anywhere `twin` can read it — only its hash is committed. If
    # reproduction needed the bytes, this would diverge or error; it does neither.
    report = reproduce(str(scratch_repo), str(out))
    assert report.reproduces, report.diff


def test_an_authored_substrate_artefact_accepts_a_human_signature() -> None:
    """The boundary the ticket asks for, made explicit: substrate content itself, marked
    `authored`, is exactly the shape a world-model or the constraint set already is — someone is
    accountable for admitting this particular generated batch as ground truth.
    """
    recipe = _recipe()
    payload = generate_deterministic(recipe)
    ref = BlobRef.of(payload)
    batch = Artefact(
        kind="substrate-batch", mark=AUTHORED, command=["twin", "substrate"],
        pins={"recipe_id": recipe.id, "recipe_seed": recipe.seed}, depth={},
        body={"substrate": str(ref)},
    )
    signature = sign.human("model-steward", batch.digest(), b"a-test-key")
    doc = attest.build(batch, [signature])
    assert attest.human_signed(doc)


def test_a_derived_artefact_referencing_substrate_still_refuses_a_human_signature() -> None:
    """`derived_never_human_signed` checked against this exact new boundary: an artefact that only
    *references* the substrate by content hash stays derived, unchanged from build ticket 01.
    """
    recipe = _recipe()
    ref = BlobRef.of(generate_deterministic(recipe))
    referencing = Artefact(
        kind="bound-signal", mark=DERIVED, command=["twin", "sense"],
        pins={"substrate": str(ref)}, depth={}, body={},
    )
    signature = sign.human("model-steward", referencing.digest(), b"a-test-key")
    with pytest.raises(AttestationError, match="derived_never_human_signed"):
        attest.build(referencing, [signature])


# -- the depth grade ------------------------------------------------------------------------------


def test_the_synthetic_substrate_capability_grade_is_computed() -> None:
    caps = Capabilities.load()
    graded = caps.require("synthetic-substrate")
    assert graded.owning_ticket == "12"
    # AC 5 was ticked here (build ticket 48); AC 1 joined it at build ticket 50
    # (twin/spine.py); the capability later reaches `full` at build ticket 87 — this test only
    # pins "AC 5 is ticked, and the grade is computed", not a snapshot grade that later work moves.
    checked = {c.index for c in graded.criteria if c.checked}
    assert {5} <= checked
