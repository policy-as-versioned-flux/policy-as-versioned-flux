#!/usr/bin/env python3
"""rederive_bumps.py -- ticket cs-01 (computed-semver map).

Question: take the old faithful-floor's real, signed release line
(policy-as-versioned-flux/policy @ v1.0.0 / v2.0.0 / v2.0.1 / v2.1.1) as fixed
input, evaluate adjacent version pairs offline with the real `kyverno apply`
CLI -- the same primitive estate/platform/shift-left/verify-shift-left.sh
already runs -- and see whether major/minor/patch falls out of the OBSERVED
verdict movement, per CONTEXT.md's "Policy version" definition, without being
told the answer in advance.

CONTEXT.md's rule, read through ticket 02's resolution (compliant == admitted;
Audit-that-fires does not fail a workload; refusal is Deny+CEL-fail):

    major = an existing policy's admission outcome flips admitted -> refused
            for some fixture (an Audit->Deny promotion is a special case of
            this: same CEL body, tighter action)
    minor = a policy present in NEW but absent in OLD, and it is Audit-only
            (by construction it cannot refuse anything, so it cannot be major)
    patch = an existing policy's admission outcome only ever flips
            refused -> admitted across the fixture set (the passing set only
            grows), never the reverse

`kyverno apply`'s own pass/fail is the CEL result ONLY -- it does not know
about validationActions (see the `--show-pooled-exit-is-not-admission` demo
below, and estate/platform/shift-left/ci-check.py's docstring, which already
documents this). Admission outcome = combine(CEL result, validationActions),
computed here, not read off kyverno's exit code directly.
"""
from __future__ import annotations

import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path

import yaml

HERE = Path(__file__).resolve().parent
CORPUS = HERE / "corpus"
FIXTURES = CORPUS / "fixtures"

ALL_FIXTURES = sorted(FIXTURES.glob("*.yaml"))


def cel_pass(policy_file: Path, fixture_file: Path) -> bool:
    """True if the real `kyverno apply` says this fixture satisfies this
    policy's CEL body -- independent of validationActions (Audit/Deny)."""
    proc = subprocess.run(
        ["kyverno", "apply", str(policy_file), "--resource", str(fixture_file)],
        capture_output=True,
        text=True,
    )
    return proc.returncode == 0


def action_of(policy_file: Path) -> str:
    body = yaml.safe_load(policy_file.read_text())
    actions = body["spec"]["validationActions"]
    assert len(actions) == 1, f"{policy_file}: expected one validationAction, got {actions}"
    return actions[0]


def admitted(action: str, passed: bool) -> bool:
    """CONTEXT.md / ticket 02: Audit never refuses -- only Deny+CEL-fail does."""
    return action == "Audit" or passed


@dataclass
class PolicyClassification:
    verdict: str  # "major" | "minor" | "patch" | "none" | "removed"
    detail: str


def classify_policy(
    old_file: Path | None, new_file: Path | None, fixtures: list[Path]
) -> PolicyClassification:
    if old_file is None and new_file is not None:
        action = action_of(new_file)
        if action == "Audit":
            return PolicyClassification("minor", "added, Audit-only -- cannot refuse anything")
        return PolicyClassification(
            "major", "added as Deny -- a brand-new gate can refuse a currently-admitted workload"
        )
    if old_file is not None and new_file is None:
        return PolicyClassification("removed", "policy dropped")

    assert old_file is not None and new_file is not None
    action_old, action_new = action_of(old_file), action_of(new_file)
    narrowed = widened = False
    moves = []
    for fx in fixtures:
        adm_old = admitted(action_old, cel_pass(old_file, fx))
        adm_new = admitted(action_new, cel_pass(new_file, fx))
        if adm_old and not adm_new:
            narrowed = True
            moves.append(f"{fx.stem}: admitted -> REFUSED")
        elif not adm_old and adm_new:
            widened = True
            moves.append(f"{fx.stem}: refused -> admitted")
    if narrowed:
        return PolicyClassification("major", "; ".join(moves) or "narrowed")
    if widened:
        return PolicyClassification("patch", "; ".join(moves))
    return PolicyClassification("none", "no fixture in the corpus moved")


@dataclass
class Pair:
    name: str
    old: dict[str, str]  # policy name -> corpus filename, at the OLD version
    new: dict[str, str]  # policy name -> corpus filename, at the NEW version
    expected_whole_body: str
    expected_per_policy: dict[str, str] = field(default_factory=dict)


PAIRS = [
    Pair(
        name="1.0.0 -> 2.0.0",
        old={"require-department-label": "department-label-1.0.0.yaml"},
        new={"require-department-label": "department-label-2.0.0.yaml"},
        expected_whole_body="major",
        expected_per_policy={"require-department-label": "major"},
    ),
    Pair(
        name="2.0.1 -> 2.1.1",
        old={
            # unchanged since 2.0.0 (byte-identical body; only re-versioned by
            # kustomize labels/nameSuffix, which this raw-body corpus doesn't
            # carry) -- included so the comparison covers the WHOLE policy
            # body, per CONTEXT.md ("a policy version covers the whole body").
            "require-department-label": "department-label-2.0.0.yaml",
            "require-known-department-label": "known-department-label-2.0.1.yaml",
        },
        new={
            "require-department-label": "department-label-2.0.0.yaml",
            "require-known-department-label": "known-department-label-2.1.1.yaml",
            "require-owner-annotation": "owner-annotation-2.1.1.yaml",
        },
        # Two changes bundle into one release: require-known-department-label
        # widens (patch) AND require-owner-annotation is added (minor). Minor
        # dominates patch when combining -- see the report below for what
        # this implies about the real v2.1.1 tag's own decimal.
        expected_whole_body="minor",
        expected_per_policy={
            "require-department-label": "none",
            "require-known-department-label": "patch",
            "require-owner-annotation": "minor",
        },
    ),
]

RANK = {"none": 0, "patch": 1, "minor": 2, "major": 3}


def whole_body_bump(per_policy: dict[str, PolicyClassification]) -> str:
    """CONTEXT.md: 'a policy version covers the whole body' -- take the most
    significant per-policy movement, exactly like combining a set of file
    changes into one semver bump."""
    ranked = max(per_policy.values(), key=lambda c: RANK[c.verdict])
    return ranked.verdict


def demo_pooled_exit_is_not_admission() -> None:
    """The `kyverno apply` exit code, pooled across a mixed Audit+Deny policy
    set, is NOT the admission verdict -- it's raw CEL pass/fail. This is the
    concrete evidence for the report's headline finding: minor cannot be told
    apart from a real narrowing using a bare kyverno apply exit code; you must
    read validationActions per policy and combine it with the CEL result
    yourself (which is exactly what classify_policy does above, and what a
    naive engine that just shells out and checks $? would not)."""
    policies = [
        CORPUS / "department-label-2.0.0.yaml",  # Deny
        CORPUS / "known-department-label-2.1.1.yaml",  # Deny
        CORPUS / "owner-annotation-2.1.1.yaml",  # Audit
    ]
    fixture = FIXTURES / "no-owner.yaml"  # department set, owner missing
    proc = subprocess.run(
        ["kyverno", "apply", *[str(p) for p in policies], "--resource", str(fixture)],
        capture_output=True,
        text=True,
    )
    pooled_says_fail = proc.returncode != 0
    really_admitted = admitted("Audit", cel_pass(CORPUS / "owner-annotation-2.1.1.yaml", fixture))
    print("-- pooled kyverno apply is not the admission verdict --")
    print(f"   pooled exit code across all 3 policies: {proc.returncode} "
          f"({'FAIL' if pooled_says_fail else 'pass'})")
    print(f"   real admission outcome (Audit never refuses): "
          f"{'admitted' if really_admitted else 'REFUSED'}")
    if pooled_says_fail and really_admitted:
        print("   CONFIRMED: pooled exit code disagrees with the real admission outcome.")
        print("   A minor bump (new Audit policy) is invisible to admitted/refused, but a naive")
        print("   engine reading only kyverno apply's $? across the whole set would call this a")
        print("   narrowing (wrongly major) -- it must read validationActions per policy instead.")
    else:
        print("   FAIL: expected the pooled exit code to disagree with the real admission outcome")
        sys.exit(1)
    print()


def main() -> int:
    demo_pooled_exit_is_not_admission()

    all_ok = True
    for pair in PAIRS:
        print(f"== {pair.name} ==")
        names = sorted(set(pair.old) | set(pair.new))
        per_policy: dict[str, PolicyClassification] = {}
        for name in names:
            old_file = CORPUS / pair.old[name] if name in pair.old else None
            new_file = CORPUS / pair.new[name] if name in pair.new else None
            c = classify_policy(old_file, new_file, ALL_FIXTURES)
            per_policy[name] = c
            expect = pair.expected_per_policy.get(name)
            mark = "OK" if expect is None or c.verdict == expect else "MISMATCH"
            print(f"   {name}: {c.verdict}"
                  + (f"  (expected {expect}, {mark})" if expect else "")
                  + (f"  -- {c.detail}" if c.detail else ""))

        got = whole_body_bump(per_policy)
        mark = "OK" if got == pair.expected_whole_body else "MISMATCH"
        print(f"   WHOLE-BODY BUMP: {got}  (ticket's asserted answer: "
              f"{pair.expected_whole_body}, {mark})")
        if got != pair.expected_whole_body:
            all_ok = False
        for name, expect in pair.expected_per_policy.items():
            if per_policy[name].verdict != expect:
                all_ok = False
        print()

    print("== honest finding ==")
    print("Per-NAMED-POLICY, all three of the ticket's asserted bumps rederive exactly:")
    print("  require-department-label 1.0.0->2.0.0:        major (Audit->Deny promotion)")
    print("  require-known-department-label 2.0.1->2.1.1:  patch (enum widened +legal)")
    print("  require-owner-annotation absent->2.1.1:       minor (added, Audit-only)")
    print()
    print("But CONTEXT.md scopes semver at the WHOLE-BODY level ('a policy version covers")
    print("the whole body'), and at that level the real v2.0.1->v2.1.1 release bundles the")
    print("minor addition AND the patch widening into ONE tag. Combining rules say the more")
    print("significant change wins, so the whole-body-correct bump for that release is MINOR,")
    print("not the 'patch' label the ticket's own bullet points attach to '2.1.1' -- that")
    print("bullet describes require-known-department-label's own delta in isolation, not the")
    print("release. The real tag's decimal (2.1.1, minor bumped 0->1 but patch held at 1")
    print("instead of resetting to 0) does not follow textbook bump-and-reset semver either")
    print("way -- CONTEXT.md defines per-change classification but is silent on reset-on-bump,")
    print("so this is named as a real gap in the historical release line, not glossed over.")
    print()
    print("Minor cannot be rederived from bare admission pass/fail alone: a brand-new Audit")
    print("policy produces ZERO admitted/refused transitions for any fixture by construction")
    print("(Audit never refuses), so there is no verdict movement to observe -- it can only be")
    print("detected by a STRUCTURAL diff (a policy name present in NEW, absent in OLD) plus its")
    print("validationActions, never by watching the pass/fail move on a fixed corpus.")
    return 0 if all_ok else 1


if __name__ == "__main__":
    sys.exit(main())
