# Domain side-condition contract v0.4-final

Zero certificates are only meaningful with their domain obligations.  v0.4-final implements a small seed entailment gate for the four current cases.

## Seed entailments

| Domain conditions | Entailed step side conditions | Used by |
|---|---|---|
| `rho > 0` | `rho>0`, `rho**2 != 0` | Rindler |
| `H > 0`, `t real` | `H real`, `t real`, `real branch` | FLRW contracted Bianchi |
| `M > 0`, `r > 2*M` | `M>0`, `r>2*M`, `r**2*(r-2*M) != 0` | Schwarzschild |
| empty / none | only empty side-condition lists | pp-wave seed |

## Rule-required refs

| Rule | Required side-condition ref |
|---|---|
| `ALG.COMMON_DENOM_CANCEL` | `DOM.NONZERO_DENOMINATOR` |
| `ALG.EXP_CANCEL` | `DOM.REAL_BRANCH` |
| `DOM.NONZERO_DENOMINATOR` | `DOM.NONZERO_DENOMINATOR` |
| `DOM.POSITIVE_COORDINATE` | `DOM.POSITIVE_COORDINATE` |
| `DOM.REAL_BRANCH` | `DOM.REAL_BRANCH` |

The checker rejects rehashed certificates that delete required refs or weaken domain conditions so that a route side condition is no longer entailed.

## Deliberate limitation

This is not a complete domain prover.  The next step is to turn domain obligations into explicit proof steps and then send the algebraic subset to the formal kernel.
