#!/usr/bin/env python3
from __future__ import annotations

import argparse, hashlib, json
from collections import defaultdict
from pathlib import Path
from typing import Any, Dict, List, Set, Tuple
import sympy as sp

SYMS = {n: sp.symbols(n) for n in ["rho","r","M","H","t","A","k","u","x","y"]}
LOCALS = dict(SYMS)
LOCALS.update({"diff": sp.diff, "exp": sp.exp, "sqrt": sp.sqrt, "log": sp.log})
TENSOR_CLASSES = {"tensor_definition", "tensor_identity"}
RULE_REQUIRED_REFS = {
    "ALG.COMMON_DENOM_CANCEL": {"DOM.NONZERO_DENOMINATOR"},
    "ALG.EXP_CANCEL": {"DOM.REAL_BRANCH"},
    "DOM.NONZERO_DENOMINATOR": {"DOM.NONZERO_DENOMINATOR"},
    "DOM.POSITIVE_COORDINATE": {"DOM.POSITIVE_COORDINATE"},
    "DOM.REAL_BRANCH": {"DOM.REAL_BRANCH"},
}

def canonical_json(obj: Any) -> str:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False)

def hash16(obj: Any) -> str:
    return hashlib.sha256(canonical_json(obj).encode("utf-8")).hexdigest()[:16]

def parse_expr(s: str) -> sp.Expr:
    return sp.sympify(s, locals=LOCALS)

def expr_equal(a: str, b: str) -> Tuple[bool, str]:
    try:
        d = sp.simplify(parse_expr(a) - parse_expr(b))
        return bool(d == 0), str(d)
    except Exception as e:
        return False, f"ERROR:{e}"

def expr_zero(s: str) -> Tuple[bool, str]:
    try:
        z = sp.simplify(parse_expr(s))
        return bool(z == 0), str(z)
    except Exception as e:
        return False, f"ERROR:{e}"

def recompute_raw_route_hash(route: Dict[str, Any]) -> str:
    return hash16({
        "route_id": route["route_id"],
        "route_kind": route["route_kind"],
        "steps": route["steps"],
        "final_expr": route["final_expr"],
        "route_notes": route.get("route_notes", ""),
    })

def recompute_normalized_hash(cert: Dict[str, Any]) -> str:
    d = cert["domain"]
    n = cert["normalized_obligation"]
    return hash16({
        "schema_major": "1.2",
        "kind": "zero_certificate",
        "claim_id": cert["claim_id"],
        "object_signature": cert["object_signature"],
        "domain_signature": {
            "domain_id": d["domain_id"],
            "conditions": sorted(d.get("conditions", [])),
            "side_condition_refs": sorted(d.get("side_condition_refs", [])),
        },
        "assumptions_canonical": sorted(cert.get("assumptions", [])),
        "zero_obligation": {
            "lhs_expr": n["lhs_expr"],
            "target_normal_form": n["target_normal_form"],
        },
        "final_normal_form": "0",
        "required_rule_classes_sorted": sorted(n.get("required_rule_classes", [])),
        "side_condition_refs_sorted": sorted(n.get("side_condition_refs", [])),
        "formal_fragment": cert["formal_fragment"],
    })

def c(s: str) -> str:
    return str(s).strip().replace(" ", "").replace("^", "**")

def cond_aliases(s: str) -> Set[str]:
    cc = c(s)
    out = {cc}
    low = cc.lower()
    if low in {"treal", "t∈r", "t∈ℝ"}: out |= {"treal", "t real"}
    if low in {"hreal", "h∈r", "h∈ℝ"}: out |= {"Hreal", "H real"}
    if low in {"realbranch", "real_branch"}: out |= {"realbranch", "real branch"}
    return out

def domain_entailments(cert: Dict[str, Any]) -> Set[str]:
    base: Set[str] = set()
    for s in cert.get("assumptions", []) + cert.get("domain", {}).get("conditions", []):
        base |= cond_aliases(s)
    ent = set(base)
    if "rho>0" in base:
        ent |= {"rho>0", "rho**2!=0"}
    if "H>0" in base:
        ent |= {"H>0", "Hreal", "H real"}
    if "treal" in base or "t real" in base:
        ent |= {"treal", "t real"}
    if ("H>0" in base or "Hreal" in base or "H real" in base) and ("treal" in base or "t real" in base):
        ent |= {"realbranch", "real branch"}
    if "M>0" in base:
        ent |= {"M>0"}
    if "r>2*M" in base and "M>0" in base:
        ent |= {"r>2*M", "r**2*(r-2*M)!=0"}
    return ent

def side_entailed(side: str, ent: Set[str]) -> bool:
    if side is None or str(side).strip() == "": return True
    aliases = cond_aliases(side)
    return bool(aliases & ent) or c(side) in ent

def add_issue(issues: List[Dict[str, Any]], gate: str, code: str, **kw):
    item = {"severity":"error", "gate":gate, "code":code}
    item.update(kw)
    issues.append(item)

def replay_step(step: Dict[str, Any], registry: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
    rid = step.get("rule_id")
    rep = {"step_id": step.get("step_id"), "rule_id": rid, "ok": False, "diagnostic": ""}
    if rid not in registry:
        rep["diagnostic"] = "unregistered rule"
        return rep
    if registry[rid].get("rule_class") != step.get("rule_class"):
        rep["diagnostic"] = "rule class mismatch"
        return rep
    if step.get("rule_class") in TENSOR_CLASSES:
        if step.get("trust_boundary") != "declared_tensor_step" or not str(step.get("replay_method","")).startswith("declared_tensor"):
            rep["diagnostic"] = "invalid tensor boundary label"
            return rep
    ok, diff = expr_equal(step.get("before_expr", "NaN"), step.get("after_expr", "NaN"))
    rep["ok"] = ok
    rep["diagnostic"] = "difference_normal_form=" + diff
    return rep

def replay_bundle(bundle: Dict[str, Any]) -> Dict[str, Any]:
    issues: List[Dict[str, Any]] = []
    warnings: List[Dict[str, Any]] = []
    for k in ["schema_id", "schema_version", "rule_registry", "certificates"]:
        if k not in bundle: add_issue(issues, "SCHEMA", "MISSING_TOP_LEVEL_KEY", key=k)
    if bundle.get("schema_id") != "eml-gr-zero-certificate-bundle": add_issue(issues, "SCHEMA", "BAD_SCHEMA_ID")
    if bundle.get("schema_version") != "1.2.0-draft": add_issue(issues, "SCHEMA", "BAD_SCHEMA_VERSION")
    registry = {r.get("rule_id"): r for r in bundle.get("rule_registry", [])}
    route_count = step_count = raw_ok = norm_ok = route_ok = step_ok = 0
    raw_by_claim, norm_by_claim = defaultdict(list), defaultdict(list)
    cert_reports = []
    for cert in bundle.get("certificates", []):
        claim = cert.get("claim_id")
        norm = cert.get("normalized_obligation", {})
        dom = cert.get("domain", {})
        ent = domain_entailments(cert)
        used_classes: Set[str] = set()
        required_classes = set(norm.get("required_rule_classes", []))
        rec_norm = recompute_normalized_hash(cert)
        norm_hash_ok = rec_norm == cert.get("normalized_hash")
        norm_ok += int(norm_hash_ok)
        norm_by_claim[claim].append(cert.get("normalized_hash"))
        if not norm_hash_ok: add_issue(issues, "RC4", "NORMALIZED_HASH_MISMATCH", claim_id=claim, reported=cert.get("normalized_hash"), recomputed=rec_norm)
        dom_refs, norm_refs = set(dom.get("side_condition_refs", [])), set(norm.get("side_condition_refs", []))
        if dom_refs != norm_refs: add_issue(issues, "RC8", "DOMAIN_REF_MISMATCH", claim_id=claim, domain_refs=sorted(dom_refs), normalized_refs=sorted(norm_refs))
        route_reports = []
        for route in cert.get("routes", []):
            route_count += 1
            rid = route.get("route_id")
            before_issue_count = len(issues)
            steps = route.get("steps", [])
            if not steps:
                add_issue(issues, "RC2", "EMPTY_ROUTE", claim_id=claim, route_id=rid)
                continue
            rec_raw = recompute_raw_route_hash(route)
            raw_hash_ok = rec_raw == route.get("raw_trace_hash")
            raw_ok += int(raw_hash_ok)
            raw_by_claim[claim].append(route.get("raw_trace_hash"))
            if not raw_hash_ok: add_issue(issues, "RC4", "RAW_HASH_MISMATCH", claim_id=claim, route_id=rid, reported=route.get("raw_trace_hash"), recomputed=rec_raw)
            init_ok, init_diff = expr_equal(steps[0].get("before_expr", "NaN"), norm.get("lhs_expr", "NaN"))
            if not init_ok: add_issue(issues, "RC1", "ROUTE_INITIAL_EXPR_MISMATCH", claim_id=claim, route_id=rid, difference_normal_form=init_diff)
            for i, (a,b) in enumerate(zip(steps, steps[1:]), start=1):
                if a.get("after_expr") != b.get("before_expr"):
                    add_issue(issues, "RC2", "ROUTE_CHAIN_DISCONNECT", claim_id=claim, route_id=rid, left_step=a.get("step_id"), right_step=b.get("step_id"))
            if steps[-1].get("after_expr") != route.get("final_expr"):
                add_issue(issues, "RC3", "ROUTE_FINAL_EXPR_MISMATCH", claim_id=claim, route_id=rid)
            fin_ok, fin_nf = expr_zero(route.get("final_expr", "NaN"))
            if not fin_ok: add_issue(issues, "RC3", "ROUTE_FINAL_NOT_ZERO", claim_id=claim, route_id=rid, final_normal_form=fin_nf)
            step_reports = []
            for st in steps:
                step_count += 1
                used_classes.add(st.get("rule_class"))
                rep = replay_step(st, registry)
                step_reports.append(rep)
                step_ok += int(rep["ok"])
                if st.get("rule_id") not in registry: add_issue(issues, "RC5", "UNREGISTERED_RULE", claim_id=claim, route_id=rid, step_id=st.get("step_id"), rule_id=st.get("rule_id"))
                elif registry[st.get("rule_id")].get("rule_class") != st.get("rule_class"):
                    add_issue(issues, "RC5", "RULE_CLASS_MISMATCH", claim_id=claim, route_id=rid, step_id=st.get("step_id"), rule_id=st.get("rule_id"))
                elif not rep["ok"]:
                    code = "TENSOR_BOUNDARY_LABEL_INVALID" if st.get("rule_class") in TENSOR_CLASSES and "tensor boundary" in rep["diagnostic"] else "STEP_SCALAR_REPLAY_FAILED"
                    add_issue(issues, "RC7" if code == "TENSOR_BOUNDARY_LABEL_INVALID" else "RC5", code, claim_id=claim, route_id=rid, step_id=st.get("step_id"), rule_id=st.get("rule_id"), diagnostic=rep["diagnostic"])
                if st.get("rule_class") in TENSOR_CLASSES:
                    warnings.append({"severity":"warning", "gate":"RC7", "code":"DECLARED_TENSOR_BOUNDARY", "claim_id":claim, "route_id":rid, "step_id":st.get("step_id")})
                for ref in RULE_REQUIRED_REFS.get(st.get("rule_id"), set()):
                    if ref not in dom_refs or ref not in norm_refs:
                        add_issue(issues, "RC8", "REQUIRED_DOMAIN_REF_MISSING", claim_id=claim, route_id=rid, step_id=st.get("step_id"), rule_id=st.get("rule_id"), required_ref=ref)
                for side in st.get("side_conditions", []) or []:
                    if not side_entailed(side, ent): add_issue(issues, "RC8", "SIDE_CONDITION_NOT_ENTAILED", claim_id=claim, route_id=rid, step_id=st.get("step_id"), side_condition=side, entailed=sorted(ent))
            route_pass = len(issues) == before_issue_count
            route_ok += int(route_pass)
            route_reports.append({"route_id":rid, "route_pass":route_pass, "raw_hash_ok":raw_hash_ok, "initial_ok":init_ok, "final_zero_ok":fin_ok, "step_reports": step_reports})
        if not used_classes.issubset(required_classes):
            add_issue(issues, "RC6", "REQUIRED_RULE_CLASSES_INCOMPLETE", claim_id=claim, classes_used=sorted(used_classes), required_rule_classes=sorted(required_classes), missing=sorted(used_classes-required_classes))
        cert_reports.append({"claim_id":claim, "normalized_hash_ok":norm_hash_ok, "classes_used":sorted(used_classes), "required_rule_classes":sorted(required_classes), "domain_entailed_seed_conditions":sorted(ent), "routes":route_reports})
    for claim, raws in raw_by_claim.items():
        unique_raw, unique_norm = set(raws), set(norm_by_claim.get(claim, []))
        if not (len(unique_norm) == 1 and len(unique_raw) >= 1 and (len(raws) < 2 or len(unique_raw)==len(raws))):
            add_issue(issues, "RC4", "ROUTE_COLLAPSE_FAILED", claim_id=claim)
    gates = {g: True for g in ["SCHEMA","RC1","RC2","RC3","RC4","RC5","RC6","RC7","RC8"]}
    for i in issues:
        gates[i.get("gate")] = False
    err_count = len(issues)
    return {
        "title":"Paper2 Zero Forests strict Level-B+ replay report v0.4-final",
        "review_pass": err_count == 0,
        "strict_level":"Level-B+ seed content",
        "schema_version": bundle.get("schema_version"),
        "artifact_version": bundle.get("artifact_version"),
        "counts": {"zero_claims":len(bundle.get("certificates", [])), "routes":route_count, "steps":step_count, "routes_ok":route_ok, "steps_ok":step_ok, "raw_hashes_recomputed_ok":raw_ok, "normalized_hashes_recomputed_ok":norm_ok, "unique_normalized_certificates":len({x.get("normalized_hash") for x in bundle.get("certificates", [])})},
        "gates": gates,
        "issue_count": err_count,
        "warning_count": len(warnings),
        "issues": issues,
        "warnings": warnings,
        "compression": {"raw_route_count":route_count, "canonical_claim_count":len(bundle.get("certificates", [])), "route_to_claim_compression":f"{route_count}:{len(bundle.get('certificates', []))}"},
        "certificate_reports": cert_reports,
    }

def main(argv=None):
    p=argparse.ArgumentParser()
    p.add_argument("--bundle", required=True)
    p.add_argument("--out", required=True)
    a=p.parse_args(argv)
    bundle=json.loads(Path(a.bundle).read_text(encoding="utf-8"))
    rep=replay_bundle(bundle)
    Path(a.out).parent.mkdir(parents=True, exist_ok=True)
    Path(a.out).write_text(json.dumps(rep, indent=2, ensure_ascii=False)+"\n", encoding="utf-8")
    print(json.dumps({"review_pass":rep["review_pass"], "counts":rep["counts"], "gates":rep["gates"], "issue_count":rep["issue_count"]}, indent=2, ensure_ascii=False))
    return 0 if rep["review_pass"] else 1
if __name__ == "__main__":
    raise SystemExit(main())
