# External-run claim posture v1.2

## Allowed claims

```text
Level-B+ Paper2 content evidence is preserved from v1.1.
A real-external-run validator and hosted-CI handoff workflow are included.
Local preflight verifies that the handoff scripts, reports, hashes, and guardrails are internally consistent.
False real-run and false compile claims are rejected by tamper tests.
```

## Not claimed in this package

```text
real_external_run=true hosted success
Lean/Coq/Rocq compiled theorem in an external environment
full tensor CAS verification
full componentwise Bianchi theorem
universal zero-decision procedure
general semantic domain theorem prover
```

## Upgrade condition

The package becomes external-evidence-bearing only after a hosted record is returned with `real_external_run=true`, hash-checked raw logs, and a passing v1.2 validator report in `--require-real` mode.
