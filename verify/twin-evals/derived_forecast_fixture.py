#!/usr/bin/env python3
"""A throwaway adopter, a throwaway feeds publisher and their bare origins, for grading the
derived-forecast seam (ecosystem ticket 93) with no token, no network and no real repository.

    derived_forecast_fixture.py build DIR [--no-forecast] [--no-outcome] [--outcome-committed ISO]
    derived_forecast_fixture.py late DIR        # merge a forecast onto main AFTER the horizon

What it builds is exactly what `.claude/skills/derive-probability/assets/example-forecast.yaml`
cites, so the worked example validates against it: a `market-moves` envelope carrying the move
of `0xfixture` from 0.40 to 0.45 between 2026-01-02 and 2026-01-03, a `news` envelope carrying
`fixture-publisher-tagged`, an overlay with two scenarios closing 2026-06-30 and a vendored
world model that believes 0.2 and 0.1. Every commit carries a FIXED committer date, because the
check reads pre-registration off the served ref's first-parent history and the fixture has to
put the forecast before the horizon (2026-02-01), the outcome after it (2026-07-01), and a late
one after it (branch commit 2026-02-15, MERGED 2026-07-15) to prove the merge date wins.

Everything here is a stand-in and the check's lines say so. Nothing here is the twin having run.
"""
from __future__ import annotations

import argparse
import copy
import json
import os
import subprocess
from pathlib import Path
from typing import Any

import yaml

HERE = Path(__file__).resolve().parent
HUB = HERE.parents[1]
EXAMPLE = HUB / ".claude" / "skills" / "derive-probability" / "assets" / "example-forecast.yaml"

BASE_DATE = "2026-01-01T00:00:00+00:00"
FORECAST_DATE = "2026-02-01T00:00:00+00:00"
OUTCOME_DATE = "2026-07-01T00:00:00+00:00"
LATE_BRANCH_DATE = "2026-02-15T00:00:00+00:00"
LATE_MERGE_DATE = "2026-07-15T00:00:00+00:00"
FORECAST_PATH = "twin/forecasts/2026-02-01-fixture.forecast.yaml"
LATE_PATH = "twin/forecasts/2026-02-15-late.forecast.yaml"
OUTCOME_PATH = "twin/orgs/driftwood/outcomes/fixture-supply-2026-resolved.yaml"


def forecast_doc() -> dict[str, Any]:
    """The worked example, as a fresh mapping."""
    return copy.deepcopy(yaml.safe_load(EXAMPLE.read_text(encoding="utf-8")))


def outcome_doc() -> dict[str, Any]:
    return {
        "id": "fixture-supply-2026-resolved",
        "proposition": "a-fixture-supplier-fails-within-the-horizon",
        "observed": True,
        "resolved_on": "2026-06-30",
        "source": "the fixture's own answer key, a stand-in (derived_forecast_fixture.py)",
        "contamination": "control",
        "source_dated": True,
    }


def _git(repo: Path, *args: str, date: str | None = None) -> str:
    # No signing and no hooks: a throwaway repository's commits are nobody's to sign, and the
    # machine's global hooks (a secret scanner with a monthly quota, on 2026-09-06 exhausted)
    # are not part of what this fixture proves. core.hooksPath is also written into each
    # repository below, so the local clock's own child commits in a worktree of it skip them too.
    env = {**os.environ, "GIT_AUTHOR_NAME": "fixture", "GIT_AUTHOR_EMAIL": "fixture@fixture.invalid",
           "GIT_COMMITTER_NAME": "fixture", "GIT_COMMITTER_EMAIL": "fixture@fixture.invalid",
           "GIT_CONFIG_COUNT": "2", "GIT_CONFIG_KEY_0": "commit.gpgsign", "GIT_CONFIG_VALUE_0": "false",
           "GIT_CONFIG_KEY_1": "core.hooksPath", "GIT_CONFIG_VALUE_1": os.devnull}
    env.pop("GIT_DIR", None)
    if date:
        env["GIT_AUTHOR_DATE"] = date
        env["GIT_COMMITTER_DATE"] = date
    run = subprocess.run(["git", "-C", str(repo), *args], capture_output=True, text=True, env=env)
    if run.returncode != 0:
        raise RuntimeError(f"git {' '.join(args)} in {repo}: {run.stderr.strip()}")
    return run.stdout


def _write(path: Path, doc: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.suffix == ".json":
        path.write_text(json.dumps(doc, indent=1) + "\n", encoding="utf-8")
    else:
        path.write_text(yaml.safe_dump(doc, sort_keys=False), encoding="utf-8")


def _repo_with_origin(root: Path, name: str) -> Path:
    repo, origin = root / name, root / f"{name}.origin.git"
    repo.mkdir(parents=True)
    _git(repo, "init", "-q", "-b", "main")
    _git(repo, "config", "core.hooksPath", os.devnull)
    _git(origin.parent, "init", "-q", "--bare", "-b", "main", str(origin))
    _git(repo, "remote", "add", "origin", str(origin))
    return repo


def _commit_push(repo: Path, message: str, date: str) -> None:
    _git(repo, "add", "-A")
    _git(repo, "commit", "-q", "-m", message, date=date)
    _git(repo, "push", "-q", "-u", "origin", "main")


def _feeds(root: Path) -> Path:
    repo = _repo_with_origin(root, "feeds")
    _write(repo / "party.yaml", {"party": "feeds", "roles": ["publisher"], "inherits": []})
    _write(repo / "market-moves" / "v1" / "feed.json", {
        "kind": "feed", "name": "market-moves", "version": "1.0.0", "published_by": "feeds",
        "published_at": "2026-01-05T00:00:00+00:00", "payload_schema": "market-moves/payload.schema.json",
        "payload": {
            "venue": "polymarket", "source": "a fixture, not a venue", "selection_rule": "fixture",
            "note": "a stand-in series built by verify/twin-evals/derived_forecast_fixture.py",
            "markets": {
                "0xfixture": {
                    "venue": "polymarket", "question": "Will the fixture supplier fail before 2026-06-30?",
                    "category": "fixture", "resolution_source": "the fixture",
                    "observations": [
                        {"date": "2026-01-02", "price_level": 0.40},
                        {"date": "2026-01-03", "price_level": 0.45},
                        {"date": "2026-01-04", "price_level": 0.44},
                    ],
                },
            },
        },
    })
    _write(repo / "news" / "v1" / "feed.json", {
        "kind": "feed", "name": "news", "version": "1.0.0", "published_by": "feeds",
        "published_at": "2026-01-05T00:00:00+00:00", "payload_schema": "news/payload.schema.json",
        "payload": {
            "source": "a fixture", "note": "a stand-in pool built by verify/twin-evals/derived_forecast_fixture.py",
            "events": [
                {"id": "fixture-publisher-tagged", "date": "2026-01-03", "source": "fixture-publisher",
                 "statement": "the fixture publisher tagged v1.0.0 of the feed this organisation reads.",
                 "provenance": {"url": "https://example.invalid/fixture/releases/tag/v1.0.0"}},
            ],
        },
    })
    _commit_push(repo, "fixture feeds", BASE_DATE)
    return repo


def _adopter(root: Path) -> Path:
    repo = _repo_with_origin(root, "driftwood")
    org = repo / "twin" / "orgs" / "driftwood"
    _write(repo / "party.yaml", {
        "party": "driftwood", "roles": ["risk-bearer", "adopter"], "reporting_currency": "GBP",
        "inherits": [{"party": "platform", "kind": "implementations", "version": "2.0.1", "since": "2026-01-01"}],
    })
    _write(repo / "twin" / "currency.yaml", {"perspectives": {"driftwood": "GBP"}})
    _write(repo / "twin" / "signals.yaml", {"schema": "twin.signal-lookup/v1", "org": "driftwood", "signals": []})
    _write(org / "meta.yaml", {"id": "driftwood", "unit": "overlay", "org": "driftwood", "world_ref": "fixture"})
    _write(org / "perspectives" / "driftwood.yaml", {"id": "driftwood", "name": "the fixture seat", "party": "employer"})
    _write(org / "scenarios" / "fixture-supply-2026.yaml", {
        "id": "fixture-supply-2026", "question": "Does the fixture supplier fail inside the horizon?",
        "proposition": "a-fixture-supplier-fails-within-the-horizon", "at": "2026-01-01", "horizon": "2026-06-30",
        "components": ["tier-one-supplier-relationship"], "world_models": ["reference-map"], "class": "supply-shock",
    })
    _write(org / "scenarios" / "fixture-quiet-2026.yaml", {
        "id": "fixture-quiet-2026", "question": "Does the quiet thing happen?",
        "proposition": "a-fixture-quiet-thing-happens", "at": "2026-01-01", "horizon": "2026-06-30",
        "components": ["brand-trust"], "world_models": ["reference-map"], "class": "supply-shock",
    })
    _write(repo / "twin" / "world" / "world_models" / "reference-map.yaml", {
        "id": "reference-map", "name": "the fixture's reference map", "credence": 0.5,
        "beliefs": {"a-fixture-supplier-fails-within-the-horizon": 0.2, "a-fixture-quiet-thing-happens": 0.1},
    })
    _commit_push(repo, "fixture adopter", BASE_DATE)
    return repo


def build(root: Path, with_forecast: bool = True, with_outcome: bool = True,
          outcome_committed: str = OUTCOME_DATE) -> Path:
    root = Path(root)
    root.mkdir(parents=True, exist_ok=True)
    _feeds(root)
    repo = _adopter(root)
    if with_forecast:
        _write(repo / FORECAST_PATH, forecast_doc())
        _commit_push(repo, "twin: a derived forecast (fixture)", FORECAST_DATE)
    if with_outcome:
        _write(repo / OUTCOME_PATH, outcome_doc())
        _commit_push(repo, "twin: the outcome (fixture)", outcome_committed)
    return root


def merge_late_forecast(root: Path) -> str:
    """A forecast committed on a branch BEFORE the horizon and merged onto main AFTER it. The
    file's own dates say early; the served ref's first-parent history says late."""
    repo = Path(root) / "driftwood"
    doc = forecast_doc()
    doc["run"]["run_at"] = "2026-02-15"
    for f in doc["forecasts"]:
        f["id"] = f["id"].replace("2026-02-01", "2026-02-15")
    _git(repo, "checkout", "-q", "-b", "late-forecast", "main")
    _write(repo / LATE_PATH, doc)
    _git(repo, "add", "-A")
    _git(repo, "commit", "-q", "-m", "twin: a forecast dated before the horizon", date=LATE_BRANCH_DATE)
    _git(repo, "checkout", "-q", "main")
    _git(repo, "merge", "-q", "--no-ff", "-m", "merge the late forecast after the horizon", "late-forecast",
         date=LATE_MERGE_DATE)
    _git(repo, "push", "-q", "origin", "main")
    return LATE_PATH


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = parser.add_subparsers(dest="cmd", required=True)
    b = sub.add_parser("build")
    b.add_argument("dir")
    b.add_argument("--no-forecast", action="store_true")
    b.add_argument("--no-outcome", action="store_true")
    b.add_argument("--outcome-committed", default=OUTCOME_DATE)
    late = sub.add_parser("late")
    late.add_argument("dir")
    args = parser.parse_args(argv)
    if args.cmd == "build":
        build(Path(args.dir), with_forecast=not args.no_forecast, with_outcome=not args.no_outcome,
              outcome_committed=args.outcome_committed)
        print(f"fixture estate built under {args.dir} (a stand-in: throwaway repositories with bare origins)")
        return 0
    print(merge_late_forecast(Path(args.dir)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
