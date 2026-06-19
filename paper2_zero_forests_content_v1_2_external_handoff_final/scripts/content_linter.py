#!/usr/bin/env python3
from __future__ import annotations

import argparse
import importlib.util
import json
from pathlib import Path
from typing import Any, Dict, List


def load_checker(checker_path: Path):
    spec = importlib.util.spec_from_file_location("zero_replay_checker_seed", str(checker_path))
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def lint_bundle(bundle: Dict[str, Any], checker) -> Dict[str, Any]:
    issues: List[Dict[str, Any]] = []
    warnings: List[Dict[str, Any]] = []
    registry = {r["rule_id"]: r for r in bundle.get("rule_registry", [])}
    if len(registry) != len(bundle.get("rule_registry", [])):
        issues.append({"level": "error", "code": "DUPLICATE_RULE_ID", "message": "rule_registry has duplicate rule_id entries"})

    for cert in bundle.get("certificates", []):
        claim_id = cert.get("claim_id")
        norm = cert.get("normalized_obligation", {})
        domain = cert.get("domain", {})
        if cert.get("formal_fragment") != norm.get("formal_fragment"):
            issues.append({"level": "error", "code": "FORMAL_FRAGMENT_MISMATCH", "claim_id": claim_id})
        try:
            norm_recomputed = checker.recompute_normalized_hash(cert)
        except Exception as exc:
            norm_recomputed = f"ERROR: {exc}"
        if norm_recomputed != cert.get("normalized_hash"):
            issues.append({
                "level": "error",
                "code": "NORMALIZED_HASH_MISMATCH",
                "claim_id": claim_id,
                "reported": cert.get("normalized_hash"),
                "recomputed": norm_recomputed,
            })
        domain_refs = set(domain.get("side_condition_refs", []))
        norm_refs = set(norm.get("side_condition_refs", []))
        if domain_refs != norm_refs:
            issues.append({
                "level": "error",
                "code": "DOMAIN_REF_MISMATCH",
                "claim_id": claim_id,
                "domain_refs": sorted(domain_refs),
                "normalized_refs": sorted(norm_refs),
            })
        required_classes = set(norm.get("required_rule_classes", []))
        if "domain" in required_classes and not domain.get("side_condition_refs"):
            issues.append({"level": "error", "code": "DOMAIN_REQUIRED_BUT_NO_SIDE_REFS", "claim_id": claim_id})

        for route in cert.get("routes", []):
            route_id = route.get("route_id")
            steps = route.get("steps", [])
            if not steps:
                issues.append({"level": "error", "code": "EMPTY_ROUTE", "claim_id": claim_id, "route_id": route_id})
                continue
            first_before = steps[0].get("before_expr")
            # Initial expressions may use alternate but equivalent surface syntax
            # (for example 1/rho versus rho**(-1)).  Require algebraic
            # equivalence to the normalized obligation, while keeping adjacent
            # step chaining syntactic below.
            try:
                initial_ok, initial_diff = checker.expr_equal_zero_difference(first_before, norm.get("lhs_expr"))
            except Exception as exc:
                initial_ok, initial_diff = False, str(exc)
            if not initial_ok:
                issues.append({
                    "level": "error",
                    "code": "ROUTE_INITIAL_EXPR_MISMATCH",
                    "claim_id": claim_id,
                    "route_id": route_id,
                    "expected": norm.get("lhs_expr"),
                    "observed": first_before,
                    "difference_normal_form": initial_diff,
                })
            last_after = steps[-1].get("after_expr")
            if last_after != route.get("final_expr"):
                issues.append({
                    "level": "error",
                    "code": "ROUTE_FINAL_EXPR_MISMATCH",
                    "claim_id": claim_id,
                    "route_id": route_id,
                    "expected_final_expr": route.get("final_expr"),
                    "last_step_after_expr": last_after,
                })
            for i, (a, b) in enumerate(zip(steps, steps[1:]), start=1):
                if a.get("after_expr") != b.get("before_expr"):
                    issues.append({
                        "level": "error",
                        "code": "ROUTE_CHAIN_DISCONNECT",
                        "claim_id": claim_id,
                        "route_id": route_id,
                        "step_index": i,
                        "left_step": a.get("step_id"),
                        "right_step": b.get("step_id"),
                        "left_after": a.get("after_expr"),
                        "right_before": b.get("before_expr"),
                    })
            raw_recomputed = checker.recompute_raw_route_hash(route)
            if raw_recomputed != route.get("raw_trace_hash"):
                issues.append({"level": "error", "code": "RAW_HASH_MISMATCH", "claim_id": claim_id, "route_id": route_id})
            for step in steps:
                rule_id = step.get("rule_id")
                if rule_id not in registry:
                    issues.append({"level": "error", "code": "UNREGISTERED_RULE", "claim_id": claim_id, "route_id": route_id, "rule_id": rule_id})
                    continue
                if registry[rule_id].get("rule_class") != step.get("rule_class"):
                    issues.append({"level": "error", "code": "RULE_CLASS_MISMATCH", "claim_id": claim_id, "route_id": route_id, "rule_id": rule_id})
                if step.get("rule_class") in {"tensor_definition", "tensor_identity"}:
                    warnings.append({
                        "level": "warning",
                        "code": "DECLARED_TENSOR_BOUNDARY",
                        "claim_id": claim_id,
                        "route_id": route_id,
                        "step_id": step.get("step_id"),
                        "message": "Tensor step is declared at Level-B boundary; only algebraic neutrality is checked by seed replay.",
                    })
    return {
        "title": "Paper2 content linter report for zero forest bundles",
        "content_lint_pass": not any(i["level"] == "error" for i in issues),
        "error_count": sum(i["level"] == "error" for i in issues),
        "warning_count": len(warnings),
        "issues": issues,
        "warnings": warnings,
    }


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--bundle", required=True)
    p.add_argument("--checker", required=True)
    p.add_argument("--out", required=True)
    args = p.parse_args()
    checker = load_checker(Path(args.checker))
    bundle = json.loads(Path(args.bundle).read_text(encoding="utf-8"))
    report = lint_bundle(bundle, checker)
    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    Path(args.out).write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({"content_lint_pass": report["content_lint_pass"], "error_count": report["error_count"], "warning_count": report["warning_count"]}, indent=2))
    return 0 if report["content_lint_pass"] else 1

if __name__ == "__main__":
    raise SystemExit(main())
