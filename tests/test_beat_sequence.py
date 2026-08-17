"""The demo sequence is b -> b -> c -> a, structurally (build ticket 77; decision ticket 22).

The ordering property itself — beats named in the declared order, £ absent from the first two,
propose preceding price/trade-off in the third — lives in exactly one place:
`the_demo_sequence_earns_credibility_before_it_spends_it` (`twin/invariants/harness.py`). Code
quality and testing review of this ticket both flagged an earlier draft that re-implemented the
same three regex checks a second time here; a property with one definition and two independently-
maintained copies is worse than one definition, the same principle `beat-royal-mail.sh` already
states for itself ("asserted by the harness guard... repeating them here would be a third copy").
So this file runs that one guard through `invariants.run(only=[...])`, the pattern
`tests/test_invariant_suite.py`'s own `_one()` helper already established for exercising a single
named check — pytest speed, one implementation.
"""

from __future__ import annotations

from pathlib import Path

from twin import PACKAGE_DIR, invariants
from twin.invariants import FAIL

SEQUENCE = PACKAGE_DIR / "beat-sequence.sh"
GUARD = "the_demo_sequence_earns_credibility_before_it_spends_it"


def test_the_sequence_script_is_executable() -> None:
    assert SEQUENCE.stat().st_mode & 0o111, "the sequence script is not executable"


def test_the_demo_sequence_guard_passes(tmp_path: Path) -> None:
    results, _ = invariants.run(only=[GUARD], tmp=tmp_path)
    assert len(results) == 1
    result = results[0]
    assert result.status != FAIL, result.detail
