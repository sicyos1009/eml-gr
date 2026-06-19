-- EML-GR Zero Forest no-admit minimal Lean target v1.2
-- Purpose: proof-assistant compile smoke for an algebraic zero leaf.
-- This file avoids Mathlib so that a bare Lean 4 environment can try it.

theorem zf_nat_sub_self (n : Nat) : n - n = 0 := by
  exact Nat.sub_self n
