# v0.7 replay gates

v0.7 keeps the strict v0.5 gates and replaces v0.6 literal-span authority with AST-path gates.

```text
AP1  tensor steps must carry AST locators
AP2  target expression must parse under the v0.7 AST profile
AP3  AST path must resolve to an existing node or factor/term window
AP4  selected AST node must match the referenced subleaf payload AST
AP5  AST locator hash must recompute
AP6  route/step binding, unique occurrence id, and subleaf-ref coverage must hold
AP7  stale literal spans are warnings only, not replay failures
```

The most important behavioral change is that benign whitespace or redundant-parenthesis changes can pass when raw hashes are recomputed, while malicious AST-path drift, payload drift, bad target fields, and missing mapped subleaf references are rejected.

