# Formal target bank v0.4-final

The formal target files are translation targets, not compile evidence.

```text
compiled_external_run: false
proof_assistant_environment_invoked: false
```

## Target priority

1. Schwarzschild common denominator leaf.
2. Rindler reciprocal derivative leaf.
3. pp-wave harmonic polynomial leaf.
4. FLRW exponential cancellation leaf.

The Schwarzschild leaf is first because it is pure algebra plus a denominator side condition:

```text
M > 0, r > 2*M
  |- 2*M/(r^2*(r-2*M)) - 2*M/(r^2*(r-2*M)) = 0
```

This should be the first WP15 external Lean/Coq/Rocq compile attempt.
