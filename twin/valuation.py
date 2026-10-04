"""Re-derive an adopter valuation and restate its signed native amount (ticket 144).

A filing's currency stays on party.size.turnover. A foreign-currency valuation
needs a pinned FX envelope verified by its caller at the signature boundary.
Missing, undated and non-positive rates are missing instruments, never zero.
"""
from __future__ import annotations

import math
import re
from datetime import date
from typing import Any


class MissingInstrument(ValueError):
    """The declared money cannot be re-derived or converted from its sources."""


def rederive(party: dict[str, Any], valuation: dict[str, Any], currency: str,
             *, fx: dict[str, Any] | None = None) -> dict[str, Any]:
    path = str(valuation.get("derived_from_party_fact", ""))
    node: Any = party
    for key in path.split("."):
        if not isinstance(node, dict) or key not in node:
            raise MissingInstrument("valuation names no resolvable party fact: " + path)
        node = node[key]
    if not isinstance(node, dict) or set(node) != {"amount", "currency"}:
        raise MissingInstrument("valuation party fact is not signed amount and currency: " + path)
    periods = float(valuation.get("periods_per_year", 1))
    share = float(valuation.get("share_of_turnover", 1))
    if periods <= 0 or not math.isfinite(periods) or share < 0 or not math.isfinite(share):
        raise MissingInstrument("valuation share/periods do not define finite non-negative money")
    native = float(node["amount"]) * share / periods
    declared = float(valuation["amount"])
    if not math.isfinite(native) or not math.isfinite(declared) or abs(native - declared) > 1:
        raise MissingInstrument("valuation amount differs from the signed party fact's derivation")
    source_currency = str(node["currency"])
    result = {"amount": native, "currency": currency, "native_amount": native,
              "native_currency": source_currency, "party_fact": path, "fx": None}
    if source_currency == currency:
        return result
    if fx is None:
        raise MissingInstrument("no signature-verified pinned FX feed for " + source_currency + " -> " + currency)
    payload = fx["payload"]
    size = party.get("size")
    as_of = size.get("as_of") if isinstance(size, dict) else None
    if not isinstance(as_of, str) or not re.fullmatch(r"[0-9]{4}-[0-9]{2}-[0-9]{2}", as_of):
        raise MissingInstrument("foreign-currency valuation names no valid valuation date")
    try:
        valuation_date = date.fromisoformat(as_of)
    except ValueError as exc:
        raise MissingInstrument("foreign-currency valuation names no valid valuation date: " + as_of) from exc
    if not re.fullmatch(r"[0-9]{4}-(0[1-9]|1[0-2])", str(payload.get("period", ""))):
        raise MissingInstrument("pinned FX feed names no valid conversion month")
    if payload["period"] != valuation_date.isoformat()[:7]:
        raise MissingInstrument("pinned FX month " + payload["period"] + " has no rate for valuation date " + as_of)
    rates = dict(payload["rates"], **{str(payload["base"]): 1.0})
    for code in (source_currency, currency):
        rate = float(rates.get(code, 0))
        if rate <= 0 or not math.isfinite(rate):
            raise MissingInstrument("pinned FX feed names no positive finite rate for " + code)
    result["amount"] = native * float(rates[currency]) / float(rates[source_currency])
    result["fx"] = {"published_by": fx["published_by"], "version": fx["version"],
                    "period": payload["period"], "valuation_date": as_of, "source": payload["source"],
                    "from_rate": rates[source_currency], "to_rate": rates[currency]}
    return result
