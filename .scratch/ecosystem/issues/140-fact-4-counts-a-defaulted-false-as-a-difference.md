# 140 — Fact 4 counts a defaulted false as a difference

Type: task
Status: open
Blocked by: none

## Question

Charted 2026-09-24 by the integrator. The first scheduled drift samples after the composed-set
moves (driftwood run 35995156466, tuppence 36006834728, ludlow 36010939303) all read
`fact_4_rendered_objects_byte_equal_to_an_offline_render` false: 0 of 26 objects absent, and 9
live but unequal. All 9 are the PriorityClasses ticket 111 delivered, each with one difference:

```
".globalDefault absent live"
```

The rendered classes declare `globalDefault: false`. The API server omits a false-valued
`globalDefault`, so the field is absent live. Fact 4's `declared_equal` compare counts a declared
field that is absent live as a difference. The classes are in signed policy bodies
(`policy/v5.0.0`), so the render cannot change.

What this ticket owes:

1. Fact 4 treats a declared zero value that the API server omits as equal, for the fields where
   the API omits it, and records the rule with its reason. It must still fail a declared
   non-zero value that is absent live, and a changed value.
2. Tests at the compare seam in each adopter's `drift/five-facts.py` (driftwood, tuppence,
   ludlow), red first, including a planted `globalDefault: true` that is absent live.
3. The change is in each adopter's own lane script, so a scheduled sample reads the result.

## Done

A scheduled sample on each adopter reads fact 4 true with the delivered PriorityClasses, and the
compare still fails a real difference.

## Build, 2026-09-24

### What the failing samples say

The newest five-facts line on each adopter's `origin/main` `drift/samples.jsonl` (driftwood
2026-09-24T11:49:48Z, tuppence 13:38:16Z, ludlow 14:12:53Z) reads fact 4 false: 0 of 26 absent,
9 unequal. Each of the 9 is a PriorityClass with the single difference `.globalDefault absent
live`, and `strict_equal` false. Read with a short Python pass over the last line of each file.

Why the API server leaves it out: `k8s.io/api` v0.34.0 `scheduling/v1/types.go` line 48 declares
`GlobalDefault bool json:"globalDefault,omitempty"`. Read from the local Go module cache. A false
bool with `omitempty` is never written out, so the live object is exactly what the render
declared.

### Decisions (delegated, ADR-0025)

1. **The rule lives in `scripts/render_composed.py` `compare()`, not in `drift/five-facts.py`.**
   Reason: `compare()` owns `declared_equal` and its ceiling. `five-facts.py` only reads the
   verdict. Putting the rule beside the ceiling keeps one definition of equal.
2. **The rule is a table, not a general "zero equals absent".** `API_OMITTED_ZERO` is keyed by
   API group, kind and top-level field, and each entry carries the Go tag as its reason. It holds
   PriorityClass `globalDefault: false` only. Reason: a general rule would also pass a false field
   that the server pruned as unknown, and a custom resource keeps a false field as sent (it is
   stored as unstructured JSON). A field joins the table only when its Go tag is measured.
3. **The declared value must be the zero of the zero's own type.** Reason: `0 == False` in
   Python. A declared `0` is not the omitted bool, and the tests plant it.
4. **`strict_equal` does not change.** Reason: it is the byte-identity record. It still reads
   false for these 9 objects, so the weaker verdict stays visible.
5. **Every object read through the rule is named.** `compare()` returns `omitted_zero`, and fact 4
   records `objects_read_through_omitted_zero`. Reason: a reader of the sample sees where an
   absence was read as equal, rather than trusting the table.
6. **`drift/window.yaml` gets a dated `amended` line beside fact 4's ceiling. The ceiling text is
   not edited.** Reason: the claim ("equal to that render") holds unchanged, but the method moved.
   A pre-registration should show that openly. The cage-facts registration date keys on the
   `cage_behaviour_sample` section only, so this does not move it.
7. **The tests live in `tests/test_fact_four_compare.py`, and shift-left runs them beside
   `test_composed_reach.py`.** Reason: the `tests/` directory is where each adopter's compose-check
   runs unit tests. The file drives `compare()` and `composed_set_facts()` from
   `drift/five-facts.py` through a stand-in cluster, so the fact 4 seam itself is under test.

### What changed, per adopter (identical code in all three)

- `scripts/render_composed.py`: `API_OMITTED_ZERO`, `omitted_zero()`, `compare()` reads it, the
  docstring section "A declared zero the API server omits", two selfcheck asserts.
- `drift/five-facts.py`: `objects_read_through_omitted_zero` on fact 4, and the ceiling string.
- `drift/window.yaml`: the `amended` line.
- `tests/test_fact_four_compare.py`: 9 tests. `.github/workflows/shift-left.yml` runs them.
- `composed/HEADER.yaml`: one recompose, the last commit. Only `comparison-inputs.after` moves:
  driftwood `21e04b4e…` to `56384b7f…`, tuppence `a4a32130…` to `fe5457a3…`, ludlow `2eaa0ca5…`
  to `e28026ff…`.

PRs:

- driftwood: https://github.com/policy-as-versioned-driftwood/driftwood/pull/43
- tuppence: https://github.com/policy-as-versioned-tuppence/tuppence/pull/41
- ludlow: https://github.com/policy-as-versioned-ludlow/ludlow/pull/38

### Tests run

- Red first. `python -m unittest discover -s tests -p test_fact_four_compare.py` on each adopter
  with the fix stashed: `FAILED (failures=3, errors=2)` of 9 on all three. The failures were the
  missing `omitted_zero` key, the missing table, `.globalDefault absent live` on the delivered
  shape, and fact 4 false on it. The planted `globalDefault: true`, the changed value, the
  declared `0` and the custom-resource case already failed as they should.
- Green. The same file: 9 tests OK on all three.
- `test_composed_reach.py`: OK. `test_platform_tools.py`: OK, 1 skipped. On all three.
- `scripts/render_composed.py selfcheck`: ok, 26 objects at v2.0.0. `drift/five-facts.py
  selfcheck`: ok. On all three.
- Replay: the render at each adopter's pinned tag v2.0.0, served with each false
  `globalDefault` removed, through the new `compare()`: 26 objects, 26 declared_equal, 9 read
  through the omitted zero. On all three.
- Recompose: each adopter's own command, `platform-tools.py --adopter-dir <u> --tools-dir
  platform-tools compose <u> --estate-clone . --out <u>`, in a scratch workspace laid out as
  compose-check lays it. Tools at v3.4.0 (driftwood, ludlow) and v3.4.1 (tuppence), read from
  `.github/platform-tools-pin.yaml`. Parents at their pinned tag and commit, and
  `verify-pinned-checkouts.py` printed ok for each. Started from `origin/main`'s committed
  `composed/`, from full clones. exit 0. A second pass was byte-identical (`diff -r` of
  `composed/`, `cmp` of the output document) on all three.
- compose-check replay: a fresh workspace from each branch head, compose again, then
  `git status --porcelain -- composed/`: empty on all three.
- PR CI: `compose-check` and `shift-left` pass on all three PRs (`gh pr checks`). The driftwood
  compose-check log shows the new unittest line and `Ran 9 tests`.

### Merge order

The three adopter PRs are independent. Any order works. This hub PR only records the build, so
it can merge before or after them.

### What remains for Done

Done needs a scheduled sample on each adopter that reads fact 4 true with the delivered
PriorityClasses. Only the scheduled drift-sample clock can supply that, after each PR merges. No
workflow was dispatched. The check to run after the next scheduled line lands: fact 4
`observed: true`, `objects_unequal: []`, and `objects_read_through_omitted_zero` naming the 9
PriorityClasses. Nothing waits on the owner.
