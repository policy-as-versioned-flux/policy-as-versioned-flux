#!/usr/bin/env bash
# A stand-in for the `claude` binary, so the local clock can be exercised end to end with no
# token and no network (verify-local-clock.sh's offline half; tests/test_local_clock.py).
# It ignores its arguments and does what the real skill would, driven by LOCAL_CLOCK_STUB:
#   claim    write one valid headless claim file into the worktree, commit it, write PR title/body
#   nothing  do nothing (the pool was fully bound)
#   leak     as claim, but also commit a declaration (composed/x.yaml) -- the clock must refuse
#   dirty    write the claim but do not commit it -- the clock must refuse
#   example  commit the skill's own worked example (example-claim.yaml: a human-run file that
#            carries an OVERRIDE and no run.headless key) and write no PR title or body -- the
#            clock must refuse it, keep the branch, and never write its "no override" body
#   misnamed commit the same worked example under a name that is not *.claim.yaml
#            (twin/claims/<date>-probe-<step>.yaml) AND write a PR title and body claiming no
#            override -- the clock must refuse the file unchecked, keep the branch, and delete
#            the title and body the stub wrote
# LOCAL_CLOCK_INJECTED (set by the clock on a rehearsal) makes the claim say injected: true.
set -euo pipefail
wt="${LOCAL_CLOCK_UNIT_WT:?}"; run="${LOCAL_CLOCK_RUN_DIR:?}"
step="${LOCAL_CLOCK_STEP:?}"; adopter="${LOCAL_CLOCK_ADOPTER:?}"
what="${LOCAL_CLOCK_STUB:-claim}"
case "$what" in
  nothing) echo '{"type":"result","result":"LOCAL-CLOCK: nothing every pool entry is bound"}'; exit 0;;
esac
mkdir -p "$wt/twin/claims"
claim="$wt/twin/claims/$(date -u +%Y-%m-%d)-stub-$step.claim.yaml"
if [ "$what" = example ] || [ "$what" = misnamed ]; then
  [ "$what" = misnamed ] && claim="$wt/twin/claims/$(date -u +%Y-%m-%d)-probe-$step.yaml"
  cp "$(dirname "${BASH_SOURCE[0]}")/../../.claude/skills/classify-and-judge/assets/example-claim.yaml" "$claim"
  git -C "$wt" add -- "twin/claims"
  git -C "$wt" -c user.name=stub -c user.email=stub@local-clock.invalid commit -q -m "twin: the worked example, as if a model had written it ($step, $adopter)"
  if [ "$what" = misnamed ]; then
    echo "twin: the worked example under a probe name ($step, $adopter)" >"$run/$step-$adopter.pr-title"
    printf '%s\n' "The worked example, saved as a probe. No override is claimed." >"$run/$step-$adopter.pr-body.md"
  fi
  echo '{"type":"result","result":"LOCAL-CLOCK: ok committed the worked example with its override"}'; exit 0
fi
{
  [ -n "${LOCAL_CLOCK_INJECTED:-}" ] && echo "injected: true"
  cat <<EOF
schema: twin.headline-claim/v1
org: $adopter
run:
  skill: classify-and-judge
  run_at: '$(date -u +%Y-%m-%d)'
  operator_role: model-steward
  headless: true
  clock: local-clock
  statements_read: 1
  statements_bound: 1
  no_model_ran_on_a_clock: false
  clock_kind: local (ticket 92), not a GitHub clock
derived_from:
  - { party: feeds, kind: feed, name: news, version: '1.0.0' }
claims:
  - id: $adopter-binding-stub
    kind: binding
    component: cage-policy-line
    evidence_grade: 5
    claimed_by: signal-classify (skill)
    evidence: a stub binding written by verify/local-clock/stub-claude.sh
    price_eligible: false
EOF
  [ -n "${LOCAL_CLOCK_INJECTED:-}" ] && echo "    injected: true"
  cat <<EOF
    signal:
      id: stub-signal
      date: '2026-09-03'
      steep: technological
      source: policy-as-versioned-platform
      statement: a stub statement
      provenance:
        url: https://github.com/policy-as-versioned-platform/platform
      from: { party: feeds, kind: feed, name: news, version: '1.0.0' }
EOF
} >"$claim"
if [ "$what" = dirty ]; then echo '{"type":"result","result":"LOCAL-CLOCK: failed ran out of turns"}'; exit 0; fi
git -C "$wt" add -- "twin/claims"
if [ "$what" = leak ]; then mkdir -p "$wt/composed"; echo "tier: 3" >"$wt/composed/x.yaml"; git -C "$wt" add -- composed; fi
git -C "$wt" -c user.name=stub -c user.email=stub@local-clock.invalid commit -q -m "twin: stub claim from the local clock ($step, $adopter)"
echo "twin: stub claim ($step, $adopter)" >"$run/$step-$adopter.pr-title"
printf '%s\n' "A stub claim. A model ran on the owner's local clock (ticket 92), not on a GitHub clock; no override is claimed; the clock never merges." >"$run/$step-$adopter.pr-body.md"
echo '{"type":"result","result":"LOCAL-CLOCK: ok one stub binding committed"}'
