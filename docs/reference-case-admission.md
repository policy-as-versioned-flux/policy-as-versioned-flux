# Reference case admission

`admit_reference(case, scope)` in `twin/reference_cases.py` conserves the supplied reference,
its already acquired source bytes and the admission decision in canonical immutable JSON.
`source_record(bytes, identity, version)` retains original bytes as base64 with their SHA256;
no network access or source refresh occurs. The returned packet digest identifies the exact
case, request and reasons, including held cases. Projection returns fresh objects.

The custodian supplies the request before predictions. The case's context must match it
exactly: purpose, claim, metric, domain, capability, organisation, source/reference date and
frame. Dates retain their declared meaning; a source Git date does not become an observation
or publication date. Rights declarations name their evidence, permitted uses and covered
support sources. Every required reference field has a separate meaning, sources and checked
byte-span witnesses. The separately supplied basis binds source hashes and is itself bound to
input, expected fields and context using `binding_for(case)` before predictions. These are
custody checks of declarations; they do not authenticate a publisher, grant legal rights,
prove annotation truth or replace independent semantic review.

Cases retain reference kind, limitations, source family, actual exposure history, and selection
or hold reasons. A previously held selection remains held. The implementation accepts only
`development`; a qualification request is held until a separately admitted population exists.
The declared claims distinguish published-coordinate agreement, agent-reference agreement,
complete causal reference and declared-constraint conformance. A reported-significance label
cannot stand in for complete causal sign, lag, elasticity and grade. Empty gameplay sets need
an explicit complete negative basis; absent mention supplies none.

For an admitted developmental case, pass `admission.evaluator_item()` to the existing
`skills.evaluate` with the ordinary skill scorer and an independently supplied basis checker.
The candidate sees only the declared input. Expected fields, separate reference basis, rights
and custody metadata are never attached to that input. `input_projection()` returns that same
input independently. Neither method can project a held case. Reference-shaped keys embedded
in input are held; substantive label leakage in natural language still needs semantic review.
No score recorder, corpus-kind registry or permission consumer is changed here.

The offline demonstration uses the already acquired, previously reviewed Coaching/Mentoring
reference from Piffio's map: the unchanged literal second coordinate `0.27`, in Sergio
Visinoni's own-business Take 2 frame at its Git-recorded source-version date. The packet
retains the original map, MIT copyright/permission notice, exact source spans, prior source
bindings, exposure and all 46 original selection decisions (four admitted, 42 withheld). It
claims source agreement only, with no world-truth, expert or human-replacement calibration,
pristine holdout, or estate qualification claim. The imported Evidence Inference case is
conserved and refused as complete causal evidence with all four original target nulls intact.

From the implementation checkout, point `--source-root` at the checkout holding the existing
research artifacts; choose a new output directory to retain the produced evidence:

```sh
PYTHONPATH=. python bench/reference_case_admission.py \
  --source-root /path/to/artifact-checkout --output /path/to/new-evidence
```

The disclosed `TEST_ONLY-literal-answer` callable returns the literal demonstration value and
selects one visible input witness. Its raw answer, stated basis and actual input are saved.
The ordinary evaluator reports one measured item against the unchanged twelve-item floor:
`not-measurable`, `passed=false`. This demonstrates software plumbing and a checked source
trace, never candidate competence or an earned permission. It does not contact providers,
load weights, write official scores or alter the frozen historical artifacts.
