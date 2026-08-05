"""Attestation sidecars.

Sign the artefact, pin the inputs, recompute the why (decision ticket 14). A human signature
asserts accountability for a judgement; a machine signature asserts reproducible origin and
attests the **absence** of human involvement, CI-style — which is what makes the authored/derived
split enforceable and manual tampering with a derived value detectable.

The sidecar is deliberately *not* byte-identical across machines: it is where runtime, platform
and interpreter facts go, precisely so the artefact itself stays identical given the pins.

Cryptographic signing (sigstore/gitsign, in-toto subject digests) lands with build ticket 11.
Until then `signature` is null and says so, rather than a placeholder that reads as signed.
"""

from __future__ import annotations

import platform
import sys
from pathlib import Path
from typing import Any

from . import TOOL_VERSION
from .artefact import DERIVED, Artefact
from .canon import canonical_json

SCHEMA = "twin.attestation/v1"
UNSIGNED = "unsigned — cryptographic signing lands with build ticket 11"


class AttestationError(RuntimeError):
    pass


def build(artefact: Artefact, human_signatures: list[dict[str, Any]] | None = None) -> dict[str, Any]:
    signatures = list(human_signatures or [])
    if artefact.mark == DERIVED and signatures:
        # The inversion that matters: for a derived artefact, human involvement is a defect, not
        # a warrant. A hand-touched derived output can no longer be recomputed.
        raise AttestationError(
            f"derived artefact {artefact.kind!r} carries {len(signatures)} human signature(s); "
            "derived_never_human_signed forbids it"
        )
    return {
        "schema": SCHEMA,
        "subject": {"kind": artefact.kind, "sha256": artefact.digest(), "bytes": len(artefact.to_bytes())},
        "mark": artefact.mark,
        "produced_by": {
            "tool": "twin",
            "tool_version": TOOL_VERSION,
            "command": list(artefact.command),
            "runtime": {
                "python": platform.python_version(),
                "implementation": sys.implementation.name,
                "platform": platform.system().lower(),
                "machine": platform.machine(),
            },
        },
        "pins": artefact.pins,
        "human_involvement": {"present": bool(signatures), "signatures": signatures},
        "signature": None,
        "signature_status": UNSIGNED,
    }


def write(artefact: Artefact, artefact_path: str | Path) -> Path:
    out = Path(str(artefact_path) + ".att.json")
    out.write_bytes(canonical_json(build(artefact)))
    return out


def human_signed(doc: dict[str, Any]) -> bool:
    involvement = doc.get("human_involvement", {})
    return bool(involvement.get("present")) or bool(involvement.get("signatures"))
