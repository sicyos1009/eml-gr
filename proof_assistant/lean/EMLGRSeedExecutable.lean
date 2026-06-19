/-
EML-GR seed theorem for v0.39.
This is not a GR tensor theorem. It is the tiny cancellation target used by
certificate replay: x - x = 0.
-/

namespace EMLGRSeed

theorem rindler_cancel_int (x : Int) : x - x = 0 := by
  simp

end EMLGRSeed
