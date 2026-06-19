# v0.8 upgrade targets

v0.7 makes the route-to-subleaf locator robust against formatting drift. The next gate should move from AST-path location to typed expression provenance.

Recommended v0.8 tasks:

1. Add typed AST nodes for scalar, tensor-scalar export, coordinate, and domain predicate expressions.
2. Attach a provenance edge from each tensor subleaf payload field to the AST node that consumes it.
3. Introduce a small AST normalization pass that can deliberately justify commutative reorderings instead of depending on textual order.
4. Split `diff(3*H**2,t)` into an explicit derivative-subleaf target so FLRW has a finer calculus/tensor boundary.
5. Export one AST locator replay theorem target into the formal-kernel seed bank.

