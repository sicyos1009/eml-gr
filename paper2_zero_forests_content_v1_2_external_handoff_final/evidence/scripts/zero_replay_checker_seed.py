#!/usr/bin/env python3
"""
EML-GR Zero Forest WP10 seed replay checker.

This checker intentionally verifies a narrow fragment:
  - bundle structure sufficient for v1.2 draft examples
  - rule IDs are present in the rule registry
  - raw route hashes recompute
  - normalized hashes recompute
  - scalar before/after steps replay by SymPy simplify(before-after)==0
  - declared tensor steps are recorded at the trust boundary and must be algebraically neutral here
  - each route ends at zero
  - all routes for each claim collapse to one normalized hash

It is not a full tensor calculus checker and not a proof-assistant development.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any, Dict, List, Tuple

import sympy as sp

SYMBOL_NAMES = ["rho", "r", "M", "H", "t", "A", "k", "u", "x", "y"]
SYMBOLS = {name: sp.symbols(name) for name in SYMBOL_NAMES}
LOCALS = dict(SYMBOLS)
LOCALS.update({"diff": sp.diff, "exp": sp.exp, "sqrt": sp.sqrt, "log": sp.log})


def canonical_json(obj: Any) -> str:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def hash16(obj: Any) -> str:
    return hashlib.sha256(canonical_json(obj).encode("utf-8")).hexdigest()[:16]


def parse_expr(expr: str) -> sp.Expr:
    try:
        return sp.sympify(expr, locals=LOCALS)
    except Exception as exc:  # pragma: no cover - diagnostic path
        raise ValueError(f"could not parse expression {expr!r}: {exc}") from exc


def expr_equal_zero_difference(before: str, after: str) -> Tuple[bool, str]:
    lhs = parse_expr(before)
    rhs = parse_expr(after)
    diff = sp.simplify(lhs - rhs)
    return bool(diff == 0), str(diff)


def expr_is_zero(expr: str) -> Tuple[bool, str]:
    parsed = parse_expr(expr)
    simplified = sp.simplify(parsed)
    return bool(simplified == 0), str(simplified)


def recompute_raw_route_hash(route: Dict[str, Any]) -> str:
    material = {
        "route_id": route["route_id"],
        "route_kind": route["route_kind"],
        "steps": route["steps"],
        "final_expr": route["final_expr"],
        "route_notes": route.get("route_notes", ""),
    }
    return hash16(material)


def recompute_normalized_hash(cert: Dict[str, Any]) -> str:
    obj_sig = cert["object_signature"]
    domain = cert["domain"]
    norm = cert["normalized_obligation"]
    material = {
        "schema_major": "1.2",
        "kind": "zero_certificate",
        "claim_id": cert["claim_id"],
        "object_signature": obj_sig,
        "domain_signature": {
            "domain_id": domain["domain_id"],
            "conditions": sorted(domain.get("conditions", [])),
            "side_condition_refs": sorted(domain.get("side_condition_refs", [])),
        },
        "assumptions_canonical": sorted(cert.get("assumptions", [])),
        "zero_obligation": {
            "lhs_expr": norm["lhs_expr"],
            "target_normal_form": norm["target_normal_form"],
        },
        "final_normal_form": "0",
        "required_rule_classes_sorted": sorted(norm.get("required_rule_classes", [])),
        "side_condition_refs_sorted": sorted(norm.get("side_condition_refs", [])),
        "formal_fragment": cert["formal_fragment"],
    }
    return hash16(material)


def validate_bundle_shape(bundle: Dict[str, Any]) -> List[str]:
    errors: List[str] = []
    for key in ["schema_id", "schema_version", "rule_registry", "certificates"]:
        if key not in bundle:
            errors.append(f"missing top-level key: {key}")
    if bundle.get("schema_id") != "eml-gr-zero-certificate-bundle":
        errors.append("unexpected schema_id")
    if bundle.get("schema_version") != "1.2.0-draft":
        errors.append("unexpected schema_version")
    return errors


def replay_step(step: Dict[str, Any], registry: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
    rule_id = step.get("rule_id")
    result = {
        "step_id": step.get("step_id"),
        "rule_id": rule_id,
        "rule_registered": rule_id in registry,
        "rule_class_matches_registry": False,
        "replay_ok": False,
        "trust_boundary": step.get("trust_boundary"),
        "replay_method": step.get("replay_method"),
        "diagnostic": "",
    }
    if rule_id not in registry:
        result["diagnostic"] = "rule ID missing from registry"
        return result
    result["rule_class_matches_registry"] = registry[rule_id]["rule_class"] == step.get("rule_class")
    if not result["rule_class_matches_registry"]:
        result["diagnostic"] = "rule class mismatch"
        return result

    method = step.get("replay_method")
    try:
        if method in {"sympy_simplify_zero_difference", "declared_tensor_rule_plus_algebra_leaf"}:
            ok, diff = expr_equal_zero_difference(step["before_expr"], step["after_expr"])
            result["replay_ok"] = ok
            result["diagnostic"] = "difference_normal_form=" + diff
        elif method == "laurent_normal_form":
            ok, diff = expr_equal_zero_difference(step["before_expr"], step["after_expr"])
            result["replay_ok"] = ok
            result["diagnostic"] = "laurent_seed_delegated_to_sympy_difference=" + diff
        else:
            result["replay_ok"] = False
            result["diagnostic"] = f"unsupported replay method in seed checker: {method}"
    except Exception as exc:
        result["replay_ok"] = False
        result["diagnostic"] = str(exc)
    return result


def replay_bundle(bundle: Dict[str, Any]) -> Dict[str, Any]:
    errors = validate_bundle_shape(bundle)
    registry = {rule["rule_id"]: rule for rule in bundle.get("rule_registry", [])}
    claim_ids = [cert.get("claim_id") for cert in bundle.get("certificates", [])]
    duplicate_claims = sorted({c for c in claim_ids if claim_ids.count(c) > 1})

    cert_reports = []
    route_count = 0
    raw_hash_ok_count = 0
    normalized_hash_ok_count = 0
    all_steps_ok = True
    all_routes_final_zero = True
    all_raw_hashes: List[str] = []
    normalized_by_claim: Dict[str, List[str]] = defaultdict(list)
    raw_by_claim: Dict[str, List[str]] = defaultdict(list)

    for cert in bundle.get("certificates", []):
        cert_norm_recomputed = recompute_normalized_hash(cert)
        norm_hash_ok = cert_norm_recomputed == cert.get("normalized_hash")
        if norm_hash_ok:
            normalized_hash_ok_count += 1
        claim_id = cert["claim_id"]
        normalized_by_claim[claim_id].append(cert.get("normalized_hash"))

        route_reports = []
        for route in cert.get("routes", []):
            route_count += 1
            raw_recomputed = recompute_raw_route_hash(route)
            raw_ok = raw_recomputed == route.get("raw_trace_hash")
            raw_hash_ok_count += int(raw_ok)
            all_raw_hashes.append(route.get("raw_trace_hash"))
            raw_by_claim[claim_id].append(route.get("raw_trace_hash"))

            step_reports = [replay_step(step, registry) for step in route.get("steps", [])]
            route_steps_ok = all(s["rule_registered"] and s["rule_class_matches_registry"] and s["replay_ok"] for s in step_reports)
            final_zero_ok, final_nf = expr_is_zero(route.get("final_expr", "NaN"))
            route_ok = raw_ok and route_steps_ok and final_zero_ok
            all_steps_ok = all_steps_ok and route_steps_ok
            all_routes_final_zero = all_routes_final_zero and final_zero_ok
            route_reports.append({
                "route_id": route.get("route_id"),
                "raw_trace_hash_reported": route.get("raw_trace_hash"),
                "raw_trace_hash_recomputed": raw_recomputed,
                "raw_trace_hash_ok": raw_ok,
                "steps_ok": route_steps_ok,
                "final_zero_ok": final_zero_ok,
                "final_normal_form": final_nf,
                "route_replay_ok": route_ok,
                "step_reports": step_reports,
            })

        cert_reports.append({
            "claim_id": claim_id,
            "normalized_hash_reported": cert.get("normalized_hash"),
            "normalized_hash_recomputed": cert_norm_recomputed,
            "normalized_hash_ok": norm_hash_ok,
            "formal_fragment": cert.get("formal_fragment"),
            "trust_boundary": cert.get("trust_boundary"),
            "route_count": len(cert.get("routes", [])),
            "routes": route_reports,
        })

    collapse_details = []
    collapse_ok = True
    for claim_id, norm_hashes in normalized_by_claim.items():
        unique_norm = sorted(set(norm_hashes))
        unique_raw = sorted(set(raw_by_claim[claim_id]))
        # In this seed each claim is one certificate with multiple routes, so norm list length is one;
        # the route collapse condition is checked against route raw hash diversity and one cert hash.
        claim_collapse_ok = len(unique_norm) == 1 and len(unique_raw) >= 1
        # For cases with two routes, require raw hashes to be different.
        if len(raw_by_claim[claim_id]) >= 2:
            claim_collapse_ok = claim_collapse_ok and len(unique_raw) == len(raw_by_claim[claim_id])
        collapse_ok = collapse_ok and claim_collapse_ok
        collapse_details.append({
            "claim_id": claim_id,
            "route_count": len(raw_by_claim[claim_id]),
            "unique_raw_trace_hashes": len(unique_raw),
            "unique_normalized_hashes": len(unique_norm),
            "collapse_ok": claim_collapse_ok,
        })

    review_pass = (
        not errors
        and not duplicate_claims
        and all_steps_ok
        and all_routes_final_zero
        and raw_hash_ok_count == route_count
        and normalized_hash_ok_count == len(bundle.get("certificates", []))
        and collapse_ok
    )

    return {
        "title": "EML-GR Zero Forest WP10 seed replay report",
        "schema_version": bundle.get("schema_version"),
        "artifact_version": bundle.get("artifact_version"),
        "review_pass": review_pass,
        "errors": errors,
        "duplicate_claims": duplicate_claims,
        "counts": {
            "zero_claims": len(bundle.get("certificates", [])),
            "routes": route_count,
            "raw_hashes_recomputed_ok": raw_hash_ok_count,
            "normalized_hashes_recomputed_ok": normalized_hash_ok_count,
            "unique_normalized_certificates": len({cert.get("normalized_hash") for cert in bundle.get("certificates", [])}),
        },
        "reviews": {
            "schema_shape_ok": not errors,
            "claim_ids_unique": not duplicate_claims,
            "all_steps_replay_ok": all_steps_ok,
            "all_routes_final_zero": all_routes_final_zero,
            "all_raw_trace_hashes_ok": raw_hash_ok_count == route_count,
            "all_normalized_hashes_ok": normalized_hash_ok_count == len(bundle.get("certificates", [])),
            "routes_collapse_by_claim": collapse_ok,
        },
        "compression": {
            "raw_route_count": route_count,
            "canonical_claim_count": len(bundle.get("certificates", [])),
            "unique_normalized_certificate_count": len({cert.get("normalized_hash") for cert in bundle.get("certificates", [])}),
            "route_to_claim_compression": f"{route_count}:{len(bundle.get('certificates', []))}",
        },
        "collapse_details": collapse_details,
        "certificate_reports": cert_reports,
    }


def main(argv: List[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--bundle", required=True, help="Path to zero certificate bundle JSON")
    parser.add_argument("--out", required=True, help="Path to write replay report JSON")
    args = parser.parse_args(argv)

    bundle_path = Path(args.bundle)
    out_path = Path(args.out)
    bundle = json.loads(bundle_path.read_text(encoding="utf-8"))
    report = replay_bundle(bundle)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({"review_pass": report["review_pass"], "counts": report["counts"], "compression": report["compression"]}, indent=2, ensure_ascii=False))
    return 0 if report["review_pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
