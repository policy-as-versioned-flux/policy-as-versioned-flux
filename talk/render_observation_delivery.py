#!/usr/bin/env python3
"""Render an adopter's thin caller with explicit immutable source and bundle pins."""
from __future__ import annotations

import argparse
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]


def render(org: str, source_sha: str, bundle_sha256: str) -> str:
    if org not in {'driftwood', 'tuppence', 'ludlow'}:
        raise ValueError('no trusted adopter profile')
    if re.fullmatch('[0-9a-f]{40}', source_sha) is None or re.fullmatch('[0-9a-f]{64}', bundle_sha256) is None:
        raise ValueError('caller requires exact source commit and bundle SHA256')
    text = (ROOT / 'talk/observation-delivery.workflow.yml').read_text()
    return text.replace('@ORG@', org).replace('@SOURCE_SHA@', source_sha).replace('@BUNDLE_SHA256@', bundle_sha256)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--org', required=True, choices=['driftwood', 'tuppence', 'ludlow'])
    parser.add_argument('--source-sha', required=True)
    parser.add_argument('--bundle-sha256', required=True)
    parser.add_argument('--output', required=True, type=Path)
    args = parser.parse_args()
    args.output.write_text(render(args.org, args.source_sha, args.bundle_sha256))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
