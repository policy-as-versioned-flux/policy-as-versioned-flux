#!/usr/bin/env python3
"""break-glass.py — posture-gated human access, priced by the op's £ (pure stdlib).

Ticket 19. The talk beat: a risky operation (break-glass / ludlow patient data)
demands *current device posture* + higher identity assurance, PROPORTIONAL to the
operation's £. A stale or unattested device is caged (read-only/scoped session) or
denied — the harder the £, the less a degraded device gets away with.

This is ticket 18's `access.py` gate (../access/access.py) with the two things that
ticket flagged as its upgrade path, now built:

  1. The bar is set by the op's **£**, not a static op→tier table. We run the op's
     FAIR scenario through ../fair/fair.py, read `carried` (TVaR + risk load), and
     the assurance band it lands in picks the required factors. Higher £ ⇒ a
     strictly stronger required set (proportional gating) — the same money the
     workload plane uses to pick Audit vs Deny (../risk/enforce.py).

  2. Device posture is not binary present/absent but has **currency**: a device
     SVID is `fresh` (attested and in currency), `stale` (was attested, now out of
     currency — the currency controller, ticket 16, has aged/dropped the entry), or
     `none` (unmanaged laptop, never on the estate root). A stale device at a
     tier-that-needs-it is *caged* to a read-only/scoped session rather than let in
     at full privilege — unless the £ is so high (patient-data class) that even a
     read-only peek is the breach, where it is denied. `none` is always denied at a
     device-requiring tier: you cannot cage trust that never existed.

Reuses ../fair/fair.py (the £ maths) and ../access/access.py (the factor set and
DENY/STEP_UP/ALLOW vocabulary). Adds only the £→band map, the CAGE rung, and
posture currency. No new risk engine, no second factor model.

Deps: none. Run `break-glass.py selfcheck` for the runnable asserts.

Usage:
  break-glass.py decide scenarios/ludlow-patient-data.json --oidc --webauthn --device fresh   # ALLOW
  break-glass.py decide scenarios/ludlow-patient-data.json --oidc --webauthn --device stale    # DENY (patient data)
  break-glass.py decide scenarios/driftwood-bulk-export.json --oidc --webauthn --device stale   # CAGE (read-only)
  break-glass.py decide scenarios/tuppence-write.json --oidc --device fresh                      # STEP_UP (prompt passkey)
  break-glass.py selfcheck
"""
from __future__ import annotations

import argparse
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
# Reuse the estate's two load-bearing engines one tree over.
sys.path.insert(0, os.path.join(HERE, "..", "fair"))
sys.path.insert(0, os.path.join(HERE, "..", "access"))
import fair    # noqa: E402  — the £ maths
import access  # noqa: E402  — FACTORS + DENY/STEP_UP/ALLOW vocabulary

DEFAULT_BANDS = os.path.join(HERE, "assurance-bands.json")

DENY, ALLOW, STEP_UP = access.DENY, access.ALLOW, access.STEP_UP
CAGE = "CAGE"  # a retained but read-only/scoped session — the graded rung access.py lacks

# Device posture currency (research 16): a device SVID's freshness, not its mere
# existence. The currency controller drops the entry when posture goes stale.
FRESH, STALE, NONE = "fresh", "stale", "none"
DEVICE_STATES = (FRESH, STALE, NONE)


def carried_gbp(scenario):
    """The op's carried £ (TVaR + risk load) from its single-state FAIR triple."""
    st = fair.state(scenario, "warn")  # single-state scenarios expose top-level lef/lm
    return fair.summarize(fair.simulate(st["lef"], st["lm"]))["carried"]


def required_tier(gbp, bands):
    """£ → assurance tier (1..3), the proportional bar. Cumulative like access.py:
    tier 1 = OIDC floor; 2 = + phishing-resistant WebAuthn; 3 = + attested device."""
    if gbp > bands["attest_at"]:
        return 3
    if gbp > bands["step_up_at"]:
        return 2
    return 1


def decide(scenario, oidc, webauthn, device, bands):
    """Graded decision for a risky op given the caller's human factors + device posture.

    Returns a dict: decision (DENY/CAGE/STEP_UP/ALLOW), the £ and tier that set the
    bar, and the human-readable reason the talk narrates.
    """
    if device not in DEVICE_STATES:
        raise ValueError(f"device must be one of {DEVICE_STATES}, got {device!r}")
    gbp = carried_gbp(scenario)
    tier = required_tier(gbp, bands)
    need = set(access.FACTORS[:tier])  # oidc / +webauthn / +device_svid, cumulative

    def out(decision, reason):
        return {
            "name": scenario.get("name"),
            "org": scenario.get("org"),
            "carried_gbp": gbp,
            "tier": tier,
            "required_factors": sorted(need),
            "device_posture": device,
            "decision": decision,
            "reason": reason,
        }

    # Floor: no authenticated human -> denied at any £.
    if not oidc:
        return out(DENY, "no authenticated human (OIDC login required)")

    # Tier 1 (low £): an authenticated human is the whole bar; posture irrelevant.
    if tier == 1:
        return out(ALLOW, f"£{gbp:,.0f} is below the step-up band — an authenticated human suffices")

    # Tier 2 (mid £): + phishing-resistant WebAuthn. A known human missing only the
    # passkey is *stepped up*, not denied — the factor is addable. Device not yet required.
    if tier == 2:
        if webauthn:
            return out(ALLOW, f"£{gbp:,.0f} needs a passkey; presented -> allowed")
        return out(STEP_UP, f"£{gbp:,.0f} is in the step-up band — prompt for the Secure-Enclave passkey")

    # Tier 3 (high £): + a CURRENT attested device. Posture currency decides the rung.
    if device == NONE:
        return out(DENY, "an unmanaged laptop (no device SVID on acme.internal) can't invoke a "
                         "device-gated op — it cannot be stepped up or caged into trust it never had")
    if device == STALE:
        # Was attested, now out of currency. Proportional: cage to read-only unless
        # the £ is so high that a read-only peek is itself the breach (patient data).
        if gbp > bands["no_cage_at"]:
            return out(DENY, f"£{gbp:,.0f} is above the cage ceiling — a stale device is denied "
                             "outright; a read-only session would still expose the data")
        return out(CAGE, f"£{gbp:,.0f}: device out of currency -> dropped to a read-only/scoped "
                         "session (caged), not full break-glass")
    # device == FRESH: a current attested device. Only the passkey can still gate.
    if webauthn:
        return out(ALLOW, f"£{gbp:,.0f}: fresh attested device + passkey -> full access")
    return out(STEP_UP, f"£{gbp:,.0f}: fresh attested device, prompt for the passkey to complete step-up")


def load_bands(path=DEFAULT_BANDS):
    with open(path) as fh:
        return json.load(fh)


def selfcheck():
    """Runnable asserts: the exact behaviours the talk beat demonstrates."""
    bands = load_bands()
    S = lambda n: fair.load(os.path.join(HERE, "scenarios", n))
    patient = S("ludlow-patient-data.json")
    export = S("driftwood-bulk-export.json")
    write = S("tuppence-write.json")
    read = S("driftwood-read.json")

    def d(sc, oidc=True, webauthn=False, device=NONE):
        return decide(sc, oidc, webauthn, device, bands)["decision"]

    # --- proportional bar: the £ orders the tiers, no static table ------------
    assert carried_gbp(read) < carried_gbp(write) < carried_gbp(export) < carried_gbp(patient)
    assert required_tier(carried_gbp(read), bands) == 1
    assert required_tier(carried_gbp(write), bands) == 2
    assert required_tier(carried_gbp(export), bands) == 3
    assert required_tier(carried_gbp(patient), bands) == 3

    # --- AC1: a risky op needs an attested device + step-up, proportionate to £ -
    # Patient-data break-glass: only a fresh attested device + passkey gets in.
    assert d(patient, webauthn=True, device=FRESH) == ALLOW
    # Same op, fresh device but no passkey -> stepped up (addable factor), not in.
    assert d(patient, webauthn=False, device=FRESH) == STEP_UP
    # A low-£ read never demands the device at all (proportionality downward).
    assert d(read, webauthn=False, device=NONE) == ALLOW

    # --- AC2: a stale/unattested device is denied or dropped to read-only/scoped -
    # Stale device on patient data (top band) -> DENIED (a read-only peek is the breach).
    assert d(patient, webauthn=True, device=STALE) == DENY
    # Stale device on a lesser tier-3 op -> CAGED to a read-only/scoped session.
    assert d(export, webauthn=True, device=STALE) == CAGE
    # Unmanaged laptop (never attested) at a device-requiring tier -> DENIED, both £.
    assert d(patient, webauthn=True, device=NONE) == DENY
    assert d(export, webauthn=True, device=NONE) == DENY
    # Proportional cage-vs-deny on the SAME posture, different £ — the money-shot.
    assert d(export, webauthn=True, device=STALE) == CAGE
    assert d(patient, webauthn=True, device=STALE) == DENY

    # --- step-up band (tier 2): stolen-credential story ------------------------
    # A known human without a passkey is stepped up, not denied; with it, allowed.
    assert d(write, webauthn=False, device=NONE) == STEP_UP
    assert d(write, webauthn=True, device=NONE) == ALLOW

    # --- floor: no human -> denied at any £ ------------------------------------
    for sc in (read, write, export, patient):
        assert d(sc, oidc=False, webauthn=True, device=FRESH) == DENY

    # --- monotonicity: improving posture never downgrades the decision ---------
    rank = {DENY: 0, CAGE: 1, STEP_UP: 2, ALLOW: 3}
    for sc in (read, write, export, patient):
        prev = -1
        for dev in (NONE, STALE, FRESH):
            r = rank[d(sc, webauthn=True, device=dev)]
            assert r >= prev, f"{sc['name']}: better posture {dev} downgraded the decision"
            prev = r

    print("break-glass selfcheck: all asserts passed "
          f"(read £{carried_gbp(read):,.0f} T1 | write £{carried_gbp(write):,.0f} T2 | "
          f"export £{carried_gbp(export):,.0f} T3-cage | patient £{carried_gbp(patient):,.0f} T3-deny)")


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)
    de = sub.add_parser("decide", help="evaluate one risky op")
    de.add_argument("scenario")
    de.add_argument("--oidc", action="store_true", help="human is OIDC-authenticated")
    de.add_argument("--webauthn", action="store_true", help="phishing-resistant WebAuthn presented")
    de.add_argument("--device", choices=DEVICE_STATES, default=NONE, help="device posture currency")
    de.add_argument("--bands", default=DEFAULT_BANDS)
    sub.add_parser("selfcheck", help="run the asserts")
    args = p.parse_args(argv)

    if args.cmd == "selfcheck":
        selfcheck()
        return 0
    r = decide(fair.load(args.scenario), args.oidc, args.webauthn, args.device, load_bands(args.bands))
    print(json.dumps(r, indent=2))
    return {ALLOW: 0, STEP_UP: 2, CAGE: 3, DENY: 1}[r["decision"]]


if __name__ == "__main__":
    sys.exit(main())
