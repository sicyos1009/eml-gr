# Replay semantics content v0.3

## Judgement forms

Use three replay judgements.

```text
Registry judgement:
  Γ_rule ⊢ rule_id : rule_class

Step replay judgement:
  Γ_rule, Γ_dom ⊢ step : e_before ↦ e_after

Route replay judgement:
  Γ_rule, Γ_dom ⊢ route : e0 ↦ 0
```

The seed checker currently implements the first two and the final-zero check.  The v0.3 content linter adds the route-chain side of the third judgement.

## Replay method classes

```text
sympy_simplify_zero_difference:
  Parse before_expr and after_expr.
  Check simplify(before - after) == 0.

laurent_normal_form:
  In this seed, delegated to SymPy difference.
  In formal kernel, should become a rational/Laurent normal-form procedure.

declared_tensor_rule_plus_algebra_leaf:
  Record a tensor-definition or tensor-identity step at the trust boundary.
  Check algebraic neutrality of the exported leaf.
```

## Route replay contract

A route is content-valid when:

```text
1. route.steps is nonempty.
2. route.steps[0].before_expr equals the normalized obligation lhs_expr.
3. Each adjacent pair satisfies previous.after_expr == next.before_expr.
4. route.steps[-1].after_expr equals route.final_expr.
5. route.final_expr simplifies to 0.
6. route.raw_trace_hash recomputes.
```

## Certificate replay contract

A certificate is content-valid when:

```text
1. schema_id and schema_version match the expected bundle type.
2. claim_id is unique.
3. rule_registry has no duplicate rule_id.
4. each route is route-valid.
5. certificate.normalized_hash recomputes.
6. every route of one claim collapses to the same normalized hash.
7. formal_fragment label matches normalized_obligation.formal_fragment.
8. domain.side_condition_refs match normalized_obligation.side_condition_refs.
```

## Important trust-boundary statement

A Level-B replay report should be read as:

```text
The exported algebraic zero obligations replay under the seed checker, and the declared tensor identities are recorded in the certificate trace.
```

It should not be read as:

```text
The entire tensor computation has been independently derived from the metric by the replay checker.
```
