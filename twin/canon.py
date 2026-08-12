"""Canonical serialisation.

Byte-identity given the pins is the whole attestation story (decision ticket 14): if the
derivation cannot be reproduced, the attestation is a claim rather than a proof. Everything
emitted at seam 1 goes through here.
"""

from __future__ import annotations

import hashlib
import json
from typing import Any


def canonical_json(obj: Any) -> bytes:
    """Sorted keys, fixed separators, ASCII-escaped, trailing newline.

    `allow_nan=False` on purpose: NaN/Infinity are not JSON and their text form is not portable,
    so a stray one must fail loudly rather than emit bytes that differ across readers.
    """
    text = json.dumps(
        obj,
        sort_keys=True,
        indent=2,
        ensure_ascii=True,
        separators=(",", ": "),
        allow_nan=False,
    )
    return (text + "\n").encode("utf-8")


def sha256_hex(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def digest_of(obj: Any) -> str:
    return sha256_hex(canonical_json(obj))


def walk_values(obj: Any) -> "list[tuple[str, Any]]":
    """Every (dotted-key-path, value) pair in a nested structure.

    Used by the refusal tests: an absence is only assertable if you can look everywhere.
    """
    out: list[tuple[str, Any]] = []

    def rec(node: Any, path: str) -> None:
        if isinstance(node, dict):
            for k, v in node.items():
                rec(v, f"{path}.{k}" if path else str(k))
        elif isinstance(node, list):
            for i, v in enumerate(node):
                rec(v, f"{path}[{i}]")
        else:
            out.append((path, node))

    rec(obj, "")
    return out


def walk_keys(obj: Any) -> "list[str]":
    """Every key name appearing anywhere in a nested structure."""
    out: list[str] = []

    def rec(node: Any) -> None:
        if isinstance(node, dict):
            for k, v in node.items():
                out.append(str(k))
                rec(v)
        elif isinstance(node, list):
            for v in node:
                rec(v)

    rec(obj)
    return out
