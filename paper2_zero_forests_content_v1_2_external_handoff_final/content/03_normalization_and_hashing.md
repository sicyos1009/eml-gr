# Normalization and hashing content v0.3

## Content distinction

The paper content needs to separate two objects that are often confused:

```text
raw trace:
  path-sensitive, backend/order-sensitive, useful for audit and debugging

normalized evidence:
  path-independent, claim-level, useful for compression and citation
```

## Raw hash material

```json
{
  "route_id": "...",
  "route_kind": "...",
  "steps": [...],
  "final_expr": "...",
  "route_notes": "..."
}
```

Changing any field above should invalidate the raw route hash.

## Normalized hash material

```json
{
  "schema_major": "1.2",
  "kind": "zero_certificate",
  "claim_id": "...",
  "object_signature": {...},
  "domain_signature": {
    "domain_id": "...",
    "conditions": [...],
    "side_condition_refs": [...]
  },
  "assumptions_canonical": [...],
  "zero_obligation": {
    "lhs_expr": "...",
    "target_normal_form": "0"
  },
  "final_normal_form": "0",
  "required_rule_classes_sorted": [...],
  "side_condition_refs_sorted": [...],
  "formal_fragment": "..."
}
```

## Ignored in normalized hash

```text
route_id
route_kind
steps
raw_trace_hash
route_notes
backend-specific rewrite order
```

## Content result from seed bundle

| Quantity | Value |
|---|---:|
| zero claims | 4 |
| raw routes | 8 |
| raw hashes recomputed OK | 8 |
| normalized hashes recomputed OK | 4 |
| unique normalized certificates | 4 |
| route-to-claim compression | 8:4 |

## Interpretive sentence for later paper

The normalized hash is a citation handle for the claim-level evidence, not for a particular simplifier path.  The raw route hash remains necessary when auditing how the claim was obtained.
