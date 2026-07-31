#!/usr/bin/env python3
"""ci-check.py — the shift-left CI check (ticket 12).

An institution dev's PR ships a workload manifest that CLAIMS a policy
version (the `policy-as-versioned.dev/policy-version` label — the same
version array contract distribution/versions.yaml renders live). This check:

  1. resolves the target's supported version WINDOW — target ±1, off the SAME
     declared array distribution/versions.yaml owns (no second source of
     truth: reuses render-orphan-guard.py's `versions()`),
  2. runs the REAL `kyverno apply` for every policy in that window against the
     workload, offline (no cluster, no flux-operator).

`kyverno apply` reports the CEL verdict (pass/fail) independent of whether
`spec.validationActions` says Audit or Deny — Audit only changes what a LIVE
cluster does with a fail (report vs block). So a workload that fails here
would be denied the moment its target version's Audit->Deny promotion PR
lands (ADR-0006: promotion is editorial, never a timer) — this check catches
that flip BEFORE merge, not at deploy.

Usage:
    ci-check.py --resource path/to/workload.yaml
    ci-check.py --resource path/to/workload.yaml --target 2.0.0   # override the label
"""
from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
DISTRIBUTION = HERE.parent / "distribution"
LABEL = "policy-as-versioned.dev/policy-version"

def _import_versions():
    """render-orphan-guard.py's `versions()` -- the one array, reused (hyphenated
    filename, so importlib by path rather than a plain `import`)."""
    import importlib.util

    spec = importlib.util.spec_from_file_location(
        "render_orphan_guard", DISTRIBUTION / "render-orphan-guard.py"
    )
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.versions


versions = _import_versions()


def target_version(resource: Path, override: str | None) -> str | None:
    """The version the workload claims — None if unversioned (out of scope)."""
    if override:
        return override
    import yaml

    docs = [d for d in yaml.safe_load_all(resource.read_text()) if d]
    claimed = {d.get("metadata", {}).get("labels", {}).get(LABEL) for d in docs}
    claimed.discard(None)
    if not claimed:
        return None
    if len(claimed) > 1:
        raise SystemExit(f"resource file claims multiple versions {claimed}; pass --target")
    return claimed.pop()


def skew_window(target: str, declared: list[str]) -> list[str]:
    """Target ±1 off the declared array (sorted by semver), clipped to the array."""
    key = lambda v: tuple(int(p) for p in v.split("."))
    ordered = sorted(declared, key=key)
    if target not in ordered:
        raise SystemExit(
            f"policy-version {target!r} is not in the platform-declared array {ordered} "
            "(orphan) -- nothing to shift-left check against"
        )
    i = ordered.index(target)
    return ordered[max(0, i - 1) : i + 2]


def policy_files(version: str) -> list[Path]:
    d = DISTRIBUTION / "policies" / f"v{version}"
    files = sorted(p for p in d.glob("*.yaml") if p.name != "kustomization.yaml")
    if not files:
        raise SystemExit(f"no policy files under {d}")
    return files


def kyverno_apply(policies: list[Path], resource: Path) -> tuple[bool, str]:
    cmd = ["kyverno", "apply", *[str(p) for p in policies], "--resource", str(resource)]
    proc = subprocess.run(cmd, capture_output=True, text=True)
    return proc.returncode == 0, proc.stdout + proc.stderr


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--resource", required=True, type=Path, help="workload manifest to check")
    ap.add_argument("--target", help="override the version read off the resource's label")
    ap.add_argument("--versions-file", type=Path, default=DISTRIBUTION / "versions.yaml")
    args = ap.parse_args(argv)

    declared = versions(args.versions_file)
    target = target_version(args.resource, args.target)
    if target is None:
        print(f"{args.resource}: unversioned (no {LABEL} label) -- out of scope, pass")
        return 0

    window = skew_window(target, declared)
    print(f"{args.resource}: targets {target}, checking supported window {window}")

    failed = False
    for v in window:
        policies = policy_files(v)
        ok, output = kyverno_apply(policies, args.resource)
        print(f"--- kyverno apply @ v{v} ---")
        print(output.strip())
        if not ok:
            failed = True
            flip = " (Audit->Deny flip: passes today's Audit, would be denied on promotion)" if v != target else ""
            print(f"FAIL @ v{v}{flip}")

    if failed:
        print(f"\nshift-left: {args.resource} would be denied somewhere in its supported window {window}")
        return 1
    print(f"\nshift-left: {args.resource} is compliant across its supported window {window}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
