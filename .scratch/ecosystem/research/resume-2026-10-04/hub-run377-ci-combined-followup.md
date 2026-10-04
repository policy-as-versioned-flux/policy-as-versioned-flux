The actual approved source PR155 at `4c4b53c` exposed two fixable fixture failures
and the unchanged coverage-floor finding. The raw CI logs are retained. Full
pytest reported2905 passed,24 skipped,2 subtests passed and2 failures: the genuine
`fx` source-alias mismatch and the unchanged floor. Full type checking reported
four missing optional importlib-spec/loader narrowings.

The clean SSH-signed local followup is
`7fa013805f1e8bdd58e5a0390997c38211c5e087`, tree
`4042ec2099f70807d916f4b72f74938bb8167806`. Relative to the public reviewed `4c4`
source, only two test files change. The loader now explicitly requires a spec
and loader. Dependency source names remain local Flux aliases: `fx` points to
the real feeds repository, while `<adopter>-composed` points to its adopter.
The test resolves each consumed source's actual URL repository path and still
requires that repository in the estate. Consumer census, dependency census,
tag, immutable commit and coverage checks are retained.

Copied GitOps blobs from existing genuine local commits/tags reproduce the
original `fx` failure. The repaired test passes on the same input. A deliberately
broken URL naming an absent repository still fails and is restored afterward.
Full type checking of208 source files passes. The candidate packet binds source,
fixture-input, red/green-log and complete/delta patch hashes. No owner clone or
primary observation was changed. The followup awaits independent review and
has not been pushed; it does not claim the floor or original CI is green.
