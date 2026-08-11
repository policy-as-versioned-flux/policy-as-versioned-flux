"""The `twin` command — seam 1, the primary boundary.

A command takes a pinned model repository and emits a signed artefact to a declared output path.
Because attestation already requires determinism given the pins, this seam is golden-file
testable, and that property is itself the first test.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import tempfile
from pathlib import Path

import yaml

from . import TOOL_VERSION, attest, constraints, evidence, fixtures, index, invariants, schedule, sign, verbs
from .artefact import AUTHORED, Artefact, ArtefactError
from .attest import AttestationError
from .blob import BlobRefError
from .canon import canonical_json, sha256_hex
from .constraints import ConstraintError
from .drift import DriftError
from .evidence import EvidenceError
from .grades import Capabilities, GradeError
from .index import IndexError_
from .invariants import FAIL, PASS, SKIP
from .invariants.harness import LIVE, MANIFEST_PATH, Suite, load_manifest
from .model import ModelError
from .pert import PertError
from .primitives import PrimitiveError
from . import propagate as propagate_mod
from .propagate import AttenuationError
from .regimes import RegimeError
from .reproduce import ReproduceError
from .repo import ModelRepo, RepoError
from .schema import REGIMES, SchemaError
from .scoring import RULES, ScoreError
from .sign import SignatureError
from .verbs import VerbError


def _say(message: str) -> None:
    print(f"==> {message}")


def _emit(artefact: Artefact, out: str) -> int:
    path = artefact.write(out)
    sidecar = attest.write(artefact, path)
    status = json.loads(sidecar.read_bytes()).get("signature_status") or "agent-signed (origin only)"
    depth = artefact.depth
    print(f"{artefact.kind} -> {path}")
    print(f"  attestation  {sidecar.name} ({status})")
    print(f"  sha256       {artefact.digest()}")
    print(f"  depth        {depth['grade']}")
    for name, summary in sorted(depth.get("capabilities", {}).items()):
        unchecked = ", ".join(str(u["index"]) for u in summary["unchecked"]) or "-"
        print(
            f"    {name:<18} {summary['grade']:<8} {summary['checked']}/{summary['total']} "
            f"of decision ticket {summary['owning_ticket']}  unchecked: {unchecked}"
        )
    return 0


def _open(args: argparse.Namespace) -> tuple[ModelRepo, Capabilities, str]:
    repo = ModelRepo.open(args.repo, args.ref)
    caps = Capabilities.load()
    return repo, caps, verbs.resolve_org(repo, args.org)


# -- verbs ----------------------------------------------------------------------------------


def cmd_sense(args: argparse.Namespace) -> int:
    repo, caps, org = _open(args)
    artefact = verbs.sense(
        repo, caps, org, args.signal, verbs.command_for("sense", org=org, signal=args.signal)
    )
    return _emit(artefact, args.out)


def cmd_run(args: argparse.Namespace) -> int:
    repo, caps, org = _open(args)
    artefact = verbs.run(
        repo,
        caps,
        org,
        args.scenario,
        args.regime,
        verbs.command_for(
            "run", org=org, scenario=args.scenario, regime=args.regime, at=args.at
        ),
        at=args.at,
    )
    gate = artefact.body["regime"]
    withheld = gate["gate"]["withheld"]
    _say(
        f"{org}: {args.scenario} under {gate['declared']} — "
        f"{'scoring-eligible' if gate['scoring_eligible'] else 'not scoring-eligible'}, "
        f"{len(withheld)} fact(s) withheld by date"
    )
    for entry in withheld:
        print(f"  withheld {entry['id']:<34} {entry['collection']}, dated {entry['dated']}")
    if not gate["gate"]["ingestion_history"]["available"]:
        print(f"  ingestion history unavailable: {gate['gate']['ingestion_history']['consequence']}")
    return _emit(artefact, args.out)


def cmd_regimes(args: argparse.Namespace) -> int:
    """The two gaps, computed. Sensing and interpretation, localised rather than inferred."""
    repo, caps, org = _open(args)
    artefact = verbs.regime_gap(
        repo,
        caps,
        org,
        args.scenario,
        verbs.command_for("regimes", org=org, scenario=args.scenario, at=args.at),
        at=args.at,
    )
    localisation = artefact.body["localisation"]
    _say(f"{org}: {args.scenario} under all three regimes")
    for regime, count in sorted(localisation["admitted_counts"].items()):
        print(f"  {regime:<16} {count} fact(s) admitted")
    for entry in localisation["gaps"]:
        names = ", ".join(entry["facts"]) or "none"
        print(f"  {entry['localises']:<16} {' vs '.join(entry['between'])}: {names}")
    print(f"  model residual not computed: {localisation['model_residual']['why']}")
    return _emit(artefact, args.out)


def cmd_positions(args: argparse.Namespace) -> int:
    """Believed map, rival forecasts, revealed truth — and the deltas between them."""
    repo, caps, org = _open(args)
    artefact = verbs.positions(
        repo, caps, org, args.scenario, verbs.command_for("positions", org=org, scenario=args.scenario)
    )
    body = artefact.body
    _say(f"{org}: {args.scenario!r} — {len(body['positions'])} position(s), {len(body['abstained'])} abstained")
    for row in body["pairwise"]:
        print(f"  delta    {row['a']:<24} vs {row['b']:<24} {row['delta']}")
    if body["revealed"]["resolved"]:
        for row in body["against_revealed"]:
            print(f"  scored   {row['id']:<24} brier {row['brier']:<10} log_loss {row['log_loss']}")
    else:
        print(f"  revealed: not yet — {body['revealed']['reason']}")
    print(f"  {body['no_privileged_position']}")
    return _emit(artefact, args.out)


def cmd_credibility(args: argparse.Namespace) -> int:
    """The credibility-weighted blend of a world-layer prior with an org's own sparse data."""
    repo, caps, org = _open(args)
    artefact = verbs.credibility(
        repo, caps, org, args.subject, verbs.command_for("credibility", org=org, subject=args.subject)
    )
    body = artefact.body
    own, blended = body["own_data"], body["blended"]
    _say(f"{org}: {args.subject!r} — n={own['n']}, z={body['credibility']['z']}")
    print(f"  world prior  {body['world_prior']['min']}/{body['world_prior']['mode']}/{body['world_prior']['max']}")
    print(f"  own data     {own['note'] if own['n'] == 0 else own['mean']}")
    print(f"  blended      {blended['min']}/{blended['mode']}/{blended['max']}")
    return _emit(artefact, args.out)


def cmd_causal_accounts(args: argparse.Namespace) -> int:
    """Rival causal accounts, each propagated independently, and the spread between them."""
    repo, caps, org = _open(args)
    artefact = verbs.causal_accounts(
        repo, caps, org, args.origin, args.account,
        verbs.command_for("causal-accounts", org=org, origin=args.origin, account="+".join(sorted(args.account))),
    )
    body = artefact.body
    _say(f"{org}: shock at {args.origin!r} across {len(body['accounts'])} account(s)")
    for row in body["spread"]:
        by = ", ".join(f"{a}={v}" for a, v in sorted(row["by_account"].items()))
        print(f"  {row['component']:<24} range={row['range']:<12} ({by})")
    if not body["spread"]:
        print("  no reached component carries a magnitude under every account named")
    return _emit(artefact, args.out)


def cmd_trade_off(args: argparse.Namespace) -> int:
    """Every admitted response's net cost of risk, per named causal account — never one figure."""
    repo, caps, org = _open(args)
    artefact = verbs.trade_off(
        repo, caps, org, args.origin, args.perspective, args.account,
        verbs.command_for(
            "trade-off", org=org, origin=args.origin, perspective=args.perspective,
            account="+".join(sorted(args.account)),
        ),
    )
    body = artefact.body
    _say(f"{org}/{args.perspective}: a shock at {args.origin!r}, {len(body['curve'])} response(s) "
         f"across {len(body['accounts'])} account(s)")
    for point in body["curve"]:
        by = ", ".join(f"{a}={v:,.0f}" for a, v in sorted(point["net_cost_of_risk"]["by_account"].items()))
        print(f"  {point['option']:<28} range={point['net_cost_of_risk']['range']:,.0f}  ({by})")
    print(f"  agreement  unanimous={body['agreement']['unanimous']}  {body['agreement']['note']}")
    print(f"  default    {body['default']['option']} — {body['default']['basis']}")
    return _emit(artefact, args.out)


def _pooled_scores(paths: list[str]) -> list[dict]:
    """`body.scores` from each named score-card artefact, concatenated (build ticket 40).

    A thin wrapper over `verbs.load_score_card` — the read-and-kind-check itself lives there,
    shared with `cmd_reliability`, rather than duplicated here.
    """
    scores: list[dict] = []
    for raw_path in paths:
        _, card_scores = verbs.load_score_card(raw_path)
        scores.extend(card_scores)
    return scores


def cmd_score(args: argparse.Namespace) -> int:
    from .artefact import digest_of_file
    from .canon import digest_of
    from .scoring import measure_discount

    repo, caps, org = _open(args)

    discount = None
    discount_sha256 = None
    if args.discount_enron or args.discount_obscure:
        discount = measure_discount(
            _pooled_scores(args.discount_enron), _pooled_scores(args.discount_obscure), rule=args.discount_rule,
        )
        # Pinned by digest, never by path — the same reason `--forecast` is recorded as
        # `forecast_sha256` (`command_for`'s own docstring): a machine-local path in the command
        # would break `identical_pins_identical_bytes` across machines. The discount's own
        # `--discount-enron`/`--discount-obscure` paths never enter the recorded command.
        discount_sha256 = digest_of(discount)

    artefact = verbs.score(
        repo,
        caps,
        org,
        args.forecast,
        args.outcome,
        verbs.command_for(
            "score", org=org, outcome=args.outcome, forecast_sha256=digest_of_file(args.forecast),
            discount_sha256=discount_sha256,
        ),
        discount=discount,
    )
    return _emit(artefact, args.out)


def cmd_sweep(args: argparse.Namespace) -> int:
    """Every scenario, every org, every named repository. No `--scenario` flag exists here.

    That absence is the point (build ticket 09): a human names nothing at run time, so the record
    cannot be selected towards the scenarios someone felt confident about.
    """
    repos = [ModelRepo.open(path, args.ref) for path in args.repo]
    caps = Capabilities.load()
    command = verbs.command_for("sweep", regime="as-consumed", at=args.at)
    artefact = schedule.sweep(repos, caps, command, at=args.at)
    counts = artefact.body["counts"]
    _say(
        f"sweep across {counts['repos']} repo(s): {counts['executed']} execution(s), "
        f"{counts['forecasts']} forecast(s), {counts['failed']} failure(s)"
    )
    for failure in artefact.body["failures"]:
        print(f"  failed  {failure['org']}/{failure['scenario']}: {failure['reason']}")
    return _emit(artefact, args.out)


def cmd_reliability(args: argparse.Namespace) -> int:
    caps = Capabilities.load()
    command = verbs.command_for("reliability", bins=str(args.bins))
    artefact = verbs.reliability(args.score_card, caps, command, bins=args.bins)
    _say(f"reliability diagram over {artefact.body['total_scored']} scored forecast(s), {args.bins} bin(s)")
    for entry in artefact.body["bins"]:
        lo, hi = entry["range"]
        mean = "-" if entry["mean_forecast"] is None else f"{entry['mean_forecast']:.2f}"
        freq = "-" if entry["empirical_frequency"] is None else f"{entry['empirical_frequency']:.2f}"
        print(f"  [{lo:.1f}, {hi:.1f})  n={entry['count']:<4} mean={mean:<6} observed={freq}")
    return _emit(artefact, args.out)


def cmd_severity(args: argparse.Namespace) -> int:
    command = verbs.command_for(
        "severity", mu=str(args.mu), sigma=str(args.sigma), threshold=str(args.threshold),
        xi=str(args.xi), beta=str(args.beta), alpha=",".join(str(a) for a in sorted(args.alpha)),
    )
    caps = Capabilities.load()
    artefact = verbs.severity_curve(args.mu, args.sigma, args.threshold, args.xi, args.beta, args.alpha, caps, command)
    _say(f"loss-exceedance curve, {len(artefact.body['curve'])} confidence level(s)")
    for row in artefact.body["curve"]:
        tvar = "-" if row["tvar"] is None else f"{row['tvar']:.2f}"
        print(f"  alpha={row['alpha']:<7} var={row['var']:<14.2f} tvar={tvar}")
    return _emit(artefact, args.out)


def cmd_severity_anchor(args: argparse.Namespace) -> int:
    command = verbs.command_for(
        "severity-anchor", subject=args.subject, alpha=",".join(str(a) for a in sorted(args.alpha)),
        sensitivity_xi=",".join(str(x) for x in sorted(args.sensitivity_xi)) if args.sensitivity_xi else None,
    )
    caps = Capabilities.load()
    artefact = verbs.anchored_severity_curve(
        args.subject, args.alpha, caps, command, sensitivity_grid=args.sensitivity_xi or None
    )
    anchoring = artefact.body["anchoring"]
    unanchored = [p["name"] for p in anchoring["parameters"] if not p["anchored"]]
    _say(
        f"{args.subject!r}: {anchoring['anchored_count']} anchored parameter(s), "
        f"{anchoring['unanchored_count']} unanchored ({', '.join(unanchored) or 'none'})"
    )
    for row in artefact.body["curve"]:
        tvar = "-" if row["tvar"] is None else f"{row['tvar']:.2f}"
        print(f"  alpha={row['alpha']:<7} var={row['var']:<14.2f} tvar={tvar}")
    if artefact.body["sensitivity"]:
        spread = artefact.body["sensitivity"]["spread"]
        print(f"  sensitivity (xi sweep): TVaR ranges {spread['min']:.2f} .. {spread['max']:.2f}")
    return _emit(artefact, args.out)


def cmd_blast(args: argparse.Namespace) -> int:
    repo, caps, org = _open(args)
    artefact = verbs.blast(
        repo, caps, org, args.origin, verbs.command_for("blast", org=org, origin=args.origin)
    )
    body = artefact.body
    _say(
        f"{org}: blast radius from {args.origin!r} — {len(body['admitted_to_pricing'])} admitted "
        f"to pricing, {len(body['unpriced'])} connected and unpriceable"
    )
    for entry in body["admitted_to_pricing"]:
        print(f"  price   {entry['component']:<28} depth {entry['depth']}, weakest grade "
              f"{entry['worst_evidence_grade']}")
    for entry in body["unpriced"]:
        print(f"  unpriced {entry['component']:<27} {entry['reason']}")
    return _emit(artefact, args.out)


def cmd_propagate(args: argparse.Namespace) -> int:
    repo, caps, org = _open(args)
    artefact = verbs.propagate(
        repo, caps, org, args.origin, verbs.command_for("propagate", org=org, origin=args.origin)
    )
    body = artefact.body
    _say(
        f"{org}: a shock at {args.origin!r} composes to {len(body['reached'])} component(s) along "
        f"{sum(len(r['paths']) for r in body['reached'])} causal path(s)"
    )
    for reached in body["reached"]:
        for path in reached["paths"]:
            mark = "*" if path["primary"] else " "
            if path["directional_only"]:
                print(f"  {mark} {reached['component']:<26} depth {path['depth']}  "
                      f"{path['sign']} direction only, no magnitude")
                continue
            composed, attenuated = path["composed"], path["attenuated"]
            print(
                f"  {mark} {reached['component']:<26} depth {path['depth']}  "
                f"composed {composed['min']:.4f}/{composed['mode']:.4f}/{composed['max']:.4f}  "
                f"x{path['attenuation']} -> {attenuated['min']:.4f}/{attenuated['mode']:.4f}/"
                f"{attenuated['max']:.4f}  sampled p50 {path['sampled']['p50']:.4f}"
            )
    print(f"  {body['attenuation']['rule']}")
    print(f"  {body['traversal']['paths_are_not_aggregated']}")
    return _emit(artefact, args.out)


def _say_query(args: argparse.Namespace, artefact: Artefact) -> int:
    body = artefact.body
    _say(f"{body['component']}: {body['operation']} — propagates {body['semantics']['propagates']}")
    for entry in body["severed"]:
        print(f"  severed  {entry['edge']:<34} {entry['from']} -> {entry['to']}, "
              f"grade {entry['evidence_grade']}")
    for entry in body["upstream"]:
        print(f"  updated  {entry['component']:<34} depth {entry['depth']}, weakest grade "
              f"{entry['worst_evidence_grade']}, no magnitude")
    for reached in body["downstream"]["reached"]:
        joint = reached.get("joint")
        if joint is None:
            figure = "direction only, no magnitude"
        elif joint["sign"] == propagate_mod.MIXED:
            figure = "routes disagree in direction, so they are not combined"
        elif joint["exact"] is None:
            figure = f"joint sampled p50 {joint['sampled']['p50']}, past the exact-form bound"
        else:
            figure = f"joint {joint['exact']} ({joint['sign']})"
        print(f"  downstream {reached['component']:<32} {len(reached['paths'])} path(s), {figure}")
    print(f"  {body['semantics']['why']}")
    if not body["upstream"] and body["operation"] == "intervene":
        print("  nothing upstream: doing a thing does not rewrite its own causes")
    return _emit(artefact, args.out)


def cmd_intervene(args: argparse.Namespace) -> int:
    repo, caps, org = _open(args)
    return _say_query(args, verbs.intervene(
        repo, caps, org, args.component,
        verbs.command_for("intervene", org=org, component=args.component),
    ))


def cmd_observe(args: argparse.Namespace) -> int:
    repo, caps, org = _open(args)
    return _say_query(args, verbs.observe(
        repo, caps, org, args.component,
        verbs.command_for("observe", org=org, component=args.component),
    ))


def cmd_price(args: argparse.Namespace) -> int:
    """One shock, priced under every declared perspective, with the responses beside it."""
    repo, caps, org = _open(args)
    artefact = verbs.price(
        repo, caps, org, args.origin, args.perspective,
        verbs.command_for("price", org=org, origin=args.origin),
    )
    body = artefact.body
    _say(f"{org}: a shock at {args.origin!r}, priced under {len(body['perspectives'])} perspective(s)")
    for entry in body["perspectives"]:
        print(f"  {entry['perspective']}")
        for impact in entry["impacts"]:
            price = impact["price"]["attenuated"]
            print(f"    price    {impact['component']:<24} {price['min']:,.0f} / "
                  f"{price['mode']:,.0f} / {price['max']:,.0f}  grade "
                  f"{impact['worst_evidence_grade']}")
        for held in entry["register"]:
            print(f"    unpriced {held['component']:<24} {held['reason']}")
        for option in entry["responses"]["priced"]:
            credit = option["mitigation"].get("credit")
            earned = f"credit {credit['mode']:,.0f}" if credit else option["mitigation"]["reason"]
            print(f"    option   {option['option']:<24} cost {option['cost']['mean']:,.0f}, {earned}")
    for row in body["attribution"]:
        if row["spread"] is not None:
            print(f"  spread   {row['component']:<26} {row['spread']:,.0f} between the widest and "
                  "narrowest eye")
    print(f"  {body['not_a_ranking']}")
    return _emit(artefact, args.out)


def cmd_drift(args: argparse.Namespace) -> int:
    """The Flux drift measurement so far (build ticket 64). A reduction, never a verdict.

    Prints rather than emitting an artefact: the input is a probe log outside any model
    repository, so there are no pins to recompute it from and an envelope claiming otherwise
    would be the one dishonest thing in the file.
    """
    import datetime

    from . import drift

    # The wall clock, named as such. Coverage is "how much of the window has passed", which is a
    # question about now — and `report` takes it as an argument so the reduction stays a function
    # of its inputs.
    now = datetime.datetime.now(datetime.timezone.utc).replace(microsecond=0).isoformat()
    body = drift.report(now)
    cover = body["coverage"]
    _say(f"Flux drift measurement, {cover['window_opens']} to {cover['window_closes']}")
    print(f"  question     {body['question']}")
    print(f"  owner        {body['owner']}")
    print(
        f"  window       {cover['window_elapsed_fraction']:.0%} elapsed, "
        f"{cover['samples_reachable']}/{cover['samples_expected_by_now']} expected samples "
        f"({cover['sampled_fraction']:.0%} coverage)"
    )
    for hole in cover["gaps_wider_than_the_cadence"]:
        print(f"  gap          {hole['from']} -> {hole['to']} ({hole['hours']}h unobserved)")
    for event in body["drift_events"]:
        interval = (
            "no deploy observed yet" if event["since_deploy_seconds"] is None
            else f"{event['since_deploy_seconds']}s after the last deploy"
        )
        print(f"  drift        {event['subject']:<26} {event['from']!r} -> {event['to']!r}, {interval}")
    if not body["drift_events"]:
        print("  no drift event observed yet — read that against the coverage above, not instead of it")
    for entry in body["open_preconditions"]:
        print(f"  precondition {entry['id']:<26} blocks {entry['blocks']}, owner: {entry['owner']}")
    print(f"  no verdict:  {body['why_no_verdict']}")
    return 0


def cmd_rewind(args: argparse.Namespace) -> int:
    """The model as it stood at a declared time — a model state, not a filtered view."""
    from .primitives import rewind

    repo = rewind(args.repo, args.at)
    caps = Capabilities.load()
    org = verbs.resolve_org(repo, args.org)
    artefact = verbs.rewind(
        repo, caps, org, args.at, verbs.command_for("rewind", org=org, at=args.at)
    )
    body = artefact.body
    _say(
        f"{org} as at {args.at}: commit {body['resolved']['commit'][:12]}, committed "
        f"{body['resolved']['committed']}"
    )
    rollups = body["rollups"]
    print(f"  {rollups['components']} components, {rollups['edges']} edges, "
          f"{rollups['causal_edges']} causal")
    print("  a model state, not a filtered view: everything downstream reads it unchanged")
    return _emit(artefact, args.out)


def cmd_backtest(args: argparse.Namespace) -> int:
    """Rewind plus projection (build ticket 37): what the model would have forecast as of a past
    time, scored against the record once `twin score` runs on this command's output.

    No backtest-specific code path — this function is `primitives.rewind` followed by `verbs.run`
    and nothing else, the same two calls `cmd_rewind` and `cmd_run` already make separately.
    Harness guard `backtest_is_a_pure_composition` asserts this against the source, not merely
    the docstring.
    """
    from .primitives import rewind

    repo = rewind(args.repo, args.at)
    caps = Capabilities.load()
    org = verbs.resolve_org(repo, args.org)
    command = verbs.command_for(
        "backtest", org=org, scenario=args.scenario, at=args.at, regime=args.regime
    )
    artefact = verbs.run(repo, caps, org, args.scenario, args.regime, command, at=args.at)
    gate = artefact.body["regime"]
    _say(
        f"{org}: {args.scenario} rewound to {args.at} — "
        f"{'scoring-eligible' if gate['scoring_eligible'] else 'not scoring-eligible'} under {gate['declared']}"
    )
    return _emit(artefact, args.out)


def cmd_options(args: argparse.Namespace) -> int:
    repo, caps, org = _open(args)
    artefact = verbs.options(
        repo, caps, org, args.perspective,
        verbs.command_for("options", org=org, perspective=args.perspective),
    )
    body = artefact.body
    pre = body["prefilter"]
    _say(
        f"{org}: {len(pre['considered'])} option(s) considered for {args.perspective!r}, "
        f"{len(pre['admitted'])} priced, {len(pre['removed'])} removed before pricing"
    )
    for record in pre["removed"]:
        print(f"  removed  {record['option']:<30} {record['class']} — {record['constraint']} "
              f"({record['tier']} tier), no figure")
    for entry in body["priced"]:
        cost = entry["cost"]
        print(f"  priced   {entry['option']:<30} {cost['min']}/{cost['mode']}/{cost['max']} "
              f"mean {cost['mean']}, sampled p50 {entry['sampled']['p50']}")
    print("  a constraint is not a very large price: a removed option carries no number at all")
    return _emit(artefact, args.out)


def cmd_exposure(args: argparse.Namespace) -> int:
    repo, caps, org = _open(args)
    artefact = verbs.exposure(
        repo,
        caps,
        org,
        args.scenario,
        args.perspective or None,
        verbs.command_for(
            "exposure",
            org=org,
            scenario=args.scenario,
            perspectives=",".join(sorted(args.perspective)) if args.perspective else None,
        ),
    )
    body = artefact.body
    _say(f"{org}: scenario {args.scenario!r} under {len(body['perspectives'])} perspective(s)")
    for entry in body["perspectives"]:
        print(f"  {entry['id']:<22} {entry['party']:<15} declared exposure {entry['declared_exposure']}")
        for held in entry["register"]:
            print(f"    register  {held['component']:<24} grade {held['evidence_grade']}, no figure")
    for row in body["attribution"]:
        figures = ", ".join(f"{k}={v}" for k, v in sorted(row["declared_value"].items()))
        print(f"    {row['component']:<24} {figures}   spread {row['spread']}")
    print(f"  spread across perspectives: {body['exposure_spread']}")
    print("  a spread, never a chosen number — the disagreement is the decision-relevant part")
    print(f"  gate: {body['gating']['rule']}")
    print("  a register entry carries no figure at all — beside the number, never inside it")
    return _emit(artefact, args.out)


def cmd_constraints(args: argparse.Namespace) -> int:
    """Publish the constraint set — the floor, the scope exclusions and the stated positions.

    Authored, like the worksheet, and signed as a role. The universal floor and the evidence
    ladder's pricing threshold ship together on purpose: changing what may be priced has to be as
    visible as changing what may be chosen, and one artefact is how that stays true.
    """
    published = constraints.published()
    artefact = constraints.artefact(verbs.command_for("constraints"))
    path = artefact.write(args.out)
    material = sign.signing_key()
    signatures = [sign.human(constraints.ROLE, artefact.digest(), material)] if material else []
    sidecar = attest.write(artefact, path, signatures)

    _say(f"constraint set -> {path} (authored, role {constraints.ROLE!r})")
    for entry in published["universal_floor"]:
        print(f"  floor      {entry['class']:<10} {entry['id']}")
    for entry in published["scope_exclusions"]:
        print(f"  excluded              {entry['id']}")
    for entry in published["positions"]:
        print(f"  position   {entry['status']:<21} {entry['id']}")
    print(f"  gate       grades 1-{evidence.threshold()} may price a scored forecast")
    if material is None:
        print(f"  unsigned: set {sign.KEY_ENV}, then `twin sign {path} --role {constraints.ROLE}`")
        return 0
    print(f"  signed as role {constraints.ROLE!r} -> {sidecar.name}")
    return 0


def cmd_challenge(args: argparse.Namespace) -> int:
    """Raise a challenge against one claim in an existing artefact (build ticket 60)."""
    from . import challenges
    from .artefact import digest_of_file
    from .artefact import load as load_artefact

    challenged_doc = load_artefact(args.artefact)
    challenged_sha256 = digest_of_file(args.artefact)
    try:
        artefact = challenges.raise_challenge(
            challenged_doc, challenged_sha256, args.claim_path, args.reason,
            verbs.command_for(
                "challenge", artefact_sha256=challenged_sha256, claim_path=args.claim_path,
            ),
        )
    except challenges.ChallengeError as exc:
        print(f"twin challenge: {exc}", file=sys.stderr)
        return 2
    path = artefact.write(args.out)
    material = sign.signing_key()
    signatures = [sign.human(args.role, artefact.digest(), material)] if material else []
    sidecar = attest.write(artefact, path, signatures)

    _say(f"challenge -> {path} (authored, role {args.role!r})")
    print(f"  claim      {args.claim_path}")
    print(f"  disputed   {artefact.body['challenged_value']!r}")
    print(f"  reason     {args.reason}")
    if material is None:
        print(f"  unsigned: set {sign.KEY_ENV}, then `twin sign {path} --role {args.role}`")
        return 0
    print(f"  signed as role {args.role!r} -> {sidecar.name}")
    return 0


def cmd_resolve_challenge(args: argparse.Namespace) -> int:
    """Resolve a challenge — the resolution names only what the challenge itself named."""
    from . import challenges
    from .artefact import digest_of_file
    from .artefact import load as load_artefact

    challenge_doc = load_artefact(args.challenge)
    challenge_sha256 = digest_of_file(args.challenge)
    try:
        artefact = challenges.resolve(
            challenge_doc, challenge_sha256, args.response,
            verbs.command_for("resolve-challenge", challenge_sha256=challenge_sha256),
        )
    except challenges.ChallengeError as exc:
        print(f"twin resolve-challenge: {exc}", file=sys.stderr)
        return 2
    path = artefact.write(args.out)
    material = sign.signing_key()
    signatures = [sign.human(args.role, artefact.digest(), material)] if material else []
    sidecar = attest.write(artefact, path, signatures)

    _say(f"resolution -> {path} (authored, role {args.role!r})")
    print(f"  claim      {artefact.body['claim_path']}")
    print(f"  response   {args.response}")
    if material is None:
        print(f"  unsigned: set {sign.KEY_ENV}, then `twin sign {path} --role {args.role}`")
        return 0
    print(f"  signed as role {args.role!r} -> {sidecar.name}")
    return 0


def cmd_graph(args: argparse.Namespace) -> int:
    repo, caps, org = _open(args)
    return _emit(verbs.graph(repo, caps, org, verbs.command_for("graph", org=org)), args.out)


def cmd_map(args: argparse.Namespace) -> int:
    """Render the Wardley map. Reads the graph artefact's own `wardley` block and nothing else,
    so a map cannot say something the graph does not (build ticket 14)."""
    from .wardley import plot

    repo, caps, org = _open(args)
    artefact = verbs.graph(repo, caps, org, verbs.command_for("graph", org=org))
    body = artefact.body["wardley"]
    _say(f"{org}: {len(body['positions'])} components on the map, rendered from the graph")
    print(plot(body))
    for entry in body["dependency_risk"]:
        print(f"  R({entry['from']} -> {entry['to']}) = {entry['dependency_risk']:.3f}")
    if body["unpositioned"]:
        print(f"  off the map (no evolution stage): {', '.join(body['unpositioned'])}")
    print(
        "\n  D, K and R describe a position. They are not forecasts, nothing scores them, and no\n"
        "  action band is inherited with them — the reader draws the action, never the artefact."
    )
    return 0


def cmd_worksheet(args: argparse.Namespace) -> int:
    """Check the pocket-org artefact against the hand-computed worksheet (build ticket 15)."""
    from . import worksheet

    if args.emit:
        return _emit_worksheet(args.emit)
    if not args.repo:
        print("twin worksheet needs --repo (a pocket-org repository) or --emit", file=sys.stderr)
        return 2

    repo, caps, org = _open(args)
    results = worksheet.check(worksheet.bodies_for(repo, caps))

    _say(f"{worksheet.WORKSHEET_PATH.name} against the emitted artefacts of {org!r}")
    for result in results:
        line = result.line
        if result.pending:
            print(f"  ..   {line.index:>2}  {line.key:<52} {line.expected:<10} pending {line.asserted_by}")
        else:
            mark = "ok  " if result.ok else "FAIL"
            print(f"  {mark} {line.index:>2}  {line.key:<52} {line.expected:<10} got {result.actual}")

    failed = [r for r in results if not r.pending and not r.ok]
    pending = [r for r in results if r.pending]
    late = worksheet.overdue(results)
    print(
        f"\n{len(results) - len(pending) - len(failed)} match, {len(failed)} differ, "
        f"{len(pending)} pending, compared at {worksheet.DECIMAL_PLACES} decimal places"
    )
    for problem in late:
        print(f"  OVERDUE {problem}")
    if failed or late:
        return 1
    return 0


def _emit_worksheet(out: str) -> int:
    """The worksheet as an authored artefact — the one place a human number is the authority."""
    from . import worksheet

    role, lines = worksheet.load()
    artefact = Artefact(
        kind="worksheet",
        mark=AUTHORED,
        # No output path in the command, for the same reason no other verb records one: a machine
        # path in the envelope breaks identical bytes across machines.
        command=verbs.command_for("worksheet"),
        pins={"worksheet_sha256": sha256_hex(worksheet.WORKSHEET_PATH.read_bytes()), "role": role},
        # No grade, rather than a grade of `authored`. A depth grade measures how much of a
        # decision ticket a **capability** has realised, and no capability produced this: the
        # number here is the authority instead of a derivation of one.
        depth={
            "grade": None,
            "capabilities": {},
            "note": "authored by a human in a declared role; no capability produced it",
        },
        body={
            "subject": worksheet.POCKET_ORG,
            "decimal_places": worksheet.DECIMAL_PLACES,
            "lines": [
                {"index": line.index, "key": line.key, "expected": line.expected,
                 "arithmetic": line.arithmetic, "asserted_by": line.asserted_by}
                for line in lines
            ],
        },
    )
    path = artefact.write(out)
    material = sign.signing_key()
    signatures = [sign.human(role, artefact.digest(), material)] if material else []
    sidecar = attest.write(artefact, path, signatures)
    print(f"worksheet -> {path} (authored, role {role!r})")
    if material is None:
        print(f"  unsigned: set {sign.KEY_ENV}, then `twin sign {path} --role {role}`")
        return 0
    print(f"  signed as role {role!r} -> {sidecar.name}")
    return 0


def cmd_validate(args: argparse.Namespace) -> int:
    """The gate an author or CI runs before committing. Nothing here writes model files, so
    "validated on write" means validated at the boundary the model crosses to get in."""
    from .model import BehaviouralOverlay, Overlay, World, orgs

    repo = ModelRepo.open(args.repo, args.ref)
    _say(f"validating {args.repo} at {repo.pin.commit[:12]}")
    World.load(repo)
    print("  ok   world layer")
    problems: list[str] = []
    for org in orgs(repo):
        overlay = Overlay.load(repo, org)
        counts = {
            name: len(getattr(overlay, name))
            for name in (
                "components", "signals", "claims", "scenarios", "outcomes", "people", "edges",
                "perspectives", "regrades",
            )
        }
        print(f"  ok   overlay {org}: " + ", ".join(f"{v} {k}" for k, v in counts.items() if v))
        # The half of evidence-grade immutability that reads git history (build ticket 18). It
        # lives here rather than in the loader because it costs a process per commit per graded
        # file, and this is the gate an author or CI runs before the commit.
        found = evidence.history_violations(repo, overlay.ref.path, overlay.ref.tree, overlay.regrades)
        if found:
            problems += found
            for violation in found:
                print(f"  FAIL {violation}")
        else:
            print(f"       {org}: every recorded evidence-grade change carries a regrade event")
        try:
            gated = BehaviouralOverlay.load(repo, org)
        except ModelError:
            print(f"       {org} has no behavioural overlay (the default, and the supported state)")
        else:
            print(
                f"  ok   {org} behavioural overlay: {len(gated.observations)} cohort observations, "
                f"DPIA {gated.meta['dpia']}, advisory only, {gated.meta['retention_days']}-day retention"
            )
    if problems:
        print(
            f"\nFAIL: {len(problems)} evidence grade(s) moved with no regrade event. A grade is "
            "immutable without one recording who moved it and why."
        )
        return 1
    print("PASS: every object validates against its closed schema")
    return 0


def cmd_index(args: argparse.Namespace) -> int:
    repo = ModelRepo.open(args.repo, args.ref)
    out = index.write(repo, args.out)
    print(f"derived index -> {out}  ({index.read_digest(out)[:16]})")
    print("  derived, never authoritative: drop it and rebuild from the repository alone")
    return 0


def cmd_fixture(args: argparse.Namespace) -> int:
    root = fixtures.build_pocket_org(args.out) if args.pocket_org else fixtures.build(args.out)
    print(f"{'pocket-org' if args.pocket_org else 'fixture'} model repository -> {root}")
    print("  deterministic: same content, same commit sha, on every machine")
    return 0


# -- grades ---------------------------------------------------------------------------------


def cmd_grade(args: argparse.Namespace) -> int:
    caps = Capabilities.load()
    for graded in caps:
        if args.capability and graded.capability != args.capability:
            continue
        checked = sum(1 for c in graded.criteria if c.checked)
        _say(
            f"{graded.capability}: {graded.grade}  ({checked}/{len(graded.criteria)} of "
            f"decision ticket {graded.owning_ticket})"
        )
        for c in graded.criteria:
            mark = "x" if c.checked else " "
            print(f"  [{mark}] {c.index}. {c.text}")
            if c.checked:
                print(f"        {c.ticked_by}: {c.evidence}")
    return 0


# -- the invariant suite ----------------------------------------------------------------------


def cmd_verify(args: argparse.Namespace) -> int:
    if args.artefact and args.attestation:
        return _attestation(args.artefact)
    if args.artefact:
        _show_challenges(args.artefact, args.challenge)
        return _reproduce(args.artefact, args.repo)
    if args.rehash:
        return _rehash(args.authorise)
    if args.bless_goldens:
        return _bless_goldens(args.authorise)

    suite = Suite()
    if args.list:
        for number, (name, is_invariant) in enumerate(suite.plan(), start=1):
            entry = next((e for e in suite.manifest if e.name == name), None)
            kind = "invariant" if is_invariant else "harness"
            state = f" [{entry.state}]" if entry else ""
            print(f"{number:>3}  {kind:<9} {name}{state}")
        return 0

    _say(f"twin invariant suite (tool {TOOL_VERSION})")
    results, ok = invariants.run(only=args.only or None)
    live = {e.name for e in suite.manifest if e.state == LIVE}

    for r in results:
        print(f"{r.number:>3}  {r.status:<4}  {r.name:<44}  {r.detail}")

    passed = sum(1 for r in results if r.status == PASS)
    failed = [r for r in results if r.status == FAIL]
    skipped = [r for r in results if r.status == SKIP]
    pending = [r for r in skipped if r.invariant and r.name not in live]
    honest = [r for r in skipped if r not in pending]

    print()
    print(
        f"RESULT: {passed} passed, {len(failed)} failed, {len(skipped)} skipped "
        f"({len(pending)} pending invariants, {len(honest)} skipped and not faked)"
    )
    if failed:
        for r in failed:
            print(f"  FAIL {r.name}: {r.detail}")
    return 0 if ok else 1


def _attestation(artefact_path: str) -> int:
    """Read the sidecar back. A write-only attestation is not tamper-evidence (build ticket 11)."""
    path = attest.sidecar_for(artefact_path)
    if not path.is_file():
        print(f"no attestation sidecar at {path}", file=sys.stderr)
        return 2
    doc = attest.load(path)
    problems = attest.check(doc, Path(artefact_path).read_bytes())
    _say(f"checking {path.name} against {artefact_path}")
    print(f"  subject      {doc['subject']['kind']} {doc['subject']['sha256'][:16]} ({doc['mark']})")
    signatures = doc.get("human_involvement", {}).get("signatures") or []
    for signature in signatures:
        print(f"  human        role {signature.get('role')!r}, asserts {signature.get('asserts')}")
    agent_signature = doc.get("agent_signature")
    print(
        f"  agent        {agent_signature['value'][:16]}, asserts origin only"
        if agent_signature
        else f"  agent        none ({doc.get('signature_status')})"
    )
    if problems:
        for problem in problems:
            print(f"  FAIL {problem}")
        print("\nANOMALY: this attestation does not hold.")
        return 1
    print(
        "\nHOLDS: the sidecar attests these exact bytes, and "
        + ("a role is accountable for the judgement inside." if doc["mark"] == AUTHORED
           else "no human touched this derived artefact.")
    )
    return 0


def cmd_sign(args: argparse.Namespace) -> int:
    """Sign an authored artefact as a role. Refuses a derived one — that is the whole invariant."""
    from .artefact import load as load_artefact

    material = sign.signing_key()
    if material is None:
        print(f"twin sign: no signing key; set {sign.KEY_ENV}", file=sys.stderr)
        return 2

    doc = load_artefact(args.artefact)
    if doc["envelope"]["mark"] != AUTHORED:
        print(
            f"twin sign: {args.artefact} is marked {doc['envelope']['mark']!r}. Only an authored "
            "artefact carries a human signature; derived_never_human_signed forbids the rest.",
            file=sys.stderr,
        )
        return 2

    sidecar = attest.sidecar_for(args.artefact)
    if not sidecar.is_file():
        print(f"twin sign: no attestation sidecar at {sidecar}", file=sys.stderr)
        return 2

    raw = Path(args.artefact).read_bytes()
    signature = sign.human(args.role, sha256_hex(raw), material)
    existing = attest.load(sidecar)
    existing["human_involvement"] = {"present": True, "signatures": [signature]}
    sidecar.write_bytes(canonical_json(existing))
    print(f"signed {args.artefact} as role {args.role!r} -> {sidecar.name}")
    print("  asserts accountability for the judgement inside, and nothing about reproducibility")
    return 0


def _show_challenges(artefact_path: str, challenge_paths: list[str]) -> None:
    """Challenges are visible wherever the challenged artefact is visible (build ticket 60) — so
    inspecting an artefact through `twin verify` is where they show, not a separate queue a reader
    has to know to check."""
    if not challenge_paths:
        return
    from . import challenges
    from .artefact import digest_of_file
    from .artefact import load as load_artefact

    artefact_sha256 = digest_of_file(artefact_path)
    docs = [load_artefact(p) for p in challenge_paths]
    known_challenges = [d for d in docs if d["envelope"]["kind"] == challenges.KIND_CHALLENGE]
    known_resolutions = [d for d in docs if d["envelope"]["kind"] == challenges.KIND_RESOLUTION]
    report = challenges.for_artefact(artefact_sha256, known_challenges, known_resolutions)
    if not report["open"] and not report["resolved"]:
        return
    _say(f"challenges against {artefact_path}")
    for entry in report["open"]:
        print(f"  OPEN     {entry['claim_path']:<40} {entry['reason']}")
    for entry in report["resolved"]:
        print(f"  resolved {entry['claim_path']:<40} {entry['response']}")
    print()


def _reproduce(artefact_path: str, repo_path: str | None) -> int:
    """`twin verify <artefact>` — recompute it from its pins and say whether it reproduces."""
    from .reproduce import reproduce

    if not repo_path:
        print(
            "twin verify <artefact> needs --repo: the pin records which model tree was read, "
            "not where that repository lives on this machine.",
            file=sys.stderr,
        )
        return 2
    report = reproduce(repo_path, artefact_path)
    _say(f"reproducing {artefact_path} from its pins")
    for link in report.chain:
        mark = "ok  " if link.reproduces else "FAIL"
        print(f"  {mark} {link.kind:<18} {link.actual[:16]} (recorded {link.expected[:16]})")
    mark = "ok  " if report.expected == report.actual else "FAIL"
    print(f"  {mark} {report.kind:<18} {report.actual[:16]} (recorded {report.expected[:16]})")
    print("  tolerance: none — byte identity. Scores carry a declared "
          f"{__import__('twin.scoring', fromlist=['x']).SIGNIFICANT_DIGITS}-significant-digit quantisation in the format.")
    if report.reproduces:
        print("\nREPRODUCES: the pins are sufficient to recompute this artefact exactly.")
        return 0
    if report.diff:
        print("\ndiverged:")
        print(report.diff)
    print("\nDIVERGES: the recorded pins do not recompute this artefact. The attestation is a claim, not a proof.")
    return 1


def _rehash(authorise: str | None) -> int:
    """Re-pin the check-body hashes. Deliberately awkward: it is how a refusal gets weakened."""
    from .invariants import body_hash, registry
    from .invariants.checks import module_hash

    checks = registry()
    wanted = {e.name: body_hash(checks[e.name]) for e in load_manifest() if e.state == LIVE}
    text = MANIFEST_PATH.read_text(encoding="utf-8")

    changed: list[str] = []
    head, blocks = _split_manifest(text)
    module_was = re.search(r"^checks_module_sha256:\s*(\S+)", "\n".join(head), re.M)
    if module_was and module_was.group(1) not in ("TBD", module_hash()):
        changed.append("checks_module_sha256")

    rewritten: list[list[str]] = []
    for block in blocks:
        name = _entry_name(block)
        if name not in wanted:
            rewritten.append(block)
            continue
        was = re.search(r"^\s*body_sha256:\s*(\S+)", "\n".join(block), re.M)
        if was and was.group(1) not in ("TBD", wanted[name]):
            changed.append(name)
        rewritten.append(_set_key(block, "body_sha256", wanted[name], after="state"))

    if changed and not _cites(authorise):
        print(
            "refusing to re-pin: "
            + ", ".join(sorted(set(changed)))
            + " already had a hash. Pass --authorise \"decision ticket NN — reason\".",
            file=sys.stderr,
        )
        return 1

    if changed:
        citation = json.dumps(authorise)
        rewritten = [
            _set_key(block, "authorised_by", citation, after="body_sha256")
            if _entry_name(block) in changed
            else block
            for block in rewritten
        ]
        if "checks_module_sha256" in changed:
            head = _set_top(head, "checks_module_authorised_by", citation)

    head = _set_top(head, "checks_module_sha256", module_hash())
    lines = head + [line for block in rewritten for line in block]
    MANIFEST_PATH.write_text("\n".join(lines).rstrip("\n") + "\n", encoding="utf-8")
    print(f"manifest re-pinned ({len(wanted)} live checks, module {module_hash()[:12]})")
    if changed:
        print(f"  authorised change to: {', '.join(sorted(set(changed)))}")
    return 0


def _split_manifest(text: str) -> tuple[list[str], list[list[str]]]:
    """Everything before the first entry, then one line-block per entry."""
    lines = text.splitlines()
    starts = [i for i, line in enumerate(lines) if re.match(r"\s*- name:\s*\S+", line)]
    if not starts:
        return lines, []
    bounds = starts + [len(lines)]
    return lines[: starts[0]], [lines[a:b] for a, b in zip(bounds, bounds[1:])]


def _drop_key(block: list[str], key: str) -> list[str]:
    """Remove `key:` and any continuation lines belonging to it (block scalars span lines)."""
    out: list[str] = []
    indent: int | None = None
    for line in block:
        match = re.match(rf"^(\s*){re.escape(key)}:", line)
        if match:
            indent = len(match.group(1))
            continue
        if indent is not None:
            if line.strip() and len(line) - len(line.lstrip()) > indent:
                continue
            indent = None
        out.append(line)
    return out


def _entry_name(block: list[str]) -> str:
    match = re.match(r"\s*- name:\s*(\S+)", block[0])
    return match.group(1) if match else ""


def _set_key(block: list[str], key: str, value: str, after: str) -> list[str]:
    block = _drop_key(block, key)
    out: list[str] = []
    placed = False
    for line in block:
        out.append(line)
        anchor = re.match(rf"^(\s*){re.escape(after)}:", line)
        if anchor and not placed:
            out.append(f"{anchor.group(1)}{key}: {value}")
            placed = True
    if not placed:  # no anchor line: append at the end of the block, at the entry's indent
        indent = " " * (len(block[0]) - len(block[0].lstrip()) + 2)
        out.append(f"{indent}{key}: {value}")
    return out


def _set_top(head: list[str], key: str, value: str) -> list[str]:
    """Set a top-level scalar, above `invariants:` — anything after it belongs to the list."""
    out = [line for line in head if not re.match(rf"^{re.escape(key)}:", line)]
    try:
        insert = next(i for i, line in enumerate(out) if re.match(r"^invariants:", line))
    except StopIteration:
        insert = len(out)
    out.insert(insert, f"{key}: {value}")
    return out


def _bless_goldens(authorise: str | None) -> int:
    """Re-record the committed artefact digests the cross-architecture check compares against.

    Gated like `--rehash`, and for the same reason: the goldens are the only thing that catches a
    change in what the engine computes, so re-blessing them is how a scoring rule or a
    serialisation gets quietly replaced. Recording them for the first time needs no citation.
    """
    from .invariants.checks import GOLDEN_PATH, golden_digests, recompute_digests
    from .invariants.harness import context

    with tempfile.TemporaryDirectory(prefix="twin-goldens-") as handle:
        ctx = context(Path(handle))
        digests = recompute_digests(ctx)
        capabilities_digest = ctx.caps.digest

    previous = golden_digests()
    moved = sorted(k for k in previous if previous[k] != digests.get(k))
    if moved and not _cites(authorise):
        print(
            f"refusing to re-bless: {', '.join(moved)} already had a golden digest. "
            'Pass --authorise "decision ticket NN — reason".',
            file=sys.stderr,
        )
        return 1
    GOLDEN_PATH.write_text(
        json.dumps(
            {
                "note": "Artefact digests from the fixture model repository. Byte-identity given "
                "the pins is the property; these are what a second architecture must reproduce.",
                "tool_version": TOOL_VERSION,
                "capabilities_digest": capabilities_digest,
                "authorised_by": authorise,
                "digests": digests,
            },
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )
    print(f"golden digests -> {GOLDEN_PATH.name} ({len(digests)} artefacts)")
    for kind, digest in sorted(digests.items()):
        print(f"  {kind:<18} {digest}")
    return 0


def _cites(text: str | None) -> bool:
    return bool(text and re.search(r"decision ticket\s+\d{1,2}", text, re.I))


# -- wiring -----------------------------------------------------------------------------------


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="twin", description=__doc__.splitlines()[0])
    parser.add_argument("--version", action="version", version=f"twin {TOOL_VERSION}")
    subs = parser.add_subparsers(dest="verb", required=True)

    def with_repo(sub: argparse.ArgumentParser) -> argparse.ArgumentParser:
        sub.add_argument("--repo", required=True, help="path to the model repository")
        sub.add_argument("--ref", default="HEAD", help="git ref to pin (default HEAD)")
        return sub

    def with_org(sub: argparse.ArgumentParser) -> argparse.ArgumentParser:
        sub.add_argument("--org", default=None, help="which overlay; required when there is more than one")
        return sub

    sense = with_org(with_repo(subs.add_parser("sense", help="bind a dated signal to a component")))
    sense.add_argument("--signal", required=True)
    sense.add_argument("--out", required=True)
    sense.set_defaults(fn=cmd_sense)

    run = with_org(with_repo(subs.add_parser("run", help="execute a scenario; emits forecasts, plural")))
    run.add_argument("--scenario", required=True)
    # Required, with no default (build ticket 36). The regime a default would pick is the one
    # whose forecasts score, so an omitted flag would be a silent claim to the honest gate.
    run.add_argument(
        "--regime", required=True, choices=list(REGIMES),
        help="the information gate this execution runs under; no default, and only as-consumed scores",
    )
    run.add_argument("--at", default=None, help="override the scenario's declared time")
    run.add_argument("--out", required=True)
    run.set_defaults(fn=cmd_run)

    gap = with_org(with_repo(subs.add_parser(
        "regimes", help="one scenario under all three regimes, with the two gaps computed"
    )))
    gap.add_argument("--scenario", required=True)
    gap.add_argument("--at", default=None, help="override the scenario's declared time")
    gap.add_argument("--out", required=True)
    gap.set_defaults(fn=cmd_regimes)

    priced = with_org(with_repo(subs.add_parser(
        "price", help="a shock priced under every declared perspective, with the responses beside it"
    )))
    priced.add_argument("--origin", required=True, help="the component the shock starts at")
    priced.add_argument(
        "--perspective", action="append", default=[],
        help="repeatable; with none given, every perspective in the overlay is priced",
    )
    priced.add_argument("--out", required=True)
    priced.set_defaults(fn=cmd_price)

    drifted = subs.add_parser(
        "drift", help="the Flux drift measurement so far — coverage, events, and no verdict"
    )
    drifted.set_defaults(fn=cmd_drift)

    positioned = with_org(with_repo(subs.add_parser(
        "positions", help="believed map, rival forecasts, revealed truth — and the deltas between them"
    )))
    positioned.add_argument("--scenario", required=True)
    positioned.add_argument("--out", required=True)
    positioned.set_defaults(fn=cmd_positions)

    credenced = with_org(with_repo(subs.add_parser(
        "credibility", help="blend a world-layer prior with an org's own sparse data"
    )))
    credenced.add_argument("--subject", required=True, help="the subject a world-layer prior names")
    credenced.add_argument("--out", required=True)
    credenced.set_defaults(fn=cmd_credibility)

    accounted = with_org(with_repo(subs.add_parser(
        "causal-accounts", help="rival causal accounts, each propagated independently, and the spread between them"
    )))
    accounted.add_argument("--origin", required=True, help="the component the shock starts at")
    accounted.add_argument(
        "--account", action="append", required=True, default=[],
        help="a causal-account id (this overlay's own edges may be named too); repeatable, at least two",
    )
    accounted.add_argument("--out", required=True)
    accounted.set_defaults(fn=cmd_causal_accounts)

    traded = with_org(with_repo(subs.add_parser(
        "trade-off", help="net cost of risk per response, across rival causal accounts, with a marked default"
    )))
    traded.add_argument("--origin", required=True, help="the component the shock starts at")
    traded.add_argument("--perspective", required=True, help="whose £ the curve is drawn in")
    traded.add_argument(
        "--account", action="append", required=True, default=[],
        help="a causal-account id (this overlay's own edges may be named too); repeatable, at least two",
    )
    traded.add_argument("--out", required=True)
    traded.set_defaults(fn=cmd_trade_off)

    score = with_org(with_repo(subs.add_parser("score", help="score a forecast bundle against an outcome")))
    score.add_argument("--forecast", required=True, help="path to a forecast-bundle artefact")
    score.add_argument("--outcome", required=True)
    score.add_argument(
        "--discount-enron", action="append", default=[],
        help="path to a score-card artefact scored against the Enron contamination control; repeatable "
             "(build ticket 40) — with --discount-obscure, folds a measured memorisation-leakage "
             "discount into this score card",
    )
    score.add_argument(
        "--discount-obscure", action="append", default=[],
        help="path to a score-card artefact scored against a low-notoriety key (Carillion or NMC, not "
             "Wirecard); repeatable",
    )
    score.add_argument(
        "--discount-rule", default="brier", choices=list(RULES),
        help="the scoring rule the discount is measured in",
    )
    score.add_argument("--out", required=True)
    score.set_defaults(fn=cmd_score)

    swept = subs.add_parser(
        "sweep",
        help="run every scenario in every org, across a named org of repositories — unconditionally",
    )
    swept.add_argument(
        "--repo", action="append", required=True, default=[],
        help="path to a model repository; repeatable — the standing set spans an org of repositories",
    )
    swept.add_argument("--ref", default="HEAD", help="git ref to pin, applied to every named repository")
    swept.add_argument("--at", default=None, help="override every scenario's declared time")
    swept.add_argument("--out", required=True)
    swept.set_defaults(fn=cmd_sweep)

    diagram = subs.add_parser("reliability", help="a reliability diagram over a population of score cards")
    diagram.add_argument(
        "--score-card", action="append", required=True, default=[],
        help="path to a score-card artefact; repeatable",
    )
    diagram.add_argument("--bins", type=int, default=10)
    diagram.add_argument("--out", required=True)
    diagram.set_defaults(fn=cmd_reliability)

    sev = subs.add_parser(
        "severity", help="a loss-exceedance curve over a declared lognormal-body/GPD-tail severity"
    )
    sev.add_argument("--mu", type=float, required=True, help="the lognormal body's underlying-normal mean")
    sev.add_argument("--sigma", type=float, required=True, help="the lognormal body's underlying-normal sigma")
    sev.add_argument("--threshold", type=float, required=True, help="the peaks-over-threshold cut, authored")
    sev.add_argument("--xi", type=float, required=True, help="the GPD tail's shape parameter")
    sev.add_argument("--beta", type=float, required=True, help="the GPD tail's scale parameter")
    sev.add_argument(
        "--alpha", type=float, action="append", required=True, default=[],
        help="a confidence level for the curve; repeatable",
    )
    sev.add_argument("--out", required=True)
    sev.set_defaults(fn=cmd_severity)

    anchor = subs.add_parser(
        "severity-anchor", help="a loss-exceedance curve fit from twin/severity-anchors.yaml's cited quantiles"
    )
    anchor.add_argument("--subject", required=True, help="a subject id from twin/severity-anchors.yaml")
    anchor.add_argument(
        "--alpha", type=float, action="append", required=True, default=[],
        help="a confidence level for the curve; repeatable",
    )
    anchor.add_argument(
        "--sensitivity-xi", type=float, action="append", default=[],
        help="sweep the unanchored xi across these values at the highest --alpha; repeatable",
    )
    anchor.add_argument("--out", required=True)
    anchor.set_defaults(fn=cmd_severity_anchor)

    graph = with_org(with_repo(subs.add_parser("graph", help="emit the typed knowledge graph")))
    graph.add_argument("--out", required=True)
    graph.set_defaults(fn=cmd_graph)

    wmap = with_org(with_repo(subs.add_parser("map", help="render the Wardley map from the graph")))
    wmap.set_defaults(fn=cmd_map)

    radius = with_org(with_repo(subs.add_parser(
        "blast", help="what is downstream of a component, and which of it may be priced"
    )))
    radius.add_argument("--origin", required=True, help="the component the shock starts at")
    radius.add_argument("--out", required=True)
    radius.set_defaults(fn=cmd_blast)

    exposed = with_org(with_repo(subs.add_parser(
        "exposure", help="a scenario valued under each declared perspective"
    )))
    exposed.add_argument("--scenario", required=True)
    exposed.add_argument(
        "--perspective", action="append", default=[],
        help="repeatable; with none given, every perspective in the overlay is reported",
    )
    exposed.add_argument("--out", required=True)
    exposed.set_defaults(fn=cmd_exposure)

    moved = with_org(with_repo(subs.add_parser(
        "propagate", help="compose a shock through the causal layer, with depth attenuation"
    )))
    moved.add_argument("--origin", required=True, help="the component the shock starts at")
    moved.add_argument("--out", required=True)
    moved.set_defaults(fn=cmd_propagate)

    # Two subcommands rather than one with a flag, for the reason `Do` and `Observe` are two
    # types: a boolean is one typo away from an intervention that rewrites its own causes.
    acted = with_org(with_repo(subs.add_parser(
        "intervene", help="do(x): cut the incoming causal edges and propagate downstream only"
    )))
    acted.add_argument("--component", required=True, help="the component acted on")
    acted.add_argument("--out", required=True)
    acted.set_defaults(fn=cmd_intervene)

    learned = with_org(with_repo(subs.add_parser(
        "observe", help="observe(x): belief updates downstream and about the causes too"
    )))
    learned.add_argument("--component", required=True, help="the component observed")
    learned.add_argument("--out", required=True)
    learned.set_defaults(fn=cmd_observe)

    past = with_org(subs.add_parser(
        "rewind", help="the model state at a declared time (Pearl's abduction)"
    ))
    past.add_argument("--repo", required=True, help="path to the model repository")
    past.add_argument("--at", required=True, help="an ISO time; the last commit at or before it")
    past.add_argument("--out", required=True)
    past.set_defaults(fn=cmd_rewind)

    backtested = with_org(subs.add_parser(
        "backtest", help="rewind plus projection: what the model would have forecast as of a past time"
    ))
    backtested.add_argument("--repo", required=True, help="path to the model repository")
    backtested.add_argument("--at", required=True, help="an ISO time; rewinds to it, then runs the scenario as of it")
    backtested.add_argument("--scenario", required=True)
    backtested.add_argument(
        "--regime", required=True, choices=list(REGIMES),
        help="the information gate this execution runs under; no default, and only as-consumed scores",
    )
    backtested.add_argument("--out", required=True)
    backtested.set_defaults(fn=cmd_backtest)

    choices = with_org(with_repo(subs.add_parser(
        "options", help="the choice set after the constraint pre-filter, with survivors costed"
    )))
    choices.add_argument("--perspective", required=True, help="whose constraint set filters the options")
    choices.add_argument("--out", required=True)
    choices.set_defaults(fn=cmd_options)

    published = subs.add_parser(
        "constraints", help="publish the constraint set, the scope exclusions and the positions"
    )
    published.add_argument("--out", required=True)
    published.set_defaults(fn=cmd_constraints)

    challenged = subs.add_parser(
        "challenge", help="raise a challenge against one claim in an existing artefact"
    )
    challenged.add_argument("--artefact", required=True, help="path to the artefact being challenged")
    challenged.add_argument(
        "--claim-path", required=True,
        help="the dotted key-path into the artefact's body naming the disputed claim",
    )
    challenged.add_argument("--reason", required=True)
    challenged.add_argument("--role", default="challenger")
    challenged.add_argument("--out", required=True)
    challenged.set_defaults(fn=cmd_challenge)

    resolved = subs.add_parser("resolve-challenge", help="resolve a challenge, naming only what it named")
    resolved.add_argument("--challenge", required=True, help="path to the challenge artefact being resolved")
    resolved.add_argument("--response", required=True)
    resolved.add_argument("--role", default="challenge-resolver")
    resolved.add_argument("--out", required=True)
    resolved.set_defaults(fn=cmd_resolve_challenge)

    validate = with_repo(subs.add_parser("validate", help="validate every object against its schema"))
    validate.set_defaults(fn=cmd_validate)

    idx = with_repo(subs.add_parser("index", help="build the derived index (never authoritative)"))
    idx.add_argument("--out", required=True)
    idx.set_defaults(fn=cmd_index)

    fixture = subs.add_parser("fixture", help="build the deterministic fixture model repository")
    fixture.add_argument("--out", required=True)
    fixture.add_argument(
        "--pocket-org", action="store_true", help="build the pocket-org golden fixture instead"
    )
    fixture.set_defaults(fn=cmd_fixture)

    sheet = with_org(subs.add_parser("worksheet", help="check the pocket org against its hand-computed worksheet"))
    sheet.add_argument("--repo", default=None, help="path to a pocket-org model repository")
    sheet.add_argument("--ref", default="HEAD", help="git ref to pin (default HEAD)")
    sheet.add_argument("--emit", default=None, help="write the worksheet as an authored artefact")
    sheet.set_defaults(fn=cmd_worksheet)

    signer = subs.add_parser("sign", help="sign an authored artefact as a role")
    signer.add_argument("artefact", help="path to an authored artefact")
    signer.add_argument("--role", required=True, help=f"one of: {', '.join(sign.role_ids())}")
    signer.set_defaults(fn=cmd_sign)

    grade = subs.add_parser("grade", help="show computed depth grades")
    grade.add_argument("--capability", default=None)
    grade.set_defaults(fn=cmd_grade)

    verify = subs.add_parser("verify", help="run the invariant suite, or reproduce an artefact")
    verify.add_argument("artefact", nargs="?", help="an artefact to recompute from its pins")
    verify.add_argument("--repo", default=None, help="the model repository the pins refer to")
    verify.add_argument(
        "--attestation", action="store_true", help="check the artefact's sidecar rather than replaying it"
    )
    verify.add_argument(
        "--challenge", action="append", default=[],
        help="path to a challenge or resolution artefact; repeatable, shown against `artefact` if it applies",
    )
    verify.add_argument("--only", action="append", default=[], help="check name or number; repeatable")
    verify.add_argument("--list", action="store_true", help="list the checks without running them")
    verify.add_argument("--rehash", action="store_true", help="re-pin check-body hashes in the manifest")
    verify.add_argument("--authorise", default=None, help="decision ticket authorising a hash change")
    verify.add_argument(
        "--bless-goldens", action="store_true", help="re-record the committed artefact digests"
    )
    verify.set_defaults(fn=cmd_verify)

    return parser


REFUSALS = (
    RepoError,
    ModelError,
    VerbError,
    AttenuationError,
    ConstraintError,
    DriftError,
    EvidenceError,
    PertError,
    PrimitiveError,
    RegimeError,
    GradeError,
    ArtefactError,
    AttestationError,
    BlobRefError,
    IndexError_,
    ReproduceError,
    SchemaError,
    ScoreError,
    SignatureError,
    yaml.YAMLError,
    OSError,
    RecursionError,
)


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        result: int = args.fn(args)
        return result
    except REFUSALS as exc:
        # A refusal is a sentence, not a traceback. A tool that sells honest refusal should not
        # answer malformed input with a stack dump.
        print(f"twin {args.verb}: {type(exc).__name__}: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
