"""verify/priced-holes — the pure arithmetic and the since rule, at the grader's own seam.

The grader re-derives what composition.py computes (ticket 38): the EOL ramp from `since` to
`as_of`, the workload share of the uncaged residual bounded at the whole residual, and the rule
that `since` is read off the first signed tag naming the namespace and survives a reopen. These
tests pin those down so a change to either side shows up here before the gate.
"""

from __future__ import annotations

import importlib.util
import math
from pathlib import Path
from types import ModuleType

import pytest

GRADER = Path(__file__).resolve().parent.parent / "verify" / "priced-holes" / "priced_holes.py"


@pytest.fixture(scope="module")
def grader() -> ModuleType:
    spec = importlib.util.spec_from_file_location("priced_holes", GRADER)
    assert spec is not None and spec.loader is not None
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


# -- the ramp ----------------------------------------------------------------------------------


def test_ramp_is_one_up_to_since_and_where_a_date_is_unknown(grader: ModuleType) -> None:
    assert grader.expected_ramp("2026-08-25", "2026-08-25") == 1.0
    assert grader.expected_ramp("2026-08-25", "2026-08-01") == 1.0
    assert grader.expected_ramp(None, "2026-08-28") == 1.0
    assert grader.expected_ramp("2026-08-25", None) == 1.0


def test_ramp_grows_one_x_per_year_and_caps_at_four(grader: ModuleType) -> None:
    three_days = grader.expected_ramp("2026-08-25", "2026-08-28")
    assert math.isclose(three_days, 1.0 + 3 / 365.0)
    one_year = grader.expected_ramp("2025-10-31", "2026-10-31")
    two_years = grader.expected_ramp("2025-10-31", "2027-10-31")
    assert 1.0 < three_days < one_year < two_years
    assert grader.expected_ramp("2020-01-01", "2030-01-01") == 5.0


# -- the share and the bound -------------------------------------------------------------------


def test_amount_is_the_workload_share_of_the_residual(grader: ModuleType) -> None:
    assert grader.expected_amount(1000.0, 1, 4, 1.0) == (250.0, False)
    assert grader.expected_amount(1000.0, 4, 4, 1.0) == (1000.0, False)


def test_amount_is_bounded_at_the_whole_residual(grader: ModuleType) -> None:
    amount, bounded = grader.expected_amount(1000.0, 3, 4, 2.0)   # 1500 raw
    assert amount == 1000.0 and bounded is True


def test_nothing_inside_and_no_residual_price_nothing(grader: ModuleType) -> None:
    assert grader.expected_amount(1000.0, 0, 0, 3.0) == (0.0, False)
    assert grader.expected_amount(None, 2, 4, 1.0) == (None, False)


# -- since-preservation and the document checks -------------------------------------------------


def _lines(grader: ModuleType, doc: dict, ctx: dict) -> list[str]:
    grader.LINES.clear()
    grader.check_doc(doc, ctx)
    return list(grader.LINES)


def test_a_reopened_namespace_keeps_the_since_the_first_signed_tag_carries(grader: ModuleType) -> None:
    doc, ctx = grader._good()
    doc["ungoverned"][0]["status"] = "new"
    doc["deltas"].append({"kind": "new-ungoverned-namespace", "namespace": "reset",
                          "perspective": "driftwood", "currency": "GBP",
                          "amount": doc["ungoverned"][0]["price"]["amount"], "detail": ""})
    assert "FAIL" not in _lines(grader, doc, ctx)


def test_a_since_no_signed_tag_carries_is_observed_false(grader: ModuleType) -> None:
    doc, ctx = grader._good()
    doc["ungoverned"][0]["price"]["since"] = "2026-08-01"
    assert "FAIL" in _lines(grader, doc, ctx)


def test_a_null_since_needs_its_limit_named(grader: ModuleType) -> None:
    doc, ctx = grader._good()
    price = doc["ungoverned"][0]["price"]
    price.update(since=None, ramp=1.0, amount=150.0, limits=[])
    ctx["since"] = {"reset": None}
    assert "FAIL" in _lines(grader, doc, ctx)
    price["limits"] = ["no signed composed artefact names reset: ramp held at 1.0"]
    assert "FAIL" not in _lines(grader, doc, ctx)


def test_an_amount_above_the_residual_is_observed_false(grader: ModuleType) -> None:
    doc, ctx = grader._good()
    doc["ungoverned"][0]["price"]["amount"] = 301.0
    assert "FAIL" in _lines(grader, doc, ctx)


def test_the_deleted_refusals_are_observed_false_and_the_old_shape_is_a_skip(grader: ModuleType) -> None:
    doc, ctx = grader._good()
    doc["refusals"] = [{"kind": "baseline-widening", "subject": "MODERATE -> HIGH"}]
    assert "FAIL" in _lines(grader, doc, ctx)
    doc, ctx = grader._good()
    doc.pop("deltas")
    lines = _lines(grader, doc, ctx)
    assert "SKIP" in lines and "FAIL" not in lines


@pytest.mark.parametrize("kind", ["new-untagged-pin", "closed-untagged-pin"])
def test_an_untagged_pin_delta_is_a_kind_this_check_admits(grader: ModuleType, kind: str) -> None:
    """Ticket 69's own deltas. DELTA_KINDS is a whitelist, so the moment an
    adopter composed an untagged pin this check failed on the delta reporting
    it -- the gate going red on the rule it was built to grade."""
    doc, ctx = grader._good()
    doc["deltas"].append({"kind": kind, "source": "insurer", "name": "quote-driftwood",
                          "version": "v2", "perspective": "driftwood", "currency": "GBP",
                          "amount": 113403.3, "priced_by": "the premium the pin books",
                          "detail": ""})
    assert "FAIL" not in _lines(grader, doc, ctx)


def test_a_kind_the_whitelist_does_not_name_is_still_observed_false(grader: ModuleType) -> None:
    doc, ctx = grader._good()
    doc["deltas"].append({"kind": "reopened-untagged-pin", "source": "insurer",
                          "perspective": "driftwood", "currency": "GBP", "amount": 1.0,
                          "detail": ""})
    assert "FAIL" in _lines(grader, doc, ctx)
