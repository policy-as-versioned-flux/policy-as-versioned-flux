"""ADR-0021: grade actual annualised selection, not a per-shock cost minimum.

The regression drives the real residual-basis grader with the estate's real cage
and adopter policy modules. The feed's uncredited mitigation curve can legitimately
have a different cheapest rung; false provenance and selection must still fail.
"""
from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

import pytest

ROOT = Path(__file__).resolve().parents[1]
GRADER = ROOT / "verify/pound-seam/pound_seam.py"
PLATFORM = ROOT / ".estate-clone/platform"
POLICY = ROOT / ".estate-clone/ludlow/selection-policy/selection_policy.py"


def _load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _estate(tmp_path: Path, *, amount: float = 13_435_900.928034885,
            impact: float = 4_907_054.7) -> tuple[Path, dict[str, Any]]:
    estate = tmp_path / "estate"
    estate.mkdir()
    (estate / "platform").symlink_to(PLATFORM, target_is_directory=True)
    package = estate / "ludlow/selection-policy"
    package.mkdir(parents=True)
    (package / "selection_policy.py").symlink_to(POLICY)
    cage = _load("_pound_test_cage", PLATFORM / "graded/cage.py")
    entry = {
        "source": "twin", "amount": amount, "currency": "GBP",
        "residual_basis": f"platform-cage-tiers@{cage.TABLE_VERSION}",
        "residuals": {t: cage.caged_residual(amount, t) for t in cage.ORDER},
        "proposed_tier": "isolated" if amount > 5000 / 0.7 else "baseline",
        "policy_version": "1.1.0",
    }
    feed = {"payload": {
        "lm": [impact / 4, impact, impact * 3],
        # Grade-5 mitigations earn no reduction at the declared threshold of 3.
        "curve": [{"account": t, "net_cost_of_risk": impact + cage.TIERS[t]["cost"]}
                  for t in cage.ORDER],
    }}
    path = estate / "ludlow/twin/forward-intel/v1/feed.json"
    path.parent.mkdir(parents=True)
    path.write_text(json.dumps(feed))
    return estate, entry


def _grade(estate: Path, entry: dict[str, Any], *,
           floor: str | None = None) -> subprocess.CompletedProcess[str]:
    path = estate / "ludlow/composed/evidence.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps({"prices": [entry]}))
    party = {"publishes": [{"name": "forward-intel", "path": "twin/forward-intel"}],
             "appetite": {"tolerance": {"amount": 5000, "currency": "GBP"}}}
    if floor is not None:
        party["overlay"] = {"floor": floor}
    # A subprocess keeps platform imports isolated from other estate-oriented tests.
    script = """
import importlib.util, json, sys
spec = importlib.util.spec_from_file_location('pound_seam', sys.argv[1])
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
module.check_residual_basis(sys.argv[2], {'ludlow': json.loads(sys.argv[3])})
sys.exit(1 if 'FAIL' in module.LINES else 3 if 'SKIP' in module.LINES else 0)
"""
    return subprocess.run([sys.executable, "-c", script, str(GRADER), str(estate),
                           json.dumps(party)], capture_output=True, text=True, check=False)


def test_different_per_shock_minimum_does_not_override_annualised_policy(tmp_path: Path):
    estate, entry = _estate(tmp_path)
    result = _grade(estate, entry)
    assert result.returncode == 0, result.stdout + result.stderr
    assert "isolated" in result.stdout and "baseline" in result.stdout
    assert "neither per-shock minimum selects" in result.stdout


@pytest.mark.parametrize("damage", ["basis", "residual", "missing-rung", "extra-rung",
                                    "tier", "version", "missing-policy", "missing-amount"])
def test_false_attribution_fails_even_when_per_shock_minima_agree(tmp_path: Path, damage: str):
    estate, entry = _estate(tmp_path, amount=1000, impact=1000)
    if damage == "basis":
        entry["residual_basis"] = "adopter-own-curve@1.0.0"
    elif damage == "residual":
        entry["residuals"]["restricted"] += 1
    elif damage == "missing-rung":
        entry["residuals"].pop("quarantine")
    elif damage == "extra-rung":
        entry["residuals"]["infra"] = 0
    elif damage == "tier":
        entry["proposed_tier"] = "isolated"
    elif damage == "version":
        entry["policy_version"] = "9.9.9"
    elif damage == "missing-policy":
        (estate / "ludlow/selection-policy/selection_policy.py").unlink()
    else:
        entry.pop("amount")
    result = _grade(estate, entry)
    assert result.returncode == 1, result.stdout + result.stderr
    assert "FAIL:" in result.stdout


def test_minimum_and_selected_rung_can_differ_in_same_instrument(tmp_path: Path):
    estate, entry = _estate(tmp_path, amount=8000, impact=1000)
    entry["proposed_tier"] = "restricted"
    result = _grade(estate, entry)
    assert result.returncode == 0, result.stdout + result.stderr
    assert "restricted" in result.stdout


@pytest.mark.parametrize("floor", ["quarantine", "isolated"])
def test_selection_replay_honours_signed_floor(tmp_path: Path, floor: str):
    estate, entry = _estate(tmp_path, amount=1000, impact=1000)
    entry["proposed_tier"] = floor
    result = _grade(estate, entry, floor=floor)
    assert result.returncode == 0, result.stdout + result.stderr
    assert f"recorded rung {floor!r}" in result.stdout


def test_policy_refuses_currency_different_from_signed_band(tmp_path: Path):
    estate, entry = _estate(tmp_path, amount=1000, impact=1000)
    entry["currency"] = "USD"
    result = _grade(estate, entry)
    assert result.returncode == 1, result.stdout + result.stderr
    assert "FAIL:" in result.stdout


@pytest.mark.parametrize("invalid", ["negative", "infinite", "boolean", "numeric-string"])
def test_invalid_numbers_cannot_earn_residual_attribution(tmp_path: Path, invalid: str):
    estate, entry = _estate(tmp_path, amount=1000, impact=1000)
    if invalid == "negative":
        entry["amount"] = -1000
        entry["residuals"] = {t: -r for t, r in entry["residuals"].items()}
    elif invalid == "infinite":
        entry["amount"] = float("inf")
        entry["residuals"] = {t: float("inf") for t in entry["residuals"]}
        entry["proposed_tier"] = "isolated"
    elif invalid == "boolean":
        entry["amount"] = 0
        entry["residuals"] = {t: False for t in entry["residuals"]}
    else:
        entry["residuals"] = {t: str(r) for t, r in entry["residuals"].items()}
    result = _grade(estate, entry)
    assert result.returncode == 1, result.stdout + result.stderr
    assert "FAIL:" in result.stdout
