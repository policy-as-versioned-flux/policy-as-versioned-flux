#!/usr/bin/env python3
"""Validate a claim file written by the classify-and-judge skill.

    validate_claim.py <claim file> --twin <hub root>

This is the check ecosystem ticket 50 asks the gate to run over the skill's PR:
**only existing claim kinds, and `derived_from` names them.** The claim kinds and
the role register are read from the twin ITSELF (`twin/schema.py::CLAIM_KINDS`,
`twin/roles.yaml`), never copied here -- a copy is how a check goes on passing
after the thing it checks has moved.

Exit 0 valid, 1 invalid (every reason printed), 2 could not read the twin.

ponytail: hand-rolled, ~20 rules, no jsonschema -- python3 in this estate has
pyyaml and not jsonschema, which is the same reason
platform/party/party_artefact.py and feeds/verify-feeds.sh hand-roll theirs.
"""
import argparse
import os
import sys

import yaml

SCHEMA = "twin.headline-claim/v1"
PIN_FIELDS = ("party", "kind", "name", "version")
PARENT_KINDS = ("controls", "implementations", "feed")


def twin_facts(hub):
    """The claim kinds and role ids, read off the twin package itself."""
    sys.path.insert(0, os.path.abspath(hub))
    try:
        from twin.schema import CLAIM_KINDS
    except Exception as exc:  # noqa: BLE001 - any import failure is "cannot look"
        raise SystemExit(f"SKIP: no twin package at {hub!r} to read CLAIM_KINDS from ({exc})")
    register = yaml.safe_load(open(os.path.join(hub, "twin", "roles.yaml")))
    return tuple(CLAIM_KINDS), {str(role["id"]) for role in register["roles"]}


def pin_key(pin):
    return tuple(str(pin.get(field, "")) for field in PIN_FIELDS)


def validate(doc, kinds, roles):
    bad = []

    def need(condition, message):
        if not condition:
            bad.append(message)

    need(doc.get("schema") == SCHEMA, f"schema is {doc.get('schema')!r}, not {SCHEMA!r}")
    need(bool(doc.get("org")), "no org: a claim file belongs to one adopter's overlay")
    run = doc.get("run") or {}
    need(run.get("skill") == "classify-and-judge",
         f"run.skill is {run.get('skill')!r}: this file names no skill that produced it")
    need(str(run.get("operator_role", "")) in roles,
         f"run.operator_role {run.get('operator_role')!r} is not a role in twin/roles.yaml -- a "
         f"human-run skill records WHICH ROLE ran it")

    derived = doc.get("derived_from") or []
    need(bool(derived), "derived_from is empty: a claim derived from nothing pinned is not evidence")
    for index, pin in enumerate(derived):
        for field in ("party", "kind", "version"):
            need(bool(pin.get(field)), f"derived_from[{index}] has no {field}")
        need(pin.get("kind") in PARENT_KINDS,
             f"derived_from[{index}] kind {pin.get('kind')!r} is not one of {PARENT_KINDS}")
    declared = {pin_key(pin) for pin in derived}

    claims = doc.get("claims") or []
    need(bool(claims), "no claims: an empty claim file is not a proposal")
    ids = [claim.get("id") for claim in claims]
    need(len(set(ids)) == len(ids), f"duplicate claim ids in {ids}")
    positions = {claim.get("id") for claim in claims if claim.get("kind") == "position"}
    cited = set()

    for claim in claims:
        where = f"claim {claim.get('id')!r}"
        kind = claim.get("kind")
        need(kind in kinds,
             f"{where}: kind {kind!r} is not one the twin has ({', '.join(kinds)}) -- a skill "
             f"never invents a claim kind")
        need(bool(claim.get("component")), f"{where}: names no component")
        need(bool(claim.get("evidence")), f"{where}: carries no evidence")
        price_eligible = claim.get("price_eligible")
        need(isinstance(price_eligible, bool), f"{where}: price_eligible is not stated")

        if kind == "binding":
            signal = claim.get("signal") or {}
            need(bool(signal), f"{where}: a binding claim must name the signal it binds")
            need("evolution_position" not in claim,
                 f"{where}: a binding declares evolution_position, which only a position or "
                 f"override asserts")
            need(claim.get("evidence_grade") == 5,
                 f"{where}: a binding is grade 5, got {claim.get('evidence_grade')!r}")
            need(str(claim.get("claimed_by", "")).endswith("(skill)"),
                 f"{where}: a binding is claimed by a skill, got {claim.get('claimed_by')!r}")
            need(price_eligible is False,
                 f"{where}: a grade-5 binding informs and ranks; only an override prices")
            for field in ("id", "date", "source", "statement", "provenance", "from"):
                need(bool(signal.get(field)), f"{where}: signal has no {field}")
            url = (signal.get("provenance") or {}).get("url", "")
            need(str(url).startswith(("http://", "https://")),
                 f"{where}: signal provenance url {url!r} is not a URL anybody can open")
            pin = signal.get("from") or {}
            if pin:
                cited.add(pin_key(pin))
                need(pin_key(pin) in declared,
                     f"{where}: signal came from {pin_key(pin)}, which derived_from does not name")

        if kind in ("position", "override"):
            need("signal" not in claim,
                 f"{where}: a {kind} claims from accumulated evidence and names no signal")
            position = claim.get("evolution_position")
            need(isinstance(position, (int, float)) and 0.0 <= float(position) <= 1.0,
                 f"{where}: evolution_position {position!r} is not an absolute position in [0,1]")

        if kind == "position":
            need(claim.get("evidence_grade") == 5,
                 f"{where}: the twin's own inference is grade 5, got {claim.get('evidence_grade')!r}")
            need(price_eligible is False, f"{where}: an inferred position does not price")

        if kind == "override":
            need(claim.get("evidence_grade") == 4,
                 f"{where}: an override is grade 4, calibrated expert judgement, got "
                 f"{claim.get('evidence_grade')!r}")
            need(str(claim.get("claimed_by", "")) in roles,
                 f"{where}: claimed_by {claim.get('claimed_by')!r} is not a role in "
                 f"twin/roles.yaml -- an override is named by role, never free text")
            need(claim.get("answers") in positions,
                 f"{where}: answers {claim.get('answers')!r}, which is not a position claim in "
                 f"this file -- an override must keep the estimate it overrules")

        if price_eligible and kind != "override":
            bad.append(f"{where}: only an override prices, and this is a {kind}")

    for pin in declared - cited:
        bad.append(f"derived_from names {pin}, which no claim cites")
    return bad


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("claim")
    parser.add_argument("--twin", default=".",
                        help="the hub checkout holding the twin package and roles.yaml")
    args = parser.parse_args(argv)

    kinds, roles = twin_facts(args.twin)
    doc = yaml.safe_load(open(args.claim))
    bad = validate(doc, kinds, roles)
    if bad:
        for line in bad:
            print(f"not ok  {line}")
        print(f"FAIL: {args.claim} is not a claim file the twin can read")
        return 1
    kinds_used = sorted({claim["kind"] for claim in doc["claims"]})
    print(f"ok  {args.claim}: {len(doc['claims'])} claims, kinds {kinds_used}, all in the twin's "
          f"own CLAIM_KINDS; every pin derived_from names is cited by a claim and every pin a "
          f"claim cites is named ({len(doc['derived_from'])} pins); only the override prices")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
