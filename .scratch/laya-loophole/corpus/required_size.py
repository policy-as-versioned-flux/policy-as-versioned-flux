#!/usr/bin/env python3
"""How many labelled items one skill needs before a Laya score means anything.

Map ticket 03 item 3 and item 4. This exists so that "42 items is not enough" is a DERIVED number
rather than an opinion, and so that the number can be re-derived when the target changes.

THE TARGET IS TICKET 04's OWN. Ticket 04 expects an expected-calibration-error near 0.129 and must
distinguish it from the vendor's headline 0.081. A measurement whose noise is the size of the gap
it is measuring decides nothing, so the required n falls out of that gap.

TWO ROUTES, DELIBERATELY. The charitable route sizes the whole-set standard error. The honest
route sizes the per-bin error that the ECE estimator actually incurs. Both are printed, because
quoting only the first would be this estate doing what ticket 01 caught the vendor doing.
"""

from __future__ import annotations

import datetime
import math

# The two calibration numbers ticket 04 has to tell apart (map Notes, corrected by ticket 01).
ECE_EXPECTED = 0.129
ECE_VENDOR_HEADLINE = 0.081

# The accuracy band the benchmark author's own card warns about (map Notes, ticket 01): a score
# much above 0.75 means the model learned the teacher's quirks rather than the task.
ACCURACY_BAND = 0.75

ECE_BINS = 10  # the usual binning for an expected-calibration-error estimate

# What this estate holds, measured 2026-09-21.
MERGED_HUMAN_LABELS = 1       # build_corpus.py, origin/main, three adopters
HAND_AUTHORED_ALL_SIX = 42
LARGEST_HAND_CORPUS = 23      # signal-classify

TODAY = datetime.date(2026, 9, 21)
EARLIEST_HORIZON = datetime.date(2027, 8, 28)  # driftwood's six scenarios
SCENARIOS_ACROSS_ADOPTERS = 18


def required_n(gap: float, accuracy: float = ACCURACY_BAND) -> int:
    """Items needed so the standard error sits at half the gap being measured."""
    target_se = gap / 2
    return math.ceil(accuracy * (1 - accuracy) / target_se**2)


def accuracy_lower_bound(n: int) -> float | None:
    """The 95% lower bound on true accuracy for a skill that scored a PERFECT n out of n.

    The rule of three: with zero observed failures in n trials, the 95% upper bound on the failure
    rate is 3/n. All six heuristics score 1.0 on their own corpora today, so this is the honest
    reading of every one of those scores.
    """
    if n < 3:
        return None
    return max(0.0, 1 - 3 / n)


def main() -> None:
    gap = ECE_EXPECTED - ECE_VENDOR_HEADLINE
    charitable = required_n(gap)
    honest = charitable * ECE_BINS

    print("required corpus size, derived from ticket 04's own target")
    print(f"  gap to resolve                 {ECE_EXPECTED} - {ECE_VENDOR_HEADLINE} = {gap:.3f}")
    print(f"  charitable (whole-set SE)      {charitable} items per skill")
    print(f"  honest (per-bin, {ECE_BINS} bins)      {honest} items per skill")
    print(f"  Laya's own published recipe    300 items per question schema")
    print()
    print("what this estate holds")
    print(f"  merged human-authored labels   {MERGED_HUMAN_LABELS}")
    print(f"  hand-authored, all six skills  {HAND_AUTHORED_ALL_SIX}")
    print(f"  largest single corpus          {LARGEST_HAND_CORPUS}")
    print(f"  shortfall, merged claims       {charitable / MERGED_HUMAN_LABELS:.0f}x")
    print(f"  shortfall, largest corpus      {charitable / LARGEST_HAND_CORPUS:.1f}x")
    print(f"  six skills at {charitable} each        {6 * charitable} items")
    print()
    print("what a PERFECT score on a corpus of each size actually bounds")
    for n in (1, 3, 4, 5, 23, 42, charitable):
        bound = accuracy_lower_bound(n)
        shown = "nothing; one item bounds nothing" if bound is None else f"true accuracy >= {bound:.3f}"
        print(f"  n = {n:<5} scored 1.0  ->  {shown}")
    print()
    print("when the first label the world wrote arrives")
    print(f"  today {TODAY}, earliest scenario horizon {EARLIEST_HORIZON}")
    print(f"  days away {(EARLIEST_HORIZON - TODAY).days}, and at most {SCENARIOS_ACROSS_ADOPTERS} items when it does")


if __name__ == "__main__":
    main()
