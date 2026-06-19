(* EML-GR Zero Forest formal target v0.4-final
   Status: target statement only; not compiled in this package. *)

Require Import Reals.
Open Scope R_scope.

Theorem schwarzschild_common_denom_zero_target :
  forall M r : R,
    0 < M -> 2*M < r ->
    (2*M)/(r^2*(r-2*M)) - (2*M)/(r^2*(r-2*M)) = 0.
Proof.
  intros M r hM hr.
  field.
  (* denominator nonzero proof obligation should be discharged from hM and hr. *)
Admitted.
