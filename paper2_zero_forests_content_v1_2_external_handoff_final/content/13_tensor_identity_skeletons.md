# Tensor identity skeletons v0.4-final

The tensor identities remain at the Level-B trust boundary.  Their role here is to identify the scalar leaf exported to the zero replay system.

## Rindler selected Riemann component

```text
component: R^eta_{rho eta rho}
exported leaf: -diff(1/rho, rho) - 1/rho**2
checked leaf: derivative of reciprocal + additive inverse
boundary: Christoffel-to-Riemann expansion declared
```

## FLRW contracted Bianchi selected component

```text
component: nabla_mu G^{mu0}
metric family: flat de Sitter FLRW, a(t)=exp(H*t)
exported leaf:
  3*H*3*H**2 + 3*(H*exp(2*H*t))*(-3*H**2*exp(-2*H*t))
checked leaf: exp cancellation + additive inverse / zero multiplication
boundary: covariant-divergence skeleton declared
```

Skeleton target for v0.5:

```text
nabla_mu G^{mu0}
  = partial_t G^{00}
  + Gamma^mu_{mu lambda} G^{lambda 0}
  + Gamma^0_{mu lambda} G^{mu lambda}
```

v0.4-final records the skeleton but does not yet name each Christoffel and Einstein-tensor subleaf.

## Schwarzschild selected Ricci channel pair

```text
exported leaf:
  2*M/(r**2*(r-2*M)) - 2*M/(r**2*(r-2*M))
checked leaf: common-denominator cancellation under r**2*(r-2*M) != 0
boundary: Ricci contraction declared
```

## pp-wave harmonic profile

```text
profile: H(u,x,y)=A*exp(k*u)*(x**2-y**2)
selected component: R_uu = -1/2*(H_xx + H_yy)
exported leaf:
  -1/2*(diff(A*exp(k*u)*(x**2-y**2), x, 2) + diff(A*exp(k*u)*(x**2-y**2), y, 2))
checked leaf: second derivatives + additive inverse / zero multiplication
boundary: pp-wave Ricci formula declared
```
