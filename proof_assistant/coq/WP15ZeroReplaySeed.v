(* EML-GR WP15a zero-certificate replay seed.
   Status: source-level formalization candidate; external Coq compile is pending for this new file.
   Scope: a tiny algebraic expression grammar plus two zero-certificate constructors.
   No tensor generator, hashing, JSON schema validation, or branch semantics are formalized here. *)

Require Import Coq.Arith.Arith.

Theorem wp15_nat_sub_self : forall n : nat, (n - n)%nat = 0%nat.
Proof.
  intro n.
  apply Nat.sub_diag.
Qed.

Require Import Coq.Reals.Reals.
Open Scope R_scope.

Inductive Expr : Type :=
| EConst : R -> Expr
| EVar : nat -> Expr
| EAdd : Expr -> Expr -> Expr
| EMul : Expr -> Expr -> Expr
| ENeg : Expr -> Expr
| EInv : Expr -> Expr.

Definition ESub (a b : Expr) : Expr := EAdd a (ENeg b).
Definition EDiv (a b : Expr) : Expr := EMul a (EInv b).
Definition ETwo : Expr := EConst 2.
Definition ESquare (e : Expr) : Expr := EMul e e.

Fixpoint eval (rho : nat -> R) (e : Expr) : R :=
  match e with
  | EConst c => c
  | EVar i => rho i
  | EAdd a b => eval rho a + eval rho b
  | EMul a b => eval rho a * eval rho b
  | ENeg a => - eval rho a
  | EInv a => / eval rho a
  end.

Inductive ZeroCert : Type :=
| CertSelfCancel : Expr -> ZeroCert
| CertCommonDenomSelfCancel : Expr -> Expr -> ZeroCert.

Definition cert_expr (c : ZeroCert) : Expr :=
  match c with
  | CertSelfCancel e => ESub e e
  | CertCommonDenomSelfCancel n d => ESub (EDiv n d) (EDiv n d)
  end.

Definition cert_domain (rho : nat -> R) (c : ZeroCert) : Prop :=
  match c with
  | CertSelfCancel _ => True
  | CertCommonDenomSelfCancel _ d => eval rho d <> 0
  end.

Definition replay (c : ZeroCert) : bool :=
  match c with
  | CertSelfCancel _ => true
  | CertCommonDenomSelfCancel _ _ => true
  end.

Theorem wp15_zero_certificate_replay_sound :
  forall (rho : nat -> R) (c : ZeroCert),
    replay c = true ->
    cert_domain rho c ->
    eval rho (cert_expr c) = 0.
Proof.
  intros rho c Hreplay Hdomain.
  destruct c as [e | n d]; simpl.
  - apply Rplus_opp_r.
  - apply Rplus_opp_r.
Qed.

Definition M : Expr := EVar 0%nat.
Definition r : Expr := EVar 1%nat.
Definition schwarzschild_numerator : Expr := EMul ETwo M.
Definition schwarzschild_denominator : Expr :=
  EMul (ESquare r) (ESub r (EMul ETwo M)).
Definition schwarzschild_common_denom_cert : ZeroCert :=
  CertCommonDenomSelfCancel schwarzschild_numerator schwarzschild_denominator.

Theorem wp15_schwarzschild_common_denom_leaf :
  forall (rho : nat -> R),
    cert_domain rho schwarzschild_common_denom_cert ->
    eval rho (cert_expr schwarzschild_common_denom_cert) = 0.
Proof.
  intros rho Hdomain.
  apply wp15_zero_certificate_replay_sound.
  - reflexivity.
  - exact Hdomain.
Qed.
