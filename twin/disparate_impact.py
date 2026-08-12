"""The disparate-impact audit channel (build ticket 61), the sealed route decision ticket 15's
Q3b finding #4 asks for: "Absence-as-alibi — structural unrepresentability of Art. 9 data prevents
discrimination *detection*, not discrimination. Disparate impact needs no protected field to
occur, but does need one to be measured. Needs a sealed audit channel, or an explicit admission
that the system cannot be checked for disparate impact." `twin/constraints.yaml`'s own
`disparate-impact-measurement` scope exclusion names this ticket as where that channel lands.

**Sealed.** The twin cannot represent a protected characteristic anywhere
(`no-special-category-representation`, the universal floor) — so a disparate-impact finding is
necessarily made *outside* the twin, by an external audit against the twin's outputs. The channel
this module gives that finding a route into the record without ever letting it name the protected
ground it was measured against: `raise_audit()` runs the identical
`schema.refuse_special_category` refusal the model repository itself runs. An auditor reports
*what* differs and *where it was checked* (a source outside this system); the twin still cannot
represent *why*, and does not pretend otherwise.

**A defined respondent role, structurally rather than by convention.** `respond()` refuses a
response whose `responded_by_role` is not exactly `disparate-impact-respondent`
(`twin/roles.yaml`) — a route anybody could answer has no defined respondent, and the check runs
against the argument, not against whether a signature happens to be attached.

Both an audit and a response are **authored artefacts**, the same shape `twin/challenges.py`'s
challenge and resolution are: no capability produced them, so they carry no depth grade.
"""

from __future__ import annotations

from typing import Any

from .artefact import AUTHORED, Artefact
from .schema import SpecialCategoryError, refuse_special_category

KIND_AUDIT = "disparate-impact-audit"
KIND_RESPONSE = "disparate-impact-response"

RESPONDENT_ROLE = "disparate-impact-respondent"

OPEN, RESPONDED = "open", "responded"

_NO_CAPABILITY_DEPTH: dict[str, Any] = {
    "grade": None,
    "capabilities": {},
    "note": "authored by a human in a role; no capability produced it",
}


class DisparateImpactError(RuntimeError):
    """An audit names what the model cannot represent, or a response answers with no defined role."""


def raise_audit(finding: str, source: str, command: list[str]) -> Artefact:
    """Open an audit: what differs, and where it was measured.

    `source` must name where the disparity was checked, because this system cannot check it
    itself — a finding with nothing behind it but the finding is unfalsifiable by construction, the
    same refusal `challenges.raise_challenge` gives a reason-less challenge.
    """
    if not finding.strip():
        raise DisparateImpactError("an audit with no finding reports nothing to check")
    if not source.strip():
        raise DisparateImpactError(
            "an audit must cite where the disparity was measured — this system cannot represent "
            "the protected characteristic itself, so it cannot measure disparate impact either, "
            "and a finding with no external source is not falsifiable"
        )
    try:
        refuse_special_category({"finding": finding, "source": source}, "disparate-impact-audit")
    except SpecialCategoryError as exc:
        raise DisparateImpactError(
            f"{exc} An audit finding names what differs and where it was checked, never the "
            "protected characteristic itself — the channel is sealed to the same refusal the "
            "model repository carries."
        ) from None
    return Artefact(
        kind=KIND_AUDIT,
        mark=AUTHORED,
        command=command,
        pins={},
        depth=dict(_NO_CAPABILITY_DEPTH),
        body={"finding": finding.strip(), "source": source.strip(), "status": OPEN},
    )


def respond(
    audit_doc: dict[str, Any], audit_sha256: str, response: str, responded_by_role: str,
    command: list[str],
) -> Artefact:
    """Close the loop: the one defined role answers, naming what it answered."""
    if audit_doc["envelope"]["kind"] != KIND_AUDIT:
        raise DisparateImpactError(f"{audit_doc['envelope']['kind']!r} is not a {KIND_AUDIT!r}")
    if not response.strip():
        raise DisparateImpactError("a response with no text answers nothing")
    if responded_by_role != RESPONDENT_ROLE:
        raise DisparateImpactError(
            f"only the {RESPONDENT_ROLE!r} role may respond to a disparate-impact audit (got "
            f"{responded_by_role!r}) — a channel any role can answer has no defined respondent"
        )
    return Artefact(
        kind=KIND_RESPONSE,
        mark=AUTHORED,
        command=command,
        pins={"audit_sha256": audit_sha256},
        depth=dict(_NO_CAPABILITY_DEPTH),
        body={
            "audit_sha256": audit_sha256,
            "finding": audit_doc["body"]["finding"],
            "response": response.strip(),
            "responded_by_role": responded_by_role,
        },
    )
