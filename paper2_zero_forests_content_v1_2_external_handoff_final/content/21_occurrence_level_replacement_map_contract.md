# v0.6 Occurrence-Level Replacement Map Contract

This is content material, not manuscript prose.

## Purpose

v0.5 verifies that tensor steps refer to named FLRW tensor subleaves. v0.6 adds exact literal-span occurrence maps from each selected scalar subleaf export to the route-step expression.

## New object fields

```text
occurrence_id
route_id
step_id
locator_kind = literal_span_v1
target_field = before_expr | after_expr
span_start, span_end
literal_occurrence_index_0_based
subleaf_id
payload_field
expr
patch_action = observe_tensor_subleaf_occurrence
occurrence_hash
```

## New gates

```text
OM1 tensor step has occurrence maps
OM2 occurrence hash recomputes
OM3 literal span and occurrence index agree
OM4 occurrence expression matches the named subleaf payload field
OM5 occurrence ids are unique and bound to owning route/step
OM6 tensor-step subleaf_refs are covered by occurrence maps
```

## Boundary

The locator improves auditability of the selected tensor boundary. It does not prove the entire tensor derivation from the metric.
