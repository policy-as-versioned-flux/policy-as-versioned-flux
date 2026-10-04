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
    with pytest.raises(MissingInstrument, match="2026-08.*2025-12-31"):
        rederive(party, value, "GBP", fx={**fx, "payload": {**fx["payload"], "period": "2026-08"}})
    for bad in (None, {**fx, "payload": {**fx["payload"], "period": "not-dated"}},
                {**fx, "payload": {**fx["payload"], "rates": {"USD": 0}}}):
        with pytest.raises(MissingInstrument):
            rederive(party, value, "GBP", fx=bad)
    with pytest.raises(MissingInstrument):
        rederive(party, {**value, "amount": 60}, "GBP", fx=fx)


@pytest.mark.parametrize("as_of", [None, "", "2025-12", "2025-02-30", "20251231"])
def test_foreign_currency_requires_a_valid_filing_date(as_of):
    party = {"size": {"turnover": {"amount": 200, "currency": "USD"}}}
    if as_of is not None:
        party["size"]["as_of"] = as_of
    value = {"amount": 200, "derived_from_party_fact": "size.turnover"}
    fx = {"published_by": "feeds", "version": "2.0.0", "payload": {
        "period": "2025-12", "base": "GBP", "rates": {"USD": 1.3126}, "source": "published monthly table"}}
    with pytest.raises(MissingInstrument, match="valid valuation date"):
        rederive(party, value, "GBP", fx=fx)


def test_native_currency_needs_no_fx_date_or_instrument():
    party = {"size": {"turnover": {"amount": 200, "currency": "GBP"}}}
    value = {"amount": 200, "derived_from_party_fact": "size.turnover"}
    assert rederive(party, value, "GBP")["amount"] == 200
