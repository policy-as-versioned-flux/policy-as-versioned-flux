#!/usr/bin/env python3
"""proposer_bounds.py — bound the AI proposer; keep the gate as the hard backstop.

Story 33. The war-gamer (../wargamer) can open signed policy PRs. That is a scary
capability: a feed storm, a mis-estimated band, or a persistent bad idea could
flood reviewers or wear them down. This wraps `wargamer.proposals()` with three
*advisory* bounds — and one *non-negotiable* one:

  confidence   — a barely-over-band verdict flip (driftwood at £41,095 vs a
                 £40,000 band = 2.7% over) is band-edge noise, not signal. Below
                 CONFIDENCE_MIN it is HELD for human triage, not auto-opened.
  rate-limit   — at most RATE_LIMIT PRs auto-opened per run; the rest DEFER to the
                 next run. One skimmer feed can't open twenty PRs at once.
  learn-from-  — the rejection ledger (rejections.json). A proposal a human has
  rejections     declined >= reject_suppress times is SUPPRESSED (stop re-proposing
                 what keeps getting a no); fewer rejections still propose but carry
                 the history so the reviewer isn't asked cold.

The hard backstop is NOT any of these. It is the PR gate + human review that every
surviving proposal STILL rides: the bounds only decide what reaches a reviewer,
never what merges. `merged=False` and `required_gate` are preserved on every
emitted proposal, and this module — like wargamer — exposes NO merge()/approve().
The bounds reduce noise; they cannot grant authority. That is the honest safety
story: the AI is bounded for courtesy, gated for safety.

ponytail: scenario-move drifts get a fixed STRUCTURAL confidence (a clean TCoR
crossover move-change is a solid categorical signal); an enforcement verdict flip
gets a *computed* materiality from how far past the band it sits. Upgrade path:
carry the TCoR delta (chosen vs deployed move) on the scenario row and compute its
materiality the same way. Not worth the re-plumb until a scenario drift is marginal.

Usage:
    proposer_bounds.py bounded    [--rejections rejections.json]   # proposals after bounds
    proposer_bounds.py dispositions                                # one line per drift + why
    proposer_bounds.py selfcheck
"""
from __future__ import annotations

import argparse
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "wargamer"))
import wargamer  # noqa: E402  the proposer we are bounding

CONFIDENCE_MIN = 0.05      # below this a verdict flip is band-edge noise -> hold
RATE_LIMIT = 3             # max PRs auto-opened per run; rest defer
STRUCTURAL_CONFIDENCE = 0.5  # a clean TCoR move-change (no £-margin on the row)
DEFAULT_REJECTIONS = os.path.join(HERE, "rejections.json")


def confidence(row):
    """Materiality of a drift in [0,1]. Enforcement flip: how far past the band,
    normalised by the band (capped at 1). Scenario move-change: structural."""
    tol = row.get("tolerance")
    rb = row.get("risk_bought_current")
    if tol and rb is not None:
        return max(0.0, min(1.0, (rb - tol) / tol))
    return STRUCTURAL_CONFIDENCE


def _key(row):
    return f"{row['org']}/{row['control']}"


def bound(rows, rejections):
    """Apply the bounds to war-game drift rows, in order: learned-rejection ->
    confidence -> rate-limit. Returns a disposition per drifting row."""
    suppress_at = rejections.get("reject_suppress", 2)
    ledger = rejections.get("rejections", {})
    out = []
    opened = 0
    for row in rows:
        if not row["drift"]:
            continue
        key = _key(row)
        conf = confidence(row)
        rej = ledger.get(key, {})
        rej_count = rej.get("count", 0)
        d = {"key": key, "kind": row["kind"], "confidence": round(conf, 4),
             "rejected_before": rej_count}

        if rej_count >= suppress_at:
            d["disposition"] = "suppress-learned-rejection"
            d["why"] = f"human rejected this {rej_count}x (>= {suppress_at}) — the loop learned, stop re-proposing"
            d["proposal"] = None
        elif conf < CONFIDENCE_MIN:
            d["disposition"] = "hold-low-confidence"
            d["why"] = f"confidence {conf:.3f} < {CONFIDENCE_MIN} — band-edge, surface for human triage not auto-PR"
            d["proposal"] = None
        elif opened >= RATE_LIMIT:
            d["disposition"] = "defer-rate-limit"
            d["why"] = f"rate limit {RATE_LIMIT} PRs/run reached — deferred to next run"
            d["proposal"] = None
        else:
            opened += 1
            p = wargamer.propose(row)
            # The hard backstop is preserved on every emitted proposal, always.
            assert p["merged"] is False and p["auto_merge"] is False, p
            assert p["required_gate"], p
            if rej_count:
                p["prior_rejections"] = rej_count
                p["note"] = f"previously rejected {rej_count}x (< {suppress_at}); re-proposed with history for the reviewer"
            d["disposition"] = "propose"
            d["why"] = f"confidence {conf:.3f} >= {CONFIDENCE_MIN}, not over-rejected, within rate limit — opened (gated, unmerged)"
            d["proposal"] = p
        out.append(d)
    return out


def _load_rejections(path):
    with open(path) as fh:
        return json.load(fh)


def dispositions(rejections=None):
    rej = rejections if rejections is not None else _load_rejections(DEFAULT_REJECTIONS)
    return bound(wargamer.wargame(), rej)


def bounded_proposals(rejections=None):
    return [d["proposal"] for d in dispositions(rejections) if d["proposal"]]


# --- commands -----------------------------------------------------------------
def cmd_bounded(args):
    print(json.dumps(bounded_proposals(_load_rejections(args.rejections)), indent=2))


def cmd_dispositions(args):
    rej = _load_rejections(args.rejections)
    for d in bound(wargamer.wargame(), rej):
        print(f"{d['disposition']:26} {d['key']:45} conf={d['confidence']:.3f} rej={d['rejected_before']}  {d['why']}")


def cmd_selfcheck(_args):
    rej = _load_rejections(DEFAULT_REJECTIONS)
    disp = bound(wargamer.wargame(), rej)
    by = {d["key"]: d for d in disp}

    # There IS drift to bound (else the test proves nothing).
    assert disp, "war-gamer produced no drift — nothing to bound"

    # 1. learn-from-rejections: the twice-rejected proposal is suppressed.
    assert by["tuppence/insider-abuse"]["disposition"] == "suppress-learned-rejection", by["tuppence/insider-abuse"]
    # ...and a once-rejected one still proposes, but carries its history.
    pq = by["tuppence/pq-harvest-now-decrypt-later"]
    assert pq["disposition"] == "propose", pq
    assert pq["proposal"]["prior_rejections"] == 1, pq

    # 2. confidence: driftwood's 2.7%-over-band verdict flip is HELD, not auto-opened.
    dw = by["driftwood/require-nonroot@2.0.0"]
    assert dw["disposition"] == "hold-low-confidence", dw
    assert dw["confidence"] < CONFIDENCE_MIN, dw

    # 3. rate-limit: a synthetic batch of many high-confidence, never-rejected flips
    #    opens exactly RATE_LIMIT and defers the rest.
    batch = [{"drift": True, "kind": "enforcement", "org": f"o{i}",
              "control": "require-nonroot@2.0.0", "policy_file": "p.yaml",
              "deployed": "Audit", "implied": "Deny", "evidence": {},
              "risk_bought_current": 90000.0, "tolerance": 40000.0}
             for i in range(RATE_LIMIT + 2)]
    bd = bound(batch, {"reject_suppress": 2, "rejections": {}})
    opened = [d for d in bd if d["disposition"] == "propose"]
    deferred = [d for d in bd if d["disposition"] == "defer-rate-limit"]
    assert len(opened) == RATE_LIMIT, bd
    assert len(deferred) == 2, bd

    # 4. HARD BACKSTOP: every emitted proposal is gated + unmerged, and this module
    #    has no way to merge/approve — the bounds never grant authority.
    for d in disp + bd:
        p = d["proposal"]
        if p:
            assert p["merged"] is False and p["auto_merge"] is False and p["required_gate"], p
    me = sys.modules[__name__]
    for banned in ("merge", "approve", "dispose", "auto_merge"):
        assert not callable(getattr(me, banned, None)), \
            f"proposer must expose no {banned}() — the gate disposes, not the agent"

    n_open = sum(1 for d in disp if d["disposition"] == "propose")
    print(
        "ok  bounded %d drift(s): %d suppressed(learned), %d held(low-conf), %d proposed(gated,unmerged) "
        "| rate-limit opens exactly %d/%d | no merge() by construction"
        % (len(disp),
           sum(1 for d in disp if d["disposition"] == "suppress-learned-rejection"),
           sum(1 for d in disp if d["disposition"] == "hold-low-confidence"),
           n_open, len(opened), RATE_LIMIT + 2)
    )


def main(argv=None):
    p = argparse.ArgumentParser(description="Bound the AI proposer; the gate stays the hard backstop.")
    sub = p.add_subparsers(dest="cmd", required=True)
    for name, fn, helptext in (
        ("bounded", cmd_bounded, "the proposals that survive the bounds (JSON)"),
        ("dispositions", cmd_dispositions, "one line per drift: disposition + why"),
    ):
        sp = sub.add_parser(name, help=helptext)
        sp.add_argument("--rejections", default=DEFAULT_REJECTIONS)
        sp.set_defaults(func=fn)
    sub.add_parser("selfcheck", help="run the proposer-bound assertions").set_defaults(func=cmd_selfcheck)
    args = p.parse_args(argv)
    args.func(args)


if __name__ == "__main__":
    main()
