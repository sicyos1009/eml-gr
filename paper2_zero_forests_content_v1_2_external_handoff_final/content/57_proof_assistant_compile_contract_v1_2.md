# Proof-assistant compile contract v1.2

The proof-assistant layer is separated into two statuses.

## Probe status

A probe records whether Lean, Lake, Coq, or Rocq is visible on the runner. This is evidence about the environment only.

## Compile status

A compile status requires:

```text
tool_found: true
compile_attempted: true
compiled_pass: true
source file hash recorded
raw compile log hash recorded
no admitted proof for the no-admit seed target
```

## Seed files

```text
formal_targets/LeanZeroLeafMinimal.lean
formal_targets/CoqZeroLeafMinimal.v
formal_targets/schwarzschild_common_denom_target.lean
formal_targets/schwarzschild_common_denom_target.v
```

The minimal targets are no-admit algebraic cancellation seeds. The Schwarzschild target remains a richer target statement; the Coq Schwarzschild file is not used as a no-admit compiled theorem unless the admission is removed.
