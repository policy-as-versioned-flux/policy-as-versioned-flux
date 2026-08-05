"""The invariant suite — the guardrail that makes a seventy-way split safe.

Most of this system's non-negotiables are **absences**, and an absence never shows up in a diff:
a new feature does, a removed refusal does not. The suite asserts them at seam 1.

Most invariants have no subject yet, so the suite ships as a harness plus a **manifest of pending
invariants**, each naming the ticket that must activate it. An invariant still pending after its
activating ticket has closed is itself a failure — otherwise "pending" becomes a silent weakening
the guardrail cannot see.

Shape carried forward from `estate/`: a numbered check per claim, each independently runnable,
reporting pass/fail, and skipping honestly rather than faking (build ticket 02).
"""

from __future__ import annotations

import hashlib
import inspect
import textwrap
from dataclasses import dataclass
from pathlib import Path
from typing import Callable

PASS, FAIL, SKIP = "PASS", "FAIL", "SKIP"


class Violated(Exception):
    """The invariant does not hold."""


class Skip(Exception):
    """Cannot be asserted here. Skipped, never faked."""


@dataclass(frozen=True)
class Result:
    number: int
    name: str
    status: str
    detail: str
    invariant: bool


CheckFn = Callable[["Context"], str]
_REGISTRY: dict[str, CheckFn] = {}
_HARNESS: dict[str, CheckFn] = {}


def invariant(name: str) -> Callable[[CheckFn], CheckFn]:
    """Register a check that asserts a named invariant from the manifest."""

    def wrap(fn: CheckFn) -> CheckFn:
        if name in _REGISTRY:
            raise RuntimeError(f"invariant {name!r} registered twice")
        _REGISTRY[name] = fn
        return fn

    return wrap


SKIPPABLE: set[str] = set()


def harness_check(name: str, may_skip: bool = False) -> Callable[[CheckFn], CheckFn]:
    """Register a check that guards the suite itself rather than the system.

    `may_skip` is deliberately rare: a guard that quietly declines to run is worth less than no
    guard, because it reads as green. Only checks whose precondition genuinely cannot exist
    everywhere — a CI-only architecture matrix, a history that does not exist yet — may set it.
    """

    def wrap(fn: CheckFn) -> CheckFn:
        if name in _HARNESS:
            raise RuntimeError(f"harness check {name!r} registered twice")
        _HARNESS[name] = fn
        if may_skip:
            SKIPPABLE.add(name)
        return fn

    return wrap


def registry() -> dict[str, CheckFn]:
    return dict(_REGISTRY)


def harness_registry() -> dict[str, CheckFn]:
    return dict(_HARNESS)


def body_hash(fn: CheckFn) -> str:
    """Hash of a check's source, normalised for whitespace.

    A test body that changes without an authorising decision ticket is how a refusal gets
    quietly weakened, so the body is pinned in the manifest.
    """
    source = textwrap.dedent(inspect.getsource(fn))
    lines = [line.rstrip() for line in source.splitlines()]
    while lines and not lines[0]:
        lines.pop(0)
    while lines and not lines[-1]:
        lines.pop()
    return hashlib.sha256("\n".join(lines).encode("utf-8")).hexdigest()


MANIFEST_PATH = Path(__file__).resolve().parent / "manifest.yaml"

from . import checks as _checks  # noqa: E402,F401  (registration side effect)
from .harness import Context, Suite, run  # noqa: E402,F401

__all__ = [
    "Context",
    "FAIL",
    "PASS",
    "Result",
    "SKIP",
    "SKIPPABLE",
    "Skip",
    "Suite",
    "Violated",
    "body_hash",
    "harness_check",
    "harness_registry",
    "invariant",
    "registry",
    "run",
]
