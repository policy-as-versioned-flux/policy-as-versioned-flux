"""The Flux falsification verdict: three branches, read separately (build ticket 65).

`drift.py` reduces and refuses to conclude. This module concludes — and the interesting part is
everything it refuses to conclude on the way.

## Why the verdict needed code at all

The question was widened from two branches to three on 2026-08-10, three days into a 91-day window
and before any verdict could be read. The original pair — continuous proof of force, or a
deploy-time attestation — looked exhaustive, and it was not:

1. **continuous-state** — proof from reconciliation of a signed pinned source. What Flux does.
2. **point-in-time** — a deploy-time attestation suffices.
3. **continuous-action** — proof at the ACTION boundary rather than the STATE boundary. A control
   can hold its declared state for a whole window while an action crosses it. Both 1 and 3 are
   continuous; they are continuous about different things.

Build ticket 64's window measures **state** drift only, and says so in its own `scope_limit`
addendum. So a null result there falsifies branch 1 and leaves branch 3 untouched — and reading it
as "Flux is a convenience, therefore point-in-time suffices" is a false dichotomy, on the critical
path, written into a durable artefact.

That defect is an *argument*, not a wrong number. No arithmetic test catches it and no reviewer
catches it reliably either, because the inference reads as obvious. So the elimination path is
**closed in code**: `point-in-time` resolves only when both other branches are falsified, and
branch 3 cannot be falsified without a pre-registered window that has never been opened. The
protocol can be read, but it cannot be read that way.

## What is pre-registered, and what that buys

`estate/driftwood/drift/verdict.yaml` declares the risk basis, the coverage floor, the three
branches and — written before the result is known — the spec amendment for the failing case. A
decision rule written after the data arrives is not a decision rule, and "we would have concluded
the same either way" is exactly what nobody can check afterwards. The harness guard
`flux_verdict_is_pre_registered_and_derived` reads that file's git history, the same way build
ticket 64's guard reads the window's.

## What this module does not do

It does not open branch 3's window. Recording that no such window exists is the honest state, and
manufacturing one that this repository's own cluster cannot support would be worse than the gap.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml

from . import REPO_DIR
from .drift import Window, coverage, events

# mo-12: repointed at .estate-clone/ (clone-estate.sh's fetch of the real driftwood repo, mo-08),
# mirroring the same fix in verify/party/party.py, verify/proportionality/render.py,
# verify/provenance/provenance.py.
PROTOCOL_PATH = REPO_DIR / ".estate-clone" / "driftwood" / "drift" / "verdict.yaml"
PROTOCOL_SCHEMA = "drift.verdict_protocol/v1"

# Named rather than discovered from the file: the whole defect this module exists to prevent is a
# branch going missing, and a protocol that declares its own branch set could drop one and still
# validate against itself.
BRANCHES = ("continuous-state", "point-in-time", "continuous-action")
STATE, RESIDUAL, ACTION = BRANCHES

# The residual branch resolves only when BOTH continuous branches are falsified — hardcoded here
# for the same reason `BRANCHES` is, and it is the more important of the two. Reading this rule out
# of the yaml would mean deleting one key re-opened the elimination path, which is precisely the
# false dichotomy this module exists to refuse: a protocol that declares its own guard can drop it
# and still validate against itself. The file still declares the rule, because a reader of the
# pre-registration must be able to see it, and `Protocol.load` refuses a file that disagrees.
ENTAILS_RESIDUAL = (STATE, ACTION)

PENDING = "pending"
HELD = "held"
FALSIFIED = "falsified"
UNMEASURED = "unmeasured"

# Two, because one is a product. Build ticket 65: "judge the *class*, not the product" — the
# action-boundary branch has at least five independent implementations and resting it on any single
# one turns a falsification test into a procurement opinion.
MINIMUM_CLASS_IMPLEMENTATIONS = 2


class VerdictError(RuntimeError):
    """The protocol does not say what it must, or a verdict was asked for on evidence that cannot carry it."""


@dataclass(frozen=True)
class Protocol:
    """The pre-registered reading of the measurement. Loaded rather than trusted."""

    question: str
    risk_basis: str
    evidence_ladder_version: int
    path_admission_threshold: int
    minimum_coverage: float
    requires_window_closed: bool
    branches: dict[str, dict[str, Any]]
    amendment_if_falsified: str
    owner: str

    @classmethod
    def load(cls, path: Path | None = None) -> "Protocol":
        source = path or PROTOCOL_PATH
        doc = yaml.safe_load(source.read_text(encoding="utf-8"))
        if not isinstance(doc, dict) or doc.get("schema") != PROTOCOL_SCHEMA:
            raise VerdictError(f"{source}: not a {PROTOCOL_SCHEMA} document")

        branches = {str(b.get("id", "")): dict(b) for b in (doc.get("branches") or [])}
        if set(branches) != set(BRANCHES):
            raise VerdictError(
                f"{source}: declares {sorted(branches)}, not the three branches build ticket 65 "
                f"names: {sorted(BRANCHES)}. The original pair looked exhaustive and was not, so a "
                "protocol that has quietly lost a branch is the defect rather than a shorthand."
            )

        entails = tuple(branches[RESIDUAL].get("entailed_only_if_both_falsified") or ())
        if entails != ENTAILS_RESIDUAL:
            raise VerdictError(
                f"{source}: the {RESIDUAL} branch declares it is entailed by {list(entails)}, the "
                f"rule is {list(ENTAILS_RESIDUAL)}. The rule is enforced from code and declared "
                "here so a reader can see it; a file that disagrees with the code is the one thing "
                "a pre-registration must never be."
            )

        implementations = branches[ACTION].get("class_implementations") or []
        if len(implementations) < MINIMUM_CLASS_IMPLEMENTATIONS:
            raise VerdictError(
                f"{source}: the {ACTION} branch names {len(implementations)} implementation(s). "
                "It is answered on the class, not on any product — one name is a procurement "
                "opinion wearing a falsification test's clothes."
            )

        amendment = str(doc.get("amendment_if_falsified", "")).strip()
        if not amendment:
            raise VerdictError(
                f"{source}: drafts no spec amendment for the failing case. A test whose negative "
                "result changes nothing was not a test, and drafting it after the result is how it "
                "comes to change nothing."
            )

        risk_basis = str(doc.get("risk_basis", "")).strip()
        if not risk_basis:
            raise VerdictError(
                f"{source}: states no risk basis. 'Continuity matters' is not one, because nothing "
                "would falsify it."
            )

        # The risk basis is stated in the ladder's terms, so it is pinned to the ladder rather than
        # left to agree with it by memory. A threshold that moved would otherwise leave a published
        # statement citing a gate that no longer exists.
        from .evidence import ladder

        live = ladder()
        for our_key, ladder_key in (
            ("path_admission_threshold", "path_admission_threshold"),
            ("evidence_ladder_version", "version"),
        ):
            declared = doc.get(our_key)
            if int(declared or 0) != int(live[ladder_key]):
                raise VerdictError(
                    f"{source}: declares {our_key} {declared!r}, the live evidence ladder's "
                    f"{ladder_key} is {live[ladder_key]!r}. The risk basis is stated in the "
                    "ladder's terms and may not drift from it."
                )

        gate = doc.get("reading_gate") or {}
        floor = float(gate.get("minimum_coverage", 0) or 0)
        if not 0 < floor < 1:
            raise VerdictError(
                f"{source}: minimum_coverage {floor!r} is not a fraction strictly between zero and "
                "one. A floor of zero reads 'no drift observed' at no coverage as a result, and a "
                "floor of one is unsatisfiable: the gate asks for coverage ABOVE the floor and "
                "nothing exceeds a fully-sampled window, so the branch could never resolve."
            )

        owner = str((doc.get("operation") or {}).get("owner", "")).strip()
        if not owner:
            raise VerdictError(f"{source}: names no owner")

        return cls(
            question=str(doc.get("question", "")).strip(),
            risk_basis=risk_basis,
            evidence_ladder_version=int(doc["evidence_ladder_version"]),
            path_admission_threshold=int(doc["path_admission_threshold"]),
            minimum_coverage=floor,
            requires_window_closed=bool(gate.get("requires_window_closed", True)),
            branches=branches,
            amendment_if_falsified=amendment,
            owner=owner,
        )


def _state_branch(
    protocol: Protocol, window: Window, samples: list[dict[str, Any]], now: str
) -> dict[str, Any]:
    """Branch 1, and the only branch any instrument in this repository can currently settle."""
    cover = coverage(window, samples, now)
    observed = events(window, samples)
    evidence = {
        "sampled_fraction": cover["sampled_fraction"],
        "window_elapsed_fraction": cover["window_elapsed_fraction"],
        "drift_events": len(observed),
    }

    if protocol.requires_window_closed and cover["window_elapsed_fraction"] < 1:
        return {
            "state": PENDING,
            "why": (
                f"the window has not closed ({cover['window_elapsed_fraction']:.0%} elapsed, closes "
                f"{window.closes}). Reading it early is the same act as truncating it once it "
                "looked worse."
            ),
            "evidence": evidence,
        }
    # `<=`, not `<`: the window's falsifier says "at coverage **above** 90%", so exactly 90% does
    # not meet it. The strict reading is the one that refuses a verdict, which is the direction to
    # round in when the two readings disagree.
    if cover["sampled_fraction"] <= protocol.minimum_coverage:
        return {
            "state": PENDING,
            "why": (
                f"coverage is {cover['sampled_fraction']:.0%}, at or below the pre-registered floor "
                f"of {protocol.minimum_coverage:.0%}. 'No drift observed' at this coverage is not a "
                "result, and the floor is the window's own falsifier rather than this protocol's "
                "invention."
            ),
            "evidence": evidence,
        }
    if observed:
        return {
            "state": HELD,
            "why": (
                f"{len(observed)} drift event(s) with no deploy between the samples, at "
                f"{cover['sampled_fraction']:.0%} coverage over a closed window. A deploy-time "
                "attestation would not have caught them."
            ),
            "evidence": evidence,
        }
    return {
        "state": FALSIFIED,
        "why": (
            f"no drift event in any subject across the full window at {cover['sampled_fraction']:.0%} "
            "coverage — the window's own first falsifier, met. Continuous proof of STATE is not "
            "required by observed drift."
        ),
        "evidence": evidence,
    }


def decide(
    protocol: Protocol, window: Window, samples: list[dict[str, Any]], now: str
) -> dict[str, Any]:
    """The verdict so far: three branch states, and an overall verdict only when one is earned.

    `now` is passed in rather than read from the clock, for the same reason `coverage` takes it:
    a verdict is a function of its inputs, and two runs over the same log agree.
    """
    if not window.does_not_measure or not window.scope_consequence:
        raise VerdictError(
            "the window declares no scope_limit, so a verdict read from it cannot state what its "
            "instrument could not see, nor what that means for the reading. That omission is the "
            "false dichotomy build ticket 65 exists to prevent, so it is refused rather than "
            "footnoted."
        )

    state = _state_branch(protocol, window, samples, now)

    action = {
        "state": UNMEASURED,
        "why": (
            "no pre-registered window measures action-boundary continuity, and none is open. "
            "Recorded as absent rather than inferred to be unnecessary: an unmeasured branch is "
            "not a falsified one."
        ),
        "what_would_settle_it": protocol.branches[ACTION].get("settled_by"),
        "judged_on_the_class": protocol.branches[ACTION].get("class_implementations"),
    }

    # The closed door. `point-in-time` is the residual of the other two and is never read off one
    # of them: with branch 3 unmeasured it cannot resolve at all, which is the intended and
    # permanent consequence of widening the question rather than a temporary data gap.
    by_id = {STATE: state, ACTION: action}
    unfalsified = [name for name in ENTAILS_RESIDUAL if by_id[name]["state"] != FALSIFIED]
    residual = {
        "state": PENDING if unfalsified else HELD,
        "why": (
            "a deploy-time attestation suffices only if BOTH continuous branches are falsified, and "
            f"{', '.join(unfalsified)} {'is' if len(unfalsified) == 1 else 'are'} not. Concluding "
            "it from the state branch alone would be elimination against an incomplete set — the "
            "false dichotomy this protocol exists to refuse."
            if unfalsified
            else "both continuous branches are falsified, so the residual branch is what is left."
        ),
    }

    branches = {STATE: state, RESIDUAL: residual, ACTION: action}

    # A verdict is earned two ways and no third. A branch that HOLDS answers the question in its own
    # right; a residual that HOLDS answers it by exhausting a complete set. Anything else is None.
    if state["state"] == HELD:
        overall = (
            "continuous-state proof of force is required. Flux's role is narrowed to exactly that: "
            "it is the evidence a control held its declared STATE between deploys, and it is not "
            "evidence that no action crossed the control, which no instrument here measured."
        )
    elif residual["state"] == HELD:
        overall = "point-in-time attestation suffices; both continuous branches are falsified."
    else:
        overall = None

    return {
        "as_at": now,
        "question": protocol.question,
        "risk_basis": protocol.risk_basis,
        "gated_on": {
            "evidence_ladder_version": protocol.evidence_ladder_version,
            "path_admission_threshold": protocol.path_admission_threshold,
        },
        "branches": branches,
        "verdict": overall,
        "amendment_if_falsified": protocol.amendment_if_falsified,
        "amendment_applies": state["state"] == FALSIFIED,
        "scope_limit": {
            "does_not_measure": window.does_not_measure,
            "consequence_for_the_verdict": window.scope_consequence,
        },
        "owner": protocol.owner,
    }
