#!/usr/bin/env python3
"""The enacted tier is bound to the priced tier, across the real estate (ticket 78; ADR-0022).

Platform publishes the rule and the check (`platform/shift-left/tier_binding.py`); each
adopter runs it on its own pull requests through the pinned platform dependency. This is the
hub's side of the same question, asked of what is COMMITTED in `.estate-clone/` right now:

  1. For every party that has both a `composed/evidence.json` and a governed Namespace
     manifest: is the declared `posture.acme.io/tier` at least as tight as the strictest
     `proposed_tier` any priced line selected, clamped to that party's own `overlay.floor`?

  2. Where a party also publishes a selection-policy package, do its fold and platform's agree?
     `platform/wargamer/wargamer.py:select_party_tier` and the adopter's own
     `selection-policy/selection_policy.py:select_party` are pinned separately (ADR-0021, the
     two-implementations guard the pound-seam check already applies to the per-line `select()`);
     this applies it to the party fold, over every combination of line tiers, declared tier and
     floor. Be honest about what that buys: unlike `select()`, the adopter's `select_party` is a
     TRANSLITERATION of platform's fold, so agreement over every shape proves the pinned copy has
     not drifted from the rule it mirrors -- copy fidelity, not two minds agreeing.

Neither reads a cluster and neither writes anything. A party with nothing composed yet, or no
governed Namespace, is could-not-look for that party, not a failure -- but if NO party could be
looked at, the whole check is could-not-look, because a PASS sentence about no one is a lie.

Exit 0 observed true; 1 observed false (a `FAIL:` line for each); 3 could not look.

Usage:  tier_binding_estate.py check [--estate-clone DIR]
        tier_binding_estate.py selfcheck
"""
from __future__ import annotations

import argparse
import importlib.util
import itertools
import os
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
DEFAULT_ESTATE = ROOT / ".estate-clone"
POLICY_PACKAGE = "selection-policy"

# Every party that could carry a governed Namespace and a priced document. `feeds`,
# `insurer`, `nist` and `ico` publish; they declare no cage of their own, and are simply
# not found rather than being named as holes.
PARTIES = ("driftwood", "tuppence", "ludlow", "platform")


def _load(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _platform_modules(estate: Path):
    """`tier_binding` and `wargamer` out of the platform checkout in this estate -- the
    pinned dependency's own copy, never a hub re-implementation of the rule."""
    shift_left = estate / "platform" / "shift-left"
    wargamer_dir = estate / "platform" / "wargamer"
    if not (shift_left / "tier_binding.py").exists():
        return None, None, (f"{shift_left}/tier_binding.py is not in this platform checkout "
                            f"-- the binding rule is platform's to publish")
    sys.path.insert(0, str(wargamer_dir))
    sys.path.insert(0, str(shift_left))
    try:
        wargamer = _load(wargamer_dir / "wargamer.py", "_tb_wargamer")
        tier_binding = _load(shift_left / "tier_binding.py", "_tb_tier_binding")
    except Exception as exc:                                    # noqa: BLE001
        return None, None, f"platform's binding modules do not import: {exc}"
    return tier_binding, wargamer, None


def _agree(wargamer, package_path: Path, name: str, out) -> int:
    """The two party-level folds, over every shape on the ladder. Returns 1 on a
    disagreement (which is a FAIL), 0 otherwise."""
    try:
        theirs = _load(package_path, f"_tb_sel_{name}")
    except Exception as exc:                                    # noqa: BLE001
        out("FAIL", f"{name}: its own {POLICY_PACKAGE} package does not import: {exc}")
        return 1
    if not hasattr(theirs, "select_party"):
        out("SKIP", f"{name}: its {POLICY_PACKAGE} package v{getattr(theirs, 'VERSION', '?')} "
                    f"publishes no select_party() yet, so there is no party fold to compare")
        return 0
    ladder = list(wargamer.LADDER)
    # A price selects only from LADDER and so does a floor; a DECLARATION may also be
    # ADR-0022's `infra`, so the declared tier is drawn from the longer list. Nothing here
    # proves independence: the adopter's select_party is a transliteration of platform's
    # fold, so an agreement over every shape is copy fidelity -- that the pinned package has
    # not drifted from the rule it mirrors -- not two implementations reaching one answer.
    declarable = list(getattr(wargamer, "DECLARABLE", wargamer.LADDER))
    cases = 0
    for n in (0, 1, 2, 3):
        for lines in itertools.combinations_with_replacement(ladder, n):
            for current in [None] + declarable:
                for floor in [None] + ladder:
                    cases += 1
                    prices = [{"source": f"s{i}", "kind": "feed", "proposed_tier": t}
                              for i, t in enumerate(lines)]
                    ours = wargamer.select_party_tier(prices, current=current, floor=floor)
                    mine = theirs.select_party(list(lines), current=current, floor=floor)
                    if (ours["tier"], ours["held"]) != (mine["tier"], mine["held"]):
                        out("FAIL", f"{name}: the two party folds disagree -- lines {list(lines)}, "
                                    f"declared {current!r}, floor {floor!r}: "
                                    f"platform/wargamer picks {ours['tier']!r} (held="
                                    f"{ours['held']}) and {name}'s own {POLICY_PACKAGE} "
                                    f"v{theirs.VERSION} picks {mine['tier']!r} (held="
                                    f"{mine['held']}) (ADR-0021)")
                        return 1
    out("PASS", f"{name}: platform/wargamer's select_party_tier and {name}'s own "
                f"{POLICY_PACKAGE} v{theirs.VERSION} select_party fold the party the same way "
                f"in all {cases} cases -- every line combination up to three, every declared "
                f"tier (including ADR-0022's `infra`) and every floor on the ladder. This is "
                f"copy fidelity, not independence: the package's fold is a transliteration of "
                f"platform's")
    return 0


def check(estate: Path) -> int:
    lines: list[str] = []

    def out(verdict: str, msg: str) -> None:
        lines.append(f"{verdict}: {msg}")
        print(f"{verdict}: {msg}")

    if not (estate / "platform").is_dir():
        print(f"SKIP: no {estate}/ -- run ./clone-estate.sh first")
        return 3
    tier_binding, wargamer, why = _platform_modules(estate)
    if why:
        print(f"SKIP: {why}")
        return 3

    looked = 0
    failed = 0
    for name in PARTIES:
        adopter = estate / name
        if not adopter.is_dir():
            continue
        rc, last, verdict = tier_binding.check(adopter / "composed" / "evidence.json", adopter)
        if rc == 3:
            out("SKIP", f"{name}: {last[len('SKIP: '):]}")
            continue
        looked += 1
        if rc == 0:
            out("PASS", f"{name}: {last[len('OK: '):]}")
        else:
            failed += 1
            out("FAIL", f"{name}: {last[len('FAIL: '):]}")
        pkg = adopter / POLICY_PACKAGE / "selection_policy.py"
        if pkg.exists():
            failed += _agree(wargamer, pkg, name, out)

    if not looked:
        print("SKIP: no party in this estate has both a composed evidence document and a "
              "governed Namespace manifest, so nothing here observed that any cage is bound")
        return 3
    return 1 if failed else 0


# --------------------------------------------------------------------------
def selfcheck(estate: Path = DEFAULT_ESTATE) -> int:
    """The estate walk itself, over a planted estate: a bound party, a loose one, a party
    with nothing composed, and a selection package that disagrees. Each must grade as it must
    -- otherwise this script could pass over a real estate for the wrong reason.

    The plant is built around the REAL platform tree (symlinked in below), so this can only run
    where `estate`'s platform checkout already carries the published rule. Where it does not,
    that is a could-not-look and this returns 3: asserting instead graded "the rule is not here
    yet" as "the planted case no longer bites", which is a different and untrue sentence
    (fixed 2026-09-04)."""
    import json
    import shutil
    import tempfile

    real = estate
    if not (real / "platform" / "shift-left" / "tier_binding.py").exists():
        print(f"SKIP: {real}/platform/shift-left/tier_binding.py is not in this platform "
              f"checkout -- there is no published rule to plant the selfcheck's estate around")
        return 3

    def party(root: Path, name: str, declared: str, priced: list[str]) -> None:
        d = root / name / "gitops" / "apps"
        d.mkdir(parents=True)
        (d / "namespace.yaml").write_text(
            'apiVersion: v1\nkind: Namespace\nmetadata:\n  name: x\n  labels:\n'
            '    policy-as-versioned.dev/governed: "true"\n'
            f'    posture.acme.io/tier: "{declared}"\n')
        (root / name / "composed").mkdir(parents=True)
        (root / name / "composed" / "evidence.json").write_text(json.dumps(
            {"prices": [{"source": f"s{i}", "kind": "feed", "proposed_tier": t}
                        for i, t in enumerate(priced)]}))

    with tempfile.TemporaryDirectory() as d:
        fake = Path(d) / ".estate-clone"
        fake.mkdir(parents=True)
        # The REAL platform tree, symlinked in: the rule under test is the one
        # platform publishes, not a copy of it, and wargamer.py imports its own
        # siblings (fair, risk, graded) that a partial copy would not carry.
        (fake / "platform").symlink_to(real / "platform")
        party(fake, "driftwood", "isolated", ["baseline", "isolated"])
        party(fake, "tuppence", "baseline", ["restricted"])        # the loose one
        (fake / "ludlow").mkdir()                                  # nothing composed
        rc = check(fake)
        assert rc == 1, ("a party declaring baseline over a restricted line must FAIL", rc)

        shutil.rmtree(fake / "tuppence")
        rc = check(fake)
        assert rc == 0, ("with the loose party gone, the rest of the estate is bound", rc)

        # a selection package that folds the party differently is a disagreement, not a vote
        pkg = fake / "driftwood" / POLICY_PACKAGE
        pkg.mkdir()
        (pkg / "selection_policy.py").write_text(
            'VERSION = "9.9.9"\n'
            'def select_party(line_tiers, current=None, floor=None):\n'
            '    return {"tier": "baseline", "held": False}\n')
        rc = check(fake)
        assert rc == 1, ("a selection package that disagrees with platform must FAIL", rc)

        # a package that publishes no party fold yet is could-not-look for that comparison,
        # never a silent pass and never a failure
        (pkg / "selection_policy.py").write_text('VERSION = "1.0.0"\n')
        rc = check(fake)
        assert rc == 0, ("a package with no select_party() yet is a skip, not a failure", rc)

        # nothing to look at at all is could-not-look, never a PASS about no one
        shutil.rmtree(fake / "driftwood")
        assert check(fake) == 3, "an estate with nothing composed must be could-not-look"

    print("ok  the estate walk grades a bound party PASS, a party declaring looser than its "
          "strictest priced line FAIL, a selection package that folds the party differently "
          "FAIL, a package with no party fold yet SKIP, and an estate with nothing composed "
          "could-not-look rather than a PASS about no one")
    return 0


def main(argv: list[str]) -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = p.add_subparsers(dest="cmd", required=True)
    default_estate = Path(os.environ.get("ESTATE_CLONE", DEFAULT_ESTATE))
    c = sub.add_parser("check")
    c.add_argument("--estate-clone", type=Path, default=default_estate)
    s = sub.add_parser("selfcheck")
    s.add_argument("--estate-clone", type=Path, default=default_estate)
    args = p.parse_args(argv[1:])
    if args.cmd == "selfcheck":
        return selfcheck(args.estate_clone)
    return check(args.estate_clone)


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
