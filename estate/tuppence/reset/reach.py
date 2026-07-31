#!/usr/bin/env python3
"""reach.py — the posture gate as pure, offline-testable logic (ticket 17).

Both surfaces of this ticket gate on the SAME thing: does a caller's SVID *path*
carry the current-posture prefix?
  * Istio AuthorizationPolicy matches `source.principals` (authorizationpolicy.yaml)
  * OpenBao jwt role globs `bound_claims["sub"]` (openbao-role.yaml)

Both are `spiffe://…/posture/<vN>/*` globs. The demonstrable claim — "a current
caller reaches + gets the secret; an out-of-currency caller is refused BOTH" —
reduces to a glob match, which is checkable without a cluster. We parse the glob
straight out of the two real manifests (not a copy) so the test guards the
shipped artifacts, and assert:
  1. a current SVID matches BOTH globs (reach AND secret),
  2. a stale SVID and a de-postured base SVID match NEITHER (lose both),
  3. the two globs pin the SAME version (reach and secret can't drift apart).

    reach.py selfcheck     # runnable asserts, no cluster
    reach.py globs         # print the two parsed globs
"""
from __future__ import annotations

import fnmatch
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
TRUST_DOMAIN = "acme.internal"


def istio_principal(path: str = None) -> str:
    """The single principal glob from the AuthorizationPolicy (via yaml if present,
    else a tolerant regex so the check runs with no pyyaml)."""
    path = path or os.path.join(HERE, "authorizationpolicy.yaml")
    text = open(path).read()
    try:
        import yaml
        doc = yaml.safe_load(text)
        principals = doc["spec"]["rules"][0]["from"][0]["source"]["principals"]
        assert len(principals) == 1, f"expected one principal glob, got {principals}"
        return principals[0]
    except ImportError:
        m = re.search(r'principals:\s*\[\s*"([^"]+)"\s*\]', text)
        assert m, "could not find principals glob in authorizationpolicy.yaml"
        return m.group(1)


def openbao_sub_glob(path: str = None) -> str:
    """The bound_claims sub glob from the OpenBao role Job's shell args."""
    path = path or os.path.join(HERE, "openbao-role.yaml")
    text = open(path).read()
    m = re.search(r'bound_claims=\'{"sub":"([^"]+)"}\'', text)
    assert m, "could not find bound_claims sub glob in openbao-role.yaml"
    return m.group(1)


def svid(version: str | None, ns: str, sa: str) -> str:
    """Construct a SPIFFE ID as the posture ClusterSPIFFEID template would.
    version=None -> the base (un-postured) SVID a de-postured pod falls back to."""
    if version is None:
        return f"spiffe://{TRUST_DOMAIN}/ns/{ns}/sa/{sa}"
    return f"spiffe://{TRUST_DOMAIN}/posture/{version}/ns/{ns}/sa/{sa}"


def admits(glob: str, spiffe_id: str) -> bool:
    return fnmatch.fnmatchcase(spiffe_id, glob)


def selfcheck() -> None:
    reach = istio_principal()
    secret = openbao_sub_glob()
    print(f"  reach glob   {reach}")
    print(f"  secret glob  {secret}")

    fails = []

    def check(cond, msg):
        (print if cond else (lambda m: (fails.append(m), print("  FAIL " + m))[0]))(
            "  ok   " + msg if cond else msg)

    # 3. the two surfaces pin the same version — reach and secret cannot drift.
    check(reach == secret,
          "Istio principal and OpenBao bound_claims glob are identical (one policy, two projections)")

    # extract the gated version from the glob for readable messages
    ver = reach.split("/posture/")[1].split("/")[0]

    current = svid(ver, "tuppence-reset", "teller-current")
    stale = svid("1.0.0" if ver != "1.0.0" else "0.9.0", "tuppence-reset", "teller-stale")
    base = svid(None, "tuppence-reset", "teller-current")

    # 1. current caller wins BOTH surfaces.
    check(admits(reach, current), f"current SVID ({ver}) REACHES the service")
    check(admits(secret, current), f"current SVID ({ver}) GETS the secret")

    # 2. stale + de-postured lose BOTH.
    check(not admits(reach, stale), "stale SVID is refused reach")
    check(not admits(secret, stale), "stale SVID is refused the secret")
    check(not admits(reach, base), "de-postured (base) SVID is refused reach")
    check(not admits(secret, base), "de-postured (base) SVID is refused the secret")

    # a forged version-lookalike must not sneak past the prefix boundary:
    # posture segment is a distinct path element, so /posture/2.0.0-evil/… must not match /posture/2.0.0/*
    evil = f"spiffe://{TRUST_DOMAIN}/posture/{ver}-evil/ns/x/sa/y"
    check(not admits(reach, evil), "a version-lookalike (vN-evil) does not satisfy the prefix")

    if fails:
        sys.exit(f"\n{len(fails)} gate invariant(s) broken")
    print("  -- posture gate holds: current wins both, out-of-currency loses both --")


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "selfcheck"
    if cmd == "globs":
        print("reach  :", istio_principal())
        print("secret :", openbao_sub_glob())
    elif cmd == "selfcheck":
        selfcheck()
    else:
        sys.exit(__doc__)
