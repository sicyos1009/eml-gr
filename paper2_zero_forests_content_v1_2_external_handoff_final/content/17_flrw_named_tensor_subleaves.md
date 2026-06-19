# 17. FLRW named tensor subleaves v0.5

This content block upgrades the FLRW contracted-Bianchi seed from a single declared tensor boundary into a named-subleaf boundary. It is still **not** a full tensor-CAS proof. The new object is a structured bridge between the tensor identity and the replayed algebraic zero leaf.

## Selected claim

```text
claim_id: zero.flrw.contracted_bianchi_divG0
selected component: ∇_μ G^{μ0}
metric family: flat FLRW with a(t)=exp(H*t)
domain: H>0, t real, real branch
```

The replayed normalized scalar leaf is:

```text
diff(3*H**2, t) + 3*H*3*H**2 + 3*(H*exp(2*H*t))*(-3*H**2*exp(-2*H*t))
```

The cancellation is:

```text
diff(3*H**2,t) = 0
exp(2*H*t)*exp(-2*H*t) = 1
9*H**3 - 9*H**3 = 0
```

## Named tensor subleaves

| subleaf | role | selected scalar payload | boundary status |
|---|---|---|---|
| `flrw.metric.scale_factor` | metric/inverse spatial diagonal | `a=exp(H*t)`, `g_ii=exp(2*H*t)`, `g^ii=exp(-2*H*t)` | declared + scalar consistency |
| `flrw.connection.gamma_trace_0` | `Σ_μ Γ^μ_{μ0}` | `3*H` | declared + scalar consistency |
| `flrw.connection.gamma_0ii` | spatial diagonal `Γ^0_{ii}` | `H*exp(2*H*t)` with multiplicity 3 | declared + scalar consistency |
| `flrw.einstein.G_contra_00` | selected Einstein component | `3*H**2` | declared tensor subleaf |
| `flrw.einstein.G_contra_ii` | selected spatial Einstein component | `-3*H**2*exp(-2*H*t)` | declared tensor subleaf |
| `flrw.divergence.expanded_nu0` | selected divergence expansion | partial + trace + spatial connection terms | declared + scalar consistency |

## Dependency graph

```text
flrw.metric.scale_factor
  -> flrw.connection.gamma_trace_0
  -> flrw.connection.gamma_0ii
  -> flrw.einstein.G_contra_00
  -> flrw.einstein.G_contra_ii

flrw.connection.gamma_trace_0
flrw.connection.gamma_0ii
flrw.einstein.G_contra_00
flrw.einstein.G_contra_ii
  -> flrw.divergence.expanded_nu0
  -> zero.flrw.contracted_bianchi_divG0
```

## Claim posture

The content-level improvement is that the tensor boundary is no longer one opaque sentence. It is a list of typed, hashed, dependency-checked subleaves feeding a replayed scalar cancellation. The remaining trust boundary is explicit: the seed still does not derive every Christoffel, Ricci, or Einstein component from the metric inside a formal tensor kernel.
