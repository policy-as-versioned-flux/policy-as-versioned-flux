#!/usr/bin/env python3
"""Validate a forecast file written by the derive-probability skill (ecosystem ticket 93).

    validate_forecast.py <forecast file> --twin <hub root> [--headless] [--feeds DIR] [--adopter DIR]

The rules live in the twin ITSELF (`twin/derived_forecast.py::validate`), never copied here:
a copy is how a check goes on passing after the thing it checks has moved. This file is the
CLI the local clock's steps table names (`<validator> FILE --twin <hub> --headless`).

What is checked: the artefact's shape; every probability strictly inside (0,1) with a
perspective, a currency the perspective prices in, a basis (derived or recorded) and the grade
the schema allows -- 5 for a derivation, none for a recorded belief; a derived probability rests
on at least one signal whose observation the SERVED feed envelope carries (a move between two
dated levels, or a news event with its URL), cited by envelope; no weight, score or probability
on a signal (no arithmetic on ordinals, no level read as a probability); a recorded belief is the
world model's number unchanged; the scenario, its horizon and the perspective are the overlay's;
`prices_through` and `recorded_belief` on every forecast, both of which SKILL.md 2 promises;
and a DUPLICATE YAML KEY anywhere in the file is refused, so the file a human reads in the pull
request is the file this validator read.

**This layer is advisory.** It runs on the owner's machine, in a tree a headless model can write
to; the measurement of record is the gate, `verify/twin-evals/verify-derived-forecast.sh`, over
`origin/main`. The local clock copies this file and the twin package OUT of the hub before the
model starts and runs the copy, and reads the hub's own copies back afterwards (review F5), but
the copy is still only as good as the machine it sits on.

`--headless` is the local clock's word (ticket 92): the file must say `run.headless: true`.
`--feeds` defaults to `$LOCAL_CLOCK_ESTATE/feeds`, then `<hub>/.estate-clone/feeds`. `--adopter`
defaults to the file's own repository (a file at `<adopter>/twin/forecasts/x.forecast.yaml`).

Exit 0 valid, 1 invalid (every reason printed), 2 could not look (SKIP: last line) -- a file
nobody could check is not proposed, and could-not-look is never a pass.
"""
import argparse
import os
import sys

import yaml


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("forecast")
    parser.add_argument("--twin", default=".", help="the hub checkout holding the twin package and roles.yaml")
    parser.add_argument("--headless", action="store_true",
                        help="the caller knows nobody was at the keyboard (the local clock, ticket 92)")
    parser.add_argument("--feeds", default=None, help="the feeds publisher's checkout (served envelopes)")
    parser.add_argument("--adopter", default=None, help="the adopter checkout the forecast belongs to")
    args = parser.parse_args(argv)

    hub = os.path.abspath(args.twin)
    sys.path.insert(0, hub)
    try:
        from twin import derived_forecast as df
    except Exception as exc:  # noqa: BLE001 - any import failure is "cannot look"
        print(f"SKIP: no twin package at {hub!r} to read the forecast rules from ({exc})")
        return 2
    register = yaml.safe_load(open(os.path.join(hub, "twin", "roles.yaml")))
    roles = {str(role["id"]) for role in register["roles"]}

    path = os.path.abspath(args.forecast)
    adopter = args.adopter
    if adopter is None:
        parts = path.split(os.sep)
        if len(parts) >= 3 and parts[-2] == "forecasts" and parts[-3] == "twin":
            adopter = os.sep.join(parts[:-3]) or os.sep
    feeds = args.feeds
    if feeds is None:
        estate = os.environ.get("LOCAL_CLOCK_ESTATE") or os.path.join(hub, ".estate-clone")
        feeds = os.path.join(estate, "feeds")
    if adopter is None:
        print(f"SKIP: {path} is not under <adopter>/twin/forecasts/ and no --adopter was given: the scenario, "
              f"perspective and recorded belief cannot be checked against an overlay")
        return 2

    # `df.load_yaml`, never `yaml.safe_load`: a duplicate mapping key is REFUSED here, because
    # PyYAML keeps the last of two and the file a human reads in the pull request would not be
    # the file this validator read (review F4, measured: a visible `probability: 0.999` above a
    # real 0.27 validated as 0.27 and the clock committed it).
    try:
        doc = df.load_yaml(open(path, encoding="utf-8").read(), path)
    except df.DerivedForecastError as exc:
        print(f"not ok  {exc}")
        print(f"FAIL: {path} is not a forecast file the twin can read")
        return 1
    if not isinstance(doc, dict):
        print(f"not ok  {path} is not a YAML mapping")
        print(f"FAIL: {path} is not a forecast file the twin can read")
        return 1
    try:
        bad = df.validate(doc, roles, headless=args.headless, adopter_root=adopter, feeds_root=feeds)
    except df.CannotLook as exc:
        print(f"SKIP: {exc}")
        return 2
    except df.DerivedForecastError as exc:
        print(f"not ok  {exc}")
        print(f"FAIL: {path} is not a forecast file the twin can read")
        return 1
    if bad:
        for line in bad:
            print(f"not ok  {line}")
        print(f"FAIL: {path} is not a forecast file the twin can read")
        return 1
    print(f"ok  {path}: {df.summary(doc)}; every signal's observation is carried by the served envelope under {feeds}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
