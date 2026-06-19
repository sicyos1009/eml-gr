# v0.9 upgrade targets

The next content-level upgrade should add a small dependency-edge verifier for typed provenance.

Recommended v0.9 targets:

```text
1. typed dependency edges between tensor subleaves
   metric -> connection -> Einstein tensor -> divergence assembly

2. local type-flow checker
   connection_scalar_export * einstein_tensor_scalar_export -> assembled_tensor_scalar_expression

3. dimensional/tag consistency stub
   distinguish scalar, coordinate, parameter, tensor-index multiplicity, domain predicate

4. formal kernel bridge
   export one typed algebra leaf to Lean/Coq with the provenance object treated as an oracle boundary

5. CI bridge
   run v0.8 checker and tamper suite as a dry-run external CI record
```
