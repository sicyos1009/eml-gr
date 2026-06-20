(* EML-GR Zero Forest no-admit minimal Coq target v1.2.
   Purpose: proof-assistant compile smoke for an algebraic zero leaf. *)

Require Import Coq.Arith.Arith.

Theorem zf_nat_sub_self : forall n : nat, n - n = 0.
Proof.
  intro n.
  apply Nat.sub_diag.
Qed.
