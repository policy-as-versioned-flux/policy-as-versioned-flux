"""Recompute an artefact from its pins.

Sign the artefact, pin the inputs, recompute the why (decision ticket 14). This is where
"deterministic given the pins" stops being an aspiration: nothing is materialised, so the only
way the attestation is a proof rather than a claim is if the derivation actually re-runs and
lands on the same bytes.

A score card reproduces the **chain**, not just itself: the forecast bundle it scored is
recomputed **at the bundle's own pin**, and its digest is checked against the digest the card
claimed. Using the card's pin instead would break every card whose answer key was committed after
the forecast was made — which is the normal case, since a forecast is made before it resolves.

**Tolerance is zero.** Comparison is byte equality, never approximate. Where platform maths could
differ in the last unit in the last place — `log`, in the scoring rules — the *format* declares a
quantisation (`scoring.SIGNIFICANT_DIGITS`) and the comparison stays exact. Putting the tolerance
in the format rather than in the comparison is what makes it a stated property instead of a
silent one.
"""

from __future__ import annotations

import difflib
import tempfile
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from . import artefact as artefact_mod
from . import scoring, verbs
from .artefact import Artefact
from .canon import sha256_hex
from .grades import Capabilities
from .repo import ModelRepo, RepoError

VERBS = ("sense", "run", "score", "graph", "propagate", "options", "intervene", "observe", "rewind")


class ReproduceError(RuntimeError):
    """The artefact cannot be recomputed — which is not the same as it not reproducing."""


@dataclass
class Report:
    kind: str
    command: list[str]
    expected: str
    actual: str
    diff: str = ""
    chain: list["Report"] = field(default_factory=list)

    @property
    def reproduces(self) -> bool:
        return self.expected == self.actual and all(link.reproduces for link in self.chain)

    def as_dict(self) -> dict[str, Any]:
        return {
            "kind": self.kind,
            "command": self.command,
            "expected_sha256": self.expected,
            "actual_sha256": self.actual,
            "reproduces": self.reproduces,
            "tolerance": "none — byte identity",
            "declared_quantisation": f"{scoring.SIGNIFICANT_DIGITS} significant digits on scores",
            "chain": [link.as_dict() for link in self.chain],
        }


def _flags(command: list[str]) -> dict[str, str]:
    body = command[2:]
    if len(body) % 2:
        raise ReproduceError(f"cannot read the recorded command: {' '.join(command)}")
    return {body[i].lstrip("-").replace("-", "_"): body[i + 1] for i in range(0, len(body), 2)}


def _need(flags: dict[str, str], name: str, command: list[str]) -> str:
    if name not in flags:
        raise ReproduceError(f"the recorded command names no --{name}: {' '.join(command)}")
    return flags[name]


def _open_at(worktree: str | Path, pin: dict[str, Any], what: str) -> ModelRepo:
    """Open the repository at a recorded pin, refusing one that does not hold it."""
    try:
        repo = ModelRepo.open(worktree, ref=pin["commit"])
    except RepoError as exc:
        raise ReproduceError(f"{what}: {exc}") from None
    if repo.pin.tree != pin["tree"]:
        raise ReproduceError(
            f"{what}: the repository at {worktree} does not hold the pinned model tree "
            f"{pin['tree'][:12]} at commit {pin['commit'][:12]} (found {repo.pin.tree[:12]}) — "
            "this is a different model, which is not a divergence"
        )
    return repo


def replay(worktree: str | Path, caps: Capabilities, doc: dict[str, Any]) -> tuple[Artefact, list[Report]]:
    """Re-run the command an artefact records, rebuilding whatever inputs it needed."""
    envelope = doc["envelope"]
    command = list(envelope["produced_by"]["command"])
    if len(command) < 2 or command[0] != "twin" or command[1] not in VERBS:
        raise ReproduceError(f"not a replayable command: {' '.join(command) or '(empty)'}")

    verb, flags = command[1], _flags(command)
    org = _need(flags, "org", command)
    repo = _open_at(worktree, envelope["pins"]["model_repo"], f"{envelope['kind']} pin")

    if verb == "sense":
        return verbs.sense(repo, caps, org, _need(flags, "signal", command), command), []
    if verb == "run":
        return verbs.run(repo, caps, org, _need(flags, "scenario", command), command, at=flags.get("at")), []
    if verb == "graph":
        return verbs.graph(repo, caps, org, command), []
    if verb == "propagate":
        return verbs.propagate(repo, caps, org, _need(flags, "origin", command), command), []
    if verb == "options":
        return verbs.options(repo, caps, org, _need(flags, "perspective", command), command), []
    if verb == "intervene":
        return verbs.intervene(repo, caps, org, _need(flags, "component", command), command), []
    if verb == "observe":
        return verbs.observe(repo, caps, org, _need(flags, "component", command), command), []
    if verb == "rewind":
        # No second rewind here. The recorded `model_repo` pin **is** the commit the rewind
        # resolved to, so re-resolving the timestamp would replay the lookup rather than the
        # derivation — and would diverge the moment a commit landed between them.
        return verbs.rewind(repo, caps, org, _need(flags, "at", command), command), []

    subject = doc["body"]["subject"]
    bundle, chain = replay(
        worktree, caps, {"envelope": {**subject, "kind": subject["kind"], "produced_by": subject["produced_by"]}, "body": {}}
    )
    rebuilt = bundle.digest()
    chain.append(Report(kind=bundle.kind, command=list(bundle.command), expected=subject["sha256"], actual=rebuilt))
    if rebuilt != subject["sha256"]:
        # The card named a bundle by digest. If the pins no longer produce that bundle, the card
        # is scoring something that no longer exists — report it rather than score on.
        return _placeholder(doc), chain
    with tempfile.TemporaryDirectory(prefix="twin-replay-") as scratch:
        path = Path(scratch) / "forecast-bundle.json"
        path.write_bytes(bundle.to_bytes())
        return verbs.score(repo, caps, org, path, _need(flags, "outcome", command), command), chain


def _placeholder(doc: dict[str, Any]) -> Artefact:
    envelope = doc["envelope"]
    return Artefact(
        kind=envelope["kind"], mark=envelope["mark"], command=list(envelope["produced_by"]["command"]),
        pins=envelope["pins"], depth=envelope["depth"], body={"unreproduced": True},
    )


def reproduce(repo_path: str | Path, artefact_path: str | Path) -> Report:
    """Recompute `artefact_path` from its own pins against the repository at `repo_path`."""
    doc = artefact_mod.load(artefact_path)
    rebuilt, chain = replay(repo_path, Capabilities.load(), doc)

    expected = sha256_hex(Path(artefact_path).read_bytes())
    actual = rebuilt.digest()
    report = Report(
        kind=doc["envelope"]["kind"], command=list(rebuilt.command), expected=expected, actual=actual, chain=chain
    )
    if actual != expected:
        report.diff = "\n".join(
            difflib.unified_diff(
                Path(artefact_path).read_text(encoding="utf-8").splitlines(),
                rebuilt.to_bytes().decode("utf-8").splitlines(),
                fromfile="recorded", tofile="recomputed", lineterm="", n=2,
            )
        )
    return report
