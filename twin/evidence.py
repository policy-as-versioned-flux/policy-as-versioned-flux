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
from typing import Any, Callable

import yaml

from . import PACKAGE_DIR
from .canon import digest_of
from .schema import EVIDENCE_GRADES

LADDER_PATH = PACKAGE_DIR / "evidence-ladder.yaml"
SCHEMA = "twin.evidence-ladder/v1"

STRENGTHENED, WEAKENED = "strengthened", "weakened"

# Collections whose objects carry an evidence grade, and are therefore regradeable.
GRADED_COLLECTIONS = ("edges", "claims")

# The pricing thresholds a party may declare on its own signed party artefact (ADR-0032 point 2;
# eco-system ticket 141). `appetite.pricing_threshold` on `party.yaml` is 2 or 3 and nothing
# else: grade 4 is an expert's say-so and grade 5 a model's, and neither may price for anybody.
# Absent means the ladder's own default. The set is spelled here beside the ladder rather than in
# `evidence-ladder.yaml` because it is not a property of a rung: it is the range within which a
# risk-bearer may move the gate for its own money, and the platform's party schema
# (`party/schema.json`) closes the same enum on the signing side.
DECLARABLE_THRESHOLDS = (2, 3)
DECLARATION_FIELD = "appetite.pricing_threshold"
# Where a threshold came from, carried by every artefact that gated on one.
LADDER_DEFAULT = "the ladder's published default"
PARTY_DECLARATION = f"the party's signed declaration ({DECLARATION_FIELD})"


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


# The same function under a name no keyword argument shadows: `may_price(grade, threshold=3)`
# takes a party's declaration under the name a reader expects, and reads the ladder through this.
_published_threshold = threshold


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


def may_price(grade: int, path: Path | None = None, *, threshold: int | None = None) -> bool:
    """The whole use-gate. Only a grade at or inside the threshold in force prices anything.

    The threshold in force is the ladder's published default unless the caller passes the one a
    party declared on its own signed artefact (`declared_threshold`). Passed explicitly, never
    read from ambient state: a gate that looked a declaration up for itself would price one
    party's valuation against another party's choice the first time two overlays shared a
    process. A caller that has no declaration passes nothing and gets the ladder.
    """
    if threshold is None:
        return int(grade) <= _published_threshold(path)
    return int(grade) <= check_threshold(threshold)


def check_threshold(value: Any) -> int:
    """A threshold a caller supplies is one a party may declare, or it is refused by name.

    `bool` excluded explicitly, as everywhere a grade is read: `True == 1` in Python, so a
    threshold of `true` would otherwise mean the strongest rung.
    """
    if isinstance(value, bool) or not isinstance(value, int) or value not in DECLARABLE_THRESHOLDS:
        raise EvidenceError(
            f"pricing threshold {value!r} is not one a party may declare; {DECLARATION_FIELD} "
            f"admits {', '.join(str(t) for t in DECLARABLE_THRESHOLDS)} and nothing else "
            "(ADR-0032 point 2: grade 4 is an expert's say-so and grade 5 a model's, and neither "
            "may price)"
        )
    return int(value)


def declared_threshold(party: Any, where: str = "party.yaml") -> int:
    """The pricing threshold a party's signed artefact declares, or the ladder's default.

    Reads `appetite.pricing_threshold` off a parsed `party.yaml` (ADR-0032 point 2; eco-system
    ticket 141). The declaration governs both of this party's thresholds, the use-gate and the
    path admission gate: a party that prices on published work prices on it end to end, and a
    valuation admitted at grade 3 through a path refused at grade 3 would be a boundary nobody
    chose.

    Absent means the ladder's own default, so every overlay that does not declare behaves exactly
    as it did before the declaration existed. Present and outside `DECLARABLE_THRESHOLDS`, or
    not an integer, it is refused by name rather than clamped: the platform's party schema
    refuses the same values on the signing side, and a reader that quietly corrected a signed
    file would be reading a file nobody signed.
    """
    if party is None:
        return threshold()
    if not isinstance(party, dict):
        raise EvidenceError(f"{where}: a party artefact is a mapping, got {type(party).__name__}")
    appetite = party.get("appetite")
    if appetite is None:
        return threshold()
    if not isinstance(appetite, dict):
        raise EvidenceError(f"{where}: appetite is not a mapping, so no declaration can be read from it")
    if "pricing_threshold" not in appetite:
        return threshold()
    try:
        return check_threshold(appetite["pricing_threshold"])
    except EvidenceError as exc:
        raise EvidenceError(f"{where}: {exc}") from None


def applied(pricing: int | None = None, admission: int | None = None) -> dict[str, Any]:
    """The thresholds a gate actually applied, and where each came from.

    Carried beside `pin()` in every artefact that gates: the pin says what the ladder published,
    this says what was applied to this party's money and why. Where nothing was declared the two
    agree and `basis` says so; where a party declared, a reader can see that a grade-3 price
    rests on the party's signed choice and not on a ladder that moved.
    """
    pricing_applied = threshold() if pricing is None else check_threshold(pricing)
    admission_applied = admission_threshold() if admission is None else check_threshold(admission)
    # The basis is read off the values, not off how the caller spelled them: the only way the
    # thresholds in force differ from the ladder's is a party's signed declaration, and a party
    # that declares the ladder's own number is pricing at the ladder's number.
    moved = pricing_applied != threshold() or admission_applied != admission_threshold()
    return {
        "pricing_threshold": pricing_applied,
        "path_admission_threshold": admission_applied,
        "basis": PARTY_DECLARATION if moved else LADDER_DEFAULT,
    }


def weakest(*grades: int | None) -> int | None:
    """The weakest grade among those a figure rests on: the one operation on grades this system
    admits (ADR-0024 point 6, the ordinal-arithmetic ruling; ADR-0032 point 3).

    An order statistic, not arithmetic: a price that rests on a grade-2 path and a grade-3
    valuation rests on grade 3, and no sum, mean or weight of the two is ever taken. `None`
    inputs are skipped rather than treated as a grade, because a path with no graded hop has no
    grade to be weakest; all-`None` returns `None` for the same reason.
    """
    held = [int(g) for g in grades if g is not None and not isinstance(g, bool)]
    if not held:
        return None
    for g in held:
        if g not in EVIDENCE_GRADES:
            raise EvidenceError(f"grade {g!r} is not on the ladder, so nothing can rest on it")
    return max(held)


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


def published(pricing: int | None = None, admission: int | None = None) -> dict[str, Any]:
    """The ladder as it goes into an artefact: the rungs, their admission criteria, the gate.

    `pricing` and `admission` are the thresholds the caller applied (eco-system ticket 141): a
    body that prices passes the ones in force for its party, and then carries `applied`, both
    figures and their basis, beside the ladder's own pin, with the rules worded for what was
    applied. A traversal that passes neither publishes the ladder alone, exactly as before.
    """
    doc = ladder()
    in_force = applied(pricing, admission)
    record = {"applied": in_force} if pricing is not None or admission is not None else {}
    return {
        "pin": pin(),
        **record,
        "rule": (
            f"only grades 1-{in_force['pricing_threshold']} may price a scored forecast; a weaker "
            "path is reported as an unpriced structural blast radius"
        ),
        "admission_rule": (
            f"an impact enters the £ only through a causal path to a declared cash flow whose "
            f"weakest hop is graded 1-{in_force['path_admission_threshold']}; the boundary is "
            "derived from the graph and nobody can declare something priceable"
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


def unrecorded_changes(
    repo: Any,
    unit_path: str,
    tree: str,
    subdirs: tuple[str, ...],
    read_at: Callable[[Any, str, str], tuple[str, Any] | None],
) -> list[tuple[str, str, Any, Any, str]]:
    """Every observed change of a graded value, as `(path, subject, was, now, commit)`.

    The walk rather than the judgement: it reads what each file declared at every commit that
    touched it and reports where that value changed. Shared with `twin/enforcement.py`, whose
    enforcement grades move under exactly the same rule and would otherwise carry a second copy of
    this loop — and a second copy of a check like this is how one of them quietly stops biting.
    """
    changes: list[tuple[str, str, Any, Any, str]] = []
    for subdir in subdirs:
        for rel in repo.list_tree(tree, subdir):
            if not rel.endswith((".yaml", ".yml")):
                continue
            full = f"{unit_path}/{rel}" if unit_path else rel
            observed: list[tuple[str, str, Any]] = []
            for commit in repo.commits_touching(full):
                seen = read_at(repo, commit, full)
                if seen is None:
                    continue
                if not observed or observed[-1][2] != seen[1]:
                    observed.append((commit, seen[0], seen[1]))
            for (_, _, was), (commit, subject, now) in zip(observed, observed[1:]):
                changes.append((full, subject, was, now, commit))
    return changes


def history_violations(repo: Any, unit_path: str, tree: str, regrades: dict[str, dict[str, Any]]) -> list[str]:
    """Every change an evidence grade has ever undergone, checked against the regrade record.

    The chain check above catches a grade that has moved *since* a regrade was recorded. This
    catches the first unrecorded move, where there is no chain yet — by reading what the file said
    at every commit that touched it.
    """
    return sorted(
        f"{full}: evidence grade of {subject!r} moved {was} -> {now} at commit "
        f"{commit[:12]} with no regrade event recording who moved it and why"
        for full, subject, was, now, commit in unrecorded_changes(
            repo, unit_path, tree, GRADED_COLLECTIONS, _graded_at
        )
        if not _covered(regrades, subject, was, now)
    )


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
