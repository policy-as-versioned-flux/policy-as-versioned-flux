"""The real E2E selection seam keeps maximal owner floors distinct from counterfactuals."""
import importlib.util
from pathlib import Path
from types import ModuleType
import pytest

@pytest.fixture
def step() -> ModuleType:
    path = Path(__file__).resolve().parents[1] / "verify/e2e/step3_band.py"
    spec = importlib.util.spec_from_file_location("step3_floor_context", path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_maximal_floor_is_checked_before_labelled_counterfactual(step: ModuleType) -> None:
    calls = []
    def pick(amount, floor):
        calls.append((amount, floor))
        return floor or ("baseline" if amount <= 100 else "restricted")
    result = step.crossing_probe(pick, 100, "isolated", ["baseline", "restricted", "quarantine", "isolated"])
    assert calls[:2] == [(50, "isolated"), (200, "isolated")]
    assert all(floor is None for _, floor in calls[2:])
    assert result[2:4] == ("baseline", "restricted")
    assert result[4] is True


def test_no_floor_preserves_original_crossing_context(step: ModuleType) -> None:
    calls = []
    def pick(amount, floor):
        calls.append(floor)
        return "baseline" if amount <= 100 else "restricted"
    result = step.crossing_probe(pick, 100, None, ["baseline", "restricted", "quarantine", "isolated"])
    assert result[4] is False
    assert set(calls) == {None}


def test_selector_ignoring_maximal_floor_is_still_a_failure(step: ModuleType) -> None:
    with pytest.raises(ValueError, match="owner floor"):
        step.crossing_probe(lambda amount, floor: "baseline", 100, "isolated",
                            ["baseline", "restricted", "quarantine", "isolated"])


def test_broken_counterfactual_selector_is_still_a_failure(step: ModuleType) -> None:
    with pytest.raises(ValueError, match="no crossing"):
        step.crossing_probe(lambda amount, floor: "isolated", 100, "isolated",
                            ["baseline", "restricted", "quarantine", "isolated"])


def test_nonmaximal_owner_floor_stays_active_during_crossing(step: ModuleType) -> None:
    calls = []
    def pick(amount, floor):
        calls.append(floor)
        assert floor == "restricted"
        return "restricted" if amount <= 100 else "quarantine"
    result = step.crossing_probe(pick, 100, "restricted",
                                ["baseline", "restricted", "quarantine", "isolated"])
    assert result[2:4] == ("restricted", "quarantine")
    assert result[4] is False
    assert set(calls) == {"restricted"}
