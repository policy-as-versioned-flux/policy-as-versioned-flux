"""Depth grades as computed checklists.

A capability's grade is one line per acceptance criterion of its **owning decision ticket**,
each checked or not. `full` means every line is checked and is *derived* — it cannot be typed.
Self-declared grades are how "premature done" happens, and the guarantee that each ticket's full
acceptance criteria remain the yardstick has no enforcement without this (build ticket 03).

Criterion text is copied into the capability file so an artefact is self-describing, and is
re-checked against the decision ticket whenever the ticket tree is present — a checklist that
has quietly drifted from its yardstick is worse than no checklist.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml

from . import PACKAGE_DIR, REPO_DIR
from .canon import digest_of

CAPABILITIES_DIR = PACKAGE_DIR / "capabilities"
DECISION_TICKETS_DIR = REPO_DIR / ".scratch" / "twin" / "issues"

STUB, PARTIAL, FULL = "stub", "partial", "full"
_ORDER = {STUB: 0, PARTIAL: 1, FULL: 2}

_ITEM = re.compile(r"^- \[([ xX])\]\s+(.*)$")
_NESTED_ITEM = re.compile(r"^\s+- \[[ xX]\]")
_HEADING = re.compile(r"^#{1,6}\s")


class GradeError(RuntimeError):
    pass


def acceptance_criteria(ticket: str, tickets_dir: Path | None = None) -> list[str]:
    """The `## Acceptance criteria` list of a decision ticket, in order.

    Deliberately the *first* such heading: a resolved ticket also carries
    `## Acceptance criteria — all met`, which is the author's claim rather than the yardstick.
    """
    directory = tickets_dir or DECISION_TICKETS_DIR
    matches = sorted(directory.glob(f"{ticket}-*.md"))
    if not matches:
        raise GradeError(f"no decision ticket {ticket} under {directory}")
    lines = matches[0].read_text(encoding="utf-8").splitlines()

    try:
        start = next(i for i, line in enumerate(lines) if line.strip() == "## Acceptance criteria")
    except StopIteration:
        raise GradeError(f"decision ticket {ticket} has no '## Acceptance criteria' section") from None

    items: list[str] = []
    for line in lines[start + 1 :]:
        if _HEADING.match(line):
            break  # any heading, not just `## ` — a `### Notes` section is not more criteria
        if _NESTED_ITEM.match(line):
            # A nested checkbox would be glued onto its parent's text, silently collapsing
            # several criteria into one and shrinking the denominator every grade divides by.
            raise GradeError(
                f"decision ticket {ticket} has a nested checkbox in its acceptance criteria "
                f"({line.strip()!r}); flatten it — the list is the yardstick and it has to be countable"
            )
        item = _ITEM.match(line)
        if item:
            items.append(item.group(2).strip())
        elif items and line.startswith(" ") and line.strip():
            items[-1] += " " + line.strip()
    if not items:
        raise GradeError(f"decision ticket {ticket} lists no acceptance criteria")
    return items


@dataclass(frozen=True)
class Criterion:
    index: int
    text: str
    checked: bool
    evidence: str
    ticked_by: str

    def as_dict(self) -> dict[str, Any]:
        out: dict[str, Any] = {"index": self.index, "text": self.text, "checked": self.checked}
        if self.checked:
            out["evidence"] = self.evidence
            out["ticked_by"] = self.ticked_by
        return out


@dataclass(frozen=True)
class DepthGrade:
    capability: str
    owning_ticket: str
    criteria: tuple[Criterion, ...]

    @property
    def grade(self) -> str:
        """Computed. There is no setter, and no file may supply one."""
        checked = sum(1 for c in self.criteria if c.checked)
        if checked == len(self.criteria):
            return FULL
        return STUB if checked == 0 else PARTIAL

    @property
    def unchecked(self) -> tuple[Criterion, ...]:
        return tuple(c for c in self.criteria if not c.checked)

    def summary(self) -> dict[str, Any]:
        """What travels with the capability at runtime, so a partial capability announces itself."""
        return {
            "grade": self.grade,
            "owning_ticket": self.owning_ticket,
            "checked": sum(1 for c in self.criteria if c.checked),
            "total": len(self.criteria),
            "unchecked": [{"index": c.index, "text": c.text} for c in self.unchecked],
        }


def _load_one(path: Path, tickets_dir: Path | None) -> DepthGrade:
    raw = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(raw, dict):
        raise GradeError(f"{path.name}: expected a mapping")

    name = raw.get("capability")
    owning = raw.get("owning_ticket")
    if not name or not owning:
        raise GradeError(f"{path.name}: needs `capability` and `owning_ticket`")
    owning = str(owning)

    declared = raw.get("criteria")
    if not isinstance(declared, list) or not declared:
        # Ticket 03: a capability with no depth grade fails to load.
        raise GradeError(f"{path.name}: capability {name!r} declares no depth-grade checklist")

    criteria = tuple(
        Criterion(
            index=int(entry["index"]),
            text=str(entry["text"]).strip(),
            checked=bool(entry.get("checked", False)),
            evidence=str(entry.get("evidence", "")).strip(),
            ticked_by=str(entry.get("ticked_by", "")).strip(),
        )
        for entry in declared
    )
    graded = DepthGrade(capability=str(name), owning_ticket=owning, criteria=criteria)

    if "grade" in raw:
        # A hand-edited grade. Name the criteria that make the claim false rather than just refusing.
        unchecked = ", ".join(f"AC {c.index} ({c.text})" for c in graded.unchecked) or "none"
        raise GradeError(
            f"{path.name}: capability {name!r} types a grade ({raw['grade']!r}); grades are computed. "
            f"Computed grade is {graded.grade!r}; unchecked criteria: {unchecked}"
        )

    for c in graded.criteria:
        if c.checked and not (c.evidence and c.ticked_by):
            raise GradeError(
                f"{path.name}: capability {name!r} AC {c.index} is checked without "
                "`evidence` and `ticked_by` — a tick with no witness is a self-declared grade"
            )

    _validate_against_ticket(path, graded, tickets_dir)
    return graded


def _validate_against_ticket(path: Path, graded: DepthGrade, tickets_dir: Path | None) -> None:
    """The owning ticket's criteria remain the yardstick; drift from them is a failure."""
    directory = tickets_dir or DECISION_TICKETS_DIR
    if not directory.is_dir():
        return  # installed away from the ticket tree; the copied text is all we have
    expected = acceptance_criteria(graded.owning_ticket, directory)
    if len(expected) != len(graded.criteria):
        raise GradeError(
            f"{path.name}: decision ticket {graded.owning_ticket} has {len(expected)} acceptance "
            f"criteria, checklist has {len(graded.criteria)} — the checklist has drifted from the yardstick"
        )
    for i, (c, want) in enumerate(zip(graded.criteria, expected, strict=True), start=1):
        if c.index != i:
            raise GradeError(f"{path.name}: criteria must be indexed 1..N in order; saw {c.index} at position {i}")
        if c.text != want:
            raise GradeError(
                f"{path.name}: AC {c.index} text has drifted from decision ticket "
                f"{graded.owning_ticket}\n  checklist: {c.text}\n  ticket:    {want}"
            )


class Capabilities:
    """The loaded set. Asking for one that has no depth grade is an error, not a default."""

    def __init__(self, graded: dict[str, DepthGrade], digest: str) -> None:
        self._graded = graded
        self.digest = digest

    @classmethod
    def load(cls, directory: Path | None = None, tickets_dir: Path | None = None) -> "Capabilities":
        directory = directory or CAPABILITIES_DIR
        graded = {}
        for path in sorted(directory.glob("*.yaml")):
            g = _load_one(path, tickets_dir)
            if g.capability in graded:
                raise GradeError(f"capability {g.capability!r} declared twice")
            graded[g.capability] = g
        if not graded:
            raise GradeError(f"no capability depth grades under {directory}")
        digest = digest_of({name: g.summary() for name, g in sorted(graded.items())})
        return cls(graded, digest)

    def __contains__(self, name: object) -> bool:
        return name in self._graded

    def __iter__(self):
        return iter(sorted(self._graded.values(), key=lambda g: g.capability))

    def require(self, name: str) -> DepthGrade:
        if name not in self._graded:
            raise GradeError(
                f"capability {name!r} has no depth grade; add twin/capabilities/<ticket>-{name}.yaml"
            )
        return self._graded[name]

    def aggregate(self) -> tuple[int, int]:
        """Ticked and total across every capability (build ticket 70).

        A per-capability grade was computed from the day ticket 03 built the checklists; the
        aggregate over them never was, so the published figure was a hand-sum and went stale twice.
        Trivial arithmetic — which is the point. It was never wrong because it was hard.
        """
        return (
            sum(1 for g in self for c in g.criteria if c.checked),
            sum(len(g.criteria) for g in self),
        )

    def depth_block(self, names: list[str]) -> dict[str, Any]:
        """The `depth` slot of an artefact envelope: every capability that produced it."""
        used = {n: self.require(n).summary() for n in sorted(set(names))}
        overall = min((v["grade"] for v in used.values()), key=lambda g: _ORDER[g], default=STUB)
        return {"grade": overall, "capabilities": used}


def worst(grades: list[str]) -> str:
    return min(grades, key=lambda g: _ORDER[g], default=STUB)
