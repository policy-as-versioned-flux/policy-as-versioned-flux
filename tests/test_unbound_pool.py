"""The decaying unbound-signal pool (build ticket 54, decision ticket 11 Q3).

Assertions are on the emitted `unbound-signal-pool` artefact's body and on the pure decay
functions, not on internals — `twin/unbound_pool.py` is as disposable as the rest of this system.
"""

from __future__ import annotations

import json
import math
from pathlib import Path

import pytest

from twin import fixtures, unbound_pool
from twin.artefact import DERIVED
from twin.cli import main
from twin.grades import Capabilities
from twin.model import Overlay
from twin.repo import ModelRepo

COMMAND = ["twin", "unbound-pool"]

# The default fixture's one netflix signal is dated 2011-07-12 and bound. Every test below adds
# its own unbound signals on top of that in a throwaway `scratch_repo`, so the shared session
# fixture (`repo`/`model_repo_dir`) is never mutated.


def _add_signal(root: Path, ident: str, date: str, steep: str = "economic") -> None:
    (root / "orgs" / "netflix" / "signals" / f"{ident}.yaml").write_text(
        f"id: {ident}\n"
        f"date: '{date}'\n"
        f"steep: {steep}\n"
        "source: harness fixture\n"
        "statement: planted for a test, never bound to a component.\n"
        "provenance:\n"
        "  observed_by: test\n",
        encoding="utf-8",
    )


def _commit(root: Path, message: str) -> None:
    fixtures.git(root, "add", "-A")
    fixtures.git(root, "commit", "-q", "-m", message)


# -- the decay function itself: versioned and published -------------------------------------


def test_decay_function_is_versioned_and_published() -> None:
    doc = unbound_pool.decay_function()
    assert doc["schema"] == "twin.decay/v1"
    assert doc["version"] == 1
    assert doc["half_life_days"] > 0
    assert 0.0 < doc["decayed_out_threshold"] < 1.0


def test_weight_is_full_at_age_zero_and_halves_at_one_half_life() -> None:
    half_life = unbound_pool.decay_function()["half_life_days"]
    assert unbound_pool.weight(0) == pytest.approx(1.0)
    assert unbound_pool.weight(half_life) == pytest.approx(0.5)
    assert unbound_pool.weight(2 * half_life) == pytest.approx(0.25)


def test_weight_refuses_a_negative_age() -> None:
    with pytest.raises(unbound_pool.DecayError, match="negative"):
        unbound_pool.weight(-1)


def test_is_decayed_crosses_at_the_published_threshold() -> None:
    threshold = unbound_pool.decay_function()["decayed_out_threshold"]
    assert unbound_pool.is_decayed(threshold - 0.001)
    assert not unbound_pool.is_decayed(threshold + 0.001)


def test_decayed_on_is_computed_and_falls_after_the_signal_date() -> None:
    on = unbound_pool.decayed_on("2020-01-01")
    assert on > "2020-01-01"
    # The computed date must actually be where weight crosses the threshold: a day earlier is
    # still live and the computed day itself is decayed.
    from datetime import date

    day_before = (date.fromisoformat(on) - date.fromisoformat("2020-01-01")).days - 1
    assert not unbound_pool.is_decayed(unbound_pool.weight(day_before))
    assert unbound_pool.is_decayed(unbound_pool.weight(day_before + 1))



def test_decayed_on_names_the_first_strictly_decayed_calendar_day(tmp_path: Path) -> None:
    path = tmp_path / "strict-half.yaml"
    path.write_text("schema: twin.decay/v1\nversion: 1\nhalf_life_days: 1\ndecayed_out_threshold: 0.5\n")
    assert unbound_pool.decayed_on("2026-01-01", path) == "2026-01-03"
    assert not unbound_pool.is_decayed(unbound_pool.weight(1, path), path)
    assert unbound_pool.is_decayed(unbound_pool.weight(2, path), path)


@pytest.mark.parametrize("half_life, threshold, expected", [
    (2.0, 0.5, "2026-01-04"),
    (0.5, 0.25, "2026-01-03"),
    (0.25, 0.0625, "2026-01-03"),
    (1.0, math.nextafter(0.5, 1.0), "2026-01-02"),
    (1.0, math.nextafter(0.5, 0.0), "2026-01-03"),
    (1.0, 0.6, "2026-01-02"),
    (2.0, 0.3, "2026-01-05"),
    (0.1, 7.703719777548945e-34, "2026-01-12"),
])
def test_decayed_on_checks_both_sides_of_exact_fractional_and_float_boundaries(
    tmp_path: Path, half_life: float, threshold: float, expected: str,
) -> None:
    from datetime import date

    path = tmp_path / "boundary.yaml"
    path.write_text(f"schema: twin.decay/v1\nversion: 1\nhalf_life_days: {half_life!r}\n"
                    f"decayed_out_threshold: {threshold!r}\n")
    on = unbound_pool.decayed_on("2026-01-01", path)
    assert on == expected
    age = (date.fromisoformat(on) - date(2026, 1, 1)).days
    assert unbound_pool.is_decayed(unbound_pool.weight(age, path), path)
    assert not unbound_pool.is_decayed(unbound_pool.weight(age - 1, path), path)


def test_a_rounded_estimate_past_the_calendar_does_not_hide_a_valid_last_day(tmp_path: Path) -> None:
    path = tmp_path / "last-day.yaml"
    path.write_text("schema: twin.decay/v1\nversion: 1\nhalf_life_days: 0.1\n"
                    "decayed_out_threshold: 7.703719777548945e-34\n")
    assert unbound_pool.decayed_on("9999-12-20", path) == "9999-12-31"
    assert not unbound_pool.is_decayed(unbound_pool.weight(10, path), path)
    assert unbound_pool.is_decayed(unbound_pool.weight(11, path), path)


@pytest.mark.parametrize("signal_date, half_life", [
    ("2026-01-01", 1e308),
    ("9999-12-31", 1.0),
    ("9999-12-30", 1.0),
])
def test_an_unrepresentable_decay_date_still_raises_overflow(
    tmp_path: Path, signal_date: str, half_life: float,
) -> None:
    path = tmp_path / "overflow.yaml"
    path.write_text(f"schema: twin.decay/v1\nversion: 1\nhalf_life_days: {half_life:.17e}\n"
                    "decayed_out_threshold: 0.5\n")
    with pytest.raises(OverflowError):
        unbound_pool.decayed_on(signal_date, path)


def test_large_accepted_half_life_still_finds_the_first_representable_crossing(tmp_path: Path) -> None:
    from datetime import date

    path = tmp_path / "large-half-life.yaml"
    path.write_text("schema: twin.decay/v1\nversion: 1\nhalf_life_days: 1.0e+20\n"
                    f"decayed_out_threshold: {math.nextafter(1.0, 0.0)!r}\n")
    on = unbound_pool.decayed_on("2026-01-01", path)
    age = (date.fromisoformat(on) - date(2026, 1, 1)).days
    assert unbound_pool.is_decayed(unbound_pool.weight(age, path), path)
    assert not unbound_pool.is_decayed(unbound_pool.weight(age - 1, path), path)


def test_pin_carries_the_published_parameters_and_a_digest() -> None:
    pin = unbound_pool.pin()
    assert pin["version"] == 1
    assert pin["half_life_days"] == unbound_pool.decay_function()["half_life_days"]
    assert pin["digest"]


# -- unbound_ids: the complement of what `sense()` refuses -----------------------------------


def test_unbound_ids_excludes_the_bound_signal(repo: ModelRepo) -> None:
    overlay = Overlay.load(repo, "netflix")
    assert "price-separation-announced" not in unbound_pool.unbound_ids(overlay)


def test_unbound_ids_includes_a_signal_with_no_binding_claim(scratch_repo: Path) -> None:
    _add_signal(scratch_repo, "unbound-one", "2020-01-01")
    _commit(scratch_repo, "add an unbound signal")
    overlay = Overlay.load(ModelRepo.open(scratch_repo), "netflix")
    assert "unbound-one" in unbound_pool.unbound_ids(overlay)
    assert "price-separation-announced" not in unbound_pool.unbound_ids(overlay)


# -- retention: never dropped, decayed or not -------------------------------------------------


def test_pool_retains_a_signal_that_has_decayed_rather_than_dropping_it(scratch_repo: Path) -> None:
    """Q3's whole point: plain decay-to-zero must not be indistinguishable from deletion."""
    _add_signal(scratch_repo, "ancient-signal", "2000-01-01")
    _commit(scratch_repo, "add an ancient unbound signal")
    overlay = Overlay.load(ModelRepo.open(scratch_repo), "netflix")

    entries = unbound_pool.pool(overlay, "2026-01-01")
    planted = next((e for e in entries if e["id"] == "ancient-signal"), None)
    assert planted is not None, "a decayed-out signal must not be silently dropped from the pool"
    assert planted["decayed"] is True
    assert planted["decayed_on"] is not None
    assert planted["decayed_on"] <= "2026-01-01"


def test_pool_reports_a_fresh_signal_as_live(scratch_repo: Path) -> None:
    _add_signal(scratch_repo, "fresh-signal", "2025-12-31")
    _commit(scratch_repo, "add a fresh unbound signal")
    overlay = Overlay.load(ModelRepo.open(scratch_repo), "netflix")

    entries = unbound_pool.pool(overlay, "2026-01-01")
    planted = next(e for e in entries if e["id"] == "fresh-signal")
    assert planted["decayed"] is False
    assert planted["age_days"] == 1


def test_pool_date_and_live_state_agree_across_the_reported_boundary(scratch_repo: Path, tmp_path: Path) -> None:
    path = tmp_path / "pool-boundary.yaml"
    path.write_text("schema: twin.decay/v1\nversion: 1\nhalf_life_days: 1\ndecayed_out_threshold: 0.5\n")
    _add_signal(scratch_repo, "boundary-signal", "2026-01-01")
    _commit(scratch_repo, "add a boundary signal")
    overlay = Overlay.load(ModelRepo.open(scratch_repo), "netflix")
    before = next(e for e in unbound_pool.pool(overlay, "2026-01-02", path) if e["id"] == "boundary-signal")
    on = next(e for e in unbound_pool.pool(overlay, "2026-01-03", path) if e["id"] == "boundary-signal")
    assert before["decayed_on"] == on["decayed_on"] == "2026-01-03"
    assert before["decayed"] is False
    assert on["decayed"] is True
    assert sum(unbound_pool.age_distribution([before], path).values()) == 1
    assert sum(unbound_pool.age_distribution([on], path).values()) == 0


def test_pool_refuses_a_signal_dated_after_the_declared_time(scratch_repo: Path) -> None:
    _add_signal(scratch_repo, "future-signal", "2027-01-01")
    _commit(scratch_repo, "add a signal from the future")
    overlay = Overlay.load(ModelRepo.open(scratch_repo), "netflix")

    with pytest.raises(unbound_pool.DecayError, match="after the declared time"):
        unbound_pool.pool(overlay, "2026-01-01")


# -- pool size and age distribution: observable ------------------------------------------------


def test_pool_size_counts_only_the_live_pool_not_the_decayed_out(scratch_repo: Path) -> None:
    _add_signal(scratch_repo, "ancient-signal", "2000-01-01")
    _add_signal(scratch_repo, "fresh-signal", "2025-12-31")
    _commit(scratch_repo, "add one ancient and one fresh unbound signal")
    overlay = Overlay.load(ModelRepo.open(scratch_repo), "netflix")

    entries = unbound_pool.pool(overlay, "2026-01-01")
    live = [e for e in entries if not e["decayed"]]
    assert len(entries) == 2
    assert len(live) == 1
    assert live[0]["id"] == "fresh-signal"


def test_age_distribution_bins_the_live_pool_by_half_life_multiple(scratch_repo: Path) -> None:
    from datetime import date, timedelta

    half_life = int(unbound_pool.decay_function()["half_life_days"])
    at = date(2026, 1, 1)
    # One signal per bin: age zero (bin 0-1), 1.5 half-lives (bin 1-2), 2.5 (bin 2-3).
    ages = {"just-observed": 0, "one-and-a-half-half-lives-old": int(1.5 * half_life),
            "two-and-a-half-half-lives-old": int(2.5 * half_life)}
    for ident, age_days in ages.items():
        _add_signal(scratch_repo, ident, (at - timedelta(days=age_days)).isoformat())
    _commit(scratch_repo, "add three unbound signals spanning three age bins")
    overlay = Overlay.load(ModelRepo.open(scratch_repo), "netflix")

    entries = unbound_pool.pool(overlay, at.isoformat())
    distribution = unbound_pool.age_distribution(entries)

    assert sum(distribution.values()) == sum(1 for e in entries if not e["decayed"])
    assert set(distribution) == {"0-1", "1-2", "2-3", "3-4", "4+"}
    assert distribution["0-1"] == 1
    assert distribution["1-2"] == 1
    assert distribution["2-3"] == 1
    assert distribution["3-4"] == 0 and distribution["4+"] == 0


def test_age_distribution_excludes_decayed_out_signals(scratch_repo: Path) -> None:
    _add_signal(scratch_repo, "ancient-signal", "2000-01-01")
    _commit(scratch_repo, "add an ancient unbound signal")
    overlay = Overlay.load(ModelRepo.open(scratch_repo), "netflix")

    entries = unbound_pool.pool(overlay, "2026-01-01")
    distribution = unbound_pool.age_distribution(entries)
    assert sum(distribution.values()) == 0


# -- the emitted artefact ----------------------------------------------------------------------


def test_unbound_pool_artefact_carries_pins_depth_and_a_derived_mark(
    repo: ModelRepo, caps: Capabilities
) -> None:
    artefact = unbound_pool.unbound_pool_artefact(repo, caps, "netflix", "2026-01-01", COMMAND)
    assert artefact.kind == unbound_pool.KIND_UNBOUND_POOL
    assert artefact.mark == DERIVED  # nothing here could carry a human's accountability
    assert artefact.pins["decay"]["version"] == 1
    assert artefact.pins["at"] == "2026-01-01"
    assert artefact.depth["grade"] in ("stub", "partial", "full")
    artefact.digest()  # does not raise: no forbidden key crept into the body


def test_unbound_pool_artefact_body_carries_observable_size_and_distribution(
    scratch_repo: Path, caps: Capabilities
) -> None:
    _add_signal(scratch_repo, "ancient-signal", "2000-01-01")
    _add_signal(scratch_repo, "fresh-signal", "2025-12-31")
    _commit(scratch_repo, "add two unbound signals")
    repo = ModelRepo.open(scratch_repo)

    artefact = unbound_pool.unbound_pool_artefact(repo, caps, "netflix", "2026-01-01", COMMAND)
    body = artefact.body
    assert body["pool_size"] == 1
    assert body["decayed_out_count"] == 1
    assert sum(body["age_distribution"].values()) == body["pool_size"]
    ids = {s["id"] for s in body["signals"]}
    assert {"ancient-signal", "fresh-signal"} <= ids  # neither is dropped, decayed or not


def test_unbound_pool_artefact_is_reproducible_given_identical_pins(
    repo: ModelRepo, caps: Capabilities
) -> None:
    first = unbound_pool.unbound_pool_artefact(repo, caps, "netflix", "2026-01-01", COMMAND)
    second = unbound_pool.unbound_pool_artefact(repo, caps, "netflix", "2026-01-01", COMMAND)
    assert first.digest() == second.digest()


# -- seam 1: the CLI verb --------------------------------------------------------------------


def test_the_cli_verb_emits_an_unbound_signal_pool_artefact(model_repo_dir: Path, tmp_path: Path) -> None:
    out = tmp_path / "pool.json"
    assert (
        main(
            [
                "unbound-pool", "--repo", str(model_repo_dir), "--org", "netflix",
                "--at", "2026-01-01", "--out", str(out),
            ]
        )
        == 0
    )
    doc = json.loads(out.read_bytes())
    assert doc["envelope"]["kind"] == "unbound-signal-pool"
    assert doc["envelope"]["mark"] == "derived"
    assert doc["envelope"]["pins"]["at"] == "2026-01-01"
    assert "pool_size" in doc["body"]
    assert "age_distribution" in doc["body"]
