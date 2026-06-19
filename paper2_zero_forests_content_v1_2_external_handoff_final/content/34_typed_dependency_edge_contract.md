# Typed dependency-edge contract v0.9

This content block upgrades typed AST provenance from isolated occurrence checks to a typed subleaf-dependency flow.

## Object

A `typed_dependency_flow` is attached to a zero certificate with named tensor subleaves. It records:

- `root_subleaves`: tensor subleaves that have no tensor-subleaf dependency inside the selected DAG.
- `sink_subleaves`: subleaves that expose the selected zero-obligation scalar expression.
- `topological_order`: an auditable order for dependency checking.
- `typed_dependency_edges`: typed source-to-target edges between subleaf payload fields.
- `flow_hash`: a normalized hash of the complete flow object.

## Edge endpoint

Each endpoint binds a subleaf id, payload field list, subleaf hash, rule id, and rule class. The replay checker recomputes this binding against the actual tensor subleaf objects.

## Type-flow registry

The current registry covers six dependency kinds:

- `metric_to_connection`
- `metric_to_einstein_tensor`
- `einstein_to_divergence_derivative`
- `connection_to_divergence_assembly`
- `einstein_to_divergence_assembly`
- `intra_divergence_assembly`

The checker verifies declared source and target node types against the payload-field type declarations introduced in v0.8.

## Trust posture

This is still Level-B+ content. It audits the selected tensor-subleaf DAG and type-flow metadata. It does not claim a full tensor CAS proof or a full componentwise Bianchi theorem.
