#!/usr/bin/env python3
"""Compatibility entrypoint for the hub's protected TRUTH delivery controller.

All authority and conservation behavior is implemented once in observation_delivery.
The immutable bundle exposes that same implementation to the six adopter clocks.
"""
from __future__ import annotations

from pathlib import Path
import sys

# Direct script invocation and package-based tests resolve the same trusted module.
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from talk.observation_delivery import (  # noqa: E402
    APP_BOT_LOGIN, APP_BOT_USER_ID, APP_ID, REPOSITORY, ROOT, WORKFLOW,
    Refusal, authority, deliver, facts, git, github_api, main, observation,
    positive, recorded, require, sha, subprocess, validate_pr, verify_signature, window,
)

if __name__ == '__main__':
    raise SystemExit(main())
