# Zero Forest Casebook v0.1

This casebook fixes the first four WP10 zero-forest proof obligations. Each case has two route traces in `examples/zero_bundle_v1_2.examples.json` and is replayed by `scripts/zero_replay_checker_seed.py`.

## 1. Rindler curvature zero forest

**Claim ID:** `zero.rindler.Riemann_eta_rho_eta_rho`  
**Domain:** `rho > 0`  
**Status target:** route count >= 2, all routes collapse to one normalized certificate.

Rindler exposes the distinction between connection nontriviality and curvature triviality. A selected algebraic leaf is:

```text
-diff(1/rho, rho) - 1/rho**2 = 0
```

Two routes are recorded:

```text
route_A: differentiate 1/rho first, then cancel common terms
route_B: rewrite 1/rho as rho**(-1), then cancel
```

Both routes have different raw trace hashes but the same normalized hash.

## 2. FLRW contracted Bianchi zero forest

**Claim ID:** `zero.flrw.contracted_bianchi_divG0`  
**Domain:** `H > 0`, real time coordinate  
**Status target:** contracted Bianchi proof object replay.

A selected de Sitter FLRW leaf is:

```text
3*H*3*H**2 + 3*(H*exp(2*H*t))*(-3*H**2*exp(-2*H*t)) = 0
```

The two route traces separate tensor identity declaration from algebraic leaf replay:

```text
route_A: expand contracted divergence, cancel exp(2Ht) exp(-2Ht)
route_B: factor 9H^3 first, then cancel
```

## 3. Schwarzschild Ricci-channel zero forest

**Claim ID:** `zero.schwarzschild.ricci_channel_pair`  
**Domain:** `M > 0`, `r > 2M`  
**Status target:** selected Ricci zero proof object replay.

A selected exterior-domain Ricci-channel leaf is:

```text
2*M/(r**2*(r-2*M)) - 2*M/(r**2*(r-2*M)) = 0
```

The replay checker requires the side condition that the denominator is nonzero on the stated domain.

## 4. pp-wave Ricci-flat harmonic-profile zero forest

**Claim ID:** `zero.ppwave.Ricci_uu_harmonic_profile`  
**Domain:** real coordinates, selected harmonic transverse profile  
**Status target:** pp-wave Ricci-flat proof object replay.

For

```text
H(u,x,y) = A*exp(k*u)*(x**2 - y**2)
```

one has

```text
R_uu = -1/2*(H_xx + H_yy) = 0.
```

The proof object records a tensor-definition step for the pp-wave Ricci component and an algebraic leaf that checks the transverse harmonic cancellation.

## 5. Compression target

The seed bundle currently has:

```text
route traces:           8
canonical zero claims:  4
expected collapse:      8 raw traces -> 4 normalized certificates
```

The next implementation target is to attach full tensor-index family metadata to each claim while keeping the algebra leaf check unchanged.
