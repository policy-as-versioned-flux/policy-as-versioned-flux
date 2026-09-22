#!/usr/bin/env python3
"""Load Laya at a pinned revision digest, run it on CPU with the network closed, and time it.

Map ticket 02 (.scratch/laya-loophole/issues/02-laya-runs-offline-pinned-and-measured-here.md).

WHY THIS EXISTS. Every quality and speed number this estate holds on Laya is Convai measuring
Convai (map ticket 01). The map's standing rule is "derive what you assert", so before ticket 04
grades the model against the six heuristics, the model has to run here, at a digest that cannot
move, on this hardware, and report its own latency. This script is that measurement and nothing
else. It grades no answer and it adopts nothing.

TWO SUBCOMMANDS, AND WHY THEY ARE SEPARATE.

  fetch   The only step allowed to touch the network. It pins `convaiinnovations/laya` by the
          40-character commit digest, downloads ONLY the English 421M checkpoint, verifies
          `model.safetensors` against the SHA-256 ticket 02 item 6 names, and records the full
          file listing at that revision so a later reader can see for themselves that the
          repository ships no LICENSE file (item 9).

  measure Runs with every outbound socket blocked by `_close_the_network()`, so "offline" is
          enforced rather than claimed. It re-verifies the digest of every pinned file, loads the
          model on CPU, and times `system_one`.

WHY THE PIN IS DONE HERE AND NOT BY THE VENDOR'S PACKAGE. `laya.Agent.__init__` (0.3.4,
`laya/agent.py:122-128`) calls `snapshot_download(model_id_or_path, **kw)` and passes NO
`revision`. The package can only ever fetch whatever `main` points at. Ticket 01 measured that
`main` moved ten times in two days on a repository three days old, so the vendor's own entry
point cannot satisfy this ticket. `Agent` does accept a local directory, so this script pins the
download itself and hands `Agent` a path. That is the whole reason for the split.

WHAT "THE SAME ANSWERS" MEANS (item 5). The script writes `answers_sha256`, a digest over the
canonical JSON of the model's output for the fixed input. Two separate processes at the same
weights digest must print the same `answers_sha256`. Comparing a hash rather than eyeballing
probabilities is the point: a silent one-bit drift in a probability fails the comparison.

WHAT THIS DOES NOT DO. It does not use the ONNX path. Ticket 02 item 8 requires that anything
going through ONNX measures its own parity against PyTorch here, because the vendor's parity
claim is prose over random token ids. This script takes the PyTorch checkpoint, which is Convai's
own artefact, so no parity question arises. If ticket 04 or ticket 09 later wants ONNX, the
parity measurement is a new ticket, not a line in this one.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import platform
import socket
import statistics
import sys
import time
from pathlib import Path

# ---------------------------------------------------------------------------
# The pin. Nothing in this file may take a tag, a branch or `main`.
# ---------------------------------------------------------------------------

REPO_ID = "convaiinnovations/laya"

# Ticket 02 item 6. This is a commit digest, not a tag.
REVISION = "1c5edc17a7acd8701df6fc341c0d179f1c62c982"

# Ticket 02 item 6. The SHA-256 of the English 421M weights at that revision. `fetch` verifies it
# against the Hub's own LFS record AND against the bytes on disk; `measure` re-verifies the bytes.
EXPECTED_WEIGHTS_SHA256 = "891102d372688fc2a094dac56a384bc537b87c63f21f9f3dac0be2b7cbc8d86c"

# Ticket 02 item 7: the English checkpoint, not the multilingual one. The repository bundles three
# checkpoints in one tree, so an unfiltered download would pull 1.5 GB of weights this map has
# ruled out of scope. `multilingual/` and `typed-decisions/` are deliberately absent from this list.
ENGLISH_CHECKPOINT_PATTERNS = [
    "rl_agent_config.json",
    "model.safetensors",
    "encoder/config.json",
    "tokenizer/tokenizer.json",
    "tokenizer/tokenizer_config.json",
]

# CPU only (item 2). `laya.Agent` otherwise picks MPS on this hardware, which would measure a GPU.
DEVICE = "cpu"

# Fixed so the number is reproducible on a machine with a different core count. Recorded in the
# output, because a latency without its thread count is not a measurement. `--threads` overrides
# it: the headline number must not be an artefact of one arbitrary choice, so ticket 02 swept this
# and recorded the sweep before quoting a p50.
TORCH_THREADS = 4

WARMUP_PASSES = 10
TIMED_PASSES = 120  # item 3 asks for at least 100


# ---------------------------------------------------------------------------
# The fixed input (item 3, item 5).
# ---------------------------------------------------------------------------
#
# A twin-shaped decision, not a toy. The state is a version bump on a pinned policy and the three
# questions are one of each type Laya answers (`choice`, `score`, `noul`), because the head path
# and the temperature bucket differ per type and a single-type input would time only one of them.
# The text is frozen: changing it invalidates every recorded latency and every `answers_sha256`.

FIXED_STATE = (
    "Adopter repository policy-as-versioned-flux-driftwood proposes moving its pinned "
    "kyverno policy bundle from version 1.4.2 to 1.5.0. The bundle adds one new deny rule "
    "covering unpinned container image tags. Three of the adopter's nine edges reference the "
    "bundle. The compose-check gate is green on the proposal branch. No human has reviewed it."
)

FIXED_QUESTIONS = {
    "route": {
        "type": "choice",
        "instructions": "Which reviewer should this change be routed to?",
        "criteria": {
            "platform-owner": "changes the policy bundle every adopter pins",
            "adopter-owner": "changes only this adopter's own configuration",
            "no-review-needed": "a mechanical bump with no behaviour change",
        },
    },
    "risk": {
        "type": "score",
        "instructions": "How much blast radius does this change carry?",
        "criteria": ["none", "one repository", "several repositories", "the whole estate"],
    },
    "needs_human": {
        "type": "noul",
        "instructions": "Does this change need a human judgement before it merges?",
    },
}

# Two more, to make a FIVE-question call. Five is not an arbitrary number: the only CPU latency
# artefact Convai publishes for this checkpoint is `ms_per_case` over 400 cases of 5 questions,
# on `cpu`, at `threads: 4`
# (https://github.com/NandhaKishorM/laya/blob/main/research/results/cpu_51_language_sweep.json,
# `part_b.by_model.english`: n=2000 decisions, 557.0 s, 1392.5 ms per case). Timing the same shape
# on the same device at the same thread count is the only way this ticket can put a measured
# number beside a published one instead of beside a marketing range.
FIXED_QUESTIONS_FIVE = dict(FIXED_QUESTIONS)
FIXED_QUESTIONS_FIVE.update(
    {
        "reversible": {
            "type": "choice",
            "instructions": "How hard is this change to reverse once it is merged?",
            "criteria": {
                "one-revert": "a single revert commit undoes it",
                "coordinated": "every adopter must be bumped back together",
                "irreversible": "it changes state outside version control",
            },
        },
        "gate_trusted": {
            "type": "noul",
            "instructions": "Is a green compose-check gate sufficient evidence on its own here?",
        },
    }
)


# ---------------------------------------------------------------------------
# Offline enforcement
# ---------------------------------------------------------------------------


class NetworkWasUsed(RuntimeError):
    """Raised if anything opens a socket during the measured run."""


def _close_the_network() -> None:
    """Block every outbound connection, so item 2 is enforced and not merely configured.

    `HF_HUB_OFFLINE=1` alone is a request to one library. This replaces `socket.socket.connect`,
    so ANY library that reaches out fails loudly instead of quietly re-fetching `main`.
    """
    os.environ["HF_HUB_OFFLINE"] = "1"
    os.environ["TRANSFORMERS_OFFLINE"] = "1"
    os.environ["HF_HUB_DISABLE_TELEMETRY"] = "1"

    def _refuse(self, *args, **kwargs):  # noqa: ANN001, ANN002, ANN003
        raise NetworkWasUsed(
            "the measured run opened a socket to %r; ticket 02 item 2 requires no network "
            "access at inference time" % (args[0] if args else "?",)
        )

    socket.socket.connect = _refuse  # type: ignore[method-assign]
    socket.socket.connect_ex = _refuse  # type: ignore[method-assign]
    socket.create_connection = _refuse  # type: ignore[assignment]


# ---------------------------------------------------------------------------
# Digests
# ---------------------------------------------------------------------------


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def digest_tree(root: Path) -> dict[str, str]:
    """SHA-256 of every pinned file, keyed by its path inside the snapshot.

    Re-taken by `measure`, because `laya.Agent._fix_tokenizer_config` (`laya/agent.py:21`) WRITES
    to `tokenizer/tokenizer_config.json` when it dislikes the `tokenizer_class` field. A
    `snapshot_download` file is a symlink into the shared blob store, so that write would corrupt
    the pinned blob for every other consumer on this machine. The digests below are taken before
    and after the load so the report can state whether it happened rather than assume it did not.
    """
    out = {}
    for name in ENGLISH_CHECKPOINT_PATTERNS:
        p = root / name
        if p.exists():
            out[name] = sha256_file(p)
    return out


def canonical_sha256(obj) -> str:
    return hashlib.sha256(
        json.dumps(obj, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


# ---------------------------------------------------------------------------
# fetch
# ---------------------------------------------------------------------------


def cmd_fetch(args) -> int:
    from huggingface_hub import HfApi, snapshot_download

    api = HfApi()

    # The full listing at the pinned revision. Ticket 02 item 9 asks this script to RECORD that
    # the weights repository ships no LICENSE file, so the listing is derived from the Hub at the
    # pin rather than copied out of ticket 01's prose.
    info = api.model_info(REPO_ID, revision=REVISION, files_metadata=True)
    if info.sha != REVISION:
        print("FAIL: the Hub resolved %s to %s, not the pin" % (REVISION, info.sha), file=sys.stderr)
        return 1

    listing = []
    hub_weights_sha = None
    for s in info.siblings:
        lfs_sha = getattr(s, "lfs", None)
        lfs_sha = getattr(lfs_sha, "sha256", None) if lfs_sha else None
        listing.append({"path": s.rfilename, "size": s.size, "lfs_sha256": lfs_sha})
        if s.rfilename == "model.safetensors":
            hub_weights_sha = lfs_sha

    license_files = [e["path"] for e in listing if e["path"].upper().startswith("LICENSE")]

    if hub_weights_sha != EXPECTED_WEIGHTS_SHA256:
        print(
            "FAIL: the Hub records model.safetensors as %s, ticket 02 item 6 expects %s"
            % (hub_weights_sha, EXPECTED_WEIGHTS_SHA256),
            file=sys.stderr,
        )
        return 1

    local = snapshot_download(
        REPO_ID,
        revision=REVISION,
        allow_patterns=ENGLISH_CHECKPOINT_PATTERNS,
        local_dir=args.model_dir,
    )
    root = Path(local)

    on_disk = sha256_file(root / "model.safetensors")
    if on_disk != EXPECTED_WEIGHTS_SHA256:
        print("FAIL: bytes on disk digest to %s, not the pin" % on_disk, file=sys.stderr)
        return 1

    record = {
        "repo_id": REPO_ID,
        "revision": REVISION,
        "revision_confirmed_by_hub": info.sha,
        "last_modified": str(info.last_modified),
        "weights_sha256_hub": hub_weights_sha,
        "weights_sha256_on_disk": on_disk,
        "weights_sha256_expected": EXPECTED_WEIGHTS_SHA256,
        "license_files_at_revision": license_files,
        "license_declared_in_card_yaml": (info.card_data or {}).get("license"),
        "files_at_revision": listing,
        "downloaded": sorted(digest_tree(root)),
        "model_dir": str(root),
    }
    Path(args.out).write_text(json.dumps(record, indent=2) + "\n")

    print("pin        %s@%s" % (REPO_ID, REVISION))
    print("weights    sha256 %s  (matches the pin)" % on_disk)
    print("licence    LICENSE files at this revision: %s" % (license_files or "NONE"))
    print("           model card YAML declares: %s" % record["license_declared_in_card_yaml"])
    print("model_dir  %s" % root)
    print("wrote      %s" % args.out)
    return 0


# ---------------------------------------------------------------------------
# measure
# ---------------------------------------------------------------------------


def cmd_measure(args) -> int:
    _close_the_network()

    root = Path(args.model_dir)
    before = digest_tree(root)
    if before.get("model.safetensors") != EXPECTED_WEIGHTS_SHA256:
        print(
            "FAIL: %s digests to %s, ticket 02 item 6 pins %s. Run `fetch` first."
            % (root / "model.safetensors", before.get("model.safetensors"), EXPECTED_WEIGHTS_SHA256),
            file=sys.stderr,
        )
        return 1

    import torch
    from laya import Agent

    threads = args.threads
    torch.set_num_threads(threads)
    torch.use_deterministic_algorithms(True)

    load_start = time.perf_counter()
    agent = Agent(str(root), device=DEVICE)
    load_seconds = time.perf_counter() - load_start

    if str(agent.device) != DEVICE:
        print("FAIL: agent placed on %s, not %s" % (agent.device, DEVICE), file=sys.stderr)
        return 1

    after = digest_tree(root)
    mutated = sorted(k for k in before if before[k] != after.get(k))

    # One question per call is the shape the vendor's 39.5 ms describes, so it is the comparable
    # number. The three-question call is the shape this estate would actually run, so both are
    # timed and both are reported. Reporting only one of them would let a reader compare the wrong
    # pair of numbers.
    shapes = {
        "one_question": {"route": FIXED_QUESTIONS["route"]},
        "three_questions": FIXED_QUESTIONS,
        "five_questions": FIXED_QUESTIONS_FIVE,
    }

    results = {}
    answers = {}
    for shape_name, questions in shapes.items():
        for _ in range(WARMUP_PASSES):
            out = agent.system_one(FIXED_STATE, questions)
        answers[shape_name] = out

        samples = []
        for _ in range(TIMED_PASSES):
            t0 = time.perf_counter()
            agent.system_one(FIXED_STATE, questions)
            samples.append((time.perf_counter() - t0) * 1000.0)

        samples.sort()
        results[shape_name] = {
            "passes": len(samples),
            "p50_ms": round(statistics.median(samples), 2),
            "p95_ms": round(samples[int(0.95 * (len(samples) - 1))], 2),
            "p99_ms": round(samples[int(0.99 * (len(samples) - 1))], 2),
            "min_ms": round(samples[0], 2),
            "max_ms": round(samples[-1], 2),
            "mean_ms": round(statistics.fmean(samples), 2),
            "stdev_ms": round(statistics.stdev(samples), 2),
        }

    record = {
        "ticket": "02",
        "repo_id": REPO_ID,
        "revision": REVISION,
        "weights_sha256": before["model.safetensors"],
        "file_digests_before_load": before,
        "file_digests_after_load": after,
        "files_mutated_by_load": mutated,
        "network": "blocked at socket.connect for the whole measured run",
        "device": str(agent.device),
        "dtype": str(agent.dtype),
        "torch_threads": threads,
        "load_seconds": round(load_seconds, 2),
        "host": {
            "platform": platform.platform(),
            "machine": platform.machine(),
            "processor": platform.processor() or platform.machine(),
            "python": platform.python_version(),
            "torch": torch.__version__,
        },
        "latency": results,
        "answers": answers,
        "answers_sha256": canonical_sha256(answers),
        "measured_at": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
    }
    Path(args.out).write_text(json.dumps(record, indent=2) + "\n")

    print("pin           %s@%s" % (REPO_ID, REVISION))
    print("weights       sha256 %s" % before["model.safetensors"])
    print("mutated       %s" % (mutated or "nothing; the pinned blobs are untouched"))
    print("device        %s  dtype %s  threads %d" % (agent.device, agent.dtype, threads))
    print("host          %s %s" % (platform.platform(), platform.machine()))
    print("load          %.2f s" % load_seconds)
    for name, r in results.items():
        print(
            "%-15s p50 %6.2f ms   p95 %6.2f ms   p99 %6.2f ms   (n=%d, min %.2f, max %.2f)"
            % (name, r["p50_ms"], r["p95_ms"], r["p99_ms"], r["passes"], r["min_ms"], r["max_ms"])
        )
    print("answers_sha256 %s" % record["answers_sha256"])
    print("wrote         %s" % args.out)
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    sub = ap.add_subparsers(dest="cmd", required=True)

    default_dir = os.environ.get(
        "LAYA_MODEL_DIR", str(Path.home() / ".cache" / "laya-bench" / "laya-english-1c5edc17")
    )
    here = Path(__file__).parent

    f = sub.add_parser("fetch", help="pin and download the English checkpoint (needs the network)")
    f.add_argument("--model-dir", default=default_dir)
    f.add_argument("--out", default=str(here / "pin.json"))
    f.set_defaults(func=cmd_fetch)

    m = sub.add_parser("measure", help="load on CPU with the network blocked and time it")
    m.add_argument("--model-dir", default=default_dir)
    m.add_argument("--out", default=str(here / "measured.json"))
    m.add_argument("--threads", type=int, default=TORCH_THREADS)
    m.set_defaults(func=cmd_measure)

    args = ap.parse_args()
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
