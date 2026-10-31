# Normative DiscoveryBinding projection — revision02

The accepted twin.xpdf-build-custody-binding/v1 shape is unchanged. For a closed Discovery result R and its Query Q, construct exactly this earlier-fact mapping:

- schema = literal twin.xpdf-build-custody-binding/v1.
- selection_sha256 = R.selection_sha256.
- command_id = literal `bootstrap-input-tools/` followed by Q.index as exactly three zero-padded ASCII decimal digits (000 through014); Q.index is its fixed query-prefix position. No alternate label/string or received command id exists.
- phase = literal bootstrap-input-tools.
- argv = Q.argv, exact ordered fixed query argv.
- environment_sha256 = SHA256 of `json.dumps(Q.environment,sort_keys=True,separators=(',',':'),ensure_ascii=True,allow_nan=False).encode('ascii') + b'\n'`. That newline belongs to the exact ENVIRONMENT.json DATA artifact retained in FILES.json; every Query environment must be the same selected fresh environment. A newline-free environment hash is different and refuses.
- command_started = Q.started, preserving the actual nullable number.
- command_deadline = Q.deadline, preserving the actual nullable number.
- checkpoint_started = R.original_started.
- checkpoint_deadline = R.deadline (the original discovery bound, never full A1800 or a new60seconds).
- leader_pid = Q.custody.leader_pid, preserving actual nullable ownership observation.

Hash this entire mapping exactly per accepted chronology: `SHA256(json.dumps(mapping,sort_keys=True,separators=(',',':'),ensure_ascii=True,allow_nan=False).encode('ascii'))`. There is **no trailing newline on the binding mapping**, unlike the environment artifact. There are no additional keys, journal/result/future-envelope hashes or fallback projections.

The command id, phase, environment bytes and original clocks must be fixed by the appointed collector before dispatch, not relabeled after execution. Any internal supervisor adapter must conserve those exact initial values and raw custody observations; a private dictionary does not establish an appointment. This mapping is a source/data projection only, not a new dispatcher or permission.

Q.command_binding_sha256 must equal Q.custody.command_binding_sha256, including null equality. If either is nonnull, both must equal the independently reconstructed digest. If both are null, this preserves an originally unobserved binding and can establish only held/partial data; computing a candidate digest does not authorize filling either null field or claiming the collector observed it. COMPLETE_DATA requires both nonnull and matching, plus all unchanged actual custody/clock/source/stream/file gates. Partial unknown clocks/leader remain explicit null in a genuinely observed nonnull binding if that is what the selected collector retained; they still cannot establish complete custody.

R.original_started, R.deadline and each required successful Q time/leader must be known for COMPLETE_DATA. R.entered/R.finished and Q.finished retain their separate actual route/terminal observations and are checked against the same original bound, but are not substituted into the earlier-fact binding. The existing custody journal references exactly the same held leader, raw wait and original clocks. Equal-tick ordinal, signal-before-first-consuming-wait, shared grace, terminal absence, stream completeness and no-next-query-on-unknown rules remain fully binding.

The pure projection proof accompanying this proposal demonstrates deterministic data encoding and context separation only. It is neither an implemented production checker nor observed query/custody evidence.
