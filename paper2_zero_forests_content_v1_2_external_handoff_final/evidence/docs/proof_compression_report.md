# Proof Compression Report v0.1

The seed bundle encodes two proof routes for each of four canonical zero forest claims.

## Summary

```text
raw_route_count:                    8
canonical_claim_count:              4
unique_normalized_certificate_count: 4
route_to_claim_compression:         8:4
```

## Interpretation

The route trace is path-sensitive: it records the actual order of tensor expansion, algebraic rewrite, and cancellation steps. The normalized certificate is path-independent: it records the canonical mathematical obligation, domain assumptions, final normal form, rule classes, and formal-fragment declaration.

A successful collapse means:

```text
same claim + same certified zero obligation
  despite different rewrite route
  -> same normalized certificate hash
```

This mirrors the intended v1.2 policy: certificates attach to claims, not to incidental backend rewrite paths.

## Current trust boundary

The seed checker directly verifies scalar algebraic leaves with SymPy simplification. Tensor rules are declared and audited for explicitness but are not yet independently derived from tensor definitions. This is the intended Level B target for the first WP10 sprint.
