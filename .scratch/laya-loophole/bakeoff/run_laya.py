#!/usr/bin/env python3
"""Step 2 of the bake-off: run Laya at the pin against the dumped corpora.

Map ticket 04 (.scratch/laya-loophole/issues/04-the-bake-off-laya-against-the-six-heuristics.md).

Run it in ticket 02's own interpreter, never the repository's:

  ~/.cache/laya-bench/venv/bin/python .scratch/laya-loophole/bakeoff/run_laya.py

WHAT THIS FILE IS. A translation layer and nothing else. It turns each corpus item's `input` into
a Laya state and a set of typed questions, calls `Agent.system_one`, and assembles the answer back
into the SAME output shape the heuristic returns, so that `score.py` can hand it to the unmodified
`twin.skills.evaluate()` and the unmodified per-skill `scorer()`. Item 2 of the ticket says change
nothing in the harness; this is how that is kept.

IT NEVER READS `expected` (item: this is an evaluation, not a tautology). `_load()` strips the
`expected` key out of every item before anything else runs, so a rendering that accidentally
leaked a label would fail with a KeyError rather than quietly flatter the model. `twin/skills.py`
`evaluate()` gives `skill_fn` only `input` for exactly the same reason; this file copies it.

THE PIN (item 11). `REVISION`, `EXPECTED_WEIGHTS_SHA256` and the download patterns are imported
from `bench/measure_laya.py`, not restated. `laya.Agent("convaiinnovations/laya")` is never called:
ticket 02 measured that `Agent.__init__` passes no `revision` to `snapshot_download`, so the
vendor's own entry point can only fetch whatever `main` points at. The weights digest is
re-verified here before the model loads, and the run refuses to start if it has moved.

OFFLINE (inherited from ticket 02). `_close_the_network()` replaces `socket.socket.connect` for
the whole run, so "no network at inference time" is enforced rather than configured.

NO SHIPPED TEMPERATURES (item 7, as item 9 collapses it). Ticket 01 found the typed-decisions
checkpoint ships the base checkpoint's `temperature_by_options` map, so its refitted temperatures
are dead code. Ticket 03 found the estate holds one merged human label, against the 326 per skill
a refit needs, so there is nothing to refit on. This file therefore uses the ENGLISH 421M
checkpoint ticket 02 pinned, reports whatever probabilities that checkpoint produces, and fits
nothing. `score.py` labels every calibration number "raw, uncalibrated".

`act_probability` IS RECORDED AND NEVER READ (item 13). Ticket 02 saw it read exactly 1.000000 on
all 16 calls it made. Every value it takes here is written to the output so `score.py` can say
whether it ever varies on a real corpus, which ticket 05 waits on. No decision in this file reads
it.

THE RENDERINGS ARE AUTHORED, AND THAT IS STATED RATHER THAN HIDDEN. Laya takes prose and typed
questions; the heuristics take dicts. Something must translate, and the translation is a choice
this file makes. The rule it follows: render exactly the fields the heuristic itself reads, in the
same words the fixture uses, and never render anything derived from the label. Each `_state_*`
function below names what the matching heuristic reads. A reader who thinks a rendering favours
one side can change it here and re-run; nothing else moves.
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE.parent / "bench"))

from measure_laya import (  # noqa: E402
    DEVICE,
    EXPECTED_WEIGHTS_SHA256,
    REPO_ID,
    REVISION,
    TORCH_THREADS,
    _close_the_network,
    canonical_sha256,
    digest_tree,
    sha256_file,
)

# -- the STEEP tag set, copied from twin/schema.py rather than imported, because this process
#    deliberately cannot import `twin` (see dump_corpora.py's docstring). score.py asserts the
#    two agree.
STEEP = ("social", "technological", "economic", "environmental", "political")

STEEP_CRITERIA = {
    "social": "demographics, culture, public attitudes, workforce behaviour",
    "technological": "a technology, a product capability, an engineering change",
    "economic": "money, trading, demand, costs, financing, accounts, solvency, markets",
    "environmental": "climate, energy use, physical resources, the natural environment",
    "political": "a government, a regulator, a court, a law or an official act of state",
}

# Wardley bands, copied from twin/wardley.py for the same reason. The midpoint of a band is the
# position this file reports when the model names that band; `score.py` asserts the midpoints
# against `twin.wardley.BANDS`.
BANDS = (("genesis", 0.0, 0.25), ("custom-built", 0.25, 0.50), ("product", 0.50, 0.75), ("commodity", 0.75, 1.0))
STAGE_NAMES = [b[0] for b in BANDS]
STAGE_MIDPOINT = {name: round((low + high) / 2, 4) for name, low, high in BANDS}

STAGE_CRITERIA = [
    "genesis: brand new, nobody agrees what it is, built from scratch every time",
    "custom-built: understood but still hand-made for each user, no standard product",
    "product: bought as a product or service, competing suppliers, feature differentiation",
    "commodity: a utility, standardised, bought on price, nobody differentiates on it",
]

# The lag buckets. The days are the heuristic's own marker values (`causal_claims._LAG_MARKERS`
# plus its 180-day default), so neither side is given a scale the other does not have. The claim
# scorer's tolerance is 60 days, so these buckets are further apart than the tolerance except for
# the 30/60 pair, which is the pair the fixture itself distinguishes.
LAG_BUCKETS = ((30, "about a month"), (60, "a few months"), (180, "about six months"), (365, "a year or more"))

# The evidence ladder's five rungs, worded from `twin/evidence-ladder.yaml`'s own rung names, which
# is the same vocabulary `causal_claims._GRADE_MARKERS` matches against.
GRADE_RUNGS = [
    "1: a dated natural experiment, measured before and after an observable change",
    "2: repeated historical co-movement across more than one episode",
    "3: an established mechanism from domain theory or published work",
    "4: calibrated expert judgement, named by role",
    "5: a model assertion with nothing stronger behind it",
]

PLAY_CRITERIA = {
    "land-grab": (
        "the component is deep in the product stage and nearing commodity, and the organisation "
        "already holds an adjacent capability in the value chain next to it"
    ),
    "exploit-commoditisation": (
        "the component has reached the commodity stage and an immature component still depends on "
        "it from the genesis or custom-built stage"
    ),
}
PLAYS = tuple(sorted(PLAY_CRITERIA))


# ---------------------------------------------------------------------------
# Renderings: state text and questions, one pair per skill
# ---------------------------------------------------------------------------
#
# Each function returns `(state, questions)`. `system_one(state, questions)` is one call.


def _signal_classify(item_input: dict) -> tuple[str, dict]:
    """`signal_classify.classify()` reads `statement`, `source` and the candidate list. Nothing
    else is rendered."""
    state = "A signal has been observed.\n\nStatement: %s\n\nSource: %s" % (
        item_input["statement"],
        item_input["source"],
    )
    candidates = item_input["candidates"]
    questions = {
        "steep": {
            "type": "choice",
            "instructions": "Which STEEP category does this signal belong to?",
            "criteria": dict(STEEP_CRITERIA),
        },
        "component": {
            "type": "choice",
            "instructions": "Which part of the business does this signal bear on?",
            "criteria": {c["id"]: c.get("name", c["id"]) for c in candidates},
        },
    }
    return state, questions


def _signal_classify_assemble(answers: dict, item_input: dict) -> dict:
    return {
        "steep": answers["steep"]["choice"],
        "claim": {
            "kind": "binding",
            "component": answers["component"]["choice"],
            "evidence_grade": 5,
            "claimed_by": "laya (candidate model)",
            "evidence": "Laya typed-decision output",
        },
    }


def _evolution_judge(item_input: dict) -> tuple[str, dict]:
    """`evolution_judge.judge()` reads the component's name and every bound evidence statement.
    Both are rendered; the dates come with the statements the way the corpus carries them."""
    lines = "\n".join("- %s: %s" % (e.get("date", "undated"), e["statement"]) for e in item_input["evidence"])
    state = (
        "A component of an organisation's value chain is being placed on the Wardley evolution "
        "axis.\n\nComponent: %s\n\nEvidence accumulated against it:\n%s"
        % (item_input["component"]["name"], lines)
    )
    questions = {
        # The declared primary route, chosen before any result was seen: an ordered `score`
        # question over the four bands, read as the argmax band's midpoint. It is the direct
        # analogue of what the heuristic does, which is pick a position and call `stage_of`.
        "stage": {
            "type": "score",
            "instructions": "How far along the evolution axis has this component travelled?",
            "criteria": list(STAGE_CRITERIA),
        },
        # The declared sensitivity check, recorded and reported beside the primary route, never
        # substituted for it. `noul` returns a bare 0-to-1 number, which is the axis's own shape.
        "position_noul": {
            "type": "noul",
            "instructions": (
                "On a scale where 0 is a brand-new genesis capability and 1 is a bought-on-price "
                "commodity utility, how evolved is this component?"
            ),
        },
    }
    return state, questions


def _evolution_judge_assemble(answers: dict, item_input: dict) -> dict:
    probs = answers["stage"]["probabilities"]
    best_bin = max(probs, key=lambda k: probs[k])
    stage = STAGE_NAMES[int(best_bin)]
    position = STAGE_MIDPOINT[stage]
    return {
        "evolution": stage,
        "evolution_position": position,
        "claim": {
            "kind": "position",
            "component": item_input["component"]["id"],
            "evidence_grade": 5,
            "claimed_by": "laya (candidate model)",
            "evidence": "Laya typed-decision output",
            "evolution_position": position,
        },
        # Carried for the sensitivity table in score.py. Never read by any scorer.
        "_noul_position": answers["position_noul"]["noul"],
    }


def _causal_claims(item_input: dict) -> tuple[str, dict]:
    """`causal_claims.propose()` reads the evidence statements for sign, lag and grade, and the
    caller-supplied confounder list for its alternatives. All are rendered."""
    evidence = "\n".join("- %s" % e["statement"] for e in item_input["evidence"])
    confounders = item_input.get("candidate_confounders") or []
    conf_text = (
        "\n\nComponents adjacent to both ends in the graph: %s"
        % ", ".join(c.get("name", c["id"]) for c in confounders)
        if confounders
        else "\n\nNo component in the graph is adjacent to both ends."
    )
    state = (
        "A causal claim is being proposed between two components of a value chain.\n\n"
        "Cause: %s\n\nEffect: %s\n\nEvidence offered:\n%s%s"
        % (item_input["from"]["name"], item_input["to"]["name"], evidence, conf_text)
    )
    questions = {
        "sign": {
            "type": "choice",
            "instructions": "In which direction does the cause move the effect?",
            "criteria": {
                "positive": "more of the cause produces more of the effect",
                "negative": "more of the cause produces less of the effect",
            },
        },
        "lag": {
            "type": "score",
            "instructions": "How long does the effect take to appear after the cause?",
            "criteria": [label for _, label in LAG_BUCKETS],
        },
        "elasticity": {
            "type": "noul",
            "instructions": (
                "How large is the proportional response? 0 is no response at all and 1 is a "
                "one-for-one proportional response."
            ),
        },
        "grade": {
            "type": "score",
            "instructions": "How strong is the evidence offered for this causal claim?",
            "criteria": list(GRADE_RUNGS),
        },
    }
    return state, questions


def _causal_claims_assemble(answers: dict, item_input: dict) -> dict:
    lag_probs = answers["lag"]["probabilities"]
    lag_days = LAG_BUCKETS[int(max(lag_probs, key=lambda k: lag_probs[k]))][0]
    grade_probs = answers["grade"]["probabilities"]
    grade = int(max(grade_probs, key=lambda k: grade_probs[k])) + 1
    mode = round(float(answers["elasticity"]["noul"]), 4)
    return {
        "edge": {
            "from": item_input["from"]["id"],
            "to": item_input["to"]["id"],
            "type": "influences",
            "sign": answers["sign"]["choice"],
            "lag_days": lag_days,
            # The heuristic reports a min/mode/max band; only `mode` is scored. The band here is
            # the same grade-scaled width the heuristic uses, so the shape round-trips, but no
            # scorer reads it.
            "elasticity": {
                "min": round(max(0.0, mode - 0.05 * grade), 4),
                "mode": mode,
                "max": round(min(1.0, mode + 0.05 * grade), 4),
            },
            "evidence_grade": grade,
        },
        "confounders": [
            {"id": c["id"], "name": c.get("name", c["id"]), "discounted_because": "candidate common cause"}
            for c in (item_input.get("candidate_confounders") or [])
        ],
        "alternatives": [
            "Reverse causation: %s could be influencing %s rather than the direction claimed here."
            % (item_input["to"]["name"], item_input["from"]["name"])
        ],
        "claimed_by": "laya (candidate model)",
    }


def _gameplay_lens(item_input: dict) -> tuple[str, dict]:
    """`gameplay_lens.propose()` reads each component's stage and evolution position, the
    structural edges in both directions, and which components a person edge holds. All three are
    rendered, for the whole map, once, because the heuristic sees the whole map too."""
    positions = {str(p["component"]): p for p in item_input["positions"]}
    needs_out: dict[str, set] = {}
    needs_in: dict[str, set] = {}
    held_by: dict[str, set] = {}
    for edge in item_input["edges"]:
        etype, source, target = str(edge["type"]), str(edge["from"]), str(edge["to"])
        if etype == "needs":
            needs_out.setdefault(source, set()).add(target)
            needs_in.setdefault(target, set()).add(source)
        elif etype in ("maintains", "knows", "owns"):
            held_by.setdefault(target, set()).add(source)

    lines = []
    for cid in sorted(positions):
        p = positions[cid]
        bits = ["%s is at evolution position %.2f, in the %s stage" % (cid, float(p["evolution"]), p["stage"])]
        if needs_out.get(cid):
            bits.append("it depends on %s" % ", ".join(sorted(needs_out[cid])))
        if needs_in.get(cid):
            bits.append("%s depend on it" % ", ".join(sorted(needs_in[cid])))
        if held_by.get(cid):
            bits.append("it is held by %s" % ", ".join(sorted(held_by[cid])))
        lines.append("- " + "; ".join(bits) + ".")
    state = (
        "An organisation's value chain has been mapped. The organisation itself owns these "
        "components: %s.\n\nThe full map, including components it does not own:\n%s"
        % (", ".join(item_input["org_components"]), "\n".join(lines))
    )
    questions = {}
    for component in sorted(item_input["org_components"]):
        for play in PLAYS:
            questions["%s|%s" % (play, component)] = {
                "type": "choice",
                "instructions": (
                    "Is the %s play available on %s right now? That play needs: %s."
                    % (play, component, PLAY_CRITERIA[play])
                ),
                "criteria": {
                    "available": "every precondition of the play holds for this component today",
                    "not-available": "at least one precondition of the play does not hold",
                },
            }
    return state, questions


def _gameplay_lens_assemble(answers: dict, item_input: dict) -> dict:
    opportunities = []
    for key in sorted(answers):
        if answers[key]["choice"] != "available":
            continue
        play, component = key.split("|", 1)
        opportunities.append(
            {
                "play": play,
                "component": component,
                "reason": "Laya typed-decision output",
                "preconditions": {},
                "claim": {
                    "kind": "opportunity",
                    "component": component,
                    "evidence_grade": 5,
                    "claimed_by": "laya (candidate model)",
                    "evidence": "Laya typed-decision output",
                },
            }
        )
    return {"opportunities": opportunities}


# The five outcomes `ethics_gate.scorer()` can grade: the pair (admitted, stopped_at). Four of
# them are ladder stops; the fifth is the DPIA block, which reports `admitted: False` with
# `stopped_at: None`, and telling those two `False` cases apart is what the scorer exists for.
ETHICS_OUTCOMES = {
    "admit": (True, None),
    "stop-at-purpose": (False, "purpose"),
    "stop-at-necessity": (False, "necessity"),
    "stop-at-proportionality": (False, "proportionality"),
    "refuse-for-missing-dpia": (False, None),
}


def _ethics_gate(item_input: dict) -> tuple[str, dict]:
    """`ethics_gate.admit()` reads the sensor id, the three ladder rungs and the four DPIA fields.
    All are rendered, in the ladder's own order."""
    purpose, necessity = item_input["purpose"], item_input["necessity"]
    prop, dpia = item_input["proportionality"], item_input["dpia"]
    alternatives = necessity.get("alternatives") or []
    alt_text = (
        ", ".join("%s at %s level" % (a["kind"], a["level"]) for a in alternatives) if alternatives else "none offered"
    )
    state = (
        "A proposed workplace sensor is being put through an admission gate. The gate walks three "
        "rungs in order, purpose then necessity then proportionality, and stops at the first that "
        "fails. A sensor that clears all three is still refused if a mandatory data protection "
        "impact assessment is not recorded complete.\n\n"
        "Sensor: %s\n"
        "Purpose: the stated scenario is %r, and the organisation %s act on what it learns.\n"
        "Necessity: the proposed measurement is %s at %s level. Less intrusive alternatives "
        "offered: %s.\n"
        "Proportionality: the intrusion costs %.0f and the value illuminated is %.0f.\n"
        "Data protection: channels observed are %s; profiling is %s; financial loss risk is %s; "
        "a data protection impact assessment is %s."
        % (
            item_input["sensor"]["name"],
            purpose.get("scenario", ""),
            "will" if purpose.get("will_act") else "will not",
            necessity.get("kind"),
            necessity.get("level"),
            alt_text,
            float(prop.get("intrusion_cost", 0.0)),
            float(prop.get("value_illuminated", 0.0)),
            ", ".join(dpia.get("channels") or []) or "none",
            "yes" if dpia.get("profiling") else "no",
            "yes" if dpia.get("financial_loss_risk") else "no",
            "recorded complete" if dpia.get("complete") else "not recorded complete",
        )
    )
    questions = {
        "outcome": {
            "type": "choice",
            "instructions": "What does the gate do with this sensor?",
            "criteria": {
                "admit": "all three rungs pass and no outstanding impact assessment blocks it",
                "stop-at-purpose": "the purpose rung fails: no named scenario, or nobody will act",
                "stop-at-necessity": "the purpose rung passes but a less intrusive alternative exists",
                "stop-at-proportionality": "purpose and necessity pass but the intrusion outweighs the value",
                "refuse-for-missing-dpia": "all three rungs pass but a mandatory impact assessment is not complete",
            },
        }
    }
    return state, questions


def _ethics_gate_assemble(answers: dict, item_input: dict) -> dict:
    admitted, stopped_at = ETHICS_OUTCOMES[answers["outcome"]["choice"]]
    return {
        "admitted": admitted,
        "ladder": {"admitted": admitted or stopped_at is None, "stopped_at": stopped_at, "rungs": []},
        "dpia": {},
        "claim": {
            "kind": "sensor-admission",
            "component": item_input["sensor"]["id"],
            "evidence_grade": 5,
            "claimed_by": "laya (candidate model)",
            "evidence": "Laya typed-decision output",
        },
    }


RENDERERS = {
    "signal-classify": (_signal_classify, _signal_classify_assemble),
    "evolution-judge": (_evolution_judge, _evolution_judge_assemble),
    "causal-claims": (_causal_claims, _causal_claims_assemble),
    "gameplay-lens": (_gameplay_lens, _gameplay_lens_assemble),
    "ethics-gate": (_ethics_gate, _ethics_gate_assemble),
}

# `substrate-generator` takes a recipe and RETURNS a channel-by-channel schedule of generated
# messages with a planted-signal list. Laya emits no tokens at all -- every call in ticket 02's
# recorded run reports `output_tokens: 0` -- so it cannot produce this output shape by any
# rendering. This is a stated "not measurable", not a score of zero. See score.py.
NOT_MEASURABLE = {
    "substrate-generator": (
        "Laya is a classifier over typed questions and emits no tokens (`output_tokens: 0` on "
        "every call ticket 02 recorded). `substrate-generator` must GENERATE a multi-channel "
        "message schedule from a recipe. No rendering of the input makes a classifier able to "
        "produce that output, so this skill is not measurable against this model at all. It is "
        "reported as not measurable, never as a score of zero."
    )
}


def _load(path: Path) -> dict:
    doc = json.loads(path.read_text())
    out = {}
    for skill, entry in doc.items():
        items = []
        for item in entry["items"]:
            assert "expected" in item, "the dump should carry a label for score.py"
            # Stripped HERE, before any renderer sees it. An accidental leak becomes a KeyError.
            items.append({"id": item["id"], "input": item["input"]})
        out[skill] = {"corpus_digest": entry["corpus_digest"], "items": items}
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    default_dir = str(Path.home() / ".cache" / "laya-bench" / "laya-english-1c5edc17")
    ap.add_argument("--model-dir", default=default_dir)
    ap.add_argument("--corpora", default=str(HERE / "corpora.json"))
    ap.add_argument("--out", default=str(HERE / "predictions.json"))
    ap.add_argument("--threads", type=int, default=TORCH_THREADS)
    args = ap.parse_args()

    corpora = _load(Path(args.corpora))

    _close_the_network()

    root = Path(args.model_dir)
    before = digest_tree(root)
    on_disk = sha256_file(root / "model.safetensors")
    if on_disk != EXPECTED_WEIGHTS_SHA256:
        print(
            "FAIL: %s digests to %s, the pin is %s. Run measure_laya.py fetch first."
            % (root / "model.safetensors", on_disk, EXPECTED_WEIGHTS_SHA256),
            file=sys.stderr,
        )
        return 1

    import torch
    from laya import Agent

    torch.set_num_threads(args.threads)
    torch.use_deterministic_algorithms(True)

    load_start = time.perf_counter()
    agent = Agent(str(root), device=DEVICE)  # item 11: a local pinned directory, never the repo id
    load_seconds = time.perf_counter() - load_start
    if str(agent.device) != DEVICE:
        print("FAIL: agent placed on %s, not %s" % (agent.device, DEVICE), file=sys.stderr)
        return 1

    predictions: dict[str, dict] = {}
    raw: dict[str, dict] = {}
    act_probabilities: list[float] = []
    call_count = 0
    question_count = 0
    wall_start = time.perf_counter()

    for skill in sorted(RENDERERS):
        render, assemble = RENDERERS[skill]
        entry = corpora[skill]
        predictions[skill] = {"corpus_digest": entry["corpus_digest"], "by_item": {}}
        raw[skill] = {}
        for item in entry["items"]:
            state, questions = render(item["input"])
            t0 = time.perf_counter()
            out = agent.system_one(state, questions)
            elapsed_ms = (time.perf_counter() - t0) * 1000.0
            call_count += 1
            question_count += len(questions)
            answers = out["answers"]
            for name, answer in answers.items():
                act = answer.get("action", {}).get("act_probability")
                if act is not None:
                    act_probabilities.append(float(act))
            predictions[skill]["by_item"][item["id"]] = assemble(answers, item["input"])
            raw[skill][item["id"]] = {
                "state": state,
                "questions": questions,
                "answers": answers,
                "usage": out.get("usage"),
                "call_ms": round(elapsed_ms, 2),
            }

    wall_seconds = time.perf_counter() - wall_start
    after = digest_tree(root)

    record = {
        "ticket": "04",
        "repo_id": REPO_ID,
        "revision": REVISION,
        "weights_sha256": on_disk,
        "files_mutated_by_load": sorted(k for k in before if before[k] != after.get(k)),
        "network": "blocked at socket.connect for the whole run",
        "device": str(agent.device),
        "dtype": str(agent.dtype),
        "torch_threads": args.threads,
        "load_seconds": round(load_seconds, 2),
        "calls": call_count,
        "questions": question_count,
        "wall_seconds": round(wall_seconds, 2),
        "ms_per_question": round(wall_seconds * 1000.0 / question_count, 2),
        "torch": torch.__version__,
        "act_probability": {
            "n": len(act_probabilities),
            "distinct": sorted(set(act_probabilities)),
            "min": min(act_probabilities) if act_probabilities else None,
            "max": max(act_probabilities) if act_probabilities else None,
        },
        "not_measurable": NOT_MEASURABLE,
        "predictions": predictions,
        "raw": raw,
        "predictions_sha256": canonical_sha256(predictions),
        "measured_at": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
    }
    Path(args.out).write_text(json.dumps(record, indent=1, sort_keys=True) + "\n")

    print("pin             %s@%s" % (REPO_ID, REVISION))
    print("weights         sha256 %s" % on_disk)
    print("mutated         %s" % (record["files_mutated_by_load"] or "nothing"))
    print("device          %s  dtype %s  threads %d" % (agent.device, agent.dtype, args.threads))
    print("load            %.2f s" % load_seconds)
    print("calls           %d  questions %d  wall %.1f s  %.1f ms/question"
          % (call_count, question_count, wall_seconds, record["ms_per_question"]))
    print("act_probability n=%d  distinct=%s" % (len(act_probabilities), record["act_probability"]["distinct"][:6]))
    print("predictions     sha256 %s" % record["predictions_sha256"])
    print("wrote           %s" % args.out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
