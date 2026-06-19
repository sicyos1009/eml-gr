#!/usr/bin/env python3
from __future__ import annotations
import argparse, importlib.util, json
from copy import deepcopy
from pathlib import Path

def load_checker(path):
    spec=importlib.util.spec_from_file_location('checker', str(path))
    m=importlib.util.module_from_spec(spec); assert spec.loader; spec.loader.exec_module(m); return m

def recalc_routes(b,c):
    for cert in b['certificates']:
        for r in cert['routes']:
            r['raw_trace_hash']=c.recompute_raw_route_hash(r)

def recalc_norms(b,c):
    for cert in b['certificates']:
        cert['normalized_hash']=c.recompute_normalized_hash(cert)

def t(b, ci=0, ri=0, si=1):
    cert=b['certificates'][ci]; route=cert['routes'][ri]; step=route['steps'][si]; return cert, route, step

def raw_hash_literal(b,c): b['certificates'][0]['routes'][0]['raw_trace_hash']='deadbeefdeadbeef'
def normalized_hash_literal(b,c): b['certificates'][0]['normalized_hash']='deadbeefdeadbeef'
def final_expr_nonzero_no_rehash(b,c): b['certificates'][0]['routes'][0]['final_expr']='1'
def final_expr_nonzero_rehashed(b,c): b['certificates'][0]['routes'][0]['final_expr']='1'; recalc_routes(b,c)
def unregistered_rule_rehashed(b,c): t(b)[2]['rule_id']='ALG.NOT_REGISTERED'; recalc_routes(b,c)
def rule_class_mismatch_rehashed(b,c): t(b,0,0,2)[2]['rule_class']='tensor_definition'; recalc_routes(b,c)
def route_initial_disconnect_rehashed(b,c): t(b,0,0,0)[2]['before_expr']='42'; recalc_routes(b,c)
def route_step_order_reversed_rehashed(b,c): b['certificates'][0]['routes'][0]['steps']=list(reversed(b['certificates'][0]['routes'][0]['steps'])); recalc_routes(b,c)
def route_last_after_mismatch_rehashed(b,c): t(b,0,0,2)[2]['after_expr']='0+0'; recalc_routes(b,c)
def step_expression_nonzero_rehashed(b,c):
    t(b,0,0,1)[2]['after_expr']='1/rho**2'; b['certificates'][0]['routes'][0]['steps'][2]['before_expr']='1/rho**2'; recalc_routes(b,c)
def domain_ref_deleted_rehashed(b,c):
    cert=b['certificates'][1]; cert['domain']['side_condition_refs']=[]; cert['normalized_obligation']['side_condition_refs']=[]; recalc_norms(b,c)
def domain_condition_deleted_rehashed(b,c):
    cert=b['certificates'][2]; cert['assumptions']=[]; cert['domain']['conditions']=[]; recalc_norms(b,c)
def domain_condition_weakened_rehashed(b,c):
    cert=b['certificates'][2]; cert['assumptions']=['M > 0','r > 0']; cert['domain']['conditions']=['M > 0','r > 0']; recalc_norms(b,c)
def tensor_boundary_changed_rehashed(b,c):
    st=t(b,0,0,0)[2]; st['trust_boundary']='checked_algebra_leaf'; st['replay_method']='sympy_simplify_zero_difference'; recalc_routes(b,c)
def required_rule_classes_missing_tensor_rehashed(b,c):
    cert=b['certificates'][0]; cert['normalized_obligation']['required_rule_classes']=[x for x in cert['normalized_obligation']['required_rule_classes'] if x!='tensor_definition']; recalc_norms(b,c)
def side_condition_unentailed_rehashed(b,c): t(b,0,0,2)[2].setdefault('side_conditions',[]).append('rho < 0'); recalc_routes(b,c)
def normalized_lhs_changed_rehashed(b,c): b['certificates'][0]['normalized_obligation']['lhs_expr']='1'; recalc_norms(b,c)

MUTS=[
('baseline_untampered', lambda b,c: None),
('raw_hash_literal', raw_hash_literal),
('normalized_hash_literal', normalized_hash_literal),
('final_expr_nonzero_no_rehash', final_expr_nonzero_no_rehash),
('final_expr_nonzero_rehashed', final_expr_nonzero_rehashed),
('unregistered_rule_rehashed', unregistered_rule_rehashed),
('rule_class_mismatch_rehashed', rule_class_mismatch_rehashed),
('route_initial_disconnect_rehashed', route_initial_disconnect_rehashed),
('route_step_order_reversed_rehashed', route_step_order_reversed_rehashed),
('route_last_after_mismatch_rehashed', route_last_after_mismatch_rehashed),
('step_expression_nonzero_rehashed', step_expression_nonzero_rehashed),
('domain_ref_deleted_rehashed', domain_ref_deleted_rehashed),
('domain_condition_deleted_rehashed', domain_condition_deleted_rehashed),
('domain_condition_weakened_rehashed', domain_condition_weakened_rehashed),
('declared_tensor_boundary_changed_rehashed', tensor_boundary_changed_rehashed),
('required_rule_classes_missing_tensor_rehashed', required_rule_classes_missing_tensor_rehashed),
('side_condition_unentailed_rehashed', side_condition_unentailed_rehashed),
('normalized_lhs_changed_rehashed', normalized_lhs_changed_rehashed),
]

def main():
    p=argparse.ArgumentParser(); p.add_argument('--bundle', required=True); p.add_argument('--checker', required=True); p.add_argument('--outdir', required=True); p.add_argument('--report', required=True); a=p.parse_args()
    c=load_checker(Path(a.checker)); base=json.loads(Path(a.bundle).read_text(encoding='utf-8')); outdir=Path(a.outdir); outdir.mkdir(parents=True, exist_ok=True)
    cases=[]
    for name, mut in MUTS:
        b=deepcopy(base); mut(b,c)
        bp=outdir/f'{name}.json'; rp=outdir/f'{name}.strict_report.json'
        bp.write_text(json.dumps(b,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
        rep=c.replay_bundle(b); rp.write_text(json.dumps(rep,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
        expected = (name == 'baseline_untampered')
        cases.append({'case_id':name, 'expected_pass':expected, 'observed_pass':rep['review_pass'], 'expectation_met': rep['review_pass']==expected, 'failed_gates':[g for g,v in rep['gates'].items() if not v], 'issue_codes':sorted({i['code'] for i in rep['issues']}), 'issue_count':rep['issue_count']})
    summary={'title':'Paper2 Zero Forests strict tamper suite v0.4-final', 'total_cases':len(cases), 'baseline_pass':cases[0]['observed_pass'], 'malicious_cases':len(cases)-1, 'malicious_cases_rejected':sum(1 for x in cases[1:] if not x['observed_pass']), 'all_expectations_met':all(x['expectation_met'] for x in cases), 'cases':cases}
    Path(a.report).parent.mkdir(parents=True, exist_ok=True); Path(a.report).write_text(json.dumps(summary,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
    md=['# Strict tamper suite v0.4-final','',f"- total cases: {summary['total_cases']}",f"- baseline pass: {summary['baseline_pass']}",f"- malicious cases rejected: {summary['malicious_cases_rejected']} / {summary['malicious_cases']}",f"- all expectations met: {summary['all_expectations_met']}",'','| case | expected pass | observed pass | expectation met | failed gates | issue codes |','|---|---:|---:|---:|---|---|']
    for x in cases: md.append(f"| {x['case_id']} | {x['expected_pass']} | {x['observed_pass']} | {x['expectation_met']} | {', '.join(x['failed_gates'])} | {', '.join(x['issue_codes'])} |")
    Path(a.report).with_suffix('.md').write_text('\n'.join(md)+'\n',encoding='utf-8')
    print(json.dumps({'all_expectations_met':summary['all_expectations_met'], 'malicious_cases_rejected':summary['malicious_cases_rejected'], 'malicious_cases':summary['malicious_cases']},indent=2))
    return 0 if summary['all_expectations_met'] else 1
if __name__ == '__main__': raise SystemExit(main())
