When a signed adopter exposure carries `total: null`, quote pricing currently reaches arithmetic with `None` and raises `TypeError`. Refuse this missing instrument before exclusions or attachment arithmetic, so an unpriced book produces neither a layer nor a premium.

Known zero and known totals retain the existing pricing formula. Previously signed quote bodies, terms, implementation pins and release workflows are unchanged. The legacy cloud implementation pin mismatch remains a separate follow-up; this change does not claim a successful estate quote or a new live observation.

Validation: four public regression tests (including missing whole total with known subset/exclusion, numeric zero and known pricing); existing formula selfcheck; public verifier selfcheck including the new regressions; focused mypy. The actual signed Ludlow v4.0.1 exposure with null total returns typed `Refused` without mutation or pricing. Exact source `16b4857260f12458e5e0c797b2f99c60b1e03295` is SSH signed and independently passed Standards and Spec reviews.

The repository configures cut/fetch/release Actions workflows but no pull-request workflow. Any empty PR check rollup is reported as such, not as an Actions test pass.
