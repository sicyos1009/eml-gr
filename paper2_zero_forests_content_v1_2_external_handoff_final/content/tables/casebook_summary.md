# Casebook summary

| claim_id | route_ids | actual_rule_classes | rule_ids | side_condition_refs | route_final_exprs |
|---|---|---|---|---|---|
| zero.rindler.Riemann_eta_rho_eta_rho | rindler_route_A_diff_then_cancel; rindler_route_B_power_form | algebra; calculus; tensor_definition | ALG.ADD_INVERSE; CALC.DIFF_POWER; TDEF.RIEMANN_FROM_GAMMA | DOM.POSITIVE_COORDINATE; DOM.NONZERO_DENOMINATOR | 0; 0 |
| zero.flrw.contracted_bianchi_divG0 | flrw_route_A_expand_then_cancel; flrw_route_B_factor_first | algebra; tensor_definition; tensor_identity | ALG.ADD_INVERSE; ALG.EXP_CANCEL; ALG.MUL_ASSOC_COMM; ALG.MUL_ZERO; TDEF.COVARIANT_DIVERGENCE; TID.CONTRACTED_BIANCHI | DOM.REAL_BRANCH | 0; 0 |
| zero.schwarzschild.ricci_channel_pair | schwarzschild_route_A_direct_pair; schwarzschild_route_B_numerator_zero | algebra; tensor_definition | ALG.ADD_INVERSE; ALG.COMMON_DENOM_CANCEL; TDEF.RICCI_CONTRACTION | DOM.NONZERO_DENOMINATOR; DOM.POSITIVE_COORDINATE | 0; 0 |
| zero.ppwave.Ricci_uu_harmonic_profile | ppwave_route_A_second_derivatives; ppwave_route_B_harmonic_laplacian | algebra; calculus; tensor_definition | ALG.ADD_INVERSE; ALG.MUL_ZERO; CALC.SECOND_DIFF_QUADRATIC; TDEF.PPWAVE_RICCI_UU | DOM.REAL_BRANCH | 0; 0 |
