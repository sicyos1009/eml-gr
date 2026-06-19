# v0.7 AST-path locator contract

v0.6 located tensor-subleaf exports by literal character spans. That made the audit trail concrete, but the proof object was too sensitive to harmless formatting changes. v0.7 promotes the locator authority from a string span to a structural AST path.

## Locator object

```json
{
  "locator_kind": "ast_path_v1",
  "ast_locator": {
    "ast_profile": "zf_expr_ast_v1.python_infix_nary_add_mul",
    "target_field": "after_expr",
    "path": "$.terms[2].factors[1:3]",
    "payload_binding": {
      "subleaf_id": "flrw.connection.gamma_0ii",
      "payload_field": "gamma_0ii_expr"
    },
    "expected_expr": "H*exp(2*H*t)",
    "literal_span_v0_6_retained_for_audit_only": true,
    "ast_node_hash": "..."
  }
}
```

## AST profile

The profile is a deliberately small Python-like infix subset used only for replay auditing:

- `+` is represented by an n-ary `Add` node with ordered `terms`.
- `*` is represented by an n-ary `Mul` node with ordered `factors`.
- `**`, unary minus, symbolic names, numeric constants, and calls such as `diff(...)` and `exp(...)` are represented structurally.
- Whitespace and redundant parentheses are ignored.
- Algebraic commutativity is not silently used by the locator. Ordered factor windows are intentional.

## Trust posture

AST-path replay is still Level-B+. It validates that the declared tensor subleaf payload is structurally present at a specified route-expression node. It does not claim full tensor-CAS verification, global Bianchi formalization, or proof-assistant compilation.

