# Expanded casebook content v0.3

This file is content inventory, not paper prose.

## zero.rindler.Riemann_eta_rho_eta_rho

### Object signature

```json
{
  "geometry": "Rindler",
  "tensor": "Riemann",
  "component": "R^eta_{rho eta rho}",
  "coordinate_chart": "Rindler wedge",
  "index_convention": "EML-GR v0.44 selected component convention",
  "structural_zero": false
}
```

### Domain

```json
{
  "domain_id": "domain.rindler.rho_positive",
  "conditions": [
    "rho > 0"
  ],
  "side_condition_refs": [
    "DOM.POSITIVE_COORDINATE",
    "DOM.NONZERO_DENOMINATOR"
  ]
}
```

### Zero obligation

```text
lhs_expr = -diff(1/rho, rho) - 1/rho**2
target_normal_form = 0
```

### Route inventory

| route_id | route_kind | steps | final_expr | raw_trace_hash |
|---|---|---:|---|---|
| `rindler_route_A_diff_then_cancel` | definition_first | 3 | `0` | `bd7990bdfb10fa14` |
| `rindler_route_B_power_form` | factored | 3 | `0` | `044afa190cec768b` |

### Step class inventory

| route_id | step_id | rule_id | class | replay_method | trust_boundary |
|---|---|---|---|---|---|
| `rindler_route_A_diff_then_cancel` | `A1` | `TDEF.RIEMANN_FROM_GAMMA` | tensor_definition | declared_tensor_rule_plus_algebra_leaf | declared_tensor_step |
| `rindler_route_A_diff_then_cancel` | `A2` | `CALC.DIFF_POWER` | calculus | sympy_simplify_zero_difference | checked_algebra_leaf |
| `rindler_route_A_diff_then_cancel` | `A3` | `ALG.ADD_INVERSE` | algebra | sympy_simplify_zero_difference | checked_algebra_leaf |
| `rindler_route_B_power_form` | `B1` | `TDEF.RIEMANN_FROM_GAMMA` | tensor_definition | declared_tensor_rule_plus_algebra_leaf | declared_tensor_step |
| `rindler_route_B_power_form` | `B2` | `CALC.DIFF_POWER` | calculus | sympy_simplify_zero_difference | checked_algebra_leaf |
| `rindler_route_B_power_form` | `B3` | `ALG.ADD_INVERSE` | algebra | sympy_simplify_zero_difference | checked_algebra_leaf |

### Content interpretation

```text
normalized_hash = 891eaefce7260d94
formal_fragment = tensor_skeleton_plus_algebra_leaf
trust_boundary = level_B_tensor_skeleton_plus_algebra_leaf_replay
```

## zero.flrw.contracted_bianchi_divG0

### Object signature

```json
{
  "geometry": "flat de Sitter FLRW",
  "tensor": "covariant divergence of Einstein tensor",
  "component": "nabla_mu G^{mu0}",
  "coordinate_chart": "cosmic time",
  "index_convention": "EML-GR v0.44 selected component convention",
  "structural_zero": false
}
```

### Domain

```json
{
  "domain_id": "domain.flrw.de_sitter_real",
  "conditions": [
    "H > 0",
    "t real"
  ],
  "side_condition_refs": [
    "DOM.REAL_BRANCH"
  ]
}
```

### Zero obligation

```text
lhs_expr = 3*H*3*H**2 + 3*(H*exp(2*H*t))*(-3*H**2*exp(-2*H*t))
target_normal_form = 0
```

### Route inventory

| route_id | route_kind | steps | final_expr | raw_trace_hash |
|---|---|---:|---|---|
| `flrw_route_A_expand_then_cancel` | identity_first | 3 | `0` | `812578f270cd652c` |
| `flrw_route_B_factor_first` | factored | 4 | `0` | `43ec0dd0687e1fbc` |

### Step class inventory

| route_id | step_id | rule_id | class | replay_method | trust_boundary |
|---|---|---|---|---|---|
| `flrw_route_A_expand_then_cancel` | `A1` | `TID.CONTRACTED_BIANCHI` | tensor_identity | declared_tensor_rule_plus_algebra_leaf | declared_tensor_step |
| `flrw_route_A_expand_then_cancel` | `A2` | `ALG.EXP_CANCEL` | algebra | sympy_simplify_zero_difference | checked_algebra_leaf |
| `flrw_route_A_expand_then_cancel` | `A3` | `ALG.ADD_INVERSE` | algebra | sympy_simplify_zero_difference | checked_algebra_leaf |
| `flrw_route_B_factor_first` | `B1` | `TDEF.COVARIANT_DIVERGENCE` | tensor_definition | declared_tensor_rule_plus_algebra_leaf | declared_tensor_step |
| `flrw_route_B_factor_first` | `B2` | `ALG.MUL_ASSOC_COMM` | algebra | sympy_simplify_zero_difference | checked_algebra_leaf |
| `flrw_route_B_factor_first` | `B3` | `ALG.EXP_CANCEL` | algebra | sympy_simplify_zero_difference | checked_algebra_leaf |
| `flrw_route_B_factor_first` | `B4` | `ALG.MUL_ZERO` | algebra | sympy_simplify_zero_difference | checked_algebra_leaf |

### Content interpretation

```text
normalized_hash = fcca5fdf44e11ef8
formal_fragment = tensor_skeleton_plus_algebra_leaf
trust_boundary = level_B_tensor_skeleton_plus_algebra_leaf_replay
```

## zero.schwarzschild.ricci_channel_pair

### Object signature

```json
{
  "geometry": "Schwarzschild exterior",
  "tensor": "Ricci",
  "component": "selected Ricci-channel pair",
  "coordinate_chart": "Schwarzschild coordinates",
  "index_convention": "EML-GR v0.44 selected component convention",
  "structural_zero": false
}
```

### Domain

```json
{
  "domain_id": "domain.schwarzschild.exterior",
  "conditions": [
    "M > 0",
    "r > 2*M"
  ],
  "side_condition_refs": [
    "DOM.NONZERO_DENOMINATOR",
    "DOM.POSITIVE_COORDINATE"
  ]
}
```

### Zero obligation

```text
lhs_expr = 2*M/(r**2*(r-2*M)) - 2*M/(r**2*(r-2*M))
target_normal_form = 0
```

### Route inventory

| route_id | route_kind | steps | final_expr | raw_trace_hash |
|---|---|---:|---|---|
| `schwarzschild_route_A_direct_pair` | direct | 2 | `0` | `b9b67cf777afdd2b` |
| `schwarzschild_route_B_numerator_zero` | factored | 3 | `0` | `78b0315d03a2ee98` |

### Step class inventory

| route_id | step_id | rule_id | class | replay_method | trust_boundary |
|---|---|---|---|---|---|
| `schwarzschild_route_A_direct_pair` | `A1` | `TDEF.RICCI_CONTRACTION` | tensor_definition | declared_tensor_rule_plus_algebra_leaf | declared_tensor_step |
| `schwarzschild_route_A_direct_pair` | `A2` | `ALG.COMMON_DENOM_CANCEL` | algebra | sympy_simplify_zero_difference | checked_algebra_leaf |
| `schwarzschild_route_B_numerator_zero` | `B1` | `TDEF.RICCI_CONTRACTION` | tensor_definition | declared_tensor_rule_plus_algebra_leaf | declared_tensor_step |
| `schwarzschild_route_B_numerator_zero` | `B2` | `ALG.COMMON_DENOM_CANCEL` | algebra | sympy_simplify_zero_difference | checked_algebra_leaf |
| `schwarzschild_route_B_numerator_zero` | `B3` | `ALG.ADD_INVERSE` | algebra | sympy_simplify_zero_difference | checked_algebra_leaf |

### Content interpretation

```text
normalized_hash = 963d459cf28463e9
formal_fragment = elementary_algebra_zero
trust_boundary = level_B_tensor_skeleton_plus_algebra_leaf_replay
```

## zero.ppwave.Ricci_uu_harmonic_profile

### Object signature

```json
{
  "geometry": "pp-wave harmonic profile",
  "tensor": "Ricci",
  "component": "R_uu",
  "coordinate_chart": "Brinkmann",
  "index_convention": "EML-GR v0.44 selected component convention",
  "structural_zero": false
}
```

### Domain

```json
{
  "domain_id": "domain.ppwave.real_harmonic_profile",
  "conditions": [
    "A real",
    "k real",
    "u,x,y real"
  ],
  "side_condition_refs": [
    "DOM.REAL_BRANCH"
  ]
}
```

### Zero obligation

```text
lhs_expr = -1/2*(diff(A*exp(k*u)*(x**2-y**2), x, 2) + diff(A*exp(k*u)*(x**2-y**2), y, 2))
target_normal_form = 0
```

### Route inventory

| route_id | route_kind | steps | final_expr | raw_trace_hash |
|---|---|---:|---|---|
| `ppwave_route_A_second_derivatives` | definition_first | 3 | `0` | `8df31e322084cf0e` |
| `ppwave_route_B_harmonic_laplacian` | factored | 3 | `0` | `52ceb8d349d74b9e` |

### Step class inventory

| route_id | step_id | rule_id | class | replay_method | trust_boundary |
|---|---|---|---|---|---|
| `ppwave_route_A_second_derivatives` | `A1` | `TDEF.PPWAVE_RICCI_UU` | tensor_definition | declared_tensor_rule_plus_algebra_leaf | declared_tensor_step |
| `ppwave_route_A_second_derivatives` | `A2` | `CALC.SECOND_DIFF_QUADRATIC` | calculus | sympy_simplify_zero_difference | checked_algebra_leaf |
| `ppwave_route_A_second_derivatives` | `A3` | `ALG.ADD_INVERSE` | algebra | sympy_simplify_zero_difference | checked_algebra_leaf |
| `ppwave_route_B_harmonic_laplacian` | `B1` | `TDEF.PPWAVE_RICCI_UU` | tensor_definition | declared_tensor_rule_plus_algebra_leaf | declared_tensor_step |
| `ppwave_route_B_harmonic_laplacian` | `B2` | `CALC.SECOND_DIFF_QUADRATIC` | calculus | sympy_simplify_zero_difference | checked_algebra_leaf |
| `ppwave_route_B_harmonic_laplacian` | `B3` | `ALG.MUL_ZERO` | algebra | sympy_simplify_zero_difference | checked_algebra_leaf |

### Content interpretation

```text
normalized_hash = 3a4ff980c09752b5
formal_fragment = tensor_skeleton_plus_algebra_leaf
trust_boundary = level_B_tensor_skeleton_plus_algebra_leaf_replay
```
