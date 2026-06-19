# v0.8 Typed AST provenance contract

This content block upgrades v0.7 AST-path locators with typed provenance.  A v0.7 locator says *where* a tensor-scalar export appears inside a route expression.  A v0.8 typed-provenance object also says *what kind of expression it is*, *which tensor subleaf produced it*, *which payload field it consumes*, and *which coordinate/parameter scope is required to interpret it*.

## Required object

Each AST-located occurrence map in a tensor step carries:

```text
typed_provenance:
  profile
  node_type
  provenance_class
  semantic_role
  scalar_codomain
  coordinate_scope
  parameter_scope
  domain_refs
  payload_binding
  source
  target
  provenance_edge
  type_hash
```

The checker treats this as a local provenance object, not as a global theorem about all tensor components.

## Gate summary

```text
TP1 typed provenance object exists and has the expected profile
TP2 payload binding agrees with the v0.7 AST locator binding
TP3 source subleaf hash, rule id, and rule class agree with the tensor subleaf
TP4 node_type and provenance_class are drawn from the seed registry
TP5 typed provenance hash recomputes
TP6 source-to-target provenance edge is well formed and route/step-bound
TP7 coordinate/parameter scopes cover free symbols of the selected expression
TP8 typed domain refs are entailed by the certificate domain side conditions
TP9 tensor-subleaf payload field type declaration exists and agrees
```

The main claim-strength delta is that the FLRW tensor boundary is now auditable not only at the AST path level but also at the typed source/target provenance level.
