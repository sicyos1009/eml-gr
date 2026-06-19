#!/usr/bin/env python3
from __future__ import annotations
import argparse, ast, copy, hashlib, importlib.util, json, re
from pathlib import Path
from typing import Any, Dict, List, Set

_BASE = Path(__file__).with_name('zero_replay_checker_v0_5_strict.py')
_SPEC = importlib.util.spec_from_file_location('zf_v05', _BASE)
zf_v05 = importlib.util.module_from_spec(_SPEC)
assert _SPEC and _SPEC.loader
_SPEC.loader.exec_module(zf_v05)
TENSOR_CLASSES = {'tensor_definition', 'tensor_identity'}
AST_PROFILE = 'zf_expr_ast_v1.python_infix_nary_add_mul'

def canonical_json(obj: Any) -> str:
    return json.dumps(obj, sort_keys=True, separators=(',', ':'), ensure_ascii=False)

def hash16(obj: Any) -> str:
    return hashlib.sha256(canonical_json(obj).encode('utf-8')).hexdigest()[:16]

def add_issue(issues: List[Dict[str, Any]], gate: str, code: str, **kw):
    x = {'severity': 'error', 'gate': gate, 'code': code}
    x.update(kw)
    issues.append(x)

def add_warning(warnings: List[Dict[str, Any]], gate: str, code: str, **kw):
    x = {'severity': 'warning', 'gate': gate, 'code': code}
    x.update(kw)
    warnings.append(x)

def convert_py_ast(node: ast.AST) -> Dict[str, Any]:
    meta = {}
    if hasattr(node, 'col_offset'):
        meta = {'span': [getattr(node, 'col_offset'), getattr(node, 'end_col_offset', None)]}
    if isinstance(node, ast.Expression):
        return convert_py_ast(node.body)
    if isinstance(node, ast.BinOp):
        if isinstance(node.op, ast.Add):
            terms = []
            for child in (convert_py_ast(node.left), convert_py_ast(node.right)):
                if child.get('kind') == 'Add':
                    terms.extend(child['terms'])
                else:
                    terms.append(child)
            return {'kind': 'Add', 'terms': terms, **meta}
        if isinstance(node.op, ast.Sub):
            left = convert_py_ast(node.left)
            right = {'kind': 'Neg', 'operand': convert_py_ast(node.right), **meta}
            terms = left['terms'][:] if left.get('kind') == 'Add' else [left]
            terms.append(right)
            return {'kind': 'Add', 'terms': terms, **meta}
        if isinstance(node.op, ast.Mult):
            factors = []
            for child in (convert_py_ast(node.left), convert_py_ast(node.right)):
                if child.get('kind') == 'Mul':
                    factors.extend(child['factors'])
                else:
                    factors.append(child)
            return {'kind': 'Mul', 'factors': factors, **meta}
        if isinstance(node.op, ast.Div):
            left = convert_py_ast(node.left)
            right = {'kind': 'Pow', 'base': convert_py_ast(node.right), 'exponent': {'kind': 'Const', 'value': -1}, **meta}
            factors = left['factors'][:] if left.get('kind') == 'Mul' else [left]
            factors.append(right)
            return {'kind': 'Mul', 'factors': factors, **meta}
        if isinstance(node.op, ast.Pow):
            return {'kind': 'Pow', 'base': convert_py_ast(node.left), 'exponent': convert_py_ast(node.right), **meta}
    if isinstance(node, ast.UnaryOp):
        if isinstance(node.op, ast.USub):
            return {'kind': 'Neg', 'operand': convert_py_ast(node.operand), **meta}
        if isinstance(node.op, ast.UAdd):
            return convert_py_ast(node.operand)
    if isinstance(node, ast.Call):
        return {'kind': 'Call', 'func': convert_py_ast(node.func), 'args': [convert_py_ast(a) for a in node.args], **meta}
    if isinstance(node, ast.Name):
        return {'kind': 'Name', 'id': node.id, **meta}
    if isinstance(node, ast.Constant):
        return {'kind': 'Const', 'value': node.value, **meta}
    raise ValueError(f'unsupported node {type(node).__name__}')

def parse_expr_ast(expr: str) -> Dict[str, Any]:
    return convert_py_ast(ast.parse(expr, mode='eval'))

def canonical_ast(node: Dict[str, Any]) -> Dict[str, Any]:
    k = node.get('kind')
    if k == 'Add': return {'kind': 'Add', 'terms': [canonical_ast(x) for x in node.get('terms', [])]}
    if k == 'Mul': return {'kind': 'Mul', 'factors': [canonical_ast(x) for x in node.get('factors', [])]}
    if k == 'Pow': return {'kind': 'Pow', 'base': canonical_ast(node['base']), 'exponent': canonical_ast(node['exponent'])}
    if k == 'Neg': return {'kind': 'Neg', 'operand': canonical_ast(node['operand'])}
    if k == 'Call': return {'kind': 'Call', 'func': canonical_ast(node['func']), 'args': [canonical_ast(x) for x in node.get('args', [])]}
    if k == 'Name': return {'kind': 'Name', 'id': node.get('id')}
    if k == 'Const': return {'kind': 'Const', 'value': node.get('value')}
    raise ValueError(f'bad kind {k}')

def resolve_path(root: Dict[str, Any], path: str) -> Dict[str, Any]:
    if path == '$':
        return root
    if not path.startswith('$.'):
        raise ValueError('path must start with $.')
    cur = root
    pos = 1
    pattern = re.compile(r'\.(terms|factors)\[(\d+)(?::(\d+))?\]')
    while pos < len(path):
        m = pattern.match(path, pos)
        if not m:
            raise ValueError(f'cannot parse path at {path[pos:]}')
        field, a_s, b_s = m.group(1), m.group(2), m.group(3)
        a = int(a_s); b = int(b_s) if b_s is not None else None
        if field == 'terms':
            if cur.get('kind') != 'Add':
                raise ValueError(f'terms selector on non-Add node {cur.get("kind")}')
            seq = cur.get('terms', [])
            if b is None:
                if a >= len(seq):
                    raise ValueError('term index out of range')
                cur = seq[a]
            else:
                if a < 0 or b > len(seq) or a >= b:
                    raise ValueError('term slice out of range')
                sl = seq[a:b]
                cur = sl[0] if len(sl) == 1 else {'kind': 'Add', 'terms': sl}
        elif field == 'factors':
            if cur.get('kind') != 'Mul':
                raise ValueError(f'factors selector on non-Mul node {cur.get("kind")}')
            seq = cur.get('factors', [])
            if b is None:
                if a >= len(seq):
                    raise ValueError('factor index out of range')
                cur = seq[a]
            else:
                if a < 0 or b > len(seq) or a >= b:
                    raise ValueError('factor slice out of range')
                sl = seq[a:b]
                cur = sl[0] if len(sl) == 1 else {'kind': 'Mul', 'factors': sl}
        pos = m.end()
    return cur

def compute_ast_locator_hash(ast_locator: Dict[str, Any], selected_node: Dict[str, Any]) -> str:
    body = copy.deepcopy(ast_locator)
    body.pop('ast_node_hash', None)
    body['resolved_canonical_ast'] = canonical_ast(selected_node)
    return hash16(body)

def validate_ast_locators(bundle: Dict[str, Any]) -> Dict[str, Any]:
    issues: List[Dict[str, Any]] = []
    warnings: List[Dict[str, Any]] = []
    total = ok_count = tensor_steps = tensor_steps_with_ast = 0
    seen_ids: Set[str] = set()
    step_reports = []
    for cert in bundle.get('certificates', []):
        leaves = {x.get('subleaf_id'): x for x in cert.get('tensor_subleaves', []) or []}
        if not leaves:
            continue
        claim = cert.get('claim_id')
        for route in cert.get('routes', []):
            rid = route.get('route_id')
            for step in route.get('steps', []):
                if step.get('rule_class') not in TENSOR_CLASSES:
                    continue
                tensor_steps += 1
                sid = step.get('step_id')
                maps = step.get('occurrence_maps', []) or []
                refs = set(step.get('subleaf_refs', []) or [])
                if maps:
                    tensor_steps_with_ast += 1
                else:
                    add_issue(issues, 'AP1', 'TENSOR_STEP_MISSING_AST_LOCATORS', claim_id=claim, route_id=rid, step_id=sid)
                mapped: Set[str] = set()
                for om in maps:
                    before = len(issues)
                    total += 1
                    oid = om.get('occurrence_id')
                    if oid in seen_ids:
                        add_issue(issues, 'AP6', 'DUPLICATE_OCCURRENCE_ID', claim_id=claim, route_id=rid, step_id=sid, occurrence_id=oid)
                    seen_ids.add(oid)
                    if om.get('route_id') != rid or om.get('step_id') != sid:
                        add_issue(issues, 'AP6', 'OCCURRENCE_ROUTE_STEP_BINDING_MISMATCH', claim_id=claim, route_id=rid, step_id=sid, occurrence_id=oid)
                    if om.get('locator_kind') != 'ast_path_v1':
                        add_issue(issues, 'AP1', 'LOCATOR_KIND_NOT_AST_PATH_V1', claim_id=claim, route_id=rid, step_id=sid, occurrence_id=oid, locator_kind=om.get('locator_kind'))
                    ast_locator = om.get('ast_locator')
                    if not isinstance(ast_locator, dict):
                        add_issue(issues, 'AP1', 'MISSING_AST_LOCATOR_OBJECT', claim_id=claim, route_id=rid, step_id=sid, occurrence_id=oid)
                        continue
                    if ast_locator.get('ast_profile') != AST_PROFILE:
                        add_issue(issues, 'AP1', 'AST_PROFILE_MISMATCH', claim_id=claim, route_id=rid, step_id=sid, occurrence_id=oid, ast_profile=ast_locator.get('ast_profile'))
                    target_field = ast_locator.get('target_field')
                    if target_field not in {'before_expr', 'after_expr'}:
                        add_issue(issues, 'AP2', 'BAD_AST_TARGET_FIELD', claim_id=claim, route_id=rid, step_id=sid, occurrence_id=oid, target_field=target_field)
                        continue
                    try:
                        root = parse_expr_ast(str(step[target_field]))
                    except Exception as e:
                        add_issue(issues, 'AP2', 'AST_PARSE_FAILED', claim_id=claim, route_id=rid, step_id=sid, occurrence_id=oid, target_field=target_field, error=str(e))
                        continue
                    try:
                        selected = resolve_path(root, str(ast_locator.get('path')))
                    except Exception as e:
                        add_issue(issues, 'AP3', 'AST_PATH_RESOLUTION_FAILED', claim_id=claim, route_id=rid, step_id=sid, occurrence_id=oid, path=ast_locator.get('path'), error=str(e))
                        continue
                    binding = ast_locator.get('payload_binding', {}) or {}
                    subleaf_id = binding.get('subleaf_id', om.get('subleaf_id'))
                    payload_field = binding.get('payload_field', om.get('payload_field'))
                    mapped.add(subleaf_id)
                    payload = leaves.get(subleaf_id, {}).get('payload', {})
                    if subleaf_id not in leaves or payload_field not in payload:
                        add_issue(issues, 'AP4', 'AST_PAYLOAD_REFERENCE_INVALID', claim_id=claim, route_id=rid, step_id=sid, occurrence_id=oid, subleaf_id=subleaf_id, payload_field=payload_field)
                    else:
                        try:
                            payload_ast = canonical_ast(parse_expr_ast(str(payload[payload_field])))
                            selected_ast = canonical_ast(selected)
                            if selected_ast != payload_ast:
                                add_issue(issues, 'AP4', 'AST_SELECTED_NODE_PAYLOAD_MISMATCH', claim_id=claim, route_id=rid, step_id=sid, occurrence_id=oid, path=ast_locator.get('path'), selected_ast=selected_ast, payload_ast=payload_ast)
                        except Exception as e:
                            add_issue(issues, 'AP4', 'AST_PAYLOAD_PARSE_FAILED', claim_id=claim, route_id=rid, step_id=sid, occurrence_id=oid, error=str(e))
                    if 'expected_expr' not in ast_locator:
                        add_issue(issues, 'AP4', 'AST_EXPECTED_EXPR_MISSING', claim_id=claim, route_id=rid, step_id=sid, occurrence_id=oid)
                    else:
                        try:
                            exp_ast = canonical_ast(parse_expr_ast(str(ast_locator.get('expected_expr'))))
                            if exp_ast != canonical_ast(selected):
                                add_issue(issues, 'AP4', 'AST_EXPECTED_EXPR_MISMATCH', claim_id=claim, route_id=rid, step_id=sid, occurrence_id=oid, expected_ast=exp_ast, selected_ast=canonical_ast(selected))
                        except Exception as e:
                            add_issue(issues, 'AP4', 'AST_EXPECTED_EXPR_PARSE_FAILED', claim_id=claim, route_id=rid, step_id=sid, occurrence_id=oid, error=str(e))
                    rec_hash = compute_ast_locator_hash(ast_locator, selected)
                    if rec_hash != ast_locator.get('ast_node_hash'):
                        add_issue(issues, 'AP5', 'AST_NODE_HASH_MISMATCH', claim_id=claim, route_id=rid, step_id=sid, occurrence_id=oid, reported=ast_locator.get('ast_node_hash'), recomputed=rec_hash)
                    # Legacy span fields are diagnostic-only in v0.7. Warn, do not fail.
                    legacy_kind = om.get('legacy_locator_kind')
                    if legacy_kind == 'literal_span_v1':
                        span_start, span_end = om.get('span_start'), om.get('span_end')
                        expr = str(om.get('expr', ''))
                        target = str(step.get(target_field, ''))
                        if not isinstance(span_start, int) or not isinstance(span_end, int) or span_start < 0 or span_end > len(target) or target[span_start:span_end] != expr:
                            add_warning(warnings, 'AP7', 'LEGACY_LITERAL_SPAN_STALE_DIAGNOSTIC_ONLY', claim_id=claim, route_id=rid, step_id=sid, occurrence_id=oid)
                    ok_count += int(len(issues) == before)
                missing = sorted(refs - mapped)
                if missing:
                    add_issue(issues, 'AP6', 'TENSOR_SUBLEAF_REF_NOT_MAPPED_BY_AST_LOCATOR', claim_id=claim, route_id=rid, step_id=sid, missing_subleaf_refs=missing)
                step_reports.append({'claim_id': claim, 'route_id': rid, 'step_id': sid, 'subleaf_refs': sorted(refs), 'ast_locator_count': len(maps)})
    gates = {f'AP{i}': True for i in range(1, 8)}
    for issue in issues:
        gates[issue['gate']] = False
    return {
        'ast_locators_total': total,
        'ast_locators_checked_ok': ok_count,
        'tensor_steps': tensor_steps,
        'tensor_steps_with_ast_locators': tensor_steps_with_ast,
        'gates': gates,
        'issue_count': len(issues),
        'warning_count': len(warnings),
        'issues': issues,
        'warnings': warnings,
        'step_reports': step_reports,
    }

def replay_bundle(bundle: Dict[str, Any]) -> Dict[str, Any]:
    base = zf_v05.replay_bundle(bundle)
    ast_report = validate_ast_locators(bundle)
    base['title'] = 'Paper2 Zero Forests strict Level-B+ replay report v0.7 AST-path locators'
    base['strict_level'] = 'Level-B+ named tensor subleaves plus AST-path occurrence locators'
    base['ast_locator_report'] = ast_report
    base['counts']['ast_locators'] = ast_report['ast_locators_total']
    base['counts']['ast_locators_checked_ok'] = ast_report['ast_locators_checked_ok']
    base['counts']['tensor_steps_with_ast_locators'] = ast_report['tensor_steps_with_ast_locators']
    base['gates'].update(ast_report['gates'])
    base['issues'].extend(ast_report['issues'])
    base['warnings'].extend(ast_report['warnings'])
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
        'ast_gates': rep['ast_locator_report']['gates'],
        'issue_count': rep['issue_count'],
        'warning_count': rep['warning_count'],
    }, indent=2, ensure_ascii=False))
    return 0 if rep['review_pass'] else 1

if __name__ == '__main__':
    raise SystemExit(main())
