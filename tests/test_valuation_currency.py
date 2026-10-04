"""Ticket 144's valuation boundary: signed native facts and a dated FX envelope."""
from __future__ import annotations

import pytest

from twin.valuation import MissingInstrument, rederive


def test_usd_filing_is_converted_with_an_explicit_dated_fx_rate():
    party = {"size": {"turnover": {"amount": 200, "currency": "USD"}, "as_of": "2025-12-31"}}
    value = {"amount": 50, "derived_from_party_fact": "size.turnover", "share_of_turnover": 0.25}
    fx = {"published_by": "feeds", "version": "1.0.0", "payload": {
        "period": "2025-12", "base": "GBP", "rates": {"USD": 2}, "source": "published monthly table"}}
    got = rederive(party, value, "GBP", fx=fx)
    assert got["amount"] == 25
    assert got["native_amount"] == 50
    assert got["fx"]["period"] == "2025-12"
    later = rederive(party, value, "GBP", fx={**fx, "payload": {**fx["payload"], "period": "2026-08"}})
    assert later["fx"]["valuation_date"] == "2025-12-31" and later["fx"]["period"] == "2026-08"
    for bad in (None, {**fx, "payload": {**fx["payload"], "period": "not-dated"}},
                {**fx, "payload": {**fx["payload"], "rates": {"USD": 0}}}):
        with pytest.raises(MissingInstrument):
            rederive(party, value, "GBP", fx=bad)
    with pytest.raises(MissingInstrument):
        rederive(party, {**value, "amount": 60}, "GBP", fx=fx)
