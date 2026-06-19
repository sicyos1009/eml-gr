# v0.6 FLRW Occurrence Map Inventory

Selected expression:

```text
diff(3*H**2, t) + 3*H*3*H**2 + 3*(H*exp(2*H*t))*(-3*H**2*exp(-2*H*t))
```

Mapped payloads:

```text
flrw.divergence.expanded_nu0 / divergence_expanded_expr
flrw.divergence.expanded_nu0 / partial_G00_expr
flrw.connection.gamma_trace_0 / gamma_trace_0_expr
flrw.einstein.G_contra_00 / G_contra_00_expr
flrw.connection.gamma_0ii / gamma_0ii_expr
flrw.einstein.G_contra_ii / G_contra_ii_expr
```

The 0-based occurrence index is required because literals such as `3*H` and `3*H**2` appear multiple times.
