"""Contestability as a primary workflow (build ticket 60), from decision tickets 07 and 15.

**Arguing with the artefact is the supported workflow, not a complaints box.** A challenge is a
versioned, signed object naming a specific claim in a specific artefact — never the artefact as a
whole, because "I dispute this number" and "I dispute everything here" are different claims and
collapsing them into one is how a challenge to one figure gets waved off by pointing at an
unrelated total.

**No hiding behind aggregation, structurally rather than by review.** `resolve()` takes the
challenge it resolves as its only source for *what* was resolved — the resolution's `claim_path`
is read out of the challenge, never re-specified by the caller — so there is no parameter through
which a resolution could name a different path from the one actually disputed. A challenge against
a constituent figure cannot be answered by a resolution that talks about the roll-up instead,
because the code has nowhere to write "roll-up" when the challenge said "constituent".

Both a challenge and a resolution are **authored artefacts**, the same shape
`twin/constraints.py`'s constraint-set is: no capability produced them, so they carry no depth
grade, and a human signs them (`twin/sign.py`) because raising or resolving a challenge is a
judgement, not a derivation.
"""

from __future__ import annotations

from typing import Any

from .artefact import AUTHORED, Artefact, ArtefactError
from .canon import walk_values

KIND_CHALLENGE = "challenge"
KIND_RESOLUTION = "challenge-resolution"

OPEN, RESOLVED = "open", "resolved"


class ChallengeError(RuntimeError):
    """A challenge that names no real claim, or a resolution with nothing to resolve."""


def _subject(doc: dict[str, Any], sha256: str) -> dict[str, Any]:
    envelope = doc["envelope"]
    return {"kind": envelope["kind"], "sha256": sha256, "produced_by": envelope["produced_by"]}


def raise_challenge(
    challenged_doc: dict[str, Any], challenged_sha256: str, claim_path: str, reason: str,
    command: list[str],
) -> Artefact:
    """A challenge against one claim in one artefact, frozen at the value it was when raised.

    `claim_path` must name a real value in `challenged_doc["body"]` — the same dotted-key-path
    `canon.walk_values` produces, so a challenge targets exactly what an auditor reading that
    function's output would call the claim. A path that resolves to nothing is refused: a
    challenge to a claim that does not exist disputes nothing.
    """
    if not reason.strip():
        raise ChallengeError("a challenge with no reason disputes nothing a reader can evaluate")
    values = dict(walk_values(challenged_doc.get("body", {})))
    if claim_path not in values:
        known = ", ".join(sorted(values)[:8])
        raise ChallengeError(
            f"{claim_path!r} is not a claim in this artefact's body (have, e.g.: {known}, ...)"
        )
    return Artefact(
        kind=KIND_CHALLENGE,
        mark=AUTHORED,
        command=command,
        pins={"challenged_artefact_sha256": challenged_sha256},
        depth={"grade": None, "capabilities": {}, "note": "authored by a human in a role; no capability produced it"},
        body={
            "challenged": _subject(challenged_doc, challenged_sha256),
            "claim_path": claim_path,
            "challenged_value": values[claim_path],
            "reason": reason.strip(),
            "status": OPEN,
        },
    )


def resolve(challenge_doc: dict[str, Any], challenge_sha256: str, response: str, command: list[str]) -> Artefact:
    """A resolution, naming only what the challenge itself named.

    There is no `claim_path` parameter here on purpose (see the module docstring): the path this
    resolution addresses is read out of `challenge_doc`, so a caller cannot construct a resolution
    that talks about anything else.
    """
    if challenge_doc["envelope"]["kind"] != KIND_CHALLENGE:
        raise ChallengeError(f"{challenge_doc['envelope']['kind']!r} is not a {KIND_CHALLENGE!r}")
    if not response.strip():
        raise ChallengeError("a resolution with no response resolves nothing")
    body = challenge_doc["body"]
    return Artefact(
        kind=KIND_RESOLUTION,
        mark=AUTHORED,
        command=command,
        pins={"challenge_sha256": challenge_sha256},
        depth={"grade": None, "capabilities": {}, "note": "authored by a human in a role; no capability produced it"},
        body={
            "challenge_sha256": challenge_sha256,
            "challenged": body["challenged"],
            "claim_path": body["claim_path"],
            "response": response.strip(),
        },
    )


def for_artefact(
    artefact_sha256: str, challenges: list[dict[str, Any]], resolutions: list[dict[str, Any]]
) -> dict[str, Any]:
    """Every challenge against one artefact, partitioned into open and resolved.

    This is the "visible wherever the challenged artefact is visible" half: a caller displaying an
    artefact hands its digest and whatever challenges/resolutions it knows about here, and gets
    back exactly what to show beside it — an unresolved challenge is a field in this return value,
    never a queue somewhere else a reader has to know to check.
    """
    resolved_by_challenge_sha256 = {
        str(r["body"]["challenge_sha256"]): r for r in resolutions if r["envelope"]["kind"] == KIND_RESOLUTION
    }
    mine = [
        c for c in challenges
        if c["envelope"]["kind"] == KIND_CHALLENGE and c["body"]["challenged"]["sha256"] == artefact_sha256
    ]
    open_challenges, resolved_challenges = [], []
    for challenge in mine:
        resolution = resolved_by_challenge_sha256.get(_self_sha256(challenge))
        entry = {
            "claim_path": challenge["body"]["claim_path"],
            "challenged_value": challenge["body"]["challenged_value"],
            "reason": challenge["body"]["reason"],
        }
        if resolution is None:
            open_challenges.append(entry)
        else:
            resolved_challenges.append({**entry, "response": resolution["body"]["response"]})
    return {
        "artefact_sha256": artefact_sha256,
        "open": open_challenges,
        "resolved": resolved_challenges,
        "has_unresolved_challenges": bool(open_challenges),
    }


def _self_sha256(challenge_doc: dict[str, Any]) -> str:
    """A loaded challenge document carries no digest of itself inside it — canonical bytes over
    the same `{envelope, body}` shape `Artefact.digest()` hashes recomputes it exactly."""
    from .canon import canonical_json, sha256_hex

    return sha256_hex(canonical_json(challenge_doc))


def refuse_answering_a_different_claim(challenge_doc: dict[str, Any], resolution_doc: dict[str, Any]) -> None:
    """Enforced where a resolution would be emitted, on top of the structural guard `resolve()`
    already is — the same double-lock `refuse_upstream_under_intervention` applies to an
    intervention's own body, in case a resolution is ever constructed by a path other than
    `resolve()` itself."""
    if resolution_doc["envelope"]["kind"] != KIND_RESOLUTION:
        return
    if resolution_doc["body"]["claim_path"] != challenge_doc["body"]["claim_path"]:
        raise ArtefactError(
            f"a resolution for claim {resolution_doc['body']['claim_path']!r} was attached to a "
            f"challenge about {challenge_doc['body']['claim_path']!r} — a challenge to a "
            "constituent cannot be answered by pointing at a different claim"
        )
