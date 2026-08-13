"""Retrospective sweep and lead-time-to-recognition (build ticket 55, decision ticket 11 Q3).

Build ticket 54 built retention (the unbound pool decays rather than discards); this is the other
half — a model change re-examines the pool and rebinds what has become interpretable. Assertions
are on the emitted `retrospective-sweep` artefact's body and on the pure `sweep()` function, not on
internals, the same discipline `tests/test_unbound_pool.py` already applies to its own module.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from twin import fixtures, retrospective_sweep, unbound_pool
from twin.artefact import DERIVED
from twin.cli import main
from twin.grades import Capabilities
from twin.model import Overlay
from twin.repo import ModelRepo

COMMAND = ["twin", "retrospective-sweep"]


def _add_signal(
    root: Path, org: str, ident: str, date: str,
    steep: str = "technological", source: str = "harness fixture",
    statement: str = "planted for a test, never bound to a component.",
) -> None:
    (root / "orgs" / org / "signals").mkdir(parents=True, exist_ok=True)
    (root / "orgs" / org / "signals" / f"{ident}.yaml").write_text(
        f"id: {ident}\n"
        f"date: '{date}'\n"
        f"steep: {steep}\n"
        f"source: {source}\n"
        f"statement: {statement}\n"
        "provenance:\n"
        "  observed_by: test\n",
        encoding="utf-8",
    )


def _add_component(root: Path, org: str, ident: str, name: str) -> None:
    (root / "orgs" / org / "components").mkdir(parents=True, exist_ok=True)
    (root / "orgs" / org / "components" / f"{ident}.yaml").write_text(
        f"id: {ident}\nname: {name}\nkind: capability\n", encoding="utf-8",
    )


def _commit(root: Path, message: str) -> None:
    fixtures.git(root, "add", "-A")
    fixtures.git(root, "commit", "-q", "-m", message)


# -- rebind: the score-gated attempt against the current candidate set -----------------------


def test_rebind_returns_none_when_no_candidate_shares_vocabulary(repo: ModelRepo) -> None:
    overlay = Overlay.load(repo, "netflix")
    entry = {"id": "x", "date": "2020-01-01", "age_days": 100, "weight": 0.5, "decayed": False}
    overlay.signals["x"] = {
        "id": "x", "date": "2020-01-01", "steep": "technological", "source": "nowhere",
        "statement": "zzyzx qwibbleflorp never seen anywhere else", "provenance": {},
    }
    candidates = retrospective_sweep.candidates_of(overlay)
    assert retrospective_sweep.rebind(overlay, entry, candidates) is None


def test_rebind_returns_a_grade_5_binding_when_a_candidate_shares_vocabulary(repo: ModelRepo) -> None:
    overlay = Overlay.load(repo, "netflix")
    entry = {"id": "x", "date": "2020-01-01", "age_days": 100, "weight": 0.5, "decayed": False}
    overlay.signals["x"] = {
        "id": "x", "date": "2020-01-01", "steep": "technological", "source": "streaming report",
        "statement": "a note about streaming experience quality", "provenance": {},
    }
    candidates = retrospective_sweep.candidates_of(overlay)
    result = retrospective_sweep.rebind(overlay, entry, candidates)
    assert result is not None
    assert result["claim"]["component"] == "streaming-experience"
    assert result["claim"]["evidence_grade"] == 5


# -- sweep: every unbound signal, re-examined against the current model ----------------------


def test_sweep_leaves_a_signal_unbound_when_nothing_in_the_graph_catches_it(scratch_repo: Path) -> None:
    _add_signal(scratch_repo, "netflix", "no-match-signal", "2020-01-01", statement="wibbleflorp zeptonium exotic matter")
    _commit(scratch_repo, "add an unbound signal with no matching component")
    overlay = Overlay.load(ModelRepo.open(scratch_repo), "netflix")

    result = retrospective_sweep.sweep(overlay, "2026-01-01")
    assert "no-match-signal" in {e["id"] for e in result["still_unbound"]}
    assert "no-match-signal" not in {e["id"] for e in result["rebound"]}


def test_sweep_rebinds_once_a_model_change_adds_a_matching_component(scratch_repo: Path) -> None:
    _add_signal(
        scratch_repo, "netflix", "zeptonium-signal", "2020-01-01",
        statement="an early note about zeptonium shielding for satellite relays",
        source="an obscure trade paper",
    )
    _commit(scratch_repo, "add a signal nothing yet binds to")
    before = Overlay.load(ModelRepo.open(scratch_repo), "netflix")
    before_result = retrospective_sweep.sweep(before, "2026-01-01")
    assert "zeptonium-signal" in {e["id"] for e in before_result["still_unbound"]}

    _add_component(scratch_repo, "netflix", "zeptonium-shielding", "Zeptonium shielding programme")
    _commit(scratch_repo, "model change: add zeptonium shielding as a tracked component")
    after = Overlay.load(ModelRepo.open(scratch_repo), "netflix")
    after_result = retrospective_sweep.sweep(after, "2026-01-01")

    rebound = {e["id"]: e for e in after_result["rebound"]}
    assert "zeptonium-signal" in rebound
    entry = rebound["zeptonium-signal"]
    assert entry["component"] == "zeptonium-shielding"
    assert entry["pool_entry_date"] == "2020-01-01"
    assert entry["binding_date"] == "2026-01-01"
    assert entry["lead_time_to_recognition_days"] == 2192  # 2020-01-01 -> 2026-01-01
    assert entry["evidence_grade"] == 5
    assert "zeptonium-signal" not in {e["id"] for e in after_result["still_unbound"]}


def test_rescue_does_not_require_the_signal_to_still_be_live(scratch_repo: Path) -> None:
    """Q3's whole point: decay must not block rescue, or the rule preferentially deletes the
    longest-lead-time signals it exists to catch."""
    _add_signal(
        scratch_repo, "netflix", "ancient-zeptonium-signal", "2000-01-01",
        statement="a decades-old zeptonium shielding observation",
    )
    _commit(scratch_repo, "add an ancient signal, then add its matching component")
    _add_component(scratch_repo, "netflix", "zeptonium-shielding", "Zeptonium shielding programme")
    _commit(scratch_repo, "model change: add zeptonium shielding as a tracked component")
    overlay = Overlay.load(ModelRepo.open(scratch_repo), "netflix")

    pool_before = {e["id"]: e for e in unbound_pool.pool(overlay, "2026-01-01")}
    assert pool_before["ancient-zeptonium-signal"]["decayed"] is True  # sanity: genuinely decayed

    result = retrospective_sweep.sweep(overlay, "2026-01-01")
    rebound = {e["id"]: e for e in result["rebound"]}
    assert "ancient-zeptonium-signal" in rebound
    assert rebound["ancient-zeptonium-signal"]["had_decayed_before_rescue"] is True


def test_sweep_never_considers_an_already_bound_signal(repo: ModelRepo) -> None:
    overlay = Overlay.load(repo, "netflix")
    result = retrospective_sweep.sweep(overlay, "2026-01-01")
    ids = {e["id"] for e in result["rebound"]} | {e["id"] for e in result["still_unbound"]}
    assert "price-separation-announced" not in ids  # the fixture's own bound signal


def test_sweep_with_no_candidates_leaves_everything_unbound(scratch_repo: Path) -> None:
    _add_signal(scratch_repo, "netflix", "orphan-signal", "2020-01-01")
    _commit(scratch_repo, "add an unbound signal")
    overlay = Overlay.load(ModelRepo.open(scratch_repo), "netflix")
    overlay.components.clear()
    overlay.world.components.clear()

    result = retrospective_sweep.sweep(overlay, "2026-01-01")
    assert not result["rebound"]
    assert "orphan-signal" in {e["id"] for e in result["still_unbound"]}


# -- lead-time-to-recognition: a first-class, reported metric --------------------------------


def test_lead_time_to_recognition_is_reported_per_rebound_signal(scratch_repo: Path) -> None:
    _add_signal(scratch_repo, "netflix", "zeptonium-signal", "2020-01-01", statement="zeptonium shielding note")
    _add_component(scratch_repo, "netflix", "zeptonium-shielding", "Zeptonium shielding programme")
    _commit(scratch_repo, "signal and matching component together")
    overlay = Overlay.load(ModelRepo.open(scratch_repo), "netflix")

    result = retrospective_sweep.sweep(overlay, "2026-01-01")
    summary = retrospective_sweep.lead_time_summary(result["rebound"])
    assert summary["unit"] == "days"
    assert summary["count"] == 1
    assert summary["min_days"] == summary["max_days"] == summary["mean_days"] == 2192
    assert summary["per_signal"] == [{"id": "zeptonium-signal", "days": 2192}]


def test_lead_time_summary_is_empty_but_present_with_no_rebound_signals() -> None:
    summary = retrospective_sweep.lead_time_summary([])
    assert summary["count"] == 0
    assert summary["min_days"] is None
    assert summary["max_days"] is None
    assert summary["mean_days"] is None
    assert summary["per_signal"] == []


# -- the emitted artefact ----------------------------------------------------------------------


def test_artefact_carries_pins_depth_and_a_derived_mark(repo: ModelRepo, caps: Capabilities) -> None:
    artefact = retrospective_sweep.retrospective_sweep_artefact(repo, caps, "netflix", "2026-01-01", COMMAND)
    assert artefact.kind == retrospective_sweep.KIND_RETROSPECTIVE_SWEEP
    assert artefact.mark == DERIVED  # nothing here could carry a human's accountability
    assert artefact.pins["at"] == "2026-01-01"
    assert artefact.pins["decay"]["version"] == 1
    assert artefact.depth["grade"] in ("stub", "partial", "full")
    artefact.digest()  # does not raise: no forbidden key crept into the body


def test_artefact_body_carries_rebound_still_unbound_and_lead_time(scratch_repo: Path, caps: Capabilities) -> None:
    _add_signal(scratch_repo, "netflix", "zeptonium-signal", "2020-01-01", statement="zeptonium shielding note")
    _add_component(scratch_repo, "netflix", "zeptonium-shielding", "Zeptonium shielding programme")
    _add_signal(scratch_repo, "netflix", "unmatched-signal", "2024-01-01", statement="qwibbleflorp exotic matter")
    _commit(scratch_repo, "one rebindable and one not")
    repo = ModelRepo.open(scratch_repo)

    artefact = retrospective_sweep.retrospective_sweep_artefact(repo, caps, "netflix", "2026-01-01", COMMAND)
    body = artefact.body
    assert {e["id"] for e in body["rebound"]} == {"zeptonium-signal"}
    assert "unmatched-signal" in {e["id"] for e in body["still_unbound"]}
    assert body["lead_time_to_recognition"]["count"] == 1
    assert body["counts"] == {"pool_size_examined": 2, "rebound": 1, "still_unbound": 1}


def test_artefact_is_reproducible_given_identical_pins(repo: ModelRepo, caps: Capabilities) -> None:
    first = retrospective_sweep.retrospective_sweep_artefact(repo, caps, "netflix", "2026-01-01", COMMAND)
    second = retrospective_sweep.retrospective_sweep_artefact(repo, caps, "netflix", "2026-01-01", COMMAND)
    assert first.digest() == second.digest()


# -- seam 1: the CLI verb --------------------------------------------------------------------


def test_the_cli_verb_emits_a_retrospective_sweep_artefact(model_repo_dir: Path, tmp_path: Path) -> None:
    out = tmp_path / "sweep.json"
    assert (
        main(
            [
                "retrospective-sweep", "--repo", str(model_repo_dir), "--org", "netflix",
                "--at", "2026-01-01", "--out", str(out),
            ]
        )
        == 0
    )
    doc = json.loads(out.read_bytes())
    assert doc["envelope"]["kind"] == "retrospective-sweep"
    assert doc["envelope"]["mark"] == "derived"
    assert doc["envelope"]["pins"]["at"] == "2026-01-01"
    assert "rebound" in doc["body"]
    assert "still_unbound" in doc["body"]
    assert "lead_time_to_recognition" in doc["body"]


# -- the worked case: the quantum/harvest-now-decrypt-later class, mechanised ------------------


def test_worked_case_a_multi_year_old_quantum_signal_is_rescued_by_a_new_crypto_dependency(
    tmp_path: Path,
) -> None:
    """Decision ticket 11 Q3's own example, made real: "add 'our authentication depends on this
    cryptographic primitive' and the sweep re-examines every unbound signal against the new
    structure — surfacing a paper from three years ago that now clearly bears on you." A
    materials-science signal about a lattice-based cryptanalysis advance, dated against the
    standing library's own `quantum-hndl` scenario class (`twin/fixtures.py`'s `LIBRARY_ORG`,
    build ticket 69), sits unbound and decays for years until a new component names exactly the
    dependency it bears on.
    """
    # Vocabulary is deliberately clear of the library world's own ten components (cryptographic
    # -key-material's own "key" among them) — the point of the "before" leg is that *nothing yet
    # in the graph* bears on this signal, not an accidental word collision with an unrelated one.
    root = fixtures.build_library_org(tmp_path / "quantum-worked-case")
    _add_signal(
        root, fixtures.LIBRARY_ORG, "materials-paper-lattice-surprise", "2023-11-02",
        source="materials-science preprint, arXiv, 2023-11-02",
        statement=(
            "A physics preprint demonstrates a lattice-based cryptanalysis technique against a "
            "widely used asymmetric encryption scheme, shortening harvest-now-decrypt-later "
            "exposure windows for previously captured ciphertext."
        ),
    )
    _commit(root, "a materials-science signal, unbound at ingestion")

    # Before the model change, nothing in the library world's own component set names the
    # dependency this paper bears on.
    before_overlay = Overlay.load(ModelRepo.open(root), fixtures.LIBRARY_ORG)
    before = retrospective_sweep.sweep(before_overlay, "2026-08-10")
    assert "materials-paper-lattice-surprise" in {e["id"] for e in before["still_unbound"]}
    assert not before["rebound"]

    # The model change: "our authentication depends on this cryptographic primitive."
    _add_component(
        root, fixtures.LIBRARY_ORG, "lattice-based-cryptanalysis-exposure",
        "Lattice-based cryptanalysis exposure in deployed encryption schemes",
    )
    _commit(root, "model change: our authentication depends on this cryptographic primitive")
    after_overlay = Overlay.load(ModelRepo.open(root), fixtures.LIBRARY_ORG)

    after = retrospective_sweep.sweep(after_overlay, "2026-08-10")
    rebound = {e["id"]: e for e in after["rebound"]}
    entry = rebound["materials-paper-lattice-surprise"]
    assert entry["component"] == "lattice-based-cryptanalysis-exposure"
    assert entry["pool_entry_date"] == "2023-11-02"
    assert entry["binding_date"] == "2026-08-10"
    assert entry["had_decayed_before_rescue"] is True  # long since past twin/decay.yaml's threshold
    assert entry["lead_time_to_recognition_days"] > 365 * 2  # a real, multi-year lead time
