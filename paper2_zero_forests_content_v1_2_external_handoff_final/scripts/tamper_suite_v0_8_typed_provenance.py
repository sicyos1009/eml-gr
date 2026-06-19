#!/usr/bin/env python3
from __future__ import annotations
import argparse, copy, importlib.util, json
from pathlib import Path
from typing import Any, Dict

_CHECKER_NAME = 'zero_replay_checker_v0_8_typed_provenance.py'
_SPEC = importlib.util.spec_from_file_location('zf_v08', Path(__file__).with_name(_CHECKER_NAME))
zf = importlib.util.module_from_spec(_SPEC)
assert _SPEC and _SPEC.loader
_SPEC.loader.exec_module(zf)

OLD_EXPR = 'diff(3*H**2, t) + 3*H*3*H**2 + 3*(H*exp(2*H*t))*(-3*H**2*exp(-2*H*t))'
REFORMATTED_EXPR = 'diff(3*H**2,t)+3*H*3*H**2+3*( H*exp(2*H*t) )*(-3*H**2*exp(-2*H*t))'

def write_json(path: Path, obj: Any):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')

def get_flrw(bundle: Dict[str, Any]) -> Dict[str, Any]:
    for cert in bundle['certificates']:
        if cert.get('claim_id') == 'zero.flrw.contracted_bianchi_divG0':
            return cert
    raise KeyError('FLRW certificate not found')

def leaves(bundle: Dict[str, Any]):
    return {x['subleaf_id']: x for x in get_flrw(bundle).get('tensor_subleaves', [])}

def recompute_subleaf_hashes(bundle: Dict[str, Any]):
    for cert in bundle.get('certificates', []):
        for leaf in cert.get('tensor_subleaves', []) or []:
            leaf['subleaf_hash'] = zf.zf_v07.zf_v05.recompute_subleaf_hash(leaf)

def recompute_ast_hashes(bundle: Dict[str, Any], best_effort=True):
    for cert in bundle.get('certificates', []):
        for route in cert.get('routes', []):
            for step in route.get('steps', []):
                for om in step.get('occurrence_maps', []) or []:
                    al = om.get('ast_locator')
                    if not isinstance(al, dict):
                        continue
                    try:
                        root = zf.zf_v07.parse_expr_ast(str(step[al['target_field']]))
                        selected = zf.zf_v07.resolve_path(root, str(al['path']))
                        al['ast_node_hash'] = zf.zf_v07.compute_ast_locator_hash(al, selected)
                    except Exception:
                        if not best_effort:
                            raise

def sync_sources(bundle: Dict[str, Any]):
    lm = leaves(bundle)
    for cert in bundle.get('certificates', []):
        for route in cert.get('routes', []):
            for step in route.get('steps', []):
                for om in step.get('occurrence_maps', []) or []:
                    tp = om.get('typed_provenance')
                    al = om.get('ast_locator', {}) or {}
                    if not isinstance(tp, dict):
                        continue
                    b = al.get('payload_binding', {}) or {}
                    sid = b.get('subleaf_id', om.get('subleaf_id'))
                    field = b.get('payload_field', om.get('payload_field'))
                    leaf = lm.get(sid)
                    if leaf:
                        tp['source']['subleaf_hash'] = leaf.get('subleaf_hash')
                        tp['source']['rule_id'] = leaf.get('rule_id')
                        tp['source']['rule_class'] = leaf.get('rule_class')
                    tp['target'] = {
                        'route_id': route.get('route_id'),
                        'step_id': step.get('step_id'),
                        'target_field': al.get('target_field'),
                        'ast_path': al.get('path'),
                        'ast_node_hash': al.get('ast_node_hash'),
                    }
                    tp['payload_binding'] = {'subleaf_id': sid, 'payload_field': field}
                    tp['provenance_edge']['source_uri'] = f'subleaf:{sid}#payload:{field}'
                    tp['provenance_edge']['target_uri'] = f'route:{route.get("route_id")}/step:{step.get("step_id")}/{al.get("target_field")}@{al.get("path")}'

def recompute_type_hashes(bundle: Dict[str, Any]):
    for cert in bundle.get('certificates', []):
        for route in cert.get('routes', []):
            for step in route.get('steps', []):
                for om in step.get('occurrence_maps', []) or []:
                    tp = om.get('typed_provenance')
                    if isinstance(tp, dict):
                        tp['type_hash'] = zf.compute_type_hash(tp)

def recompute_route_hashes(bundle: Dict[str, Any]):
    for cert in bundle.get('certificates', []):
        for route in cert.get('routes', []):
            route['raw_trace_hash'] = zf.zf_v07.zf_v05.recompute_raw_route_hash(route)

def recompute_all(bundle: Dict[str, Any], ast_best_effort=True):
    recompute_subleaf_hashes(bundle)
    recompute_ast_hashes(bundle, best_effort=ast_best_effort)
    sync_sources(bundle)
    recompute_type_hashes(bundle)
    recompute_route_hashes(bundle)

def first_occ(bundle: Dict[str, Any], needle: str) -> Dict[str, Any]:
    for route in get_flrw(bundle)['routes']:
        for step in route['steps']:
            for om in step.get('occurrence_maps', []) or []:
                if needle in om.get('occurrence_id', ''):
                    return om
    raise KeyError(needle)

def first_tensor_step(bundle: Dict[str, Any], step_id='A2') -> Dict[str, Any]:
    for route in get_flrw(bundle)['routes']:
        for step in route['steps']:
            if step.get('step_id') == step_id:
                return step
    raise KeyError(step_id)

def mutate_whitespace_reformat(bundle):
    for route in get_flrw(bundle)['routes']:
        for step in route['steps']:
            for fld in ('before_expr', 'after_expr'):
                if step.get(fld) == OLD_EXPR:
                    step[fld] = REFORMATTED_EXPR
    recompute_all(bundle)

def mutate_literal_span_shift(bundle):
    om = first_occ(bundle, 'partial_time_derivative')
    om['span_start'] = 777
    om['span_end'] = 888
    recompute_route_hashes(bundle)

def mutate_missing_typed_provenance(bundle):
    om = first_occ(bundle, 'partial_time_derivative')
    om.pop('typed_provenance', None)
    recompute_route_hashes(bundle)

def mutate_type_hash_literal(bundle):
    om = first_occ(bundle, 'partial_time_derivative')
    om['typed_provenance']['type_hash'] = '0000000000000000'
    recompute_route_hashes(bundle)

def mutate_profile_mismatch(bundle):
    om = first_occ(bundle, 'partial_time_derivative')
    om['typed_provenance']['profile'] = 'wrong_profile'
    recompute_type_hashes(bundle); recompute_route_hashes(bundle)

def mutate_payload_binding_drift(bundle):
    om = first_occ(bundle, 'connection_trace_factor')
    om['typed_provenance']['payload_binding']['payload_field'] = 'gamma_0ii_expr'
    recompute_type_hashes(bundle); recompute_route_hashes(bundle)

def mutate_source_hash_stale(bundle):
    om = first_occ(bundle, 'spatial_connection_factor')
    om['typed_provenance']['source']['subleaf_hash'] = 'badbadbadbadbadb'
    recompute_type_hashes(bundle); recompute_route_hashes(bundle)

def mutate_source_rule_mismatch(bundle):
    om = first_occ(bundle, 'einstein_00_factor')
    om['typed_provenance']['source']['rule_id'] = 'TDEF.WRONG_RULE'
    recompute_type_hashes(bundle); recompute_route_hashes(bundle)

def mutate_node_type_invalid(bundle):
    om = first_occ(bundle, 'spatial_einstein_factor')
    om['typed_provenance']['node_type'] = 'untyped_blob'
    om['typed_provenance']['provenance_edge']['edge_type'] = 'untyped_blob'
    recompute_type_hashes(bundle); recompute_route_hashes(bundle)

def mutate_field_type_declaration_drift(bundle):
    lf = leaves(bundle)['flrw.connection.gamma_trace_0']
    lf['payload_field_types']['gamma_trace_0_expr']['node_type'] = 'metric_component_scalar'
    recompute_all(bundle)

def mutate_coordinate_scope_missing(bundle):
    om = first_occ(bundle, 'spatial_connection_factor')
    om['typed_provenance']['coordinate_scope'] = []
    recompute_type_hashes(bundle); recompute_route_hashes(bundle)

def mutate_parameter_scope_missing(bundle):
    om = first_occ(bundle, 'einstein_00_factor')
    om['typed_provenance']['parameter_scope'] = []
    recompute_type_hashes(bundle); recompute_route_hashes(bundle)

def mutate_edge_target_wrong(bundle):
    om = first_occ(bundle, 'spatial_connection_factor')
    om['typed_provenance']['provenance_edge']['target_uri'] = 'route:wrong/step:wrong/after_expr@$'
    recompute_type_hashes(bundle); recompute_route_hashes(bundle)

def mutate_edge_type_mismatch(bundle):
    om = first_occ(bundle, 'connection_trace_factor')
    om['typed_provenance']['provenance_edge']['edge_type'] = 'einstein_tensor_scalar_export'
    recompute_type_hashes(bundle); recompute_route_hashes(bundle)

def mutate_domain_ref_unentailed(bundle):
    om = first_occ(bundle, 'spatial_einstein_factor')
    om['typed_provenance']['domain_refs'] = ['DOM.NONZERO_DENOMINATOR']
    recompute_type_hashes(bundle); recompute_route_hashes(bundle)

def mutate_target_ast_hash_mismatch(bundle):
    om = first_occ(bundle, 'partial_time_derivative')
    om['typed_provenance']['target']['ast_node_hash'] = 'ffffffffffffffff'
    recompute_type_hashes(bundle); recompute_route_hashes(bundle)

CASES = [
    ('baseline_untampered', None, True, 'baseline'),
    ('benign_whitespace_reformatted_route_expr_rehashed', mutate_whitespace_reformat, True, 'benign_robustness'),
    ('benign_literal_span_shift_diagnostic_only_rehashed', mutate_literal_span_shift, True, 'benign_robustness'),
    ('missing_typed_provenance_object', mutate_missing_typed_provenance, False, 'malicious'),
    ('typed_provenance_hash_literal', mutate_type_hash_literal, False, 'malicious'),
    ('typed_provenance_profile_mismatch_rehashed', mutate_profile_mismatch, False, 'malicious'),
    ('typed_payload_binding_drift_rehashed', mutate_payload_binding_drift, False, 'malicious'),
    ('typed_source_hash_stale_rehashed', mutate_source_hash_stale, False, 'malicious'),
    ('typed_source_rule_mismatch_rehashed', mutate_source_rule_mismatch, False, 'malicious'),
    ('typed_node_type_invalid_rehashed', mutate_node_type_invalid, False, 'malicious'),
    ('typed_payload_field_type_declaration_drift_rehashed', mutate_field_type_declaration_drift, False, 'malicious'),
    ('typed_coordinate_scope_missing_rehashed', mutate_coordinate_scope_missing, False, 'malicious'),
    ('typed_parameter_scope_missing_rehashed', mutate_parameter_scope_missing, False, 'malicious'),
    ('typed_edge_target_wrong_rehashed', mutate_edge_target_wrong, False, 'malicious'),
    ('typed_edge_type_mismatch_rehashed', mutate_edge_type_mismatch, False, 'malicious'),
    ('typed_domain_ref_unentailed_rehashed', mutate_domain_ref_unentailed, False, 'malicious'),
    ('typed_target_ast_hash_mismatch_rehashed', mutate_target_ast_hash_mismatch, False, 'malicious'),
]

def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('--bundle', required=True)
    ap.add_argument('--outdir', required=True)
    args = ap.parse_args(argv)
    base = json.loads(Path(args.bundle).read_text(encoding='utf-8'))
    outdir = Path(args.outdir)
    cases_dir = outdir / 'tamper_cases_v0_8_typed_provenance'
    cases_dir.mkdir(parents=True, exist_ok=True)
    rows = []
    for name, mutator, expected_pass, kind in CASES:
        b = copy.deepcopy(base)
        if mutator is not None:
            mutator(b)
        case_path = cases_dir / f'{name}.json'
        report_path = cases_dir / f'{name}.typed_report.json'
        write_json(case_path, b)
        report = zf.replay_bundle(b)
        write_json(report_path, report)
        observed_pass = bool(report.get('review_pass'))
        rows.append({
            'case': name,
            'kind': kind,
            'expected_pass': expected_pass,
            'observed_pass': observed_pass,
            'expectation_met': expected_pass == observed_pass,
            'issue_count': report.get('issue_count'),
            'warning_count': report.get('warning_count'),
            'failed_gates': sorted([k for k, v in report.get('gates', {}).items() if not v]),
        })
    summary = {
        'suite': 'v0.8_typed_ast_provenance_tamper_suite',
        'total_cases': len(rows),
        'baseline_pass': rows[0]['observed_pass'],
        'benign_robustness_cases': sum(1 for r in rows if r['kind'] == 'benign_robustness'),
        'benign_robustness_cases_passed': sum(1 for r in rows if r['kind'] == 'benign_robustness' and r['observed_pass']),
        'malicious_cases': sum(1 for r in rows if r['kind'] == 'malicious'),
        'malicious_cases_rejected': sum(1 for r in rows if r['kind'] == 'malicious' and not r['observed_pass']),
        'all_expectations_met': all(r['expectation_met'] for r in rows),
        'cases': rows,
    }
    write_json(outdir / 'tamper_suite_v0_8_typed_provenance_report.json', summary)
    md = ['# v0.8 typed AST provenance tamper suite report', '', f"- total_cases: {summary['total_cases']}", f"- baseline_pass: {summary['baseline_pass']}", f"- benign_robustness_cases_passed: {summary['benign_robustness_cases_passed']} / {summary['benign_robustness_cases']}", f"- malicious_cases_rejected: {summary['malicious_cases_rejected']} / {summary['malicious_cases']}", f"- all_expectations_met: {summary['all_expectations_met']}", '', '| case | kind | expected_pass | observed_pass | expectation_met | failed_gates |', '|---|---:|---:|---:|---:|---|']
    for r in rows:
        md.append(f"| {r['case']} | {r['kind']} | {r['expected_pass']} | {r['observed_pass']} | {r['expectation_met']} | {', '.join(r['failed_gates'])} |")
    (outdir / 'tamper_suite_v0_8_typed_provenance_report.md').write_text('\n'.join(md) + '\n', encoding='utf-8')
    print(json.dumps(summary, indent=2, ensure_ascii=False))
    return 0 if summary['all_expectations_met'] else 1

if __name__ == '__main__':
    raise SystemExit(main())
