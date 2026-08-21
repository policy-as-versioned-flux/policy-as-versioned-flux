#!/usr/bin/env python3
"""PROTOTYPE — spike cs-06. Throwaway. Answers one question and then stops.

  Does computing the bump require policies to `extends` their predecessor,
  or is a rendered-artefact diff enough?

Path A  flat files + a rendered diff (what the estate has today).
Path B  one source per policy, each version declaring its delta, rendered
        down to today's flat per-version files.

Both paths run over the same real material in material/, and both are asked
for the ONE thing the release gate actually consumes: the facts in GateFacts.
The adversarial section then tries to break path A on purpose.

Run: ./run.sh
"""

import difflib
import pathlib
import re
import sys
from dataclasses import dataclass

import yaml

HERE = pathlib.Path(__file__).parent
FLAT = HERE / "material" / "flat"
EXTENDS = HERE / "material" / "extends"
ADV = HERE / "material" / "adversarial"

IDENT_LABEL = "policy-as-versioned.dev/policy"
VERSION_LABEL = "policy-as-versioned.dev/policy-version"


def rule(title):
    print(f"\n{'=' * 78}\n{title}\n{'=' * 78}")


# ---------------------------------------------------------------------------
# Path A — read the rendered artefact, recover the delta by diffing.
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class GateFacts:
    """Everything the release gate needs from ONE rendered policy version.

    Deliberately short. If a fact is not here, the gate does not read it, and
    inheritance cannot help with it.
    """

    identity: str  # pairs this policy with its predecessor
    actions: tuple  # Audit / Deny — cs-01: the only source of the major signal
    expressions: tuple  # cs-03 generates the corpus per CEL expression


def normalise_version(text, version):
    """Blank the policy's own version string wherever it appears.

    The version is in the name (dashed), a label, the self-scoping
    matchConditions expression and every message. All of that is noise across
    a pair. THIS IS THE WHOLE OF PATH A's cleverness — see ADVERSARIAL 1 for
    where it is wrong.
    """
    dashed = version.replace(".", "-")
    return text.replace(version, "${V}").replace(dashed, "${V}")


def load(path):
    return yaml.safe_load(path.read_text())


def facts(doc, version):
    md = doc.get("metadata", {})
    labels = md.get("labels") or {}
    identity = labels.get(IDENT_LABEL) or normalise_version(md["name"], version).rstrip("-").replace("-${V}", "")
    spec = doc["spec"]
    exprs = tuple(
        normalise_version(" ".join(v["expression"].split()), version)
        for v in spec.get("validations", [])
    )
    return GateFacts(identity, tuple(spec.get("validationActions", [])), exprs)


@dataclass
class Delta:
    identity: str
    actions_from: tuple
    actions_to: tuple
    added: tuple
    removed: tuple

    @property
    def empty(self):
        return not (self.added or self.removed or self.actions_from != self.actions_to)

    def render(self, indent="    "):
        out = []
        if self.actions_from != self.actions_to:
            out.append(f"{indent}actions {list(self.actions_from)} -> {list(self.actions_to)}")
        for e in self.added:
            out.append(f"{indent}+ {e}")
        for e in self.removed:
            out.append(f"{indent}- {e}")
        return "\n".join(out) or f"{indent}(no change)"


def delta_from_diff(old, new, ordered=False):
    """Path A's answer. Rules are matched as a SET of normalised expressions."""
    if ordered:  # the naive version, kept to show what set-matching buys
        added = tuple(n for i, n in enumerate(new.expressions)
                      if i >= len(old.expressions) or old.expressions[i] != n)
        removed = tuple(o for i, o in enumerate(old.expressions)
                        if i >= len(new.expressions) or new.expressions[i] != o)
    else:
        added = tuple(e for e in new.expressions if e not in old.expressions)
        removed = tuple(e for e in old.expressions if e not in new.expressions)
    return Delta(new.identity, old.actions, new.actions, added, removed)


# ---------------------------------------------------------------------------
# Path B — one source, each version declares its delta, rendered down to flat.
# ---------------------------------------------------------------------------


def resolve(src, version):
    """Walk the extends chain and apply the ops. Three ops cover the whole of
    the estate's real release line: actions, addValidations, replaceValidations.
    """
    spec = src["versions"][version]
    if "extends" not in spec:
        return {"actions": spec["actions"], "validations": list(spec["validations"])}
    base = resolve(src, spec["extends"])
    base["actions"] = spec.get("actions", base["actions"])
    base["validations"] += spec.get("addValidations", [])
    for repl in spec.get("replaceValidations", []):
        base["validations"] = [repl if v["id"] == repl["id"] else v for v in base["validations"]]
    return base


def render(src, version):
    """Flatten to exactly what Kyverno gets today, self-scoping via
    matchConditions — never objectSelector, which Kyverno collapses into one
    shared webhook and silently breaks multi-version coexistence.
    """
    r = resolve(src, version)
    return {
        "apiVersion": src["apiVersion"],
        "kind": src["kind"],
        "metadata": {
            "name": f"{src['policy']}-{version.replace('.', '-')}",
            "labels": {
                "app.kubernetes.io/part-of": src["partOf"],
                IDENT_LABEL: src["policy"],
                VERSION_LABEL: version,
            },
        },
        "spec": {
            "validationActions": r["actions"],
            "matchConstraints": {
                "resourceRules": [{
                    "apiGroups": [""], "apiVersions": ["v1"],
                    "operations": ["CREATE", "UPDATE"], "resources": ["pods"],
                }]
            },
            "matchConditions": [{
                "name": "only-this-policy-version",
                "expression": f"object.metadata.?labels['{VERSION_LABEL}'].orValue('') == '{version}'",
            }],
            "validations": [{
                "expression": " ".join(v["expression"].split()),
                "message": v["message"].replace("{{version}}", version),
            } for v in r["validations"]],
        },
    }


def declared_delta(src, version):
    """Path B's answer: read straight off the source. No diff, no guessing."""
    spec = src["versions"][version]
    prev = resolve(src, spec["extends"])
    return Delta(
        src["policy"],
        tuple(prev["actions"]),
        tuple(spec.get("actions", prev["actions"])),
        tuple(" ".join(v["expression"].split()).replace(version, "${V}")
              for v in spec.get("addValidations", [])),
        (),
    )


def semantic_equal(rendered, committed):
    """Compare the parsed documents, not the bytes. Comments are prose; the
    spec is the policy. Normalise whitespace inside CEL so the folded-scalar
    line breaks in the committed file do not count as a difference.
    """
    def clean(d):
        d = yaml.safe_load(yaml.safe_dump(d))
        for v in d["spec"].get("validations", []):
            v["expression"] = " ".join(v["expression"].split())
        for m in d["spec"].get("matchConditions", []):
            m["expression"] = " ".join(m["expression"].split())
        d["metadata"].pop("annotations", None)
        return d
    return clean(rendered) == clean(committed)


# ---------------------------------------------------------------------------
# The run
# ---------------------------------------------------------------------------

PAIRS = [
    ("require-nonroot", "1.0.0", "2.0.0", "the pair cs-06 names: byte-identical CEL copied, version hand-edited in 4 places, one rule appended"),
    ("department-label", "1.0.0", "2.0.0", "cs-01's known-good MAJOR: Audit -> Deny, body untouched"),
    ("known-department-label", "2.0.1", "2.1.1", "cs-01's known-good PATCH: enum widened +legal"),
]


def main():
    failures = []

    rule("0. THE BASELINE — what a plain text diff of the pair looks like")
    old = (FLAT / "require-nonroot-1.0.0.yaml").read_text().splitlines()
    new = (FLAT / "require-nonroot-2.0.0.yaml").read_text().splitlines()
    changed = [l for l in difflib.unified_diff(old, new, lineterm="", n=0)
               if l[:1] in "+-" and not l.startswith(("+++", "---"))]
    comment_lines = [l for l in changed if l[1:].lstrip().startswith("#")]
    print(f"    changed lines, raw text diff : {len(changed)}")
    print(f"    of which are comment prose   : {len(comment_lines)}")
    print(f"    substantive rule change      : 1 (one appended validation)")
    print("\n    Reading: a raw TEXT diff is mostly prose. Parse the YAML first and")
    print("    every comment disappears for free. That is step one of path A.")

    rule("1. PATH A — parse the rendered artefacts, recover the delta by diff")
    for name, v_old, v_new, note in PAIRS:
        f_old = facts(load(FLAT / f"{name}-{v_old}.yaml"), v_old)
        f_new = facts(load(FLAT / f"{name}-{v_new}.yaml"), v_new)
        d = delta_from_diff(f_old, f_new)
        print(f"\n  {name} {v_old} -> {v_new}")
        print(f"    ({note})")
        print(f"    paired on identity: {f_old.identity!r} == {f_new.identity!r}")
        print(d.render())
        if f_old.identity != f_new.identity:
            failures.append(f"{name}: identities did not pair")
        if d.empty:
            failures.append(f"{name}: path A recovered no delta")

    added = load(FLAT / "owner-annotation-2.1.1.yaml")
    f_added = facts(added, "2.1.1")
    print("\n  owner-annotation, absent at 2.0.1 -> present at 2.1.1")
    print("    (cs-01's known-good MINOR, and the one bump no verdict can show)")
    print(f"    presence: NEW only; actions {list(f_added.actions)}")
    print("    Reading: this needs no delta at all. It is a set difference over")
    print("    identities plus that actions field. Inheritance is not involved.")
    if f_added.actions != ("Audit",):
        failures.append("owner-annotation: actions not Audit")

    rule("2. PATH B — one source, the delta IS the source, rendered down to flat")
    src = yaml.safe_load((EXTENDS / "require-nonroot.yaml").read_text())
    for version in ("1.0.0", "2.0.0"):
        committed = load(FLAT / f"require-nonroot-{version}.yaml")
        ok = semantic_equal(render(src, version), committed)
        print(f"    render {version} == committed flat file (parsed): {'YES' if ok else 'NO'}")
        if not ok:
            failures.append(f"render {version} did not match the committed file")
    print("\n    Constraint held: each rendered version still self-scopes via")
    print("    matchConditions, so 1.0.0 and 2.0.0 coexist exactly as today.")

    d_b = declared_delta(src, "2.0.0")
    print("\n  require-nonroot 1.0.0 -> 2.0.0, delta read off the source:")
    print(d_b.render())

    d_a = delta_from_diff(facts(load(FLAT / "require-nonroot-1.0.0.yaml"), "1.0.0"),
                          facts(load(FLAT / "require-nonroot-2.0.0.yaml"), "2.0.0"))
    same = (d_a.added, d_a.removed, d_a.actions_from, d_a.actions_to) == \
           (d_b.added, d_b.removed, d_b.actions_from, d_b.actions_to)
    print(f"\n    path A delta == path B delta: {'YES' if same else 'NO'}")
    if not same:
        failures.append("paths disagreed on the require-nonroot delta")

    rule("3. ADVERSARIAL — where path A is wrong, on purpose")
    print("\n  1. A value that happens to equal the version string (pin-image).")
    d = delta_from_diff(facts(load(ADV / "pin-image-1.0.0.yaml"), "1.0.0"),
                        facts(load(ADV / "pin-image-2.0.0.yaml"), "2.0.0"))
    print("     true delta: EMPTY. The approved image tag stayed at 1.0.0.")
    print(f"     path A says:\n{d.render(indent='       ')}")
    print(f"     FALSE POSITIVE: {'yes' if not d.empty else 'no'}")
    if d.empty:
        failures.append("adversarial 1 did not reproduce the false positive")

    print("\n  2. Two rules, order swapped (two-rules).")
    fo = facts(load(ADV / "two-rules-1.0.0.yaml"), "1.0.0")
    fn = facts(load(ADV / "two-rules-1.0.1.yaml"), "1.0.1")
    naive = delta_from_diff(fo, fn, ordered=True)
    setwise = delta_from_diff(fo, fn)
    print("     true delta: EMPTY.")
    print(f"     positional compare: {len(naive.added)} added, {len(naive.removed)} removed  <- wrong")
    print(f"     set compare       : {len(setwise.added)} added, {len(setwise.removed)} removed  <- right")
    if naive.empty or not setwise.empty:
        failures.append("adversarial 2 did not behave as described")

    print("\n     Path B is immune to both: rules carry an id, and the version")
    print("     is a {{version}} placeholder rather than a literal to guess at.")

    rule("4. IS THE PAIRING KEY ACTUALLY UNIQUE? — checked against the live estate")
    check_pairing_key(failures)

    rule("VERDICT")
    print(VERDICT)

    if failures:
        print("\nSELF-CHECK FAILED:")
        for f in failures:
            print(f"  - {f}")
        return 1
    print("self-check: all assertions held")
    return 0


def check_pairing_key(failures):
    """Path A pairs versions on the identity label. Does that label actually
    identify ONE policy? Read the real estate rather than assume.

    SKIPs if .estate-clone/ is absent, matching verify-shift-left.sh.
    """
    clone = HERE.parents[1] / ".estate-clone"
    if not clone.is_dir():
        print("    SKIP: .estate-clone/ absent. Run ./clone-estate.sh first.")
        return

    families = {}
    for path in sorted(clone.rglob("*.yaml")):
        if "computed-semver" in path.parts or "tests" in path.parts:
            continue
        try:
            docs = list(yaml.safe_load_all(path.read_text()))
        except yaml.YAMLError:
            continue
        for doc in docs:
            if not isinstance(doc, dict) or "Policy" not in str(doc.get("kind", "")):
                continue
            labels = (doc.get("metadata") or {}).get("labels") or {}
            ident = labels.get(IDENT_LABEL)
            if not ident:
                continue
            families.setdefault(ident, set()).add(
                (doc["metadata"]["name"], labels.get(VERSION_LABEL)))

    for ident, members in sorted(families.items()):
        versions = {v for _, v in members}
        flag = ""
        if len(members) > 1 and versions == {None}:
            flag = "  <- SAME identity, DIFFERENT policies, no version label"
        print(f"    {ident:24} {len(members)} policy version(s), versions={sorted(str(v) for v in versions)}{flag}")

    ambiguous = {i: m for i, m in families.items()
                 if len(m) > 1 and {v for _, v in m} == {None}}
    print("\n    Reading: the identity label is a FAMILY name, not a unique key.")
    print(f"    {len(ambiguous)} family/families group several distinct policies with no")
    print("    version label at all, so (identity) alone cannot pair a predecessor.")
    print("    The gate's key must be (identity, name-with-version-stripped), and it")
    print("    must refuse — not guess — when a member carries no version label.")
    if not ambiguous:
        failures.append("expected at least one ambiguous identity family in the live estate")


VERDICT = """\
  A rendered-artefact diff is ENOUGH for the gate. Inheritance leaves this map.

  The reason is not that the diff is clean. It is that the gate never
  classifies from the delta:

    identity   -> a stable label already on every policy that reaches a pod
                  (policy-as-versioned.dev/policy). Pairing needs no diff.
                  But section 4: that label is a FAMILY name, not a unique
                  key. The pairing key is (identity, name-with-version-
                  stripped), and an unversioned member must fail the gate.
    major      -> from verdict movement on the corpus (cs-01), plus the
                  actions field. Not from the delta.
    minor      -> from PRESENCE of a policy name plus its actions (cs-01
                  proved verdict movement cannot see it). A set difference,
                  not a delta.
    patch      -> from verdict movement on the corpus. Not from the delta.
    corpus     -> cs-03 enumerates per CEL expression. That wants the LIST
                  of expressions on each side. A list, not a delta.

  So the delta is only ever evidence prose for the reviewer. Adversarial 1
  shows the cost of getting it wrong: a noisy line in the evidence, next to a
  bump that was still computed correctly from the evaluated verdicts.

  What path A does need, and this spike is the reason to write it down:
    - Parse the YAML. Never text-diff. Comments are 60% of the raw noise.
    - Pair on (identity label, metadata.name with the version stripped).
      The label alone is a family name: section 4 finds two families whose
      members are different policies carrying no version label at all. Those
      must fail the gate loudly rather than pair by accident.
    - Compare rules as a SET (adversarial 2).
    - Treat a normalised-version difference as UNPROVEN, not as a change
      (adversarial 1).

  If inheritance ships anyway as the DRY win it is, path B renders down to
  today's flat, self-scoping files with no runtime change, and the minimum
  shape is three ops: actions, addValidations, replaceValidations. That is
  the whole of the estate's real release line. It is a follow-on effort.\
"""


if __name__ == "__main__":
    sys.exit(main())
