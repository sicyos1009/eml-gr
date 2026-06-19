#!/usr/bin/env python3
from __future__ import annotations
import argparse, copy, hashlib, importlib.util, json
from pathlib import Path
from typing import Any, Dict

def canonical_json(obj: Any) -> str:
    return json.dumps(obj, sort_keys=True, separators=(',', ':'), ensure_ascii=False)

def hash16(obj: Any) -> str:
    return hashlib.sha256(canonical_json(obj).encode('utf-8')).hexdigest()[:16]

def route_hash(route: Dict[str, Any]) -> str:
    return hash16({'route_id': route['route_id'], 'route_kind': route['route_kind'], 'steps': route['steps'], 'final_expr': route['final_expr'], 'route_notes': route.get('route_notes','')})

def norm_hash(cert: Dict[str, Any]) -> str:
    d=cert['domain']; n=cert['normalized_obligation']
    return hash16({'schema_major':'1.2','kind':'zero_certificate','claim_id':cert['claim_id'],'object_signature':cert['object_signature'],'domain_signature':{'domain_id':d['domain_id'],'conditions':sorted(d.get('conditions',[])),'side_condition_refs':sorted(d.get('side_condition_refs',[]))},'assumptions_canonical':sorted(cert.get('assumptions',[])),'zero_obligation':{'lhs_expr':n['lhs_expr'],'target_normal_form':n['target_normal_form']},'final_normal_form':'0','required_rule_classes_sorted':sorted(n.get('required_rule_classes',[])),'side_condition_refs_sorted':sorted(n.get('side_condition_refs',[])),'formal_fragment':cert['formal_fragment']})

def subleaf_hash(leaf: Dict[str, Any]) -> str:
    tmp=dict(leaf); tmp.pop('subleaf_hash', None); return hash16(tmp)

def flrw(bundle: Dict[str, Any]) -> Dict[str, Any]:
    return next(c for c in bundle['certificates'] if c['claim_id']=='zero.flrw.contracted_bianchi_divG0')

def leaf(cert: Dict[str, Any], sid: str) -> Dict[str, Any]:
    return next(x for x in cert['tensor_subleaves'] if x['subleaf_id']==sid)

def rehash_flrw(cert: Dict[str, Any]):
    for lf in cert.get('tensor_subleaves', []):
        lf['subleaf_hash'] = subleaf_hash(lf)
    for rt in cert.get('routes', []):
        rt['raw_trace_hash'] = route_hash(rt)
    cert['normalized_hash'] = norm_hash(cert)

def run_case(mod, case, outdir: Path, bundle: Dict[str, Any]):
    path = outdir / f'{case}.json'
    rep_path = outdir / f'{case}.strict_report.json'
    path.write_text(json.dumps(bundle, indent=2, ensure_ascii=False)+'\n', encoding='utf-8')
    rep = mod.replay_bundle(bundle)
    rep_path.write_text(json.dumps(rep, indent=2, ensure_ascii=False)+'\n', encoding='utf-8')
    return {'case': case, 'review_pass': rep['review_pass'], 'issue_count': rep['issue_count'], 'failed_gates': [k for k,v in rep['gates'].items() if not v], 'path': str(path.name), 'report': str(rep_path.name)}

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--bundle', required=True)
    ap.add_argument('--outdir', required=True)
    ap.add_argument('--report-json', required=True)
    ap.add_argument('--report-md', required=True)
    args=ap.parse_args()
    here=Path(__file__).resolve().parent
    spec=importlib.util.spec_from_file_location('z05', here/'zero_replay_checker_v0_5_strict.py')
    mod=importlib.util.module_from_spec(spec); assert spec.loader is not None; spec.loader.exec_module(mod)
    base=json.loads(Path(args.bundle).read_text(encoding='utf-8'))
    outdir=Path(args.outdir); outdir.mkdir(parents=True, exist_ok=True)
    cases=[]
    cases.append(run_case(mod, 'baseline_untampered', outdir, copy.deepcopy(base)))
    # 1 stale subleaf hash.
    b=copy.deepcopy(base); leaf(flrw(b),'flrw.connection.gamma_trace_0')['subleaf_hash']='0000000000000000'
    cases.append(run_case(mod,'flrw_subleaf_hash_literal',outdir,b))
    # 2 semantically wrong gamma trace but hash refreshed.
    b=copy.deepcopy(base); l=leaf(flrw(b),'flrw.connection.gamma_trace_0'); l['payload']['gamma_trace_0_expr']='4*H'; rehash_flrw(flrw(b))
    cases.append(run_case(mod,'flrw_gamma_trace_mutated_rehashed',outdir,b))
    # 3 wrong sign for Gii.
    b=copy.deepcopy(base); l=leaf(flrw(b),'flrw.einstein.G_contra_ii'); l['payload']['G_contra_ii_expr']='3*H**2*exp(-2*H*t)'; rehash_flrw(flrw(b))
    cases.append(run_case(mod,'flrw_Gii_sign_mutated_rehashed',outdir,b))
    # 4 remove required dependency.
    b=copy.deepcopy(base); l=leaf(flrw(b),'flrw.divergence.expanded_nu0'); l['dependencies']=[x for x in l['dependencies'] if x!='flrw.einstein.G_contra_ii']; rehash_flrw(flrw(b))
    cases.append(run_case(mod,'flrw_divergence_dependency_deleted_rehashed',outdir,b))
    # 5 divergence expression drifts away from normalized lhs.
    b=copy.deepcopy(base); l=leaf(flrw(b),'flrw.divergence.expanded_nu0'); l['payload']['divergence_expanded_expr']='diff(3*H**2, t) + 3*H*3*H**2'; rehash_flrw(flrw(b))
    cases.append(run_case(mod,'flrw_divergence_expr_drift_rehashed',outdir,b))
    # 6 route subleaf refs deleted but route raw hashes refreshed.
    b=copy.deepcopy(base); c=flrw(b)
    for rt in c['routes']:
        for st in rt['steps']:
            if st.get('rule_class') in {'tensor_definition','tensor_identity'}:
                st['subleaf_refs']=[]
    rehash_flrw(c)
    cases.append(run_case(mod,'flrw_route_subleaf_refs_deleted_rehashed',outdir,b))
    # 7 normalized lhs mutated consistently except route initial not updated: should fail route/subleaf matching.
    b=copy.deepcopy(base); c=flrw(b); c['normalized_obligation']['lhs_expr']='3*H*3*H**2 + 3*(H*exp(2*H*t))*(-3*H**2*exp(-2*H*t)) + H'; c['normalized_hash']=norm_hash(c)
    cases.append(run_case(mod,'flrw_normalized_lhs_mutated_rehashed',outdir,b))
    malicious=[x for x in cases if x['case']!='baseline_untampered']
    summary={'title':'Paper2 v0.5 tensor-subleaf tamper suite','baseline_pass':cases[0]['review_pass'],'total_cases':len(cases),'malicious_cases':len(malicious),'malicious_cases_rejected':sum(not x['review_pass'] for x in malicious),'all_expectations_met':cases[0]['review_pass'] and all(not x['review_pass'] for x in malicious),'cases':cases}
    Path(args.report_json).write_text(json.dumps(summary, indent=2, ensure_ascii=False)+'\n', encoding='utf-8')
    md=['# Paper2 v0.5 tensor-subleaf tamper suite','',f"baseline_pass: `{summary['baseline_pass']}`",f"total_cases: `{summary['total_cases']}`",f"malicious_cases_rejected: `{summary['malicious_cases_rejected']}/{summary['malicious_cases']}`",f"all_expectations_met: `{summary['all_expectations_met']}`",'','| case | review_pass | failed gates | issues |','|---|---:|---|---:|']
    for x in cases:
        md.append(f"| `{x['case']}` | `{x['review_pass']}` | `{', '.join(x['failed_gates'])}` | `{x['issue_count']}` |")
    Path(args.report_md).write_text('\n'.join(md)+'\n', encoding='utf-8')
    print(json.dumps({'all_expectations_met':summary['all_expectations_met'],'malicious_cases_rejected':summary['malicious_cases_rejected'],'malicious_cases':summary['malicious_cases']}, indent=2))
    return 0 if summary['all_expectations_met'] else 1
if __name__ == '__main__':
    raise SystemExit(main())
