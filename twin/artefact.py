"""The artefact envelope — seam 1's unit of output.

Carries the input pins, the producing command, a depth-grade slot and an authored/derived mark
(build ticket 01). Nothing here is allowed to vary with the machine: the wall clock, the host
and the interpreter are absent by design, because `identical_pins_identical_bytes` has to hold
across architectures. Machine-varying facts live in the attestation sidecar instead.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from . import TOOL_VERSION
from .canon import canonical_json, sha256_hex, walk_keys

SCHEMA = "twin.artefact/v1"

AUTHORED = "authored"
DERIVED = "derived"
MARKS = (AUTHORED, DERIVED)

# Absences enforced at the point of emission, so they hold by construction rather than by review.
# Each entry names the invariant it serves; the suite plants violations to prove the guard bites.
# Grows as invariants activate — a key added here must never be removed without an authorising
# decision ticket (constitution: every ticket extends the suite and never weakens it).
FORBIDDEN_KEYS: dict[str, str] = {
    "recommended_action": "no_recommended_action_field",
    "recommendation": "no_recommended_action_field",
    "recommended": "no_recommended_action_field",
    "consensus": "no_collapse_mechanism",
    "consensus_forecast": "no_collapse_mechanism",
    "combined_forecast": "no_collapse_mechanism",
    "collapsed": "no_collapse_mechanism",
    "point_forecast": "no_collapse_mechanism",
    "best_forecast": "no_collapse_mechanism",
}


class ArtefactError(RuntimeError):
    pass


@dataclass(frozen=True)
class Artefact:
    kind: str
    mark: str
    command: list[str]
    pins: dict[str, Any]
    depth: dict[str, Any]
    body: dict[str, Any] = field(default_factory=dict)

    def envelope(self) -> dict[str, Any]:
        if self.mark not in MARKS:
            raise ArtefactError(f"artefact mark must be one of {MARKS}, got {self.mark!r}")
        return {
            "envelope": {
                "schema": SCHEMA,
                "kind": self.kind,
                "mark": self.mark,
                "produced_by": {"tool": "twin", "tool_version": TOOL_VERSION, "command": list(self.command)},
                "pins": self.pins,
                "depth": self.depth,
            },
            "body": self.body,
        }

    def to_bytes(self) -> bytes:
        doc = self.envelope()
        refuse_forbidden_keys(doc)
        return canonical_json(doc)

    def digest(self) -> str:
        return sha256_hex(self.to_bytes())

    def write(self, path: str | Path) -> Path:
        out = Path(path)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_bytes(self.to_bytes())
        return out


def refuse_forbidden_keys(doc: dict[str, Any]) -> None:
    for key in walk_keys(doc):
        invariant = FORBIDDEN_KEYS.get(key)
        if invariant:
            raise ArtefactError(
                f"artefact carries a {key!r} field, which {invariant} forbids. "
                "Removing this refusal needs an authorising decision ticket."
            )


def load(path: str | Path) -> dict[str, Any]:
    import json

    doc = json.loads(Path(path).read_bytes().decode("utf-8"))
    if not isinstance(doc, dict) or doc.get("envelope", {}).get("schema") != SCHEMA:
        raise ArtefactError(f"{path}: not a {SCHEMA} artefact")
    return doc


def digest_of_file(path: str | Path) -> str:
    return sha256_hex(Path(path).read_bytes())
