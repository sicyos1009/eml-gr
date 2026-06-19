#!/usr/bin/env python3
from __future__ import annotations
import argparse, ast, copy, hashlib, importlib.util, json
from pathlib import Path
from typing import Any, Dict, List, Set

_BASE = Path(__file__).with_name('zero_replay_checker_v0_7_ast_locators.py')
_SPEC = importlib.util.spec_from_file_location('zf_v07', _BASE)
zf_v07 = importlib.util.module_from_spec(_SPEC)
assert _SPEC and _SPEC.loader
_SPEC.loader.exec_module(zf_v07)

TENSOR_CLASSES = {'tensor_definition', 'tensor_identity'}
PROFILE = 'zf_typed_ast_provenance_v1'
VALID_NODE_TYPES = {
    'metric_scalar_function', 'metric_component_scalar', 'inverse_metric_component_scalar',
    'connection_scalar_export', 'einstein_tensor_scalar_export', 'calculus_scalar_export',
    'assembled_tensor_scalar_expression', 'multiplicity_constant', 'normal_form_literal'
}
VALID_PROVENANCE_CLASSES = {
    'metric_definition', 'connection_component', 'einstein_tensor_component',
    'partial_derivative_component', 'covariant_divergence_assembly', 'index_multiplicity', 'zero_target'
}
BUILTIN_SYMBOLS = {'diff', 'exp', 'sqrt', 'log'}

def canonical_json(obj: Any) -> str:
    return json.dumps(obj, sort_keys=True, separators=(',', ':'), ensure_ascii=False)

def hash16(obj: Any) -> str:
    return hashlib.sha256(canonical_json(obj).encode('utf-8')).hexdigest()[:16]

def add_issue(issues: List[Dict[str, Any]], gate: str, code: str, **kw):
    x = {'severity': 'error', 'gate': gate, 'code': code}
    x.update(kw)
    issues.append(x)

def compute_type_hash(tp: Dict[str, Any]) -> str:
    body = copy.deepcopy(tp)
    body.pop('type_hash', None)
    return hash16(body)

def free_names(expr: str) -> Set[str]:
    names: Set[str] = set()
    tree = ast.parse(str(expr), mode='eval')
    for n in ast.walk(tree):
        if isinstance(n, ast.Name):
            names.add(n.id)
    return names - BUILTIN_SYMBOLS

def validate_typed_provenance(bundle: Dict[str, Any]) -> Dict[str, Any]:
    issues: List[Dict[str, Any]] = []
    warnings: List[Dict[str, Any]] = []
    total = ok_count = tensor_steps = tensor_steps_with_typed = 0
    rows: List[Dict[str, Any]] = []
    seen_type_hashes: Set[str] = set()
    for cert in bundle.get('certificates', []):
        leaves = {x.get('subleaf_id'): x for x in cert.get('tensor_subleaves', []) or []}
        if not leaves:
            continue
        claim = cert.get('claim_id')
        entailed = zf_v07.zf_v05.domain_entailments(cert)
        for route in cert.get('routes', []):
            rid = route.get('route_id')
            for step in route.get('steps', []):
                if step.get('rule_class') not in TENSOR_CLASSES:
                    continue
                tensor_steps += 1
                sid_step = step.get('step_id')
                maps = step.get('occurrence_maps', []) or []
                if any(isinstance(om.get('typed_provenance'), dict) for om in maps):
                    tensor_steps_with_typed += 1
                else:
                    add_issue(issues, 'TP1', 'TENSOR_STEP_MISSING_TYPED_PROVENANCE', claim_id=claim, route_id=rid, step_id=sid_step)
                for om in maps:
                    before = len(issues)
                    total += 1
                    oid = om.get('occurrence_id')
                    al = om.get('ast_locator', {}) or {}
                    binding = al.get('payload_binding', {}) or {}
                    tp = om.get('typed_provenance')
                    if not isinstance(tp, dict):
                        add_issue(issues, 'TP1', 'MISSING_TYPED_PROVENANCE_OBJECT', claim_id=claim, route_id=rid, step_id=sid_step, occurrence_id=oid)
                        continue
                    if tp.get('profile') != PROFILE:
                        add_issue(issues, 'TP1', 'TYPED_PROVENANCE_PROFILE_MISMATCH', claim_id=claim, route_id=rid, step_id=sid_step, occurrence_id=oid, profile=tp.get('profile'))
                    sid = binding.get('subleaf_id', om.get('subleaf_id'))
                    field = binding.get('payload_field', om.get('payload_field'))
                    if tp.get('payload_binding') != {'subleaf_id': sid, 'payload_field': field}:
                        add_issue(issues, 'TP2', 'PAYLOAD_BINDING_MISMATCH', claim_id=claim, route_id=rid, step_id=sid_step, occurrence_id=oid, expected={'subleaf_id': sid, 'payload_field': field}, observed=tp.get('payload_binding'))
                    leaf = leaves.get(sid)
                    if not leaf:
                        add_issue(issues, 'TP2', 'TYPED_SOURCE_SUBLEAF_NOT_FOUND', claim_id=claim, route_id=rid, step_id=sid_step, occurrence_id=oid, subleaf_id=sid)
                        continue
                    source = tp.get('source', {}) or {}
                    if source.get('subleaf_id') != sid or source.get('payload_field') != field:
                        add_issue(issues, 'TP3', 'SOURCE_BINDING_MISMATCH', claim_id=claim, route_id=rid, step_id=sid_step, occurrence_id=oid, source=source)
                    if source.get('rule_id') != leaf.get('rule_id') or source.get('rule_class') != leaf.get('rule_class'):
                        add_issue(issues, 'TP3', 'SOURCE_RULE_BINDING_MISMATCH', claim_id=claim, route_id=rid, step_id=sid_step, occurrence_id=oid, source_rule_id=source.get('rule_id'), leaf_rule_id=leaf.get('rule_id'), source_rule_class=source.get('rule_class'), leaf_rule_class=leaf.get('rule_class'))
                    if source.get('subleaf_hash') != leaf.get('subleaf_hash'):
                        add_issue(issues, 'TP3', 'SOURCE_SUBLEAF_HASH_MISMATCH', claim_id=claim, route_id=rid, step_id=sid_step, occurrence_id=oid, source_hash=source.get('subleaf_hash'), leaf_hash=leaf.get('subleaf_hash'))
                    node_type = tp.get('node_type')
                    prov_class = tp.get('provenance_class')
                    if node_type not in VALID_NODE_TYPES:
                        add_issue(issues, 'TP4', 'INVALID_NODE_TYPE', claim_id=claim, route_id=rid, step_id=sid_step, occurrence_id=oid, node_type=node_type)
                    if prov_class not in VALID_PROVENANCE_CLASSES:
                        add_issue(issues, 'TP4', 'INVALID_PROVENANCE_CLASS', claim_id=claim, route_id=rid, step_id=sid_step, occurrence_id=oid, provenance_class=prov_class)
                    if not tp.get('semantic_role'):
                        add_issue(issues, 'TP4', 'MISSING_SEMANTIC_ROLE', claim_id=claim, route_id=rid, step_id=sid_step, occurrence_id=oid)
                    rec_hash = compute_type_hash(tp)
                    if rec_hash != tp.get('type_hash'):
                        add_issue(issues, 'TP5', 'TYPED_PROVENANCE_HASH_MISMATCH', claim_id=claim, route_id=rid, step_id=sid_step, occurrence_id=oid, reported=tp.get('type_hash'), recomputed=rec_hash)
                    if tp.get('type_hash') in seen_type_hashes:
                        # Repeated full divergence is allowed across route A/B only if the route/step target differs, so the type hash should differ.
                        add_issue(issues, 'TP5', 'DUPLICATE_TYPED_PROVENANCE_HASH', claim_id=claim, route_id=rid, step_id=sid_step, occurrence_id=oid, type_hash=tp.get('type_hash'))
                    seen_type_hashes.add(tp.get('type_hash'))
                    target = tp.get('target', {}) or {}
                    expected_target = {
                        'route_id': rid,
                        'step_id': sid_step,
                        'target_field': al.get('target_field'),
                        'ast_path': al.get('path'),
                        'ast_node_hash': al.get('ast_node_hash'),
                    }
                    if target != expected_target:
                        add_issue(issues, 'TP6', 'TARGET_BINDING_MISMATCH', claim_id=claim, route_id=rid, step_id=sid_step, occurrence_id=oid, expected=expected_target, observed=target)
                    edge = tp.get('provenance_edge', {}) or {}
                    expected_source_uri = f'subleaf:{sid}#payload:{field}'
                    expected_target_uri = f'route:{rid}/step:{sid_step}/{al.get("target_field")}@{al.get("path")}'
                    if edge.get('edge_kind') != 'binds_typed_tensor_scalar_export' or edge.get('source_uri') != expected_source_uri or edge.get('target_uri') != expected_target_uri:
                        add_issue(issues, 'TP6', 'PROVENANCE_EDGE_BINDING_MISMATCH', claim_id=claim, route_id=rid, step_id=sid_step, occurrence_id=oid, expected_source_uri=expected_source_uri, expected_target_uri=expected_target_uri, observed=edge)
                    if edge.get('edge_type') != node_type:
                        add_issue(issues, 'TP6', 'PROVENANCE_EDGE_TYPE_MISMATCH', claim_id=claim, route_id=rid, step_id=sid_step, occurrence_id=oid, edge_type=edge.get('edge_type'), node_type=node_type)
                    # Type table coverage and agreement with declared occurrence type.
                    field_types = leaf.get('payload_field_types', {}) or {}
                    field_decl = field_types.get(field)
                    if not isinstance(field_decl, dict):
                        add_issue(issues, 'TP9', 'PAYLOAD_FIELD_TYPE_MISSING', claim_id=claim, route_id=rid, step_id=sid_step, occurrence_id=oid, subleaf_id=sid, payload_field=field)
                    else:
                        for key in ['node_type', 'provenance_class', 'semantic_role', 'scalar_codomain']:
                            if field_decl.get(key) != tp.get(key):
                                add_issue(issues, 'TP9', 'PAYLOAD_FIELD_TYPE_DECLARATION_MISMATCH', claim_id=claim, route_id=rid, step_id=sid_step, occurrence_id=oid, key=key, field_decl=field_decl.get(key), typed_provenance=tp.get(key))
                    # Scope coverage: every free symbol must be listed as coordinate or parameter.
                    expr = al.get('expected_expr') or om.get('expr')
                    try:
                        names = free_names(str(expr))
                    except Exception as e:
                        add_issue(issues, 'TP7', 'TYPE_SCOPE_EXPR_PARSE_FAILED', claim_id=claim, route_id=rid, step_id=sid_step, occurrence_id=oid, error=str(e))
                        names = set()
                    declared = set(tp.get('coordinate_scope', []) or []) | set(tp.get('parameter_scope', []) or [])
                    missing = sorted(names - declared)
                    if missing:
                        add_issue(issues, 'TP7', 'FREE_SYMBOL_SCOPE_NOT_DECLARED', claim_id=claim, route_id=rid, step_id=sid_step, occurrence_id=oid, free_symbols=sorted(names), coordinate_scope=tp.get('coordinate_scope'), parameter_scope=tp.get('parameter_scope'), missing=missing)
                    # Domain refs must either be normalized side-condition refs or directly entailed seed conditions.
                    for dref in tp.get('domain_refs', []) or []:
                        if dref not in cert.get('domain', {}).get('side_condition_refs', []) and not zf_v07.zf_v05.side_entailed(dref, entailed):
                            add_issue(issues, 'TP8', 'TYPED_PROVENANCE_DOMAIN_REF_NOT_ENTAILED', claim_id=claim, route_id=rid, step_id=sid_step, occurrence_id=oid, domain_ref=dref, entailed=sorted(entailed))
                    rows.append({
                        'claim_id': claim,
                        'route_id': rid,
                        'step_id': sid_step,
                        'occurrence_id': oid,
                        'subleaf_id': sid,
                        'payload_field': field,
                        'node_type': node_type,
                        'provenance_class': prov_class,
                        'coordinate_scope': tp.get('coordinate_scope'),
                        'parameter_scope': tp.get('parameter_scope'),
                        'domain_refs': tp.get('domain_refs'),
                        'type_hash': tp.get('type_hash'),
                    })
                    ok_count += int(len(issues) == before)
    gates = {f'TP{i}': True for i in range(1, 10)}
    for issue in issues:
        gates[issue['gate']] = False
    return {
        'typed_provenance_total': total,
        'typed_provenance_checked_ok': ok_count,
        'tensor_steps': tensor_steps,
        'tensor_steps_with_typed_provenance': tensor_steps_with_typed,
        'gates': gates,
        'issue_count': len(issues),
        'warning_count': len(warnings),
        'issues': issues,
        'warnings': warnings,
        'rows': rows,
    }

def replay_bundle(bundle: Dict[str, Any]) -> Dict[str, Any]:
    base = zf_v07.replay_bundle(bundle)
    tp_report = validate_typed_provenance(bundle)
    base['title'] = 'Paper2 Zero Forests strict Level-B+ replay report v0.8 typed AST provenance'
    base['strict_level'] = 'Level-B+ named tensor subleaves plus AST-path locators plus typed provenance'
    base['typed_provenance_report'] = tp_report
    base['counts']['typed_provenance'] = tp_report['typed_provenance_total']
    base['counts']['typed_provenance_checked_ok'] = tp_report['typed_provenance_checked_ok']
    base['counts']['tensor_steps_with_typed_provenance'] = tp_report['tensor_steps_with_typed_provenance']
    base['gates'].update(tp_report['gates'])
    base['issues'].extend(tp_report['issues'])
    base['warnings'].extend(tp_report['warnings'])
    base['issue_count'] = len(base['issues'])
    base['warning_count'] = len(base['warnings'])
    base['review_pass'] = base['issue_count'] == 0
    return base

def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('--bundle', required=True)
    ap.add_argument('--out', required=True)
    args = ap.parse_args(argv)
    bundle = json.loads(Path(args.bundle).read_text(encoding='utf-8'))
    rep = replay_bundle(bundle)
    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    Path(args.out).write_text(json.dumps(rep, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
    print(json.dumps({
        'review_pass': rep['review_pass'],
        'counts': rep['counts'],
        'typed_provenance_gates': rep['typed_provenance_report']['gates'],
        'issue_count': rep['issue_count'],
        'warning_count': rep['warning_count'],
    }, indent=2, ensure_ascii=False))
    return 0 if rep['review_pass'] else 1

if __name__ == '__main__':
    raise SystemExit(main())
