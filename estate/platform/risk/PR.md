# PR: escalate driftwood cart-PII admission Audit → Deny

**Type:** risk-tuned enforcement change · **Approver:** risk officer · **Trigger:** a number, not a date

## Why (the number)

An ICO-fine reassessment widened the per-event loss magnitude for the "unversioned
image ships cart PII" event. That single estimate change raises the residual a Deny
buys past driftwood's £40,000 tolerance band, so Audit is no longer proportionate.

```
$ enforce.py decide scenarios/driftwood-cart-pii-tightened.json --org driftwood
  risk_bought £54,520  >  tolerance £40,000  -> Deny
# before (loose triple): risk_bought £19,439  <=  £40,000  -> Audit
```

The escalation is justified by `ALE_warn − ALE_deny` crossing the band — no timer,
no date logic in any policy body (ADR-0006).

## Change 1 — tighten the versioned triple (this repo)

```diff
--- a/estate/platform/fair/scenarios/driftwood-cart-pii.json
+++ b/estate/platform/risk/scenarios/driftwood-cart-pii-tightened.json
-  "version": "v1",
+  "version": "v2",
   "warn": {
     "lef": [2, 4, 9],
-    "lm": [1000, 4000, 9000]
+    "lm": [3000, 10000, 30000]
   },
   "deny": {
     "lef": [0, 0, 1],
-    "lm": [1000, 4000, 9000]
+    "lm": [3000, 10000, 30000]
   }
```

## Change 2 — the driven admission action (platform distribution)

`enforce.py action … --org driftwood` now emits `Deny`, so the cart-PII admission
policy's `validationActions` follows — the field is a function of the £, hand-edited
only to match what the number already decided:

```diff
   spec:
-    validationActions: [Audit]   # residual £19,439 within the £40k band
+    validationActions: [Deny]    # residual £54,520 over the £40k band
```

## Verify

```
$ ./verify-risk-tuned.sh          # asserts the flip + the justification, offline
PASS: the £ picks Audit vs Deny; tightening a triple flips Audit->Deny by a number.
```
