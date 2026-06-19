# Claim evidence matrix

| claim_id | object_kind | coordinate_chart | domain_id | domain_conditions | lhs_expr | target_normal_form | route_count | formal_fragment | trust_boundary | normalized_hash |
|---|---|---|---|---|---|---|---|---|---|---|
| zero.rindler.Riemann_eta_rho_eta_rho |  | Rindler wedge | domain.rindler.rho_positive | rho > 0 | -diff(1/rho, rho) - 1/rho**2 | 0 | 2 | tensor_skeleton_plus_algebra_leaf | level_B_tensor_skeleton_plus_algebra_leaf_replay | 891eaefce7260d94 |
| zero.flrw.contracted_bianchi_divG0 |  | cosmic time | domain.flrw.de_sitter_real | H > 0; t real | 3*H*3*H**2 + 3*(H*exp(2*H*t))*(-3*H**2*exp(-2*H*t)) | 0 | 2 | tensor_skeleton_plus_algebra_leaf | level_B_tensor_skeleton_plus_algebra_leaf_replay | fcca5fdf44e11ef8 |
| zero.schwarzschild.ricci_channel_pair |  | Schwarzschild coordinates | domain.schwarzschild.exterior | M > 0; r > 2*M | 2*M/(r**2*(r-2*M)) - 2*M/(r**2*(r-2*M)) | 0 | 2 | elementary_algebra_zero | level_B_tensor_skeleton_plus_algebra_leaf_replay | 963d459cf28463e9 |
| zero.ppwave.Ricci_uu_harmonic_profile |  | Brinkmann | domain.ppwave.real_harmonic_profile | A real; k real; u,x,y real | -1/2*(diff(A*exp(k*u)*(x**2-y**2), x, 2) + diff(A*exp(k*u)*(x**2-y**2), y, 2)) | 0 | 2 | tensor_skeleton_plus_algebra_leaf | level_B_tensor_skeleton_plus_algebra_leaf_replay | 3a4ff980c09752b5 |
