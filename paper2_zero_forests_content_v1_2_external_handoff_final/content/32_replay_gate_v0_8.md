# Replay gate v0.8

The v0.8 checker composes three layers:

```text
v0.5 strict route and tensor-subleaf replay
  + v0.7 AST-path locator replay
  + v0.8 typed provenance replay
```

The typed provenance layer is intentionally finite and local.  It validates the typed source/target record attached to selected FLRW tensor-scalar exports.  It does not infer tensor types for arbitrary expressions and does not claim to replace a proof assistant.

The strict pass condition is:

```text
base_review_pass == true
AP1..AP7 == true
TP1..TP9 == true
issue_count == 0
```
