"""A synthetic record never raises a grade (ADR-0032 point 4; twin ticket 12).

Eco-system ticket 141. A synthetic result is evidence about detection machinery, never about the
world (`twin/planter.py` `SHARED_PRIOR_LIMITATION`; driftwood's `drift/forced-campaign.yaml`).
Grade 2 is "repeated historical co-movement ... the repetition is the evidence", so a record that
earned grade 2 would have had to invent repeated history. This module names what a synthetic
record is and says whether a graded subject rests on one; `twin/pricing.py` refuses to price
through anything that does.

## What a synthetic record is

Today the estate marks a record synthetic in two places, and this module reads both:

* a `signal` whose `substrate` is a content-hash reference to bulk substrate of non-zero size.
  `twin/blob.py` calls the substrate synthetic by definition (decision ticket 07 Q4), and the
  fixtures' `ABSENT_SUBSTRATE` is the empty blob, size 0, which deliberately resolves to nothing
  and marks nothing.
* a `signal` whose `provenance` carries `synthetic`, `planted` or `injected` set true. The feed
  envelope stamp `injected: true` (ticket 92, the local clock's world simulator) never becomes a
  signal at all, because `twin/feed_signal.py` refuses it at lookup; a signal authored by hand
  with the same stamp in its provenance is refused here for the same reason.

## What it means for a grade to rest on one

The code never ties a grade to a record: a grade is an integer on an edge, a claim or a valuation.
So the chain from a grade to a record is read where the model actually records it:

1. a **claim** names the signal it binds (`claim.signal`); a claim bound to a synthetic signal
   rests on it, whatever its grade says.
2. a **regrade** that strengthened a subject (`direction: strengthened`) names its evidence in
   prose; a regrade whose evidence names a synthetic signal by id, or carries one of the marker
   words, strengthened the subject on a synthetic record.
3. the subject's **own prose** (an edge's `note`, a valuation's `basis`, a claim's `evidence`)
   carrying a marker word.

Legs 2 and 3 are a **net, not a proof**: the evidence fields are free text, so a determined author
can rest a grade on a synthetic drill without ever writing the word. The net catches the honest
case, which is the one ticket 30 round 1 would have created ("a marked synthetic incident record
counts as grade 2"), and a false positive costs an author one rewording, as `schema.py`'s
Article 9 net already trades. The limit is stated here rather than papered over.
"""

from __future__ import annotations

import re
from typing import Any, Iterable

from .blob import BlobRef

MARKERS = ("synthetic", "planted", "injected")

_WORDS = re.compile(r"[a-z0-9]+(?:-[a-z0-9]+)*")


def _words(text: Any) -> set[str]:
    """Every hyphenated token in the prose and every part of one: a signal id is matched whole
    (`incident-drill-2026`) and a marker word on either side of a hyphen (`planted-signal`)."""
    tokens = set(_WORDS.findall(str(text or "").lower()))
    return tokens | {part for token in tokens for part in token.split("-")}


def marker_in(text: Any) -> str | None:
    """The first marker word this prose carries, on word boundaries, or None."""
    words = _words(text)
    for marker in MARKERS:
        if marker in words:
            return marker
    return None


def is_synthetic_record(signal: dict[str, Any]) -> str | None:
    """Why this signal is a synthetic record, or None if nothing marks it as one."""
    raw = signal.get("substrate")
    if raw is not None:
        try:
            ref = BlobRef.parse(str(raw))
        except ValueError:
            ref = None
        if ref is not None and int(ref.size) > 0:
            return f"its substrate is bulk synthetic substrate ({ref.size} bytes at {ref.digest[:12]})"
    provenance = signal.get("provenance")
    if isinstance(provenance, dict):
        for marker in MARKERS:
            if provenance.get(marker) is True or str(provenance.get(marker, "")).lower() == "true":
                return f"its provenance is stamped {marker}: true"
    return None


def synthetic_records(overlay: Any) -> dict[str, str]:
    """Every synthetic signal in this overlay, id to the reason it is one."""
    out: dict[str, str] = {}
    for ident, signal in sorted(getattr(overlay, "signals", {}).items()):
        why = is_synthetic_record(signal)
        if why:
            out[str(ident)] = why
    return out


def _names_a_record(text: Any, records: dict[str, str]) -> str | None:
    words = _words(text)
    for ident in sorted(records):
        if ident in words:
            return ident
    return None


def rests_on(overlay: Any, subject: str, prose: Iterable[Any] = ()) -> str | None:
    """Why the grade of `subject` rests on a synthetic record, or None if nothing shows it does.

    `subject` is an edge or claim id in the overlay; `prose` is the subject's own evidence text
    (an edge's note, a valuation's basis) for the third leg. A valuation has no id and no regrade
    chain, so a caller passes its basis as prose and any string as the subject.
    """
    records = synthetic_records(overlay)
    claim = getattr(overlay, "claims", {}).get(subject)
    if claim is not None:
        bound = str(claim.get("signal", "")) if claim.get("signal") else ""
        if bound and bound in records:
            return f"claim {subject!r} binds signal {bound!r}, a synthetic record: {records[bound]}"
        marker = marker_in(claim.get("evidence"))
        if marker:
            return f"claim {subject!r} says its evidence is {marker}"
    for ident, regrade in sorted(getattr(overlay, "regrades", {}).items()):
        if str(regrade.get("subject")) != str(subject):
            continue
        if int(regrade["to_grade"]) >= int(regrade["from_grade"]):
            continue  # a weakening cannot raise a grade, whatever it cites
        named = _names_a_record(regrade.get("evidence"), records)
        if named:
            return (
                f"regrade {ident!r} strengthened {subject!r} to grade {regrade['to_grade']} on "
                f"signal {named!r}, a synthetic record: {records[named]}"
            )
        marker = marker_in(regrade.get("evidence"))
        if marker:
            return (
                f"regrade {ident!r} strengthened {subject!r} to grade {regrade['to_grade']} and "
                f"says its evidence is {marker}"
            )
    for text in prose:
        marker = marker_in(text)
        if marker:
            return f"{subject!r} says its own evidence is {marker}"
        named = _names_a_record(text, records)
        if named:
            return f"{subject!r} cites signal {named!r}, a synthetic record: {records[named]}"
    return None
