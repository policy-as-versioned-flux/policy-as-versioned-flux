"""The organisational digital twin.

Code here is disposable by default (constitution, failure mode 3). The durable artefacts are
the versioned model repository and the decision record under `.scratch/twin/`.
"""

from pathlib import Path

PACKAGE_DIR = Path(__file__).resolve().parent
REPO_DIR = PACKAGE_DIR.parent

# mo-12 deleted the hub's committed estate/ tree; the six units are real repos now (mo-08),
# fetched into .estate-clone/ by clone-estate.sh (git-ignored, disposable). One source of truth
# for every twin/*.py module that reads from it (verify/*/*.py has its own copy, deliberately:
# twin/ and verify/ do not import from each other).
ESTATE_CLONE_DIR = REPO_DIR / ".estate-clone"

# Bumped when a change alters emitted artefact bytes. It is a pin: an artefact says which tool
# produced it, and `identical_pins_identical_bytes` is only meaningful pin-for-pin.
TOOL_VERSION = "0.1.0"

__all__ = ["ESTATE_CLONE_DIR", "PACKAGE_DIR", "REPO_DIR", "TOOL_VERSION"]
