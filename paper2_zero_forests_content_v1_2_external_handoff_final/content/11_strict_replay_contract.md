# Strict replay contract v0.4-final

This contract upgrades the v0.3 split between replay checker and content linter into one strict **Level-B+** content gate.

Checked directly:

```text
SCHEMA  JSON shape needed by the seed bundle
RC1     route initial expression equivalent to normalized obligation lhs
RC2     adjacent route-chain continuity
RC3     final step output equals route final expression, and final expression is zero
RC4     raw route hash and normalized evidence hash recomputation
RC5     rule registry membership, rule-class agreement, scalar step replay
RC6     required rule classes cover actual route classes
RC7     tensor steps remain declared tensor-boundary steps
RC8     seed domain side-condition entailment
```

Still outside the checker:

```text
full tensor calculus derivation
full proof-assistant formalization
general real-algebraic domain solving
global coordinate equivalence
```

The current status label is therefore:

```text
Level-B+ seed content =
  declared tensor skeleton
  + replayed algebra/calculus leaves
  + strict route-chain gate
  + seed domain gate
  + route-sensitive raw hash
  + route-independent normalized hash
  + executable tamper evidence
```

## Route initial gate

For a route `R` belonging to certificate `C`:

```text
simplify(R.steps[0].before_expr - C.normalized_obligation.lhs_expr) = 0
```

This allows surface-syntax variants such as `1/rho` and `rho**(-1)`.

## Route chain gate

For adjacent steps:

```text
steps[i].after_expr == steps[i+1].before_expr
```

This is intentionally textual.  If a route changes surface syntax, that change must be a proof step.

## Final zero gate

```text
steps[-1].after_expr == route.final_expr
simplify(route.final_expr) = 0
```

## Tensor boundary gate

A step with class `tensor_definition` or `tensor_identity` must remain explicitly declared:

```text
trust_boundary == declared_tensor_step
replay_method starts with declared_tensor
```

The scalar leaf exported by that tensor step is replayed for algebraic neutrality, but the tensor derivation itself is not claimed as checked.
