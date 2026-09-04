#!/usr/bin/env python3
"""step3_band.py — NORTH-STAR §4 step 3, the python half, offline: a priced residual that
crosses the adopter's OWN signed appetite band selects a different tier, and the proposer either
opens a pull request editing the tier DECLARATION — `posture.acme.io/tier` on the adopter's
governed Namespace manifest (ADR-0022), never the pod label, which is that declaration's output
and is clobbered at every admission — or HOLDS, because ticket 78's clamp only ever tightens.

BOTH outcomes are graded, every run. Which one is correct depends on what the party declares
today, so the step reads the declaration and decides: the LAND is right when the priced tier
tightens it, the HOLD is right when it does not. The other outcome is then reached on a
THROWAWAY COPY whose declaration this step rewrites itself — the same synthetic licence it
already takes with the fabricated residual and the fabricated prices[] entry, and the reason it
never has to touch driftwood's real `isolated` line to keep a green.

The manifest is found here the same way the proposer finds it and by a second implementation:
the one manifest in the adopter's repo whose Namespace document carries
`policy-as-versioned.dev/governed: "true"`. The pod manifest is carried into the throwaway copy
too, so this step can observe that the proposer leaves it alone.

Nothing is opened. `tier_pr.py run --dry-run` returns before it ever calls `gh` or a network
git. Each copy IS initialised as a git repository — otherwise the "no branch was created"
observation is a `git branch` that fails for being outside a repository whatever the proposer
did, which is not an observation at all — but it is a repository with NO remote and no
credential, so the non-dry-run path dies on its own `git fetch origin main` before it can push
or open anything, and the real repository is never the working directory of any of this.

The band is read from the adopter's own party.yaml (appetite.tolerance), never from a platform
fixture (ADR-0021). A party with no appetite is a MISSING INSTRUMENT and refuses (ADR-0020).
The selection is made BY the adopter's own published selection-policy package -- the version in
the PASS line is the one that picked, not a string read out of a file beside it -- with
platform/graded/cage.py as the cross-check the two must agree on (ADR-0021).

Exit 0 observed true; 3 could not look; 1 observed false.
"""
from __future__ import annotations

import copy
import glob
import importlib.util
import json
import os
import subprocess
import sys
import tempfile

import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
from _estate import ESTATE  # noqa: E402

# The gate never passes this. It exists so this step can be smoke-tested against a scratch
# estate (a fixture with the not-yet-published files planted) without touching a real unit.
if "--estate" in sys.argv:
    ESTATE = sys.argv[sys.argv.index("--estate") + 1]

PLATFORM = os.path.join(ESTATE, "platform")
TIER_PR = os.path.join(PLATFORM, "wargamer", "tier_pr.py")
TIER_LABEL = "posture.acme.io/tier"
GOVERNED_LABEL = "policy-as-versioned.dev/governed"


def governed_namespace_manifests(repo_dir):
    """Every COMMITTED manifest in the adopter's repo declaring a governed Namespace, read as
    YAML — deliberately a SECOND implementation of the proposer's own line-based search, so the
    two have to agree on which file carries the declaration. Committed only: an ignored scratch
    tree (`.work/`) is not a signed declaration and a merged PR could not carry it."""
    listed = subprocess.run(["git", "-C", repo_dir, "ls-files", "-z", "--", "*.yaml", "*.yml"],
                            capture_output=True, text=True)
    if listed.returncode != 0:
        skip(f"{repo_dir} is not a git clone, so which manifests are committed cannot be read")
    found = []
    for rel in sorted(x for x in listed.stdout.split("\0") if x):
        path = os.path.join(repo_dir, rel)
        try:
            with open(path) as fh:
                docs = list(yaml.safe_load_all(fh))
        except (yaml.YAMLError, OSError, UnicodeDecodeError):
            continue
        for doc in docs:
            if not isinstance(doc, dict) or doc.get("kind") != "Namespace":
                continue
            labels = ((doc.get("metadata") or {}).get("labels") or {})
            if str(labels.get(GOVERNED_LABEL, "")).lower() == "true":
                found.append(path)
                break
    return found


def declared_tier_of(path):
    """The tier the governed Namespace document in `path` declares today — read as YAML, the
    same second implementation as `governed_namespace_manifests()` and deliberately not
    `tier_pr.declared_tier()`'s line scan, so the two have to agree. A governed Namespace with
    no tier label declares `isolated` by ADR-0022 (fail closed), which is what the proposer's
    own `_tightens(None, ...)` assumes."""
    with open(path) as fh:
        for doc in yaml.safe_load_all(fh):
            if not isinstance(doc, dict) or doc.get("kind") != "Namespace":
                continue
            labels = ((doc.get("metadata") or {}).get("labels") or {})
            if str(labels.get(GOVERNED_LABEL, "")).lower() == "true":
                return str(labels[TIER_LABEL]) if labels.get(TIER_LABEL) else "isolated"
    return None


def rewrite_declared_tier(text, tier):
    """(text with the tier line rewritten to `tier`, how many lines moved).

    A line edit, so every other byte — comments, ordering, the governed label — survives, the
    same property `tier_pr.apply_tier_declaration()` keeps. ONLY EVER APPLIED TO A THROWAWAY
    COPY: this is how the step fabricates the declaration it needs to reach the outcome the
    real party's declaration does not produce today. The real manifest is opened read-only and
    is re-read at the end of the run to prove it."""
    out, moved = [], 0
    for line in text.splitlines(keepends=True):
        if line.strip().startswith(f"{TIER_LABEL}:"):
            indent = line[:len(line) - len(line.lstrip())]
            out.append(f'{indent}{TIER_LABEL}: "{tier}"\n')
            moved += 1
        else:
            out.append(line)
    return "".join(out), moved


def load_yaml(path):
    with open(path) as fh:
        return yaml.safe_load(fh) or {}


def skip(msg):
    print(f"SKIP: {' '.join(str(msg).split())}")  # one line: the verdict is the last line
    sys.exit(3)


def fail(msg):
    print(f"FAIL: {' '.join(str(msg).split())}")  # one line: the verdict is the last line
    sys.exit(1)


def adopters():
    for p in sorted(glob.glob(os.path.join(ESTATE, "*", "party.yaml"))):
        doc = load_yaml(p)
        if "adopter" in (doc.get("roles") or []):
            yield os.path.basename(os.path.dirname(p)), doc


def selfcheck():
    """Both judgements above, exercised on documents this step cannot make the real estate
    produce on demand — and, for the guards the estate never reaches at all, on the only
    material there is. Pure: no estate, no proposer, no temp dir.

    Every guard in `judge_held` and `judge_landed` has a case here. Three of judge_held's had
    none until 2026-09-04 (a proposal that is not a pull request, tiers the ladder cannot rank,
    and a `line_tier` that disagrees with the line this step priced), which made them guards
    nobody had ever seen bite."""
    order = ["baseline", "restricted", "quarantine", "isolated"]
    held = {"branch": "wargamer/retune-tier-driftwood-cage-tier-ico-feed",
            "proposal_kind": "pull_request", "held": "tighten-only", "line": "ico-feed",
            "line_tier": "restricted", "party_tier": "restricted", "current_tier": "isolated",
            "why": "strictest priced line is 'restricted'; the declaration says 'isolated'"}
    held_cases = [
        ("the real held document is accepted", [held], None),
        ("nothing proposed at all is caught", [], "proposed nothing"),
        ("a LANDED document is caught -- the clamp did not hold",
         [{**held, "landed": "dry-run"}], "LANDED"),
        ("an errored document is caught", [{k: v for k, v in held.items() if k != "why"} |
                                           {"error": "no governed Namespace"}], "error"),
        ("a document that is not held is caught",
         [{k: v for k, v in held.items() if k != "held"}], "held"),
        ("a hold that is not the tighten-only clamp is caught",
         [{**held, "held": "some-other-reason"}], "tighten-only"),
        ("a held proposal that is not a pull request is caught",
         [{**held, "proposal_kind": "issue"}], "not a pull request"),
        ("a hold naming a tier this estate does not rank is caught",
         [{**held, "current_tier": "infra"}], "does not rank"),
        ("a hold naming a party tier off the ladder is caught",
         [{**held, "party_tier": "quarantined"}], "does not rank"),
        ("a hold whose party tier TIGHTENS the declaration is caught -- that one should have "
         "landed", [{**held, "party_tier": "isolated", "current_tier": "restricted"}],
         "tightens"),
        ("a hold whose line_tier is not the tier this step priced is caught",
         [{**held, "line_tier": "quarantine"}], "this step priced it"),
        ("a hold that names no basis is caught",
         [{k: v for k, v in held.items() if k != "why"}], "why"),
    ]
    ns = "gitops/apps/namespace.yaml"
    diff = ('apiVersion: v1\nkind: Namespace\nmetadata:\n  name: driftwood\n  labels:\n'
            f'    {GOVERNED_LABEL}: "true"\n    {TIER_LABEL}: "restricted"\n')
    landed_doc = {"branch": "wargamer/retune-tier-driftwood-cage-tier-ico-feed",
                  "proposal_kind": "pull_request", "manifest": ns,
                  "landed": "dry-run", "diff": diff}
    landed_cases = [
        ("the real landed dry-run document is accepted", [landed_doc], None),
        ("nothing proposed at all is caught", [], "proposed nothing"),
        ("an errored document is caught",
         [{k: v for k, v in landed_doc.items() if k != "diff"} |
          {"error": "no governed Namespace"}], "error"),
        ("a HELD document is caught -- this one should have landed",
         [{k: v for k, v in landed_doc.items() if k != "landed"} |
          {"held": "tighten-only"}], "HELD"),
        ("a proposal that did not stop at the dry run is caught",
         [{**landed_doc, "landed": "https://github.com/x/y/pull/1"}], "dry run"),
        ("a proposal that is not a pull request is caught",
         [{**landed_doc, "proposal_kind": "issue"}], "not a pull request"),
        ("a proposal moving a manifest that is not the governed Namespace is caught",
         [{**landed_doc, "manifest": "deploy/pod.yaml"}], "governed Namespace"),
        ("a diff that declares the wrong tier is caught",
         [{**landed_doc, "diff": diff.replace('"restricted"', '"quarantine"')}],
         "does not declare"),
        ("a diff that declares no tier at all is caught",
         [{**landed_doc, "diff": f'kind: Namespace\n    {GOVERNED_LABEL}: "true"\n'}],
         "does not declare"),
        ("a diff that dropped the governed label is caught",
         [{**landed_doc, "diff": diff.replace(f'{GOVERNED_LABEL}: "true"\n', "")}],
         "dropped"),
    ]
    ok = True
    for name, docs, want in held_cases:
        got = judge_held(docs, "driftwood", "restricted", order)
        if want is None and got is not None:
            print(f"  selfcheck: held: {name}: unexpectedly rejected: {got}")
            ok = False
        elif want is not None and (got is None or want not in got):
            print(f"  selfcheck: held: {name}: wanted {want!r} in the reason, got {got!r}")
            ok = False
    for name, docs, want in landed_cases:
        got = judge_landed(docs, "driftwood", ns, "restricted")
        if want is None and got is not None:
            print(f"  selfcheck: landed: {name}: unexpectedly rejected: {got}")
            ok = False
        elif want is not None and (got is None or want not in got):
            print(f"  selfcheck: landed: {name}: wanted {want!r} in the reason, got {got!r}")
            ok = False
    # The synthetic licence itself: the rewrite that fabricates a declaration must move the
    # line it claims to move, and the YAML reader must read the tier back. A rewrite that
    # silently changed nothing would make the whole second leg a test of the first.
    text = ('kind: Namespace\nmetadata:\n  labels:\n'
            f'    {GOVERNED_LABEL}: "true"\n    {TIER_LABEL}: "isolated"   # a comment\n')
    new, moved = rewrite_declared_tier(text, "baseline")
    if moved != 1 or f'{TIER_LABEL}: "baseline"' not in new or GOVERNED_LABEL not in new:
        print(f"  selfcheck: rewrite_declared_tier moved {moved} line(s): {new!r}")
        ok = False
    if rewrite_declared_tier("kind: Namespace\n", "baseline")[1] != 0:
        print("  selfcheck: rewrite_declared_tier claimed to move a line that is not there")
        ok = False
    if not ok:
        print("FAIL: step3 selfcheck: the proposal-document judgements do not bite")
        return 1
    print(f"PASS: selfcheck: {len(held_cases)} held-document and {len(landed_cases)} "
          f"landed-document judgements bite -- the tighten-only hold and the dry-run pull "
          f"request are each accepted; nothing proposed, an error, the wrong one of hold/land, "
          f"a proposal that is not a pull request, tiers off the ladder, a line_tier that is "
          f"not the priced one, a hold with no basis, a diff on the wrong manifest, a diff "
          f"declaring the wrong tier and a diff that dropped the governed label are each "
          f"caught, and the throwaway rewrite that fabricates a declaration moves exactly the "
          f"line it says it does")
    return 0


def judge_held(landed, org, line_tier, order):
    """The observable fact NORTH-STAR §4 step 3 has to grade since ticket 78's tighten-only
    clamp: the proposer produced a HELD document of the right shape, and nothing landed.
    Returns None if the documents are what a held proposal looks like, else the reason.

    Pure so the selfcheck can drive it: the estate can only make the proposer emit ONE of
    these shapes today, and a judgement only ever exercised on the shape it happens to see is
    not a judgement."""
    if not landed:
        return (f"a residual crossing {org}'s band proposed nothing at all -- the proposer "
                f"must still emit the held document that says why it wrote nothing")
    p = landed[0]
    if "landed" in p:
        return (f"the proposer LANDED a proposal the tighten-only clamp should have held: "
                f"{json.dumps(p)[:300]}")
    if "error" in p:
        return f"the proposer errored instead of holding: {p['error']}"
    if p.get("held") != "tighten-only":
        return (f"the proposal is not held by the tighten-only clamp (held="
                f"{p.get('held')!r}): {json.dumps(p)[:300]}")
    if p.get("proposal_kind") != "pull_request":
        return (f"the held proposal is a {p.get('proposal_kind')!r}, not a pull request -- "
                f"every proposal is a PR (ADR-0022)")
    current, party = p.get("current_tier"), p.get("party_tier")
    if current not in order or party not in order:
        return (f"the held document names tiers this estate does not rank "
                f"(current={current!r}, party={party!r}); the ladder is {order}")
    if order.index(party) > order.index(current):
        return (f"the proposer HELD a proposal that tightens {current!r} to {party!r} -- a "
                f"tightening is the one thing the clamp must let through")
    if p.get("line_tier") != line_tier:
        return (f"the held document says the priced line selected {p.get('line_tier')!r}, but "
                f"this step priced it to {line_tier!r}")
    if not str(p.get("why") or "").strip():
        return "the held document carries no `why` -- a hold with no basis is not auditable"
    return None


def judge_landed(landed, org, want_manifest, want_tier):
    """The other observable fact of NORTH-STAR §4 step 3, and the one the file is named for:
    where the priced tier TIGHTENS what the party declares, the proposer opens a pull request
    that moves the tier declaration -- and moves nothing else.

    These are the assertions this step made until 2026-09-04, when the tighten-only clamp made
    driftwood's real declaration unable to reach them. They are back, graded against a copy
    whose declaration this step loosened itself. Returns None or the reason.

    Pure, for the same reason judge_held is: only one of the two shapes can be the real
    party's today, so the other is only ever fixtures."""
    if not landed:
        return (f"a residual crossing {org}'s band proposed nothing at all -- a priced tier "
                f"that tightens the declaration must reach a pull request")
    p = landed[0]
    if "error" in p:
        return f"the proposer errored instead of proposing: {p['error']}"
    if "held" in p:
        return (f"the proposer HELD a proposal whose tier TIGHTENS the declaration -- a "
                f"tightening is the one thing the clamp must let through: "
                f"{json.dumps(p)[:300]}")
    if p.get("landed") != "dry-run":
        return f"the proposer did not stop at the dry run: {json.dumps(p)[:300]}"
    if p.get("proposal_kind") != "pull_request":
        return (f"the crossing proposed a {p.get('proposal_kind')!r}, not a pull request "
                f"editing the tier declaration -- every proposal is a PR (ADR-0022 retired "
                f"the issue branch: the bottom rung is a running cage, so nothing is refused)")
    if p.get("manifest") != want_manifest:
        return (f"the proposal moves {p.get('manifest')!r}, not {org}'s governed Namespace "
                f"declaration {want_manifest!r} -- a merged edit to anything else is "
                f"overwritten at the next admission and changes nothing (ADR-0022)")
    diff = p.get("diff") or ""
    declared = [ln for ln in diff.splitlines() if ln.strip().startswith(f"{TIER_LABEL}:")]
    if not any(ln.strip() == f'{TIER_LABEL}: "{want_tier}"' for ln in declared):
        return (f"the proposed pull request does not declare {TIER_LABEL}: {want_tier} on "
                f"{want_manifest}: {declared or diff.strip()[:300]}")
    if GOVERNED_LABEL not in diff:
        return (f"the proposed edit dropped {GOVERNED_LABEL} from {want_manifest} -- the tier "
                f"must be declared next to it, on the same signed object")
    return None


def main():
    if "--selfcheck" in sys.argv or "selfcheck" in sys.argv[1:]:
        return selfcheck()
    return observe()


def observe():
    if not os.path.isdir(ESTATE):
        skip(f"{ESTATE} absent — run ./clone-estate.sh first")
    if not os.path.exists(TIER_PR):
        skip(f"{TIER_PR} absent — no proposer to run")

    chosen = None
    for name, doc in adopters():
        pkg = os.path.join(ESTATE, name, "selection-policy", "selection_policy.py")
        version_file = os.path.join(ESTATE, name, "selection-policy", "VERSION")
        if os.path.exists(pkg) and os.path.exists(version_file):
            chosen = (name, doc, version_file, pkg)
            break
    if chosen is None:
        skip("no adopter publishes a selection-policy package with a VERSION yet — the "
             "versioned package ticket 25 publishes in driftwood is what MAKES the selection")
    org, party, version_file, pkg = chosen
    with open(version_file) as fh:
        declared = fh.read().strip()
    # The package that will pick, imported from the adopter's own repo. A VERSION file that
    # disagrees with the package beside it means the attribution cannot be trusted either way.
    try:
        spec = importlib.util.spec_from_file_location(f"_selpol_{org}", pkg)
        policy = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(policy)
    except Exception as exc:                                    # noqa: BLE001
        fail(f"{org}'s own selection-policy package does not import, so no versioned rule "
             f"could have picked its tier: {exc!r}")
    policy_version = getattr(policy, "VERSION", None)
    if policy_version != declared:
        fail(f"{org}/selection-policy/VERSION says {declared!r} but the package beside it is "
             f"{policy_version!r} — a tier cannot be attributed to either")

    tol = ((party.get("appetite") or {}).get("tolerance") or {})
    if not isinstance(tol.get("amount"), (int, float)):
        fail(f"{org}/party.yaml declares no appetite.tolerance — a party with no appetite is a "
             f"MISSING INSTRUMENT and refuses (ADR-0020)")
    band, ccy = float(tol["amount"]), tol.get("currency")

    # The estate's engine prices the caged residuals; the ADOPTER's own package picks from
    # them. Both run over the same numbers and must agree -- a proposal that names a policy
    # version which did not in fact pick is the unfalsifiable claim this estate refuses.
    sys.path.insert(0, os.path.join(PLATFORM, "graded"))
    try:
        import cage  # noqa: E402
    except Exception as exc:                                    # noqa: BLE001
        skip(f"cannot import {PLATFORM}/graded/cage.py: {exc!r}")
    floor = (party.get("overlay") or {}).get("floor")

    def pick(ale):
        """The tier the adopter's OWN versioned package selects for this uncaged ALE."""
        residuals = {t: {"amount": cage.caged_residual(ale, t), "currency": ccy}
                     for t in cage.ORDER}
        try:
            chose = policy.select(residuals, {"amount": band, "currency": ccy}, floor)
        except Exception as exc:                                # noqa: BLE001
            fail(f"{org}'s own selection-policy package refused to pick at an uncaged residual "
                 f"of {ale:,.2f} {ccy}: {exc}")
        theirs, ours = chose["tier"], cage.select_tier(ale, band, floor)
        if theirs != ours:
            fail(f"at an uncaged residual of {ale:,.2f} {ccy}, {org}'s own selection-policy "
                 f"package picks {theirs!r} and platform/graded/cage.py picks {ours!r} — a "
                 f"proposal could name a version that did not pick (ADR-0021)")
        return theirs

    under = band * 0.5
    tier_under = pick(under)
    over, tier_over = under, tier_under
    for _ in range(4000):
        over *= 1.02
        tier_over = pick(over)
        if tier_over != tier_under:
            break
    if tier_over == tier_under:
        fail(f"no residual between {under:,.0f} and {over:,.0f} {ccy} changes {org}'s tier off "
             f"{tier_under} against its own band of {band:,.0f} {ccy} — the band selects nothing")
    print(f"    {org} band {band:,.0f} {ccy} (its own party.yaml), selection policy "
          f"{policy_version} ({os.path.relpath(version_file, ESTATE)})")
    print(f"    residual {under:,.2f} -> tier {tier_under}; {over:,.2f} (crosses the band) -> "
          f"tier {tier_over}")

    # The crossing, as one prices[] entry the proposer reads — the adopter's real committed
    # entry with the crossing residual on it, so nothing about the entry's shape is invented.
    real = os.path.join(ESTATE, org, "composed", "evidence.json")
    if not os.path.exists(real):
        skip(f"{org} has no composed/evidence.json to take a real prices[] entry from")
    with open(real) as fh:
        evidence = json.load(fh)
    if not evidence.get("prices"):
        fail(f"{org}'s composed evidence carries no prices[] to cross a band with")
    entry = copy.deepcopy(evidence["prices"][0])
    entry.update({"old_price": under, "new_price": over, "old_tier": tier_under,
                  "proposed_tier": tier_over, "changed": True, "proposed_as": "label",
                  "policy_version": policy_version})

    # The declaration this crossing must move: the adopter's governed Namespace manifest.
    declarations = governed_namespace_manifests(os.path.join(ESTATE, org))
    if not declarations:
        fail(f"{org} declares no Namespace carrying {GOVERNED_LABEL}: \"true\", so there is no "
             f"tier declaration for a band crossing to move (ADR-0022)")
    if len(declarations) > 1:
        fail(f"{org} carries {len(declarations)} governed Namespace manifests "
             f"({', '.join(os.path.relpath(d, ESTATE) for d in declarations)}) -- which one a "
             f"proposal moves is then not decidable")
    declaration = declarations[0]
    rel_declaration = os.path.relpath(declaration, os.path.join(ESTATE, org))
    pod_manifest = os.path.join(ESTATE, org, "deploy", "pod.yaml")
    declared_now = declared_tier_of(declaration)
    if declared_now is None:
        fail(f"{rel_declaration} was found by its governed label but its tier could not be "
             f"read back by this step's own YAML reader")

    declaration_on_disk = open(declaration).read()
    pod_on_disk = open(pod_manifest).read() if os.path.exists(pod_manifest) else None
    order = list(cage.ORDER)

    # --- what this step grades, and why (2026-09-04, delegated, ADR-0025) -----------------
    # Until ticket 78 this asserted a LANDED dry-run PR. Ticket 78 gave the proposer a
    # tighten-only clamp: the party's folded tier is never written when it does not tighten
    # what the governed Namespace declares today. driftwood declares `isolated` -- the top rung
    # of cage.ORDER -- since ticket 26, so no priced line can tighten it and the real fixture
    # reaches a HOLD, not a landed PR. tier_pr.py's own selfcheck asserts exactly that.
    #
    # THE THIRD OPTION, taken here. The 2026-09-04 repair recorded only two ways out -- drive a
    # different party, or re-point the step at the hold -- and said the only route to a landed
    # PR was loosening driftwood's REAL declaration, which would weaken the estate's posture to
    # keep a green. That was wrong: tier_pr.py reads `current` out of --adopter-dir, and this
    # step has always passed a THROWAWAY COPY as --adopter-dir. Writing a looser tier into the
    # COPY reaches the landed path with the real repository untouched -- the same synthetic
    # licence this step already takes with its fabricated residual and its fabricated prices[]
    # entry, and the technique tier_pr.py's own selfcheck uses. It is also what closes the
    # narrower defect: grading only the hold made ANY landed proposal a fault, so the day a
    # party declares a tier the priced line tightens, correct behaviour would read as a red.
    #
    # So both outcomes are graded, every run. The one that is correct against what the party
    # declares TODAY is run against a faithful copy; the complement is run against a copy whose
    # declaration this step rewrote itself, and the transcript says which is which.
    if order.index(tier_over) <= order.index(tier_under):
        fail(f"the crossing selected {tier_over} at the higher residual and {tier_under} at the "
             f"lower one, which is not stricter on {order} -- a band crossing that does not "
             f"tighten as the residual grows has no tighten-only outcome to grade")
    if declared_now in order and order.index(tier_over) > order.index(declared_now):
        real_outcome, real_note = "land", (
            f"{org} declares {declared_now} and the priced line selects {tier_over}, which "
            f"tightens it")
        synthetic_tier, synthetic_outcome = order[-1], "hold"
    else:
        real_outcome, real_note = "hold", (
            f"{org} declares {declared_now} and the priced line selects {tier_over}, which "
            f"does not tighten it")
        synthetic_tier, synthetic_outcome = tier_under, "land"

    legs = [("as declared", None, real_outcome), ("SYNTHETIC declaration", synthetic_tier,
                                                  synthetic_outcome)]
    results = {}
    with tempfile.TemporaryDirectory() as tmp:
        ev_path = os.path.join(tmp, "evidence.json")
        with open(ev_path, "w") as fh:
            json.dump({**evidence, "prices": [entry]}, fh)
        env = {k: v for k, v in os.environ.items() if k != "GITHUB_REPOSITORY"}
        env["GIT_TERMINAL_PROMPT"] = "0"

        for i, (leg, plant, want) in enumerate(legs):
            work = os.path.join(tmp, f"{i}-{org}")
            os.makedirs(os.path.dirname(os.path.join(work, rel_declaration)), exist_ok=True)
            text = declaration_on_disk
            if plant is not None:
                text, moved = rewrite_declared_tier(text, plant)
                if moved != 1:
                    fail(f"the throwaway copy's {TIER_LABEL} line could not be rewritten to "
                         f"{plant} ({moved} line(s) moved), so the {want} outcome has no "
                         f"material to be graded on")
            with open(os.path.join(work, rel_declaration), "w") as fh:
                fh.write(text)
            pod_before = None
            if pod_on_disk is not None:
                os.makedirs(os.path.join(work, "deploy"), exist_ok=True)
                with open(os.path.join(work, "deploy", "pod.yaml"), "w") as fh:
                    fh.write(pod_on_disk)
                pod_before = pod_on_disk
            # A real repository, with NO remote: `git branch` below then means something (it
            # listed nothing in a non-repo whatever the proposer did, which published a
            # refusal as an observation), and the proposer's non-dry-run path would die on its
            # own `git fetch origin main` long before it could push or open anything.
            for cmd in (["git", "init", "-q", "-b", "main", work],
                        ["git", "-C", work, "config", "user.email", "step3@invalid"],
                        ["git", "-C", work, "config", "user.name", "step3"],
                        ["git", "-C", work, "add", "-A"],
                        ["git", "-C", work, "commit", "-q", "-m", "throwaway copy"]):
                made = subprocess.run(cmd, capture_output=True, text=True)
                if made.returncode != 0:
                    skip(f"the throwaway copy could not be made a git repository "
                         f"({' '.join(cmd[:3])}): {(made.stderr or made.stdout).strip()[:200]}")
            planted = declared_tier_of(os.path.join(work, rel_declaration))
            want_current = plant if plant is not None else declared_now
            if planted != want_current:
                fail(f"the throwaway copy declares {planted!r}, not the {want_current!r} this "
                     f"leg is graded against")
            before = text

            r = subprocess.run([sys.executable, TIER_PR, "run", "--adopter-dir", work,
                                "--evidence", ev_path, "--org", org,
                                "--dry-run"], capture_output=True, text=True, env=env)
            if r.returncode != 0:
                # The proposer EXISTS (asserted above); one that will not run is the estate
                # failing to propose, which this step observed. Not a could-not-look.
                fail(f"tier_pr.py exited {r.returncode} on the {leg} leg, so the estate cannot "
                     f"propose the tier it selected: "
                     f"{(r.stderr or r.stdout).strip().splitlines()[-1:]}")
            after = open(os.path.join(work, rel_declaration)).read()
            pod_after = (open(os.path.join(work, "deploy", "pod.yaml")).read()
                         if pod_before is not None else None)
            branched = subprocess.run(
                ["git", "-C", work, "branch", "--format=%(refname:short)"],
                capture_output=True, text=True)
            if branched.returncode != 0:
                fail(f"`git branch` in the throwaway copy exited {branched.returncode}, so "
                     f"whether the {want} run branched was not looked at: "
                     f"{branched.stderr.strip()[:200]}")
            try:
                docs = json.loads(r.stdout)
            except ValueError:
                # stdout is the document stream. Anything else on it (a human note, a log line)
                # breaks every machine reader, so it is named as that rather than "bad JSON".
                fail(f"tier_pr.py --dry-run did not print a clean proposal document on stdout "
                     f"on the {leg} leg -- the document stream carries other text: "
                     f"{r.stdout.strip()[:200]}")

            if want == "hold":
                reason = judge_held(docs, org, tier_over, order)
            else:
                reason = judge_landed(docs, org, rel_declaration, tier_over)
            if reason:
                fail(f"[{leg}, declared {want_current}] {reason}")
            p = docs[0]
            if want == "hold" and p.get("current_tier") != want_current:
                fail(f"[{leg}] the hold is against {p.get('current_tier')!r}, but the copy it "
                     f"ran on declares {want_current!r} -- the clamp read a different "
                     f"declaration from the one this step planted")
            if after != before:
                fail(f"[{leg}] the {want} run edited {rel_declaration} in the throwaway copy; "
                     f"a --dry-run writes nothing anywhere")
            if pod_after is not None and pod_after != pod_before:
                fail(f"[{leg}] the {want} run edited the adopter's pod manifest -- the pod "
                     f"label is cage-tier's OUTPUT and never a thing a proposal moves "
                     f"(ADR-0022)")
            extra = [b for b in branched.stdout.split() if b != "main"]
            if extra:
                fail(f"[{leg}] the {want} run created branch(es) {extra} in the throwaway copy "
                     f"-- a --dry-run branches nothing, held or landed")
            results[want] = (leg, want_current, p)

    # The real repository is byte-for-byte what it was before either leg ran. Both copies were
    # made from these strings and neither was ever the proposer's working directory.
    if open(declaration).read() != declaration_on_disk:
        fail(f"{rel_declaration} changed in {org}'s real repository during this run -- this "
             f"step proposes against throwaway copies and writes to the estate never")
    if pod_on_disk is not None and open(pod_manifest).read() != pod_on_disk:
        fail(f"deploy/pod.yaml changed in {org}'s real repository during this run")

    hold_leg, hold_current, hp = results["hold"]
    land_leg, land_current, lp = results["land"]
    print(f"    HOLD  [{hold_leg}, declared {hold_current}]: {hp['proposal_kind']}, "
          f"held={hp['held']} on line {hp['line']}; the priced line selects {hp['line_tier']} "
          f"and the party folds to {hp['party_tier']}, which does not tighten it: {hp['why']}")
    print(f"    LAND  [{land_leg}, declared {land_current}]: {lp['proposal_kind']}, "
          f"landed={lp['landed']} on {lp['manifest']}; the diff declares {TIER_LABEL}: "
          f"\"{tier_over}\" and keeps {GOVERNED_LABEL}")
    print(f"    both legs: no branch beyond the copy's own main, nothing written in either "
          f"copy, {rel_declaration} and deploy/pod.yaml byte-identical in {org}'s real "
          f"repository, nothing opened")
    # 2026-08-29 review: this used to read "a residual crossing {org}'s own
    # appetite band", which a deck reader takes as "{org}'s actual priced
    # position crossed its band". It did not: the two residuals are placed
    # either side of the band by construction (`under = band * 0.5`, then
    # stepped up until the tier moves), so the probe crosses whatever band it
    # reads. The property under test is real -- the selection is band-sensitive
    # and the proposer tightens and only tightens -- and the wording now says
    # which one it is.
    print(f"PASS: a SYNTHETIC residual placed either side of {org}'s own signed appetite band of "
          f"{band:,.0f} {ccy} ({under:,.2f} -> {over:,.2f} {ccy}, not {org}'s real priced "
          f"position) selects {tier_under} -> {tier_over} through {org}'s own selection-policy "
          f"package {policy_version} (which platform/graded/cage.py agrees with), and BOTH "
          f"tighten-only outcomes are graded on throwaway copies (ADR-0022): against "
          f"{org}'s own declaration ({real_note}) the proposer {real_outcome.upper()}S, and "
          f"against a SYNTHETIC copy this step rewrote to {synthetic_tier} it "
          f"{synthetic_outcome.upper()}S -- the landed one a --dry-run pull request declaring "
          f"{TIER_LABEL}: {tier_over} on {rel_declaration}, {org}'s governed Namespace, beside "
          f"an untouched pod manifest; the estate does not loosen a declaration to match a "
          f"price, and {org}'s real repository is byte-identical after both")
    return 0


if __name__ == "__main__":
    sys.exit(main())
