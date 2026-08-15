"""Multi-channel enactment sensing, with corroboration setting the evidence grade.

Build ticket 68, from decision ticket 18 Q3. The question it answers is the one ticket 08 leaves
open: **was the recommendation acted upon?** The answer is not a new record type. It is an
observation, and it reaches the model through the sensing path that already exists.

## What is new here, and what deliberately is not

**Not new: the pipeline.** A declaration and a machine-verified fact are both `signal` documents,
and both bind through a `claim`. The only difference from build ticket 05's original binding is
what the claim binds *to* — a `response` rather than a `component` — and `twin sense` walks both
kinds through the same code path. There is no enactment ingest, no enactment verb and no parallel
collection; deleting this module would leave the sensing path intact and unbranched.

**New: which channel observed it, and what one channel is worth.** `twin/enactment-channels.yaml`
is a versioned, closed table of six channels. Each declares what it observes, whether the subject
of the response is the one declaring it, and the rung it holds **alone**. Nothing else.

## Why no channel prices alone

Every channel observes a *proxy* for the claim being graded. The claim is "this response was
actually enacted"; the proxies are a declaration, a merged change, a payroll line, a
counter-signature, a moved pin, a reconciler's report. The step from proxy to enactment is a
mechanism nobody has evidenced in this instance, which is the evidence ladder's own grade 3: the
mechanism is real, whether it operated here is not evidenced.

So `table()` refuses a channel whose `alone` grade may price. The acceptance criterion asks only
that an uncorroborated *self-declaration* cannot reach a price-eligible grade; making it a rule
about every channel is both stronger and simpler than a rule about one of them, and it removes
the argument about which channel deserves the exemption.

## Why a subject cannot corroborate itself

Corroboration counts **independent** channels, and every subject-declared channel counts as one
between them. Without that, the cheapest way to earn credit for acting would be to declare twice
— which inverts the incentive this whole mechanism exists to set. What survives is the incentive
decision ticket 18 Q3 wanted: **be verifiable rather than be watched.** A declaration corroborated
by a reconciler grades higher than either alone, and nobody had to be monitored to get there.

## The surveillance guard, run rather than restated

Decision ticket 18 Q3 attaches a guard: multi-channel sensing does not licence sensing people to
verify enactment, which still has to pass decision ticket 15's ladder. One channel here observes
people at all, and `table()` walks it through `twin/ethics_gate.py` on load — a channel that
declares `observes_people: true` and carries no admission is refused, an admission the gate does
not admit is refused, and an admission on a channel that observes nobody is refused as ceremony.

`ponytail:` the grade is computed from **which** channels observed, never from how many
observations each one made. Ten reconciler reports are one channel, on purpose: repetition within
a channel is the thing a channel is already worth its rung for. If per-channel recency or volume
ever needs to count, it belongs in the table as a declared property of the channel, not as a
second knob in the rule here.
"""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Any, Iterable

import yaml

from . import PACKAGE_DIR, evidence
from .canon import digest_of
from .schema import ENACTMENT as KIND, EVIDENCE_GRADES

TABLE_PATH = PACKAGE_DIR / "enactment-channels.yaml"
SCHEMA = "twin.enactment-channels/v1"

# `KIND` is `schema.ENACTMENT`, re-exported rather than re-spelled: the kind belongs beside the
# other claim kinds, and everything that decides what it *means* belongs here.

# What a channel row may say, and nothing else. The closure is what makes "no channel is
# privileged" structural — there is no field by which one could outrank another, so a reader
# looking for the reconciler's special status finds that there is nowhere to write one.
CHANNEL_REQUIRED = (
    "channel", "name", "declared_by_subject", "observes_people", "alone", "observes",
    "alone_because", "example",
)
CHANNEL_OPTIONAL = ("admission",)

CORROBORATION_REQUIRED = ("rule", "step_rungs", "reading", "self_corroboration", "absence")

STRONGEST_GRADE = min(EVIDENCE_GRADES)


class CorroborationError(RuntimeError):
    """The channel table does not say what it must, or a claim disagrees with it."""


@lru_cache(maxsize=8)
def table(path: Path | None = None) -> dict[str, Any]:
    """The versioned channel table, validated on read.

    Validated here rather than trusted, for the reason the evidence ladder is: a table that has
    quietly grown a channel able to price on its own would let a self-declared enactment earn
    credit through a channel nobody looked at.

    `ponytail:` cached per path, the same ceiling `evidence.ladder()` carries and for the same
    reason — every graded response asks for a channel's rung and the table is immutable within a
    process. A test that rewrites a table file in place will see the first version; write a new
    temp file instead.
    """
    source = path or TABLE_PATH
    doc = yaml.safe_load(source.read_text(encoding="utf-8"))
    if not isinstance(doc, dict) or doc.get("schema") != SCHEMA:
        raise CorroborationError(f"{source}: not a {SCHEMA} document")
    if not (isinstance(doc.get("version"), int) and not isinstance(doc["version"], bool)):
        raise CorroborationError(f"{source}: declares no integer version, so a change to it is invisible")

    channels = doc.get("channels")
    if not isinstance(channels, list) or len(channels) < 2:
        raise CorroborationError(
            f"{source}: fewer than two channels, so nothing can ever corroborate anything and the "
            "grade is whichever single channel happened to look"
        )
    seen: set[str] = set()
    for row in channels:
        if not isinstance(row, dict):
            raise CorroborationError(f"{source}: a channel is not a mapping")
        _check_channel_keys(source, row)
        ident = str(row["channel"])
        if ident in seen:
            raise CorroborationError(f"{source}: channel {ident!r} is declared twice")
        seen.add(ident)
        for flag in ("declared_by_subject", "observes_people"):
            if not isinstance(row.get(flag), bool):
                raise CorroborationError(
                    f"{source}: channel {ident!r} does not say whether it is {flag.replace('_', ' ')}"
                )
        for field in ("name", "observes", "alone_because", "example"):
            if not str(row.get(field, "")).strip():
                raise CorroborationError(
                    f"{source}: channel {ident!r} declares no {field}. A channel with no written "
                    "account of what it observes is worth whatever a reader assumes."
                )
        # `bool` excluded explicitly, as everywhere else a grade is read: `True == 1` in Python,
        # so `alone: true` would pass a bare membership test and silently mean the strongest rung.
        grade = row.get("alone")
        if isinstance(grade, bool) or grade not in EVIDENCE_GRADES:
            raise CorroborationError(
                f"{source}: channel {ident!r} holds {grade!r} alone, which is not a grade on the "
                "evidence ladder"
            )
        if evidence.may_price(int(grade)):
            raise CorroborationError(
                f"{source}: channel {ident!r} prices alone at grade {grade}. Every channel here "
                "observes a proxy for the claim 'this response was enacted', and the step from "
                "proxy to enactment is unevidenced in any single instance — so corroboration is "
                "what earns a number, and a channel that skips it makes the rest of this table "
                "decorative."
            )
        _check_admission(source, row)

    subject_declared = [r for r in channels if bool(r["declared_by_subject"])]
    if not subject_declared:
        raise CorroborationError(
            f"{source}: no channel is declared by the subject, so declarations are not sensor "
            "inputs at all and decision ticket 18 Q3's answer is unimplemented"
        )
    if len(channels) - len(subject_declared) < 2:
        raise CorroborationError(
            f"{source}: fewer than two channels are independent of the subject, so nothing a "
            "subject declares can ever be corroborated by two others and the grade tops out below "
            "anything the ladder prices"
        )

    rule = doc.get("corroboration")
    if not isinstance(rule, dict) or set(rule) != set(CORROBORATION_REQUIRED):
        raise CorroborationError(
            f"{source}: the corroboration block declares {sorted(rule) if isinstance(rule, dict) else rule!r}, "
            f"and it must declare exactly {list(CORROBORATION_REQUIRED)} — the rule, its reading "
            "against the ladder, what stops self-corroboration, and what absence means"
        )
    step = rule.get("step_rungs")
    if isinstance(step, bool) or not isinstance(step, int) or step < 1:
        raise CorroborationError(
            f"{source}: step_rungs is {step!r}. A step of zero or less means corroboration moves "
            "nothing, which is this table's only purpose."
        )
    for field in ("rule", "reading", "self_corroboration", "absence"):
        if not str(rule.get(field, "")).strip():
            raise CorroborationError(f"{source}: the corroboration block declares no {field}")
    return doc


def _check_channel_keys(source: Path, row: dict[str, Any]) -> None:
    known = set(CHANNEL_REQUIRED) | set(CHANNEL_OPTIONAL)
    unknown = sorted(str(k) for k in row if str(k) not in known)
    if unknown:
        raise CorroborationError(
            f"{source}: channel {row.get('channel')!r} declares {', '.join(unknown)}, which this "
            "table has no room for. The table is closed so that no channel can be given a status "
            "the others do not have — a privileged channel needs a field, and there is none."
        )
    missing = sorted(f for f in CHANNEL_REQUIRED if f not in row)
    if missing:
        raise CorroborationError(
            f"{source}: channel {row.get('channel')!r} declares no {', '.join(missing)}"
        )


def _check_admission(source: Path, row: dict[str, Any]) -> None:
    """Decision ticket 18 Q3's surveillance guard, walked rather than restated.

    Multi-channel sensing reduces surveillance pressure — a corroborated declaration means nobody
    needs watching — and it does not licence sensing people to verify enactment. A channel that
    observes people at all walks decision ticket 15's ladder here, on load, and the table is
    refused if `twin/ethics_gate.py` does not admit it.
    """
    from .ethics_gate import EthicsGateError, admit

    ident = str(row["channel"])
    admission = row.get("admission")
    if not bool(row["observes_people"]):
        if admission is not None:
            raise CorroborationError(
                f"{source}: channel {ident!r} observes nobody and carries an admission ladder "
                "anyway. A gate for a sensor that senses no person reads as the guard having been "
                "applied where it was not needed, which is how it stops being read where it is."
            )
        return
    if not isinstance(admission, dict):
        raise CorroborationError(
            f"{source}: channel {ident!r} observes people and declares no admission. Decision "
            "ticket 18 Q3's guard is that multi-channel sensing does not licence sensing people "
            "to verify enactment — it still passes decision ticket 15's ladder."
        )
    try:
        verdict = admit(admission)
    except EthicsGateError as exc:
        raise CorroborationError(f"{source}: channel {ident!r} admission — {exc}") from None
    if not verdict["admitted"]:
        raise CorroborationError(
            f"{source}: channel {ident!r} observes people and the admission ladder refuses it: "
            f"{verdict['claim']['evidence']}"
        )


def channel_ids(path: Path | None = None) -> tuple[str, ...]:
    return tuple(str(row["channel"]) for row in table(path)["channels"])


def channel(ident: str, path: Path | None = None) -> dict[str, Any]:
    for row in table(path)["channels"]:
        if str(row["channel"]) == str(ident):
            return dict(row)
    raise CorroborationError(
        f"{ident!r} is not an enactment channel (have: {', '.join(channel_ids(path))})"
    )


def alone_grade(ident: str, path: Path | None = None) -> int:
    """What this channel is worth with nothing agreeing with it."""
    return int(channel(ident, path)["alone"])


def pin(path: Path | None = None) -> dict[str, Any]:
    """Which table a grade was computed against: its version and its exact content.

    Carried with the evidence ladder's own pin, because the computed grade is a reading of one
    against the other and neither alone says what it meant.
    """
    doc = table(path)
    return {
        "version": int(doc["version"]),
        "digest": digest_of(doc),
        "evidence_ladder": evidence.pin(),
    }


def published(path: Path | None = None) -> dict[str, Any]:
    """The table as it goes into an artefact: the channels, what each observes, and the rule."""
    doc = table(path)
    rule = doc["corroboration"]
    return {
        "pin": pin(path),
        "rule": str(rule["rule"]).strip(),
        "reading": str(rule["reading"]).strip(),
        "self_corroboration": str(rule["self_corroboration"]).strip(),
        "absence": str(rule["absence"]).strip(),
        "no_channel_prices_alone": (
            "every channel observes a proxy for the claim that a response was enacted, and the "
            "step from proxy to enactment is unevidenced in any single instance. The table is "
            "refused at load if a channel holds a price-eligible grade alone."
        ),
        "channels": [
            {
                "channel": str(row["channel"]),
                "name": str(row["name"]),
                "declared_by_subject": bool(row["declared_by_subject"]),
                "observes_people": bool(row["observes_people"]),
                "alone": int(row["alone"]),
                "observes": str(row["observes"]).strip(),
                "alone_because": str(row["alone_because"]).strip(),
                "example": str(row["example"]).strip(),
            }
            for row in doc["channels"]
        ],
    }


# -- the computation ---------------------------------------------------------------------------


def independent_count(channels: Iterable[str], path: Path | None = None) -> int:
    """How many independent channels a set of channel ids amounts to.

    Every subject-declared channel counts as one between them. A subject cannot corroborate
    itself, so declaring the same enactment through two of its own routes buys exactly what
    declaring it once does.
    """
    distinct = {str(c) for c in channels}
    independent = {c for c in distinct if not bool(channel(c, path)["declared_by_subject"])}
    return len(independent) + (1 if len(distinct) > len(independent) else 0)


def corroborate(claims: list[dict[str, Any]], path: Path | None = None) -> dict[str, Any]:
    """The evidence grade of "this response was enacted", computed from the channels that observed it.

    Never authored. A claim carries its own channel's `alone` rung and nothing else, so there is
    no field anywhere an author could write this number into — the same discipline
    `twin/enforcement.py` applies to posture-as-identity and `twin/grades.py` applies to `full`.
    """
    doc = table(path)
    step = int(doc["corroboration"]["step_rungs"])
    by_channel: dict[str, list[str]] = {}
    for claim in claims:
        by_channel.setdefault(str(claim["channel"]), []).append(str(claim["id"]))

    if not by_channel:
        return {
            "observed": False,
            "channels": [],
            "independent_channels": 0,
            "strongest_alone": None,
            "evidence_grade": None,
            "may_price": False,
            "why": str(doc["corroboration"]["absence"]).strip(),
        }

    rows = [
        {
            "channel": ident,
            "alone": alone_grade(ident, path),
            "declared_by_subject": bool(channel(ident, path)["declared_by_subject"]),
            "claims": sorted(claim_ids),
        }
        for ident, claim_ids in sorted(by_channel.items())
    ]
    strongest = min(alone_grade(ident, path) for ident in by_channel)
    independent = independent_count(by_channel, path)
    grade = max(STRONGEST_GRADE, strongest - step * (independent - 1))
    return {
        "observed": True,
        "channels": rows,
        "independent_channels": independent,
        "strongest_alone": strongest,
        "evidence_grade": grade,
        "may_price": evidence.may_price(grade),
        "why": _why(rows, independent, strongest, grade),
    }


def _why(rows: list[dict[str, Any]], independent: int, strongest: int, grade: int) -> str:
    named = ", ".join(str(row["channel"]) for row in rows)
    if independent == 1 and len(rows) > 1:
        return (
            f"{len(rows)} channels ({named}) observed this response and all of them are the "
            f"subject's own, so they count as one: a subject cannot corroborate itself. The grade "
            f"stays at that channel's own rung, {grade}."
        )
    if independent == 1:
        return (
            f"one channel ({named}) observed this response, so nothing corroborates it and the "
            f"grade is that channel's own rung, {grade}."
        )
    return (
        f"{independent} independent channel(s) ({named}) observed this response. The strongest "
        f"alone holds rung {strongest}; each independent channel beyond the first strengthens it "
        f"one rung, giving {grade}."
    )


def claims_for(overlay: Any, response_id: str) -> list[dict[str, Any]]:
    """Every enactment claim in this overlay bound to one response, oldest id first."""
    return [
        dict(claim, id=ident)
        for ident, claim in sorted(overlay.claims.items())
        if str(claim.get("kind")) == KIND and str(claim.get("response")) == str(response_id)
    ]


def state(overlay: Any, response_id: str, path: Path | None = None) -> dict[str, Any]:
    """The action state of one response: which channels have observed it enacted, and at what grade.

    This is the read side of the loop decision ticket 18 Q3 closes — "was the recommendation acted
    upon?" answered from the ordinary model, with no store and no separate record to keep in sync.
    """
    return {"response": str(response_id), **corroborate(claims_for(overlay, response_id), path)}


def refuse_disagreeing_grade(doc: dict[str, Any], where: str) -> None:
    """An enactment claim declares the rung its own channel holds alone, or it is refused.

    The grade still travels **with** the claim, because everything downstream reads it there. What
    it may not do is disagree with the table: a claim free to name its own rung would let a
    self-declaration be typed at grade 1, and corroboration would be advisory.

    `ponytail:` always the shipped table. `schema.validate` takes no table path, so a claim
    validated while a test is exercising a scratch table is still graded against
    `TABLE_PATH` — which is right for every real caller and wrong for nobody yet. Threading a path
    through `validate()` is the upgrade, and it costs a parameter on every schema in the package.
    """
    ident = str(doc.get("channel", ""))
    try:
        expected = alone_grade(ident)
    except CorroborationError as exc:
        raise CorroborationError(f"{where}: {exc}") from None
    if int(doc["evidence_grade"]) != expected:
        raise CorroborationError(
            f"{where}: declares evidence grade {doc['evidence_grade']} on channel {ident!r}, which "
            f"holds grade {expected} alone. A channel's worth is a property of the channel, and a "
            "claim that could name its own would make the corroboration rule advisory."
        )
