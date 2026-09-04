"""A pinned feed version becomes one dated signal, by lookup, with no judgement.

Ticket 29 / ticket 11 resolution 3, spec user story 45: "As the twin, I want a subscribed feed
version to map to one dated signal by lookup, so that the clock binds without judgement."

The rule, verbatim from ticket 11's resolution: *each new pinned version of a subscribed feed maps
to one signal with no judgement; `date` is the payload's event date where its schema carries one;
provenance carries `published_at`, tag and commit; `source` is the signed tag; `steep` comes from a
fixed table keyed by feed name; grade 5, contestable.*

**Why a table and not a classifier.** `twin/signal_classify.py` exists and is a heuristic — a good
one, measured against a labelled corpus, and still a heuristic. Ticket 28 (superseding ADR-0015
point 5) says a clock consumes only committed, reviewed claim files and reasoning is a skill a
human runs. A pinned version arriving on the 06:20 sweep is not a judgement call: the estate
already decided what kind of thing that feed is when it subscribed to it, in a pull request. So
this module reads `STEEP_BY_FEED` and nothing else, and a feed name with no row is a **named hole**
that raises rather than a guess — the hole is closed by adding a row in a reviewed diff, which is
the same act as subscribing to the feed in the first place.

**What this deliberately does not do.** It carries no probability, no elasticity, no price and no
scenario binding. `date` is read from a fixed key per feed or from the envelope's own publication
date; it is never inferred from prose. Binding the signal to a component is a claim, contestable,
and it is somebody else's module (`twin/challenges.py`, `twin/signal_classify.py` for the
skill-run path). The adopter's `twin/signals.yaml` binds a *pin* to a *standing scenario*; that is
the other half of the same seam and lives in the adopter's repo because the scenario library does.

**Grade 5.** The signal is machine-derived from a publisher's own envelope with no human having
looked at it, which is the bottom rung of the evidence ladder, and grade 5 never prices
(`grade_5_only_path_never_prices`). That is the safety argument for binding on a clock at all.

`ponytail:` `tag` and `commit` are handed in by the caller rather than discovered here. The caller
is whatever verified the signature — the source boundary — and it already holds both; discovering
them here would mean this module deciding which ref corresponds to a version, which is exactly the
judgement it exists not to make. Upgrade path: when the feed envelope itself carries the tag it was
published under (ADR-0019 does not require it today), read it from the envelope and keep the
argument as an override.
"""

from __future__ import annotations

import re
from typing import Any

from . import schema

# Grade 5, contestable — see the docstring. Named rather than inlined so a reader grepping for the
# rung finds this path with the others.
EVIDENCE_GRADE = 5

# THE FIXED TABLE. Keyed by feed name, as ticket 11 resolved it. Each row is a subscription
# decision already taken in a reviewed pull request, written down so that the clock does not have
# to take it again at 06:20.
STEEP_BY_FEED: dict[str, str] = {
    # A regulator's fine schedule is a political fact: it moves when a legislature or a regulator
    # moves, not when a market or a vendor does.
    "penalty-schema": "political",
    # Vendor lifecycles, vulnerability disclosures and a register of who can be attacked how are
    # facts about technology and the people who build it.
    "eol": "technological",
    "cve": "technological",
    "threat-register": "technological",
    # Exchange rates and market prices are the economy talking.
    "fx": "economic",
    "market-moves": "economic",
    # Added 2026-08-29 with the same reasoning applied to the two feeds that did not exist when
    # ticket 11 was resolved. A premium is a price under a contract, and forward intelligence is a
    # priced shock under a perspective; both are money moving, so both are economic.
    "quote": "economic",
    "forward-intel": "economic",
}

# Feeds deliberately NOT in the table, with the reason, so that "no row" can be read as a decision
# where it is one. A headline is a claim somebody made, and what kind of thing it is IS the
# judgement — ticket 23 / ticket 50 make that a skill a human runs over the unbound pool.
EXCLUDED_FROM_LOOKUP: dict[str, str] = {
    "news": (
        "a headline is not a fact about the world, it is a report of one, and deciding which it "
        "moves is the judgement the classify-and-judge skill exists for (ticket 50). Bound by a "
        "human through the unbound pool, never on the clock."
    ),
}

# The one top-level payload key, per feed, that carries the event's own date. Ticket 11: "`date` is
# the payload's event date **where its schema carries one**." Most of these feeds are registers
# rather than events — an eol feed carries one date per component, not one date — and for those the
# dated fact is the publication itself, which the envelope already carries. So this table is short
# on purpose, and short is not an omission.
EVENT_DATE_KEY: dict[str, str] = {
    "quote": "valid_from",  # the date the cover this quote prices attaches
}

_SLUG = re.compile(r"[^a-z0-9]+")


class FeedSignalError(ValueError):
    """A feed this table has no row for, or an envelope that is not one."""


def _key(feed_name: str) -> str:
    """The table key for a feed name.

    `quote-driftwood`, `quote-tuppence` and `quote-ludlow` are one feed KIND published per adopter
    (ticket 36), so they key on `quote`. Exact name first, so a feed genuinely called
    `threat-register` is never mistaken for a `threat` row that does not exist.
    """
    if feed_name in STEEP_BY_FEED or feed_name in EXCLUDED_FROM_LOOKUP:
        return feed_name
    head = feed_name.split("-", 1)[0]
    return head if head in STEEP_BY_FEED or head in EXCLUDED_FROM_LOOKUP else feed_name


def steep_for(feed_name: str) -> str:
    """The STEEP letter for a feed, from the table. Raises on a hole rather than guessing."""
    key = _key(feed_name)
    if key in EXCLUDED_FROM_LOOKUP:
        raise FeedSignalError(
            f"{feed_name!r} is excluded from the version->signal lookup: {EXCLUDED_FROM_LOOKUP[key]}"
        )
    try:
        return STEEP_BY_FEED[key]
    except KeyError:
        raise FeedSignalError(
            f"no row in STEEP_BY_FEED for feed {feed_name!r}. That is a hole in the table, not a "
            "reason to guess: add a row in a reviewed pull request, the way the subscription "
            "itself was added."
        ) from None


def slug(*parts: str) -> str:
    return _SLUG.sub("-", "-".join(parts).lower()).strip("-")


def signal_for(envelope: dict[str, Any], tag: str, commit: str) -> dict[str, Any]:
    """One dated signal for one pinned feed version. Pure, total, and mechanical.

    `envelope` is an ADR-0019 feed envelope as published (`kind, name, version, published_by,
    published_at, payload_schema, payload`). `tag` and `commit` are the signed tag the version was
    published under and the commit it points at — the caller's, because the caller is what verified
    the signature.
    """
    for field in ("kind", "name", "version", "published_by", "published_at"):
        if not str(envelope.get(field, "")).strip():
            raise FeedSignalError(f"not a feed envelope: {field} is missing or empty")
    if envelope["kind"] != "feed":
        raise FeedSignalError(f"kind is {envelope['kind']!r}, and only a feed is looked up here")
    # Ticket 92: the local clock's world simulator stamps a rehearsal signal `injected: true`.
    # A rehearsal is never cited, so it never becomes a signal here -- not even a grade-5 one.
    if envelope.get("injected"):
        raise FeedSignalError(
            "this envelope is marked injected: it is a world-simulator rehearsal signal "
            "(talk/local-clock.sh --inject) and never becomes a signal by lookup"
        )
    if not str(tag).strip() or not str(commit).strip():
        raise FeedSignalError(
            "a signal needs the signed tag it came from and the commit that tag points at; "
            "without them the source is a name and the provenance is a claim"
        )

    name, version = str(envelope["name"]), str(envelope["version"])
    published_at = str(envelope["published_at"])
    payload = envelope.get("payload") or {}
    key = _key(name)

    # The event date where the schema carries one, the publication date otherwise. Both are read;
    # neither is inferred.
    date_key = EVENT_DATE_KEY.get(key)
    event_date = str(payload.get(date_key, "")) if date_key and isinstance(payload, dict) else ""
    dated = event_date if schema.ISO_DATE.match(event_date or "") else published_at[:10]

    doc = {
        "id": slug(str(envelope["published_by"]), name, version, "published"),
        "date": dated,
        "steep": steep_for(name),
        "source": tag,
        "statement": (
            f"{envelope['published_by']} published {name} version {version} on "
            f"{published_at}, and this organisation pins it."
        ),
        "provenance": {
            "published_at": published_at,
            "tag": tag,
            "commit": commit,
            "feed": name,
            "version": version,
            "published_by": str(envelope["published_by"]),
            "bound_by": "twin.feed_signal lookup",
            "evidence_grade": EVIDENCE_GRADE,
            "contestable": (
                "grade 5: derived by table lookup with no human having read it, so it never "
                "prices and any binding it supports is challengeable"
            ),
            "date_basis": (
                f"payload.{date_key}" if dated == event_date and date_key else "envelope.published_at"
            ),
        },
    }
    schema.validate("signal", doc, f"feed_signal {name}@{version}")
    return doc


def demo() -> None:
    """The runnable check. `python3 -m twin.feed_signal`."""
    quote = {
        "kind": "feed", "name": "quote-driftwood", "version": "1.0.0", "published_by": "insurer",
        "published_at": "2026-08-28T00:00:00Z", "payload_schema": "quote/payload.schema.json",
        "payload": {"valid_from": "2026-09-01", "currency": "GBP"},
    }
    one = signal_for(quote, tag="v1.0.0", commit="a" * 40)
    assert one["steep"] == "economic", one
    assert one["date"] == "2026-09-01", one          # the payload's own event date wins
    assert one["source"] == "v1.0.0", one
    assert one["provenance"]["published_at"] == "2026-08-28T00:00:00Z", one
    assert one["provenance"]["commit"] == "a" * 40, one
    assert one["provenance"]["date_basis"] == "payload.valid_from", one

    # ONE signal, deterministically: the same envelope maps to the same document, every time.
    assert signal_for(quote, tag="v1.0.0", commit="a" * 40) == one

    ico = {**quote, "name": "penalty-schema", "version": "3.0.0", "published_by": "ico",
           "published_at": "2026-08-28T10:00:00+01:00", "payload": {"regimes": {}}}
    two = signal_for(ico, tag="v3.0.0", commit="b" * 40)
    assert two["steep"] == "political", two
    assert two["date"] == "2026-08-28", two          # no event date in the schema: publication
    assert two["provenance"]["date_basis"] == "envelope.published_at", two
    assert two["id"] != one["id"], (one["id"], two["id"])

    # A hole is named, never guessed.
    for bad, expect in (("weather", "no row in STEEP_BY_FEED"), ("news", "excluded")):
        try:
            steep_for(bad)
        except FeedSignalError as exc:
            assert expect in str(exc), exc
        else:  # pragma: no cover - the guard is the point
            raise AssertionError(f"{bad} should have no row")

    # No tag, no commit, no signal: the provenance is the whole value of the lookup.
    for missing in ({"tag": "", "commit": "c" * 40}, {"tag": "v1.0.0", "commit": ""}):
        try:
            signal_for(quote, **missing)  # type: ignore[arg-type]
        except FeedSignalError:
            pass
        else:  # pragma: no cover
            raise AssertionError(f"{missing} should refuse")

    # No judgement anywhere: no field of the emitted document is a probability, an amount or a
    # recommendation. Checked on the KEYS and on the value types, not on the prose — the
    # `contestable` note says the word "prices" while asserting that this path never does.
    flat = {**one, **one["provenance"]}
    for field, value in flat.items():
        assert not any(w in field for w in ("probability", "price", "amount", "recommend", "action")), field
        assert not isinstance(value, float), (field, value)

    print(f"ok  feed_signal: {len(STEEP_BY_FEED)} rows, {len(EXCLUDED_FROM_LOOKUP)} excluded; "
          f"{two['id']} steep={two['steep']} date={two['date']} source={two['source']}")


if __name__ == "__main__":
    demo()
