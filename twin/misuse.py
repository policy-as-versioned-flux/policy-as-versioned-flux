"""The misuse catalogue and constraint-removal logging (build ticket 62), from decision ticket 15's
carried-forward item: "log constraint removals WITH the attractiveness of the forbidden option —
recovers the signal finding #5 says pre-filtering destroys, and lets a principled exclusion be
told from a convenient one."

**The catalogue names mechanisms, not just risks** (`twin/misuse-catalogue.yaml`) — a risk is a
sentence anyone could write; a mechanism is the code a reader can go and check.

**Attractiveness is computed, never stated.** `log_removal()` takes no float parameter for the
figure it records — the only way to produce one is to name the perspective, the option and the
constraint being removed, and let `compute_attractiveness()` re-run `twin/options.py`'s own
pre-filter with that one constraint stripped. There is no code path here through which a caller
could type a number into the log directly, which is what "computed, not stated" means as a
property of the code rather than a habit of whoever calls it.

**Only a perspective's own declared constraint can be removed this way.** The universal floor
(`twin/constraints.yaml`) is not a perspective's to remove — `refuse_floor_override` already
forbids a perspective from even shadowing a floor id — so "removing" one is a governance-document
edit, a different and larger act this module does not cover. Named here as a known limit rather
than silently narrowed.
"""

from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Any

import yaml

from . import PACKAGE_DIR
from . import options as options_mod
from .canon import digest_of

CATALOGUE_PATH = PACKAGE_DIR / "misuse-catalogue.yaml"
REMOVAL_LOG_PATH = PACKAGE_DIR / "removal-log.jsonl"
CATALOGUE_SCHEMA = "twin.misuse-catalogue/v1"


class MisuseError(RuntimeError):
    """The catalogue does not say what it must, or a removal cannot be logged as one."""


@lru_cache(maxsize=8)
def load_catalogue(path: Path | None = None) -> dict[str, Any]:
    """The versioned misuse catalogue, validated on read — the same discipline the constraint set
    and the evidence ladder apply: a catalogue that has quietly lost a mechanism still looks named."""
    source = path or CATALOGUE_PATH
    doc = yaml.safe_load(source.read_text(encoding="utf-8"))
    if not isinstance(doc, dict) or doc.get("schema") != CATALOGUE_SCHEMA:
        raise MisuseError(f"{source}: not a {CATALOGUE_SCHEMA} document")
    entries = doc.get("entries")
    if not isinstance(entries, list) or not entries:
        raise MisuseError(f"{source}: names no misuse entry")
    ids = set()
    for entry in entries:
        eid = str(entry.get("id", ""))
        if not eid:
            raise MisuseError(f"{source}: an entry declares no id")
        if eid in ids:
            raise MisuseError(f"{source}: entry {eid!r} declared twice")
        ids.add(eid)
        if not str(entry.get("risk", "")).strip():
            raise MisuseError(f"{source}: entry {eid!r} names no risk")
        if not str(entry.get("mechanism", "")).strip():
            raise MisuseError(
                f"{source}: entry {eid!r} names no mechanism — a risk with no mechanism is a "
                "concern, not a catalogue entry"
            )
    return doc


def pin(path: Path | None = None) -> dict[str, Any]:
    doc = load_catalogue(path)
    return {"version": int(doc["version"]), "digest": digest_of(doc)}


# -- constraint-removal logging --------------------------------------------------------------


def compute_attractiveness(
    perspective: dict[str, Any], responses: dict[str, dict[str, Any]], option_id: str, constraint_id: str,
) -> dict[str, Any]:
    """What `option_id` would cost this perspective if `constraint_id` no longer excluded it.

    Re-runs `options.prefilter()` against a copy of `perspective` with `constraint_id` stripped
    from its own `forbidden`/`ruin` declarations — never against a hand-built constraint set — so
    the figure is derived from the same machinery `twin options` uses, not a second implementation
    of pricing that could quietly disagree with it.
    """
    option = responses.get(option_id)
    if option is None:
        raise MisuseError(f"no response {option_id!r} among the named responses")
    crosses = {str(k) for k in (option.get("crosses") or {})}
    if constraint_id not in crosses:
        raise MisuseError(
            f"{option_id!r} does not cross {constraint_id!r}; removing it would change nothing "
            "this option needed, so there is no attractiveness to compute here"
        )
    declared = {str(k) for k in (perspective.get("forbidden") or {})} | {
        str(k) for k in (perspective.get("ruin") or {})
    }
    if constraint_id not in declared:
        raise MisuseError(
            f"perspective {perspective.get('id')!r} does not declare {constraint_id!r} itself — "
            "only a perspective's own declared constraint can be removed this way; the universal "
            "floor is not a perspective's to remove"
        )
    stripped = {
        **perspective,
        "forbidden": {k: v for k, v in (perspective.get("forbidden") or {}).items() if k != constraint_id},
        "ruin": {k: v for k, v in (perspective.get("ruin") or {}).items() if k != constraint_id},
    }
    admitted = options_mod.prefilter(stripped, responses)
    priced = admitted.priced()
    entry = next((p for p in priced["priced"] if p["option"] == option_id), None)
    if entry is None:
        raise MisuseError(
            f"{option_id!r} is still excluded once {constraint_id!r} is removed — another "
            "constraint also excludes it, so this removal alone buys nothing to record"
        )
    return entry["cost"]


def log_removal(
    perspective: dict[str, Any], responses: dict[str, dict[str, Any]], option_id: str, constraint_id: str,
    removed_by_role: str, reason: str, removed_on: str, path: Path | None = None,
) -> dict[str, Any]:
    """Append one removal to the log. Computing the attractiveness happens here, unconditionally
    — there is no parameter through which a caller could skip it and supply a number instead."""
    if not reason.strip():
        raise MisuseError("a removal with no reason is not a record, it is a deletion")
    attractiveness = compute_attractiveness(perspective, responses, option_id, constraint_id)
    entry = {
        "perspective": str(perspective["id"]),
        "constraint_id": constraint_id,
        "option": option_id,
        "attractiveness": attractiveness,
        "removed_by_role": removed_by_role,
        "removed_on": removed_on,
        "reason": reason.strip(),
    }
    target = path or REMOVAL_LOG_PATH
    target.parent.mkdir(parents=True, exist_ok=True)
    with target.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(entry, sort_keys=True) + "\n")
    return entry


def load_removal_log(path: Path | None = None) -> list[dict[str, Any]]:
    """Every logged removal, oldest first. A missing log is empty, never an error — the ordinary
    state before any constraint has ever been removed."""
    source = path or REMOVAL_LOG_PATH
    if not source.is_file():
        return []
    out = []
    for number, line in enumerate(source.read_text(encoding="utf-8").splitlines(), start=1):
        if not line.strip():
            continue
        try:
            doc = json.loads(line)
        except json.JSONDecodeError:
            raise MisuseError(f"{source}:{number}: not a JSON object") from None
        missing = [f for f in ("perspective", "constraint_id", "option", "attractiveness") if f not in doc]
        if missing:
            raise MisuseError(f"{source}:{number}: a removal entry declares no {', '.join(missing)}")
        out.append(doc)
    return out


def removed_ids(before: dict[str, Any], after: dict[str, Any]) -> set[str]:
    """Which of a perspective's own declared constraint ids existed before and not after."""
    was = {str(k) for k in (before.get("forbidden") or {})} | {str(k) for k in (before.get("ruin") or {})}
    now = {str(k) for k in (after.get("forbidden") or {})} | {str(k) for k in (after.get("ruin") or {})}
    return was - now


def verify_removals(
    before: dict[str, Any], after: dict[str, Any], log_entries: list[dict[str, Any]],
) -> list[str]:
    """Every id `removed_ids` finds must have a matching removal-log entry for this perspective.

    A removal with no attractiveness record is rejected: this is where that rejection actually
    happens, returning what is missing rather than raising, so a caller comparing many perspectives
    can collect every violation at once instead of stopping at the first.
    """
    perspective_id = str(after.get("id") or before.get("id") or "")
    logged = {
        (str(e["perspective"]), str(e["constraint_id"])) for e in log_entries
    }
    missing = sorted(
        constraint_id
        for constraint_id in removed_ids(before, after)
        if (perspective_id, constraint_id) not in logged
    )
    return [
        f"perspective {perspective_id!r} no longer declares {constraint_id!r}, and no removal-log "
        "entry with a computed attractiveness records it"
        for constraint_id in missing
    ]
