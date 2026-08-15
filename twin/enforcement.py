"""Graded enforcement, and posture-as-identity narrowed to what the evidence supports.

Build ticket 67, from decision ticket 18 Q4. Both were **prior-estate hypotheses** rather than
findings: the old estate asserted them and built them. Tested against the risk basis they come out
differently, and this module is where the difference is structural rather than stated.

## Graded enforcement survives, and needs no special status

A control that modifies a FAIR factor **by degree rather than binary** is what graded enforcement
is, and the £ engine already prices partial mitigation through the control's own evidence-graded
`mitigates` claim (build ticket 30). So the ladder here orders **consequence** and prices nothing:
`twin/enforcement-grades.yaml` carries no number on any rung, and the loader refuses one.

That refusal is the load-bearing half. A reduction per rung would be a free multiplier — tighten
the rung, earn more credit, with nothing evidencing it — which is precisely the unfalsifiable
claim the mitigation grade exists to stop. **Moving a control up a rung earns nothing on its own;
it earns what somebody can evidence at the new rung.**

`block` is the bottom rung of four rather than the mechanism, which is the whole of "a spectrum
rather than a cliff edge".

## Posture-as-identity survives narrowed, and the narrowing is computed

Decision ticket 18 Q4: valid as an *implementation* of "provably in force" for machine-enforceable
controls, **not** as a governance philosophy. So no author declares it. A control **qualifies** —
by rule, from two declared facts — or it is excluded, by name, with the reason attached:

1. its rung **changes the outcome**, because an identity stamped by a control that leaves the
   outcome alone attests that the control ran, never that anything was in force; and
2. the posture is **stamped by something that is not the subject**, because the estate's own trust
   boundary is only worth anything while the workload has no write path to its own label.

Everything else is an exclusion, listed in `POSTURE_EXCLUSIONS` and published in the artefact.

## Moving a control between rungs

Versioned like an evidence grade and for the same reason: a rung that travels with a control means
an edited rung is an edited control. `enforcement_moves` records who moved it, when, from what, to
what and why; the chain must be contiguous and end where the control now stands; and `twin
validate` reads the file's **git history**, which is the half that catches the first unrecorded
move, before any chain exists to be inconsistent with.

Signed at the level this repository can actually sign: the published posture artefact is
**authored** and carries a human signature bound to a registered role, and every move names a
registered role. `ponytail:` the git commit that carries a move is *not* keyless-signed —
`estate/verify/provenance/verify-provenance.sh` records that this repository's commits are not —
so "signed" attaches to the artefact and the role binding, not to the commit. The upgrade is the
one decision ticket 14 already names, and it is the same limit build ticket 66 reported on the
dependency pins rather than letting the word carry weight the files do not support.
"""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Any

import yaml

from . import PACKAGE_DIR
from .canon import digest_of, walk_values

LADDER_PATH = PACKAGE_DIR / "enforcement-grades.yaml"
SCHEMA = "twin.enforcement-grades/v1"
KIND = "enforcement-posture"
CAPABILITY = "enactment"

# Who stands behind where a control sits. Reused rather than registered fresh: the rung a control
# occupies is a committed property of the model repository, which is what this role is already
# accountable for.
ROLE = "model-steward"

TIGHTENED, LOOSENED = "tightened", "loosened"

# What a control with no `enforcement` block reads as in the git-history check. Not a rung, and
# deliberately not a valid one: no move record can name it, so losing a rung can never be covered
# and is always reported.
NO_RUNG = "(no rung)"

# The only numeric field a rung may carry. Anything else numeric would be a price on a rung, and
# a price on a rung is credit nobody evidenced.
RANK = "rank"

# The cases posture-as-identity does *not* cover, named rather than left to be discovered. Each
# one is a case the prior estate's version of the claim would have swept in.
POSTURE_EXCLUSIONS: tuple[dict[str, str], ...] = (
    {
        "case": "a lever that is not code",
        "excluded_because": (
            "there is no enforcement point to bind an identity to. A pay rise, a supplier switch "
            "or a process change cannot be a path segment in an SVID, and most levers are these "
            "— which is the same finding that narrowed policy-as-versioned-dependency itself"
        ),
    },
    {
        "case": "a control at a rung that does not change the outcome",
        "excluded_because": (
            "an identity stamped by an observing or warning control attests that the control ran, "
            "never that anything was in force. The action would have proceeded identically"
        ),
    },
    {
        "case": "a posture the subject can write",
        "excluded_because": (
            "the identity then carries the subject's own claim about itself. The estate's trust "
            "boundary exists for this: the label is worth something only while the workload has "
            "no write path to it, so a control with no trusted stamper is excluded by rule"
        ),
    },
    {
        "case": "posture-as-identity as a governance philosophy",
        "excluded_because": (
            "decision ticket 18 Q4 admits it as an implementation of 'provably in force' for the "
            "machine-enforceable subset, and refuses it as the shape of governance — the same "
            "narrowing policy-as-code got, for the same reason: most levers are not code"
        ),
    },
    {
        "case": "proof that a control is in force *now*",
        "excluded_because": (
            "the identity attests the posture at issue, not since. Whether continuous proof of "
            "force is required at all is build ticket 65's pre-registered question and is open"
        ),
    },
)

GRADE_NEVER_PRICES = (
    "A rung orders consequence and carries no number. The £ comes from the control's own "
    "evidence-graded `mitigates` claim, so moving a control up a rung earns nothing on its own — "
    "it earns what somebody can evidence at the new rung."
)


class EnforcementError(RuntimeError):
    """The ladder does not say what it must, or a rung moved without a record."""


@lru_cache(maxsize=8)
def ladder(path: Path | None = None) -> dict[str, Any]:
    """The versioned ladder, validated on read.

    Validated here rather than trusted, for the reason the evidence ladder is: a ladder that has
    quietly grown a number on a rung would price enforcement without anybody deciding to.
    """
    source = path or LADDER_PATH
    doc = yaml.safe_load(source.read_text(encoding="utf-8"))
    if not isinstance(doc, dict) or doc.get("schema") != SCHEMA:
        raise EnforcementError(f"{source}: not a {SCHEMA} document")
    grades = doc.get("grades")
    if not isinstance(grades, list) or len(grades) < 2:
        raise EnforcementError(
            f"{source}: a ladder with fewer than two rungs is a cliff edge with extra steps"
        )
    ranks = [int(g.get(RANK, 0)) for g in grades]
    if ranks != list(range(1, len(grades) + 1)):
        raise EnforcementError(
            f"{source}: ranks {ranks} are not 1..{len(grades)} in order. The order is what makes "
            "'tightened' and 'loosened' derivable rather than authored."
        )
    for rung_doc in grades:
        for field in ("grade", "admits", "does_not", "realised_by"):
            if not str(rung_doc.get(field, "")).strip():
                raise EnforcementError(
                    f"{source}: rung {rung_doc.get('grade')!r} declares no {field}. A rung with no "
                    "written admission criterion admits anything, and one with no stated "
                    "realisation implies one it may not have."
                )
        if not isinstance(rung_doc.get("changes_the_outcome"), bool):
            raise EnforcementError(
                f"{source}: rung {rung_doc.get('grade')!r} does not say whether it changes the "
                "outcome, which is the property posture-as-identity is scoped by"
            )
        # At any depth, not just at the top of the rung: a `run_cost: {gbp: 500}` is the same
        # free multiplier as a bare `reduction: 0.4`, and a flat key scan would admit it. Same
        # move `refuse_special_category` makes about a slot that must not exist anywhere.
        priced = sorted(
            path
            for path, value in walk_values(rung_doc)
            if path != RANK and isinstance(value, (int, float)) and not isinstance(value, bool)
        )
        if priced:
            raise EnforcementError(
                f"{source}: rung {rung_doc.get('grade')!r} carries {', '.join(priced)}. A number on "
                "a rung is a reduction nobody evidenced — tighten the rung, earn more credit. The "
                "£ comes from the control's own graded mitigation claim and from nowhere else."
            )
    if not (isinstance(doc.get("version"), int) and not isinstance(doc.get("version"), bool)):
        raise EnforcementError(f"{source}: declares no integer version, so a change to it is invisible")
    if not any(bool(g["changes_the_outcome"]) for g in grades):
        raise EnforcementError(f"{source}: no rung changes the outcome, so nothing here enforces anything")
    if not any(not bool(g["changes_the_outcome"]) for g in grades):
        raise EnforcementError(
            f"{source}: every rung changes the outcome, so the ladder is a cliff edge — the point "
            "of grading enforcement is that consequence is a spectrum"
        )
    return doc


def grades(path: Path | None = None) -> tuple[str, ...]:
    """The rung names, loosest first."""
    return tuple(str(g["grade"]) for g in ladder(path)["grades"])


def rung(grade: str, path: Path | None = None) -> dict[str, Any]:
    for entry in ladder(path)["grades"]:
        if str(entry["grade"]) == str(grade):
            return dict(entry)
    raise EnforcementError(f"{grade!r} is not a rung on the enforcement ladder (have: {', '.join(grades(path))})")


def rank(grade: str, path: Path | None = None) -> int:
    return int(rung(grade, path)[RANK])


def changes_the_outcome(grade: str, path: Path | None = None) -> bool:
    return bool(rung(grade, path)["changes_the_outcome"])


def pin(path: Path | None = None) -> dict[str, Any]:
    """Which ladder a control was graded against: its version and its exact content."""
    doc = ladder(path)
    return {"version": int(doc["version"]), "digest": digest_of(doc)}


def published(path: Path | None = None) -> dict[str, Any]:
    """The ladder as it goes into an artefact: the rungs, what each admits, and what none of them do."""
    doc = ladder(path)
    return {
        "pin": pin(path),
        "rule": (
            f"consequence is a spectrum of {len(doc['grades'])} rungs and "
            f"{grades(path)[-1]!r} is the bottom one, reached when the rung below it still leaves "
            "a residual over the appetite band"
        ),
        "grade_never_prices": GRADE_NEVER_PRICES,
        "grades": [
            {
                "grade": str(g["grade"]),
                RANK: int(g[RANK]),
                "changes_the_outcome": bool(g["changes_the_outcome"]),
                "admits": str(g["admits"]).strip(),
                "does_not": str(g["does_not"]).strip(),
                "realised_by": str(g["realised_by"]).strip(),
            }
            for g in doc["grades"]
        ],
    }


# -- posture-as-identity, computed rather than declared ----------------------------------------


def posture_as_identity(response: dict[str, Any]) -> dict[str, Any]:
    """Whether this control's identity proves its control was in force, and why not when it does not.

    Never a field an author sets. `full` is derived and never typed for the same reason: a claim
    that can be asserted is a claim that will be, and this one was the prior estate's philosophy.
    """
    enforcement = response.get("enforcement") or {}
    if not enforcement:
        return {"admitted": False, "excluded_as": POSTURE_EXCLUSIONS[0]["case"]}
    if not changes_the_outcome(str(enforcement["grade"])):
        return {"admitted": False, "excluded_as": POSTURE_EXCLUSIONS[1]["case"]}
    if not str(enforcement.get("stamped_by", "")).strip():
        return {"admitted": False, "excluded_as": POSTURE_EXCLUSIONS[2]["case"]}
    return {
        "admitted": True,
        "because": (
            f"the control occupies {str(enforcement['grade'])!r}, which changes the outcome, and "
            f"its posture is stamped by {str(enforcement['stamped_by'])} rather than by the "
            "subject — so the identity attests that the control was in force at issue"
        ),
        "still_not": POSTURE_EXCLUSIONS[4]["case"],
    }


def refuse_untrusted_stamp(enforcement: dict[str, Any], where: str) -> None:
    """A trusted stamper on a rung that changes nothing reads as posture-as-identity and is not.

    Refused rather than silently computed to `false`, because the field would then sit in the
    model looking like the claim while meaning nothing — and the one thing decision ticket 18 Q4
    narrowed is exactly the claim that reads bigger than it is.
    """
    grade = str(enforcement.get("grade", ""))
    if str(enforcement.get("stamped_by", "")).strip() and not changes_the_outcome(grade):
        raise EnforcementError(
            f"{where}: declares a trusted stamper at rung {grade!r}, which does not change the "
            f"outcome. {POSTURE_EXCLUSIONS[1]['excluded_because']}. Loosening a control below the "
            "outcome-changing line means it stops being posture-as-identity, and the stamper goes "
            "with it in the same move."
        )


# -- the move record ---------------------------------------------------------------------------


def direction(from_grade: str, to_grade: str) -> str:
    """Named, never implied, and derived from the rank rather than from the rung's name."""
    if str(from_grade) == str(to_grade):
        raise EnforcementError("a move that changes nothing is not a move")
    return TIGHTENED if rank(to_grade) > rank(from_grade) else LOOSENED


def record(move: dict[str, Any]) -> dict[str, Any]:
    """One move, as it appears in an artefact. `direction` is derived, never authored."""
    from_grade, to_grade = str(move["from_grade"]), str(move["to_grade"])
    return {
        "id": str(move["id"]),
        "subject": str(move["subject"]),
        "from_grade": from_grade,
        "to_grade": to_grade,
        "direction": direction(from_grade, to_grade),
        "moved_on": str(move["moved_on"]),
        "by_role": str(move["by_role"]),
        "reason": str(move["reason"]),
        "evidence": str(move["evidence"]),
    }


def chain_for(subject: str, moves: dict[str, dict[str, Any]]) -> list[dict[str, Any]]:
    """This control's moves, oldest first. Ties broken by id so the order is deterministic."""
    mine = [m for m in moves.values() if str(m.get("subject")) == subject]
    return sorted(mine, key=lambda m: (str(m["moved_on"]), str(m["id"])))


def check_chain(subject: str, current: str, chain: list[dict[str, Any]], where: str) -> None:
    """The recorded chain is contiguous and ends where the control now stands."""
    if not chain:
        return
    for earlier, later in zip(chain, chain[1:]):
        if str(later["from_grade"]) != str(earlier["to_grade"]):
            raise EnforcementError(
                f"{where}: move {later['id']!r} starts at {later['from_grade']!r}, but "
                f"{earlier['id']!r} left {subject!r} at {earlier['to_grade']!r} — the record has a "
                "gap, so some part of this control's consequence history is unaccounted for"
            )
    last = str(chain[-1]["to_grade"])
    if last != str(current):
        raise EnforcementError(
            f"{where}: {subject!r} declares enforcement grade {current!r}, but its last move "
            f"({chain[-1]['id']!r}) left it at {last!r}. A rung is immutable without a move event "
            "recording who moved it and why."
        )


def _graded_at(repo: Any, commit: str, full: str) -> tuple[str, str] | None:
    """The (id, enforcement grade) this response declared at that commit.

    A control with no `enforcement` block reads as `NO_RUNG` rather than as nothing, so that
    **deleting the block is an observed change**. Losing a rung removes every consequence a
    control carried, and a deletion is the shape a weakening takes when nothing forces it to be
    recorded — the same reason the constitution treats absences as the hard case.
    """
    from .repo import RepoError

    try:
        doc = repo.read_yaml_at(commit, full)
    except RepoError:
        return None  # the file did not exist at that commit, or was not readable as YAML
    ident = doc.get("id")
    if not ident:
        return None
    grade = (doc.get("enforcement") or {}).get("grade")
    return str(ident), grade if isinstance(grade, str) else NO_RUNG


def history_violations(repo: Any, unit_path: str, tree: str, moves: dict[str, dict[str, Any]]) -> list[str]:
    """Every change an enforcement grade has ever undergone, checked against the move record.

    The chain check catches a rung that has moved *since* a move was recorded. This catches the
    first unrecorded move, where there is no chain yet — by reading what the file said at every
    commit that touched it.
    """
    from .evidence import unrecorded_changes

    def covered(subject: str, was: Any, now: Any) -> bool:
        return any(
            str(m.get("subject")) == subject
            and str(m["from_grade"]) == str(was)
            and str(m["to_grade"]) == str(now)
            for m in moves.values()
        )

    return sorted(
        f"{full}: enforcement grade of {subject!r} moved {was} -> {now} at commit {commit[:12]} "
        "with no move event recording who moved it and why"
        for full, subject, was, now, commit in unrecorded_changes(
            repo, unit_path, tree, ("responses",), _graded_at
        )
        # Arriving at a rung is not a move: a control that gains consequence has none to have
        # moved from. Losing one is, which is why the two directions are treated differently.
        if was != NO_RUNG and not covered(subject, was, now)
    )


# -- the published posture ----------------------------------------------------------------------


def artefact(repo: Any, org: str, command: list[str]) -> Any:
    """The enforcement posture of one overlay: where every control sits, and what that proves.

    **Authored**, like the constraint set and for the same reason: which rung a control occupies is
    a *declaration* — somebody in a role chose the consequence that control carries — and this
    publishes the declaration together with the ladder it was declared against. It carries no depth
    grade rather than a grade of `authored`: a depth grade measures how much of a decision ticket a
    capability has realised, and nothing here is derived from a model the twin could be wrong about.
    """
    from .artefact import AUTHORED, Artefact
    from .model import Overlay

    overlay = Overlay.load(repo, org)
    controls, unenforced = [], []
    for ident, response in sorted(overlay.responses.items()):
        enforcement = response.get("enforcement") or {}
        if not enforcement:
            unenforced.append({"control": ident, "name": str(response.get("name", ""))})
            continue
        grade = str(enforcement["grade"])
        mitigates = response.get("mitigates") or {}
        controls.append({
            "control": ident,
            "name": str(response.get("name", "")),
            "grade": grade,
            RANK: rank(grade),
            "changes_the_outcome": changes_the_outcome(grade),
            "point": str(enforcement["point"]),
            "posture_as_identity": posture_as_identity(response),
            # Beside the rung, never inside it: what the control claims it removes is its own
            # graded claim, and the rung neither supplies nor multiplies it.
            "claims": (
                {
                    "component": str(mitigates["component"]),
                    "evidence_grade": int(mitigates["evidence_grade"]),
                }
                if mitigates
                else None
            ),
        })

    return Artefact(
        kind=KIND,
        mark=AUTHORED,
        command=command,
        pins={
            "model_repo": repo.pin.as_dict(),
            "overlay": overlay.ref.as_dict(),
            "world": overlay.world.ref.as_dict(),
            "org": overlay.org,
            "enforcement_ladder": pin(),
            "role": ROLE,
        },
        depth={
            "grade": None,
            "capabilities": {},
            "note": "declared by a human in a role; no capability produced it",
        },
        body={
            "ladder": published(),
            "controls": controls,
            "not_enforced": {
                "controls": unenforced,
                "why": (
                    "a lever that is not code occupies no rung, and that is the majority case "
                    "rather than an omission. The £ engine's cross-domain comparison exists "
                    "because most levers are not code"
                ),
            },
            "posture_as_identity": {
                "admits": (
                    "a control whose rung changes the outcome and whose posture is stamped by "
                    "something that is not the subject. Computed from those two facts; there is "
                    "no field an author can set to claim it"
                ),
                "excluded": [dict(case) for case in POSTURE_EXCLUSIONS],
            },
            "moves": overlay.enforcement_move_records(),
            "signed": {
                "role": ROLE,
                "covers": "the ladder in force, where every control sits, and every recorded move",
                "not_covered": (
                    "the git commit that carried a move is not keyless-signed — "
                    "estate/verify/provenance/verify-provenance.sh records that this repository's "
                    "commits are not — so 'signed' attaches to this artefact and to each move's "
                    "role binding, never to the commit"
                ),
            },
        },
    )
