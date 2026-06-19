(***
EML-GR seed theorem for v0.39.
This is not a GR tensor theorem. It is the tiny cancellation target used by
certificate replay: x - x = 0.
***)

From Coq Require Import ZArith Lia.
Open Scope Z_scope.

Theorem rindler_cancel_Z : forall x : Z, x - x = 0.
Proof.
  intros x; lia.
Qed.
