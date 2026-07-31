#!/usr/bin/env python3
"""access.py — the human+device access gate, as a pure-stdlib decision engine.

This is the load-bearing logic behind the talk's "human/device gate" beat
(spec beat 8): a WebAuthn login from the *attested* Mac reaches a gated op; a
login lacking the device SVID is refused; break-glass demands step-up.

It's the same one policy — "which version of the policy do you satisfy?" —
projected onto the *human/device* surface: the risk (£) of the operation sets
the assurance bar, and posture only ever *tightens*. Higher-risk op ⇒ higher
required assurance (proportional gating), exactly as the workload plane gates
service-to-service reach by posture in the SVID path.

Assurance is earned from three independent factors, mirroring the estate roots:
  - OIDC-authenticated human  (Dex issuer — same subject as the gitsign commit)
  - phishing-resistant WebAuthn  (Secure-Enclave-bound passkey — unclonable)
  - a valid device SVID  (SPIRE tpm_devid, on the acme.internal root)

Deps: none. Run `access.py selfcheck` for the runnable asserts.

Usage:
    access.py decide read       --oidc --webauthn --device
    access.py decide break-glass --oidc --webauthn          # DENY: unattested device
    access.py selfcheck
"""
from __future__ import annotations

import argparse
import sys

# Operation → required assurance level. The £ of the op sets the bar; expressed
# as tiers over dials (PSS-style presets), the tier picked by risk. Break-glass
# and cluster-admin sit at the top: they demand an attested device AND a passkey.
# ponytail: static tier table. Wire the tier to fair.py's £-crossover only if the
# demo needs the bar to move live with the risk number.
OP_TIER = {
    "read":        1,   # get/list/watch — low blast radius
    "list":        1,
    "write":       2,   # apply/edit/scale — mutates estate state
    "exec":        2,   # kubectl exec/port-forward — into a running workload
    "delete":      3,   # destructive
    "break-glass": 3,   # emergency privileged access
    "cluster-admin": 3,
}

# The factors, in strictly increasing strength. A tier-N op requires factors
# 1..N *cumulatively* (not N-of-any): OIDC is the floor (a known human), then
# phishing-resistant WebAuthn, then an attested device. So each higher-risk op
# demands a strictly stronger set, never a mere swap of one factor for another.
FACTORS = ("oidc", "webauthn", "device_svid")
DENY, STEP_UP, ALLOW = "DENY", "STEP_UP", "ALLOW"


def required_factors(op: str) -> set[str]:
    tier = OP_TIER.get(op)
    if tier is None:
        raise ValueError(f"unknown operation {op!r}; known: {sorted(OP_TIER)}")
    return set(FACTORS[:tier])


def decide(op: str, oidc: bool, webauthn: bool, device_svid: bool):
    """Return (decision, reason) for an operation given the caller's factors.

    - has every factor the op requires    -> ALLOW
    - only the passkey is missing          -> STEP_UP (prompt for WebAuthn — the
                                              human is real, the factor is addable)
    - unauthenticated, or missing the
      device SVID the op requires          -> DENY (an unmanaged laptop or a
                                              stolen credential can't be stepped up)
    """
    need = required_factors(op)
    have = {f for f, ok in zip(FACTORS, (oidc, webauthn, device_svid)) if ok}
    missing = need - have

    if not missing:
        return ALLOW, f"has all required factors {sorted(need)}"
    if "oidc" in missing:
        return DENY, "no authenticated human (OIDC login required)"
    if "device_svid" in missing:
        return DENY, "operation requires an attested device (valid device SVID); laptop is unattested"
    # Only WebAuthn is missing — the human is known, prompt for the passkey.
    return STEP_UP, "phishing-resistant WebAuthn required — prompt for the Secure-Enclave passkey"


def selfcheck():
    """Runnable asserts: the exact behaviours the talk beat demonstrates."""
    # Attested Mac (OIDC + Secure-Enclave passkey + device SVID) reaches break-glass.
    d, why = decide("break-glass", oidc=True, webauthn=True, device_svid=True)
    assert d == ALLOW, (d, why)

    # A login LACKING the device SVID is refused for break-glass — the headline
    # "a stolen credential or an unmanaged laptop can't invoke it".
    d, why = decide("break-glass", oidc=True, webauthn=True, device_svid=False)
    assert d == DENY, (d, why)
    assert "attested device" in why

    # Unauthenticated caller: denied outright, whatever the op.
    for op in OP_TIER:
        d, _ = decide(op, oidc=False, webauthn=False, device_svid=False)
        assert d == DENY, op

    # Proportionality: a low-risk read needs only an authenticated human.
    d, _ = decide("read", oidc=True, webauthn=False, device_svid=False)
    assert d == ALLOW, d

    # ...but the SAME human hitting a write with no passkey gets stepped up,
    # not denied — the factor is addable.
    d, why = decide("write", oidc=True, webauthn=False, device_svid=True)
    assert d == STEP_UP, (d, why)

    # A write from an attested device with a passkey: allowed.
    d, _ = decide("write", oidc=True, webauthn=True, device_svid=True)
    assert d == ALLOW, d

    # Monotonicity: adding a factor never downgrades the decision. For every op,
    # ALLOW once earned stays earned as factors are added.
    rank = {DENY: 0, STEP_UP: 1, ALLOW: 2}
    for op in OP_TIER:
        prev = -1
        for w, dv in [(False, False), (True, False), (True, True)]:
            d, _ = decide(op, oidc=True, webauthn=w, device_svid=dv)
            assert rank[d] >= prev, f"{op}: adding a factor downgraded {d}"
            prev = rank[d]

    # Higher-risk op never has a LOWER bar than a lower-risk one.
    assert OP_TIER["break-glass"] >= OP_TIER["write"] >= OP_TIER["read"]

    print("access selfcheck: all asserts passed")


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)
    d = sub.add_parser("decide", help="evaluate one operation")
    d.add_argument("op", choices=sorted(OP_TIER))
    d.add_argument("--oidc", action="store_true", help="human is OIDC-authenticated")
    d.add_argument("--webauthn", action="store_true", help="phishing-resistant WebAuthn presented")
    d.add_argument("--device", action="store_true", help="valid device SVID present")
    sub.add_parser("selfcheck", help="run the asserts")
    args = p.parse_args(argv)

    if args.cmd == "selfcheck":
        selfcheck()
        return 0
    decision, reason = decide(args.op, args.oidc, args.webauthn, args.device)
    print(f"{decision}: {reason}")
    return 0 if decision == ALLOW else (2 if decision == STEP_UP else 1)


if __name__ == "__main__":
    sys.exit(main())
