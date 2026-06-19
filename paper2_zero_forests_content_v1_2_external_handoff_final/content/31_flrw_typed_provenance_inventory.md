# FLRW typed provenance inventory

The v0.8 seed keeps the same selected FLRW/de Sitter contracted-Bianchi scalar route from v0.7, but labels each AST-located tensor-scalar export.

The selected expression remains:

```text
diff(3*H**2, t) + 3*H*3*H**2 + 3*(H*exp(2*H*t))*(-3*H**2*exp(-2*H*t))
```

The main typed payloads are:

```text
flrw.divergence.expanded_nu0 / divergence_expanded_expr
  node_type: assembled_tensor_scalar_expression
  provenance_class: covariant_divergence_assembly

flrw.divergence.expanded_nu0 / partial_G00_expr
  node_type: calculus_scalar_export
  provenance_class: partial_derivative_component

flrw.connection.gamma_trace_0 / gamma_trace_0_expr
  node_type: connection_scalar_export
  provenance_class: connection_component

flrw.einstein.G_contra_00 / G_contra_00_expr
  node_type: einstein_tensor_scalar_export
  provenance_class: einstein_tensor_component

flrw.connection.gamma_0ii / gamma_0ii_expr
  node_type: connection_scalar_export
  provenance_class: connection_component

flrw.einstein.G_contra_ii / G_contra_ii_expr
  node_type: einstein_tensor_scalar_export
  provenance_class: einstein_tensor_component
```

Coordinate and parameter scopes are deliberately tiny:

```text
coordinate_scope: t, when the selected expression depends on t
parameter_scope: H, when the selected expression depends on H
domain_refs: DOM.REAL_BRANCH, when an exponential real-branch assumption is consumed
```
