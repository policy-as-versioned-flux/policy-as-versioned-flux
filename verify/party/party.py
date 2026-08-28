#!/usr/bin/env python3
"""party.py — the roles: declaration (roles.json), machine-checked against the
filesystem (pure stdlib, offline).

CONTEXT.md's *Role* section names three roles, composable: **publisher** ships a
signed, versioned artefact others pin; **risk-bearer** carries a declared
appetite band; **adopter** pins and consumes another party's artefact. Ticket 03
warned that a `roles:` field nothing checks would be the estate's fourth
assertion that cannot fail — this module is the guard that makes it fail
correctly. It REFUSES a party whose declared role has no filesystem evidence:

    risk-bearer  ->  an entry in platform/risk/appetite.json
    publisher    ->  a *.sig file, a recorded *VERSION*.json, or a party.yaml that declares
                     publishes[] (ADR-0019: the tag signs, so an untagged feed.json is not
                     evidence; a declared feed is delegated to verify/feed-contract, which
                     SKIPs until the signed tag exists)
    platform, insurer -> declared only
    adopter      ->  a reference to another party's repo (policy-as-versioned-X)
                     or in-repo path (estate/X/) under its own dir

Institutions (driftwood/tuppence/ludlow) are derived, not hard-coded: risk-bearer
+ adopter, but NOT publisher. That third role is exactly what keeps `platform` —
which is also risk-bearer+adopter, see reflexive.py — off the institution count
when its appetite band moves into the shared store (ticket 16 part 2).

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

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))  # verify/, for _estate
from _estate import ESTATE  # noqa: E402

ROLES = os.path.join(HERE, "roles.json")
APPETITE = os.path.join(ESTATE, "platform", "risk", "appetite.json")

VALID_ROLES = {"publisher", "risk-bearer", "adopter", "platform", "insurer"}  # ADR-0019/ticket 21: platform, insurer


def load_parties(roles_path=ROLES):
    with open(roles_path) as fh:
        return json.load(fh)["parties"]


def _files(party_dir):
    for root, _dirs, files in os.walk(party_dir):
        for name in files:
            yield os.path.join(root, name)


def is_risk_bearer(party, appetite_path=APPETITE):
    with open(appetite_path) as fh:
        orgs = json.load(fh).get("orgs", {})
    return party in orgs


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
    }
    for role, (has_evidence, missing) in checks.items():
        if role in roles and not has_evidence():
            problems.append(f"{party}: declared {role}, {missing}")
    return problems


def check_all(roles_path=ROLES, estate_dir=ESTATE, appetite_path=APPETITE):
    parties = load_parties(roles_path)
    problems = []
    for party, roles in parties.items():
        problems += check_party(party, roles, list(parties), estate_dir, appetite_path)
    return parties, problems


def institutions(parties):
    """risk-bearer + adopter, but NOT publisher — see module docstring."""
    return sorted(
        p for p, roles in parties.items()
        if "risk-bearer" in roles and "adopter" in roles and "publisher" not in roles
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
        # a. risk-bearer with no appetite entry.
        empty_appetite = os.path.join(tmp, "appetite.json")
        with open(empty_appetite, "w") as fh:
            json.dump({"orgs": {}}, fh)
        p = check_party("driftwood", ["risk-bearer"], list(parties),
                         estate_dir=tmp, appetite_path=empty_appetite)
        assert p and "risk-bearer" in p[0], f"risk-bearer violation not caught: {p}"

        # b. publisher that ships nothing (no dir at all under the fake estate).
        p = check_party("nist", ["publisher"], list(parties), estate_dir=tmp)
        assert p and "publisher" in p[0], f"publisher violation not caught: {p}"

        # c. adopter that pins nothing (a real dir, but no reference to a peer).
        os.makedirs(os.path.join(tmp, "driftwood"))
        with open(os.path.join(tmp, "driftwood", "note.txt"), "w") as fh:
            fh.write("nothing here pins anyone")
        p = check_party("driftwood", ["adopter"], list(parties), estate_dir=tmp)
        assert p and "adopter" in p[0], f"adopter violation not caught: {p}"

        # d. and the same planted state passes once evidence is added back —
        #    the guard refuses the absence, not the party.
        with open(empty_appetite, "w") as fh:
            json.dump({"orgs": {"driftwood": {"tolerance": 1}}}, fh)
        p = check_party("driftwood", ["risk-bearer"], list(parties),
                         estate_dir=tmp, appetite_path=empty_appetite)
        assert not p, f"risk-bearer with a real entry must pass: {p}"

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
