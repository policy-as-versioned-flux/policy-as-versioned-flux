"""Finite owner renewals through the public record checker, using disposable files.

Dates passed to check() exercise boundaries; they are not future acknowledgements.
"""
from __future__ import annotations

import datetime as dt
import importlib.util
from pathlib import Path

import pytest
import yaml

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "enact_record", ROOT / "verify/enact-record/enact_record.py")
assert SPEC is not None and SPEC.loader is not None
enact_record = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(enact_record)


@pytest.fixture
def renewal(tmp_path: Path) -> Path:
    (tmp_path / "twin").mkdir()
    (tmp_path / "twin/ENACT_MODE").write_text("development\n")
    (tmp_path / "owner.md").write_text(
        '2026-10-22, owner: "agree to renew this until the end of the year". '
        'The assistant interprets the exclusive endpoint as 2027-01-01.\n')
    record = {"mode": "development", "until": "2027-01-01", "said": [
        {"on": "2026-10-22", "by": "owner",
         "words": "agree to renew this until the end of the year",
         "where": "owner.md", "until": "2027-01-01"}]}
    (tmp_path / "twin/ENACT_MODE.why").write_text(yaml.safe_dump(record))
    return tmp_path


@pytest.mark.parametrize("today", [dt.date(2026, 10, 22), dt.date(2026, 12, 31)])
def test_explicit_owner_year_end_renewal_covers_december_31(renewal: Path, today: dt.date) -> None:
    assert enact_record.check(renewal, today) == []


def test_explicit_renewal_expires_on_january_1(renewal: Path) -> None:
    assert enact_record.check(renewal, dt.date(2027, 1, 1)) == [
        "development window lapsed on 2027-01-01; guard continues, grade is red"]


@pytest.mark.parametrize(("change", "diagnostic"), [
    ("assistant", "must be by the owner"),
    ("missing_endpoint", "no explicit endpoint"),
    ("separate_endpoint", "no explicit endpoint"),
    ("fenced_endpoint", "no explicit endpoint"),
    ("no_explicit_renewal", "exceeds 28 days"),
    ("different_endpoint", "differs from the newest owner's explicit endpoint"),
    ("beyond_year_end", "exceeds year end"),
    ("before_acknowledgement", "ends before its acknowledgement"),
    ("future_acknowledgement", "is in the future"),
    ("moved_date", "no exact dated quote"),
    ("changed_words", "no exact dated quote"),
    ("unrecorded_mode", "moved without a matching mode record"),
])
def test_explicit_renewal_preserves_owner_and_provenance_safeguards(
    renewal: Path, change: str, diagnostic: str,
) -> None:
    path = renewal / "twin/ENACT_MODE.why"
    record = yaml.load(path.read_text(), Loader=yaml.BaseLoader)
    newest = record["said"][-1]
    prose = renewal / "owner.md"
    if change == "assistant":
        newest["by"] = "assistant"
    elif change == "missing_endpoint":
        prose.write_text(prose.read_text().replace("2027-01-01", "year end"))
    elif change == "separate_endpoint":
        prose.write_text(prose.read_text().replace(". The assistant", ".\n\nThe assistant"))
    elif change == "fenced_endpoint":
        prose.write_text(prose.read_text().split(" The assistant")[0]
                         + "\n\n```yaml\nuntil: 2027-01-01\n```\n")
    elif change == "no_explicit_renewal":
        del newest["until"]
    elif change == "different_endpoint":
        record["until"] = "2026-12-31"
    elif change in {"beyond_year_end", "before_acknowledgement"}:
        endpoint = "2027-01-02" if change == "beyond_year_end" else "2026-10-21"
        newest["until"] = record["until"] = endpoint
        prose.write_text(prose.read_text().replace("2027-01-01", endpoint))
    elif change == "future_acknowledgement":
        newest["on"] = "2026-10-23"
        prose.write_text(prose.read_text().replace("2026-10-22", "2026-10-23"))
    elif change == "moved_date":
        newest["on"] = "2026-10-21"
    elif change == "changed_words":
        newest["words"] = "agreed to renew this until the end of the year"
    elif change == "unrecorded_mode":
        (renewal / "twin/ENACT_MODE").write_text("operations\n")
    path.write_text(yaml.safe_dump(record))
    assert any(diagnostic in failure
               for failure in enact_record.check(renewal, dt.date(2026, 10, 22)))


@pytest.mark.parametrize(("until", "today", "diagnostic"), [
    ("2026-10-22", dt.date(2026, 10, 21), None),
    ("2026-10-22", dt.date(2026, 10, 22), "lapsed on 2026-10-22"),
    ("2026-10-23", dt.date(2026, 10, 21), "exceeds 28 days"),
])
def test_legacy_acknowledgement_keeps_its_28_day_limit(
    renewal: Path, until: str, today: dt.date, diagnostic: str | None,
) -> None:
    (renewal / "owner.md").write_text('2026-09-24, owner: "agree".\n')
    record = {"mode": "development", "until": until, "said": [
        {"on": "2026-09-24", "by": "owner", "words": "agree", "where": "owner.md"}]}
    (renewal / "twin/ENACT_MODE.why").write_text(yaml.safe_dump(record))
    failures = enact_record.check(renewal, today)
    if diagnostic is None:
        assert failures == []
    else:
        assert any(diagnostic in failure for failure in failures)
