-- EML-GR Zero Forest formal target v0.4-final
-- Status: target statement only; not compiled in this package.
-- Intended environment: Lean 4 + Mathlib.

import Mathlib

theorem schwarzschild_common_denom_zero
    (M r : ℝ)
    (hM : 0 < M)
    (hr : 2*M < r) :
    (2*M)/(r^2*(r-2*M)) - (2*M)/(r^2*(r-2*M)) = 0 := by
  ring
