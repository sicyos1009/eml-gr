(* EML-GR Zero Forest v1.1 formal seed target.
   Status: target source only in this artifact; no external compile evidence claimed. *)

Require Import Reals.
Open Scope R_scope.

Theorem zero_leaf_self_cancel : forall x : R, x - x = 0.
Proof.
  intro x.
  ring.
Qed.
