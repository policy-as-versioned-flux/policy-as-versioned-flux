"""The trade-off curve across the ensemble, with a marked default (build ticket 33), from decision
tickets 09 and 13.

`twin/pricing.py` already reports what a response costs and what it earns in mitigation credit,
under one causal account's own propagation. `twin/causal_accounts.py` already lets rival causal
accounts disagree about how a shock propagates, with no privileged account. Until this module, the
two never touched: a response's net cost of risk was one number, read off whichever account
happened to be in the graph, and cost and credit sat in the same artefact with nothing computing
the net between them (`twin/pricing.py`'s own docstring names this as build ticket 33's job).

**A net figure is computed, never a rank.** For each admitted response, cost is authored and fixed
across the ensemble; credit is not — it is what the causal account you believe was priced through.
`net_cost_of_risk = cost.mode - credit.mode`, computed identically under every named account and
reported **per account**, side by side, never averaged into one line. `twin/pricing.py` runs once
per account, unmodified — the causal account is the only thing that changes between calls, so a
difference in the curve is a difference the account made and nothing else.

**The default is a computed point, not a verdict.** Decision ticket 09's objective function is
"minimise total net cost of risk", marked as a default rather than an answer. The default here is
the option whose *mean* net cost of risk across the named accounts is lowest — mean rather than any
one account's own figure, because no account is privileged (`twin/causal_accounts.py`) — and its
`basis` says so in the artefact. **When the accounts disagree about which option is cheapest, that
disagreement is reported explicitly and first**, because it is, per the spec, "the most
decision-relevant thing on the page" — never averaged away underneath the default.
"""

from __future__ import annotations

from typing import Any

from . import pricing
from .canon import walk_keys
from .artefact import ArtefactError
from .model import ModelError, Overlay
from .pert import quantise

# This module's own vocabulary, closed to exactly it — deliberately not `pricing.BODY_KEYS |
# {...}`. Each `ensemble[i]["price"]` is a whole `pricing.price()` body, already validated
# against pricing's own closed vocabulary before this module ever receives it; merging that
# vocabulary into this set would legalise any of pricing's ~40 field names anywhere in *this*
# module's own top-level structure, not only inside the sub-bodies where they belong — a
# materially weaker guarantee than either module makes alone. See `_own_shape` below: the embedded
# sub-bodies are excluded from this check and trusted to their own instead.
BODY_KEYS = frozenset(
    {
        "origin", "perspective", "accounts", "ensemble", "account",
        "curve", "option", "name", "net_cost_of_risk", "by_account", "min", "max", "range",
        "credited_by", "uncredited_by",
        "agreement", "cheapest_by_account", "unanimous", "note",
        "default", "basis", "reading_note",
    }
)


class TradeOffError(ModelError):
    """Fewer than two accounts were named, or no admitted response could be compared."""


def _net(entry: dict[str, Any]) -> tuple[float, bool]:
    """A response's net cost of risk under one account: cost minus credit, if any was earned.

    Point-wise on the modal figures, the same exact-arithmetic discipline `twin/pricing.py`'s own
    `_priced_triple` uses for a magnitude scaled by an influence — this is a magnitude (the
    authored cost) reduced by another (the credit), not a distribution composed with one, so there
    is nothing here for a Monte-Carlo draw to add.
    """
    cost_mode = float(entry["cost"]["mode"])
    # `pricing.price()` sets `mitigation` on every priced entry, never omits it — `.get` rather
    # than `[...]` only because `credit` itself is the part that is genuinely absent when a claim
    # earned nothing.
    credit = entry["mitigation"].get("credit")
    if credit is None:
        return cost_mode, False
    return cost_mode - float(credit["mode"]), True


def curve(
    overlay: Overlay,
    perspective: dict[str, Any],
    origin: str,
    responses: dict[str, dict[str, Any]],
    account_ids: list[str],
) -> dict[str, Any]:
    """The net cost of risk of every admitted response, under every named causal account.

    `ids` reads identically to `causal_accounts.ensemble_spread`'s own contract: at least two
    accounts, sorted and de-duplicated, none privileged. Dropping any one account changes nothing
    about how the remaining ones are computed, because each account's price is computed from a
    fresh call to `pricing.price` against that account's own graph alone.
    """
    ids = sorted(dict.fromkeys(str(i) for i in account_ids))
    if len(ids) < 2:
        raise TradeOffError(
            f"{len(ids)} account(s) named; a trade-off curve across the ensemble needs at least "
            "two rival accounts to have a curve across"
        )

    ensemble: list[dict[str, Any]] = []
    by_account: dict[str, dict[str, float]] = {a: {} for a in ids}
    credited_by: dict[str, list[str]] = {}
    names: dict[str, str] = {}
    for account_id in ids:
        graph = overlay.causal_graph(account_id)
        priced = pricing.price(graph, perspective, origin, responses)
        ensemble.append({"account": account_id, "price": priced})
        for entry in priced["responses"]["priced"]:
            option_id = entry["option"]
            names[option_id] = entry["name"]
            net, credited = _net(entry)
            by_account[account_id][option_id] = net
            if credited:
                credited_by.setdefault(option_id, []).append(account_id)

    option_ids = sorted(names)
    if not option_ids:
        raise TradeOffError(
            "no admitted response survived the constraint pre-filter; there is nothing to compare "
            "a net cost of risk across"
        )

    assembled = _assemble(ids, option_ids, names, by_account, credited_by)
    body = {
        "origin": origin,
        "perspective": str(perspective["id"]),
        "accounts": ids,
        "ensemble": ensemble,
        **assembled,
        "reading_note": (
            "a curve, not an answer. Cost and credit are reported per account, side by side, for "
            "every admitted response; the default above is one point on it, marked and reasoned, "
            "never asserted as the twin's own choice — the reader draws the trade-off"
        ),
    }
    refuse_undeclared_keys(body)
    return body


def _assemble(
    ids: list[str],
    option_ids: list[str],
    names: dict[str, str],
    by_account: dict[str, dict[str, float]],
    credited_by: dict[str, list[str]],
) -> dict[str, Any]:
    """The pure part of `curve()`: the per-option rows, the ranking agreement across accounts, and
    the computed default — none of it needing a model repository, so it is a plain function of
    already-computed numbers and is exercised directly with synthetic figures in
    `tests/test_tradeoff.py` (a real fixture with the specific numbers to make two accounts
    disagree about which response is cheapest has not been authored; this is the honest substitute
    until one is).
    """
    points = []
    for option_id in option_ids:
        row = {a: by_account[a][option_id] for a in ids}
        values = list(row.values())
        points.append(
            {
                "option": option_id,
                "name": names[option_id],
                "net_cost_of_risk": {
                    "by_account": {a: quantise(v) for a, v in row.items()},
                    "min": quantise(min(values)),
                    "max": quantise(max(values)),
                    "range": quantise(max(values) - min(values)),
                },
                "credited_by": sorted(credited_by.get(option_id, [])),
                "uncredited_by": sorted(set(ids) - set(credited_by.get(option_id, []))),
            }
        )

    cheapest_by_account = {a: min(option_ids, key=lambda o: by_account[a][o]) for a in ids}
    unanimous = len(set(cheapest_by_account.values())) == 1

    default_option = min(option_ids, key=lambda o: sum(by_account[a][o] for a in ids) / len(ids))

    return {
        "curve": points,
        "agreement": {
            "cheapest_by_account": cheapest_by_account,
            "unanimous": unanimous,
            "note": (
                "every named account agrees which response is cheapest"
                if unanimous
                else "the named accounts disagree about which response is cheapest — reported here "
                "rather than smoothed into the default below, because a credible disagreement "
                "about the mechanism is the most decision-relevant fact on the page"
            ),
        },
        "default": {
            "option": default_option,
            "name": names[default_option],
            "basis": (
                "the option whose mean net cost of risk across the named accounts is lowest — a "
                "default point for a reader who wants one, computed rather than declared, and not "
                "a recommendation. No account is privileged, so the mean rather than any one "
                "account's own figure is what breaks the tie; naming or dropping a rival account "
                "can move it"
            ),
        },
    }


def _own_shape(body: dict[str, Any]) -> dict[str, Any]:
    """`body`, with each embedded `pricing.price()` sub-body dropped down to just its account id.

    `pricing.price()` already validated its own vocabulary before ever handing this module a
    result (`pricing.refuse_undeclared_keys` runs inside `price()` itself), so re-scanning it here
    would only ever do one of two things: pass trivially because it was already closed, or force
    this module's own `BODY_KEYS` to widen to cover a vocabulary that belongs to `pricing.py`. The
    embedded body is excluded from this walk and trusted to its own check instead.
    """
    return {**body, "ensemble": [{"account": entry["account"]} for entry in body["ensemble"]]}


_ACCOUNT_KEYED = ("by_account", "cheapest_by_account")


def _blank_account_keyed_maps(node: Any) -> Any:
    """`node`, with every account-keyed map emptied out before the key-closure walk.

    `by_account` and `cheapest_by_account` are keyed by whatever id the caller named — data, not a
    declared field name a closed set could enumerate in advance. This is exactly the reason
    `causal_accounts.py`'s own `by_account` map carries no closure check of its own; here the map
    sits beside genuinely closed fields, so the exemption is scoped to these two keys rather than
    dropped for the whole body.
    """
    if isinstance(node, dict):
        return {k: ({} if k in _ACCOUNT_KEYED else _blank_account_keyed_maps(v)) for k, v in node.items()}
    if isinstance(node, list):
        return [_blank_account_keyed_maps(v) for v in node]
    return node


def refuse_undeclared_keys(body: dict[str, Any]) -> None:
    """The trade-off-curve body is closed to its own vocabulary. A key nobody declared does not
    serialise, and neither does pricing's own vocabulary leaking in unchecked — see `_own_shape`.
    """
    shape = _blank_account_keyed_maps(_own_shape(body))
    stray = sorted(set(walk_keys(shape)) - BODY_KEYS)
    if stray:
        raise ArtefactError(
            f"a trade-off curve carries undeclared field(s) {', '.join(stray)}. This body is "
            "closed: adding a slot beside the curve needs an authorising decision ticket."
        )
