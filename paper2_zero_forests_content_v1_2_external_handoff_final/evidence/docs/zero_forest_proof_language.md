# Zero Forest Proof Language v0.1 / Certificate Schema v1.2 Draft

**Project:** EML-GR Forest  
**Component:** WP10 — Zero forest proof language expansion  
**Status:** draft seed, designed to extend v0.18--v0.22B zero/domain certificates and v0.34 formal checker seed  
**Date:** 2026-06-19

## 1. Purpose

A **zero forest** is a tensor-indexed family of nonstructural IR expressions that evaluates to zero on a certified domain. It is not the same as a structural zero suppressed by sparsity, symmetry, or index conventions. In EML-GR, zero forests arise from tensor symmetries, Bianchi identities, metric compatibility, coordinate artifacts, and field equations.

The proof language exists to make these vanishings replayable without trusting the original tensor generator.

The design goal is:

```text
raw tensor/IR computation
  -> route-sensitive trace certificate
  -> route-independent normalized zero evidence
  -> replay report
  -> optional formal-seed fragment
```

The critical separation is:

```text
route trace:        how a particular backend got from expression A to expression B
claim evidence:     what mathematical zero/domain claim is certified
formal fragment:    which small part can be moved to Lean/Coq/Rocq later
```

## 2. Core objects

### 2.1 ZeroForest

```ebnf
ZeroForest ::= {
  object_id: ClaimID,
  tensor_family: TensorFamily,
  index_signature: IndexSignature,
  domain_ref: DomainID | InlineDomain,
  components: ZeroComponent+
}

ZeroComponent ::= {
  component_id: string,
  lhs_expr: IRExpr,
  target_normal_form: "0",
  proof_certificate_id: CertificateID
}
```

A zero forest may contain one component, a selected witness component, or a full tensor-indexed bundle.

### 2.2 ZeroCertificate

```ebnf
ZeroCertificate ::= {
  kind: "zero_certificate",
  claim_id: ClaimID,
  object_signature: ObjectSignature,
  assumptions: Assumption+,
  domain: Domain,
  normalized_obligation: NormalizedObligation,
  routes: RouteTrace+,
  normalized_hash: Hash,
  replay_status: ReplayStatus,
  formal_fragment: FormalFragment
}
```

The certificate is accepted only if every route that claims `replay_ok=true` replays locally and every route collapses to the same normalized hash.

## 3. Expression layer

This draft allows three expression encodings.

### 3.1 SymPy-compatible scalar leaf encoding

Used by the seed replay checker:

```text
rho, r, M, H, t, A, k, u, x, y
+, -, *, /, **, exp, sqrt, log, diff
```

This is not the full EML-GR IR. It is the algebraic leaf language for selected zero witnesses.

### 3.2 IR AST encoding

For future implementation:

```ebnf
IRExpr ::= Const(q)
         | Symbol(name, type)
         | Add(IRExpr*)
         | Mul(IRExpr*)
         | Neg(IRExpr)
         | Pow(IRExpr, Integer)
         | Exp(IRExpr)
         | Log(IRExpr)
         | EML(IRExpr, IRExpr)
         | TensorRef(name, indices)
         | Deriv(coord, IRExpr)
         | CovDeriv(index, TensorExpr)
         | Contract(index_pair, TensorExpr)
```

### 3.3 Formal seed fragment

The current formal seed should remain narrow:

```ebnf
FormalExpr ::= rat(n,d)
             | sym(x)
             | add(FormalExpr*)
             | mul(FormalExpr*)
             | neg(FormalExpr)
             | pow(FormalExpr, integer)
             | exp(FormalExpr)   // opaque atom in seed kernel
             | sqrt(FormalExpr)  // opaque atom in seed kernel
             | log(FormalExpr)   // opaque atom in seed kernel
```

The formal fragment proves algebraic zero claims after tensor expansion has been exported as an algebraic obligation. It does not verify full tensor generation yet.

## 4. Proof step grammar

```ebnf
ProofStep ::= {
  step_id: string,
  rule_id: RuleID,
  rule_class: RuleClass,
  before_expr: Expr,
  after_expr: Expr,
  side_conditions: SideCondition*,
  replay_method: ReplayMethod,
  trust_boundary: TrustBoundary
}

RuleClass ::= "algebra"
            | "calculus"
            | "tensor_definition"
            | "tensor_identity"
            | "domain"
            | "lowering"
            | "hashing"

ReplayMethod ::= "sympy_simplify_zero_difference"
               | "laurent_normal_form"
               | "declared_tensor_rule_plus_algebra_leaf"
               | "domain_limit"
               | "grammar_check"
```

A route replays if every step satisfies its replay method and the route final expression has normal form zero.

## 5. Rule registry v0.1

The rule registry is intentionally explicit. A backend may not silently use a rule outside the registry and still claim a v1.2 replay pass.

### 5.1 Elementary algebra rules

```text
ALG.ADD_ASSOC_COMM          canonical associativity/commutativity of addition
ALG.MUL_ASSOC_COMM          canonical associativity/commutativity of multiplication
ALG.ADD_INVERSE             f + (-f) -> 0
ALG.MUL_ZERO                0*f -> 0
ALG.DIV_ZERO_NUMERATOR      0/f -> 0 under certified f != 0
ALG.COMMON_DENOM_CANCEL     a/d - a/d -> 0 under certified d != 0
ALG.POW_INTEGER             integer power simplification
ALG.EXP_CANCEL              exp(a)*exp(-a) -> 1 on real branch
ALG.RATIONAL_NORMAL_FORM    Laurent/rational coefficient normalization
```

### 5.2 Calculus rules

```text
CALC.DIFF_SYMBOL            d(x)/dx -> 1, d(y)/dx -> 0 when x != y
CALC.DIFF_POWER             d(x^n)/dx -> n*x^(n-1)
CALC.DIFF_EXP_LINEAR        d(exp(k*u))/du -> k*exp(k*u)
CALC.SECOND_DIFF_QUADRATIC  d^2(x^2)/dx^2 -> 2
```

### 5.3 Tensor-definition rules

These expand geometry definitions to algebraic obligations. The seed checker records them but does not yet independently prove the abstract tensor step.

```text
TDEF.CHRISTOFFEL_LEVI_CIVITA
TDEF.RIEMANN_FROM_GAMMA
TDEF.RICCI_CONTRACTION
TDEF.EINSTEIN_TENSOR
TDEF.COVARIANT_DIVERGENCE
TDEF.PPWAVE_RICCI_UU
```

### 5.4 Tensor-identity rules

```text
TID.RIEMANN_ANTISYM_LAST_PAIR
TID.RIEMANN_PAIR_EXCHANGE
TID.FIRST_BIANCHI
TID.SECOND_BIANCHI
TID.CONTRACTED_BIANCHI
TID.METRIC_COMPATIBILITY
TID.INDEX_SYMMETRY_ZERO
```

A tensor identity step must specify whether it is:

```text
structural_zero:  component never generated because of symmetry/sparsity
zero_forest:      component generated, then certified to vanish
```

This distinction prevents structural sparsity from being mistaken for a replayed zero forest.

### 5.5 Domain and side-condition rules

```text
DOM.NONZERO_DENOMINATOR     denominator != 0 on certified domain
DOM.POSITIVE_COORDINATE     e.g. rho > 0, r > 2M
DOM.REAL_BRANCH             exp/log/sqrt branch conditions
DOM.ONE_SIDED_LIMIT         limit as variable -> point from direction
DOM.LORENTZIAN_DET_NONZERO  det(g) != 0 on coordinate domain
```

## 6. Normalization policy

Each raw route has a route-sensitive hash:

```text
raw_trace_hash = H(canonical_json(route_id, steps, notes, route_metadata))
```

The normalized certificate hash intentionally ignores route ordering but keeps the mathematical obligation:

```text
normalized_hash = H(canonical_json({
  schema_major,
  kind,
  claim_id,
  object_signature,
  domain_signature,
  assumptions_canonical,
  zero_obligation,
  final_normal_form,
  required_rule_classes_sorted,
  side_condition_refs_sorted,
  formal_fragment
}))
```

Two different raw routes for the same claim should satisfy:

```text
raw_trace_hash_A != raw_trace_hash_B
normalized_hash_A == normalized_hash_B
```

This is the v1.2 form of path-independent claim evidence.

## 7. Acceptance semantics

A certificate bundle passes if all of the following hold.

```text
1. schema metadata is present and versioned
2. claim IDs are unique
3. every rule_id appears in the rule registry
4. every route step replays according to its replay_method, or is explicitly outside the formal fragment
5. each route final expression has normal form zero
6. raw hashes recompute exactly
7. normalized hashes recompute exactly
8. all routes for a claim collapse to one normalized hash
9. domain side conditions required by denominators are present
10. formal_fragment and trust_boundary are explicit
```

## 8. Trust boundary

The v1.2 draft has three levels.

```text
Level A: algebra leaf replay
  The checker verifies scalar equality or Laurent normal form directly.

Level B: tensor skeleton + algebra leaf replay
  The checker records tensor-rule use and verifies the exported scalar obligation.
  It does not yet prove the tensor rule from first principles.

Level C: formal proof assistant candidate
  The obligation lies inside the small AST fragment that can be ported to Lean/Coq/Rocq.
```

The first WP10 implementation should target Level B for Rindler, FLRW, Schwarzschild, and pp-wave selected claims, while extracting Level C leaves where possible.

## 9. First four canonical zero cases

```text
zero.rindler.Riemann_eta_rho_eta_rho
zero.flrw.contracted_bianchi_divG0
zero.schwarzschild.ricci_channel_pair
zero.ppwave.Ricci_uu_harmonic_profile
```

Required acceptance targets:

```text
Rindler:        at least two route traces collapse to one normalized certificate
FLRW:           contracted Bianchi proof object replays
Schwarzschild:  Ricci-channel zero proof object replays
pp-wave:        Ricci-flat harmonic-profile proof object replays
```

## 10. Non-claims

This proof language does not claim:

```text
- a complete elementary-function identity decision procedure
- full diffeomorphism equivalence
- full Cartan-Karlhede implementation
- complete tensor-rule formalization in Lean/Coq/Rocq
- full GR tensor generation independent of any CAS
```

It is a disciplined replay language for finite, selected, certificate-bearing zero forests.
