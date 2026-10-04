#!/usr/bin/env python3
"""Grade the owner's decided mode record; expiry changes the grade, never the guard."""
from __future__ import annotations

import argparse
import copy
import datetime as dt
import re
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]
MODES = {"development", "other-hand", "operations"}


def grade(mode: str, record: dict, root: Path, today: dt.date) -> list[str]:
    failures: list[str] = []
    if mode not in MODES:
        return [f"mode declaration {mode!r} is not a known mode"]
    if record.get("mode") != mode:
        failures.append("ENACT_MODE moved without a matching mode record")
    entries = record.get("said")
    if not isinstance(entries, list) or not entries:
        return failures + ["mode record carries no dated acknowledgements"]
    if any(not isinstance(entry, dict) for entry in entries):
        return failures + ["every acknowledgement must be a record"]
    dates: list[dt.date] = []
    for entry in entries:
        if not isinstance(entry, dict):
            failures.append("acknowledgement is not a record")
            continue
        try:
            date = dt.date.fromisoformat(str(entry.get("on", "")))
        except ValueError:
            failures.append("acknowledgement has no real date")
            continue
        dates.append(date)
        if date > today:
            failures.append(f"acknowledgement on {date} is in the future")
        if entry.get("by") not in {"owner", "assistant"}:
            failures.append(f"acknowledgement on {date} names no owner or assistant")
        relative = Path(str(entry.get("where", "")))
        path = (root / relative).resolve()
        if relative.is_absolute() or not path.is_relative_to(root.resolve()) or not path.is_file():
            failures.append(f"acknowledgement on {date} cites no file inside this repository")
            continue
        # An example YAML record is not evidence for its own quoted authorization.
        prose = re.sub(r"(?ms)^```.*?^```[^\n]*\n?", "", path.read_text())
        words = entry.get("words")
        if not isinstance(words, str) or not words or not any(
            str(date) in paragraph and words in re.findall(r'["“](.*?)["”]', paragraph, re.S)
            for paragraph in re.split(r"\n\s*\n", prose)):
            failures.append(f"acknowledgement on {date} has no exact dated quote in {relative}")
    if dates != sorted(dates):
        failures.append("acknowledgements are not ordered oldest first")
    if mode != "operations" and entries[-1].get("by") != "owner":
        failures.append(f"the newest {mode} acknowledgement must be by the owner")
    if mode == "development":
        try:
            until = dt.date.fromisoformat(str(record.get("until", "")))
            if not dates or until > max(dates) + dt.timedelta(days=28) or until < max(dates):
                failures.append("development window exceeds 28 days or ends before its acknowledgement")
            if today >= until:
                failures.append(f"development window lapsed on {until}; guard continues, grade is red")
        except ValueError:
            failures.append("development record has no valid until date")
    return failures


def check(root: Path, today: dt.date) -> list[str]:
    try:
        mode = (root / "twin/ENACT_MODE").read_text().strip()
        # This record consists of strings and a list. BaseLoader preserves its `on` key;
        # YAML 1.1's boolean resolver otherwise turns the owner's decided key into True.
        record = yaml.load((root / "twin/ENACT_MODE.why").read_text(), Loader=yaml.BaseLoader)
        if not isinstance(record, dict):
            return ["mode record is not a mapping"]
        return grade(mode, record, root, today)
    except (OSError, yaml.YAMLError) as error:
        return [f"mode declaration or record cannot be read: {error}"]


def selfcheck() -> None:
    import tempfile
    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory)
        (root / "owner.md").write_text('2026-09-24, owner: "agree".\n')
        record: dict = {"mode": "development", "until": "2026-10-22", "said": [
            {"on": "2026-09-24", "by": "owner", "words": "agree", "where": "owner.md"}]}
        today = dt.date(2026, 10, 3)
        assert not grade("development", record, root, today)
        assert grade("operations", record, root, today)
        assert grade("development", record, root, dt.date(2026, 10, 22))
        for field, value in (("until", "2026-10-23"), ("until", "2026-09-23")):
            planted = copy.deepcopy(record)
            planted[field] = value
            assert grade("development", planted, root, today)
        for field, value in (("on", "2026-09-25"), ("by", "assistant"),
                             ("words", "agreed"), ("where", "missing.md")):
            planted = copy.deepcopy(record)
            planted["said"][0][field] = value
            assert grade("development", planted, root, today)
        (root / "owner.md").write_text('```yaml\n2026-09-24: "agree"\n```\n')
        assert grade("development", record, root, today)
    print("PASS: unrecorded flip, lapsed or overlong window, moved date, assistant loosening, missing quote and self-citing example all read false")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("check", "selfcheck"))
    parser.add_argument("--root", type=Path, default=ROOT)
    args = parser.parse_args()
    if args.command == "selfcheck":
        selfcheck()
        return 0
    failures = check(args.root, dt.datetime.now(dt.timezone.utc).date())
    for failure in failures:
        print(f"FAIL: {failure}")
    if not failures:
        print("PASS: ENACT_MODE agrees with exact dated owner words and its development window is current")
        print("LIMIT: the assistant can write a false dated quote; this catches accidents, not malicious authorization")
    return int(bool(failures))


if __name__ == "__main__":
    raise SystemExit(main())
