"""The organisational digital twin.

Code here is disposable by default (constitution, failure mode 3). The durable artefacts are
the versioned model repository and the decision record under `.scratch/twin/`.
"""

from pathlib import Path

PACKAGE_DIR = Path(__file__).resolve().parent
REPO_DIR = PACKAGE_DIR.parent

# Bumped when a change alters emitted artefact bytes. It is a pin: an artefact says which tool
# produced it, and `identical_pins_identical_bytes` is only meaningful pin-for-pin.
TOOL_VERSION = "0.1.0"

__all__ = ["PACKAGE_DIR", "REPO_DIR", "TOOL_VERSION"]
