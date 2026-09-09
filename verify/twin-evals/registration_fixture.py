#!/usr/bin/env python3
"""Throwaway repositories for `verify/twin-evals/verify-scenario-registration.sh` (ticket 51).

One adopter with a bare origin, whose overlay carries **the edge the ticket names, planted**:
components `nb-refining-capacity` and `pq-cryptanalysis`, with the second declaring
`needs: [nb-refining-capacity]`. Neither exists in any real twin model -- that is the ticket's
finding -- so the only way to exercise the ruling on the pair it asks about is to plant it here and
say so. Every line the check prints about this fixture says fixture.

`unwatched-thing` extends the chain by one hop (`needs: [pq-cryptanalysis]`) and `island-thing` is
on no chain at all, so the difference between "not adjacent" and "not connected" can be MEASURED
rather than argued -- and `--no-needs` builds the same overlay with every `needs` list removed, so
a reachability set can be observed moving from empty to two components when one line of YAML
arrives. Everything this module's ruling says about dates it derives from git; before review F4
everything it said about reachability it derived from reading another module.

It also carries the shapes the ruling has to refuse: a scenario whose horizon is not after its own
authoring date, an override on a component no scenario names, an override whose number is rewritten
after it landed on the served ref, and a scenario whose question is rewritten after its own horizon
-- beside a scenario whose NOTE was appended and whose question was not, which re-registers just
the same and must not be reported as the question moving.

Dates are fixed and the commits are made with fixed committer dates, so first-parent history is the
same on every machine. `core.hooksPath` is written to the null device in every throwaway repository
and in its commit environment, for the reason ticket 93's fixture does it: a proof that depends on
whether a machine's secret scanner has quota left is not a proof.
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any

import yaml

ORG = "driftwood"
BASE_DATE = "2026-01-01T00:00:00+00:00"
OVERRIDE_DATE = "2026-02-01T00:00:00+00:00"
REWRITE_DATE = "2026-07-20T00:00:00+00:00"
HORIZON = "2026-06-30"

AFFECTED = [{
    "id": "the-planted-suppliers-workforce",
    "who": "The workforce of the planted supplier, not represented in this fixture model.",
    "consequence": "A fixture prices from the buyer's side only; nobody here carries their seat.",
}]

OVERRIDE_PATH = f"twin/orgs/{ORG}/claims/planted-supply-position.yaml"
ORPHAN_PATH = f"twin/orgs/{ORG}/claims/planted-orphan-position.yaml"
SCENARIO_PATH = f"twin/orgs/{ORG}/scenarios/planted-supply-2026.yaml"
BAD_HORIZON_PATH = f"twin/orgs/{ORG}/scenarios/planted-same-day-2026.yaml"


def _git(repo: Path, *args: str, date: str | None = None) -> str:
    env = dict(os.environ)
    env.update({
        "GIT_AUTHOR_NAME": "registration fixture", "GIT_AUTHOR_EMAIL": "fixture@example.invalid",
        "GIT_COMMITTER_NAME": "registration fixture", "GIT_COMMITTER_EMAIL": "fixture@example.invalid",
        "GIT_CONFIG_GLOBAL": os.devnull, "GIT_CONFIG_SYSTEM": os.devnull,
    })
    if date:
        env["GIT_AUTHOR_DATE"] = env["GIT_COMMITTER_DATE"] = date
    run = subprocess.run(["git", "-C", str(repo), *args], capture_output=True, text=True, env=env)
    if run.returncode != 0:
        raise SystemExit(f"git {' '.join(args)} failed in {repo}: {run.stderr.strip()}")
    return run.stdout


def _write(path: Path, doc: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(yaml.safe_dump(doc, sort_keys=False), encoding="utf-8")


def _commit_push(repo: Path, message: str, date: str) -> None:
    _git(repo, "add", "-A")
    _git(repo, "commit", "-q", "-m", message, date=date)
    _git(repo, "push", "-q", "-u", "origin", "main")


def override_doc(position: float = 0.55) -> dict[str, Any]:
    return {
        "id": "planted-supply-position", "kind": "override", "component": "pq-cryptanalysis",
        "evolution_position": position, "claimed_by": "model-steward", "evidence_grade": 4,
        "evidence": "a fixture override, planted by verify/twin-evals/registration_fixture.py",
    }


def build(root: Path, with_override: bool = True, with_needs: bool = True) -> Path:
    root = Path(root)
    root.mkdir(parents=True, exist_ok=True)
    repo, origin = root / ORG, root / f"{ORG}.origin.git"
    repo.mkdir(parents=True)
    _git(repo, "init", "-q", "-b", "main")
    _git(repo, "config", "core.hooksPath", os.devnull)
    _git(origin.parent, "init", "-q", "--bare", "-b", "main", str(origin))
    _git(repo, "remote", "add", "origin", str(origin))
    org = repo / "twin" / "orgs" / ORG
    _write(repo / "party.yaml", {"party": ORG, "roles": ["adopter"], "reporting_currency": "GBP"})
    _write(org / "meta.yaml", {"id": ORG, "unit": "overlay", "org": ORG, "world_ref": "fixture"})
    # THE PLANTED EDGE. Neither id is a component of any real twin model; the ticket's whole
    # finding is that the pair is two rows of platform's Wardley intel JSON naming one shared
    # links_risk. Planted here, and only here, so the ruling can be exercised on it.
    _write(org / "components" / "nb-refining-capacity.yaml", {
        "id": "nb-refining-capacity", "name": "planted refining capacity", "kind": "activity",
        "evolution": "product", "visibility": 0.2,
    })
    _write(org / "components" / "pq-cryptanalysis.yaml", {
        "id": "pq-cryptanalysis", "name": "planted cryptanalysis capability", "kind": "activity",
        "evolution": "custom-built", "visibility": 0.4,
        **({"needs": ["nb-refining-capacity"]} if with_needs else {}),
    })
    # The SECOND hop, and the reason it is here: reachability is transitive to blast.MAX_DEPTH and
    # adjacency is not. `unwatched-thing` is two hops from `nb-refining-capacity` and adjacent to
    # neither end of the ticket's pair, so the traversal reaches it and no edge between them says
    # so -- which is the shape review F2 found being reported as "no dependency, in either
    # direction".
    _write(org / "components" / "unwatched-thing.yaml", {
        "id": "unwatched-thing", "name": "a component no scenario names", "kind": "activity",
        "evolution": "product", "visibility": 0.3,
        **({"needs": ["pq-cryptanalysis"]} if with_needs else {}),
    })
    # A component nothing needs and which needs nothing: the pair that really is unrelated, so
    # `no-relation-in-this-model` is exercised on a pair the traversal genuinely cannot connect
    # rather than on one it was never asked about.
    _write(org / "components" / "island-thing.yaml", {
        "id": "island-thing", "name": "a component on no value chain here", "kind": "activity",
        "evolution": "product", "visibility": 0.1,
    })
    _write(repo / SCENARIO_PATH, {
        "id": "planted-supply-2026", "question": "Does the planted supplier fail inside the horizon?",
        "proposition": "a-planted-supplier-fails-within-the-horizon", "at": "2026-01-01",
        "horizon": HORIZON, "components": ["pq-cryptanalysis"], "world_models": ["reference-map"],
        "affected_parties": AFFECTED,
    })
    _write(repo / "twin" / "world" / "propositions" / "a-planted-supplier-fails-within-the-horizon.yaml", {
        "id": "a-planted-supplier-fails-within-the-horizon",
        "text": "A planted supplier fails to deliver within the horizon.",
    })
    _write(repo / "twin" / "world" / "world_models" / "reference-map.yaml", {
        "id": "reference-map", "name": "the fixture's reference map", "credence": 0.5,
        "beliefs": {"a-planted-supplier-fails-within-the-horizon": 0.2},
    })
    _commit_push(repo, "fixture adopter (planted)", BASE_DATE)
    if with_override:
        _write(repo / OVERRIDE_PATH, override_doc())
        _commit_push(repo, "fixture override (planted)", OVERRIDE_DATE)
    return repo


def bad_horizon(root: Path) -> str:
    """A scenario whose horizon is its own authoring date: nothing could EVER be registered
    against it, because registration is strictly before the outcome date."""
    repo = Path(root) / ORG
    _write(repo / BAD_HORIZON_PATH, {
        "id": "planted-same-day-2026", "question": "Does it resolve on the day it was asked?",
        "proposition": "a-planted-supplier-fails-within-the-horizon", "at": "2026-01-01",
        "horizon": "2026-01-01", "components": ["pq-cryptanalysis"], "world_models": ["reference-map"],
        "affected_parties": AFFECTED,
    })
    _commit_push(repo, "fixture: a question that resolves on the day it was asked", OVERRIDE_DATE)
    return BAD_HORIZON_PATH


def rewrite_override(root: Path) -> str:
    """The override's number, changed after the file was already on the served ref. Ticket 93's
    F1 applied to an override: the rewrite is a NEW claim and registers on the day of the rewrite."""
    repo = Path(root) / ORG
    _write(repo / OVERRIDE_PATH, override_doc(position=0.95))
    _commit_push(repo, "fixture: the override's number, moved after it landed", REWRITE_DATE)
    return OVERRIDE_PATH


def orphan_override(root: Path) -> str:
    """An override on a component no scenario in this overlay names: unscoreable, with a reason."""
    repo = Path(root) / ORG
    _write(repo / ORPHAN_PATH, {
        "id": "planted-orphan-position", "kind": "override", "component": "unwatched-thing",
        "evolution_position": 0.7, "claimed_by": "model-steward", "evidence_grade": 4,
        "evidence": "a fixture override on a component no question depends on",
    })
    _commit_push(repo, "fixture: an override nothing resolves", OVERRIDE_DATE)
    return ORPHAN_PATH


def rewrite_question(root: Path) -> str:
    """The scenario's question, rewritten after its own horizon has passed. Every score taken
    against it moves, and until this ticket nothing on the record said so."""
    repo = Path(root) / ORG
    _write(repo / SCENARIO_PATH, {
        "id": "planted-supply-2026", "question": "A DIFFERENT question, written after the answer was knowable.",
        "proposition": "a-planted-supplier-fails-within-the-horizon", "at": "2026-01-01",
        "horizon": HORIZON, "components": ["pq-cryptanalysis"], "world_models": ["reference-map"],
        "affected_parties": AFFECTED,
    })
    _commit_push(repo, "fixture: the question, rewritten after its own horizon", REWRITE_DATE)
    return SCENARIO_PATH


def append_note(root: Path) -> str:
    """A `note` appended to the entry after it landed, and NOTHING else touched.

    Still a rewrite -- the blob changed, so the file re-registers on the day of the edit -- but
    the QUESTION did not move. The override PR ecosystem ticket 51 writes does exactly this to
    driftwood's niobium entry, and a report that says only "rewritten" cannot tell the two apart
    (ticket 93 review G2, applied to the words instead of the numbers).
    """
    repo = Path(root) / ORG
    _write(repo / SCENARIO_PATH, {
        "id": "planted-supply-2026", "question": "Does the planted supplier fail inside the horizon?",
        "proposition": "a-planted-supplier-fails-within-the-horizon", "at": "2026-01-01",
        "horizon": HORIZON, "components": ["pq-cryptanalysis"], "world_models": ["reference-map"],
        "affected_parties": AFFECTED,
        "note": "a note appended after this entry landed; the question itself is untouched",
    })
    _commit_push(repo, "fixture: a note appended, the question untouched", REWRITE_DATE)
    return SCENARIO_PATH


RISK = "pq-harvest-now-decrypt-later"


def plant_platform(root: Path, cross_link: bool = False) -> Path:
    """A throwaway `platform` unit carrying the two Wardley intel rows the ticket reads.

    Decision 1's factual half is a claim about somebody ELSE's file: the two rows both name a FAIR
    risk id and never each other. `cross_link` builds the version where one row DOES name the
    other -- the shape ticket 23 recorded and this decision rests on not existing -- so the
    grading of that claim has a red to be measured against (review F5).
    """
    repo = Path(root) / "platform"
    intel = repo / "wardley" / "intel"
    intel.mkdir(parents=True, exist_ok=True)
    rows = [
        {"id": "nb-refining-capacity", "actor": "planted refiner", "evolution": "product",
         "velocity": 0.1, "links_risk": "pq-cryptanalysis" if cross_link else RISK},
        {"id": "pq-cryptanalysis", "actor": "planted analyst", "evolution": "custom-built",
         "velocity": 0.2, "links_risk": RISK},
    ]
    (intel / "market-intel.json").write_text(
        json.dumps({"components": rows}, indent=2) + "\n", encoding="utf-8")
    _git(repo.parent, "init", "-q", "-b", "main", str(repo))
    _git(repo, "config", "core.hooksPath", os.devnull)
    _git(repo, "add", "-A")
    _git(repo, "commit", "-q", "-m", "fixture platform intel (planted)", date=BASE_DATE)
    sha = _git(repo, "rev-parse", "HEAD").strip()
    _git(repo, "update-ref", "refs/remotes/origin/main", sha)
    return repo


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("command", choices=[
        "build", "bad-horizon", "rewrite-override", "orphan-override", "rewrite-question",
        "append-note", "platform", "platform-cross-linked"])
    parser.add_argument("root")
    parser.add_argument("--no-override", action="store_true")
    parser.add_argument("--no-needs", action="store_true",
                        help="the same overlay with every `needs` list removed: the graph WITHOUT "
                             "the planted edge, so a reachability set can be measured moving")
    args = parser.parse_args(argv)
    root = Path(args.root)
    if args.command == "build":
        print(build(root, with_override=not args.no_override, with_needs=not args.no_needs))
    elif args.command == "bad-horizon":
        print(bad_horizon(root))
    elif args.command == "rewrite-override":
        print(rewrite_override(root))
    elif args.command == "orphan-override":
        print(orphan_override(root))
    elif args.command == "append-note":
        print(append_note(root))
    elif args.command in ("platform", "platform-cross-linked"):
        print(plant_platform(root, cross_link=args.command == "platform-cross-linked"))
    else:
        print(rewrite_question(root))
    return 0


if __name__ == "__main__":
    sys.exit(main())
