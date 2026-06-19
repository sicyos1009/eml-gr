#!/usr/bin/env python3
from __future__ import annotations
import argparse, copy, hashlib, importlib.util, json
from pathlib import Path
from typing import Any, Dict, List, Set, Tuple

_BASE = Path(__file__).with_name('zero_replay_checker_v0_5_strict.py')
_SPEC = importlib.util.spec_from_file_location('zf_v05', _BASE)
zf_v05 = importlib.util.module_from_spec(_SPEC)
assert _SPEC and _SPEC.loader
_SPEC.loader.exec_module(zf_v05)
TENSOR_CLASSES = {'tensor_definition','tensor_identity'}

def canonical_json(obj: Any) -> str:
    return json.dumps(obj, sort_keys=True, separators=(',', ':'), ensure_ascii=False)

def hash16(obj: Any) -> str:
    return hashlib.sha256(canonical_json(obj).encode('utf-8')).hexdigest()[:16]

def recompute_occurrence_hash(occ: Dict[str, Any]) -> str:
    tmp = dict(occ); tmp.pop('occurrence_hash', None)
    return hash16(tmp)

def literal_spans(target: str, needle: str) -> List[Tuple[int,int]]:
    out=[]; pos=target.find(needle)
    while pos >= 0:
        out.append((pos, pos+len(needle)))
        pos=target.find(needle, pos+1)
    return out

def add_issue(issues: List[Dict[str, Any]], gate: str, code: str, **kw):
    x={'severity':'error','gate':gate,'code':code}; x.update(kw); issues.append(x)

def validate_occurrence_maps(bundle: Dict[str, Any]) -> Dict[str, Any]:
    issues: List[Dict[str, Any]] = []
    occurrence_total = 0
    occurrence_ok = 0
    tensor_steps = 0
    tensor_steps_with_maps = 0
    seen_ids: Set[str] = set()
    reports = []
    for cert in bundle.get('certificates', []):
        leaves = {x.get('subleaf_id'): x for x in cert.get('tensor_subleaves', []) or []}
        if not leaves:
            continue
        claim = cert.get('claim_id')
        for route in cert.get('routes', []):
            rid = route.get('route_id')
            for st in route.get('steps', []):
                if st.get('rule_class') not in TENSOR_CLASSES:
                    continue
                tensor_steps += 1
                sid = st.get('step_id')
                maps = st.get('occurrence_maps', []) or []
                refs = set(st.get('subleaf_refs', []) or [])
                if maps:
                    tensor_steps_with_maps += 1
                else:
                    add_issue(issues, 'OM1', 'TENSOR_STEP_MISSING_OCCURRENCE_MAPS', claim_id=claim, route_id=rid, step_id=sid)
                mapped: Set[str] = set()
                for om in maps:
                    before = len(issues)
                    occurrence_total += 1
                    oid = om.get('occurrence_id')
                    if oid in seen_ids:
                        add_issue(issues, 'OM5', 'DUPLICATE_OCCURRENCE_ID', claim_id=claim, route_id=rid, step_id=sid, occurrence_id=oid)
                    seen_ids.add(oid)
                    if om.get('route_id') != rid or om.get('step_id') != sid:
                        add_issue(issues, 'OM5', 'OCCURRENCE_ROUTE_STEP_BINDING_MISMATCH', claim_id=claim, route_id=rid, step_id=sid, occurrence_id=oid)
                    rec = recompute_occurrence_hash(om)
                    if rec != om.get('occurrence_hash'):
                        add_issue(issues, 'OM2', 'OCCURRENCE_HASH_MISMATCH', claim_id=claim, route_id=rid, step_id=sid, occurrence_id=oid, reported=om.get('occurrence_hash'), recomputed=rec)
                    if om.get('locator_kind') != 'literal_span_v1' or om.get('patch_action') != 'observe_tensor_subleaf_occurrence':
                        add_issue(issues, 'OM3', 'OCCURRENCE_LOCATOR_OR_ACTION_INVALID', claim_id=claim, route_id=rid, step_id=sid, occurrence_id=oid)
                    target_field = om.get('target_field')
                    target = str(st.get(target_field, '')) if target_field in {'before_expr','after_expr'} else ''
                    if target_field not in {'before_expr','after_expr'}:
                        add_issue(issues, 'OM3', 'BAD_TARGET_FIELD', claim_id=claim, route_id=rid, step_id=sid, occurrence_id=oid, target_field=target_field)
                    expr = str(om.get('expr',''))
                    a,b = om.get('span_start'), om.get('span_end')
                    if not isinstance(a, int) or not isinstance(b, int) or a < 0 or b < a or b > len(target):
                        add_issue(issues, 'OM3', 'BAD_SPAN', claim_id=claim, route_id=rid, step_id=sid, occurrence_id=oid, span_start=a, span_end=b, target_length=len(target))
                    elif target[a:b] != expr:
                        add_issue(issues, 'OM3', 'TARGET_SPAN_DOES_NOT_MATCH_EXPR', claim_id=claim, route_id=rid, step_id=sid, occurrence_id=oid, actual=target[a:b], expr=expr)
                    spans = literal_spans(target, expr) if expr else []
                    ix = om.get('literal_occurrence_index_0_based')
                    if not isinstance(ix, int) or ix < 0 or ix >= len(spans):
                        add_issue(issues, 'OM3', 'BAD_LITERAL_OCCURRENCE_INDEX', claim_id=claim, route_id=rid, step_id=sid, occurrence_id=oid, index=ix, available_spans=spans)
                    elif isinstance(a, int) and isinstance(b, int) and spans[ix] != (a,b):
                        add_issue(issues, 'OM3', 'LITERAL_OCCURRENCE_INDEX_SPAN_MISMATCH', claim_id=claim, route_id=rid, step_id=sid, occurrence_id=oid, indexed_span=spans[ix], declared_span=[a,b])
                    subleaf_id = om.get('subleaf_id'); field = om.get('payload_field')
                    mapped.add(subleaf_id)
                    payload = leaves.get(subleaf_id, {}).get('payload', {})
                    if subleaf_id not in leaves or field not in payload:
                        add_issue(issues, 'OM4', 'OCCURRENCE_PAYLOAD_REFERENCE_INVALID', claim_id=claim, route_id=rid, step_id=sid, occurrence_id=oid, subleaf_id=subleaf_id, payload_field=field)
                    elif str(payload[field]) != expr:
                        add_issue(issues, 'OM4', 'OCCURRENCE_EXPR_PAYLOAD_MISMATCH', claim_id=claim, route_id=rid, step_id=sid, occurrence_id=oid, payload_expr=str(payload[field]), expr=expr)
                    occurrence_ok += int(len(issues) == before)
                missing = sorted(refs - mapped)
                if missing:
                    add_issue(issues, 'OM6', 'TENSOR_SUBLEAF_REF_NOT_MAPPED_TO_OCCURRENCE', claim_id=claim, route_id=rid, step_id=sid, missing_subleaf_refs=missing)
                reports.append({'claim_id':claim,'route_id':rid,'step_id':sid,'subleaf_refs':sorted(refs),'occurrence_map_count':len(maps)})
    gates = {f'OM{i}': True for i in range(1,7)}
    for issue in issues:
        gates[issue['gate']] = False
    return {
        'occurrence_maps_total': occurrence_total,
        'occurrence_maps_ok': occurrence_ok,
        'tensor_steps': tensor_steps,
        'tensor_steps_with_occurrence_maps': tensor_steps_with_maps,
        'gates': gates,
        'issue_count': len(issues),
        'issues': issues,
        'step_reports': reports,
    }

def replay_bundle(bundle: Dict[str, Any]) -> Dict[str, Any]:
    base = zf_v05.replay_bundle(bundle)
    occ = validate_occurrence_maps(bundle)
    base['title'] = 'Paper2 Zero Forests strict Level-B+ replay report v0.6 occurrence maps'
    base['strict_level'] = 'Level-B+ named tensor subleaves plus occurrence-level literal-span maps'
    base['occurrence_map_report'] = occ
    base['counts']['occurrence_maps'] = occ['occurrence_maps_total']
    base['counts']['occurrence_maps_checked_ok'] = occ['occurrence_maps_ok']
    base['counts']['tensor_steps_with_occurrence_maps'] = occ['tensor_steps_with_occurrence_maps']
    base['gates'].update(occ['gates'])
    base['issues'].extend(occ['issues'])
    base['issue_count'] = len(base['issues'])
    base['review_pass'] = base['issue_count'] == 0
    return base

def main(argv=None) -> int:
    ap=argparse.ArgumentParser()
    ap.add_argument('--bundle', required=True)
    ap.add_argument('--out', required=True)
    args=ap.parse_args(argv)
    bundle=json.loads(Path(args.bundle).read_text(encoding='utf-8'))
    rep=replay_bundle(bundle)
    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    Path(args.out).write_text(json.dumps(rep, indent=2, ensure_ascii=False)+'\n', encoding='utf-8')
    print(json.dumps({'review_pass':rep['review_pass'], 'counts':rep['counts'], 'occurrence_gates':rep['occurrence_map_report']['gates'], 'issue_count':rep['issue_count']}, indent=2, ensure_ascii=False))
    return 0 if rep['review_pass'] else 1

if __name__ == '__main__':
    raise SystemExit(main())
