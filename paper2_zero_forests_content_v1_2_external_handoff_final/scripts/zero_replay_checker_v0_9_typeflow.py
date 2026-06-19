#!/usr/bin/env python3
from __future__ import annotations
import argparse, copy, hashlib, importlib.util, json
from pathlib import Path
from typing import Any, Dict, List, Set, Tuple

_BASE = Path(__file__).with_name('zero_replay_checker_v0_8_typed_provenance.py')
_SPEC = importlib.util.spec_from_file_location('zf_v08', _BASE)
zf_v08 = importlib.util.module_from_spec(_SPEC)
assert _SPEC and _SPEC.loader
_SPEC.loader.exec_module(zf_v08)

FLOW_PROFILE = 'zf_typed_dependency_flow_v1'
EDGE_PROFILE = 'zf_typed_dependency_edge_v1'

TYPEFLOW_REGISTRY = {
    'metric_to_connection': {
        'source_provenance': {'metric_definition'},
        'target_provenance': {'connection_component'},
        'source_nodes': {'metric_scalar_function', 'metric_component_scalar', 'inverse_metric_component_scalar'},
        'target_nodes': {'connection_scalar_export'},
    },
    'metric_to_einstein_tensor': {
        'source_provenance': {'metric_definition'},
        'target_provenance': {'einstein_tensor_component'},
        'source_nodes': {'metric_scalar_function', 'metric_component_scalar', 'inverse_metric_component_scalar'},
        'target_nodes': {'einstein_tensor_scalar_export'},
    },
    'einstein_to_divergence_derivative': {
        'source_provenance': {'einstein_tensor_component'},
        'target_provenance': {'partial_derivative_component'},
        'source_nodes': {'einstein_tensor_scalar_export'},
        'target_nodes': {'calculus_scalar_export'},
    },
    'connection_to_divergence_assembly': {
        'source_provenance': {'connection_component', 'index_multiplicity'},
        'target_provenance': {'covariant_divergence_assembly'},
        'source_nodes': {'connection_scalar_export', 'multiplicity_constant'},
        'target_nodes': {'assembled_tensor_scalar_expression'},
    },
    'einstein_to_divergence_assembly': {
        'source_provenance': {'einstein_tensor_component', 'index_multiplicity'},
        'target_provenance': {'covariant_divergence_assembly'},
        'source_nodes': {'einstein_tensor_scalar_export', 'multiplicity_constant'},
        'target_nodes': {'assembled_tensor_scalar_expression'},
    },
    'intra_divergence_assembly': {
        'source_provenance': {'partial_derivative_component', 'covariant_divergence_assembly'},
        'target_provenance': {'covariant_divergence_assembly'},
        'source_nodes': {'calculus_scalar_export', 'assembled_tensor_scalar_expression'},
        'target_nodes': {'assembled_tensor_scalar_expression'},
    },
}


def canonical_json(obj: Any) -> str:
    return json.dumps(obj, sort_keys=True, separators=(',', ':'), ensure_ascii=False)


def hash16(obj: Any) -> str:
    return hashlib.sha256(canonical_json(obj).encode('utf-8')).hexdigest()[:16]


def add_issue(issues: List[Dict[str, Any]], gate: str, code: str, **kw):
    item = {'severity': 'error', 'gate': gate, 'code': code}
    item.update(kw)
    issues.append(item)


def compute_edge_hash(edge: Dict[str, Any]) -> str:
    body = copy.deepcopy(edge)
    body.pop('edge_hash', None)
    return hash16(body)


def compute_flow_hash(flow: Dict[str, Any]) -> str:
    body = copy.deepcopy(flow)
    body.pop('flow_hash', None)
    return hash16(body)


def field_types(leaf: Dict[str, Any], fields: List[str]) -> List[Dict[str, Any]]:
    types = leaf.get('payload_field_types', {}) or {}
    return [types[f] for f in fields if f in types]


def collect_typed_provenance_sources(cert: Dict[str, Any]) -> Set[str]:
    out: Set[str] = set()
    for route in cert.get('routes', []):
        for step in route.get('steps', []):
            for om in step.get('occurrence_maps', []) or []:
                tp = om.get('typed_provenance')
                if isinstance(tp, dict):
                    sid = (tp.get('payload_binding') or {}).get('subleaf_id') or (tp.get('source') or {}).get('subleaf_id')
                    if sid:
                        out.add(sid)
    return out


def reachable(graph: Dict[str, Set[str]], roots: Set[str]) -> Set[str]:
    seen = set(roots)
    stack = list(roots)
    while stack:
        u = stack.pop()
        for v in graph.get(u, set()):
            if v not in seen:
                seen.add(v)
                stack.append(v)
    return seen


def has_cycle(graph: Dict[str, Set[str]]) -> bool:
    temp: Set[str] = set()
    perm: Set[str] = set()
    def dfs(u: str) -> bool:
        if u in perm:
            return False
        if u in temp:
            return True
        temp.add(u)
        for v in graph.get(u, set()):
            if dfs(v):
                return True
        temp.remove(u)
        perm.add(u)
        return False
    return any(dfs(u) for u in list(graph))


def validate_flow_for_cert(cert: Dict[str, Any]) -> Dict[str, Any]:
    issues: List[Dict[str, Any]] = []
    warnings: List[Dict[str, Any]] = []
    rows: List[Dict[str, Any]] = []
    claim = cert.get('claim_id')
    leaves = {x.get('subleaf_id'): x for x in cert.get('tensor_subleaves', []) or []}
    if not leaves:
        return {'dependency_edges_total': 0, 'dependency_edges_checked_ok': 0, 'gates': {f'DF{i}': True for i in range(1, 11)}, 'issue_count': 0, 'warning_count': 0, 'issues': [], 'warnings': [], 'rows': []}
    flow = cert.get('typed_dependency_flow')
    if not isinstance(flow, dict):
        add_issue(issues, 'DF1', 'MISSING_TYPED_DEPENDENCY_FLOW', claim_id=claim)
        return {'dependency_edges_total': 0, 'dependency_edges_checked_ok': 0, 'gates': {**{f'DF{i}': True for i in range(1, 11)}, 'DF1': False}, 'issue_count': len(issues), 'warning_count': 0, 'issues': issues, 'warnings': [], 'rows': []}
    if flow.get('profile') != FLOW_PROFILE:
        add_issue(issues, 'DF1', 'FLOW_PROFILE_MISMATCH', claim_id=claim, profile=flow.get('profile'))
    if flow.get('claim_id') != claim:
        add_issue(issues, 'DF1', 'FLOW_CLAIM_ID_MISMATCH', claim_id=claim, flow_claim_id=flow.get('claim_id'))
    edges = flow.get('typed_dependency_edges', []) or []
    if not edges:
        add_issue(issues, 'DF1', 'NO_TYPED_DEPENDENCY_EDGES', claim_id=claim)
    edge_ids: Set[str] = set()
    ok_count = 0
    covered_pairs: Set[Tuple[str, str]] = set()
    graph: Dict[str, Set[str]] = {sid: set() for sid in leaves}
    entailed = zf_v08.zf_v07.zf_v05.domain_entailments(cert)
    for edge in edges:
        before = len(issues)
        eid = edge.get('edge_id')
        if not eid or eid in edge_ids:
            add_issue(issues, 'DF1', 'EDGE_ID_MISSING_OR_DUPLICATE', claim_id=claim, edge_id=eid)
        edge_ids.add(eid)
        if edge.get('profile') != EDGE_PROFILE:
            add_issue(issues, 'DF1', 'EDGE_PROFILE_MISMATCH', claim_id=claim, edge_id=eid, profile=edge.get('profile'))
        source = edge.get('source', {}) or {}
        target = edge.get('target', {}) or {}
        ssid, tsid = source.get('subleaf_id'), target.get('subleaf_id')
        sl, tl = leaves.get(ssid), leaves.get(tsid)
        if sl is None or tl is None:
            add_issue(issues, 'DF2', 'EDGE_SOURCE_OR_TARGET_SUBLEAF_MISSING', claim_id=claim, edge_id=eid, source=ssid, target=tsid)
            continue
        if source.get('subleaf_hash') != sl.get('subleaf_hash') or target.get('subleaf_hash') != tl.get('subleaf_hash'):
            add_issue(issues, 'DF2', 'EDGE_SUBLEAF_HASH_BINDING_MISMATCH', claim_id=claim, edge_id=eid, source_hash=source.get('subleaf_hash'), target_hash=target.get('subleaf_hash'), actual_source_hash=sl.get('subleaf_hash'), actual_target_hash=tl.get('subleaf_hash'))
        for side_name, side_obj, leaf in [('source', source, sl), ('target', target, tl)]:
            if side_obj.get('rule_id') != leaf.get('rule_id') or side_obj.get('rule_class') != leaf.get('rule_class'):
                add_issue(issues, 'DF2', 'EDGE_RULE_BINDING_MISMATCH', claim_id=claim, edge_id=eid, side=side_name, edge_rule_id=side_obj.get('rule_id'), leaf_rule_id=leaf.get('rule_id'), edge_rule_class=side_obj.get('rule_class'), leaf_rule_class=leaf.get('rule_class'))
        kind = (edge.get('type_flow') or {}).get('dependency_kind')
        if ssid != tsid:
            if ssid not in set(tl.get('dependencies', []) or []):
                add_issue(issues, 'DF3', 'EDGE_NOT_DECLARED_IN_TARGET_DEPENDENCIES', claim_id=claim, edge_id=eid, source=ssid, target=tsid, target_dependencies=tl.get('dependencies'))
            else:
                covered_pairs.add((ssid, tsid))
                graph.setdefault(ssid, set()).add(tsid)
        else:
            if kind != 'intra_divergence_assembly':
                add_issue(issues, 'DF3', 'SELF_EDGE_WITH_NON_INTRASUBLEAF_KIND', claim_id=claim, edge_id=eid, kind=kind)
        sfields = source.get('payload_fields', []) or []
        tfields = target.get('payload_fields', []) or []
        for f in sfields:
            if f not in (sl.get('payload') or {}):
                add_issue(issues, 'DF4', 'SOURCE_PAYLOAD_FIELD_MISSING', claim_id=claim, edge_id=eid, field=f)
            if f not in (sl.get('payload_field_types') or {}):
                add_issue(issues, 'DF4', 'SOURCE_PAYLOAD_FIELD_TYPE_MISSING', claim_id=claim, edge_id=eid, field=f)
        for f in tfields:
            if f not in (tl.get('payload') or {}):
                add_issue(issues, 'DF4', 'TARGET_PAYLOAD_FIELD_MISSING', claim_id=claim, edge_id=eid, field=f)
            if f not in (tl.get('payload_field_types') or {}):
                add_issue(issues, 'DF4', 'TARGET_PAYLOAD_FIELD_TYPE_MISSING', claim_id=claim, edge_id=eid, field=f)
        stypes = field_types(sl, sfields)
        ttypes = field_types(tl, tfields)
        actual_source_nodes = sorted({x.get('node_type') for x in stypes})
        actual_target_nodes = sorted({x.get('node_type') for x in ttypes})
        actual_source_prov = sorted({x.get('provenance_class') for x in stypes})
        actual_target_prov = sorted({x.get('provenance_class') for x in ttypes})
        tf = edge.get('type_flow') or {}
        if tf.get('source_node_types') != actual_source_nodes or tf.get('target_node_types') != actual_target_nodes or tf.get('source_provenance_classes') != actual_source_prov or tf.get('target_provenance_classes') != actual_target_prov:
            add_issue(issues, 'DF4', 'EDGE_TYPE_DECLARATION_MISMATCH', claim_id=claim, edge_id=eid, declared=tf, actual={'source_node_types': actual_source_nodes, 'target_node_types': actual_target_nodes, 'source_provenance_classes': actual_source_prov, 'target_provenance_classes': actual_target_prov})
        reg = TYPEFLOW_REGISTRY.get(kind)
        if reg is None:
            add_issue(issues, 'DF5', 'UNKNOWN_DEPENDENCY_KIND', claim_id=claim, edge_id=eid, kind=kind)
        else:
            if not set(actual_source_nodes).issubset(reg['source_nodes']) or not set(actual_target_nodes).issubset(reg['target_nodes']) or not set(actual_source_prov).issubset(reg['source_provenance']) or not set(actual_target_prov).issubset(reg['target_provenance']):
                add_issue(issues, 'DF5', 'DEPENDENCY_KIND_TYPEFLOW_MISMATCH', claim_id=claim, edge_id=eid, kind=kind, actual={'source_node_types': actual_source_nodes, 'target_node_types': actual_target_nodes, 'source_provenance_classes': actual_source_prov, 'target_provenance_classes': actual_target_prov}, registry={k: sorted(v) for k, v in reg.items()})
        coord = sorted({x for typ in stypes + ttypes for x in (typ.get('coordinate_scope') or [])})
        params = sorted({x for typ in stypes + ttypes for x in (typ.get('parameter_scope') or [])})
        doms = sorted({x for typ in stypes + ttypes for x in (typ.get('domain_refs') or [])})
        scope = edge.get('scope') or {}
        if scope.get('coordinate_scope') != coord or scope.get('parameter_scope') != params or scope.get('domain_refs') != doms:
            add_issue(issues, 'DF6', 'EDGE_SCOPE_UNION_MISMATCH', claim_id=claim, edge_id=eid, expected={'coordinate_scope': coord, 'parameter_scope': params, 'domain_refs': doms}, observed=scope)
        for dref in doms:
            if dref not in cert.get('domain', {}).get('side_condition_refs', []) and not zf_v08.zf_v07.zf_v05.side_entailed(dref, entailed):
                add_issue(issues, 'DF6', 'EDGE_DOMAIN_REF_NOT_ENTAILED', claim_id=claim, edge_id=eid, domain_ref=dref, entailed=sorted(entailed))
        rec_edge = compute_edge_hash(edge)
        if rec_edge != edge.get('edge_hash'):
            add_issue(issues, 'DF9', 'EDGE_HASH_MISMATCH', claim_id=claim, edge_id=eid, reported=edge.get('edge_hash'), recomputed=rec_edge)
        rows.append({'claim_id': claim, 'edge_id': eid, 'kind': kind, 'source': ssid, 'source_fields': sfields, 'target': tsid, 'target_fields': tfields, 'edge_hash': edge.get('edge_hash')})
        ok_count += int(len(issues) == before)
    # Coverage and graph-level checks.
    declared_pairs = set()
    for sid, leaf in leaves.items():
        for dep in leaf.get('dependencies', []) or []:
            declared_pairs.add((dep, sid))
    missing_pairs = sorted(declared_pairs - covered_pairs)
    if missing_pairs:
        add_issue(issues, 'DF8', 'DECLARED_DEPENDENCY_PAIR_NOT_COVERED_BY_TYPED_EDGE', claim_id=claim, missing_pairs=missing_pairs)
    extra_pairs = sorted(covered_pairs - declared_pairs)
    if extra_pairs:
        add_issue(issues, 'DF8', 'TYPED_EDGE_PAIR_NOT_DECLARED_BY_SUBLEAF_DAG', claim_id=claim, extra_pairs=extra_pairs)
    if has_cycle(graph):
        add_issue(issues, 'DF7', 'DEPENDENCY_GRAPH_CYCLE_DETECTED', claim_id=claim)
    order = flow.get('topological_order', []) or []
    if set(order) != set(leaves):
        add_issue(issues, 'DF7', 'TOPOLOGICAL_ORDER_LEAF_SET_MISMATCH', claim_id=claim, observed=order, expected=sorted(leaves))
    index = {sid: i for i, sid in enumerate(order)}
    for dep, sid in declared_pairs:
        if dep in index and sid in index and not (index[dep] < index[sid]):
            add_issue(issues, 'DF7', 'TOPOLOGICAL_ORDER_DEPENDENCY_VIOLATION', claim_id=claim, dependency=dep, target=sid, order=order)
    roots = set(flow.get('root_subleaves', []) or [])
    sinks = set(flow.get('sink_subleaves', []) or [])
    if not roots or not roots.issubset(leaves):
        add_issue(issues, 'DF7', 'ROOT_SUBLEAVES_INVALID', claim_id=claim, roots=sorted(roots), leaves=sorted(leaves))
    if not sinks or not sinks.issubset(leaves):
        add_issue(issues, 'DF7', 'SINK_SUBLEAVES_INVALID', claim_id=claim, sinks=sorted(sinks), leaves=sorted(leaves))
    reach = reachable(graph, roots)
    unreachable = sorted(set(leaves) - reach)
    if unreachable:
        add_issue(issues, 'DF7', 'SUBLEAF_NOT_REACHABLE_FROM_ROOT', claim_id=claim, unreachable=unreachable, roots=sorted(roots))
    sink_unreachable = sorted(sinks - reach)
    if sink_unreachable:
        add_issue(issues, 'DF7', 'SINK_NOT_REACHABLE_FROM_ROOT', claim_id=claim, sink_unreachable=sink_unreachable)
    # A valid sink must expose the selected normalized zero-obligation lhs as one of its payload fields.
    norm_lhs = (cert.get('normalized_obligation') or {}).get('lhs_expr')
    sink_exposes_norm_lhs = False
    if norm_lhs is not None:
        for sid in sinks:
            leaf = leaves.get(sid)
            if not leaf:
                continue
            for field_name, payload_value in (leaf.get('payload') or {}).items():
                if isinstance(payload_value, (str, int, float)):
                    try:
                        eq, _diag = zf_v08.zf_v07.zf_v05.expr_equal(str(payload_value), str(norm_lhs))
                    except Exception:
                        eq = str(payload_value) == str(norm_lhs)
                    if eq:
                        sink_exposes_norm_lhs = True
                        break
            if sink_exposes_norm_lhs:
                break
    if not sink_exposes_norm_lhs:
        add_issue(issues, 'DF7', 'SINK_DOES_NOT_EXPOSE_NORMALIZED_LHS', claim_id=claim, sinks=sorted(sinks), normalized_lhs=norm_lhs)
    tp_sources = collect_typed_provenance_sources(cert)
    if not tp_sources.issubset(set(leaves)):
        add_issue(issues, 'DF10', 'TYPED_PROVENANCE_SOURCE_NOT_IN_SUBLEAF_DAG', claim_id=claim, bad=sorted(tp_sources - set(leaves)))
    tp_not_reachable = sorted(tp_sources - reach)
    if tp_not_reachable:
        add_issue(issues, 'DF10', 'TYPED_PROVENANCE_SOURCE_NOT_REACHABLE_IN_TYPEFLOW', claim_id=claim, bad=tp_not_reachable)
    flow_hash = compute_flow_hash(flow)
    if flow_hash != flow.get('flow_hash'):
        add_issue(issues, 'DF9', 'FLOW_HASH_MISMATCH', claim_id=claim, reported=flow.get('flow_hash'), recomputed=flow_hash)
    gates = {f'DF{i}': True for i in range(1, 11)}
    for issue in issues:
        gates[issue['gate']] = False
    return {'dependency_edges_total': len(edges), 'dependency_edges_checked_ok': ok_count, 'gates': gates, 'issue_count': len(issues), 'warning_count': len(warnings), 'issues': issues, 'warnings': warnings, 'rows': rows, 'graph': {'covered_pairs': sorted(list(covered_pairs)), 'declared_pairs': sorted(list(declared_pairs)), 'reachable_from_roots': sorted(reach if 'reach' in locals() else [])}}


def validate_typed_dependency_flows(bundle: Dict[str, Any]) -> Dict[str, Any]:
    issues: List[Dict[str, Any]] = []
    warnings: List[Dict[str, Any]] = []
    total = ok = 0
    cert_reports = []
    rows = []
    for cert in bundle.get('certificates', []):
        if cert.get('tensor_subleaves'):
            rep = validate_flow_for_cert(cert)
            cert_reports.append({'claim_id': cert.get('claim_id'), **rep})
            total += rep.get('dependency_edges_total', 0)
            ok += rep.get('dependency_edges_checked_ok', 0)
            issues.extend(rep.get('issues', []))
            warnings.extend(rep.get('warnings', []))
            rows.extend(rep.get('rows', []))
    gates = {f'DF{i}': True for i in range(1, 11)}
    for issue in issues:
        gates[issue['gate']] = False
    return {'dependency_edges_total': total, 'dependency_edges_checked_ok': ok, 'cert_reports': cert_reports, 'gates': gates, 'issue_count': len(issues), 'warning_count': len(warnings), 'issues': issues, 'warnings': warnings, 'rows': rows}


def replay_bundle(bundle: Dict[str, Any]) -> Dict[str, Any]:
    base = zf_v08.replay_bundle(bundle)
    df_report = validate_typed_dependency_flows(bundle)
    base['title'] = 'Paper2 Zero Forests strict Level-B+ replay report v0.9 typed dependency flow'
    base['strict_level'] = 'Level-B+ named tensor subleaves plus AST-path locators plus typed provenance plus typed dependency flow'
    base['typed_dependency_flow_report'] = df_report
    base['counts']['typed_dependency_edges'] = df_report['dependency_edges_total']
    base['counts']['typed_dependency_edges_checked_ok'] = df_report['dependency_edges_checked_ok']
    base['gates'].update(df_report['gates'])
    base['issues'].extend(df_report['issues'])
    base['warnings'].extend(df_report['warnings'])
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
    print(json.dumps({'review_pass': rep['review_pass'], 'counts': rep['counts'], 'typeflow_gates': rep['typed_dependency_flow_report']['gates'], 'issue_count': rep['issue_count'], 'warning_count': rep['warning_count']}, indent=2, ensure_ascii=False))
    return 0 if rep['review_pass'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
