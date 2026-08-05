"""The model repository, the artefact envelope and the substrate reference form (build ticket 01)."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest

from twin import attest, fixtures
from twin.artefact import DERIVED, Artefact, ArtefactError, refuse_forbidden_keys
from twin.attest import AttestationError
from twin.blob import BlobRef, BlobRefError
from twin.canon import canonical_json
from twin.repo import DirtyTreeError, ModelRepo, RepoError


# -- the substrate reference form ------------------------------------------------------------


def test_a_substrate_reference_round_trips_with_no_substrate_present() -> None:
    ref = BlobRef.of(b"a bundle of synthetic chatter")
    assert BlobRef.parse(str(ref)) == ref
    assert str(BlobRef.parse(fixtures.ABSENT_SUBSTRATE)) == fixtures.ABSENT_SUBSTRATE


def test_a_substrate_reference_survives_the_artefact_envelope(model_repo_dir: Path, tmp_path: Path) -> None:
    from twin.cli import main
    import json

    out = tmp_path / "intel-signal.json"
    assert (
        main(
            [
                "sense",
                "--repo",
                str(model_repo_dir),
                "--org",
                "intel",
                "--signal",
                "foundry-segment-loss-disclosed",
                "--out",
                str(out),
            ]
        )
        == 0
    )
    pinned = json.loads(out.read_bytes())["envelope"]["pins"]["substrate"]
    assert BlobRef.parse(pinned).digest == BlobRef.parse(fixtures.ABSENT_SUBSTRATE).digest


def test_a_malformed_substrate_reference_is_refused() -> None:
    for bad in ("sha256:short:0", "md5:" + "0" * 64 + ":1", "e3b0c442", "sha256:" + "0" * 64):
        with pytest.raises(BlobRefError, match="not a substrate reference"):
            BlobRef.parse(bad)


def test_a_substrate_reference_only_resolves_against_its_own_bytes() -> None:
    ref = BlobRef.of(b"exactly this")
    assert ref.resolves(b"exactly this")
    assert not ref.resolves(b"exactly this ")


# -- pins ------------------------------------------------------------------------------------


def test_a_pin_names_the_commit_and_the_content(repo: ModelRepo) -> None:
    assert len(repo.pin.commit) == 40 and len(repo.pin.tree) == 40
    assert repo.pin.committed.startswith("2026-01-01"), "the commit date, not the wall clock"


def test_the_fixture_repository_is_reproducible_byte_for_byte(tmp_path: Path) -> None:
    """Same content, same commit sha — what makes a committed golden digest mean anything."""
    one = ModelRepo.open(fixtures.build(tmp_path / "one"))
    two = ModelRepo.open(fixtures.build(tmp_path / "two"))
    assert one.pin.commit == two.pin.commit
    assert one.pin.tree == two.pin.tree


def test_a_dirty_tree_is_refused(scratch_repo: Path) -> None:
    (scratch_repo / "world" / "meta.yaml").write_text("scribbled\n", encoding="utf-8")
    with pytest.raises(DirtyTreeError, match="uncommitted changes"):
        ModelRepo.open(scratch_repo)


def test_a_missing_ref_is_refused(model_repo_dir: Path) -> None:
    # Not a bare RepoError: DirtyTreeError subclasses it, so a dirty fixture would satisfy that.
    with pytest.raises(RepoError, match="rev-parse") as caught:
        ModelRepo.open(model_repo_dir, ref="no-such-ref")
    assert not isinstance(caught.value, DirtyTreeError)


def test_reads_come_from_the_ref_not_the_working_tree(scratch_repo: Path) -> None:
    repo = ModelRepo.open(scratch_repo)
    before = repo.read("world/meta.yaml")
    (scratch_repo / "world" / "meta.yaml").write_text("scribbled\n", encoding="utf-8")
    assert repo.read("world/meta.yaml") == before


# -- the envelope ------------------------------------------------------------------------------


def _artefact(**overrides: Any) -> Artefact:
    base: dict[str, Any] = {
        "kind": "probe",
        "mark": DERIVED,
        "command": ["twin", "probe"],
        "pins": {},
        "depth": {},
        "body": {},
    }
    return Artefact(**{**base, **overrides})


def test_an_unmarked_artefact_will_not_serialise() -> None:
    with pytest.raises(ArtefactError, match="mark"):
        _artefact(mark="").to_bytes()
    with pytest.raises(ArtefactError, match="mark"):
        _artefact(mark="probably-derived").to_bytes()


def test_a_recommended_action_field_is_refused_at_emission() -> None:
    with pytest.raises(ArtefactError, match="no_recommended_action_field"):
        _artefact(body={"recommended_action": "restructure"}).to_bytes()
    with pytest.raises(ArtefactError, match="no_collapse_mechanism"):
        _artefact(body={"forecasts": [{"consensus": 0.5}]}).to_bytes()


def test_the_refusal_reaches_arbitrary_depth() -> None:
    with pytest.raises(ArtefactError):
        refuse_forbidden_keys({"a": [{"b": {"c": [{"recommendation": "x"}]}}]})


@pytest.mark.parametrize("value", [float("nan"), float("inf"), float("-inf")])
def test_canonical_json_refuses_values_that_are_not_portable(value: float) -> None:
    # `match=` on purpose: json.dumps raises ValueError for unrelated reasons too, so a bare
    # raises() would not pin `allow_nan=False` specifically.
    with pytest.raises(ValueError, match="Out of range float"):
        canonical_json({"probability": value})
    assert canonical_json({"probability": 0.1}) == b'{\n  "probability": 0.1\n}\n'


def test_canonical_json_is_stable_under_key_order() -> None:
    assert canonical_json({"b": 1, "a": 2}) == canonical_json({"a": 2, "b": 1})


# -- attestation --------------------------------------------------------------------------------


def test_a_derived_artefact_refuses_a_human_signature() -> None:
    signature = {"identity": "someone@example.invalid"}
    with pytest.raises(AttestationError, match="derived_never_human_signed"):
        attest.build(_artefact(), [signature])


def test_an_authored_artefact_carries_the_signature_that_gives_it_accountability() -> None:
    doc = attest.build(_artefact(mark="authored"), [{"identity": "someone@example.invalid"}])
    assert attest.human_signed(doc)


def test_a_machine_attestation_asserts_the_absence_of_human_involvement() -> None:
    doc = attest.build(_artefact())
    assert doc["human_involvement"] == {"present": False, "signatures": []}
    assert doc["produced_by"]["runtime"]["machine"], "runtime facts belong here, not in the artefact"
