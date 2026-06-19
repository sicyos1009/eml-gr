#!/usr/bin/env python3
from __future__ import annotations
import argparse, copy, hashlib, importlib.util, json
from pathlib import Path
from typing import Any

_CHECKER = Path(__file__).with_name('zero_replay_checker_v0_6_occurrence_maps.py')
_SPEC = importlib.util.spec_from_file_location('zf_v06', _CHECKER)
zf_v06 = importlib.util.module_from_spec(_SPEC)
assert _SPEC and _SPEC.loader
_SPEC.loader.exec_module(zf_v06)

def canonical_json(obj: Any) -> str:
    return json.dumps(obj, sort_keys=True, separators=(',', ':'), ensure_ascii=False)

def hash16(obj: Any) -> str:
    return hashlib.sha256(canonical_json(obj).encode('utf-8')).hexdigest()[:16]

def occ_hash(occ):
    d=dict(occ); d.pop('occurrence_hash', None)
    return hash16(d)

def route_hash(route):
    return hash16({'route_id':route['route_id'],'route_kind':route['route_kind'],'steps':route['steps'],'final_expr':route['final_expr'],'route_notes':route.get('route_notes','')})

def subleaf_hash(leaf):
    d=dict(leaf); d.pop('subleaf_hash', None)
    return hash16(d)

def rehash_occ_routes(bundle):
    for cert in bundle.get('certificates', []):
        for route in cert.get('routes', []):
            for st in route.get('steps', []):
                for om in st.get('occurrence_maps', []) or []:
                    om['occurrence_hash'] = occ_hash(om)
            route['raw_trace_hash'] = route_hash(route)

def rehash_subleaves(bundle):
    for cert in bundle.get('certificates', []):
        for leaf in cert.get('tensor_subleaves', []) or []:
            leaf['subleaf_hash'] = subleaf_hash(leaf)

def flrw(bundle):
    return next(c for c in bundle['certificates'] if c['claim_id'] == 'zero.flrw.contracted_bianchi_divG0')

def step(bundle, step_id='A2'):
    c=flrw(bundle)
    for route in c['routes']:
        for st in route['steps']:
            if st.get('step_id') == step_id:
                return route, st
    raise KeyError(step_id)

def occ(st, role='connection_trace_factor'):
    return next(o for o in st['occurrence_maps'] if role in o['occurrence_id'])

def make_cases(base):
    cases=[]
    def add(name, b, expect, note):
        cases.append((name,b,expect,note))
    add('baseline_untampered', copy.deepcopy(base), True, 'baseline should pass occurrence-map validation')
    b=copy.deepcopy(base); r,s=step(b); occ(s)['occurrence_hash']='0'*16; add('occurrence_hash_literal', b, False, 'hash literal mutation')
    b=copy.deepcopy(base); r,s=step(b); occ(s)['span_end'] += 1; rehash_occ_routes(b); add('occurrence_span_shift_rehashed', b, False, 'span shift with recomputed hashes')
    b=copy.deepcopy(base); r,s=step(b); occ(s)['expr']='4*H'; rehash_occ_routes(b); add('occurrence_expr_drift_rehashed', b, False, 'expression drift with recomputed hashes')
    b=copy.deepcopy(base); r,s=step(b); occ(s)['literal_occurrence_index_0_based']=2; rehash_occ_routes(b); add('occurrence_index_mismatch_rehashed', b, False, 'wrong occurrence index')
    b=copy.deepcopy(base); r,s=step(b); occ(s)['payload_field']='missing_field'; rehash_occ_routes(b); add('occurrence_payload_field_missing_rehashed', b, False, 'payload field deleted')
    b=copy.deepcopy(base); r,s=step(b); s['occurrence_maps']=[x for x in s['occurrence_maps'] if x.get('subleaf_id')!='flrw.connection.gamma_trace_0']; rehash_occ_routes(b); add('occurrence_for_ref_deleted_rehashed', b, False, 'referenced subleaf no longer mapped')
    b=copy.deepcopy(base); r,s=step(b); occ(s)['subleaf_id']='flrw.no_such_leaf'; rehash_occ_routes(b); add('occurrence_subleaf_wrong_rehashed', b, False, 'wrong subleaf id')
    b=copy.deepcopy(base); r,s=step(b); s['subleaf_refs'].append('flrw.metric.scale_factor'); rehash_occ_routes(b); add('unmapped_extra_subleaf_ref_rehashed', b, False, 'extra subleaf ref without map')
    b=copy.deepcopy(base); c=flrw(b); leaf=next(x for x in c['tensor_subleaves'] if x['subleaf_id']=='flrw.connection.gamma_trace_0'); leaf['payload']['gamma_trace_0_expr']='4*H'; rehash_subleaves(b); rehash_occ_routes(b); add('subleaf_payload_changed_rehashed', b, False, 'payload drift')
    b=copy.deepcopy(base); r,s=step(b); s['after_expr']=s['after_expr'].replace('3*H*3*H**2','4*H*3*H**2',1); rehash_occ_routes(b); add('route_expr_mutated_stale_occurrences_rehashed', b, False, 'route expression drift')
    b=copy.deepcopy(base); r,s=step(b); s['occurrence_maps'].append(copy.deepcopy(s['occurrence_maps'][1])); rehash_occ_routes(b); add('duplicate_occurrence_id_rehashed', b, False, 'duplicate id')
    return cases

def main(argv=None):
    ap=argparse.ArgumentParser()
    ap.add_argument('--bundle', required=True)
    ap.add_argument('--out', required=True)
    ap.add_argument('--cases-dir', required=True)
    args=ap.parse_args(argv)
    base=json.loads(Path(args.bundle).read_text(encoding='utf-8'))
    outdir=Path(args.cases_dir); outdir.mkdir(parents=True, exist_ok=True)
    records=[]
    for name,b,expect,note in make_cases(base):
        case_path=outdir/(name+'.json')
        case_path.write_text(json.dumps(b, indent=2, ensure_ascii=False)+'\n', encoding='utf-8')
        rep=zf_v06.validate_occurrence_maps(b)
        rep_path=outdir/(name+'.occurrence_report.json')
        rep_path.write_text(json.dumps(rep, indent=2, ensure_ascii=False)+'\n', encoding='utf-8')
        got = rep['issue_count'] == 0
        records.append({'case':name,'expect_pass':expect,'got_pass':got,'expectation_met':got==expect,'issue_count':rep['issue_count'],'first_issue_codes':[i['code'] for i in rep['issues'][:5]],'note':note})
    report={'title':'Paper2 Zero Forests v0.6 occurrence-map tamper suite','baseline_pass':records[0]['got_pass'],'total_cases':len(records),'malicious_cases':len(records)-1,'malicious_cases_rejected':sum(not r['got_pass'] for r in records[1:]),'all_expectations_met':all(r['expectation_met'] for r in records),'records':records}
    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    Path(args.out).write_text(json.dumps(report, indent=2, ensure_ascii=False)+'\n', encoding='utf-8')
    print(json.dumps({k:report[k] for k in ['baseline_pass','total_cases','malicious_cases_rejected','all_expectations_met']}, indent=2))
    return 0 if report['all_expectations_met'] else 1

if __name__ == '__main__':
    raise SystemExit(main())
