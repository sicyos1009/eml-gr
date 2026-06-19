# Tamper model content v0.3

## Goal

The tamper model is used to decide which failures are caught by the current seed replay checker, which failures require the content linter, and which failures require future semantic validation.

## Threat classes

```text
T1. Raw trace hash mutation
T2. Normalized evidence hash mutation
T3. Nonzero route final expression
T4. Unregistered proof rule
T5. Rule-class mismatch
T6. Non-equivalent scalar rewrite step
T7. Domain side-condition deletion
T8. Route initial expression disconnect
T9. Route step-order permutation
```

## Gate separation

```text
seed replay checker:
  catches T1--T6 in executable seed tests

content linter:
  catches T8--T9 and route-chain consistency issues

future domain validator:
  should catch self-consistent domain weakening, especially T7 with recomputed normalized hash
```

## Executed report

See:

```text
outputs/tamper_suite_report.json
outputs/tamper_suite_report.md
content/tables/tamper_expectation_matrix.csv
```

## Main negative-control result

Two important limitations are now explicit content, not hidden weaknesses:

```text
1. Route-chain consistency should be integrated into the replay checker.
2. Domain side-condition semantics should be validated beyond hash consistency.
```
