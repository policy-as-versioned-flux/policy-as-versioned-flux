# Foreign-currency valuation date guard

Ludlow’s actual producer replay used the 2025-12-31 native filing amount with an August 2026 FX envelope. That output was removed from the unpublished adopter rollout. The publisher’s existing payload schema says a date outside the payload month has no rate.

The hub now parses a complete valid ISO calendar date and requires the pinned FX period to match its month. A missing, invalid or mismatched date raises `MissingInstrument`; the producer can report `CANNOT LOOK` without emitting an invalid price. A native-currency valuation still needs no FX date or instrument.

The boundary regression failed six cases before the fix and passes seven after it. Valuation module mypy passes. The official December 2025 table is separately captured and hashed; its authentic signed release remains a prerequisite for pricing Ludlow.

This does not turn the registered live coverage floor green. Its historical sample deficit remains a separate observed failure.
