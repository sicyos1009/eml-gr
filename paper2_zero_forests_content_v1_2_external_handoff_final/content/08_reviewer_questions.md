# Reviewer questions and content answers v0.3

## Q1. Is this just a simplifier log?

Content answer: no.  A raw simplifier log is route-sensitive.  The zero forest additionally stores route-independent normalized evidence, domain assumptions, object signatures, rule registry, trust boundary labels, and replay outputs.

## Q2. Does the checker independently derive the tensor expressions?

Content answer: not in v0.3.  Tensor-definition and tensor-identity steps are recorded at a Level-B boundary.  The replayed fragment is the exported algebraic zero leaf plus structural/hash checks.

## Q3. What is actually compressed?

Content answer: raw routes are compressed into normalized claim evidence.  In the seed bundle, 8 raw traces across 4 claims collapse to 4 normalized certificates.

## Q4. What stops a malicious route edit?

Content answer: stale raw hashes, wrong final expressions, unknown rules, rule-class mismatches, and scalar non-equivalence are rejected by seed replay.  Route initial/adjacency consistency is enforced by the v0.3 content linter and should be integrated into the checker.

## Q5. What stops malicious domain weakening?

Content answer: stale domain edits are caught by normalized hash and linter mismatch.  Self-consistent domain weakening with a recomputed normalized hash is a known next-gate problem requiring a domain semantic validator.

## Q6. Why keep the raw routes if normalized evidence is the citation handle?

Content answer: normalized evidence supports route-independent claim citation; raw routes support audit, debugging, backend comparison, and tamper localization.

## Q7. What is the smallest formal proof target?

Content answer: a rational/Laurent algebra leaf, especially the Schwarzschild pair cancellation under a nonzero denominator side condition.
