"""The evidence ladder, the use-gate that reads it, and the regrade record.

Build tickets 18 and 19. Two things live here because they are one mechanism:

**The ladder** (`twin/evidence-ladder.yaml`) is five typed grades with written admission criteria,
versioned. It is data rather than code so that a reader who does not write Python can see what
each rung admits, and so that changing a rung is a diff against a version number.

**The gate** is a single threshold on that ladder: only grades 1-2 may price a scored forecast.
Grade 5 is a model assertion, which is exactly where parametric contamination hides — an edge
asserted from training data looks identical to a well-evidenced one unless something forces the
distinction. The threshold is published in the same versioned document, so changing it is as
visible as changing the constraint set.

**The regrade record** is what makes a grade immutable. A grade travels with its claim, so an
edited grade is an edited claim; a regrade event says who moved it, when, from what, to what, and
why. Two guards, at different depths:

* At load, the recorded chain must be contiguous and must terminate at the grade the file
  declares. A chain that stops short of the current grade means a grade moved unrecorded.
* At `twin validate`, the file's **git history** is read and every observed change to a grade must
  be covered by a regrade event. That is the one that bites on the first unrecorded edit, before
  any chain exists to be contiguous with.

`ponytail:` the history check does not follow renames, so moving a file and changing its grade in
one commit reads as a new file at its original grade. Naming the limit rather than implying a
completeness the check does not have; `git log --follow` per file is the upgrade if it matters.
"""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Any

import yaml

from . import PACKAGE_DIR
from .canon import digest_of
from .schema import EVIDENCE_GRADES

LADDER_PATH = PACKAGE_DIR / "evidence-ladder.yaml"
SCHEMA = "twin.evidence-ladder/v1"

STRENGTHENED, WEAKENED = "strengthened", "weakened"

# Collections whose objects carry an evidence grade, and are therefore regradeable.
GRADED_COLLECTIONS = ("edges", "claims")


class EvidenceError(RuntimeError):
    """The ladder does not say what it must, or a grade moved without a record."""


@lru_cache(maxsize=8)
def ladder(path: Path | None = None) -> dict[str, Any]:
    """The versioned ladder, validated on read.

    Validated here rather than trusted: a ladder that has quietly lost a rung, or whose threshold
    names a grade that does not exist, would gate on nothing while still looking published.

    `ponytail:` cached per path, because every emitted causal edge asks for a rung name and the
    ladder is immutable within a process. A test that rewrites a ladder file in place will see
    the first version; write a new temp file instead.
    """
    source = path or LADDER_PATH
    doc = yaml.safe_load(source.read_text(encoding="utf-8"))
    if not isinstance(doc, dict) or doc.get("schema") != SCHEMA:
        raise EvidenceError(f"{source}: not a {SCHEMA} document")
    grades = doc.get("grades")
    if not isinstance(grades, list):
        raise EvidenceError(f"{source}: declares no grades")
    if tuple(int(g["grade"]) for g in grades) != EVIDENCE_GRADES:
        raise EvidenceError(
            f"{source}: the ladder runs {[g.get('grade') for g in grades]}, the schema admits "
            f"{list(EVIDENCE_GRADES)} — a rung with no grade, or a grade with no rung"
        )
    for rung_doc in grades:
        for field in ("name", "admits", "example"):
            if not str(rung_doc.get(field, "")).strip():
                raise EvidenceError(
                    f"{source}: grade {rung_doc.get('grade')} declares no {field}. A rung with no "
                    "written admission criterion admits anything."
                )
        if not isinstance(rung_doc.get("may_price"), bool):
            raise EvidenceError(f"{source}: grade {rung_doc.get('grade')} does not say whether it may price")
    # `bool` excluded explicitly, as everywhere else a grade is read: `True == 1` in Python, so
    # `pricing_threshold: true` would pass a bare membership test and silently mean the strongest
    # rung. A threshold set by a typo is a gate nobody chose.
    for field in ("pricing_threshold", "path_admission_threshold"):
        value = doc.get(field)
        if isinstance(value, bool) or value not in EVIDENCE_GRADES:
            raise EvidenceError(
                f"{source}: {field} {value!r} is not a grade on this ladder. It decides what may "
                "carry a number, so a ladder that does not state one gates on nothing while still "
                "looking published."
            )
    threshold = doc["pricing_threshold"]
    for rung_doc in grades:
        if bool(rung_doc["may_price"]) != (int(rung_doc["grade"]) <= int(threshold)):
            raise EvidenceError(
                f"{source}: grade {rung_doc['grade']} says may_price {rung_doc['may_price']!r}, "
                f"which disagrees with pricing_threshold {threshold}"
            )
    if set(doc.get("directions") or {}) != {STRENGTHENED, WEAKENED}:
        raise EvidenceError(f"{source}: a regrade has exactly two directions, {STRENGTHENED} and {WEAKENED}")
    return doc


def threshold(path: Path | None = None) -> int:
    return int(ladder(path)["pricing_threshold"])


def admission_threshold(path: Path | None = None) -> int:
    """The grade a causal path to cash flow must hold to admit an impact to the £ (ticket 29).

    A separate threshold rather than `pricing_threshold` reused, so that widening the currency is
    an act somebody has to perform rather than a side effect of widening the use-gate.
    """
    return int(ladder(path)["path_admission_threshold"])


def rung(grade: int) -> dict[str, Any]:
    for entry in ladder()["grades"]:
        if int(entry["grade"]) == int(grade):
            return dict(entry)
    raise EvidenceError(f"grade {grade!r} is not on the ladder")


def may_price(grade: int, path: Path | None = None) -> bool:
    """The whole use-gate. Only a grade at or inside the published threshold prices anything."""
    return int(grade) <= threshold(path)


def pin(path: Path | None = None) -> dict[str, Any]:
    """Which ladder a gate was applied against: its version, its threshold and its exact content.

    Carried by every artefact that gates, for the reason the role register is pinned in a
    signature — a threshold that moved later must not silently change what an old gate meant.
    """
    doc = ladder(path)
    return {
        "version": int(doc["version"]),
        "pricing_threshold": int(doc["pricing_threshold"]),
        "path_admission_threshold": int(doc["path_admission_threshold"]),
        "digest": digest_of(doc),
    }


def published() -> dict[str, Any]:
    """The ladder as it goes into an artefact: the rungs, their admission criteria, the gate."""
    doc = ladder()
    return {
        "pin": pin(),
        "rule": (
            f"only grades 1-{doc['pricing_threshold']} may price a scored forecast; a weaker path "
            "is reported as an unpriced structural blast radius"
        ),
        "admission_rule": (
            f"an impact enters the £ only through a causal path to a declared cash flow whose "
            f"weakest hop is graded 1-{doc['path_admission_threshold']}; the boundary is derived "
            "from the graph and nobody can declare something priceable"
        ),
        "grades": [
            {
                "grade": int(g["grade"]),
                "name": str(g["name"]),
                "admits": str(g["admits"]).strip(),
                "example": str(g["example"]).strip(),
                "may_price": bool(g["may_price"]),
            }
            for g in doc["grades"]
        ],
    }


# -- the regrade record ----------------------------------------------------------------------


def direction(from_grade: int, to_grade: int) -> str:
    """Named, never implied: `up` is ambiguous on a ladder whose strongest rung is numbered 1."""
    if int(to_grade) == int(from_grade):
        raise EvidenceError("a regrade that changes nothing is not a regrade")
    return STRENGTHENED if int(to_grade) < int(from_grade) else WEAKENED


def record(regrade: dict[str, Any]) -> dict[str, Any]:
    """One regrade, as it appears in an artefact. `direction` is derived, never authored."""
    from_grade, to_grade = int(regrade["from_grade"]), int(regrade["to_grade"])
    return {
        "id": str(regrade["id"]),
        "subject": str(regrade["subject"]),
        "from_grade": from_grade,
        "to_grade": to_grade,
        "direction": direction(from_grade, to_grade),
        "regraded_on": str(regrade["regraded_on"]),
        "by_role": str(regrade["by_role"]),
        "reason": str(regrade["reason"]),
        "evidence": str(regrade["evidence"]),
    }


def chain_for(subject: str, regrades: dict[str, dict[str, Any]]) -> list[dict[str, Any]]:
    """This subject's regrades, oldest first. Ties broken by id so the order is deterministic."""
    mine = [r for r in regrades.values() if str(r.get("subject")) == subject]
    return sorted(mine, key=lambda r: (str(r["regraded_on"]), str(r["id"])))


def check_chain(subject: str, current_grade: int, chain: list[dict[str, Any]], where: str) -> None:
    """The recorded chain is contiguous and ends where the file now stands.

    A chain that ends anywhere else means a grade moved and nobody wrote it down — which is the
    thing the regrade record exists to make impossible.
    """
    if not chain:
        return
    for earlier, later in zip(chain, chain[1:]):
        if int(later["from_grade"]) != int(earlier["to_grade"]):
            raise EvidenceError(
                f"{where}: regrade {later['id']!r} starts at grade {later['from_grade']}, but "
                f"{earlier['id']!r} left {subject!r} at grade {earlier['to_grade']} — the record "
                "has a gap, so some part of this claim's history is unaccounted for"
            )
    last = int(chain[-1]["to_grade"])
    if last != int(current_grade):
        raise EvidenceError(
            f"{where}: {subject!r} declares evidence grade {current_grade}, but its last regrade "
            f"({chain[-1]['id']!r}) left it at {last}. A grade is immutable without a regrade "
            "event recording who moved it and why."
        )


def history_violations(repo: Any, unit_path: str, tree: str, regrades: dict[str, dict[str, Any]]) -> list[str]:
    """Every change an evidence grade has ever undergone, checked against the regrade record.

    The chain check above catches a grade that has moved *since* a regrade was recorded. This
    catches the first unrecorded move, where there is no chain yet — by reading what the file said
    at every commit that touched it.
    """
    violations: list[str] = []
    for subdir in GRADED_COLLECTIONS:
        for rel in repo.list_tree(tree, subdir):
            if not rel.endswith((".yaml", ".yml")):
                continue
            full = f"{unit_path}/{rel}" if unit_path else rel
            observed: list[tuple[str, str, int]] = []
            for commit in repo.commits_touching(full):
                seen = _graded_at(repo, commit, full)
                if seen is None:
                    continue
                if not observed or observed[-1][2] != seen[1]:
                    observed.append((commit, seen[0], seen[1]))
            for (_, _, was), (commit, subject, now) in zip(observed, observed[1:]):
                if not _covered(regrades, subject, was, now):
                    violations.append(
                        f"{full}: evidence grade of {subject!r} moved {was} -> {now} at commit "
                        f"{commit[:12]} with no regrade event recording who moved it and why"
                    )
    return sorted(violations)


def _graded_at(repo: Any, commit: str, full: str) -> tuple[str, int] | None:
    """The (id, evidence grade) this file declared at that commit, or None if it declared none."""
    from .repo import RepoError

    try:
        doc = repo.read_yaml_at(commit, full)
    except RepoError:
        return None  # the file did not exist at that commit, or was not readable as YAML
    grade, ident = doc.get("evidence_grade"), doc.get("id")
    if not isinstance(grade, int) or isinstance(grade, bool) or not ident:
        return None
    return str(ident), int(grade)


def _covered(regrades: dict[str, dict[str, Any]], subject: str, was: int, now: int) -> bool:
    return any(
        str(r.get("subject")) == subject and int(r["from_grade"]) == was and int(r["to_grade"]) == now
        for r in regrades.values()
    )
