"""Path to the disposable local estate checkout — one source of truth.

Post-split (mo-12): the six parties are no longer sibling directories of this hub repo, they are
six real GitHub repos. ESTATE points at .estate-clone/, the disposable local checkout
clone-estate.sh assembles from those repos (git-ignored) — same shape these checks always walked,
fetched instead of committed. Shared by verify/party/party.py, verify/proportionality/render.py,
verify/provenance/provenance.py. (twin/ has its own copy, twin.ESTATE_CLONE_DIR — deliberately not
imported from here: twin/ and verify/ do not depend on each other.)
"""
import os

VERIFY_DIR = os.path.dirname(os.path.abspath(__file__))
ESTATE = os.path.normpath(os.path.join(VERIFY_DIR, "..", ".estate-clone"))
