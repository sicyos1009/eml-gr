# 19. v0.5 claim delta

## New in v0.5

```text
- FLRW contracted-Bianchi seed has named tensor subleaves.
- The replay bundle includes tensor_subleaves on the FLRW certificate.
- v0.5 strict checker adds RC9 tensor-subleaf discipline.
- Tamper suite includes subleaf hash, sign, dependency, divergence, and route-reference attacks.
- Metric-compatibility and index-symmetry rules are registered as explicit tensor-identity boundaries.
```

## Strengthened claim

The FLRW seed is no longer only:

```text
declared tensor boundary -> scalar algebra cancellation
```

It is now:

```text
declared tensor boundary
  -> named tensor subleaves
  -> checked subleaf dependency/hash discipline
  -> selected scalar divergence assembly
  -> scalar zero replay
```

## Still not claimed

```text
- full tensor CAS verification
- full contracted-Bianchi formalization
- complete proof-assistant evidence
- arbitrary FLRW equation-of-state treatment
```
