# Core definitions and proposition bank v0.3

## D1. Zero obligation

A zero obligation is a tuple

\[
  Z=(\mathsf{claim},\mathsf{obj},\mathsf{dom},A,e_0,0),
\]

where `claim` is a stable claim identifier, `obj` is the tensor/scalar object signature, `dom` is a certified domain, `A` is a finite list of assumptions, `e_0` is the exported expression to be reduced, and `0` is the target normal form.

In the seed bundle, examples include:

```text
zero.rindler.Riemann_eta_rho_eta_rho:
  e0 = -diff(1/rho, rho) - 1/rho**2

zero.flrw.contracted_bianchi_divG0:
  e0 = 3*H*3*H**2 + 3*(H*exp(2*H*t))*(-3*H**2*exp(-2*H*t))

zero.schwarzschild.ricci_channel_pair:
  e0 = 2*M/(r**2*(r-2*M)) - 2*M/(r**2*(r-2*M))

zero.ppwave.Ricci_uu_harmonic_profile:
  e0 = -1/2*(diff(A*exp(k*u)*(x**2-y**2), x, 2) + diff(A*exp(k*u)*(x**2-y**2), y, 2))
```

## D2. Proof step

A proof step is a typed rewrite record

\[
  s=(i,\rho,c,e_{\mathrm{before}},e_{\mathrm{after}},S,m,\tau),
\]

where `i` is a step identifier, `rho` is a registered rule id, `c` is a rule class, `S` is a list of side conditions, `m` is the replay method, and `tau` is the trust-boundary label.

A seed step is replay-valid when:

```text
rule_id is registered
rule_class matches the registry
before_expr - after_expr simplifies to zero under the replay method
```

For declared tensor steps, the current Level-B checker records the tensor rule at the trust boundary and checks only algebraic neutrality of the exported leaf.

## D3. Proof route

A proof route is an ordered list of proof steps with a final expression:

\[
  r=(\mathsf{route\_id},\mathsf{route\_kind},[s_1,\ldots,s_n],e_n,h_{raw}).
\]

A content-complete route must satisfy:

```text
s1.before_expr = normalized_obligation.lhs_expr
si.after_expr = s(i+1).before_expr
sn.after_expr = route.final_expr
simplify(route.final_expr) = 0
raw_trace_hash recomputes from route_id, route_kind, steps, final_expr, route_notes
```

## D4. Zero forest certificate

A zero forest certificate is a tuple

\[
  F=(Z,R,h_{norm},\mathsf{formal\_fragment},\mathsf{trust\_boundary}),
\]

where `R` is a finite set of proof routes and `h_norm` is computed from route-independent material.

## D5. Raw trace hash

The raw trace hash is route-sensitive:

```text
sha256-16(canonical_json(route_id, route_kind, steps, final_expr, route_notes))
```

It should change when route order, route identifiers, intermediate expressions, final expressions, or route notes change.

## D6. Normalized evidence hash

The normalized evidence hash is route-independent:

```text
sha256-16(canonical_json(
  schema_major,
  kind,
  claim_id,
  object_signature,
  domain_signature,
  assumptions,
  zero_obligation,
  final_normal_form,
  required_rule_classes,
  side_condition_refs,
  formal_fragment
))
```

It intentionally ignores route ids, step order, raw trace hashes, and backend-specific rewrite order.

## D7. Route collapse

Two routes collapse when they have distinct raw trace hashes but the same normalized hash for the same claim.

Seed result:

```text
4 claims
8 raw routes
4 normalized certificates
route_to_claim_compression = 8:4
```

## D8. Trust level

```text
Level A:
  proof-assistant replayed algebra/tensor fragment, not yet achieved here

Level B:
  declared tensor skeleton plus replayed algebraic leaf, achieved by this seed

Level C:
  raw backend log only, not sufficient as paper evidence by itself
```

## D9. Content linter

The content linter is not a mathematical proof checker.  It enforces extra manuscript-facing consistency gates that the seed replay checker does not fully enforce:

```text
route starts from normalized obligation
route steps are chain-connected
route final expression equals last step output
domain side-condition references match normalized obligation references
formal fragment label is consistent
```

## Proposition bank

### P1. Raw route sensitivity

Under collision resistance of SHA-256 and canonical serialization, changing route-specific material changes the raw trace hash except with negligible collision probability.

Status: engineering claim, not a mathematical theorem inside the checker.

### P2. Normalized route invariance

If two certificates agree on normalized material and differ only in ignored route-specific fields, they compute the same normalized hash.

Status: direct consequence of the normalization policy.

### P3. Route collapse is observable

In the seed bundle, each of the four claims has two raw routes and one normalized certificate.  This gives an observed compression of 8 raw routes to 4 canonical claim certificates.

Status: benchmark evidence.

### P4. Rule-registry rejection

A replay step with an unregistered rule id or mismatched rule class is rejected by the seed replay checker.

Status: executable tamper evidence.

### P5. Nonzero final rejection

A route whose final expression simplifies to a nonzero expression is rejected even if its raw hash is recomputed.

Status: executable tamper evidence.

### P6. Route-chain consistency requires a stronger gate

A checker that validates individual step equality but not route-chain adjacency can accept some disconnected routes if hashes are recomputed.  Therefore a content linter or upgraded replay checker is required before stronger claims are made.

Status: identified gap and executable negative control.

### P7. Domain weakening is not ruled out by hashing alone

If a bundle weakens domain side-condition references and recomputes the normalized hash, a purely structural seed replay may accept the weakened bundle.  Semantic domain validation must be a separate gate.

Status: identified gap and executable negative control.

### P8. Formal kernel separation

The algebraic zero-leaf fragment can be specified independently from JSON schema validation, SHA-256, tensor generation, and CAS simplification oracles.

Status: formalization plan, not compiled evidence.
