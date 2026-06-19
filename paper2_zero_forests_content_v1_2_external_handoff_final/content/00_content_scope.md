# Paper2 content scope v0.3

## Working title content, not manuscript prose

Zero Forests and Certificate Normalization in EML-GR.

## Core content thesis

A zero forest is a proof-carrying object for a vanishing obligation.  It stores the object being checked, the certified domain, the raw proof routes used by a simplifier or tensor pipeline, the normalized route-independent evidence, and the boundary between replayed algebra and trusted tensor generation.

The content claim is deliberately narrower than full tensor CAS verification:

```text
Level-B seed result:
  declared tensor skeleton
  + replayed algebraic zero leaves
  + route-sensitive raw trace hashes
  + route-independent normalized evidence hashes
  + tamper/lint checks for bundle integrity
```

## Positive claims supported by v0.3 content

```text
C1. Zero forests can be represented as explicit certificate objects.
C2. Raw route traces and normalized evidence can be separated by hash policy.
C3. Multiple raw routes can collapse to one normalized certificate per claim.
C4. A seed checker can replay a finite algebra/tensor-boundary fragment.
C5. Tamper tests can detect stale hashes, unregistered rules, class mismatches, nonzero final expressions, and several route consistency failures.
C6. The formalizable subfragment can be separated from external oracles.
```

## Negative claims not supported

```text
N1. This is not a complete tensor calculus verifier.
N2. This is not a proof-assistant formalization.
N3. This is not a universal zero-decision procedure.
N4. This is not a full Cartan-Karlhede equivalence algorithm.
N5. This is not a global diffeomorphism solver.
```

## Why content-first

The manuscript should only be written after the objects below are stable:

```text
definition bank
proof-step registry
casebook obligations
hash policies
tamper expectations
formal-kernel boundary
claim/evidence labels
```
