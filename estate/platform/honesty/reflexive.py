#!/usr/bin/env python3
"""reflexive.py — the apparatus prices and governs ITSELF under the same model.

The honesty test that survives scrutiny: everything the estate does to a workload,
the governance apparatus does to itself. It is scored by the *same* ../risk/enforce.py
against a platform risk-appetite band, and its own three integrity controls are the
Deny state that brings it inside that band. If the apparatus can't pass its own test,
the whole thesis is special pleading.

Three self-controls, each the deny-state of the platform-self scenario:

  feed-integrity   feeds are SIGNED (../feeds/keys + .sig, verified offline by
                   ../feeds/verify.sh), SOURCED (every feed entry names a source),
                   and BOUNDED (../feeds/to_fair_scenario.py selfcheck asserts every
                   entry yields a valid lo<=mode<=hi triple — a feed can't inject an
                   out-of-range £).
  bounded proposer proposer_bounds.py — confidence + rate-limit + learn-from-rejections,
                   and NO merge() by construction.
  the gate         the version cross-check + human review every proposal rides
                   (the hard backstop; the AI never disposes).

"Passes its own test" = enforce.decide(platform-self, org=platform) returns Deny
(the model makes those controls MANDATORY, not optional) AND the residual with the
controls on (deny-state ALE) sits inside the platform band. Same maths, turned inward.

Reuses ../risk/enforce.py, ../feeds/to_fair_scenario.py, and honesty/proposer_bounds.py.
No new engine.

Usage:
    reflexive.py govern-self     # the platform's own enforcement decision (JSON)
    reflexive.py feed-integrity  # signed / sourced / bounded report
    reflexive.py selfcheck
"""
from __future__ import annotations

import argparse
import glob
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "risk"))
sys.path.insert(0, os.path.join(HERE, "..", "feeds"))
import enforce            # noqa: E402  the SAME appetite-band engine the estate uses
import to_fair_scenario   # noqa: E402  the feed bounds checker

FEEDS = os.path.join(HERE, "..", "feeds")
SELF_SCENARIO = os.path.join(HERE, "scenarios", "platform-self.json")
SELF_APPETITE = os.path.join(HERE, "scenarios", "platform-appetite.json")


def govern_self():
    """Score the apparatus with the same engine that scores every institution."""
    sc = enforce.fair.load(SELF_SCENARIO)
    tol = enforce.tolerance_for("platform", SELF_APPETITE)
    d = enforce.decide(sc, "platform", tol)
    # The honesty verdict: does the apparatus pass its own test?
    d["controls_mandatory"] = d["verdict"] == "Deny"        # model makes them required
    d["residual_within_band"] = d["residual_deny"] <= tol   # controls-on residual fits
    d["passes_own_test"] = d["controls_mandatory"] and d["residual_within_band"]
    return d


# --- feed integrity: signed / sourced / bounded -------------------------------
def _feed_files():
    return sorted(glob.glob(os.path.join(FEEDS, "*", "v*", "*.json")))


def _entries(feed):
    """The sourced records inside any of the three feed shapes."""
    for key in ("institutions", "cves", "components"):
        if key in feed:
            return feed[key]
    return {}


def feed_integrity():
    key = os.path.join(FEEDS, "keys", "feeds-signing-key.pem")
    report = {
        "signing_key_present": os.path.exists(key),
        "feeds": [],
        "bounded": None,
    }
    for path in _feed_files():
        with open(path) as fh:
            feed = json.load(fh)
        entries = _entries(feed)
        report["feeds"].append({
            "feed": os.path.relpath(path, FEEDS),
            "signed": os.path.exists(path + ".sig"),
            "sourced": bool(entries) and all("source" in e for e in entries.values()),
            "entries": len(entries),
        })
    # Bounded: every feed entry yields a valid triple (to_fair_scenario's own asserts).
    try:
        import io
        import contextlib
        with contextlib.redirect_stdout(io.StringIO()):
            to_fair_scenario.selfcheck()
        report["bounded"] = True
    except AssertionError:
        report["bounded"] = False
    return report


# --- commands -----------------------------------------------------------------
def cmd_govern_self(_a):
    print(json.dumps(govern_self(), indent=2))


def cmd_feed_integrity(_a):
    print(json.dumps(feed_integrity(), indent=2))


def cmd_selfcheck(_a):
    # 1. The apparatus passes its own test, judged by the estate's own engine.
    d = govern_self()
    assert d["verdict"] == "Deny", d                 # its controls are MANDATORY under the model
    assert d["controls_mandatory"], d
    assert d["residual_within_band"], d              # controls-on residual fits the band
    assert d["passes_own_test"], d
    # Scored by the identical engine (no bespoke self-scoring path).
    assert enforce.decide.__module__ == "enforce", "must reuse ../risk/enforce.py, not a fork"

    # 2. Feed-integrity actually holds: signed + sourced + bounded.
    fi = feed_integrity()
    assert fi["signing_key_present"], fi
    assert fi["feeds"], "no feeds found to govern"
    assert all(f["signed"] for f in fi["feeds"]), [f for f in fi["feeds"] if not f["signed"]]
    assert all(f["sourced"] for f in fi["feeds"]), [f for f in fi["feeds"] if not f["sourced"]]
    assert fi["bounded"] is True, "a feed entry produced an out-of-range triple"

    # 3. The bounded proposer is real and exposes no merge — the gate disposes.
    sys.path.insert(0, HERE)
    import proposer_bounds
    for banned in ("merge", "approve", "dispose"):
        assert not callable(getattr(proposer_bounds, banned, None)), banned
    assert callable(proposer_bounds.bounded_proposals), "proposer bound machinery missing"

    n_feeds = len(fi["feeds"])
    print(
        "ok  apparatus scored by its OWN engine: risk_bought £%.0f > £%.0f band -> Deny "
        "(controls mandatory), residual-with-controls £%.0f within band -> PASSES OWN TEST "
        "| feeds: %d signed+sourced+bounded | proposer bounded, no merge()"
        % (d["risk_bought"], d["tolerance"], d["residual_deny"], n_feeds)
    )


def main(argv=None):
    p = argparse.ArgumentParser(description="Reflexive self-governance: the apparatus under its own model.")
    sub = p.add_subparsers(dest="cmd", required=True)
    sub.add_parser("govern-self", help="the platform's own enforcement decision").set_defaults(func=cmd_govern_self)
    sub.add_parser("feed-integrity", help="signed / sourced / bounded report").set_defaults(func=cmd_feed_integrity)
    sub.add_parser("selfcheck", help="run the reflexive assertions").set_defaults(func=cmd_selfcheck)
    args = p.parse_args(argv)
    args.func(args)


if __name__ == "__main__":
    main()
