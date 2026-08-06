"""Attestation sidecars.

Sign the artefact, pin the inputs, recompute the why (decision ticket 14). A human signature
asserts accountability for a judgement; an agent signature asserts reproducible origin and
attests the **absence** of human involvement, CI-style — which is what makes the authored/derived
split enforceable and manual tampering with a derived value detectable.

The sidecar is deliberately *not* byte-identical across machines: it is where runtime, platform
and interpreter facts go, precisely so the artefact itself stays identical given the pins. That
is also why the signature lives here and never in the artefact — a keyed value would break
`identical_pins_identical_bytes` on the first machine that held a different key.

Sidecars are **read back** (build ticket 11). `check` recomputes the subject digest, verifies
whatever signature is present, and refuses a human signature on a derived artefact. Without that,
a sidecar is write-only and provides no tamper-evidence even in principle.
"""

from __future__ import annotations

import json
import platform
import sys
from pathlib import Path
from typing import Any

from . import TOOL_VERSION, sign
from .artefact import AUTHORED, DERIVED, Artefact
from .canon import canonical_json, sha256_hex

SCHEMA = "twin.attestation/v1"
UNSIGNED = f"unsigned — no signing key present (set {sign.KEY_ENV})"
SUFFIX = ".att.json"


class AttestationError(RuntimeError):
    pass


def runtime() -> dict[str, str]:
    """What an agent signature actually asserts: enough to re-run this, and nothing more."""
    return {
        "python": platform.python_version(),
        "implementation": sys.implementation.name,
        "platform": platform.system().lower(),
        "machine": platform.machine(),
        "tool_version": TOOL_VERSION,
    }


def build(
    artefact: Artefact,
    human_signatures: list[dict[str, Any]] | None = None,
    material: bytes | None = None,
) -> dict[str, Any]:
    signatures = list(human_signatures or [])
    if artefact.mark == DERIVED and signatures:
        # The inversion that matters: for a derived artefact, human involvement is a defect, not
        # a warrant. A hand-touched derived output can no longer be recomputed.
        raise AttestationError(
            f"derived artefact {artefact.kind!r} carries {len(signatures)} human signature(s); "
            "derived_never_human_signed forbids it"
        )
    for signature in signatures:
        if not sign.is_human(signature):
            raise AttestationError(
                "an agent signature was supplied as a human one. An agent signature asserts "
                f"{sign.ASSERTS[sign.AGENT]}; it never carries accountability."
            )
        try:
            sign.check_human_shape(signature)
        except sign.SignatureError as exc:
            raise AttestationError(str(exc)) from None

    digest = artefact.digest()
    material = material if material is not None else sign.signing_key()
    return {
        "schema": SCHEMA,
        "subject": {"kind": artefact.kind, "sha256": digest, "bytes": len(artefact.to_bytes())},
        "mark": artefact.mark,
        "produced_by": {
            "tool": "twin",
            "tool_version": TOOL_VERSION,
            "command": list(artefact.command),
            "runtime": runtime(),
        },
        "pins": artefact.pins,
        "human_involvement": {"present": bool(signatures), "signatures": signatures},
        # Present on any artefact, authored or derived: it says where the bytes came from, which
        # is true either way. It is never a substitute for the human signature an authored
        # artefact needs, because it asserts nothing about the judgement inside.
        "agent_signature": sign.agent(digest, runtime(), material) if material else None,
        "signature_status": None if material else UNSIGNED,
    }


def write(
    artefact: Artefact,
    artefact_path: str | Path,
    human_signatures: list[dict[str, Any]] | None = None,
) -> Path:
    out = Path(str(artefact_path) + SUFFIX)
    out.write_bytes(canonical_json(build(artefact, human_signatures)))
    return out


def load(path: str | Path) -> dict[str, Any]:
    doc = json.loads(Path(path).read_bytes().decode("utf-8"))
    if not isinstance(doc, dict) or doc.get("schema") != SCHEMA:
        raise AttestationError(f"{path}: not a {SCHEMA} sidecar")
    return doc


def sidecar_for(artefact_path: str | Path) -> Path:
    return Path(str(artefact_path) + SUFFIX)


def human_signed(doc: dict[str, Any]) -> bool:
    involvement = doc.get("human_involvement", {})
    return bool(involvement.get("present")) or bool(involvement.get("signatures"))


def check(doc: dict[str, Any], artefact_bytes: bytes, material: bytes | None = None) -> list[str]:
    """Everything this sidecar can be held to, as a list of problems. Empty means it holds.

    A list rather than an exception: an auditor wants every problem at once, and "the digest is
    wrong *and* the signature is over something else" is a different story from either alone.
    """
    problems: list[str] = []
    actual = sha256_hex(artefact_bytes)
    subject = doc.get("subject", {})
    if subject.get("sha256") != actual:
        problems.append(
            f"the sidecar attests {str(subject.get('sha256'))[:16]} but the artefact is "
            f"{actual[:16]} — one of the two has been edited since"
        )
    if subject.get("bytes") != len(artefact_bytes):
        problems.append(f"the sidecar records {subject.get('bytes')} bytes, the artefact is {len(artefact_bytes)}")

    signatures = list(doc.get("human_involvement", {}).get("signatures") or [])
    if doc.get("mark") == DERIVED and (signatures or doc.get("human_involvement", {}).get("present")):
        # The anomaly the whole ticket exists for. Detected, not trusted.
        problems.append(
            "a derived artefact carries human involvement, which derived_never_human_signed "
            "forbids — a derived value with human fingerprints on it can no longer be recomputed"
        )
    if doc.get("mark") == AUTHORED and not signatures:
        problems.append("an authored artefact carries no human signature, so nobody is accountable for it")

    material = material if material is not None else sign.signing_key()
    if material is None:
        if signatures or doc.get("agent_signature"):
            problems.append(f"signatures are present but no key is available to check them (set {sign.KEY_ENV})")
        return problems

    for signature in signatures:
        try:
            sign.verify(signature, sign.HUMAN, actual, material)
        except sign.SignatureError as exc:
            problems.append(f"human signature: {exc}")
    agent_signature = doc.get("agent_signature")
    if agent_signature is None:
        problems.append("no agent signature: nothing attests where these bytes came from")
    else:
        try:
            sign.verify(agent_signature, sign.AGENT, actual, material)
        except sign.SignatureError as exc:
            problems.append(f"agent signature: {exc}")
    return problems
