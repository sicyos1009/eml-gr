#!/usr/bin/env python3
from __future__ import annotations
import argparse, copy, importlib.util, json
from pathlib import Path
from typing import Any, Dict, List

_CHECKER_NAME = 'zero_replay_checker_v0_9_typeflow.py'
_SPEC = importlib.util.spec_from_file_location('zf_v09', Path(__file__).with_name(_CHECKER_NAME))
zf = importlib.util.module_from_spec(_SPEC)
assert _SPEC and _SPEC.loader
_SPEC.loader.exec_module(zf)


def write_json(path: Path, obj: Any):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')


def get_flrw(bundle: Dict[str, Any]) -> Dict[str, Any]:
    for cert in bundle['certificates']:
        if cert.get('claim_id') == 'zero.flrw.contracted_bianchi_divG0':
            return cert
    raise KeyError('FLRW certificate not found')


def leaves(bundle: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
    return {x['subleaf_id']: x for x in get_flrw(bundle).get('tensor_subleaves', [])}


def flow(bundle: Dict[str, Any]) -> Dict[str, Any]:
    return get_flrw(bundle)['typed_dependency_flow']


def edges(bundle: Dict[str, Any]) -> List[Dict[str, Any]]:
    return flow(bundle)['typed_dependency_edges']


def edge(bundle: Dict[str, Any], edge_id_substring: str) -> Dict[str, Any]:
    for e in edges(bundle):
        if edge_id_substring in e.get('edge_id', ''):
            return e
    raise KeyError(edge_id_substring)


def recompute_edge_hashes(bundle: Dict[str, Any]):
    for e in edges(bundle):
        e['edge_hash'] = zf.compute_edge_hash(e)


def recompute_flow_hash(bundle: Dict[str, Any]):
    flow(bundle)['flow_hash'] = zf.compute_flow_hash(flow(bundle))


def recompute_all_typeflow_hashes(bundle: Dict[str, Any]):
    recompute_edge_hashes(bundle)
    recompute_flow_hash(bundle)


def sync_edge_leaf_hashes(bundle: Dict[str, Any]):
    lm = leaves(bundle)
    for e in edges(bundle):
        for side in ('source', 'target'):
            sid = e[side]['subleaf_id']
            if sid in lm:
                e[side]['subleaf_hash'] = lm[sid].get('subleaf_hash')
                e[side]['rule_id'] = lm[sid].get('rule_id')
                e[side]['rule_class'] = lm[sid].get('rule_class')


def mutate_edge_order_rehashed(bundle):
    flow(bundle)['typed_dependency_edges'] = list(reversed(edges(bundle)))
    recompute_flow_hash(bundle)


def mutate_missing_flow_object(bundle):
    get_flrw(bundle).pop('typed_dependency_flow', None)


def mutate_edge_hash_literal(bundle):
    edge(bundle, 'metric_to_gamma_trace')['edge_hash'] = '0000000000000000'
    recompute_flow_hash(bundle)


def mutate_flow_hash_literal(bundle):
    flow(bundle)['flow_hash'] = '1111111111111111'


def mutate_source_subleaf_hash_stale(bundle):
    edge(bundle, 'gamma_0ii_to_spatial_term')['source']['subleaf_hash'] = 'badbadbadbadbadb'
    recompute_flow_hash(bundle)


def mutate_source_rule_mismatch(bundle):
    edge(bundle, 'metric_to_G00')['source']['rule_id'] = 'TDEF.WRONG_METRIC'
    recompute_edge_hashes(bundle); recompute_flow_hash(bundle)


def mutate_dependency_kind_unknown(bundle):
    edge(bundle, 'G00_to_trace_term')['type_flow']['dependency_kind'] = 'unknown_dependency_kind'
    recompute_all_typeflow_hashes(bundle)


def mutate_dependency_kind_wrong_registry(bundle):
    edge(bundle, 'metric_to_gamma_0ii')['type_flow']['dependency_kind'] = 'einstein_to_divergence_assembly'
    recompute_all_typeflow_hashes(bundle)


def mutate_target_payload_field_missing(bundle):
    edge(bundle, 'G00_to_partial_term')['target']['payload_fields'] = ['missing_partial_field']
    edge(bundle, 'G00_to_partial_term')['type_flow']['target_node_types'] = []
    edge(bundle, 'G00_to_partial_term')['type_flow']['target_provenance_classes'] = []
    recompute_all_typeflow_hashes(bundle)


def mutate_type_declaration_mismatch(bundle):
    e = edge(bundle, 'gamma_trace_to_trace_term')
    e['type_flow']['source_node_types'] = ['einstein_tensor_scalar_export']
    recompute_all_typeflow_hashes(bundle)


def mutate_scope_omission(bundle):
    edge(bundle, 'Gii_to_spatial_term')['scope']['domain_refs'] = []
    recompute_all_typeflow_hashes(bundle)


def mutate_unentailed_domain(bundle):
    e = edge(bundle, 'Gii_to_spatial_term')
    e['scope']['domain_refs'] = ['DOM.NONZERO_DENOMINATOR']
    recompute_all_typeflow_hashes(bundle)


def mutate_declared_dependency_edge_deleted(bundle):
    flow(bundle)['typed_dependency_edges'] = [e for e in edges(bundle) if 'metric_to_Gii' not in e.get('edge_id', '')]
    recompute_flow_hash(bundle)


def mutate_root_invalid(bundle):
    flow(bundle)['root_subleaves'] = ['flrw.connection.gamma_trace_0']
    recompute_flow_hash(bundle)


def mutate_sink_invalid(bundle):
    flow(bundle)['sink_subleaves'] = ['flrw.einstein.G_contra_00']
    recompute_flow_hash(bundle)


def mutate_topological_order_invalid(bundle):
    order = flow(bundle)['topological_order']
    flow(bundle)['topological_order'] = list(reversed(order))
    recompute_flow_hash(bundle)


def mutate_duplicate_edge_id(bundle):
    edges(bundle)[1]['edge_id'] = edges(bundle)[0]['edge_id']
    recompute_all_typeflow_hashes(bundle)


def mutate_self_edge_wrong_kind(bundle):
    edge(bundle, 'term_fields_to_divergence_expr')['type_flow']['dependency_kind'] = 'connection_to_divergence_assembly'
    recompute_all_typeflow_hashes(bundle)


def mutate_typed_provenance_source_disconnect(bundle):
    # Remove all edges into the divergence sink while retaining hashes, so typed provenance sources are not connected to sink coverage.
    flow(bundle)['typed_dependency_edges'] = [e for e in edges(bundle) if e['target']['subleaf_id'] != 'flrw.divergence.expanded_nu0']
    recompute_flow_hash(bundle)


CASES = [
    ('baseline_untampered', None, True, 'baseline'),
    ('benign_dependency_edge_order_reversed_rehashed', mutate_edge_order_rehashed, True, 'benign_robustness'),
    ('missing_typed_dependency_flow_object', mutate_missing_flow_object, False, 'malicious'),
    ('typed_dependency_edge_hash_literal', mutate_edge_hash_literal, False, 'malicious'),
    ('typed_dependency_flow_hash_literal', mutate_flow_hash_literal, False, 'malicious'),
    ('typed_dependency_source_subleaf_hash_stale', mutate_source_subleaf_hash_stale, False, 'malicious'),
    ('typed_dependency_source_rule_mismatch_rehashed', mutate_source_rule_mismatch, False, 'malicious'),
    ('typed_dependency_kind_unknown_rehashed', mutate_dependency_kind_unknown, False, 'malicious'),
    ('typed_dependency_kind_registry_mismatch_rehashed', mutate_dependency_kind_wrong_registry, False, 'malicious'),
    ('typed_dependency_target_payload_field_missing_rehashed', mutate_target_payload_field_missing, False, 'malicious'),
    ('typed_dependency_type_declaration_mismatch_rehashed', mutate_type_declaration_mismatch, False, 'malicious'),
    ('typed_dependency_scope_omission_rehashed', mutate_scope_omission, False, 'malicious'),
    ('typed_dependency_unentailed_domain_ref_rehashed', mutate_unentailed_domain, False, 'malicious'),
    ('declared_dependency_edge_deleted_rehashed', mutate_declared_dependency_edge_deleted, False, 'malicious'),
    ('typed_dependency_root_invalid_rehashed', mutate_root_invalid, False, 'malicious'),
    ('typed_dependency_sink_invalid_rehashed', mutate_sink_invalid, False, 'malicious'),
    ('typed_dependency_topological_order_invalid_rehashed', mutate_topological_order_invalid, False, 'malicious'),
    ('typed_dependency_duplicate_edge_id_rehashed', mutate_duplicate_edge_id, False, 'malicious'),
    ('typed_dependency_self_edge_wrong_kind_rehashed', mutate_self_edge_wrong_kind, False, 'malicious'),
    ('typed_dependency_sink_disconnected_rehashed', mutate_typed_provenance_source_disconnect, False, 'malicious'),
]


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('--bundle', required=True)
    ap.add_argument('--outdir', required=True)
    args = ap.parse_args(argv)
    base = json.loads(Path(args.bundle).read_text(encoding='utf-8'))
    outdir = Path(args.outdir)
    cases_dir = outdir / 'tamper_cases_v0_9_typeflow'
    cases_dir.mkdir(parents=True, exist_ok=True)
    rows = []
    for name, mutator, expected_pass, kind in CASES:
        b = copy.deepcopy(base)
        if mutator is not None:
            mutator(b)
        case_path = cases_dir / f'{name}.json'
        report_path = cases_dir / f'{name}.typeflow_report.json'
        write_json(case_path, b)
        report = zf.replay_bundle(b)
        write_json(report_path, report)
        observed_pass = bool(report.get('review_pass'))
        rows.append({'case': name, 'kind': kind, 'expected_pass': expected_pass, 'observed_pass': observed_pass, 'expectation_met': expected_pass == observed_pass, 'issue_count': report.get('issue_count'), 'warning_count': report.get('warning_count'), 'failed_gates': sorted([k for k, v in report.get('gates', {}).items() if not v])})
    summary = {
        'suite': 'v0.9_typed_dependency_flow_tamper_suite',
        'total_cases': len(rows),
        'baseline_pass': rows[0]['observed_pass'],
        'benign_robustness_cases': sum(1 for r in rows if r['kind'] == 'benign_robustness'),
        'benign_robustness_cases_passed': sum(1 for r in rows if r['kind'] == 'benign_robustness' and r['observed_pass']),
        'malicious_cases': sum(1 for r in rows if r['kind'] == 'malicious'),
        'malicious_cases_rejected': sum(1 for r in rows if r['kind'] == 'malicious' and not r['observed_pass']),
        'all_expectations_met': all(r['expectation_met'] for r in rows),
        'cases': rows,
    }
    write_json(outdir / 'tamper_suite_v0_9_typeflow_report.json', summary)
    md = ['# v0.9 typed dependency flow tamper suite report', '', f"- total_cases: {summary['total_cases']}", f"- baseline_pass: {summary['baseline_pass']}", f"- benign_robustness_cases_passed: {summary['benign_robustness_cases_passed']} / {summary['benign_robustness_cases']}", f"- malicious_cases_rejected: {summary['malicious_cases_rejected']} / {summary['malicious_cases']}", f"- all_expectations_met: {summary['all_expectations_met']}", '', '| case | kind | expected_pass | observed_pass | expectation_met | failed_gates |', '|---|---:|---:|---:|---:|---|']
    for r in rows:
        md.append(f"| {r['case']} | {r['kind']} | {r['expected_pass']} | {r['observed_pass']} | {r['expectation_met']} | {', '.join(r['failed_gates'])} |")
    (outdir / 'tamper_suite_v0_9_typeflow_report.md').write_text('\n'.join(md) + '\n', encoding='utf-8')
    print(json.dumps(summary, indent=2, ensure_ascii=False))
    return 0 if summary['all_expectations_met'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
