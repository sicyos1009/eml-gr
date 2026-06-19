# 20. v0.6 upgrade targets

The next content step should move from selected tensor subleaf discipline to partial tensor derivation discipline.

## Recommended v0.6 tasks

```text
1. Derive Γ^0_{ii}=a*a_dot and Γ^i_{i0}=a_dot/a from metric subleaf payloads.
2. Add a small formula registry for diagonal FLRW Christoffel components.
3. Split Einstein tensor leaves into Ricci/scalar-curvature subleaves.
4. Add a route showing ∂_t G^{00}=0 as a named calculus subleaf.
5. Add optional general-a(t) FLRW leaf where Bianchi becomes dρ/dt + 3H(ρ+p)=0.
6. Add Lean/Coq scalar target for the FLRW exponential cancellation.
```

## Go/no-go for manuscript drafting

A manuscript draft should wait until either:

```text
- v0.6 partial tensor derivation discipline exists, or
- v0.5 is frozen with explicit Level-B+ limitations and no stronger tensor claim.
```
