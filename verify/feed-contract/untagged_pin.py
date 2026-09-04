#!/usr/bin/env python3
"""untagged_pin.py — eco-system ticket 69 made checkable: an untagged pin is a priced hole.

For every adopter `inherits[]` feed pin, the pin's signature state is read from the publisher's
REAL remote -- `git ls-remote --tags` for existence (feed_contract.py's own lookup), then the
platform's identity-pinned verifier (`identity/gitsign-verifier/verify_gitsign.py`, the one
`verify-source-verification.sh` grades) over the tag object fetched read-only, under the
publisher's own `release.yml` identity regexp and issuer -- and graded against the adopter's
`composed/evidence.json`:

  signed     a tag of the pinned form exists and verifies under the publisher's pins: PASS,
             no hole (an open hole the evidence still carries from before the tag is noted:
             re-composition closes it, nothing here fails on it);
  untagged   no tag of the pinned form, or one whose signature does not verify: PASS only if
             the adopter's evidence prices the pin as a hole on the premium entry -- status new
             or recorded, under the adopter's own perspective and currency, a positive amount
             and a `priced_by` (composition.py, ticket 69); FAIL otherwise;
  could not look (remote unreachable, no verifier, no identity pins, trust material absent):
             SKIP, never PASS.

Grading, per the gate contract: any FAIL -> 1; else any SKIP -> 3; else 0.

Usage:
    untagged_pin.py check        # every adopter pin in the estate (network: ls-remote + one
                                 # read-only tag fetch per pin)
    untagged_pin.py selfcheck    # planted fixtures, remote stubbed: proves each grade bites

PAVC_ESTATE_CLONE=<dir> names another estate to grade (the same override composition.py and
verify-priced-holes.sh take), so a scratch estate of freshly composed adopter copies can be
graded before the owner pushes the real ones. The gate never sets it.
"""
from __future__ import annotations

import json
import os
import re
import subprocess
import sys
import tempfile
from typing import Any, Callable

import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.dirname(HERE))
import feed_contract  # type: ignore[import-not-found]  # noqa: E402
from _estate import ESTATE  # type: ignore[import-not-found]  # noqa: E402

LINES: list[str] = []
OPEN = ("new", "recorded")
HOLE_FIELDS = {"kind", "source", "name", "version", "status", "perspective", "currency",
               "amount", "priced_by"}
VERIFIER_REL = os.path.join("platform", "identity", "gitsign-verifier", "verify_gitsign.py")
DEPLOYMENT_REL = os.path.join("platform", "identity", "gitsign-verifier", "deployment.yaml")
SKEW_ENV = "GITSIGN_TAGGER_SKEW_SECONDS"


def out(status: str, msg: str) -> None:
    LINES.append(status)
    print(f"{status}: {msg}")


# --------------------------------------------------------------------------
# reading signature state from the publisher's real remote
# --------------------------------------------------------------------------
def _identity_pins(estate: str, party: str) -> tuple[str, str] | None:
    """The publisher's own EXPECTED_IDENTITY_REGEXP and EXPECTED_ISSUER, read off its
    release.yml in the clone -- the same two values verify-e2e-step6-provenance.sh reads."""
    wf = os.path.join(estate, party, ".github", "workflows", "release.yml")
    if not os.path.isfile(wf):
        return None
    with open(wf) as fh:
        text = fh.read()
    regexp = re.search(r"^\s*EXPECTED_IDENTITY_REGEXP:\s*(\S.*?)\s*$", text, re.M)
    issuer = re.search(r"^\s*EXPECTED_ISSUER:\s*(\S+)\s*$", text, re.M)
    if not regexp or not issuer:
        return None
    return regexp.group(1), issuer.group(1)


def _declared_skew(estate: str) -> str | None:
    """The tagger-skew bound the verifier's deployment declares (ticket 73, ADR-0027), read
    off deployment.yaml so this check never carries a literal of its own."""
    path = os.path.join(estate, DEPLOYMENT_REL)
    if not os.path.isfile(path):
        return None
    with open(path) as fh:
        m = re.search(rf"name:\s*{SKEW_ENV}\s*\n\s*value:\s*\"?(\d+)\"?", fh.read())
    return m.group(1) if m else None


def verify_signature(estate: str, party: str, tag: str) -> tuple[str, str]:
    """('verified' | 'rejected' | 'could-not-look', detail) for one tag on the publisher's
    real remote. The tag ref alone is fetched read-only into a bare cache; the platform's own
    verifier reads it there. Nothing is written to any remote and nothing is signed."""
    verifier = os.path.join(estate, VERIFIER_REL)
    if not os.path.isfile(verifier):
        return "could-not-look", f"no {VERIFIER_REL} in the estate to verify {tag} with"
    pins = _identity_pins(estate, party)
    if pins is None:
        return "could-not-look", f"{party}/.github/workflows/release.yml pins no identity regexp and issuer"
    url = feed_contract.REMOTE.format(p=party)
    with tempfile.TemporaryDirectory() as tmp:
        cache = os.path.join(tmp, "repo.git")
        subprocess.run(["git", "init", "--bare", "-q", cache], check=True)
        fetched = subprocess.run(["git", "-C", cache, "fetch", "--depth=1", "-q", url,
                                  f"+refs/tags/{tag}:refs/tags/{tag}"],
                                 capture_output=True, text=True, timeout=120)
        if fetched.returncode:
            return "could-not-look", f"could not fetch {tag} from {url}: {fetched.stderr.strip()[-160:]}"
        env = dict(os.environ)
        skew = _declared_skew(estate)
        if skew is not None:
            env[SKEW_ENV] = skew
        r = subprocess.run([sys.executable, verifier, "verify-tag", "--repo", cache, "--tag", tag,
                            "--identity-regexp", pins[0], "--issuer", pins[1]],
                           capture_output=True, text=True, timeout=120, env=env)
    last = (r.stdout.strip().splitlines() or [r.stderr.strip()[-160:]])[-1]
    if r.returncode == 0:
        return "verified", last
    if r.returncode == 1 and last.startswith("REJECTED"):
        return "rejected", last
    return "could-not-look", last


# Injection points for selfcheck; `check` uses the real lookups.
_remote_tags: Callable[[str], set | None] = feed_contract.remote_tags
_verify: Callable[[str, str, str], tuple[str, str]] = verify_signature


def signature_state(estate: str, party: str, entry: dict, version: str) -> dict:
    """{state, tag, detail}: signed | untagged | unreachable | unverifiable."""
    tags = _remote_tags(party)
    if tags is None:
        return {"state": "unreachable", "tag": None,
                "detail": f"could not reach {feed_contract.REMOTE.format(p=party)}"}
    tag = feed_contract.match_tag(entry, version, tags)
    if tag is None:
        return {"state": "untagged", "tag": None,
                "detail": f"no tag of the form {entry['name']}/v* or v* signs @{version} on {party}'s real remote"}
    verdict, detail = _verify(estate, party, tag)
    if verdict == "verified":
        return {"state": "signed", "tag": tag, "detail": f"tag {tag} on {party}: {detail}"}
    if verdict == "rejected":
        return {"state": "untagged", "tag": tag,
                "detail": f"tag {tag} exists on {party}'s real remote but does not verify under "
                          f"{party}'s own identity pins ({detail}); an unverifiable signature signs nothing"}
    return {"state": "unverifiable", "tag": tag, "detail": f"tag {tag} on {party}: {detail}"}


# --------------------------------------------------------------------------
# the grade -- pure, so selfcheck and tests can plant every case
# --------------------------------------------------------------------------
def evidence_hole(evidence: dict | None, party: str, name: str) -> tuple[bool, dict | None]:
    """(entry_present, hole) for the adopter's premium entry on this pin."""
    for e in (evidence or {}).get("prices") or []:
        if e.get("kind") == "premium" and e.get("source") == party and e.get("name") == name:
            hole = e.get("hole")
            return True, hole if isinstance(hole, dict) else None
    return False, None


def grade(state: dict, evidence: dict | None, *, adopter: str, currency: str, party: str,
          name: str, version: str) -> tuple[str, str]:
    """One (status, message) for one pin, from its signature state and the adopter's evidence."""
    label = f"{adopter} pins {party}/feed/{name}@{version}"
    present, hole = evidence_hole(evidence, party, name)
    if state["state"] == "unreachable":
        return "SKIP", f"{label}: {state['detail']}"
    if state["state"] == "unverifiable":
        return "SKIP", f"{label}: {state['detail']} -- could not look at the signature"
    if state["state"] == "signed":
        note = (" (composed/evidence.json still prices a hole from before the tag; re-composition closes it)"
                if hole and hole.get("status") in OPEN else "")
        return "PASS", f"{label}: signed -- {state['detail']}; no hole{note}"
    # untagged: never refused, never free
    if evidence is None:
        return "FAIL", f"{label}: untagged ({state['detail']}) and {adopter} has no composed/evidence.json to price it"
    if not present:
        return "FAIL", f"{label}: untagged ({state['detail']}) and no premium entry in prices[] carries the pin"
    if hole is None or hole.get("status") not in OPEN:
        return "FAIL", (f"{label}: untagged ({state['detail']}) and the premium entry carries no open hole "
                        f"-- an untagged pin is a priced hole, never free (ticket 69, ADR-0020)")
    missing = sorted(HOLE_FIELDS - set(hole))
    if missing:
        return "FAIL", f"{label}: untagged and the hole lacks {missing}"
    if hole["kind"] != "untagged-pin" or (hole["source"], hole["name"]) != (party, name):
        return "FAIL", f"{label}: untagged and the hole names {hole['source']}/{hole['name']} ({hole['kind']})"
    if hole["perspective"] != adopter or hole["currency"] != currency:
        return "FAIL", (f"{label}: untagged and the hole is under {hole['perspective']}/{hole['currency']}, "
                        f"not {adopter}/{currency}")
    amount = hole["amount"]
    if isinstance(amount, bool) or not isinstance(amount, (int, float)) or amount <= 0 or not hole["priced_by"]:
        return "FAIL", f"{label}: untagged and the hole carries amount {amount!r} priced_by {hole['priced_by']!r}"
    return "PASS", (f"{label}: untagged ({state['detail']}) and priced as a {hole['status']} hole of "
                    f"{amount:,.2f} {currency} under {adopter}'s own perspective ({hole['priced_by']})")


# --------------------------------------------------------------------------
# the estate
# --------------------------------------------------------------------------
def _evidence(estate: str, adopter: str) -> dict | None:
    path = os.path.join(estate, adopter, "composed", "evidence.json")
    if not os.path.isfile(path):
        return None
    try:
        with open(path) as fh:
            doc = json.load(fh)
    except (OSError, ValueError) as exc:
        out("FAIL", f"{adopter}: composed/evidence.json does not parse: {exc}")
        return None
    return doc if isinstance(doc, dict) else None


def run(estate: str) -> None:
    all_parties = feed_contract.parties(estate)
    pins = 0
    for adopter, doc in sorted(all_parties.items()):
        if "adopter" not in (doc.get("roles") or []):
            continue
        currency = doc.get("reporting_currency") or "USD"
        evidence = _evidence(estate, adopter)
        for inh in doc.get("inherits") or []:
            if inh.get("kind") != "feed":
                continue
            party, name, version = str(inh.get("party")), str(inh.get("name")), str(inh.get("version"))
            pub, entry = feed_contract.resolve(all_parties, inh)
            if entry is None:
                out("SKIP", f"{adopter} pins {party}/feed/{name}@{version}: no publishes[] record to name "
                            f"a tag form by (verify-feed-contract grades that)")
                continue
            pins += 1
            state = signature_state(estate, party, entry, version)
            out(*grade(state, evidence, adopter=adopter, currency=currency, party=party,
                       name=name, version=version))
    if not pins:
        out("FAIL", f"no adopter feed pin observed under {estate}: absence is not a pass")


def exit_code() -> int:
    if "FAIL" in LINES:
        return 1
    return 3 if "SKIP" in LINES else 0


# --------------------------------------------------------------------------
# selfcheck -- planted fixtures, the remote and the verifier stubbed
# --------------------------------------------------------------------------
def _hole(adopter: str, status: str = "new", **over: Any) -> dict:
    hole = {"kind": "untagged-pin", "source": "insurer", "name": f"quote-{adopter}", "version": "v1",
            "status": status, "perspective": adopter, "currency": "GBP", "amount": 113403.3,
            "priced_by": f"insurer quote-{adopter}@v1: the premium the pin books, paid against a "
                         f"quote no signed tag carries", "detail": "x"}
    hole.update(over)
    return hole


def _evidence_with(adopter: str, hole: dict | None, *, entry: bool = True) -> dict:
    if not entry:
        return {"prices": []}
    return {"prices": [{"source": "insurer", "kind": "premium", "name": f"quote-{adopter}",
                        "perspective": adopter, "currency": "GBP", "amount": 113403.3, "hole": hole}]}


def selfcheck() -> None:
    global _remote_tags, _verify
    signed = {"state": "signed", "tag": "v1.0.0", "detail": "tag v1.0.0 on insurer: VERIFIED"}
    untagged = {"state": "untagged", "tag": None, "detail": "no tag"}
    kw = dict(party="insurer", name="quote-a", version="v1", adopter="a", currency="GBP")
    cases: list[tuple[str, dict, dict | None, str]] = [
        ("signed, no hole", signed, _evidence_with("a", None), "PASS"),
        ("signed, stale open hole is a PASS with a note", signed, _evidence_with("a", _hole("a")), "PASS"),
        ("untagged, priced new hole", untagged, _evidence_with("a", _hole("a")), "PASS"),
        ("untagged, priced recorded hole", untagged, _evidence_with("a", _hole("a", "recorded")), "PASS"),
        ("untagged, no evidence", untagged, None, "FAIL"),
        ("untagged, no premium entry", untagged, _evidence_with("a", None, entry=False), "FAIL"),
        ("untagged, entry with no hole", untagged, _evidence_with("a", None), "FAIL"),
        ("untagged, hole already closed", untagged, _evidence_with("a", _hole("a", "closed")), "FAIL"),
        ("untagged, hole under another perspective", untagged, _evidence_with("a", _hole("a", perspective="b")), "FAIL"),
        ("untagged, hole in another currency", untagged, _evidence_with("a", _hole("a", currency="USD")), "FAIL"),
        ("untagged, zero amount", untagged, _evidence_with("a", _hole("a", amount=0.0)), "FAIL"),
        ("untagged, no priced_by", untagged, _evidence_with("a", _hole("a", priced_by=None)), "FAIL"),
        ("untagged, hole missing a field", untagged, _evidence_with("a", {k: v for k, v in _hole("a").items() if k != "version"}), "FAIL"),
        ("unreachable remote", {"state": "unreachable", "tag": None, "detail": "could not reach"}, _evidence_with("a", None), "SKIP"),
        ("verifier could not look", {"state": "unverifiable", "tag": "v1.0.0", "detail": "COULD-NOT-LOOK"}, _evidence_with("a", None), "SKIP"),
    ]
    for label, state, evidence, want in cases:
        status, msg = grade(state, evidence, **kw)  # type: ignore[arg-type]
        assert status == want, (label, status, msg)
    note = grade(signed, _evidence_with("a", _hole("a")), **kw)[1]  # type: ignore[arg-type]
    assert "re-composition closes it" in note, note
    print(f"ok  grade: {len(cases)} planted cases graded as expected (signed passes with no hole, "
          f"untagged passes only with an open priced hole under the adopter's own perspective and "
          f"currency, could-not-look skips)")

    # signature_state through stubbed lookups: existence off ls-remote, then the verifier
    entry = {"kind": "feed", "name": "quote-a", "path": "quote/a"}
    _remote_tags = lambda party: {"insurer": {"v1.0.0", "v1.2.0"}, "down": None, "bad": {"v1.0.0"},
                                  "blind": {"v1.0.0"}}.get(party)  # noqa: E731
    _verify = lambda estate, party, tag: {  # noqa: E731
        "insurer": ("verified", "VERIFIED"), "bad": ("rejected", "REJECTED: identity"),
        "blind": ("could-not-look", "COULD-NOT-LOOK: no roots")}[party]
    s = signature_state("/nowhere", "insurer", entry, "v1")
    assert s["state"] == "signed" and s["tag"] == "v1.2.0", s
    assert signature_state("/nowhere", "insurer", entry, "v3")["state"] == "untagged"
    assert signature_state("/nowhere", "down", entry, "v1")["state"] == "unreachable"
    bad = signature_state("/nowhere", "bad", entry, "v1")
    assert bad["state"] == "untagged" and "does not verify" in bad["detail"], bad
    assert signature_state("/nowhere", "blind", entry, "v1")["state"] == "unverifiable"
    print("ok  signature_state: the highest tag of the pinned form, verified, is signed; none is "
          "untagged; a rejected signature is untagged; an unreachable remote or a verifier that "
          "could not look is never a signature")

    # the estate walk: a two-adopter estate, one priced, one not
    with tempfile.TemporaryDirectory() as tmp:
        def w(rel: str, obj: Any, as_yaml: bool = False) -> None:
            p = os.path.join(tmp, rel)
            os.makedirs(os.path.dirname(p), exist_ok=True)
            with open(p, "w") as fh:
                (yaml.safe_dump if as_yaml else json.dump)(obj, fh)
        w("insurer/party.yaml", {"party": "insurer", "roles": ["publisher"], "publishes": [
            {"kind": "feed", "name": "quote-a", "path": "quote/a"},
            {"kind": "feed", "name": "quote-b", "path": "quote/b"}]}, True)
        for a in ("a", "b"):
            w(f"{a}/party.yaml", {"party": a, "roles": ["adopter"], "reporting_currency": "GBP",
                                  "inherits": [{"party": "insurer", "kind": "feed", "name": f"quote-{a}", "version": "v9"},
                                               {"party": "insurer", "kind": "feed", "name": "nope", "version": "v1"}]}, True)
        w("a/composed/evidence.json", _evidence_with("a", _hole("a", name="quote-a", version="v9")))
        w("b/composed/evidence.json", _evidence_with("b", None))
        LINES.clear()
        run(tmp)
        assert LINES.count("PASS") == 1 and LINES.count("FAIL") == 1 and LINES.count("SKIP") == 2, LINES
        assert exit_code() == 1
        LINES.clear()
        run(os.path.join(tmp, "insurer"))
        assert LINES == ["FAIL"], LINES  # no adopter pin: absence is not a pass
    LINES.clear()
    _remote_tags, _verify = feed_contract.remote_tags, verify_signature
    print("ok  selfcheck: untagged priced, untagged unpriced, signed, rejected, unreachable, "
          "could-not-look and an empty estate all graded")


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "check"
    if cmd == "selfcheck":
        selfcheck()
        sys.exit(0)
    if cmd != "check":
        print(__doc__)
        sys.exit(2)
    estate = os.environ.get("PAVC_ESTATE_CLONE") or ESTATE
    if not os.path.isdir(os.path.join(estate, "platform")):
        print(f"SKIP: {estate}/platform absent -- run ./clone-estate.sh first")
        sys.exit(3)
    run(estate)
    sys.exit(exit_code())
