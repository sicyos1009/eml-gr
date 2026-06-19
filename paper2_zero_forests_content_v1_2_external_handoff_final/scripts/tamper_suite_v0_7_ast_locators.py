#!/usr/bin/env python3
from __future__ import annotations
import argparse, copy, importlib.util, json, subprocess, sys
from pathlib import Path
from typing import Any, Dict, List

_CHECKER_NAME = 'zero_replay_checker_v0_7_ast_locators.py'
_SPEC = importlib.util.spec_from_file_location('zf_v07', Path(__file__).with_name(_CHECKER_NAME))
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

def recompute_route_hashes(bundle: Dict[str, Any]):
    for cert in bundle.get('certificates', []):
        for route in cert.get('routes', []):
            route['raw_trace_hash'] = zf.zf_v05.recompute_raw_route_hash(route)

def recompute_subleaf_hashes(bundle: Dict[str, Any]):
    for cert in bundle.get('certificates', []):
        for leaf in cert.get('tensor_subleaves', []) or []:
            leaf['subleaf_hash'] = zf.zf_v05.recompute_subleaf_hash(leaf)

def recompute_ast_hashes(bundle: Dict[str, Any], best_effort: bool = True):
    for cert in bundle.get('certificates', []):
        for route in cert.get('routes', []):
            for step in route.get('steps', []):
                for om in step.get('occurrence_maps', []) or []:
                    al = om.get('ast_locator')
                    if not isinstance(al, dict):
                        continue
                    try:
                        root = zf.parse_expr_ast(str(step[al['target_field']]))
                        selected = zf.resolve_path(root, str(al['path']))
                        al['ast_node_hash'] = zf.compute_ast_locator_hash(al, selected)
                    except Exception:
                        if not best_effort:
                            raise

def recompute_all(bundle: Dict[str, Any], ast_best_effort: bool = True):
    recompute_subleaf_hashes(bundle)
    recompute_ast_hashes(bundle, best_effort=ast_best_effort)
    recompute_route_hashes(bundle)

def first_occ(bundle: Dict[str, Any], needle: str) -> Dict[str, Any]:
    flrw = get_flrw(bundle)
    for route in flrw['routes']:
        for step in route['steps']:
            for om in step.get('occurrence_maps', []) or []:
                if needle in om.get('occurrence_id', ''):
                    return om
    raise KeyError(needle)

def first_tensor_step(bundle: Dict[str, Any], step_id: str = 'A2') -> Dict[str, Any]:
    for route in get_flrw(bundle)['routes']:
        for step in route['steps']:
            if step.get('step_id') == step_id:
                return step
    raise KeyError(step_id)

def mutate_whitespace_reformat(bundle: Dict[str, Any]):
    for route in get_flrw(bundle)['routes']:
        for step in route['steps']:
            for fld in ('before_expr', 'after_expr'):
                if step.get(fld) == OLD_EXPR:
                    step[fld] = REFORMATTED_EXPR
            if route.get('final_expr') == OLD_EXPR:
                route['final_expr'] = REFORMATTED_EXPR
    recompute_all(bundle)

def mutate_literal_span_shift(bundle: Dict[str, Any]):
    om = first_occ(bundle, 'partial_time_derivative')
    om['span_start'] = 999
    om['span_end'] = 1009
    # v0.7 treats literal spans as diagnostic-only, so AST hashes do not change.
    recompute_route_hashes(bundle)

def mutate_ast_hash_literal(bundle: Dict[str, Any]):
    om = first_occ(bundle, 'partial_time_derivative')
    om['ast_locator']['ast_node_hash'] = '0000000000000000'
    recompute_route_hashes(bundle)

def mutate_ast_path_wrong(bundle: Dict[str, Any]):
    om = first_occ(bundle, 'connection_trace_factor')
    om['ast_locator']['path'] = '$.terms[1].factors[1:3]'
    recompute_ast_hashes(bundle)
    recompute_route_hashes(bundle)

def mutate_expected_expr_drift(bundle: Dict[str, Any]):
    om = first_occ(bundle, 'connection_trace_factor')
    om['ast_locator']['expected_expr'] = 'H*3'
    recompute_ast_hashes(bundle)
    recompute_route_hashes(bundle)

def mutate_bad_target_field(bundle: Dict[str, Any]):
    om = first_occ(bundle, 'partial_time_derivative')
    om['ast_locator']['target_field'] = 'notes'
    recompute_ast_hashes(bundle)
    recompute_route_hashes(bundle)

def mutate_factor_window_off_by_one(bundle: Dict[str, Any]):
    om = first_occ(bundle, 'einstein_00_factor')
    om['ast_locator']['path'] = '$.terms[1].factors[1:4]'
    recompute_ast_hashes(bundle)
    recompute_route_hashes(bundle)

def mutate_route_expr_structural_changed(bundle: Dict[str, Any]):
    step = first_tensor_step(bundle, 'A2')
    bad = OLD_EXPR + ' + H'
    step['after_expr'] = bad
    # preserve chain so the failure is semantic/AST, not only chain-disconnect
    for route in get_flrw(bundle)['routes']:
        if route['route_id'].startswith('flrw_route_A'):
            for st in route['steps']:
                if st.get('step_id') == 'A3':
                    st['before_expr'] = bad
    recompute_ast_hashes(bundle)
    recompute_route_hashes(bundle)

def mutate_subleaf_payload_drift(bundle: Dict[str, Any]):
    flrw = get_flrw(bundle)
    for leaf in flrw.get('tensor_subleaves', []):
        if leaf.get('subleaf_id') == 'flrw.connection.gamma_0ii':
            leaf['payload']['gamma_0ii_expr'] = 'H*exp(2*H*t) + 1'
    recompute_all(bundle)

def mutate_duplicate_occurrence_id(bundle: Dict[str, Any]):
    step = first_tensor_step(bundle, 'A2')
    if len(step.get('occurrence_maps', [])) >= 2:
        step['occurrence_maps'][1]['occurrence_id'] = step['occurrence_maps'][0]['occurrence_id']
    recompute_all(bundle)

def mutate_missing_ast_locator_for_ref(bundle: Dict[str, Any]):
    step = first_tensor_step(bundle, 'A2')
    step['occurrence_maps'] = [om for om in step.get('occurrence_maps', []) if om.get('subleaf_id') != 'flrw.connection.gamma_0ii']
    recompute_all(bundle)

def mutate_nonparseable_target_expr(bundle: Dict[str, Any]):
    step = first_tensor_step(bundle, 'A2')
    bad = 'diff(3*H**2,'
    step['after_expr'] = bad
    for route in get_flrw(bundle)['routes']:
        if route['route_id'].startswith('flrw_route_A'):
            for st in route['steps']:
                if st.get('step_id') == 'A3':
                    st['before_expr'] = bad
    recompute_ast_hashes(bundle)
    recompute_route_hashes(bundle)

def mutate_ast_profile_mismatch(bundle: Dict[str, Any]):
    om = first_occ(bundle, 'partial_time_derivative')
    om['ast_locator']['ast_profile'] = 'wrong_profile'
    recompute_ast_hashes(bundle)
    recompute_route_hashes(bundle)

CASES = [
    ('baseline_untampered', None, True, 'baseline'),
    ('benign_whitespace_reformatted_route_expr_rehashed', mutate_whitespace_reformat, True, 'benign_robustness'),
    ('benign_literal_span_shift_diagnostic_only_rehashed', mutate_literal_span_shift, True, 'benign_robustness'),
    ('ast_hash_literal', mutate_ast_hash_literal, False, 'malicious'),
    ('ast_path_wrong_rehashed', mutate_ast_path_wrong, False, 'malicious'),
    ('ast_expected_expr_drift_rehashed', mutate_expected_expr_drift, False, 'malicious'),
    ('ast_target_field_bad_rehashed', mutate_bad_target_field, False, 'malicious'),
    ('ast_factor_window_off_by_one_rehashed', mutate_factor_window_off_by_one, False, 'malicious'),
    ('route_expr_structural_changed_rehashed', mutate_route_expr_structural_changed, False, 'malicious'),
    ('subleaf_payload_drift_rehashed', mutate_subleaf_payload_drift, False, 'malicious'),
    ('duplicate_occurrence_id_rehashed', mutate_duplicate_occurrence_id, False, 'malicious'),
    ('missing_ast_locator_for_subleaf_ref_rehashed', mutate_missing_ast_locator_for_ref, False, 'malicious'),
    ('nonparseable_target_expr_rehashed', mutate_nonparseable_target_expr, False, 'malicious'),
    ('ast_profile_mismatch_rehashed', mutate_ast_profile_mismatch, False, 'malicious'),
]

def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('--bundle', required=True)
    ap.add_argument('--outdir', required=True)
    args = ap.parse_args(argv)
    base = json.loads(Path(args.bundle).read_text(encoding='utf-8'))
    outdir = Path(args.outdir)
    cases_dir = outdir / 'tamper_cases_v0_7_ast_locators'
    cases_dir.mkdir(parents=True, exist_ok=True)
    rows = []
    for name, mutator, expected_pass, kind in CASES:
        b = copy.deepcopy(base)
        if mutator is not None:
            mutator(b)
        case_path = cases_dir / f'{name}.json'
        report_path = cases_dir / f'{name}.ast_report.json'
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
        'suite': 'v0.7_ast_path_locator_tamper_suite',
        'total_cases': len(rows),
        'baseline_pass': rows[0]['observed_pass'],
        'benign_robustness_cases': sum(1 for r in rows if r['kind'] == 'benign_robustness'),
        'benign_robustness_cases_passed': sum(1 for r in rows if r['kind'] == 'benign_robustness' and r['observed_pass']),
        'malicious_cases': sum(1 for r in rows if r['kind'] == 'malicious'),
        'malicious_cases_rejected': sum(1 for r in rows if r['kind'] == 'malicious' and not r['observed_pass']),
        'all_expectations_met': all(r['expectation_met'] for r in rows),
        'cases': rows,
    }
    write_json(outdir / 'tamper_suite_v0_7_ast_locators_report.json', summary)
    md = ['# v0.7 AST-path locator tamper suite report', '', f"- total_cases: {summary['total_cases']}", f"- baseline_pass: {summary['baseline_pass']}", f"- benign_robustness_cases_passed: {summary['benign_robustness_cases_passed']} / {summary['benign_robustness_cases']}", f"- malicious_cases_rejected: {summary['malicious_cases_rejected']} / {summary['malicious_cases']}", f"- all_expectations_met: {summary['all_expectations_met']}", '', '| case | kind | expected_pass | observed_pass | expectation_met | failed_gates |', '|---|---:|---:|---:|---:|---|']
    for r in rows:
        md.append(f"| {r['case']} | {r['kind']} | {r['expected_pass']} | {r['observed_pass']} | {r['expectation_met']} | {', '.join(r['failed_gates'])} |")
    (outdir / 'tamper_suite_v0_7_ast_locators_report.md').write_text('\n'.join(md) + '\n', encoding='utf-8')
    print(json.dumps(summary, indent=2, ensure_ascii=False))
    return 0 if summary['all_expectations_met'] else 1

if __name__ == '__main__':
    raise SystemExit(main())
