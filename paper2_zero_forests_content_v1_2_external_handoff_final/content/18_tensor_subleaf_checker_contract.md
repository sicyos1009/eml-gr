# 18. Tensor subleaf checker contract v0.5

The v0.5 checker adds a ninth gate:

```text
RC9 tensor-subleaf discipline
```

RC9 checks only selected FLRW subleaf structure. It does not replace the tensor oracle boundary.

## RC9 requirements

```text
1. Required FLRW subleaf IDs are present.
2. Each subleaf hash recomputes under canonical JSON with subleaf_hash removed.
3. Each dependency references an existing subleaf.
4. The divergence subleaf depends exactly on the selected connection and Einstein leaves.
5. Metric/inverse spatial diagonal scalar checks pass.
6. a_dot/a, Γ trace, Γ^0_ii selected scalar checks pass.
7. G^{00} and G^{ii} selected scalar payloads match the seed convention.
8. The divergence expression equals the expression assembled from named subleaves.
9. The divergence expression equals the normalized zero obligation.
10. The divergence expression simplifies to zero.
11. Each FLRW tensor route references the named divergence subleaf and its required dependencies.
```

## What RC9 deliberately does not check

```text
- full Christoffel derivation from arbitrary metric components
- full Einstein tensor derivation from Riemann/Ricci contractions
- proof-assistant formal replay of index notation
- semantic theorem proving over arbitrary domains
```

The value of RC9 is review discipline: a reader can now see which selected tensor leaves feed the algebraic cancellation, and the executable checker detects stale hashes, dependency deletion, sign mutation, and route/subleaf disconnects.
