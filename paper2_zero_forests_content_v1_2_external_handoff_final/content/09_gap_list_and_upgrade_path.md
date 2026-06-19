# Gap list and upgrade path v0.3

## Gap G1. Route-chain validation not inside seed checker

Observed by negative controls:

```text
tamper_route_initial_disconnect_rehashed
tamper_route_step_order_reversed_rehashed
```

Action:

```text
Move content_linter route checks into zero_replay_checker_seed.py v0.4.
```

## Gap G2. Domain semantics not validated

Observed by:

```text
tamper_domain_ref_deleted_rehashed
```

Action:

```text
Add domain policy objects:
  DOM.NONZERO_DENOMINATOR requires denominator nonzero witness
  DOM.POSITIVE_COORDINATE requires explicit inequality domain
  DOM.REAL_BRANCH requires branch predicate
```

## Gap G3. Tensor steps are declared, not derived

Action:

```text
Add tensor-step replay skeleton:
  index signature
  source formula
  contracted indices
  symmetry rule references
  exported scalar leaf
```

## Gap G4. FLRW Bianchi case is still too leaf-level

Action:

```text
Expand from selected algebraic leaf to a covariant-divergence skeleton:
  ∇^μ G_{μν}
  selected ν channel
  Christoffel terms
  scale-factor assumptions
  exported zero leaf
```

## Gap G5. Formal kernel not compiled externally

Action:

```text
Start with Schwarzschild algebra leaf in Lean/Coq.
Record external_ci_results.v1.json after real compile.
```

## Suggested v0.4 content sprint

```text
1. Integrate content_linter into checker.
2. Add domain semantic validator stubs.
3. Strengthen FLRW tensor-index trace.
4. Add one Lean/Coq algebra leaf source file.
5. Rerun tamper suite in CI template.
```
