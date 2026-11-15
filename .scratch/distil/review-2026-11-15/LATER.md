# Later: what waits until the first release has run

This file lists every change from the verified review that waits until after the loop's first release. That release is due on 2026-11-22. The rule, from the session's fix brief: a change waits if its ruling has `on_release_path: true` or `changes_cage_rules: true`. The orchestrator also put these design memos "later": D2a, D2b, D3a, D3b, D4a, D4d, D5, D6, D8a, D8b, D8e, and the code parts of D4b and D4c.

## How to read this file

- **Line numbers.** Line numbers are those of platform `f5ef7c7` (tag `policy/v8.0.2`) and driftwood `49f467c`, the copies the verifiers read. The platform commit that landed after the review (platform pull request 83, `1b7fcf9`, tag `policy/v8.0.3`) moved almost every line of `loop.py`, `probe.py` and `test_loop.py`; the shebang removal alone moved every line of `loop.py` and `probe.py` by one. So each item quotes the old text. Find the line by its text, not its number. Driftwood's `loop.yml` and `pins.sh` did not change, so their numbers still hold.
- **Counting.** One item is one change. Every ruling id that names that change goes on the same item. Each id sits in one group only, and any other group points to it. A design memo (D...) and a ruling (key in `rulings-all.json`) that are the same change share an item.
- **Sources.** "v1" means `verified-v1-loop-a.md`, "v2" `verified-v2-loop-b.md`, and so on up to "v10" for `verified-v10-design.md`. The combined copy is `verify-work/v10-memos/v-all/`. That copy holds D2a, D2b, D3a, D3b, D4a, D4c, D4d and the `next_pin` half of D6. Its diff against `verify-work/v10-memos/platform/` is the tested code for group 2.
- **What the hub keeps (added 2026-11-15).** The sources this file names were working files of the session: the verifiers' reports v1 to v10, the combined copy and the other copies under `verify-work/`, the rehearsal scripts, `rulings-all.json`, `memos.json` and the fix brief. The hub does not keep them. So each item states its change in its own words, and where an item says the combined copy has the text, the item's own text is the change. CG6's tested expressions, which item 3.4 needs, are copied in full in the appendix. A rehearsal named below has to be built again before it can be run.
- **The combined copy is not enough on its own.** It was diffed against the 38 tests of `policy/v8.0.2`. The commit that landed (`policy/v8.0.3`, 42 tests) added new assertions on fields that group 2 removes. Item 1.2 lists them.

## Group 1. Platform `loop.py` and its tests: release-path changes

### 1.1 `_index`'s refusal (V14; R069, R167, R238, C25)

- **File.** `platform/loop/loop.py` lines 207-208.
- **Change.** Delete these two lines:
  ```python
      if rung not in names:
          raise Refused(f"{rung} is not a rung of the ladder")
  ```
  `_index` keeps `names = [...]` and `return names.index(rung)`. No test is added, because the add-test proposals were refuted.
- **Source.** v1, section V14.
- **Order.** Goes in the one later platform tag (see "Landing order"). It is independent of every other item.

### 1.2 Tests that landed in `policy/v8.0.3` and must change with group 2

This item is a checklist, not a ruling. The commit that landed (`policy/v8.0.3`) added assertions that hold today's ledger shape. Each later change below must edit them in the same commit, or the unit tests go red. Each source report says what to drop.

- **V07** (v1, section V07: "If V20 removes `bound`, drop the bound column"). In `test_amounts`, the triples `(amount, bound, sourced)` lose the `bound` member. The `bare` assertion on `["estimate", "estimate"]` goes. This goes with 2.5 (D4a). `sourced` and `sourced_share` stay, because D4b keeps the field.
- **V10** (v1, section V10). In `test_within_partial_never_releases`:
  - `line["unpriced"]` goes from the tuple assertion. This goes with 2.9.
  - The `command_line` run that expects `(0, "within-partial", [ids])` must expect exit code 2, and must check `amount is None` on the rows in place of `unpriced`. This goes with 2.3 and 2.9.
- **v2 ruling 29** (v2: "These hold only while those fields stay"). Its `unpriced` assertion and V10's are one assertion. It landed once, in V10's form, on the tighten line of `test_within_partial_never_releases`: `self.assertEqual((line["verdict"], line["rung_to"], line["unpriced"]), ("tighten", "quarantine", ["unknown"]))`. That is the tuple assertion the V10 bullet names, and `line["unpriced"]` goes from it with 2.9. Its second, `line["reference"]` in `test_figure_at_baseline`, did not land: it caught no change that `test_could_not_look`'s `carried` check does not catch.
- **v2 rulings 4 and 21 and V07's zero-figure case.** These assert `sourced_share`. They stay, because D4b keeps the field.
- **`test_dwell`'s fourth ledger.** It still has `{"cause": "reset"}` in the middle. It changes with 2.1 and 2.2, as the combined copy shows:
  ```python
  self.assertFalse(loop.dwell_met([ready_since(7), ready_since(6), unseen], NOW, 7))
  ```
- **The probe tests on `reference`.** Line 232, `(line["pods"], line["reference"])`, reads the ledger field, so it changes with 2.9 itself. Lines 466 and 488 and `test_probe_reference_brackets` change only if the `probe.py` half of 2.9 is taken.
- **How to check.** After the group 2 edits, run `grep -n '"bound"\|"looked"\|"unpriced"\|"reference"\|within-partial' loop/test_loop.py`. Every hit must be a test that still means something. Then run `python3 -m unittest discover -s loop -p 'test_*.py'`.

### 1.3 `check_diff`'s pins branch: drop `not old` (ruling `check-diff-not-old`, R115; R178 is on 2.7)

- **File.** `platform/loop/loop.py` line 369, in `check_diff`.
- **Change.** `    if not old or old != new:` becomes `    if old != new:`.
- **Why it waits.** Both flags are false, but `check_diff` is on v10's list of release-path code ("On the release path"). Driftwood's `check` job runs `check-diff` on the open `loop/rung` and `loop/pins` pull requests in every cycle in `act` mode (driftwood `loop.yml` line 155), so the release's cycle runs it. Line 369 is in the pins branch. The platform check of the fix, round 1, held it back.
- **Tests.** None change. The `test_check_diff_pins` cases that landed in `policy/v8.0.3` pass with the line as it is and with the change.
- **Source.** v2 ruling 13.
- **Order.** Goes in the one later platform tag. It is independent of every other item.

## Group 2. The ledger fields and the verdict (D2, D3, D4)

These change the line that the `write` job appends, or how the dwell reads it. The memo's rule is: put D3a, D3b, D4a, D4c and D4d in one platform tag, so the ledger line changes shape once. D4b's refusal goes in the same tag (v10, "The decisions at a glance").

### 2.1 A `could-not-look` line counts by its own `release_ready` (D2a; ruling `dwell-could-not-look-skip`, R104, R221)

- **File.** `platform/loop/loop.py` lines 265-266, in `dwell_met`:
  ```python
          if line.get("verdict") in (None, "could-not-look"):
              continue
  ```
- **Change.** Delete both lines, together with 2.2. `dwell_met` then walks back while `release_ready` is true. The combined copy has the tested text.
- **Test.** In `test_dwell`, the `unseen` case expects False (see 1.2).
- **Records (hub).** Correct contract 4.1 (`dwell_met`: "Skip `could-not-look` lines ...") and section 11 ("a `could-not-look` line is passed over", in "The release that waits"), and `LOOP.md`.
- **Source.** v10 D2a; v2 ruling 1.
- **Order.** Must land with 2.2, because both change the same line. Driftwood's README dwell sentence ("it skips `could-not-look` lines", added by driftwood pull request 144 under D10) changes in the pin pull request (L4).

### 2.2 The dwell no longer passes over a line with no verdict (D2b; ruling `dwell-no-verdict-skip`, R222)

- **File.** The same two lines as 2.1.
- **Change.** Delete them; 2.1 and 2.2 together remove both lines. In `test_dwell`, take the reset line out of the middle of the fourth ledger (see 1.2).
- **Records.** Contract 3.5 ("Readers skip any line with no `verdict`") and 4.1 (`dwell_met`) now speak of people reading the ledger, not the loop. Keep driftwood's README sentence "Skip a line with no `verdict`": it is for a person.
- **Source.** v10 D2b; v2 ruling 2.
- **Order.** With 2.1.

### 2.3 `within-partial` exits 2 (D3a; ruling V23, R224)

- **File.** `platform/loop/loop.py` line 29: `EXIT = {"within": 0, "within-partial": 0, ...`.
- **Change.** Change it to `"within-partial": 2`.
- **Tests.**
  - Add `self.assertEqual(loop.EXIT[line["verdict"]], 2)` in `test_within_partial_never_releases`, as in the combined copy.
  - V10's `command_line` assertion expects 2 (see 1.2).
- **Driftwood README.** Line 30 and the last paragraph name `within-partial` among the reds. This goes in the pin pull request (L4).
- **Records.** Contract 4.1, which chose 0.
- **Source.** v10 D3a; v1 V23.
- **Order.** Must land with 2.4 (memo: "Land it with D3a"). The driftwood README edit must ride the same pull request that moves the platform pin.

### 2.4 `release_ready` needs every row priced (D3b; found by the design verifier, under R224)

- **File.** `platform/loop/loop.py` lines 279-286, in `decide`.
- **Change.** Move `all_priced` above `release_ready` and write `release_ready = all_priced and goal(priced, rungs, (1 - margin) * tol) < k`. The release branch becomes `elif release_ready and dwell_ok:`. The exact text is in the combined copy.
- **Test.** `test_within_partial_never_releases` expects `release_ready` False: `("within-partial", False, None)`.
- **Driftwood README.** The `release_ready` bullet added by driftwood pull request 144 says "A release needs every row priced and `release_ready` on each line". After this change, `release_ready` itself means every row is priced. Reword it in the pin pull request (L4).
- **Source.** v10 D3b.
- **Order.** With 2.3.

### 2.5 Remove `bound` (D4a; ruling V20, R227, C20)

- **File.** `platform/loop/loop.py` lines 173, 191-192, 200 and 415.
- **Change.**
  - Line 173: `bound, penalty = "estimate", 0` becomes `penalty = 0`.
  - Delete lines 191-192 (`if rate is None or tier is None:` / `bound = "upper"`).
  - Drop `"bound": bound` on line 200 and `"bound": row["bound"]` on line 415.
  - Keep the comment on line 189, which states the two fallbacks.
- **Tests.**
  - Delete the assertion `[one["bound"] for one in priced]` at old line 136.
  - Drop `"bound": "upper", ` from the JSON at old line 146.
  - Change V07's columns (see 1.2).
  - The combined copy has the first two.
- **Driftwood README.** The `rows` bullet (written by driftwood pull request 144 under D10) loses its `bound` clause. This goes in the pin pull request.
- **Records.** Contract 3.5, and B20, B21 and B23.
- **Source.** v10 D4a; v1 V20.
- **Order.** In the one ledger-shape tag.

### 2.6 A `cost_basis` must start `unsourced:` or `measured:` (D4b code part, and part of D4c; ruling `cost-basis-prefix`, R230)

- **File.** `platform/loop/loop.py` lines 111-113, in `read_rungs`.
- **Change.** Take v2 ruling 31's text, which was verified. Replace line 112 (`or not isinstance(rung["cost_basis"], str) or not rung["cost_basis"]:`) with:
  ```python
                  or not isinstance(rung["cost_basis"], str) \
                  or not rung["cost_basis"].startswith(("unsourced:", "measured:")):
  ```
  The combined copy writes it on one line and also changes the message on line 113 to "... a cost_basis that starts unsourced: or measured:". Take that message as well, so a refusal says what is wanted. No test matches on the old message: V06's cases, which landed in `test_no_deny_and_no_reduction`, use `assertRaises` only.
- **Test.** This test was held back from `policy/v8.0.3`, because it fails without the fix. V06's cases did not land as a test of their own: they are the `(key, value)` pairs of the `bad` list in `test_no_deny_and_no_reduction`. Add `("cost_basis", "Unsourced: no measurement")` to those pairs, or add this to `test_weakest_basis`:
  ```python
          slipped = json.dumps({"ladder": [dict(RUNGS[0], cost_basis="Unsourced: no measurement")]})
          with self.assertRaises(loop.Refused):
              loop.read_rungs(slipped)
  ```
  D4b's other half, the test with one sourced row and a measured cost basis, landed in `policy/v8.0.3` as v2 ruling 4 and V07 (`test_weakest_basis` and `test_amounts`). Nothing else of D4b waits.
- **Records.** Contract 3.4 ("A `cost_basis` that does not start `unsourced:` must name a measurement") then says a `cost_basis` starts `unsourced:` or `measured:`.
- **Source.** v2 ruling 31; v10 D4b and D4c.
- **Order.** In the ledger-shape tag. No input that exists today changes: all three bases start `unsourced:`.

### 2.7 Drop `weakest_basis`'s dead clause (D4c code part; ruling `weakest-basis-regime-once`, R107, R178)

- **File.** `platform/loop/loop.py` line 298.
- **Change.** `if row["penalty"] is not None and row["penalty"]["regime"] not in regimes:` becomes `if row["penalty"] is not None:`. No test changes; 3000 random inputs gave the same output.
- **Source.** v2 ruling 5; v10 D4c.
- **Order.** In the ledger-shape tag.

### 2.8 Line 182: refuse a rate whose basis kind does not match (D4c code part; R229, related to V17)

- **File.** `platform/loop/loop.py` lines 182-184, in `price`.
- **Starting text.** V17, line 182's narrow fix, did not land in `policy/v8.0.3` (corrected 2026-11-15). It waits with this item. Line 182 (line 181 in `policy/v8.0.3`) still reads `if (rate is None) == counted:`.
- **Change.** Line 182 becomes the combined copy's text, which replaces V17's narrow fix:
  ```python
              if regime["penalty_rate_basis"]["kind"] != ("not-counted" if rate is None else "counted"):
  ```
  - Keep the message on lines 183-184. V17's message change ("..., and the kind is a known one") is not taken.
  - Add V17's test here. In `test_malformed_values_are_refused`, after the `uncounted` lines, add:
    ```python
            estimated = copy.deepcopy(PENALTIES)
            estimated["regimes"]["uk-gdpr"]["penalty_rate_basis"]["kind"] = "estimated"
    ```
    and change `for penalties in (counted(None), uncounted)` to `for penalties in (counted(None), uncounted, estimated)`. It fails before the change and passes after (v1, section V17).
- **What this changes.** It is stricter than V17. It also refuses a null rate of kind `editorial`, which today is accepted and priced, and which contract section 11 says "is still accepted" (v1 V17). No input that exists today changes: ico publishes `counted` with a number, and the fixture publishes `not-counted` with null.
- **Records.** Correct contract section 11's sentence on a null rate.
- **Note.** V17 was ruled to apply only if V09 keeps the loop's copies of the publishers' checks. V09 has no ruling (see "Not ruled"). Today's code keeps those copies, so this item stands.
- **Source.** v10 D4c; v1 V17.
- **Order.** In the ledger-shape tag.

### 2.9 Remove `looked`, `reference` and `unpriced` from the ledger line (D4d; rulings `ledger-field-looked`, `ledger-field-reference`, `ledger-field-unpriced`, P19; R121, R122, R123, R225, R232, R233)

- **File.** `platform/loop/loop.py` lines 426, 429 and 431, in `cycle`.
- **Change.**
  - Line 426: drop `"looked": looked, `. Keep the local variable `looked`, which lines 428 and 430 use.
  - Delete line 429 (`"reference": probe.get("reference") if probe else None,`).
  - Line 431: `"rows": rows, "unpriced": [...]` becomes `"rows": rows,`.
  - The combined copy has the text.
- **Tests.**
  - The `FIELDS` tuple loses `looked`, `reference` and `unpriced`.
  - The `line["looked"]` assertions in `test_cage_ineffective`, `test_closed_but_undeclared_is_could_not_look` and `test_could_not_look` assert the verdict instead.
  - `(line["pods"], line["reference"])` becomes `line["pods"]`.
  - In `test_within_partial_never_releases`, the first assertion, `self.assertEqual((line["unpriced"], line["rows"][0]["amount"]), (["unknown"], None))`, keeps only the amount: `self.assertIsNone(line["rows"][0]["amount"])` (v2 ruling 20; added 2026-11-15, because no item named it).
  - The combined copy has all of these. Make the edits of 1.2 to the assertions that landed in `policy/v8.0.3`.
- **`probe.py` half (P19). Open choice, not ruled.** The `reference` key could also leave `probe.py`'s result. Lines 147 and 164 would become local variables, and the key would leave line 174. The memo did not patch it. If it is not taken, `probe.py` keeps writing a key that nothing reads. If it is taken, `test_probe_reference_brackets` asserts on `why` and `slept` instead (v3 ruling 19). It would ride the same tag.
- **Driftwood README.** Lines 32 and 33 change (v2 rulings 18 and 20). Driftwood pull request 144 made line 32, the `looked` bullet, much longer, and line 33 now ends "`unpriced` names the rows with a missing number". Only the `looked`, `unpriced` and `reference` wording goes; the rest of each bullet stays. Line 32 then speaks of the verdict, not `looked`: "When the verdict is `could-not-look`, `why` says what failed". Line 33's last sentence becomes "a row whose `amount` is null has a missing number". The D10 sentence on `reference` (line 37) goes too. All of this goes in the pin pull request.
- **Records.** Contract 3.5 and its example line; B6 and section 1 step 10 ("unpriced and named").
- **Source.** v10 D4d; v2 rulings 18 to 20; v3 ruling 19.
- **Order.** In the ledger-shape tag.

## Group 3. One new cage version

All of these go in one cage version. Under K20 the cage takes the version of the platform tag that carries it, called "X.Y.Z" below. The orchestrator picks the number at dispatch. Today the cage is 8.0.2. `policy/v8.0.3` (`1b7fcf9`) carries it unchanged.

Sources: `verified-v6-cage.md` (CG...) and v10 D8.

What this version proves, and what it does not:
- Neither verifier ran these CEL changes on Kyverno 1.18.2, the pinned engine. The cage verifier used the 1.19.1 command-line tool, which does not run the API server's checks.
- So the platform pull request's own proof run (kind with Kyverno 1.18.2) is the first time these expressions compile and act. It must be green before the tag is cut.
- After the release, driftwood sits at `baseline`, so its first cycle on the new cage proves nothing about `quarantine` (v10 D8). Platform's proof covers `quarantine` with the fixture pod only.

### 3.1 Move the version everywhere, together (K20)

- **Files, all in one go.**
  - `platform/cage/cage-tier.yaml` line 5, `name: cage-tier-8-0-2`, becomes `cage-tier-X-Y-Z`.
  - `platform/cage/cage-tier.yaml` line 28, the `only-this-policy-version` literal `'8.0.2'`, becomes `'X.Y.Z'`.
  - `platform/cage/cage-netpol.yaml` line 5, `cage-netpol-8-0-2`, and line 31, the literal, change the same way.
  - `platform/harness/fixture/apps/shop.yaml` line 7: the claim `"8.0.2"` becomes `"X.Y.Z"`.
  - Driftwood's `gitops/apps/api.yaml`, `pod.yaml` and `storefront.yaml` line 7: the claim `"8.0.2"` becomes `"X.Y.Z"`. This goes in the driftwood pin pull request, not the platform commit.
  - Line 9 (the `policy-version` label) is not moved. It is deleted (3.9).
- **D8f's test.** `test_cage_version_agrees`, which landed in `policy/v8.0.3`, checks that the seven copies of the version agree. It must still pass on the new copies (see 3.9, which takes the two labels out, so that it counts five).
- **Order.**
  - The platform half lands in the same tag as the rest of group 3.
  - The driftwood half (the three pods) lands in the same pull request that moves driftwood's platform pin. A claim that does not match the cage, in either direction, leaves the pods unstamped, and every cycle reads `could-not-look`.

### 3.2 Remove the CPU and memory limits (D8a; CG4; R081, C7). CG3 is superseded.

- **Files.**
  - `platform/cage/cage-tier.yaml` line 35 (`dial`): drop the `cpu` and `mem` keys of all three rungs, so each rung keeps only `harden`.
  - Line 40 (the CREATE expression): delete the `resources: Object.spec.containers.resources{ limits: {...} }` entry, about 10 CEL lines.
- **Proof (`platform/harness/proof.sh`).**
  - Line 104: `# 4. No restart, and baseline's limits stay until the pod is replaced.` loses the words "and baseline's limits stay until the pod is replaced".
  - Delete lines 108-109 (the `cpu=$(pod ...limits.cpu}')` witness and its check). Lines 105-107 still show the pod was not replaced.
  - Drop `cpu` from the `local` line 77. CG13 landed in `policy/v8.0.3`, so that line (line 74 there) reads `local start uid cpu rules`; it becomes `local start uid rules`.
  - Line 113 says `# Before cage 8.0.2 that update was refused: the cage tried to lower a running pod's limits.` This is a note for the fixer, not a ruling: with no limits left, decide whether that history line still earns its keep.
- **CG3 (R081, the requests cap).** This was a confirmed fix, but it is superseded by D8a: with no limits there is nothing to cap against (CG4: "CG3's fix (it has nothing left to cap against)"). Take CG3 only if D8a is not taken. Its text is in CG3 and in the `?requests:` block of CG6's full expression. CG1's held-back test statement `c["resources"] = {"requests": {...}}` is dropped with it.
- **Cost.** The rung costs are not changed; they are money and the owner's.
- **Order.** Lands in the cage version, with 3.3. It needs no rehearsal at `quarantine`, because removing a constraint cannot stop a pod from starting (v10 D8a).

### 3.3 Remove `readOnlyRootFilesystem` (D8b; CG5; R082, C8)

- **File.** `platform/cage/cage-tier.yaml` line 40: delete the `readOnlyRootFilesystem: ...` entry in the containers' `securityContext`, both of its lines. If CG6 is taken (3.4), the init-container body does not get it either.
- **What stays.** `harden` stays in `dial`, because D8c keeps `runAsNonRoot` and the drop-ALL patch.
- **Test.** None to drop: CG1's `hardened.py` leaves this field out on purpose.
- **Order.** In the same cage version as 3.2.

### 3.4 Harden init containers (CG6; R086)

- **File.** `platform/cage/cage-tier.yaml` lines 40 and 43.
  - Line 40: add the `?initContainers:` entry, a copy of the containers body with `Object.spec.containers` written `Object.spec.initContainers`.
  - Line 43: add the init-container JSONPatch after the containers map (`}) + (has(object.spec.initContainers) ? ... : [])`).
- **The full tested expressions.** They are printed in CG6, "Mutation 1" and "Mutation 2", and copied in the appendix of this file. Those texts include the limits, the `?requests:` block and `readOnlyRootFilesystem`. With 3.2 and 3.3 taken, delete those three entries from both bodies. Each body then keeps `name` and a `securityContext` with `runAsNonRoot`, `allowPrivilegeEscalation: false` and `privileged: false`.
- **Not run in that form.** No verifier ran this exact expression. The proof run on the platform pull request is its first check.
- **Style.** Keep each expression one double-quoted YAML scalar: backslash becomes `\\`, `"` becomes `\"`, newline becomes `\n`. Load the edited file with a YAML reader. Every key except `spec.mutations` must equal today's file.
- **Test (held back from `policy/v8.0.3`).** Put the CG1 `hostile.py` statement that adds an init container back into the guard step that landed in `policy/v8.0.3` (the `hostile.py` written by `proof.sh`):
  ```python
  pod["spec"]["initContainers"] = [{"name": "side", "image": c["image"], "restartPolicy": "Always",
                                    "securityContext": {"privileged": True}}]
  ```
  It is red on cage 8.0.2 (`side: privilege kept`) and green with this fix. Do not put back the `c["resources"]` statement (3.2).
- **Not this.** CG6b, ephemeral containers, was refuted. Do not pass it on.
- **Source.** CG6; CG1 notes.
- **Order.** In the cage version.

### 3.5 Remove `is-caged` from cage-netpol (CG12; R091)

- **File.** `platform/cage/cage-netpol.yaml` lines 26-27, the `is-caged` matchCondition.
- **Change.** Delete it. Keep `tier-restricts-reach` and `only-this-policy-version`. After this, `only-this-policy-version` is the one condition that ties the file to its version. CG14's proof check, which landed in `policy/v8.0.3`, holds it.
- **Order.** In the cage version, not alone.

### 3.6 Remove the labels on each generated NetworkPolicy (CG17; R096, R097, R098, R245)

- **File.** `platform/cage/cage-netpol.yaml` line 40.
- **Change.** `\"metadata\": dyn({\"name\": dyn(\"cage-reach-\" + t), \"namespace\": dyn(variables.nsName),\n               \"labels\": dyn({...three entries...})}),` ends at the namespace: `\"metadata\": dyn({\"name\": dyn(\"cage-reach-\" + t), \"namespace\": dyn(variables.nsName)}),`.
- **Keep.** The `podSelector`'s two labels, which carry the rule.
- **Order.** In the cage version. The proof runs on the pull request confirm it.

### 3.7 Delete the opening comment of each cage file (CG8; R071, R087, R214)

- **Files.** Line 1 of `platform/cage/cage-tier.yaml` and of `platform/cage/cage-netpol.yaml`: `# Applies only to pods that carry this policy version's label: see the matchCondition only-this-policy-version.`
- **Order.** This is not a rule change. It rides with the cage version.

### 3.8 Delete the labels `part-of` and `policy` on the two policies (CG9; R072, R073, R088, R089, R243)

- **Files.** Lines 7-8 of both cage files: `app.kubernetes.io/part-of: platform` and `policy-as-versioned.dev/policy: graded-enforcement`.
- **Order.** Rides with the cage version. Lands with 3.9, which then deletes the empty `labels:` key.

### 3.9 Delete the `policy-version` label, and update D8f's test and the README (CG10; R074, R090, R209, R244)

- **Files.** Line 9 of both cage files, `policy-as-versioned.dev/policy-version: 8.0.2`. With 3.8 taken, also delete the now-empty `labels:` key on line 6.
- **D8f's test (corrected 2026-11-15).** `test_cage_version_agrees` landed in `policy/v8.0.3`, and it reads the `policy-version` label of both cage files among seven copies ("the version label, the policy names, the match conditions and shop.yaml's claim must agree", v10 D8f). With the labels gone it finds five copies, not seven, and goes red. So this item must change that test in the same commit:
  - drop `re.findall(r"policy-version: ([0-9.]+)$", text, re.M) + ` from the line that adds each cage file's copies, so it reads `copies += re.findall(r"== '([0-9.]+)'$", text, re.M)`;
  - change `(7, 1)` to `(5, 1)`;
  - drop "labels" from its comment, so it names the policies' names and match conditions and the fixture's claim.
  It then compares the two names, the two `only-this-policy-version` literals and `shop.yaml`'s claim. Its regular expression for `shop.yaml` reads the quoted claim, `policy-version: "8.0.2"`, and stays.
  - CG10 itself refused an agreement test. The orchestrator ruled D8f's test in, so it stays.
- **`platform/README.md` line 13.** Change "and `policy-version` in `cage/` is the cage's version" to "and the version that the cage's match condition `only-this-policy-version` asks of a pod is the cage's version". D8f/CG11's sentence, which landed in `policy/v8.0.3`, says the tie to the tag is kept by hand. Keep it, and keep the line's two sentences consistent.
- **Order.** In the cage version. The test edit must be in the same commit, or the unit tests go red.

### 3.10 A comment above `rungs` in cage-netpol (CG15, part 2; R094)

- **File.** `platform/cage/cage-netpol.yaml`, above line 35 (`  - name: rungs`).
- **Change.** Add:
  ```yaml
    # Both restricting rungs' rules are written, so a pod moved in place between them is never under no rule.
  ```
- **What else.** The proof line of CG15 (part 1) landed in `policy/v8.0.3`.
- **Order.** Rides with the cage version.

### 3.11 Close quarantine's DNS allowance (D8e; CG16 option A; R095, C4). Only after a cluster run.

- **Prerequisite (no landing).** A cluster run must put driftwood's own three pods at `quarantine` with DNS closed and read `serving` 3 of 3.
  - Use a local copy of `cage-netpol.yaml` with the change below.
  - The cluster that stays up can do it.
  - Today's evidence does not show the pods can do without DNS. They have no readiness probe, and at `isolated` they serve 0 of 3 (v10 D8e).
- **If that run passes:**
  - `platform/cage/cage-netpol.yaml` line 38: the `reach` expression becomes `"{'isolated': {'ingress': dyn([]), 'egress': dyn([])},\n 'other':    {'ingress': dyn([dyn({})]), 'egress': dyn([])}}"`.
  - Add the proof line that holds it (CG16; not run): from `shop` at `quarantine`, `timeout 10 getent hosts kubernetes.default.svc.cluster.local` must fail. A success is RED and sets `failed=1`. A failed `kubectl exec` is RED, never green.
- **If it fails, or has not been run** when the cage version is cut, D8e stays out. Keep the allowance. D8e then waits for the next cage change and gets no tag of its own. Do not take option B's "assert DNS stays open".
- **Order.** The cluster run comes first; this item rides the cage version only if that run passed. It never lands before the release, which passes through `quarantine`.

## Group 4. The proof's first run (D5; R231, overriding H10)

### 4.1 Run 3 deletes both rules; run 1 and `--no-netpol` go

- **Why this overrides H10.** H10 ("refuted, no change") kept run 1 because it was the only real-cluster run of the probe's short branch. With run 3 deleting `cage-reach-isolated` too, run 3 takes that branch, so the reason goes (v10 D5).
- **Files and changes.**
  - `platform/harness/proof.sh`: in run 3, after `k -n fixture delete networkpolicy cage-reach-quarantine` (line 71), also delete `cage-reach-isolated` (one line).
  - `proof.sh`: delete run 1 (lines 59-62: its heading, comment and `run 1 ...` call). Delete lines 65-66 of run 2: `k -n fixture delete pod shop --timeout=120s` and the re-run of `up.sh`.
  - `proof.sh` lines 2-3 and 127: say "three runs", and drop `--no-netpol` from the comment on line 3.
  - `proof.sh` line 64, run 2's heading, says the rule is written "when the pod is admitted again". This is a note for the fixer, not in the memo: once lines 65-66 go the pod is not admitted again, so reword it to what run 2 then shows.
  - `platform/harness/up.sh`: remove the flag. That is line 2's `[--no-netpol]`; on line 7 only `netpol=yes` goes, and `cage=$1 apps=$2` stays; line 8 (the flag test) goes; lines 58 and 60 (the `if [ "$netpol" = yes ]` around applying `cage-netpol.yaml`), and the first test on line 71 (`[ "$netpol" = yes ] &&`).
  - `platform/.github/workflows/proof.yml` line 15: `bash harness/up.sh cage harness/fixture/apps` with no flag.
  - `platform/README.md` line 38: the same command with no flag. Line 42: three runs, without "the cage with no network rule".
  - Net: about 9 lines fewer, one flag and one cluster run fewer.
- **Lines that landed in `policy/v8.0.3` and stay valid.**
  - CG15's line after run 2's `run` call.
  - CG13's check inside `climb`: it looks only for `cage-reach-quarantine`, which is still deleted.
  - CG1's guard step, which runs after run 4.
  - H5's `diagnose.sh` call and H6/H11's edits in `run()`.
  - Their line numbers shift. Edit by text.
- **Run numbers.** Keep runs 2, 3 and 4 numbered as they are, or renumber them. The memo does not say. If renumbered, the `run N` arguments and every message that names a run change together.
- **Lost.** A run on a Namespace that never had a rule.
- **Prove.** One green proof run on the platform pull request. Driftwood's `loop.yml` calls `up.sh` with two arguments and no flag (line 36), so driftwood needs no change.
- **Records.** Contract 6.2 (the proof's runs).
- **Source.** v10 D5; memos.json D5.
- **Order.**
  - `up.sh` builds every driftwood cluster, so this lands in the platform tag after the release.
  - It touches `proof.sh` beside 3.2. Both go in the same tag; edit by text.

## Group 5. Driftwood's `loop.yml`

The source is `verified-v7-workflow.md`. The whole changed `check` step (V7-3 and V7-4 together) is lines 145 to 183 of `verify-work/v7-workflow/proposed/loop.yml`, with the diff in `proposed/loop.yml.diff`.

What a rehearsal does not prove:
- how GitHub evaluates `if:` and `needs`;
- the concurrency group;
- the app's token and merge;
- a real signature.

`write`, `check` and `land` are skipped on a pull request, so the pull request does not run the changed `check` step. A merge that changes only `loop.yml` starts no cycle, so the first live run is the next daily cycle.

### 5.1 Delete line 60 (V7-2; R100)

- **File.** `driftwood/.github/workflows/loop.yml` line 60, `            git checkout -- gitops/apps/namespace.yaml` (12 spaces of indent).
- **Change.** Delete it. Change nothing else.
- **Offline rehearsal.**
  ```
  cd verify-work/v7-workflow
  bash setup.sh > /dev/null && bash run-cycle.sh
  bash setup.sh > /dev/null && bash run-verify.sh
  ```
  - The first command (rehearsals 1 and 1b) must print "outputs equal with and without line 60".
  - The second (V1, the changed cycle step) must give `release`, `isolated` to `quarantine`, the same one-line rung patch, and an empty pins patch.
- **Live proof.** The pull request's own cycle runs the changed `cycle` step, and so does every daily `act` cycle after it.
- **Order.** Independent. It can share one driftwood pull request with 5.2, 5.3 and 6.1.

### 5.2 `check` stops when `party.json` or `gitops/apps` changed on main during the run (V7-3; R101)

- **File.** The `check` step of `driftwood/.github/workflows/loop.yml`, after line 149 (`          land=()`).
- **Change.** Insert the lines below: 10 spaces of indent, and 12 for the `if` body. `refused=0` belongs to 5.3; leave it out if 5.3 is not taken.
  ```
            refused=0
            # A merge that changed the loop's inputs on main after this run began has started a cycle of its own (line 5). That cycle decides again.
            if ! git diff --quiet "$GITHUB_SHA" refs/remotes/origin/main -- party.json gitops/apps; then
              echo "::warning::party.json or gitops/apps changed on main after this run began, so nothing lands; the cycle that change started decides again"
              echo "land=" >> "$GITHUB_OUTPUT"
              exit 0
            fi
  ```
  Do not edit line 131. The path list must stay the same as the push trigger's `paths` on line 5.
- **Offline rehearsal.**
  ```
  cd verify-work/v7-workflow
  bash setup.sh > /dev/null && bash run-verify.sh
  ```
  The expected results:

  | Case | Expected |
  |---|---|
  | V0, the daily path | `step exit 0; land=''`, no warning |
  | V2, a good release | `land='7:…'` |
  | V5, the tip says `measure` | `land=''`, with the warning |
  | V5b, the step as it is | `land='7:<head>'`, the defect |
  | V6, README-only change on the tip | it lands |
  | V7, `gitops/apps/pod.yaml` changed on the tip | `land=''`, with the warning |
  | V15, the chain of two releases | the push run at C1 lands nothing; the run at C2 lands `land='14:…'` |

  `run-verify.sh` cuts the step from `proposed/loop.yml` lines 145-183. If the final file's line numbers differ, change the three `pstep` lines at the top of the script.
- **Live proof.** The next daily cycle after the merge runs the guard on equal trees and must end green.
- **Order.** Land with 5.3 as one step, as rehearsed. Before the platform pin pull request (L4), see at least one daily cycle on main run the new `check` step green.

### 5.3 A refused rung turns `check` red; each pins skip warns (V7-4; R102)

- **File.** The same `check` step.
- **Change.** These go with `refused=0` from 5.2:
  1. Replace line 155, `            python3 "$platform/loop/loop.py" check-diff "${args[@]}" || continue`, with:
     ```
                 # A refused rung is a fault, because this run made the patch: the job ends red. A refused pin only warns, so it never stops the rung landing.
                 if ! python3 "$platform/loop/loop.py" check-diff "${args[@]}"; then
                   echo "::warning::loop/$kind: check-diff refused pull request ${pair%%:*}"
                   [ "$kind" = pins ] || refused=1
                   continue
                 fi
     ```
  2. Line 158: `|| continue` becomes `|| { echo "::warning::loop/pins: bump-pins failed, so pull request ${pair%%:*} does not land"; continue; }`.
  3. Line 159: `|| continue` becomes `|| { echo "::warning::loop/pins: pull request ${pair%%:*} is not the pins this job works out"; continue; }`.
  4. Line 160: `|| continue` becomes `|| { echo "::warning::loop/pins: the pins of pull request ${pair%%:*} do not check out"; continue; }`.
  5. Line 167: `[ "$code" -eq 3 ] || continue` becomes `[ "$code" -eq 3 ] || { echo "::warning::loop/pins: the loop the pins of pull request ${pair%%:*} name ended $code, not 3"; continue; }`.
  6. After line 171 (`echo "land=${land[*]}" >> "$GITHUB_OUTPUT"`), add:
     ```
               [ "$refused" -eq 0 ] || { echo "::error::the loop/rung pull request was refused, so the move did not land"; exit 1; }
     ```
- **Offline rehearsal.** The same command as 5.2. The expected results:

  | Case | Expected |
  |---|---|
  | V3 and V4 | `step exit 1; land=''`, with the warning and the error |
  | V8, a stale `loop/rung` pull request | exit 1 |
  | V9, a good rung and pins together | both land, exit 0 |
  | V10 to V14 | exit 0, the rung lands, and each pins skip prints its own warning |

  V2 and V9 show the paths that have run live do not change.
- **Not rehearsable.** That a red `check` skips `land`, that `::warning::` and `::error::` show on the run, and that a red `check` turns the run red.
- **Order.** With 5.2.

### 5.4 The `# v4.4.0` comments on the three checkout lines (added 2026-11-15)

- **Why it is here.** Driftwood's Renovate configuration (driftwood pull request 143) landed before the release, but these comments were held back, so that Renovate opens nothing against `loop.yml` before the release.
- **File.** `driftwood/.github/workflows/loop.yml` lines 23, 92 and 137, each `      - uses: actions/checkout@11d5960a326750d5838078e36cf38b85af677262`.
- **Change.** Add ` # v4.4.0` at the end of each, as platform, ico and feeds already have it. Change nothing else.
- **What follows.** Renovate can then follow the pinned action in `loop.yml`, and may open a pull request for a newer `actions/checkout`, as it did in platform (81) and ico (17). Nothing merges by itself.
- **Order.** It can share the pull request of L2.

## Group 6. `pins.sh` and `next_pin` (D6)

The source is v10 D6. The text below is V7-5's rehearsed `pins.sh` change plus the memo's `return ref, commit`. It is not R216's refusal in `next_pin`, which would also need tag refs in `PARTY_TEXT` and in the harness fixture.

### 6.1 `pins.sh` refuses a ref that is not a version tag (V7-5; R103, R203; driftwood half of D6)

- **File.** `driftwood/.github/pins.sh` lines 29-30.
- **Change.** Replace these two lines:
  ```
      # A branch: the pinned commit must have landed on it.
      git -C "$dir" merge-base --is-ancestor "$commit" "refs/remotes/origin/$ref" || refuse "$name: $commit is not on $ref"
  ```
  with one line (4 spaces of indent):
  ```
      refuse "$name: $ref is not a version tag"
  ```
  Keep lines 19, 28 (`  else`) and 31 (`  fi`). Do not delete the `else`: without it, a non-tag ref would pass with line 18 as its only check.
- **Offline rehearsal.**
  ```
  cd verify-work/v7-workflow
  bash setup.sh > /dev/null && bash run-trust.sh
  ```
  | Case | Expected |
  |---|---|
  | T7a, `main`'s party file | exit 0, three signature checks, each with its publisher's own identity |
  | T7b, a branch pin | refused: "ico: main is not a version tag" |
  | T8 and T9, the script as it is | a branch pin passes with 2 checks, and `bump-pins` follows the branch head |
- **Live proof.** The pull request's own cycle runs the changed file on the three tag pins, the same path the release takes.
- **Order.** Independent of 6.2 ("both or neither" was refuted). V7-5's flags are all false, but the fix brief holds `pins.sh` until after the release. It can share one driftwood pull request with group 5.

### 6.2 `next_pin` holds a ref that is not a tag (ruling `branch-pin-path`, R216; platform half of D6)

- **File.** `platform/loop/loop.py` line 379, `return ref, refs.get(f"refs/heads/{ref}", commit)`.
- **Change.** It becomes `return ref, commit`. The combined copy adds the comment `# only a signed tag is followed`; keep it only if it says something the line does not.
- **Test.** The first assertion of `test_next_pin` (old line 362) expects `("main", ZEROS)`.
  - v4 ruling 11 and v2 rulings 14 to 16 changed `test_next_pin` and the lines after 379 in `policy/v8.0.3`. Apply this edit by text, on top of theirs.
- **Records.** Contract section 7 ("Today ... `ref: main`"), K6 and K13 (their reason has run out).
- **Order.**
  - Goes in the one later platform tag.
  - Once 6.1 is on driftwood's main, this branch of `next_pin` cannot be reached from driftwood. So 6.1 may land first, and this one later.

## Not ruled: design decisions with no orchestrator ruling

Nothing is scheduled for these. They are listed so they are not lost. If any is chosen later, it would ride the same platform tag (and, for CG7, the same cage version).

- **V09** (R057, R059, R062, R063, R064, R164, R201, R240, C21, C22, C23, C29): the loop's copies of the publishers' checks. Kept as they are. 2.8 assumes they stay.
- **P03** (R020, C34, R032, C40): `probe.py`'s two nets for answers kubectl never gives. The options are (a), (b) and (c) in v3 ruling 3.
- **`bump-pins-write-flag`** (R130, R205, R250, R173): `bump-pins --write`, the dry run that nobody calls. Removing it couples `loop.py` lines 489-490 and 515 with `loop.yml` lines 61 and 158 in one driftwood pull request with the pin (v2 ruling 27).
- **CG7** (R075): the `namespaceObject != null` guard in `cage-tier.yaml` line 31. Option A removes it, which is a rule change. Option B keeps it and adds a comment (CG7).
- **P19's `probe.py` half**: see 2.9.

The other design decisions are settled:
- D1 (V22) keep; the hub's records got the corrected reason on 2026-11-15.
- D9 keep; D12's tests landed in `policy/v8.0.3`.
- D4b (V21) keep `sourced_share`; only its code part waits (2.6).
- D10 (`turnover-as-of`) keep.
- D14 (H2) keep.
- D15 (V19) keep.
- D16 (V24) option B, landed in ico `v5.2.0`.
- D17 (P20) keep.
- D11 (V9-05, V9-08) landed: the envelope keys and each fine's `year` left ico `v5.2.0` and feeds `threat-register/v5.2.0`, and the fixture's header left `policy/v8.0.3`.
- H9 (`note`) keep, under D10.
- CG4, CG5 and CG16 are 3.2, 3.3 and 3.11.

## Landing order

**Precondition.** The release of 2026-11-22 has run, and driftwood sits at `baseline`. The rehearsals say the two notches, `isolated` to `quarantine` to `baseline`, follow each other within the hour on that day.

**L1. The D8e cluster run (3.11).** No landing, no tag. Do it first. It decides whether D8e joins the one cage version. This is the only thing that could otherwise force a second cage version.

**L2. One driftwood pull request for its own files.** It carries 5.1, 5.2, 5.3, 5.4 and 6.1. No tag, no pin.
- Before merging, run `run-cycle.sh`, `run-verify.sh` and `run-trust.sh` and match the results above.
- The pull request's own cycle runs the new `pins.sh`. Its `check` step first runs live on the next daily cycle, and that cycle must be green before L4.

**L3. All platform work, then one tag.** The tag is `policy/vX.Y.Z`, cut by `cut-release.yml` dispatch. It carries:
- group 1;
- group 2, so the ledger changes shape once;
- group 3, the cage named X.Y.Z;
- group 4;
- 6.2.

How to land it:
- Because the tag is cut by dispatch, the work may land as several platform pull requests, each with its own green proof run (for example loop, cage and proof). They still make one tag.
- The cage pull request names X.Y.Z before the tag exists.
- Before dispatch, check these:
  1. The unit tests pass.
  2. `bash -n harness/*.sh` passes.
  3. The proof (three runs plus the checks that landed in `policy/v8.0.3`) is green on kind with Kyverno 1.18.2. That is the first compile of the CEL in 3.2 to 3.6.
  4. An offline cycle of the new loop on driftwood's real inputs reads `within` at `baseline`. Run `python3 -B loop/loop.py cycle` with:
     - driftwood's `party.json` and namespace file;
     - the pinned ico and feeds feeds;
     - the new `cage/rungs.json`;
     - a probe stand-in at `baseline`, both capabilities `open`;
     - `--ledger` set to a copy of driftwood's real ledger, which by then holds the release lines.

     `verify-work/v10-memos/rehearse.py` and `verify-work/v2-loop-b/rehearse.py` (not kept) build their own made-up ledger and clock for 2026-11-22. They show the release's shape, not the live ledger.

**L4. One driftwood pull request: the pin.** It carries:
- the platform pin line moved to `policy/vX.Y.Z`;
- the three pods' claims moved to `X.Y.Z` (3.1);
- the README changes of 2.1, 2.3, 2.4, 2.5 and 2.9.

Its own cycle runs the new loop and the new cage at `baseline`. On fewer pin changes:
- Driftwood's pin to `policy/v8.0.3` and its README commit landed on 2026-11-15, together, in driftwood pull request 144 (`9ff3a9b`). So this pull request moves the pin from `policy/v8.0.3` to X.Y.Z.
- No `party.json` key changes in any later item, so the exact-keys rule does not apply.

**L5. One hub pull request for the records.** It carries:
- contract 3.5 ("Readers skip any line with no `verdict`"), 4.1 (`dwell_met`) and section 11 ("a `could-not-look` line is passed over"), and `LOOP.md` (2.1, 2.2, 2.3);
- contract 3.5, B6, B20, B21, B23 and section 1 step 10 (2.5, 2.9);
- contract 3.4's line on `cost_basis` (2.6);
- contract section 11 (2.8);
- contract 6.2 (4.1);
- contract section 7, K6 and K13 (6.1, 6.2);
- contract 3.4's cage description (3.2, 3.3, and 3.11 if taken).

**Result.** One platform tag and one platform pin change, and no feed tag; the ico and feeds 5.2.0 tags are this round's. A second tag or pin change would come only from:
- D8e passing its cluster run after L3;
- a red proof run on the cage that has to be split out;
- the owner choosing one of the unruled items after L3.

## Appendix: CG6's tested expressions (copied 2026-11-15)

Item 3.4 needs these, and the cage verifier's report that printed them is not kept. They are copied here as the verifier ran them, with CG3's fix and CG6's fix together. They still carry the limits, the `?requests:` block and `readOnlyRootFilesystem`: with 3.2 and 3.3 taken, delete those entries from both bodies, as item 3.4 says. They were run with the Kyverno 1.19.1 command-line tool, not on Kyverno 1.18.2 (see group 3).

Mutation 1, the `expression` on line 40 of `platform/cage/cage-tier.yaml`:

```
request.operation == "CREATE" ? Object{
  metadata: Object.metadata{ labels: {
    "posture.acme.io/caged": "true",
    "posture.acme.io/tier": string(variables.tier)
  } },
  spec: Object.spec{
    hostNetwork: false,
    hostPID: false,
    hostIPC: false,
    containers: object.spec.containers.map(c, Object.spec.containers{
      name: c.name,
      resources: Object.spec.containers.resources{
        limits: {
          "cpu": (has(c.resources) && c.resources.?limits["cpu"].hasValue() &&
                  quantity(string(c.resources.limits["cpu"])).isLessThan(quantity(variables.dial.cpu)))
                   ? string(c.resources.limits["cpu"]) : variables.dial.cpu,
          "memory": (has(c.resources) && c.resources.?limits["memory"].hasValue() &&
                  quantity(string(c.resources.limits["memory"])).isLessThan(quantity(variables.dial.mem)))
                   ? string(c.resources.limits["memory"]) : variables.dial.mem
        },
        ?requests: (has(c.resources) && has(c.resources.requests)) ? optional.of({
          ?"cpu": (c.resources.?requests["cpu"].hasValue() &&
                   quantity(string(c.resources.requests["cpu"])).isGreaterThan(quantity(variables.dial.cpu)))
                    ? optional.of(variables.dial.cpu) : optional.none(),
          ?"memory": (c.resources.?requests["memory"].hasValue() &&
                   quantity(string(c.resources.requests["memory"])).isGreaterThan(quantity(variables.dial.mem)))
                    ? optional.of(variables.dial.mem) : optional.none()
        }) : optional.none()
      },
      securityContext: Object.spec.containers.securityContext{
        readOnlyRootFilesystem: variables.dial.harden == 'true' ||
          (has(c.securityContext) && c.securityContext.?readOnlyRootFilesystem.orValue(false)),
        runAsNonRoot: variables.dial.harden == 'true' ||
          c.?securityContext.?runAsNonRoot.orValue(object.spec.?securityContext.?runAsNonRoot.orValue(false)),
        allowPrivilegeEscalation: false,
        privileged: false
      }
    }),
    ?initContainers: has(object.spec.initContainers) ? optional.of(object.spec.initContainers.map(c, Object.spec.initContainers{
      name: c.name,
      resources: Object.spec.initContainers.resources{
        limits: {
          "cpu": (has(c.resources) && c.resources.?limits["cpu"].hasValue() &&
                  quantity(string(c.resources.limits["cpu"])).isLessThan(quantity(variables.dial.cpu)))
                   ? string(c.resources.limits["cpu"]) : variables.dial.cpu,
          "memory": (has(c.resources) && c.resources.?limits["memory"].hasValue() &&
                  quantity(string(c.resources.limits["memory"])).isLessThan(quantity(variables.dial.mem)))
                   ? string(c.resources.limits["memory"]) : variables.dial.mem
        },
        ?requests: (has(c.resources) && has(c.resources.requests)) ? optional.of({
          ?"cpu": (c.resources.?requests["cpu"].hasValue() &&
                   quantity(string(c.resources.requests["cpu"])).isGreaterThan(quantity(variables.dial.cpu)))
                    ? optional.of(variables.dial.cpu) : optional.none(),
          ?"memory": (c.resources.?requests["memory"].hasValue() &&
                   quantity(string(c.resources.requests["memory"])).isGreaterThan(quantity(variables.dial.mem)))
                    ? optional.of(variables.dial.mem) : optional.none()
        }) : optional.none()
      },
      securityContext: Object.spec.initContainers.securityContext{
        readOnlyRootFilesystem: variables.dial.harden == 'true' ||
          (has(c.securityContext) && c.securityContext.?readOnlyRootFilesystem.orValue(false)),
        runAsNonRoot: variables.dial.harden == 'true' ||
          c.?securityContext.?runAsNonRoot.orValue(object.spec.?securityContext.?runAsNonRoot.orValue(false)),
        allowPrivilegeEscalation: false,
        privileged: false
      }
    })) : optional.none()
  }
}
: Object{
  metadata: Object.metadata{ labels: {
    "posture.acme.io/caged": "true",
    "posture.acme.io/tier": string(variables.tier)
  } }
}
```

Mutation 2, the `expression` on line 43:

```
request.operation == "CREATE" && variables.dial.harden == 'true'
  ? object.spec.containers.map(c,
      JSONPatch{
        op: "add",
        path: "/spec/containers/" + string(object.spec.containers.indexOf(c)) + "/securityContext/capabilities",
        value: {"drop": ["ALL"]}
      }) +
    (has(object.spec.initContainers) ? object.spec.initContainers.map(c,
      JSONPatch{
        op: "add",
        path: "/spec/initContainers/" + string(object.spec.initContainers.indexOf(c)) + "/securityContext/capabilities",
        value: {"drop": ["ALL"]}
      }) : [])
  : []
```
