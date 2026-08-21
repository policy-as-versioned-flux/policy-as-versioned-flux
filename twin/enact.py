"""The enactment arm: the twin proposes, in two layers, and disposes in none (build ticket 66).

**Propose only is derived here, not inherited.** The prior estate asserted "propose, never
dispose"; decision ticket 18 Q1 re-derived it from three independent places, and any one of them
would be enough on its own:

1. **Article 22** admits no solely-automated significant decision. Law, not preference.
2. **The output is a trade-off curve with a marked default**, so there is nothing to auto-execute —
   choosing a point on the curve is inherently the human's act, and that is the design.
3. **An agent signature asserts reproducible origin, never endorsement** (`twin/sign.py`), so an
   agent-initiated change has nobody accountable behind it.

Graduated autonomy — auto-apply the cheap reversible things — was rejected for a reason worth
keeping in view: cheapness is computed by the twin's own £ model, which is model-relative and
explicitly never authoritative, so the twin would be deciding its own leash length.

## The two layers, and how each one fails

**Layer 1, here: a structural absence.** This module exposes `propose` and nothing that merges,
and `enactment_is_propose_only_at_both_layers` asserts its public surface against an allow-list
rather than screening for merge-shaped names — a free function called `land` or `ship` reopens the
question whatever it is called. *It fails under composition:* this is a property of `twin/` as it
is today, and the day the twin gains a shell tool, an MCP GitHub server or a subagent with `gh`,
the absence still holds and the guarantee is gone with no diff to this file. The constitution says
code is disposable by default, so an absence has a scheduled expiry.

**Layer 2, `twin/enact_guard.py`: a constraint at the tool-call boundary.** It survives
composition, because each of those paths ends in a tool call. *It fails by being forgotten:* a
policy check is a call site, and a call site can be deleted from `.claude/settings.json` or simply
not exist in whatever runner is driving the twin today.

Neither is redundant, because they fail in opposite directions. An absence has no call site to
forget; a boundary check has no dependency on what the code happens to contain. The harness check
asserts both, including that layer 2's registration is still there.

## Policy as a signed, pinned dependency — and the narrowing that matters

Decision ticket 18 Q2 tested the prior estate's central thesis against the risk basis and it
**survives narrowed**, into two roles and no third:

1. the **enactment channel** for the subset of controls that are machine-enforceable, and
2. the **verification substrate** for the ones that are not — a pay rise carries a versioned,
   signed record that it was enacted without being enforced by policy.

What does *not* survive is the claim that versioned policy is how governance works. Responses are
priced by the FAIR factor they modify and **most levers are not code** — a pay rise, a JIT access
change, a supplier switch, a strategic play. If versioned policy were the shape of governance, the
cross-domain comparison that is the entire point of the £ engine could not exist. That is why
`--channel` is required with no default: the two roles are different claims, and a proposal that
did not have to say which one it was making would default to the flattering one.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

import yaml

from . import REPO_DIR, TOOL_VERSION
from .artefact import DERIVED, Artefact
from .canon import digest_of
from .constraints import floor_ids
from .grades import Capabilities
from .model import Overlay
from .repo import ModelRepo
from .sign import AGENT, AGENT_ASSERTS_NOTHING_ABOUT, ASSERTS

KIND = "enactment-proposal"
CAPABILITY = "enactment"

# The two roles decision ticket 18 Q2 narrowed policy-as-versioned-dependency down to. Required
# with no default, for the same reason the information regime is (build ticket 36): a parameter
# that can be omitted is a default in everything but name.
POLICY, RECORD = "policy", "record"
CHANNELS = {
    POLICY: (
        "the enactment channel — a machine-enforceable control, shipped as a signed pinned policy "
        "version, where the dependency is what makes 'this control is actually running' verifiable "
        "rather than asserted"
    ),
    RECORD: (
        "the verification substrate — a lever that is not code, carrying a versioned signed record "
        "that it was enacted without being enforced by policy. Most levers are this one, and the £ "
        "engine's cross-domain comparison depends on it"
    ),
}

# Stated in the artefact rather than only in this docstring: a proposal that is silent about how
# its own guarantee fails will be read as not having one.
LAYERS: tuple[dict[str, str], ...] = (
    {
        "layer": "structural absence",
        "where": "twin/enact.py",
        "holds": "no merge code path exists; the module's public surface is an allow-list",
        "fails_when": (
            "the twin is composed with a shell tool, an MCP GitHub server or a subagent with `gh` "
            "— the absence still holds and the guarantee is gone, with no diff to twin/ at all"
        ),
        "cannot_fail_by": "being forgotten — an absence has no call site to forget",
    },
    {
        "layer": "tool-call boundary",
        "where": "twin/enact_guard.py, registered as a PreToolUse hook",
        "holds": "a disposing tool call is refused before it runs, including a subagent's own",
        "fails_when": (
            "the registration is deleted, or the twin is driven by a runner that does not honour "
            "hooks — a policy check is a call site, and a forgotten call site fails open in silence"
        ),
        "cannot_fail_by": "composition — every added capability still ends in a tool call",
    },
)

NARROWED_CLAIM = (
    "Policy-as-code is AN enactment arm, not THE definition of governance. Responses are priced by "
    "the FAIR factor they modify and most levers are not code, so if versioned policy were the "
    "shape of governance the cross-domain comparison the £ engine exists for could not exist."
)

# Where the real pins live. Read rather than described: 'consumed by real separate repositories' is
# a claim about files that either exist or do not.
# mo-12 deleted the hub's committed estate/ tree; the six units are real repos now (mo-08), fetched
# into .estate-clone/ by clone-estate.sh (git-ignored, disposable). Same repoint already applied to
# verify/party/party.py, verify/proportionality/render.py, verify/provenance/provenance.py.
ESTATE_DIR = REPO_DIR / ".estate-clone"
_GIT_REPOSITORY = "source.toolkit.fluxcd.io"
# A commit line that is present but commented out is the shape every pin in this estate currently
# has, and it is the difference between an immutable pin and a movable one.
_COMMENTED_COMMIT = re.compile(r"^\s*#\s*commit:", re.M)


class EnactError(RuntimeError):
    """A proposal that names no response, or names a channel that is not one of the two roles."""


def dependency_pins(estate_dir: Path | None = None) -> list[dict[str, Any]]:
    """Every signed, version-pinned dependency the estate's repositories actually consume.

    Read out of the committed Flux sources rather than asserted, and reported with the property
    that decides how much the pin is worth: a **tag** pin is not immutable, because a tag can be
    moved. Every pin in this estate carries its commit line commented out as a placeholder, so
    `commit_pinned` is false everywhere and says so rather than letting "pinned" carry a weight
    the files do not support.
    """
    root = estate_dir or ESTATE_DIR
    pins: list[dict[str, Any]] = []
    for path in sorted(root.glob("*/gitops/**/*.yaml")):
        text = path.read_text(encoding="utf-8")
        if _GIT_REPOSITORY not in text:
            continue
        for doc in yaml.safe_load_all(text):
            if not isinstance(doc, dict) or doc.get("kind") != "GitRepository":
                continue
            ref = doc.get("spec", {}).get("ref", {}) or {}
            consumer = path.relative_to(root).parts[0]
            dependency = str(doc.get("metadata", {}).get("name", ""))
            pins.append({
                "consumer": consumer,
                "dependency": dependency,
                # A repository syncing itself is not consuming anybody's policy, and counting the
                # two together would inflate the only number this claim rests on.
                "cross_repository": dependency != consumer,
                "url": str(doc.get("spec", {}).get("url", "")),
                "tag": str(ref.get("tag", "")) or None,
                "commit_pinned": bool(ref.get("commit")),
                "source": path.relative_to(REPO_DIR).as_posix(),
            })
    return pins


def _dependency_block(pins: list[dict[str, Any]], org: str) -> dict[str, Any]:
    consumed = [p for p in pins if p["cross_repository"]]
    unpinned = [p for p in pins if not p["commit_pinned"]]
    return {
        "pins": pins,
        "consumer_repositories": sorted({p["consumer"] for p in consumed}),
        "dependencies": sorted({p["dependency"] for p in consumed}),
        "cross_repository_pins": len(consumed),
        "self_sync_pins": len(pins) - len(consumed),
        # Deliberately not a `signing` field stating how the tags are signed. That reads as this
        # code having checked, and it has not: the claim is the sources' own, repeated here with
        # its status attached rather than laundered into the asserted half of the artefact.
        "signing_declared_by_the_sources": (
            "the consumed tags are gitsign-keyless (OIDC -> Fulcio -> Rekor), verified out-of-band "
            "by `git verify-tag` / Rekor lookup, because Flux's GitRepository.spec.verify speaks "
            "only OpenPGP and the sources refuse to fake a PGP block. NOT VERIFIED HERE — see limits."
        ),
        "limits": [
            (
                f"{len(unpinned)} of {len(pins)} pins name a tag and no commit, so the pin is only "
                "as immutable as the tag. Every commit line in this estate is a commented-out "
                "placeholder; until one is filled in, 'pinned' means 'pinned to a movable name'."
            ),
            (
                f"{len(pins) - len(consumed)} of {len(pins)} pins are a repository syncing itself "
                "rather than consuming anybody's policy, and are counted separately: only the "
                f"{len(consumed)} cross-repository pins evidence a dependency at all."
            ),
            (
                "the signature is the sources' own declaration, checked by nothing here: no tag is "
                "verified, no Rekor entry is looked up, and estate/verify/provenance/"
                "verify-provenance.sh records that this repository's own commits are not "
                "keyless-signed either. 'Signed' is therefore a property of the design, not an "
                "observation, and the word does no work until something verifies it."
            ),
            (
                "the consumer repositories are separate by URL and not yet by existence: "
                "estate/README.md describes a monorepo-style working tree whose top-level "
                "directories become their own GitHub repositories *at split*, and each up.sh "
                "rewrites the pinned URL to an in-cluster git server for the offline demo. The "
                "pins name real separate repositories; whether those repositories are live is a "
                "question this code does not ask."
            ),
            (
                "read from committed sources, not from a running cluster: this evidences what the "
                "repositories declare they consume, never that a control is in force right now. "
                "Whether continuous proof of force is required at all is build ticket 65's "
                "question and is still open."
            ),
            (
                f"these pins are read from this tool's own repository ({ESTATE_DIR.relative_to(REPO_DIR).as_posix()}), "
                f"not from any repository {org!r} owns. The dependency block above evidences "
                "what THIS estate consumes; it names no pin, tag or repository belonging to the "
                f"subject the proposal is about, and {org!r} is not assumed to have an estate "
                "under Flux at all."
            ),
        ],
    }


def propose(
    repo: ModelRepo,
    caps: Capabilities,
    org: str,
    response_id: str,
    channel: str,
    command: list[str],
) -> Artefact:
    """A proposal to enact one response, through one of the two narrowed channels.

    **Derived, deliberately.** The twin produced it, so it carries an agent signature asserting
    reproducible origin — and `derived_never_human_signed` then refuses a human signature on it.
    That is the whole of "no proposal carries implied endorsement", made structural rather than
    stated: there is no field a human could sign into, and an artefact with human fingerprints on
    it becomes a detectable anomaly rather than a convention breach.
    """
    if channel not in CHANNELS:
        raise EnactError(
            f"channel {channel!r} is not one of {', '.join(sorted(CHANNELS))}. Decision ticket 18 "
            "Q2 narrowed policy-as-versioned-dependency to exactly two roles, and a proposal that "
            "did not have to name which one it was making would default to the flattering one."
        )

    overlay = Overlay.load(repo, org)
    response = overlay.responses.get(response_id)
    if response is None:
        known = ", ".join(sorted(overlay.responses)) or "none"
        raise EnactError(f"no response {response_id!r} in overlay {org!r} (have: {known})")

    # The universal floor, checked here rather than trusted to have been checked upstream. This
    # verb has no `--perspective`, so a perspective's own declared red lines are out of scope for
    # it — but the floor binds every perspective identically (`twin/constraints.yaml`'s own
    # words), so a response crossing a floor id is refused regardless of which eye is asking. This
    # is a real gap the beat's own review found: `twin options`/`twin price` run this response
    # through the pre-filter and never see it again, so nothing stopped `twin propose` reading the
    # overlay directly and pricing a response the choice set had already removed.
    crossed = sorted(set(response.get("crosses") or {}) & floor_ids())
    if crossed:
        raise EnactError(
            f"{response_id!r} crosses the universal floor ({', '.join(crossed)}) and is refused "
            "before pricing by `twin options`/`twin price`; a proposal is not a second door "
            "past the constraint pre-filter. A perspective's own declared red lines are not "
            "checked here — this verb carries no perspective — and that is a stated limit, not "
            "a clearance."
        )

    pins = dependency_pins()
    return Artefact(
        kind=KIND,
        mark=DERIVED,
        command=command,
        pins={
            "model_repo": repo.pin.as_dict(),
            "overlay": overlay.ref.as_dict(),
            "world": overlay.world.ref.as_dict(),
            "org": overlay.org,
            "tool": {"name": "twin", "version": TOOL_VERSION, "capabilities_digest": caps.digest},
            # The enactment sources live outside the model repository, so they are pinned by
            # content: an artefact claiming a set of real pins has to say which ones it read.
            "enactment_sources": digest_of(pins),
        },
        depth=caps.depth_block([CAPABILITY]),
        body={
            "response": {
                "id": response_id,
                "name": str(response.get("name", "")),
                "addresses": str(response.get("addresses", "")),
                "cost": response.get("cost"),
                "mitigates": response.get("mitigates"),
            },
            "channel": {"role": channel, "means": CHANNELS[channel]},
            "dependency": _dependency_block(pins, org),
            "disposition": {
                "state": "proposed",
                "proposed_by": "the twin, as an agent",
                "disposed_by": "a human, out of band — this tool has no path to it",
                "why": (
                    "Article 22 admits no solely-automated significant decision; a trade-off curve "
                    "has nothing to auto-execute, so choosing a point on it is the human's act; and "
                    "an agent signature asserts origin, so an agent-initiated change has nobody "
                    "accountable behind it. Three independent derivations, not an inherited thesis."
                ),
            },
            "layers": [dict(layer) for layer in LAYERS],
            "signature": {
                "agent_asserts": ASSERTS[AGENT],
                "asserts_nothing_about": list(AGENT_ASSERTS_NOTHING_ABOUT),
                "human_signature_refused": (
                    "this artefact is derived, so derived_never_human_signed refuses one — a "
                    "proposal has no slot an endorsement could be written into"
                ),
            },
            "narrowed_claim": NARROWED_CLAIM,
            "acts_freely_on": (
                "its own model — scheduled executions, signal ingestion, inferred positions, its "
                "own contests. That is the carve-out and not an exception: all of it is derived, "
                "machine-signed and reproducible, and none of it changes the world."
            ),
        },
    )
