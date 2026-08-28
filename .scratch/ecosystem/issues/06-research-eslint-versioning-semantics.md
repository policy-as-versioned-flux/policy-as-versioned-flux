# 06 — Research eslint versioning semantics

Type: research (AFK)
Status: open
Blocked by: none

## Question

The owner's instruction for versioning is: 'copy the behaviour of how eslint linting packs are versioned, and how you can supersede, mashup, join them, republish, inner source'. Document precisely how ESLint shareable configs and plugin packs behave: each package's own semver; `extends` and flat-config composition order; overrides and rule severity precedence; peer dependencies and version ranges versus pins; republishing a composed config as a new package; scoped (inner-source) registries. Then map each behaviour onto policy packages: publisher policy, regulator baseline, composed adopter set, tier floor, restatement. Produce the rule set the computed-semver gate and composition must follow, and name every place the current estate disagrees.

## Notes

Re-grill 2. Output: a research note plus a table of current-vs-required behaviour.
