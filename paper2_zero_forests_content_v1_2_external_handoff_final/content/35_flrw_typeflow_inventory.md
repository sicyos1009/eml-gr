# FLRW contracted Bianchi type-flow inventory v0.9

Selected claim:

```text
zero.flrw.contracted_bianchi_divG0
```

Flow id:

```text
flrw.contracted_bianchi.nu0.typed_dependency_flow.v0_9
```

Root:

```text
flrw.metric.scale_factor
```

Sink:

```text
flrw.divergence.expanded_nu0
```

The dependency flow represents the selected chain

```text
metric -> connection -> divergence assembly
metric -> Einstein tensor -> divergence assembly
```

and includes an intra-subleaf assembly edge for

```text
partial_G00_expr + gamma_trace_term_expr + spatial_connection_term_expr
  -> divergence_expanded_expr
```

## Edge table

See `content/tables/typed_dependency_edge_table_v0_9.md`.
