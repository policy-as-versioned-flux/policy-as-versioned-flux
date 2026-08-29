#!/usr/bin/env python3
"""party.py — the roles: declaration (roles.json), machine-checked against the
filesystem (pure stdlib, offline).

CONTEXT.md's *Role* section names three roles, composable: **publisher** ships a
signed, versioned artefact others pin; **risk-bearer** carries a declared
appetite band; **adopter** pins and consumes another party's artefact. Ticket 03
warned that a `roles:` field nothing checks would be the estate's fourth
assertion that cannot fail — this module is the guard that makes it fail
correctly. It REFUSES a party whose declared role has no filesystem evidence:

    risk-bearer  ->  an `appetite` band on the party's OWN signed party.yaml
    publisher    ->  a *.sig file, a recorded *VERSION*.json, or a party.yaml that declares
                     publishes[] (ADR-0019: the tag signs, so an untagged feed.json is not
                     evidence; a declared feed is delegated to verify/feed-contract, which
                     SKIPs until the signed tag exists)
    platform, insurer -> declared only
    adopter      ->  a reference to another party's repo (policy-as-versioned-X)
                     or in-repo path (estate/X/) under its own dir

Institutions (driftwood/tuppence/ludlow) are derived, not hard-coded: risk-bearer
+ adopter, but NOT a `platform`-role party. The exclusion used to read "NOT
publisher", which worked only while `platform` was the one party that published.
Eco-system ticket 21 opened `publishes[]` to any party and ticket 25 had driftwood
publish its own forward-intel feed, so "publisher" stopped discriminating and would
have silently dropped driftwood off the count. The `platform` role is what actually
means "the apparatus, not one of the institutions it governs", so that is what the
derivation now reads.

Usage:
    party.py check       # refuse (non-zero, lists why) any role the filesystem contradicts
    party.py selfcheck   # + proves the guard bites (plants each violation) + the count
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
import tempfile

import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))  # verify/, for _estate
from _estate import ESTATE  # noqa: E402

ROLES = os.path.join(HERE, "roles.json")
# risk-bearer evidence moved onto each party's OWN signed artefact (eco-system
# ticket 25 / ADR-0021): platform/risk/appetite.json is retired, and a band no
# party signs is a missing instrument, not a fixture entry.
APPETITE = ESTATE

VALID_ROLES = {"publisher", "risk-bearer", "adopter", "platform", "insurer"}  # ADR-0019/ticket 21: platform, insurer


def load_parties(roles_path=ROLES):
    with open(roles_path) as fh:
        return json.load(fh)["parties"]


def _files(party_dir):
    for root, _dirs, files in os.walk(party_dir):
        for name in files:
            yield os.path.join(root, name)


def is_risk_bearer(party, appetite_path=APPETITE):
    """risk-bearer evidence: the party's OWN party.yaml declares an appetite band.

    `appetite_path` is the estate directory the party artefacts live under, kept
    as the parameter name so check_party()/check_all()'s callers and their
    planted-violation fixtures do not change.

    The artefact is PARSED, not pattern-matched: `appetite: {tolerance: {...}}`
    on one line is the same signed fact as the block form, both are valid under
    platform/party/schema.json, and a party that wrote the flow form would have
    been reported as a role the filesystem contradicts. This reads the same
    shape `platform/risk/enforce.py:appetite_money` reads.
    """
    path = os.path.join(appetite_path, party, "party.yaml")
    if not os.path.isfile(path):
        return False
    try:
        with open(path) as fh:
            doc = yaml.safe_load(fh) or {}
    except (OSError, yaml.YAMLError):
        return False
    return bool(isinstance(doc, dict) and (doc.get("appetite") or {}).get("tolerance"))


def ships_signed_versioned_artefact(party_dir):
    """publisher evidence: a signature or a recorded version+checksum manifest
    lives somewhere under the party's own directory, or the party's own
    party.yaml declares publishes[] (delegated to verify/feed-contract, which
    checks the signed tag; an untagged feed.json is not a signature)."""
    party_yaml = os.path.join(party_dir, "party.yaml")
    if os.path.isfile(party_yaml):
        with open(party_yaml, errors="ignore") as fh:  # flat scan, stdlib only
            if re.search(r"^publishes:\s*\n\s+- ", fh.read(), re.M):
                return True
    for path in _files(party_dir):
        name = os.path.basename(path)
        if name.endswith(".sig") or "VERSION" in name.upper():
            return True
    return False


def pins_another_party(party_dir, other_parties):
    """adopter evidence: a reference to another party's shipped artefact — its
    repo naming (policy-as-versioned-<other>) or its in-repo path
    (estate/<other>/) — appears in a file under this party's own directory."""
    if not other_parties:
        return False
    pattern = re.compile(
        "|".join(
            rf"policy-as-versioned-{re.escape(p)}\b|estate/{re.escape(p)}/"
            for p in other_parties
        )
    )
    for path in _files(party_dir):
        try:
            with open(path, errors="ignore") as fh:
                if pattern.search(fh.read()):
                    return True
        except OSError:
            continue
    return False


def signed_roles(party, estate_dir=ESTATE):
    """The roles the party itself SIGNS, off its own party.yaml. `None` when the
    party has no artefact to read (a fixture, or a unit not cloned)."""
    path = os.path.join(estate_dir, party, "party.yaml")
    if not os.path.exists(path):
        return None
    doc = yaml.safe_load(open(path).read()) or {}
    roles = doc.get("roles")
    return sorted(roles) if isinstance(roles, list) else None


def ships_platform_apparatus(party_dir):
    """platform evidence: the version fan-out and the served cage it publishes.

    ADR-0022 makes `platform` the entitlement to declare the top rung of the
    cage ladder (verify-infra-declaration.sh proof 2 reads roles[] for exactly
    this), so before 2026-08-29 the strongest entitlement in the estate was the
    one role with no evidence function at all."""
    return (os.path.isfile(os.path.join(party_dir, "distribution", "versions.yaml"))
            and os.path.isdir(os.path.join(party_dir, "graded", "policies")))


def publishes_quote_feed(party_dir):
    """insurer evidence: at least one quote/<adopter>/v*/feed.json it publishes."""
    quote = os.path.join(party_dir, "quote")
    if not os.path.isdir(quote):
        return False
    for root, _dirs, files in os.walk(quote):
        if "feed.json" in files and re.search(r"[/\\]v[0-9]", root):
            return True
    return False


def check_party(party, roles, all_parties, estate_dir=ESTATE, appetite_path=APPETITE):
    """Return the list of ways `party`'s declared roles contradict the
    filesystem. Empty means every declared role has real evidence."""
    problems = []
    unknown = sorted(set(roles) - VALID_ROLES)
    if unknown:
        problems.append(f"{party}: unknown role(s) {unknown}")
    party_dir = os.path.join(estate_dir, party)
    others = [p for p in all_parties if p != party]
    # role -> (zero-arg evidence check, what's missing when it fails). A lambda so a
    # role that isn't declared never pays for its check (e.g. never opens appetite.json).
    checks = {
        "risk-bearer": (lambda: is_risk_bearer(party, appetite_path), f"no entry in {appetite_path}"),
        "publisher": (lambda: ships_signed_versioned_artefact(party_dir),
                      f"ships no signed/versioned artefact under {party_dir}"),
        "adopter": (lambda: pins_another_party(party_dir, others), f"pins nothing under {party_dir}"),
        "platform": (lambda: ships_platform_apparatus(party_dir),
                     f"ships no distribution/versions.yaml and graded/policies/ under {party_dir}"),
        "insurer": (lambda: publishes_quote_feed(party_dir),
                    f"publishes no quote/<adopter>/v*/feed.json under {party_dir}"),
    }
    assert set(checks) == VALID_ROLES, sorted(VALID_ROLES - set(checks))
    for role, (has_evidence, missing) in checks.items():
        if role in roles and not has_evidence():
            problems.append(f"{party}: declared {role}, {missing}")
    # roles.json only DECLARES; the party SIGNS. Its own artefact is the source
    # of truth and this file is a mirror, so a mirror that has drifted is a
    # problem in itself -- on 2026-08-29 it said tuppence and ludlow were
    # [risk-bearer, adopter] while both signed [risk-bearer, adopter, publisher].
    signed = signed_roles(party, estate_dir)
    if signed is not None and signed != sorted(roles):
        problems.append(f"{party}: roles.json declares {sorted(roles)}, but {party}'s own signed "
                        f"party.yaml declares {signed}")
    return problems


def check_all(roles_path=ROLES, estate_dir=ESTATE, appetite_path=APPETITE):
    parties = load_parties(roles_path)
    problems = []
    for party, roles in parties.items():
        problems += check_party(party, roles, list(parties), estate_dir, appetite_path)
    return parties, problems


def institutions(parties):
    """risk-bearer + adopter, but NOT a `platform`-role party — see module docstring.
    An institution that publishes a feed of its own (driftwood's forward-intel, ADR-0021)
    is still an institution; only the apparatus stands outside the count."""
    return sorted(
        p for p, roles in parties.items()
        if "risk-bearer" in roles and "adopter" in roles and "platform" not in roles
    )


# --- commands -------------------------------------------------------------
def cmd_check(_args):
    parties, problems = check_all()
    if problems:
        sys.exit("REFUSED — declared role(s) contradict the filesystem:\n" +
                  "\n".join(f"  - {p}" for p in problems))
    insts = institutions(parties)
    print(
        "ok  %d parties, every declared role backed by the filesystem | institutions: %s (%d)"
        % (len(parties), ", ".join(insts), len(insts))
    )


def cmd_selfcheck(_args):
    # 1. The real estate: every declared role holds today, and the merge of
    #    platform's appetite band into the shared store did not sweep it in as
    #    a fourth institution (ticket 16 part 2's "verify the counts still
    #    read three").
    parties, problems = check_all()
    assert not problems, problems
    insts = institutions(parties)
    assert insts == ["driftwood", "ludlow", "tuppence"], insts
    assert "platform" not in insts, "platform must not count as an institution"

    # 2. The guard actually bites: plant each violation in isolation (never
    #    touching the real committed files) and watch check_party refuse it.
    with tempfile.TemporaryDirectory() as tmp:
        # a. risk-bearer whose own party.yaml declares no appetite band.
        os.makedirs(os.path.join(tmp, "driftwood"))
        with open(os.path.join(tmp, "driftwood", "party.yaml"), "w") as fh:
            fh.write("party: driftwood\nroles: [risk-bearer]\n")
        p = check_party("driftwood", ["risk-bearer"], list(parties),
                         estate_dir=tmp, appetite_path=tmp)
        assert p and "risk-bearer" in p[0], f"risk-bearer violation not caught: {p}"

        # b. publisher that ships nothing (no dir at all under the fake estate).
        p = check_party("nist", ["publisher"], list(parties), estate_dir=tmp)
        assert p and "publisher" in p[0], f"publisher violation not caught: {p}"

        # c. adopter that pins nothing (a real dir, but no reference to a peer).
        with open(os.path.join(tmp, "driftwood", "note.txt"), "w") as fh:
            fh.write("nothing here pins anyone")
        p = check_party("driftwood", ["adopter"], list(parties), estate_dir=tmp)
        assert p and "adopter" in p[0], f"adopter violation not caught: {p}"

        # d. and the same planted state passes once evidence is added back —
        #    the guard refuses the absence, not the party.
        with open(os.path.join(tmp, "driftwood", "party.yaml"), "w") as fh:
            fh.write("party: driftwood\nroles: [risk-bearer]\n"
                     "appetite:\n  tolerance: { amount: 1, currency: GBP }\n")
        p = check_party("driftwood", ["risk-bearer"], list(parties),
                         estate_dir=tmp, appetite_path=tmp)
        assert not p, f"risk-bearer with a signed band must pass: {p}"

    print("ok  guard bites: risk-bearer/publisher/adopter violations each refused when planted, "
          "cleared once evidence is restored")
    print(f"ok  real estate: {len(parties)} parties clean | institutions: {', '.join(insts)} (still three)")


def main(argv=None):
    p = argparse.ArgumentParser(description="roles: declared per party, checked against the filesystem.")
    sub = p.add_subparsers(dest="cmd", required=True)
    sub.add_parser("check", help="refuse any party whose declared role the filesystem contradicts").set_defaults(func=cmd_check)
    sub.add_parser("selfcheck", help="check + prove the guard bites + the institution count").set_defaults(func=cmd_selfcheck)
    args = p.parse_args(argv)
    args.func(args)


if __name__ == "__main__":
    main()
