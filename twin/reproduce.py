"""Recompute an artefact from its pins.

Sign the artefact, pin the inputs, recompute the why (decision ticket 14). This is where
"deterministic given the pins" stops being an aspiration: nothing is materialised, so the only
way the attestation is a proof rather than a claim is if the derivation actually re-runs and
lands on the same bytes.

A score card reproduces the **chain**, not just itself: the forecast bundle it scored is
recomputed **at the bundle's own pin**, and its digest is checked against the digest the card
claimed. Using the card's pin instead would break every card whose answer key was committed after
the forecast was made — which is the normal case, since a forecast is made before it resolves.

The chain is not one hop deep by construction. Any artefact whose body or pins names another
artefact by `{kind, sha256, produced_by, pins}` — a **subject reference** — has that reference
walked recursively by `_replay_subject`: a reliability diagram pools score cards this way (its
`pins["score_cards"]` entries are subject references, plural), so reproducing one walks reliability
-> score-card -> forecast-bundle, three artefacts deep, each hop re-opening its own pinned model
tree (build ticket 89, decision ticket 14 Q3: "unbounded but recomputable"). A subject reference
missing the fields needed to re-run it (most likely `produced_by`, the one field a digest-and-pins
summary does not need for anything *except* walking) fails loudly rather than silently reporting
an empty chain — an artefact that names something it cannot walk is a gap in what that artefact
kind declared, not a reason to pretend nothing was named.

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

VERBS = ("sense", "run", "score", "graph", "propagate", "options", "intervene", "observe", "rewind",
         "regimes", "price", "backtest", "reliability")

# The fields a subject reference must carry to be walked, not merely digest-checked (build ticket
# 89). `kind` and `produced_by` are exactly what `produced_by`-less pooling (the pre-89 shape of
# `reliability`'s own `score_cards` pin) leaves out — enough to verify a claimed digest, never
# enough to re-run it.
_SUBJECT_FIELDS = ("kind", "sha256", "produced_by", "pins")


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


def _replay_subject(
    worktree: str | Path, caps: Capabilities, ref: dict[str, Any]
) -> tuple[Artefact | None, Report]:
    """Recursively replay one artefact named by digest — a **subject reference**.

    Every reference this module walks shares the one shape `score()`'s own `body["subject"]`
    invented: `{kind, sha256, produced_by, pins}`, plus an optional `body` — whatever body content
    *that* kind's own `replay()` branch reads (a score card's own `subject`, say), carried
    verbatim rather than re-derived, so the recursion below can walk one more kind however deep
    the reference chain actually goes. `pins` alone is enough to check a claimed digest was ever
    real; `produced_by["command"]` is the part that turns a check into a *walk* — without it there
    is a byte string to compare against and nothing left to re-run, so a reference missing it
    fails loudly here rather than a `KeyError` three frames down or, worse, a chain link silently
    absent from the report.

    Returns the rebuilt artefact, or `None` (with the report still describing the mismatch) if
    the reference's own pins no longer produce the digest it claimed.
    """
    missing = [name for name in _SUBJECT_FIELDS if name not in ref]
    if missing:
        raise ReproduceError(
            f"a chain reference carries {sorted(ref)} but is missing {missing} — this artefact "
            "kind was not built with enough declared pins to walk its own chain, only enough to "
            "check a digest"
        )
    envelope = {"kind": ref["kind"], "produced_by": ref["produced_by"], "pins": ref["pins"]}
    synthetic = {"envelope": envelope, "body": ref.get("body", {})}
    rebuilt, nested_chain = replay(worktree, caps, synthetic)
    actual = rebuilt.digest()
    report = Report(
        kind=rebuilt.kind, command=list(rebuilt.command), expected=ref["sha256"], actual=actual,
        chain=nested_chain,
    )
    if actual != ref["sha256"]:
        return None, report
    return rebuilt, report


def replay(worktree: str | Path, caps: Capabilities, doc: dict[str, Any]) -> tuple[Artefact, list[Report]]:
    """Re-run the command an artefact records, rebuilding whatever inputs it needed."""
    envelope = doc["envelope"]
    command = list(envelope["produced_by"]["command"])
    if len(command) < 2 or command[0] != "twin" or command[1] not in VERBS:
        raise ReproduceError(f"not a replayable command: {' '.join(command) or '(empty)'}")

    verb, flags = command[1], _flags(command)

    if verb == "reliability":
        # No `org`, no `model_repo` pin — a reliability diagram is standalone, pooled entirely
        # from named score cards (`verbs.reliability`'s own docstring). Each pooled card carries
        # its own model-repo pin and is opened at that pin by its own recursive `replay()` call
        # below, so nothing here needs `worktree` opened directly.
        sources = envelope["pins"].get("score_cards")
        if not sources:
            raise ReproduceError(
                f"{' '.join(command)}: no score_cards pin to walk a reliability diagram's chain "
                "from"
            )
        chain: list[Report] = []
        with tempfile.TemporaryDirectory(prefix="twin-replay-") as scratch:
            paths: list[str | Path] = []
            for index, ref in enumerate(sources):
                card, report = _replay_subject(worktree, caps, ref)
                chain.append(report)
                if card is None:
                    # One pooled card no longer reproduces at its own pin — the diagram pooled
                    # something that no longer exists, so report it rather than pool on.
                    return _placeholder(doc), chain
                path = Path(scratch) / f"score-card-{index}.json"
                path.write_bytes(card.to_bytes())
                paths.append(path)
            bins = int(_need(flags, "bins", command))
            return verbs.reliability(paths, caps, command, bins=bins), chain

    org = _need(flags, "org", command)
    repo = _open_at(worktree, envelope["pins"]["model_repo"], f"{envelope['kind']} pin")

    if verb == "sense":
        return verbs.sense(repo, caps, org, _need(flags, "signal", command), command), []
    if verb in ("run", "backtest"):
        # The regime is read from the recorded command, never defaulted. A replay that guessed it
        # could reproduce an `as-consumed` bundle from a `with-hindsight` execution and report a
        # match, which is the one thing this whole module exists to make impossible.
        #
        # `backtest` needs no separate branch: it recorded `model_repo` pins at the commit
        # `primitives.rewind` already resolved to, and `_open_at` above opened exactly that commit
        # — so replaying it is replaying `run()` against an already-rewound repository, the same
        # composition `cmd_backtest` itself is (build ticket 37).
        return verbs.run(
            repo, caps, org, _need(flags, "scenario", command), _need(flags, "regime", command),
            command, at=flags.get("at"),
        ), []
    if verb == "price":
        return verbs.price(repo, caps, org, _need(flags, "origin", command), None, command), []
    if verb == "regimes":
        return verbs.regime_gap(
            repo, caps, org, _need(flags, "scenario", command), command, at=flags.get("at")
        ), []
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

    if verb == "score":
        if flags.get("discount_sha256"):
            # A discount (build ticket 40) is measured from other score cards named by path at
            # the CLI, never recorded in the pinned command (`discount_sha256` is pinned by
            # digest for the same reason `forecast_sha256` is — see `verbs.command_for`'s
            # docstring), so there is nothing here to re-derive it from. Unlike `reliability`'s
            # pooling above, a discount's own sources carry no `produced_by` at all — there is no
            # reference here to walk, honest or otherwise.
            raise ReproduceError(
                f"{' '.join(command)}: this score card names --discount-sha256 "
                f"{flags['discount_sha256']!r}; a discount is measured from other score cards "
                "named by path at the CLI, not pinned in the command, so it cannot be replayed "
                "from pins alone"
            )

        bundle, report = _replay_subject(worktree, caps, doc["body"]["subject"])
        chain = [report]
        if bundle is None:
            # The card named a bundle by digest. If the pins no longer produce that bundle, the
            # card is scoring something that no longer exists — report it rather than score on.
            return _placeholder(doc), chain
        with tempfile.TemporaryDirectory(prefix="twin-replay-") as scratch:
            path = Path(scratch) / "forecast-bundle.json"
            path.write_bytes(bundle.to_bytes())
            return verbs.score(repo, caps, org, path, _need(flags, "outcome", command), command), chain

    # Unreachable given `VERBS` enumerates every branch above, but a kind that declines
    # chain-walking support should say so rather than fall through and guess at a shape it does
    # not own — the exact failure mode build ticket 89 closes (decision ticket 14 Q3).
    raise ReproduceError(f"{' '.join(command)}: {verb!r} chain-walking is not implemented")


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
