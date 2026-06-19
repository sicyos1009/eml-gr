# Formal kernel boundary content v0.3

## Aim

Separate the fragment that can be moved to Lean/Coq/Rocq from the engineering oracles that should remain outside the proof assistant.

## Formalizable first fragment

```text
Expr ::= rational constants
       | variables
       | addition
       | multiplication
       | negation
       | integer powers
       | Laurent monomials

Step ::= registered algebra rewrite
Route ::= finite list of connected steps
Certificate ::= route replay plus final zero normal form
```

## Candidate Lean/Coq statement shape

```text
Given:
  a finite registry of algebra rules,
  a finite route whose steps are connected,
  a normal-form function NF for Laurent/rational expressions,
  and a proof that each step preserves NF,

show:
  if the route starts at e0 and ends at 0,
  then e0 = 0 in the chosen algebraic semantics.
```

## Outside-oracle boundary

```text
JSON schema validation:
  outside proof assistant

SHA-256 hashing:
  outside proof assistant, recorded as audit metadata

Tensor generator:
  outside current Level-B kernel

SymPy simplification:
  seed oracle only; formal kernel should replace this for rational/Laurent leaves

Domain semantics:
  needs either a formal predicate layer or an external domain validator with explicit trust label
```

## First formal target

The lowest-cost first theorem should be a Schwarzschild algebra leaf:

```text
2*M/(r**2*(r-2*M)) - 2*M/(r**2*(r-2*M)) = 0
under r**2*(r-2*M) ≠ 0
```

This is better than starting with a tensor identity because it isolates the formal algebra replay problem.

## Formal-kernel readiness

```text
ready now:
  algebra expression grammar
  finite route syntax
  route-chain condition
  final-zero condition

not ready:
  metric-derived tensor steps
  branch/domain semantics for exp/log
  hash validation inside proof assistant
```
