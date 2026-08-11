"""Signatures: two kinds, and they are not interchangeable (build ticket 11).

**A human signature asserts accountability for a judgement.** Somebody in a named role stands
behind a number they chose.

**An agent signature asserts reproducible origin only** — runtime, model version, config. It
says "this came out of that, and here is enough to re-run it". It asserts nothing about whether
the output is correct, and it never inherits human authority.

The consequence is the interesting half. Because a derived artefact may carry an agent signature
and may **not** carry a human one, a signature attests the *absence* of human involvement,
CI-style. A derived artefact with human fingerprints on it stops being a convention breach and
becomes a **detectable anomaly**: the check fails, and it fails on evidence rather than on trust.

Signatures bind to **roles**, never to named individuals (decision ticket 15). The role register
is versioned and a signature records the version and digest it was made against, so a role that
is later renamed or withdrawn cannot silently change what an old signature meant.

`ponytail:` HMAC-SHA256 over the subject digest, keyed from `TWIN_SIGNING_KEY`. That is real
verification with no dependency, and it has a named ceiling: **a shared key proves possession,
not identity**, so anybody holding it can produce any role's signature. The upgrade is
sigstore/gitsign with in-toto subject digests, which decision ticket 14 already names; the shape
here — subject digest, role binding, register pin, typed assertion — is what that upgrade would
keep. With no key present nothing is signed, and the sidecar says so rather than carrying a
placeholder that reads as signed.
"""

from __future__ import annotations

import hashlib
import hmac
import os
from pathlib import Path
from typing import Any

import yaml

from . import PACKAGE_DIR
from .canon import canonical_json, digest_of

ROLES_PATH = PACKAGE_DIR / "roles.yaml"
ALGORITHM = "hmac-sha256"
KEY_ENV = "TWIN_SIGNING_KEY"

HUMAN, AGENT = "human", "agent"
TYPES = (HUMAN, AGENT)

ASSERTS = {
    HUMAN: "accountability for a judgement",
    AGENT: "reproducible origin — runtime, model version and config, and nothing else",
}
# Said in the artefact rather than only in this docstring: an agent signature that is silent
# about what it does not claim will be read as claiming it.
AGENT_ASSERTS_NOTHING_ABOUT = ("correctness", "accountability", "human review")

# A signature names a role. These are the shapes of a named individual, refused so that
# "role, not person" is enforced rather than encouraged.
PERSONAL_FIELDS = ("email", "identity", "individual", "name", "person", "signer", "user")


class SignatureError(RuntimeError):
    """A signature that is not one, or one that does not hold."""


def roles(path: Path | None = None) -> dict[str, Any]:
    doc = yaml.safe_load((path or ROLES_PATH).read_text(encoding="utf-8"))
    if not isinstance(doc, dict) or not doc.get("roles"):
        raise SignatureError(f"{path or ROLES_PATH}: not a role register")
    return doc


def register_pin(path: Path | None = None) -> dict[str, Any]:
    """Which register a signature was made against: its version and its exact content."""
    doc = roles(path)
    return {"version": int(doc["version"]), "digest": digest_of(doc["roles"])}


def role_ids(path: Path | None = None) -> list[str]:
    return sorted(str(r["id"]) for r in roles(path)["roles"])


def signing_key(explicit: str | None = None) -> bytes | None:
    material = explicit if explicit is not None else os.environ.get(KEY_ENV)
    return material.encode("utf-8") if material else None


def _value(payload: dict[str, Any], material: bytes) -> str:
    return hmac.new(material, canonical_json(payload), hashlib.sha256).hexdigest()


def human(role: str, subject_sha256: str, material: bytes, roles_path: Path | None = None) -> dict[str, Any]:
    """Accountability, attached to a role. Refuses a role the register does not carry."""
    known = role_ids(roles_path)
    if role not in known:
        raise SignatureError(
            f"role {role!r} is not in the register (have: {', '.join(known)}). A signature binds "
            "to a role, so an unregistered one has nobody accountable behind it."
        )
    payload = {
        "type": HUMAN,
        "asserts": ASSERTS[HUMAN],
        "role": role,
        "role_register": register_pin(roles_path),
        "subject_sha256": subject_sha256,
    }
    return {**payload, "algorithm": ALGORITHM, "value": _value(payload, material)}


def agent(subject_sha256: str, runtime: dict[str, Any], material: bytes) -> dict[str, Any]:
    """Reproducible origin, and explicitly nothing else."""
    payload = {
        "type": AGENT,
        "asserts": ASSERTS[AGENT],
        "asserts_nothing_about": list(AGENT_ASSERTS_NOTHING_ABOUT),
        "runtime": runtime,
        "subject_sha256": subject_sha256,
    }
    return {**payload, "algorithm": ALGORITHM, "value": _value(payload, material)}


def refuse_personal(signature: dict[str, Any]) -> None:
    """Signatures bind to roles, not to named individuals. Enforced, not encouraged."""
    personal = sorted(set(signature) & set(PERSONAL_FIELDS))
    if personal:
        raise SignatureError(
            f"signature carries {', '.join(personal)}; signatures bind to roles, not to named "
            "individuals — accountability attaches without creating a personal target."
        )


def check_human_shape(signature: dict[str, Any], roles_path: Path | None = None) -> None:
    """What a human signature must be before anybody looks at its value.

    Checked at the point a sidecar is built as well as when one is read, so an unsigned-but-
    well-formed personal claim never gets written in the first place.
    """
    refuse_personal(signature)
    role = signature.get("role")
    known = role_ids(roles_path)
    if not role:
        raise SignatureError(
            f"a human signature names no role (have: {', '.join(known)}); accountability attaches "
            "to a role, so an unattributed signature attaches to nobody"
        )
    if str(role) not in known:
        raise SignatureError(f"role {str(role)!r} is not in the register (have: {', '.join(known)})")


def is_human(signature: dict[str, Any]) -> bool:
    """A signature is human if it is *not* a well-formed agent signature.

    Deliberately not `type == "human"`. Deleting the type field, or misspelling it, must not be a
    way to slip a human signature past `derived_never_human_signed` — the refusal has to be the
    default, so anything that does not positively identify itself as an agent counts as human.
    """
    return str(signature.get("type", HUMAN)) != AGENT


def verify(signature: dict[str, Any], expected_type: str, subject_sha256: str, material: bytes) -> None:
    """Refuse a signature of the wrong type, over the wrong subject, or with the wrong value.

    The type is checked first and separately: the two kinds are non-interchangeable, so an agent
    signature presented as a human one must be refused **as a type error** even when its value
    verifies perfectly. Otherwise "reproducible origin" could be passed off as accountability by
    moving one field.
    """
    if expected_type not in TYPES:
        raise SignatureError(f"unknown signature type {expected_type!r}")
    actual = str(signature.get("type", ""))
    if actual != expected_type:
        raise SignatureError(
            f"a {actual or 'untyped'!r} signature was presented where a {expected_type!r} one is "
            f"required. The two are not interchangeable: a human signature asserts "
            f"{ASSERTS[HUMAN]}, an agent signature asserts {ASSERTS[AGENT]}."
        )
    refuse_personal(signature)
    if signature.get("subject_sha256") != subject_sha256:
        raise SignatureError(
            f"signature is over {str(signature.get('subject_sha256'))[:16]}, not over this "
            f"artefact ({subject_sha256[:16]})"
        )
    if signature.get("algorithm") != ALGORITHM:
        raise SignatureError(f"unknown signature algorithm {signature.get('algorithm')!r}")
    payload = {k: v for k, v in signature.items() if k not in ("algorithm", "value")}
    if not hmac.compare_digest(_value(payload, material), str(signature.get("value", ""))):
        raise SignatureError("signature does not verify against the artefact it names")
